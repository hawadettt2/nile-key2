import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.provider import KnowledgeProvider
from app.agent.knowledge.gccstat_provider import GccstatExternalSourceAdapter
from app.agent.knowledge.gccstat_client import GccstatApiClient
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.knowledge.regulations_provider import RegulationsKnowledgeProvider
from app.agent.decision_engine.engine import ReasoningEngine


class TestGccstatAdapterIntegration:
    """Integration tests for GCC-Stat external source adapter bootstrap registration."""

    def test_adapter_registers_in_registry(self):
        registry = KnowledgeProviderRegistry()
        adapter = GccstatExternalSourceAdapter(
            config={
                "source_id": "gccstat",
                "name": "GCC-Stat Data Portal",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))
        sources = asyncio.run(registry.list_providers())
        assert any(s["id"] == "gccstat" for s in sources)

    def test_adapter_is_queryable_via_registry(self):
        registry = KnowledgeProviderRegistry()
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
                "source_id": "gccstat",
                "name": "GCC-Stat Data Portal",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value={
            "meta": {"prepared": "2026-08-14T07:42:57"},
            "data": {
                "dataSets": [
                    {
                        "series": {
                            "SA:0:0:0:0": {
                                "observations": {"2024": ["12345"]},
                            }
                        }
                    }
                ]
            },
        }):
            result = asyncio.run(registry.query("gccstat", "population", context={"country": "SA"}))

        assert "results" in result
        assert result["sources"] == ["gccstat"]

    def test_existing_providers_still_register_after_gccstat(self):
        registry = KnowledgeProviderRegistry()
        gccstat_adapter = GccstatExternalSourceAdapter(
            config={
                "source_id": "gccstat",
                "name": "GCC-Stat Data Portal",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )
        regulations_provider = RegulationsKnowledgeProvider(file_path="backend/data/regulations.json")

        asyncio.run(registry.register(gccstat_adapter))
        asyncio.run(registry.register(regulations_provider))

        sources = asyncio.run(registry.list_providers())
        assert any(s["id"] == "gccstat" for s in sources)
        assert any(s["id"] == "regulations" for s in sources)

    def test_graceful_degradation_does_not_crash_startup(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
                "source_id": "gccstat",
                "name": "GCC-Stat Data Portal",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            result = asyncio.run(adapter.query("population", context={"country": "SA"}, scope="population", limit=10))

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["gccstat"]

    def test_adapter_provider_interface_compliance(self):
        adapter = GccstatExternalSourceAdapter(
            config={
                "source_id": "gccstat",
                "name": "GCC-Stat Data Portal",
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
        assert sources[0]["id"] == "gccstat"
        assert sources[0]["type"] == "external_trade_intelligence"

    def test_registry_returns_gccstat_results_with_correct_shape(self):
        registry = KnowledgeProviderRegistry()
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
                "source_id": "gccstat",
                "name": "GCC-Stat Data Portal",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))

        raw_response = {
            "meta": {"prepared": "2026-08-14T07:42:57"},
            "data": {
                "dataSets": [
                    {
                        "series": {
                            "SA:0:0:0:0": {
                                "observations": {"2024": ["12345"]},
                            }
                        }
                    }
                ]
            },
        }

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(registry.query("gccstat", "population", context={"country": "SA"}))

        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["source_id"] == "gccstat"
        assert "id" in item
        assert "content" in item
        assert "confidence" in item
        assert "metadata" in item
        assert item["metadata"]["source_authority"] == "GCC-Stat"
        assert item["metadata"]["country"] == "SA"
        assert item["metadata"]["retrieval_status"] == "success"
        assert isinstance(item["metadata"]["record_hash"], str)

    def test_reasoning_engine_can_query_gccstat_provider_through_registry(self):
        registry = KnowledgeProviderRegistry()
        adapter = GccstatExternalSourceAdapter(
            config={
                "base_url": "https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest",
                "source_id": "gccstat",
                "name": "GCC-Stat Data Portal",
                "type": "external_trade_intelligence",
                "version": "1.0",
                "updated_at": "2026-08-14T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))

        reasoning_engine = ReasoningEngine(knowledge_provider_registry=registry)

        with patch.object(GccstatApiClient, "request", new_callable=AsyncMock, return_value={
            "meta": {"prepared": "2026-08-14T07:42:57"},
            "data": {
                "dataSets": [
                    {
                        "series": {
                            "SA:0:0:0:0": {
                                "observations": {"2024": ["12345"]},
                            }
                        }
                    }
                ]
            },
        }):
            knowledge = asyncio.run(reasoning_engine._query_knowledge("population", {"country": "SA"}))

        assert len(knowledge) == 1
        assert knowledge[0]["source_id"] == "gccstat"
        assert "id" in knowledge[0]
        assert "content" in knowledge[0]
        assert "metadata" in knowledge[0]
