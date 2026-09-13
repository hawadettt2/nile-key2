import pytest
from datetime import datetime, timezone

from app.agent.business_intelligence.schema import (
    EvidenceReference,
    Finding,
    Entity,
    Comparison,
    BusinessRanking,
    RankingEntry,
    Opportunity,
    Risk,
    Recommendation,
    Limitation,
    BusinessIntelligenceAnswer,
)
from app.agent.business_intelligence.evidence import (
    adapt_evidence_item,
    adapt_finding_item,
    adapt_research_result,
)
from app.agent.business_intelligence.synthesizer import BusinessIntelligenceSynthesizer
from app.schemas.research import EvidenceItem, FindingItem, ResearchResult


class FakeMission:
    def __init__(self, mission_id, status, result=None, context=None, goal=None):
        self.mission_id = mission_id
        self.status = status
        self.result = result or {}
        self.context = context or {}
        self.goal = goal


def _make_evidence_item(source_id="src-1", content_excerpt="excerpt", confidence=0.9):
    return EvidenceItem(
        source_id=source_id,
        source_url="https://example.com",
        retrieval_timestamp=datetime.now(timezone.utc),
        content_excerpt=content_excerpt,
        metadata={"key": "value"},
    )


def _make_finding_item(topic="topic", content="content", evidence=None, confidence=0.9, limitations=None):
    return FindingItem(
        topic=topic,
        content=content,
        evidence=evidence or [_make_evidence_item()],
        confidence=confidence,
        limitations=limitations,
    )


def _make_research_result(findings=None, sources_consulted=None, status="completed"):
    return ResearchResult(
        request_id="req-1",
        status=status,
        goal="Test goal",
        findings=findings or [_make_finding_item()],
        sources_consulted=sources_consulted or ["src-1"],
        sources_failed=[],
        errors=None,
        created_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        metadata={"key": "value"},
    )


class TestEvidenceReference:
    def test_required_fields(self):
        ref = EvidenceReference(source_id="src-1", content_excerpt="excerpt", retrieval_timestamp="2024-01-01T00:00:00")
        assert ref.source_id == "src-1"
        assert ref.content_excerpt == "excerpt"
        assert ref.retrieval_timestamp == "2024-01-01T00:00:00"
        assert ref.confidence is None
        assert ref.limitations is None
        assert ref.provenance is None

    def test_optional_fields(self):
        ref = EvidenceReference(
            source_id="src-1",
            source_url="https://example.com",
            content_excerpt="excerpt",
            retrieval_timestamp="2024-01-01T00:00:00",
            confidence=0.8,
            limitations=["lim1"],
            provenance={"origin": "test"},
        )
        assert ref.source_url == "https://example.com"
        assert ref.confidence == 0.8
        assert ref.limitations == ["lim1"]
        assert ref.provenance == {"origin": "test"}

    def test_confidence_range(self):
        with pytest.raises(Exception):
            EvidenceReference(
                source_id="src-1",
                content_excerpt="excerpt",
                retrieval_timestamp="2024-01-01T00:00:00",
                confidence=1.5,
            )


class TestAdaptEvidenceItem:
    def test_adapt_evidence_item(self):
        item = _make_evidence_item(source_id="src-1", content_excerpt="test excerpt", confidence=0.9)
        ref = adapt_evidence_item(item)
        assert ref.source_id == "src-1"
        assert ref.source_url == "https://example.com"
        assert ref.content_excerpt == "test excerpt"
        assert isinstance(ref.retrieval_timestamp, str)
        assert ref.confidence is None
        assert ref.provenance is None


class TestAdaptFindingItem:
    def test_adapt_finding_item(self):
        finding = _make_finding_item(topic="t1", content="c1", confidence=0.9)
        adapted = adapt_finding_item(finding)
        assert adapted.topic == "t1"
        assert adapted.content == "c1"
        assert len(adapted.evidence) == 1
        assert adapted.confidence == 0.9
        assert adapted.limitations is None


class TestAdaptResearchResult:
    def test_adapt_research_result(self):
        research = _make_research_result()
        evidence, sources = adapt_research_result(research)
        assert len(evidence) == 1
        assert len(sources) == 1
        assert sources[0] == "src-1"


class TestBusinessIntelligenceAnswer:
    def test_minimal_insufficient_evidence(self):
        answer = BusinessIntelligenceAnswer(
            executive_summary="لا توجد أدلة كافية.",
            confidence="insufficient_evidence",
        )
        assert answer.goal is None
        assert answer.confidence == "insufficient_evidence"
        assert answer.key_findings == []
        assert answer.limitations == []

    def test_full_answer(self):
        ref = EvidenceReference(
            source_id="src-1",
            content_excerpt="excerpt",
            retrieval_timestamp="2024-01-01T00:00:00",
        )
        finding = Finding(topic="t1", content="c1", evidence=[ref])
        entity = Entity(name="Company A", type="company", source="src-1", evidence=[ref])
        opportunity = Opportunity(description="opp", evidence=[ref])
        risk = Risk(description="risk", evidence=[ref])
        recommendation = Recommendation(
            action="act",
            type="business_recommendation",
            rationale="rationale",
            evidence=[ref],
        )
        limitation = Limitation(
            what_is_missing="data",
            why_it_matters="matters",
            what_evidence_is_needed="evidence",
        )
        answer = BusinessIntelligenceAnswer(
            goal="goal",
            executive_summary="summary",
            key_findings=[finding],
            entities=[entity],
            opportunities=[opportunity],
            risks=[risk],
            recommendations=[recommendation],
            limitations=[limitation],
            evidence=[ref],
            sources=["src-1"],
        )
        assert answer.goal == "goal"
        assert len(answer.key_findings) == 1
        assert len(answer.entities) == 1
        assert len(answer.recommendations) == 1
        assert answer.recommendations[0].type == "business_recommendation"
        assert len(answer.limitations) == 1


class TestBusinessIntelligenceSynthesizer:
    @pytest.mark.asyncio
    async def test_synthesize_without_research_returns_insufficient_evidence(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(mission=mission)
        assert answer.confidence == "insufficient_evidence"
        assert len(answer.recommendations) == 1
        assert answer.recommendations[0].type == "next_evidence_requirement"

    @pytest.mark.asyncio
    async def test_synthesize_with_research(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result()
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.confidence != "insufficient_evidence"
        assert len(answer.key_findings) == 1
        assert len(answer.evidence) == 1
        assert len(answer.sources) == 1

    @pytest.mark.asyncio
    async def test_synthesize_preserves_mission_result(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        original_result = {"shipment_id": 42}
        mission = FakeMission(mission_id="m1", status="completed", result=original_result)
        await synthesizer.synthesize(mission=mission)
        assert mission.result == original_result

    @pytest.mark.asyncio
    async def test_synthesize_no_fabricated_entities(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(mission=mission)
        assert answer.entities == []

    @pytest.mark.asyncio
    async def test_synthesize_no_fabricated_rankings(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(mission=mission)
        assert answer.rankings is None

    @pytest.mark.asyncio
    async def test_synthesize_no_fabricated_recommendations_without_evidence(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result(
            findings=[_make_finding_item(topic="t", content="c", evidence=[], confidence=None)]
        )
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        for rec in answer.recommendations:
            if rec.type == "business_recommendation":
                assert rec.evidence
