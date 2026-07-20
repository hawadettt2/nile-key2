import uuid

import pytest


def _unique_email(role):
    return f"sec_{role}_{uuid.uuid4().hex[:8]}@example.com"


def _register_and_login(client, role="owner"):
    email = _unique_email(role)
    password = "TestPassword123!"

    client.post("/api/v1/auth/register", json={
        "email": email,
        "username": email,
        "full_name": "Sec Test User",
        "password": password,
        "role": role,
        "phone": "000",
        "company": "TestCo"
    })

    res = client.post("/api/v1/auth/login", json={
        "username": email,
        "password": password
    })

    return res.json()["access_token"]


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ========== Authentication Tests ==========


def test_all_mutation_endpoints_require_authentication(client):
    endpoints = [
        ("POST", "/api/v1/knowledge-graph/nodes", {"entity_type": "customer", "entity_id": 1, "label": "Test"}),
        ("DELETE", "/api/v1/knowledge-graph/nodes/customer/1", None),
        ("POST", "/api/v1/knowledge-graph/edges", {"source_node_id": "customer:1", "target_node_id": "supplier:1", "relationship_type": "ref"}),
        ("DELETE", "/api/v1/knowledge-graph/edges/edge-1", None),
        ("POST", "/api/v1/knowledge-graph/sync", None),
    ]

    for method, path, body in endpoints:
        if method == "POST":
            response = client.post(path, json=body)
        else:
            response = client.delete(path)

        assert response.status_code == 401, f"{method} {path} should require authentication"


# ========== Authorization Tests ==========


def test_mutations_require_manager_or_owner(client):
    staff_token = _register_and_login(client, role="staff")

    response = client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "Test"
    }, headers=_auth_headers(staff_token))
    assert response.status_code == 403

    response = client.post("/api/v1/knowledge-graph/edges", json={
        "source_node_id": "customer:1",
        "target_node_id": "supplier:1",
        "relationship_type": "ref"
    }, headers=_auth_headers(staff_token))
    assert response.status_code == 403

    response = client.post("/api/v1/knowledge-graph/sync", headers=_auth_headers(staff_token))
    assert response.status_code == 403


def test_read_endpoints_allow_authenticated_users(client):
    staff_token = _register_and_login(client, role="staff")

    response = client.get("/api/v1/knowledge-graph/nodes/customer/1", headers=_auth_headers(staff_token))
    assert response.status_code in (200, 404)

    response = client.get("/api/v1/knowledge-graph/search?query=test", headers=_auth_headers(staff_token))
    assert response.status_code == 200


# ========== Input Validation Tests ==========


def test_invalid_entity_type_rejected(client):
    token = _register_and_login(client, role="owner")
    response = client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "invalid_type",
        "entity_id": 1,
        "label": "Test"
    }, headers=_auth_headers(token))
    assert response.status_code in (400, 422)


def test_missing_required_fields_rejected(client):
    token = _register_and_login(client, role="owner")
    response = client.post("/api/v1/knowledge-graph/nodes", json={}, headers=_auth_headers(token))
    assert response.status_code == 422


def test_invalid_node_id_format_rejected(client):
    token = _register_and_login(client, role="owner")
    response = client.get("/api/v1/knowledge-graph/nodes/customer/abc", headers=_auth_headers(token))
    assert response.status_code == 422


# ========== Audit Completeness Tests ==========


def test_mutations_succeed_without_crash(client):
    token = _register_and_login(client, role="owner")

    response = client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "Audit Test"
    }, headers=_auth_headers(token))
    assert response.status_code == 200

    response = client.delete("/api/v1/knowledge-graph/nodes/customer/1", headers=_auth_headers(token))
    assert response.status_code == 200
