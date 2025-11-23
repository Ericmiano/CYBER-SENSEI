from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_knowledge_documents():
    response = client.get("/api/knowledge-base")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_topic_quiz():
    # Ensure topic exists
    topic_response = client.get("/api/learning/topic/1")
    assert topic_response.status_code == 200

    quiz_response = client.get("/api/learning/topic/1/quiz")
    assert quiz_response.status_code == 200
    payload = quiz_response.json()
    assert payload["question_count"] >= 1
    assert len(payload["questions"]) == payload["question_count"]
