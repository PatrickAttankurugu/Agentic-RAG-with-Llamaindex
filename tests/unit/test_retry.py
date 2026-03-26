"""Unit tests for retry logic and resilience utilities."""

import pytest
import time

from src.utils.retry import (
    exponential_backoff,
    retry_with_exponential_backoff,
    CircuitBreaker,
    timeout,
)
from src.core.exceptions import LLMTimeoutError


class TestExponentialBackoff:
    def test_first_attempt(self):
        delay = exponential_backoff(0, base_delay=1.0)
        assert delay == 1.0

    def test_second_attempt(self):
        delay = exponential_backoff(1, base_delay=1.0, exponential_base=2.0)
        assert delay == 2.0

    def test_third_attempt(self):
        delay = exponential_backoff(2, base_delay=1.0, exponential_base=2.0)
        assert delay == 4.0

    def test_max_delay_cap(self):
        delay = exponential_backoff(100, base_delay=1.0, max_delay=10.0)
        assert delay == 10.0

    def test_custom_base(self):
        delay = exponential_backoff(2, base_delay=0.5, exponential_base=3.0)
        assert delay == 0.5 * (3.0 ** 2)


class TestRetryDecorator:
    def test_succeeds_first_try(self):
        call_count = 0

        @retry_with_exponential_backoff(max_retries=3, base_delay=0.01)
        def always_works():
            nonlocal call_count
            call_count += 1
            return "ok"

        result = always_works()
        assert result == "ok"
        assert call_count == 1

    def test_retries_then_succeeds(self):
        call_count = 0

        @retry_with_exponential_backoff(max_retries=3, base_delay=0.01)
        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("not yet")
            return "ok"

        result = fails_twice()
        assert result == "ok"
        assert call_count == 3

    def test_exhausts_retries(self):
        @retry_with_exponential_backoff(
            max_retries=2, base_delay=0.01, exceptions=(ValueError,)
        )
        def always_fails():
            raise ValueError("always")

        with pytest.raises(ValueError, match="always"):
            always_fails()

    def test_on_retry_callback(self):
        retries = []

        def on_retry(exc, attempt):
            retries.append(attempt)

        @retry_with_exponential_backoff(
            max_retries=2, base_delay=0.01, on_retry=on_retry
        )
        def fails_once():
            if len(retries) == 0:
                raise ValueError("first")
            return "ok"

        result = fails_once()
        assert result == "ok"
        assert len(retries) == 1
        assert retries[0] == 0

    def test_only_catches_specified_exceptions(self):
        @retry_with_exponential_backoff(
            max_retries=3, base_delay=0.01, exceptions=(ValueError,)
        )
        def raises_type_error():
            raise TypeError("wrong type")

        with pytest.raises(TypeError):
            raises_type_error()


class TestCircuitBreaker:
    def test_closed_state_passes_through(self):
        cb = CircuitBreaker(failure_threshold=3)
        result = cb.call(lambda: "ok")
        assert result == "ok"
        assert cb.state == "closed"

    def test_opens_after_threshold(self):
        cb = CircuitBreaker(failure_threshold=2, expected_exceptions=(ValueError,))

        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(self._raise_value_error)

        assert cb.state == "open"

    def test_open_circuit_rejects_calls(self):
        cb = CircuitBreaker(
            failure_threshold=1, recovery_timeout=100, expected_exceptions=(ValueError,)
        )
        with pytest.raises(ValueError):
            cb.call(self._raise_value_error)

        assert cb.state == "open"
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            cb.call(lambda: "should not reach")

    def test_half_open_after_recovery_timeout(self):
        cb = CircuitBreaker(
            failure_threshold=1, recovery_timeout=0.01, expected_exceptions=(ValueError,)
        )
        with pytest.raises(ValueError):
            cb.call(self._raise_value_error)

        assert cb.state == "open"
        time.sleep(0.02)

        # Should attempt reset (half-open) and succeed
        result = cb.call(lambda: "recovered")
        assert result == "recovered"
        assert cb.state == "closed"

    def test_manual_reset(self):
        cb = CircuitBreaker(failure_threshold=1, expected_exceptions=(ValueError,))
        with pytest.raises(ValueError):
            cb.call(self._raise_value_error)

        assert cb.state == "open"
        cb.reset()
        assert cb.state == "closed"
        assert cb.failure_count == 0

    @staticmethod
    def _raise_value_error():
        raise ValueError("fail")


class TestTimeout:
    def test_function_completes_within_timeout(self):
        @timeout(5)
        def fast():
            return "done"

        assert fast() == "done"

    def test_function_exceeds_timeout(self):
        @timeout(1)
        def slow():
            time.sleep(5)
            return "should not reach"

        with pytest.raises(LLMTimeoutError):
            slow()
