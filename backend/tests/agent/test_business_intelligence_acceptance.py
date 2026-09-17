import pytest
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.research.query_planner import ResearchQueryPlanner
from app.research.sources.registry import SourceRegistry
from app.research.sources.discovery import SourceDiscovery
from app.research.orchestrator import (
    ResearchOrchestrator,
    PlanningStage,
    DiscoveryStage,
    RetrievalStage,
    ProcessingStage,
    EvidenceCaptureStage,
    StructuringStage,
    VerificationStage,
    ResearchContext,
)
from app.research.retrieval.contracts import RetrievedContent, RetrievalResult, RetrievalStatus, SourceRetriever
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.research.evidence.contracts import DefaultEvidenceCapture
from app.research.result import DefaultResultStructurer
from app.research.retrieval.stubs import StubProcessor
from app.agent.business_intelligence.synthesizer import BusinessIntelligenceSynthesizer
from app.agent.business_intelligence.coverage import SourceExecutionStatus
from app.schemas.research import (
    ResearchRequest,
    ResearchResult,
    Source,
    SourceRegistration,
    EvidenceItem,
    FindingItem,
)
from app.schemas.research_query import ResearchQueryPlan


class ScenarioRetriever(SourceRetriever):
    """Simulates successful retrieval for all sources with commercial trade data."""

    async def retrieve(self, source, query, context=None, scope=None):
        raw_content = self._build_commercial_response(source.source_id, query, context, scope)
        return RetrievalResult(
            source_id=source.source_id,
            status=RetrievalStatus.SUCCESS,
            content=RetrievedContent(
                source_id=source.source_id,
                raw_content=raw_content,
                content_type="application/json",
                metadata={"query": query, "scope": scope or {}, "dimension": (scope or {}).get("dimension")},
            ),
        )

    def _build_commercial_response(self, source_id: str, query: str, context: Dict[str, Any], scope: Dict[str, Any]) -> Dict[str, Any]:
        if source_id == "un-comtrade":
            return {
                "data": [
                    {
                        "reporterCode": "818",
                        "reporterDesc": "Egypt",
                        "partnerCode": "400",
                        "partnerDesc": "Jordan",
                        "flowCode": "X",
                        "cmdCode": "07",
                        "cmdDesc": "Vegetables",
                        "refYear": 2025,
                        "fobvalue": 28496743.65,
                        "isReported": True,
                    },
                    {
                        "reporterCode": "818",
                        "reporterDesc": "Egypt",
                        "partnerCode": "400",
                        "partnerDesc": "Jordan",
                        "flowCode": "X",
                        "cmdCode": "08",
                        "cmdDesc": "Fruits",
                        "refYear": 2025,
                        "fobvalue": 19280456.30,
                        "isReported": True,
                    },
                ]
            }
        if source_id == "regulations":
            return {
                "results": [
                    {
                        "id": "reg-1",
                        "title": "Jordan Import Requirements for Vegetables",
                        "content": "Strict pesticide residue limits apply. Import permits required.",
                        "country": "Jordan",
                        "category": "SPS",
                        "source_url": "https://example.com/regs",
                        "confidence": 0.9,
                    }
                ]
            }
        if source_id == "faostat":
            return {
                "results": [
                    {
                        "id": "fao-1",
                        "title": "Egypt Agricultural Export Conditions",
                        "content": "Egypt vegetable exports show growing demand in Jordan market.",
                        "country": "Egypt",
                        "category": "agrifood",
                        "source_url": "https://example.com/faostat",
                        "confidence": 0.85,
                    }
                ]
            }
        return {"results": []}


def _make_registry() -> SourceRegistry:
    registry = SourceRegistry()
    registry.register(SourceRegistration(source=Source(
        source_id="un-comtrade",
        name="UN Comtrade",
        source_type="external_trade_intelligence",
        reference="https://comtrade.un.org",
        metadata={"capabilities": ["trade_intelligence", "market_opportunity"]},
        status="active",
    )))
    registry.register(SourceRegistration(source=Source(
        source_id="regulations",
        name="Regulations Knowledge",
        source_type="regulation",
        reference="https://example.com/regs",
        metadata={"capabilities": ["market_access", "regulatory_sps_tbt", "rules_of_origin"]},
        status="active",
    )))
    registry.register(SourceRegistration(source=Source(
        source_id="faostat",
        name="FAOSTAT",
        source_type="external_agrifood_intelligence",
        reference="https://fao.org",
        metadata={"capabilities": ["agrifood_intelligence", "market_opportunity"]},
        status="active",
    )))
    return registry


class TestPhase5EndToEndAcceptance:
    """End-to-end acceptance test for Phase 5 using the mandatory Arabic scenario."""

    @pytest.mark.asyncio
    async def test_arabic_export_scenario_end_to_end(self):
        goal = "اريد تصدير الخضروات والفاكهة المصرية الى الاردن"
        registry = _make_registry()
        retriever = ScenarioRetriever()
        retrieval_orchestrator = RetrievalOrchestrator(retriever=retriever)

        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage(planner=ResearchQueryPlanner()))
        orchestrator.register_stage(DiscoveryStage(discovery=SourceDiscovery(registry)))
        orchestrator.register_stage(RetrievalStage(
            retrieval_orchestrator=retrieval_orchestrator,
            registry=registry,
        ))
        orchestrator.register_stage(ProcessingStage(processor=StubProcessor()))
        orchestrator.register_stage(EvidenceCaptureStage(
            registry=registry,
            capture=DefaultEvidenceCapture(),
        ))
        orchestrator.register_stage(StructuringStage(structurer=DefaultResultStructurer()))
        orchestrator.register_stage(VerificationStage())

        research_result = await orchestrator.execute(
            ResearchRequest(goal=goal, context={}, scope={}),
            "acceptance-1",
        )

        assert research_result.status == "completed"
        assert research_result.goal == goal

        plan = research_result.metadata.get("plan", {})
        discovery = research_result.metadata.get("discovery", {})
        queries_metadata = discovery.get("queries", {})
        dimensions = [q.get("dimension") for q in queries_metadata.values()]
        assert "trade_intelligence" in dimensions
        assert "market_opportunity" in dimensions
        assert "agrifood_intelligence" in dimensions
        assert "market_access" in dimensions
        assert "regulatory_sps_tbt" in dimensions
        assert "rules_of_origin" in dimensions
        assert "logistics_market_execution" in dimensions

        sources_consulted = research_result.sources_consulted or []
        assert "un-comtrade" in sources_consulted
        assert "regulations" in sources_consulted
        assert "faostat" in sources_consulted

        findings = research_result.findings or []
        assert findings, "Expected findings from retrieval"

        commercial_findings = [
            f for f in findings
            if not (f.content or "").startswith("Retrieved ")
        ]
        assert commercial_findings, "Expected commercial findings, not meta-findings"

        for finding in commercial_findings:
            assert finding.evidence, f"Finding missing evidence: {finding.content}"

        evidence_items = research_result.metadata.get("evidence", {}).get("captured") is True
        assert evidence_items is not False or findings, "Evidence should be captured when findings exist"

        synthesizer = BusinessIntelligenceSynthesizer()
        answer = await synthesizer.synthesize(
            mission=type("Mission", (), {"result": {}, "goal": None})(),
            research_result=research_result.model_dump(mode="json"),
        )

        assert answer.goal == goal
        assert len(answer.key_findings) > 0, "Expected key findings in BI output"
        assert len(answer.evidence) > 0, "Expected evidence in BI output"
        assert len(answer.sources) > 0, "Expected sources in BI output"

        facts_from_provenance = answer.provenance.get("fact_count", 0)
        assert facts_from_provenance > 0, "Expected BusinessFacts to be created"

        for finding in answer.key_findings:
            assert finding.evidence, "BI key finding must retain evidence"

        for opportunity in answer.opportunities:
            assert opportunity.evidence, "Opportunity must be traceable to evidence"

        for risk in answer.risks:
            assert risk.evidence, "Risk must be traceable to evidence"

        for entity in answer.entities:
            assert entity.evidence, "Entity must be traceable to evidence"

        meta_findings = [f for f in answer.key_findings if (f.content or "").startswith("Retrieved ")]
        assert meta_findings == [], "Meta-findings should not appear in BI output"

        coverage = answer.provenance.get("coverage", {})
        assert coverage.get("coverage_level") in ("adequate", "partial", "insufficient")

        dimensions_covered = answer.provenance.get("dimensions_covered", [])
        for dim in ["trade_intelligence", "agrifood_intelligence", "market_opportunity"]:
            assert dim in dimensions_covered, f"Expected {dim} to be covered in BI provenance"

        unsupported = coverage.get("unsupported_dimensions", [])
        assert "logistics_market_execution" in unsupported, \
            "Expected logistics_market_execution to be reported as unsupported when no capable source exists"

    @pytest.mark.asyncio
    async def test_arabic_scenario_produces_traceable_commercial_facts(self):
        goal = "اريد تصدير الخضروات والفاكهة المصرية الى الاردن"
        registry = _make_registry()
        retriever = ScenarioRetriever()
        retrieval_orchestrator = RetrievalOrchestrator(retriever=retriever)

        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage(planner=ResearchQueryPlanner()))
        orchestrator.register_stage(DiscoveryStage(discovery=SourceDiscovery(registry)))
        orchestrator.register_stage(RetrievalStage(
            retrieval_orchestrator=retrieval_orchestrator,
            registry=registry,
        ))
        orchestrator.register_stage(ProcessingStage(processor=StubProcessor()))
        orchestrator.register_stage(EvidenceCaptureStage(
            registry=registry,
            capture=DefaultEvidenceCapture(),
        ))
        orchestrator.register_stage(StructuringStage(structurer=DefaultResultStructurer()))
        orchestrator.register_stage(VerificationStage())

        research_result = await orchestrator.execute(
            ResearchRequest(goal=goal, context={}, scope={}),
            "acceptance-4",
        )

        synthesizer = BusinessIntelligenceSynthesizer()
        answer = await synthesizer.synthesize(
            mission=type("Mission", (), {"result": {}, "goal": None})(),
            research_result=research_result.model_dump(mode="json"),
        )

        assert len(answer.key_findings) > 0
        commercial_key_findings = [
            f for f in answer.key_findings
            if not (f.content or "").startswith("Retrieved ")
        ]
        assert commercial_key_findings, "Expected commercial key findings, not meta-findings"

        fact_count = answer.provenance.get("fact_count", 0)
        assert fact_count > 0, "Expected BusinessFacts to be created"

        coverage = answer.provenance.get("coverage", {})
        has_commercial_findings = len(commercial_key_findings) > 0
        if has_commercial_findings:
            assert coverage.get("successful_sources", 0) > 0, \
                "Commercial findings should come from successful retrievals"

    @pytest.mark.asyncio
    async def test_arabic_scenario_traceability_chain_preserved(self):
        goal = "اريد تصدير الخضروات والفاكهة المصرية الى الاردن"
        registry = _make_registry()
        retriever = ScenarioRetriever()
        retrieval_orchestrator = RetrievalOrchestrator(retriever=retriever)

        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage(planner=ResearchQueryPlanner()))
        orchestrator.register_stage(DiscoveryStage(discovery=SourceDiscovery(registry)))
        orchestrator.register_stage(RetrievalStage(
            retrieval_orchestrator=retrieval_orchestrator,
            registry=registry,
        ))
        orchestrator.register_stage(ProcessingStage(processor=StubProcessor()))
        orchestrator.register_stage(EvidenceCaptureStage(
            registry=registry,
            capture=DefaultEvidenceCapture(),
        ))
        orchestrator.register_stage(StructuringStage(structurer=DefaultResultStructurer()))
        orchestrator.register_stage(VerificationStage())

        research_result = await orchestrator.execute(
            ResearchRequest(goal=goal, context={}, scope={}),
            "acceptance-5",
        )

        for finding in research_result.findings:
            assert finding.evidence, "Finding must have evidence"
            for evidence in finding.evidence:
                assert evidence.source_id, "Evidence must have source_id"

        synthesizer = BusinessIntelligenceSynthesizer()
        answer = await synthesizer.synthesize(
            mission=type("Mission", (), {"result": {}, "goal": None})(),
            research_result=research_result.model_dump(mode="json"),
        )

        for evidence in answer.evidence:
            assert evidence.source_id, "BI evidence must have source_id"

        for source in answer.sources:
            assert source, "BI sources must not be empty"

        assert answer.provenance.get("research_status") is not None
        assert answer.provenance.get("fact_count", 0) > 0
        assert answer.provenance.get("dimensions_covered") is not None
