
import pytest
from fastapi import HTTPException, status


def create_ai_test_employee(client):
    response = client.post(
        "/employees/",
        json={
            "name": "AI Test Employee",
            "email": "ai_test@example.com",
            "password": "TestPassword123",
            "department": "Engineering",
        },
    )

    assert response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": "ai_test@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_ai_task_analysis_success(client, monkeypatch):
    headers = create_ai_test_employee(client)

    async def mock_analyze_task(title, description):
        return {
            "category": "Software Development",
            "suggested_priority": "HIGH",
            "summary": "Develop an employee attendance module.",
            "reasoning": "The feature supports an important business workflow.",
        }

    monkeypatch.setattr(
        "app.routers.ai.analyze_task",
        mock_analyze_task,
    )

    response = client.post(
        "/ai/analyze-task",
        headers=headers,
        json={
            "title": "Develop attendance module",
            "description": "Create a system for tracking employee attendance.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["category"] == "Software Development"
    assert data["suggested_priority"] == "HIGH"
    assert "summary" in data
    assert "reasoning" in data


def test_ai_task_analysis_requires_authentication(client):
    response = client.post(
        "/ai/analyze-task",
        json={
            "title": "Develop attendance module",
            "description": "Create a system for tracking employee attendance.",
        },
    )

    assert response.status_code == 401


def test_ai_task_analysis_rejects_invalid_request(client, monkeypatch):
    headers = create_ai_test_employee(client)

    async def mock_analyze_task(title, description):
        pytest.fail("AI service should not be called for invalid input.")

    monkeypatch.setattr(
        "app.routers.ai.analyze_task",
        mock_analyze_task,
    )

    response = client.post(
        "/ai/analyze-task",
        headers=headers,
        json={
            "title": "AB",
            "description": "Test",
        },
    )

    assert response.status_code == 422


def test_ai_task_analysis_handles_provider_error(client, monkeypatch):
    headers = create_ai_test_employee(client)

    async def mock_analyze_task(title, description):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not configured.",
        )

    monkeypatch.setattr(
        "app.routers.ai.analyze_task",
        mock_analyze_task,
    )

    response = client.post(
        "/ai/analyze-task",
        headers=headers,
        json={
            "title": "Develop attendance module",
            "description": "Create a system for tracking employee attendance.",
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "AI service is not configured."
