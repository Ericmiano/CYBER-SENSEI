"""User annotations and bookmarks endpoints."""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db, SessionLocal
from ..models import Annotation, AnnotationType, Content, User
from ..schemas import (
    AnnotationCreate, AnnotationUpdate, AnnotationRead
)
from ..security import get_current_user

router = APIRouter(prefix="/api/annotations", tags=["annotations"])


# ============================================================================
# CREATE ANNOTATIONS
# ============================================================================

@router.post("", response_model=AnnotationRead, status_code=status.HTTP_201_CREATED)
async def create_annotation(
    annotation: AnnotationCreate,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new annotation/bookmark on a resource.
    
    Annotation Types:
    - bookmark: Save a resource for later
    - highlight: Highlight important text in a resource
    - note: Add a note/comment to a resource
    - tag: Tag a resource with custom labels
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Get authenticated user
        user = db.query(User).filter(User.email == current_user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate resource_id
        if annotation.resource_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid resource ID")
        
        # Verify resource exists
        resource = db.query(Content).filter(Content.id == annotation.resource_id).first()
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        # Check if annotation already exists (for bookmarks)
        if annotation.annotation_type == AnnotationType.BOOKMARK:
            existing = db.query(Annotation).filter(
                Annotation.user_id == user.id,
                Annotation.resource_id == annotation.resource_id,
                Annotation.annotation_type == AnnotationType.BOOKMARK
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Resource already bookmarked"
                )
        
        # Create annotation
        db_annotation = Annotation(
            user_id=user.id,
            resource_id=annotation.resource_id,
            annotation_type=annotation.annotation_type,
            highlighted_text=annotation.highlighted_text[:5000] if annotation.highlighted_text else None,
            content=annotation.content[:10000] if annotation.content else None,
            position=annotation.position,
            is_public=annotation.is_public or False,
            created_at=datetime.utcnow()
        )
        
        db.add(db_annotation)
        db.commit()
        db.refresh(db_annotation)
        
        logger.info(f"Annotation created: {db_annotation.id} by user {user.id}")
        return db_annotation
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating annotation: {e}")
        raise HTTPException(status_code=500, detail="Failed to create annotation")


# ============================================================================
# READ ANNOTATIONS
# ============================================================================

@router.get("", response_model=List[AnnotationRead])
async def list_user_annotations(
    annotation_type: Optional[AnnotationType] = Query(None),
    resource_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all annotations for the current user.
    
    Query Parameters:
    - annotation_type: Filter by type (bookmark, highlight, note, tag)
    - resource_id: Filter by resource
    - skip: Pagination offset
    - limit: Pagination limit
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        user = db.query(User).filter(User.email == current_user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        query = db.query(Annotation).filter(Annotation.user_id == user.id)
        
        # Apply filters
        if annotation_type:
            query = query.filter(Annotation.annotation_type == annotation_type)
        
        if resource_id:
            if resource_id <= 0:
                raise HTTPException(status_code=400, detail="Invalid resource ID")
            query = query.filter(Annotation.resource_id == resource_id)
        
        annotations = query\
            .order_by(Annotation.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        return annotations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing annotations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve annotations")


@router.get("/{annotation_id}", response_model=AnnotationRead)
async def get_annotation(
    annotation_id: int,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific annotation."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    # Check ownership or public
    if annotation.user_id != user.id and not annotation.is_public:
        raise HTTPException(status_code=403, detail="Not authorized to view this annotation")
    
    return annotation


@router.get("/resource/{resource_id}/bookmarks", response_model=List[AnnotationRead])
async def get_resource_bookmarks(
    resource_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all public bookmarks for a resource.
    Useful for community knowledge curation.
    """
    # Verify resource exists
    resource = db.query(Content).filter(Content.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    bookmarks = db.query(Annotation)\
        .filter(
            Annotation.resource_id == resource_id,
            Annotation.annotation_type == AnnotationType.BOOKMARK,
            Annotation.is_public == True
        )\
        .order_by(Annotation.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return bookmarks


@router.get("/resource/{resource_id}/highlights", response_model=List[AnnotationRead])
async def get_resource_highlights(
    resource_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all public highlights for a resource.
    Community-curated important passages.
    """
    resource = db.query(Content).filter(Content.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    highlights = db.query(Annotation)\
        .filter(
            Annotation.resource_id == resource_id,
            Annotation.annotation_type == AnnotationType.HIGHLIGHT,
            Annotation.is_public == True
        )\
        .order_by(Annotation.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return highlights


# ============================================================================
# UPDATE ANNOTATIONS
# ============================================================================

@router.put("/{annotation_id}", response_model=AnnotationRead)
async def update_annotation(
    annotation_id: int,
    annotation_update: AnnotationUpdate,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an annotation."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    # Check ownership
    if annotation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this annotation")
    
    # Update fields
    if annotation_update.content is not None:
        annotation.content = annotation_update.content
    
    if annotation_update.highlighted_text is not None:
        annotation.highlighted_text = annotation_update.highlighted_text
    
    if annotation_update.position is not None:
        annotation.position = annotation_update.position
    
    if annotation_update.is_public is not None:
        annotation.is_public = annotation_update.is_public
    
    annotation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(annotation)
    
    return annotation


# ============================================================================
# DELETE ANNOTATIONS
# ============================================================================

@router.delete("/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_annotation(
    annotation_id: int,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an annotation."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")
    
    # Check ownership
    if annotation.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this annotation")
    
    db.delete(annotation)
    db.commit()
    
    return None


@router.delete("/resource/{resource_id}/bookmarks", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bookmark(
    resource_id: int,
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove all bookmarks (user's bookmark only) for a resource."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    annotation = db.query(Annotation).filter(
        Annotation.user_id == user.id,
        Annotation.resource_id == resource_id,
        Annotation.annotation_type == AnnotationType.BOOKMARK
    ).first()
    
    if annotation:
        db.delete(annotation)
        db.commit()
    
    return None


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

@router.post("/batch", response_model=List[AnnotationRead])
async def batch_create_annotations(
    annotations: List[AnnotationCreate],
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create multiple annotations in one request.
    Useful for bulk bookmarking or highlighting.
    """
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    created = []
    
    for ann_data in annotations:
        # Verify resource exists
        resource = db.query(Content).filter(Content.id == ann_data.resource_id).first()
        if not resource:
            continue
        
        db_annotation = Annotation(
            user_id=user.id,
            resource_id=ann_data.resource_id,
            annotation_type=ann_data.annotation_type,
            highlighted_text=ann_data.highlighted_text,
            content=ann_data.content,
            position=ann_data.position,
            is_public=ann_data.is_public or False,
            created_at=datetime.utcnow()
        )
        
        db.add(db_annotation)
        created.append(db_annotation)
    
    db.commit()
    for ann in created:
        db.refresh(ann)
    
    return created


# ============================================================================
# STATISTICS
# ============================================================================

@router.get("/stats/summary", response_model=dict)
async def get_annotation_stats(
    current_user_email: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get annotation statistics for current user."""
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    bookmarks = db.query(Annotation).filter(
        Annotation.user_id == user.id,
        Annotation.annotation_type == AnnotationType.BOOKMARK
    ).count()
    
    highlights = db.query(Annotation).filter(
        Annotation.user_id == user.id,
        Annotation.annotation_type == AnnotationType.HIGHLIGHT
    ).count()
    
    notes = db.query(Annotation).filter(
        Annotation.user_id == user.id,
        Annotation.annotation_type == AnnotationType.NOTE
    ).count()
    
    tags = db.query(Annotation).filter(
        Annotation.user_id == user.id,
        Annotation.annotation_type == AnnotationType.TAG
    ).count()
    
    return {
        "bookmarks": bookmarks,
        "highlights": highlights,
        "notes": notes,
        "tags": tags,
        "total": bookmarks + highlights + notes + tags
    }
