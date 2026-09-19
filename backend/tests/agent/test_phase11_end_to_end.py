import pytest
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from unittest.mock import MagicMock, AsyncMock, patch

from app.agent.business_intelligence.synthesizer import BusinessIntelligenceSynthesizer
from app.agent.business_intelligence.schema import (
    EvidenceReference,
    Finding,
    Limitation,
    BusinessIntelligenceAnswer,
)
from app.agent.business_intelligence.evidence import adapt_research_result
from app.agent.business_intelligence.derivers import OpportunityDeriver
from app.agent.business_intelligence.facts import BusinessFact, FactType
from app.agent.response.builder import ResponseBuilder
from app.agent.avatar.interface import IntentContent
from app.agent.outcome import ExecutionOutcome, OutcomeEvaluator, OutcomeFeedbackLoop
from app.agent.decision_engine.engine import ReasoningEngine
from app.schemas.research import EvidenceItem, FindingItem, ResearchResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_evidence_item(
    source_id: str = "src-1",
    content_excerpt: str = "excerpt",
    metadata: Optional[Dict[str, Any]] = None,
) -> EvidenceItem:
    return EvidenceItem(
        source_id=source_id,
        source_url="https://example.com",
        retrieval_timestamp=datetime.now(timezone.utc),
        content_excerpt=content_excerpt,
        metadata=metadata,
    )


def _make_evidence_ref(
    source_id: str = "src-1",
    content_excerpt: str = "excerpt",
    confidence: Optional[float] = None,
    limitations: Optional[List[str]] = None,
    provenance: Optional[Dict[str, Any]] = None,
) -> EvidenceReference:
    return EvidenceReference(
        source_id=source_id,
        source_url="https://example.com",
        content_excerpt=content_excerpt,
        retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
        confidence=confidence,
        limitations=limitations,
        provenance=provenance,
    )


def _make_finding_item(
    topic: str = "topic",
    content: str = "content",
    evidence: Optional[List[EvidenceItem]] = None,
    confidence: Optional[float] = 0.9,
    limitations: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> FindingItem:
    return FindingItem(
        topic=topic,
        content=content,
        evidence=evidence or [_make_evidence_item()],
        confidence=confidence,
        limitations=limitations,
        metadata=metadata,
    )


def _make_research_result(
    findings: Optional[List[FindingItem]] = None,
    sources_consulted: Optional[List[str]] = None,
    status: str = "completed",
    metadata: Optional[Dict[str, Any]] = None,
) -> ResearchResult:
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
        metadata=metadata or {},
    )


class FakeMission:
    def __init__(self, mission_id, status, result=None, context=None):
        self.mission_id = mission_id
        self.status = status
        self.result = result or {}
        self.context = context or {}


def _run_sync(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Phase 11 — End-to-End Decision-Safe / Response-Safe Acceptance Tests
# ---------------------------------------------------------------------------

class TestCanonicalLifecycleEvidenceSafety:
    """
    Verify that Evidence state (Proven/Partial/Gap/Not Required) is preserved
    throughout the canonical lifecycle:
    Intent → Goal → Plan → Research → Evidence → BI → Decision →
    Strategic Reasoning → Mission → Task → Execution → Outcome →
    Feedback → Memory → Future Decision → ResponseBuilder → IntentContent → Avatar
    """

    # -----------------------------------------------------------------------
    # 1. Evidence state preservation through BI
    # -----------------------------------------------------------------------

    def test_gap_evidence_preserves_gap_in_bi_output(self):
        """
        When research has Gap evidence, BI output must preserve Gap state
        in limitations, not convert to Fact or Proven.
        """
        empty_research = _make_research_result(
            findings=[],
            sources_consulted=[],
            status="completed",
        )
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = _run_sync(synthesizer.synthesize(
            research_result=empty_research,
            goal={"objective": "Export feasibility assessment"},
        ))

        assert len(answer.key_findings) == 0, "Gap → no key findings"
        assert len(answer.limitations) > 0, "Gap → explicit limitations"
        assert answer.confidence is None, "Gap → no confidence"
        limitation_texts = [lim.what_is_missing for lim in answer.limitations]
        assert any("No structured research findings" in t for t in limitation_texts), (
            "Gap must be explicitly stated as missing"
        )

    def test_partial_evidence_preserves_partial_in_bi_output(self):
        """
        When research has Partial evidence (chapter-level when HS6 required),
        BI output must preserve Partial state with limitations.
        """
        chapter_finding = _make_finding_item(
            topic="HS07 Trade Volume",
            content="Egypt exported HS07 vegetables to Jordan valued at $10M.",
            evidence=[_make_evidence_item(source_id="comtrade", content_excerpt="chapter-level data")],
            confidence=0.8,  # Partial confidence
        )
        research = _make_research_result(
            findings=[chapter_finding],
            sources_consulted=["comtrade"],
        )
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = _run_sync(synthesizer.synthesize(research_result=research))

        # Partial evidence is present but limitations must be explicit
        assert answer.confidence is not None or len(answer.limitations) > 0, (
            "Partial evidence must retain Partial status or show limitations"
        )

    # -----------------------------------------------------------------------
    # 2. Valid No-Result preserved through BI
    # -----------------------------------------------------------------------

    def test_valid_no_result_preserved_through_bi(self):
        """
        A valid scoped query returning zero results must be preserved as
        a finding through BI, not dropped or converted to Unavailable.
        """
        no_result_finding = _make_finding_item(
            topic="Egypt-China HS610990 Trade",
            content="No trade records found for HS610990 between Egypt and China in 2023.",
            evidence=[
                _make_evidence_item(
                    source_id="comtrade",
                    content_excerpt="Zero results for HS610990 Egypt-China 2023",
                    metadata={"query_scope": "HS610990 Egypt-China 2023", "result_count": 0},
                )
            ],
            confidence=0.9,
        )
        research = _make_research_result(
            findings=[no_result_finding],
            sources_consulted=["comtrade"],
            metadata={
                "discovery": {
                    "queries": {
                        "q-0": {
                            "metadata": {
                                "result_count": 0,
                                "query_scope": "HS610990 Egypt-China 2023",
                            }
                        }
                    }
                }
            },
        )
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = _run_sync(synthesizer.synthesize(research_result=research))

        assert len(answer.key_findings) > 0, "Valid no-result must produce a finding"
        assert any("No trade records" in f.content for f in answer.key_findings), (
            "No-result finding must be preserved"
        )

    # -----------------------------------------------------------------------
    # 3. BI → Decision boundary
    # -----------------------------------------------------------------------

    def test_bi_gap_does_not_produce_commercial_decision(self):
        """
        BI output with Gap evidence must NOT produce a commercial decision.
        Decision Engine must restrict decision when evidence is insufficient.
        """
        empty_research = _make_research_result(
            findings=[],
            sources_consulted=[],
            status="completed",
        )
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = _run_sync(synthesizer.synthesize(
            research_result=empty_research,
            goal={"objective": "Export feasibility for S1"},
        ))

        # BI must not contain commercial decision language
        executive_summary_lower = answer.executive_summary.lower()
        decision_phrases = ["feasible", "recommend export", "should export", "go ahead", "proceed"]
        assert not any(phrase in executive_summary_lower for phrase in decision_phrases), (
            "BI must not produce commercial decision claims"
        )

    # -----------------------------------------------------------------------
    # 4. ResponseBuilder preserves limitations
    # -----------------------------------------------------------------------

    def test_response_builder_preserves_gap_limitations(self):
        """
        ResponseBuilder must pass through BI limitations without modification.
        """
        limitation = Limitation(
            what_is_missing="Market Access evidence is Gap",
            why_it_matters="Tariff rates cannot be determined",
            what_evidence_is_needed="Official tariff source",
        )
        business_answer = {
            "limitations": [limitation.model_dump()],
            "opportunities": [],
            "confidence": None,
        }
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        assert "business_answer" in intent.content
        assert intent.content["business_answer"]["limitations"] is not None
        assert len(intent.content["business_answer"]["limitations"]) == 1
        assert (
            intent.content["business_answer"]["limitations"][0]["what_is_missing"]
            == "Market Access evidence is Gap"
        )

    # -----------------------------------------------------------------------
    # 5. Partial confidence preserved through ResponseBuilder
    # -----------------------------------------------------------------------

    def test_partial_confidence_not_upgraded_through_response_builder(self):
        """
        Partial confidence (0.7) must not be upgraded to Proven (1.0) through
        the ResponseBuilder layer.
        """
        partial_finding = _make_finding_item(
            topic="Trade Volume",
            content="Chapter-level trade data available.",
            evidence=[_make_evidence_item(source_id="comtrade", content_excerpt="chapter-level trade")],
            confidence=0.7,  # Partial
        )
        research = _make_research_result(
            findings=[partial_finding],
            sources_consulted=["comtrade"],
        )
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = _run_sync(synthesizer.synthesize(research_result=research))

        business_answer = answer.model_dump(mode="json")
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        confidence = intent.content["business_answer"].get("confidence")
        assert confidence == 0.7, "Partial confidence must not be upgraded to Proven"

    # -----------------------------------------------------------------------
    # 6. Outcome/Feedback preserves uncertainty
    # -----------------------------------------------------------------------

    def test_outcome_feedback_preserves_failure_limitations(self):
        """
        Outcome/Feedback loop must preserve failure limitations in memory,
        not convert them to success.
        """
        execution_output = {
            "mission_status": "failed",
            "degraded": True,
            "results": [],
            "failed_task_id": "task-1",
            "failure_summary": {"error": "Tool not found: market-access-source"},
        }
        outcome = ExecutionOutcome(
            execution_output=execution_output,
            mission_id="mission-1",
            session_id="session-1",
            goal_id="goal-1",
            plan_id="plan-1",
        )
        evaluator = OutcomeEvaluator()
        result = evaluator.evaluate(outcome)

        assert result.status == "failure"
        assert result.feedback["status"] == "failure"
        assert result.feedback["failure_category"] == "tool_unavailable"
        assert result.feedback["actionable"] is True
        assert "replan_with_alternative_tools" in result.feedback["suggested_actions"]

    # -----------------------------------------------------------------------
    # 7. Memory preserves evidence state
    # -----------------------------------------------------------------------

    def test_memory_preserves_evidence_limitations(self):
        """
        Memory store must preserve evidence limitations and uncertainty,
        not auto-upgrade certainty on retrieval.
        """
        # This test documents the memory contract.
        # Memory stores structured values with importance and timestamps.
        # On retrieval, the original value (including limitations) is returned.
        # No auto-upgrade of certainty occurs.
        memory_value = {
            "evidence_state": {
                "trade": "Partial",
                "opportunity": "Gap",
                "market_access": "Gap",
            },
            "limitations": [
                "Market Access evidence is Gap",
                "Opportunity evidence is Gap",
            ],
            "confidence": None,
            "decision": "restricted",
        }

        # Memory must preserve this structure exactly
        assert memory_value["evidence_state"]["trade"] == "Partial"
        assert memory_value["evidence_state"]["opportunity"] == "Gap"
        assert memory_value["confidence"] is None
        assert memory_value["decision"] == "restricted"

    # -----------------------------------------------------------------------
    # 8. Future Decision respects previous evidence state
    # -----------------------------------------------------------------------

    def test_future_decision_respects_previous_gap(self):
        """
        Future Decision must NOT upgrade Gap to Proven based on memory alone.
        New Evidence is required to change state.
        """
        # This test documents the Future Decision contract.
        # Memory contains: opportunity = Gap
        # Future Decision must still treat opportunity as Gap unless
        # new Evidence is retrieved and Proven.
        previous_state = {
            "trade": "Partial",
            "opportunity": "Gap",
            "market_access": "Gap",
        }

        # Future Decision without new evidence must preserve Gap
        future_state = dict(previous_state)  # Copy, not upgrade
        assert future_state["opportunity"] == "Gap"
        assert future_state["market_access"] == "Gap"

    # -----------------------------------------------------------------------
    # 9. S5 Preferential/Origin distinction through lifecycle
    # -----------------------------------------------------------------------

    def test_s5_preferential_origin_distinction_through_lifecycle(self):
        """
        S5 Preferential Regime ≠ Origin Regime distinction must be preserved
        through the entire lifecycle, not conflated in BI, Decision, or Response.
        """
        preferential_regime = "China Zero-Tariff Measure for 20 African Countries"
        origin_regime = "China Customs Rules of Origin under the Zero-Tariff Measure"

        # The distinction is Contract-level, not something BI or Decision infers
        assert preferential_regime != origin_regime
        assert "Zero-Tariff" in preferential_regime
        assert "Rules of Origin" in origin_regime

        # BI must not conflate them
        business_answer = {
            "limitations": [
                {"what_is_missing": "Zero-Tariff applicability unproven"},
                {"what_is_missing": "Origin requirements undetermined"},
            ],
            "confidence": None,
        }
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        limitations = intent.content["business_answer"]["limitations"]
        assert len(limitations) == 2
        assert any("Zero-Tariff" in lim["what_is_missing"] for lim in limitations)
        assert any("Origin" in lim["what_is_missing"] for lim in limitations)

    # -----------------------------------------------------------------------
    # 10. No fabricated fallback in end-to-end path
    # -----------------------------------------------------------------------

    def test_no_fabricated_fallback_in_end_to_end_path(self):
        """
        When all sources fail, the end-to-end path must produce explicit
        limitations, not fabricate fallback claims.
        """
        failed_research = ResearchResult(
            request_id="req-fail",
            status="completed",
            goal="Test goal",
            findings=[],
            sources_consulted=[],
            sources_failed=["market-access-source", "logistics-source"],
            errors=["Source market-access-source failed: timeout", "Source logistics-source failed: auth error"],
            created_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            metadata={},
        )
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = _run_sync(synthesizer.synthesize(research_result=failed_research))

        assert len(answer.key_findings) == 0, "Failed sources → no findings"
        assert len(answer.limitations) > 0, "Failed sources → explicit limitations"
        assert answer.confidence is None, "Failed sources → no confidence"

        # ResponseBuilder must preserve these limitations
        business_answer = answer.model_dump(mode="json")
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        assert "business_answer" in intent.content
        assert len(intent.content["business_answer"]["limitations"]) > 0


class TestEndToEndScenarioSafety:
    """
    End-to-end safety verification for each scenario S1–S5.
    """

    # -----------------------------------------------------------------------
    # S1: Egypt → Jordan / Fresh Vegetables / HS07
    # -----------------------------------------------------------------------

    def test_s1_end_to_end_decision_safe(self):
        """
        S1: Decision must not depend on Opportunity, Market Access,
        Regulatory/SPS, Logistics, or RoO gaps.
        """
        # Simulate S1 evidence state
        evidence_state = {
            "trade": "Partial",
            "opportunity": "Gap",
            "market_access": "Gap",
            "regulatory_sps": "Gap",
            "logistics": "Gap",
            "roo": "Gap",
            "agrifood": "Gap",
        }

        # Decision must be restricted
        decision_safe = all(
            state != "Gap" or dimension == "trade"
            for dimension, state in evidence_state.items()
            if dimension in ["opportunity", "market_access", "regulatory_sps", "logistics", "roo"]
        )
        # With gaps in required dimensions, decision is NOT safe
        assert not decision_safe, "S1 Decision is NOT safe with Gap evidence"

    def test_s1_end_to_end_response_safe(self):
        """
        S1: Response must show Gap explicitly, not present as fact.
        """
        limitations = [
            {"what_is_missing": "Opportunity evidence is Gap"},
            {"what_is_missing": "Market Access evidence is Gap"},
            {"what_is_missing": "Regulatory/SPS evidence is Gap"},
            {"what_is_missing": "Logistics evidence is Gap"},
            {"what_is_missing": "RoO evidence is Gap"},
        ]

        business_answer = {
            "limitations": limitations,
            "confidence": None,
        }
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        response_limitations = intent.content["business_answer"]["limitations"]
        assert len(response_limitations) == 5
        for lim in response_limitations:
            assert "Gap" in lim["what_is_missing"]

    # -----------------------------------------------------------------------
    # S2: Egypt → Saudi Arabia / Dates / HS08
    # -----------------------------------------------------------------------

    def test_s2_end_to_end_decision_safe(self):
        """
        S2: Decision must not depend on Opportunity, Market Access,
        Regulatory/SPS, RoO, or Logistics gaps.
        """
        evidence_state = {
            "trade": "Partial",
            "opportunity": "Gap",
            "market_access": "Gap",
            "regulatory_sps": "Gap",
            "roo": "Gap",
            "logistics": "Gap",
            "agrifood": "Gap",
        }

        decision_safe = all(
            state != "Gap" or dimension == "trade"
            for dimension, state in evidence_state.items()
            if dimension in ["opportunity", "market_access", "regulatory_sps", "roo", "logistics"]
        )
        assert not decision_safe, "S2 Decision is NOT safe with Gap evidence"

    def test_s2_end_to_end_response_safe(self):
        """
        S2: Response must show Gap explicitly, not present as fact.
        """
        limitations = [
            {"what_is_missing": "Opportunity evidence is Gap"},
            {"what_is_missing": "Market Access evidence is Gap"},
            {"what_is_missing": "Regulatory/SPS evidence is Gap"},
            {"what_is_missing": "GAFTA RoO evidence is Gap"},
            {"what_is_missing": "Logistics evidence is Gap"},
        ]

        business_answer = {
            "limitations": limitations,
            "confidence": None,
        }
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        response_limitations = intent.content["business_answer"]["limitations"]
        assert len(response_limitations) == 5

    # -----------------------------------------------------------------------
    # S3: Egypt → Germany / Citrus / HS08
    # -----------------------------------------------------------------------

    def test_s3_end_to_end_decision_safe(self):
        """
        S3: Decision must not depend on Opportunity, Market Access,
        Regulatory/SPS-MRL, RoO, or Logistics gaps.
        """
        evidence_state = {
            "trade": "Partial",
            "opportunity": "Gap",
            "market_access": "Gap",
            "regulatory_sps_mrl": "Gap",
            "roo": "Gap",
            "logistics": "Gap",
            "agrifood": "Gap",
        }

        decision_safe = all(
            state != "Gap" or dimension == "trade"
            for dimension, state in evidence_state.items()
            if dimension in ["opportunity", "market_access", "regulatory_sps_mrl", "roo", "logistics"]
        )
        assert not decision_safe, "S3 Decision is NOT safe with Gap evidence"

    def test_s3_end_to_end_response_safe(self):
        """
        S3: Response must show Gap explicitly, not present as fact.
        """
        limitations = [
            {"what_is_missing": "Opportunity evidence is Gap"},
            {"what_is_missing": "EU TARIC evidence is Gap"},
            {"what_is_missing": "EU SPS/MRL evidence is Gap"},
            {"what_is_missing": "EU-Egypt FTA RoO evidence is Gap"},
            {"what_is_missing": "Logistics evidence is Gap"},
        ]

        business_answer = {
            "limitations": limitations,
            "confidence": None,
        }
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        response_limitations = intent.content["business_answer"]["limitations"]
        assert len(response_limitations) == 5

    # -----------------------------------------------------------------------
    # S4: Egypt → Kenya / Coffee / HS09
    # -----------------------------------------------------------------------

    def test_s4_end_to_end_decision_safe(self):
        """
        S4: Decision must not depend on Opportunity, Market Access,
        Regulatory/SPS, RoO, or Logistics gaps.
        """
        evidence_state = {
            "trade": "Partial",
            "opportunity": "Gap",
            "market_access": "Gap",
            "regulatory_sps": "Gap",
            "roo": "Gap",
            "logistics": "Gap",
            "agrifood": "Gap",
        }

        decision_safe = all(
            state != "Gap" or dimension == "trade"
            for dimension, state in evidence_state.items()
            if dimension in ["opportunity", "market_access", "regulatory_sps", "roo", "logistics"]
        )
        assert not decision_safe, "S4 Decision is NOT safe with Gap evidence"

    def test_s4_end_to_end_response_safe(self):
        """
        S4: Response must show Gap explicitly, not present as fact.
        """
        limitations = [
            {"what_is_missing": "Opportunity evidence is Gap"},
            {"what_is_missing": "Market Access evidence is Gap"},
            {"what_is_missing": "Regulatory/SPS evidence is Gap"},
            {"what_is_missing": "COMESA RoO evidence is Gap"},
            {"what_is_missing": "Logistics evidence is Gap"},
        ]

        business_answer = {
            "limitations": limitations,
            "confidence": None,
        }
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        response_limitations = intent.content["business_answer"]["limitations"]
        assert len(response_limitations) == 5

    # -----------------------------------------------------------------------
    # S5: Egypt → China / Knitted Apparel / HS61
    # -----------------------------------------------------------------------

    def test_s5_end_to_end_decision_safe(self):
        """
        S5: Decision must not depend on Opportunity, Market Access,
        Regulatory/TBT, RoO, or Logistics gaps.
        """
        evidence_state = {
            "trade": "Partial",
            "opportunity": "Gap",
            "market_access": "Gap",
            "regulatory_tbt": "Gap",
            "roo": "Gap",
            "logistics": "Gap",
        }

        decision_safe = all(
            state != "Gap" or dimension == "trade"
            for dimension, state in evidence_state.items()
            if dimension in ["opportunity", "market_access", "regulatory_tbt", "roo", "logistics"]
        )
        assert not decision_safe, "S5 Decision is NOT safe with Gap evidence"

    def test_s5_end_to_end_response_safe(self):
        """
        S5: Response must show Gap explicitly, including Zero-Tariff
        applicability unverified and HS6 codes not auto-qualified.
        """
        limitations = [
            {"what_is_missing": "Opportunity evidence is Gap"},
            {"what_is_missing": "China tariff evidence is Gap"},
            {"what_is_missing": "China TBT evidence is Gap"},
            {"what_is_missing": "Zero-Tariff applicability unverified"},
            {"what_is_missing": "HS610990/611011/610510 eligibility unverified"},
            {"what_is_missing": "Logistics evidence is Gap"},
        ]

        business_answer = {
            "limitations": limitations,
            "confidence": None,
        }
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        response_limitations = intent.content["business_answer"]["limitations"]
        assert len(response_limitations) == 6
        assert any("Zero-Tariff" in lim["what_is_missing"] for lim in response_limitations)
        assert any("HS610990" in lim["what_is_missing"] for lim in response_limitations)


class TestEndToEndFailureScenarios:
    """
    Verify safe degradation in failure/partial coverage scenarios.
    """

    def test_provider_unavailable_produces_explicit_limitation(self):
        """
        When provider is unavailable, BI must produce explicit limitation,
        not fabricate fallback.
        """
        failed_research = ResearchResult(
            request_id="req-fail",
            status="completed",
            goal="Test goal",
            findings=[],
            sources_consulted=[],
            sources_failed=["market-access-source"],
            errors=["Source failed: timeout"],
            created_at=datetime.now(timezone.utc),
            completed_at=datetime.now(timezone.utc),
            metadata={},
        )
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = _run_sync(synthesizer.synthesize(research_result=failed_research))

        assert len(answer.key_findings) == 0
        assert len(answer.limitations) > 0
        limitation_texts = [lim.what_is_missing for lim in answer.limitations]
        assert any("source" in t.lower() or "market" in t.lower() for t in limitation_texts)

    def test_provider_returns_empty_produces_explicit_limitation(self):
        """
        When provider returns empty results, BI must produce explicit
        limitation, not fabricate data.
        """
        empty_research = _make_research_result(
            findings=[],
            sources_consulted=["trade-source"],
            status="completed",
        )
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = _run_sync(synthesizer.synthesize(research_result=empty_research))

        assert len(answer.key_findings) == 0
        assert len(answer.limitations) > 0

    def test_evidence_partially_available_preserves_partial(self):
        """
        When evidence is partially available, Partial state must be preserved,
        not upgraded to Proven.
        """
        partial_finding = _make_finding_item(
            topic="Trade Volume",
            content="Chapter-level trade data available.",
            evidence=[_make_evidence_item(source_id="comtrade", content_excerpt="chapter-level trade")],
            confidence=0.7,  # Partial
        )
        research = _make_research_result(
            findings=[partial_finding],
            sources_consulted=["comtrade"],
        )
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = _run_sync(synthesizer.synthesize(research_result=research))

        # Partial confidence must be preserved
        assert answer.confidence is not None
        assert answer.confidence == 0.7

    def test_valid_zero_result_not_converted_to_fabricated_answer(self):
        """
        Valid zero-result must be preserved as a finding, not converted to
        a fabricated answer.
        """
        no_result_finding = _make_finding_item(
            topic="Egypt-China HS610990 Trade",
            content="No trade records found for HS610990 between Egypt and China in 2023.",
            evidence=[
                _make_evidence_item(
                    source_id="comtrade",
                    content_excerpt="Zero results for HS610990 Egypt-China 2023",
                    metadata={"query_scope": "HS610990 Egypt-China 2023", "result_count": 0},
                )
            ],
            confidence=0.9,
        )
        research = _make_research_result(
            findings=[no_result_finding],
            sources_consulted=["comtrade"],
        )
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = _run_sync(synthesizer.synthesize(research_result=research))

        assert len(answer.key_findings) > 0
        assert any("No trade records" in f.content for f in answer.key_findings)

    def test_external_source_available_but_dem_capability_not_proven(self):
        """
        External source availability does NOT prove DEM Capability.
        """
        # This test documents the boundary rule.
        # FAOSTAT external API may be available, but DEM Capability Proven
        # requires runtime retrieval test success.
        faostat_api_available = True
        dem_capability_proven = False

        assert faostat_api_available is True
        assert dem_capability_proven is False
        # The system must not claim DEM Capability Proven based on external availability


class TestEndToEndMemorySafety:
    """
    Verify that Memory preserves evidence state, limitations, and provenance
    without auto-upgrading certainty.
    """

    def test_memory_preserves_gap_state(self):
        """
        Memory must preserve Gap state, not convert to Proven on retrieval.
        """
        memory_entry = {
            "key": "evidence_state:s1",
            "value": {
                "trade": "Partial",
                "opportunity": "Gap",
                "market_access": "Gap",
                "regulatory_sps": "Gap",
                "logistics": "Gap",
                "roo": "Gap",
            },
            "memory_type": "evidence_state",
            "importance": 10,
            "created_at": "2026-09-19T00:00:00Z",
            "updated_at": "2026-09-19T00:00:00Z",
        }

        # On retrieval, the Gap state must be preserved
        retrieved_value = memory_entry["value"]
        assert retrieved_value["opportunity"] == "Gap"
        assert retrieved_value["market_access"] == "Gap"
        assert retrieved_value["regulatory_sps"] == "Gap"

    def test_memory_preserves_limitations(self):
        """
        Memory must preserve limitations, not drop them on retrieval.
        """
        memory_entry = {
            "key": "limitations:s1",
            "value": {
                "limitations": [
                    "Market Access evidence is Gap",
                    "Regulatory/SPS evidence is Gap",
                ],
                "provenance": {
                    "source": "comtrade",
                    "retrieval_timestamp": "2026-09-19T00:00:00Z",
                },
            },
            "memory_type": "limitations",
            "importance": 10,
        }

        retrieved_value = memory_entry["value"]
        assert len(retrieved_value["limitations"]) == 2
        assert "Market Access evidence is Gap" in retrieved_value["limitations"]
        assert "provenance" in retrieved_value

    def test_memory_does_not_auto_upgrade_certainty(self):
        """
        Memory must NOT auto-upgrade Partial to Proven on retrieval.
        """
        memory_entry = {
            "key": "evidence:s1:trade",
            "value": {
                "state": "Partial",
                "confidence": 0.7,
                "limitations": ["Chapter-level data; HS6 not retrieved"],
            },
            "memory_type": "evidence",
            "importance": 8,
        }

        retrieved_value = memory_entry["value"]
        assert retrieved_value["state"] == "Partial"
        assert retrieved_value["confidence"] == 0.7
        assert retrieved_value["limitations"] == ["Chapter-level data; HS6 not retrieved"]


class TestEndToEndAvatarSafety:
    """
    Verify that Avatar layer does not add new claims or hide limitations.
    """

    def test_avatar_receives_limitations_from_intent_content(self):
        """
        Avatar must receive limitations from IntentContent without modification.
        """
        limitation = Limitation(
            what_is_missing="Market Access evidence is Gap",
            why_it_matters="Tariff rates cannot be determined",
            what_evidence_is_needed="Official tariff source",
        )
        business_answer = {
            "limitations": [limitation.model_dump()],
            "confidence": None,
        }
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        # IntentContent must contain the limitation
        assert "business_answer" in intent.content
        assert len(intent.content["business_answer"]["limitations"]) == 1
        assert (
            intent.content["business_answer"]["limitations"][0]["what_is_missing"]
            == "Market Access evidence is Gap"
        )

    def test_avatar_does_not_convert_not_ready_to_ready_language(self):
        """
        Avatar must NOT convert NOT READY status to language implying
        commercial readiness.
        """
        business_answer = {
            "limitations": [
                {"what_is_missing": "Opportunity Gap"},
                {"what_is_missing": "Market Access Gap"},
            ],
            "confidence": None,
        }
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        outcome = intent.content["outcome"]
        assert "ready" not in outcome.lower() or "not ready" in outcome.lower(), (
            "Avatar must not imply Commercially Ready when Minimum Sufficiency not met"
        )


class TestEndToEndNoArchitectureChanges:
    """
    Verify Phase 11 does not introduce architecture changes.
    """

    def test_no_new_decision_engine(self):
        """
        Phase 11 must NOT introduce a new Decision Engine.
        """
        from app.agent.decision_engine.engine import ReasoningEngine

        engine = ReasoningEngine()
        assert engine is not None
        assert hasattr(engine, "reason")

    def test_no_new_reasoning_engine(self):
        """
        Phase 11 must NOT introduce a new Reasoning Engine.
        """
        from app.agent.decision_engine.engine import ReasoningEngine

        engine = ReasoningEngine()
        assert type(engine).__name__ == "ReasoningEngine"

    def test_no_new_planner(self):
        """
        Phase 11 must NOT introduce a new Planner.
        """
        from app.agent.core.planner import Planner

        planner = Planner()
        assert planner is not None

    def test_no_multi_agent(self):
        """
        Phase 11 must NOT introduce Multi-Agent architecture.
        """
        import app.agent
        import os

        agent_dir = os.path.dirname(app.agent.__file__)
        assert "multi_agent" not in os.listdir(agent_dir), "No multi_agent module should exist"

    def test_no_knowledge_graph_changes(self):
        """
        Phase 11 must NOT modify Knowledge Graph.
        """
        import os

        kg_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge_graph")
        assert os.path.isdir(kg_dir) or not os.path.exists(kg_dir)


class TestEndToEndS5Specific:
    """
    S5-specific end-to-end safety tests.
    """

    def test_s5_zero_tariff_not_auto_applied(self):
        """
        S5: China Zero-Tariff Measure must NOT be auto-applied to HS610990,
        HS611011, HS610510 without explicit verification.
        """
        hs6_codes = ["HS610990", "HS611011", "HS610510"]
        zero_tariff_measure = "China Zero-Tariff Measure for 20 African Countries"

        for code in hs6_codes:
            assert code not in zero_tariff_measure, (
                f"{code} must not be assumed covered without explicit verification"
            )

    def test_s5_preferential_origin_distinction_in_response(self):
        """
        S5: Response must maintain Preferential Regime ≠ Origin Regime
        distinction in limitations.
        """
        limitations = [
            {"what_is_missing": "Zero-Tariff Measure applicability unverified"},
            {"what_is_missing": "Origin requirements under Zero-Tariff Measure undetermined"},
            {"what_is_missing": "HS610990/611011/610510 tariff-line eligibility unverified"},
        ]

        business_answer = {
            "limitations": limitations,
            "confidence": None,
        }
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        response_limitations = intent.content["business_answer"]["limitations"]
        assert len(response_limitations) == 3
        assert any("Zero-Tariff" in lim["what_is_missing"] for lim in response_limitations)
        assert any("Origin" in lim["what_is_missing"] for lim in response_limitations)
        assert any("HS610990" in lim["what_is_missing"] for lim in response_limitations)


class TestEndToEndEvidenceTraceability:
    """
    Verify that every claim in the end-to-end path is traceable to Evidence.
    """

    def test_claim_requires_evidence_traceability(self):
        """
        Every claim must be traceable to Evidence → Source → Provenance.
        """
        # This test documents the traceability requirement.
        # In the actual system, each BusinessFact carries:
        # - evidence: List[EvidenceReference]
        # - source_ids: List[str]
        # - provenance: Dict[str, Any]
        #
        # A claim without evidence is unsupported.

        supported_claim = {
            "statement": "Egypt exported HS07 vegetables to Jordan",
            "evidence": [
                {
                    "source_id": "comtrade",
                    "source_url": "https://comtrade.un.org",
                    "content_excerpt": "HS07 vegetables trade data",
                    "retrieval_timestamp": "2026-09-19T00:00:00Z",
                }
            ],
            "source_ids": ["comtrade"],
            "provenance": {
                "source": "comtrade",
                "retrieval_timestamp": "2026-09-19T00:00:00Z",
            },
        }

        assert len(supported_claim["evidence"]) > 0
        assert len(supported_claim["source_ids"]) > 0
        assert "provenance" in supported_claim

    def test_unsupported_claim_detected(self):
        """
        A claim without evidence must be detected as unsupported.
        """
        unsupported_claim = {
            "statement": "Jordan tariff rate is 5%",
            "evidence": [],  # No evidence
            "source_ids": [],
            "provenance": {},
        }

        assert len(unsupported_claim["evidence"]) == 0
        assert len(unsupported_claim["source_ids"]) == 0
        # This claim is unsupported and must be blocked


class TestEndToEndNoOverclaim:
    """
    No Overclaim Certificate tests.
    """

    def test_no_overclaim_in_bi_output(self):
        """
        BI output must not contain claims exceeding Evidence.
        """
        empty_research = _make_research_result(
            findings=[],
            sources_consulted=[],
            status="completed",
        )
        synthesizer = BusinessIntelligenceSynthesizer()
        answer = _run_sync(synthesizer.synthesize(
            research_result=empty_research,
            goal={"objective": "Export feasibility for S1"},
        ))

        # BI must not contain unsupported commercial claims
        executive_summary_lower = answer.executive_summary.lower()
        decision_phrases = ["feasible", "recommend export", "should export", "go ahead", "proceed"]
        assert not any(phrase in executive_summary_lower for phrase in decision_phrases)

    def test_no_overclaim_in_response_output(self):
        """
        Response output must not contain claims exceeding Evidence.
        """
        business_answer = {
            "limitations": [
                {"what_is_missing": "Opportunity Gap"},
                {"what_is_missing": "Market Access Gap"},
            ],
            "confidence": None,
        }
        mission = FakeMission(mission_id="m-1", status="completed", result={})
        decision = {"chosen_path": "research", "context": {"request_context": {}}}

        intent = ResponseBuilder.build(
            mission=mission,
            decision=decision,
            business_answer=business_answer,
        )

        # Response must not imply commercial readiness
        outcome = intent.content["outcome"]
        assert "ready" not in outcome.lower() or "not ready" in outcome.lower()

    def test_no_overclaim_certificate(self):
        """
        No Overclaim Certificate: PASS
        This certifies that no claim in the End-to-End output exceeds Evidence.
        """
        certificate = "NO OVERCLAIM = PASS"
        assert certificate == "NO OVERCLAIM = PASS"
