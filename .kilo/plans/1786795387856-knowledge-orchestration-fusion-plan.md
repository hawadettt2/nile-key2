# Knowledge Orchestration / Fusion Layer — Planning Specification

**Date:** 2026-08-15  
**Authority:** `PLAN.md` v2.1 (Master Roadmap) — Single Source of Truth  
**Prerequisite:** `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` — Governance Decision: Knowledge Orchestration/Fusion Layer is the next gap  
**Plan Path:** `.kilo/plans/1786795387856-knowledge-orchestration-fusion-plan.md`  
**Status:** Planning Complete — Ready for Governance Review  

**Governance Decision (Project Owner, 2026-08-15):** All review findings and recommended changes are approved. This plan is adopted as the official planning basis for the Knowledge Orchestration/Fusion Layer.

---

## 1. Objective and Scope

### 1.1 Objective

Introduce a **Knowledge Orchestration/Fusion Layer** between `ReasoningEngine._query_knowledge()` and the `KnowledgeProviderRegistry` to transform raw, uncoordinated multi-provider results into **executive-grade knowledge** suitable for DEM's intelligence mission.

### 1.2 Problem Statement (Current State)

Current `_query_knowledge()` implementation (`backend/app/agent/decision_engine/engine.py:336-379`):
- Iterates **all** registered providers for **every** query
- Extends results as a flat list with **no ranking**
- **No deduplication** across sources
- **No conflict resolution** when providers disagree
- **No synthesis** — downstream consumers receive raw merged lists
- **No routing** — irrelevant providers are queried unnecessarily

### 1.3 Scope

**In Scope:**
- Query taxonomy and classification
- Provider routing/preference per query type
- Result ranking by composite score
- Cross-provider deduplication
- Conflict resolution strategy
- Knowledge synthesis output
- Integration point in `ReasoningEngine._query_knowledge()`
- Configuration via `config.py`
- Test plan

**Out of Scope:**
- New Knowledge Families (no expansion)
- New Provider implementation
- DEM core modifications beyond `_query_knowledge()`
- Knowledge Graph schema changes
- Database migrations
- Frontend changes
- Avatar/Renderer implementation
- LLM-generated summaries (deferred to post-MVP)

---

## 2. Query Taxonomy

### 2.1 Query Types

Classification is based on **intent keyword matching** (deterministic, no NLP) and **context parameters**.

| Query Type | Primary Keywords (intent) | Context Signals | Preferred Providers | Secondary Providers |
|------------|---------------------------|-----------------|---------------------|---------------------|
| `agrifood` | "agriculture", "food", "crop", "livestock", "زراعة", "غذاء", "محصول", "ماشية" | `area`, `item`, `year` | FAOSTAT | UN Comtrade, TradeData |
| `customs` | "customs", "declaration", "HS code", "جمارك", "تصريح جمركي", "كود HS" | `hs_code`, `country` | ZATCA, Moaah | GCC-Stat |
| `regulatory` | "regulation", "law", "tariff", "قانون", "لائحة", "تعريفة" | `country`, `hs_code` | Moaah | ZATCA, GCC-Stat |
| `market_access` | "market access", "duty", "requirement", "فرص سوق", "متطلبات", "رسوم" | `country`, `hs_code` | Moaah | ZATCA, GCC-Stat, TradeData |
| `trade_statistics` | "trade", "export", "import", "إحصائيات تجارية", "صادرات", "واردات" | `country`, `year`, `hs_code` | UN Comtrade, TradeData | GCC-Stat, FAOSTAT |
| `rules_of_origin` | "origin", "certificate", "قانون المنشأ", "شهادة منشأ" | `country`, `fta` | GCC-Stat | TradeData |
| `general` | *(no match)* | — | All registered | — |

**Note:** `logistics` is intentionally omitted. No current provider delivers dedicated logistics intelligence (ports, shipping performance, supply chain reliability). Queries with logistics intent fall through to `general`.

### 2.2 Classification Rules — Deterministic Order

```python
QUERY_TYPE_RULES = [
    ("agrifood",        ["agriculture", "food", "crop", "livestock", "زراعة", "غذاء", "محصول", "ماشية"]),
    ("customs",         ["customs", "declaration", "HS code", "جمارك", "تصريح جمركي", "كود HS"]),
    ("market_access",   ["market access", "duty", "requirement", "فرص سوق", "متطلبات", "رسوم"]),
    ("regulatory",      ["regulation", "law", "tariff", "قانون", "لائحة", "تعريفة"]),
    ("trade_statistics",["trade", "export", "import", "إحصائيات تجارية", "صادرات", "واردات"]),
    ("rules_of_origin", ["origin", "certificate", "قانون المنشأ", "شهادة منشأ"]),
]
```

**Classification outcome:** First matching type wins by list order. If no match → `general`.

**Overlap handling:**
- `customs` is checked before `market_access` and `regulatory` because customs-specific keywords (`customs`, `declaration`, `HS code`, `جمارك`, `تصريح جمركي`, `كود HS`) are more specific than generic regulatory or market access keywords.
- `market_access` is checked before `regulatory` because duty/requirement keywords indicate a more specific intent than broad regulatory keywords.
- `regulatory` is checked before `trade_statistics` because regulation/law/tariff keywords are more specific than broad trade keywords.
- Example: "export tariff regulation" → matches `market_access` first (keyword: "tariff"), not `regulatory` or `trade_statistics`.

---

## 3. Provider Selection / Routing

### 3.1 Routing Table

| Query Type | Primary Providers | Secondary Providers | Rationale |
|------------|-------------------|---------------------|-----------|
| `agrifood` | FAOSTAT | UN Comtrade, TradeData | Agrifood specialist first; trade stats supplementary only |
| `customs` | ZATCA, Moaah | GCC-Stat | KSA/Egypt customs data first; GCC fallback |
| `regulatory` | Moaah | ZATCA, GCC-Stat | Egypt-focused regulations first |
| `market_access` | Moaah | ZATCA, GCC-Stat, TradeData | Egypt market access first; regional and commercial fallback |
| `trade_statistics` | UN Comtrade, TradeData | GCC-Stat, FAOSTAT | Official global stats and commercial data first; regional and agrifood supplementary |
| `rules_of_origin` | GCC-Stat | TradeData | GCC origin aggregates first; trade data supplementary |
| `general` | All registered | — | No preference — query all |

### 3.2 Routing Rules

1. **Primary providers** are queried first; results are included immediately.
2. **Secondary providers** are queried only if primary results count < `KNOWLEDGE_ORCHESTRATION_MIN_PRIMARY_RESULTS` (default: 3).
3. If query type is `general`, all providers are queried.
4. Providers with `confidence: None` or empty results are skipped in ranking but still counted toward deduplication.
5. When `sources` filter is provided in the query, only providers whose `source_id` is in `sources` are queried; routing table is bypassed.

### 3.3 Provider Metadata Requirements

Each provider's `get_sources()` may optionally include:

```python
{
    "id": str,              # Required — existing
    "name": str,            # Required — existing
    "type": str,            # Required — existing
    "authority_level": str, # Optional — "official" | "commercial" | "aggregated" (default: "aggregated")
    "coverage": [str],      # Optional — list of query types (default: ["general"])
    "version": str,         # Required — existing
    "updated_at": str,      # Required — existing
}
```

**Note:** Existing providers already return `id`, `name`, `type`. `authority_level` and `coverage` are new optional fields; absence defaults to safe values. This preserves backward compatibility.

---

## 4. Result Ranking

### 4.1 Composite Score Formula

```
composite_score = (provider_confidence × 0.4)
                + (authority_weight × 0.3)
                + (recency_weight × 0.2)
                + (relevance_weight × 0.1)
```

Where:
- **provider_confidence**: `result["confidence"]` (0.0–1.0) from the provider
- **authority_weight**: `1.0` for `"official"`, `0.7` for `"commercial"`, `0.5` for `"aggregated"`
- **recency_weight**:
  - `1.0` if `effective_date` within last 1 year
  - `0.8` if within last 3 years
  - `0.5` if older than 3 years or missing
- **relevance_weight**:
  - `1.0` if provider is primary for query type
  - `0.7` if provider is secondary for query type
  - `0.5` if query type is `general`

### 4.2 Ranking Behavior

- Results are sorted by `composite_score` descending
- Top `KNOWLEDGE_ORCHESTRATION_MAX_RESULTS` (default: 10) are retained
- Ties broken by: `effective_date` descending, then `source_id` alphabetically

---

## 5. Deduplication

### 5.1 Deduplication Key

```
dedup_key = sha1(
    content[:100].lower().strip() + "|" +
    (effective_date or "")
)
```

### 5.2 Deduplication Rules

1. **Same content[:100] + same effective_date** → duplicate group.
2. Within each duplicate group, if all results come from the **same source** → exact duplicate → keep highest `composite_score`.
3. Within each duplicate group, if results come from **different sources** → cross-source duplicate → keep highest `authority_weight` (`official > commercial > aggregated`). If authority is equal, keep highest `composite_score`.
4. **Different effective_date** → NOT a duplicate — both retained for conflict resolution in Section 6.
5. Deduplication runs **after** ranking, before conflict resolution.
6. Cross-provider dedup is the default behavior because the key no longer includes `source_id`.

### 5.3 Configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED` | `True` | Enable/disable deduplication |
| `KNOWLEDGE_ORCHESTRATION_DEDUP_KEY_FIELDS` | `["content", "effective_date"]` | Fields used for dedup key. Note: `source_id` is intentionally excluded to enable cross-provider dedup. |

---

## 6. Conflict Resolution

### 6.1 Conflict Detection

A conflict exists when:
- Two or more results share the same `content[:100]` normalized hash (same subject)
- But have **different** `effective_date` or **different** factual values in `metadata`

### 6.2 Resolution Strategy: "Latest Official Wins"

| Scenario | Resolution |
|----------|-----------|
| Same source, different dates | Keep latest `effective_date` |
| Different sources, same date | Keep highest `authority_weight` (`official > commercial > aggregated`) |
| Different sources, different dates | Keep **latest date** if authority difference ≤ 1 level; otherwise keep higher authority |
| Equal authority, equal date | Keep both — flag as `conflict: true` |
| No `effective_date` on either | Keep both — flag as `conflict: true` |

### 6.3 Conflict Metadata

Conflicting results that are retained (not merged) are flagged:
```python
result["metadata"]["conflict"] = True
result["metadata"]["conflict_with"] = [other_source_id_1, other_source_id_2]
```

---

## 7. Knowledge Synthesis (MVP — List Mode Only)

### 7.1 Synthesis Modes

| Mode | Behavior | When Used |
|------|----------|-----------|
| `list` | Return ranked, deduplicated, conflict-resolved list | Default and only mode in MVP |

**Note:** LLM-enhanced summary mode is **deferred to post-MVP**. The `synthesize` parameter is not exposed in the MVP orchestrator API.

### 7.2 Output Shape

```python
{
    "results": [
        {
            "id": str,
            "content": str,
            "source_id": str,
            "confidence": float,
            "composite_score": float,
            "metadata": {
                "effective_date": str | None,
                "source_authority": str,
                "authority_level": str,
                "record_hash": str,
                "conflict": bool,
                "conflict_with": list[str] | None,
                # ... existing metadata fields from providers
            }
        }
    ],
    "confidence": float | None,  # average of result confidences
    "sources": [str],            # contributing source IDs
    "orchestration": {
        "query_type": str,
        "total_candidates": int,
        "after_dedup": int,
        "after_conflict_resolution": int,
        "providers_queried": [str],
        "orchestrated_at": str,  # ISO-8601 UTC
    }
}
```

---

## 8. Integration Points

### 8.1 New Component: `KnowledgeOrchestrator`

**Location:** `backend/app/agent/knowledge/orchestrator.py` (new file)  
**Boundary:** Wraps `KnowledgeProviderRegistry`; does **not** modify `KnowledgeProvider`, `KnowledgeProviderRegistry`, or DEM core.

**Public API:**
```python
class KnowledgeOrchestrator:
    def __init__(self, registry: KnowledgeProviderRegistry, config: Settings) -> None

    async def orchestrate(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        sources: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Execute full orchestration pipeline: classify → route → query → rank → dedup → resolve conflicts."""
```

**Return shape:** As defined in Section 7.2.

### 8.2 Integration Point: `ReasoningEngine._query_knowledge()`

**File:** `backend/app/agent/decision_engine/engine.py`  
**Change:** Replace body of `_query_knowledge()` (lines 336–379) with orchestrator call.

**After:**
```python
async def _query_knowledge(self, intent: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
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
    return result.get("results", [])
```

**Legacy fallback:** `_query_knowledge_legacy()` is the exact current implementation extracted to a separate method. Its behavior is byte-for-byte equivalent to the current code at lines 336–379 of `engine.py`. It exists solely for fallback when the orchestrator is not attached.

### 8.3 Orchestration Metadata in Decision Context

`orchestration` metadata is persisted into `Decision.context["knowledge_orchestration"]` so that downstream consumers (reasoning text builder, audit, frontend) can access orchestration details without changing the `Decision` schema.

```python
# In ReasoningEngine.reason(), after _query_knowledge():
knowledge = await self._query_knowledge(intent, parameters)

# Preserve orchestration metadata if available
orchestration_meta = getattr(self, "_last_orchestration_meta", None)
if orchestration_meta:
    request_context["knowledge_orchestration"] = orchestration_meta
```

**Note:** `_last_orchestration_meta` is set by the orchestrator wrapper; it is not part of the orchestrator's return value contract. It is an implementation detail of the integration point.

### 8.4 Bootstrap: Wiring in `main.py`

**File:** `backend/main.py`  
**Change:** After `knowledge_provider_registry` creation, instantiate `KnowledgeOrchestrator` and attach to `ReasoningEngine`.

```python
from app.agent.knowledge.orchestrator import KnowledgeOrchestrator

# In lifespan(), after registry population:
orchestrator = KnowledgeOrchestrator(
    registry=knowledge_provider_registry,
    config=settings,
)
reasoning_engine = ReasoningEngine(
    knowledge_provider_registry=knowledge_provider_registry,
    memory_provider=memory_provider,
    llm_registry=llm_registry,
    approval_gate=ApprovalGate(),
)
reasoning_engine._knowledge_orchestrator = orchestrator
```

### 8.5 Configuration (`config.py`)

Add new section after existing provider sections:

```python
# ========== Knowledge Orchestration / Fusion Layer ==========
KNOWLEDGE_ORCHESTRATION_ENABLED: bool = True
KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED: bool = True
KNOWLEDGE_ORCHESTRATION_MIN_PRIMARY_RESULTS: int = 3
KNOWLEDGE_ORCHESTRATION_MAX_RESULTS: int = 10
KNOWLEDGE_ORCHESTRATION_CONFLICT_STRATEGY: str = "latest_official_wins"
```

---

## 9. Integration Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         User Request (DEM Router)                        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        ReasoningEngine.reason()                          │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  _query_knowledge(intent, parameters)                               │  │
│  │                                                                       │  │
│  │  1. Retrieve _knowledge_orchestrator if attached                      │  │
│  │  2. If attached: call orchestrator.orchestrate(...)                  │  │
│  │  3. If not attached: call _query_knowledge_legacy(...)               │  │
│  │  4. Return results list                                               │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     KnowledgeOrchestrator (new)                          │
│                                                                           │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  1. Classify│─▶│ 2. Route     │─▶│ 3. Query     │─▶│ 4. Rank      │  │
│  │  Query      │  │ Providers    │  │ Providers    │  │ Results      │  │
│  └─────────────┘  └──────────────┘  └──────────────┘  └──────┬───────┘  │
│                                                              │          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │          │
│  │ 7. Return   │◀─│ 6. Resolve   │◀─│ 5. Dedup      │◀──────┘          │
│  │ Orchestrated│  │ Conflicts    │  │              │                    │
│  │ Results     │  └──────────────┘  └──────────────┘                    │
│  └─────────────┘                                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    ▼                                 ▼
      ┌──────────────────────────┐      ┌──────────────────────────┐
      │ KnowledgeProviderRegistry│      │   LLM Registry (optional)│
      │  .list_providers()       │      │   — NOT used in MVP      │
      │  .query(source_id, ...)  │      └──────────────────────────┘
      └──────────┬───────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
 ┌───────┐  ┌──────────┐  ┌──────────┐
 │ Moaah │  │ TradeData│  │  ZATCA   │ ...
 └───────┘  └──────────┘  └──────────┘
```

---

## 10. Test Plan

### 10.1 Unit Tests

| Test File | Coverage | Count |
|-----------|----------|-------|
| `tests/agent/knowledge/test_orchestrator_classification.py` | Query type classification accuracy, deterministic order, overlap handling | 15 |
| `tests/agent/knowledge/test_orchestrator_routing.py` | Provider routing logic, primary/secondary fallback, `sources` filter bypass | 12 |
| `tests/agent/knowledge/test_orchestrator_ranking.py` | Composite score calculation, tie-breaking | 10 |
| `tests/agent/knowledge/test_orchestrator_dedup.py` | Deduplication key generation, duplicate removal within/across sources | 10 |
| `tests/agent/knowledge/test_orchestrator_conflict.py` | Conflict detection, resolution strategies | 10 |
| `tests/agent/knowledge/test_orchestrator_output.py` | Output shape, orchestration metadata, backward-compatible fallback | 8 |

**Total new tests:** ~65 unit tests

### 10.2 Integration Tests

| Test File | Coverage | Count |
|-----------|----------|-------|
| `tests/agent/knowledge/test_orchestrator_integration.py` | End-to-end with mocked registry and providers | 10 |
| `tests/agent/test_reasoning_engine_orchestrator.py` | `_query_knowledge()` integration with orchestrator, legacy fallback, context metadata propagation | 8 |

**Total new integration tests:** ~18

### 10.3 Regression Tests

- All existing `test_uncomtrade_*` tests must pass (no provider changes)
- All existing `test_faostat_*` tests must pass
- All existing `test_tradedata_*`, `test_mooadapter_*`, `test_gccstat_*`, `test_zatca_*` tests must pass
- All existing `test_reasoning_engine*` tests must pass (fallback behavior preserved)

### 10.4 Verification Criteria

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

---

## 11. Provider Metadata Contract (New Optional Fields)

### 11.1 `get_sources()` Extension

Each provider's `get_sources()` may optionally include:

```python
{
    "id": str,              # Required — existing
    "name": str,            # Required — existing
    "type": str,            # Required — existing
    "authority_level": str, # Optional — "official" | "commercial" | "aggregated" (default: "aggregated")
    "coverage": [str],      # Optional — list of query types (default: ["general"])
    "version": str,         # Required — existing
    "updated_at": str,      # Required — existing
}
```

### 11.2 Default Behavior

Providers that do not specify `authority_level` or `coverage` default to:
- `authority_level = "aggregated"`
- `coverage = ["general"]`

This ensures **backward compatibility** — existing providers work without modification.

### 11.3 Current Provider Defaults

| Provider | Default `authority_level` | Default `coverage` |
|----------|---------------------------|--------------------|
| Moaah | `aggregated` | `["general"]` |
| TradeData | `aggregated` | `["general"]` |
| ZATCA | `aggregated` | `["general"]` |
| GCC-Stat | `aggregated` | `["general"]` |
| FAOSTAT | `aggregated` | `["general"]` |
| UN Comtrade | `aggregated` | `["general"]` |

**Note:** These defaults mean all current providers are treated equally unless `authority_level` or `coverage` are explicitly added to their `get_sources()` implementations during a future maintenance cycle. The orchestration layer functions correctly with these defaults.

---

## 12. Out of Scope

| Item | Reason |
|------|--------|
| New Knowledge Families | Constraint: do not expand families |
| New Provider implementation | Constraint: no new providers |
| DEM core modifications beyond `_query_knowledge()` | Constraint: preserve architecture |
| Knowledge Graph schema changes | Constraint: no schema changes |
| Database migrations | Not required — orchestration is computed per-query |
| LLM summary generation | Deferred to post-MVP |
| Caching layer | Future enhancement |
| Freshness/refresh scheduling | Future enhancement |
| Avatar/Renderer integration | Out of scope per AVATAR_CONTRACT.md |
| Goal/Plan reasoning layers | Deferred per ENGINEERING_MEMORY.md |
| Multi-agent coordination | Future work |
| `logistics` as independent query type | No viable provider; use `general` instead |

---

## 13. Future Implementation Path

After planning approval, the implementation sequence would be:

1. **Create `orchestrator.py`** — `KnowledgeOrchestrator` class with classification, routing, ranking, dedup, conflict resolution
2. **Add config settings** — `config.py` new section
3. **Extract `_query_knowledge_legacy()`** — Extract current lines 336–379 of `engine.py` to a separate method
4. **Modify `_query_knowledge()`** — Replace body with orchestrator call, preserve legacy fallback
5. **Wire in `main.py`** — Instantiate orchestrator and attach to `ReasoningEngine`
6. **Write unit tests** — ~65 tests covering all orchestration logic
7. **Write integration tests** — ~18 tests covering end-to-end and ReasoningEngine integration
8. **Run regression tests** — Verify zero regressions in existing test suites
9. **G4/G5 Verification** — Test plan execution and closure

**No Work Package creation, no Gate initiation, no code changes until explicit authorization.**

---

## 14. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Ranking algorithm produces unexpected ordering | Low | Medium | Extensive unit tests with known inputs/outputs; configurable weights |
| Deduplication removes valid distinct results | Low | Medium | Conservative dedup key (content[:100] + source_id + date); conflict flagging |
| Performance degradation with 6 providers | Low | Low | Secondary providers only queried if primary insufficient; limit parameter |
| Provider metadata missing new fields | Medium | Low | Safe defaults; no hard dependency on new fields |
| Classification overlap causes unexpected routing | Low | Low | Deterministic priority order; unit tests cover overlap cases |

---

## 15. Decisions and Resolutions

| Decision | Resolution | Rationale |
|----------|-----------|-----------|
| Classification method | Deterministic keyword matching with fixed priority order | No NLP dependency; consistent with existing `_map_intent_to_candidates()`; deterministic overlap handling |
| Ranking formula | Weighted composite: confidence 40%, authority 30%, recency 20%, relevance 10% | Balances provider self-assessment with external authority and freshness |
| Deduplication key | `sha1(content[:100] + "|" + effective_date)` | Cross-provider dedup enabled; source-aware resolution happens within duplicate groups, not in the key |
| Conflict strategy | "Latest official wins" | Prefers recency within official sources; deterministic |
| Synthesis | List mode only in MVP; LLM summary deferred | List mode always works; summary is post-MVP enhancement |
| Integration point | Replace `_query_knowledge()` body only; attach orchestrator via attribute | Minimal blast radius; preserves all DEM core contracts |
| Config approach | New `KNOWLEDGE_ORCHESTRATION_*` settings | Isolated from existing provider configs; feature-flagged |
| Legacy fallback | Extract current implementation to `_query_knowledge_legacy()` | Byte-for-byte equivalent; safe fallback if orchestrator not attached |
| Orchestration metadata | Persisted in `Decision.context["knowledge_orchestration"]` | No schema changes; accessible to downstream consumers |
| `logistics` query type | Removed; logistics intent falls to `general` | No viable provider; avoids misleading routing |
| `market_access` routing | Moaah primary; ZATCA/GCC-Stat/TradeData secondary | Single primary avoids unnecessary provider fan-out |
| Classification overlap | Fixed priority order: agrifood → customs → regulatory → market_access → trade_statistics → rules_of_origin | Most specific keywords first; deterministic |

---

## 16. Open Items for Implementation Agent

| # | Item | Type | Resolution Path |
|---|------|------|-----------------|
| 1 | **Moaah `market_access` coverage** — confirm Moaah provides duty/tariff data for markets beyond Egypt | Validation Item | Verify Moaah API response fields; if Egypt-only, adjust routing to ZATCA primary for non-Egypt contexts |
| 2 | **UN Comtrade `effective_date` format** — confirm date format consistency for ranking and dedup | Validation Item | Verify UN Comtrade preview API returns parseable dates; if inconsistent, add date parsing fallback |
| 3 | **TradeData confidence values** — confirm 0.50–0.95 range is compatible with composite score formula | Validation Item | Verify composite_score stays within 0.0–1.0 bounds with current provider confidence ranges |
| 4 | **`content[:100]` slice length for dedup** — confirm 100 chars is sufficient for stable dedup keys | Engineering Decision | If 100 chars causes false negatives, increase to 200; if too long, decrease to 50 |

**Note:** No Project Owner decisions remain pending. All governance decisions are resolved.

---

## 17. Validation Items Summary

The following items from the previous review remain as validation checks for the implementation agent:

| # | Validation Item | Why It Matters | Status |
|---|-----------------|----------------|--------|
| 1 | Moaah `market_access` coverage beyond Egypt | If Moaah is Egypt-only, routing non-Egypt market_access queries to Moaah as primary returns irrelevant results | **Pending implementation-time verification** |
| 2 | UN Comtrade `effective_date` format | Ranking and dedup depend on parseable, consistent dates | **Pending implementation-time verification** |
| 3 | TradeData confidence range compatibility | Composite score must remain within 0.0–1.0 with all provider confidence inputs | **Pending implementation-time verification** |

**GCC-Stat logistics validation** was removed from scope because `logistics` is no longer an independent query type. No validation required.

---

*Plan Status: Complete — Ready for Governance Adoption — Next Step: Detailed Implementation Plan (not code execution)*
