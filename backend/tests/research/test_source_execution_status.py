import uuid
import pytest
import asyncio
from typing import Optional, Dict, Any

from app.research.retrieval.contracts import (
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
    SourceExecutionStatus,
    SourceRetriever,
)
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.research.orchestrator import (
    ResearchOrchestrator,
    PlanningStage,
    DiscoveryStage,
    RetrievalStage,
    ProcessingStage,
    EvidenceCaptureStage,
    StructuringStage,
)
from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.schemas.research import Source, SourceRegistration, ResearchRequest


def _make_source(source_id=None, source_type="market_data", status="active"):
    return Source(
        source_id=source_id or f"src_{uuid.uuid4().hex[:8]}",
        name=f"Test Source {source_id or 'unknown'}",
        source_type=source_type,
        reference="https://example.com/data",
        metadata={"domains": ["agriculture"]},
        status=status,
    )


class _DataRetriever(SourceRetriever):
    async def retrieve(self, source: Source, query: str, context: Optional[Dict[str, Any]] = None, scope: Optional[Dict[str, Any]] = None) -> RetrievalResult:
        return RetrievalResult(
            source_id=source.source_id,
            status=RetrievalStatus.SUCCESS,
            content=RetrievedContent(
                source_id=source.source_id,
                raw_content={"query": query, "source": source.name},
                content_type="application/json",
                metadata={"retrieved": True},
            ),
        )


class _EmptyRetriever(SourceRetriever):
    async def retrieve(self, source: Source, query: str, context: Optional[Dict[str, Any]] = None, scope: Optional[Dict[str, Any]] = None) -> RetrievalResult:
        return RetrievalResult(
            source_id=source.source_id,
            status=RetrievalStatus.SUCCESS,
            content=RetrievedContent(
                source_id=source.source_id,
                raw_content=None,
                content_type="application/json",
                metadata={"retrieved": True},
            ),
        )


class _MixedRetriever(SourceRetriever):
    def __init__(self, empty_source_id=None, fail_on_source_id=None):
        self.empty_source_id = empty_source_id
        self.fail_on_source_id = fail_on_source_id

    async def retrieve(self, source: Source, query: str, context: Optional[Dict[str, Any]] = None, scope: Optional[Dict[str, Any]] = None) -> RetrievalResult:
        if self.fail_on_source_id and source.source_id == self.fail_on_source_id:
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.FAILED,
                error="Connection refused",
            )
        if self.empty_source_id and source.source_id == self.empty_source_id:
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.SUCCESS,
                content=RetrievedContent(
                    source_id=source.source_id,
                    raw_content=None,
                    content_type="application/json",
                    metadata={"retrieved": True},
                ),
            )
        return RetrievalResult(
            source_id=source.source_id,
            status=RetrievalStatus.SUCCESS,
            content=RetrievedContent(
                source_id=source.source_id,
                raw_content={"query": query, "source": source.name},
                content_type="application/json",
                metadata={"retrieved": True},
            ),
        )


class TestSourceExecutionStatusNormalization:
    def test_success_with_data_sets_correct_status(self):
        registry = SourceRegistry()
        source = _make_source(source_id="src_data")
        registry.register(SourceRegistration(source=source))
        discovery = SourceDiscovery(registry=registry)
        orchestrator = RetrievalOrchestrator(retriever=_DataRetriever())

        research_orchestrator = ResearchOrchestrator()
        research_orchestrator.register_stage(PlanningStage())
        research_orchestrator.register_stage(DiscoveryStage(discovery=discovery))
        research_orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=orchestrator, registry=registry))
        research_orchestrator.register_stage(ProcessingStage())
        research_orchestrator.register_stage(EvidenceCaptureStage())
        research_orchestrator.register_stage(StructuringStage())

        request = ResearchRequest(goal="test", source_preferences=["src_data"])
        result = asyncio.run(research_orchestrator.execute(request, "req_data"))
        assert result.status == "completed"
        assert "src_data" in result.sources_consulted
        assert result.source_execution_statuses is not None
        assert result.source_execution_statuses.get("src_data") == SourceExecutionStatus.SUCCESS_WITH_DATA

    def test_success_empty_sets_correct_status(self):
        registry = SourceRegistry()
        source = _make_source(source_id="src_empty")
        registry.register(SourceRegistration(source=source))
        discovery = SourceDiscovery(registry=registry)
        orchestrator = RetrievalOrchestrator(retriever=_EmptyRetriever())

        research_orchestrator = ResearchOrchestrator()
        research_orchestrator.register_stage(PlanningStage())
        research_orchestrator.register_stage(DiscoveryStage(discovery=discovery))
        research_orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=orchestrator, registry=registry))
        research_orchestrator.register_stage(ProcessingStage())
        research_orchestrator.register_stage(EvidenceCaptureStage())
        research_orchestrator.register_stage(StructuringStage())

        request = ResearchRequest(goal="test", source_preferences=["src_empty"])
        result = asyncio.run(research_orchestrator.execute(request, "req_empty"))
        assert result.status == "failed"
        assert "src_empty" not in result.sources_consulted
        assert "src_empty" not in result.sources_failed
        assert result.source_execution_statuses is not None
        assert result.source_execution_statuses.get("src_empty") == SourceExecutionStatus.SUCCESS_EMPTY

    def test_failed_sets_correct_status(self):
        registry = SourceRegistry()
        source_fail = _make_source(source_id="src_fail")
        registry.register(SourceRegistration(source=source_fail))
        discovery = SourceDiscovery(registry=registry)
        orchestrator = RetrievalOrchestrator(retriever=_MixedRetriever(fail_on_source_id="src_fail"))

        research_orchestrator = ResearchOrchestrator()
        research_orchestrator.register_stage(PlanningStage())
        research_orchestrator.register_stage(DiscoveryStage(discovery=discovery))
        research_orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=orchestrator, registry=registry))
        research_orchestrator.register_stage(ProcessingStage())
        research_orchestrator.register_stage(EvidenceCaptureStage())
        research_orchestrator.register_stage(StructuringStage())

        request = ResearchRequest(goal="test", source_preferences=["src_fail"])
        result = asyncio.run(research_orchestrator.execute(request, "req_fail"))
        assert result.status == "failed"
        assert "src_fail" in result.sources_failed
        assert result.source_execution_statuses is not None
        assert result.source_execution_statuses.get("src_fail") == SourceExecutionStatus.FAILED

    def test_failed_distinct_from_success_empty(self):
        registry = SourceRegistry()
        source_empty = _make_source(source_id="src_empty")
        source_fail = _make_source(source_id="src_fail")
        registry.register(SourceRegistration(source=source_empty))
        registry.register(SourceRegistration(source=source_fail))
        discovery = SourceDiscovery(registry=registry)
        orchestrator = RetrievalOrchestrator(retriever=_MixedRetriever(empty_source_id="src_empty", fail_on_source_id="src_fail"))

        research_orchestrator = ResearchOrchestrator()
        research_orchestrator.register_stage(PlanningStage())
        research_orchestrator.register_stage(DiscoveryStage(discovery=discovery))
        research_orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=orchestrator, registry=registry))
        research_orchestrator.register_stage(ProcessingStage())
        research_orchestrator.register_stage(EvidenceCaptureStage())
        research_orchestrator.register_stage(StructuringStage())

        request = ResearchRequest(goal="test", source_preferences=["src_empty", "src_fail"])
        result = asyncio.run(research_orchestrator.execute(request, "req_mixed"))
        assert result.source_execution_statuses is not None
        assert result.source_execution_statuses.get("src_empty") == SourceExecutionStatus.SUCCESS_EMPTY
        assert result.source_execution_statuses.get("src_fail") == SourceExecutionStatus.FAILED
        assert result.source_execution_statuses.get("src_empty") != result.source_execution_statuses.get("src_fail")

    def test_aggregation_preserves_per_source_status(self):
        registry = SourceRegistry()
        source_data = _make_source(source_id="src_data")
        source_empty = _make_source(source_id="src_empty")
        source_fail = _make_source(source_id="src_fail")
        registry.register(SourceRegistration(source=source_data))
        registry.register(SourceRegistration(source=source_empty))
        registry.register(SourceRegistration(source=source_fail))
        discovery = SourceDiscovery(registry=registry)
        orchestrator = RetrievalOrchestrator(retriever=_MixedRetriever(empty_source_id="src_empty", fail_on_source_id="src_fail"))

        research_orchestrator = ResearchOrchestrator()
        research_orchestrator.register_stage(PlanningStage())
        research_orchestrator.register_stage(DiscoveryStage(discovery=discovery))
        research_orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=orchestrator, registry=registry))
        research_orchestrator.register_stage(ProcessingStage())
        research_orchestrator.register_stage(EvidenceCaptureStage())
        research_orchestrator.register_stage(StructuringStage())

        request = ResearchRequest(goal="test", source_preferences=["src_data", "src_empty", "src_fail"])
        result = asyncio.run(research_orchestrator.execute(request, "req_agg"))
        assert result.source_execution_statuses is not None
        assert len(result.source_execution_statuses) == 3
        assert result.source_execution_statuses.get("src_data") == SourceExecutionStatus.SUCCESS_WITH_DATA
        assert result.source_execution_statuses.get("src_empty") == SourceExecutionStatus.SUCCESS_EMPTY
        assert result.source_execution_statuses.get("src_fail") == SourceExecutionStatus.FAILED
