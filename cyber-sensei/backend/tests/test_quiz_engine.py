"""
Unit tests for the QuizEngine database-backed quiz system.

Tests cover:
- Question retrieval and filtering
- Quiz generation with randomization
- Answer grading
- Subset selection for practice quizzes
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base
from app.models import Topic, Module, QuizQuestion, QuizOption, User
from app.engines.quiz import QuizEngine


# Use in-memory SQLite for fast testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def test_db():
    """Create a test database and populate it with sample data."""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    
    # Create sample module and topic
    module = Module(name="Network Fundamentals", description="Networking basics")
    db.add(module)
    db.flush()
    
    topic = Topic(
        module_id=module.id,
        name="The OSI Model",
        description="Understanding the OSI reference model",
        content="The OSI model is a 7-layer framework...",
    )
    db.add(topic)
    db.flush()
    
    # Create sample quiz questions
    questions_data = [
        {
            "prompt": "Which layer handles routing?",
            "explanation": "Layer 3 (Network) handles routing.",
            "options": {
                "A": ("Application Layer", False),
                "B": ("Network Layer", True),
                "C": ("Data Link Layer", False),
                "D": ("Physical Layer", False),
            }
        },
        {
            "prompt": "What is TCP/IP?",
            "explanation": "TCP/IP is a protocol suite for internet communication.",
            "options": {
                "A": ("A type of firewall", False),
                "B": ("Protocol suite for internet", True),
                "C": ("A networking cable", False),
                "D": ("A routing algorithm", False),
            }
        },
        {
            "prompt": "Which layer handles encryption?",
            "explanation": "Layer 6 (Presentation) handles encryption and data formatting.",
            "options": {
                "A": ("Transport Layer", False),
                "B": ("Network Layer", False),
                "C": ("Presentation Layer", True),
                "D": ("Application Layer", False),
            }
        },
    ]
    
    for q_data in questions_data:
        question = QuizQuestion(
            topic_id=topic.id,
            prompt=q_data["prompt"],
            explanation=q_data["explanation"],
        )
        db.add(question)
        db.flush()
        
        for key, (label, is_correct) in q_data["options"].items():
            option = QuizOption(
                question_id=question.id,
                option_key=key,
                label=label,
                is_correct=is_correct,
            )
            db.add(option)
    
    db.commit()
    yield db
    db.close()


class TestQuizEngine:
    """Test suite for QuizEngine functionality."""
    
    def test_get_quiz(self, test_db):
        """Test retrieving full quiz for a topic."""
        quiz_engine = QuizEngine(test_db)
        topic_id = 1
        
        questions = quiz_engine.get_quiz(topic_id)
        
        assert len(questions) == 3
        assert all("id" in q for q in questions)
        assert all("prompt" in q for q in questions)
        assert all("options" in q for q in questions)
    
    def test_get_quiz_with_randomization(self, test_db):
        """Test that randomization works without errors."""
        quiz_engine = QuizEngine(test_db)
        topic_id = 1
        
        # Get quiz with randomization
        questions = quiz_engine.get_quiz(topic_id, randomize=True)
        
        assert len(questions) == 3
        # Options should be shuffled
        assert all(len(q["options"]) == 4 for q in questions)
    
    def test_get_quiz_subset(self, test_db):
        """Test retrieving a subset of questions."""
        quiz_engine = QuizEngine(test_db)
        topic_id = 1
        
        subset = quiz_engine.get_quiz_subset(topic_id, limit=2)
        
        assert len(subset) <= 2
        assert all("id" in q for q in subset)
    
    def test_get_quiz_subset_randomized(self, test_db):
        """Test that subset randomization works."""
        quiz_engine = QuizEngine(test_db)
        topic_id = 1
        
        # Get multiple subsets to verify randomization
        subset1 = quiz_engine.get_quiz_subset(topic_id, limit=2, randomize=True)
        subset2 = quiz_engine.get_quiz_subset(topic_id, limit=2, randomize=True)
        
        assert len(subset1) <= 2
        assert len(subset2) <= 2
    
    def test_get_question_by_id(self, test_db):
        """Test retrieving a single question by ID."""
        quiz_engine = QuizEngine(test_db)
        
        question = quiz_engine.get_question_by_id(1)
        
        assert question is not None
        assert question["id"] == 1
        assert "prompt" in question
        assert "options" in question
        assert len(question["options"]) == 4
    
    def test_get_nonexistent_question(self, test_db):
        """Test that nonexistent question returns None."""
        quiz_engine = QuizEngine(test_db)
        
        question = quiz_engine.get_question_by_id(9999)
        
        assert question is None
    
    def test_get_question_count(self, test_db):
        """Test getting the count of questions for a topic."""
        quiz_engine = QuizEngine(test_db)
        topic_id = 1
        
        count = quiz_engine.get_question_count(topic_id)
        
        assert count == 3
    
    def test_question_exists(self, test_db):
        """Test checking if a question exists."""
        quiz_engine = QuizEngine(test_db)
        
        assert quiz_engine.question_exists(1) is True
        assert quiz_engine.question_exists(9999) is False
    
    def test_get_answer_key(self, test_db):
        """Test retrieving the answer key for a topic."""
        quiz_engine = QuizEngine(test_db)
        topic_id = 1
        
        answer_key = quiz_engine.get_answer_key(topic_id)
        
        assert len(answer_key) == 3
        assert answer_key["1"] == "B"  # Network Layer
        assert answer_key["2"] == "B"  # Protocol suite
        assert answer_key["3"] == "C"  # Presentation Layer
    
    def test_grade_submission_all_correct(self, test_db):
        """Test grading a submission with all correct answers."""
        quiz_engine = QuizEngine(test_db)
        topic_id = 1
        
        # Submit all correct answers
        answers = {
            "1": "B",  # Correct
            "2": "B",  # Correct
            "3": "C",  # Correct
        }
        
        correct, total = quiz_engine.grade_submission(topic_id, answers)
        
        assert correct == 3
        assert total == 3
    
    def test_grade_submission_partial_correct(self, test_db):
        """Test grading a submission with some correct answers."""
        quiz_engine = QuizEngine(test_db)
        topic_id = 1
        
        # Submit some correct, some wrong
        answers = {
            "1": "B",  # Correct
            "2": "A",  # Wrong (correct is B)
            "3": "C",  # Correct
        }
        
        correct, total = quiz_engine.grade_submission(topic_id, answers)
        
        assert correct == 2
        assert total == 3
    
    def test_grade_submission_all_wrong(self, test_db):
        """Test grading a submission with all wrong answers."""
        quiz_engine = QuizEngine(test_db)
        topic_id = 1
        
        # Submit all wrong answers
        answers = {
            "1": "A",  # Wrong
            "2": "C",  # Wrong
            "3": "A",  # Wrong
        }
        
        correct, total = quiz_engine.grade_submission(topic_id, answers)
        
        assert correct == 0
        assert total == 3
    
    def test_add_question(self, test_db):
        """Test adding a new question to the database."""
        quiz_engine = QuizEngine(test_db)
        topic_id = 1
        
        # Add a new question
        new_question = quiz_engine.add_question(
            topic_id=topic_id,
            prompt="What is the Internet?",
            explanation="The Internet is a global network.",
            options_dict={
                "A": ("A local network", False),
                "B": ("A global network", True),
                "C": ("A protocol", False),
                "D": ("A server", False),
            }
        )
        
        assert new_question.id is not None
        assert new_question.prompt == "What is the Internet?"
        assert len(new_question.options) == 4
        
        # Verify question was saved
        count = quiz_engine.get_question_count(topic_id)
        assert count == 4
    
    def test_get_quiz_for_nonexistent_topic(self, test_db):
        """Test that requesting quiz for nonexistent topic raises ValueError."""
        quiz_engine = QuizEngine(test_db)
        
        with pytest.raises(ValueError, match="No quiz defined"):
            quiz_engine.get_quiz(9999)
    
    def test_get_answer_key_for_nonexistent_topic(self, test_db):
        """Test that getting answer key for nonexistent topic raises ValueError."""
        quiz_engine = QuizEngine(test_db)
        
        with pytest.raises(ValueError, match="No quiz defined"):
            quiz_engine.get_answer_key(9999)
