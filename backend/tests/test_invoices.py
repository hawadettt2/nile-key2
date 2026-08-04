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


def test_list_invoices_authorized(client):
    _, token = _register_and_login(client)
    response = client.get("/api/v1/invoices/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_invoice_authorized(client):
    _, token = _register_and_login(client, role="accountant")
    create_resp = client.post("/api/v1/invoices/", json={
        "subtotal": 100.0,
        "total": 114.0,
        "issue_date": "2026-07-05",
        "items": [{"description": "Item 1", "quantity": 1.0, "unit_price": 100.0, "total": 100.0}],
    }, headers={"Authorization": f"Bearer {token}"})
    invoice_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/invoices/{invoice_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == invoice_id


def test_get_invoice_not_found(client):
    _, token = _register_and_login(client)
    response = client.get("/api/v1/invoices/999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Invoice not found" in response.json().get("detail", "")


def test_create_invoice_with_accountant_role(client):
    _, token = _register_and_login(client, role="accountant")
    response = client.post("/api/v1/invoices/", json={
        "subtotal": 100.0,
        "total": 114.0,
        "issue_date": "2026-07-05",
        "items": [{"description": "Item 1", "quantity": 1.0, "unit_price": 100.0, "total": 100.0}],
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "invoice_number" in data


def test_create_invoice_with_staff_role_forbidden(client):
    _, token = _register_and_login(client, role="staff")
    response = client.post("/api/v1/invoices/", json={
        "subtotal": 100.0,
        "total": 114.0,
        "items": [{"description": "Item 1", "quantity": 1.0, "unit_price": 100.0, "total": 100.0}],
            "issue_date": "2026-07-05",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json().get("detail", "")


def test_update_invoice_with_manager_role(client):
    _, token = _register_and_login(client, role="manager")
    create_resp = client.post("/api/v1/invoices/", json={
        "subtotal": 100.0,
        "total": 114.0,
        "items": [{"description": "Item 1", "quantity": 1.0, "unit_price": 100.0, "total": 100.0}],
            "issue_date": "2026-07-05",
    }, headers={"Authorization": f"Bearer {token}"})
    invoice_id = create_resp.json()["id"]
    response = client.put(f"/api/v1/invoices/{invoice_id}", json={
        "notes": "Updated invoice",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Invoice updated successfully" in response.json().get("message", "")


def test_validate_invoice_with_accountant_role(client):
    _, token = _register_and_login(client, role="accountant")
    create_resp = client.post("/api/v1/invoices/", json={
        "subtotal": 100.0,
        "total": 114.0,
        "items": [{"description": "Item 1", "quantity": 1.0, "unit_price": 100.0, "total": 100.0}],
            "issue_date": "2026-07-05",
    }, headers={"Authorization": f"Bearer {token}"})
    invoice_id = create_resp.json()["id"]
    response = client.post(f"/api/v1/invoices/{invoice_id}/validate", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "validated" in response.json().get("message", "").lower()


def test_cancel_invoice_with_accountant_role(client):
    _, token = _register_and_login(client, role="accountant")
    create_resp = client.post("/api/v1/invoices/", json={
        "subtotal": 100.0,
        "total": 114.0,
        "items": [{"description": "Item 1", "quantity": 1.0, "unit_price": 100.0, "total": 100.0}],
            "issue_date": "2026-07-05",
    }, headers={"Authorization": f"Bearer {token}"})
    invoice_id = create_resp.json()["id"]
    response = client.post(f"/api/v1/invoices/{invoice_id}/cancel", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "cancelled" in response.json().get("message", "").lower()


def test_cancel_invoice_not_found(client):
    _, token = _register_and_login(client, role="accountant")
    response = client.post("/api/v1/invoices/999999/cancel", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Invoice not found" in response.json().get("detail", "")


def test_get_invoice_status_authorized(client):
    _, token = _register_and_login(client, role="accountant")
    create_resp = client.post("/api/v1/invoices/", json={
        "subtotal": 100.0,
        "total": 114.0,
        "items": [{"description": "Item 1", "quantity": 1.0, "unit_price": 100.0, "total": 100.0}],
            "issue_date": "2026-07-05",
    }, headers={"Authorization": f"Bearer {token}"})
    invoice_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/invoices/{invoice_id}/status", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == invoice_id
