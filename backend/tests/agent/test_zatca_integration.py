import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.provider import KnowledgeProvider
from app.agent.knowledge.zatca_provider import ZatcaExternalSourceAdapter
from app.agent.knowledge.zatca_client import ZatcaApiClient
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.knowledge.regulations_provider import RegulationsKnowledgeProvider
from app.agent.decision_engine.engine import ReasoningEngine


class TestZatcaAdapterIntegration:
    """Integration tests for ZATCA external source adapter bootstrap registration."""

    def test_adapter_registers_in_registry(self):
        registry = KnowledgeProviderRegistry()
        adapter = ZatcaExternalSourceAdapter(
            config={
                "source_id": "zatca",
                "name": "ZATCA Open Data APIs",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))
        sources = asyncio.run(registry.list_providers())
        assert any(s["id"] == "zatca" for s in sources)

    def test_adapter_is_queryable_via_registry(self):
        registry = KnowledgeProviderRegistry()
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
        asyncio.run(registry.register(adapter))

        with patch.object(ZatcaApiClient, "request", new_callable=AsyncMock, return_value={
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
        }):
            result = asyncio.run(registry.query("zatca", "electronics", context={"country": "SA"}))

        assert "results" in result
        assert result["sources"] == ["zatca"]

    def test_existing_providers_still_register_after_zatca(self):
        registry = KnowledgeProviderRegistry()
        zatca_adapter = ZatcaExternalSourceAdapter(
            config={
                "source_id": "zatca",
                "name": "ZATCA Open Data APIs",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )
        regulations_provider = RegulationsKnowledgeProvider(file_path="backend/data/regulations.json")

        asyncio.run(registry.register(zatca_adapter))
        asyncio.run(registry.register(regulations_provider))

        sources = asyncio.run(registry.list_providers())
        assert any(s["id"] == "zatca" for s in sources)
        assert any(s["id"] == "regulations" for s in sources)

    def test_graceful_degradation_does_not_crash_startup(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "base_url": "https://api.zatca.gov.sa",
                "api_key": "invalid-key",
                "source_id": "zatca",
                "name": "ZATCA Open Data APIs",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        with patch.object(ZatcaApiClient, "request", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            result = asyncio.run(adapter.query("test", context={"country": "SA"}, scope="export_import_details", limit=10))

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["zatca"]

    def test_adapter_provider_interface_compliance(self):
        adapter = ZatcaExternalSourceAdapter(
            config={
                "source_id": "zatca",
                "name": "ZATCA Open Data APIs",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        assert isinstance(adapter, KnowledgeProvider)
        assert hasattr(adapter, "query")
        assert hasattr(adapter, "get_sources")

        sources = asyncio.run(adapter.get_sources())
        assert len(sources) == 1
        assert sources[0]["id"] == "zatca"
        assert sources[0]["type"] == "external_trade_intelligence"

    def test_registry_returns_zatca_results_with_correct_shape(self):
        registry = KnowledgeProviderRegistry()
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
        asyncio.run(registry.register(adapter))

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
            result = asyncio.run(registry.query("zatca", "electronics", context={"country": "SA"}))

        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["source_id"] == "zatca"
        assert "id" in item
        assert "content" in item
        assert "confidence" in item
        assert "metadata" in item
        assert item["metadata"]["source_authority"] == "ZATCA_OpenData"
        assert item["metadata"]["effective_date"] == "2025-08-22"
        assert item["metadata"]["country"] == "SA"
        assert item["metadata"]["retrieval_status"] == "success"
        assert isinstance(item["metadata"]["record_hash"], str)
