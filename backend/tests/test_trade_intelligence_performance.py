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


# ========== Supplier Analysis Performance ==========


def test_analyze_supplier_latency(client):
    token = _register_and_login(client, role="owner")
    client.post("/api/v1/suppliers/", json={
        "name": "Perf Supplier",
        "country": "Egypt",
    }, headers=_auth_headers(token))

    start = time.perf_counter()
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": 1,
        "analysis_type": "performance",
        "requested_by": "perf_test",
    }, headers=_auth_headers(token))
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 2.0


# ========== Buyer Analysis Performance ==========


def test_analyze_buyer_latency(client):
    token = _register_and_login(client, role="owner")
    start = time.perf_counter()
    response = client.post("/api/v1/trade-intelligence/buyers/analyze", json={
        "buyer_id": 1,
        "analysis_type": "behavior",
        "requested_by": "perf_test",
    }, headers=_auth_headers(token))
    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 404)
    assert elapsed < 2.0


# ========== Trends Detection Performance ==========


def test_detect_trends_latency(client):
    token = _register_and_login(client, role="owner")
    start = time.perf_counter()
    response = client.post("/api/v1/trade-intelligence/trends/detect", json={
        "entity_type": "supplier",
        "trend_parameters": {},
        "requested_by": "perf_test",
    }, headers=_auth_headers(token))
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 2.0


# ========== Comparison Performance ==========


def test_compare_entities_latency(client):
    token = _register_and_login(client, role="owner")
    start = time.perf_counter()
    response = client.post("/api/v1/trade-intelligence/compare", json={
        "entity_ids": [1, 2],
        "comparison_criteria": {},
        "requested_by": "perf_test",
    }, headers=_auth_headers(token))
    elapsed = time.perf_counter() - start

    assert response.status_code in (200, 404)
    assert elapsed < 2.0


# ========== Report Generation Performance ==========


def test_generate_report_latency(client):
    token = _register_and_login(client, role="owner")
    start = time.perf_counter()
    response = client.post("/api/v1/trade-intelligence/reports/generate", json={
        "analysis_ids": ["perf-test-1"],
        "report_type": "summary",
        "requested_by": "perf_test",
    }, headers=_auth_headers(token))
    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 5.0
