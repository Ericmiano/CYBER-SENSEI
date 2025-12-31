from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
import logging

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

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with validation."""
    try:
        # Check for existing username (case-insensitive)
        existing_username = db.query(User).filter(
            User.username.ilike(payload.username)
        ).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check for existing email (case-insensitive)
        existing_email = db.query(User).filter(
            User.email.ilike(payload.email)
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create user
        user = User(
            username=payload.username,
            email=payload.email.lower(),  # Normalize email
            full_name=payload.full_name,
            bio=payload.bio,
            profile_picture_url=payload.profile_picture_url,
            hashed_password=hash_password(payload.password),
            skill_level=payload.skill_level,
            learning_style=payload.learning_style,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again."
        )


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token."""
    try:
        # Normalize email (case-insensitive lookup)
        user = db.query(User).filter(
            User.email.ilike(payload.email)
        ).first()
        
        if not user:
            # Don't reveal if user exists - security best practice
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        if not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        logger.info(f"User logged in: {user.username} ({user.email})")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (admin endpoint)."""
    try:
        # Check for existing username (case-insensitive)
        existing = db.query(User).filter(
            User.username.ilike(payload.username)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check for existing email (case-insensitive)
        existing_email = db.query(User).filter(
            User.email.ilike(payload.email)
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user = User(
            username=payload.username,
            email=payload.email.lower(),  # Normalize email
            full_name=payload.full_name,
            bio=payload.bio,
            profile_picture_url=payload.profile_picture_url,
            hashed_password=hash_password(payload.password),
            skill_level=payload.skill_level,
            learning_style=payload.learning_style,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User created: {user.username} ({user.email})")
        return user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user. Please try again."
        )


@router.get("/{username}", response_model=UserResponse)
def get_user(username: str, db: Session = Depends(get_db)):
    """Get user profile by username."""
    if not username or len(username.strip()) == 0:
        raise HTTPException(status_code=400, detail="Username is required")
    
    try:
        user = db.query(User).filter_by(username=username.strip()).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {username}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user")


@router.get("/{username}/dashboard", response_model=dict)
def get_user_dashboard(username: str, db: Session = Depends(get_db)):
    """Gets the dashboard data for a specific user."""
    if not username or len(username.strip()) == 0:
        raise HTTPException(status_code=400, detail="Username is required")
    
    try:
        # Verify user exists first
        user = db.query(User).filter_by(username=username.strip()).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        tracker = ProgressTracker(db)
        dashboard_data = tracker.generate_dashboard_data(username.strip())
        if not dashboard_data:
            # Return empty dashboard if no progress yet
            return {
                "overall": {
                    "total": 0,
                    "mastered": 0,
                    "progress_percentage": 0
                },
                "topics": []
            }
        return dashboard_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard for {username}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")


@router.post("/{user_id}/enroll/{module_id}", response_model=EnrollmentResponse)
def enroll_user_in_module(user_id: int, module_id: int, db: Session = Depends(get_db)):
    """Enroll a user in a module."""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    if module_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid module ID")
    
    try:
        from ..models import Module
        
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        module = db.query(Module).filter_by(id=module_id).first()
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        existing = db.query(UserModuleEnrollment).filter_by(
            user_id=user_id, module_id=module_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already enrolled in this module"
            )
        
        enrollment = UserModuleEnrollment(
            user_id=user_id,
            module_id=module_id,
            status="in_progress",
            completion_percentage=0
        )
        db.add(enrollment)
        db.commit()
        db.refresh(enrollment)
        logger.info(f"User {user_id} enrolled in module {module_id}")
        return enrollment
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error enrolling user {user_id} in module {module_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to enroll user in module")


@router.get("/{user_id}/enrollments", response_model=List[EnrollmentResponse])
def get_user_enrollments(user_id: int, db: Session = Depends(get_db)):
    """Get all module enrollments for a user."""
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    try:
        # Verify user exists
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        enrollments = db.query(UserModuleEnrollment).filter_by(user_id=user_id).all()
        return enrollments
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting enrollments for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve enrollments")


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    """Update user profile."""
    try:
        if user_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate skill_level if provided
        if payload.skill_level is not None:
            valid_levels = ['beginner', 'intermediate', 'advanced', 'expert']
            if payload.skill_level not in valid_levels:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid skill_level. Must be one of: {', '.join(valid_levels)}"
                )
        
        # Validate learning_style if provided
        if payload.learning_style is not None:
            valid_styles = ['visual', 'auditory', 'kinesthetic', 'reading', 'mixed']
            if payload.learning_style not in valid_styles:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid learning_style. Must be one of: {', '.join(valid_styles)}"
                )
        
        # Update fields
        if payload.full_name is not None:
            user.full_name = payload.full_name[:200] if payload.full_name else None
        if payload.bio is not None:
            user.bio = payload.bio[:1000] if payload.bio else None
        if payload.profile_picture_url is not None:
            user.profile_picture_url = payload.profile_picture_url[:500] if payload.profile_picture_url else None
        if payload.skill_level is not None:
            user.skill_level = payload.skill_level
        if payload.learning_style is not None:
            user.learning_style = payload.learning_style
        
        db.commit()
        db.refresh(user)
        logger.info(f"User updated: {user.username} (ID: {user_id})")
        return user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user")