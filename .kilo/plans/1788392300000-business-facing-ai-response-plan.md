# Business-facing AI Response — WP Planning

**Purpose:** Define the next logical Work Package after WP-44 Autonomy Policy, formalizing Business-facing AI Response within the DEM AI Architecture sequence.
**Authority:** `PLAN.md` Section 22 (Architecture Vision Statement), `.kilo/plans/1788376865110-goal-plan-architecture-contract.md` Section 7.3, `.kilo/plans/1788387293955-reasoning-depth-plan.md`, `.kilo/plans/1788389600000-autonomy-policy-plan.md`, `.kilo/plans/AVATAR_CONTRACT.md`
**Gap Reference:** `Business-facing AI Response` identified as the next gap after WP-44 Autonomy Policy closure per approved AI Architecture Gap Audit and Architecture Contract Section 7.3.

---

## 1. Position in Roadmap Sequence

```
Goal/Plan Foundation (CLOSED)
    ↓
Reasoning Depth / WP-43 (CLOSED)
    ↓
Autonomy Policy / WP-44 (CLOSED)
    ↓
Business-facing AI Response  ← THIS WP
```

---

## 2. Why Business-facing AI Response

### 2.1 Current State

DEM currently has:

- **Decision.reasoning** — a plain text string produced by `ReasoningEngine`. It is human-readable but not structured for business consumption.
- **MissionResponse.result** — a raw `Dict[str, Any]` containing tool execution output. It lacks business context, Goal/Plan linkage, or actionable summary.
- **MissionResponse.reasoning** — the same plain text string from `Decision.reasoning`, passed through.
- **Goal/Plan status** — stored in repositories but not surfaced to the user in a structured, consumable format.
- **Autonomy Policy** — contract defined in WP-44 but not communicated to the user.
- **Avatar contract** — `IntentContent` and `AvatarRenderer` interfaces defined in `backend/app/agent/avatar/interface.py` and `.kilo/plans/AVATAR_CONTRACT.md`, but DEM does not currently produce structured `IntentContent` objects.
- **Frontend** — consumes `MissionResponse` directly and renders raw `result` and `reasoning` fields.

### 2.2 Gap

The system currently lacks a **structured response layer** that:

- Transforms internal engine outputs (`Decision`, `Mission.result`, `Goal.status`, `Plan.status`) into business-facing structured responses.
- Surfaces Goal progress, Plan status, and Mission outcomes in a consistent, machine-readable format.
- Communicates Autonomy Policy implications (e.g., "approval required", "operation permitted under supervised mode") without enforcing them.
- Provides actionable suggestions to the user.
- Remains presentation-agnostic (no UI markup, no audio streams, no avatar-specific data in DEM core).

The current `ApprovalGate` and `MissionResponse` are **tactical and data-dump** patterns. They cannot:

- Express business outcomes (e.g., "Shipment created successfully", "Invoice submitted to ETA")
- Link outcomes to strategic Goal/Plan progress
- Communicate policy context (autonomy level, approval requirements)
- Provide structured suggested actions

### 2.3 What Business-facing AI Response Adds

Business-facing AI Response introduces a **response contract** that transforms DEM internal state into structured, business-facing responses:

| Aspect | Current | After Business-facing AI Response |
|--------|---------|----------------------------------|
| Decision output | Plain text `reasoning` string | Structured response with outcome, context, and suggested actions |
| Mission result | Raw tool output dict | Business-outcome dict with Goal/Plan linkage |
| Goal/Plan visibility | Not surfaced | Progress indicators and status in structured response |
| Autonomy context | Not communicated | Policy hints (approval required, permitted, etc.) in structured response |
| Presentation contract | Implicit, ad-hoc | Explicit `IntentContent`-aligned contract; DEM produces structured intents only |

---

## 3. Relationship to Existing Contracts

### 3.1 Inheritance from Closed WPs

Business-facing AI Response builds on:

- **Goal/Plan Foundation (CLOSED):** `Goal.status`, `Plan.status`, `Goal.objective`, `Plan.objective` exist and are stable.
- **WP-43 Reasoning Depth (CLOSED):** `ReasoningEngine` preserves `goal_id`/`plan_id` in `Decision.context`. It does not enforce autonomy.
- **WP-44 Autonomy Policy (CLOSED):** `AutonomyPolicy` contract and `AutonomyPolicyInterpreter` define policy rules. They do not enforce runtime behavior.
- **WP-30H Avatar Contract (CLOSED):** `IntentContent` and `AvatarRenderer` interfaces defined in `backend/app/agent/avatar/interface.py`. DEM never imports or calls `AvatarRenderer`. DEM produces structured intents only.

### 3.2 Relationship to IntentContent / AvatarRenderer

The existing `IntentContent` contract defines:

```python
class IntentContent(BaseModel):
    intent_type: str
    content: Dict[str, Any]
    context: Dict[str, Any]
    suggested_actions: List[str]
```

**WP-45 approach:**

- `IntentContent` is the **foundational response contract**.
- Business-facing AI Response defines **how DEM internal outputs map to `IntentContent`**.
- The DEM router or a new `ResponseBuilder` transforms `Decision`, `Mission.result`, `Goal.status`, `Plan.status`, and `AutonomyPolicy` hints into `IntentContent` objects.
- The DEM never calls `AvatarRenderer.render()`.
- The DEM never imports any Avatar implementation.
- A separate presentation layer or gateway consumes `IntentContent` and renders it.

**Key distinction:** `IntentContent` is the **shape** of the response. Business-facing AI Response defines the **transformation rules** that produce that shape from DEM internal state.

---

## 4. Scope

### 4.1 In Scope

| Component | Responsibility |
|-----------|----------------|
| Response contract definition | Define `BusinessResponse` or extend `IntentContent` with business-specific fields: `outcome`, `progress`, `policy_hints`, `suggested_actions` |
| Response builder | A new `ResponseBuilder` or router-level transformation that converts `Decision`, `Mission.result`, `Goal.status`, `Plan.status`, and `AutonomyPolicy` into structured responses |
| Goal/Plan progress surfacing | Define how `Goal.status` and `Plan.status` are expressed in the response |
| Autonomy Policy hints | Define how `AutonomyPolicy` interpretation is surfaced as `policy_hints` in the response (e.g., `approval_required`, `permitted`, `escalation_available`) |
| Mission outcome formatting | Define how raw `Mission.result` is transformed into business-outcome language |
| Reasoning text enhancement | Define how `Decision.reasoning` is preserved or enhanced in the structured response |
| Tests | Unit tests for response builder; integration tests for end-to-end response flow; regression tests |

### 4.2 Out of Scope

- **No Avatar/UI implementation** — concrete `AvatarRenderer` implementations, text/voice/embodied rendering, HTML/Markdown generation, frontend code
- **No changes to ReasoningEngine** — signature unchanged, no business logic added
- **No changes to ApprovalGate** — tactical enforcer unchanged
- **No changes to Goal/Plan schemas** — `autonomy_level` and `approval_policy` already exist
- **No changes to Decision/Mission/Task/ExecutionPlan schemas** — response transformation happens at the boundary
- **No database migration**
- **No reopening WP-30 through WP-35**
- **No changes to WP-34/WP-35 contracts**
- **No new public API endpoints** as an executive decision; API surface for response management is deferred to future design decision
- **No Multi-agent coordination**
- **No Human Approval UI/workflow** — that is enforcement, not response formatting
- **No runtime enforcement** — Autonomy Policy is surfaced as hints only

---

## 5. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Goal/Plan Foundation | CLOSED | `Goal.status`, `Plan.status`, `Goal.objective`, `Plan.objective` stable |
| WP-43 Reasoning Depth | CLOSED | `ReasoningEngine` preserves `goal_id`/`plan_id` in `Decision.context` |
| WP-44 Autonomy Policy | CLOSED | `AutonomyPolicy` contract and interpreter defined; no runtime enforcement |
| WP-30H Avatar Contract | CLOSED | `IntentContent` and `AvatarRenderer` interfaces defined; DEM does not import Avatar |

**Critical path:** WP-44 must be stable before Business-facing AI Response begins. No other dependencies block this WP.

---

## 6. Architecture Boundaries

### 6.1 Response Transformation / Normalization Boundary

**Nature of the layer:**
- `ResponseBuilder` is a **deterministic mapping and normalization layer**, not a business logic engine.
- It consumes existing DEM internal state and normalizes it into a structured response shape.
- It does **not** infer new business decisions, apply business rules, or change the meaning of underlying data.

**Where transformation happens:**
- Inside the existing DEM mission response flow, after mission execution completes.
- The DEM router (`digital_export_manager.py`) or a new `ResponseBuilder` component transforms the existing `MissionResponse` payload into `IntentContent` before returning it to the caller.
- No new public API endpoint is created. The transformation is internal to the existing mission execution flow.

**Inputs consumed as-is:**
- `Decision.reasoning` — preserved or normalized; not rewritten.
- `Mission.result` — raw tool output dict; preserved under `result` in `content`. Not reinterpreted.
- `Goal.status`, `Plan.status`, `Goal.objective`, `Plan.objective` — read from repositories and surfaced as `progress` fields. Not transformed into new business state.
- `AutonomyPolicy` interpretation — read as `policy_hints` only. Not enforced.

**Output structure (`IntentContent`-aligned):**
- `intent_type`: normalized from mission terminal state (e.g., `completed`, `failed`, `pending_approval`). Mapped deterministically.
- `content`:
  - `outcome`: **representation/summary of existing `Mission.result`**, not a new business decision. Derived from `chosen_path` and execution status using fixed mapping rules defined in the contract.
  - `result`: raw tool output preserved unchanged.
  - `progress`: Goal/Plan status values copied as-is into structured fields. No new progress calculation.
  - `policy_hints`: `AutonomyPolicy` data reflected as hints only (e.g., `approval_required: true/false`, `autonomy_level: "supervised"`). No enforcement.
- `context`: execution context (session_id, mission_id, goal_id, plan_id, correlation_id).
- `suggested_actions`: derived from **existing state or display rules** in the contract (e.g., if `mission.status == "completed"` then suggest `["view_result", "create_another"]`). Not new Business Intelligence recommendations.

**What the response layer does NOT do:**
- It does **not** infer or generate new business decisions.
- It does **not** change the meaning or semantics of `Mission.result`.
- It does **not** add business rules not already present in the system.
- It does **not** enter Reasoning, Planning, or Goal/Plan lifecycle.
- It does **not** call `ReasoningEngine`, `ApprovalGate`, or any enforcement layer.
- It does **not** produce UI markup, HTML, Markdown, audio streams, or avatar animation data.
- It does **not** import or call `AvatarRenderer`.

### 6.2 Integration with Existing DEM Mission Response Flow

**Current flow:**
```
ToolOrchestrator.execute() → execution_output
    ↓
mission.status = final_status
mission.result = execution_output
    ↓
MissionResponse returned to frontend
```

**WP-45 flow:**
```
ToolOrchestrator.execute() → execution_output
    ↓
mission.status = final_status
mission.result = execution_output
    ↓
ResponseBuilder transforms existing MissionResponse fields into IntentContent
    ↓
Structured IntentContent returned alongside existing MissionResponse
```

**Key point:** The existing `MissionResponse` contract is unchanged. `ResponseBuilder` produces additional structured content; it does not replace or modify `MissionResponse`. Frontend may continue using `MissionResponse` directly or consume the new `IntentContent`.

### 6.3 Separation of Concerns

| Layer | Owns | Does NOT own |
|-------|------|--------------|
| `ReasoningEngine` | Tactical Decision with string `reasoning` | Structured response formatting, business outcome language |
| `ResponseBuilder` (new) | Deterministic mapping/normalization of existing DEM state into `IntentContent` shape | Business logic, business decisions, enforcement, rendering |
| `GoalManager` / `PlanManager` | Goal/Plan lifecycle and state | Response formatting |
| `AutonomyPolicyInterpreter` | Policy interpretation rules | Runtime enforcement, response rendering |
| `AvatarRenderer` | Presentation rendering | DEM core logic, response transformation |
| DEM Router | Orchestrates mission flow, invokes response transformation | Business logic, rendering |

### 6.4 Invariants

1. **Business-facing AI Response is a contract and deterministic transformation layer only.** No UI implementation.
2. **ResponseBuilder does not infer new business decisions.** It normalizes existing state only.
3. **ReasoningEngine does not produce structured responses.** It produces `Decision` with string `reasoning`.
4. **Goal/Plan schemas unchanged.** Status and objective fields already exist.
5. **ApprovalGate unchanged.** Tactical enforcer remains independent.
6. **No new public API endpoints** as an executive decision; transformation is internal to existing flow.
7. **No database migration.** Response transformation is in-memory/context-only.
8. **DEM never imports AvatarRenderer.** Presentation independence preserved.
9. **`Mission.result` is preserved unchanged.** `outcome` is a summary/representation of existing result, not a new decision.
10. **`suggested_actions` are derived from existing state or display rules.** Not new Business Intelligence recommendations.
11. **`policy_hints` reflect existing AutonomyPolicy data only.** Not enforcement.
12. **IntentContent is the foundational response contract.** Business-facing AI Response defines the deterministic transformation rules.

---

## 7. Acceptance Gates (Planning Level)

| Gate | Criterion | Verification |
|------|-----------|-------------|
| G1 | Goal/Plan Foundation closed and stable | No open defects in Goal/Plan chain |
| G2 | WP-43 Reasoning Depth closed and stable | No open defects in ReasoningEngine |
| G3 | WP-44 Autonomy Policy closed and stable | No open defects in AutonomyPolicy |
| G4 | WP-30H Avatar Contract closed and stable | `IntentContent` and `AvatarRenderer` interfaces exist |
| G5 | WP-45 defines response transformation/normalization only; no business logic or new business decisions | Document review + code inspection |
| G6 | `ResponseBuilder` does not infer new business decisions; maps existing state deterministically | Document review |
| G7 | `Mission.result` is preserved unchanged in structured response | Document review |
| G8 | `outcome` is representation/summary of existing result, not new business decision | Document review |
| G9 | `suggested_actions` derived from existing state or display rules only; not new Business Intelligence | Document review |
| G10 | `policy_hints` reflect existing AutonomyPolicy data only; not enforcement | Document review |
| G11 | ReasoningEngine behavior unchanged | Diff inspection |
| G12 | ApprovalGate behavior unchanged | Diff inspection |
| G13 | Goal/Plan schemas unchanged | Diff inspection |
| G14 | Decision/Mission/Task/ExecutionPlan schemas unchanged | Diff inspection |
| G15 | No database migration required | Document review |
| G16 | No changes to WP-34/WP-35 contracts | Contract review |
| G17 | No new public API endpoints as executive decision | Document review |
| G18 | DEM does not import AvatarRenderer | Code inspection |
| G19 | Structured response enters existing DEM mission flow without new public API | Document review |

---

## 8. Planning Constraints

- **Plan Mode only.** No implementation.
- **Do not modify production code.**
- **Do not execute Business-facing AI Response.**
- **Do not modify Goal/Plan Foundation.**
- **Do not modify WP-43 or WP-44.**
- **Do not reopen WP-30 to WP-35 or WP-34/WP-35.**
- **Do not create more than one WP.**
- **Do not invent additional WPs.**
- **Do not enter detailed implementation design.**
- **Do not modify Architecture Contract unless explicit conflict; if conflict, stop and write: `ARCHITECTURE CONTRACT CONFLICT`**

---

## 9. WP Identification

**WP Number:** WP-45 (next sequential after WP-44)
**WP Name:** Business-facing AI Response
**Phase:** Phase 2 — Digital Export Manager (AI Layer Enhancement)

---

*Plan created: 2026-09-03*
*Author: Architecture Planning — Plan Mode*
*Next step: Implementation WP execution*

---

```
BUSINESS-FACING AI RESPONSE WP PLANNED
```
