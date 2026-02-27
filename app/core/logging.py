"""Structured logging configuration."""

import logging
import sys
from pythonjsonlogger import jsonlogger
from app.core.config import get_settings

settings = get_settings()

# Global error counter
_error_counts: dict[str, int] = {}


def increment_error_count(error_type: str = "general") -> None:
    """Increment the error count for a given error type."""
    _error_counts[error_type] = _error_counts.get(error_type, 0) + 1


def get_error_counts() -> dict[str, int]:
    """Return a copy of the current error counts."""
    return dict(_error_counts)


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter for structured logging."""

    def add_fields(
        self, log_record: dict, record: logging.LogRecord, message_dict: dict
    ) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)

        # Add standard fields
        log_record["timestamp"] = self.formatTime(record, self.datefmt)
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module
        log_record["function"] = record.funcName

        # Add service info
        log_record["service"] = settings.app_name
        log_record["environment"] = settings.environment

        # Track and attach error counts
        if record.levelno >= logging.ERROR:
            error_type = getattr(record, "error_type", record.module)
            increment_error_count(error_type)
        log_record["error_counts"] = get_error_counts()

        # Add request_id if available in context
        try:
            from app.core.middleware import get_request_id

            request_id = get_request_id()
            if request_id:
                log_record["request_id"] = request_id
        except Exception:
            # If middleware not initialized or outside request context
            pass


def setup_logging() -> logging.Logger:
    """Configure and return application logger."""

    # Create formatter
    formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")

    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Apply to root "app" logger so all app.* child loggers inherit it
    app_logger = logging.getLogger("app")
    app_logger.setLevel(getattr(logging, settings.log_level.upper()))
    app_logger.handlers.clear()
    app_logger.addHandler(console_handler)
    app_logger.propagate = False

    # Also set up the named ocr_service logger
    logger = logging.getLogger("ocr_service")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    logger.handlers.clear()
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


def get_logger(name: str = "ocr_service") -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)


# Initialize logger
logger = setup_logging()
