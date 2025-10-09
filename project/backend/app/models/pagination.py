from typing import Generic, TypeVar, List
from pydantic import BaseModel, Field

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Query parameters for pagination"""
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=10, ge=1, le=100, description="Number of records to return")
    order_by: str = Field(default="id", description="Field to order by")
    order_dir: str = Field(default="desc", description="Order direction (asc or desc)")

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool

    class Config:
        from_attributes = True

