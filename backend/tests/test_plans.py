import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


class TestPlanEndpoints:
    """Test plan endpoints."""

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
        response = client.post("/api/plans/generate", json={})
        assert response.status_code == 422  # Validation error

        response = client.post("/api/plans/generate", json={
            "goal": "Run",  # Too short (min 10 chars)
            "current_level": "Beginner",
            "timeline": "3 months"
        })
        assert response.status_code == 422

    def test_update_task_status_nonexistent_plan(self, client: TestClient):
        response = client.patch(
            "/api/plans/nonexistent-id/weeks/1/tasks/task-1",
            json={"completed": True}
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "Plan or task not found"

    def test_update_task_status_invalid_data(self, client: TestClient):
        response = client.patch(
            "/api/plans/some-plan-id/weeks/1/tasks/task-1",
            json={}
        )
        assert response.status_code == 422

        response = client.patch(
            "/api/plans/some-plan-id/weeks/1/tasks/task-1",
            json={"completed": "not-a-boolean"}
        )
        assert response.status_code == 422
