import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.tradedata_provider import TradeDataExternalSourceAdapter
from app.agent.knowledge.tradedata_client import TradeDataApiClient


class TestTradeDataAdapterContract:
    """Verify TradeData external source adapter contract boundaries."""

    def test_get_sources_returns_registry_compatible_entry(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "source_id": "tradedata",
                "name": "TradeData API",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-13T00:00:00Z",
            }
        )

        sources = asyncio.run(adapter.get_sources())
        assert len(sources) == 1
        source = sources[0]
        assert source["id"] == "tradedata"
        assert source["name"] == "TradeData API"
        assert source["type"] == "external_trade_intelligence"
        assert source["version"] == "1.0"
        assert source["updated_at"] == "2026-08-13T00:00:00Z"

    def test_default_source_metadata_when_config_is_empty(self):
        adapter = TradeDataExternalSourceAdapter()

        sources = asyncio.run(adapter.get_sources())
        assert sources[0]["id"] == "tradedata"
        assert sources[0]["type"] == "external_trade_intelligence"


class TestTradeDataAdapterQuery:
    """Verify TradeData adapter query transformation and error handling."""

    def test_successful_response_transforms_to_contract_shape(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "test-key",
                "source_id": "tradedata",
                "name": "TradeData API",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-13T00:00:00Z",
            }
        )

        raw_response = {
            "code": 200,
            "success": True,
            "data": [
                {
                    "dataSource": "United States_Import",
                    "date": "2025-08-22",
                    "buyerName": "Target Corporation",
                    "supplierName": "Samsung Electronics",
                    "originCountryCode": "KR",
                    "destinationCountryCode": "US",
                    "hsCode": "854231",
                    "hsCodeDesc": "Electronic integrated circuits",
                    "productKeyword": "smartphone",
                    "quantity": 500,
                    "weight": 120.0,
                    "tradeAmount": 999950.0,
                    "masterBl": "MAEU123456789",
                    "containerNo": "SEGU1234567",
                    "otherInfo": {"billType": "Regular Bill"},
                }
            ],
            "total": 1,
            "pageSize": 10,
            "current": 1,
        }

        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("smartphone", context={"country": "US"}, scope="tradeDetail", limit=10)
            )

        assert "results" in result
        assert "confidence" in result
        assert "sources" in result
        assert result["sources"] == ["tradedata"]
        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["source_id"] == "tradedata"
        assert 0.0 <= item["confidence"] <= 1.0
        assert "id" in item
        assert "content" in item
        assert "metadata" in item
        assert item["metadata"]["source_authority"] == "United States_Import"
        assert item["metadata"]["effective_date"] == "2025-08-22"
        assert item["metadata"]["country"] == "US"
        assert item["metadata"]["retrieval_status"] == "success"

    def test_empty_response_returns_empty_results(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "test-key",
            }
        )

        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, return_value={"code": 200, "data": []}):
            result = asyncio.run(
                adapter.query("test", context={"country": "US"}, scope="tradeDetail", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["tradedata"]

    def test_malformed_response_returns_empty_results(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "test-key",
            }
        )

        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, return_value="not-a-dict"):
            result = asyncio.run(
                adapter.query("test", context={"country": "US"}, scope="tradeDetail", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["tradedata"]

    def test_authentication_failure_returns_empty_results(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "test-key",
            }
        )

        import httpx
        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, side_effect=httpx.HTTPStatusError("Unauthorized", request=None, response=None)):
            result = asyncio.run(
                adapter.query("test", context={"country": "US"}, scope="tradeDetail", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["tradedata"]

    def test_upstream_failure_returns_empty_results(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "test-key",
            }
        )

        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            result = asyncio.run(
                adapter.query("test", context={"country": "US"}, scope="tradeDetail", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["tradedata"]

    def test_missing_country_context_returns_empty_results(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "test-key",
            }
        )

        result = asyncio.run(
            adapter.query("test", context={}, scope="tradeDetail", limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["tradedata"]

    def test_configuration_without_base_url_skips_api_call(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "api_key": "test-key",
            }
        )

        result = asyncio.run(
            adapter.query("test", context={"country": "US"}, scope="tradeDetail", limit=10)
        )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["tradedata"]

    def test_confidence_scores_within_valid_range(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "test-key",
            }
        )

        raw_response = {
            "code": 200,
            "success": True,
            "data": [
                {
                    "dataSource": "United States_Import",
                    "date": "2025-08-22",
                    "buyerName": "Target Corporation",
                    "supplierName": "Samsung Electronics",
                    "originCountryCode": "KR",
                    "destinationCountryCode": "US",
                    "hsCode": "854231",
                    "hsCodeDesc": "Electronic integrated circuits",
                    "productKeyword": "smartphone",
                    "quantity": 500,
                    "weight": 120.0,
                    "tradeAmount": 999950.0,
                    "masterBl": "MAEU123456789",
                    "containerNo": "SEGU1234567",
                    "otherInfo": {"billType": "Regular Bill"},
                }
            ],
            "total": 1,
            "pageSize": 10,
            "current": 1,
        }

        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("smartphone", context={"country": "US"}, scope="tradeDetail", limit=10)
            )

        assert 0.0 <= result["confidence"] <= 1.0
        for item in result["results"]:
            assert 0.0 <= item["confidence"] <= 1.0

    def test_provenance_metadata_populated(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "test-key",
                "source_id": "tradedata",
                "version": "1.0",
                "updated_at": "2026-08-13T00:00:00Z",
            }
        )

        raw_response = {
            "code": 200,
            "success": True,
            "data": [
                {
                    "dataSource": "United States_Import",
                    "date": "2025-08-22",
                    "buyerName": "Target Corporation",
                    "supplierName": "Samsung Electronics",
                    "originCountryCode": "KR",
                    "destinationCountryCode": "US",
                    "hsCode": "854231",
                    "hsCodeDesc": "Electronic integrated circuits",
                    "productKeyword": "smartphone",
                    "quantity": 500,
                    "weight": 120.0,
                    "tradeAmount": 999950.0,
                    "masterBl": "MAEU123456789",
                    "containerNo": "SEGU1234567",
                    "otherInfo": {"billType": "Regular Bill"},
                }
            ],
            "total": 1,
            "pageSize": 10,
            "current": 1,
        }

        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("smartphone", context={"country": "US"}, scope="tradeDetail", limit=10)
            )

        item = result["results"][0]
        assert item["metadata"]["source_authority"] == "United States_Import"
        assert item["metadata"]["effective_date"] == "2025-08-22"
        assert item["metadata"]["country"] == "US"
        assert item["metadata"]["source_url"] == "MAEU123456789"
        assert item["metadata"]["legal_act_reference"] == "{'billType': 'Regular Bill'}"
        assert item["metadata"]["updated_at"] == "2026-08-13T00:00:00Z"
        assert item["metadata"]["version"] == "1.0"
        assert "record_hash" in item["metadata"]
        assert item["metadata"]["retrieval_status"] == "success"

    def test_configuration_settings_loaded(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "test-key",
                "source_id": "tradedata",
                "name": "TradeData API",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-13T00:00:00Z",
                "timeout_seconds": 45.0,
            }
        )

        assert adapter._source_id == "tradedata"
        assert adapter._provider_name == "TradeData API"
        assert adapter._provider_type == "external_trade_intelligence"
        assert adapter._version == "1.0"
        assert adapter._updated_at == "2026-08-13T00:00:00Z"
        assert adapter._client._timeout_seconds == 45.0

    def test_retry_backoff_on_rate_limit(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "test-key",
            }
        )

        import httpx
        error_response = httpx.Response(429, request=None)
        success_response = {
            "code": 200,
            "success": True,
            "data": [],
            "total": 0,
            "pageSize": 10,
            "current": 1,
        }

        responses = [error_response, success_response]
        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, side_effect=lambda **kwargs: responses.pop(0)):
            result = asyncio.run(
                adapter.query("test", context={"country": "US"}, scope="tradeDetail", limit=10)
            )

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["tradedata"]

    def test_hs_code_only_record_gets_low_confidence(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "test-key",
            }
        )

        raw_response = {
            "code": 200,
            "success": True,
            "data": [
                {
                    "hsCode": "854231",
                    "hsCodeDesc": "Electronic integrated circuits",
                }
            ],
            "total": 1,
            "pageSize": 10,
            "current": 1,
        }

        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(
                adapter.query("smartphone", context={"country": "US"}, scope="tradeDetail", limit=10)
            )

        assert len(result["results"]) == 1
        assert result["results"][0]["confidence"] == 0.65
        assert result["results"][0]["metadata"]["retrieval_status"] == "partial"
