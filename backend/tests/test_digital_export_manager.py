import uuid

import pytest

from app.agent.schemas.enums import MissionStatus
from app.agent.schemas.api_response import MissionResponse
from app.agent.session.manager import SessionManager
from app.core.database import get_db, init_db


def _unique_credentials(role: str = "customer") -> dict:
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"dem_{unique_id}@example.com",
        "username": f"dem_user_{unique_id}",
        "full_name": "DEM Test User",
        "password": "TestPassword123!",
    }


def _register_and_login(client, role: str = "customer") -> tuple[dict, str]:
    user = _unique_credentials(role=role)
    reg_resp = client.post("/api/v1/auth/register", json=user)
    assert reg_resp.status_code == 200
    user_id = reg_resp.json().get("user_id") or reg_resp.json().get("id")
    owner_resp = client.post("/api/v1/auth/login", json={
        "username": "owner",
        "password": "TestOwnerPass123!"
    })
    assert owner_resp.status_code == 200
    client.post(f"/api/v1/users/{user_id}/approve?role={role}", json={})
    response = client.post("/api/v1/auth/login", json={
        "username": user["username"],
        "password": user["password"],
    })
    token = response.json()["access_token"]
    return user, token


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_mission_status_enum_has_pending_approval():
    assert MissionStatus.PENDING_APPROVAL.value == "pending_approval"
    assert MissionStatus.PENDING_APPROVAL in MissionStatus


def test_mission_response_has_new_fields():
    from datetime import datetime, timezone
    response = MissionResponse(
        mission_id="mission-123",
        session_id="session-123",
        status="pending_approval",
        created_at=datetime.now(timezone.utc),
        reasoning="Test reasoning",
        requires_approval=True,
        approval_status="pending",
    )
    assert response.reasoning == "Test reasoning"
    assert response.requires_approval is True
    assert response.approval_status == "pending"


def test_connect_creates_session(client):
    _, token = _register_and_login(client, role="sales")
    response = client.post(
        "/api/v1/digital-export-manager/connect",
        json={"user_id": 1},
        headers=_auth_headers(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "connected"


def test_list_tools_endpoint(client):
    _, token = _register_and_login(client, role="sales")
    response = client.get(
        "/api/v1/digital-export-manager/tools",
        headers=_auth_headers(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert "count" in data


def test_approval_inbox_requires_manager_role(client):
    _, token = _register_and_login(client)
    response = client.get(
        "/api/v1/digital-export-manager/approvals",
        headers=_auth_headers(token),
    )
    assert response.status_code == 403


def test_approve_requires_manager_role(client):
    _, token = _register_and_login(client)
    response = client.post(
        "/api/v1/digital-export-manager/approvals/mission-123/approve",
        headers=_auth_headers(token),
    )
    assert response.status_code == 403


def test_reject_requires_manager_role(client):
    _, token = _register_and_login(client)
    response = client.post(
        "/api/v1/digital-export-manager/approvals/mission-123/reject",
        headers=_auth_headers(token),
    )
    assert response.status_code == 403


def test_approve_not_found(client):
    _, token = _register_and_login(client, role="manager")
    response = client.post(
        "/api/v1/digital-export-manager/approvals/nonexistent-mission/approve",
        headers=_auth_headers(token),
    )
    assert response.status_code == 404


def test_reject_not_found(client):
    _, token = _register_and_login(client, role="manager")
    response = client.post(
        "/api/v1/digital-export-manager/approvals/nonexistent-mission/reject",
        headers=_auth_headers(token),
    )
    assert response.status_code == 404


def test_session_manager_get_pending_approvals():
    init_db()
    manager = SessionManager(get_db)
    approvals = manager.get_pending_approvals()
    assert isinstance(approvals, list)


def test_approve_creates_audit_log_entry(client):
    import uuid
    import json
    import hashlib
    from datetime import datetime, timezone
    unique_id = str(uuid.uuid4())[:8]
    credentials = {
        "email": f"audit_{unique_id}@example.com",
        "username": f"audit_user_{unique_id}",
        "full_name": "Audit Test User",
        "password": "TestPassword123!",
    }
    reg_resp = client.post("/api/v1/auth/register", json=credentials)
    assert reg_resp.status_code == 200
    user_id = reg_resp.json().get("user_id") or reg_resp.json().get("id")
    owner_resp = client.post("/api/v1/auth/login", json={
        "username": "owner",
        "password": "TestOwnerPass123!"
    })
    assert owner_resp.status_code == 200
    client.post(f"/api/v1/users/{user_id}/approve?role=manager", json={})
    response = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"],
    })
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    connect_resp = client.post(
        "/api/v1/digital-export-manager/connect",
        json={"user_id": 1},
        headers=headers,
    )
    assert connect_resp.status_code == 200
    session_id = connect_resp.json()["session_id"]

    manager = SessionManager(get_db)
    context = manager.get_context(session_id) or {}
    context["missions"] = [
        {
            "mission_id": "mission-audit-123",
            "session_id": session_id,
            "status": "pending_approval",
            "requires_approval": True,
            "approval_status": "pending",
            "reasoning": "Audit test reasoning",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    ]
    manager.update_context(session_id, context)

    approve_resp = client.post(
        "/api/v1/digital-export-manager/approvals/mission-audit-123/approve",
        headers=headers,
    )
    assert approve_resp.status_code == 200
    data = approve_resp.json()
    assert data["decision"] == "approved"
    assert isinstance(data["approved_by"], int)
    assert data["approved_by"] > 0

    expected_input = {"approval_id": "mission-audit-123", "decision": "approved"}
    expected_input_hash = hashlib.sha256(json.dumps(expected_input, sort_keys=True).encode()).hexdigest()

    import sqlite3
    from app.core.config import settings

    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Check if table exists
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_audit_logs'").fetchall()
    
    session_row = conn.execute(
        "SELECT id, status FROM agent_sessions WHERE id = ?",
        (session_id,),
    ).fetchone()
    all_rows = conn.execute(
        "SELECT session_id, tool_name, input_hash, result_ref FROM agent_audit_logs WHERE session_id = ?",
        (session_id,),
    ).fetchall()
    rows = [r for r in all_rows if r["tool_name"] == "approval_decision"]
    conn.close()

    assert session_row is not None, f"Session {session_id} not found in agent_sessions"
    assert len(rows) >= 1, f"Expected approval_decision audit log, found {len(rows)} rows. All tool_names: {[r['tool_name'] for r in all_rows]}, db_path={db_path}, session_id={session_id}"
    tool_name = rows[0]["tool_name"]
    input_hash = rows[0]["input_hash"]
    result_ref = rows[0]["result_ref"]
    assert tool_name == "approval_decision"
    assert input_hash == expected_input_hash
    output_data = json.loads(result_ref)
    assert output_data["decision"] == "approved"
    assert output_data["approved_by"] == data["approved_by"]


def test_connect_requires_internal_role(client):
    _, token = _register_and_login(client, role="supplier")
    response = client.post(
        "/api/v1/digital-export-manager/connect",
        json={"user_id": 1},
        headers=_auth_headers(token),
    )
    assert response.status_code == 403


def test_connect_requires_internal_role_customer(client):
    _, token = _register_and_login(client, role="customer")
    response = client.post(
        "/api/v1/digital-export-manager/connect",
        json={"user_id": 1},
        headers=_auth_headers(token),
    )
    assert response.status_code == 403


def test_missions_requires_internal_role(client):
    _, token = _register_and_login(client, role="supplier")
    response = client.post(
        "/api/v1/digital-export-manager/missions",
        json={"mission_type": "export_readiness", "payload": {}},
        headers=_auth_headers(token),
    )
    assert response.status_code == 403


def test_sessions_list_requires_internal_role(client):
    _, token = _register_and_login(client, role="customer")
    response = client.get(
        "/api/v1/digital-export-manager/sessions",
        headers=_auth_headers(token),
    )
    assert response.status_code == 403


def test_session_detail_requires_internal_role(client):
    _, token = _register_and_login(client, role="supplier")
    response = client.get(
        "/api/v1/digital-export-manager/sessions/nonexistent-session",
        headers=_auth_headers(token),
    )
    assert response.status_code == 403


def test_close_session_requires_internal_role(client):
    _, token = _register_and_login(client, role="customer")
    response = client.post(
        "/api/v1/digital-export-manager/sessions/nonexistent-session/close",
        headers=_auth_headers(token),
    )
    assert response.status_code == 403


def test_tools_requires_authentication(client):
    response = client.get("/api/v1/digital-export-manager/tools")
    assert response.status_code == 401


