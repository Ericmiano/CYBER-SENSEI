from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy.ext.hybrid import hybrid_property

# This table implements our BKT engine's data model
class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    
    # BKT Core Fields
    mastery_probability = Column(Float, default=0.2) # p_k - knowledge state
    slip_probability = Column(Float, default=0.1) # p_s - probability of slip
    guess_probability = Column(Float, default=0.25) # p_g - probability of guess
    learn_probability = Column(Float, default=0.1) # p_l - probability of learning
    
    # Tracking Fields
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    status = Column(String, default="not_started") # not_started, in_progress, mastered
    
    # Spaced Repetition Fields
    next_review_date = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Completion tracking (percentage 0.0 - 100.0)
    completion_percentage = Column(Float, default=0.0)

    # Relationships
    user = relationship("User", back_populates="progress")
    topic = relationship("Topic", backref="progress")

    @hybrid_property
    def computed_completion_percentage(self):
        """Return the stored completion_percentage if set; otherwise compute from attempts."""
        try:
            if self.total_attempts and self.total_attempts > 0:
                return (float(self.correct_attempts) / float(self.total_attempts)) * 100.0
        except Exception:
            pass
        return float(self.completion_percentage or 0.0)