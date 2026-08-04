import uuid
from datetime import datetime, timedelta

import pytest


def _unique_email(role):
    return f"audit_{role}_{uuid.uuid4().hex[:8]}@example.com"


def _register_and_login(client, role="customer"):
    email = _unique_email(role)
    password = "Test1234!"

    reg = client.post("/api/v1/auth/register", json={
        "email": email,
        "username": email,
        "full_name": "Test User",
        "password": password,
        "phone": "000",
        "company": "TestCo"
    })
    if reg.status_code != 200:
        raise RuntimeError(f"Registration failed: {reg.status_code} {reg.text}")
    user_id = reg.json().get("user_id") or reg.json().get("id")
    owner_resp = client.post("/api/v1/auth/login", json={
        "username": "owner",
        "password": "TestOwnerPass123!"
    })
    assert owner_resp.status_code == 200
    client.post(f"/api/v1/users/{user_id}/approve?role={role}", json={})
    res = client.post("/api/v1/auth/login", json={
        "username": email,
        "password": password
    })
    if res.status_code != 200:
        raise RuntimeError(f"Login failed: {res.status_code} {res.text}")

    user = {
        "email": email,
        "username": email,
        "full_name": "Test User",
        "password": password,
    }
    token = res.json()["access_token"]
    return user, token


def _seed_audit_logs(client):
    from app.core.database import init_db, get_db_connection

    init_db()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM audit_logs")
        conn.commit()

    now = datetime.utcnow()
    logs = [
        {"user_id": 1, "action": "created", "entity_type": "customer", "entity_id": 1, "details": "Created customer 1", "created_at": (now - timedelta(minutes=5)).isoformat()},
        {"user_id": 1, "action": "updated", "entity_type": "customer", "entity_id": 1, "details": "Updated customer 1", "created_at": (now - timedelta(minutes=4)).isoformat()},
        {"user_id": 2, "action": "created", "entity_type": "invoice", "entity_id": 10, "details": "Created invoice 10", "created_at": (now - timedelta(minutes=3)).isoformat()},
        {"user_id": 2, "action": "deleted", "entity_type": "invoice", "entity_id": 10, "details": "Deleted invoice 10", "created_at": (now - timedelta(minutes=2)).isoformat()},
        {"user_id": None, "action": "system", "entity_type": "config", "entity_id": None, "details": "System startup", "created_at": (now - timedelta(minutes=1)).isoformat()},
    ]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        for log in logs:
            cursor.execute(
                """INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    log["user_id"],
                    log["action"],
                    log["entity_type"],
                    log["entity_id"],
                    log["details"],
                    log["created_at"],
                ),
            )
        conn.commit()


# ========== Authorization Tests ==========


def test_get_audit_logs_requires_authorization(client):
    response = client.get("/api/v1/audit/logs")
    assert response.status_code in (401, 403)


def test_get_audit_logs_authorized_with_owner(client):
    _, token = _register_and_login(client, role="owner")
    _seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_audit_logs_authorized_with_manager(client):
    _, token = _register_and_login(client, role="manager")
    _seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_get_audit_logs_authorized_with_admin_staff(client):
    _, token = _register_and_login(client, role="admin_staff")
    _seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_get_audit_logs_forbidden_for_sales(client):
    _, token = _register_and_login(client, role="sales")
    _seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


# ========== Query Parameter Tests ==========


def test_get_audit_logs_filters_by_user_id(client):
    _, token = _register_and_login(client, role="owner")
    _seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
        params={"user_id": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(row["user_id"] == 1 for row in data)
    assert len(data) == 2


def test_get_audit_logs_filters_by_entity_type(client):
    _, token = _register_and_login(client, role="owner")
    _seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
        params={"entity_type": "invoice"},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(row["entity_type"] == "invoice" for row in data)
    assert len(data) == 2


def test_get_audit_logs_filters_by_action(client):
    _, token = _register_and_login(client, role="owner")
    _seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
        params={"action": "created"},
    )
    assert response.status_code == 200
    data = response.json()
    assert all(row["action"] == "created" for row in data)
    assert len(data) == 2


def test_get_audit_logs_filters_by_date_range(client):
    _, token = _register_and_login(client, role="owner")
    _seed_audit_logs(client)

    now = datetime.utcnow()
    date_from = (now - timedelta(hours=1)).isoformat()
    date_to = (now + timedelta(hours=1)).isoformat()

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
        params={"date_from": date_from, "date_to": date_to},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5


def test_get_audit_logs_pagination_skip(client):
    _, token = _register_and_login(client, role="owner")
    _seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
        params={"skip": 2, "limit": 100},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_get_audit_logs_pagination_limit(client):
    _, token = _register_and_login(client, role="owner")
    _seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
        params={"skip": 0, "limit": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_audit_logs_response_model(client):
    _, token = _register_and_login(client, role="owner")
    _seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
        params={"limit": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    row = data[0]
    expected_keys = {"id", "user_id", "action", "entity_type", "entity_id", "details", "created_at", "ip_address", "user_agent", "session_id"}
    assert expected_keys.issubset(row.keys())


def test_get_audit_logs_empty_result(client):
    _, token = _register_and_login(client, role="owner")
    _seed_audit_logs(client)

    response = client.get(
        "/api/v1/audit/logs",
        headers={"Authorization": f"Bearer {token}"},
        params={"user_id": 999},
    )
    assert response.status_code == 200
    data = response.json()
    assert data == []