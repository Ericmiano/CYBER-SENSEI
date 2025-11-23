from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas.user import UserResponse, UserCreate
from ..engines.progress import ProgressTracker

router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter_by(username=payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(
        username=payload.username,
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