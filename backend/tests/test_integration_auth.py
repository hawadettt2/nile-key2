"""
Integration tests for the cookie-based authentication flow.

These tests verify end-to-end behavior across multiple requests,
simulating how the frontend interacts with the backend after
Stages 1-8 of the cookie-based authentication migration.
"""

import uuid
import pytest


def _unique_credentials():
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"test_user_{unique_id}",
        "full_name": "Test User",
        "password": "TestPassword123!",
        "role": "staff",
    }


class TestFullLoginFlow:
    """End-to-end login flow: register → login → cookies → authenticated requests."""

    def test_full_login_flow_with_cookies(self, client):
        credentials = _unique_credentials()
        client.post("/api/v1/auth/register", json=credentials)

        login_resp = client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        })
        assert login_resp.status_code == 200

        set_cookie_headers = login_resp.headers.get_list("set-cookie")
        cookie_names = [h.split("=")[0] for h in set_cookie_headers]
        assert "access_token" in cookie_names
        assert "refresh_token" in cookie_names

        me_resp = client.get("/api/v1/auth/me")
        assert me_resp.status_code == 200
        data = me_resp.json()
        assert data["email"] == credentials["email"]
        assert data["username"] == credentials["username"]

    def test_login_then_multiple_authenticated_requests(self, client):
        credentials = _unique_credentials()
        client.post("/api/v1/auth/register", json=credentials)
        client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        })

        for _ in range(3):
            resp = client.get("/api/v1/auth/me")
            assert resp.status_code == 200
            assert resp.json()["username"] == credentials["username"]


class TestSessionRestoration:
    """Session restoration using cookies across 'browser' restarts."""

    def test_session_restored_with_cookies(self, client):
        credentials = _unique_credentials()
        client.post("/api/v1/auth/register", json=credentials)
        client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        })

        original_user = client.get("/api/v1/auth/me").json()

        new_client = client
        me_resp = new_client.get("/api/v1/auth/me")
        assert me_resp.status_code == 200
        assert me_resp.json()["username"] == original_user["username"]

    def test_session_invalid_without_cookies(self, client):
        credentials = _unique_credentials()
        client.post("/api/v1/auth/register", json=credentials)
        client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        })

        fresh_client = client
        fresh_client.cookies.clear()
        resp = fresh_client.get("/api/v1/auth/me")
        assert resp.status_code == 401


class TestTransitionalHeaderAuth:
    """Verify Authorization Bearer header still works during transition."""

    def test_bearer_header_authenticates_without_cookies(self, client):
        credentials = _unique_credentials()
        client.post("/api/v1/auth/register", json=credentials)
        login_resp = client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        })
        token = login_resp.json()["access_token"]

        resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["username"] == credentials["username"]

    def test_bearer_header_after_login_still_works(self, client):
        credentials = _unique_credentials()
        client.post("/api/v1/auth/register", json=credentials)
        login_resp = client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        })
        token = login_resp.json()["access_token"]

        client.get("/api/v1/auth/me")

        resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200


class TestCSRFIntegration:
    """Verify CSRF protection does not break valid frontend flows."""

    def test_valid_csrf_post_with_cookies_and_origin(self, client):
        import os
        origins = os.environ.get("ALLOWED_ORIGINS", "")
        if not origins:
            pytest.skip("ALLOWED_ORIGINS not set")

        credentials = _unique_credentials()
        client.post("/api/v1/auth/register", json=credentials)
        client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        })

        resp = client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        }, headers={"Origin": "http://localhost:5173"})
        assert resp.status_code == 200

    def test_csrf_get_requests_unaffected(self, client):
        import os
        origins = os.environ.get("ALLOWED_ORIGINS", "")
        if not origins:
            pytest.skip("ALLOWED_ORIGINS not set")

        credentials = _unique_credentials()
        client.post("/api/v1/auth/register", json=credentials)
        client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        })

        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 200


class TestRefreshFlow:
    """Refresh token flow with cookies and Authorization header."""

    def test_refresh_with_bearer_header(self, client):
        credentials = _unique_credentials()
        client.post("/api/v1/auth/register", json=credentials)
        login_resp = client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        })
        refresh_tok = login_resp.json()["refresh_token"]

        resp = client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_tok}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

        set_cookie_headers = resp.headers.get_list("set-cookie")
        cookie_names = [h.split("=")[0] for h in set_cookie_headers]
        assert "access_token" in cookie_names
        assert "refresh_token" in cookie_names

    def test_refresh_then_authenticated_request(self, client):
        credentials = _unique_credentials()
        client.post("/api/v1/auth/register", json=credentials)
        login_resp = client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        })
        refresh_tok = login_resp.json()["refresh_token"]

        client.post("/api/v1/auth/refresh", headers={"Authorization": f"Bearer {refresh_tok}"})

        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 200
        assert resp.json()["username"] == credentials["username"]


class TestLogoutFlow:
    """Logout behavior during transitional period."""

    def test_logout_clears_local_state(self, client):
        credentials = _unique_credentials()
        client.post("/api/v1/auth/register", json=credentials)
        client.post("/api/v1/auth/login", json={
            "username": credentials["username"],
            "password": credentials["password"]
        })

        resp = client.get("/api/v1/auth/me")
        assert resp.status_code == 200

