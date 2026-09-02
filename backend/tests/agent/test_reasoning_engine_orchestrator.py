import pytest
from app.agent.decision_engine.engine import ReasoningEngine


class FakeProvider:
    def __init__(self, source_id, results):
        self._source_id = source_id
        self._results = results

    async def get_sources(self):
        return [{"id": self._source_id, "name": self._source_id, "type": "external"}]

    async def query(self, query, context=None, scope=None, limit=10):
        return {"results": self._results, "confidence": 0.8, "sources": [self._source_id]}


class FakeRegistry:
    def __init__(self, providers=None):
        self._providers = {}
        for p in (providers or []):
            if hasattr(p, "_source_id"):
                self._providers[p._source_id] = p
            elif isinstance(p, dict):
                self._providers[p["id"]] = p

    def exists(self, source_id):
        return source_id in self._providers

    async def list_providers(self):
        results = []
        for provider in self._providers.values():
            if hasattr(provider, "get_sources"):
                sources = await provider.get_sources()
                results.extend(sources)
            elif isinstance(provider, dict):
                results.append(provider)
        return results

    async def query(self, source_id, query, context=None, scope=None, limit=10):
        provider = self._providers.get(source_id)
        if not provider:
            raise KeyError(f"Source '{source_id}' not registered")
        if hasattr(provider, "query"):
            return await provider.query(query, context, scope, limit)
        return provider.get("query_result", {"results": []})


class FakeConfig:
    KNOWLEDGE_ORCHESTRATION_ENABLED = True
    KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED = True
    KNOWLEDGE_ORCHESTRATION_MAX_RESULTS = 10
    KNOWLEDGE_ORCHESTRATION_CONFLICT_STRATEGY = "latest_official_wins"


class FakeResearchOrchestrator:
    def __init__(self, result):
        self._result = result

    async def execute(self, request, request_id):
        return self._result


class FakeResearchResult:
    def __init__(self, data):
        self._data = data

    def model_dump(self, mode=None):
        return self._data


@pytest.mark.asyncio
class TestReasoningEngineExternalResearch:
    async def test_external_research_triggered_for_market_request(self):
        engine = ReasoningEngine()
        orchestrator = FakeResearchOrchestrator(
            FakeResearchResult({
                "request_id": "req_test123",
                "status": "completed",
                "goal": "market study",
                "findings": [{"topic": "market", "content": "finding"}],
                "sources_consulted": ["source_a"],
                "sources_failed": [],
                "errors": None,
                "created_at": "2026-01-01T00:00:00Z",
                "completed_at": "2026-01-01T00:01:00Z",
                "metadata": {},
            })
        )
        engine._research_orchestrator = orchestrator
        results = await engine._query_external_research("أريد دراسة جدوى تصدير الفواكه المصرية إلى الأردن", {})
        assert isinstance(results, dict)
        assert results["status"] == "completed"
        assert results["request_id"] == "req_test123"

    async def test_egypt_jordan_scenario_triggers_external_research(self):
        engine = ReasoningEngine()
        orchestrator = FakeResearchOrchestrator(
            FakeResearchResult({
                "request_id": "req_egypt_jordan",
                "status": "completed",
                "goal": "أريد تصدير الفواكه والخضر المصرية إلى الأردن",
                "findings": [{"topic": "market", "content": "Egypt fruits export to Jordan market study"}],
                "sources_consulted": ["faostat", "uncomtrade"],
                "sources_failed": [],
                "errors": None,
                "created_at": "2026-01-01T00:00:00Z",
                "completed_at": "2026-01-01T00:01:00Z",
                "metadata": {},
            })
        )
        engine._research_orchestrator = orchestrator
        results = await engine._query_external_research("أريد تصدير الفواكه والخضر المصرية إلى الأردن", {})
        assert isinstance(results, dict)
        assert results["status"] == "completed"
        assert "faostat" in results["sources_consulted"]

    async def test_decision_context_contains_research_on_success(self):
        engine = ReasoningEngine()
        orchestrator = FakeResearchOrchestrator(
            FakeResearchResult({
                "request_id": "req_ctx",
                "status": "completed",
                "goal": "market study",
                "findings": [{"topic": "market", "content": "finding"}],
                "sources_consulted": ["source_a"],
                "sources_failed": [],
                "errors": None,
                "created_at": "2026-01-01T00:00:00Z",
                "completed_at": "2026-01-01T00:01:00Z",
                "metadata": {},
            })
        )
        engine._research_orchestrator = orchestrator
        decision = await engine.reason("session-1", {"intent": "أريد دراسة جدوى تصدير الفواكه المصرية إلى الأردن"})
        assert "research" in decision["context"]
        assert isinstance(decision["context"]["research"], dict)
        assert decision["context"]["research"]["status"] == "completed"

    async def test_graceful_degradation_when_orchestrator_missing(self):
        engine = ReasoningEngine()
        assert not hasattr(engine, "_research_orchestrator")
        results = await engine._query_external_research("market study export", {})
        assert results == []

    async def test_graceful_degradation_when_execute_raises(self):
        engine = ReasoningEngine()

        class FailingOrchestrator:
            async def execute(self, request, request_id):
                raise RuntimeError("external research failed")

        engine._research_orchestrator = FailingOrchestrator()
        results = await engine._query_external_research("market study export", {})
        assert results == []

    async def test_non_research_request_does_not_trigger_external_research(self):
        engine = ReasoningEngine()
        calls = []

        class TrackingOrchestrator:
            async def execute(self, request, request_id):
                calls.append(request_id)
                return FakeResearchResult({
                    "request_id": request_id,
                    "status": "completed",
                    "goal": request.goal,
                    "findings": [],
                    "sources_consulted": [],
                    "sources_failed": [],
                    "errors": None,
                    "created_at": "2026-01-01T00:00:00Z",
                    "completed_at": "2026-01-01T00:01:00Z",
                    "metadata": {},
                })

        engine._research_orchestrator = TrackingOrchestrator()
        results = await engine._query_external_research("create shipment to Saudi Arabia", {})
        assert results == []
        assert calls == []

    async def test_full_reason_flow_preserves_knowledge_and_research(self):
        engine = ReasoningEngine()
        knowledge_orchestrator = FakeOrchestrator([
            {"source_id": "provider_a", "content": "knowledge result", "confidence": 0.9},
        ])
        research_orchestrator = FakeResearchOrchestrator(
            FakeResearchResult({
                "request_id": "req_full",
                "status": "completed",
                "goal": "أريد تصدير الفواكه والخضر المصرية إلى الأردن",
                "findings": [{"topic": "market", "content": "research finding"}],
                "sources_consulted": ["source_r"],
                "sources_failed": [],
                "errors": None,
                "created_at": "2026-01-01T00:00:00Z",
                "completed_at": "2026-01-01T00:01:00Z",
                "metadata": {},
            })
        )
        engine._knowledge_orchestrator = knowledge_orchestrator
        engine._research_orchestrator = research_orchestrator
        decision = await engine.reason("session-1", {"intent": "أريد تصدير الفواكه والخضر المصرية إلى الأردن"})
        assert "knowledge" in decision["context"]
        assert "research" in decision["context"]
        assert isinstance(decision["context"]["knowledge"], list)
        assert isinstance(decision["context"]["research"], dict)
        assert decision["context"]["research"]["status"] == "completed"


class FakeOrchestrator:
    def __init__(self, results):
        self._results = results
        self._orchestration = {"query_type": "trade_statistics", "providers_queried": ["provider_a"]}

    async def orchestrate(self, query, context=None, scope=None, sources=None, limit=10):
        return {
            "results": self._results,
            "confidence": 0.9,
            "sources": ["provider_a"],
            "orchestration": self._orchestration,
        }


@pytest.mark.asyncio
class TestReasoningEngineOrchestrator:
    async def test_orchestrator_attached_uses_orchestrator(self):
        provider = FakeProvider("provider_a", [
            {"source_id": "provider_a", "content": "result", "confidence": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ])
        registry = FakeRegistry([provider])
        orchestrator = FakeOrchestrator([
            {"source_id": "provider_a", "content": "result", "confidence": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ])
        engine = ReasoningEngine(knowledge_provider_registry=registry)
        engine._knowledge_orchestrator = orchestrator
        results = await engine._query_knowledge("trade statistics", {})
        assert len(results) == 1
        assert results[0]["source_id"] == "provider_a"

    async def test_orchestrator_not_attached_uses_legacy(self):
        provider = FakeProvider("provider_a", [
            {"source_id": "provider_a", "content": "result", "confidence": 0.9},
        ])
        registry = FakeRegistry([provider])
        engine = ReasoningEngine(knowledge_provider_registry=registry)
        results = await engine._query_knowledge("trade statistics", {})
        assert len(results) == 1

    async def test_legacy_fallback_returns_same_shape(self):
        provider = FakeProvider("provider_a", [
            {"source_id": "provider_a", "content": "result", "confidence": 0.9},
        ])
        registry = FakeRegistry([provider])
        engine = ReasoningEngine(knowledge_provider_registry=registry)
        results = await engine._query_knowledge_legacy("trade statistics", {})
        assert isinstance(results, list)
        assert len(results) == 1
        assert results[0]["source_id"] == "provider_a"

    async def test_orchestration_metadata_in_decision_context(self):
        provider = FakeProvider("provider_a", [
            {"source_id": "provider_a", "content": "result", "confidence": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ])
        registry = FakeRegistry([provider])
        orchestrator = FakeOrchestrator([
            {"source_id": "provider_a", "content": "result", "confidence": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ])
        engine = ReasoningEngine(knowledge_provider_registry=registry)
        engine._knowledge_orchestrator = orchestrator
        results = await engine._query_knowledge("trade statistics", {})
        assert engine._last_orchestration_meta is not None
        assert engine._last_orchestration_meta["query_type"] == "trade_statistics"

    async def test_no_orchestration_metadata_when_orchestrator_absent(self):
        provider = FakeProvider("provider_a", [
            {"source_id": "provider_a", "content": "result", "confidence": 0.9},
        ])
        registry = FakeRegistry([provider])
        engine = ReasoningEngine(knowledge_provider_registry=registry)
        results = await engine._query_knowledge("trade statistics", {})
        assert getattr(engine, "_last_orchestration_meta", None) is None

    async def test_registry_none_returns_empty(self):
        engine = ReasoningEngine(knowledge_provider_registry=None)
        results = await engine._query_knowledge("trade statistics", {})
        assert results == []

    async def test_full_reason_flow_with_orchestrator(self):
        provider = FakeProvider("provider_a", [
            {"source_id": "provider_a", "content": "result", "confidence": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ])
        registry = FakeRegistry([provider])
        orchestrator = FakeOrchestrator([
            {"source_id": "provider_a", "content": "result", "confidence": 0.9, "metadata": {"effective_date": "2025-01-01T00:00:00Z", "authority_level": "official"}},
        ])
        engine = ReasoningEngine(knowledge_provider_registry=registry)
        engine._knowledge_orchestrator = orchestrator
        decision = await engine.reason("session-1", {"intent": "trade statistics export"})
        assert decision["chosen_path"] is not None

    async def test_full_reason_flow_without_orchestrator(self):
        provider = FakeProvider("provider_a", [
            {"source_id": "provider_a", "content": "result", "confidence": 0.9},
        ])
        registry = FakeRegistry([provider])
        engine = ReasoningEngine(knowledge_provider_registry=registry)
        decision = await engine.reason("session-1", {"intent": "trade statistics export"})
        assert decision["chosen_path"] is not None
