import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.provider import KnowledgeProvider
from app.agent.knowledge.faostat_provider import FaostatExternalSourceAdapter
from app.agent.knowledge.faostat_client import FaostatApiClient
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.knowledge.regulations_provider import RegulationsKnowledgeProvider


class TestFaostatAdapterIntegration:
    """Integration tests for FAOSTAT external source adapter bootstrap registration."""

    def test_adapter_registers_in_registry(self):
        registry = KnowledgeProviderRegistry()
        adapter = FaostatExternalSourceAdapter(
            config={
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))
        sources = asyncio.run(registry.list_providers())
        assert any(s["id"] == "faostat" for s in sources)

    def test_adapter_is_queryable_via_registry(self):
        registry = KnowledgeProviderRegistry()
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))

        with patch.object(FaostatApiClient, "request", new_callable=AsyncMock, return_value={
            "data": [
                {
                    "area": "Egypt",
                    "areaCode": "EGY",
                    "item": "Wheat",
                    "itemCode": "15",
                    "element": "Production",
                    "elementCode": "5510",
                    "year": "2023",
                    "unit": "Tonnes",
                    "value": "1234567",
                    "flag": "A",
                }
            ],
            "message": {
                "total": 1,
            },
        }):
            result = asyncio.run(registry.query("faostat", "wheat production", context={"area": "Egypt", "item": "Wheat", "element": "Production", "year": "2023"}))

        assert "results" in result
        assert result["sources"] == ["faostat"]

    def test_existing_providers_still_register_after_faostat(self):
        registry = KnowledgeProviderRegistry()
        faostat_adapter = FaostatExternalSourceAdapter(
            config={
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )
        regulations_provider = RegulationsKnowledgeProvider(file_path="backend/data/regulations.json")

        asyncio.run(registry.register(faostat_adapter))
        asyncio.run(registry.register(regulations_provider))

        sources = asyncio.run(registry.list_providers())
        assert any(s["id"] == "faostat" for s in sources)
        assert any(s["id"] == "regulations" for s in sources)

    def test_graceful_degradation_does_not_crash_startup(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        with patch.object(FaostatApiClient, "request", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            result = asyncio.run(adapter.query("test", context={"area": "Egypt"}, scope="QC", limit=10))

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["faostat"]

    def test_adapter_provider_interface_compliance(self):
        adapter = FaostatExternalSourceAdapter(
            config={
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        assert isinstance(adapter, KnowledgeProvider)
        assert hasattr(adapter, "query")
        assert hasattr(adapter, "get_sources")

        sources = asyncio.run(adapter.get_sources())
        assert len(sources) == 1
        assert sources[0]["id"] == "faostat"
        assert sources[0]["type"] == "external_agrifood_intelligence"

    def test_registry_returns_faostat_results_with_correct_shape(self):
        registry = KnowledgeProviderRegistry()
        adapter = FaostatExternalSourceAdapter(
            config={
                "base_url": "https://faostatservices.fao.org/api/v1",
                "source_id": "faostat",
                "name": "FAOSTAT External Knowledge",
                "type": "external_agrifood_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))

        raw_response = {
            "data": [
                {
                    "area": "Egypt",
                    "areaCode": "EGY",
                    "item": "Wheat",
                    "itemCode": "15",
                    "element": "Production",
                    "elementCode": "5510",
                    "year": "2023",
                    "unit": "Tonnes",
                    "value": "1234567",
                    "flag": "A",
                }
            ],
            "message": {
                "total": 1,
            },
        }

        with patch.object(FaostatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(registry.query("faostat", "wheat production", context={"area": "Egypt", "item": "Wheat", "element": "Production", "year": "2023"}))

        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["source_id"] == "faostat"
        assert "id" in item
        assert "content" in item
        assert "confidence" in item
        assert "metadata" in item
        assert item["metadata"]["source_authority"] == "FAO"
        assert item["metadata"]["effective_date"] == "2023-12-31"
        assert item["metadata"]["area"] == "Egypt"
        assert item["metadata"]["retrieval_status"] == "success"
        assert isinstance(item["metadata"]["record_hash"], str)
