import time
import uuid

import pytest


def _unique_email(role):
    return f"perf_{role}_{uuid.uuid4().hex[:8]}@example.com"


def _register_and_login(client, role="owner"):
    email = _unique_email(role)
    password = "TestPassword123!"

    client.post("/api/v1/auth/register", json={
        "email": email,
        "username": email,
        "full_name": "Perf Test User",
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


# ========== Node Lookup Performance ==========


def test_get_node_latency(client):
    token = _register_and_login(client, role="owner")
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "Perf Customer"
    }, headers=_auth_headers(token))

    start = time.perf_counter()
    response = client.get("/api/v1/knowledge-graph/nodes/customer/1", headers=_auth_headers(token))
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 0.5


# ========== Search Performance ==========


def test_search_nodes_latency(client):
    token = _register_and_login(client, role="owner")
    for i in range(10):
        client.post("/api/v1/knowledge-graph/nodes", json={
            "entity_type": "customer",
            "entity_id": i + 1,
            "label": f"Perf Customer {i}"
        }, headers=_auth_headers(token))

    start = time.perf_counter()
    response = client.get("/api/v1/knowledge-graph/search?query=Perf", headers=_auth_headers(token))
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 1.0


# ========== Traversal Performance ==========


def test_traverse_latency(client):
    token = _register_and_login(client, role="owner")
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "Perf Customer"
    }, headers=_auth_headers(token))

    start = time.perf_counter()
    response = client.get("/api/v1/knowledge-graph/traverse/customer/1?depth=2", headers=_auth_headers(token))
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 1.0


# ========== Bulk Sync Performance ==========


def test_sync_latency(client):
    token = _register_and_login(client, role="owner")
    start = time.perf_counter()
    response = client.post("/api/v1/knowledge-graph/sync", headers=_auth_headers(token))
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 5.0
