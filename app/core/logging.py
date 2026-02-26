"""Structured logging configuration."""

import logging
import sys
from typing import Any
from pythonjsonlogger import jsonlogger
from app.core.config import get_settings

settings = get_settings()


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


def setup_logging() -> logging.Logger:
    """Configure and return application logger."""

    # Create logger
    logger = logging.getLogger("ocr_service")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper()))

    # Set JSON formatter
    formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str = "ocr_service") -> logging.Logger:
    """Get logger instance."""
    return logging.getLogger(name)


# Initialize logger
logger = setup_logging()
