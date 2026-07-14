import pytest


def _unique_credentials(role="staff"):
    import uuid
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


def test_list_export_workflows_authorized(client):
    token, _ = _register_and_login(client, role="manager")
    response = client.get("/api/v1/export-workflows", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_create_export_workflow_authorized(client):
    token, _ = _register_and_login(client, role="logistics")
    response = client.post("/api/v1/export-workflows", json={
        "customer_id": 1,
        "supplier_id": 1,
        "invoice_id": 1,
        "notes": "Test workflow",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "workflow_number" in data
    assert data["message"] == "Workflow created successfully"


def test_create_export_workflow_with_staff_role_forbidden(client):
    token, _ = _register_and_login(client, role="staff")
    response = client.post("/api/v1/export-workflows", json={
        "customer_id": 1,
        "supplier_id": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json().get("detail", "")


def test_get_export_workflow_authorized(client):
    token, _ = _register_and_login(client, role="manager")
    create_resp = client.post("/api/v1/export-workflows", json={
        "customer_id": 1,
        "supplier_id": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    workflow_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/export-workflows/{workflow_id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workflow_id
    assert "items" in data


def test_get_export_workflow_not_found(client):
    token, _ = _register_and_login(client, role="manager")
    response = client.get("/api/v1/export-workflows/999999", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert "Workflow not found" in response.json().get("detail", "")


def test_update_export_workflow_authorized(client):
    token, _ = _register_and_login(client, role="logistics")
    create_resp = client.post("/api/v1/export-workflows", json={
        "customer_id": 1,
        "supplier_id": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    workflow_id = create_resp.json()["id"]

    response = client.put(f"/api/v1/export-workflows/{workflow_id}", json={
        "state": "customs_ready",
        "notes": "Updated notes",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Workflow updated successfully" in response.json().get("message", "")


def test_submit_export_workflow_authorized(client):
    token, _ = _register_and_login(client, role="logistics")
    create_resp = client.post("/api/v1/export-workflows", json={
        "customer_id": 1,
        "supplier_id": 1,
        "shipment_id": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    workflow_id = create_resp.json()["id"]

    response = client.post(f"/api/v1/export-workflows/{workflow_id}/submit", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "state" in data


def test_get_export_workflow_summary_authorized(client):
    token, _ = _register_and_login(client, role="manager")
    create_resp = client.post("/api/v1/export-workflows", json={
        "customer_id": 1,
        "supplier_id": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    workflow_id = create_resp.json()["id"]

    response = client.get(f"/api/v1/export-workflows/{workflow_id}/summary", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "workflow" in data
    assert "customer" in data
    assert "supplier" in data
    assert "invoice" in data
    assert "customs_declaration" in data
    assert "shipment" in data
    assert "documents" in data
    assert "audit_logs" in data


def test_add_export_workflow_item_authorized(client):
    token, _ = _register_and_login(client, role="logistics")
    create_resp = client.post("/api/v1/export-workflows", json={
        "customer_id": 1,
        "supplier_id": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    workflow_id = create_resp.json()["id"]

    response = client.post(f"/api/v1/export-workflows/{workflow_id}/items", json={
        "workflow_id": workflow_id,
        "entity_type": "document",
        "entity_id": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Workflow item added successfully"
    assert "id" in data


def test_add_export_workflow_item_with_staff_role_forbidden(client):
    token, _ = _register_and_login(client, role="staff")
    create_resp = client.post("/api/v1/export-workflows", json={
        "customer_id": 1,
        "supplier_id": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    assert create_resp.status_code == 403
