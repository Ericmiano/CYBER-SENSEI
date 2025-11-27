"""Annotation and bookmark schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AnnotationType(str, Enum):
    """Types of annotations."""
    BOOKMARK = "bookmark"
    HIGHLIGHT = "highlight"
    NOTE = "note"
    TAG = "tag"


class AnnotationCreate(BaseModel):
    """Schema for creating annotations."""
    resource_id: int = Field(..., description="ID of the resource being annotated")
    annotation_type: AnnotationType = Field(default=AnnotationType.BOOKMARK)
    highlighted_text: Optional[str] = Field(None, description="Text that was highlighted")
    content: Optional[str] = Field(None, description="Note or tag content")
    position: Optional[str] = Field(None, description="Position in document (e.g., 'char:100-150')")
    is_public: bool = Field(default=False, description="Whether annotation is publicly visible")


class AnnotationUpdate(BaseModel):
    """Schema for updating annotations."""
    content: Optional[str] = Field(None)
    highlighted_text: Optional[str] = Field(None)
    position: Optional[str] = Field(None)
    is_public: Optional[bool] = Field(None)


class AnnotationRead(BaseModel):
    """Schema for reading annotations."""
    id: int
    user_id: int
    resource_id: int
    annotation_type: AnnotationType
    highlighted_text: Optional[str] = None
    content: Optional[str] = None
    position: Optional[str] = None
    is_public: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
