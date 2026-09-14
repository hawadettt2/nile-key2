# DEM — Business Intelligence Synthesis Completion Plan

**Status:** APPROVED PLAN — NOT FOR IMPLEMENTATION YET  
**Mode:** Plan  
**Branch:** `main`  
**Authority:** Repository governance + canonical backend contracts + approved External Research architecture  
**Scope:** Complete the Business Intelligence capability so the Avatar can present an evidence-grounded, execution-ready Executive Business Answer for broad business requests.  
**Implementation owner:** Kilo Code only after explicit execution authorization.  
**Planning owner:** Project/Architecture review.  

---

## 0. Executive Decision

The current repository has a valid end-to-end transport path from business intent through External Research, Evidence, Business Intelligence, ResponseBuilder, IntentContent, and Avatar presentation. The recent frontend work in `b1c1dbe` closes the presentation contract gap, but it does **not** establish that the Business Intelligence layer can produce the breadth of business information expected by an ordinary employee.

The current `BusinessIntelligenceSynthesizer` is intentionally conservative and evidence-grounded, but its implementation is still primarily a Research-Result adapter. It currently produces structured findings and evidence while leaving entities, comparisons, rankings, opportunities, risks, and business recommendations empty in the normal evidence-present path. Its executive summary is also generic rather than a substantive business synthesis.

Therefore a dedicated completion Work Package is required. This plan covers the eleven validated gaps identified during repository review and adds the missing BI synthesis/knowledge-fusion capability itself as an explicit workstream rather than treating it as an accidental side effect of the fixes.

The target is **not** to fabricate a complete answer. The target is to make the Avatar answer as complete as the available authoritative evidence and registered capabilities allow, while explicitly exposing missing evidence and coverage limitations.

Core principle:

> **Business usefulness must increase without weakening evidence authority, determinism, provenance, autonomy boundaries, or existing architectural ownership.**

---

# 1. Governing Architecture and Non-Negotiable Boundaries

## 1.1 Repository authority reviewed

This plan is governed by, and must remain compatible with:

- `PLAN.md` — project constitution / master roadmap and architecture principles.
- `.kilo/plans/WP-34-spec.md` — External Research capability and its lifecycle/boundaries.
- `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md` — Company Knowledge boundary.
- `.kilo/plans/RESEARCH_QUERY_PLANNING_ARCHITECTURE.md` — approved Research Query Planning architecture.
- Existing Business Intelligence schemas/contracts under `backend/app/agent/business_intelligence/`.
- Existing Research schemas/results/providers/orchestrator/retrieval contracts.
- Existing Reasoning/Decision/Outcome contracts.
- Existing Avatar/ResponseBuilder/IntentContent contracts.

WP-34 explicitly separates External Research from final Business Analysis: Research supplies structured, traceable information; downstream capabilities interpret what it means for the business. It also requires source-level success/failure handling, partial-result visibility, multi-source provenance, and evidence traceability. fileciteturn86file0

The Knowledge Ingestion contract explicitly keeps ingestion limited to import/transform/register and keeps Business Analysis, Reasoning, External Research, provenance, evidence verification, and quality scoring outside that capability. This plan therefore must not move BI logic into Knowledge Ingestion. fileciteturn87file0

The approved Research Query Planning architecture establishes seven knowledge dimensions and the rule **Knowledge Coverage > Provider Count**. It explicitly forbids turning query planning into BI, provider execution, a second reasoning engine, or a decision authority. fileciteturn90file0

`PLAN.md` establishes production-grade principles, with correctness, stability, maintainability, scalability, security, and readability taking precedence over speed. It also establishes backend domain models/Pydantic schemas/API contracts as the primary source of truth. fileciteturn88file0

## 1.2 Target architecture

```text
Employee Business Intent
        ↓
Canonical DEM Application Flow
        ↓
Intent / Goal / Decision Context
        ↓
ResearchQueryPlanner
        ↓
Specialized Research Queries
        ↓
External Research + Knowledge Providers
        ↓
Evidence + Provenance + Coverage Status
        ↓
Business Fact Normalization / Fusion
        ↓
BusinessIntelligenceSynthesizer
        ↓
BusinessIntelligenceAnswer
        ↓
ResponseBuilder
        ↓
IntentContent
        ↓
Avatar Parser / ExecutiveResultCard
        ↓
Employee
```

The missing capability is **Business Fact Normalization / Fusion + substantive BI synthesis**, not another reasoning engine and not another research orchestrator.

## 1.3 Hard boundaries

The implementation MUST NOT:

- create a second `ReasoningEngine`;
- make BI responsible for Goal/Plan/Mission/Task creation;
- execute tools/providers from BI;
- bypass approval/autonomy policy;
- mutate memory or knowledge;
- replace `ResponseBuilder`;
- make Avatar responsible for business analysis;
- introduce Knowledge Graph work;
- introduce Multi-Agent work;
- introduce a new LLM source of truth;
- invent buyers, companies, prices, tariffs, rankings, opportunities, risks, or recommendations;
- treat raw `mission.result` as authoritative evidence by default;
- force every query to every knowledge dimension/provider;
- use provider count as a success criterion;
- hide provider failures as if they were empty business data;
- perform a broad unrelated `run_dem_mission()` rewrite.

---

# 2. User-Value Definition

For a request such as:

> `اريد تصدير الخضروات والفاكهة المصرية الى الاردن`

the system should attempt to produce, when supported by available evidence/capabilities:

1. What the request is about and what was researched.
2. Trade-market evidence.
3. Market/opportunity indicators.
4. Agrifood-specific intelligence where available.
5. Market-access requirements.
6. SPS/TBT/regulatory requirements where available.
7. Rules-of-origin information where applicable.
8. Logistics/execution considerations where supported.
9. Relevant companies/importers/buyers only when documented.
10. Comparisons only where comparable candidates and explicit criteria exist.
11. Rankings only where an existing deterministic scoring basis exists.
12. Evidence-grounded opportunities.
13. Evidence-grounded risks.
14. Evidence-backed recommendations when the evidence supports action.
15. Explicit limitations and missing evidence.
16. Source/provenance information sufficient for verification.
17. Clear next evidence requirements when the answer cannot yet support an action.

The answer must remain useful even when coverage is incomplete. Incomplete evidence must reduce the answer's claims, not cause fabrication.

---

# 3. Validated Gap Register — Eleven Gaps

## GAP-01 — BI Synthesis is currently a ResearchResult adapter

### Evidence
`backend/app/agent/business_intelligence/synthesizer.py` currently adapts research findings/evidence and returns empty `entities`, `comparisons`, `rankings`, `opportunities`, and `risks` in the normal path; recommendations are only generated for an evidence-absence requirement. The executive summary is generic (`N structured finding(s) were identified`). fileciteturn92file0

### Required correction
Create a deterministic evidence-grounded synthesis pipeline that derives typed business facts from authoritative carriers and composes them into the existing `BusinessIntelligenceAnswer` contract.

### Acceptance
A research result containing sufficiently structured evidence can produce non-empty business sections when and only when their evidence prerequisites are met. Sparse evidence still yields a useful answer plus explicit limitations.

---

## GAP-02 — Knowledge/Decision/Outcome context is not actually fused into BI

### Evidence
`BusinessIntelligenceInput` already exposes `goal`, `decision`, `mission_result`, `execution_outcome`, and `research_result`, but the current synthesizer's substantive processing is centered on `research_result`. The schema itself is already designed for richer context. fileciteturn93file0

### Required correction
Introduce a BI input normalization/fusion boundary that can consume:

- authoritative ResearchResult evidence;
- explicit typed BI-compatible carriers;
- structured Knowledge results when present;
- decision context for interpretation/context, not for inventing evidence;
- execution outcome only as operational context, not as business evidence unless explicitly typed and sourced.

### Acceptance
Every derived business claim identifies its authoritative evidence carrier. Context may influence organization/prioritization but cannot silently become evidence.

---

## GAP-03 — Source coverage is not visible enough to distinguish empty data from unavailable/failed sources

### Evidence
WP-34 requires per-source retrieval status and error metadata and says partial results must indicate source coverage. fileciteturn86file0 Current provider/orchestration behavior can collapse exceptions into empty results, making `completed` compatible with very incomplete actual coverage.

### Required correction
Normalize source execution state into explicit categories, at minimum:

- `success_with_data`
- `success_empty`
- `failed`
- `unavailable`
- `not_applicable` where justified

Preserve these statuses into ResearchResult/BI provenance with minimal compatible extensions.

### Acceptance
The Avatar can distinguish "no relevant data returned" from "provider failed/unavailable". A successful partial research run cannot imply full coverage.

---

## GAP-04 — Research completion semantics overstate practical completeness

### Required correction
Separate lifecycle completion from coverage sufficiency:

```text
research_status = completed
coverage_status = partial | adequate | insufficient
```

Coverage must be dimension/evidence driven, not provider-count driven.

### Acceptance
A run with one useful provider and several empty/failed providers is still operationally completed but explicitly marked partial/limited when relevant knowledge dimensions remain unsupported.

---

## GAP-05 — Query/source routing does not guarantee dimension-relevant source coverage

### Evidence
The approved query-planning architecture intentionally leaves provider selection to Source Discovery and forbids hardcoded dimension→provider ownership. fileciteturn90file0 Current discovery can fall back to active sources when routing metadata is insufficient.

### Required correction
Improve source capability metadata and deterministic routing semantics without hardcoding ownership. Each provider/source should declare the knowledge capabilities/dimensions it can support where this metadata already fits the registry contract.

### Acceptance
For each planned query, discovery can explain why a source was selected or why no capable source was available. No dimension-specific provider ownership is introduced.

---

## GAP-06 — Research findings are retrieval wrappers, not sufficiently normalized business facts

### Evidence
The current structuring layer can produce findings whose content effectively says that evidence was retrieved, rather than expressing typed business facts that BI can compare, aggregate, or qualify.

### Required correction
Add a deterministic `BusinessFact`/equivalent normalization layer inside BI or its immediate input boundary. It must preserve source evidence and support fact types such as:

- trade flow/value/quantity/year;
- market indicator;
- market-access requirement;
- regulatory requirement;
- origin requirement;
- agrifood condition;
- logistics fact;
- documented entity;
- explicit comparison datum.

Do not redesign ResearchResult wholesale; adapt it into BI-native facts while retaining source traceability.

### Acceptance
The same evidence can support multiple BI sections without duplicating or altering the underlying evidence.

---

## GAP-07 — Entity, opportunity, risk, and recommendation derivation is absent

### Required correction
Implement explicit deterministic derivation rules:

**Entities:** only documented/sourced entities; no name guessing.

**Opportunities:** only evidence-backed signals with a declared basis and limitations.

**Risks:** only evidence-backed constraints/signals; severity only when explicitly supported by an existing deterministic rule or source.

**Business recommendations:** only when evidence supports the action; every recommendation carries supporting evidence and rationale.

**Next evidence requirements:** allowed without supporting evidence only when explicitly describing what is missing, why it matters, and what must be retrieved.

### Acceptance
No business recommendation/opportunity/risk/entity can exist without a traceable authoritative basis.

---

## GAP-08 — Comparisons and rankings are contractually rich but operationally unused

### Evidence
The schema already defines `BusinessComparison`, `ComparisonResult`, `BusinessRanking`, and `RankingEntry`, including explicit criteria, scores, evidence, scoring method, and limitations. fileciteturn93file0

### Required correction
Implement comparison/ranking synthesis only when the input contains:

- a candidate set;
- explicit comparison criteria;
- observed values;
- evidence per value;
- an existing deterministic scoring basis for rankings.

No inferred scoring, no LLM ranking, no arbitrary ordering.

### Acceptance
The system either produces an explainable deterministic comparison/ranking or explicitly states why it cannot.

---

## GAP-09 — Provenance/limitations are not sufficiently rich for an executive answer

### Evidence
Current provenance is effectively reduced to research status in the synthesizer. fileciteturn92file0 WP-34 requires source identity, URL/reference, retrieval timestamp, evidence association, and per-source failure metadata. fileciteturn86file0

### Required correction
Build a BI provenance object containing, where available:

- request/goal identity;
- query IDs and dimensions;
- consulted sources;
- contributing sources;
- empty sources;
- failed/unavailable sources;
- retrieval timestamps;
- evidence references;
- coverage status;
- limitations;
- transformation/derivation trace where a fact was normalized or synthesized.

### Acceptance
A reviewer can trace every material business claim back to its evidence and understand the known coverage limitations.

---

## GAP-10 — Goal/context can be lost or become null in the final BI answer

### Evidence
The current synthesizer derives goal from limited mission/goal paths and does not guarantee fallback to the research request context. fileciteturn92file0

### Required correction
Normalize goal/request context once at the BI boundary and preserve it through the answer. Do not create a competing intent parser.

### Acceptance
For the same user request, the final `BusinessIntelligenceAnswer.goal` remains populated whenever the request/goal is known, without inventing a goal.

---

## GAP-11 — Avatar presentation can lose evidence context for future rich BI sections

### Evidence
The frontend now exposes the major BI sections, but evidence presentation is not uniformly attached to every business object type. This becomes a trust problem once opportunities, risks, entities, and recommendations become populated.

### Required correction
Extend the presentation contract minimally so every evidence-bearing BI object can expose its supporting evidence/provenance in the executive UI. Do not redesign the Avatar.

### Acceptance
A user viewing an entity/opportunity/risk/recommendation can inspect its source evidence and limitations. Empty sections remain hidden; no fabricated UI content appears.

---

# 4. Missing Work Package — Formal Decision

The eleven gaps are not independent defects that can safely be patched one by one. GAP-01, GAP-02, GAP-06, GAP-07, GAP-08, and GAP-09 demonstrate a missing capability boundary:

> **Evidence-grounded Business Fact Fusion and Executive BI Synthesis.**

Therefore the plan explicitly creates the missing work package as the central implementation workstream.

### Proposed work package name

**WP-BI-SYNTHESIS-001 — Evidence-Grounded Executive Business Intelligence Synthesis**

### Purpose

Transform authoritative Research/Knowledge evidence into a structured, traceable, deterministic `BusinessIntelligenceAnswer` that is useful to an employee without making unsupported claims or taking autonomous action.

### Position

```text
Research / Knowledge
        ↓
Evidence
        ↓
WP-BI-SYNTHESIS-001
        ↓
BusinessIntelligenceAnswer
        ↓
ResponseBuilder / Avatar
```

### Explicit non-responsibilities

- no retrieval;
- no source execution;
- no provider calls;
- no research planning;
- no mission planning;
- no execution;
- no approval decisions;
- no autonomous action;
- no memory mutation;
- no Knowledge Graph;
- no Multi-Agent;
- no new LLM dependency.

---

# 5. Target Internal BI Pipeline

Implement the following deterministic stages inside the BI capability, preferably as small testable components rather than one large synthesizer method:

```text
BusinessIntelligenceInput
        ↓
InputNormalizer
        ↓
EvidenceAdapter / ProvenanceAdapter
        ↓
BusinessFactNormalizer
        ↓
FactFusion / Deduplication
        ↓
Section Derivers
 ├── Executive Summary
 ├── Key Findings
 ├── Entities
 ├── Comparisons
 ├── Rankings
 ├── Opportunities
 ├── Risks
 └── Recommendations
        ↓
Coverage + Limitation Builder
        ↓
Confidence/Qualification Builder
        ↓
BusinessIntelligenceAnswer
```

## 5.1 Deterministic fact fusion

Facts with the same semantic identity may be consolidated only when the consolidation rule is explicit. Conflicting source values must remain distinguishable and produce a limitation/conflict marker rather than an invented resolution.

The implementation must preserve distinct evidence excerpts even when `source_id` is identical.

## 5.2 Confidence

Never average unrelated confidences unless an authoritative contract already defines that aggregation. Preserve a single explicit confidence where valid. For multiple independent confidence values, expose them at their fact/finding level and leave aggregate confidence null unless an approved deterministic aggregation rule is added with tests and governance justification.

## 5.3 Recommendations

Two distinct cases:

1. `business_recommendation`: action supported by evidence and existing deterministic business rules.
2. `next_evidence_requirement`: no business action is asserted; it identifies the missing evidence required to continue.

## 5.4 Ranking

Ranking requires explicit candidate set + criteria + values + deterministic scoring basis. Otherwise do not rank.

## 5.5 Executive summary

The summary must describe the actual evidence-backed business situation, not merely count findings. It must remain conservative when evidence is sparse.

Example shape, not fixed wording:

```text
For Egypt → Jordan vegetable/fruit exports, the current evidence confirms [supported trade fact].
The available evidence is insufficient to confirm [missing business dimension].
Before execution, the highest-value next checks are [evidence-backed requirements].
```

No unsupported market conclusion may be inserted.

---

# 6. Knowledge Fusion Strategy

The BI layer may consume Company Knowledge results through an explicit typed adapter. It must not reach into provider implementations directly.

### Allowed input priority

1. Explicit typed BI evidence carriers.
2. WP-34 ResearchResult findings/evidence.
3. Explicit typed Knowledge results with source/confidence metadata.
4. Structured decision/context carriers for context only.
5. Raw mission execution result only as non-authoritative context unless it contains an explicit evidence carrier.

This maintains the existing no-invention principle while allowing company-specific intelligence to enrich the executive answer.

---

# 7. Coverage Model

Coverage must be evaluated by **knowledge dimension and evidence sufficiency**, not source count.

For each requested dimension:

```text
requested
  ↓
planned
  ↓
source available?
  ↓
source executed?
  ↓
data returned?
  ↓
evidence sufficient?
```

This enables BI to say:

- `covered`
- `partially_covered`
- `not_covered`
- `unavailable`
- `not_applicable`

A query returning no data is not automatically a failure; a provider failure is not automatically no data.

---

# 8. Source/Provider Failure Handling

Minimal changes only.

Do not rewrite all providers.

Introduce a normalized source outcome contract at the retrieval boundary and adapt existing provider outputs/exceptions into it. Existing provider-specific errors should remain available for diagnostics.

Required invariant:

```text
provider failure ≠ empty result
empty result ≠ business fact absent everywhere
one successful source ≠ full research coverage
```

---

# 9. Query Planning Relationship

`ResearchQueryPlanner` remains unchanged in responsibility.

It continues to answer:

> What knowledge questions should be researched?

BI answers:

> What does the authoritative evidence mean for this business request?

Research does not become BI, and BI does not become Research.

The approved planner architecture explicitly preserves this separation. fileciteturn90file0

---

# 10. Avatar Relationship

Avatar remains a presentation/transport consumer.

Required final chain:

```text
BusinessIntelligenceAnswer
        ↓
ResponseBuilder
        ↓
IntentContent.content["business_answer"]
        ↓
avatarResultParser
        ↓
ExecutiveResultCard
```

The Avatar must not:

- derive opportunities;
- calculate rankings;
- infer risks;
- merge evidence;
- query providers;
- decide what the business answer means.

---

# 11. Implementation Phases

## Phase 0 — Baseline freeze and contract inventory

- Record current `main` SHA.
- Confirm `b1c1dbe` is present.
- Verify clean/expected working tree.
- Inventory all existing BI schemas/tests/integration points.
- Inventory ResearchResult/source status contracts.
- Inventory KnowledgeProvider result contracts.
- No implementation changes.

**Exit:** baseline reproducible and all authoritative contracts identified.

## Phase 1 — Source coverage/status normalization

Addresses GAP-03, GAP-04, part of GAP-09.

- Introduce normalized source execution status.
- Preserve source errors.
- Distinguish empty/success/failure/unavailable.
- Add coverage summary without provider-count assumptions.
- Preserve backward compatibility with existing ResearchResult consumers.

**Tests:** provider failure, empty provider, partial success, all-fail, mixed results.

## Phase 2 — Source capability metadata/routing qualification

Addresses GAP-05.

- Audit provider registry metadata.
- Add minimal capability/dimension metadata where necessary.
- Keep discovery ownership centralized.
- Do not hardcode dimension→provider mapping.

**Tests:** relevant source selection, unavailable capability, fallback behavior, no accidental global fan-out.

## Phase 3 — BI input normalization and Business Fact model

Addresses GAP-02, GAP-06, GAP-10.

- Normalize goal/request.
- Define internal typed business fact representation.
- Adapt ResearchResult evidence.
- Adapt explicit Knowledge results.
- Preserve evidence/provenance.
- Keep raw mission result non-authoritative.

**Tests:** source authority, context-only carriers, malformed input rejection, provenance preservation.

## Phase 4 — Fact fusion and conflict handling

Addresses GAP-06, GAP-09.

- Deterministic deduplication.
- Preserve distinct excerpts.
- Detect conflicting values.
- Never silently choose one conflicting fact.
- Produce limitations for unresolved conflicts.

**Tests:** same-source distinct excerpts, cross-source same fact, conflicting values, duplicate evidence.

## Phase 5 — Executive BI section derivation

Addresses GAP-01, GAP-07, GAP-08.

Implement in this order:

1. key findings;
2. executive summary;
3. entities;
4. comparisons;
5. opportunities;
6. risks;
7. rankings;
8. recommendations;
9. limitations.

Each section must have explicit evidence prerequisites and tests.

## Phase 6 — Provenance and coverage answer

Addresses GAP-09 and reinforces GAP-03/04.

Populate `BusinessIntelligenceAnswer.provenance` with structured traceability and coverage information.

## Phase 7 — Avatar evidence presentation hardening

Addresses GAP-11.

Only after backend BI sections are populated by real evidence:

- attach evidence display to all evidence-bearing sections;
- display limitations where relevant;
- preserve existing UI structure;
- no redesign.

## Phase 8 — End-to-end acceptance

Run the same user scenario:

```text
اريد تصدير الخضروات والفاكهة المصرية الى الاردن
```

Validate at three levels:

1. raw backend/WS payload;
2. `BusinessIntelligenceAnswer` semantic correctness;
3. actual Avatar rendered UI.

Only then rebuild/validate the final frontend/runtime image as the final operational check.

---

# 12. Test Strategy

## 12.1 Unit tests

Every new derivation rule must have:

- positive evidence-backed case;
- insufficient-evidence case;
- conflicting-evidence case where relevant;
- no-invention case;
- provenance case;
- deterministic repeatability case.

## 12.2 Contract tests

Validate:

- Pydantic schemas;
- ResponseBuilder compatibility;
- IntentContent compatibility;
- Avatar parser compatibility;
- ResearchResult compatibility.

## 12.3 Integration tests

At minimum:

- broad intent → multiple relevant research queries → evidence → BI;
- simple intent → one query → BI;
- partial provider coverage → explicit limitation;
- failed provider → failed status, not empty;
- company knowledge + external research → fused answer;
- no company evidence → no invented entity;
- no deterministic ranking basis → no ranking;
- evidence-backed opportunity → opportunity with evidence;
- evidence-backed risk → risk with evidence;
- evidence-backed recommendation → recommendation with evidence;
- insufficient evidence → next-evidence recommendation.

## 12.4 Regression

Run focused BI tests first, then affected Research/Decision/Avatar tests, then the repository's relevant regression suite.

A passing test suite cannot override an architectural violation.

## 12.5 Final runtime verification

Only after all code-level acceptance criteria pass:

- rebuild frontend/runtime from the final `main` commit;
- execute the canonical Avatar query;
- inspect raw WebSocket payload;
- inspect rendered Avatar;
- verify no duplicate/legacy-only rendering;
- verify empty sections remain hidden;
- verify evidence can be traced from every displayed claim.

---

# 13. Acceptance Criteria for the Whole Work Package

The work package is NOT complete unless all are true:

1. Broad business intent produces relevant knowledge coverage rather than merely one generic research result.
2. Research coverage distinguishes success-with-data, success-empty, failure, and unavailable.
3. BI consumes authoritative Research and explicit Knowledge carriers without treating context as evidence.
4. Business facts are typed, deterministic, traceable, and conflict-aware.
5. Executive summary expresses evidence-backed business meaning rather than result count.
6. Entities are sourced.
7. Opportunities are evidence-derived.
8. Risks are evidence-derived.
9. Recommendations are evidence-backed or explicitly marked as next-evidence requirements.
10. Comparisons use explicit criteria and observed values.
11. Rankings are deterministic and explainable, or absent with a limitation.
12. Aggregate confidence is never invented.
13. Every material business claim remains traceable to evidence.
14. Coverage limitations are visible.
15. Avatar displays all populated BI sections and their evidence context.
16. No LLM becomes source of truth.
17. No new autonomy/decision authority is introduced.
18. No Knowledge Graph or Multi-Agent implementation is introduced.
19. Existing Research Query Planning boundaries remain intact.
20. Existing simple research behavior remains compatible.
21. Existing mission/goal/plan/task/execution architecture remains intact.
22. Focused and regression tests pass.
23. Final runtime verification confirms the same business answer reaches and is visibly usable in Avatar.

---

# 14. Example Expected Behavior for the Canonical Scenario

The system must NOT be required to fabricate a perfect market report when the repository lacks evidence.

Instead, the final answer should evolve according to available evidence.

### Minimum evidence scenario

If only UN Comtrade provides valid trade evidence:

- show trade findings;
- identify the exact source/evidence;
- state that market opportunity, buyer identity, regulatory/access, logistics, etc. are not yet established where evidence is missing;
- identify the highest-value next evidence requirements;
- do not claim that Jordan is a good opportunity merely because trade exists.

### Rich evidence scenario

If external and company sources provide sufficient evidence:

- summarize the market situation;
- surface documented buyers/importers;
- compare supported options;
- identify evidence-backed opportunities and risks;
- provide deterministic ranking only where a valid scoring basis exists;
- recommend concrete next actions backed by evidence;
- expose provenance and limitations.

This is the correct meaning of "complete" under the project's evidence-grounded architecture: **complete relative to authoritative available evidence, not artificially complete.**

---

# 15. Rollout and Safety Rules

1. Implement one phase at a time.
2. Commit each logically isolated phase atomically.
3. Never mix cleanup/refactoring unrelated to BI.
4. Preserve existing contracts unless a minimal, explicitly tested extension is necessary.
5. If a test fails unexpectedly, stop and diagnose before continuing.
6. If an architectural conflict appears, stop implementation and return to Plan/Forensic review.
7. Do not weaken tests to obtain green status.
8. Do not convert source failures into empty data for convenience.
9. Do not add heuristic business facts merely to populate UI sections.
10. Do not mark the work package complete from unit tests alone.

---

# 16. Required Evidence Package at Closure

The final implementation report must include:

- commit SHA(s);
- changed files grouped by phase;
- focused test results;
- regression results;
- coverage/status evidence;
- sample `BusinessIntelligenceAnswer` for the canonical scenario;
- raw payload verification;
- rendered Avatar verification;
- explicit list of populated and intentionally empty BI sections;
- provenance trace for displayed claims;
- confirmation that no unsupported claims were generated;
- confirmation of `main == origin/main` if push is part of execution authorization;
- confirmation that no unrelated files were changed.

---

# 17. Definition of Done

```text
WP-BI-SYNTHESIS-001

Architecture reviewed                 ✅
Governance boundaries preserved       ☐
11 validated gaps addressed           ☐
Business Fact Fusion implemented      ☐
Evidence-grounded BI synthesis       ☐
Knowledge + Research fusion           ☐
Coverage semantics                    ☐
Failure vs empty semantics            ☐
Entities/opportunities/risks          ☐
Comparisons/rankings                  ☐
Evidence-backed recommendations       ☐
Provenance/limitations                ☐
Avatar evidence presentation          ☐
Focused tests                         ☐
Regression                            ☐
Raw payload verification              ☐
Final visual Avatar verification      ☐
No architectural violations           ☐
```

**No implementation begins from this document until an explicit execution decision is made.**

**This document is the implementation baseline for the next BI work package; it does not authorize execution by itself.**
