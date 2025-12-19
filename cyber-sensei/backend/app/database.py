# backend/app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Get the database URL from environment variable or use a default
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/cyber_sensei.db")

# Create the SQLAlchemy engine
# check_same_thread is only needed for SQLite
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for our models to inherit from
Base = declarative_base()

# Dependency to get a DB session in our API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add this function to backend/app/database.py

def create_tables():
    """Creates all database tables defined in the models."""
    from .models import (  # noqa: F401
        User,
        Module,
        Topic,
        Project,
        UserProgress,
        project_topics,
        Content,
        UserModuleEnrollment,
        KnowledgeDocument,
        Document,
        QuizQuestion,
        QuizOption,
        Annotation,
    )

    Base.metadata.create_all(bind=engine)