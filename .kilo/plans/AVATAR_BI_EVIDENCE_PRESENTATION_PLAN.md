# Executive Avatar UX & Evidence Presentation — Work Package Plan

**Status:** APPROVED PLAN — NOT FOR IMPLEMENTATION YET  
**Mode:** Plan  
**Branch:** `main`  
**Authority:** Repository governance + canonical backend contracts + Avatar Contract (`AVATAR_CONTRACT.md`) + Business Intelligence Synthesis Completion Plan  
**Scope:** Improve Executive Avatar evidence presentation UX while preserving all existing contracts, BI synthesis logic, and DEM architecture.  
**Implementation owner:** Kilo Code only after explicit execution authorization.  
**Planning owner:** Project/Architecture review.  

---

## 0. Executive Decision

The current `BusinessIntelligenceAnswer` contract, `ResponseBuilder`, `IntentContent`, and Avatar presentation layer form a valid transport path for evidence-grounded business intelligence. The backend correctly preserves evidence, provenance, and traceability through `EvidenceReference`, `BusinessFinding`, `BusinessEntity`, `ComparisonResult`, `RankingEntry`, and the top-level `evidence`/`sources`/`provenance` fields.

However, manual inspection of the Avatar UI shows two presentation-layer concerns:

1. **Raw technical payload exposure:** The Avatar can display the raw JSON response (`response` / `showRawResponse`) in addition to the structured `ExecutiveResultCard`. While this is technically useful, exposing raw internal payloads as a primary or prominent view can surface implementation details to executive users.
2. **Evidence repetition across sections:** The same evidence reference can appear in multiple BI sections (`key_findings`, `entities`, `comparisons`, `rankings`, etc.) because each section carries its own `evidence` list. This is contractually correct but may create visual redundancy in the UI.

These are **presentation-layer observations**, not architectural violations. The contracts are intact; the issue is how evidence is rendered.

This Work Package is therefore scoped **only** to Avatar evidence presentation UX. No BI synthesis, schema, provenance, or DEM core changes are required or authorized.

---

## 1. Governing Architecture and Non-Negotiable Boundaries

This plan is governed by, and must remain compatible with:

- `PLAN.md` — project constitution / master roadmap and architecture principles.
- `.kilo/plans/AVATAR_CONTRACT.md` — `IntentContent` and `AvatarRenderer` boundaries.
- `.kilo/plans/BUSINESS_INTELLIGENCE_SYNTHESIS_COMPLETION_PLAN.md` — BI synthesis architecture and acceptance criteria.
- `backend/app/agent/business_intelligence/schema.py` — `BusinessIntelligenceAnswer` and related schemas.
- `backend/app/agent/response/builder.py` — `ResponseBuilder.build()` deterministic mapping.
- `backend/app/agent/avatar/interface.py` — `IntentContent` contract.
- `frontend/src/lib/avatarResultParser.ts` — frontend parsing contract.
- `frontend/src/components/avatar/ExecutiveResultCard.tsx` — current evidence rendering.

### Hard boundaries — the implementation MUST NOT:

- modify `BusinessIntelligenceAnswer` schema or any BI synthesis component;
- modify `ResponseBuilder` or `IntentContent`;
- modify DEM reasoning, decision, planning, execution, autonomy, approval, or workflow components;
- introduce new backend endpoints or change API contracts;
- mutate `EvidenceReference`, `BusinessFinding`, `BusinessEntity`, `ComparisonResult`, `RankingEntry`, or provenance structures;
- invent, summarize, or alter evidence content;
- add fallback/mock data or hide real evidence;
- change how evidence is stored or transmitted;
- perform unrelated refactoring in backend routers, services, or BI modules.

---

## 2. Problem Statement

### Current behavior

When the Avatar renders a `BusinessIntelligenceAnswer`, evidence is displayed at multiple levels:

- **Top-level `evidence`** — rendered as a standalone section when present.
- **Per-section evidence** — each `key_findings`, `entities`, `comparisons`, `rankings`, `opportunities`, `risks`, and `recommendations` item renders its own evidence inline via `renderEvidenceItems()`.
- **Raw response fallback** — when structured parsing fails or when `showRawResponse` is enabled, the raw JSON payload is rendered directly in the UI.

### Observed symptoms

1. **Raw technical details surfaced to executive users:** The raw JSON payload contains internal fields such as `mission_id`, `session_id`, `execution_trace`, `approval_state`, `business_answer.provenance.research_status`, and other implementation-specific data. While this is useful for debugging, it is not appropriate as a primary user-facing view.
2. **Evidence repetition:** The same source (`source_id`, `source_url`, `content_excerpt`) can appear under multiple sections because each section independently renders its own evidence list. This creates visual redundancy without adding new information.

### Impact

- Executive users may see internal technical details that are not actionable.
- Trust and readability decrease when the same evidence appears repeatedly across sections.
- The current UI does not distinguish between "debug/raw view" and "executive summary view."

### Non-problems

- The backend data model, evidence provenance, and BI synthesis are **not** broken.
- The repetition is a consequence of the correct contract design where each business object owns its evidence.
- The raw response view is intentionally available for debugging; it is not an architectural defect.

---

## 3. Goal

Improve the Executive Avatar evidence presentation so that:

1. Executive users see a clean, structured business answer by default.
2. Technical/raw details remain accessible but are clearly separated from the executive view.
3. Evidence repetition is reduced visually without removing or altering the underlying evidence structure.
4. All traceability, provenance, and evidence-grounded guarantees remain intact.
5. No backend contract, schema, or BI logic changes are required.

---

## 4. Scope

### In scope

- **Frontend only** (`frontend/src/pages/Avatar.tsx`, `frontend/src/components/avatar/ExecutiveResultCard.tsx`, `frontend/src/lib/avatarResultParser.ts`).
- Evidence presentation UX improvements within the existing `ExecutiveResultCard` and Avatar response flow.
- Introduction of a clear separation between:
  - **Executive view:** structured business answer with summarized, deduplicated evidence display.
  - **Technical/debug view:** optional raw payload and full technical details, clearly labeled as such.
- Evidence deduplication logic in the frontend renderer only (not in the backend).
- Minor parser extensions if needed to support new presentation fields, without changing the backend payload shape.

### Out of scope

- Any change to `BusinessIntelligenceAnswer`, `EvidenceReference`, `BusinessFinding`, `BusinessEntity`, `ComparisonResult`, `RankingEntry`, `Opportunity`, `Risk`, `Recommendation`, `Limitation`, or `provenance` schemas.
- Any change to `ResponseBuilder`, `IntentContent`, `AvatarRenderer`, or backend routers.
- Any change to BI synthesis, fact fusion, coverage builder, or derivation rules.
- Any change to Research, Knowledge, Decision, Execution, Autonomy, Approval, or Workflow components.
- Any new backend endpoints, API contracts, or database migrations.
- Multi-Agent, Knowledge Graph, or LLM behavior changes.
- Reopening Phase 7, Phase 8, or any closed Work Package.

---

## 5. Components Affected

| Component | Path | Change type |
|-----------|------|-------------|
| Avatar page | `frontend/src/pages/Avatar.tsx` | UX adjustment |
| ExecutiveResultCard | `frontend/src/components/avatar/ExecutiveResultCard.tsx` | Evidence rendering logic |
| Avatar result parser | `frontend/src/lib/avatarResultParser.ts` | Optional parser extension for presentation helpers |
| Translation strings | `frontend/src/locales/...` | Labels for new sections if needed |

No backend components are in scope.

---

## 6. Proposed Presentation Changes

### 6.1 Separate executive and technical views

The current `showRawResponse` toggle already exists. The UX change is to:

- Make the **structured executive card** the default and dominant view.
- Move the raw response into an explicitly labeled **"Technical Details"** or **"Developer View"** section, not mixed with executive content.
- The raw response must only be shown when the user explicitly opts in (e.g., via a dedicated button).

**Current fallback behavior:** When structured parsing fails, `Avatar.tsx` currently renders the raw JSON payload directly in a `<pre>` block. This behavior is **existing and accepted** within the current state. It is not a blocking acceptance criterion for this Work Package. Improving or replacing this fallback may be revisited in future work, but it is **out of scope** for this package.

### 6.2 Evidence deduplication in the renderer

Because the backend contract intentionally places evidence on each business object, the frontend should deduplicate evidence **only for display purposes**:

- Build a global evidence map keyed by a stable identifier (e.g., `source_id + source_url + content_excerpt`).
- When rendering evidence for a section, reference the global map.
- When the same evidence item appears under multiple sections, render it once under the first occurrence and render a compact reference (e.g., "see Key Findings #1") elsewhere.
- Preserve the full evidence object in the data model; only the rendered output is deduplicated.

### 6.3 Evidence grouping and summarization

- Group evidence by `source_id` when multiple excerpts come from the same source.
- Show a concise evidence label (source + URL + excerpt preview) rather than the full technical `EvidenceReference` fields.
- Keep `retrieval_timestamp`, `confidence`, `limitations`, and `provenance` accessible in a drill-down or hover state, not inline by default.

### 6.4 Limitations and provenance visibility

- `limitations` are already rendered inline in several sections; ensure they remain visible.
- `provenance` is already available in the parsed result; expose it as a visible, collapsible **"Provenance"** section in the Avatar UI so users can inspect traceability without leaving the structured view.

---

## 7. Acceptance Criteria

The Work Package is NOT complete unless all are true:

1. The Avatar default view shows the structured `ExecutiveResultCard` with no raw JSON visible.
2. A clearly labeled technical/debug option exists to view the raw response; it is off by default.
3. When the same evidence item supports multiple BI sections, the UI renders it once and uses compact references elsewhere.
4. No evidence item is removed, altered, or hidden from the data model; only the rendered view changes.
5. `limitations` remain visible inline where they already appear.
6. `provenance` is visible to the user inside the Avatar UI in a dedicated collapsible section, preserving all provenance data without removing or altering any backend payload or contract.
7. All existing Avatar tests pass; no regression in BI/Avatar contracts.
8. The frontend build succeeds.
9. No backend code, schema, API contract, or BI logic is changed.
10. The implementation does not introduce new dependencies or redesign the Avatar layout.

---

## 8. Implementation Phases

### Phase 1 — Executive / Technical view separation

- Adjust `Avatar.tsx` so raw response is only shown in an explicitly labeled technical section.
- The current raw JSON fallback behavior when structured parsing fails remains unchanged and is **out of scope** for this Work Package.

### Phase 2 — Evidence deduplication in the renderer

- Add a frontend-only evidence deduplication helper in `ExecutiveResultCard` or parser utilities.
- Render unique evidence items per section, with compact cross-references for repeated items.

### Phase 3 — Evidence grouping and drill-down

- Group evidence by source in the renderer.
- Add optional hover/click to expand full `EvidenceReference` details.

### Phase 4 — Verification and closure

- Run focused Avatar tests.
- Run BI contract tests.
- Run frontend build.
- Manual runtime verification of the canonical scenario.

---

## 9. Test Strategy

### 9.1 Unit/component tests (frontend)

- Verify default view does not render raw JSON.
- Verify technical view toggle shows raw response with correct label.
- Verify evidence deduplication produces unique rendered items per section.
- Verify compact cross-references are rendered when evidence is reused.
- Verify evidence grouping by `source_id` works.
- Verify drill-down exposes full `EvidenceReference` fields.

### 9.2 Contract tests

- Verify `avatarResultParser` still produces the same `ParsedAvatarResult` shape from unchanged backend payloads.
- Verify `ExecutiveResultCard` props contract is unchanged.

### 9.3 Regression tests

- Run existing Avatar and BI test suites.
- Ensure no backend test failures are introduced.

### 9.4 Runtime verification

- Execute the canonical scenario: `اريد تصدير الخضروات والفاكهة المصرية الى الاردن`.
- Inspect rendered Avatar:
  - structured executive card is default;
  - raw JSON is absent unless explicitly requested;
  - evidence appears once per section with compact cross-references;
  - limitations and provenance are accessible;
  - no fabricated UI content appears.

---

## 10. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Frontend deduplication logic diverges from backend evidence model | Medium | Medium | Keep deduplication purely presentational; never mutate the parsed `businessAnswer` object. |
| Evidence cross-references become confusing | Medium | Low | Use clear labels such as "Also cited in: Entities". |
| Technical view accidentally exposed to end users | Low | Medium | Default is executive view; technical view requires explicit user action. |
| Layout breakage on small screens | Medium | Low | Preserve existing responsive classes; test at common breakpoints. |

---

## 11. Rollout and Safety Rules

1. Implement one phase at a time.
2. Commit each phase atomically.
3. Do not modify backend code, schemas, or contracts.
4. Do not weaken or remove evidence fields.
5. If a test fails unexpectedly, stop and diagnose before continuing.
6. Do not add mock data or fabricated UI content.
7. Do not mark the Work Package complete from frontend tests alone; runtime Avatar inspection is required.

---

## 12. Definition of Done

```text
Executive Avatar UX & Evidence Presentation

Architecture reviewed                 ✅
Governance boundaries preserved       ☐
Executive/technical view separated    ☐
Evidence deduplication in renderer    ☐
Evidence grouping + drill-down        ☐
Limitations + provenance visible      ☐
Focused frontend tests                ☐
Regression tests pass                 ☐
Frontend build succeeds               ☐
Runtime Avatar verification           ☐
No backend/BI contract changes        ☐
```

**No implementation begins from this document until an explicit execution decision is made.**
