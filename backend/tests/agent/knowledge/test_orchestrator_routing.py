import pytest
from app.agent.knowledge.orchestrator import KnowledgeOrchestrator


class FakeRegistry:
    def __init__(self, providers=None):
        self._providers = {p["id"]: p for p in (providers or [])}

    def exists(self, source_id):
        return source_id in self._providers

    async def list_providers(self):
        return list(self._providers.values())


class FakeConfig:
    KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED = True
    KNOWLEDGE_ORCHESTRATION_CONFLICT_STRATEGY = "latest_official_wins"


@pytest.fixture
def base_providers():
    return [
        {"id": "faostat", "name": "FAOSTAT", "type": "external", "authority_level": "official"},
        {"id": "uncomtrade", "name": "UN Comtrade", "type": "external", "authority_level": "official"},
        {"id": "tradedata", "name": "TradeData", "type": "external", "authority_level": "commercial"},
        {"id": "zatca", "name": "ZATCA", "type": "external", "authority_level": "official"},
        {"id": "moaah", "name": "Moaah", "type": "external", "authority_level": "official"},
        {"id": "gccstat", "name": "GCC-Stat", "type": "external", "authority_level": "official"},
    ]


@pytest.fixture
def orchestrator(base_providers):
    registry = FakeRegistry(base_providers)
    config = FakeConfig()
    return KnowledgeOrchestrator(registry, config)


@pytest.mark.asyncio
class TestRouting:
    async def test_agrifood_primary_contains_faostat(self, orchestrator):
        providers = await orchestrator._route_providers("agrifood", None)
        primary = [sid for sid, is_primary in providers if is_primary]
        assert "faostat" in primary

    async def test_agrifood_secondary_contains_tradedata(self, orchestrator):
        providers = await orchestrator._route_providers("agrifood", None)
        secondary = [sid for sid, is_primary in providers if not is_primary]
        assert "tradedata" in secondary

    async def test_customs_primary_contains_zatca_moaah(self, orchestrator):
        providers = await orchestrator._route_providers("customs", None)
        primary = [sid for sid, is_primary in providers if is_primary]
        assert "zatca" in primary
        assert "moaah" in primary

    async def test_regulatory_primary_contains_moaah_only(self, orchestrator):
        providers = await orchestrator._route_providers("regulatory", None)
        primary = [sid for sid, is_primary in providers if is_primary]
        assert "moaah" in primary
        assert len(primary) == 1

    async def test_market_access_primary_contains_moaah_only(self, orchestrator):
        providers = await orchestrator._route_providers("market_access", None)
        primary = [sid for sid, is_primary in providers if is_primary]
        assert "moaah" in primary
        assert len(primary) == 1

    async def test_market_access_secondary_contains_zatca_gccstat_tradedata(self, orchestrator):
        providers = await orchestrator._route_providers("market_access", None)
        secondary = [sid for sid, is_primary in providers if not is_primary]
        assert "zatca" in secondary
        assert "gccstat" in secondary
        assert "tradedata" in secondary

    async def test_trade_statistics_primary_contains_uncomtrade_tradedata(self, orchestrator):
        providers = await orchestrator._route_providers("trade_statistics", None)
        primary = [sid for sid, is_primary in providers if is_primary]
        assert "uncomtrade" in primary
        assert "tradedata" in primary

    async def test_general_returns_all_registered(self, orchestrator):
        providers = await orchestrator._route_providers("general", None)
        assert len(providers) == 6

    async def test_sources_filter_bypasses_routing(self, orchestrator):
        providers = await orchestrator._route_providers("market_access", ["faostat", "uncomtrade"])
        assert len(providers) == 2
        assert all(is_primary for _, is_primary in providers)

    async def test_missing_provider_skipped_gracefully(self, orchestrator):
        providers = await orchestrator._route_providers("market_access", ["nonexistent"])
        assert len(providers) == 0

    async def test_empty_registry_returns_empty(self, orchestrator):
        registry = FakeRegistry([])
        config = FakeConfig()
        orch = KnowledgeOrchestrator(registry, config)
        providers = await orch._route_providers("market_access", None)
        assert providers == []

    async def test_primary_providers_not_in_registry_skipped(self, orchestrator):
        providers = await orchestrator._route_providers("market_access", None)
        source_ids = [sid for sid, _ in providers]
        assert "nonexistent" not in source_ids
