import uuid

import pytest


def _unique_credentials():
    """Generate unique credentials for each test to avoid collisions."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"test_user_{unique_id}",
        "full_name": "Test User",
        "password": "TestPassword123!",
        "role": "staff"
    }


def test_register_new_user(client):
    credentials = _unique_credentials()
    response = client.post("/api/v1/auth/register", json=credentials)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data or "id" in data


def test_register_duplicate_email(client):
    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
    response = client.post("/api/v1/auth/register", json=credentials)
    assert response.status_code == 400
    assert "already exists" in response.json().get("detail", "").lower()


def test_login_success(client):
    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
    response = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login_wrong_password(client):
    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
    response = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": "wrongpassword"
    })
    assert response.status_code in (401, 400)