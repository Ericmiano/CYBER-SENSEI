from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from ..database import Base

# Association table for many-to-many relationship between projects and topics
project_topics = Table(
    'project_topics',
    Base.metadata,
    Column('project_id', ForeignKey('projects.id'), primary_key=True),
    Column('topic_id', ForeignKey('topics.id'), primary_key=True)
)

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text)
    topics = relationship("Topic", back_populates="module")

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    content = Column(Text) # Markdown-formatted learning content
    module = relationship("Module", back_populates="topics")
    projects = relationship("Project", secondary=project_topics, back_populates="topics")
    quiz_questions = relationship("QuizQuestion", back_populates="topic", cascade="all, delete-orphan")

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