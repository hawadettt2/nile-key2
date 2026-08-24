# Knowledge Orchestration / Fusion Layer â€” Detailed Implementation Plan

**Date:** 2026-08-15  
**Authority:** `\.kilo/plans/archive/1786795387856-knowledge-orchestration-fusion-plan\.md` â€” Single Source of Truth  
**Plan Path:** `\.kilo/plans/archive/1786795387856-knowledge-orchestration-fusion-detailed-implementation-plan\.md`  
**Status:** Detailed Planning Complete â€” Ready for Implementation Authorization  

**Governance Basis:** Project Owner approved all review findings and recommended changes on 2026-08-15. This detailed plan translates the approved planning specification into executable implementation steps.

---

## 1. Files to Create or Modify

### 1.1 New Files

| File | Responsibility | Notes |
|------|----------------|-------|
| `backend/app/agent/knowledge/orchestrator.py` | `KnowledgeOrchestrator` class: classification, routing, ranking, dedup, conflict resolution, output assembly | New component; wraps registry |
| `backend/tests/agent/knowledge/test_orchestrator_classification.py` | Unit tests for query classification | 15 tests |
| `backend/tests/agent/knowledge/test_orchestrator_routing.py` | Unit tests for provider routing | 12 tests |
| `backend/tests/agent/knowledge/test_orchestrator_ranking.py` | Unit tests for composite score ranking | 10 tests |
| `backend/tests/agent/knowledge/test_orchestrator_dedup.py` | Unit tests for deduplication | 10 tests |
| `backend/tests/agent/knowledge/test_orchestrator_conflict.py` | Unit tests for conflict resolution | 10 tests |
| `backend/tests/agent/knowledge/test_orchestrator_output.py` | Unit tests for output shape and metadata | 8 tests |
| `backend/tests/agent/knowledge/test_orchestrator_integration.py` | Integration tests with mocked registry/providers | 10 tests |
| `backend/tests/agent/test_reasoning_engine_orchestrator.py` | Integration tests for `_query_knowledge()` + `Decision.context` | 8 tests |

### 1.2 Modified Files

| File | Changes | Constraints |
|------|---------|-------------|
| `backend/app/agent/decision_engine/engine.py` | Extract `_query_knowledge_legacy()`; replace `_query_knowledge()` body; add `_last_orchestration_meta` handling in `reason()` | No other DEM core changes |
| `backend/main.py` | Instantiate `KnowledgeOrchestrator` and attach to `ReasoningEngine` in `lifespan()` | After registry population, before first request |
| `backend/app/core/config.py` | Add `KNOWLEDGE_ORCHESTRATION_*` settings | New section after provider settings; defaults are safe |

### 1.3 Files That Must NOT Change

| File | Reason |
|------|--------|
| `backend/app/agent/knowledge/provider.py` | `KnowledgeProvider` interface unchanged |
| `backend/app/agent/knowledge/registry.py` | `KnowledgeProviderRegistry` unchanged |
| `backend/app/agent/schemas/decision.py` | `Decision` schema unchanged |
| Any `knowledge_nodes`/`knowledge_edges` schema | No Knowledge Graph schema changes |
| Any router files | No DEM endpoint changes |
| `PLAN.md` | Single Source of Truth; not modified |

---

## 2. orchestrator.py â€” Exact Structure

### 2.1 File Layout

```
backend/app/agent/knowledge/orchestrator.py
â”œâ”€â”€ imports
â”œâ”€â”€ class KnowledgeOrchestrator
â”‚   â”œâ”€â”€ __init__(self, registry, config)
â”‚   â”œâ”€â”€ orchestrate(self, query, context, scope, sources, limit)  â†’ Dict[str, Any]
â”‚   â”œâ”€â”€ _classify_query(self, query)  â†’ str
â”‚   â”œâ”€â”€ _route_providers(self, query_type, sources_filter)  â†’ List[Tuple[str, bool]]
â”‚   â”œâ”€â”€ _query_providers(self, providers, query, context, limit)  â†’ List[Dict[str, Any]]
â”‚   â”œâ”€â”€ _compute_composite_score(self, result, provider_meta, query_type, is_primary)  â†’ float
â”‚   â”œâ”€â”€ _rank_results(self, results, provider_meta_map)  â†’ List[Dict[str, Any]]
â”‚   â”œâ”€â”€ _deduplicate(self, results)  â†’ List[Dict[str, Any]]
â”‚   â”œâ”€â”€ _detect_conflicts(self, results)  â†’ List[Dict[str, Any]]
â”‚   â”œâ”€â”€ _resolve_conflicts(self, results)  â†’ List[Dict[str, Any]]
â”‚   â””â”€â”€ _build_orchestration_meta(self, ...)  â†’ Dict[str, Any]
```

### 2.2 `__init__`

```python
class KnowledgeOrchestrator:
    def __init__(self, registry: KnowledgeProviderRegistry, config: Settings) -> None:
        self._registry = registry
        self._config = config
        self._classification_rules = [
            ("agrifood",         ["agriculture", "food", "crop", "livestock", "ط²ط±ط§ط¹ط©", "ط؛ط°ط§ط،", "ظ…ط­طµظˆظ„", "ظ…ط§ط´ظٹط©"]),
            ("customs",          ["customs", "declaration", "HS code", "ط¬ظ…ط§ط±ظƒ", "طھطµط±ظٹط­ ط¬ظ…ط±ظƒظٹ", "ظƒظˆط¯ HS"]),
            ("market_access",    ["market access", "duty", "requirement", "ظپط±طµ ط³ظˆظ‚", "ظ…طھط·ظ„ط¨ط§طھ", "ط±ط³ظˆظ…"]),
            ("regulatory",       ["regulation", "law", "tariff", "ظ‚ط§ظ†ظˆظ†", "ظ„ط§ط¦ط­ط©", "طھط¹ط±ظٹظپط©"]),
            ("trade_statistics", ["trade", "export", "import", "ط¥ط­طµط§ط¦ظٹط§طھ طھط¬ط§ط±ظٹط©", "طµط§ط¯ط±ط§طھ", "ظˆط§ط±ط¯ط§طھ"]),
            ("rules_of_origin",  ["origin", "certificate", "ظ‚ط§ظ†ظˆظ† ط§ظ„ظ…ظ†ط´ط£", "ط´ظ‡ط§ط¯ط© ظ…ظ†ط´ط£"]),
        ]
        self._routing_table = {
            "agrifood":         {"primary": ["faostat"], "secondary": ["uncomtrade", "tradedata"]},
            "customs":          {"primary": ["zatca", "moaah"], "secondary": ["gccstat"]},
            "regulatory":       {"primary": ["moaah"], "secondary": ["zatca", "gccstat"]},
            "market_access":    {"primary": ["moaah"], "secondary": ["zatca", "gccstat", "tradedata"]},
            "trade_statistics": {"primary": ["uncomtrade", "tradedata"], "secondary": ["gccstat", "faostat"]},
            "rules_of_origin":  {"primary": ["gccstat"], "secondary": ["tradedata"]},
            "general":          {"primary": [], "secondary": []},  # all registered
        }
```

### 2.3 `orchestrate()` â€” Public API

```python
async def orchestrate(
    self,
    query: str,
    context: Optional[Dict[str, Any]] = None,
    scope: Optional[str] = None,
    sources: Optional[List[str]] = None,
    limit: int = 10,
) -> Dict[str, Any]:
    # 1. Classify
    query_type = self._classify_query(query)
    
    # 2. Route
    providers_to_query = self._route_providers(query_type, sources)
    
    # 3. Query
    raw_results = await self._query_providers(providers_to_query, query, context, limit)
    
    # 4. Rank
    provider_meta = self._build_provider_meta_map()
    ranked = self._rank_results(raw_results, provider_meta, query_type)
    
    # 5. Dedup
    deduped = self._deduplicate(ranked)
    
    # 6. Resolve conflicts
    resolved = self._resolve_conflicts(deduped)
    
    # 7. Build output
    output = self._build_output(
        resolved, query_type, providers_to_query, limit,
        total_candidates=len(raw_results),
        after_dedup=len(deduped),
    )
    
    # 8. Cache orchestration metadata for integration point
    self._last_orchestration_meta = output.get("orchestration")
    
    return output
```

### 2.4 `_classify_query()` â€” Deterministic Algorithm

```python
def _classify_query(self, query: str) -> str:
    intent_lower = query.lower().strip()
    for query_type, keywords in self._classification_rules:
        for keyword in keywords:
            if keyword in intent_lower:
                return query_type
    return "general"
```

**Determinism guarantee:** Fixed list order; first match wins; no randomness; no NLP.

### 2.5 `_route_providers()` â€” Primary/Secondary Logic

```python
def _route_providers(self, query_type: str, sources_filter: Optional[List[str]]) -> List[Tuple[str, bool]]:
    if sources_filter:
        return [(sid, True) for sid in sources_filter if self._registry.exists(sid)]
    
    routing = self._routing_table.get(query_type, self._routing_table["general"])
    primary = routing["primary"]
    secondary = routing["secondary"]
    
    if query_type == "general":
        all_providers = [p["id"] for p in self._registry.list_providers()]
        return [(sid, True) for sid in all_providers]
    
    result = []
    for sid in primary:
        if self._registry.exists(sid):
            result.append((sid, True))
    for sid in secondary:
        if self._registry.exists(sid):
            result.append((sid, False))
    return result
```

**Return:** `List[Tuple[source_id, is_primary]]` â€” preserves primary/secondary distinction for downstream ranking.

### 2.6 `_query_providers()` â€” Parallel Query Execution

```python
async def _query_providers(
    self,
    providers: List[Tuple[str, bool]],
    query: str,
    context: Optional[Dict[str, Any]],
    limit: int,
) -> List[Dict[str, Any]]:
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

async def _query_single_provider(self, source_id, query, context, limit, is_primary) -> List[Dict[str, Any]]:
    try:
        data = await self._registry.query(source_id=source_id, query=query, context=context, limit=limit)
        if isinstance(data, dict):
            source_results = data.get("results", [])
            if isinstance(source_results, list):
                return source_results
    except Exception:
        pass
    return []
```

**Note:** All providers are queried in parallel via `asyncio.gather()`. The primary/secondary distinction is used only for ranking relevance weight in MVP. The `KNOWLEDGE_ORCHESTRATION_MIN_PRIMARY_RESULTS`-based fallback trigger is deferred to post-MVP to keep the MVP deterministic and simple. In MVP, every routed provider is queried unconditionally.

### 2.7 `_compute_composite_score()` â€” Ranking Formula

```python
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
        from datetime import datetime, timezone
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
```

### 2.8 `_rank_results()` â€” Sorting and Limiting

```python
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
    
    scored.sort(key=lambda r: r["composite_score"], reverse=True)
    return scored

def _is_primary_for_query_type(self, source_id: str, query_type: str) -> bool:
    routing = self._routing_table.get(query_type, {})
    return source_id in routing.get("primary", [])
```

**Tie-breaking:** Deterministic multi-pass stable sort:
1. Sort by `source_id` ASC
2. Sort by `effective_date` DESC
3. Sort by `composite_score` DESC

Python's sort is stable, so the last sort is the primary key and earlier sorts serve as tiebreakers.

```python
scored.sort(key=lambda r: r.get("source_id", ""))  # ASC
scored.sort(key=lambda r: r.get("metadata", {}).get("effective_date", "") or "", reverse=True)  # DESC
scored.sort(key=lambda r: r["composite_score"], reverse=True)  # DESC
```

### 2.9 `_deduplicate()` â€” Cross-Provider Dedup

```python
def _deduplicate(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not self._config.KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED:
        return results
    
    # Group by content+date first (cross-provider aware)
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
        
        # Check if all from same source
        sources = {r.get("source_id") for r in group}
        if len(sources) == 1:
            # Exact duplicate: same source, same content, same date
            winner = max(group, key=lambda r: r.get("composite_score", 0))
            deduped.append(winner)
        else:
            # Cross-source duplicate: keep highest authority, then highest composite_score
            def auth_score(r):
                return authority_order.get(r.get("metadata", {}).get("authority_level", "aggregated"), 1)
            
            max_auth = max(auth_score(r) for r in group)
            candidates = [r for r in group if auth_score(r) == max_auth]
            winner = max(candidates, key=lambda r: r.get("composite_score", 0))
            deduped.append(winner)
    
    return deduped
```

### 2.10 `_resolve_conflicts()` â€” Conflict Detection and Resolution

```python
def _resolve_conflicts(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not results:
        return results
    
    strategy = getattr(self._config, "KNOWLEDGE_ORCHESTRATION_CONFLICT_STRATEGY", "latest_official_wins")
    if strategy != "latest_official_wins":
        return results  # Only supported strategy in MVP
    
    # Group by content hash (content[:100] normalized)
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
        
        # Determine authority spread
        auth_levels = [get_authority_level(r) for r in group]
        max_auth = max(auth_levels)
        min_auth = min(auth_levels)
        
        if max_auth - min_auth > 1:
            # Authority difference > 1: keep higher authority (date is secondary tiebreaker)
            winner = max(group, key=lambda r: (get_authority_level(r), get_date(r)))
        else:
            # Authority difference <= 1: keep latest date (authority is secondary tiebreaker)
            winner = max(group, key=lambda r: (get_date(r), get_authority_level(r)))
        
        # Check for true conflicts (different dates OR different authorities)
        unique_dates = {get_date(r) for r in group}
        unique_authorities = {get_authority_level(r) for r in group}
        
        if len(unique_dates) == 1 and len(unique_authorities) == 1:
            # Same date, same authority â€” keep both and flag conflict per planning spec
            for r in group:
                r_copy = {**r, "metadata": {**r.get("metadata", {})}}
                r_copy["metadata"]["conflict"] = True
                r_copy["metadata"]["conflict_with"] = [
                    other.get("source_id") for other in group if other.get("source_id") != r.get("source_id")
                ]
                resolved.append(r_copy)
        else:
            # True conflict â€” keep winner, flag others
            winner_copy = {**winner, "metadata": {**winner.get("metadata", {})}}
            winner_copy["metadata"]["conflict"] = True
            winner_copy["metadata"]["conflict_with"] = [
                r.get("source_id") for r in group if r.get("source_id") != winner.get("source_id")
            ]
            resolved.append(winner_copy)
    
    return resolved
```

### 2.11 `_build_output()` â€” Final Assembly

```python
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
```

### 2.12 `_build_provider_meta_map()` â€” Metadata Lookup

```python
def _build_provider_meta_map(self) -> Dict[str, Dict[str, Any]]:
    meta: Dict[str, Dict[str, Any]] = {}
    try:
        for source in self._registry.list_providers():
            sid = source.get("id")
            if sid:
                meta[sid] = source
    except Exception:
        pass
    return meta
```

---

## 3. engine.py Changes â€” Exact Diffs

### 3.1 Extract `_query_knowledge_legacy()`

Add this new method to `ReasoningEngine`:

```python
async def _query_knowledge_legacy(self, intent: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Legacy knowledge query â€” iterates all providers, extends results blindly.
    
    Byte-for-byte equivalent to the original _query_knowledge() at lines 336-379.
    Used only as fallback when KnowledgeOrchestrator is not attached.
    """
    results: List[Dict[str, Any]] = []

    if self.knowledge_provider_registry is not None:
        try:
            providers_info = await self.knowledge_provider_registry.list_providers()
            for source in providers_info:
                source_id = source.get("id")
                if not source_id:
                    continue
                try:
                    data = await self.knowledge_provider_registry.query(
                        source_id=source_id,
                        query=intent,
                        context=parameters,
                        limit=10,
                    )
                    if isinstance(data, dict):
                        source_results = data.get("results")
                        if isinstance(source_results, list):
                            results.extend(source_results)
                except Exception:
                    continue
        except Exception:
            pass

    if not results and self.knowledge_provider is not None:
        try:
            data = await self.knowledge_provider.query(
                intent,
                context=parameters,
                limit=10,
            )
            if isinstance(data, dict):
                provider_results = data.get("results")
                if isinstance(provider_results, list):
                    results.extend(provider_results)
            elif isinstance(data, list):
                results.extend(data)
        except Exception:
            pass

    return results
```

### 3.2 Replace `_query_knowledge()` Body

```python
async def _query_knowledge(self, intent: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Query knowledge providers via KnowledgeOrchestrator if attached, else legacy fallback."""
    if self.knowledge_provider_registry is None:
        return []

    orchestrator = getattr(self, "_knowledge_orchestrator", None)
    if orchestrator is None:
        return await self._query_knowledge_legacy(intent, parameters)

    result = await orchestrator.orchestrate(
        query=intent,
        context=parameters,
        limit=10,
    )
    
    # Cache orchestration metadata for Decision.context
    self._last_orchestration_meta = result.get("orchestration")
    
    return result.get("results", [])
```

### 3.3 Add `_last_orchestration_meta` to `reason()`

In `reason()` method, after `knowledge = await self._query_knowledge(intent, parameters)` (line 93), add:

```python
# Preserve orchestration metadata in request_context
orchestration_meta = getattr(self, "_last_orchestration_meta", None)
if orchestration_meta:
    request_context["knowledge_orchestration"] = orchestration_meta
```

And in the `Decision.context` construction (lines 119-127), ensure `request_context` already contains the orchestration metadata:

```python
decision = Decision(
    decision_id=str(uuid.uuid4()),
    session_id=session_id,
    reasoning=reasoning,
    chosen_path=chosen_path,
    alternatives=alternatives,
    context={
        "intent": intent,
        "parameters": parameters,
        "request_context": request_context,  # now contains knowledge_orchestration if available
        "memories": memories,
        "knowledge": knowledge,
        "candidates": scored_candidates,
        "requires_approval": is_destructive,
    },
    ...
)
```

---

## 4. main.py Changes â€” Exact Diff

### 4.1 Add Orchestrator Import and Wiring

In `backend/main.py`, after the existing provider registrations and before the `yield` statement, add:

```python
# ========== Knowledge Orchestration / Fusion Layer ==========
if getattr(settings, "KNOWLEDGE_ORCHESTRATION_ENABLED", True):
    try:
        from app.agent.knowledge.orchestrator import KnowledgeOrchestrator
        orchestrator = KnowledgeOrchestrator(
            registry=knowledge_provider_registry,
            config=settings,
        )
        reasoning_engine._knowledge_orchestrator = orchestrator
        print("[SUCCESS] Knowledge Orchestrator attached to ReasoningEngine")
    except Exception as exc:
        print(f"[WARNING] Knowledge Orchestrator attachment failed: {exc}")
```

**Placement:** After all knowledge providers are registered, after `set_knowledge_registry(knowledge_provider_registry)` (line 215), before `yield` (line 236).

**Behavior:** If orchestrator attachment fails, `ReasoningEngine` falls back to legacy behavior automatically because `_knowledge_orchestrator` attribute is absent.

---

## 5. config.py Changes â€” Exact Diff

### 5.1 Add New Settings Section

In `backend/app/core/config.py`, after the FAOSTAT section (after line 105), add:

```python
    # ========== Knowledge Orchestration / Fusion Layer ==========
    KNOWLEDGE_ORCHESTRATION_ENABLED: bool = True
    KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED: bool = True
    KNOWLEDGE_ORCHESTRATION_MIN_PRIMARY_RESULTS: int = 3  # Post-MVP: not wired in MVP implementation
    KNOWLEDGE_ORCHESTRATION_MAX_RESULTS: int = 10
    KNOWLEDGE_ORCHESTRATION_CONFLICT_STRATEGY: str = "latest_official_wins"
```

---

## 6. Full Request-to-Results Sequence

### 6.1 Happy Path (Orchestrator Attached)

```
1. DEM Router receives POST /missions or equivalent
2. ReasoningEngine.reason(session_id, request) called
3. intent = request["intent"], parameters = request.get("parameters", {})
4. _map_intent_to_candidates(intent, parameters) â†’ mission candidates
5. _query_memory(session_id, intent) â†’ memory entries
6. _query_knowledge(intent, parameters):
   a. Retrieve self._knowledge_orchestrator
   b. Call orchestrator.orchestrate(query=intent, context=parameters, limit=10):
      i. _classify_query(intent) â†’ query_type (e.g., "trade_statistics")
      ii. _route_providers(query_type, sources_filter) â†’ [(source_id, is_primary), ...]
      iii. _query_providers(providers, query, context, limit) â†’ raw_results
      iv. _build_provider_meta_map() â†’ provider_meta
      v. _rank_results(raw_results, provider_meta, query_type) â†’ ranked_results
      vi. _deduplicate(ranked_results) â†’ deduped_results
      vii. _resolve_conflicts(deduped_results) â†’ resolved_results
      viii. _build_output(resolved_results, query_type, providers, limit) â†’ {
              "results": [...],
              "confidence": float | None,
              "sources": [str],
              "orchestration": {query_type, total_candidates, after_dedup, providers_queried, orchestrated_at}
          }
   c. self._last_orchestration_meta = output["orchestration"]
   d. return output["results"]
7. _apply_memory_biases(candidates, memories)
8. _evaluate_options(candidates, memories, knowledge, parameters)
9. _enhance_candidates_with_llm(...)
10. _select_best_option(scored_candidates)
11. _check_approval(chosen_path, intent, parameters)
12. _build_reasoning(chosen_path, scored_candidates, memories, knowledge)
13. _enhance_reasoning_with_llm(...)
14. request_context["knowledge_orchestration"] = self._last_orchestration_meta
15. Decision(context={..., "request_context": request_context, ...})
16. Return Decision.model_dump()
```

### 6.2 Fallback Path (Orchestrator Not Attached)

```
1-5. Same as above
6. _query_knowledge(intent, parameters):
   a. orchestrator = getattr(self, "_knowledge_orchestrator", None) â†’ None
   b. return await self._query_knowledge_legacy(intent, parameters)
      â†’ byte-for-byte equivalent to current behavior
7-16. Same as above (no orchestration metadata in request_context)
```

---

## 7. Test Plan â€” Exact Distribution

### 7.1 Unit Tests (66 total)

**File:** `tests/agent/knowledge/test_orchestrator_classification.py` (16 tests)

| # | Test Case | Input | Expected |
|---|-----------|-------|----------|
| 1 | "agriculture export" | intent | `agrifood` |
| 2 | "food commodity" | intent | `agrifood` |
| 3 | "crop livestock" | intent | `agrifood` |
| 4 | "customs declaration HS code" | intent | `customs` |
| 5 | "ط¬ظ…ط§ط±ظƒ طھطµط±ظٹط­" | intent | `customs` |
| 6 | "regulation law" | intent | `regulatory` |
| 7 | "ظ‚ط§ظ†ظˆظ† ظ„ط§ط¦ط­ط©" | intent | `regulatory` |
| 8 | "market access duty" | intent | `market_access` |
| 9 | "requirement ظ…طھط·ظ„ط¨ط§طھ" | intent | `market_access` |
| 10 | "tariff regulation" (overlap) | intent | `market_access` (priority over regulatory) |
| 11 | "trade statistics export" | intent | `trade_statistics` |
| 12 | "import ط¥ط­طµط§ط¦ظٹط§طھ" | intent | `trade_statistics` |
| 13 | "origin certificate" | intent | `rules_of_origin` |
| 14 | "ط´ظ‡ط§ط¯ط© ظ…ظ†ط´ط£" | intent | `rules_of_origin` |
| 15 | "random unrelated text" | intent | `general` |
| 16 | "export tariff regulation" (overlap) | intent | `market_access` (priority) |

**File:** `tests/agent/knowledge/test_orchestrator_routing.py` (12 tests)

| # | Test Case | Expected |
|---|-----------|----------|
| 1 | agrifood â†’ primary contains faostat | True |
| 2 | agrifood â†’ secondary contains tradedata | True |
| 3 | customs â†’ primary contains zatca, moaah | True |
| 4 | regulatory â†’ primary contains moaah only | True |
| 5 | market_access â†’ primary contains moaah only | True |
| 6 | market_access â†’ secondary contains zatca, gccstat, tradedata | True |
| 7 | trade_statistics â†’ primary contains uncomtrade, tradedata | True |
| 8 | general â†’ all registered providers | True |
| 9 | sources_filter bypasses routing table | Only filtered providers |
| 10 | Missing provider skipped gracefully | No KeyError |
| 11 | Empty registry returns empty | [] |
| 12 | Primary providers not in registry skipped | Graceful |

**File:** `tests/agent/knowledge/test_orchestrator_ranking.py` (10 tests)

| # | Test Case | Expected |
|---|-----------|----------|
| 1 | confidence=0.9, official, recent, primary | 0.96 |
| 2 | confidence=0.5, aggregated, old, general | 0.50 |
| 3 | Same score tie â€” effective_date DESC | Newer date wins |
| 4 | Same date tie â€” source_id ASC | Alphabetical wins |
| 5 | Missing confidence defaults to 0.0 | Handled |
| 6 | Missing effective_date â†’ recency 0.5 | Handled |
| 7 | Unknown authority_level â†’ 0.5 weight | Handled |
| 8 | Max score capped at 1.0 | 1.0 |
| 9 | Min score floored at 0.0 | 0.0 |
| 10 | Relevance weight for general = 0.5 | Correct |

**File:** `tests/agent/knowledge/test_orchestrator_dedup.py` (10 tests)

| # | Test Case | Expected |
|---|-----------|----------|
| 1 | Same source, same content, same date | 1 result kept |
| 2 | Different sources, same content, same date | 1 result kept (highest authority) |
| 3 | Different sources, same content, different dates | 2 results kept |
| 4 | Empty results | Empty |
| 5 | Dedup disabled via config | All results kept |
| 6 | content[:100] stable hash | Deterministic |
| 7 | None effective_date handled | Empty string in key |
| 8 | Unicode content normalized | Lowercased correctly |
| 9 | Mixed duplicates and unique | Correct subset |
| 10 | Large result set performance | Completes in <1s |

**File:** `tests/agent/knowledge/test_orchestrator_conflict.py` (10 tests)

| # | Test Case | Expected |
|---|-----------|----------|
| 1 | Same source, different dates | Latest date kept |
| 2 | Different sources, same date, different authorities | Higher authority kept |
| 3 | Different sources, different dates, same authority | Latest date kept |
| 4 | Different sources, different dates, different authorities | Higher authority kept (diff > 1 level) |
| 5 | Equal authority, equal date | Both kept, flagged |
| 6 | No effective_date on either | Both kept, flagged |
| 7 | conflict flag set on winner | True |
| 8 | conflict_with list populated | Correct source IDs |
| 9 | Unsupported strategy passthrough | No modification |
| 10 | Empty results | Empty |

**File:** `tests/agent/knowledge/test_orchestrator_output.py` (8 tests)

| # | Test Case | Expected |
|---|-----------|----------|
| 1 | Output has "results" key | Present |
| 2 | Output has "confidence" key | Present |
| 3 | Output has "sources" key | Present |
| 4 | Output has "orchestration" key | Present |
| 5 | orchestration has query_type | Correct type |
| 6 | orchestration has providers_queried | List of source IDs |
| 7 | orchestrated_at is ISO-8601 | Parseable |
| 8 | Empty results â†’ confidence=None | None |

### 7.2 Integration Tests (18 total)

**File:** `tests/agent/knowledge/test_orchestrator_integration.py` (10 tests)

| # | Test Case | Expected |
|---|-----------|----------|
| 1 | End-to-end with 2 mocked providers | Ranked results |
| 2 | End-to-end with empty providers | Empty results |
| 3 | End-to-end with provider raising exception | Graceful skip |
| 4 | End-to-end with sources filter | Only filtered queried |
| 5 | End-to-end dedup across providers | Duplicates removed |
| 6 | End-to-end conflict resolution | Winner selected |
| 7 | End-to-end all query types | Each classified correctly |
| 8 | End-to-end config disabled | Raw merged results |
| 9 | End-to-end max_results limit | Correct truncation |
| 10 | End-to-end orchestration metadata | Populated |

**File:** `tests/agent/test_reasoning_engine_orchestrator.py` (8 tests)

| # | Test Case | Expected |
|---|-----------|----------|
| 1 | Orchestrator attached â†’ _query_knowledge uses orchestrator | Orchestrated results |
| 2 | Orchestrator not attached â†’ _query_knowledge uses legacy | Legacy results |
| 3 | Legacy fallback returns same shape as current | Identical output shape |
| 4 | orchestration metadata in Decision.context | Present when orchestrator active |
| 5 | No orchestration metadata when orchestrator absent | Absent |
| 6 | Registry None â†’ empty results | [] |
| 7 | Full reason() flow with orchestrator | Decision produced |
| 8 | Full reason() flow without orchestrator | Decision produced (legacy) |

### 7.3 Regression Tests

| Test Suite | Requirement |
|------------|-------------|
| `test_uncomtrade_*` | All pass (no provider changes) |
| `test_faostat_*` | All pass |
| `test_tradedata_*`, `test_mooadapter_*`, `test_gccstat_*`, `test_zatca_*` | All pass |
| `test_reasoning_engine*` | All pass (fallback behavior preserved) |

---

## 8. Acceptance Criteria by Stage

### Stage 1: orchestrator.py Skeleton + Classification + Routing

**Acceptance Criteria:**
- [ ] `KnowledgeOrchestrator` class instantiable with `(registry, config)`
- [ ] `_classify_query()` returns correct type for all 6 query types + general
- [ ] Classification is deterministic: same input â†’ same output across 1000 runs
- [ ] Overlap handling: "export tariff regulation" â†’ `market_access` (not `trade_statistics`)
- [ ] `_route_providers()` returns correct primary/secondary lists for each query type
- [ ] `sources` filter bypasses routing table correctly
- [ ] Missing providers are skipped gracefully

**Tests:** 28 (16 classification + 12 routing)

### Stage 2: Query Execution + Ranking

**Acceptance Criteria:**
- [ ] `_query_providers()` queries all assigned providers in parallel
- [ ] `_query_providers()` handles provider exceptions gracefully
- [ ] `_compute_composite_score()` returns value in [0.0, 1.0] for all input combinations
- [ ] Ranking sorts by composite_score DESC, then effective_date DESC, then source_id ASC
- [ ] Top `KNOWLEDGE_ORCHESTRATION_MAX_RESULTS` retained
- [ ] Tie-breaking is deterministic

**Tests:** 10 (ranking)

### Stage 3: Deduplication + Conflict Resolution

**Acceptance Criteria:**
- [ ] Exact duplicates (same source, content[:100], date) â†’ 1 result kept
- [ ] Cross-source duplicates (different sources, same content[:100], same date) â†’ 1 result kept (highest authority)
- [ ] Different dates â†’ both retained (not deduplicated)
- [ ] Conflict detection flags conflicts correctly
- [ ] "Latest official wins" strategy applied deterministically
- [ ] Dedup disabled via config â†’ all results retained

**Tests:** 18 (10 dedup + 8 conflict)

### Stage 4: Output + Integration

**Acceptance Criteria:**
- [ ] Output shape matches Section 7.2 of planning spec exactly
- [ ] `orchestration` metadata populated correctly
- [ ] `_query_knowledge()` returns `results` list when orchestrator attached
- [ ] `_query_knowledge()` returns legacy results when orchestrator not attached
- [ ] `Decision.context["knowledge_orchestration"]` populated when orchestrator active
- [ ] `Decision.context["knowledge_orchestration"]` absent when orchestrator inactive
- [ ] No modifications to `Decision` schema
- [ ] No modifications to `KnowledgeProvider` or `KnowledgeProviderRegistry`

**Tests:** 18 (8 output + 10 integration)

### Stage 5: End-to-End Regression

**Acceptance Criteria:**
- [ ] All 66 new unit tests pass
- [ ] All 18 new integration tests pass
- [ ] All existing provider tests pass (no regressions)
- [ ] All existing reasoning engine tests pass (fallback preserved)
- [ ] `orchestrator.py` imports cleanly
- [ ] `main.py` starts without errors
- [ ] `_query_knowledge_legacy()` produces identical output to current `_query_knowledge()` for same inputs

**Tests:** 66 + 18 + existing suites

---

## 9. Implementation Phase Order and Dependencies

```
Phase 1: orchestrator.py (Stages 1-3)
â”œâ”€â”€ Stage 1.1: Classification + Routing
â”œâ”€â”€ Stage 1.2: Query Execution
â”œâ”€â”€ Stage 1.3: Ranking
â”œâ”€â”€ Stage 1.4: Deduplication
â””â”€â”€ Stage 1.5: Conflict Resolution
    â†“
Phase 2: engine.py Changes
â”œâ”€â”€ Stage 2.1: Extract _query_knowledge_legacy()
â”œâ”€â”€ Stage 2.2: Replace _query_knowledge() body
â””â”€â”€ Stage 2.3: Add orchestration metadata to reason()
    â†“
Phase 3: main.py + config.py
â”œâ”€â”€ Stage 3.1: Add config settings
â””â”€â”€ Stage 3.2: Wire orchestrator in lifespan()
    â†“
Phase 4: Tests (parallel with Phases 1-3)
â”œâ”€â”€ Stage 4.1: Unit tests (66)
â”œâ”€â”€ Stage 4.2: Integration tests (18)
â””â”€â”€ Stage 4.3: Regression verification
    â†“
Phase 5: Verification
â”œâ”€â”€ Stage 5.1: All tests pass
â”œâ”€â”€ Stage 5.2: No regressions
â””â”€â”€ Stage 5.3: Acceptance criteria met
```

**Dependency graph:**
- Phase 1 must complete before Phase 2 (orchestrator must exist before engine can use it)
- Phase 2 must complete before Phase 3 (engine changes must exist before wiring)
- Phase 4 can run in parallel with Phases 1-3 (tests can be written against the plan)
- Phase 5 requires all previous phases complete

---

## 10. Verification Criteria (Master Checklist)

1. `_query_knowledge()` returns ranked, deduplicated, conflict-resolved results when orchestrator is attached
2. Composite score is computed correctly for all authority levels and relevance weights
3. Deduplication removes exact duplicates within and across sources
4. Conflict resolution applies "latest official wins" strategy deterministically
5. `orchestration` metadata is present in `Decision.context["knowledge_orchestration"]` when orchestrator is active
6. Legacy fallback works when orchestrator is not set (byte-for-byte equivalent to current behavior)
7. No regressions in existing knowledge layer tests
8. No modifications to `KnowledgeProvider`, `KnowledgeProviderRegistry`, or DEM core schemas
9. Query classification is deterministic and order-independent for non-overlapping queries
10. Overlapping queries (e.g., "export tariff regulation") are classified by priority order, not randomly
11. All 66 unit tests pass
12. All 18 integration tests pass
13. `main.py` starts without errors with orchestrator enabled
14. `main.py` starts without errors with orchestrator disabled (fallback)
15. No new Knowledge Families added
16. No new Providers added
17. No Knowledge Graph schema changes
18. No database migrations required

---

## 11. Open Items for Implementation Agent

| # | Item | Type | Status | Action Required |
|---|------|------|--------|-----------------|
| 1 | Moaah `market_access` coverage beyond Egypt | Validation | Pending | Verify at implementation time; if Egypt-only, adjust routing |
| 2 | UN Comtrade `effective_date` format | Validation | Pending | Verify parseability; add fallback if needed |
| 3 | TradeData confidence range compatibility | Validation | Pending | Verify composite_score stays in [0.0, 1.0] |
| 4 | `content[:100]` dedup slice length | Engineering Decision | Pending | Keep 100 for MVP; adjust if false negatives found |

**No Project Owner decisions remain pending.**

---

## 12. Constraints Checklist

| Constraint | Status | Evidence |
|------------|--------|----------|
| No new Knowledge Families | âœ… | Section 1.3 Out of Scope |
| No new Providers | âœ… | Section 1.3 Out of Scope |
| No DEM core modifications beyond `_query_knowledge()` | âœ… | Section 1.3, 8.2 |
| No Knowledge Graph schema changes | âœ… | Section 1.3 Out of Scope |
| No database migrations | âœ… | Section 1.3 Out of Scope |
| No frontend changes | âœ… | Section 1.3 Out of Scope |
| No Avatar/Renderer changes | âœ… | Section 1.3 Out of Scope |
| No LLM summary in MVP | âœ… | Section 7.1 |
| `logistics` not a query type | âœ… | Section 2.1 Note |
| Moaah primary for market_access | âœ… | Section 3.1 |
| Legacy fallback preserved | âœ… | Section 8.2, 3.1 |
| orchestration in Decision.context | âœ… | Section 8.3 |
| Deterministic classification | âœ… | Section 2.2 |

---

## 13. Contradictions and Assumptions Log

**No contradictions found between this detailed plan and the approved planning specification.**

**Assumptions verified against code:**
1. `_query_knowledge()` exists at lines 336-379 of `engine.py` â€” **verified**
2. `Decision.context` is a plain dict â€” **verified** (Pydantic `Dict[str, Any]`)
3. `main.py` lifespan has provider registration before `yield` â€” **verified**
4. `config.py` uses Pydantic Settings with defaults â€” **verified**
5. `registry.list_providers()` returns list of source dicts â€” **verified**
6. `registry.query(source_id, ...)` returns dict with `results` key â€” **verified**
7. All providers return `source_id` in result items â€” **verified** (mooadapter, tradedata, zatca, gccstat, faostat, uncomtrade all set `source_id`)

---

*Plan Status: Detailed Implementation Plan Complete â€” Ready for Implementation Authorization â€” Next Step: Code Execution (not authorized in this mode)*

