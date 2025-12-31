from datetime import datetime, timedelta
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.learning import (
    LearningStepResponse,
    QuizPayload,
    QuizSubmission,
    TopicContentResponse,
    QuizResultResponse,
)
from ..engines.curriculum import CurriculumEngine
from ..engines.progress import ProgressTracker
from ..engines.quiz import QuizEngine
from ..models import Topic, User, UserProgress

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/{username}/next-step", response_model=LearningStepResponse)
def get_next_step(username: str, db: Session = Depends(get_db)):
    """API endpoint to get the user's next learning step."""
    if not username or len(username.strip()) == 0:
        raise HTTPException(status_code=400, detail="Username is required")
    
    try:
        engine = CurriculumEngine(db)
        step = engine.get_next_step(username.strip())
        
        if step.get("type") == "error":
            raise HTTPException(status_code=404, detail=step.get("message", "User not found"))
        
        return LearningStepResponse(**step)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting next step for {username}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get next learning step")


@router.post("/{username}/submit-quiz", response_model=QuizResultResponse)
def submit_quiz(username: str, submission: QuizSubmission, db: Session = Depends(get_db)):
    """Endpoint to submit a quiz and update mastery via BKT."""
    if not username or len(username.strip()) == 0:
        raise HTTPException(status_code=400, detail="Username is required")
    
    if not submission.topic_id or submission.topic_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid topic_id")
    
    if not submission.answers or len(submission.answers) == 0:
        raise HTTPException(status_code=400, detail="Answers are required")
    
    try:
        tracker = ProgressTracker(db)
        quiz_engine = QuizEngine(db)
        user = db.query(User).filter_by(username=username.strip()).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Validate topic exists
        topic = db.query(Topic).filter(Topic.id == submission.topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        correct, total = quiz_engine.grade_submission(submission.topic_id, submission.answers)
        
        if total == 0:
            raise HTTPException(status_code=400, detail="No valid questions found for this topic")

        final_mastery = tracker.update_mastery(user.id, submission.topic_id, correct == total)

        return {
            "message": "Quiz submitted!",
            "correct": correct,
            "total": total,
            "final_mastery": f"{final_mastery:.0%}",
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as e:
        logger.error(f"Error submitting quiz for {username}: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit quiz")


@router.get("/topic/{topic_id}/quiz", response_model=QuizPayload)
def get_topic_quiz(topic_id: int, db: Session = Depends(get_db)):
    """Get quiz questions for a topic."""
    if topic_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid topic ID")
    
    try:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        quiz_engine = QuizEngine(db)
        try:
            questions = quiz_engine.get_quiz(topic_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        
        if not questions or len(questions) == 0:
            raise HTTPException(
                status_code=404,
                detail="No quiz questions available for this topic"
            )

        return {
            "topic_id": topic.id,
            "topic_name": topic.name or f"Topic {topic_id}",
            "question_count": len(questions),
            "questions": questions,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting quiz for topic {topic_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve quiz")


@router.get("/topic/{topic_id}", response_model=TopicContentResponse)
def get_topic_content(topic_id: int, db: Session = Depends(get_db)):
    """Get content for a specific topic."""
    if topic_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid topic ID")
    
    try:
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        return TopicContentResponse(
            id=topic.id,
            name=topic.name or f"Topic {topic_id}",
            description=topic.description or "",
            content=topic.content or "",
            module_name=topic.module.name if topic.module else None,
            related_projects=[project.title for project in topic.projects] if topic.projects else [],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting topic content for {topic_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve topic content")


@router.post("/{username}/topic/{topic_id}/complete")
def mark_topic_complete(username: str, topic_id: int, db: Session = Depends(get_db)):
    """Mark a topic as complete for a user."""
    if not username or len(username.strip()) == 0:
        raise HTTPException(status_code=400, detail="Username is required")
    
    if topic_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid topic ID")
    
    try:
        user = db.query(User).filter_by(username=username.strip()).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        topic = db.query(Topic).filter_by(id=topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found")

        progress = (
            db.query(UserProgress)
            .filter(UserProgress.user_id == user.id, UserProgress.topic_id == topic_id)
            .first()
        )
        if not progress:
            progress = UserProgress(
                user_id=user.id,
                topic_id=topic_id,
                status="mastered",
                mastery_probability=1.0,
            )
            db.add(progress)
        else:
            progress.status = "mastered"
            progress.mastery_probability = 1.0

        progress.last_accessed_at = datetime.utcnow()
        progress.next_review_date = datetime.utcnow() + timedelta(days=7)

        db.commit()
        logger.info(f"Topic {topic_id} marked complete for user {username}")
        return {"message": f"Topic '{topic.name or f'Topic {topic_id}'}' marked as complete."}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error marking topic complete: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark topic as complete")