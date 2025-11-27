"""Search and advanced filtering endpoints."""

from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Module, Topic, QuizQuestion, UserProgress, User, Content

router = APIRouter(prefix="/api/search", tags=["search"])


# ============================================================================
# FULL-TEXT SEARCH
# ============================================================================

@router.get("/modules")
async def search_modules(
    q: str = Query(..., min_length=1, max_length=100, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    difficulty: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Search modules by name and description.
    
    Query Parameters:
    - q: Search query (required)
    - skip: Pagination offset
    - limit: Pagination limit
    - difficulty: Filter by difficulty level (beginner, intermediate, advanced)
    """
    query = db.query(Module)
    
    # Full-text search in name and description
    search_term = f"%{q}%"
    query = query.filter(
        or_(
            Module.name.ilike(search_term),
            Module.description.ilike(search_term)
        )
    )
    
    # Filter by difficulty if provided
    if difficulty:
        query = query.filter(Module.difficulty == difficulty)
    
    total_count = query.count()
    results = query.offset(skip).limit(limit).all()
    
    return results


@router.get("/topics")
async def search_topics(
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    module_id: Optional[int] = Query(None),
    difficulty: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Search topics by name and description with optional filtering.
    
    Query Parameters:
    - q: Search query (required)
    - module_id: Filter by module
    - difficulty: Filter by difficulty level
    """
    query = db.query(Topic)
    
    # Full-text search
    search_term = f"%{q}%"
    query = query.filter(
        or_(
            Topic.name.ilike(search_term),
            Topic.description.ilike(search_term)
        )
    )
    
    # Apply filters
    if module_id:
        query = query.filter(Topic.module_id == module_id)
    
    if difficulty:
        query = query.filter(Topic.difficulty == difficulty)
    
    return query.offset(skip).limit(limit).all()


@router.get("/resources")
async def search_resources(
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    content_type: Optional[str] = Query(None),
    topic_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Search learning resources/content.
    
    Query Parameters:
    - q: Search query (required)
    - content_type: Filter by type (video, document, text, exercise)
    - topic_id: Filter by topic
    """
    query = db.query(Content)
    
    # Full-text search
    search_term = f"%{q}%"
    query = query.filter(
        or_(
            Content.title.ilike(search_term),
            Content.description.ilike(search_term)
        )
    )
    
    # Apply filters
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    if topic_id:
        query = query.filter(Content.topic_id == topic_id)
    
    return query.offset(skip).limit(limit).all()


@router.get("/quiz-questions")
async def search_quiz_questions(
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    difficulty: Optional[str] = Query(None),
    topic_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Search quiz questions by text.
    
    Query Parameters:
    - q: Search query (required)
    - difficulty: Filter by difficulty
    - topic_id: Filter by topic
    """
    query = db.query(QuizQuestion)
    
    # Full-text search
    search_term = f"%{q}%"
    query = query.filter(
        or_(
            QuizQuestion.question_text.ilike(search_term)
        )
    )
    
    # Apply filters
    if difficulty:
        query = query.filter(QuizQuestion.difficulty == difficulty)
    
    if topic_id:
        query = query.filter(QuizQuestion.topic_id == topic_id)
    
    return query.offset(skip).limit(limit).all()
    - sort_order: Sort order (asc, desc)
    """
    query = db.query(Module)
    
    # Apply filters
    if name:
        query = query.filter(Module.name.ilike(f"%{name}%"))
    
    if created_after:
        try:
            date = datetime.fromisoformat(created_after)
            query = query.filter(Module.created_at >= date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    if created_before:
        try:
            date = datetime.fromisoformat(created_before)
            query = query.filter(Module.created_at <= date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    # Apply sorting
    if sort_by == "created_at":
        sort_column = Module.created_at
    elif sort_by == "difficulty":
        sort_column = Module.difficulty
    else:
        sort_column = Module.name
    
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    return query.offset(skip).limit(limit).all()


@router.get("/topics/advanced", response_model=List[TopicRead])
async def advanced_search_topics(
    name: Optional[str] = Query(None),
    module_id: Optional[int] = Query(None),
    difficulty: Optional[str] = Query(None),
    has_quiz: Optional[bool] = Query(None),
    sort_by: str = Query("order", pattern="^(name|created_at|difficulty|order)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(SessionLocal)
):
    """Advanced topic search with filtering and sorting."""
    query = db.query(Topic)
    
    # Apply filters
    if name:
        query = query.filter(Topic.name.ilike(f"%{name}%"))
    
    if module_id:
        query = query.filter(Topic.module_id == module_id)
    
    if difficulty:
        query = query.filter(Topic.difficulty == difficulty)
    
    if has_quiz is not None:
        if has_quiz:
            query = query.filter(Topic.quiz_questions.any())
        else:
            query = query.filter(~Topic.quiz_questions.any())
    
    # Apply sorting
    if sort_by == "created_at":
        sort_column = Topic.created_at
    elif sort_by == "difficulty":
        sort_column = Topic.difficulty
    elif sort_by == "order":
        sort_column = Topic.order
    else:
        sort_column = Topic.name
    
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    return query.offset(skip).limit(limit).all()


# ============================================================================
# SORTING ENDPOINTS
# ============================================================================

@router.get("/modules/popular", response_model=List[ModuleRead])
async def get_popular_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(SessionLocal)
):
    """Get most popular modules by number of enrolled users."""
    modules = db.query(Module)\
        .outerjoin(UserProgress)\
        .group_by(Module.id)\
        .order_by(desc(func.count(UserProgress.id)))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return modules


@router.get("/topics/trending", response_model=List[TopicRead])
async def get_trending_topics(
    days: int = Query(7, ge=1, le=90),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(SessionLocal)
):
    """Get trending topics (most activity in last N days)."""
    since = datetime.utcnow() - timedelta(days=days)
    
    topics = db.query(Topic)\
        .outerjoin(UserProgress)\
        .filter(UserProgress.updated_at >= since)\
        .group_by(Topic.id)\
        .order_by(desc(func.count(UserProgress.id)))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return topics


@router.get("/modules/recent", response_model=List[ModuleRead])
async def get_recent_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(SessionLocal)
):
    """Get most recently created modules."""
    modules = db.query(Module)\
        .order_by(desc(Module.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return modules


# ============================================================================
# FACETED SEARCH (GET AVAILABLE FILTERS)
# ============================================================================

@router.get("/facets/difficulties")
async def get_available_difficulties(
    db: Session = Depends(SessionLocal)
):
    """Get available difficulty levels with counts."""
    results = db.query(
        Topic.difficulty,
        func.count(Topic.id).label("count")
    ).group_by(Topic.difficulty).all()
    
    return {
        "difficulties": [
            {"value": r[0], "count": r[1]} for r in results
        ]
    }


@router.get("/facets/content-types")
async def get_available_content_types(
    db: Session = Depends(SessionLocal)
):
    """Get available content types with counts."""
    results = db.query(
        Content.content_type,
        func.count(Content.id).label("count")
    ).group_by(Content.content_type).all()
    
    return {
        "content_types": [
            {"value": r[0], "count": r[1]} for r in results
        ]
    }


# ============================================================================
# CROSS-ENTITY SEARCH
# ============================================================================

@router.get("/all", response_model=dict)
async def global_search(
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(SessionLocal)
):
    """
    Global search across all entities.
    
    Returns matching modules, topics, resources, and quiz questions.
    """
    search_term = f"%{q}%"
    
    modules = db.query(Module)\
        .filter(or_(Module.name.ilike(search_term), Module.description.ilike(search_term)))\
        .limit(limit).all()
    
    topics = db.query(Topic)\
        .filter(or_(Topic.name.ilike(search_term), Topic.description.ilike(search_term)))\
        .limit(limit).all()
    
    resources = db.query(Content)\
        .filter(or_(Content.title.ilike(search_term), Content.description.ilike(search_term)))\
        .limit(limit).all()
    
    questions = db.query(QuizQuestion)\
        .filter(QuizQuestion.question_text.ilike(search_term))\
        .limit(limit).all()
    
    return {
        "query": q,
        "modules": modules,
        "topics": topics,
        "resources": resources,
        "questions": questions
    }
