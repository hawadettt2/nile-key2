import io
import uuid

import pytest


def _unique_credentials(role: str = "customer") -> dict:
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"test_user_{unique_id}",
        "full_name": "Test User",
        "password": "TestPassword123!",
    }


def _register_and_login(client, role: str = "customer") -> tuple[dict, str]:
    user = _unique_credentials(role=role)
    if "role" in user:
        del user["role"]
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


def test_list_documents_authorized(client):
    _, token = _register_and_login(client)
    response = client.get("/api/v1/documents/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_document_authorized(client):
    _, token = _register_and_login(client)
    create_resp = client.post("/api/v1/documents/", json={
        "title": "Test Document",
        "document_type": "uploaded",
    }, headers={"Authorization": f"Bearer {token}"})
    document_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/documents/{document_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == document_id


def test_get_document_not_found(client):
    _, token = _register_and_login(client)
    response = client.get("/api/v1/documents/999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Document not found" in response.json().get("detail", "")


def test_create_document_authorized(client):
    _, token = _register_and_login(client)
    response = client.post("/api/v1/documents/", json={
        "title": "Test Document",
        "document_type": "uploaded",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["message"] == "Document created successfully"


def test_upload_document_authorized(client):
    _, token = _register_and_login(client)
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.pdf", b"%PDF-1.4 hello", "application/pdf")},
        data={"title": "Uploaded Document"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "filename" in data


def test_update_document_authorized(client):
    _, token = _register_and_login(client)
    create_resp = client.post("/api/v1/documents/", json={
        "title": "Test Document",
        "document_type": "uploaded",
    }, headers={"Authorization": f"Bearer {token}"})
    document_id = create_resp.json()["id"]
    response = client.put(f"/api/v1/documents/{document_id}", json={
        "title": "Updated Document",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Document updated successfully" in response.json().get("message", "")


def test_delete_document_with_owner_role(client):
    _, token = _register_and_login(client, role="owner")
    create_resp = client.post("/api/v1/documents/", json={
        "title": "Test Document",
        "document_type": "uploaded",
    }, headers={"Authorization": f"Bearer {token}"})
    document_id = create_resp.json()["id"]
    response = client.delete(f"/api/v1/documents/{document_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "deleted" in response.json().get("message", "").lower()
