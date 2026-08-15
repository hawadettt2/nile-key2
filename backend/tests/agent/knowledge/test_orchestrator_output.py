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
    ]


@pytest.fixture
def orchestrator(base_providers):
    registry = FakeRegistry(base_providers)
    config = FakeConfig()
    return KnowledgeOrchestrator(registry, config)


class TestOutput:
    def test_output_has_results_key(self, orchestrator):
        output = orchestrator._build_output([], "general", [], 10, 0, 0)
        assert "results" in output

    def test_output_has_confidence_key(self, orchestrator):
        output = orchestrator._build_output([], "general", [], 10, 0, 0)
        assert "confidence" in output

    def test_output_has_sources_key(self, orchestrator):
        output = orchestrator._build_output([], "general", [], 10, 0, 0)
        assert "sources" in output

    def test_output_has_orchestration_key(self, orchestrator):
        output = orchestrator._build_output([], "general", [], 10, 0, 0)
        assert "orchestration" in output

    def test_orchestration_has_query_type(self, orchestrator):
        output = orchestrator._build_output([], "trade_statistics", [], 10, 0, 0)
        assert output["orchestration"]["query_type"] == "trade_statistics"

    def test_orchestration_has_providers_queried(self, orchestrator):
        output = orchestrator._build_output([], "general", [("faostat", True)], 10, 0, 0)
        assert output["orchestration"]["providers_queried"] == ["faostat"]

    def test_orchestrated_at_is_iso8601(self, orchestrator):
        output = orchestrator._build_output([], "general", [], 10, 0, 0)
        from datetime import datetime
        datetime.fromisoformat(output["orchestration"]["orchestrated_at"])

    def test_empty_results_confidence_none(self, orchestrator):
        output = orchestrator._build_output([], "general", [], 10, 0, 0)
        assert output["confidence"] is None
