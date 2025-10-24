from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel


class ResponseBase(BaseModel):
    """Base response schema."""

    success: bool = True
    message: str = "Operation completed successfully"


class ErrorResponse(BaseModel):
    """Error response schema."""

    success: bool = False
    message: str
    error_code: str | None = None
    details: dict[str, Any] | None = None


class PaginationResponse(BaseModel):
    """Pagination response schema."""

    page: int
    size: int
    total: int
    pages: int


class HealthCheckResponse(BaseModel):
    """Health check response schema."""

    status: str = "healthy"
    timestamp: datetime
    version: str
    environment: str
    database_status: dict[str, str]


class MessageResponse(BaseModel):
    """Simple message response schema."""

    message: str
