import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.zatca_provider import ZatcaExternalSourceAdapter
from app.agent.knowledge.zatca_client import ZatcaApiClient


class TestZatcaAdapterContract:
    """Verify ZATCA external source adapter contract boundaries."""

    def test_get_sources_returns_registry_compatible_entry(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "source_id": "zatca",
                "name": "ZATCA Open Data APIs",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        sources = asyncio.run(adapter.get_sources())
        assert len(sources) == 1
        source = sources[0]
        assert source["id"] == "zatca"
        assert source["name"] == "ZATCA Open Data APIs"
        assert source["type"] == "external_trade_intelligence"
        assert source["version"] == "1.0"
        assert source["updated_at"] == "2026-08-14T00:00:00Z"

    def test_default_source_metadata_when_config_is_empty(self):
        adapter = ZatcaExternalSourceAdapter()

        sources = asyncio.run(adapter.get_sources())
        assert sources[0]["id"] == "zatca"
        assert sources[0]["type"] == "external_trade_intelligence"


class TestZatcaAdapterQuery:
    """Verify ZATCA adapter query transformation and error handling."""

    def test_successful_list_response_transforms_to_contract_shape(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "base_url": "https://api.zatca.gov.sa",
                "api_key": "test-key",
                "source_id": "zatca",
                "name": "ZATCA Open Data APIs",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        raw_response = {
            "data": [
                {
                    "description": "Electronics import declaration",
                    "date": "2025-08-22",
                    "country": "SA",
                    "port_name": "Jeddah",
                    "traffic_type": "import",
                    "quantity": 500,
                    "weight": 120.0,
                    "amount": 999950.0,
                    "endpoint": "/api/v1/export-import-details",
                }
            ],
            "total": 1,
        }

        with patch.object(ZatcaApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("electronics", context={"country": "SA"}, scope="export_import_details", limit=10)
            )

        assert "results" in result
        assert "confidence" in result
        assert "sources" in result
        assert result["sources"] == ["zatca"]
        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["source_id"] == "zatca"
        assert 0.0 <= item["confidence"] <= 1.0
        assert "id" in item
        assert "content" in item
        assert "metadata" in item
        assert item["metadata"]["source_authority"] == "ZATCA_OpenData"
        assert item["metadata"]["effective_date"] == "2025-08-22"
        assert item["metadata"]["country"] == "SA"
        assert item["metadata"]["retrieval_status"] == "success"

    def test_empty_response_returns_empty_results(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "base_url": "https://api.zatca.gov.sa",
                "api_key": "test-key",
            }
        )

        with patch.object(ZatcaApiClient, "request", new_callable=AsyncMock, return_value={"code": 200, "data": []}):
            result = asyncio.run(
                adapter.query("test", context={"country": "SA"}, scope="export_import_details", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["zatca"]

    def test_non_dict_response_returns_empty_results(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "base_url": "https://api.zatca.gov.sa",
                "api_key": "test-key",
            }
        )

        with patch.object(ZatcaApiClient, "request", new_callable=AsyncMock, return_value="not-a-dict"):
            result = asyncio.run(
                adapter.query("test", context={"country": "SA"}, scope="export_import_details", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["zatca"]

    def test_authentication_failure_returns_empty_results(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "base_url": "https://api.zatca.gov.sa",
                "api_key": "test-key",
            }
        )

        import httpx
        with patch.object(ZatcaApiClient, "request", new_callable=AsyncMock, side_effect=httpx.HTTPStatusError("Unauthorized", request=None, response=None)):
            result = asyncio.run(
                adapter.query("test", context={"country": "SA"}, scope="export_import_details", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["zatca"]

    def test_upstream_failure_returns_empty_results(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "base_url": "https://api.zatca.gov.sa",
                "api_key": "test-key",
            }
        )

        with patch.object(ZatcaApiClient, "request", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            result = asyncio.run(
                adapter.query("test", context={"country": "SA"}, scope="export_import_details", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["zatca"]

    def test_missing_country_context_returns_empty_results(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "base_url": "https://api.zatca.gov.sa",
                "api_key": "test-key",
            }
        )

        result = asyncio.run(
            adapter.query("test", context={}, scope="export_import_details", limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["zatca"]

    def test_configuration_without_base_url_skips_api_call(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "api_key": "test-key",
            }
        )

        result = asyncio.run(
            adapter.query("test", context={"country": "SA"}, scope="export_import_details", limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["zatca"]

    def test_confidence_scores_within_valid_range(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "base_url": "https://api.zatca.gov.sa",
                "api_key": "test-key",
            }
        )

        raw_response = {
            "data": [
                {
                    "description": "Electronics import declaration",
                    "date": "2025-08-22",
                    "country": "SA",
                    "port_name": "Jeddah",
                    "traffic_type": "import",
                    "quantity": 500,
                    "weight": 120.0,
                    "amount": 999950.0,
                    "endpoint": "/api/v1/export-import-details",
                }
            ],
            "total": 1,
        }

        with patch.object(ZatcaApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("electronics", context={"country": "SA"}, scope="export_import_details", limit=10)
            )

        assert 0.0 <= result["confidence"] <= 1.0
        for item in result["results"]:
            assert 0.0 <= item["confidence"] <= 1.0

    def test_provenance_metadata_populated(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "base_url": "https://api.zatca.gov.sa",
                "api_key": "test-key",
                "source_id": "zatca",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        raw_response = {
            "data": [
                {
                    "description": "Electronics import declaration",
                    "date": "2025-08-22",
                    "country": "SA",
                    "port_name": "Jeddah",
                    "traffic_type": "import",
                    "quantity": 500,
                    "weight": 120.0,
                    "amount": 999950.0,
                    "endpoint": "/api/v1/export-import-details",
                }
            ],
            "total": 1,
        }

        with patch.object(ZatcaApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("electronics", context={"country": "SA"}, scope="export_import_details", limit=10)
            )

        item = result["results"][0]
        assert item["metadata"]["source_authority"] == "ZATCA_OpenData"
        assert item["metadata"]["effective_date"] == "2025-08-22"
        assert item["metadata"]["country"] == "SA"
        assert item["metadata"]["source_url"] == "/api/v1/export-import-details"
        assert item["metadata"]["updated_at"] == "2026-08-14T00:00:00Z"
        assert item["metadata"]["version"] == "1.0"
        assert "record_hash" in item["metadata"]
        assert item["metadata"]["retrieval_status"] == "success"

    def test_configuration_settings_loaded(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "base_url": "https://api.zatca.gov.sa",
                "api_key": "test-key",
                "source_id": "zatca",
                "name": "ZATCA Open Data APIs",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
                "timeout_seconds": 45.0,
            }
        )

        assert adapter._source_id == "zatca"
        assert adapter._provider_name == "ZATCA Open Data APIs"
        assert adapter._provider_type == "external_trade_intelligence"
        assert adapter._version == "1.0"
        assert adapter._updated_at == "2026-08-14T00:00:00Z"
        assert adapter._client._timeout_seconds == 45.0

    def test_retry_backoff_on_rate_limit(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "base_url": "https://api.zatca.gov.sa",
                "api_key": "test-key",
            }
        )

        import httpx
        error_response = httpx.Response(429, request=None)
        success_response = {
            "data": [],
            "total": 0,
        }

        responses = [error_response, success_response]
        with patch.object(ZatcaApiClient, "request", new_callable=AsyncMock, side_effect=lambda **kwargs: responses.pop(0)):
            result = asyncio.run(
                adapter.query("test", context={"country": "SA"}, scope="export_import_details", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["zatca"]
