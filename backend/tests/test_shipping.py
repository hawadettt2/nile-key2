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


def test_get_rates_authorized(client):
    token, _ = _register_and_login(client)
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
    token, _ = _register_and_login(client)
    response = client.get("/api/v1/shipping/shipments", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_track_shipment_authorized(client):
    token, _ = _register_and_login(client, role="sales")
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
    token, _ = _register_and_login(client)
    response = client.get("/api/v1/shipping/track/UNKNOWN123", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Shipment not found" in response.json().get("detail", "")


def test_get_shipment_authorized(client):
    token, _ = _register_and_login(client, role="sales")
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
    token, _ = _register_and_login(client, role="sales")
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
    token, _ = _register_and_login(client, role="staff")
    response = client.post("/api/v1/shipping/shipments", json={
        "origin": "EG",
        "destination": "US",
        "weight": 10,
        "weight_unit": "kg",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json().get("detail", "")


def test_update_shipment_with_manager_role(client):
    token, _ = _register_and_login(client, role="manager")
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
    token, _ = _register_and_login(client, role="sales")
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
