# Reasoning Depth — WP Planning

**Purpose:** Define the next logical Work Package after Goal/Plan Foundation closure, focusing on Reasoning Depth within the DEM AI Architecture sequence.
**Authority:** `PLAN.md` Section 22 (Architecture Vision Statement), `.kilo/plans/1788376865110-goal-plan-architecture-contract.md` Section 7.1, AI Architecture Gap Audit
**Gap Reference:** `Reasoning Depth` identified as the next gap after Goal/Plan Foundation closure per approved AI Architecture Gap Audit.

---

## 1. Position in Roadmap Sequence

```
Goal/Plan Foundation (CLOSED)
    ↓
Reasoning Depth  ← THIS WP
    ↓
Autonomy Policy (future)
    ↓
Business-facing AI Response (future)
```

---

## 2. Why Reasoning Depth

### 2.1 Current State

DEM currently operates with:
- **Reactive routing:** user intent → keyword matching → Mission → Task → Execution
- **LLM Provider integration** (WP-LLM-001): Google AI (Gemini) integrated for candidate selection and reasoning text improvement
- **Goal/Plan Foundation** (planned/implemented): strategic objective and plan decomposition layer
- **Existing ReasoningEngine**: tactical Decision output, does not consider Goal progress or strategic context

### 2.2 Gap

The current `ReasoningEngine` is **context-unaware of Goal/Plan progress**. It reasons about the current request only, not about:
- Whether the current request advances an active Goal
- Which Plan mission is currently being executed
- Goal constraints that should filter candidate evaluation
- Plan progress that should influence decision confidence

### 2.3 What Reasoning Depth Adds

Reasoning Depth enhances `ReasoningEngine` to be **Goal-aware** without redesigning the architecture:

| Aspect | Before | After |
|--------|--------|-------|
| Context | Current request only | Current request + Goal scope + Plan constraints |
| Candidate evaluation | Rule-based + LLM | Goal-aligned filtering + constraint-aware scoring |
| Decision output | Tactical Decision | Tactical Decision with Goal/Plan context preserved |
| Reasoning text | Request-focused | Goal-progress-aware |

---

## 3. Goal / Plan Relationship

### 3.1 Inheritance from Goal/Plan Foundation

Reasoning Depth builds directly on the closed Goal/Plan Foundation:

- `Goal` and `Plan` schemas, managers, and repositories are stable
- `GoalManager.create_plan_for_goal()` establishes strategic context
- `PlanManager` owns Plan lifecycle and `Plan.missions` mutation
- `TaskPlanner` reads `goal_id`/`plan_id` from `session_context` (read-only)
- `ReasoningEngine` receives `goal_id`/`plan_id` in `request.context` (context-only, no lifecycle)

### 3.2 What Changes

Only `ReasoningEngine.reason()` internal logic; **signature unchanged**.

```python
class ReasoningEngine:
    def __init__(self, knowledge_provider_registry=None, memory_provider=None, 
                 approval_gate=None, knowledge_provider=None, llm_registry=None):
        # Existing parameters unchanged
        # NO new parameters for Goal/Plan managers
```

**Contract rule:** ReasoningEngine does NOT call `GoalManager`, `PlanManager`, `GoalRepository`, or `PlanRepository`. It treats `goal_id`/`plan_id` as opaque context hints received through the existing `request.context` dict. The `reason()` method signature and return type are unchanged.

---

## 4. Scope

### 4.1 In Scope

| Component | Responsibility |
|-----------|----------------|
| `ReasoningEngine.reason()` | Enhanced to read `goal_id`/`plan_id` from `request.context`; applies Goal scope and Plan constraints as context-aware filters in candidate evaluation |
| `ReasoningEngine` context handling | Preserve `goal_id`/`plan_id` in returned `Decision.context` |
| Goal-aware candidate scoring | No redesign; no change to baseline scoring formula or weights. Adds only a context-aware filtering/qualification pass using existing Goal scope and Plan constraints as opaque hints. Requests without Goal/Plan context are unaffected. |
| Plan constraint propagation | Ensure Plan.constraints flow from `PlanManager` → DEM router → `session_context` → `TaskPlanner` → `Mission.context` (verification/enforcement, not redesign) |
| Tests | Unit tests for ReasoningEngine with Goal/Plan context; integration tests for end-to-end flow |

### 4.2 Out of Scope

- **No redesign of ReasoningEngine** architecture or lifecycle
- **No new schemas** for Goal/Plan (already defined in Foundation)
- **No new public API endpoints**
- **No Autonomy Policy** design or enforcement
- **No Business-facing AI Response** (Avatar layer)
- **No Multi-agent coordination**
- **No changes to existing schemas** (`Decision`, `Mission`, `Task`, `ExecutionPlan`)
- **No database migrations**
- **No reopening WP-30 through WP-35**
- **No new external providers**
- **No changes to WP-34/WP-35 contracts**

---

## 5. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Goal/Plan Foundation | CLOSED | Schemas, managers, repositories, DEM chain integration stable |
| WP-LLM-001 (LLM Provider) | CLOSED | Gemini integration available for candidate enhancement |
| WP-30F (Knowledge Layer) | CLOSED | KnowledgeProviderRegistry operational |
| WP-30G (Memory Layer) | CLOSED | MemoryProvider operational |
| WP-30D (Decision Engine) | CLOSED | ReasoningEngine baseline exists |
| WP-30C (Task Planner) | CLOSED | TaskPlanner reads Plan context |

**Critical path:** Goal/Plan Foundation must be stable before Reasoning Depth begins. No other dependencies block this WP.

---

## 6. Acceptance Gates (Planning Level)

| Gate | Criterion | Verification |
|------|-----------|-------------|
| G1 | Goal/Plan Foundation closed and stable | No open defects in Goal/Plan chain |
| G2 | ReasoningEngine.reason() signature unchanged | Diff inspection |
| G3 | ReasoningEngine does NOT call Goal/Plan managers | Code inspection |
| G4 | Goal/Plan state NOT stored in MemoryProvider | Code inspection + test |
| G5 | Plan.missions mutation ONLY via PlanRepository.append_mission() | Code inspection + test |
| G6 | Decision.context preserves goal_id/plan_id if present | Integration test |
| G7 | Existing DEM tests pass without modification | Regression suite |
| G8 | No database migration required | init_db() pattern verified |
| G9 | No changes to WP-34/WP-35 contracts | Contract review |
| G10 | No new public API endpoints | Code inspection |

---

## 7. Planning Constraints

- **Plan Mode only.** No implementation.
- **Do not modify production code.**
- **Do not execute Reasoning Depth.**
- **Do not modify Goal/Plan Foundation.**
- **Do not reopen WP-30 to WP-35 or WP-34/WP-35.**
- **Do not create more than one WP.**
- **Do not invent additional WPs.**
- **Do not enter detailed implementation design.**
- **Do not modify Architecture Contract unless explicit conflict; if conflict, stop and write: `ARCHITECTURE CONTRACT CONFLICT`**

---

## 8. WP Identification

**WP Number:** WP-43 (next sequential after WP-42)
**WP Name:** Reasoning Depth
**Phase:** Phase 2 — Digital Export Manager (AI Layer Enhancement)
**Status:** Implemented

---

*Plan created: 2026-09-03*
*Author: Architecture Planning — Plan Mode*
*Implementation completed: 2026-09-03*

---

```
REASONING DEPTH WP IMPLEMENTED
```
