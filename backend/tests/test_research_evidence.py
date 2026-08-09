import asyncio
from datetime import datetime
from typing import Optional

import pytest

from app.schemas.research import (
    Evidence,
    ResearchRequest,
    Source,
    SourceRegistration,
)
from app.research.evidence.contracts import DefaultEvidenceCapture, EvidenceCapture, ProvenanceRecord
from app.research.retrieval.contracts import RetrievedContent, RetrievalStatus
from app.research.orchestrator import (
    EvidenceCaptureStage,
    PlanningStage,
    ProcessingStage,
    ResearchContext,
    ResearchOrchestrator,
    RetrievalStage,
    DiscoveryStage,
    StructuringStage,
)
from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.research.retrieval.stubs import StubRetriever, StubProcessor


def _make_source(source_id: str = "src_1", reference: Optional[str] = None):
    return Source(
        source_id=source_id,
        name=f"Source {source_id}",
        source_type="market_data",
        reference=reference,
    )


class TestEvidenceModel:
    def test_create_evidence_with_required_fields(self):
        evidence = Evidence(
            evidence_id="ev_1",
            source_id="src_1",
            captured_at=datetime.utcnow(),
            content="sample content",
            provenance={},
        )
        assert evidence.evidence_id == "ev_1"
        assert evidence.source_id == "src_1"
        assert evidence.content == "sample content"
        assert evidence.evidence_type == "raw"

    def test_evidence_links_to_source_id(self):
        evidence = Evidence(
            evidence_id="ev_1",
            source_id="src_42",
            captured_at=datetime.utcnow(),
            content="content",
            provenance={},
        )
        assert evidence.source_id == "src_42"

    def test_evidence_links_to_reference(self):
        evidence = Evidence(
            evidence_id="ev_1",
            source_id="src_1",
            source_reference="https://example.com/data",
            captured_at=datetime.utcnow(),
            content="content",
            provenance={},
        )
        assert evidence.source_reference == "https://example.com/data"

    def test_captured_at_is_recorded(self):
        now = datetime.utcnow()
        evidence = Evidence(
            evidence_id="ev_1",
            source_id="src_1",
            captured_at=now,
            content="content",
            provenance={},
        )
        assert evidence.captured_at == now


class TestProvenanceContract:
    def test_provenance_record_creation(self):
        record = ProvenanceRecord(
            request_id="req_1",
            source_id="src_1",
            source_reference="https://example.com",
            transformation="processed",
        )
        assert record.request_id == "req_1"
        assert record.source_id == "src_1"
        assert record.source_reference == "https://example.com"
        assert record.transformation == "processed"

    def test_provenance_to_dict(self):
        record = ProvenanceRecord(
            request_id="req_1",
            source_id="src_1",
        )
        data = record.to_dict()
        assert data["request_id"] == "req_1"
        assert data["source_id"] == "src_1"
        assert "retrieval_timestamp" in data


class TestEvidenceCapture:
    @pytest.mark.asyncio
    async def test_capture_from_retrieved_content(self):
        source = _make_source("src_1", reference="https://example.com/1")
        content = RetrievedContent(
            source_id="src_1",
            raw_content="raw evidence text",
            content_type="text/plain",
        )
        capture = DefaultEvidenceCapture()
        evidence = await capture.capture(content, source, "req_1")
        assert evidence.source_id == "src_1"
        assert evidence.source_reference == "https://example.com/1"
        assert evidence.content == "raw evidence text"
        assert evidence.evidence_type == "raw"
        assert evidence.provenance["request_id"] == "req_1"

    @pytest.mark.asyncio
    async def test_capture_without_source_uses_content_source_id(self):
        content = RetrievedContent(
            source_id="src_unknown",
            raw_content="orphan evidence",
        )
        capture = DefaultEvidenceCapture()
        evidence = await capture.capture(content, None, "req_1")
        assert evidence.source_id == "src_unknown"
        assert evidence.source_reference is None
        assert evidence.content == "orphan evidence"

    @pytest.mark.asyncio
    async def test_capture_marks_processed_type(self):
        source = _make_source("src_1")
        content = RetrievedContent(source_id="src_1", raw_content="text")
        capture = DefaultEvidenceCapture()
        evidence = await capture.capture(content, source, "req_1", transformation="processed")
        assert evidence.evidence_type == "processed"
        assert evidence.provenance["transformation"] == "processed"


class TestEvidenceContextStorage:
    def test_research_context_stores_evidence(self):
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        assert context.evidence == []

    def test_evidence_can_be_added_to_context(self):
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        evidence = Evidence(
            evidence_id="ev_1",
            source_id="src_1",
            captured_at=datetime.utcnow(),
            content="content",
            provenance={},
        )
        context.evidence.append(evidence)
        assert len(context.evidence) == 1
        assert context.evidence[0].source_id == "src_1"


class TestEvidenceCaptureStageIntegration:
    @pytest.mark.asyncio
    async def test_evidence_capture_stage_with_registry(self):
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

        request = ResearchRequest(goal="test")
        result = await orchestrator.execute(request, "req_1")
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_evidence_capture_stage_without_registry(self):
        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage())
        orchestrator.register_stage(DiscoveryStage())
        orchestrator.register_stage(RetrievalStage())
        orchestrator.register_stage(ProcessingStage())
        orchestrator.register_stage(EvidenceCaptureStage())
        orchestrator.register_stage(StructuringStage())

        request = ResearchRequest(goal="test")
        result = await orchestrator.execute(request, "req_1")
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_multiple_evidence_from_same_source(self):
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

        request = ResearchRequest(goal="test")
        result = await orchestrator.execute(request, "req_1")
        assert result.status == "completed"

    @pytest.mark.asyncio
    async def test_evidence_from_multiple_sources(self):
        registry = SourceRegistry()
        registry.register(SourceRegistration(source=_make_source("src_1", reference="https://example.com/1")))
        registry.register(SourceRegistration(source=_make_source("src_2", reference="https://example.com/2")))

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

        request = ResearchRequest(goal="test")
        result = await orchestrator.execute(request, "req_1")
        assert result.status == "completed"


class TestEvidenceNoVerification:
    @pytest.mark.asyncio
    async def test_evidence_capture_does_not_verify(self):
        capture = DefaultEvidenceCapture()
        content = RetrievedContent(source_id="src_1", raw_content="unverified content")
        source = _make_source("src_1")
        evidence = await capture.capture(content, source, "req_1")
        assert evidence.provenance.get("verified") is None
        assert not hasattr(evidence, "trust_score")

    @pytest.mark.asyncio
    async def test_no_llm_dependency_in_capture(self):
        capture = DefaultEvidenceCapture()
        assert not hasattr(capture, "llm")
        assert not hasattr(capture, "model")


class TestEvidenceProvenancePreserved:
    @pytest.mark.asyncio
    async def test_provenance_preserved_after_processing(self):
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

        request = ResearchRequest(goal="test")
        result = await orchestrator.execute(request, "req_1")
        assert result.status == "completed"
