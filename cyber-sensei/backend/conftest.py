"""
Pytest configuration for CYBER-SENSEI tests
Handles test database setup and fixtures
"""

import os
import sys
from pathlib import Path

# Set test environment first
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SKIP_ML_ENGINE"] = "true"

# Add backend to path (resolve relative to repo root)
ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = ROOT / 'backend'
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

import pytest
from starlette.testclient import TestClient


@pytest.fixture(scope="function")
def client():
    """Provide FastAPI test client"""
    from app.main import app
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Sample test user data"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }


@pytest.fixture
def test_topic_data():
    """Sample test topic data"""
    return {
        "title": "Network Security",
        "description": "Learn network security fundamentals",
        "difficulty_level": "beginner"
    }


@pytest.fixture
def test_quiz_data():
    """Sample test quiz data"""
    return {
        "title": "Network Security Quiz",
        "description": "Test your network security knowledge",
        "passing_score": 70
    }
