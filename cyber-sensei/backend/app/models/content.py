from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, DateTime
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from ..database import Base

# Association table for many-to-many relationship between projects and topics
project_topics = Table(
    'project_topics',
    Base.metadata,
    Column('project_id', ForeignKey('projects.id'), primary_key=True),
    Column('topic_id', ForeignKey('topics.id'), primary_key=True)
)

class Content(Base):
    """Base content/resource model for learning materials."""
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(String(50), nullable=False)  # video, document, text, exercise, etc.
    url = Column(String, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    topic = relationship("Topic", back_populates="resources")
    annotations = relationship("Annotation", back_populates="resource", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Content(id={self.id}, title={self.title}, type={self.content_type})>"

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    difficulty = Column(String, default="beginner")
    icon = Column(String, nullable=True)
    color = Column(String, nullable=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    topics = relationship("Topic", back_populates="module")
    enrolled_users = relationship("UserModuleEnrollment", back_populates="module", cascade="all, delete-orphan")

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=True)
    name = Column(String, nullable=True)
    description = Column(Text)
    content = Column(Text) # Markdown-formatted learning content
    difficulty = Column(String, default="beginner")
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # Backwards-compatible column names used in earlier tests/code
    # Make `title` nullable for older tests that set `name` instead of `title`.
    title = Column(String, nullable=True)
    difficulty_level = Column(String, default="beginner")

    module = relationship("Module", back_populates="topics")
    projects = relationship("Project", secondary=project_topics, back_populates="topics")
    # Keep both legacy quiz model relationship and new question model
    quiz_questions = relationship("QuizQuestion", back_populates="topic", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="topic", cascade="all, delete-orphan")
    resources = relationship("Content", back_populates="topic", cascade="all, delete-orphan")

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    passing_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=True)
    text = Column(Text, nullable=False)
    question_type = Column(String, default="multiple_choice")
    difficulty_level = Column(String, default="beginner")
    options = Column(JSON, nullable=True)
    correct_answer = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    topic = relationship("Topic", back_populates="questions")
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    objective = Column(Text, nullable=False)
    setup_instructions = Column(Text) # Markdown
    guided_steps = Column(Text) # JSON string
    validation_script = Column(Text) # Python script for auto-grading
    difficulty_level = Column(String, default="beginner")
    topics = relationship("Topic", secondary=project_topics, back_populates="projects")

class UserModuleEnrollment(Base):
    __tablename__ = "user_module_enrollments"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completion_percentage = Column(Integer, default=0)
    status = Column(String, default="in_progress")  # in_progress, completed, dropped
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    module = relationship("Module", back_populates="enrolled_users")