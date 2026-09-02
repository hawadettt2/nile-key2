# Goal / Plan Architecture Contract

**Purpose:** Define the formal architecture contract for `Goal` and `Plan` layers as the root cognitive gap in the DEM AI Architecture.

**Status:** Approved — Ready for Implementation WP  
**Authority:** PLAN.md Section 22 (Architecture Vision Statement)  
**Gap Reference:** AI Architecture PARTIALLY COMPLETE — Goal/Plan reasoning layers deferred per ENGINEERING_MEMORY.md Section 22.3

---

## 1. Purpose

### 1.1 Why DEM needs Goal and Plan

DEM today operates in **reactive routing** mode: user intent → keyword matching → Mission → Task → Execution. This works for single-step operations but cannot:

- Maintain strategic context across multiple sessions
- Decompose high-level business objectives into coordinated missions
- Express trade-offs between alternative strategies for the same goal
- Enforce consistent constraints across a campaign of missions

### 1.2 Difference from existing layers

| Layer | Role | Time Horizon | Scope |
|-------|------|--------------|-------|
| `Decision` | Select execution path for a single request | One request | Tactical |
| `Mission` | Execute a bounded set of tasks | Minutes to hours | Operational |
| `Goal` | Strategic objective the user wants to achieve | Hours to weeks | Strategic |
| `Plan` | Strategy to achieve a Goal, decomposed into Missions | Hours to weeks | Strategic → Operational |

**Key distinction:** `Decision` chooses **how** to fulfill a request. `Goal` defines **what** the user wants to achieve. `Plan` defines **how to achieve the Goal** through coordinated Missions.

`ExecutionPlanner` is NOT a substitute for `Plan`. `ExecutionPlanner` determines execution mode (sequential/parallel) for a Mission's tasks. `Plan` determines which Missions are needed, in what sequence, to fulfill a Goal.

---

## 2. Architecture Placement

### 2.1 Target location

```
backend/app/agent/
├── goal/
│   ├── __init__.py
│   ├── schema.py          # Goal schema
│   ├── manager.py         # Goal lifecycle management
│   └── repository.py      # Goal persistence interface
├── plan/
│   ├── __init__.py
│   ├── schema.py          # Plan schema
│   ├── planner.py         # Plan decomposition
│   └── repository.py      # Plan persistence interface
```

### 2.2 Relationship to existing layers

```
User Intent
    ↓
ReasoningEngine → Decision (existing)
    ↓
Goal (new) — strategic objective, persists across sessions
    ↓
Plan (new) — strategy decomposed into Missions
    ↓
Mission (existing) — executable unit
    ↓
Task (existing) — atomic work
    ↓
ExecutionPlan (existing) — execution mode
    ↓
ToolOrchestrator (existing) — actual execution
```

### 2.3 Placement rules

- `Goal` and `Plan` are **pure domain schemas + lifecycle managers**. No business logic.
- `Goal` does NOT call tools directly.
- `Plan` does NOT execute tasks.
- Both depend on `Memory` for context and `Knowledge` for constraints.
- Both are consumed by `TaskPlanner` to produce Missions.
- Neither replaces nor modifies `Decision`, `Mission`, `Task`, or `ExecutionPlan`.

---

## 3. Goal Contract

### 3.1 Purpose

A `Goal` represents a **strategic business objective** that the user wants to achieve. Goals outlive single sessions and missions. A single Goal may spawn multiple Plans over time.

### 3.2 Goal Schema (contract)

```python
class Goal(BaseModel):
    goal_id: str                    # UUID, immutable
    user_id: int                    # Owner
    session_id: str                 # Originating session
    objective: str                  # Free-text objective statement
    scope: Dict[str, Any]           # Bounded scope: markets, products, timeframes
    constraints: List[Dict[str, Any]]  # Standing orders, regulations, preferences
    stakeholders: List[Dict[str, Any]] # Who must approve / be informed
    autonomy_level: str             # "full", "supervised", "manual"
    status: str                     # "active", "paused", "completed", "abandoned"
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    parent_goal_id: Optional[str]   # For goal hierarchies
    metadata: Dict[str, Any]        # Implementation detail — free-form
```

### 3.3 Contract rules

| Field | Contract stability | Notes |
|-------|-------------------|-------|
| `goal_id`, `user_id`, `objective`, `status`, `created_at` | **STABLE** | Must not change after creation |
| `scope`, `constraints`, `stakeholders`, `autonomy_level` | **STABLE** | May be updated only via explicit transition |
| `parent_goal_id` | **STABLE** | Set once, never changed |
| `metadata` | **UNSTABLE** | Implementation detail, no contract guarantee |

### 3.4 Lifecycle / Status

```
active → paused → active
active → completed
active → abandoned
paused → active
paused → abandoned
```

Transitions are triggered by:
- `active → completed`: All associated Plans reached terminal state
- `active → abandoned`: User or policy aborts
- `active → paused`: User defers

### 3.5 Ownership

- `user_id` is the single owner.
- `stakeholders` are informational only at the Goal level. Approval happens at Plan/Mission level.
- Goal does NOT enforce approval. Approval is a Plan/Mission concern.

### 3.6 What Goal must NOT do

- Goal must NOT call tools.
- Goal must NOT produce Decisions.
- Goal must NOT execute Missions.
- Goal must NOT contain business logic.
- Goal must NOT couple to external providers.

---

## 4. Plan Contract

### 4.1 Purpose

A `Plan` is a **strategy to achieve a specific Goal**. A Plan decomposes into ordered Missions. Multiple Plans may exist for the same Goal over time (re-planning).

### 4.2 Relationship to Goal

- One Goal → Many Plans (over time)
- One Plan → Exactly one Goal
- A Plan is the **current** strategy for its Goal. Superseded Plans remain for audit.
- Plan does NOT outlive its Goal. When Goal is completed/abandoned, associated Plans become terminal.

### 4.3 Plan Schema (contract)

```python
class Plan(BaseModel):
    plan_id: str                    # UUID, immutable
    goal_id: str                    # Required — parent Goal
    user_id: int                    # Owner (inherited from Goal)
    session_id: str                 # Originating session
    objective: str                  # Inherited from Goal at creation
    missions: List[str]             # Ordered mission_ids
    dependencies: List[Tuple[str, str]]  # (predecessor_mission_id, successor_mission_id)
    constraints: List[Dict[str, Any]]     # Inherited + Plan-specific
    approval_policy: Dict[str, Any]       # Hooks for autonomy — structure only
    fallback_strategy: Dict[str, Any]     # What to do if a Mission fails
    status: str                     # "draft", "active", "executing", "completed", "failed", "abandoned"
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]        # Implementation detail
```

### 4.4 Contract rules

| Field | Contract stability | Notes |
|-------|-------------------|-------|
| `plan_id`, `goal_id`, `user_id`, `missions`, `dependencies`, `status`, `created_at` | **STABLE** | Must not change after creation |
| `constraints`, `approval_policy`, `fallback_strategy` | **STABLE** | Set at creation, may be extended but not removed |
| `metadata` | **UNSTABLE** | Implementation detail |

### 4.5 Ordered steps/tasks

- `missions` is an **ordered list** of `mission_id` strings.
- `dependencies` captures explicit precedence constraints between missions.
- Execution order is derived from `missions` list order + `dependencies`.
- A Mission may appear in only one active Plan at a time (enforced by TaskPlanner, not by Goal/Plan).

### 4.6 Approval / Autonomy hooks

- `approval_policy` is a **structure only**. It records:
  - Which mission types require approval
  - Who can approve
  - Escalation path
- Autonomy Policy design is **out of scope** for this contract.
- Goal/Plan stores the policy; Execution Engine enforces it.

### 4.7 What Plan must NOT do

- Plan must NOT execute Missions.
- Plan must NOT call tools.
- Plan must NOT produce Decisions.
- Plan must NOT contain business logic.
- Plan must NOT couple to external providers.

---

## 4.8 Goal / Plan Repository Contract

### 4.8.1 Purpose

Goal and Plan state requires **durable domain persistence** with structured queries, lifecycle operations, and relationship management. This contract defines the repository responsibilities independent of `MemoryProvider`.

### 4.8.2 Goal Repository responsibilities

| Operation | Description |
|-----------|-------------|
| `create_goal(goal: Goal)` | Persist a new Goal |
| `get_goal(goal_id: str)` | Retrieve Goal by ID |
| `list_goals(user_id: int, filters: Dict)` | List Goals for a user with optional filters |
| `update_goal(goal_id: str, updates: Dict)` | Apply allowed updates to Goal fields |
| `archive_goal(goal_id: str)` | Mark Goal as abandoned/completed |
| `get_active_goals(user_id: int)` | Get all active Goals for a user |
| `get_goal_hierarchy(goal_id: str)` | Get Goal with its children via `parent_goal_id` |

### 4.8.3 Plan Repository responsibilities

| Operation | Description |
|-----------|-------------|
| `create_plan(plan: Plan)` | Persist a new Plan |
| `get_plan(plan_id: str)` | Retrieve Plan by ID |
| `list_plans(goal_id: str)` | List all Plans for a Goal |
| `update_plan(plan_id: str, updates: Dict)` | Apply allowed updates to Plan fields |
| `append_mission(plan_id: str, mission_id: str)` | Add a Mission to Plan.missions |
| `get_active_plan(goal_id: str)` | Get the current active Plan for a Goal |
| `get_plan_missions(plan_id: str)` | Get ordered Mission list for a Plan |
| `archive_plan(plan_id: str)` | Mark Plan as completed/failed/abandoned |

### 4.8.4 Contract rules

- Goal Repository and Plan Repository are **separate contracts**. They may share a persistence backend but must not share implementation details.
- `Plan.missions` is mutated **only** via `PlanRepository.append_mission()`. No other layer may mutate Plan state directly.
- Queries MUST respect ownership: `user_id` is the owner filter for all Goal/Plan operations.
- Lifecycle transitions are validated by the repository against the state machine defined in Section 5.
- This contract defines **operations**, not database schema. Implementation may use dedicated tables, `agent_sessions.context`, or any other durable storage.

### 4.8.5 What Repository must NOT do

- Repository must NOT call tools.
- Repository must NOT produce Decisions.
- Repository must NOT execute Missions.
- Repository must NOT contain business logic.
- Repository must NOT couple to external providers.

---

## 5. Lifecycle

### 5.1 Full chain

```
Goal
  ↓ created (user or system)
Plan
  ↓ decomposed
Mission (existing)
  ↓ planned
Task (existing)
  ↓ executed
ExecutionPlan (existing)
  ↓ invoked
Tool (existing)
```

### 5.2 Transitions

| From | To | Trigger | Responsible layer |
|------|----|---------|-------------------|
| — | Goal(active) | User creates strategic objective | `GoalManager` |
| Goal(active) | Plan(draft) | Strategy formulated | `PlanPlanner` |
| Plan(draft) | Plan(active) | User approves strategy | `PlanManager` |
| Plan(active) | Plan(executing) | First Mission starts | `TaskPlanner` |
| Plan(executing) | Plan(completed) | All Missions completed | `TaskPlanner` |
| Plan(executing) | Plan(failed) | Mission fails, no fallback | `TaskPlanner` |
| Plan(executing) | Plan(abandoned) | User aborts or Goal abandoned | `PlanManager` |
| Goal(active) | Goal(completed) | All Plans terminal + user confirms | `GoalManager` |
| Goal(active) | Goal(abandoned) | User aborts | `GoalManager` |

### 5.3 Responsibility matrix

| Layer | Owns | Does not own |
|-------|------|--------------|
| `GoalManager` | Goal lifecycle, Goal→Plan initiation, Goal status | Mission execution, tool invocation, Plan mutation |
| `PlanManager` | Plan lifecycle, Plan.missions list, Plan status, Plan dependencies | Goal creation, Mission execution, tool invocation |
| `PlanPlanner` | Plan creation from Goal + Decision context | Goal creation, Mission execution, Plan persistence |
| `TaskPlanner` (existing) | Mission creation, Task creation, ExecutionPlan creation from Decision + Plan context | Goal/Plan lifecycle, Plan persistence, Plan.missions mutation |
| `ToolOrchestrator` (existing) | Task execution | Goal/Plan/Decision logic, Plan mutation |

---

## 6. Integration Contracts

### 6.1 Goal/Plan ↔ ReasoningEngine

**Interface:** `ReasoningEngine` receives a `Goal` (or `goal_id`) in its request context.

**Contract:**
- When `context` contains `goal_id`, ReasoningEngine MUST consider Goal scope and constraints in candidate evaluation.
- ReasoningEngine MUST NOT modify Goal or Plan.
- ReasoningEngine returns `Decision` with optional `goal_id` and `plan_id` in `context` if operating within an active Goal/Plan.

**Invariant:** Decision is still tactical. Goal/Plan are strategic. Decision does not replace Goal/Plan.

### 6.2 Goal/Plan ↔ Decision

**Interface:** `Decision.context` may contain `goal_id` and `plan_id`.

**Contract:**
- `TaskPlanner` reads `goal_id` and `plan_id` from `Decision.context`.
- If `goal_id` is present, `TaskPlanner` returns the new Mission with `goal_id` and `plan_id` in its context. The caller or `PlanManager` is responsible for appending the Mission to `Plan.missions`.
- If `plan_id` is present but `goal_id` is absent, this is an error — Plan implies Goal.
- Decision does NOT create Goal or Plan. That is `GoalManager`/`PlanPlanner` responsibility.

### 6.3 Goal/Plan ↔ TaskPlanner

**Interface:** `TaskPlanner.plan(decision, session_context)` receives enriched context.

**Contract:**
- `session_context` may contain `goal_id`, `plan_id`, `goal_constraints`, `plan_constraints`.
- `TaskPlanner` applies `constraints` to Mission creation.
- `TaskPlanner` does NOT update `Plan.missions` or mutate Plan state in any way.
- `TaskPlanner` returns the created Mission with `goal_id` and `plan_id` embedded in its context. The caller or `PlanManager` is responsible for Plan mutation via `PlanRepository`.
- `TaskPlanner` does NOT create or modify Goal.

### 6.4 Goal/Plan ↔ ExecutionPlanner

**Interface:** `ExecutionPlanner` is unchanged.

**Contract:**
- ExecutionPlanner receives Mission (existing contract).
- Goal/Plan do not affect execution mode selection.
- Future: ExecutionPlanner may read `fallback_strategy` from Plan, but this is out of scope for initial implementation.

### 6.5 Goal/Plan ↔ Memory

**Interface:** `MemoryProvider` (existing ABC).

**Contract:**
- `MemoryProvider` is **NOT** used for Goal/Plan state persistence.
- `MemoryProvider` remains responsible for long-term/contextual institutional memory only.
- `SessionManager.enrich_context()` MAY add `goal_id` and `plan_id` references to session context for runtime enrichment.
- Memory graceful degradation applies to context enrichment only: if Memory is unavailable, Goal/Plan operate with session context only.
- Goal/Plan state durability is the responsibility of the Persistence Repository, not MemoryProvider.

### 6.6 Goal/Plan ↔ Knowledge

**Interface:** `KnowledgeProvider` (existing ABC) + `KnowledgeOrchestrator` (existing).

**Contract:**
- Goal creation may query Knowledge for relevant constraints (regulations, procedures).
- Plan creation may query Knowledge for best practices and precedence rules.
- Goal/Plan do NOT modify Knowledge providers or schemas.
- Knowledge queries from Goal/Plan use the same `KnowledgeProviderRegistry` as ReasoningEngine.

### 6.7 Goal/Plan ↔ External Research

**Interface:** `ResearchOrchestrator` (existing).

**Contract:**
- Plan may trigger External Research as part of mission sequencing (e.g., "research market before filing customs").
- Research integration happens at Plan level via explicit mission type `RESEARCH` in the missions list.
- Goal/Plan do NOT modify Research schemas, stages, or orchestration logic.
- This preserves the WP-34/WP-35 boundary: Goal/Plan are consumers of Research, not extenders.

---

## 7. Future Integration Boundaries

### 7.1 Reasoning depth

- Future: Goal decomposition into sub-goals.
- Current contract: Goal has `parent_goal_id` for hierarchy, but decomposition logic is deferred.
- ReasoningEngine future enhancement: Goal-aware reasoning that considers Goal progress, not just current intent.

### 7.2 Autonomy

- Future: AutonomyPolicy determines which Goal/Plan operations require human approval.
- Current contract: `autonomy_level` field on Goal is a **label only**. Enforcement is deferred.
- `approval_policy` on Plan is a **structure only**. Enforcement is deferred.

### 7.3 Business-facing AI response

- Future: Avatar renders Goal progress, Plan status, Mission outcomes.
- Current contract: Goal/Plan expose `status` and `objective` fields. Avatar integration is deferred.
- Goal/Plan do NOT produce UI markup or audio streams.

---

## 8. Architectural Invariants

1. **No Business Logic inside Goal/Plan contracts.** Validation only.
2. **No bypass of Mission/Task execution architecture.** Goal/Plan decompose into Missions, which follow existing lifecycle.
3. **Goal/Plan do NOT replace Decision Engine.** Decision remains the tactical output of ReasoningEngine.
4. **No direct coupling with providers.** Goal/Plan interact with Knowledge, Memory, and Research only through existing interfaces.
5. **No change to WP-34/WP-35.** External Research and Knowledge Ingestion contracts remain untouched.
6. **No modification to existing schemas.** `Decision`, `Mission`, `Task`, `ExecutionPlan` schemas are not changed.
7. **Goal/Plan state is NOT stored in `MemoryProvider`.** `MemoryProvider` remains for long-term/contextual institutional memory only. Goal/Plan state is owned by the Persistence Repository.
8. **`TaskPlanner` does NOT own Plan lifecycle.** `TaskPlanner` creates Missions only. `PlanManager` owns Plan state, including `Plan.missions`.
9. **`PlanManager` is the sole owner of `Plan.missions`.** No layer other than `PlanManager` may mutate Plan state. `TaskPlanner` returns Missions; the caller or `PlanManager` appends them to the Plan.
10. **Persistence is a separate contract from Memory.** Goal/Plan durability is the responsibility of the Repository/Persistence Contract, not `MemoryProvider`.

---

## 9. Non-Goals

- **No Code.** This document is a contract only.
- **No implementation.** No classes, no files, no migrations.
- **No Reasoning redesign.** ReasoningEngine remains unchanged in this contract.
- **No Autonomy Policy.** Autonomy boundaries are noted as future integration, not designed here.
- **No Business Answer layer.** Avatar and Business Answer are deferred.
- **No Multi-agent coordination.** Out of scope.
- **No database migration.** Persistence is an implementation concern.
- **No reopening WP-30 through WP-35.** All existing WPs remain closed.

---

## 10. Acceptance Criteria

These criteria are used to validate the Goal/Plan Architecture Contract before any Implementation WP begins.

| # | Criterion | Verification |
|---|-----------|-------------|
| AC-1 | Goal schema is stable and immutable where marked | Schema review |
| AC-2 | Plan schema references Goal via stable `goal_id` | Schema review |
| AC-3 | Lifecycle transitions are unambiguous and finite | State machine review |
| AC-4 | Goal/Plan do not call tools or providers directly | Code inspection |
| AC-5 | Goal/Plan integrate with ReasoningEngine through `context` only | Interface review |
| AC-6 | `TaskPlanner` creates Missions only and does NOT mutate Plan state | Code inspection |
| AC-7 | Memory integration uses `MemoryProvider` for contextual memory only; Goal/Plan state is NOT stored in Memory | Interface review |
| AC-8 | Persistence Repository is defined as the owner of Goal/Plan durable state | Document review |
| AC-9 | Knowledge integration uses existing `KnowledgeProviderRegistry` | Interface review |
| AC-10 | Research integration does not modify WP-34/WP-35 contracts | Contract review |
| AC-11 | Existing schemas (`Decision`, `Mission`, `Task`, `ExecutionPlan`) are not modified | Diff inspection |
| AC-12 | Autonomy and Business Answer are deferred, not designed | Document review |
| AC-13 | `PlanManager` is the sole owner of `Plan.missions` mutation | Document review |
| AC-14 | No database migration is required by this contract | Document review |

---

## 11. Open Questions for Implementation WP

These questions are **out of scope** for this contract but must be resolved in the Implementation WP:

1. Should Goal/Plan state be stored in dedicated tables, `agent_sessions.context` (JSON), or another persistence mechanism?
2. What is the maximum depth of Goal hierarchy (`parent_goal_id`)?
3. How are superseded Plans marked and retrieved for audit?
4. What is the maximum number of Missions per Plan?
5. How does Goal completion get determined — explicit user action or automatic when all Plans complete?
6. What is the exact API surface for Goal/Plan — new routers, extension of existing DEM router, or internal-only?

---

*Contract created: 2026-09-02*  
*Author: Architecture Planning — Forensic Audit Mode*  
*Next step: Implementation WP for Goal/Plan foundation*

---

```
GOAL/PLAN CONTRACT APPROVED FOR IMPLEMENTATION
```
