# Autonomy Policy — WP Planning

**Purpose:** Define the next logical Work Package after WP-43 Reasoning Depth, formalizing Autonomy Policy within the DEM AI Architecture sequence.
**Authority:** `PLAN.md` Section 22 (Architecture Vision Statement), `.kilo/plans/1788376865110-goal-plan-architecture-contract.md` Section 7.2, `.kilo/plans/1788387293955-reasoning-depth-plan.md`
**Gap Reference:** `Autonomy Policy` identified as the next gap after WP-43 Reasoning Depth closure per approved AI Architecture Gap Audit and Architecture Contract Section 7.2.

---

## 1. Position in Roadmap Sequence

```
Goal/Plan Foundation (CLOSED)
    ↓
Reasoning Depth / WP-43 (CLOSED)
    ↓
Autonomy Policy  ← THIS WP
    ↓
Business-facing AI Response (future)
```

---

## 2. Why Autonomy Policy

### 2.1 Current State

DEM currently has:

- **Goal.autonomy_level** — a label field with values `"full"`, `"supervised"`, `"manual"`. It is stored in the Goal schema but **not enforced**.
- **Plan.approval_policy** — a structural field in the Plan schema. It stores hooks for autonomy but enforcement is **deferred**.
- **ApprovalGate** — a hardcoded deterministic checker in `backend/app/agent/approval/gate.py` that detects destructive operations based on path + intent keywords. It is **tactical and path-level only**, not goal-aware or policy-aware.
- **WP-43 Reasoning Depth** — made `ReasoningEngine` Goal/Plan-aware via context-only filtering. It preserves `goal_id`/`plan_id` in `Decision.context` but does not enforce any autonomy rules.

### 2.2 Gap

The system currently lacks a **policy layer** that answers:

- Given a Goal's `autonomy_level`, which operations are permitted without human approval?
- Given a Plan's `approval_policy`, which Mission types require approval, and who can approve?
- How does the system escalate when approval is required but not granted?
- How does `ReasoningEngine` incorporate autonomy constraints into candidate evaluation?

The current `ApprovalGate` is a **fixed rule set** (destructive keyword detection). It cannot:

- Vary by Goal or Plan
- Respect user-defined autonomy preferences
- Handle escalation paths
- Produce structured approval requirements that flow through the DEM chain

### 2.3 What Autonomy Policy Adds

Autonomy Policy introduces a **policy boundary** that defines, but does not enforce, the rules for autonomous vs. supervised operation:

| Aspect | Current | After Autonomy Policy |
|--------|---------|----------------------|
| Autonomy level | Label only on Goal | Interpreted policy that determines per-operation permissions |
| Approval policy | Empty structure on Plan | Structured hooks defining required approvals, approvers, escalation |
| ReasoningEngine | Goal/Plan context preserved | Reads autonomy policy as context hints; does not enforce |
| Execution | Hardcoded `ApprovalGate` | `ApprovalGate` becomes one enforcer of many possible policies |
| Scope | Tactical (path-level) | Strategic (Goal-level) + Tactical (Plan-level) |

---

## 3. Goal / Plan / Reasoning Relationship

### 3.1 Inheritance from Closed WPs

Autonomy Policy builds on:

- **Goal/Plan Foundation (CLOSED):** `Goal.autonomy_level` and `Plan.approval_policy` fields exist. `GoalManager` and `PlanManager` own lifecycle. `PlanManager` is sole owner of `Plan.missions`.
- **WP-43 Reasoning Depth (CLOSED):** `ReasoningEngine.reason()` signature unchanged. It reads `goal_id`/`plan_id` from `request.context` and applies context-aware filtering. It does **not** enforce autonomy.

### 3.2 What Changes

Only **policy definition and interpretation**, not enforcement:

- `ReasoningEngine` may read `autonomy_level` and `approval_policy` from `request_context` as **opaque hints**.
- `ReasoningEngine` does **not** block or allow operations based on autonomy policy.
- `ApprovalGate` remains the existing tactical enforcer. Autonomy Policy does **not** replace or modify `ApprovalGate`.
- `GoalManager` and `PlanManager` remain unchanged. Autonomy Policy does **not** modify Goal/Plan lifecycle.

---

## 4. Scope

### 4.1 In Scope

| Component | Responsibility |
|-----------|----------------|
| Autonomy Policy schema/contract | Define `AutonomyPolicy` data structure: `autonomy_level`, `allowed_operations`, `required_approvals`, `approvers`, `escalation_path` |
| Policy interpretation rules | Define how `Goal.autonomy_level` and `Plan.approval_policy` map to operation permissions |
| ReasoningEngine context handling | `ReasoningEngine` may read autonomy policy from `request_context` as opaque hints; does not enforce |
| Approval policy propagation | Define how `Plan.approval_policy` flows from `PlanManager` → DEM router → `session_context` → `TaskPlanner` → `Mission.context` (verification/enforcement boundary, not implementation) |
| Tests | Unit tests for policy interpretation; integration tests for context propagation; regression tests |

### 4.2 Out of Scope

- **No enforcement implementation** — Autonomy Policy defines rules only; enforcement is a future WP or remains with `ApprovalGate`
- **No changes to Goal/Plan schemas** — `autonomy_level` and `approval_policy` already exist
- **No changes to ReasoningEngine architecture** — signature unchanged, no lifecycle changes
- **No changes to ApprovalGate** — existing tactical enforcer unchanged
- **No Human Approval UI/workflow** — that is enforcement, not policy
- **No Business-facing AI Response** (Avatar layer)
- **No Multi-agent coordination**
- **No changes to existing schemas** (`Decision`, `Mission`, `Task`, `ExecutionPlan`)
- **No database migrations**
- **No reopening WP-30 through WP-35**
- **No changes to WP-34/WP-35 contracts**
- **No new public API endpoints** as an executive decision; API surface for policy management is deferred to future design decision

---

## 5. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Goal/Plan Foundation | CLOSED | `Goal.autonomy_level` and `Plan.approval_policy` fields stable |
| WP-43 Reasoning Depth | CLOSED | `ReasoningEngine` Goal/Plan-aware via context-only; signature unchanged |
| WP-30D Decision Engine | CLOSED | ReasoningEngine baseline exists |
| WP-30C Task Planner | CLOSED | TaskPlanner reads Plan context |
| Existing ApprovalGate | CLOSED | Tactical enforcer unchanged |

**Critical path:** WP-43 must be stable before Autonomy Policy begins. No other dependencies block this WP.

---

## 6. Architecture Boundaries

### 6.1 Policy Boundary (Contract Only — No Runtime Enforcement)

**Contract inputs:**
- `Goal.autonomy_level` — stored on Goal; values are `"full"`, `"supervised"`, `"manual"`. These are **policy labels**, not enforcement directives.
- `Plan.approval_policy` — stored on Plan as a structure. It contains hooks for autonomy but is **inactive data** until an enforcement WP consumes it.

**Where the policy is defined:**
- `Goal.autonomy_level` — defines the Goal owner's preferred autonomy tier.
- `Plan.approval_policy` — defines which Mission types require approval, who can approve, and the escalation path.
- Both are **contract inputs** for a future enforcement layer. WP-44 does not activate them.

**Where the policy is read (contractually):**
- `GoalRepository` / `GoalManager` — Goal-level autonomy label storage and retrieval.
- `PlanRepository` / `PlanManager` — Plan-level `approval_policy` structure storage and retrieval.
- `ReasoningEngine` — may read `autonomy_level` and `approval_policy` from `request_context` as **opaque hints only**; does not branch, block, or alter decisions based on them.
- `TaskPlanner` — reads `plan_constraints` from `session_context`; does not read autonomy policy.
- `ApprovalGate` — existing tactical enforcer; does not read Goal/Plan autonomy policy.

**Policy rules specification (for future enforcement):**
- Under `autonomy_level = "manual"`, **all operations require human approval** per the policy rules defined in this WP.
- Under `autonomy_level = "supervised"`, **destructive or high-impact operations require approval** per the policy rules.
- Under `autonomy_level = "full"`, **no approval required** per the policy rules, subject to tactical `ApprovalGate` checks.
- `Plan.approval_policy` may restrict or extend permissions beyond the Goal-level default; the policy rules define the resolution order.
- Escalation paths and approver roles are defined in the policy contract; runtime escalation is out of scope.

**What WP-44 does NOT do at runtime:**
- WP-44 does **not** add flags to `Decision.context`.
- WP-44 does **not** block or permit any operation.
- WP-44 does **not** change `ReasoningEngine` behavior.
- WP-44 does **not** change `ApprovalGate` behavior.
- WP-44 does **not** execute escalation or approval workflows.
- WP-44 defines the rules; a future WP implements enforcement.

### 6.2 Separation of Concerns

| Layer | Owns | Does NOT own |
|-------|------|--------------|
| `AutonomyPolicy` (new contract) | Policy interpretation rules, autonomy level definitions, approval requirements mapping — **specification only** | Runtime enforcement, UI, workflow, runtime blocking |
| `GoalManager` | Goal lifecycle, `autonomy_level` field storage | Policy enforcement, approval blocking |
| `PlanManager` | Plan lifecycle, `approval_policy` structure storage | Policy enforcement, approval blocking |
| `ReasoningEngine` | Reads autonomy policy as opaque context hints; unchanged behavior | Policy enforcement, approval blocking |
| `ApprovalGate` | Tactical destructive-operation detection | Goal-aware policy, strategic autonomy, policy enforcement |
| `TaskPlanner` | Mission creation from Decision + context | Plan mutation, autonomy policy enforcement |

### 6.3 Invariants

1. **Autonomy Policy is a contract only.** No runtime enforcement in this WP.
2. **ReasoningEngine does not enforce autonomy.** It may read policy hints; behavior unchanged.
3. **Goal/Plan schemas unchanged.** `autonomy_level` and `approval_policy` already exist; WP-44 defines their meaning.
4. **ApprovalGate unchanged.** Tactical enforcer remains independent and unchanged.
5. **No new public API endpoints** as an executive decision; deferred to future design.
6. **No database migration.** Policy interpretation is contract-only in this WP.

---

## 7. Acceptance Gates (Planning Level)

| Gate | Criterion | Verification |
|------|-----------|-------------|
| G1 | Goal/Plan Foundation closed and stable | No open defects in Goal/Plan chain |
| G2 | WP-43 Reasoning Depth closed and stable | No open defects in ReasoningEngine |
| G3 | WP-44 defines the policy contract only; runtime enforcement is absent | Document review + code inspection |
| G4 | ReasoningEngine behavior unchanged | Diff inspection |
| G5 | ApprovalGate behavior unchanged | Diff inspection |
| G6 | Goal/Plan schemas unchanged | Diff inspection |
| G7 | `autonomy_level` and `approval_policy` are contract inputs only; no runtime flags added to `Decision.context` | Code inspection |
| G8 | No database migration required | Document review |
| G9 | No changes to WP-34/WP-35 contracts | Contract review |
| G10 | No new public API endpoints as executive decision | Document review |

---

## 8. Planning Constraints

- **Plan Mode only.** No implementation.
- **Do not modify production code.**
- **Do not execute Autonomy Policy.**
- **Do not modify Goal/Plan Foundation.**
- **Do not modify WP-43.**
- **Do not reopen WP-30 to WP-35 or WP-34/WP-35.**
- **Do not create more than one WP.**
- **Do not invent additional WPs.**
- **Do not enter detailed implementation design.**
- **Do not modify Architecture Contract unless explicit conflict; if conflict, stop and write: `ARCHITECTURE CONTRACT CONFLICT`**

---

## 9. WP Identification

**WP Number:** WP-44 (next sequential after WP-43)
**WP Name:** Autonomy Policy
**Phase:** Phase 2 — Digital Export Manager (AI Layer Enhancement)

---

*Plan created: 2026-09-03*
*Author: Architecture Planning — Plan Mode*
*Next step: Implementation WP execution*

---

```
AUTONOMY POLICY WP PLANNED
```
