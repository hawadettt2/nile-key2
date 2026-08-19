import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.knowledge.worldbank_lpi_provider import WorldBankLpiExternalSourceAdapter
from app.agent.knowledge.worldbank_lpi_client import WorldBankLpiApiClient
from app.agent.knowledge.registry import KnowledgeProviderRegistry


class TestWorldBankLpiAdapterIntegration:
    """Integration tests for World Bank LPI external source adapter bootstrap registration."""

    def test_adapter_registers_in_registry(self):
        registry = KnowledgeProviderRegistry()
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "source_id": "worldbank-lpi",
                "name": "World Bank Logistics Performance Index",
                "type": "external_logistics_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-18T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))
        sources = asyncio.run(registry.list_providers())
        assert any(s["id"] == "worldbank-lpi" for s in sources)

    def test_adapter_is_queryable_via_registry(self):
        registry = KnowledgeProviderRegistry()
        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "base_url": "https://api.worldbank.org/v2",
                "source_id": "worldbank-lpi",
                "name": "World Bank Logistics Performance Index",
                "type": "external_logistics_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-18T00:00:00Z",
            }
        )
        asyncio.run(registry.register(adapter))

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, return_value=[
            {
                "page": 1,
                "pages": 1,
                "per_page": 10,
                "total": 1,
                "sourceid": "2",
                "lastupdated": "2026-07-13",
            },
            [
                {
                    "indicator": {
                        "id": "LP.LPI.OVRL.XQ",
                        "value": "Logistics performance index: Overall (1=low to 5=high)"
                    },
                    "country": {
                        "id": "EG",
                        "value": "Egypt, Arab Rep."
                    },
                    "countryiso3code": "EGY",
                    "date": "2022",
                    "value": 3.1,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2
                }
            ]
        ]):
            result = asyncio.run(registry.query("worldbank-lpi", "Egypt logistics", context={"country": "EG", "indicator": "LP.LPI.OVRL.XQ"}))

        assert "results" in result
        assert result["sources"] == ["worldbank-lpi"]
        assert len(result["results"]) == 1

    def test_existing_providers_still_register_alongside_worldbank_lpi(self):
        registry = KnowledgeProviderRegistry()

        existing_adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "source_id": "worldbank-lpi-existing",
                "name": "World Bank LPI Existing",
                "type": "external_logistics_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-18T00:00:00Z",
            }
        )

        new_adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "source_id": "worldbank-lpi",
                "name": "World Bank Logistics Performance Index",
                "type": "external_logistics_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-18T00:00:00Z",
            }
        )

        asyncio.run(registry.register(existing_adapter))
        asyncio.run(registry.register(new_adapter))

        sources = asyncio.run(registry.list_providers())
        ids = {s["id"] for s in sources}
        assert "worldbank-lpi-existing" in ids
        assert "worldbank-lpi" in ids

    def test_fallback_to_other_providers_when_worldbank_lpi_unavailable(self):
        registry = KnowledgeProviderRegistry()

        primary_adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "source_id": "worldbank-lpi",
                "name": "World Bank Logistics Performance Index",
                "type": "external_logistics_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-18T00:00:00Z",
            }
        )

        fallback_adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "source_id": "worldbank-lpi-fallback",
                "name": "World Bank LPI Fallback",
                "type": "external_logistics_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-18T00:00:00Z",
            }
        )

        asyncio.run(registry.register(primary_adapter))
        asyncio.run(registry.register(fallback_adapter))

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            primary_result = asyncio.run(registry.query("worldbank-lpi", "test", context={"country": "EG"}))
            fallback_result = asyncio.run(registry.query("worldbank-lpi-fallback", "test", context={"country": "EG"}))

        assert primary_result["results"] == []
        assert primary_result["confidence"] is None
        assert fallback_result["results"] == []
        assert fallback_result["confidence"] is None

    def test_graceful_degradation_does_not_crash_application_startup(self):
        registry = KnowledgeProviderRegistry()

        adapter = WorldBankLpiExternalSourceAdapter(
            config={
                "source_id": "worldbank-lpi",
                "name": "World Bank Logistics Performance Index",
                "type": "external_logistics_intelligence",
                "version": "1.0.0",
                "updated_at": "2026-08-18T00:00:00Z",
            }
        )

        asyncio.run(registry.register(adapter))

        with patch.object(WorldBankLpiApiClient, "request", new_callable=AsyncMock, side_effect=Exception("Upstream error")):
            try:
                result = asyncio.run(registry.query("worldbank-lpi", "test", context={"country": "EG"}))
                assert "results" in result
                assert "confidence" in result
                assert "sources" in result
            except Exception:
                pytest.fail("World Bank LPI provider should not raise exceptions on upstream failure")
