# backend/app/engines/progress.py
import math
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import SessionLocal
from ..models.user import User
from ..models.progress import UserProgress
from ..models.content import Topic
from rich.console import Console
from rich.table import Table
from rich.progress import BarColumn, Progress, TextColumn

# BKT parameters (can be tuned)
BKT_DEFAULTS = {"p_init": 0.2, "p_learn": 0.3, "p_guess": 0.2, "p_slip": 0.1}

class ProgressTracker:
    def __init__(self, db: Session):
        self.db = db

    def update_mastery(self, user_id: int, topic_id: int, is_correct: bool) -> float:
        """Updates mastery using BKT and returns the new probability."""
        progress = self.db.query(UserProgress).filter_by(user_id=user_id, topic_id=topic_id).first()
        if not progress:
            progress = UserProgress(
                user_id=user_id, 
                topic_id=topic_id, 
                mastery_probability=BKT_DEFAULTS['p_init'],
                learn_probability=BKT_DEFAULTS['p_learn'],
                guess_probability=BKT_DEFAULTS['p_guess'],
                slip_probability=BKT_DEFAULTS['p_slip'],
            )
            self.db.add(progress)

        p_known = progress.mastery_probability
        p_slip = progress.slip_probability
        p_guess = progress.guess_probability
        p_learn = progress.learn_probability
        
        # Update attempt tracking
        progress.total_attempts += 1
        if is_correct:
            progress.correct_attempts += 1
            p_observed = (p_known * (1 - p_slip)) + ((1 - p_known) * p_guess)
            p_known_new = (p_known * (1 - p_slip)) / p_observed if p_observed > 0 else p_known
        else:
            p_observed = (p_known * p_slip) + ((1 - p_known) * (1 - p_guess))
            p_known_new = (p_known * p_slip) / p_observed if p_observed > 0 else p_known

        # Apply learning and update
        progress.mastery_probability = p_known_new + (1 - p_known_new) * p_learn
        progress.last_accessed_at = datetime.utcnow()
        
        # Update status and schedule next review
        if progress.mastery_probability >= 0.9:
            progress.status = 'mastered'
            progress.next_review_date = datetime.utcnow() + timedelta(days=7) # Review in a week
        else:
            progress.status = 'in_progress'
            progress.next_review_date = datetime.utcnow() + timedelta(days=2) # Review soon

        self.db.commit()
        return progress.mastery_probability

    def generate_dashboard_data(self, username: str) -> dict:
        """Generates data for the frontend dashboard."""
        user = self.db.query(User).filter_by(username=username).first()
        if not user: return {}

        # Overall Progress
        total_topics = self.db.query(UserProgress).filter_by(user_id=user.id).count()
        mastered_topics = self.db.query(UserProgress).filter_by(user_id=user.id, status='mastered').count()
        
        # Topic Breakdown
        progress_list = self.db.query(UserProgress).outerjoin(Topic).filter(UserProgress.user_id == user.id).all()
        
        dashboard_data = {
            "overall": {
                "total": max(total_topics, 1),  # Avoid division by zero
                "mastered": mastered_topics,
                "progress_percentage": (mastered_topics / max(total_topics, 1) * 100) if total_topics else 0
            },
            "topics": [
                {
                    "name": progress.topic.name if progress.topic else f"Topic {progress.topic_id}",
                    "mastery": f"{progress.mastery_probability * 100:.0f}%",
                    "status": progress.status
                } for progress in progress_list
            ]
        }
        return dashboard_data