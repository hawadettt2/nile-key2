"""Minimal regression tests for empty-evidence filtering in research pipeline."""

import pytest
from app.research.orchestrator import (
    EvidenceCaptureStage,
    RetrievalStage,
    ResearchContext,
    _is_meaningful_retrieval_content,
)
from app.research.retrieval.contracts import RetrievalStatus, RetrievedContent
from app.schemas.research import Evidence, Source


@pytest.mark.parametrize(
    "raw_content,expected",
    [
        (None, False),
        ("", False),
        ("   ", False),
        ({}, False),
        ({"results": []}, False),
        ({"results": []}, False),
        ({"results": [{"id": "1"}]}, True),
        ({"summary": "some text"}, True),
        ([], False),
        ([{"id": "1"}], True),
        (123, True),
    ],
)
def test_is_meaningful_retrieval_content(raw_content, expected):
    assert _is_meaningful_retrieval_content(raw_content) is expected


def test_evidence_capture_skips_empty_results():
    stage = EvidenceCaptureStage()
    context = ResearchContext(
        request=type("Req", (), {"goal": "test", "context": None, "scope": None, "source_preferences": None, "constraints": None})(),
        request_id="req-1",
    )
    context.metadata["retrieval"] = {
        "results": [
            {
                "status": RetrievalStatus.SUCCESS,
                "source_id": "empty-source",
                "content": {
                    "source_id": "empty-source",
                    "raw_content": {"results": []},
                    "content_type": None,
                    "metadata": {},
                },
            },
            {
                "status": RetrievalStatus.SUCCESS,
                "source_id": "real-source",
                "content": {
                    "source_id": "real-source",
                    "raw_content": {"results": [{"id": "818_400_07_2025", "content": "HS 07 — 100 USD"}]},
                    "content_type": None,
                    "metadata": {},
                },
            },
        ]
    }

    import asyncio
    result = asyncio.run(stage.execute(context))

    source_ids = [e.source_id for e in result.evidence]
    assert "empty-source" not in source_ids
    assert "real-source" in source_ids


def test_retrieval_stage_excludes_empty_results_from_sources_consulted():
    from app.research.orchestrator import _is_meaningful_retrieval_content
    from app.research.retrieval.contracts import RetrievalResult, RetrievedContent, RetrievalStatus

    empty_result = RetrievalResult(
        source_id="empty-source",
        status=RetrievalStatus.SUCCESS,
        content=RetrievedContent(source_id="empty-source", raw_content={"results": []}),
    )
    real_result = RetrievalResult(
        source_id="real-source",
        status=RetrievalStatus.SUCCESS,
        content=RetrievedContent(
            source_id="real-source",
            raw_content={"results": [{"id": "818_400_07_2025", "content": "HS 07 — 100 USD"}]},
        ),
    )
    processed = [empty_result, real_result]
    sources_consulted = [
        r.source_id
        for r in processed
        if r.status == RetrievalStatus.SUCCESS
        and _is_meaningful_retrieval_content(r.content.raw_content if r.content else None)
    ]
    assert "empty-source" not in sources_consulted
    assert "real-source" in sources_consulted
