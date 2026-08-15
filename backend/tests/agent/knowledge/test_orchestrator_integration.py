import pytest
from app.agent.knowledge.orchestrator import KnowledgeOrchestrator


class FakeProvider:
    def __init__(self, source_id, results):
        self._source_id = source_id
        self._results = results

    async def get_sources(self):
        return [{"id": self._source_id, "name": self._source_id, "type": "external"}]

    async def query(self, query, context=None, scope=None, limit=10):
        return {"results": self._results, "confidence": 0.8, "sources": [self._source_id]}


class FakeRegistry:
    def __init__(self, providers):
        self._providers = {p._source_id: p for p in providers}

    def exists(self, source_id):
        return source_id in self._providers

    async def list_providers(self):
        results = []
        for provider in self._providers.values():
            sources = await provider.get_sources()
            results.extend(sources)
        return results

    async def query(self, source_id, query, context=None, scope=None, limit=10):
        provider = self._providers.get(source_id)
        if not provider:
            raise KeyError(f"Source '{source_id}' not registered")
        return await provider.query(query, context, scope, limit)


class FakeConfig:
    KNOWLEDGE_ORCHESTRATION_ENABLED = True
    KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED = True
    KNOWLEDGE_ORCHESTRATION_MAX_RESULTS = 10
    KNOWLEDGE_ORCHESTRATION_CONFLICT_STRATEGY = "latest_official_wins"


@pytest.fixture
def registry_and_providers():
    provider_a = FakeProvider("uncomtrade", [
        {"source_id": "uncomtrade", "content": "result A", "confidence": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
    ])
    provider_b = FakeProvider("tradedata", [
        {"source_id": "tradedata", "content": "result B", "confidence": 0.7, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "commercial"}},
    ])
    registry = FakeRegistry([provider_a, provider_b])
    return registry, [provider_a, provider_b]


@pytest.fixture
def orchestrator(registry_and_providers):
    registry, _ = registry_and_providers
    config = FakeConfig()
    return KnowledgeOrchestrator(registry, config)


@pytest.mark.asyncio
class TestOrchestratorIntegration:
    async def test_end_to_end_with_two_mocked_providers(self, orchestrator):
        result = await orchestrator.orchestrate("trade statistics export", limit=10)
        assert "results" in result
        assert len(result["results"]) > 0

    async def test_end_to_end_with_empty_providers(self):
        registry = FakeRegistry([])
        config = FakeConfig()
        orch = KnowledgeOrchestrator(registry, config)
        result = await orch.orchestrate("trade statistics export", limit=10)
        assert result["results"] == []

    async def test_end_to_end_with_provider_raising_exception(self):
        class FailingProvider(FakeProvider):
            async def query(self, query, context=None, scope=None, limit=10):
                raise RuntimeError("provider failed")

        provider = FailingProvider("failing", [])
        registry = FakeRegistry([provider])
        config = FakeConfig()
        orch = KnowledgeOrchestrator(registry, config)
        result = await orch.orchestrate("trade statistics export", limit=10)
        assert result["results"] == []

    async def test_end_to_end_with_sources_filter(self, orchestrator):
        result = await orchestrator.orchestrate("trade statistics export", sources=["uncomtrade"], limit=10)
        assert all(r["source_id"] == "uncomtrade" for r in result["results"])

    async def test_end_to_end_dedup_across_providers(self, orchestrator):
        provider = FakeProvider("uncomtrade", [
            {"source_id": "uncomtrade", "content": "same content", "confidence": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "tradedata", "content": "same content", "confidence": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "commercial"}},
        ])
        registry = FakeRegistry([provider])
        config = FakeConfig()
        orch = KnowledgeOrchestrator(registry, config)
        result = await orch.orchestrate("trade statistics export", sources=["uncomtrade", "tradedata"], limit=10)
        assert len(result["results"]) == 1

    async def test_end_to_end_conflict_resolution(self, orchestrator):
        provider = FakeProvider("uncomtrade", [
            {"source_id": "uncomtrade", "content": "same content", "confidence": 0.9, "metadata": {"effective_date": "2024-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "tradedata", "content": "same content", "confidence": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ])
        registry = FakeRegistry([provider])
        config = FakeConfig()
        orch = KnowledgeOrchestrator(registry, config)
        result = await orch.orchestrate("trade statistics export", sources=["uncomtrade", "tradedata"], limit=10)
        assert len(result["results"]) == 1

    async def test_end_to_end_all_query_types(self, orchestrator):
        queries = [
            ("agriculture export", "agrifood"),
            ("customs declaration", "customs"),
            ("regulation law", "regulatory"),
            ("market access duty", "market_access"),
            ("trade statistics export", "trade_statistics"),
            ("origin certificate", "rules_of_origin"),
            ("random text", "general"),
        ]
        for query, expected_type in queries:
            result = await orchestrator.orchestrate(query, limit=10)
            assert result["orchestration"]["query_type"] == expected_type

    async def test_end_to_end_config_disabled(self, orchestrator):
        orchestrator._config.KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED = False
        provider = FakeProvider("uncomtrade", [
            {"source_id": "uncomtrade", "content": "same content A", "confidence": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
            {"source_id": "tradedata", "content": "same content B", "confidence": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "commercial"}},
        ])
        registry = FakeRegistry([provider])
        config = FakeConfig()
        orch = KnowledgeOrchestrator(registry, config)
        result = await orch.orchestrate("trade statistics export", sources=["uncomtrade", "tradedata"], limit=10)
        assert len(result["results"]) == 2

    async def test_end_to_end_max_results_limit(self, orchestrator):
        provider = FakeProvider("uncomtrade", [
            {"source_id": "uncomtrade", "content": f"result {i}", "confidence": 0.8, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}}
            for i in range(20)
        ])
        registry = FakeRegistry([provider])
        config = FakeConfig()
        orch = KnowledgeOrchestrator(registry, config)
        result = await orch.orchestrate("trade statistics export", sources=["uncomtrade"], limit=5)
        assert len(result["results"]) == 5

    async def test_end_to_end_orchestration_metadata_populated(self, orchestrator):
        result = await orchestrator.orchestrate("trade statistics export", limit=10)
        assert result["orchestration"]["query_type"] == "trade_statistics"
        assert len(result["orchestration"]["providers_queried"]) > 0
        assert "orchestrated_at" in result["orchestration"]
