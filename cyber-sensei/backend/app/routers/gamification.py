from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from ..database import get_db
from ..models.gamification import Badge, UserBadge
from ..models.user import User

router = APIRouter(prefix="/gamification", tags=["gamification"])

class BadgeSchema(BaseModel):
    id: int
    name: str
    description: str
    icon_url: str | None
    awarded_at: datetime | None = None

    class Config:
        from_attributes = True

@router.get("/badges", response_model=List[BadgeSchema])
def get_all_badges(db: Session = Depends(get_db)):
    return db.query(Badge).all()

@router.get("/user/{user_id}/badges", response_model=List[BadgeSchema])
def get_user_badges(user_id: int, db: Session = Depends(get_db)):
    user_badges = db.query(UserBadge).filter(UserBadge.user_id == user_id).all()
    
    result = []
    for ub in user_badges:
        badge_data = BadgeSchema.model_validate(ub.badge)
        badge_data.awarded_at = ub.awarded_at
        result.append(badge_data)
        
    return result

@router.post("/seed-badges")
def seed_badges(db: Session = Depends(get_db)):
    """Seeds initial badges."""
    initial_badges = [
        {"name": "First Step", "description": "Complete your first topic.", "criteria_type": "topic_completion", "criteria_value": 1, "icon_url": "🌱"},
        {"name": "Quiz Master", "description": "Score 100% on a quiz.", "criteria_type": "perfect_quiz", "criteria_value": 1, "icon_url": "🧠"},
        {"name": "Dedicated Learner", "description": "Complete 5 topics.", "criteria_type": "topic_completion", "criteria_value": 5, "icon_url": "📚"},
    ]
    
    created = 0
    for b_data in initial_badges:
        if not db.query(Badge).filter_by(name=b_data["name"]).first():
            badge = Badge(**b_data)
            db.add(badge)
            created += 1
    
    db.commit()
    return {"message": f"Created {created} new badges."}
