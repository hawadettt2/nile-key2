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


def test_csrf_allows_post_with_valid_origin(client):
    import os
    origins = os.environ.get("ALLOWED_ORIGINS", "")
    if not origins:
        pytest.skip("ALLOWED_ORIGINS not set; CSRF middleware is inactive in this environment")

    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
    client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    response = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    }, headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200


def test_csrf_blocks_post_with_invalid_origin(client):
    import os
    origins = os.environ.get("ALLOWED_ORIGINS", "")
    if not origins:
        pytest.skip("ALLOWED_ORIGINS not set; CSRF middleware is inactive in this environment")

    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
    client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    response = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    }, headers={"Origin": "http://evil.com"})
    assert response.status_code == 403
    assert "CSRF" in response.json().get("detail", "")


def test_csrf_blocks_post_without_origin_or_referer(client):
    import os
    origins = os.environ.get("ALLOWED_ORIGINS", "")
    if not origins:
        pytest.skip("ALLOWED_ORIGINS not set; CSRF middleware is inactive in this environment")

    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
    client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    response = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    assert response.status_code == 403
    assert "CSRF" in response.json().get("detail", "")


def test_csrf_allows_post_with_authorization_header(client):
    import os
    origins = os.environ.get("ALLOWED_ORIGINS", "")
    if not origins:
        pytest.skip("ALLOWED_ORIGINS not set; CSRF middleware is inactive in this environment")

    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
    login_resp = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    token = login_resp.json()["access_token"]
    response = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_csrf_allows_get_requests(client):
    import os
    origins = os.environ.get("ALLOWED_ORIGINS", "")
    if not origins:
        pytest.skip("ALLOWED_ORIGINS not set; CSRF middleware is inactive in this environment")

    credentials = _unique_credentials()
    client.post("/api/v1/auth/register", json=credentials)
    client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
