"""
Test suite for CRUD endpoints.

Tests all entity creation, retrieval, update, and deletion operations.
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import json

from app.main import app
from app.database import SessionLocal
from app.core.security import create_access_token


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers."""
    token = create_access_token(data={"sub": "test_user"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_module(client, auth_headers):
    """Create a test module."""
    response = client.post(
        "/api/modules",
        json={
            "name": "Test Module",
            "description": "Test Description",
            "icon": "🧪",
            "color": "#FF0000"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def test_topic(client, auth_headers, test_module):
    """Create a test topic."""
    response = client.post(
        "/api/topics",
        json={
            "name": "Test Topic",
            "description": "Test Topic Description",
            "module_id": test_module["id"],
            "order": 1,
            "difficulty": "intermediate"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    return response.json()


class TestModuleCRUD:
    """Test module CRUD operations."""
    
    def test_create_module(self, client, auth_headers):
        """Test module creation."""
        response = client.post(
            "/api/modules",
            json={
                "name": "New Module",
                "description": "New Module Description",
                "icon": "📚",
                "color": "#3498db"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Module"
        assert data["created_by"] == "test_user"
    
    def test_create_module_duplicate(self, client, auth_headers, test_module):
        """Test that duplicate module names are rejected."""
        response = client.post(
            "/api/modules",
            json={
                "name": test_module["name"],
                "description": "Duplicate",
                "icon": "🔒",
                "color": "#FF0000"
            },
            headers=auth_headers
        )
        assert response.status_code == 409
    
    def test_list_modules(self, client, test_module):
        """Test listing modules."""
        response = client.get("/api/modules")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(m["id"] == test_module["id"] for m in data)
    
    def test_get_module(self, client, test_module):
        """Test getting a specific module."""
        response = client.get(f"/api/modules/{test_module['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_module["id"]
        assert data["name"] == test_module["name"]
    
    def test_get_nonexistent_module(self, client):
        """Test getting non-existent module."""
        response = client.get("/api/modules/99999")
        assert response.status_code == 404
    
    def test_update_module(self, client, auth_headers, test_module):
        """Test updating a module."""
        response = client.put(
            f"/api/modules/{test_module['id']}",
            json={
                "name": "Updated Module",
                "description": "Updated Description"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Module"
    
    def test_delete_module(self, client, auth_headers, test_module):
        """Test deleting a module."""
        response = client.delete(
            f"/api/modules/{test_module['id']}",
            headers=auth_headers
        )
        assert response.status_code == 204
        
        # Verify deleted
        response = client.get(f"/api/modules/{test_module['id']}")
        assert response.status_code == 404


class TestTopicCRUD:
    """Test topic CRUD operations."""
    
    def test_create_topic(self, client, auth_headers, test_module):
        """Test topic creation."""
        response = client.post(
            "/api/topics",
            json={
                "name": "New Topic",
                "description": "New Topic Description",
                "module_id": test_module["id"],
                "difficulty": "advanced"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Topic"
        assert data["module_id"] == test_module["id"]
    
    def test_list_module_topics(self, client, test_topic, test_module):
        """Test listing topics in a module."""
        response = client.get(f"/api/modules/{test_module['id']}/topics")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert any(t["id"] == test_topic["id"] for t in data)
    
    def test_get_topic(self, client, test_topic):
        """Test getting a specific topic."""
        response = client.get(f"/api/topics/{test_topic['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_topic["id"]
    
    def test_update_topic(self, client, auth_headers, test_topic):
        """Test updating a topic."""
        response = client.put(
            f"/api/topics/{test_topic['id']}",
            json={
                "difficulty": "expert"
            },
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["difficulty"] == "expert"
    
    def test_delete_topic(self, client, auth_headers, test_topic):
        """Test deleting a topic."""
        response = client.delete(
            f"/api/topics/{test_topic['id']}",
            headers=auth_headers
        )
        assert response.status_code == 204


class TestResourceCRUD:
    """Test resource CRUD operations."""
    
    def test_create_resource(self, client, auth_headers, test_topic):
        """Test resource creation."""
        response = client.post(
            "/api/resources",
            json={
                "title": "Learning Resource",
                "description": "Resource Description",
                "resource_type": "video",
                "url": "https://example.com/video",
                "topic_id": test_topic["id"]
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Learning Resource"
        assert data["topic_id"] == test_topic["id"]
    
    def test_list_topic_resources(self, client, test_topic, auth_headers):
        """Test listing resources for a topic."""
        # Create a resource first
        client.post(
            "/api/resources",
            json={
                "title": "Test Resource",
                "resource_type": "article",
                "url": "https://example.com",
                "topic_id": test_topic["id"]
            },
            headers=auth_headers
        )
        
        response = client.get(f"/api/topics/{test_topic['id']}/resources")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_resource(self, client, auth_headers, test_topic):
        """Test getting a specific resource."""
        create_response = client.post(
            "/api/resources",
            json={
                "title": "Get Test Resource",
                "resource_type": "pdf",
                "url": "https://example.com",
                "topic_id": test_topic["id"]
            },
            headers=auth_headers
        )
        resource_id = create_response.json()["id"]
        
        response = client.get(f"/api/resources/{resource_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == resource_id


class TestQuizQuestionCRUD:
    """Test quiz question CRUD operations."""
    
    def test_create_quiz_question(self, client, auth_headers, test_topic):
        """Test quiz question creation."""
        response = client.post(
            "/api/quiz-questions",
            json={
                "prompt": "What is cybersecurity?",
                "explanation": "Cybersecurity is...",
                "topic_id": test_topic["id"],
                "options": [
                    {"option_key": "a", "label": "Correct answer", "is_correct": True},
                    {"option_key": "b", "label": "Wrong answer", "is_correct": False}
                ]
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["prompt"] == "What is cybersecurity?"
        assert len(data["options"]) == 2
    
    def test_list_topic_questions(self, client, test_topic, auth_headers):
        """Test listing questions for a topic."""
        # Create a question first
        client.post(
            "/api/quiz-questions",
            json={
                "prompt": "Test Question",
                "topic_id": test_topic["id"],
                "options": [
                    {"option_key": "a", "label": "Option A", "is_correct": True},
                    {"option_key": "b", "label": "Option B", "is_correct": False}
                ]
            },
            headers=auth_headers
        )
        
        response = client.get(f"/api/topics/{test_topic['id']}/quiz-questions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestProjectCRUD:
    """Test project CRUD operations."""
    
    def test_create_project(self, client, auth_headers):
        """Test project creation."""
        response = client.post(
            "/api/projects",
            json={
                "name": "Security Audit Project",
                "description": "Audit a network",
                "status": "planning"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Security Audit Project"
        assert data["owner"] == "test_user"
    
    def test_list_user_projects(self, client, auth_headers):
        """Test listing user's projects."""
        # Create a project first
        client.post(
            "/api/projects",
            json={
                "name": "Test Project",
                "status": "in_progress"
            },
            headers=auth_headers
        )
        
        response = client.get("/api/projects", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_update_project_status(self, client, auth_headers):
        """Test updating project status."""
        create_response = client.post(
            "/api/projects",
            json={
                "name": "Status Test",
                "status": "planning"
            },
            headers=auth_headers
        )
        project_id = create_response.json()["id"]
        
        response = client.put(
            f"/api/projects/{project_id}",
            json={"status": "completed"},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"


class TestUserProgress:
    """Test user progress endpoints."""
    
    def test_update_user_progress(self, client, auth_headers, test_topic):
        """Test updating user progress."""
        response = client.put(
            f"/api/progress/{test_topic['id']}?completion_percentage=75",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["completion_percentage"] == 75
    
    def test_get_all_user_progress(self, client, auth_headers):
        """Test getting all user progress."""
        response = client.get("/api/progress", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
