import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def get_owner_id() -> int:
    import sqlite3
    from app.core.config import settings
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", ("owner@nile-key.com",))
    row = cursor.fetchone()
    conn.close()
    assert row, "Owner user not found in database"
    return row[0]


def register_user(role: str):
    email = f"{role}_test@example.com"
    password = "Test1234!"

    client.post("/api/v1/auth/register", json={
        "email": email,
        "username": email,
        "full_name": "Test User",
        "password": password,
        "phone": "000",
        "company": "TestCo"
    })

    owner_resp = client.post("/api/v1/auth/login", json={
        "username": "owner",
        "password": "TestOwnerPass123!"
    })
    assert owner_resp.status_code == 200

    import sqlite3
    from app.core.config import settings
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    user_id = row[0] if row else None
    conn.close()

    if user_id:
        client.post(f"/api/v1/users/{user_id}/approve?role={role}", json={})

    res = client.post("/api/v1/auth/login", json={
        "username": email,
        "password": password
    })

    return res.json()["access_token"]


def test_owner_can_create_supplier():
    token = register_user("owner")

    response = client.post(
        "/api/v1/suppliers/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Test Supplier",
            "email": "supplier@test.com"
        }
    )

    assert response.status_code == 200


def test_manager_cannot_update_owner():
    manager_token = register_user("manager")
    owner_id = get_owner_id()

    response = client.put(
        f"/api/v1/users/{owner_id}",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={"full_name": "Hacked Owner"}
    )

    assert response.status_code == 403
    assert "protected" in response.json()["detail"].lower()


def test_manager_cannot_deactivate_owner():
    manager_token = register_user("manager")
    owner_id = get_owner_id()

    response = client.put(
        f"/api/v1/users/{owner_id}",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={"is_active": False}
    )

    assert response.status_code == 403
    assert "protected" in response.json()["detail"].lower()


def test_manager_cannot_demote_owner():
    manager_token = register_user("manager")
    owner_id = get_owner_id()

    response = client.put(
        f"/api/v1/users/{owner_id}",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={"role": "customer"}
    )

    assert response.status_code == 403
    assert "protected" in response.json()["detail"].lower()


def test_manager_cannot_approve_owner():
    manager_token = register_user("manager")
    owner_id = get_owner_id()

    response = client.post(
        f"/api/v1/users/{owner_id}/approve",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={}
    )

    assert response.status_code == 403
    assert "protected" in response.json()["detail"].lower()


def test_manager_cannot_reject_owner():
    manager_token = register_user("manager")
    owner_id = get_owner_id()

    response = client.post(
        f"/api/v1/users/{owner_id}/reject",
        headers={"Authorization": f"Bearer {manager_token}"},
        json={}
    )

    assert response.status_code == 403
    assert "protected" in response.json()["detail"].lower()


def test_manager_cannot_delete_owner():
    manager_token = register_user("manager")
    owner_id = get_owner_id()

    response = client.delete(
        f"/api/v1/users/{owner_id}",
        headers={"Authorization": f"Bearer {manager_token}"}
    )

    assert response.status_code == 403


def test_owner_can_update_self():
    owner_resp = client.post("/api/v1/auth/login", json={
        "username": "owner",
        "password": "TestOwnerPass123!"
    })
    assert owner_resp.status_code == 200
    owner_token = owner_resp.json()["access_token"]
    owner_id = get_owner_id()

    response = client.put(
        f"/api/v1/users/{owner_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"full_name": "Updated Owner Name"}
    )

    assert response.status_code == 200


def test_refresh_token_checks_active_status():
    import sqlite3
    from app.core.config import settings

    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    owner_id = get_owner_id()
    cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (owner_id,))
    conn.commit()
    conn.close()

    try:
        owner_resp = client.post("/api/v1/auth/login", json={
            "username": "owner",
            "password": "TestOwnerPass123!"
        })
        assert owner_resp.status_code == 403
    finally:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_active = 1 WHERE id = ?", (owner_id,))
        conn.commit()
        conn.close()
