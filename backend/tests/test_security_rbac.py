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
        "role": role,
        "phone": "000",
        "company": "TestCo"
    })

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
