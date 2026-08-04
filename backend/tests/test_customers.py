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


def test_list_customers_authorized(client):
    _, token = _register_and_login(client)
    response = client.get("/api/v1/customers/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_customers_unauthorized(client):
    response = client.get("/api/v1/customers/")
    assert response.status_code == 401


def test_get_customer_authorized(client):
    _, token = _register_and_login(client, role="owner")
    create_resp = client.post("/api/v1/customers/", json={
        "name": "Test Customer",
        "country": "Egypt",
    }, headers={"Authorization": f"Bearer {token}"})
    customer_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/customers/{customer_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == customer_id


def test_get_customer_not_found(client):
    _, token = _register_and_login(client)
    response = client.get("/api/v1/customers/999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Customer not found" in response.json().get("detail", "")


def test_create_customer_with_owner_role(client):
    _, token = _register_and_login(client, role="owner")
    response = client.post("/api/v1/customers/", json={
        "name": "Test Customer",
        "country": "Egypt",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["message"] == "Customer created successfully"


def test_create_customer_with_staff_role_forbidden(client):
    _, token = _register_and_login(client, role="staff")
    response = client.post("/api/v1/customers/", json={
        "name": "Test Customer",
        "country": "Egypt",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json().get("detail", "")


def test_update_customer_with_manager_role(client):
    _, token = _register_and_login(client, role="manager")
    create_resp = client.post("/api/v1/customers/", json={
        "name": "Test Customer",
        "country": "Egypt",
    }, headers={"Authorization": f"Bearer {token}"})
    customer_id = create_resp.json()["id"]
    response = client.put(f"/api/v1/customers/{customer_id}", json={
        "name": "Updated Customer",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Customer updated successfully" in response.json().get("message", "")


def test_delete_customer_with_owner_role(client):
    _, token = _register_and_login(client, role="owner")
    create_resp = client.post("/api/v1/customers/", json={
        "name": "Test Customer",
        "country": "Egypt",
    }, headers={"Authorization": f"Bearer {token}"})
    customer_id = create_resp.json()["id"]
    response = client.delete(f"/api/v1/customers/{customer_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "deactivated" in response.json().get("message", "").lower()


def test_import_customers_with_sales_role(client):
    _, token = _register_and_login(client, role="sales")
    csv_content = "name,country,email\nImport Customer,Egypt,import@example.com\n"
    response = client.post(
        "/api/v1/customers/import",
        files={"file": ("customers.csv", csv_content, "text/csv")},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "count" in data
