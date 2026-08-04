import uuid

import pytest


def _unique_email(role):
    return f"kg_{role}_{uuid.uuid4().hex[:8]}@example.com"


def _register_and_login(client, role="customer"):
    email = _unique_email(role)
    password = "TestPassword123!"

    reg = client.post("/api/v1/auth/register", json={
        "email": email,
        "username": email,
        "full_name": "KG Test User",
        "password": password,
        "phone": "000",
        "company": "TestCo"
    })
    if reg.status_code != 200:
        raise RuntimeError(f"Registration failed: {reg.status_code} {reg.text}")
    user_id = reg.json().get("user_id") or reg.json().get("id")
    owner_resp = client.post("/api/v1/auth/login", json={
        "username": "owner",
        "password": "TestOwnerPass123!"
    })
    assert owner_resp.status_code == 200
    client.post(f"/api/v1/users/{user_id}/approve?role={role}", json={})
    res = client.post("/api/v1/auth/login", json={
        "username": email,
        "password": password
    })
    if res.status_code != 200:
        raise RuntimeError(f"Login failed: {res.status_code} {res.text}")

    user = {
        "email": email,
        "username": email,
        "full_name": "KG Test User",
        "password": password,
    }
    token = res.json()["access_token"]
    return user, token


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ========== Authentication Tests ==========


def test_get_node_requires_authentication(client):
    response = client.get("/api/v1/knowledge-graph/nodes/customer/1")
    assert response.status_code == 401


def test_create_node_requires_authentication(client):
    response = client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "Test"
    })
    assert response.status_code == 401


def test_delete_node_requires_authentication(client):
    response = client.delete("/api/v1/knowledge-graph/nodes/customer/1")
    assert response.status_code == 401


def test_get_relationships_requires_authentication(client):
    response = client.get("/api/v1/knowledge-graph/nodes/customer/1/relationships")
    assert response.status_code == 401


def test_create_edge_requires_authentication(client):
    response = client.post("/api/v1/knowledge-graph/edges", json={
        "source_node_id": "customer:1",
        "target_node_id": "supplier:1",
        "relationship_type": "ref"
    })
    assert response.status_code == 401


def test_delete_edge_requires_authentication(client):
    response = client.delete("/api/v1/knowledge-graph/edges/edge-1")
    assert response.status_code == 401


def test_traverse_requires_authentication(client):
    response = client.get("/api/v1/knowledge-graph/traverse/customer/1")
    assert response.status_code == 401


def test_search_requires_authentication(client):
    response = client.get("/api/v1/knowledge-graph/search?query=test")
    assert response.status_code == 401


def test_sync_requires_authentication(client):
    response = client.post("/api/v1/knowledge-graph/sync")
    assert response.status_code == 401


# ========== Authorization Tests ==========


def test_create_node_forbidden_for_staff(client):
    _, token = _register_and_login(client, role="staff")
    response = client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "Test"
    }, headers=_auth_headers(token))
    assert response.status_code == 403


def test_delete_node_forbidden_for_staff(client):
    _, token = _register_and_login(client, role="staff")
    response = client.delete("/api/v1/knowledge-graph/nodes/customer/1", headers=_auth_headers(token))
    assert response.status_code == 403


def test_create_edge_forbidden_for_staff(client):
    _, token = _register_and_login(client, role="staff")
    response = client.post("/api/v1/knowledge-graph/edges", json={
        "source_node_id": "customer:1",
        "target_node_id": "supplier:1",
        "relationship_type": "ref"
    }, headers=_auth_headers(token))
    assert response.status_code == 403


def test_delete_edge_forbidden_for_staff(client):
    _, token = _register_and_login(client, role="staff")
    response = client.delete("/api/v1/knowledge-graph/edges/edge-1", headers=_auth_headers(token))
    assert response.status_code == 403


def test_sync_forbidden_for_staff(client):
    _, token = _register_and_login(client, role="staff")
    response = client.post("/api/v1/knowledge-graph/sync", headers=_auth_headers(token))
    assert response.status_code == 403


# ========== Node Endpoint Tests ==========


def test_get_node_not_found(client):
    _, token = _register_and_login(client, role="owner")
    response = client.get("/api/v1/knowledge-graph/nodes/customer/999999", headers=_auth_headers(token))
    assert response.status_code == 404


def test_create_and_get_node(client):
    _, token = _register_and_login(client, role="owner")
    create_resp = client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "Integration Test Customer",
        "properties": {"key": "value"}
    }, headers=_auth_headers(token))
    assert create_resp.status_code == 200
    node = create_resp.json()
    assert node["id"] == "customer:1"
    assert node["label"] == "Integration Test Customer"

    get_resp = client.get("/api/v1/knowledge-graph/nodes/customer/1", headers=_auth_headers(token))
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == "customer:1"


def test_update_node_via_upsert(client):
    _, token = _register_and_login(client, role="owner")
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "Original"
    }, headers=_auth_headers(token))

    update_resp = client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "Updated"
    }, headers=_auth_headers(token))
    assert update_resp.status_code == 200
    assert update_resp.json()["label"] == "Updated"


def test_delete_node(client):
    _, token = _register_and_login(client, role="owner")
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "To Delete"
    }, headers=_auth_headers(token))

    delete_resp = client.delete("/api/v1/knowledge-graph/nodes/customer/1", headers=_auth_headers(token))
    assert delete_resp.status_code == 200
    assert "deleted" in delete_resp.json()["message"].lower()

    get_resp = client.get("/api/v1/knowledge-graph/nodes/customer/1", headers=_auth_headers(token))
    assert get_resp.status_code == 404


# ========== Edge Endpoint Tests ==========


def test_create_and_get_edge(client):
    _, token = _register_and_login(client, role="owner")
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "C1"
    }, headers=_auth_headers(token))
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "supplier",
        "entity_id": 1,
        "label": "S1"
    }, headers=_auth_headers(token))

    create_resp = client.post("/api/v1/knowledge-graph/edges", json={
        "source_node_id": "customer:1",
        "target_node_id": "supplier:1",
        "relationship_type": "references_supplier",
        "properties": {"note": "test"}
    }, headers=_auth_headers(token))
    assert create_resp.status_code == 200
    edge = create_resp.json()
    assert edge["source_node_id"] == "customer:1"
    assert edge["target_node_id"] == "supplier:1"
    assert edge["relationship_type"] == "references_supplier"
    assert edge["created_by"] is not None


def test_create_edge_source_not_found(client):
    _, token = _register_and_login(client, role="owner")
    response = client.post("/api/v1/knowledge-graph/edges", json={
        "source_node_id": "missing:1",
        "target_node_id": "supplier:1",
        "relationship_type": "ref"
    }, headers=_auth_headers(token))
    assert response.status_code == 400


def test_create_edge_target_not_found(client):
    _, token = _register_and_login(client, role="owner")
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "C1"
    }, headers=_auth_headers(token))

    response = client.post("/api/v1/knowledge-graph/edges", json={
        "source_node_id": "customer:1",
        "target_node_id": "missing:1",
        "relationship_type": "ref"
    }, headers=_auth_headers(token))
    assert response.status_code == 400


def test_delete_edge(client):
    _, token = _register_and_login(client, role="owner")
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "C1"
    }, headers=_auth_headers(token))
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "supplier",
        "entity_id": 1,
        "label": "S1"
    }, headers=_auth_headers(token))
    create_resp = client.post("/api/v1/knowledge-graph/edges", json={
        "source_node_id": "customer:1",
        "target_node_id": "supplier:1",
        "relationship_type": "ref"
    }, headers=_auth_headers(token))
    edge_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/knowledge-graph/edges/{edge_id}", headers=_auth_headers(token))
    assert delete_resp.status_code == 200
    assert "deleted" in delete_resp.json()["message"].lower()


def test_delete_edge_not_found(client):
    _, token = _register_and_login(client, role="owner")
    response = client.delete("/api/v1/knowledge-graph/edges/nonexistent", headers=_auth_headers(token))
    assert response.status_code == 404


# ========== Relationships Endpoint Tests ==========


def test_get_relationships_returns_derived_and_explicit(client):
    _, token = _register_and_login(client, role="owner")
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "C1"
    }, headers=_auth_headers(token))

    response = client.get("/api/v1/knowledge-graph/nodes/customer/1/relationships", headers=_auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert "node" in data
    assert "relationships" in data
    assert data["node"]["id"] == "customer:1"


def test_get_relationships_not_found(client):
    _, token = _register_and_login(client, role="owner")
    response = client.get("/api/v1/knowledge-graph/nodes/customer/999999/relationships", headers=_auth_headers(token))
    assert response.status_code == 404


# ========== Traverse Endpoint Tests ==========


def test_traverse_node(client):
    _, token = _register_and_login(client, role="owner")
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "C1"
    }, headers=_auth_headers(token))

    response = client.get("/api/v1/knowledge-graph/traverse/customer/1?depth=1", headers=_auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert "depth" in data


def test_traverse_invalid_depth(client):
    _, token = _register_and_login(client, role="owner")
    response = client.get("/api/v1/knowledge-graph/traverse/customer/1?depth=0", headers=_auth_headers(token))
    assert response.status_code == 422


# ========== Search Endpoint Tests ==========


def test_search_nodes(client):
    _, token = _register_and_login(client, role="owner")
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "Searchable Customer"
    }, headers=_auth_headers(token))

    response = client.get("/api/v1/knowledge-graph/search?query=Searchable", headers=_auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_search_nodes_with_entity_type_filter(client):
    _, token = _register_and_login(client, role="owner")
    client.post("/api/v1/knowledge-graph/nodes", json={
        "entity_type": "customer",
        "entity_id": 1,
        "label": "Filtered Customer"
    }, headers=_auth_headers(token))

    response = client.get("/api/v1/knowledge-graph/search?query=Filtered&entity_type=customer", headers=_auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert all(node["entity_type"] == "customer" for node in data)


def test_search_nodes_empty_query(client):
    _, token = _register_and_login(client, role="owner")
    response = client.get("/api/v1/knowledge-graph/search?query=", headers=_auth_headers(token))
    assert response.status_code == 422


# ========== Sync Endpoint Tests ==========


def test_sync_requires_manager_role(client):
    _, token = _register_and_login(client, role="staff")
    response = client.post("/api/v1/knowledge-graph/sync", headers=_auth_headers(token))
    assert response.status_code == 403


def test_sync_with_owner_role(client):
    _, token = _register_and_login(client, role="owner")
    response = client.post("/api/v1/knowledge-graph/sync", headers=_auth_headers(token))
    assert response.status_code == 200
    data = response.json()
    assert "synced_nodes" in data
    assert data["synced_edges"] == 0
    assert isinstance(data["errors"], list)


# ========== KnowledgeProvider Registration Tests ==========


@pytest.mark.asyncio
async def test_knowledge_graph_provider_is_registered():
    from app.agent.knowledge.registry import KnowledgeProviderRegistry
    from app.agent.knowledge.graph_provider import KnowledgeGraphProvider

    registry = KnowledgeProviderRegistry()
    provider = KnowledgeGraphProvider()
    await registry.register(provider)
    assert registry.exists("knowledge-graph")


@pytest.mark.asyncio
async def test_knowledge_graph_provider_get_sources():
    from app.agent.knowledge.graph_provider import KnowledgeGraphProvider

    provider = KnowledgeGraphProvider()
    sources = await provider.get_sources()
    assert isinstance(sources, list)
    assert len(sources) >= 1
    assert sources[0]["id"] == "knowledge-graph"
    assert sources[0]["type"] == "graph"


@pytest.mark.asyncio
async def test_knowledge_graph_provider_query():
    from app.agent.knowledge.graph_provider import KnowledgeGraphProvider

    provider = KnowledgeGraphProvider()
    result = await provider.query("test")
    assert "results" in result
    assert "confidence" in result
    assert "sources" in result
