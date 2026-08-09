import uuid
import pytest


def _unique_credentials(role="staff"):
    """Generate unique credentials for each test to avoid collisions."""
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"test_user_{unique_id}",
        "full_name": "Test User",
        "password": "TestPassword123!",
    }


def _register_and_approve(client, role="customer"):
    """Register a new user and approve them via owner."""
    credentials = _unique_credentials(role)
    reg_resp = client.post("/api/v1/auth/register", json=credentials)
    assert reg_resp.status_code == 200, f"Registration failed: {reg_resp.text}"
    user_id = reg_resp.json().get("user_id") or reg_resp.json().get("id")
    owner_resp = client.post("/api/v1/auth/login", json={
        "username": "owner",
        "password": "TestOwnerPass123!"
    })
    assert owner_resp.status_code == 200, f"Owner login failed: {owner_resp.text}"
    approve_resp = client.post(f"/api/v1/users/{user_id}/approve?role={role}", json={})
    assert approve_resp.status_code == 200, f"Approval failed: {approve_resp.text}"
    login_resp = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    return login_resp.json()["access_token"], credentials


# ========== Research Request Creation ==========


def test_create_research_request_authorized(client):
    token, credentials = _register_and_approve(client, role="owner")
    response = client.post("/api/v1/research/requests", json={
        "goal": "Study feasibility of opening a new market in Jordan for Egyptian vegetables and fruits export",
        "context": {"session_id": "sess_123", "mission": "market_expansion"},
        "scope": {"domains": ["agriculture", "export"], "regions": ["Jordan"], "time_range": {"start": "2025-01-01", "end": "2025-12-31"}},
        "source_preferences": ["trade_statistics", "market_data"],
        "constraints": {"max_sources": 10},
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "request_id" in data
    assert data["status"] == "completed"
    assert data["goal"] == "Study feasibility of opening a new market in Jordan for Egyptian vegetables and fruits export"
    assert data["findings"] == []
    assert "created_at" in data
    assert "completed_at" in data
    assert "metadata" in data
    assert data["metadata"]["requested_by"] == credentials["username"]


def test_create_research_request_minimal(client):
    token, _ = _register_and_approve(client, role="owner")
    response = client.post("/api/v1/research/requests", json={
        "goal": "Simple research goal",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["goal"] == "Simple research goal"


def test_create_research_request_unauthorized(client):
    response = client.post("/api/v1/research/requests", json={
        "goal": "Study feasibility of opening a new market",
    })
    assert response.status_code == 401


def test_create_research_request_empty_goal(client):
    token, _ = _register_and_approve(client, role="owner")
    response = client.post("/api/v1/research/requests", json={
        "goal": "",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


def test_create_research_request_missing_goal(client):
    token, _ = _register_and_approve(client, role="owner")
    response = client.post("/api/v1/research/requests", json={}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


# ========== Research Request Retrieval ==========


def test_get_research_request_authorized(client):
    token, credentials = _register_and_approve(client, role="owner")
    create_resp = client.post("/api/v1/research/requests", json={
        "goal": "Research Jordan market",
    }, headers={"Authorization": f"Bearer {token}"})
    request_id = create_resp.json()["request_id"]

    response = client.get(f"/api/v1/research/requests/{request_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == request_id
    assert data["goal"] == "Research Jordan market"


def test_get_research_request_not_found(client):
    token, _ = _register_and_approve(client, role="owner")
    response = client.get("/api/v1/research/requests/nonexistent_id", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_get_research_request_unauthorized(client):
    response = client.get("/api/v1/research/requests/req_123456")
    assert response.status_code == 401


# ========== Research Request Cancellation ==========


def test_cancel_research_request_authorized(client):
    token, _ = _register_and_approve(client, role="owner")
    create_resp = client.post("/api/v1/research/requests", json={
        "goal": "Research to cancel",
    }, headers={"Authorization": f"Bearer {token}"})
    request_id = create_resp.json()["request_id"]

    response = client.post(f"/api/v1/research/requests/{request_id}/cancel", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 400
    data = response.json()
    assert "Cannot cancel research in status: completed" in data["detail"]


def test_cancel_research_request_not_found(client):
    token, _ = _register_and_approve(client, role="owner")
    response = client.post("/api/v1/research/requests/nonexistent_id/cancel", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


def test_cancel_research_request_unauthorized(client):
    response = client.post("/api/v1/research/requests/req_123456/cancel")
    assert response.status_code == 401
