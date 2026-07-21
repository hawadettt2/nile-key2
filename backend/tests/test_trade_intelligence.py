import uuid

import pytest


def _unique_credentials(role="staff"):
    """Generate unique credentials for each test to avoid collisions."""
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


# ========== Supplier Analysis Endpoints ==========


def test_analyze_supplier_authorized(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": 1,
        "analysis_type": "performance",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (200, 404)


def test_analyze_supplier_unauthorized(client):
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": 1,
        "analysis_type": "performance",
        "requested_by": "test",
    })
    assert response.status_code == 401


def test_analyze_supplier_creates_supplier_then_analyzes(client):
    token, _ = _register_and_login(client, role="owner")
    create_resp = client.post("/api/v1/suppliers/", json={
        "name": "Test Supplier",
        "country": "Egypt",
    }, headers={"Authorization": f"Bearer {token}"})
    supplier_id = create_resp.json()["id"]
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": supplier_id,
        "analysis_type": "performance",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "insights" in data
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0


def test_analyze_supplier_not_found_returns_404(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": 999999,
        "analysis_type": "performance",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


# ========== Buyer Analysis Endpoints ==========


def test_analyze_buyer_authorized(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/buyers/analyze", json={
        "buyer_id": 1,
        "analysis_type": "behavior",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (200, 404)


def test_analyze_buyer_unauthorized(client):
    response = client.post("/api/v1/trade-intelligence/buyers/analyze", json={
        "buyer_id": 1,
        "analysis_type": "behavior",
        "requested_by": "test",
    })
    assert response.status_code == 401


def test_analyze_buyer_not_found_returns_404(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/buyers/analyze", json={
        "buyer_id": 999999,
        "analysis_type": "behavior",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404


# ========== Trends Detection Endpoints ==========


def test_detect_trends_authorized(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/trends/detect", json={
        "entity_type": "supplier",
        "trend_parameters": {},
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "insights" in data


def test_detect_trends_unauthorized(client):
    response = client.post("/api/v1/trade-intelligence/trends/detect", json={
        "entity_type": "supplier",
        "trend_parameters": {},
        "requested_by": "test",
    })
    assert response.status_code == 401


def test_detect_trends_unsupported_entity_returns_error(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/trends/detect", json={
        "entity_type": "unsupported_type",
        "trend_parameters": {},
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422
    data = response.json()
    assert data["detail"]["error_code"] == "unsupported_entity_type"


# ========== Comparison Endpoints ==========


def test_compare_entities_authorized(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/compare", json={
        "entity_ids": [1, 2],
        "comparison_criteria": {},
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (200, 404)


def test_compare_entities_unauthorized(client):
    response = client.post("/api/v1/trade-intelligence/compare", json={
        "entity_ids": [1, 2],
        "comparison_criteria": {},
        "requested_by": "test",
    })
    assert response.status_code == 401


def test_compare_entities_not_enough_returns_error(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/compare", json={
        "entity_ids": [1],
        "comparison_criteria": {},
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


# ========== Report Generation Endpoints ==========


def test_generate_report_authorized(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/reports/generate", json={
        "analysis_ids": ["test-analysis-1"],
        "report_type": "summary",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert "sections" in data
    assert "content" in data
    assert "csv" in data["content"]
    assert "pdf" in data["content"]


def test_generate_report_unauthorized(client):
    response = client.post("/api/v1/trade-intelligence/reports/generate", json={
        "analysis_ids": ["test-analysis-1"],
        "report_type": "summary",
        "requested_by": "test",
    })
    assert response.status_code == 401


def test_generate_report_empty_analysis_ids_returns_error(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/reports/generate", json={
        "analysis_ids": [],
        "report_type": "summary",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


# ========== Perform Analysis Dispatcher ==========


def test_perform_analysis_authorized(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post(
        "/api/v1/trade-intelligence/perform-analysis?analysis_type=supplier",
        json={
            "supplier_id": 1,
            "analysis_type": "performance",
            "requested_by": "test",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 404)


def test_perform_analysis_unauthorized(client):
    response = client.post(
        "/api/v1/trade-intelligence/perform-analysis?analysis_type=supplier",
        json={
            "supplier_id": 1,
            "analysis_type": "performance",
            "requested_by": "test",
        }
    )
    assert response.status_code == 401


def test_perform_analysis_missing_analysis_type_returns_422(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post(
        "/api/v1/trade-intelligence/perform-analysis",
        json={
            "supplier_id": 1,
            "analysis_type": "performance",
            "requested_by": "test",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


# ========== Input Validation ==========


def test_analyze_supplier_missing_supplier_id_returns_422(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "analysis_type": "performance",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


def test_analyze_buyer_missing_buyer_id_returns_422(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/buyers/analyze", json={
        "analysis_type": "behavior",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


def test_compare_missing_entity_ids_returns_422(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/compare", json={
        "comparison_criteria": {},
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


def test_generate_report_missing_analysis_ids_returns_422(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/reports/generate", json={
        "report_type": "summary",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


# ========== Role-based Access ==========


def test_all_endpoints_require_authentication(client):
    endpoints = [
        ("/api/v1/trade-intelligence/suppliers/analyze", "post", {"supplier_id": 1, "analysis_type": "performance", "requested_by": "test"}),
        ("/api/v1/trade-intelligence/buyers/analyze", "post", {"buyer_id": 1, "analysis_type": "behavior", "requested_by": "test"}),
        ("/api/v1/trade-intelligence/trends/detect", "post", {"entity_type": "supplier", "trend_parameters": {}, "requested_by": "test"}),
        ("/api/v1/trade-intelligence/compare", "post", {"entity_ids": [1, 2], "comparison_criteria": {}, "requested_by": "test"}),
        ("/api/v1/trade-intelligence/reports/generate", "post", {"analysis_ids": ["a1"], "report_type": "summary", "requested_by": "test"}),
    ]
    for path, method, json_data in endpoints:
        if method == "post":
            response = client.post(path, json=json_data)
        assert response.status_code == 401


# ========== Response Structure Validation ==========


def test_analyze_supplier_response_structure(client):
    token, _ = _register_and_login(client, role="owner")
    client.post("/api/v1/suppliers/", json={"name": "Test Supplier", "country": "Egypt"}, headers={"Authorization": f"Bearer {token}"})
    response = client.post("/api/v1/trade-intelligence/suppliers/analyze", json={
        "supplier_id": 1,
        "analysis_type": "performance",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "insights" in data
    assert "generated_at" in data
    assert "confidence" in data
    assert "data_sources" in data
    insight = data["insights"][0]
    assert "finding" in insight
    assert "confidence" in insight
    assert "evidence" in insight
    assert "sources" in insight
    assert "analysis_id" in insight


def test_generate_report_response_structure(client):
    token, _ = _register_and_login(client, role="owner")
    response = client.post("/api/v1/trade-intelligence/reports/generate", json={
        "analysis_ids": ["test-1"],
        "report_type": "summary",
        "requested_by": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "report_id" in data
    assert "report_type" in data
    assert "format" in data
    assert "sections" in data
    assert "content" in data
    assert "generated_at" in data
    assert "metadata" in data
