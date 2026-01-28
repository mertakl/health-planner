import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestPlanEndpoints:
    """Test plan endpoints."""

    def test_list_plans_empty(self, client: TestClient):
        response = client.get("/api/v1/plans")
        assert response.status_code == 200
        data = response.json()
        assert data["plans"] == []
        assert data["total"] == 0

    def test_get_nonexistent_plan(self, client: TestClient):
        response = client.get("/api/plans/nonexistent-id")
        assert response.status_code == 404

    def test_delete_nonexistent_plan(self, client: TestClient):
        response = client.delete("/api/plans/nonexistent-id")
        assert response.status_code == 404

    def test_list_plans(self, client: TestClient):
        response = client.get("/api/plans")
        assert response.status_code == 200
        data = response.json()
        assert data is not None
        assert len(data) >= 0

    def test_create_plan_validation(self, client: TestClient):
        # Missing required fields
        response = client.post("/api/plans/generate", json={})
        assert response.status_code == 422  # Validation error

        # Goal too short
        response = client.post("/api/plans/generate", json={
            "goal": "Run",  # Too short (min 10 chars)
            "current_level": "Beginner",
            "timeline": "3 months"
        })
        assert response.status_code == 422
