"""
Structured Logging Configuration
Industry-standard logging with JSON support
"""

import logging
import sys
import json
from typing import Any, Dict, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger
from config.settings import LoggingConfig


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)


class LoggerManager:
    """Centralized logger management"""

    _instance: Optional['LoggerManager'] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._loggers: Dict[str, Any] = {}
            LoggerManager._initialized = True

    def setup_logger(
        self,
        name: str,
        config: Optional[LoggingConfig] = None
    ) -> Any:
        """
        Set up logger with configuration

        Args:
            name: Logger name
            config: Logging configuration

        Returns:
            Configured logger instance
        """
        if name in self._loggers:
            return self._loggers[name]

        # Remove default handlers
        logger.remove()

        # Console handler
        if config and config.format == "json":
            logger.add(
                sys.stderr,
                format=self._json_format,
                level=config.level if config else "INFO",
                serialize=True
            )
        else:
            logger.add(
                sys.stderr,
                format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                       "<level>{level: <8}</level> | "
                       "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                       "<level>{message}</level>",
                level=config.level if config else "INFO",
                colorize=True
            )

        # File handler
        if config and config.output_file:
            output_path = Path(config.output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            logger.add(
                config.output_file,
                rotation=config.rotation,
                retention=config.retention,
                level=config.level,
                format=self._json_format if config.format == "json" else None,
                serialize=config.format == "json"
            )

        self._loggers[name] = logger
        return logger

    @staticmethod
    def _json_format(record: Dict[str, Any]) -> str:
        """Format record as JSON"""
        return json.dumps({
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "message": record["message"],
            "module": record["module"],
            "function": record["function"],
            "line": record["line"],
        }) + "\n"

    def get_logger(self, name: str) -> Any:
        """Get or create logger"""
        if name not in self._loggers:
            return self.setup_logger(name)
        return self._loggers[name]


# Global logger manager instance
_logger_manager = LoggerManager()


def get_logger(name: str, config: Optional[LoggingConfig] = None) -> Any:
    """
    Get configured logger instance

    Args:
        name: Logger name
        config: Optional logging configuration

    Returns:
        Logger instance
    """
    if config:
        return _logger_manager.setup_logger(name, config)
    return _logger_manager.get_logger(name)


def log_function_call(logger_instance: Any):
    """
    Decorator to log function calls

    Args:
        logger_instance: Logger to use for logging
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger_instance.info(
                f"Calling {func.__name__}",
                extra={
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs": list(kwargs.keys())
                }
            )
            try:
                result = func(*args, **kwargs)
                logger_instance.info(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger_instance.error(
                    f"{func.__name__} failed: {str(e)}",
                    extra={"error": str(e), "error_type": type(e).__name__}
                )
                raise
        return wrapper
    return decorator


class ContextLogger:
    """Context manager for logging with additional context"""

    def __init__(self, logger_instance: Any, operation: str, **context):
        self.logger = logger_instance
        self.operation = operation
        self.context = context
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.info(
            f"Starting {self.operation}",
            extra={"operation": self.operation, **self.context}
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds()

        if exc_type is None:
            self.logger.info(
                f"Completed {self.operation}",
                extra={
                    "operation": self.operation,
                    "duration_seconds": duration,
                    **self.context
                }
            )
        else:
            self.logger.error(
                f"Failed {self.operation}",
                extra={
                    "operation": self.operation,
                    "duration_seconds": duration,
                    "error": str(exc_val),
                    "error_type": exc_type.__name__,
                    **self.context
                }
            )
        return False
