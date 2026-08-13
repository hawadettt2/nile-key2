import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.provider import KnowledgeProvider
from app.agent.knowledge.tradedata_provider import TradeDataExternalSourceAdapter
from app.agent.knowledge.tradedata_client import TradeDataApiClient
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.knowledge.regulations_provider import RegulationsKnowledgeProvider
from app.agent.decision_engine.engine import ReasoningEngine


class TestTradeDataAdapterIntegration:
    """Integration tests for TradeData external source adapter bootstrap registration."""

    def test_adapter_registers_in_registry(self):
        registry = KnowledgeProviderRegistry()
        adapter = TradeDataExternalSourceAdapter(
            config={
                "source_id": "tradedata",
                "name": "TradeData API",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-13T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))
        sources = asyncio.run(registry.list_providers())
        assert any(s["id"] == "tradedata" for s in sources)

    def test_adapter_is_queryable_via_registry(self):
        registry = KnowledgeProviderRegistry()
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
        asyncio.run(registry.register(adapter))

        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, return_value={
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
        }):
            result = asyncio.run(registry.query("tradedata", "smartphone", context={"country": "US"}))

        assert "results" in result
        assert result["sources"] == ["tradedata"]

    def test_existing_providers_still_register_after_tradedata(self):
        registry = KnowledgeProviderRegistry()
        tradedata_adapter = TradeDataExternalSourceAdapter(
            config={
                "source_id": "tradedata",
                "name": "TradeData API",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-13T00:00:00Z",
            }
        )
        regulations_provider = RegulationsKnowledgeProvider(file_path="backend/data/regulations.json")

        asyncio.run(registry.register(tradedata_adapter))
        asyncio.run(registry.register(regulations_provider))

        sources = asyncio.run(registry.list_providers())
        assert any(s["id"] == "tradedata" for s in sources)
        assert any(s["id"] == "regulations" for s in sources)

    def test_graceful_degradation_does_not_crash_startup(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "base_url": "https://api.tradedata.io",
                "api_key": "invalid-key",
                "source_id": "tradedata",
                "name": "TradeData API",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-13T00:00:00Z",
            }
        )

        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            result = asyncio.run(adapter.query("test", context={"country": "US"}, scope="tradeDetail", limit=10))

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["tradedata"]

    def test_adapter_provider_interface_compliance(self):
        adapter = TradeDataExternalSourceAdapter(
            config={
                "source_id": "tradedata",
                "name": "TradeData API",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-13T00:00:00Z",
            }
        )

        assert isinstance(adapter, KnowledgeProvider)
        assert hasattr(adapter, "query")
        assert hasattr(adapter, "get_sources")

        sources = asyncio.run(adapter.get_sources())
        assert len(sources) == 1
        assert sources[0]["id"] == "tradedata"
        assert sources[0]["type"] == "external_trade_intelligence"

    def test_registry_returns_tradedata_results_with_correct_shape(self):
        registry = KnowledgeProviderRegistry()
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
        asyncio.run(registry.register(adapter))

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
            result = asyncio.run(registry.query("tradedata", "smartphone", context={"country": "US"}))

        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["source_id"] == "tradedata"
        assert "id" in item
        assert "content" in item
        assert "confidence" in item
        assert "metadata" in item
        assert item["metadata"]["source_authority"] == "United States_Import"
        assert item["metadata"]["effective_date"] == "2025-08-22"
        assert item["metadata"]["country"] == "US"
        assert item["metadata"]["retrieval_status"] == "success"
        assert isinstance(item["metadata"]["record_hash"], str)

    def test_reasoning_engine_can_query_tradedata_provider_through_registry(self):
        registry = KnowledgeProviderRegistry()
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
        asyncio.run(registry.register(adapter))

        reasoning_engine = ReasoningEngine(knowledge_provider_registry=registry)

        with patch.object(TradeDataApiClient, "trade_detail", new_callable=AsyncMock, return_value={
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
        }):
            knowledge = asyncio.run(reasoning_engine._query_knowledge("smartphone", {"country": "US"}))

        assert len(knowledge) == 1
        assert knowledge[0]["source_id"] == "tradedata"
        assert "id" in knowledge[0]
        assert "content" in knowledge[0]
        assert "metadata" in knowledge[0]
