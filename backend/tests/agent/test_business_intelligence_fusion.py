import pytest
from datetime import datetime, timezone

from app.agent.business_intelligence.facts import BusinessFact, FactType
from app.agent.business_intelligence.fusion import (
    InputNormalizer,
    BusinessFactNormalizer,
    FactFusion,
)
from app.agent.business_intelligence.schema import (
    BusinessIntelligenceInput,
    EvidenceReference,
)
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


class TestInputNormalizer:
    def test_normalize_extracts_goal_from_bi_input_goal(self):
        bi_input = BusinessIntelligenceInput(
            goal={"objective": "test goal"},
            research_result=None,
        )
        normalized = InputNormalizer.normalize(bi_input)
        assert normalized["goal"] == "test goal"

    def test_normalize_extracts_goal_from_research_result(self):
        research = _make_research_result()
        bi_input = BusinessIntelligenceInput(
            goal=None,
            research_result=research,
        )
        normalized = InputNormalizer.normalize(bi_input)
        assert normalized["goal"] == "Test goal"

    def test_normalize_returns_none_goal_when_no_sources(self):
        bi_input = BusinessIntelligenceInput(
            goal=None,
            research_result=None,
            decision=None,
            execution_outcome=None,
        )
        normalized = InputNormalizer.normalize(bi_input)
        assert normalized["goal"] is None

    def test_normalize_validates_research_result_dict(self):
        research_dict = _make_research_result().model_dump(mode="json")
        bi_input = BusinessIntelligenceInput(
            goal=None,
            research_result=research_dict,
        )
        normalized = InputNormalizer.normalize(bi_input)
        assert normalized["research"] is not None
        assert normalized["research"].status == "completed"

    def test_normalize_handles_invalid_research_result_dict(self):
        bi_input = BusinessIntelligenceInput(
            goal=None,
            research_result={"invalid": True},
        )
        with pytest.raises(ValueError):
            InputNormalizer.normalize(bi_input)

    def test_normalize_extracts_goal_from_decision(self):
        bi_input = BusinessIntelligenceInput(
            goal=None,
            decision={"chosen_path": "research path"},
            research_result=None,
        )
        normalized = InputNormalizer.normalize(bi_input)
        assert normalized["goal"] == "research path"


class TestBusinessFactNormalizer:
    def test_normalize_findings_creates_facts(self):
        normalizer = BusinessFactNormalizer()
        findings = [_make_finding_item(topic="t1", content="c1")]
        facts = normalizer.normalize_findings(findings, "trade_intelligence", "q-1")
        assert len(facts) == 1
        assert facts[0].fact_type == FactType.TRADE_FLOW
        assert facts[0].dimension == "trade_intelligence"
        assert facts[0].query_id == "q-1"
        assert facts[0].statement == "c1"

    def test_normalize_findings_maps_dimensions_to_fact_types(self):
        normalizer = BusinessFactNormalizer()
        mapping = {
            "trade_intelligence": FactType.TRADE_FLOW,
            "market_opportunity": FactType.MARKET_INDICATOR,
            "market_access": FactType.MARKET_ACCESS_REQUIREMENT,
            "regulatory_sps_tbt": FactType.REGULATORY_REQUIREMENT,
            "rules_of_origin": FactType.ORIGIN_REQUIREMENT,
            "agrifood_intelligence": FactType.AGRIFOOD_CONDITION,
            "logistics_market_execution": FactType.LOGISTICS_FACT,
        }
        for dimension, expected_type in mapping.items():
            facts = normalizer.normalize_findings([_make_finding_item()], dimension, "q-1")
            assert facts[0].fact_type == expected_type

    def test_normalize_findings_unknown_dimension_maps_to_other(self):
        normalizer = BusinessFactNormalizer()
        facts = normalizer.normalize_findings([_make_finding_item()], "unknown_dimension", "q-1")
        assert facts[0].fact_type == FactType.OTHER

    def test_normalize_findings_preserves_evidence(self):
        normalizer = BusinessFactNormalizer()
        evidence = [_make_evidence_item(source_id="src-1", content_excerpt="excerpt")]
        finding = _make_finding_item(evidence=evidence)
        facts = normalizer.normalize_findings([finding], "trade_intelligence", "q-1")
        assert len(facts[0].evidence) == 1
        assert facts[0].evidence[0].source_id == "src-1"
        assert facts[0].evidence[0].content_excerpt == "excerpt"

    def test_normalize_findings_preserves_confidence(self):
        normalizer = BusinessFactNormalizer()
        finding = _make_finding_item(confidence=0.85)
        facts = normalizer.normalize_findings([finding], "trade_intelligence", "q-1")
        assert facts[0].confidence == 0.85

    def test_normalize_findings_sets_source_ids(self):
        normalizer = BusinessFactNormalizer()
        evidence = [
            _make_evidence_item(source_id="src-1"),
            _make_evidence_item(source_id="src-2"),
            _make_evidence_item(source_id="src-1"),
        ]
        finding = _make_finding_item(evidence=evidence)
        facts = normalizer.normalize_findings([finding], "trade_intelligence", "q-1")
        assert facts[0].source_ids == ["src-1", "src-2"]

    def test_normalize_findings_extracts_commercial_value_and_unit(self):
        normalizer = BusinessFactNormalizer()
        evidence = [
            _make_evidence_item(
                source_id="un-comtrade",
                content_excerpt="HS 07 — 28496743.65 USD (2025)",
                metadata={"query_id": "q1", "dimension": "trade_intelligence"},
            )
        ]
        finding = _make_finding_item(
            topic="[trade_intelligence] Trade value",
            content="Values: 28496743.65 USD; Period(s): 2025",
            evidence=evidence,
            confidence=0.9,
        )
        facts = normalizer.normalize_findings([finding], "trade_intelligence", "q-1")
        assert len(facts) == 1
        assert facts[0].value == 28496743.65
        assert facts[0].unit == "USD"
        assert "28496743.65 USD" in facts[0].statement
        assert "2025" in facts[0].statement

    def test_normalize_findings_does_not_create_fact_from_meta_finding(self):
        normalizer = BusinessFactNormalizer()
        evidence = [
            _make_evidence_item(
                source_id="un-comtrade",
                content_excerpt="some content",
            )
        ]
        finding = _make_finding_item(
            topic="[trade_intelligence] Findings from un-comtrade",
            content="Retrieved 1 evidence item(s) from source un-comtrade.",
            evidence=evidence,
        )
        facts = normalizer.normalize_findings([finding], "trade_intelligence", "q-1")
        assert facts == []

    def test_normalize_findings_skips_finding_without_evidence(self):
        normalizer = BusinessFactNormalizer()
        finding = FindingItem(
            topic="t1",
            content="c1",
            evidence=[],
            confidence=None,
            limitations=None,
        )
        facts = normalizer.normalize_findings([finding], "trade_intelligence", "q-1")
        assert facts == []

    def test_normalize_findings_preserves_provenance_traceability(self):
        normalizer = BusinessFactNormalizer()
        evidence = [
            _make_evidence_item(
                source_id="un-comtrade",
                content_excerpt="HS 07 — 28496743.65 USD (2025)",
                metadata={"query_id": "q1", "dimension": "trade_intelligence"},
            )
        ]
        finding = _make_finding_item(
            topic="[trade_intelligence] Trade value",
            content="Values: 28496743.65 USD; Period(s): 2025",
            evidence=evidence,
            confidence=0.9,
        )
        facts = normalizer.normalize_findings([finding], "trade_intelligence", "q-1")
        assert len(facts) == 1
        assert facts[0].source_ids == ["un-comtrade"]
        assert facts[0].evidence[0].source_id == "un-comtrade"
        assert facts[0].evidence[0].content_excerpt == "HS 07 — 28496743.65 USD (2025)"
        assert facts[0].provenance["topic"] == "[trade_intelligence] Trade value"

    def test_normalize_knowledge_result_creates_facts(self):
        normalizer = BusinessFactNormalizer()
        knowledge_result = {
            "results": [
                {
                    "id": "k1",
                    "content": "Egypt exports vegetables to Jordan",
                    "source_id": "company-knowledge",
                    "confidence": 0.9,
                    "metadata": {"title": "Trade Guide", "source_url": "https://example.com/guide"},
                }
            ],
            "confidence": 0.9,
            "sources": ["company-knowledge"],
        }
        facts = normalizer.normalize_knowledge_result(knowledge_result)
        assert len(facts) == 1
        assert facts[0].fact_type == FactType.DOCUMENTED_ENTITY
        assert facts[0].dimension == "company_knowledge"
        assert facts[0].statement == "Egypt exports vegetables to Jordan"
        assert facts[0].confidence == 0.9
        assert facts[0].source_ids == ["company-knowledge"]
        assert len(facts[0].evidence) == 1
        assert facts[0].evidence[0].source_url == "https://example.com/guide"

    def test_normalize_knowledge_result_skips_empty_content(self):
        normalizer = BusinessFactNormalizer()
        knowledge_result = {
            "results": [
                {"id": "k1", "content": "", "source_id": "company-knowledge", "confidence": 0.9},
            ],
            "confidence": 0.9,
            "sources": ["company-knowledge"],
        }
        facts = normalizer.normalize_knowledge_result(knowledge_result)
        assert facts == []

    def test_normalize_knowledge_result_handles_non_dict_items(self):
        normalizer = BusinessFactNormalizer()
        knowledge_result = {
            "results": ["not-a-dict"],
            "confidence": 0.9,
            "sources": ["company-knowledge"],
        }
        facts = normalizer.normalize_knowledge_result(knowledge_result)
        assert facts == []


class TestFactFusion:
    def test_deduplicate_removes_duplicate_facts(self):
        ref1 = EvidenceReference(
            source_id="src-1",
            source_url="https://example.com",
            content_excerpt="excerpt",
            retrieval_timestamp="2024-01-01T00:00:00",
        )
        ref2 = EvidenceReference(
            source_id="src-2",
            source_url="https://example.com",
            content_excerpt="excerpt",
            retrieval_timestamp="2024-01-01T00:00:00",
        )
        fact1 = BusinessFact(
            fact_type=FactType.TRADE_FLOW,
            dimension="trade_intelligence",
            query_id="q-1",
            statement="same statement",
            evidence=[ref1],
            source_ids=["src-1"],
        )
        fact2 = BusinessFact(
            fact_type=FactType.TRADE_FLOW,
            dimension="trade_intelligence",
            query_id="q-1",
            statement="same statement",
            evidence=[ref2],
            source_ids=["src-2"],
        )
        result = FactFusion.deduplicate([fact1, fact2])
        assert len(result) == 1
        assert len(result[0].evidence) == 2
        assert result[0].source_ids == ["src-1", "src-2"]

    def test_deduplicate_preserves_unique_facts(self):
        fact1 = BusinessFact(
            fact_type=FactType.TRADE_FLOW,
            dimension="trade_intelligence",
            query_id="q-1",
            statement="statement A",
        )
        fact2 = BusinessFact(
            fact_type=FactType.MARKET_INDICATOR,
            dimension="market_opportunity",
            query_id="q-2",
            statement="statement B",
        )
        result = FactFusion.deduplicate([fact1, fact2])
        assert len(result) == 2

    def test_detect_conflicts_identifies_conflicting_values(self):
        fact1 = BusinessFact(
            fact_type=FactType.MARKET_INDICATOR,
            dimension="market_opportunity",
            query_id="q-1",
            statement="market size",
            value=100,
            source_ids=["src-1"],
        )
        fact2 = BusinessFact(
            fact_type=FactType.MARKET_INDICATOR,
            dimension="market_opportunity",
            query_id="q-1",
            statement="market size",
            value=200,
            source_ids=["src-2"],
        )
        conflicts = FactFusion.detect_conflicts([fact1, fact2])
        assert len(conflicts) == 1
        assert conflicts[0]["values"] == [100, 200]
        assert conflicts[0]["source_ids"] == ["src-1", "src-2"]

    def test_detect_conflicts_no_conflict_when_same_value(self):
        fact1 = BusinessFact(
            fact_type=FactType.MARKET_INDICATOR,
            dimension="market_opportunity",
            query_id="q-1",
            statement="market size",
            value=100,
        )
        fact2 = BusinessFact(
            fact_type=FactType.MARKET_INDICATOR,
            dimension="market_opportunity",
            query_id="q-1",
            statement="market size",
            value=100,
        )
        conflicts = FactFusion.detect_conflicts([fact1, fact2])
        assert conflicts == []

    def test_detect_conflicts_no_conflict_when_none_values(self):
        fact1 = BusinessFact(
            fact_type=FactType.MARKET_INDICATOR,
            dimension="market_opportunity",
            query_id="q-1",
            statement="market size",
        )
        fact2 = BusinessFact(
            fact_type=FactType.MARKET_INDICATOR,
            dimension="market_opportunity",
            query_id="q-1",
            statement="market size",
        )
        conflicts = FactFusion.detect_conflicts([fact1, fact2])
        assert conflicts == []


class TestBusinessIntelligenceSynthesizerFactFusion:
    @pytest.mark.asyncio
    async def test_synthesize_produces_facts_with_research(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert len(answer.key_findings) == 1
        assert len(answer.evidence) == 1
        assert answer.provenance.get("fact_count", 0) == 1

    @pytest.mark.asyncio
    async def test_synthesize_no_facts_without_research(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(mission=mission)
        assert answer.provenance.get("fact_count", 0) == 0

    @pytest.mark.asyncio
    async def test_synthesize_facts_deduplicated(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        finding = _make_finding_item(topic="t1", content="c1")
        research = _make_research_result(findings=[finding, finding])
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.provenance.get("fact_count", 0) == 2

    @pytest.mark.asyncio
    async def test_synthesize_preserves_provenance(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert "research_status" in answer.provenance
        assert answer.provenance["research_status"] == "completed"
        assert "fact_count" in answer.provenance

    @pytest.mark.asyncio
    async def test_synthesize_conflicts_become_limitations(self, monkeypatch):
        conflicts = [
            {
                "dimension": "trade_intelligence",
                "query_id": "q-0",
                "statement": "market size",
                "values": [100, 200],
                "source_ids": ["src-1", "src-2"],
            }
        ]
        monkeypatch.setattr(FactFusion, "detect_conflicts", lambda facts: conflicts)
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert len(answer.limitations) >= 1
        assert any("Conflicting values" in str(lim.what_is_missing) for lim in answer.limitations)
        assert any("src-1" in str(lim.what_evidence_is_needed) for lim in answer.limitations)

    @pytest.mark.asyncio
    async def test_synthesize_produces_facts_from_knowledge_result(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        knowledge_result = {
            "results": [
                {
                    "id": "k1",
                    "content": "company knowledge fact",
                    "source_id": "company-knowledge",
                    "confidence": 0.9,
                    "metadata": {"title": "Guide", "source_url": "https://example.com/guide"},
                }
            ],
            "confidence": 0.9,
            "sources": ["company-knowledge"],
        }
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            knowledge_result=knowledge_result,
        )
        assert answer.provenance.get("fact_count", 0) == 1
        assert len(answer.evidence) == 1
        assert answer.evidence[0].source_id == "company-knowledge"
        assert answer.sources == ["company-knowledge"]

    @pytest.mark.asyncio
    async def test_synthesize_knowledge_result_skips_empty_content(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        knowledge_result = {
            "results": [
                {"id": "k1", "content": "", "source_id": "company-knowledge", "confidence": 0.9},
            ],
            "confidence": 0.9,
            "sources": ["company-knowledge"],
        }
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            knowledge_result=knowledge_result,
        )
        assert answer.provenance.get("fact_count", 0) == 0
        assert len(answer.evidence) == 0

    @pytest.mark.asyncio
    async def test_synthesize_knowledge_and_research_fused_together(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        research = _make_research_result()
        knowledge_result = {
            "results": [
                {
                    "id": "k1",
                    "content": "knowledge fact",
                    "source_id": "company-knowledge",
                    "confidence": 0.8,
                    "metadata": {},
                }
            ],
            "confidence": 0.8,
            "sources": ["company-knowledge"],
        }
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
            knowledge_result=knowledge_result,
        )
        assert answer.provenance.get("fact_count", 0) == 2
        assert len(answer.evidence) == 2
        assert "src-1" in answer.sources
        assert "company-knowledge" in answer.sources
