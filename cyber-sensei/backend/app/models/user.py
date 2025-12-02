from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    profile_picture_url = Column(String, nullable=True)
    skill_level = Column(String, default="beginner")
    learning_style = Column(String, default="mixed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    annotations = relationship("Annotation", back_populates="user", cascade="all, delete-orphan")
    progress = relationship("UserProgress", back_populates="user")
    enrollments = relationship("UserModuleEnrollment", back_populates="user")
    badges = relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")