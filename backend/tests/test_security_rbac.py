import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

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
