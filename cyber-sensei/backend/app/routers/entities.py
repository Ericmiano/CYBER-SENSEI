"""
Complete CRUD endpoints for all Cyber-Sensei entities.

Provides full Create, Read, Update, Delete operations for:
- Modules
- Topics
- Projects
- Quizzes
- Resources
- User Progress
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import SessionLocal
from ..models import (
    Module, Topic, Project, QuizQuestion, Content, UserProgress, User
)
from ..schemas import (
    ModuleCreate, ModuleUpdate, ModuleRead,
    TopicCreate, TopicUpdate, TopicRead,
    ProjectCreate, ProjectUpdate, ProjectRead,
    ResourceCreate, ResourceUpdate, ResourceRead,
    QuizQuestionCreate, QuizQuestionUpdate, QuizQuestionRead,
    UserProgressRead
)
from ..security import get_current_user

router = APIRouter(prefix="/api", tags=["entities"])


# ==================== MODULES ====================

@router.post("/modules", response_model=ModuleRead, status_code=status.HTTP_201_CREATED)
async def create_module(
    module: ModuleCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Create a new learning module."""
    # Check if module with same name already exists
    existing = db.query(Module).filter(Module.name == module.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Module '{module.name}' already exists"
        )
    
    db_module = Module(
        name=module.name,
        description=module.description,
        icon=module.icon,
        color=module.color,
        created_by=current_user,
        created_at=datetime.utcnow()
    )
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module


@router.get("/modules", response_model=List[ModuleRead])
async def list_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(SessionLocal)
):
    """List all modules with pagination."""
    modules = db.query(Module).offset(skip).limit(limit).all()
    return modules


@router.get("/modules/{module_id}", response_model=ModuleRead)
async def get_module(module_id: int, db: Session = Depends(SessionLocal)):
    """Get a specific module by ID."""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


@router.put("/modules/{module_id}", response_model=ModuleRead)
async def update_module(
    module_id: int,
    module_update: ModuleUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Update a module."""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    # Check permission (creator or admin)
    if module.created_by != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to update this module")
    
    update_data = module_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(module, key, value)
    module.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(module)
    return module


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Delete a module (and all associated topics)."""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    if module.created_by != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this module")
    
    # Delete associated topics and questions
    topics = db.query(Topic).filter(Topic.module_id == module_id).all()
    for topic in topics:
        db.query(QuizQuestion).filter(QuizQuestion.topic_id == topic.id).delete()
    db.query(Topic).filter(Topic.module_id == module_id).delete()
    
    db.delete(module)
    db.commit()


# ==================== TOPICS ====================

@router.post("/topics", response_model=TopicRead, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic: TopicCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Create a new topic within a module."""
    # Verify module exists
    module = db.query(Module).filter(Module.id == topic.module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    db_topic = Topic(
        name=topic.name,
        description=topic.description,
        module_id=topic.module_id,
        order=topic.order or 0,
        difficulty=topic.difficulty or "intermediate",
        created_by=current_user,
        created_at=datetime.utcnow()
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic


@router.get("/modules/{module_id}/topics", response_model=List[TopicRead])
async def list_module_topics(
    module_id: int,
    db: Session = Depends(SessionLocal)
):
    """List all topics in a module."""
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    topics = db.query(Topic).filter(Topic.module_id == module_id).order_by(Topic.order).all()
    return topics


@router.get("/topics/{topic_id}", response_model=TopicRead)
async def get_topic(topic_id: int, db: Session = Depends(SessionLocal)):
    """Get a specific topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


@router.put("/topics/{topic_id}", response_model=TopicRead)
async def update_topic(
    topic_id: int,
    topic_update: TopicUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Update a topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    if topic.created_by != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to update this topic")
    
    update_data = topic_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(topic, key, value)
    topic.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(topic)
    return topic


@router.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Delete a topic (and all questions)."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    if topic.created_by != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this topic")
    
    # Delete associated questions
    db.query(QuizQuestion).filter(QuizQuestion.topic_id == topic_id).delete()
    db.delete(topic)
    db.commit()


# ==================== RESOURCES ====================

@router.post("/resources", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
async def create_resource(
    resource: ResourceCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Create a new learning resource."""
    # Verify topic exists
    topic = db.query(Topic).filter(Topic.id == resource.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    db_resource = Resource(
        title=resource.title,
        description=resource.description,
        resource_type=resource.resource_type,
        url=resource.url,
        topic_id=resource.topic_id,
        uploaded_by=current_user,
        uploaded_at=datetime.utcnow(),
        file_size=resource.file_size,
        mime_type=resource.mime_type
    )
    db.add(db_resource)
    db.commit()
    db.refresh(db_resource)
    return db_resource


@router.get("/topics/{topic_id}/resources", response_model=List[ResourceRead])
async def list_topic_resources(topic_id: int, db: Session = Depends(SessionLocal)):
    """List all resources for a topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    resources = db.query(Resource).filter(Resource.topic_id == topic_id).all()
    return resources


@router.get("/resources/{resource_id}", response_model=ResourceRead)
async def get_resource(resource_id: int, db: Session = Depends(SessionLocal)):
    """Get a specific resource."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.put("/resources/{resource_id}", response_model=ResourceRead)
async def update_resource(
    resource_id: int,
    resource_update: ResourceUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Update a resource."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    if resource.uploaded_by != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to update this resource")
    
    update_data = resource_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(resource, key, value)
    
    db.commit()
    db.refresh(resource)
    return resource


@router.delete("/resources/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resource(
    resource_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Delete a resource."""
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    if resource.uploaded_by != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this resource")
    
    db.delete(resource)
    db.commit()


# ==================== QUIZ QUESTIONS ====================

@router.post("/quiz-questions", response_model=QuizQuestionRead, status_code=status.HTTP_201_CREATED)
async def create_quiz_question(
    question: QuizQuestionCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Create a new quiz question."""
    topic = db.query(Topic).filter(Topic.id == question.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    db_question = QuizQuestion(
        prompt=question.prompt,
        explanation=question.explanation,
        topic_id=question.topic_id,
        created_by=current_user,
        created_at=datetime.utcnow()
    )
    
    # Add options
    for opt in question.options:
        db_question.options.append({
            "option_key": opt.option_key,
            "label": opt.label,
            "is_correct": opt.is_correct
        })
    
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


@router.get("/topics/{topic_id}/quiz-questions", response_model=List[QuizQuestionRead])
async def list_topic_questions(topic_id: int, db: Session = Depends(SessionLocal)):
    """List all quiz questions for a topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    questions = db.query(QuizQuestion).filter(QuizQuestion.topic_id == topic_id).all()
    return questions


@router.get("/quiz-questions/{question_id}", response_model=QuizQuestionRead)
async def get_quiz_question(question_id: int, db: Session = Depends(SessionLocal)):
    """Get a specific quiz question."""
    question = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.put("/quiz-questions/{question_id}", response_model=QuizQuestionRead)
async def update_quiz_question(
    question_id: int,
    question_update: QuizQuestionUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Update a quiz question."""
    question = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if question.created_by != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to update this question")
    
    update_data = question_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        if key != "options":
            setattr(question, key, value)
    
    question.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(question)
    return question


@router.delete("/quiz-questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quiz_question(
    question_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Delete a quiz question."""
    question = db.query(QuizQuestion).filter(QuizQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if question.created_by != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this question")
    
    db.delete(question)
    db.commit()


# ==================== PROJECTS ====================

@router.post("/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Create a new project."""
    db_project = Project(
        name=project.name,
        description=project.description,
        owner=current_user,
        created_at=datetime.utcnow(),
        status=project.status or "planning"
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/projects", response_model=List[ProjectRead])
async def list_projects(
    current_user: str = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(SessionLocal)
):
    """List user's projects."""
    projects = db.query(Project).filter(
        Project.owner == current_user
    ).offset(skip).limit(limit).all()
    return projects


@router.get("/projects/{project_id}", response_model=ProjectRead)
async def get_project(
    project_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Get a specific project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to view this project")
    
    return project


@router.put("/projects/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Update a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to update this project")
    
    update_data = project_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)
    project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    return project


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Delete a project."""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner != current_user:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")
    
    db.delete(project)
    db.commit()


# ==================== USER PROGRESS ====================

@router.get("/progress/{topic_id}", response_model=UserProgressRead)
async def get_user_progress(
    topic_id: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Get user's progress on a topic."""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user,
        UserProgress.topic_id == topic_id
    ).first()
    
    if not progress:
        raise HTTPException(status_code=404, detail="No progress found for this topic")
    
    return progress


@router.get("/progress", response_model=List[UserProgressRead])
async def get_all_user_progress(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Get user's progress across all topics."""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user
    ).all()
    return progress


@router.put("/progress/{topic_id}", response_model=UserProgressRead)
async def update_user_progress(
    topic_id: int,
    completion_percentage: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(SessionLocal)
):
    """Update user's progress on a topic."""
    if not 0 <= completion_percentage <= 100:
        raise HTTPException(status_code=400, detail="Completion percentage must be 0-100")
    
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user,
        UserProgress.topic_id == topic_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user,
            topic_id=topic_id,
            completion_percentage=completion_percentage,
            last_accessed=datetime.utcnow()
        )
        db.add(progress)
    else:
        progress.completion_percentage = completion_percentage
        progress.last_accessed = datetime.utcnow()
    
    db.commit()
    db.refresh(progress)
    return progress
