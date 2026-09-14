from typing import Any, Dict, List, Optional

from app.research.intent_extractor import extract_intent_facts, build_qualified_query
from app.schemas.research_query import ResearchQuery, ResearchQueryPlan
from app.schemas.research import ResearchRequest


class ResearchQueryPlanner:
    """Deterministic planner that decomposes a business intent into specialized research queries.

    Responsibilities:
    - Understand intent/context facts
    - Identify relevant knowledge dimensions
    - Create specialized research queries
    - Produce a deterministic ResearchQueryPlan

    This planner does NOT:
    - Make business decisions
    - Generate recommendations
    - Perform retrieval or evidence synthesis
    - Call LLMs or external APIs
    """

    _AGRIFOOD_COMMODITIES = {"07", "08"}
    _EXPORT_IMPORT_TYPES = {"export", "import"}
    _STUDY_TYPES = {"market_study", "market_research"}

    def plan(self, request: ResearchRequest) -> ResearchQueryPlan:
        """Create a research query plan from a research request."""
        extracted = extract_intent_facts(request.goal, request.context or {})
        intent_profile = self._build_intent_profile(request, extracted)
        queries = self._build_queries(request, extracted, intent_profile)
        return ResearchQueryPlan(
            intent_profile=intent_profile,
            queries=queries,
            decomposition_strategy="deterministic_rules",
        )

    def _build_intent_profile(self, request: ResearchRequest, extracted: Dict[str, Any]) -> Dict[str, Any]:
        """Build a profile of the intent from extracted facts."""
        profile: Dict[str, Any] = {
            "request_type": extracted.get("request_type"),
            "reporter": extracted.get("reporter"),
            "partner": extracted.get("partner"),
            "commodities": extracted.get("commodities") or [],
            "has_countries": bool(extracted.get("reporter") or extracted.get("partner")),
            "has_commodities": bool(extracted.get("commodities")),
            "is_agrifood": bool(self._AGRIFOOD_COMMODITIES.intersection(extracted.get("commodities") or [])),
            "is_trade_flow": extracted.get("request_type") in self._EXPORT_IMPORT_TYPES,
            "is_market_study": extracted.get("request_type") in self._STUDY_TYPES,
        }
        return profile

    def _build_queries(
        self,
        request: ResearchRequest,
        extracted: Dict[str, Any],
        intent_profile: Dict[str, Any],
    ) -> List[ResearchQuery]:
        """Build specialized queries based on intent profile."""
        queries: List[ResearchQuery] = []
        base_query = build_qualified_query(request.goal, extracted)
        context = dict(request.context or {})
        scope = dict(request.scope) if request.scope else None

        # Trade Intelligence: always relevant when there is a trade flow or market study
        if intent_profile.get("is_trade_flow") or intent_profile.get("is_market_study"):
            queries.append(self._trade_intelligence_query(base_query, context, scope, extracted))

        # Agrifood Intelligence: when commodities are agrifood
        if intent_profile.get("is_agrifood"):
            queries.append(self._agrifood_intelligence_query(base_query, context, scope, extracted))

        # Market Opportunity: when there is a clear export/import direction
        if intent_profile.get("is_trade_flow") and intent_profile.get("has_countries"):
            queries.append(self._market_opportunity_query(base_query, context, scope, extracted))

        # Logistics / Market Execution: relevant for physical export/import
        if intent_profile.get("is_trade_flow") and intent_profile.get("has_countries"):
            queries.append(self._logistics_query(base_query, context, scope, extracted))

        # If no specialized queries were generated, fall back to a single general query
        if not queries:
            queries.append(self._fallback_query(request.goal, context, scope))

        return queries

    def _trade_intelligence_query(
        self, base_query: str, context: Dict[str, Any], scope: Optional[Dict[str, Any]], extracted: Dict[str, Any]
    ) -> ResearchQuery:
        query_id = f"trade_{_stable_hash(base_query + 'trade')}"
        query_text = f"trade flow statistics {base_query}"
        query_scope = dict(scope) if scope else {}
        query_scope.setdefault("domains", []).append("trade_intelligence")
        return ResearchQuery(
            query_id=query_id,
            dimension="trade_intelligence",
            purpose="Find actual trade flows, volumes, and commercial transactions between the countries for the specified commodities",
            query=query_text,
            context=context,
            scope=query_scope,
        )

    def _agrifood_intelligence_query(
        self, base_query: str, context: Dict[str, Any], scope: Optional[Dict[str, Any]], extracted: Dict[str, Any]
    ) -> ResearchQuery:
        query_id = f"agrifood_{_stable_hash(base_query + 'agrifood')}"
        commodities = extracted.get("commodities") or []
        commodity_names = []
        for code in commodities:
            if code == "07":
                commodity_names.append("vegetables")
            elif code == "08":
                commodity_names.append("fruits")
        commodity_str = " ".join(commodity_names) if commodity_names else "agricultural"
        query_text = f"agrifood {commodity_str} export market conditions {base_query}"
        query_scope = dict(scope) if scope else {}
        query_scope.setdefault("domains", []).append("agrifood_intelligence")
        return ResearchQuery(
            query_id=query_id,
            dimension="agrifood_intelligence",
            purpose="Find agrifood-specific market conditions, prices, and export opportunities for the specified agricultural commodities",
            query=query_text,
            context=context,
            scope=query_scope,
        )

    def _market_opportunity_query(
        self, base_query: str, context: Dict[str, Any], scope: Optional[Dict[str, Any]], extracted: Dict[str, Any]
    ) -> ResearchQuery:
        query_id = f"opportunity_{_stable_hash(base_query + 'opportunity')}"
        reporter = extracted.get("reporter")
        partner = extracted.get("partner")
        countries = []
        if reporter:
            countries.append(reporter)
        if partner:
            countries.append(partner)
        country_str = " ".join(countries) if countries else ""
        query_text = f"export market opportunity demand {country_str} {base_query}"
        query_scope = dict(scope) if scope else {}
        query_scope.setdefault("domains", []).append("market_opportunity")
        return ResearchQuery(
            query_id=query_id,
            dimension="market_opportunity",
            purpose="Identify market demand, growth segments, and export opportunities beyond current trade patterns",
            query=query_text,
            context=context,
            scope=query_scope,
        )

    def _logistics_query(
        self, base_query: str, context: Dict[str, Any], scope: Optional[Dict[str, Any]], extracted: Dict[str, Any]
    ) -> ResearchQuery:
        query_id = f"logistics_{_stable_hash(base_query + 'logistics')}"
        reporter = extracted.get("reporter")
        partner = extracted.get("partner")
        countries = []
        if reporter:
            countries.append(reporter)
        if partner:
            countries.append(partner)
        country_str = " ".join(countries) if countries else ""
        query_text = f"logistics shipping performance {country_str} {base_query}"
        query_scope = dict(scope) if scope else {}
        query_scope.setdefault("domains", []).append("logistics_market_execution")
        return ResearchQuery(
            query_id=query_id,
            dimension="logistics_market_execution",
            purpose="Assess logistics performance, shipping reliability, and cross-border trade execution for the route",
            query=query_text,
            context=context,
            scope=query_scope,
        )

    def _fallback_query(self, goal: str, context: Dict[str, Any], scope: Optional[Dict[str, Any]]) -> ResearchQuery:
        query_id = f"general_{_stable_hash(goal)}"
        return ResearchQuery(
            query_id=query_id,
            dimension="general",
            purpose="General research query when no specific dimension applies",
            query=goal.strip(),
            context=context,
            scope=scope,
        )


def _stable_hash(text: str) -> str:
    """Deterministic short hash for query IDs."""
    import hashlib
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    return digest
