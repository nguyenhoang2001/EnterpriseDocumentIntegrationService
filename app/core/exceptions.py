"""Custom exceptions for the application."""

from typing import Any, Optional


class OCRServiceException(Exception):
    """Base exception for OCR service."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(OCRServiceException):
    """Exception raised for validation errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class MappingError(OCRServiceException):
    """Exception raised for mapping errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class DatabaseError(OCRServiceException):
    """Exception raised for database errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)


class NotFoundError(OCRServiceException):
    """Exception raised when resource is not found."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)
