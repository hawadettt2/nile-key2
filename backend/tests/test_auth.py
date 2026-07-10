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


def test_login_sets_cookies(client):
    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
    response = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    assert response.status_code == 200
    set_cookie_headers = response.headers.get_list("set-cookie")
    cookie_names = [h.split("=")[0] for h in set_cookie_headers]
    assert "access_token" in cookie_names
    assert "refresh_token" in cookie_names
    for header in set_cookie_headers:
        header_lower = header.lower()
        assert "httponly" in header_lower
        assert "path=/" in header_lower
        assert "samesite=lax" in header_lower


def test_login_returns_token_in_body(client):
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


def test_get_me_with_cookie_auth(client):
    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
    client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == credentials["email"]
    assert data["username"] == credentials["username"]


def test_get_me_with_bearer_auth_still_works(client):
    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
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
