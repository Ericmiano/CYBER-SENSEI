from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.learning import (
    LearningStepResponse,
    QuizPayload,
    QuizSubmission,
    TopicContentResponse,
)
from ..engines.curriculum import CurriculumEngine
from ..engines.progress import ProgressTracker
from ..engines.quiz import QuizEngine
from ..models import Topic, User, UserProgress

router = APIRouter(prefix="/api/learning", tags=["learning"])


@router.get("/{username}/next-step", response_model=LearningStepResponse)
def get_next_step(username: str, db: Session = Depends(get_db)):
    """API endpoint to get the user's next learning step."""
    engine = CurriculumEngine(db)
    step = engine.get_next_step(username)
    return LearningStepResponse(**step)


@router.post("/{username}/submit-quiz")
def submit_quiz(username: str, submission: QuizSubmission, db: Session = Depends(get_db)):
    """Endpoint to submit a quiz and update mastery via BKT."""
    tracker = ProgressTracker(db)
    quiz_engine = QuizEngine(db)
    user = db.query(User).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        correct, total = quiz_engine.grade_submission(submission.topic_id, submission.answers)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    final_mastery = tracker.update_mastery(user.id, submission.topic_id, correct == total)

    return {
        "message": "Quiz submitted!",
        "correct": correct,
        "total": total,
        "final_mastery": f"{final_mastery:.0%}",
    }


@router.get("/topic/{topic_id}/quiz", response_model=QuizPayload)
def get_topic_quiz(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    quiz_engine = QuizEngine(db)
    try:
        questions = quiz_engine.get_quiz(topic_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "topic_id": topic.id,
        "topic_name": topic.name,
        "question_count": len(questions),
        "questions": questions,
    }


@router.get("/topic/{topic_id}", response_model=TopicContentResponse)
def get_topic_content(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    return TopicContentResponse(
        id=topic.id,
        name=topic.name,
        description=topic.description,
        content=topic.content,
        module_name=topic.module.name if topic.module else None,
        related_projects=[project.title for project in topic.projects],
    )


@router.post("/{username}/topic/{topic_id}/complete")
def mark_topic_complete(username: str, topic_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username).first()
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
        progress = UserProgress(user_id=user.id, topic_id=topic_id)
        db.add(progress)

    progress.status = "mastered"
    progress.mastery_probability = 1.0
    progress.last_accessed_at = datetime.utcnow()
    progress.next_review_date = datetime.utcnow() + timedelta(days=7)

    db.commit()
    return {"message": f"Topic '{topic.name}' marked as complete."}