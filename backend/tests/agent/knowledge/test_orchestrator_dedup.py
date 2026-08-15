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
    ]


@pytest.fixture
def orchestrator(base_providers):
    registry = FakeRegistry(base_providers)
    config = FakeConfig()
    return KnowledgeOrchestrator(registry, config)


class TestDedup:
    def test_same_source_same_content_same_date(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
            {"source_id": "faostat", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
        ]
        deduped = orchestrator._deduplicate(results)
        assert len(deduped) == 1
        assert deduped[0]["composite_score"] == 0.9

    def test_different_sources_same_content_same_date(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "tradedata", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "commercial"}},
        ]
        deduped = orchestrator._deduplicate(results)
        assert len(deduped) == 1
        assert deduped[0]["source_id"] == "faostat"

    def test_different_sources_same_content_different_dates(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
            {"source_id": "tradedata", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2024-01-01T00:00:00Z"}},
        ]
        deduped = orchestrator._deduplicate(results)
        assert len(deduped) == 2

    def test_empty_results(self, orchestrator):
        deduped = orchestrator._deduplicate([])
        assert deduped == []

    def test_dedup_disabled_via_config(self, orchestrator):
        orchestrator._config.KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED = False
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
            {"source_id": "tradedata", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
        ]
        deduped = orchestrator._deduplicate(results)
        assert len(deduped) == 2

    def test_content_100_stable_hash(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "a" * 200, "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
            {"source_id": "tradedata", "content": "a" * 200, "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
        ]
        deduped = orchestrator._deduplicate(results)
        assert len(deduped) == 1

    def test_none_effective_date_handled(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "same content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": None}},
            {"source_id": "tradedata", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": None}},
        ]
        deduped = orchestrator._deduplicate(results)
        assert len(deduped) == 1

    def test_unicode_content_normalized(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "Same Content", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
            {"source_id": "tradedata", "content": "same content", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
        ]
        deduped = orchestrator._deduplicate(results)
        assert len(deduped) == 1

    def test_mixed_duplicates_and_unique(self, orchestrator):
        results = [
            {"source_id": "faostat", "content": "A", "confidence": 0.8, "composite_score": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
            {"source_id": "tradedata", "content": "A", "confidence": 0.9, "composite_score": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
            {"source_id": "faostat", "content": "B", "confidence": 0.7, "composite_score": 0.7, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}},
        ]
        deduped = orchestrator._deduplicate(results)
        assert len(deduped) == 2

    def test_large_result_set_performance(self, orchestrator):
        results = [
            {"source_id": f"provider{i % 3}", "content": f"content {i % 10}", "confidence": 0.5, "composite_score": 0.5, "metadata": {"effective_date": "2025-01-01T00:00:00Z"}}
            for i in range(1000)
        ]
        deduped = orchestrator._deduplicate(results)
        assert len(deduped) < len(results)
