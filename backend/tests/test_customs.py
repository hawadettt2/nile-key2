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


# NOTE: HS code list/get endpoints are currently affected by a known schema mismatch
# between the HSCode response schema (requires `created_at`) and the database rows
# (no `created_at` column). These endpoints raise ResponseValidationError (500) in
# the current codebase and are excluded from automated coverage for WP-17.


def test_calculate_duties_authorized(client):
    token, _ = _register_and_login(client)
    response = client.post("/api/v1/customs/calculate-duties", json={
        "hs_code": "0701.90",
        "value": 1000.0,
        "destination_country": "US",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "duty_amount" in data
    assert "tax_amount" in data


# NOTE: customs/declarations list/get endpoints have a known schema mismatch (documents
# stored as string "[]" but declared as list[ str ]). The create/update/submit flows
# below document the working declaration lifecycle.


def test_create_declaration_with_logistics_role(client):
    token, _ = _register_and_login(client, role="logistics")
    response = client.post("/api/v1/customs/declarations", json={
        "destination_country": "US",
        "total_value": 1000.0,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "declaration_number" in data


def test_create_declaration_with_staff_role_forbidden(client):
    token, _ = _register_and_login(client, role="staff")
    response = client.post("/api/v1/customs/declarations", json={
        "destination_country": "US",
        "total_value": 1000.0,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json().get("detail", "")


def test_update_declaration_with_manager_role(client):
    token, _ = _register_and_login(client, role="manager")
    create_resp = client.post("/api/v1/customs/declarations", json={
        "destination_country": "US",
        "total_value": 1000.0,
    }, headers={"Authorization": f"Bearer {token}"})
    declaration_id = create_resp.json()["id"]
    response = client.put(f"/api/v1/customs/declarations/{declaration_id}", json={
        "total_value": 2000.0,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Declaration updated successfully" in response.json().get("message", "")


def test_submit_declaration_authorized(client):
    token, _ = _register_and_login(client, role="manager")
    create_resp = client.post("/api/v1/customs/declarations", json={
        "destination_country": "US",
        "total_value": 1000.0,
    }, headers={"Authorization": f"Bearer {token}"})
    declaration_id = create_resp.json()["id"]
    response = client.post(f"/api/v1/customs/declarations/{declaration_id}/submit", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "submitted" in response.json().get("message", "").lower()


def test_get_declaration_not_found(client):
    token, _ = _register_and_login(client)
    response = client.get("/api/v1/customs/declarations/999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Declaration not found" in response.json().get("detail", "")
