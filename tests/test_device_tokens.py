
from app.models.device_token import DeviceToken


def create_device_test_employee(client, email):
    response = client.post(
        "/employees/",
        json={
            "name": "Device Test Employee",
            "email": email,
            "password": "TestPassword123",
            "department": "Engineering",
        },
    )

    assert response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "TestPassword123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_register_device_token(client, db_session):
    headers = create_device_test_employee(
        client,
        "device_test@example.com"
    )

    response = client.post(
        "/device-tokens/",
        headers=headers,
        json={
            "device_token": "firebase_test_token_123456789",
            "platform": "ANDROID",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["device_token"] == "firebase_test_token_123456789"
    assert data["platform"] == "ANDROID"

    saved_token = db_session.query(DeviceToken).filter_by(
        device_token="firebase_test_token_123456789"
    ).first()

    assert saved_token is not None


def test_register_same_device_token_twice(client, db_session):
    headers = create_device_test_employee(
        client,
        "duplicate_device@example.com"
    )

    payload = {
        "device_token": "firebase_duplicate_token_123456",
        "platform": "ANDROID",
    }

    first_response = client.post(
        "/device-tokens/",
        headers=headers,
        json=payload,
    )

    second_response = client.post(
        "/device-tokens/",
        headers=headers,
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    tokens = db_session.query(DeviceToken).filter_by(
        device_token=payload["device_token"]
    ).all()

    assert len(tokens) == 1


def test_register_device_token_requires_authentication(client):
    response = client.post(
        "/device-tokens/",
        json={
            "device_token": "firebase_test_token_123456789",
            "platform": "ANDROID",
        },
    )

    assert response.status_code == 401


def test_register_device_token_rejects_invalid_platform(client):
    headers = create_device_test_employee(
        client,
        "invalid_platform@example.com"
    )

    response = client.post(
        "/device-tokens/",
        headers=headers,
        json={
            "device_token": "firebase_test_token_123456789",
            "platform": "WINDOWS",
        },
    )

    assert response.status_code == 422


def test_unregister_device_token(client, db_session):
    headers = create_device_test_employee(
        client,
        "remove_device@example.com"
    )

    device_token = "firebase_remove_token_123456"

    client.post(
        "/device-tokens/",
        headers=headers,
        json={
            "device_token": device_token,
            "platform": "WEB",
        },
    )

    response = client.delete(
        "/device-tokens/",
        headers=headers,
        params={"device_token": device_token},
    )

    assert response.status_code == 200

    saved_token = db_session.query(DeviceToken).filter_by(
        device_token=device_token
    ).first()

    assert saved_token is None


def test_user_cannot_unregister_another_users_token(client):
    first_headers = create_device_test_employee(
        client,
        "device_owner@example.com"
    )

    second_headers = create_device_test_employee(
        client,
        "different_device_user@example.com"
    )

    device_token = "firebase_owner_token_123456"

    client.post(
        "/device-tokens/",
        headers=first_headers,
        json={
            "device_token": device_token,
            "platform": "ANDROID",
        },
    )

    response = client.delete(
        "/device-tokens/",
        headers=second_headers,
        params={"device_token": device_token},
    )

    assert response.status_code == 404
