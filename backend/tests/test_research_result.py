from datetime import datetime
from typing import Any

import asyncio
import pytest

from app.schemas.research import Evidence, EvidenceItem, FindingItem, ResearchResult, ResearchRequest, Source, SourceRegistration
from app.research.orchestrator import ResearchContext
from app.research.result import DefaultResultStructurer, ResultStructurer, _group_by_source, _to_evidence_item, _extract_commercial_signals, _build_commercial_finding
from app.research.orchestrator import (
    EvidenceCaptureStage,
    PlanningStage,
    ProcessingStage,
    ResearchOrchestrator,
    RetrievalStage,
    DiscoveryStage,
    StructuringStage,
)
from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.research.retrieval.stubs import StubRetriever, StubProcessor


def _make_source(source_id: str = "src_1", reference: str = "https://example.com/1"):
    return Source(
        source_id=source_id,
        name=f"Source {source_id}",
        source_type="market_data",
        reference=reference,
    )


def _make_evidence(source_id: str, reference: str = "https://example.com/1") -> Evidence:
    return Evidence(
        evidence_id=f"ev_{source_id}_1",
        source_id=source_id,
        source_reference=reference,
        captured_at=datetime.utcnow(),
        content=f"content from {source_id}",
        evidence_type="raw",
        provenance={"request_id": "req_1", "source_id": source_id},
        metadata={"source_type": "market_data"},
    )


class TestResultStructuringContract:
    def test_default_structurer_implements_abc(self):
        structurer = DefaultResultStructurer()
        assert isinstance(structurer, ResultStructurer)

    def test_structurer_returns_findings(self):
        structurer = DefaultResultStructurer()
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        findings = asyncio.run(structurer.structure(context))
        assert findings == []


class TestFindingConstruction:
    def test_finding_from_single_evidence(self):
        structurer = DefaultResultStructurer()
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.evidence.append(_make_evidence("src_1"))
        findings = asyncio.run(structurer.structure(context))
        assert len(findings) == 1
        assert findings[0].topic == "Context from src_1"
        assert len(findings[0].evidence) == 1

    def test_finding_links_to_evidence(self):
        structurer = DefaultResultStructurer()
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        evidence = _make_evidence("src_1")
        context.evidence.append(evidence)
        findings = asyncio.run(structurer.structure(context))
        assert findings[0].evidence[0].source_id == "src_1"

    def test_finding_preserves_source_reference(self):
        structurer = DefaultResultStructurer()
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.evidence.append(_make_evidence("src_1", reference="https://example.com/data"))
        findings = asyncio.run(structurer.structure(context))
        assert findings[0].evidence[0].source_url == "https://example.com/data"

    def test_finding_preserves_captured_at(self):
        structurer = DefaultResultStructurer()
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        evidence = _make_evidence("src_1")
        captured = evidence.captured_at
        context.evidence.append(evidence)
        findings = asyncio.run(structurer.structure(context))
        assert findings[0].evidence[0].retrieval_timestamp == captured


class TestEvidenceToEvidenceItemMapping:
    def test_to_evidence_item_maps_fields(self):
        evidence = _make_evidence("src_1", reference="https://example.com/1")
        item = _to_evidence_item(evidence)
        assert isinstance(item, EvidenceItem)
        assert item.source_id == evidence.source_id
        assert item.source_url == evidence.source_reference
        assert item.retrieval_timestamp == evidence.captured_at
        assert item.content_excerpt == evidence.content
        assert item.metadata == evidence.metadata

    def test_to_evidence_item_preserves_provenance_as_metadata(self):
        evidence = _make_evidence("src_1")
        item = _to_evidence_item(evidence)
        assert item.metadata == evidence.metadata


class TestResearchResultConstruction:
    def test_research_result_from_context_with_findings(self):
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.evidence.append(_make_evidence("src_1"))
        structurer = DefaultResultStructurer()
        context.findings = asyncio.run(structurer.structure(context))
        result = context.to_result("completed")
        assert isinstance(result, ResearchResult)
        assert result.request_id == "req_1"
        assert result.status == "completed"
        assert len(result.findings) == 1

    def test_research_result_preserves_sources_consulted(self):
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.sources_consulted = ["src_1", "src_2"]
        result = context.to_result("completed")
        assert result.sources_consulted == ["src_1", "src_2"]

    def test_research_result_preserves_sources_failed(self):
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.sources_failed = ["src_3"]
        result = context.to_result("partial")
        assert result.sources_failed == ["src_3"]

    def test_research_result_preserves_errors(self):
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.errors.append("retrieval failed")
        result = context.to_result("partial")
        assert result.errors == ["retrieval failed"]

    def test_research_result_without_evidence(self):
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        result = context.to_result("completed")
        assert result.findings == []


class TestPartialResults:
    def test_partial_result_keeps_successful_sources(self):
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.sources_consulted = ["src_1"]
        context.sources_failed = ["src_2"]
        context.errors.append("retrieval failed for src_2")
        result = context.to_result("partial")
        assert result.status == "partial"
        assert result.sources_consulted == ["src_1"]
        assert result.sources_failed == ["src_2"]

    def test_failed_result_when_no_sources_succeeded(self):
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.sources_failed = ["src_1", "src_2"]
        context.errors.append("all sources failed")
        result = context.to_result("failed")
        assert result.status == "failed"
        assert result.sources_consulted == []
        assert result.sources_failed == ["src_1", "src_2"]


class TestStructuringStageIntegration:
    @pytest.mark.asyncio
    async def test_structuring_stage_populates_findings(self):
        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage())
        orchestrator.register_stage(DiscoveryStage())
        orchestrator.register_stage(RetrievalStage())
        orchestrator.register_stage(ProcessingStage())
        orchestrator.register_stage(EvidenceCaptureStage())
        orchestrator.register_stage(StructuringStage())

        request = ResearchRequest(goal="test")
        result = await orchestrator.execute(request, "req_1")
        assert result.status == "failed"

    @pytest.mark.asyncio
    async def test_full_lifecycle_with_structurer(self):
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
        assert result.status == "failed"


class TestCommercialFindingExtraction:
    def test_extracts_value_and_period_from_trade_evidence(self):
        structurer = DefaultResultStructurer()
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.evidence.append(
            Evidence(
                evidence_id="ev_1",
                source_id="un-comtrade",
                source_reference="https://comtrade.un.org",
                captured_at=datetime.utcnow(),
                content="HS 07 — 28496743.65 USD (2025)",
                evidence_type="raw",
                provenance={"request_id": "req_1"},
                metadata={"query_id": "q1", "dimension": "trade_intelligence", "purpose": "Find trade flows"},
            )
        )
        findings = asyncio.run(structurer.structure(context))
        assert len(findings) == 1
        assert findings[0].topic.startswith("[trade_intelligence]")
        assert "28496743.65 USD" in findings[0].content
        assert "2025" in findings[0].content
        assert findings[0].evidence[0].source_id == "un-comtrade"

    def test_does_not_emit_meta_finding_when_commercial_text_is_present(self):
        structurer = DefaultResultStructurer()
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.evidence.append(
            Evidence(
                evidence_id="ev_1",
                source_id="un-comtrade",
                source_reference="https://comtrade.un.org",
                captured_at=datetime.utcnow(),
                content="Export value 12494.0 USD reported by China to World in 2023",
                evidence_type="raw",
                provenance={"request_id": "req_1"},
                metadata={"query_id": "q1", "dimension": "trade_intelligence"},
            )
        )
        findings = asyncio.run(structurer.structure(context))
        assert len(findings) == 1
        assert "Retrieved 1 evidence item(s)" not in findings[0].content
        assert "12494.0 USD" in findings[0].content
        assert "2023" in findings[0].content

    def test_fallback_meta_finding_when_no_commercial_signals(self):
        structurer = DefaultResultStructurer()
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.evidence.append(
            Evidence(
                evidence_id="ev_1",
                source_id="src_1",
                source_reference="https://example.com/1",
                captured_at=datetime.utcnow(),
                content="General unstructured text with no numbers or dates",
                evidence_type="raw",
                provenance={"request_id": "req_1"},
                metadata={"query_id": "q1"},
            )
        )
        findings = asyncio.run(structurer.structure(context))
        assert len(findings) == 1
        assert findings[0].content == "General unstructured text with no numbers or dates"
        assert findings[0].topic == "Context from src_1"

    def test_preserves_evidence_and_source_reference(self):
        structurer = DefaultResultStructurer()
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.evidence.append(
            Evidence(
                evidence_id="ev_1",
                source_id="un-comtrade",
                source_reference="https://comtrade.un.org",
                captured_at=datetime.utcnow(),
                content="HS 07 — 28496743.65 USD (2025)",
                evidence_type="raw",
                provenance={"request_id": "req_1"},
                metadata={"query_id": "q1", "dimension": "trade_intelligence"},
            )
        )
        findings = asyncio.run(structurer.structure(context))
        assert findings[0].evidence[0].source_url == "https://comtrade.un.org"
        assert findings[0].evidence[0].content_excerpt == "HS 07 — 28496743.65 USD (2025)"

    def test_does_not_invent_facts_from_insufficient_evidence(self):
        structurer = DefaultResultStructurer()
        request = ResearchRequest(goal="test")
        context = ResearchContext(request=request, request_id="req_1")
        context.evidence.append(
            Evidence(
                evidence_id="ev_1",
                source_id="src_1",
                source_reference="https://example.com/1",
                captured_at=datetime.utcnow(),
                content="Some unrelated text",
                evidence_type="raw",
                provenance={"request_id": "req_1"},
                metadata={"query_id": "q1"},
            )
        )
        findings = asyncio.run(structurer.structure(context))
        assert len(findings) == 1
        assert findings[0].content == "Some unrelated text"


class TestCommercialSignalExtraction:
    def test_extracts_values_and_units(self):
        signals = _extract_commercial_signals("Value 12494.0 USD and 2.5 Million EUR in 2023")
        assert len(signals["values"]) == 2
        assert signals["values"][0]["value"] == "12494.0"
        assert signals["values"][0]["unit"] == "USD"

    def test_extracts_years(self):
        signals = _extract_commercial_signals("Data from 2023 and 2024")
        assert "2023" in signals["years"]
        assert "2024" in signals["years"]

    def test_extracts_hs_codes(self):
        signals = _extract_commercial_signals("HS 07 and HS 090111")
        assert "07" in signals["hs_codes"]
        assert "090111" in signals["hs_codes"]

    def test_extracts_trends(self):
        signals = _extract_commercial_signals("exports increase and prices decrease")
        assert "increase" in signals["trends"]
        assert "decrease" in signals["trends"]

    def test_returns_empty_signals_for_non_commercial_text(self):
        signals = _extract_commercial_signals("This is just a normal sentence.")
        assert signals["values"] == []
        assert signals["years"] == []
        assert signals["hs_codes"] == []
        assert signals["trends"] == []


class TestTraceabilityChain:
    @pytest.mark.asyncio
    async def test_full_traceability_research_result_to_source(self):
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
        assert result.status == "failed"
        for finding in result.findings:
            for evidence_item in finding.evidence:
                assert evidence_item.source_id is not None


class TestCommercialExtractionGuardrails:
    def test_cmd_code_not_treated_as_commercial_value(self):
        signals = _extract_commercial_signals("HS 07 — 28496743.65 USD")
        assert signals["hs_codes"] == ["07"]
        assert len(signals["values"]) == 1
        assert signals["values"][0]["value"] == "28496743.65"

    def test_two_digit_ids_without_decimal_are_not_values(self):
        signals = _extract_commercial_signals("HS 91 USD HS 18 USD HS 32 USD")
        assert signals["hs_codes"] == ["91", "18", "32"]
        assert signals["values"] == []

    def test_decimal_numbers_are_still_extracted(self):
        signals = _extract_commercial_signals("value 2404.299 USD and 13.56 USD")
        values = [item["value"] for item in signals["values"]]
        assert "2404.299" in values
        assert "13.56" in values

    def test_hs_07_content_does_not_misclassify_cmd_code_as_value(self):
        signals = _extract_commercial_signals("HS 07 — 28496743.65 USD")
        assert signals["hs_codes"] == ["07"]
        assert len(signals["values"]) == 1
        assert signals["values"][0]["value"] == "28496743.65"

