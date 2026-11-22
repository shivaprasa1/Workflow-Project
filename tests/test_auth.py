from datetime import datetime, timedelta, timezone

import jwt

from app.utils.security import JWT_SECRET_KEY, JWT_ALGORITHM

from app.models.user import User

def create_test_employee(client):
    employee_data = {
        "name": "Auth Test Employee",
        "email": "auth_test@example.com",
        "password": "TestPassword123",
        "department": "Engineering",
    }

    response = client.post("/employees/", json=employee_data)
    assert response.status_code == 201


def test_login_with_valid_credentials(client):
    create_test_employee(client)

    login_data = {
        "email": "auth_test@example.com",
        "password": "TestPassword123",
    }

    response = client.post("/auth/login", json=login_data)

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"].lower() == "bearer"


def test_login_with_wrong_password(client):
    create_test_employee(client)

    login_data = {
        "email": "auth_test@example.com",
        "password": "WrongPassword123",
    }

    response = client.post("/auth/login", json=login_data)

    assert response.status_code == 401


def test_access_profile_without_token(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_access_profile_with_valid_token(client):
    create_test_employee(client)

    login_response = client.post(
        "/auth/login",
        json={
            "email": "auth_test@example.com",
            "password": "TestPassword123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "auth_test@example.com"











def test_access_profile_with_expired_token(client):
    expired_payload = {
        "sub": "expired_user@example.com",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
    }

    expired_token = jwt.encode(
        expired_payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token."





def test_inactive_user_cannot_access_profile(client, db_session):
    # Register an employee.
    create_test_employee(client)

    # Login and obtain a valid token.
    login_response = client.post(
        "/auth/login",
        json={
            "email": "auth_test@example.com",
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    # Deactivate the employee in the database.
    employee = (
        db_session.query(User)
        .filter(User.email == "auth_test@example.com")
        .first()
    )

    assert employee is not None

    employee.is_active = False
    db_session.commit()

    # Attempt to access the protected profile using the old token.
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User account is unavailable."















def test_inactive_user_login_returns_generic_error(client, db_session):
    create_test_employee(client)

    employee = (
        db_session.query(User)
        .filter(User.email == "auth_test@example.com")
        .first()
    )

    employee.is_active = False
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={
            "email": "auth_test@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."
