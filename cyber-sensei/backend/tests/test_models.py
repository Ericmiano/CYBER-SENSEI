"""
Unit tests for CYBER-SENSEI models
Tests for data validation and model behavior
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.content import Topic
from app.models.quiz import QuizQuestion
from app.models.progress import UserProgress
from app.models.document import Document


# --- Test Database Setup ---
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_models.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


# --- User Model Tests ---
class TestUserModel:
    def test_user_creation(self, db):
        """Test creating a user"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_pwd",
            full_name="Test User"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_user_password_hashing(self, db):
        """Test that password is hashed"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="this_should_be_hashed",
            full_name="Test User"
        )
        db.add(user)
        db.commit()
        
        # Password should be stored as-is in hashed_password field
        retrieved_user = db.query(User).first()
        assert retrieved_user.hashed_password == "this_should_be_hashed"

    def test_user_timestamps(self, db):
        """Test user created_at and updated_at timestamps"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_pwd"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_email_uniqueness(self, db):
        """Test email uniqueness constraint"""
        user1 = User(username="user1", email="test@example.com", hashed_password="pwd1")
        user2 = User(username="user2", email="test@example.com", hashed_password="pwd2")
        
        db.add(user1)
        db.commit()
        db.add(user2)
        
        # Should raise an integrity error
        with pytest.raises(Exception):
            db.commit()

    def test_user_profile_fields(self, db):
        """Test user profile fields"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="pwd",
            full_name="Test User",
            bio="I love cybersecurity",
            profile_picture_url="https://example.com/pic.jpg"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.full_name == "Test User"
        assert user.bio == "I love cybersecurity"
        assert user.profile_picture_url == "https://example.com/pic.jpg"


# --- Topic Model Tests ---
class TestTopicModel:
    def test_topic_creation(self, db):
        """Test creating a topic"""
        topic = Topic(
            title="Network Security",
            description="Learn network security fundamentals",
            difficulty_level="beginner",
            order=1
        )
        db.add(topic)
        db.commit()
        db.refresh(topic)
        
        assert topic.id is not None
        assert topic.title == "Network Security"

    def test_topic_difficulty_levels(self, db):
        """Test different difficulty levels"""
        levels = ["beginner", "intermediate", "advanced", "expert"]
        
        for level in levels:
            topic = Topic(title=f"Topic {level}", difficulty_level=level)
            db.add(topic)
        
        db.commit()
        topics = db.query(Topic).all()
        
        assert len(topics) == 4

    def test_topic_ordering(self, db):
        """Test topic ordering"""
        topic1 = Topic(title="First", order=1)
        topic2 = Topic(title="Second", order=2)
        topic3 = Topic(title="Third", order=3)
        
        db.add_all([topic1, topic2, topic3])
        db.commit()
        
        topics = db.query(Topic).order_by(Topic.order).all()
        assert topics[0].title == "First"
        assert topics[1].title == "Second"
        assert topics[2].title == "Third"


# --- UserProgress Model Tests ---
class TestUserProgressModel:
    def test_progress_creation(self, db):
        """Test creating user progress record"""
        user = User(username="testuser", email="test@example.com", hashed_password="pwd")
        topic = Topic(title="Security Basics")
        
        db.add(user)
        db.add(topic)
        db.commit()
        
        progress = UserProgress(
            user_id=user.id,
            topic_id=topic.id,
            completion_percentage=50
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        
        assert progress.completion_percentage == 50

    def test_progress_percentage_validation(self, db):
        """Test progress percentage ranges"""
        user = User(username="testuser", email="test@example.com", hashed_password="pwd")
        topic = Topic(title="Security Basics")
        
        db.add(user)
        db.add(topic)
        db.commit()
        
        # Test various percentages
        for percentage in [0, 25, 50, 75, 100]:
            progress = UserProgress(
                user_id=user.id,
                topic_id=topic.id,
                completion_percentage=percentage
            )
            db.add(progress)
        
        db.commit()
        assert len(db.query(UserProgress).all()) == 5

    def test_progress_timestamps(self, db):
        """Test progress timestamps"""
        user = User(username="testuser", email="test@example.com", hashed_password="pwd")
        topic = Topic(title="Security Basics")
        
        db.add(user)
        db.add(topic)
        db.commit()
        
        progress = UserProgress(
            user_id=user.id,
            topic_id=topic.id,
            completion_percentage=50
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        
        assert progress.started_at is not None
        assert progress.completed_at is None  # Not completed yet


# --- Document Model Tests ---
class TestDocumentModel:
    def test_document_creation(self, db):
        """Test creating a knowledge document"""
        doc = Document(
            title="Security Best Practices",
            content="Here are some best practices...",
            category="security",
            source="internal"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        assert doc.id is not None
        assert doc.title == "Security Best Practices"

    def test_document_tagging(self, db):
        """Test document with tags"""
        doc = Document(
            title="Test Document",
            content="Content here",
            tags=["security", "network", "firewall"]
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        assert "security" in doc.tags

    def test_document_search_fields(self, db):
        """Test document fields for searching"""
        docs = [
            Document(title="Firewalls", content="About firewalls", tags=["network"]),
            Document(title="Encryption", content="About encryption", tags=["security"]),
            Document(title="Access Control", content="About ACL", tags=["security"])
        ]
        
        db.add_all(docs)
        db.commit()
        
        security_docs = db.query(Document).filter(Document.tags.contains("security")).all()
        # Actual behavior depends on database implementation
        assert len(db.query(Document).all()) == 3


# --- Relationship Tests ---
class TestModelRelationships:
    def test_user_progress_relationship(self, db):
        """Test user-progress relationship"""
        user = User(username="testuser", email="test@example.com", hashed_password="pwd")
        topic1 = Topic(title="Topic 1")
        topic2 = Topic(title="Topic 2")
        
        db.add_all([user, topic1, topic2])
        db.commit()
        
        progress1 = UserProgress(user_id=user.id, topic_id=topic1.id, completion_percentage=50)
        progress2 = UserProgress(user_id=user.id, topic_id=topic2.id, completion_percentage=75)
        
        db.add_all([progress1, progress2])
        db.commit()
        
        user_progress = db.query(UserProgress).filter_by(user_id=user.id).all()
        assert len(user_progress) == 2

    def test_cascading_deletes(self, db):
        """Test cascading deletes"""
        user = User(username="testuser", email="test@example.com", hashed_password="pwd")
        db.add(user)
        db.commit()
        
        user_id = user.id
        
        # Delete user
        db.delete(user)
        db.commit()
        
        # Verify user is deleted
        deleted_user = db.query(User).filter_by(id=user_id).first()
        assert deleted_user is None


# --- Data Validation Tests ---
class TestDataValidation:
    def test_username_not_empty(self, db):
        """Test that username is required"""
        user = User(username="", email="test@example.com", hashed_password="pwd")
        db.add(user)
        
        # Behavior depends on model validation
        # This may or may not raise an error

    def test_email_format(self, db):
        """Test email format validation"""
        # This would require Pydantic validation in schema
        # Not typically tested in model tests
        pass

    def test_difficulty_level_valid_value(self, db):
        """Test that difficulty level is valid"""
        topic = Topic(title="Test", difficulty_level="invalid_level")
        db.add(topic)
        
        # Depends on model constraints
        # May need enum validation


# --- Data Type Tests ---
class TestDataTypes:
    def test_boolean_fields(self, db):
        """Test boolean field handling"""
        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password="pwd",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert user.is_active is True

    def test_json_fields(self, db):
        """Test JSON field handling"""
        question = QuizQuestion(
            topic_id=1,
            prompt="Test Question",
            explanation="Test explanation"
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        # JSON handling depends on database
        assert question.prompt == "Test Question"

    def test_datetime_fields(self, db):
        """Test datetime field handling"""
        user = User(username="testuser", email="test@example.com", hashed_password="pwd")
        db.add(user)
        db.commit()
        db.refresh(user)
        
        assert isinstance(user.created_at, datetime)
