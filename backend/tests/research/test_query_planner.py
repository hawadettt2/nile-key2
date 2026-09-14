import pytest
from app.research.query_planner import ResearchQueryPlanner
from app.schemas.research import ResearchRequest
from app.schemas.research_query import ResearchQueryPlan


def _make_request(goal: str, context: dict = None, scope: dict = None) -> ResearchRequest:
    return ResearchRequest(
        goal=goal,
        context=context or {},
        scope=scope,
    )


class TestResearchQueryPlanner:
    def test_simple_query_does_not_decompose_artificially(self):
        planner = ResearchQueryPlanner()
        request = _make_request("What is the weather in Cairo?")
        plan = planner.plan(request)
        assert len(plan.queries) == 1
        assert plan.queries[0].dimension == "general"

    def test_complex_export_intent_decomposes(self):
        planner = ResearchQueryPlanner()
        request = _make_request(
            "export vegetables and fruits from Egypt to Jordan",
            context={},
            scope={},
        )
        plan = planner.plan(request)
        assert len(plan.queries) > 1
        dimensions = [q.dimension for q in plan.queries]
        assert "trade_intelligence" in dimensions
        assert "agrifood_intelligence" in dimensions

    def test_complex_export_intent_extracts_facts(self):
        planner = ResearchQueryPlanner()
        request = _make_request(
            "export vegetables and fruits from Egypt to Jordan",
            context={},
            scope={},
        )
        plan = planner.plan(request)
        profile = plan.intent_profile
        assert profile["reporter"] == "818"
        assert profile["partner"] == "400"
        assert "07" in profile["commodities"]
        assert "08" in profile["commodities"]
        assert profile["request_type"] == "export"
        assert profile["is_agrifood"] is True
        assert profile["is_trade_flow"] is True

    def test_queries_are_different_from_goal(self):
        planner = ResearchQueryPlanner()
        request = _make_request(
            "اريد تصدير الخضروات والفاكهة المصرية الى الاردن",
            context={},
            scope={},
        )
        plan = planner.plan(request)
        goal = request.goal.strip()
        for query in plan.queries:
            assert query.query != goal

    def test_deterministic_output(self):
        planner = ResearchQueryPlanner()
        request = _make_request(
            "اريد تصدير الخضروات والفاكهة المصرية الى الاردن",
            context={},
            scope={},
        )
        plan1 = planner.plan(request)
        plan2 = planner.plan(request)
        assert len(plan1.queries) == len(plan2.queries)
        for q1, q2 in zip(plan1.queries, plan2.queries):
            assert q1.query_id == q2.query_id
            assert q1.dimension == q2.dimension
            assert q1.query == q2.query

    def test_no_invented_parameters(self):
        planner = ResearchQueryPlanner()
        request = _make_request("export vegetables Egypt to Jordan")
        plan = planner.plan(request)
        for query in plan.queries:
            assert "2025" not in query.query
            assert "HS" not in query.query or "HS" in request.goal
            assert "indicator" not in query.query.lower()

    def test_source_boundary_preserved(self):
        planner = ResearchQueryPlanner()
        request = _make_request(
            "اريد تصدير الخضروات والفاكهة المصرية الى الاردن",
            context={},
            scope={},
        )
        plan = planner.plan(request)
        for query in plan.queries:
            assert query.source_preferences is None or isinstance(query.source_preferences, list)

    def test_query_traceability(self):
        planner = ResearchQueryPlanner()
        request = _make_request(
            "اريد تصدير الخضروات والفاكهة المصرية الى الاردن",
            context={},
            scope={},
        )
        plan = planner.plan(request)
        for query in plan.queries:
            assert query.query_id
            assert query.dimension
            assert query.purpose
            assert query.query

    def test_backward_compatibility_simple_search(self):
        planner = ResearchQueryPlanner()
        request = _make_request("Hello world")
        plan = planner.plan(request)
        assert len(plan.queries) == 1
        assert plan.queries[0].dimension == "general"

    def test_agrifood_dimension_only_for_agrifood(self):
        planner = ResearchQueryPlanner()
        request = _make_request("export software services Egypt to Jordan")
        plan = planner.plan(request)
        dimensions = [q.dimension for q in plan.queries]
        assert "agrifood_intelligence" not in dimensions

    def test_market_opportunity_requires_countries(self):
        planner = ResearchQueryPlanner()
        request = _make_request("export vegetables")
        plan = planner.plan(request)
        dimensions = [q.dimension for q in plan.queries]
        assert "market_opportunity" not in dimensions

    def test_logistics_requires_countries_and_trade_flow(self):
        planner = ResearchQueryPlanner()
        request = _make_request("market study Egypt")
        plan = planner.plan(request)
        dimensions = [q.dimension for q in plan.queries]
        assert "logistics_market_execution" not in dimensions
