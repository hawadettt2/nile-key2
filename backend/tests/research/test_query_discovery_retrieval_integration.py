import asyncio

from app.research.orchestrator import DiscoveryStage, PlanningStage, ResearchContext, ResearchOrchestrator, RetrievalStage
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


class FixedPlanner:
    def __init__(self, plan):
        self.plan_value = plan

    def plan(self, request):
        return self.plan_value


def _registry():
    registry = SourceRegistry()
    for source in [
        Source(source_id="trade", name="Trade", source_type="external_trade_intelligence"),
        Source(source_id="logistics", name="Logistics", source_type="external_logistics_intelligence"),
        Source(source_id="reg", name="Regulations", source_type="regulation"),
    ]:
        registry.register(SourceRegistration(source=source))
    return registry


def _plan():
    return ResearchQueryPlan(
        intent_profile={},
        queries=[
            ResearchQuery(query_id="q-trade", dimension="trade_intelligence", purpose="trade", query="trade query"),
            ResearchQuery(query_id="q-logistics", dimension="logistics_market_execution", purpose="logistics", query="logistics query"),
        ],
    )


def _context():
    context = ResearchContext(ResearchRequest(goal="export Egyptian produce"), "integration-1")
    context.query_plan = _plan()
    return context


def test_discovery_and_retrieval_are_qualified_per_query_without_fan_out():
    async def run():
        registry = _registry()
        context = _context()
        await DiscoveryStage(SourceDiscovery(registry)).execute(context)

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


def test_canonical_planning_discovery_query_id_retrieval_path_isolated():
    async def run():
        registry = _registry()
        recorder = RecordingRetrievalOrchestrator()
        orchestrator = ResearchOrchestrator()
        orchestrator.register_stage(PlanningStage(FixedPlanner(_plan())))
        orchestrator.register_stage(DiscoveryStage(SourceDiscovery(registry)))
        orchestrator.register_stage(RetrievalStage(recorder, registry))

        result = await orchestrator.execute(ResearchRequest(goal="export Egyptian produce"), "integration-canonical")

        assert result.status == "completed"
        assert [(query, sources) for query, sources, _ in recorder.calls] == [
            ("trade query", ["trade"]),
            ("logistics query", ["logistics"]),
        ]
        assert result.metadata["discovery"]["queries"]["q-trade"]["source_ids"] == ["trade"]
        assert result.metadata["discovery"]["queries"]["q-logistics"]["source_ids"] == ["logistics"]
        assert result.metadata["retrieval"]["query_routing"] == {
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


def test_general_query_keeps_broad_discovery():
    async def run():
        registry = _registry()
        context = ResearchContext(ResearchRequest(goal="general market research"), "integration-general")
        context.query_plan = ResearchQueryPlan(
            intent_profile={},
            queries=[ResearchQuery(
                query_id="q-general",
                dimension="general",
                purpose="general",
                query="general query",
            )],
        )
        await DiscoveryStage(SourceDiscovery(registry)).execute(context)
        assert context.metadata["discovery"]["queries"]["q-general"]["source_ids"] == ["trade", "logistics", "reg"]

    asyncio.run(run())
