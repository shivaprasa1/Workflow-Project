
from datetime import datetime, timedelta, timezone

from app.models.user import User
from app.utils.security import hash_password


def create_test_user(db_session, name, email, role):
    user = User(
        name=name,
        email=email,
        password_hash=hash_password("TestPassword123"),
        role=role,
        department="Engineering",
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user


def get_token(client, email):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200
    return response.json()["access_token"]


def create_task_payload(employee_id):
    due_date = (
        datetime.now(timezone.utc) + timedelta(days=2)
    ).isoformat()

    return {
        "title": "Complete API Testing",
        "description": "Test the workflow management API.",
        "priority": "HIGH",
        "due_date": due_date,
        "assigned_to": employee_id,
    }


def test_admin_can_assign_task_to_employee(client, db_session):
    admin = create_test_user(
        db_session, "Test Admin", "task_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Test Employee", "task_employee@example.com", "EMPLOYEE"
    )

    token = get_token(client, admin.email)

    response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Complete API Testing"
    assert response.json()["assigned_to"] == employee.id
    assert response.json()["status"] == "ASSIGNED"


def test_employee_cannot_create_task(client, db_session):
    employee = create_test_user(
        db_session, "Regular Employee", "regular_employee@example.com", "EMPLOYEE"
    )

    token = get_token(client, employee.email)

    response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_employee_can_view_assigned_task(client, db_session):
    admin = create_test_user(
        db_session, "Task Admin", "view_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Task Employee", "view_employee@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)

    create_response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    employee_token = get_token(client, employee.email)

    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == task_id






def test_employee_can_start_task(client, db_session):
    admin = create_test_user(
        db_session, "Workflow Admin", "workflow_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Workflow Employee", "workflow_employee@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)

    create_response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    employee_token = get_token(client, employee.email)

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "IN_PROGRESS"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "IN_PROGRESS"


def test_employee_can_submit_task(client, db_session):
    admin = create_test_user(
        db_session, "Submit Admin", "submit_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Submit Employee", "submit_employee@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)

    create_response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    task_id = create_response.json()["id"]
    employee_token = get_token(client, employee.email)

    client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "IN_PROGRESS"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "SUBMITTED"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "SUBMITTED"


def test_admin_can_approve_submitted_task(client, db_session):
    admin = create_test_user(
        db_session, "Approve Admin", "approve_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Approve Employee", "approve_employee@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)

    create_response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    task_id = create_response.json()["id"]
    employee_token = get_token(client, employee.email)

    client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "IN_PROGRESS"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "SUBMITTED"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "APPROVED"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"


def test_employee_cannot_approve_own_task(client, db_session):
    admin = create_test_user(
        db_session, "Security Admin", "security_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Security Employee", "security_employee@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)

    create_response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    task_id = create_response.json()["id"]
    employee_token = get_token(client, employee.email)

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "APPROVED"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 403









def test_employee_cannot_view_another_employees_task(client, db_session):
    admin = create_test_user(
        db_session, "Access Admin", "access_admin@example.com", "ADMIN"
    )
    employee_one = create_test_user(
        db_session, "Employee One", "employee_one@example.com", "EMPLOYEE"
    )
    employee_two = create_test_user(
        db_session, "Employee Two", "employee_two@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)

    create_response = client.post(
        "/tasks/",
        json=create_task_payload(employee_one.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    employee_two_token = get_token(client, employee_two.email)

    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {employee_two_token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this task."


def test_manager_cannot_access_another_managers_task(client, db_session):
    manager_one = create_test_user(
        db_session, "Manager One", "manager_one@example.com", "MANAGER"
    )
    manager_two = create_test_user(
        db_session, "Manager Two", "manager_two@example.com", "MANAGER"
    )
    employee = create_test_user(
        db_session, "Manager Employee", "manager_employee@example.com", "EMPLOYEE"
    )

    manager_two_token = get_token(client, manager_two.email)

    create_response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {manager_two_token}"},
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    manager_one_token = get_token(client, manager_one.email)

    response = client.get(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {manager_one_token}"},
    )

    assert response.status_code == 403

    approval_response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "APPROVED"},
        headers={"Authorization": f"Bearer {manager_one_token}"},
    )

    assert approval_response.status_code == 403


def test_employee_cannot_submit_task_before_starting(client, db_session):
    admin = create_test_user(
        db_session, "Transition Admin", "transition_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Transition Employee", "transition_employee@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)

    create_response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    employee_token = get_token(client, employee.email)

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "SUBMITTED"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid task status transition."




def test_task_assignment_triggers_push_notification(
    client, db_session, monkeypatch
):
    admin = create_test_user(
        db_session, "Push Admin", "push_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Push Employee", "push_employee@example.com", "EMPLOYEE"
    )

    push_calls = []

    def mock_send_push_to_user(**kwargs):
        push_calls.append(kwargs)
        return 1

    monkeypatch.setattr(
        "app.services.task_service.send_push_to_user",
        mock_send_push_to_user,
    )

    admin_token = get_token(client, admin.email)

    response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 201
    assert len(push_calls) == 1
    assert push_calls[0]["user_id"] == employee.id
    assert push_calls[0]["data"]["task_id"] == response.json()["id"]
    assert push_calls[0]["data"]["notification_type"] == "TASK_ASSIGNED"


def test_task_submission_triggers_push_notification(
    client, db_session, monkeypatch
):
    admin = create_test_user(
        db_session, "Submit Push Admin", "submit_push_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Submit Push Employee",
        "submit_push_employee@example.com", "EMPLOYEE"
    )

    push_calls = []

    def mock_send_push_to_user(**kwargs):
        push_calls.append(kwargs)
        return 1

    monkeypatch.setattr(
        "app.services.task_service.send_push_to_user",
        mock_send_push_to_user,
    )

    admin_token = get_token(client, admin.email)

    create_response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    employee_token = get_token(client, employee.email)

    client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "IN_PROGRESS"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    # Ignore the task-assignment push notification.
    push_calls.clear()

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "SUBMITTED"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert len(push_calls) == 1
    assert push_calls[0]["user_id"] == admin.id
    assert push_calls[0]["data"]["task_id"] == task_id
    assert push_calls[0]["data"]["notification_type"] == "TASK_SUBMITTED"


def test_task_approval_triggers_push_notification(
    client, db_session, monkeypatch
):
    admin = create_test_user(
        db_session, "Approve Push Admin", "approve_push_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Approve Push Employee",
        "approve_push_employee@example.com", "EMPLOYEE"
    )

    push_calls = []

    def mock_send_push_to_user(**kwargs):
        push_calls.append(kwargs)
        return 1

    monkeypatch.setattr(
        "app.services.task_service.send_push_to_user",
        mock_send_push_to_user,
    )

    admin_token = get_token(client, admin.email)

    create_response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    employee_token = get_token(client, employee.email)

    client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "IN_PROGRESS"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "SUBMITTED"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    # Ignore earlier assignment and submission notifications.
    push_calls.clear()

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "APPROVED"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert len(push_calls) == 1
    assert push_calls[0]["user_id"] == employee.id
    assert push_calls[0]["data"]["task_id"] == task_id
    assert push_calls[0]["data"]["notification_type"] == "TASK_APPROVED"
