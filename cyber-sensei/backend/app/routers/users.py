from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from ..database import get_db
from ..models import User, UserModuleEnrollment
from ..schemas.user import (
    UserResponse,
    UserCreate,
    UserLogin,
    UserUpdate,
    TokenResponse,
    EnrollmentResponse,
)
from ..core.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..engines.progress import ProgressTracker

from ..database import get_db
from ..models import User, UserModuleEnrollment
from ..schemas.user import UserResponse, UserCreate, UserLogin, UserUpdate
from ..core.security import hash_password, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..engines.progress import ProgressTracker

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing_username = db.query(User).filter_by(username=payload.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    existing_email = db.query(User).filter_by(email=payload.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        bio=payload.bio,
        profile_picture_url=payload.profile_picture_url,
        hashed_password=hash_password(payload.password),
        skill_level=payload.skill_level,
        learning_style=payload.learning_style,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user": UserResponse.from_orm(user)}


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(username=payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    existing_email = db.query(User).filter_by(email=payload.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        username=payload.username,
        email=payload.email,
        full_name=payload.full_name,
        bio=payload.bio,
        profile_picture_url=payload.profile_picture_url,
        hashed_password=hash_password(payload.password),
        skill_level=payload.skill_level,
        learning_style=payload.learning_style,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{username}", response_model=UserResponse)
def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{username}/dashboard", response_model=dict)
def get_user_dashboard(username: str, db: Session = Depends(get_db)):
    """Gets the dashboard data for a specific user."""
    tracker = ProgressTracker(db)
    dashboard_data = tracker.generate_dashboard_data(username)
    if not dashboard_data:
        raise HTTPException(status_code=404, detail="User not found")
    return dashboard_data


@router.post("/{user_id}/enroll/{module_id}", response_model=EnrollmentResponse)
def enroll_user_in_module(user_id: int, module_id: int, db: Session = Depends(get_db)):
    """Enroll a user in a module."""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing = db.query(UserModuleEnrollment).filter_by(
        user_id=user_id, module_id=module_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already enrolled in this module")
    
    enrollment = UserModuleEnrollment(user_id=user_id, module_id=module_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.get("/{user_id}/enrollments", response_model=List[EnrollmentResponse])
def get_user_enrollments(user_id: int, db: Session = Depends(get_db)):
    """Get all module enrollments for a user."""
    enrollments = db.query(UserModuleEnrollment).filter_by(user_id=user_id).all()
    return enrollments


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    """Update user profile."""
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if payload.full_name is not None:
        user.full_name = payload.full_name
    if payload.bio is not None:
        user.bio = payload.bio
    if payload.profile_picture_url is not None:
        user.profile_picture_url = payload.profile_picture_url
    if payload.skill_level is not None:
        user.skill_level = payload.skill_level
    if payload.learning_style is not None:
        user.learning_style = payload.learning_style
    
    db.commit()
    db.refresh(user)
    return user