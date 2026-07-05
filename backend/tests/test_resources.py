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


def test_list_resources_authorized(client):
    token, _ = _register_and_login(client)
    response = client.get("/api/v1/resources/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_search_resources_authorized(client):
    token, _ = _register_and_login(client)
    response = client.get("/api/v1/resources/search?q=import", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_resource_authorized(client):
    token, _ = _register_and_login(client, role="owner")
    create_resp = client.post("/api/v1/resources/", json={
        "title": "Test Resource",
        "resource_type": "guide",
        "category": "exports",
    }, headers={"Authorization": f"Bearer {token}"})
    resource_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/resources/{resource_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == resource_id


def test_get_resource_not_found(client):
    token, _ = _register_and_login(client)
    response = client.get("/api/v1/resources/999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Resource not found" in response.json().get("detail", "")


def test_create_resource_with_owner_role(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/resources/", json={
        "title": "Test Resource",
        "resource_type": "guide",
        "category": "exports",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["message"] == "Resource created successfully"


def test_create_resource_with_staff_role_forbidden(client):
    token, _ = _register_and_login(client, role="staff")
    response = client.post("/api/v1/resources/", json={
        "title": "Test Resource",
        "resource_type": "guide",
        "category": "exports",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json().get("detail", "")


def test_update_resource_with_manager_role(client):
    token, _ = _register_and_login(client, role="manager")
    create_resp = client.post("/api/v1/resources/", json={
        "title": "Test Resource",
        "resource_type": "guide",
        "category": "exports",
    }, headers={"Authorization": f"Bearer {token}"})
    resource_id = create_resp.json()["id"]
    response = client.put(f"/api/v1/resources/{resource_id}", json={
        "title": "Updated Resource",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Resource updated successfully" in response.json().get("message", "")


def test_delete_resource_with_owner_role(client):
    token, _ = _register_and_login(client, role="owner")
    create_resp = client.post("/api/v1/resources/", json={
        "title": "Test Resource",
        "resource_type": "guide",
        "category": "exports",
    }, headers={"Authorization": f"Bearer {token}"})
    resource_id = create_resp.json()["id"]
    response = client.delete(f"/api/v1/resources/{resource_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "deactivated" in response.json().get("message", "").lower()
