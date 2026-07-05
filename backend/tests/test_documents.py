import io
import uuid

import pytest


def _unique_credentials(role="staff"):
    unique_id = str(uuid.uuid4())[:8]
    return {
        "email": f"test_{unique_id}@example.com",
        "username": f"test_user_{unique_id}",
        "full_name": "Test User",
        "password": "TestPassword123!",
        "role": role,
    }


def _register_and_login(client, role="staff"):
    credentials = _unique_credentials(role)
    client.post("/api/v1/auth/register", json=credentials)
    login_resp = client.post("/api/v1/auth/login", json={
        "username": credentials["username"],
        "password": credentials["password"]
    })
    return login_resp.json()["access_token"], credentials


def test_list_documents_authorized(client):
    token, _ = _register_and_login(client)
    response = client.get("/api/v1/documents/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_document_authorized(client):
    token, _ = _register_and_login(client)
    create_resp = client.post("/api/v1/documents/", json={
        "title": "Test Document",
        "document_type": "uploaded",
    }, headers={"Authorization": f"Bearer {token}"})
    document_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/documents/{document_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == document_id


def test_get_document_not_found(client):
    token, _ = _register_and_login(client)
    response = client.get("/api/v1/documents/999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Document not found" in response.json().get("detail", "")


def test_create_document_authorized(client):
    token, _ = _register_and_login(client)
    response = client.post("/api/v1/documents/", json={
        "title": "Test Document",
        "document_type": "uploaded",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["message"] == "Document created successfully"


def test_upload_document_authorized(client):
    token, _ = _register_and_login(client)
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
    token, _ = _register_and_login(client)
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
    token, _ = _register_and_login(client, role="owner")
    create_resp = client.post("/api/v1/documents/", json={
        "title": "Test Document",
        "document_type": "uploaded",
    }, headers={"Authorization": f"Bearer {token}"})
    document_id = create_resp.json()["id"]
    response = client.delete(f"/api/v1/documents/{document_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "deleted" in response.json().get("message", "").lower()
