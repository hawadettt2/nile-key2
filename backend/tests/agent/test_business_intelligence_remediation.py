import pytest
from datetime import datetime, timezone

from app.agent.business_intelligence.schema import (
    BusinessIntelligenceInput,
    BusinessComparison,
    ComparisonResult,
    BusinessRanking,
    RankingEntry,
    BusinessIntelligenceAnswer,
    EvidenceReference,
)
from app.agent.business_intelligence.evidence import adapt_research_result
from app.agent.business_intelligence.synthesizer import BusinessIntelligenceSynthesizer
from app.agent.response.builder import ResponseBuilder
from app.schemas.research import EvidenceItem, FindingItem, ResearchResult


class FakeMission:
    def __init__(self, mission_id="m1", status="completed", result=None, context=None, goal=None):
        self.mission_id = mission_id
        self.status = status
        self.result = result or {}
        self.context = context or {}
        self.goal = goal


def make_research(findings=None):
    return ResearchResult(
        request_id="req-1",
        status="completed",
        goal="test goal",
        findings=findings or [],
        sources_consulted=["src-1"],
        sources_failed=[],
        errors=None,
        created_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        metadata=None,
    )


def make_finding(confidence=None, source_id="src-1", excerpt="excerpt"):
    return FindingItem(
        topic="topic",
        content="content",
        evidence=[
            EvidenceItem(
                source_id=source_id,
                source_url="https://example.com",
                retrieval_timestamp=datetime.now(timezone.utc),
                content_excerpt=excerpt,
                metadata=None,
            )
        ],
        confidence=confidence,
        limitations=None,
    )


class TestBIContractRemediation:
    def test_transport_neutral_input_contract_exists(self):
        value = BusinessIntelligenceInput(
            goal={"objective": "test"},
            decision={"chosen_path": "research"},
            mission_result={"x": 1},
            execution_outcome={"status": "completed"},
            research_result=make_research(),
        )
        assert value.goal["objective"] == "test"
        assert value.mission_result["x"] == 1

    def test_comparison_contract_is_typed(self):
        ref = EvidenceReference(source_id="src-1", content_excerpt="x", retrieval_timestamp="2026-01-01T00:00:00")
        result = ComparisonResult(option="A", criterion="demand", value=10, evidence=[ref])
        comparison = BusinessComparison(options=["A"], criteria=["demand"], results=[result])
        assert comparison.results[0].option == "A"
        assert comparison.results[0].evidence[0].source_id == "src-1"

    def test_ranking_contract_contains_scoring_metadata(self):
        ref = EvidenceReference(source_id="src-1", content_excerpt="x", retrieval_timestamp="2026-01-01T00:00:00")
        entry = RankingEntry(
            rank=1,
            candidate="A",
            criteria_scores={"demand": 0.8},
            total_score=0.8,
            evidence=[ref],
            explanation="existing scoring basis",
        )
        ranking = BusinessRanking(
            criteria=["demand"],
            entries=[entry],
            scoring_method="declared_basis",
            limitations=[],
        )
        assert ranking.criteria == ["demand"]
        assert ranking.scoring_method == "declared_basis"
        assert ranking.entries[0].total_score == 0.8


class TestBISafetyRemediation:
    @pytest.mark.asyncio
    async def test_multiple_confidences_do_not_get_aggregated(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = make_research([
            make_finding(0.9, source_id="src-1", excerpt="a"),
            make_finding(0.3, source_id="src-2", excerpt="b"),
        ])
        answer = await synthesizer.synthesize(
            mission=FakeMission(),
            research_result=research.model_dump(mode="json"),
        )
        assert answer.confidence is None

    def test_distinct_evidence_from_same_source_is_preserved(self):
        research = make_research([
            make_finding(0.9, source_id="src-1", excerpt="a"),
            make_finding(0.8, source_id="src-1", excerpt="b"),
        ])
        evidence, _ = adapt_research_result(research)
        assert len(evidence) == 2
        assert {item.content_excerpt for item in evidence} == {"a", "b"}

    @pytest.mark.asyncio
    async def test_invalid_research_result_is_observable(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        with pytest.raises(ValueError):
            await synthesizer.synthesize(
                mission=FakeMission(),
                research_result={"status": "completed", "invalid": True},
            )

    @pytest.mark.asyncio
    async def test_insufficient_research_returns_next_evidence_requirement(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = await synthesizer.synthesize(
            mission=FakeMission(),
            research_result=make_research(findings=[]).model_dump(mode="json"),
        )
        assert len(answer.recommendations) == 1
        recommendation = answer.recommendations[0]
        assert recommendation.type == "next_evidence_requirement"
        assert recommendation.evidence == []
        assert recommendation.confidence is None

    def test_response_builder_passes_business_answer_unchanged(self):
        mission = FakeMission(result={"id": 1}, context={"session_id": "s1"})
        decision = {"chosen_path": "research", "context": {"request_context": {"session_id": "s1"}}}
        answer = BusinessIntelligenceAnswer(executive_summary="summary")
        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=answer.model_dump(mode="json"),
        )
        assert intent.content["business_answer"] == answer.model_dump(mode="json")
        assert intent.content["result"] == {"id": 1}
