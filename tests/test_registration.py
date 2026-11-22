def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_employee_registration(client):
    employee_data = {
        "name": "Test Employee",
        "email": "testemployee@example.com",
        "password": "TestPassword123",
        "department": "Engineering",
    }

    response = client.post("/employees/", json=employee_data)

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Employee"
    assert data["email"] == "testemployee@example.com"
    assert data["role"] == "EMPLOYEE"

    # The API must never return the password.
    assert "password" not in data
    assert "password_hash" not in data


def test_duplicate_employee_registration(client):
    employee_data = {
        "name": "Test Employee",
        "email": "duplicate@example.com",
        "password": "TestPassword123",
        "department": "Engineering",
    }

    first_response = client.post("/employees/", json=employee_data)
    second_response = client.post("/employees/", json=employee_data)

    assert first_response.status_code == 201
    assert second_response.status_code == 409











def test_registration_normalizes_uppercase_email(client):
    employee_data = {
        "name": "Uppercase Employee",
        "email": "USER@EXAMPLE.COM",
        "password": "TestPassword123",
        "department": "Engineering",
    }

    response = client.post("/employees/", json=employee_data)

    assert response.status_code == 201
    assert response.json()["email"] == "user@example.com"


def test_registration_rejects_duplicate_email_with_different_case(client):
    first_employee = {
        "name": "First Employee",
        "email": "duplicate@example.com",
        "password": "TestPassword123",
        "department": "Engineering",
    }

    second_employee = {
        "name": "Second Employee",
        "email": "DUPLICATE@EXAMPLE.COM",
        "password": "TestPassword123",
        "department": "Engineering",
    }

    first_response = client.post("/employees/", json=first_employee)
    second_response = client.post("/employees/", json=second_employee)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
