from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    skill_level = Column(String, default="beginner")
    learning_style = Column(String, default="mixed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())