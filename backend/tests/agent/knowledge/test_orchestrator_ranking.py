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
        {"id": "gccstat", "name": "GCC-Stat", "type": "external", "authority_level": "aggregated"},
    ]


@pytest.fixture
def orchestrator(base_providers):
    registry = FakeRegistry(base_providers)
    config = FakeConfig()
    return KnowledgeOrchestrator(registry, config)


@pytest.mark.asyncio
class TestRanking:
    async def test_high_confidence_official_recent_primary(self, orchestrator):
        result = {
            "confidence": 0.9,
            "metadata": {"effective_date": "2025-08-15T00:00:00Z", "authority_level": "official"},
            "source_id": "uncomtrade",
        }
        provider_meta = await orchestrator._build_provider_meta_map()
        score = orchestrator._compute_composite_score(result, provider_meta["uncomtrade"], "trade_statistics", True)
        assert score == pytest.approx(0.96, rel=1e-2)

    async def test_low_confidence_aggregated_old_general(self, orchestrator):
        result = {
            "confidence": 0.5,
            "metadata": {"effective_date": "2022-08-15T00:00:00Z", "authority_level": "aggregated"},
            "source_id": "gccstat",
        }
        provider_meta = await orchestrator._build_provider_meta_map()
        score = orchestrator._compute_composite_score(result, provider_meta["gccstat"], "general", False)
        assert score == pytest.approx(0.50, rel=1e-2)

    async def test_same_score_tie_effective_date_desc(self, orchestrator):
        results = [
            {"confidence": 0.8, "metadata": {"effective_date": "2024-01-01T00:00:00Z", "authority_level": "official"}, "source_id": "uncomtrade"},
            {"confidence": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}, "source_id": "uncomtrade"},
        ]
        provider_meta = await orchestrator._build_provider_meta_map()
        ranked = orchestrator._rank_results(results, provider_meta, "trade_statistics")
        assert ranked[0]["metadata"]["effective_date"] == "2025-01-01T00:00:00Z"

    async def test_same_date_tie_source_id_asc(self, orchestrator):
        results = [
            {"confidence": 0.8, "metadata": {"effective_date": "2026-08-14T00:00:00Z", "authority_level": "official"}, "source_id": "uncomtrade"},
            {"confidence": 0.8, "metadata": {"effective_date": "2026-08-14T00:00:00Z", "authority_level": "official"}, "source_id": "faostat"},
        ]
        provider_meta = await orchestrator._build_provider_meta_map()
        ranked = orchestrator._rank_results(results, provider_meta, "general")
        assert ranked[0]["source_id"] == "faostat"
        assert ranked[1]["source_id"] == "uncomtrade"

    async def test_missing_confidence_defaults_to_zero(self, orchestrator):
        result = {
            "confidence": "not_a_number",
            "metadata": {"effective_date": "2026-08-14T00:00:00Z", "authority_level": "official"},
            "source_id": "uncomtrade",
        }
        provider_meta = await orchestrator._build_provider_meta_map()
        score = orchestrator._compute_composite_score(result, provider_meta["uncomtrade"], "trade_statistics", True)
        assert score == pytest.approx(0.6, rel=1e-2)

    async def test_missing_effective_date_recency_0_5(self, orchestrator):
        result = {
            "confidence": 0.8,
            "metadata": {"authority_level": "official"},
            "source_id": "uncomtrade",
        }
        provider_meta = await orchestrator._build_provider_meta_map()
        score = orchestrator._compute_composite_score(result, provider_meta["uncomtrade"], "trade_statistics", True)
        assert score == pytest.approx(0.82, rel=1e-2)

    async def test_unknown_authority_level_weight_0_5(self, orchestrator):
        provider_meta = {"authority_level": "unknown"}
        result = {
            "confidence": 0.8,
            "metadata": {"effective_date": "2026-08-14T00:00:00Z"},
            "source_id": "unknown_provider",
        }
        score = orchestrator._compute_composite_score(result, provider_meta, "trade_statistics", True)
        assert score == pytest.approx(0.77, rel=1e-2)

    async def test_max_score_capped_at_1_0(self, orchestrator):
        result = {
            "confidence": 1.0,
            "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"},
            "source_id": "uncomtrade",
        }
        provider_meta = await orchestrator._build_provider_meta_map()
        score = orchestrator._compute_composite_score(result, provider_meta["uncomtrade"], "trade_statistics", True)
        assert score <= 1.0

    async def test_min_score_floored_at_0_0(self, orchestrator):
        result = {
            "confidence": 0.0,
            "metadata": {"effective_date": "1970-01-01T00:00:00Z", "authority_level": "aggregated"},
            "source_id": "gccstat",
        }
        provider_meta = await orchestrator._build_provider_meta_map()
        score = orchestrator._compute_composite_score(result, provider_meta["gccstat"], "general", False)
        assert score >= 0.0

    async def test_relevance_weight_general_is_0_5(self, orchestrator):
        result = {
            "confidence": 1.0,
            "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"},
            "source_id": "uncomtrade",
        }
        provider_meta = await orchestrator._build_provider_meta_map()
        score_primary = orchestrator._compute_composite_score(result, provider_meta["uncomtrade"], "general", True)
        score_secondary = orchestrator._compute_composite_score(result, provider_meta["uncomtrade"], "general", False)
        assert score_primary == pytest.approx(score_secondary, rel=1e-2)
