"""
Integration tests for backend components - simplified to existing endpoints
"""

import pytest


class TestBasicIntegration:
    def test_health_and_metrics(self, client):
        # Health check
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"

        # Metrics endpoint (cached)
        r2 = client.get("/api/monitoring/metrics")
        assert r2.status_code == 200
        assert isinstance(r2.json(), dict)

    def test_recommendations_and_dlq(self, client):
        # Recommendations (uses SKIP_ML_ENGINE in test env so it's fast)
        r = client.post("/api/recommendations/testuser")
        assert r.status_code in (200, 404)
        # DLQ endpoint
        r2 = client.get("/api/monitoring/dead-letter-queue")
        assert r2.status_code == 200
        assert isinstance(r2.json(), dict)


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
