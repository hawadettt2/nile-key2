# Work Package: Core AI → Frontend Destinations Integration

**Work Package ID:** WP-FD-001
**Title:** Frontend Destinations Integration
**Phase:** Phase 2 — Intelligence Expansion
**Baseline:** `2822277` (Multi-Mission Orchestration closure)
**Authority:** `.kilo/plans/earp-001/executive-architecture-vision.md` Section 7.1
**Governing Documents:** Executive Architecture Vision (EARP-001), `AVATAR_CONTRACT.md`, `BA-ARCH-001.md`
**Date:** 2026-09-07
**Status:** Plan — Ready for Review

---

## 1. Current State

### 1.1 Core AI Architecture (Existing, Stable)

The Core AI Architecture is implemented and operational:

| Layer | Component | Status |
|-------|-----------|--------|
| Executive Intelligence | Digital Export Manager (DEM) | CLOSED |
| Reasoning | ReasoningEngine | CLOSED |
| Planning | TaskPlanner, ExecutionPlanner | CLOSED |
| Execution | ToolOrchestrator | CLOSED |
| Knowledge | KnowledgeOrchestrator, KnowledgeProviderRegistry | CLOSED |
| Memory | SQLiteMemoryProvider, cross-system memory | CLOSED |
| Analytics | Trade Intelligence | CLOSED |
| ERP Tools | 14 tools registered | CLOSED |
| Governance | ApprovalGate, AutonomyEnforcer, AuditRecorder | CLOSED |

### 1.2 Frontend Destinations (Partial)

| Frontend Destination | Status | Gap |
|---------------------|--------|-----|
| Digital Export Manager (DEM) | Operational | Free-text intent not exposed in UI; payload-driven only |
| AI Avatar / Persona | Contract only (`AVATAR_CONTRACT.md`) | Not implemented |
| Future Destinations | Not started | — |

### 1.3 Confirmed Gap

The **Frontend Integration / Consumption Gap**:

- The Core AI already supports free-text `Intent → Reasoning → Knowledge → Decision → Mission → Execution → Structured Business Response`.
- The DEM UI does not expose a natural-language entry point that feeds this chain directly.
- The current `MissionRequest` contract requires `mission_type` + structured `payload`, not free-text intent.
- The `AI Avatar` contract exists but has no UI implementation.

**This is not a Knowledge Gap, a Reasoning Gap, or a Core AI Gap.** The capability exists; the Frontend Destination connection is incomplete.

---

## 2. Target Architecture

### 2.1 Conceptual Model

```
Core AI Architecture
    ↓
Frontend Destinations / Intelligent Interfaces
    ↓
Company Employees
```

### 2.2 Frontend Destinations

1. **Digital Export Manager (DEM)** — Primary operational Frontend Destination.
   - Interface: Web application (`/digital-export-manager`)
   - Contract: `MissionRequest(mission_type, payload)` with optional free-text `query`
   - Core AI exposure: Full chain `Intent → Reasoning → Knowledge → Decision → Plan → Mission → Task → Execution → Structured Business Response`

2. **AI Avatar / Employee-facing AI Persona** — Future Frontend Destination.
   - Interface: Conversational UI
   - Contract: Same Core AI capabilities, different presentation
   - Scope: Out of scope for this WP; documented as future extension only

3. **Future Intelligent Destinations** — Architecture permits additional destinations without Core AI changes.

### 2.3 Integration Contract

Every Frontend Destination must be able to access the Core AI through this chain:

```
Employee Intent
  → DEM Frontend / Avatar Frontend
  → DEM Business Façade (POST /api/v1/digital-export-manager/missions)
  → ReasoningEngine.reason()
  → KnowledgeOrchestrator (optional)
  → Decision (with context.knowledge, context.memories)
  → TaskPlanner.plan() → Mission + Tasks
  → ExecutionPlanner.plan() → ExecutionPlan
  → ToolOrchestrator.execute() → Tool results
  → ResponseBuilder.build() → IntentContent
  → DEM Frontend / Avatar Frontend
```

Supporting capabilities preserved across all destinations:
- Memory (short-term + cross-system)
- Autonomy Policy
- ApprovalGate
- Audit
- Security
- Knowledge Orchestration

---

## 3. Scope

### 3.1 In Scope

| Component | Responsibility |
|-----------|----------------|
| DEM Frontend — Free-text input | Add natural-language entry point to `DEMMissionComposer` that passes `query` into `payload` |
| DEM Frontend — Intent routing | Ensure `MissionRequest` carries `payload.query` to `ReasoningEngine.reason()` |
| DEM Router — Intent passthrough | Preserve `request.payload.get("query")` as `intent` in `reasoning_engine.reason()` call |
| Core AI — No changes | Core AI components remain unchanged; only consumption is updated |
| Contract documentation | Update `MissionRequest` contract to explicitly support free-text `query` |

### 3.2 Out of Scope

| Item | Reason |
|------|--------|
| AI Avatar implementation | Future Frontend Destination; contract exists, UI not built |
| New Core AI components | Core AI is stable and complete |
| New API endpoints | Use existing `/api/v1/digital-export-manager/missions` |
| New providers | No new Knowledge, Memory, or Tool providers |
| Database migrations | No schema changes required |
| Multi-agent coordination | Out of scope per architecture invariants |
| Long-term Goal Evolution | Separate WP; not required for Frontend Destination connection |
| Advanced Autonomy | Separate WP; not required for Frontend Destination connection |

---

## 4. Acceptance Criteria

| AC | Criterion | Verification |
|----|-----------|--------------|
| AC-1 | DEM Frontend sends free-text user intent to Core AI | UI test: user types "أريد تصدير الخضر والفواكه المصرية إلى الأردن" and submits |
| AC-2 | Intent reaches `ReasoningEngine.reason()` as `intent` parameter | Code inspection + integration test |
| AC-3 | `Decision.context.knowledge` is populated from `KnowledgeOrchestrator` | Integration test |
| AC-4 | `Decision → Plan → Mission → Task → Execution` chain executes end-to-end | Integration test |
| AC-5 | `Structured Business Response` (`IntentContent`) returns to DEM Frontend | UI test: response includes `intent_content` |
| AC-6 | No new AI Engine created in Frontend | Code inspection: no new AI components in `frontend/src/` |
| AC-7 | ApprovalGate, Autonomy, Audit, Security, Memory, Knowledge contracts preserved | Regression test suite |
| AC-8 | DEM API façade and bounded-context boundaries unchanged | Code inspection |
| AC-9 | AI Avatar documented as future extension only | Documentation review |
| AC-10 | Existing DEM tests pass without modification | Regression suite |

---

## 5. Verification Strategy

### 5.1 Automated Tests
- Add integration test for free-text intent flow through DEM `/missions`
- Add regression test for existing structured `payload` flow
- Run existing agent test suite to ensure no regression

### 5.2 Manual Verification
- Open DEM Frontend
- Enter free-text intent: "أريد تصدير الخضر والفواكه المصرية إلى الأردن"
- Verify Mission is created with `reasoning` reflecting the intent
- Verify `intent_content` is present in response
- Verify Knowledge entries appear in `Decision.context`

### 5.3 Contract Verification
- Inspect `MissionRequest` schema to confirm `payload.query` is accepted
- Inspect `create_mission()` to confirm `intent = request.payload.get("query")` passthrough
- Inspect `ResponseBuilder.build()` to confirm `IntentContent` is produced

---

## 6. Sequencing / Gates

| Gate | Criterion | Status |
|------|-----------|--------|
| G1 | Core AI Architecture stable | PASS — Multi-Mission Orchestration closed |
| G2 | Executive Architecture Vision Section 7.1 approved | PASS — Updated 2026-09-07 |
| G3 | DEM API contract supports free-text `query` in payload | PASS — `request.payload.get("query")` exists |
| G4 | No changes to Core AI components required | PASS — Consumption-only change |
| G5 | Regression suite passes | PASS — Verified before WP start |

---

## 7. Definition of Done

1. DEM Frontend exposes free-text input field for user intent.
2. Free-text intent flows through `MissionRequest.payload.query` → `ReasoningEngine.reason(intent=...)`.
3. Full Core AI chain executes: Reasoning → Knowledge → Decision → Plan → Mission → Task → Execution → Structured Business Response.
4. `IntentContent` is returned to DEM Frontend and displayed.
5. All existing DEM tests pass without modification.
6. No new AI Engine, provider, or Core AI component created.
7. AI Avatar documented as future Frontend Destination only.
8. Executive Architecture Vision Section 7.1 is the governing reference.

---

## 8. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Free-text input introduces ambiguous routing | Medium | Medium | ReasoningEngine already handles free-text via keyword matching + LLM enhancement |
| Frontend change breaks existing structured payload flow | Low | High | Preserve existing `mission_type` + payload fields; add free-text as optional |
| Users expect AI Avatar behavior from DEM | Low | Medium | Clear UI labeling; AI Avatar documented as separate future destination |
| Core AI contract drift | Low | High | No changes to Core AI components; consumption-only |

---

## 9. Out of Scope Clarifications

The following are **explicitly out of scope** for this WP and must not be started during implementation:

1. **AI Avatar UI** — The conversational interface is a future Frontend Destination. This WP only documents its architectural placement.
2. **New Reasoning or Decision logic** — Core AI logic is stable.
3. **New Knowledge providers** — Knowledge layer is complete.
4. **New API endpoints** — Use existing `/missions` endpoint.
5. **Database migrations** — No schema changes required.
6. **Multi-agent coordination** — Not part of Frontend Destinations.

---

**Status:** Plan — Ready for Review
**Next Action:** Implementation agent to execute acceptance criteria AC-1 through AC-10
**Location:** `.kilo/plans/earp-001/wp-frontend-destinations-integration.md`
