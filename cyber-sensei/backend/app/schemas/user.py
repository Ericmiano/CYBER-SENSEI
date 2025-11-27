from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    skill_level: str = "beginner"
    learning_style: str = "mixed"

class UserCreate(UserBase):
    password: str

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