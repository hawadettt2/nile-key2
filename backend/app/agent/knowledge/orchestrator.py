import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

from .registry import KnowledgeProviderRegistry


class KnowledgeOrchestrator:
    """Knowledge Orchestration / Fusion Layer.

    Wraps KnowledgeProviderRegistry to provide:
    - deterministic query classification
    - provider routing
    - parallel querying
    - composite ranking
    - cross-provider deduplication
    - conflict resolution
    - output assembly with orchestration metadata
    """

    def __init__(self, registry: KnowledgeProviderRegistry, config: Any) -> None:
        self._registry = registry
        self._config = config
        self._last_orchestration_meta: Optional[Dict[str, Any]] = None
        self._classification_rules = [
            ("agrifood", ["agriculture", "food", "crop", "livestock", "زراعة", "غذاء", "محصول", "ماشية"]),
            ("customs", ["customs", "declaration", "hs code", "جمارك", "تصريح جمركي", "كود hs"]),
            ("market_access", ["market access", "duty", "requirement", "فرص سوق", "متطلبات", "رسوم"]),
            ("regulatory", ["regulation", "law", "tariff", "قانون", "لائحة", "تعريفة"]),
            ("trade_statistics", ["trade", "export", "import", "إحصائيات تجارية", "صادرات", "واردات"]),
            ("rules_of_origin", ["origin", "certificate", "قانون المنشأ", "شهادة منشأ"]),
        ]
        self._routing_table = {
            "agrifood": {"primary": ["faostat"], "secondary": ["uncomtrade", "tradedata"]},
            "customs": {"primary": ["zatca", "moaah"], "secondary": ["gccstat"]},
            "regulatory": {"primary": ["moaah"], "secondary": ["zatca", "gccstat"]},
            "market_access": {"primary": ["moaah"], "secondary": ["zatca", "gccstat", "tradedata"]},
            "trade_statistics": {"primary": ["uncomtrade", "tradedata"], "secondary": ["gccstat", "faostat"]},
            "rules_of_origin": {"primary": ["gccstat"], "secondary": ["tradedata"]},
            "general": {"primary": [], "secondary": []},
        }

    async def orchestrate(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        sources: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        query_type = self._classify_query(query)
        providers_to_query = await self._route_providers(query_type, sources)
        raw_results = await self._query_providers(providers_to_query, query, context, limit)
        provider_meta = await self._build_provider_meta_map()
        ranked = self._rank_results(raw_results, provider_meta, query_type)
        deduped = self._deduplicate(ranked)
        resolved = self._resolve_conflicts(deduped)
        output = self._build_output(
            resolved,
            query_type,
            providers_to_query,
            limit,
            total_candidates=len(raw_results),
            after_dedup=len(deduped),
        )
        self._last_orchestration_meta = output.get("orchestration")
        return output

    def _classify_query(self, query: str) -> str:
        intent_lower = query.lower().strip()
        for query_type, keywords in self._classification_rules:
            for keyword in keywords:
                if keyword in intent_lower:
                    return query_type
        return "general"

    async def _route_providers(self, query_type: str, sources_filter: Optional[List[str]]) -> List[Tuple[str, bool]]:
        if sources_filter:
            return [(sid, True) for sid in sources_filter if self._registry.exists(sid)]

        routing = self._routing_table.get(query_type, self._routing_table["general"])
        primary = routing["primary"]
        secondary = routing["secondary"]

        if query_type == "general":
            all_providers = [p["id"] for p in await self._registry.list_providers()]
            return [(sid, True) for sid in all_providers]

        result = []
        for sid in primary:
            if self._registry.exists(sid):
                result.append((sid, True))
        for sid in secondary:
            if self._registry.exists(sid):
                result.append((sid, False))
        return result

    async def _query_providers(
        self,
        providers: List[Tuple[str, bool]],
        query: str,
        context: Optional[Dict[str, Any]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        import asyncio

        tasks = []
        for source_id, is_primary in providers:
            tasks.append(self._query_single_provider(source_id, query, context, limit, is_primary))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        flat: List[Dict[str, Any]] = []
        for result in results:
            if isinstance(result, Exception):
                continue
            if isinstance(result, list):
                flat.extend(result)
        return flat

    async def _query_single_provider(self, source_id: str, query: str, context: Optional[Dict[str, Any]], limit: int, is_primary: bool) -> List[Dict[str, Any]]:
        try:
            data = await self._registry.query(source_id=source_id, query=query, context=context, limit=limit)
            if isinstance(data, dict):
                source_results = data.get("results", [])
                if isinstance(source_results, list):
                    return source_results
        except Exception:
            pass
        return []

    async def _build_provider_meta_map(self) -> Dict[str, Dict[str, Any]]:
        meta: Dict[str, Dict[str, Any]] = {}
        try:
            for source in await self._registry.list_providers():
                sid = source.get("id")
                if sid:
                    meta[sid] = source
        except Exception:
            pass
        return meta

    def _compute_composite_score(
        self,
        result: Dict[str, Any],
        provider_meta: Dict[str, Any],
        query_type: str,
        is_primary: bool,
    ) -> float:
        confidence = result.get("confidence", 0.0)
        if not isinstance(confidence, (int, float)):
            confidence = 0.0

        authority_level = provider_meta.get("authority_level", "aggregated")
        authority_weights = {"official": 1.0, "commercial": 0.7, "aggregated": 0.5}
        authority_weight = authority_weights.get(authority_level, 0.5)

        effective_date = result.get("metadata", {}).get("effective_date", "")
        recency_weight = self._compute_recency_weight(effective_date)

        if query_type == "general":
            relevance_weight = 0.5
        else:
            relevance_weight = 1.0 if is_primary else 0.7

        score = (
            (confidence * 0.4) +
            (authority_weight * 0.3) +
            (recency_weight * 0.2) +
            (relevance_weight * 0.1)
        )
        return max(0.0, min(1.0, score))

    def _compute_recency_weight(self, effective_date: str) -> float:
        if not effective_date or not isinstance(effective_date, str):
            return 0.5
        try:
            dt = datetime.fromisoformat(effective_date.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age_days = (now - dt).days
            if age_days <= 365:
                return 1.0
            elif age_days <= 1095:
                return 0.8
            else:
                return 0.5
        except (ValueError, TypeError):
            return 0.5

    def _is_primary_for_query_type(self, source_id: str, query_type: str) -> bool:
        routing = self._routing_table.get(query_type, {})
        return source_id in routing.get("primary", [])

    def _rank_results(
        self,
        results: List[Dict[str, Any]],
        provider_meta: Dict[str, Any],
        query_type: str,
    ) -> List[Dict[str, Any]]:
        scored = []
        for result in results:
            source_id = result.get("source_id", "")
            is_primary = self._is_primary_for_query_type(source_id, query_type)
            provider_meta_for_source = provider_meta.get(source_id, {})
            composite = self._compute_composite_score(result, provider_meta_for_source, query_type, is_primary)
            scored.append({**result, "composite_score": composite})

        scored.sort(key=lambda r: r.get("source_id", ""))
        scored.sort(key=lambda r: r.get("metadata", {}).get("effective_date", "") or "", reverse=True)
        scored.sort(key=lambda r: r["composite_score"], reverse=True)
        return scored

    def _deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not getattr(self._config, "KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED", True):
            return results

        groups: Dict[str, List[Dict[str, Any]]] = {}
        for result in results:
            content = (result.get("content", "") or "")[:100].lower().strip()
            effective_date = result.get("metadata", {}).get("effective_date") or ""
            group_key = hashlib.sha1(f"{content}|{effective_date}".encode()).hexdigest()
            groups.setdefault(group_key, []).append(result)

        authority_order = {"official": 3, "commercial": 2, "aggregated": 1}

        deduped: List[Dict[str, Any]] = []
        for group in groups.values():
            if len(group) == 1:
                deduped.append(group[0])
                continue

            sources = {r.get("source_id") for r in group}
            if len(sources) == 1:
                winner = max(group, key=lambda r: r.get("composite_score", 0))
                deduped.append(winner)
            else:
                def auth_score(r):
                    return authority_order.get(r.get("metadata", {}).get("authority_level", "aggregated"), 1)

                max_auth = max(auth_score(r) for r in group)
                candidates = [r for r in group if auth_score(r) == max_auth]
                winner = max(candidates, key=lambda r: r.get("composite_score", 0))
                deduped.append(winner)

        return deduped

    def _resolve_conflicts(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not results:
            return results

        strategy = getattr(self._config, "KNOWLEDGE_ORCHESTRATION_CONFLICT_STRATEGY", "latest_official_wins")
        if strategy != "latest_official_wins":
            return results

        groups: Dict[str, List[Dict[str, Any]]] = {}
        for result in results:
            content_key = (result.get("content", "") or "")[:100].lower().strip()
            groups.setdefault(content_key, []).append(result)

        authority_order = {"official": 3, "commercial": 2, "aggregated": 1}

        def get_authority_level(result):
            level = result.get("metadata", {}).get("authority_level", "aggregated")
            return authority_order.get(level, 1)

        def get_date(result):
            return result.get("metadata", {}).get("effective_date") or ""

        resolved: List[Dict[str, Any]] = []
        for group in groups.values():
            if len(group) == 1:
                resolved.append(group[0])
                continue

            auth_levels = [get_authority_level(r) for r in group]
            max_auth = max(auth_levels)
            min_auth = min(auth_levels)

            if max_auth - min_auth > 1:
                winner = max(group, key=lambda r: (get_authority_level(r), get_date(r)))
            else:
                winner = max(group, key=lambda r: (get_date(r), get_authority_level(r)))

            unique_dates = {get_date(r) for r in group}
            unique_authorities = {get_authority_level(r) for r in group}

            if len(unique_dates) == 1 and len(unique_authorities) == 1:
                for r in group:
                    r_copy = {**r, "metadata": {**r.get("metadata", {})}}
                    r_copy["metadata"]["conflict"] = True
                    r_copy["metadata"]["conflict_with"] = [
                        other.get("source_id") for other in group if other.get("source_id") != r.get("source_id")
                    ]
                    resolved.append(r_copy)
            else:
                winner_copy = {**winner, "metadata": {**winner.get("metadata", {})}}
                winner_copy["metadata"]["conflict"] = True
                winner_copy["metadata"]["conflict_with"] = [
                    r.get("source_id") for r in group if r.get("source_id") != winner.get("source_id")
                ]
                resolved.append(winner_copy)

        return resolved

    def _build_output(
        self,
        results: List[Dict[str, Any]],
        query_type: str,
        providers_queried: List[Tuple[str, bool]],
        limit: int,
        total_candidates: int = 0,
        after_dedup: int = 0,
    ) -> Dict[str, Any]:
        trimmed = results[:limit]

        confidences = [r["confidence"] for r in trimmed if isinstance(r.get("confidence"), (int, float))]
        avg_confidence = sum(confidences) / len(confidences) if confidences else None

        orchestration_meta = {
            "query_type": query_type,
            "total_candidates": total_candidates,
            "after_dedup": after_dedup,
            "after_conflict_resolution": len(results),
            "providers_queried": [sid for sid, _ in providers_queried],
            "orchestrated_at": datetime.now(timezone.utc).isoformat(),
        }

        return {
            "results": trimmed,
            "confidence": avg_confidence,
            "sources": list({r.get("source_id") for r in trimmed if r.get("source_id")}),
            "orchestration": orchestration_meta,
        }
