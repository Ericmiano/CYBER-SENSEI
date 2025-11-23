# backend/app/engines/curriculum.py
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from ..models.progress import UserProgress
from ..models.user import User
from ..models.content import Topic, Project

class CurriculumEngine:
    def __init__(self, db: Session):
        self.db = db

    def get_next_step(self, username: str) -> dict:
        """Determines the next learning step for the user."""
        user = self.db.query(User).filter_by(username=username).first()
        if not user: return {"type": "error", "message": "User not found."}

        # 1. Check for due reviews (Spaced Repetition)
        due_review = self.db.query(UserProgress, Topic).join(Topic).filter(
            UserProgress.user_id == user.id,
            UserProgress.next_review_date <= datetime.utcnow(),
            UserProgress.status.in_(["in_progress", "mastered"])
        ).order_by(UserProgress.next_review_date).first()

        if due_review:
            progress, topic = due_review
            return {
                "type": "review",
                "message": f"Time for a review! Let's revisit '{topic.name}'.",
                "topic_id": topic.id,
                "topic_name": topic.name
            }

        # 2. Suggest the next new topic
        next_topic = self.db.query(Topic).filter(
            ~Topic.id.in_(
                self.db.query(UserProgress.topic_id).filter(UserProgress.user_id == user.id)
            )
        ).order_by(Topic.id).first()
        
        if next_topic:
            project = next_topic.projects[0] if next_topic.projects else None
            return {
                "type": "new",
                "message": f"Let's start a new topic: '{next_topic.name}'.",
                "topic_id": next_topic.id,
                "topic_name": next_topic.name,
                "project_title": project.title if project else None
            }

        # 3. All caught up
        return {"type": "complete", "message": "You're all caught up! Great work."}