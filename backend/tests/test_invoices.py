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


def test_list_invoices_authorized(client):
    token, _ = _register_and_login(client)
    response = client.get("/api/v1/invoices/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_invoice_authorized(client):
    token, _ = _register_and_login(client, role="accountant")
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
    token, _ = _register_and_login(client)
    response = client.get("/api/v1/invoices/999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Invoice not found" in response.json().get("detail", "")


def test_create_invoice_with_accountant_role(client):
    token, _ = _register_and_login(client, role="accountant")
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
    token, _ = _register_and_login(client, role="staff")
    response = client.post("/api/v1/invoices/", json={
        "subtotal": 100.0,
        "total": 114.0,
        "items": [{"description": "Item 1", "quantity": 1.0, "unit_price": 100.0, "total": 100.0}],
            "issue_date": "2026-07-05",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json().get("detail", "")


def test_update_invoice_with_manager_role(client):
    token, _ = _register_and_login(client, role="manager")
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
    token, _ = _register_and_login(client, role="accountant")
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
    token, _ = _register_and_login(client, role="accountant")
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
    token, _ = _register_and_login(client, role="accountant")
    response = client.post("/api/v1/invoices/999999/cancel", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Invoice not found" in response.json().get("detail", "")


def test_get_invoice_status_authorized(client):
    token, _ = _register_and_login(client, role="accountant")
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
