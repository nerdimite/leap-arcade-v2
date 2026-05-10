from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationInfo(BaseModel):
    total: int = Field(..., description="Total items matching the filter")
    count: int = Field(..., description="Items returned in this response")
    page: Optional[int] = Field(None, description="Current page number (1-indexed)")
    page_size: Optional[int] = Field(None, description="Items per page")
    total_pages: Optional[int] = Field(None, description="Total pages available")


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = Field(default=True)
    message: str
    data: Optional[T] = None


class ErrorResponse(BaseModel):
    success: bool = Field(default=False)
    message: str
    code: int
    http_status: int
    error: dict[str, Any] = Field(default_factory=dict)


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(50, ge=1, le=200, description="Items per page")
