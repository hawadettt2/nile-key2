import pytest
from app.agent.knowledge.orchestrator import KnowledgeOrchestrator


class FakeRegistry:
    def __init__(self, providers=None):
        self._providers = {p["id"]: p for p in (providers or [])}

    def exists(self, source_id):
        return source_id in self._providers

    def list_providers(self):
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
        {"id": "gccstat", "name": "GCC-Stat", "type": "external", "authority_level": "aggregated"},
    ]


@pytest.fixture
def orchestrator(base_providers):
    registry = FakeRegistry(base_providers)
    config = FakeConfig()
    return KnowledgeOrchestrator(registry, config)


class TestConflictResolution:
    def test_same_source_different_dates(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2024-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "faostat", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ]
        resolved = orchestrator._resolve_conflicts(results)
        assert len(resolved) == 1
        assert resolved[0]["metadata"]["effective_date"] == "2025-01-01T00:00:00Z"

    def test_different_sources_same_date_different_authorities(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "tradedata", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "commercial"}},
        ]
        resolved = orchestrator._resolve_conflicts(results)
        assert len(resolved) == 1
        assert resolved[0]["source_id"] == "faostat"

    def test_different_sources_different_dates_same_authority(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2024-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "uncomtrade", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ]
        resolved = orchestrator._resolve_conflicts(results)
        assert len(resolved) == 1
        assert resolved[0]["metadata"]["effective_date"] == "2025-01-01T00:00:00Z"

    def test_different_sources_different_dates_different_authorities_diff_greater_than_1(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "gccstat", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2024-01-01T00:00:00Z", "authority_level": "aggregated"}},
        ]
        resolved = orchestrator._resolve_conflicts(results)
        assert len(resolved) == 1
        assert resolved[0]["source_id"] == "faostat"

    def test_equal_authority_equal_date_both_kept_flagged(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "uncomtrade", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ]
        resolved = orchestrator._resolve_conflicts(results)
        assert len(resolved) == 2
        for r in resolved:
            assert r["metadata"]["conflict"] is True
            assert len(r["metadata"]["conflict_with"]) == 1

    def test_no_effective_date_on_either_both_kept_flagged(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"authority_level": "official"}},
            {"source_id": "uncomtrade", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"authority_level": "official"}},
        ]
        resolved = orchestrator._resolve_conflicts(results)
        assert len(resolved) == 2
        for r in resolved:
            assert r["metadata"]["conflict"] is True

    def test_conflict_flag_set_on_winner(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2024-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "uncomtrade", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ]
        resolved = orchestrator._resolve_conflicts(results)
        assert len(resolved) == 1
        assert resolved[0]["metadata"]["conflict"] is True

    def test_conflict_with_list_populated(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2024-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "uncomtrade", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ]
        resolved = orchestrator._resolve_conflicts(results)
        assert len(resolved) == 1
        assert resolved[0]["metadata"]["conflict"] is True
        assert "faostat" in resolved[0]["metadata"]["conflict_with"]

    def test_unsupported_strategy_passthrough(self, orchestrator):
        orchestrator._config.KNOWLEDGE_ORCHESTRATION_CONFLICT_STRATEGY = "unsupported"
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2024-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "uncomtrade", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ]
        resolved = orchestrator._resolve_conflicts(results)
        assert len(resolved) == 2

    def test_empty_results(self, orchestrator):
        resolved = orchestrator._resolve_conflicts([])
        assert resolved == []
