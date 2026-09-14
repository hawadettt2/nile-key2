import asyncio

from app.research.retrieval.contracts import RetrievedContent, RetrievalResult, RetrievalStatus, SourceRetriever
from app.research.retrieval.orchestrator import RetrievalOrchestrator
from app.schemas.research import Source


class RecordingRetriever(SourceRetriever):
    def __init__(self) -> None:
        self.calls = []

    async def retrieve(self, source, query, context=None, scope=None):
        self.calls.append((source.source_id, query, scope or {}))
        return RetrievalResult(
            source_id=source.source_id,
            status=RetrievalStatus.SUCCESS,
            content=RetrievedContent(source_id=source.source_id, raw_content={"results": [query]}),
        )


def test_each_query_retrieves_only_from_capable_sources():
    async def run():
        retriever = RecordingRetriever()
        orchestrator = RetrievalOrchestrator(retriever)
        sources = [
            Source(source_id="trade", name="Trade", source_type="external_trade_intelligence"),
            Source(source_id="logistics", name="Logistics", source_type="external_logistics_intelligence"),
            Source(source_id="reg", name="Regulations", source_type="regulation"),
        ]

        await orchestrator.retrieve_sources(sources, "trade query", scope={"domains": ["trade_intelligence"]})
        await orchestrator.retrieve_sources(sources, "logistics query", scope={"domains": ["logistics_market_execution"]})
        await orchestrator.retrieve_sources(sources, "regulation query", scope={"domains": ["regulatory_sps_tbt"]})

        assert [call[0] for call in retriever.calls] == ["trade", "logistics", "reg"]

    asyncio.run(run())


def test_unsupported_dimension_does_not_fan_out_to_all_sources():
    async def run():
        retriever = RecordingRetriever()
        orchestrator = RetrievalOrchestrator(retriever)
        sources = [
            Source(source_id="trade", name="Trade", source_type="external_trade_intelligence"),
            Source(source_id="reg", name="Regulations", source_type="regulation"),
        ]

        results = await orchestrator.retrieve_sources(
            sources,
            "unsupported query",
            scope={"domains": ["logistics_market_execution"]},
        )

        assert results == []
        assert retriever.calls == []

    asyncio.run(run())


def test_general_query_retains_broad_source_selection():
    async def run():
        retriever = RecordingRetriever()
        orchestrator = RetrievalOrchestrator(retriever)
        sources = [
            Source(source_id="trade", name="Trade", source_type="external_trade_intelligence"),
            Source(source_id="logistics", name="Logistics", source_type="external_logistics_intelligence"),
        ]

        await orchestrator.retrieve_sources(sources, "general query", scope={})

        assert [call[0] for call in retriever.calls] == ["trade", "logistics"]

    asyncio.run(run())
