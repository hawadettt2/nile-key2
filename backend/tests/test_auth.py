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
    _register_and_approve(client, credentials)
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
    _register_and_approve(client, credentials)
    response = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": "wrongpassword"
    })
    assert response.status_code in (401, 400)


def test_login_sets_cookies(client):
    credentials = _unique_credentials()
    _register_and_approve(client, credentials)
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
    _register_and_approve(client, credentials)
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
    _register_and_approve(client, credentials)
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


def test_login_pending_user_forbidden(client):
    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
    response = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    assert response.status_code == 403
    assert "pending approval" in response.json().get("detail", "").lower()


def test_register_creates_pending_inactive_user(client):
    credentials = _unique_credentials()
    response = client.post("/api/v1/auth/register", json=credentials)
    assert response.status_code == 200
    user_id = response.json().get("user_id") or response.json().get("id")
    assert user_id is not None

    user_resp = client.get(f"/api/v1/users/{user_id}", headers={"Authorization": "Bearer dummy"})
    assert user_resp.status_code in (401, 403)

    import sqlite3
    from app.core.config import settings
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    assert row is not None
    assert row["is_active"] == 0
    assert row["approval_status"] == "pending"


def test_register_rejects_arbitrary_role_from_client(client):
    credentials = _unique_credentials()
    credentials["role"] = "owner"
    response = client.post("/api/v1/auth/register", json=credentials)
    assert response.status_code == 422


def test_approve_assigns_role(client):
    credentials = _unique_credentials()
    _register_and_approve(client, credentials, role="sales")
    response = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["role"] == "sales"


def test_register_response_has_no_role(client):
    credentials = _unique_credentials()
    response = client.post("/api/v1/auth/register", json=credentials)
    assert response.status_code == 200
    data = response.json()
    assert "role" not in data
