# DEM — Business Intelligence Synthesis — Final Implementation Plan

**Status:** FINAL PLAN — IMPLEMENTATION READY  
**Target implementation mode:** Code  
**Branch:** `main`

## 1. Architectural Decision

Implement **Evidence-Grounded Business Intelligence Synthesis** as a deterministic v1 downstream capability.

BI is **not** a second ReasoningEngine/Decision Engine, Planning, Autonomy, execution, approval, mission orchestration, LLM source of truth, WP-34 replacement, ResponseBuilder replacement, Avatar implementation, or frontend business-logic layer.

Placement:

`Intent → Goal/Plan → Decision/Reasoning → Mission/Task → Execution → Outcome → Business Intelligence → ResponseBuilder/IntentContent`

HTTP and Avatar share the same BI contract/synthesizer, but are not forced into identical runtime lifecycles. No broad lifecycle refactor is part of this package.

## 2. BI Input Contract

Use a transport-neutral input contract:

```python
BusinessIntelligenceInput(
    goal,
    decision,
    mission_result,
    execution_outcome,
    research_result,
)
```

The fields are mostly optional. The BI layer must not directly read repository/application state.

## 3. Evidence Authority

Evidence authority is ordered:

1. WP-34 `ResearchResult.findings[].evidence[]`.
2. Explicit typed BI-compatible evidence carriers.
3. Explicit structured analysis carriers.
4. Mission execution context/raw result only as lower-authority context.

Raw `mission.result` never automatically becomes authoritative evidence.

### Evidence model separation

Do not conflate WP-34 `EvidenceItem` with the separate `Evidence` model.

WP-34 `EvidenceItem` is the primary research-to-BI carrier:

- `source_id: str`
- `source_url: Optional[str]`
- `retrieval_timestamp: str`
- `content_excerpt: str`
- `metadata: Dict[str, Any]`

## 4. EvidenceReference

```python
EvidenceReference(
    source_id: str,
    source_url: Optional[str],
    retrieval_timestamp: datetime,
    content_excerpt: str,
    confidence: Optional[float],
    limitations: List[str],
    provenance: Optional[Dict[str, Any]],
)
```

`content_excerpt` maps from `EvidenceItem.content_excerpt`. Confidence remains numeric (`Optional[float]`). Do not use string confidence labels. Provenance is preserved only when actually supplied.

## 5. Typed BI Contract

Implement the following typed contracts:

```python
BusinessFinding(
    topic: str,
    content: str,
    evidence: List[EvidenceReference],
    confidence: Optional[float],
    limitations: List[str],
)

BusinessEntity(
    name: str,
    entity_type: str,
    attributes: Dict[str, Any],
    evidence: List[EvidenceReference],
)

ComparisonResult(
    option: str,
    criterion: str,
    value: Any,
    evidence: List[EvidenceReference],
)

BusinessComparison(
    options: List[str],
    criteria: List[str],
    results: List[ComparisonResult],
    limitations: List[str],
)

RankingEntry(
    rank: int,
    candidate: str,
    criteria_scores: Dict[str, Any],
    total_score: Optional[float],
    evidence: List[EvidenceReference],
    explanation: Optional[str],
)

BusinessRanking(
    criteria: List[str],
    entries: List[RankingEntry],
    scoring_method: Optional[str],
    limitations: List[str],
)

Opportunity(
    description: str,
    evidence: List[EvidenceReference],
    confidence: Optional[float],
    limitations: List[str],
)

Risk(
    description: str,
    evidence: List[EvidenceReference],
    severity: Optional[str],
    mitigation: Optional[str],
    limitations: List[str],
)

Recommendation(
    action: str,
    type: str,
    rationale: str,
    evidence: List[EvidenceReference],
    confidence: Optional[float],
    limitations: List[str],
)

Limitation(
    what_is_missing: str,
    why_it_matters: str,
    what_evidence_is_needed: str,
)

BusinessIntelligenceAnswer(
    goal,
    executive_summary,
    key_findings,
    entities,
    comparisons,
    rankings,
    opportunities,
    risks,
    recommendations,
    confidence: Optional[float],
    limitations,
    evidence,
    sources,
    provenance,
)
```

## 6. Ranking Safety

Rank only when candidate set, criteria, candidate/criterion values, criterion evidence, and an existing valid scoring basis are explicitly supplied.

Never invent candidates, criteria, weights, scores, ranking order, or scoring formulas. Unsupported ranking returns an empty ranking plus an explicit limitation.

## 7. Recommendation Safety

Allowed types:

- `business_recommendation`
- `next_evidence_requirement`

A `business_recommendation` must have evidence and is informational only. It cannot mutate Decision/Plan, execute a Mission, or bypass Approval/Autonomy.

A `next_evidence_requirement` may have empty evidence, but must explain what is missing, why it matters, and what evidence is needed.

Opportunities and risks are evidence-derived only. No invented business claims.

## 8. Overall Confidence

No invented aggregation formula. If no defensible aggregate confidence is supplied, leave the final confidence as `None`.

## 9. Synthesis Algorithm

v1 is deterministic and evidence-grounded:

1. Normalize inputs.
2. Build the evidence set using the authority order above.
3. Normalize supported findings.
4. Produce the executive summary.
5. Normalize only explicitly supplied structured entities/comparisons/rankings/opportunities/risks/recommendations with sufficient support.
6. Emit limitations when evidence or structured support is insufficient.

Use an existing structured summary when available; otherwise use only deterministic scope/findings statements. Never add unsupported facts, numbers, market claims, or conclusions.

## 10. LLM Boundary

No new LLM call in v1. WP-34 may use LLM for processing/summarization/structuring, but evidence remains the source of truth. BI must not become a hidden LLM Decision Engine, ranking engine, or scoring engine. Any future semantic LLM synthesis requires a separate governed work package.

## 11. WP-34 Boundary

`ResearchPresentResultTool` remains an adapter/presentation helper, not the BI engine.

BI owns an explicit evidence adapter. Do not extract or modify `ResearchPresentResultTool` unless actual duplication is proven and a strictly behavior-preserving helper is necessary. Do not reopen or change WP-34 semantics.

## 12. ResponseBuilder Boundary

Extend `ResponseBuilder` minimally:

```python
build(..., business_answer: Optional[BusinessIntelligenceAnswer] = None)
```

When supplied, pass it through as structured content, e.g.:

```python
content["business_answer"] = business_answer.model_dump(mode="json")
```

ResponseBuilder remains deterministic normalization/mapping. It must not perform BI analysis, research calls, reasoning calls, LLM calls, or invented business content.

## 13. Mission/Avatar/Frontend Boundaries

Raw `mission.result` remains the execution result. `business_answer` is additional structured output in `IntentContent`.

Avatar contract remains unchanged; no renderer/audio/UI/animation is introduced into DEM BI.

Do not redesign the frontend. Existing structured-result presentation remains presentation-only. Any tiny presentation adjustment must contain no business logic.

## 14. Failure Semantics

Distinguish:

1. valid BI result;
2. valid insufficient-evidence BI result;
3. BI implementation failure.

Do not use broad exception swallowing such as `except Exception: business_answer = None`. Real BI implementation defects must remain observable and testable without corrupting the established mission outcome lifecycle.

## 15. Non-Research Inputs

BI is not research-only. It may consume explicitly supported structured mission result/outcome carriers. It must not infer facts from arbitrary raw output.

## 16. Package Structure

```text
backend/app/agent/business_intelligence/
  __init__.py
  schema.py
  evidence.py
  synthesizer.py
```

- `schema.py`: typed BI contracts.
- `evidence.py`: WP-34 and other explicit typed evidence adapters.
- `synthesizer.py`: deterministic evidence-grounded synthesis.

## 17. Integration Strategy

Integrate minimally at the actual existing post-outcome boundary in:

```text
backend/app/routers/digital_export_manager.py
backend/app/routers/avatar_ws.py
```

Use the shared BI component in both paths after existing execution/outcome processing and before ResponseBuilder/IntentContent emission.

**Critical restriction:** do not extract `run_dem_mission()`, do not create a broad canonical lifecycle refactor, and do not force HTTP and Avatar to become identical runtimes. This is a downstream BI insertion, not a lifecycle redesign.

## 18. Closed Core Packages

Do not change the behavior or contracts of Goal/Plan, ReasoningEngine/Decision, Replanning, Mission/Task planning, Execution/ToolOrchestrator, Approval/Autonomy, OutcomeEvaluator, OutcomeFeedbackLoop, Memory, WP-34, or closed governance/consolidation documents.

Required compatibility adaptation must be local and behavior-preserving.

## 19. Tests

Unit coverage must include:

- evidence mapping and provenance;
- numeric confidence preservation;
- findings;
- comparisons;
- ranking safety;
- recommendation safety;
- opportunity/risk grounding;
- insufficient evidence;
- failure observability;
- non-research structured inputs;
- `EvidenceItem` vs `Evidence` separation.

Integration/regression coverage must include:

- HTTP BI integration;
- Avatar BI integration;
- BI-contract equivalence between transports;
- ERP success/failure;
- pending approval;
- non-research missions;
- Goal/Plan behavior;
- autonomy/approval behavior;
- outcome-feedback behavior;
- existing ResponseBuilder behavior.

## 20. Architectural Invariants

- BI is downstream of Reasoning/Decision, Execution, and Outcome.
- BI never mutates Decision.
- BI never executes.
- BI is evidence-grounded.
- v1 is deterministic.
- No invented scoring.
- No invented confidence aggregation.
- WP-34 remains unchanged.
- ResponseBuilder remains normalization only.
- Avatar remains presentation only.
- HTTP and Avatar share BI contract/logic without requiring identical lifecycles.

## 21. Non-Goals

No Knowledge Graph, Multi-Agent architecture, new research providers/sources, autonomous decision making, autonomous execution, new approval/autonomy logic, new goal/plan logic, LLM decision/ranking/scoring, DB migrations, new public API endpoints, Avatar implementation, frontend architecture redesign, or frontend business logic.

## 22. Acceptance Criteria

| ID | Criterion |
|---|---|
| AC-01 | BI is downstream of execution/outcome and upstream of ResponseBuilder/IntentContent. |
| AC-02 | HTTP and Avatar use the same BI synthesizer/contract without identical mission lifecycles. |
| AC-03 | Evidence is traceable to explicit evidence carriers. |
| AC-04 | Evidence confidence remains numeric and compatible with `Optional[float]`. |
| AC-05 | `EvidenceItem` and `Evidence` remain distinct. |
| AC-06 | Typed BI contracts exist for findings, entities, comparisons, rankings, opportunities, risks, recommendations, limitations, and final answer. |
| AC-07 | Rankings require explicit candidates, criteria, values, evidence, and scoring basis. |
| AC-08 | Business recommendations are evidence-grounded and cannot mutate Decision/Plan or execute; next-evidence requirements explain gaps. |
| AC-09 | Insufficient evidence produces a valid explainable BI answer. |
| AC-10 | Decision state is unchanged. |
| AC-11 | BI performs no execution. |
| AC-12 | ResponseBuilder remains a deterministic pass-through/normalization boundary. |
| AC-13 | Avatar contract remains unchanged. |
| AC-14 | WP-34 files/semantics remain unchanged. |
| AC-15 | Valid result, insufficient evidence, and implementation failure are distinguishable. |
| AC-16 | Implementation failures remain observable. |
| AC-17 | Full regression remains green. |
| AC-18 | No database migration is introduced. |

## 23. Implementation Sequence

1. Contract (`schema.py`)
2. Evidence adapter (`evidence.py`)
3. Deterministic synthesizer (`synthesizer.py`)
4. Unit tests
5. Minimal ResponseBuilder integration
6. HTTP integration
7. Avatar integration
8. Integration/regression tests
9. Final forensic verification

## 24. Final Evidence Required

Before completion, record:

- exact files changed;
- final contract;
- evidence mapping/provenance;
- WP-34 untouched;
- ResponseBuilder boundary;
- HTTP/Avatar integration points;
- ranking and recommendation safety;
- insufficient-evidence behavior;
- failure observability;
- Decision unchanged;
- Goal/Plan unchanged;
- Autonomy/Approval unchanged;
- Outcome/Feedback unchanged;
- full tests/regression;
- final `git status`;
- commit hash;
- push result.

## 25. Completion Gate

Complete only when all acceptance criteria pass, regression tests pass, final forensic verification passes, implementation is committed, and the commit is pushed to `origin/main`.

## 26. Execution Authority

This document is the **authoritative frozen implementation plan** for Business Intelligence Synthesis.

The implementation agent must execute this plan as written and must not enter Plan Mode, rewrite this plan, redesign its architecture, or introduce a broad lifecycle refactor.

If a genuine contradiction between this plan and the actual repository code is discovered, stop and report the exact contradiction and source evidence rather than silently redesigning the work package.
