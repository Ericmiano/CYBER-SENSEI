"""
Pagination utilities for handling paginated responses
"""

from typing import TypeVar, Generic, List, Optional, Any
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model"""
    items: List[Any] = Field(default_factory=list)
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    limit: int = Field(ge=1)
    pages: int = Field(ge=1)
    
    class Config:
        arbitrary_types_allowed = True
        schema_extra = {
            "example": {
                "items": [],
                "total": 100,
                "page": 1,
                "limit": 10,
                "pages": 10
            }
        }

def paginate(
    query,
    page: int = 1,
    limit: int = 10,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> dict:
    """
    Paginate a SQLAlchemy query
    
    Args:
        query: SQLAlchemy query object
        page: Page number (1-indexed)
        limit: Items per page
        sort_by: Field to sort by
        sort_order: 'asc' or 'desc'
    
    Returns:
        Dict with paginated response data
    """
    # Validate inputs
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10
    if limit > 100:
        limit = 100
    
    # Get total count
    total = query.count()
    
    # Apply sorting if specified
    if sort_by and hasattr(query.statement.froms[0].entity, sort_by):
        sort_column = getattr(query.statement.froms[0].entity, sort_by)
        if sort_order.lower() == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())
    
    # Get items for current page
    items = query.offset((page - 1) * limit).limit(limit).all()
    
    # Calculate total pages
    pages = (total + limit - 1) // limit if total > 0 else 1
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": pages
    }

def create_paginated_response(data: dict, items_schema=None) -> PaginatedResponse:
    """
    Create a PaginatedResponse from paginate() output
    
    Args:
        data: Dict from paginate() function
        items_schema: Pydantic schema for items (optional)
    
    Returns:
        PaginatedResponse instance
    """
    items = data.get("items", [])
    
    # Convert to schema if provided
    if items_schema:
        items = [items_schema.from_orm(item) for item in items]
    
    return PaginatedResponse(
        items=items,
        total=data["total"],
        page=data["page"],
        limit=data["limit"],
        pages=data["pages"]
    )

__all__ = ["PaginatedResponse", "paginate", "create_paginated_response"]
