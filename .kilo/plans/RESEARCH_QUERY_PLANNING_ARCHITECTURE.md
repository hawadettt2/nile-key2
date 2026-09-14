# DEM Research Query Planning Architecture

**Status:** Approved — Implementation Baseline  
**Capability:** External Research (WP-34)  
**Branch:** `main`

## 1. Purpose

Record the repository-level architecture for transforming a complex Business Intent into **specialized Research Queries** before external retrieval.

Governing principle: **Knowledge Coverage > Provider Count**.

This closes the gap between a broad business request and the distinct knowledge questions needed for effective multi-source research. It does not introduce a new provider, a second reasoning engine, a BI engine, or a new decision authority.

## 2. Architectural Decision

Introduce a dedicated External Research component:

```text
ResearchQueryPlanner
        ↓
ResearchQueryPlan
        ↓
Specialized ResearchQuery(ies)
        ↓
QueryEnhancer (existing, downstream)
        ↓
Source Discovery / Source Registry
        ↓
Retrieval
        ↓
Processing / Evidence / Provenance
        ↓
Research Result
        ↓
Reasoning / downstream consumers
```

`ResearchQueryPlanner` operates before retrieval and remains entirely inside the External Research boundary.

## 3. Responsibilities

### MUST

- consume existing research intent/context and reuse normalized information where possible;
- select relevant Knowledge Dimensions for the specific request;
- decompose a broad intent into distinct, specialized research queries when justified;
- preserve known facts, context, and scope;
- remain deterministic;
- preserve query-level traceability;
- degrade gracefully to one query when decomposition is not justified.

### MUST NOT

- make business decisions or recommendations;
- synthesize Business Intelligence;
- execute missions/tasks/tools;
- call providers or retrieve data;
- verify evidence;
- become a second `ReasoningEngine`;
- use an LLM as source of truth;
- replace Research Orchestration, Source Discovery, or QueryEnhancer;
- modify Goal/Plan/Mission/Task/Execution architecture;
- introduce Knowledge Graph, Multi-Agent, Avatar, or BI work.

## 4. Contracts

The implementation may follow existing repository naming conventions, but these semantics are mandatory.

### `ResearchQuery`

```python
ResearchQuery(
    query_id: str,
    dimension: str,
    purpose: str,
    query: str,
    source_preferences: Optional[List[str]],
    context: Dict[str, Any],
    scope: Optional[Dict[str, Any]],
)
```

`query_id` must support traceability. `dimension` identifies the knowledge need. `purpose` explains why the query exists. `query` must be specialized rather than a blind copy of the goal. `source_preferences` are optional routing metadata only.

### `ResearchQueryPlan`

```python
ResearchQueryPlan(
    intent_profile=...,
    queries=[ResearchQuery(...), ...],
)
```

The plan is deterministic and serializable through repository-native contracts.

## 5. Knowledge Dimensions

Use the existing validated portfolio vocabulary:

1. `trade_intelligence`
2. `market_opportunity`
3. `market_access`
4. `regulatory_sps_tbt`
5. `rules_of_origin`
6. `agrifood_intelligence`
7. `logistics_market_execution`

These are **knowledge needs, not provider ownership**.

Do **not** force all seven dimensions onto every request. Do **not** impose universal minimums such as two queries or two sources. One justified query is valid. Multiple queries are justified only when they represent distinct relevant knowledge needs.

Examples of dimension meaning:

- trade flows / historical exports → `trade_intelligence`
- demand / growth / market attractiveness → `market_opportunity`
- tariffs / duties / entry procedures → `market_access`
- SPS/TBT / standards / MRLs / conformity → `regulatory_sps_tbt`
- FTA origin criteria / documentation → `rules_of_origin`
- agricultural/food-specific market intelligence → `agrifood_intelligence`
- shipping / route / logistics execution → `logistics_market_execution`

Adjacent family boundaries remain those already established by the External Knowledge Portfolio.

## 6. Specialized Query Rules

For a broad intent such as:

```text
اريد تصدير الخضروات والفاكهة المصرية الى الاردن
```

the planner may derive, where justified, distinct research needs such as trade flows, market opportunity, agrifood conditions, market access, SPS/TBT requirements, and logistics. This is an architectural example, **not a fixed mandatory list**.

The planner must never invent missing values such as year, HS code, tariff, indicator, price, score, quantity, or provider-specific identifiers. Missing information remains explicit/unresolved.

## 7. Source Selection Boundary

The planner does not own provider selection.

```text
ResearchQuery
    ↓
Source Discovery / Source Registry
    ↓
Available relevant sources
```

Do not hardcode mappings such as `trade_intelligence → UN Comtrade` or `agrifood_intelligence → FAOSTAT`. A provider may contribute to multiple dimensions. Source selection remains with the existing discovery/registry layer.

## 8. Intent Extraction Boundary

Existing Reasoning-layer research parameter extraction/normalization must remain coherent.

Preferred relationship:

```text
Existing normalized intent/context
        ↓
ResearchQueryPlanner
```

Do not create competing independent parsers for the same business intent. If extraction is moved, refactor it once rather than duplicating it.

## 9. QueryEnhancer Boundary

`QueryEnhancer` remains downstream and separate:

```text
ResearchQueryPlanner
        ↓
QueryEnhancer (existing trigger only)
        ↓
Provider Retrieval
```

It retains its current deterministic provider-specific enrichment role, limited retry behavior, and no-invention rules. Research Query Planning must not absorb this responsibility.

## 10. Traceability

Preserve query provenance through the research lifecycle as far as the existing contracts allow:

```text
ResearchQueryPlan
   └── query_id
       └── dimension
           └── retrieval / processing metadata
               └── evidence / finding provenance
```

Implement this with minimal compatible metadata extensions; do not redesign `ResearchResult` wholesale.

## 11. Determinism / No-Invention

Equivalent intent + context + scope must produce an equivalent query plan.

Allowed: reuse explicit facts, existing normalization, unresolved parameters, deterministic dimension selection.

Forbidden: fabricated dates, identifiers, metrics, tariffs, prices, scores, codes, or unsupported business facts.

## 12. Backward Compatibility

- Existing simple queries continue to work.
- One query remains valid where only one dimension is justified.
- No unnecessary fan-out.
- Failure to decompose does not block research; single-query fallback remains valid.
- Existing Source Discovery, Retrieval, and QueryEnhancer behavior remains compatible.

## 13. Scope

### In scope

- `ResearchQueryPlanner`
- `ResearchQueryPlan`
- `ResearchQuery`
- Research Planning integration
- Knowledge-dimension selection
- Specialized query generation
- query-level traceability
- minimal retrieval/provenance metadata needed for traceability
- focused tests and relevant regression

### Out of scope

- provider implementation/expansion;
- Knowledge Ingestion;
- Knowledge Graph;
- Multi-Agent;
- LLM introduction;
- BI / Avatar changes;
- Goal/Plan/Mission/Task/Execution lifecycle changes;
- broad `run_dem_mission()` refactor;
- replacing ReasoningEngine, Source Discovery, or QueryEnhancer;
- final business decisions/recommendations.

## 14. Acceptance Criteria

1. Research Planning produces structured specialized queries when distinct knowledge needs exist.
2. Query selection is driven by relevant Knowledge Coverage, not provider/query count.
3. Queries are genuinely specialized and not duplicate copies of the original goal.
4. One query remains valid for simple intent.
5. No unsupported parameter is invented.
6. Output is deterministic.
7. Source selection boundary is preserved; no fixed dimension→provider ownership is introduced.
8. QueryEnhancer remains downstream and unchanged in responsibility.
9. `query_id` and dimension remain traceable into retrieval/provenance where supported.
10. Existing simple research behavior remains compatible.
11. No new decision/BI/execution/Knowledge Graph/Multi-Agent/LLM authority is introduced.
12. Tests and regression provide evidence; passing tests alone does not override an architectural violation.

## 15. Relationship to Existing Architecture

This document extends the existing External Research design rather than replacing it:

- **WP-34** already defines Query/Research Planning as the stage for sub-queries, source-selection strategy, and retrieval parameters.
- **External Knowledge Portfolio** establishes the seven-family model and the principle **Knowledge Coverage > Provider Count**.
- **Source Discovery / Source Registry** remain responsible for source discovery/selection.
- **Retrieval Orchestrator** remains responsible for retrieval.
- **QueryEnhancer** remains provider-specific downstream enrichment after a successful empty retrieval when its trigger applies.
- **Reasoning** consumes Research Results and is not replaced by the planner.

## 16. Implementation Baseline

Any implementation claiming to close this architectural gap must be reviewed against this document. A test-passing implementation does not satisfy the architecture if it merely returns the original goal, hardcodes provider ownership, invents parameters, merges QueryEnhancer into planning, bypasses Source Discovery, or creates a second reasoning/decision authority.
