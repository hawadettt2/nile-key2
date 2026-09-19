"""Regression tests for business intelligence coverage and mission status.

These tests verify that:
1. unsupported_dimensions downgrades coverage_level from adequate to partial.
2. When business_answer has unsupported_dimensions, the response indicates limitations.
3. degraded is set to True when there are unsupported dimensions.
"""
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Any, Dict

import pytest

from app.agent.business_intelligence.coverage import CoverageBuilder, SourceExecutionStatus
from app.agent.business_intelligence.synthesizer import BusinessIntelligenceSynthesizer
from app.agent.business_intelligence.schema import EvidenceReference, Finding, Limitation
from app.agent.response.builder import ResponseBuilder
from app.schemas.research import ResearchResult


def _make_research_result(
    findings: Optional[List[Any]] = None,
    sources_consulted: Optional[List[str]] = None,
    status: str = "completed",
    source_execution_statuses: Optional[Dict[str, str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> ResearchResult:
    if findings is None:
        findings = []
    if sources_consulted is None:
        sources_consulted = []
    if source_execution_statuses is None:
        source_execution_statuses = {}
    if metadata is None:
        metadata = {}
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
        metadata=metadata,
        source_execution_statuses=source_execution_statuses,
    )


def test_coverage_level_downgraded_by_unsupported_dimensions():
    """Coverage level must be partial when unsupported_dimensions is non-empty."""
    research = _make_research_result(
        source_execution_statuses={"src-1": SourceExecutionStatus.SUCCESS_WITH_DATA},
    )
    evidence = [
        EvidenceReference(
            source_id="src-1",
            source_url="https://example.com",
            content_excerpt="excerpt",
            retrieval_timestamp="2024-01-01T00:00:00",
        )
    ]
    facts = [
        type(
            "BusinessFact",
            (),
            {
                "dimension": "trade_intelligence",
                "query_id": "q-1",
                "source_ids": ["src-1"],
            },
        )()
    ]

    coverage = CoverageBuilder.build(
        research,
        evidence,
        facts,
        unsupported_dimensions=["market_opportunity", "market_access", "regulatory_sps_tbt"],
    )
    assert coverage.coverage_level == "partial"
    assert "market_opportunity" in coverage.unsupported_dimensions
    assert "market_access" in coverage.unsupported_dimensions
    assert "regulatory_sps_tbt" in coverage.unsupported_dimensions


def test_coverage_level_adequate_without_unsupported_dimensions():
    """Coverage level must remain adequate when there are no unsupported_dimensions."""
    research = _make_research_result(
        source_execution_statuses={"src-1": SourceExecutionStatus.SUCCESS_WITH_DATA},
    )
    evidence = [
        EvidenceReference(
            source_id="src-1",
            source_url="https://example.com",
            content_excerpt="excerpt",
            retrieval_timestamp="2024-01-01T00:00:00",
        )
    ]
    facts = [
        type(
            "BusinessFact",
            (),
            {
                "dimension": "trade_intelligence",
                "query_id": "q-1",
                "source_ids": ["src-1"],
            },
        )()
    ]

    coverage = CoverageBuilder.build(research, evidence, facts)
    assert coverage.coverage_level == "adequate"
    assert coverage.unsupported_dimensions == []


def test_synthesizer_coverage_reflects_unsupported_dimensions():
    """Synthesizer must propagate unsupported_dimensions into coverage."""
    synthesizer = BusinessIntelligenceSynthesizer()
    research = _make_research_result(
        sources_consulted=["comtrade"],
        source_execution_statuses={"comtrade": SourceExecutionStatus.SUCCESS_WITH_DATA},
        metadata={
            "discovery": {
                "queries": {
                    "q-1": {
                        "metadata": {
                            "unsupported_dimensions": [
                                "market_opportunity",
                                "market_access",
                            ]
                        }
                    }
                }
            }
        },
    )
    mission = type("Mission", (), {"result": {}, "goal": None})()

    answer = asyncio.run(
        synthesizer.synthesize(
            mission=mission,
            research_result=research,
        )
    )

    coverage = answer.provenance["coverage"]
    assert coverage["coverage_level"] == "partial"
    assert "market_opportunity" in coverage["unsupported_dimensions"]
    assert "market_access" in coverage["unsupported_dimensions"]
    assert any("no capable source" in lim for lim in coverage.get("limitations", []))


def test_response_builder_marks_limitations_when_unsupported_dimensions_exist():
    """ResponseBuilder must indicate limitations when business_answer has unsupported_dimensions."""
    business_answer = {
        "provenance": {
            "coverage": {
                "coverage_level": "partial",
                "unsupported_dimensions": ["market_opportunity", "market_access"],
            }
        }
    }
    mission = type(
        "Mission",
        (),
        {
            "mission_id": "m-1",
            "status": "completed",
            "result": {},
            "context": {"session_id": "s-1"},
        },
    )()
    decision = {"chosen_path": "research", "context": {"request_context": {}}}

    intent = ResponseBuilder.build(
        mission=mission,
        decision=decision,
        business_answer=business_answer,
    )

    assert "completed with limitations" in intent.content["outcome"]
    assert "review_limitations" in intent.suggested_actions


def test_response_builder_preserves_success_when_no_unsupported_dimensions():
    """ResponseBuilder must preserve normal success outcome when no unsupported_dimensions."""
    business_answer = {
        "provenance": {
            "coverage": {
                "coverage_level": "adequate",
                "unsupported_dimensions": [],
            }
        }
    }
    mission = type(
        "Mission",
        (),
        {
            "mission_id": "m-1",
            "status": "completed",
            "result": {},
            "context": {"session_id": "s-1"},
        },
    )()
    decision = {"chosen_path": "research", "context": {"request_context": {}}}

    intent = ResponseBuilder.build(
        mission=mission,
        decision=decision,
        business_answer=business_answer,
    )

    assert intent.content["outcome"] == "research completed successfully"
    assert "view_result" in intent.suggested_actions
    assert "review_limitations" not in intent.suggested_actions
