from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$',
                          description="Username must be 3-50 characters, alphanumeric with _ or -")
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=200)
    bio: Optional[str] = Field(None, max_length=1000)
    profile_picture_url: Optional[str] = Field(None, max_length=500)
    skill_level: str = Field(default="beginner", pattern=r'^(beginner|intermediate|advanced|expert)$')
    learning_style: str = Field(default="mixed", pattern=r'^(visual|auditory|kinesthetic|reading|mixed)$')
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        if v.lower() in ['admin', 'root', 'system', 'test', 'null', 'undefined']:
            raise ValueError('Username is reserved')
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128,
                          description="Password must be at least 8 characters")
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    bio: Optional[str]
    profile_picture_url: Optional[str]
    skill_level: str
    learning_style: str

    class Config:
        from_attributes = True # Allows Pydantic to read data from ORM models

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    skill_level: Optional[str] = None
    learning_style: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    module_id: int
    enrolled_at: Optional[datetime]
    completion_percentage: int
    status: str

    class Config:
        from_attributes = True