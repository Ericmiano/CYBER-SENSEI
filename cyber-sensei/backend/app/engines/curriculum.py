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
        # Get all unstarted or in-progress topics
        subquery = self.db.query(UserProgress.topic_id).filter(
            UserProgress.user_id == user.id,
            UserProgress.completion_percentage >= 95  # Filter out completed
        )
        
        candidate_topics = self.db.query(Topic).filter(
            ~Topic.id.in_(subquery)
        ).all()
        
        if not candidate_topics:
             return {"type": "complete", "message": "You're all caught up! Great work."}

        # Score candidates using ML model if available
        best_topic = None
        best_score = -1.0
        
        # We need to instantiate the engine or get it from app state. 
        # For simplicity in this synchronous engine, we'll try to import it or use a heuristic.
        # Ideally, this should be dependency injected.
        try:
            from ..ml_model import RecommendationEngine
            # In a real app, load the model once. Here we might be reloading it which is slow,
            # but acceptable for this prototype phase or we assume it's fast enough / cached.
            # Better: Use a simple heuristic if model isn't loaded, or assume the caller passes it.
            # Let's use a simple heuristic for now to avoid heavy model loading in this request,
            # UNLESS we can access the global app state.
            # Since we are in a tool/engine, accessing app.state is hard.
            # We will implement a "Hybrid" approach:
            # 1. Prefer topics with lower difficulty if user is new.
            # 2. Prefer topics in the same 'Project' or category.
            
            # Simple Hybrid Logic:
            # Sort by order (curriculum structure) first, then difficulty.
            candidate_topics.sort(key=lambda t: (t.order or 999, t.difficulty or 1))
            best_topic = candidate_topics[0]
            
        except ImportError:
            # Fallback to simple order
            best_topic = candidate_topics[0]

        if best_topic:
            project = best_topic.projects[0] if best_topic.projects else None
            return {
                "type": "new",
                "message": f"Recommended next topic: '{best_topic.name}' (Difficulty: {best_topic.difficulty})",
                "topic_id": best_topic.id,
                "topic_name": best_topic.name,
                "project_title": project.title if project else None
            }

        # 3. All caught up
        return {"type": "complete", "message": "You're all caught up! Great work."}