
from tests.test_tasks import (
    create_test_user,
    get_token,
)


def test_employee_can_access_dashboard(client, db_session):
    employee = create_test_user(
        db_session,
        "Dashboard Employee",
        "dashboard_employee@example.com",
        "EMPLOYEE",
    )

    token = get_token(client, employee.email)

    response = client.get(
        "/dashboard/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


def test_dashboard_requires_authentication(client):
    response = client.get("/dashboard/")

    assert response.status_code == 401


def test_dashboard_returns_task_statistics(client, db_session):
    employee = create_test_user(
        db_session,
        "Statistics Employee",
        "statistics_employee@example.com",
        "EMPLOYEE",
    )

    token = get_token(client, employee.email)

    response = client.get(
        "/dashboard/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert "statistics" in data
    assert data["statistics"]["total_tasks"] == 0
