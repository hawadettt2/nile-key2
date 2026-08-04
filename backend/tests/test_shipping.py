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


def test_get_rates_authorized(client):
    _, token = _register_and_login(client)
    response = client.request("GET", "/api/v1/shipping/rates", json={
        "origin": "EG",
        "destination": "US",
        "weight": 10,
        "weight_unit": "kg",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "carrier" in data[0]
        assert "cost" in data[0]


def test_list_shipments_authorized(client):
    _, token = _register_and_login(client)
    response = client.get("/api/v1/shipping/shipments", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_track_shipment_authorized(client):
    _, token = _register_and_login(client, role="sales")
    create_resp = client.post("/api/v1/shipping/shipments", json={
        "origin": "EG",
        "destination": "US",
        "weight": 10,
        "weight_unit": "kg",
    }, headers={"Authorization": f"Bearer {token}"})
    tracking_number = create_resp.json()["tracking_number"]
    response = client.get(f"/api/v1/shipping/track/{tracking_number}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["tracking_number"] == tracking_number


def test_track_shipment_not_found(client):
    _, token = _register_and_login(client)
    response = client.get("/api/v1/shipping/track/UNKNOWN123", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Shipment not found" in response.json().get("detail", "")


def test_get_shipment_authorized(client):
    _, token = _register_and_login(client, role="sales")
    create_resp = client.post("/api/v1/shipping/shipments", json={
        "origin": "EG",
        "destination": "US",
        "weight": 10,
        "weight_unit": "kg",
    }, headers={"Authorization": f"Bearer {token}"})
    shipment_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/shipping/shipments/{shipment_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == shipment_id


def test_create_shipment_with_sales_role(client):
    _, token = _register_and_login(client, role="sales")
    response = client.post("/api/v1/shipping/shipments", json={
        "origin": "EG",
        "destination": "US",
        "weight": 10,
        "weight_unit": "kg",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "tracking_number" in data


def test_create_shipment_with_staff_role_forbidden(client):
    _, token = _register_and_login(client, role="staff")
    response = client.post("/api/v1/shipping/shipments", json={
        "origin": "EG",
        "destination": "US",
        "weight": 10,
        "weight_unit": "kg",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json().get("detail", "")


def test_update_shipment_with_manager_role(client):
    _, token = _register_and_login(client, role="manager")
    create_resp = client.post("/api/v1/shipping/shipments", json={
        "origin": "EG",
        "destination": "US",
        "weight": 10,
        "weight_unit": "kg",
    }, headers={"Authorization": f"Bearer {token}"})
    shipment_id = create_resp.json()["id"]
    response = client.put(f"/api/v1/shipping/shipments/{shipment_id}", json={
        "status": "in_transit",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Shipment updated successfully" in response.json().get("message", "")


def test_get_label_authorized(client):
    _, token = _register_and_login(client, role="sales")
    create_resp = client.post("/api/v1/shipping/shipments", json={
        "origin": "EG",
        "destination": "US",
        "weight": 10,
        "weight_unit": "kg",
    }, headers={"Authorization": f"Bearer {token}"})
    shipment_id = create_resp.json()["id"]
    response = client.get(f"/api/v1/shipping/shipments/{shipment_id}/label", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "label_url" in response.json()
