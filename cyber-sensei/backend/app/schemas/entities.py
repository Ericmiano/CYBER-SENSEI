"""
Enhanced Pydantic schemas for all Cyber-Sensei entities with complete validation.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class DifficultyEnum(str, Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
    expert = "expert"


class ResourceTypeEnum(str, Enum):
    video = "video"
    article = "article"
    pdf = "pdf"
    interactive = "interactive"
    code_snippet = "code_snippet"
    challenge = "challenge"


class ProjectStatusEnum(str, Enum):
    planning = "planning"
    in_progress = "in_progress"
    completed = "completed"
    on_hold = "on_hold"


# ==================== MODULE SCHEMAS ====================

class ModuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=2000)
    icon: Optional[str] = None
    color: Optional[str] = Field(default="#3498db", pattern="^#[0-9A-Fa-f]{6}$")
    
    @validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Module name cannot be empty")
        return v.strip()


class ModuleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    icon: Optional[str] = None
    color: Optional[str] = None


class ModuleRead(BaseModel):
    id: int
    name: str
    description: str
    icon: Optional[str]
    color: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== TOPIC SCHEMAS ====================

class TopicCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=2000)
    module_id: int
    order: int = Field(default=0, ge=0)
    difficulty: DifficultyEnum = DifficultyEnum.intermediate
    
    @validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Topic name cannot be empty")
        return v.strip()


class TopicUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    order: Optional[int] = None
    difficulty: Optional[DifficultyEnum] = None


class TopicRead(BaseModel):
    id: int
    name: str
    description: str
    module_id: int
    order: int
    difficulty: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== RESOURCE SCHEMAS ====================

class ResourceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    resource_type: ResourceTypeEnum
    url: str
    topic_id: int
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    
    @validator("url")
    def validate_url(cls, v):
        if not v.startswith(("http://", "https://", "/")):
            raise ValueError("URL must be valid HTTP/HTTPS or relative path")
        return v


class ResourceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    resource_type: Optional[ResourceTypeEnum] = None
    url: Optional[str] = None


class ResourceRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    resource_type: str
    url: str
    topic_id: int
    uploaded_by: str
    uploaded_at: datetime
    file_size: Optional[int]
    mime_type: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== QUIZ OPTION SCHEMAS ====================

class QuizOptionBase(BaseModel):
    option_key: str = Field(..., min_length=1, max_length=10)
    label: str = Field(..., min_length=1, max_length=1000)
    is_correct: bool


class QuizOptionCreate(QuizOptionBase):
    pass


class QuizOptionRead(QuizOptionBase):
    class Config:
        from_attributes = True


# ==================== QUIZ QUESTION SCHEMAS ====================

class QuizQuestionCreate(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=2000)
    explanation: Optional[str] = Field(None, max_length=3000)
    topic_id: int
    options: List[QuizOptionCreate] = Field(..., min_items=2, max_items=6)
    
    @validator("options")
    def validate_options(cls, v):
        # Ensure at least one correct answer
        if not any(opt.is_correct for opt in v):
            raise ValueError("At least one option must be marked as correct")
        # Ensure unique keys
        keys = [opt.option_key for opt in v]
        if len(keys) != len(set(keys)):
            raise ValueError("Option keys must be unique")
        return v


class QuizQuestionUpdate(BaseModel):
    prompt: Optional[str] = Field(None, min_length=5, max_length=2000)
    explanation: Optional[str] = Field(None, max_length=3000)
    topic_id: Optional[int] = None
    options: Optional[List[QuizOptionCreate]] = None


class QuizQuestionRead(BaseModel):
    id: int
    prompt: str
    explanation: Optional[str]
    topic_id: int
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime]
    options: List[QuizOptionRead]
    
    class Config:
        from_attributes = True


# ==================== PROJECT SCHEMAS ====================

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=3000)
    status: ProjectStatusEnum = ProjectStatusEnum.planning
    
    @validator("name")
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Project name cannot be empty")
        return v.strip()


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, max_length=3000)
    status: Optional[ProjectStatusEnum] = None


class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    owner: str
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== USER PROGRESS SCHEMAS ====================

class UserProgressRead(BaseModel):
    id: int
    user_id: str
    topic_id: int
    completion_percentage: int
    last_accessed: datetime
    
    class Config:
        from_attributes = True


# ==================== USER SCHEMAS ====================

class UserPreferencesBase(BaseModel):
    theme: str = Field(default="light", pattern="^(light|dark)$")
    language: str = Field(default="en")
    notifications_enabled: bool = True
    daily_reminder: Optional[str] = None  # HH:MM format


class UserProfileUpdate(BaseModel):
    bio: Optional[str] = Field(None, max_length=1000)
    preferences: Optional[UserPreferencesBase] = None


class UserProfileRead(BaseModel):
    id: int
    username: str
    email: str
    bio: Optional[str]
    created_at: datetime
    preferences: Optional[UserPreferencesBase]
    
    class Config:
        from_attributes = True


# ==================== BATCH OPERATION SCHEMAS ====================

class BulkDeleteRequest(BaseModel):
    ids: List[int] = Field(..., min_items=1, max_items=100)


class BulkImportRequest(BaseModel):
    data: List[dict]
    dry_run: bool = False
