import pytest
from app.research.retrieval.contracts import (
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
)
from app.research.retrieval.query_enhancer import QueryEnhancer
from app.schemas.research import Source


class FakeSourceRetriever:
    def __init__(self, responses):
        self._responses = responses
        self.calls = []

    async def retrieve(self, source, query, context=None, scope=None):
        self.calls.append({
            "source_id": source.source_id,
            "query": query,
            "context": dict(context or {}),
            "scope": dict(scope or {}) if scope else None,
        })
        response = self._responses.get(source.source_id)
        if response is None:
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.FAILED,
                error="no response configured",
            )
        if callable(response):
            return response(source, query, context, scope)
        return response


def _source(source_id: str) -> Source:
    return Source(
        source_id=source_id,
        name=source_id,
        source_type="other",
        reference=None,
        metadata={},
        status="active",
    )


def _success_with_results(source_id: str, results) -> RetrievalResult:
    return RetrievalResult(
        source_id=source_id,
        status=RetrievalStatus.SUCCESS,
        content=RetrievedContent(
            source_id=source_id,
            raw_content={"results": results},
            content_type="application/json",
            metadata={},
        ),
    )


def _success_empty(source_id: str) -> RetrievalResult:
    return RetrievalResult(
        source_id=source_id,
        status=RetrievalStatus.SUCCESS,
        content=RetrievedContent(
            source_id=source_id,
            raw_content={"results": []},
            content_type="application/json",
            metadata={},
        ),
    )


def _failed(source_id: str, error: str = "failed") -> RetrievalResult:
    return RetrievalResult(
        source_id=source_id,
        status=RetrievalStatus.FAILED,
        error=error,
    )


class TestQueryEnhancer:
    def test_no_retry_when_all_sources_have_results(self):
        retriever = FakeSourceRetriever({
            "source-a": _success_empty("source-a"),
            "source-b": _success_with_results("source-b", [{"id": 1}]),
        })
        enhancer = QueryEnhancer(retriever=retriever)

        import asyncio
        result = asyncio.run(enhancer.enhance_empty_results(
            sources=[_source("source-a"), _source("source-b")],
            results=[_success_empty("source-a"), _success_with_results("source-b", [{"id": 1}])],
            query="test",
            context={},
        ))

        assert len(result) == 2
        assert len(retriever.calls) == 0

    def test_retry_when_enhancement_is_possible(self):
        def faostat_retry(source, query, context, scope):
            if context.get("area") == "Egypt":
                return _success_with_results("faostat", [{"area": "Egypt", "value": 100}])
            return _success_empty("faostat")

        retriever = FakeSourceRetriever({
            "comtrade": _success_with_results("comtrade", [{"reporter_desc": "Egypt", "partner_desc": "Jordan"}]),
            "faostat": faostat_retry,
        })
        enhancer = QueryEnhancer(retriever=retriever)

        import asyncio
        result = asyncio.run(enhancer.enhance_empty_results(
            sources=[_source("comtrade"), _source("faostat")],
            results=[
                _success_with_results("comtrade", [{"reporter_desc": "Egypt", "partner_desc": "Jordan"}]),
                _success_empty("faostat"),
            ],
            query="export vegetables Egypt",
            context={},
        ))

        assert len(result) == 3
        faostat_calls = [c for c in retriever.calls if c["source_id"] == "faostat"]
        assert len(faostat_calls) == 1
        assert faostat_calls[0]["context"]["area"] == "Egypt"

    def test_no_retry_when_enhancement_is_not_possible(self):
        retriever = FakeSourceRetriever({
            "faostat": _success_empty("faostat"),
        })
        enhancer = QueryEnhancer(retriever=retriever)

        import asyncio
        result = asyncio.run(enhancer.enhance_empty_results(
            sources=[_source("faostat")],
            results=[_success_empty("faostat")],
            query="export vegetables Egypt",
            context={},
        ))

        assert len(result) == 1
        assert len(retriever.calls) == 0

    def test_no_retry_on_failed_sources(self):
        retriever = FakeSourceRetriever({
            "source-a": _failed("source-a"),
        })
        enhancer = QueryEnhancer(retriever=retriever)

        import asyncio
        result = asyncio.run(enhancer.enhance_empty_results(
            sources=[_source("source-a")],
            results=[_failed("source-a")],
            query="test",
            context={},
        ))

        assert len(result) == 1
        assert len(retriever.calls) == 0

    def test_no_retry_loop(self):
        call_count = 0

        def always_empty(source, query, context, scope):
            nonlocal call_count
            call_count += 1
            return _success_empty("source-a")

        retriever = FakeSourceRetriever({
            "source-a": always_empty,
        })
        enhancer = QueryEnhancer(retriever=retriever)

        import asyncio
        result = asyncio.run(enhancer.enhance_empty_results(
            sources=[_source("source-a")],
            results=[_success_empty("source-a")],
            query="test",
            context={},
        ))

        assert call_count == 0
        assert len(result) == 1

    def test_worldbank_lpi_retry_with_country(self):
        def wb_retry(source, query, context, scope):
            if context.get("country") == "818":
                return _success_with_results("worldbank-lpi", [{"country": "Egypt", "indicator": "LP.LPI.OVRL.XQ"}])
            return _success_empty("worldbank-lpi")

        retriever = FakeSourceRetriever({
            "comtrade": _success_with_results("comtrade", [{"reporter_code": "818", "reporter_desc": "Egypt"}]),
            "worldbank-lpi": wb_retry,
        })
        enhancer = QueryEnhancer(retriever=retriever)

        import asyncio
        result = asyncio.run(enhancer.enhance_empty_results(
            sources=[_source("comtrade"), _source("worldbank-lpi")],
            results=[
                _success_with_results("comtrade", [{"reporter_code": "818", "reporter_desc": "Egypt"}]),
                _success_empty("worldbank-lpi"),
            ],
            query="export Egypt",
            context={},
        ))

        wb_calls = [c for c in retriever.calls if c["source_id"] == "worldbank-lpi"]
        assert len(wb_calls) == 1
        assert wb_calls[0]["context"]["country"] == "818"

    def test_unknown_source_not_enhanced(self):
        retriever = FakeSourceRetriever({
            "unknown-source": _success_empty("unknown-source"),
        })
        enhancer = QueryEnhancer(retriever=retriever)

        import asyncio
        result = asyncio.run(enhancer.enhance_empty_results(
            sources=[_source("unknown-source")],
            results=[_success_empty("unknown-source")],
            query="test",
            context={},
        ))

        assert len(result) == 1
        assert len(retriever.calls) == 0

    def test_enhancement_uses_partner_desc_when_reporter_desc_missing(self):
        def faostat_retry(source, query, context, scope):
            if context.get("area") == "Jordan":
                return _success_with_results("faostat", [{"area": "Jordan", "value": 100}])
            return _success_empty("faostat")

        retriever = FakeSourceRetriever({
            "comtrade": _success_with_results("comtrade", [{"partner_desc": "Jordan"}]),
            "faostat": faostat_retry,
        })
        enhancer = QueryEnhancer(retriever=retriever)

        import asyncio
        result = asyncio.run(enhancer.enhance_empty_results(
            sources=[_source("comtrade"), _source("faostat")],
            results=[
                _success_with_results("comtrade", [{"partner_desc": "Jordan"}]),
                _success_empty("faostat"),
            ],
            query="export Egypt to Jordan",
            context={},
        ))

        assert len(result) == 3
        faostat_calls = [c for c in retriever.calls if c["source_id"] == "faostat"]
        assert len(faostat_calls) == 1
        assert faostat_calls[0]["context"]["area"] == "Jordan"

    def test_faostat_no_retry_when_descs_are_empty(self):
        retriever = FakeSourceRetriever({
            "comtrade": _success_with_results("comtrade", [{"reporter_desc": "", "partner_desc": ""}]),
            "faostat": _success_empty("faostat"),
        })
        enhancer = QueryEnhancer(retriever=retriever)

        import asyncio
        result = asyncio.run(enhancer.enhance_empty_results(
            sources=[_source("comtrade"), _source("faostat")],
            results=[
                _success_with_results("comtrade", [{"reporter_desc": "", "partner_desc": ""}]),
                _success_empty("faostat"),
            ],
            query="export Egypt to Jordan",
            context={},
        ))

        faostat_calls = [c for c in retriever.calls if c["source_id"] == "faostat"]
        assert len(faostat_calls) == 0
        assert len(result) == 2

    def test_worldbank_lpi_no_retry_when_codes_are_empty(self):
        retriever = FakeSourceRetriever({
            "comtrade": _success_with_results("comtrade", [{"reporter_code": None, "partner_code": None}]),
            "worldbank-lpi": _success_empty("worldbank-lpi"),
        })
        enhancer = QueryEnhancer(retriever=retriever)

        import asyncio
        result = asyncio.run(enhancer.enhance_empty_results(
            sources=[_source("comtrade"), _source("worldbank-lpi")],
            results=[
                _success_with_results("comtrade", [{"reporter_code": None, "partner_code": None}]),
                _success_empty("worldbank-lpi"),
            ],
            query="export Egypt",
            context={},
        ))

        wb_calls = [c for c in retriever.calls if c["source_id"] == "worldbank-lpi"]
        assert len(wb_calls) == 0
        assert len(result) == 2
