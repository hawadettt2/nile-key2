from datetime import datetime
from typing import Any, List

import pytest

from app.schemas.research import Evidence, EvidenceItem, FindingItem, ResearchResult, ResearchRequest, Source, SourceRegistration
from app.research.quality import (
    DefaultVerifier,
    FailureHandler,
    OpenArchitecturalDecision,
    QualityIndicator,
    VerificationResult,
    Verifier,
)
from app.research.orchestrator import (
    EvidenceCaptureStage,
    PlanningStage,
    ProcessingStage,
    ResearchOrchestrator,
    RetrievalStage,
    DiscoveryStage,
    StructuringStage,
    VerificationStage,
)
from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.research.retrieval.contracts import RetrievedContent
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.research.retrieval.stubs import StubRetriever, StubProcessor


def _make_source(source_id: str = "src_1", reference: str = "https://example.com/1"):
    return Source(
        source_id=source_id,
        name=f"Source {source_id}",
        source_type="market_data",
        reference=reference,
    )


def _make_evidence(source_id: str) -> Evidence:
    return Evidence(
        evidence_id=f"ev_{source_id}_1",
        source_id=source_id,
        source_reference="https://example.com/1",
        captured_at=datetime.utcnow(),
        content="content",
        evidence_type="raw",
        provenance={"request_id": "req_1", "source_id": source_id},
        metadata={"source_type": "market_data"},
    )


class TestVerificationLayer:
    @pytest.mark.asyncio
    async def test_verify_complete_result(self):
        verifier = DefaultVerifier()
        result = ResearchResult(
            request_id="req_1",
            status="completed",
            goal="test",
            findings=[],
            sources_consulted=["src_1"],
            sources_failed=[],
            errors=None,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        verification = await verifier.verify(result)
        assert verification.verified is True

    @pytest.mark.asyncio
    async def test_verify_result_with_evidence(self):
        verifier = DefaultVerifier()
        finding = FindingItem(
            topic="topic",
            content="content",
            evidence=[EvidenceItem(source_id="src_1", retrieval_timestamp=datetime.utcnow(), content_excerpt="excerpt")],
        )
        result = ResearchResult(
            request_id="req_1",
            status="completed",
            goal="test",
            findings=[finding],
            sources_consulted=["src_1"],
            sources_failed=[],
            errors=None,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        verification = await verifier.verify(result)
        assert verification.verified is True
        assert not verification.provenance_issues

    @pytest.mark.asyncio
    async def test_verify_detects_missing_fields(self):
        verifier = DefaultVerifier()
        result = ResearchResult(
            request_id="",
            status="",
            goal="",
            findings=[],
            sources_consulted=[],
            sources_failed=[],
            errors=None,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        verification = await verifier.verify(result)
        assert verification.verified is False
        assert len(verification.missing_fields) > 0

    @pytest.mark.asyncio
    async def test_verify_detects_finding_without_evidence(self):
        verifier = DefaultVerifier()
        finding = FindingItem(
            topic="topic",
            content="content",
            evidence=[],
        )
        result = ResearchResult(
            request_id="req_1",
            status="completed",
            goal="test",
            findings=[finding],
            sources_consulted=["src_1"],
            sources_failed=[],
            errors=None,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        verification = await verifier.verify(result)
        assert any("no evidence" in issue for issue in verification.provenance_issues)

    @pytest.mark.asyncio
    async def test_verify_records_open_decisions(self):
        verifier = DefaultVerifier()
        result = ResearchResult(
            request_id="req_1",
            status="completed",
            goal="test",
            findings=[],
            sources_consulted=[],
            sources_failed=[],
            errors=None,
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
        )
        verification = await verifier.verify(result)
        assert len(verification.open_decisions) == 3
        assert verification.open_decisions[0].id == "OAD-1"


class TestFailureHandling:
    def test_determine_status_completed(self):
        status = FailureHandler.determine_status(
            sources_consulted=["src_1"],
            sources_failed=[],
            errors=[],
        )
        assert status == "completed"

    def test_determine_status_partial(self):
        status = FailureHandler.determine_status(
            sources_consulted=["src_1"],
            sources_failed=["src_2"],
            errors=["retrieval failed"],
        )
        assert status == "partial"

    def test_determine_status_failed(self):
        status = FailureHandler.determine_status(
            sources_consulted=[],
            sources_failed=["src_1"],
            errors=["all failed"],
        )
        assert status == "failed"

    def test_is_partial(self):
        assert FailureHandler.is_partial(["src_1"], ["src_2"]) is True
        assert FailureHandler.is_partial([], ["src_1"]) is False

    def test_is_failed(self):
        assert FailureHandler.is_failed([], ["src_1"]) is True
        assert FailureHandler.is_failed(["src_1"], ["src_2"]) is False


class TestVerificationStageIntegration:
    @pytest.mark.asyncio
    async def test_verification_stage_runs(self):
        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage())
        orchestrator.register_stage(DiscoveryStage())
        orchestrator.register_stage(RetrievalStage())
        orchestrator.register_stage(ProcessingStage())
        orchestrator.register_stage(EvidenceCaptureStage())
        orchestrator.register_stage(StructuringStage())
        orchestrator.register_stage(VerificationStage())

        request = ResearchRequest(goal="test")
        result = await orchestrator.execute(request, "req_1")
        assert result.status == "completed"


class TestPartialAndFailedResults:
    @pytest.mark.asyncio
    async def test_partial_result_keeps_successful_sources(self):
        registry = SourceRegistry()
        registry.register(SourceRegistration(source=_make_source("src_1")))
        registry.register(SourceRegistration(source=_make_source("src_2")))

        class FailingRetriever:
            async def retrieve(self, source, query):
                from app.research.retrieval.contracts import RetrievalResult, RetrievalStatus
                return RetrievalResult(
                    source_id=source.source_id,
                    status=RetrievalStatus.SUCCESS if source.source_id == "src_1" else RetrievalStatus.FAILED,
                    content=RetrievedContent(
                        source_id=source.source_id,
                        raw_content="content",
                        content_type="text/plain",
                    ) if source.source_id == "src_1" else None,
                    error="failed" if source.source_id == "src_2" else None,
                )

        retrieval_orchestrator = RetrievalOrchestrator(
            retriever=FailingRetriever(),
            processor=StubProcessor(),
        )

        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage())
        orchestrator.register_stage(DiscoveryStage(discovery=SourceDiscovery(registry=registry)))
        orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=retrieval_orchestrator, registry=registry))
        orchestrator.register_stage(ProcessingStage(processor=StubProcessor()))
        orchestrator.register_stage(EvidenceCaptureStage(registry=registry))
        orchestrator.register_stage(StructuringStage())
        orchestrator.register_stage(VerificationStage())

        request = ResearchRequest(goal="test", source_preferences=["src_1", "src_2"])
        result = await orchestrator.execute(request, "req_1")
        assert result.status == "partial"
        assert "src_1" in result.sources_consulted
        assert "src_2" in result.sources_failed

    @pytest.mark.asyncio
    async def test_failed_result_when_all_sources_fail(self):
        registry = SourceRegistry()
        registry.register(SourceRegistration(source=_make_source("src_1")))

        class FailingRetriever:
            async def retrieve(self, source, query):
                from app.research.retrieval.contracts import RetrievalResult, RetrievalStatus
                return RetrievalResult(
                    source_id=source.source_id,
                    status=RetrievalStatus.FAILED,
                    content=None,
                    error="failed",
                )

        retrieval_orchestrator = RetrievalOrchestrator(
            retriever=FailingRetriever(),
            processor=StubProcessor(),
        )

        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage())
        orchestrator.register_stage(DiscoveryStage(discovery=SourceDiscovery(registry=registry)))
        orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=retrieval_orchestrator, registry=registry))
        orchestrator.register_stage(ProcessingStage(processor=StubProcessor()))
        orchestrator.register_stage(EvidenceCaptureStage(registry=registry))
        orchestrator.register_stage(StructuringStage())
        orchestrator.register_stage(VerificationStage())

        request = ResearchRequest(goal="test", source_preferences=["src_1"])
        result = await orchestrator.execute(request, "req_1")
        assert result.status == "failed"


class TestNoLLMDependency:
    def test_verifier_has_no_llm_dependency(self):
        verifier = DefaultVerifier()
        assert not hasattr(verifier, "llm")
        assert not hasattr(verifier, "model")

    def test_failure_handler_has_no_llm_dependency(self):
        handler = FailureHandler()
        assert not hasattr(handler, "llm")
        assert not hasattr(handler, "model")


class TestTraceabilityAfterVerification:
    @pytest.mark.asyncio
    async def test_traceability_preserved_after_verification(self):
        registry = SourceRegistry()
        source = _make_source("src_1", reference="https://example.com/1")
        registry.register(SourceRegistration(source=source))

        retrieval_orchestrator = RetrievalOrchestrator(
            retriever=StubRetriever(),
            processor=StubProcessor(),
        )

        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage())
        orchestrator.register_stage(DiscoveryStage())
        orchestrator.register_stage(RetrievalStage(retrieval_orchestrator=retrieval_orchestrator, registry=registry))
        orchestrator.register_stage(ProcessingStage(processor=StubProcessor()))
        orchestrator.register_stage(EvidenceCaptureStage(registry=registry))
        orchestrator.register_stage(StructuringStage())
        orchestrator.register_stage(VerificationStage())

        request = ResearchRequest(goal="test")
        result = await orchestrator.execute(request, "req_1")
        assert result.status == "completed"
        for finding in result.findings:
            for evidence_item in finding.evidence:
                assert evidence_item.source_id is not None
