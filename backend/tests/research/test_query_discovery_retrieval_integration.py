import asyncio

from app.research.orchestrator import DiscoveryStage, ResearchContext, RetrievalStage
from app.research.sources.discovery import SourceDiscovery
from app.research.sources.registry import SourceRegistry
from app.research.retrieval.contracts import RetrievedContent, RetrievalResult, RetrievalStatus
from app.schemas.research import ResearchRequest, Source, SourceRegistration
from app.schemas.research_query import ResearchQuery, ResearchQueryPlan


class RecordingRetrievalOrchestrator:
    def __init__(self):
        self.calls = []

    async def retrieve_sources(self, sources, query, context=None, scope=None):
        self.calls.append((query, [source.source_id for source in sources], scope or {}))
        return [
            RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.SUCCESS,
                content=RetrievedContent(source_id=source.source_id, raw_content={"results": [query]}),
            )
            for source in sources
        ]

    async def process_results(self, results):
        return results


def _registry():
    registry = SourceRegistry()
    for source in [
        Source(source_id="trade", name="Trade", source_type="external_trade_intelligence"),
        Source(source_id="logistics", name="Logistics", source_type="external_logistics_intelligence"),
        Source(source_id="reg", name="Regulations", source_type="regulation"),
    ]:
        registry.register(SourceRegistration(source=source))
    return registry


def _context():
    request = ResearchRequest(goal="export Egyptian produce")
    context = ResearchContext(request=request, request_id="integration-1")
    context.query_plan = ResearchQueryPlan(
        intent_profile={},
        queries=[
            ResearchQuery(query_id="q-trade", dimension="trade_intelligence", purpose="trade", query="trade query"),
            ResearchQuery(query_id="q-logistics", dimension="logistics_market_execution", purpose="logistics", query="logistics query"),
        ],
    )
    return context


def test_discovery_and_retrieval_are_qualified_per_query_without_fan_out():
    async def run():
        registry = _registry()
        context = _context()
        discovery = SourceDiscovery(registry)
        await DiscoveryStage(discovery).execute(context)

        routing = context.metadata["discovery"]["queries"]
        assert routing["q-trade"]["source_ids"] == ["trade"]
        assert routing["q-logistics"]["source_ids"] == ["logistics"]

        recorder = RecordingRetrievalOrchestrator()
        await RetrievalStage(recorder, registry).execute(context)

        assert [(query, sources) for query, sources, _ in recorder.calls] == [
            ("trade query", ["trade"]),
            ("logistics query", ["logistics"]),
        ]
        assert context.metadata["retrieval"]["query_routing"] == {
            "q-trade": ["trade"],
            "q-logistics": ["logistics"],
        }

    asyncio.run(run())


def test_unsupported_query_dimension_produces_no_provider_call():
    async def run():
        registry = _registry()
        context = ResearchContext(ResearchRequest(goal="unsupported"), "integration-2")
        context.query_plan = ResearchQueryPlan(
            intent_profile={},
            queries=[ResearchQuery(
                query_id="q-unsupported",
                dimension="unknown_dimension",
                purpose="unsupported",
                query="unsupported query",
            )],
        )
        await DiscoveryStage(SourceDiscovery(registry)).execute(context)
        assert context.metadata["discovery"]["queries"]["q-unsupported"]["source_ids"] == []

        recorder = RecordingRetrievalOrchestrator()
        await RetrievalStage(recorder, registry).execute(context)
        assert recorder.calls == []
        assert context.metadata["retrieval"]["query_routing"] == {"q-unsupported": []}

    asyncio.run(run())
