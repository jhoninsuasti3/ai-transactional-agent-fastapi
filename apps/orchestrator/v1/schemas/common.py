"""Common schemas for API v1."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model for all API responses."""

    success: bool = Field(..., description="Whether the request was successful")
    message: str | None = Field(None, description="Optional message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class ErrorDetail(BaseModel):
    """Error detail information."""

    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    field: str | None = Field(None, description="Field that caused the error")


class ErrorResponse(BaseResponse):
    """Error response model."""

    success: bool = Field(default=False, description="Always false for errors")
    error: ErrorDetail = Field(..., description="Error details")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")
    components: dict[str, str] | None = Field(None, description="Status of individual components")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    items: list[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")
