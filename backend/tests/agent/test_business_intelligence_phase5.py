import pytest
from datetime import datetime, timezone

from app.agent.business_intelligence.derivers import (
    ComparisonDeriver,
    EntityDeriver,
    ExecutiveSummaryDeriver,
    OpportunityDeriver,
    RiskDeriver,
)
from app.agent.business_intelligence.facts import BusinessFact, FactType
from app.agent.business_intelligence.schema import (
    BusinessEntity,
    EvidenceReference,
    Finding,
    Limitation,
    Opportunity,
    Risk,
    BusinessComparison,
    ComparisonResult,
    BusinessRanking,
    BusinessIntelligenceAnswer,
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


class TestEntityDeriver:
    def test_valid_entity_evidence_produces_entity(self):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Company A is a supplier in Egypt.",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        fact = BusinessFact(
            fact_type=FactType.DOCUMENTED_ENTITY,
            dimension="company_knowledge",
            query_id="q-1",
            statement="Company A is a supplier.",
            evidence=evidence,
            provenance={"entity_name": "Company A", "entity_type": "supplier"},
            source_ids=["src-1"],
        )
        entities = EntityDeriver.derive([fact])
        assert len(entities) == 2
        names = [e.name for e in entities]
        assert "Company A" in names
        assert "Egypt" in names

    def test_insufficient_entity_evidence_returns_empty(self):
        fact = BusinessFact(
            fact_type=FactType.DOCUMENTED_ENTITY,
            dimension="company_knowledge",
            query_id="q-1",
            statement="Some fact.",
            evidence=[],
            provenance={"entity_name": "Company A"},
            source_ids=[],
        )
        entities = EntityDeriver.derive([fact])
        assert entities == []

    def test_non_documented_entity_fact_type_returns_empty(self):
        fact = BusinessFact(
            fact_type=FactType.TRADE_FLOW,
            dimension="trade_intelligence",
            query_id="q-1",
            statement="Trade fact.",
            evidence=[],
            source_ids=[],
        )
        entities = EntityDeriver.derive([fact])
        assert entities == []

    def test_invalid_entity_type_returns_empty(self):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="No named entity here.",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        fact = BusinessFact(
            fact_type=FactType.DOCUMENTED_ENTITY,
            dimension="company_knowledge",
            query_id="q-1",
            statement="No named entity here.",
            evidence=evidence,
            provenance={"entity_name": "Company A", "entity_type": "invalid_type"},
            source_ids=["src-1"],
        )
        entities = EntityDeriver.derive([fact])
        assert entities == []

    def test_duplicate_entity_names_deduplicated(self):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Company A is a supplier.",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        fact1 = BusinessFact(
            fact_type=FactType.DOCUMENTED_ENTITY,
            dimension="company_knowledge",
            query_id="q-1",
            statement="Company A is a supplier.",
            evidence=evidence,
            provenance={"entity_name": "Company A", "entity_type": "supplier"},
            source_ids=["src-1"],
        )
        fact2 = BusinessFact(
            fact_type=FactType.DOCUMENTED_ENTITY,
            dimension="company_knowledge",
            query_id="q-2",
            statement="Company A exports vegetables.",
            evidence=evidence,
            provenance={"entity_name": "Company A", "entity_type": "supplier"},
            source_ids=["src-1"],
        )
        entities = EntityDeriver.derive([fact1, fact2])
        assert len(entities) == 1
        assert entities[0].name == "Company A"


class TestOpportunityDeriver:
    def test_valid_opportunity_signal_produces_opportunity(self):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Growing demand for Egyptian vegetables in Jordan.",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        fact = BusinessFact(
            fact_type=FactType.MARKET_INDICATOR,
            dimension="market_opportunity",
            query_id="q-1",
            statement="Growing demand for Egyptian vegetables in Jordan.",
            evidence=evidence,
            confidence=0.8,
            provenance={"opportunity_basis": "demand_growth"},
            source_ids=["src-1"],
        )
        opportunities = OpportunityDeriver.derive([fact])
        assert len(opportunities) == 1
        assert opportunities[0].description == "Growing demand for Egyptian vegetables in Jordan."
        assert opportunities[0].confidence == 0.8

    def test_neutral_fact_without_opportunity_basis_returns_empty(self):
        fact = BusinessFact(
            fact_type=FactType.TRADE_FLOW,
            dimension="trade_intelligence",
            query_id="q-1",
            statement="Trade volume is stable.",
            evidence=[],
            source_ids=[],
        )
        opportunities = OpportunityDeriver.derive([fact])
        assert opportunities == []

    def test_fact_type_not_allowed_returns_empty(self):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Regulatory requirement.",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        fact = BusinessFact(
            fact_type=FactType.REGULATORY_REQUIREMENT,
            dimension="regulatory_sps_tbt",
            query_id="q-1",
            statement="Import license required.",
            evidence=evidence,
            provenance={"opportunity_basis": "demand_growth"},
            source_ids=["src-1"],
        )
        opportunities = OpportunityDeriver.derive([fact])
        assert opportunities == []

    def test_no_evidence_returns_empty(self):
        fact = BusinessFact(
            fact_type=FactType.MARKET_INDICATOR,
            dimension="market_opportunity",
            query_id="q-1",
            statement="Growing demand.",
            evidence=[],
            provenance={"opportunity_basis": "demand_growth"},
            source_ids=[],
        )
        opportunities = OpportunityDeriver.derive([fact])
        assert opportunities == []


class TestRiskDeriver:
    def test_valid_risk_signal_produces_risk(self):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Strict pesticide residue limits apply.",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        fact = BusinessFact(
            fact_type=FactType.REGULATORY_REQUIREMENT,
            dimension="regulatory_sps_tbt",
            query_id="q-1",
            statement="Strict pesticide residue limits apply.",
            evidence=evidence,
            provenance={"risk_signal": "compliance_gap", "severity": "high"},
            source_ids=["src-1"],
        )
        risks = RiskDeriver.derive([fact])
        assert len(risks) == 1
        assert risks[0].description == "Strict pesticide residue limits apply."
        assert risks[0].severity is None

    def test_unsupported_severity_becomes_none(self):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Strict limits apply.",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        fact = BusinessFact(
            fact_type=FactType.REGULATORY_REQUIREMENT,
            dimension="regulatory_sps_tbt",
            query_id="q-1",
            statement="Strict limits apply.",
            evidence=evidence,
            provenance={"risk_signal": "compliance_gap", "severity": "critical"},
            source_ids=["src-1"],
        )
        risks = RiskDeriver.derive([fact])
        assert len(risks) == 1
        assert risks[0].severity is None

    def test_no_risk_signal_returns_empty(self):
        fact = BusinessFact(
            fact_type=FactType.REGULATORY_REQUIREMENT,
            dimension="regulatory_sps_tbt",
            query_id="q-1",
            statement="Import license required.",
            evidence=[],
            source_ids=[],
        )
        risks = RiskDeriver.derive([fact])
        assert risks == []

    def test_limitation_not_converted_to_risk(self):
        fact = BusinessFact(
            fact_type=FactType.LOGISTICS_FACT,
            dimension="logistics_market_execution",
            query_id="q-1",
            statement="Limited data available.",
            evidence=[],
            provenance={"risk_signal": "compliance_gap"},
            source_ids=[],
        )
        risks = RiskDeriver.derive([fact])
        assert risks == []


class TestComparisonDeriver:
    def test_valid_comparison_prerequisites_produce_comparison(self):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Tariff 5%",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        facts = [
            BusinessFact(
                fact_type=FactType.COMPARISON_DATUM,
                dimension="market_access",
                query_id="q-1",
                statement="Jordan tariff",
                value=5,
                evidence=evidence,
                provenance={"candidate": "Jordan", "criterion": "tariff"},
                source_ids=["src-1"],
            ),
            BusinessFact(
                fact_type=FactType.COMPARISON_DATUM,
                dimension="market_access",
                query_id="q-2",
                statement="UAE tariff",
                value=0,
                evidence=evidence,
                provenance={"candidate": "UAE", "criterion": "tariff"},
                source_ids=["src-1"],
            ),
        ]
        comparison = ComparisonDeriver.derive(facts)
        assert comparison is not None
        assert comparison.options == ["Jordan", "UAE"]
        assert comparison.criteria == ["tariff"]
        assert len(comparison.results) == 2
        assert comparison.results[0].value == 5
        assert comparison.results[1].value == 0

    def test_missing_value_skips_datum(self):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Tariff unknown",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        facts = [
            BusinessFact(
                fact_type=FactType.COMPARISON_DATUM,
                dimension="market_access",
                query_id="q-1",
                statement="Jordan tariff",
                value=None,
                evidence=evidence,
                provenance={"candidate": "Jordan", "criterion": "tariff"},
                source_ids=["src-1"],
            ),
        ]
        comparison = ComparisonDeriver.derive(facts)
        assert comparison is None

    def test_no_comparison_facts_returns_none(self):
        facts = [
            BusinessFact(
                fact_type=FactType.TRADE_FLOW,
                dimension="trade_intelligence",
                query_id="q-1",
                statement="Trade fact.",
                evidence=[],
                source_ids=[],
            ),
        ]
        comparison = ComparisonDeriver.derive(facts)
        assert comparison is None

    def test_missing_candidate_or_criterion_skips_datum(self):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Tariff 5%",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        facts = [
            BusinessFact(
                fact_type=FactType.COMPARISON_DATUM,
                dimension="market_access",
                query_id="q-1",
                statement="Jordan tariff",
                value=5,
                evidence=evidence,
                provenance={"candidate": "Jordan"},
                source_ids=["src-1"],
            ),
        ]
        comparison = ComparisonDeriver.derive(facts)
        assert comparison is None


class TestExecutiveSummaryDeriver:
    def test_substantive_summary_with_evidence(self):
        summary = ExecutiveSummaryDeriver.build(
            goal="Export vegetables to Jordan",
            key_findings=[],
            entities=[BusinessEntity(name="Company A", entity_type="supplier")],
            comparisons=None,
            opportunities=[],
            risks=[],
            limitations=[],
            fact_count=1,
        )
        assert "Goal: Export vegetables to Jordan." in summary
        assert "1 business fact(s)" in summary
        assert "1 documented entity/entities" in summary

    def test_summary_with_no_evidence_remains_qualified(self):
        summary = ExecutiveSummaryDeriver.build(
            goal="Export vegetables to Jordan",
            key_findings=[],
            entities=[],
            comparisons=None,
            opportunities=[],
            risks=[],
            limitations=[],
            fact_count=0,
        )
        assert "No substantive business sections could be derived from the current evidence." in summary

    def test_summary_mentions_limitations(self):
        summary = ExecutiveSummaryDeriver.build(
            goal="Export vegetables to Jordan",
            key_findings=[],
            entities=[],
            comparisons=None,
            opportunities=[],
            risks=[],
            limitations=[object(), object()],
            fact_count=0,
        )
        assert "2 limitation(s)" in summary

    def test_summary_without_goal(self):
        summary = ExecutiveSummaryDeriver.build(
            goal=None,
            key_findings=[],
            entities=[],
            comparisons=None,
            opportunities=[],
            risks=[],
            limitations=[],
            fact_count=0,
        )
        assert "No substantive business sections could be derived from the current evidence." in summary


class TestBusinessIntelligenceSynthesizerPhase5:
    @pytest.mark.asyncio
    async def test_synthesize_entities_from_documented_facts(self, monkeypatch):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Company A is a supplier.",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        fact = BusinessFact(
            fact_type=FactType.DOCUMENTED_ENTITY,
            dimension="company_knowledge",
            query_id="q-1",
            statement="Company A is a supplier.",
            evidence=evidence,
            provenance={"entity_name": "Company A", "entity_type": "supplier"},
            source_ids=["src-1"],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.BusinessFactNormalizer.normalize_knowledge_result",
            lambda knowledge_result: [fact],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.FactFusion.deduplicate",
            lambda facts: [fact],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.FactFusion.detect_conflicts",
            lambda facts: [],
        )

        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            knowledge_result={"results": []},
        )
        assert len(answer.entities) == 1
        assert answer.entities[0].name == "Company A"

    @pytest.mark.asyncio
    async def test_synthesize_opportunities_from_signaled_facts(self, monkeypatch):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Growing demand.",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        fact = BusinessFact(
            fact_type=FactType.MARKET_INDICATOR,
            dimension="market_opportunity",
            query_id="q-1",
            statement="Growing demand.",
            evidence=evidence,
            provenance={"opportunity_basis": "demand_growth"},
            source_ids=["src-1"],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.BusinessFactNormalizer.normalize_knowledge_result",
            lambda knowledge_result: [fact],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.FactFusion.deduplicate",
            lambda facts: [fact],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.FactFusion.detect_conflicts",
            lambda facts: [],
        )

        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            knowledge_result={"results": []},
        )
        assert len(answer.opportunities) == 1
        assert answer.opportunities[0].description == "Growing demand."

    @pytest.mark.asyncio
    async def test_synthesize_risks_from_constraint_facts(self, monkeypatch):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Strict limits apply.",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        fact = BusinessFact(
            fact_type=FactType.REGULATORY_REQUIREMENT,
            dimension="regulatory_sps_tbt",
            query_id="q-1",
            statement="Strict limits apply.",
            evidence=evidence,
            provenance={"risk_signal": "compliance_gap", "severity": "high"},
            source_ids=["src-1"],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.BusinessFactNormalizer.normalize_knowledge_result",
            lambda knowledge_result: [fact],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.FactFusion.deduplicate",
            lambda facts: [fact],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.FactFusion.detect_conflicts",
            lambda facts: [],
        )

        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            knowledge_result={"results": []},
        )
        assert len(answer.risks) == 1
        assert answer.risks[0].severity is None

    @pytest.mark.asyncio
    async def test_synthesize_comparison_from_datum_facts(self, monkeypatch):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Tariff 5%",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        facts = [
            BusinessFact(
                fact_type=FactType.COMPARISON_DATUM,
                dimension="market_access",
                query_id="q-1",
                statement="Jordan tariff",
                value=5,
                evidence=evidence,
                provenance={"candidate": "Jordan", "criterion": "tariff"},
                source_ids=["src-1"],
            ),
            BusinessFact(
                fact_type=FactType.COMPARISON_DATUM,
                dimension="market_access",
                query_id="q-2",
                statement="UAE tariff",
                value=0,
                evidence=evidence,
                provenance={"candidate": "UAE", "criterion": "tariff"},
                source_ids=["src-1"],
            ),
        ]
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.BusinessFactNormalizer.normalize_knowledge_result",
            lambda knowledge_result: [],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.FactFusion.deduplicate",
            lambda x: x,
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.FactFusion.detect_conflicts",
            lambda facts: [],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.EntityDeriver.derive",
            lambda facts: [],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.OpportunityDeriver.derive",
            lambda facts: [],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.RiskDeriver.derive",
            lambda facts: [],
        )

        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        research = _make_research_result()
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.BusinessFactNormalizer.normalize_findings",
            lambda self, findings, dimension, query_id: facts if query_id == "q-0" else [],
        )
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.comparisons is not None
        assert answer.comparisons.options == ["Jordan", "UAE"]

    @pytest.mark.asyncio
    async def test_synthesize_rankings_none_without_scoring_basis(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(mission=mission)
        assert answer.rankings is None

    @pytest.mark.asyncio
    async def test_synthesize_no_business_recommendation_without_rule(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(mission=mission)
        assert answer.recommendations == []

    @pytest.mark.asyncio
    async def test_synthesize_next_evidence_requirement_when_no_research(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(mission=mission)
        assert answer.recommendations == []

    @pytest.mark.asyncio
    async def test_synthesize_executive_summary_substantive(self, monkeypatch):
        evidence = [
            EvidenceReference(
                source_id="src-1",
                source_url="https://example.com",
                content_excerpt="Company A is a supplier.",
                retrieval_timestamp="2024-01-01T00:00:00",
            )
        ]
        fact = BusinessFact(
            fact_type=FactType.DOCUMENTED_ENTITY,
            dimension="company_knowledge",
            query_id="q-1",
            statement="Company A is a supplier.",
            evidence=evidence,
            provenance={"entity_name": "Company A", "entity_type": "supplier"},
            source_ids=["src-1"],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.BusinessFactNormalizer.normalize_knowledge_result",
            lambda knowledge_result: [fact],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.FactFusion.deduplicate",
            lambda facts: [fact],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.FactFusion.detect_conflicts",
            lambda facts: [],
        )
        monkeypatch.setattr(
            "app.agent.business_intelligence.synthesizer.EntityDeriver.derive",
            lambda facts: [BusinessEntity(name="Company A", entity_type="supplier")],
        )

        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            goal={"objective": "Export vegetables"},
            knowledge_result={"results": []},
        )
        assert "Goal: Export vegetables." in answer.executive_summary
        assert "documented entity/entities" in answer.executive_summary

    @pytest.mark.asyncio
    async def test_synthesize_sparse_evidence_remains_qualified(self):
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(mission=mission)
        assert answer.executive_summary != ""
        assert "No substantive business sections could be derived from the current evidence." in answer.executive_summary or "insufficient evidence" in answer.executive_summary.lower()
        assert len(answer.entities) == 0
        assert answer.rankings is None
        assert answer.comparisons is None

    @pytest.mark.asyncio
    async def test_research_metadata_preserved_in_fact_provenance(self):
        finding = FindingItem(
            topic="entities",
            content="Company A is a supplier.",
            evidence=[_make_evidence_item(source_id="src-1", content_excerpt="Company A is a supplier.")],
            confidence=0.9,
            metadata={"entity_name": "Company A", "entity_type": "supplier"},
        )
        research = _make_research_result(findings=[finding])
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.provenance.get("fact_count", 0) == 1
        assert len(answer.entities) == 1

    @pytest.mark.asyncio
    async def test_research_finding_without_metadata_does_not_fabricate_entity(self):
        finding = FindingItem(
            topic="entities",
            content="Some finding.",
            evidence=[_make_evidence_item(source_id="src-1", content_excerpt="Some finding.")],
            confidence=0.9,
            metadata={},
        )
        research = _make_research_result(findings=[finding])
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert len(answer.entities) == 0

    @pytest.mark.asyncio
    async def test_knowledge_result_metadata_flows_into_entity_provenance(self):
        knowledge_result = {
            "results": [
                {
                    "id": "k1",
                    "content": "Company A is a supplier.",
                    "source_id": "company-knowledge",
                    "confidence": 0.9,
                    "metadata": {"entity_name": "Company A", "entity_type": "supplier"},
                }
            ],
            "confidence": 0.9,
            "sources": ["company-knowledge"],
        }
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            knowledge_result=knowledge_result,
        )
        assert len(answer.entities) == 1
        assert answer.entities[0].name == "Company A"
        assert answer.entities[0].entity_type == "company"

    @pytest.mark.asyncio
    async def test_research_dimension_metadata_produces_correct_fact_type(self):
        finding = FindingItem(
            topic="trade",
            content="Trade volume increased.",
            evidence=[_make_evidence_item(source_id="src-1", content_excerpt="Trade volume increased.")],
            confidence=0.8,
            metadata={"dimension": "trade_intelligence", "opportunity_basis": "demand_growth"},
        )
        research = _make_research_result(findings=[finding])
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.provenance.get("fact_count", 0) == 1
        assert len(answer.opportunities) == 1
        assert answer.opportunities[0].description == "Trade volume increased."

    @pytest.mark.asyncio
    async def test_research_fallback_general_dimension_when_missing(self):
        finding = FindingItem(
            topic="general",
            content="Some finding.",
            evidence=[_make_evidence_item(source_id="src-1", content_excerpt="Some finding.")],
            confidence=0.8,
            metadata={},
        )
        research = _make_research_result(findings=[finding])
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.provenance.get("fact_count", 0) == 1
        assert len(answer.entities) == 0
        assert len(answer.opportunities) == 0

    @pytest.mark.asyncio
    async def test_research_regulatory_dimension_produces_risk(self):
        finding = FindingItem(
            topic="regulatory",
            content="Strict limits apply.",
            evidence=[_make_evidence_item(source_id="src-1", content_excerpt="Strict limits apply.")],
            confidence=0.9,
            metadata={"dimension": "regulatory_sps_tbt", "risk_signal": "compliance_gap", "severity": "high"},
        )
        research = _make_research_result(findings=[finding])
        synthesizer = BusinessIntelligenceSynthesizer()
        mission = type("Mission", (), {"result": {}, "goal": None})()
        answer = await synthesizer.synthesize(
            mission=mission,
            research_result=research.model_dump(mode="json"),
        )
        assert answer.provenance.get("fact_count", 0) == 1
        assert len(answer.risks) == 1
        assert answer.risks[0].severity is None
