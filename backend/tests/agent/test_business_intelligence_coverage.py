import pytest
from datetime import datetime, timezone

from app.agent.business_intelligence.coverage import (
    BusinessIntelligenceCoverage,
    CoverageBuilder,
    CoverageEntry,
    SourceExecutionStatus,
)
from app.agent.business_intelligence.schema import EvidenceReference
from app.agent.business_intelligence.synthesizer import BusinessIntelligenceSynthesizer
from app.schemas.research import EvidenceItem, FindingItem, ResearchResult


def _make_evidence_item(source_id="src-1", content_excerpt="excerpt", metadata=None):
    return EvidenceItem(
        source_id=source_id,
        source_url="https://example.com",
        retrieval_timestamp=datetime.now(timezone.utc),
        content_excerpt=content_excerpt,
        metadata=metadata,
    )


def _make_finding_item(topic="topic", content="content", evidence=None, confidence=0.9, limitations=None):
    return FindingItem(
        topic=topic,
        content=content,
        evidence=evidence or [_make_evidence_item()],
        confidence=confidence,
        limitations=limitations,
    )


def _make_research_result(
    findings=None,
    sources_consulted=None,
    status="completed",
    source_execution_statuses=None,
):
    if findings is None:
        findings = [_make_finding_item()]
    if sources_consulted is None:
        sources_consulted = ["src-1"]
    if source_execution_statuses is None:
        source_execution_statuses = {"src-1": SourceExecutionStatus.SUCCESS_WITH_DATA}
    return ResearchResult(
        request_id="req-1",
        status=status,
        goal="Test goal",
        findings=findings,
        sources_consulted=sources_consulted,
        sources_failed=[],
        errors=None,
        created_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        metadata={"key": "value"},
        source_execution_statuses=source_execution_statuses,
    )


class TestCoverageBuilder:
    def test_adequate_coverage_with_successful_sources(self):
        research = _make_research_result(
            source_execution_statuses={"src-1": SourceExecutionStatus.SUCCESS_WITH_DATA}
        )
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="excerpt",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        coverage = CoverageBuilder.build(research, evidence, [])
        assert coverage.coverage_level == "adequate"
        assert coverage.successful_sources == 1
        assert coverage.failed_sources == 0
        assert coverage.empty_sources == 0

    def test_partial_coverage_with_failed_sources(self):
        research = _make_research_result(
            source_execution_statuses={
                "src-1": SourceExecutionStatus.SUCCESS_WITH_DATA,
                "src-2": SourceExecutionStatus.FAILED,
            }
        )
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="excerpt",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        coverage = CoverageBuilder.build(research, evidence, [])
        assert coverage.coverage_level == "partial"
        assert coverage.failed_sources == 1

    def test_partial_coverage_with_empty_sources(self):
        research = _make_research_result(
            source_execution_statuses={
                "src-1": SourceExecutionStatus.SUCCESS_EMPTY,
                "src-2": SourceExecutionStatus.SUCCESS_WITH_DATA,
            }
        )
        evidence = [
            EvidenceReference(
                source_id="src-2",
                source_url="https://example.com",
                content_excerpt="excerpt",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        coverage = CoverageBuilder.build(research, evidence, [])
        assert coverage.coverage_level == "partial"
        assert coverage.empty_sources == 1

    def test_insufficient_coverage_without_successful_sources(self):
        research = _make_research_result(
            source_execution_statuses={
                "src-1": SourceExecutionStatus.FAILED,
            }
        )
        coverage = CoverageBuilder.build(research, [], [])
        assert coverage.coverage_level == "insufficient"
        assert coverage.successful_sources == 0

    def test_insufficient_coverage_with_no_evidence(self):
        research = _make_research_result(
            source_execution_statuses={
                "src-1": SourceExecutionStatus.SUCCESS_EMPTY,
            }
        )
        coverage = CoverageBuilder.build(research, [], [])
        assert coverage.coverage_level == "insufficient"

    def test_coverage_without_research_but_with_evidence(self):
        coverage = CoverageBuilder.build(None, [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="excerpt",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ], [])
        assert coverage.coverage_level == "adequate"
        assert coverage.total_sources == 1

    def test_coverage_entries_preserve_source_identity(self):
        research = _make_research_result(
            source_execution_statuses={
                "src-1": SourceExecutionStatus.SUCCESS_WITH_DATA,
                "src-2": SourceExecutionStatus.FAILED,
            }
        )
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com/1",
                content_excerpt="excerpt",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        coverage = CoverageBuilder.build(research, evidence, [])
        src1_entry = next(e for e in coverage.entries if e.source_id == "src-1")
        src2_entry = next(e for e in coverage.entries if e.source_id == "src-2")
        assert src1_entry.status == SourceExecutionStatus.SUCCESS_WITH_DATA
        assert src1_entry.source_url == "https://example.com/1"
        assert src2_entry.status == SourceExecutionStatus.FAILED
        assert src2_entry.has_evidence is False

    def test_coverage_dimensions_from_facts(self):
        from app.agent.business_intelligence.facts import BusinessFact, FactType
        facts = [
            BusinessFact(
                fact_type=FactType.TRADE_FLOW,
                dimension="trade_intelligence",
                query_id="q-1",
                statement="Trade fact.",
            ),
            BusinessFact(
                fact_type=FactType.MARKET_INDICATOR,
                dimension="market_opportunity",
                query_id="q-2",
                statement="Opportunity fact.",
            ),
        ]
        coverage = CoverageBuilder.build(None, [], facts)
        assert "trade_intelligence" in coverage.dimensions_covered
        assert "market_opportunity" in coverage.dimensions_covered

    def test_coverage_limitations_for_failed_sources(self):
        research = _make_research_result(
            source_execution_statuses={
                "src-1": SourceExecutionStatus.FAILED,
            }
        )
        coverage = CoverageBuilder.build(research, [], [])
        assert any("failed during retrieval" in lim for lim in coverage.limitations)

    def test_coverage_limitations_for_empty_sources(self):
        research = _make_research_result(
            source_execution_statuses={
                "src-1": SourceExecutionStatus.SUCCESS_EMPTY,
            }
        )
        coverage = CoverageBuilder.build(research, [], [])
        assert any("returned no usable data" in lim for lim in coverage.limitations)

    def test_coverage_limitations_for_no_successful_evidence(self):
        research = _make_research_result(
            source_execution_statuses={
                "src-1": SourceExecutionStatus.SUCCESS_EMPTY,
            }
        )
        coverage = CoverageBuilder.build(research, [], [])
        assert any("No authoritative evidence was successfully retrieved" in lim for lim in coverage.limitations)


class TestBusinessIntelligenceSynthesizerPhase6:
    @pytest.mark.asyncio
    async def test_synthesize_includes_coverage_in_provenance(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert "coverage" in answer.provenance
        coverage = answer.provenance["coverage"]
        assert coverage["coverage_level"] == "adequate"

    @pytest.mark.asyncio
    async def test_synthesize_coverage_partial_with_failed_sources(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result(
            source_execution_statuses={
                "src-1": SourceExecutionStatus.SUCCESS_WITH_DATA,
                "src-2": SourceExecutionStatus.FAILED,
            }
        )
        research.sources_consulted = ["src-1", "src-2"]
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.provenance["coverage"]["coverage_level"] == "partial"
        assert answer.provenance["coverage"]["failed_sources"] == 1

    @pytest.mark.asyncio
    async def test_synthesize_coverage_insufficient_without_evidence(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result(
            source_execution_statuses={
                "src-1": SourceExecutionStatus.SUCCESS_EMPTY,
            }
        )
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.provenance["coverage"]["coverage_level"] == "insufficient"

    @pytest.mark.asyncio
    async def test_synthesize_coverage_distinguishes_failed_from_empty(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result(
            source_execution_statuses={
                "src-1": SourceExecutionStatus.FAILED,
                "src-2": SourceExecutionStatus.SUCCESS_EMPTY,
                "src-3": SourceExecutionStatus.SUCCESS_WITH_DATA,
            }
        )
        research.sources_consulted = ["src-1", "src-2", "src-3"]
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        coverage = answer.provenance["coverage"]
        assert coverage["coverage_level"] == "partial"
        assert coverage["failed_sources"] == 1
        assert coverage["empty_sources"] == 1
        assert coverage["successful_sources"] == 1

    @pytest.mark.asyncio
    async def test_synthesize_coverage_does_not_treat_completed_status_as_adequate(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result(
            status="completed",
            source_execution_statuses={
                "src-1": SourceExecutionStatus.SUCCESS_EMPTY,
            },
        )
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.provenance["research_status"] == "completed"
        assert answer.provenance["coverage"]["coverage_level"] == "insufficient"

    @pytest.mark.asyncio
    async def test_synthesize_coverage_preserves_source_identity_and_url(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        finding = _make_finding_item(
            evidence=[
                EvidenceItem(
                    source_id="src-1",
                    source_url="https://example.com/1",
                    retrieval_timestamp=datetime.now(timezone.utc),
                    content_excerpt="excerpt",
                    metadata=None,
                )
            ]
        )
        research = _make_research_result(
            findings=[finding],
            source_execution_statuses={"src-1": SourceExecutionStatus.SUCCESS_WITH_DATA},
        )
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        coverage = answer.provenance["coverage"]
        src1_entry = next(e for e in coverage["entries"] if e["source_id"] == "src-1")
        assert src1_entry["source_url"] == "https://example.com/1"
        assert src1_entry["has_evidence"] is True
