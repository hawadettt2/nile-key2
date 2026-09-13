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


def _make_research_result(findings=None, sources_consulted=None, status="completed"):
    if findings is None:
        findings = [_make_finding_item()]
    if sources_consulted is None:
        sources_consulted = ["src-1"]
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
    def test_adapt_evidence_item_preserves_fields(self):
        item = _make_evidence_item(source_id="src-1", content_excerpt="test excerpt", metadata={"origin": "test"})
        ref = adapt_evidence_item(item)
        assert ref.source_id == "src-1"
        assert ref.source_url == "https://example.com"
        assert ref.content_excerpt == "test excerpt"
        assert isinstance(ref.retrieval_timestamp, str)
        assert ref.confidence is None
        assert ref.limitations is None
        assert ref.provenance is None

    def test_adapt_evidence_item_with_none_metadata(self):
        item = _make_evidence_item(metadata=None)
        item.metadata = None
        ref = adapt_evidence_item(item)
        assert ref.source_id == "src-1"
        assert ref.content_excerpt == "excerpt"


class TestAdaptFindingItem:
    def test_adapt_finding_item(self):
        finding = _make_finding_item(topic="t1", content="c1", confidence=0.9)
        adapted = adapt_finding_item(finding)
        assert adapted.topic == "t1"
        assert adapted.content == "c1"
        assert len(adapted.evidence) == 1
        assert adapted.confidence == 0.9
        assert adapted.limitations is None

    def test_adapt_finding_item_preserves_confidence(self):
        finding = _make_finding_item(topic="t1", content="c1", confidence=0.7, limitations=["lim1"])
        adapted = adapt_finding_item(finding)
        assert adapted.confidence == 0.7
        assert adapted.limitations == ["lim1"]


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
            confidence=None,
        )
        assert answer.goal is None
        assert answer.confidence is None
        assert answer.key_findings == []
        assert answer.limitations == []
        assert answer.entities == []
        assert answer.opportunities == []
        assert answer.risks == []
        assert answer.recommendations == []

    def test_full_answer(self):
        ref = EvidenceReference(
            source_id="src-1",
            content_excerpt="excerpt",
            retrieval_timestamp="2024-01-01T00:00:00",
        )
        finding = Finding(topic="t1", content="c1", evidence=[ref], confidence=0.9)
        entity = Entity(name="Company A", type="company", source="src-1", evidence=[ref])
        opportunity = Opportunity(description="opp", evidence=[ref], confidence=0.8)
        risk = Risk(description="risk", evidence=[ref], severity="high")
        recommendation = Recommendation(
            action="act",
            type="business_recommendation",
            rationale="rationale",
            evidence=[ref],
            confidence=0.9,
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
            confidence=0.85,
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
        assert answer.confidence == 0.85


class TestBusinessIntelligenceSynthesizer:
    @pytest.mark.asyncio
    async def test_synthesize_without_research_returns_numeric_confidence_none(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(mission=mission)
        assert answer.confidence is None
        assert answer.recommendations == []
        assert answer.entities == []
        assert answer.opportunities == []
        assert answer.risks == []

    @pytest.mark.asyncio
    async def test_synthesize_with_research(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result()
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert len(answer.key_findings) == 1
        assert len(answer.evidence) == 1
        assert len(answer.sources) == 1
        assert answer.confidence == 0.9

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
    async def test_synthesize_no_heuristic_opportunities(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result(
            findings=[_make_finding_item(topic="growth", content="potential growth in market")]
        )
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.opportunities == []

    @pytest.mark.asyncio
    async def test_synthesize_no_heuristic_risks(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result(
            findings=[_make_finding_item(topic="risk", content="potential risk in market")]
        )
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.risks == []

    @pytest.mark.asyncio
    async def test_synthesize_no_heuristic_recommendations(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result(
            findings=[_make_finding_item(topic="t", content="c", evidence=[], confidence=None)]
        )
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.recommendations == []

    @pytest.mark.asyncio
    async def test_synthesize_confidence_numeric(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result(
            findings=[_make_finding_item(topic="t", content="c", confidence=0.7)]
        )
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert isinstance(answer.confidence, float)
        assert answer.confidence == 0.7

    @pytest.mark.asyncio
    async def test_synthesize_confidence_none_when_no_confidence(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result(
            findings=[_make_finding_item(topic="t", content="c", confidence=None)]
        )
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.confidence is None

    @pytest.mark.asyncio
    async def test_synthesize_confidence_none_when_no_findings(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result(findings=[])
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.confidence is None

    @pytest.mark.asyncio
    async def test_synthesize_comparisons_none(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result()
        mission = FakeMission(mission_id="m1", status="completed")
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.comparisons is None
