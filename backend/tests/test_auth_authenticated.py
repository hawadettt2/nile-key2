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
    }


def _register_and_approve(client, credentials, role="customer"):
    reg_resp = client.post("/api/v1/auth/register", json=credentials)
    assert reg_resp.status_code == 200
    user_id = reg_resp.json().get("user_id") or reg_resp.json().get("id")
    owner_resp = client.post("/api/v1/auth/login", json={
        "username": "owner",
        "password": "TestOwnerPass123!"
    })
    assert owner_resp.status_code == 200
    response = client.post(f"/api/v1/users/{user_id}/approve?role={role}", json={})
    assert response.status_code == 200


def test_get_me_authorized(client):
    credentials = _unique_credentials()
    _register_and_approve(client, credentials)
    login_resp = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    token = login_resp.json()["access_token"]
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == credentials["email"]
    assert data["username"] == credentials["username"]


def test_get_me_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_refresh_token_success(client):
    credentials = _unique_credentials()
    _register_and_approve(client, credentials)
    login_resp = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    refresh_tok = login_resp.json()["refresh_token"]
    response = client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_tok}"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_token_invalid_token(client):
    response = client.post("/api/v1/auth/refresh", headers={"Authorization": "Bearer invalidtoken123"})
    assert response.status_code == 401