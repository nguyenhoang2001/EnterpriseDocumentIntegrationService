"""Request tracking middleware."""

import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from contextvars import ContextVar

# Context variable to store request_id
request_id_context: ContextVar[str] = ContextVar("request_id", default=None)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and track request IDs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Generate a unique request ID for each request.

        - Checks for existing X-Request-ID header
        - Generates new UUID if not present
        - Adds to response headers
        - Stores in context for logging
        """
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Store in context for access by loggers
        request_id_context.set(request_id)

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


def get_request_id() -> str:
    """Get current request ID from context."""
    return request_id_context.get()
