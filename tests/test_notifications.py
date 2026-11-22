
from tests.test_tasks import (
    create_test_user,
    get_token,
    create_task_payload,
)


def test_task_assignment_creates_notification(client, db_session):
    admin = create_test_user(
        db_session, "Notification Admin",
        "notification_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Notification Employee",
        "notification_employee@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)

    create_response = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert create_response.status_code == 201

    employee_token = get_token(client, employee.email)

    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200

    notifications = response.json()

    assert len(notifications) == 1
    assert notifications[0]["notification_type"] == "TASK_ASSIGNED"
    assert notifications[0]["is_read"] is False


def test_notification_unread_count(client, db_session):
    admin = create_test_user(
        db_session, "Count Admin",
        "count_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Count Employee",
        "count_employee@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)

    client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    employee_token = get_token(client, employee.email)

    response = client.get(
        "/notifications/unread-count",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert response.json()["unread_count"] == 1


def test_employee_can_mark_notification_as_read(client, db_session):
    admin = create_test_user(
        db_session, "Read Admin",
        "read_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Read Employee",
        "read_employee@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)

    client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    employee_token = get_token(client, employee.email)

    notifications_response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    notification_id = notifications_response.json()[0]["id"]

    response = client.patch(
        f"/notifications/{notification_id}/read",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert response.json()["is_read"] is True






def test_task_submission_notifies_creator(client, db_session):
    admin = create_test_user(
        db_session, "Submission Admin",
        "submission_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Submission Employee",
        "submission_employee@example.com", "EMPLOYEE"
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

    submit_response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "SUBMITTED"},
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert submit_response.status_code == 200

    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    assert any(
        item["notification_type"] == "TASK_SUBMITTED"
        for item in response.json()
    )


def test_task_approval_notifies_employee(client, db_session):
    admin = create_test_user(
        db_session, "Approval Admin",
        "approval_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Approval Employee",
        "approval_employee@example.com", "EMPLOYEE"
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

    approve_response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "APPROVED"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert approve_response.status_code == 200

    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert any(
        item["notification_type"] == "TASK_APPROVED"
        for item in response.json()
    )






def test_employee_can_mark_all_notifications_as_read(client, db_session):
    admin = create_test_user(
        db_session, "Bulk Read Admin",
        "bulk_read_admin@example.com", "ADMIN"
    )
    employee = create_test_user(
        db_session, "Bulk Read Employee",
        "bulk_read_employee@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)
    employee_token = get_token(client, employee.email)

    # Create two notifications by assigning two tasks.
    first_task = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    second_task = client.post(
        "/tasks/",
        json=create_task_payload(employee.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert first_task.status_code == 201
    assert second_task.status_code == 201

    # Mark the first notification as read.
    notifications = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {employee_token}"},
    ).json()

    assert len(notifications) == 2

    first_notification_id = notifications[0]["id"]

    single_read_response = client.patch(
        f"/notifications/{first_notification_id}/read",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert single_read_response.status_code == 200

    # Mark all remaining unread notifications as read.
    response = client.patch(
        "/notifications/read-all",
        headers={"Authorization": f"Bearer {employee_token}"},
    )

    assert response.status_code == 200
    assert response.json() == 1

    # Verify every notification is now read.
    final_notifications = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {employee_token}"},
    ).json()

    assert all(item["is_read"] is True for item in final_notifications)


def test_employee_cannot_mark_other_employee_notifications_as_read(
    client, db_session
):
    admin = create_test_user(
        db_session, "Ownership Admin",
        "ownership_admin@example.com", "ADMIN"
    )
    employee_one = create_test_user(
        db_session, "Ownership Employee One",
        "ownership_employee_one@example.com", "EMPLOYEE"
    )
    employee_two = create_test_user(
        db_session, "Ownership Employee Two",
        "ownership_employee_two@example.com", "EMPLOYEE"
    )

    admin_token = get_token(client, admin.email)
    employee_one_token = get_token(client, employee_one.email)
    employee_two_token = get_token(client, employee_two.email)

    # Create a notification for employee one.
    task_response = client.post(
        "/tasks/",
        json=create_task_payload(employee_one.id),
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert task_response.status_code == 201

    notification = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {employee_one_token}"},
    ).json()[0]

    notification_id = notification["id"]

    # Employee two attempts to mark employee one's notification as read.
    response = client.patch(
        f"/notifications/{notification_id}/read",
        headers={"Authorization": f"Bearer {employee_two_token}"},
    )

    assert response.status_code == 404

    # Confirm employee one's notification remains unread.
    owner_notifications = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {employee_one_token}"},
    ).json()

    assert owner_notifications[0]["is_read"] is False
