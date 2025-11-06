"""
Retry Logic and Resilience Utilities
Industry-standard patterns for handling transient failures
"""

import time
import functools
from typing import Callable, Type, Tuple, Optional, Any
from src.core.exceptions import LLMTimeoutError, LLMRateLimitError
from src.utils.logging import get_logger

logger = get_logger(__name__)


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
) -> float:
    """
    Calculate exponential backoff delay

    Args:
        attempt: Current attempt number (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation

    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (exponential_base ** attempt), max_delay)
    return delay


def retry_with_exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator for retrying function calls with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        exceptions: Tuple of exception types to catch and retry
        on_retry: Optional callback function called on each retry

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}",
                            extra={
                                "function": func.__name__,
                                "error": str(e),
                                "attempts": attempt + 1
                            }
                        )
                        raise

                    delay = exponential_backoff(
                        attempt,
                        base_delay,
                        max_delay,
                        exponential_base
                    )

                    logger.warning(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.2f}s",
                        extra={
                            "function": func.__name__,
                            "error": str(e),
                            "attempt": attempt + 1,
                            "delay": delay
                        }
                    )

                    if on_retry:
                        on_retry(e, attempt)

                    time.sleep(delay)

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def retry_on_rate_limit(max_retries: int = 5, base_delay: float = 2.0):
    """
    Specialized retry decorator for rate limit errors

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds

    Returns:
        Decorated function
    """
    def on_retry_callback(exception: Exception, attempt: int):
        if isinstance(exception, LLMRateLimitError):
            logger.warning(
                f"Rate limit hit, backing off exponentially",
                extra={"attempt": attempt + 1}
            )

    return retry_with_exponential_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=300.0,  # 5 minutes max
        exponential_base=2.0,
        exceptions=(LLMRateLimitError,),
        on_retry=on_retry_callback
    )


def retry_on_timeout(max_retries: int = 3, base_delay: float = 1.0):
    """
    Specialized retry decorator for timeout errors

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds

    Returns:
        Decorated function
    """
    return retry_with_exponential_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=30.0,
        exponential_base=2.0,
        exceptions=(LLMTimeoutError, TimeoutError)
    )


class CircuitBreaker:
    """
    Circuit breaker pattern implementation
    Prevents cascading failures by stopping requests after threshold failures
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exceptions: Tuple[Type[Exception], ...] = (Exception,)
    ):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting to close circuit
            expected_exceptions: Exceptions that count as failures
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exceptions = expected_exceptions

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Call function through circuit breaker

        Args:
            func: Function to call
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is open or function fails
        """
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
                logger.info("Circuit breaker: Attempting reset (half-open state)")
            else:
                raise Exception(
                    f"Circuit breaker is OPEN. "
                    f"Retry after {self.recovery_timeout}s"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exceptions as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call"""
        if self.state == "half_open":
            logger.info("Circuit breaker: Closing after successful call")
            self.state = "closed"
        self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.error(
                f"Circuit breaker: OPENED after {self.failure_count} failures",
                extra={"failure_count": self.failure_count}
            )

    def reset(self):
        """Manually reset circuit breaker"""
        self.state = "closed"
        self.failure_count = 0
        self.last_failure_time = None
        logger.info("Circuit breaker: Manually reset")


def with_circuit_breaker(circuit_breaker: CircuitBreaker):
    """
    Decorator to apply circuit breaker to function

    Args:
        circuit_breaker: CircuitBreaker instance

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            return circuit_breaker.call(func, *args, **kwargs)
        return wrapper
    return decorator


def timeout(seconds: int):
    """
    Decorator to add timeout to function

    Args:
        seconds: Timeout in seconds

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import signal

            def timeout_handler(signum, frame):
                raise LLMTimeoutError(
                    f"Function {func.__name__} timed out after {seconds}s"
                )

            # Set the timeout handler
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)

            try:
                result = func(*args, **kwargs)
            finally:
                # Restore the old handler and disable alarm
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            return result
        return wrapper
    return decorator
