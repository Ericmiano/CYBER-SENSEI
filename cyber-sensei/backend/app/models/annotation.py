"""User annotations and bookmarks models."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.database import Base


class AnnotationType(str, enum.Enum):
    """Types of annotations."""
    BOOKMARK = "bookmark"
    HIGHLIGHT = "highlight"
    NOTE = "note"
    TAG = "tag"


class Annotation(Base):
    """User annotation and bookmark model."""
    
    __tablename__ = "annotations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    resource_id = Column(Integer, ForeignKey("content.id", ondelete="CASCADE"), index=True, nullable=False)
    
    annotation_type = Column(
        SQLEnum(AnnotationType),
        default=AnnotationType.BOOKMARK,
        index=True,
        nullable=False
    )
    
    # For highlights: the highlighted text
    highlighted_text = Column(Text, nullable=True)
    
    # For notes and tags: the content
    content = Column(Text, nullable=True)
    
    # Position in document (for highlights)
    position = Column(String(255), nullable=True)  # e.g., "char:100-150"
    
    # Is public/shared
    is_public = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="annotations")
    resource = relationship("Content", back_populates="annotations")
    
    def __repr__(self):
        return f"<Annotation(id={self.id}, type={self.annotation_type}, resource_id={self.resource_id})>"
