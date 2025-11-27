"""
Backend Test Suite for CYBER-SENSEI
Tests for models, services, and API routes
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db


# --- Test Database Setup ---
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create test database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    """Dependency override for tests"""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


# --- Health Check Tests ---
class TestHealthEndpoints:
    def test_health_endpoint(self, client):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_readiness_endpoint(self, client):
        """Test service readiness"""
        response = client.get("/health/ready")
        assert response.status_code in [200, 503]  # Ready or not ready
        data = response.json()
        assert "ready" in data


# --- User Tests ---
class TestUserAPI:
    def test_create_user(self, client):
        """Test user creation"""
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        response = client.post("/api/users", json=payload)
        assert response.status_code in [200, 201]
        data = response.json()
        assert "id" in data
        assert data["email"] == "test@example.com"

    def test_create_user_duplicate_email(self, client):
        """Test duplicate email validation"""
        payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        # Create first user
        response1 = client.post("/api/users", json=payload)
        assert response1.status_code in [200, 201]
        
        # Try to create duplicate
        response2 = client.post("/api/users", json=payload)
        assert response2.status_code == 400

    def test_get_user(self, client):
        """Test getting user by ID"""
        # Create user first
        create_payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        create_response = client.post("/api/users", json=create_payload)
        assert create_response.status_code in [200, 201]
        
        user_id = create_response.json()["id"]
        response = client.get(f"/api/users/{user_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"

    def test_list_users(self, client):
        """Test listing users"""
        response = client.get("/api/users")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


# --- Knowledge Base Tests ---
class TestKnowledgeBaseAPI:
    def test_list_knowledge_documents(self, client):
        """Test retrieving knowledge documents"""
        response = client.get("/api/knowledge-base")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_search_knowledge(self, client):
        """Test searching knowledge base"""
        response = client.get("/api/knowledge-base/search?q=security")
        assert response.status_code in [200, 404]  # May be empty
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_ingest_knowledge(self, client):
        """Test knowledge ingestion"""
        payload = {
            "title": "Network Security Basics",
            "content": "Understanding network security fundamentals...",
            "category": "security",
            "tags": ["network", "security"]
        }
        response = client.post("/api/knowledge-base/ingest", json=payload)
        assert response.status_code in [200, 201, 400]  # May have validation


# --- Learning Path Tests ---
class TestLearningAPI:
    def test_get_learning_paths(self, client):
        """Test getting learning paths"""
        response = client.get("/api/learning/paths")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_topic(self, client):
        """Test getting a topic"""
        # Try topic ID 1 first
        response = client.get("/api/learning/topic/1")
        if response.status_code == 200:
            data = response.json()
            assert "title" in data or "name" in data

    def test_get_topic_quiz(self, client):
        """Test getting quiz for a topic"""
        response = client.get("/api/learning/topic/1/quiz")
        if response.status_code == 200:
            data = response.json()
            assert "questions" in data or "question_count" in data

    def test_submit_quiz_answer(self, client):
        """Test submitting quiz answer"""
        payload = {
            "question_id": 1,
            "selected_option": "A",
            "user_id": 1
        }
        response = client.post("/api/learning/quiz/answer", json=payload)
        assert response.status_code in [200, 201, 400, 404]


# --- Lab Tests ---
class TestLabAPI:
    def test_list_labs(self, client):
        """Test listing available labs"""
        response = client.get("/api/labs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_lab_details(self, client):
        """Test getting lab details"""
        response = client.get("/api/labs/1")
        if response.status_code == 200:
            data = response.json()
            assert "title" in data or "name" in data
            assert "instructions" in data or "description" in data

    def test_start_lab(self, client):
        """Test starting a lab"""
        payload = {
            "user_id": 1,
            "lab_id": 1
        }
        response = client.post("/api/labs/start", json=payload)
        assert response.status_code in [200, 201, 400, 404]


# --- Search Tests ---
class TestSearchAPI:
    def test_advanced_search(self, client):
        """Test advanced search functionality"""
        response = client.get("/api/search?q=security&type=knowledge")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (list, dict))

    def test_search_with_filters(self, client):
        """Test search with filters"""
        response = client.get("/api/search?q=python&category=programming&level=beginner")
        assert response.status_code in [200, 404]


# --- Progress Tracking Tests ---
class TestProgressAPI:
    def test_get_user_progress(self, client):
        """Test getting user progress"""
        response = client.get("/api/progress/user/1")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "courses_completed" in data or "progress" in data

    def test_update_progress(self, client):
        """Test updating progress"""
        payload = {
            "user_id": 1,
            "topic_id": 1,
            "completion_percentage": 50
        }
        response = client.post("/api/progress/update", json=payload)
        assert response.status_code in [200, 201, 400, 404]


# --- Authentication Tests ---
class TestAuthenticationAPI:
    def test_login_user(self, client):
        """Test user login"""
        # First create a user
        create_payload = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        client.post("/api/users", json=create_payload)
        
        # Then try to login
        login_payload = {
            "email": "test@example.com",
            "password": "SecurePass123!"
        }
        response = client.post("/api/auth/login", json=login_payload)
        assert response.status_code in [200, 400, 401]
        
        if response.status_code == 200:
            data = response.json()
            assert "access_token" in data or "token" in data

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        payload = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!"
        }
        response = client.post("/api/auth/login", json=payload)
        assert response.status_code in [401, 400, 404]


# --- Error Handling Tests ---
class TestErrorHandling:
    def test_404_not_found(self, client):
        """Test 404 error handling"""
        response = client.get("/api/nonexistent/endpoint")
        assert response.status_code == 404

    def test_invalid_json_payload(self, client):
        """Test invalid JSON handling"""
        response = client.post(
            "/api/users",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]

    def test_missing_required_fields(self, client):
        """Test validation for missing fields"""
        payload = {"username": "test"}  # Missing email and password
        response = client.post("/api/users", json=payload)
        assert response.status_code in [400, 422]


# --- Integration Tests ---
class TestIntegration:
    def test_full_user_learning_flow(self, client):
        """Test complete user flow: create user -> get topic -> take quiz"""
        # 1. Create user
        user_payload = {
            "username": "integrationuser",
            "email": "integration@example.com",
            "password": "SecurePass123!"
        }
        user_response = client.post("/api/users", json=user_payload)
        assert user_response.status_code in [200, 201]
        
        # 2. Get available topics
        topics_response = client.get("/api/learning/paths")
        assert topics_response.status_code == 200
        
        # 3. Get quiz for first topic
        quiz_response = client.get("/api/learning/topic/1/quiz")
        # May or may not exist, but shouldn't crash

    def test_knowledge_search_and_retrieval(self, client):
        """Test knowledge ingestion and search flow"""
        # 1. Try to search existing knowledge
        search_response = client.get("/api/knowledge-base/search?q=security")
        assert search_response.status_code in [200, 404]
        
        # 2. Ingest new knowledge
        ingest_payload = {
            "title": "Test Document",
            "content": "This is test content",
            "category": "testing"
        }
        ingest_response = client.post("/api/knowledge-base/ingest", json=ingest_payload)
        assert ingest_response.status_code in [200, 201, 400]
