import uuid

import pytest
from fastapi.testclient import TestClient
from main import app


def _unique_email(role):
    return f"sec_{role}_{uuid.uuid4().hex[:8]}@example.com"


def _register_and_login(client, role="owner"):
    email = _unique_email(role)
    password = "TestPassword123!"

    client.post("/api/v1/auth/register", json={
        "email": email,
        "username": email,
        "full_name": "Security Test User",
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


def test_supplier_analyze_requires_auth(client):
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": 1,
        "analysis_type": "performance",
        "requested_by": "test",
    })
    assert response.status_code == 401


def test_buyer_analyze_requires_auth(client):
    response = client.post("/api/v1/trade-intelligence/buyers/analyze", json={
        "buyer_id": 1,
        "analysis_type": "behavior",
        "requested_by": "test",
    })
    assert response.status_code == 401


def test_trends_detect_requires_auth(client):
    response = client.post("/api/v1/trade-intelligence/trends/detect", json={
        "entity_type": "supplier",
        "trend_parameters": {},
        "requested_by": "test",
    })
    assert response.status_code == 401


def test_compare_requires_auth(client):
    response = client.post("/api/v1/trade-intelligence/compare", json={
        "entity_ids": [1, 2],
        "comparison_criteria": {},
        "requested_by": "test",
    })
    assert response.status_code == 401


def test_reports_generate_requires_auth(client):
    response = client.post("/api/v1/trade-intelligence/reports/generate", json={
        "analysis_ids": ["test-1"],
        "report_type": "summary",
        "requested_by": "test",
    })
    assert response.status_code == 401


# ========== Input Validation Tests ==========


def test_supplier_analyze_validates_positive_supplier_id(client):
    token = _register_and_login(client, "owner")
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": 0,
        "analysis_type": "performance",
        "requested_by": "test",
    }, headers=_auth_headers(token))
    assert response.status_code == 422


def test_buyer_analyze_validates_positive_buyer_id(client):
    token = _register_and_login(client, "owner")
    response = client.post("/api/v1/trade-intelligence/buyers/analyze", json={
        "buyer_id": -1,
        "analysis_type": "behavior",
        "requested_by": "test",
    }, headers=_auth_headers(token))
    assert response.status_code == 422


def test_compare_validates_min_two_entities(client):
    token = _register_and_login(client, "owner")
    response = client.post("/api/v1/trade-intelligence/compare", json={
        "entity_ids": [1],
        "comparison_criteria": {},
        "requested_by": "test",
    }, headers=_auth_headers(token))
    assert response.status_code == 422


def test_report_generate_validates_non_empty_analysis_ids(client):
    token = _register_and_login(client, "owner")
    response = client.post("/api/v1/trade-intelligence/reports/generate", json={
        "analysis_ids": [],
        "report_type": "summary",
        "requested_by": "test",
    }, headers=_auth_headers(token))
    assert response.status_code == 422


# ========== Error Response Contract Tests ==========


def test_error_response_has_required_fields(client):
    token = _register_and_login(client, "owner")
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": 999999,
        "analysis_type": "performance",
        "requested_by": "test",
    }, headers=_auth_headers(token))
    assert response.status_code == 404
    data = response.json()
    detail = data.get("detail", data)
    assert "error_code" in detail
    assert "category" in detail
    assert "message" in detail
    assert "caller_action" in detail


def test_error_response_category_maps_to_status_code(client):
    token = _register_and_login(client, "owner")
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": 999999,
        "analysis_type": "performance",
        "requested_by": "test",
    }, headers=_auth_headers(token))
    assert response.status_code == 404


# ========== Audit Completeness Tests ==========


def test_analysis_is_audited(client):
    token = _register_and_login(client, "owner")
    client.post("/api/v1/suppliers/", json={"name": "Audit Supplier", "country": "Egypt"}, headers=_auth_headers(token))
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": 1,
        "analysis_type": "performance",
        "requested_by": "test",
    }, headers=_auth_headers(token))
    assert response.status_code == 200


# ========== No Data Modification Tests ==========


def test_analysis_does_not_modify_supplier(client):
    token = _register_and_login(client, "owner")
    create_resp = client.post("/api/v1/suppliers/", json={
        "name": "Immutable Supplier",
        "country": "Egypt",
    }, headers=_auth_headers(token))
    supplier_id = create_resp.json()["id"]

    client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": supplier_id,
        "analysis_type": "performance",
        "requested_by": "test",
    }, headers=_auth_headers(token))

    get_resp = client.get(f"/api/v1/suppliers/{supplier_id}", headers=_auth_headers(token))
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Immutable Supplier"


# ========== SQL Injection Prevention ==========


def test_supplier_analyze_prevents_sql_injection(client):
    token = _register_and_login(client, "owner")
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": 1,
        "analysis_type": "performance' OR '1'='1",
        "requested_by": "test",
    }, headers=_auth_headers(token))
    assert response.status_code == 200
