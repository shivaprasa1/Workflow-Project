
from app.models.user import User
from app.utils.security import hash_password


def create_user(
    db_session,
    name,
    email,
    role
):
    user = User(
        name=name,
        email=email,
        password_hash=hash_password("TestPassword123"),
        role=role,
        department="Engineering",
        is_active=True
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
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_employee_cannot_access_users_without_token(client):
    response = client.get("/users/")

    assert response.status_code == 401


def test_employee_cannot_access_admin_user_management(client):
    employee_data = {
        "name": "Role Test Employee",
        "email": "role_test@example.com",
        "password": "TestPassword123",
        "department": "Engineering"
    }

    client.post("/employees/", json=employee_data)

    token = get_token(client, "role_test@example.com")

    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 403


def test_admin_can_list_users(client, db_session):
    admin = create_user(
        db_session,
        "Admin User",
        "admin@example.com",
        "ADMIN"
    )

    token = get_token(client, admin.email)

    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_admin_can_update_employee_role(client, db_session):
    admin = create_user(
        db_session,
        "Admin User",
        "admin@example.com",
        "ADMIN"
    )

    employee = create_user(
        db_session,
        "Employee User",
        "employee@example.com",
        "EMPLOYEE"
    )

    token = get_token(client, admin.email)

    response = client.patch(
        f"/users/{employee.id}/role",
        json={"role": "MANAGER"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["role"] == "MANAGER"


def test_admin_cannot_remove_own_admin_role(client, db_session):
    admin = create_user(
        db_session,
        "Admin User",
        "admin@example.com",
        "ADMIN"
    )

    token = get_token(client, admin.email)

    response = client.patch(
        f"/users/{admin.id}/role",
        json={"role": "EMPLOYEE"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "You cannot remove your own Admin role."


def test_admin_cannot_deactivate_own_account(client, db_session):
    admin = create_user(
        db_session,
        "Admin User",
        "admin@example.com",
        "ADMIN"
    )

    token = get_token(client, admin.email)

    response = client.patch(
        f"/users/{admin.id}/status",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "You cannot deactivate your own account."


def test_last_active_admin_cannot_be_demoted(client, db_session):
    admin = create_user(
        db_session,
        "Admin User",
        "admin@example.com",
        "ADMIN"
    )

    employee = create_user(
        db_session,
        "Employee User",
        "employee@example.com",
        "EMPLOYEE"
    )

    token = get_token(client, admin.email)

    response = client.patch(
        f"/users/{employee.id}/role",
        json={"role": "ADMIN"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    response = client.patch(
        f"/users/{admin.id}/role",
        json={"role": "MANAGER"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400


def test_last_active_admin_cannot_be_deactivated(client, db_session):
    admin = create_user(
        db_session,
        "Admin User",
        "admin@example.com",
        "ADMIN"
    )

    token = get_token(client, admin.email)

    # Create a second Admin so the first Admin can attempt
    # to deactivate the other account.
    second_admin = create_user(
        db_session,
        "Second Admin",
        "second_admin@example.com",
        "ADMIN"
    )

    response = client.patch(
        f"/users/{second_admin.id}/status",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    response = client.patch(
        f"/users/{admin.id}/status",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
