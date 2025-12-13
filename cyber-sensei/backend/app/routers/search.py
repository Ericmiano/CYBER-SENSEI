"""Search and advanced filtering endpoints."""

from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Module, Topic, QuizQuestion, UserProgress, User, Content
from ..schemas import ModuleRead, TopicRead, ResourceRead, QuizQuestionRead

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/modules", response_model=List[ModuleRead])
async def search_modules(
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search modules by name or description."""
    search_term = f"%{q}%"
    modules = db.query(Module).filter(
        or_(
            Module.name.ilike(search_term),
            Module.description.ilike(search_term)
        )
    ).offset(skip).limit(limit).all()
    return modules


@router.get("/topics", response_model=List[TopicRead])
async def search_topics(
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search topics by name or description."""
    search_term = f"%{q}%"
    topics = db.query(Topic).filter(
        or_(
            Topic.name.ilike(search_term),
            Topic.description.ilike(search_term)
        )
    ).offset(skip).limit(limit).all()
    return topics


@router.get("/questions", response_model=List[QuizQuestionRead])
async def search_questions(
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search quiz questions by text."""
    search_term = f"%{q}%"
    questions = db.query(QuizQuestion).filter(
        QuizQuestion.question_text.ilike(search_term)
    ).offset(skip).limit(limit).all()
    return questions


@router.get("/global")
async def global_search(
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(5, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Global search across all entities."""
    search_term = f"%{q}%"
    
    modules = db.query(Module).filter(
        or_(Module.name.ilike(search_term), Module.description.ilike(search_term))
    ).limit(limit).all()
    
    topics = db.query(Topic).filter(
        or_(Topic.name.ilike(search_term), Topic.description.ilike(search_term))
    ).limit(limit).all()
    
    resources = db.query(Content).filter(
        or_(Content.title.ilike(search_term), Content.description.ilike(search_term))
    ).limit(limit).all()
    
    questions = db.query(QuizQuestion).filter(
        QuizQuestion.question_text.ilike(search_term)
    ).limit(limit).all()
    
    return {
        "query": q,
        "modules": modules,
        "topics": topics,
        "resources": resources,
        "questions": questions
    }
