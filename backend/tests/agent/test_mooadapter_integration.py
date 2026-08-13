import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.agent.knowledge.provider import KnowledgeProvider
from app.agent.knowledge.mooadapter import MoaahExternalSourceAdapter
from app.agent.knowledge.mooadapter_client import MoaahApiClient
from app.agent.knowledge.registry import KnowledgeProviderRegistry
from app.agent.knowledge.regulations_provider import RegulationsKnowledgeProvider
from app.core.config import Settings


class TestMoaahAdapterIntegration:
    """Integration tests for Moaah external source adapter."""

    def test_adapter_registers_in_registry(self):
        registry = KnowledgeProviderRegistry()
        adapter = MoaahExternalSourceAdapter(
            config={
                "source_id": "moaah",
                "name": "Moaah External Knowledge",
                "type": "external",
                "version": "1.0.0",
                "updated_at": "2026-08-12T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))
        sources = asyncio.run(registry.list_providers())
        assert any(s["id"] == "moaah" for s in sources)

    def test_adapter_is_queryable_via_registry(self):
        registry = KnowledgeProviderRegistry()
        adapter = MoaahExternalSourceAdapter(
            config={
                "source_id": "moaah",
                "name": "Moaah External Knowledge",
                "type": "external",
                "version": "1.0.0",
                "updated_at": "2026-08-12T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))

        with patch.object(MoaahApiClient, "search_regulations", new_callable=AsyncMock, return_value={
            "antidumping": {"antidumping_investigations": [{"uuid": "inv-1", "subject_product": "Steel pipes", "duty_measure_detail": "Affirmative", "publication_date": "2025-03-25", "id_link": "https://example.com/inv-1", "country": "840"}]},
            "importLicensing": [],
            "qr": {"data": [], "dataOrigin": []},
            "matched_hs_codes": [],
        }):
            result = asyncio.run(registry.query("moaah", "steel pipes", context={"country": "840"}))

        assert "results" in result
        assert result["sources"] == ["moaah"]

    def test_existing_providers_still_register_after_moaah(self):
        registry = KnowledgeProviderRegistry()
        moaah_adapter = MoaahExternalSourceAdapter(
            config={
                "source_id": "moaah",
                "name": "Moaah External Knowledge",
                "type": "external",
                "version": "1.0.0",
                "updated_at": "2026-08-12T00:00:00Z",
            }
        )
        regulations_provider = RegulationsKnowledgeProvider(file_path="backend/data/regulations.json")

        asyncio.run(registry.register(moaah_adapter))
        asyncio.run(registry.register(regulations_provider))

        sources = asyncio.run(registry.list_providers())
        assert any(s["id"] == "moaah" for s in sources)
        assert any(s["id"] == "regulations" for s in sources)

    def test_graceful_degradation_does_not_crash_startup(self):
        adapter = MoaahExternalSourceAdapter(
            config={
                "base_url": "https://mtech-api.com/client/api",
                "api_key": "invalid-key",
                "source_id": "moaah",
                "name": "Moaah External Knowledge",
                "type": "external",
                "version": "1.0.0",
                "updated_at": "2026-08-12T00:00:00Z",
            }
        )

        with patch.object(MoaahApiClient, "search_regulations", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            result = asyncio.run(adapter.query("test", context={"country": "840"}, scope="keyword", limit=10))

        assert result["results"] == []
        assert result["confidence"] is None
        assert result["sources"] == ["moaah"]

    def test_adapter_provider_interface_compliance(self):
        adapter = MoaahExternalSourceAdapter(
            config={
                "source_id": "moaah",
                "name": "Moaah External Knowledge",
                "type": "external",
                "version": "1.0.0",
                "updated_at": "2026-08-12T00:00:00Z",
            }
        )

        assert isinstance(adapter, KnowledgeProvider)
        assert hasattr(adapter, "query")
        assert hasattr(adapter, "get_sources")

        sources = asyncio.run(adapter.get_sources())
        assert len(sources) == 1
        assert sources[0]["id"] == "moaah"
        assert sources[0]["type"] == "external"

    def test_registry_returns_moaah_results_with_correct_shape(self):
        registry = KnowledgeProviderRegistry()
        adapter = MoaahExternalSourceAdapter(
            config={
                "base_url": "https://mtech-api.com/client/api",
                "api_key": "test-key",
                "source_id": "moaah",
                "name": "Moaah External Knowledge",
                "type": "external",
                "version": "1.0.0",
                "updated_at": "2026-08-12T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))

        raw_response = {
            "antidumping": {
                "antidumping_investigations": [
                    {
                        "uuid": "inv-1",
                        "subject_product": "Steel pipes",
                        "duty_measure_detail": "Affirmative | Measure applied",
                        "publication_date": "2025-03-25",
                        "id_link": "https://example.com/inv-1",
                        "country": "840",
                    }
                ],
                "antidumping_measures": [],
                "countervailing_investigations": [],
                "countervailing_measures": [],
            },
            "importLicensing": [],
            "qr": {"data": [], "dataOrigin": []},
            "matched_hs_codes": [],
        }

        with patch.object(MoaahApiClient, "search_regulations", new_callable=AsyncMock, return_value=raw_response):
            result = asyncio.run(registry.query("moaah", "steel pipes", context={"country": "840"}))

        assert len(result["results"]) == 1
        item = result["results"][0]
        assert item["source_id"] == "moaah"
        assert "id" in item
        assert "content" in item
        assert "confidence" in item
        assert "metadata" in item
        assert item["metadata"]["fetch_timestamp"] == "2026-08-12T00:00:00Z"
        assert item["metadata"]["retrieval_status"] == "success"
        assert isinstance(item["metadata"]["record_hash"], str)
