import uuid
import pytest
from app.research.orchestrator import (
    ResearchOrchestrator,
    ResearchContext,
    ResearchStage,
    StageResult,
    PlanningStage,
    DiscoveryStage,
    RetrievalStage,
    ProcessingStage,
    EvidenceCaptureStage,
    StructuringStage,
)
from app.schemas.research import ResearchRequest
from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.schemas.research import Source, SourceRegistration


def _make_request(goal="Test goal", scope=None, source_preferences=None):
    return ResearchRequest(
        goal=goal,
        context={"session_id": "sess_test"},
        scope=scope,
        source_preferences=source_preferences,
        constraints={"max_sources": 5},
    )


def _make_source(source_id=None, source_type="market_data", status="active", domains=None):
    return Source(
        source_id=source_id or f"src_{uuid.uuid4().hex[:8]}",
        name=f"Test Source {source_id or 'unknown'}",
        source_type=source_type,
        reference="https://example.com/data",
        metadata={"domains": domains or ["agriculture"]},
        status=status,
    )


class FailingStage(ResearchStage):
    name = "failing_stage"

    async def execute(self, context: ResearchContext) -> ResearchContext:
        context.record_stage_result(StageResult(stage_name=self.name, success=False, error="intentional failure"))
        return context


class ContextCollectingStage(ResearchStage):
    name = "context_collecting_stage"

    async def execute(self, context: ResearchContext) -> ResearchContext:
        context.metadata["collected_goal"] = context.request.goal
        context.metadata["collected_scope"] = context.request.scope
        context.record_stage_result(StageResult(stage_name=self.name, success=True))
        return context


def _make_request(goal="Test goal", scope=None, source_preferences=None):
    return ResearchRequest(
        goal=goal,
        context={"session_id": "sess_test"},
        scope=scope,
        source_preferences=source_preferences,
        constraints={"max_sources": 5},
    )


# ========== Orchestrator Initialization ==========


def test_empty_orchestrator_returns_failed_result():
    orchestrator = ResearchOrchestrator()
    request = _make_request()
    import asyncio
    result = asyncio.run(orchestrator.execute(request, "req_1"))
    assert result.status == "failed"
    assert result.request_id == "req_1"
    assert "No research stages registered" in (result.errors or [""])[0]


# ========== Stage Registration ==========


def test_stages_are_executed_in_registration_order():
    orchestrator = ResearchOrchestrator()
    order = []
    class OrderStage(ResearchStage):
        async def execute(self, context: ResearchContext) -> ResearchContext:
            order.append(self.name)
            context.record_stage_result(StageResult(stage_name=self.name, success=True))
            return context

    orchestrator.register_stage(OrderStage())
    orchestrator.register_stage(OrderStage())
    request = _make_request()
    import asyncio
    asyncio.run(orchestrator.execute(request, "req_order"))
    assert order == ["unnamed_stage", "unnamed_stage"]


# ========== Successful Lifecycle ==========


def test_successful_lifecycle_completes_all_stages():
    orchestrator = ResearchOrchestrator()
    orchestrator.register_stage(PlanningStage())
    orchestrator.register_stage(DiscoveryStage())
    orchestrator.register_stage(RetrievalStage())
    orchestrator.register_stage(ProcessingStage())
    orchestrator.register_stage(EvidenceCaptureStage())
    orchestrator.register_stage(StructuringStage())
    request = _make_request(goal="Jordan market study", source_preferences=["trade_statistics", "market_data"])
    import asyncio
    result = asyncio.run(orchestrator.execute(request, "req_success"))
    assert result.status == "completed"
    assert result.request_id == "req_success"
    assert result.goal == "Jordan market study"
    assert result.findings == []
    assert result.sources_consulted == []
    assert result.sources_failed == []
    assert result.errors is None


# ========== Context Propagation ==========


def test_context_propagates_between_stages():
    orchestrator = ResearchOrchestrator()
    orchestrator.register_stage(ContextCollectingStage())
    request = _make_request(goal="Propagated goal", scope={"domains": ["agriculture"]})
    import asyncio
    result = asyncio.run(orchestrator.execute(request, "req_ctx"))
    assert result.status == "completed"
    assert result.metadata["collected_goal"] == "Propagated goal"
    assert result.metadata["collected_scope"] == {"domains": ["agriculture"]}


# ========== Failure Handling ==========


def test_stage_failure_stops_lifecycle():
    orchestrator = ResearchOrchestrator()
    orchestrator.register_stage(PlanningStage())
    orchestrator.register_stage(FailingStage())
    orchestrator.register_stage(RetrievalStage())
    request = _make_request()
    import asyncio
    result = asyncio.run(orchestrator.execute(request, "req_fail"))
    assert result.status == "failed"
    executed_stages = [r["stage_name"] for r in result.metadata.get("stage_results", [])]
    assert "failing_stage" in executed_stages
    assert "retrieval_stage" not in executed_stages


def test_stage_failure_records_error():
    orchestrator = ResearchOrchestrator()
    orchestrator.register_stage(FailingStage())
    request = _make_request()
    import asyncio
    result = asyncio.run(orchestrator.execute(request, "req_err"))
    assert result.status == "failed"
    assert result.errors is not None
    assert any("intentional failure" in err for err in result.errors)


# ========== No External Dependencies ==========


def test_orchestrator_has_no_external_search_dependency():
    orchestrator = ResearchOrchestrator()
    orchestrator.register_stage(PlanningStage())
    orchestrator.register_stage(DiscoveryStage())
    request = _make_request()
    import asyncio
    result = asyncio.run(orchestrator.execute(request, "req_no_ext"))
    assert result.status == "completed"
    assert "stage_results" in result.metadata


def test_orchestrator_has_no_llm_dependency():
    orchestrator = ResearchOrchestrator()
    orchestrator.register_stage(PlanningStage())
    request = _make_request()
    import asyncio
    result = asyncio.run(orchestrator.execute(request, "req_no_llm"))
    assert result.status == "completed"
    assert "plan" in result.metadata


# ========== Partial Results ==========


def test_partial_results_after_source_failure():
    from app.research.sources.registry import SourceRegistry
    from app.research.sources.discovery import SourceDiscovery
    from app.schemas.research import Source, SourceRegistration

    registry = SourceRegistry()
    source_a = Source(source_id="source_a", name="A", source_type="market_data", status="active")
    source_b = Source(source_id="source_b", name="B", source_type="market_data", status="active")
    registry.register(SourceRegistration(source=source_a))
    registry.register(SourceRegistration(source=source_b))
    discovery = SourceDiscovery(registry=registry)

    orchestrator = ResearchOrchestrator()
    orchestrator.register_stage(PlanningStage())
    orchestrator.register_stage(DiscoveryStage(discovery=discovery))
    orchestrator.register_stage(RetrievalStage())
    orchestrator.register_stage(FailingStage())
    orchestrator.register_stage(StructuringStage())
    request = _make_request(source_preferences=["source_a", "source_b"])
    import asyncio
    result = asyncio.run(orchestrator.execute(request, "req_partial"))
    assert result.status == "partial"
    assert "source_a" in result.sources_consulted
    assert "source_b" in result.sources_consulted
    assert "failing_stage" in [r["stage_name"] for r in result.metadata.get("stage_results", []) if not r["success"]]
    assert "structuring_stage" not in [r["stage_name"] for r in result.metadata.get("stage_results", [])]


# ========== DiscoveryStage Integration ==========


def test_discovery_stage_with_registry():
    from app.research.sources.registry import SourceRegistry
    from app.research.sources.discovery import SourceDiscovery

    registry = SourceRegistry()
    source = _make_source(source_type="market_data", domains=["agriculture"])
    registry.register(SourceRegistration(source=source))
    discovery = SourceDiscovery(registry=registry)
    orchestrator = ResearchOrchestrator()
    orchestrator.register_stage(PlanningStage())
    orchestrator.register_stage(DiscoveryStage(discovery=discovery))
    orchestrator.register_stage(RetrievalStage())
    orchestrator.register_stage(ProcessingStage())
    orchestrator.register_stage(EvidenceCaptureStage())
    orchestrator.register_stage(StructuringStage())
    request = _make_request(goal="Jordan market", source_preferences=[source.source_id])
    import asyncio
    result = asyncio.run(orchestrator.execute(request, "req_disc"))
    assert result.status == "completed"
    assert source.source_id in result.sources_consulted


def test_discovery_stage_without_registry_returns_empty():
    orchestrator = ResearchOrchestrator()
    orchestrator.register_stage(PlanningStage())
    orchestrator.register_stage(DiscoveryStage())
    orchestrator.register_stage(RetrievalStage())
    orchestrator.register_stage(ProcessingStage())
    orchestrator.register_stage(EvidenceCaptureStage())
    orchestrator.register_stage(StructuringStage())
    request = _make_request()
    import asyncio
    result = asyncio.run(orchestrator.execute(request, "req_no_reg"))
    assert result.status == "completed"
    assert result.sources_consulted == []


def test_discovery_stage_respects_source_preferences():
    from app.research.sources.registry import SourceRegistry
    from app.research.sources.discovery import SourceDiscovery

    registry = SourceRegistry()
    source_a = _make_source(source_type="market_data")
    source_b = _make_source(source_type="news")
    registry.register(SourceRegistration(source=source_a))
    registry.register(SourceRegistration(source=source_b))
    discovery = SourceDiscovery(registry=registry)
    orchestrator = ResearchOrchestrator()
    orchestrator.register_stage(PlanningStage())
    orchestrator.register_stage(DiscoveryStage(discovery=discovery))
    orchestrator.register_stage(RetrievalStage())
    orchestrator.register_stage(ProcessingStage())
    orchestrator.register_stage(EvidenceCaptureStage())
    orchestrator.register_stage(StructuringStage())
    request = _make_request(source_preferences=[source_a.source_id])
    import asyncio
    result = asyncio.run(orchestrator.execute(request, "req_pref"))
    assert result.status == "completed"
    assert result.sources_consulted == [source_a.source_id]
