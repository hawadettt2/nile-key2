# Goal / Plan Foundation — Implementation WP Specification

**Purpose:** Implementation specification for Goal/Plan Foundation WP  
**Authority:** `.kilo/plans/1788376865110-goal-plan-architecture-contract.md` (Approved)  
**Scope:** Goal domain, Plan domain, lifecycle managers, repositories, DEM chain integration

---

## 1. Implementation Scope

| Domain | Components | Responsibility |
|--------|-----------|----------------|
| Goal | schema, manager, repository | Strategic objective lifecycle |
| Plan | schema, planner, manager, repository | Strategy decomposition, mission sequencing |
| Persistence | GoalRepository, PlanRepository | Durable state via dedicated tables |
| Integration | ReasoningEngine, TaskPlanner, DEM router | Minimal wiring without redesign |

**Out of scope:** Reasoning redesign, Autonomy Policy, Business Answer layer, Multi-agent, new providers, WP-34/WP-35 changes.

---

## 2. Files

### 2.1 New files

```
backend/app/agent/goal/
├── __init__.py
├── schema.py          # Goal Pydantic schema
├── manager.py         # GoalManager lifecycle
└── repository.py      # GoalRepository interface + SQLite implementation

backend/app/agent/plan/
├── __init__.py
├── schema.py          # Plan Pydantic schema
├── planner.py         # PlanPlanner decomposition
├── manager.py         # PlanManager lifecycle
└── repository.py      # PlanRepository interface + SQLite implementation

backend/tests/agent/
├── test_goal.py
├── test_goal_manager.py
├── test_goal_repository.py
├── test_plan.py
├── test_plan_planner.py
├── test_plan_manager.py
├── test_plan_repository.py
└── test_goal_plan_chain.py
```

### 2.2 Modified files

| File | Change |
|------|--------|
| `backend/app/core/database.py` | Add `agent_goals` and `agent_plans` tables in `_create_tables()` |
| `backend/app/agent/mission_planner/planner.py` | Read `goal_id`/`plan_id` from `session_context`; embed in Mission context; do NOT mutate Plan |
| `backend/app/routers/digital_export_manager.py` | Add internal Goal/Plan creation helper inside existing `create_mission` handler; detect strategic objective, create Goal/Plan, pass `goal_id`/`plan_id` to existing mission flow; endpoint contract unchanged |
| `backend/app/agent/schemas/decision.py` | No change — `context` is `Dict[str, Any]`, sufficient for `goal_id`/`plan_id` |

---

## 3. Goal Design

### 3.1 Schema

```python
class Goal(BaseModel):
    goal_id: str                    # UUID, immutable
    user_id: int                    # Owner
    session_id: str                 # Originating session
    objective: str                  # Free-text objective
    scope: Dict[str, Any]           # Markets, products, timeframes
    constraints: List[Dict[str, Any]]  # Standing orders, regulations
    stakeholders: List[Dict[str, Any]] # Informational only
    autonomy_level: str             # "full", "supervised", "manual"
    status: str                     # "active", "paused", "completed", "abandoned"
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    parent_goal_id: Optional[str]   # Hierarchy
    metadata: Dict[str, Any]        # Implementation detail
```

### 3.2 GoalManager

**File:** `backend/app/agent/goal/manager.py`

**Responsibilities:**
- Create Goal from user request or system trigger
- Transition Goal status (active → paused/completed/abandoned)
- Enforce ownership: all operations filter by `user_id`
- Orchestrate Goal → Plan creation: call `PlanPlanner.create_plan()` then `PlanManager.activate_plan()`
- Own Goal lifecycle end-to-end

**Key methods:**
- `create_goal(user_id, session_id, objective, scope, ...) -> Goal`
- `get_goal(goal_id, user_id) -> Goal`
- `list_goals(user_id, filters) -> List[Goal]`
- `update_goal(goal_id, user_id, updates) -> Goal`
- `complete_goal(goal_id, user_id) -> Goal`
- `abandon_goal(goal_id, user_id) -> Goal`
- `create_plan_for_goal(goal_id, user_id, session_id) -> Plan` — convenience orchestration: calls `PlanPlanner.create_plan()` then `PlanManager.activate_plan()`
- `create_plan_for_goal(goal_id, user_id, session_id) -> Plan` — convenience method that calls PlanPlanner + PlanManager

**What GoalManager must NOT do:**
- Call tools
- Produce Decisions
- Execute Missions
- Mutate Plan state after creation
- Contain business logic

### 3.3 GoalRepository

**File:** `backend/app/agent/goal/repository.py`

**Interface:**
- `create(goal: Goal) -> Goal`
- `get(goal_id: str) -> Optional[Goal]`
- `list(user_id: int, filters: Dict) -> List[Goal]`
- `update(goal_id: str, updates: Dict) -> Optional[Goal]`
- `archive(goal_id: str, status: str) -> bool`
- `get_active_goals(user_id: int) -> List[Goal]`

**Implementation:** SQLite via `get_db()` raw SQL, following project pattern.

---

## 4. Plan Design

### 4.1 Schema

```python
class Plan(BaseModel):
    plan_id: str                    # UUID, immutable
    goal_id: str                    # Required — parent Goal
    user_id: int                    # Owner (inherited from Goal)
    session_id: str                 # Originating session
    objective: str                  # Inherited from Goal at creation
    missions: List[str]             # Ordered mission_ids
    dependencies: List[Tuple[str, str]]  # (predecessor, successor)
    constraints: List[Dict[str, Any]]     # Inherited + Plan-specific
    approval_policy: Dict[str, Any]       # Structure only
    fallback_strategy: Dict[str, Any]     # Structure only
    status: str                     # "draft", "active", "executing", "completed", "failed", "abandoned"
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]        # Implementation detail
```

### 4.2 PlanPlanner

**File:** `backend/app/agent/plan/planner.py`

**Purpose in Foundation:** Pure creation utility — builds a Plan object from a Goal.

**Called by:** `GoalManager` (preferred) or DEM router directly.

**Responsibilities:**
- Receive `goal_id`, `user_id`, `session_id`
- Load Goal via `GoalRepository` (not GoalManager, to avoid circular dependency)
- Create `Plan` with:
  - `goal_id` from parent Goal
  - `objective` copied from Goal at creation time
  - Initial `missions` list empty
  - Initial `dependencies` list empty
  - `constraints` inherited from Goal
  - `approval_policy` and `fallback_strategy` as empty structures
  - `status = "draft"`
- Return Plan object (does NOT persist it)

**What PlanPlanner must NOT do:**
- Persist Plan (that's PlanRepository's job)
- Activate Plan (that's PlanManager's job)
- Call ReasoningEngine
- Call TaskPlanner
- Execute Missions
- Query Knowledge or Research
- Contain business logic or strategic reasoning
- Mutate Goal state

### 4.3 PlanManager

**File:** `backend/app/agent/plan/manager.py`

**Responsibilities:**
- Own Plan lifecycle (draft → active → executing → completed/failed/abandoned)
- Own `Plan.missions` mutation via `PlanRepository.append_mission()`
- Track superseded Plans
- Enforce ownership via `user_id`

**Key methods:**
- `create_plan(goal_id, user_id, session_id, ...) -> Plan`
- `get_plan(plan_id, user_id) -> Plan`
- `list_plans(goal_id, user_id) -> List[Plan]`
- `activate_plan(plan_id, user_id) -> Plan`
- `append_mission(plan_id, user_id, mission_id) -> Plan`
- `complete_plan(plan_id, user_id) -> Plan`
- `abandon_plan(plan_id, user_id) -> Plan`
- `get_active_plan(goal_id, user_id) -> Optional[Plan]`

**What PlanManager must NOT do:**
- Create Missions
- Call tools
- Produce Decisions
- Contain business logic

### 4.4 PlanRepository

**File:** `backend/app/agent/plan/repository.py`

**Interface:**
- `create(plan: Plan) -> Plan`
- `get(plan_id: str) -> Optional[Plan]`
- `list(goal_id: str) -> List[Plan]`
- `update(plan_id: str, updates: Dict) -> Optional[Plan]`
- `append_mission(plan_id: str, mission_id: str) -> bool`
- `get_active_plan(goal_id: str) -> Optional[Plan]`
- `get_plan_missions(plan_id: str) -> List[str]`
- `archive(plan_id: str, status: str) -> bool`

**Implementation:** SQLite via `get_db()` raw SQL.

---

## 5. Persistence Strategy

### 5.1 Storage mechanism

**Decision: Dedicated tables via `init_db()` — no migration required.**

**Rationale:**
- `agent_sessions.context` is JSON and not suitable for structured Goal/Plan queries
- `MemoryProvider` is excluded by contract (Decision 1)
- Adding tables via `init_db()` follows existing project pattern (no Alembic migration needed for new tables)
- Goal/Plan outlive sessions and require durable, queryable state

### 5.2 Tables

**`agent_goals`:**
```sql
CREATE TABLE IF NOT EXISTS agent_goals (
    goal_id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    objective TEXT NOT NULL,
    scope TEXT,
    constraints TEXT,
    stakeholders TEXT,
    autonomy_level TEXT DEFAULT 'supervised',
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    parent_goal_id TEXT,
    metadata TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
)
```

**`agent_plans`:**
```sql
CREATE TABLE IF NOT EXISTS agent_plans (
    plan_id TEXT PRIMARY KEY,
    goal_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    objective TEXT NOT NULL,
    missions TEXT,
    dependencies TEXT,
    constraints TEXT,
    approval_policy TEXT,
    fallback_strategy TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (goal_id) REFERENCES agent_goals(goal_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
)
```

**Indexes:**
```sql
CREATE INDEX IF NOT EXISTS idx_agent_goals_user_id ON agent_goals(user_id)
CREATE INDEX IF NOT EXISTS idx_agent_goals_status ON agent_goals(status)
CREATE INDEX IF NOT EXISTS idx_agent_plans_goal_id ON agent_plans(goal_id)
CREATE INDEX IF NOT EXISTS idx_agent_plans_user_id ON agent_plans(user_id)
CREATE INDEX IF NOT EXISTS idx_agent_plans_status ON agent_plans(status)
```

### 5.3 Why no migration

- Tables use `CREATE TABLE IF NOT EXISTS`
- `init_db()` runs on every startup
- Existing databases will create tables on next startup without data loss
- No Alembic migration needed (matches project pattern for new tables)

---

## 6. Integration Sequence

### 6.1 Two distinct flows

**Flow A — Goal/Plan creation (internal, no new public API):**

```
User intent with strategic objective
    ↓
POST /api/v1/digital-export-manager/missions  (existing endpoint)
    ↓
DEM router internal helper detects strategic objective
    ↓
GoalManager.create_goal(user_id, session_id, objective, scope, ...) → Goal persisted
    ↓
PlanPlanner.create_plan(goal_id, user_id, session_id) → Plan(draft)
    ↓
PlanManager.activate_plan(plan_id, user_id) → Plan(active)
    ↓
[existing mission flow continues with goal_id/plan_id in context]
```

**Detection mechanism:**
- Strategic objective detection happens INSIDE the existing `create_mission` handler
- No new endpoint, no new public API
- Detection is based on explicit intent signals (e.g., keywords, mission_type, or payload flags)
- Once Goal/Plan are created, the existing mission flow proceeds normally

**Flow B — Mission execution within active Goal/Plan (ongoing):**

```
User intent
    ↓
ReasoningEngine.reason() → Decision (with goal_id/plan_id in context if active Goal/Plan exists)
    ↓
TaskPlanner.plan(decision, session_context) → Mission (with goal_id/plan_id in Mission.context)
    ↓
PlanManager.append_mission(plan_id, user_id, mission_id) → Plan.missions updated
    ↓
ExecutionPlanner.plan(mission) → ExecutionPlan
    ↓
ToolOrchestrator.execute() → Tool results
    ↓
PlanManager.complete_plan() or continue
```

### 6.2 Relationship between flows

- Flow A establishes the strategic context (Goal + active Plan) INSIDE the existing mission creation endpoint
- Flow B operates within that context
- ReasoningEngine does NOT create Goal/Plan; it only references existing ones via `context`
- PlanPlanner does NOT depend on Decision; it creates Plan from Goal alone
- TaskPlanner does NOT create Plan; it creates Mission and returns it with Goal/Plan references

### 6.2.1 Goal/Plan orchestration ownership

| Who | Does | Does NOT |
|-----|------|----------|
| `GoalManager` | Orchestrates Goal → Plan creation: calls `PlanPlanner.create_plan()` then `PlanManager.activate_plan()` | Create Missions, execute tools |
| `PlanPlanner` | Creates Plan object from Goal (one-time) | Persist Plan, activate Plan, mutate Goal |
| `PlanManager` | Owns Plan lifecycle, activates Plan, mutates `Plan.missions` | Create Plan object, create Missions |

**No implicit coupling:** PlanPlanner is a pure function-like utility. GoalManager owns the orchestration between Goal and Plan.

### 6.3 Integration points (minimal)

| Integration | What changes | What stays |
|-------------|-------------|------------|
| ReasoningEngine | Receives `goal_id`/`plan_id` in `request.context` if present; does NOT query Goal/Plan managers | Existing candidate scoring, LLM enhancement unchanged |
| Decision | `context` dict may include `goal_id`/`plan_id` | Schema unchanged |
| TaskPlanner | Reads `goal_id`/`plan_id` from `session_context`; embeds in `Mission.context`; does NOT mutate Plan | Mission/Task/ExecutionPlan creation unchanged |
| PlanManager | Appends Mission to `Plan.missions` via repository | Does NOT create Missions |
| ExecutionPlanner | Unchanged | Receives Mission only |
| DEM router | Adds internal Goal/Plan creation helper inside existing `create_mission` handler | Existing endpoint contract unchanged |

---

## 7. Reasoning Integration

**Context-only. No lifecycle, no orchestration, no active querying.**

- `ReasoningEngine.reason()` receives `request.context` which MAY contain `goal_id` and `plan_id`
- If present, ReasoningEngine treats these as **opaque context hints** for candidate evaluation
- ReasoningEngine does NOT call `GoalManager`, `PlanManager`, `GoalRepository`, or `PlanRepository`
- ReasoningEngine does NOT validate Goal/Plan existence or status
- ReasoningEngine returns `Decision` with `goal_id`/`plan_id` preserved in `context` if they were present in input
- No changes to `Decision` schema
- No new responsibilities added to ReasoningEngine

**Interface change:**
```python
class ReasoningEngine:
    def __init__(self, knowledge_provider_registry=None, memory_provider=None, approval_gate=None, knowledge_provider=None, llm_registry=None):
        # Existing parameters unchanged
        # NO goal_manager, NO plan_manager parameters
```

---

## 8. Memory Integration

**Context enrichment only:**

- `SessionManager.enrich_context()` MAY add `goal_id` and `plan_id` to session context
- `MemoryProvider` is NOT used for Goal/Plan state persistence
- Goal/Plan state durability is the responsibility of `GoalRepository` and `PlanRepository`
- Memory graceful degradation applies to context enrichment only: if Memory is unavailable, Goal/Plan operate with session context only

---

## 9. TaskPlanner Integration

**Read-only Plan context, Mission creation only:**

### 9.1 Constraints path: Plan → TaskPlanner

**Exact path (no direct repository access from TaskPlanner):**

1. `PlanManager` owns `Plan.constraints` in `PlanRepository`
2. DEM router (or caller) reads Plan via `PlanManager.get_active_plan(goal_id, user_id)` or `PlanManager.get_plan(plan_id, user_id)`
3. DEM router extracts `constraints` from the Plan object
4. DEM router passes constraints in `session_context` under key `plan_constraints` (and/or `goal_constraints` from Goal)
5. `TaskPlanner.plan(decision, session_context)` reads `plan_constraints` and `goal_constraints` from `session_context`
6. `TaskPlanner` applies these constraints to Mission creation (e.g., filtering excluded tools, setting priority)
7. `TaskPlanner` does NOT access `PlanRepository`, `GoalRepository`, or any persistence layer

**Code path:**
```
PlanRepository.append_mission(plan_id, mission_id)
    ↓
PlanManager returns updated Plan (with constraints)
    ↓
DEM router extracts Plan.constraints
    ↓
session_context["plan_constraints"] = Plan.constraints
    ↓
TaskPlanner.plan(decision, session_context)
    ↓
TaskPlanner applies constraints to Mission creation
```

### 9.2 What TaskPlanner must NOT do

- TaskPlanner must NOT access PlanRepository
- TaskPlanner must NOT access GoalRepository
- TaskPlanner must NOT call PlanManager
- TaskPlanner must NOT mutate Plan.missions
- TaskPlanner must NOT create or modify Goal/Plan

### 9.3 Mission context embedding

- `TaskPlanner` returns `Mission` with `goal_id` and `plan_id` embedded in `Mission.context`
- `Mission.context` is a `Dict[str, Any]` — no schema change required
- DEM router uses these embedded references to call `PlanManager.append_mission()`

---

## 9.1 Goal → Plan → Mission Boundary

**Separation of concerns:**

| Layer | Owns | Does NOT own |
|-------|------|--------------|
| `GoalManager` | Goal lifecycle, Goal status, Goal→Plan initiation | Plan mutation, Mission creation, tool execution |
| `PlanManager` | Plan lifecycle, `Plan.missions` list, Plan status | Goal creation, Mission creation, tool execution |
| `PlanPlanner` | Creating Plan from Goal (one-time) | Goal lifecycle, Plan mutation after creation, Mission creation |
| `TaskPlanner` | Mission creation, Task creation, ExecutionPlan creation | Plan mutation, Goal lifecycle, tool execution |
| `ExecutionPlanner` | Execution mode selection within Mission | Goal/Plan lifecycle, Mission creation |
| `ToolOrchestrator` | Tool execution, retry, audit | Goal/Plan/Mission/Task creation |

**Key invariants:**
- Goal/Plan creation is a separate flow from Mission execution
- PlanPlanner creates Plan; it does not execute or mutate Plan after creation
- TaskPlanner creates Mission; it does not mutate Plan.missions
- PlanManager is the ONLY layer that mutates Plan.missions via `PlanRepository.append_mission()`
- No layer bypasses Mission/Task architecture to execute tools directly

---

## 10. API Decision

**Internal-only for this WP.**

**Rationale:**
- Goal/Plan are orchestration constructs, not direct user-facing resources at this stage
- User interacts through existing `/api/v1/digital-export-manager/missions` endpoint
- Goal/Plan creation is triggered implicitly when a mission is created with strategic context
- Future: read-only status endpoints (`/goals/{id}`, `/plans/{id}`) can be added in a subsequent WP

**No new public API endpoints in this WP.**

---

## 11. Authorization / Ownership

**Ownership model:**

- `user_id` is the single owner field on both Goal and Plan
- All repository queries filter by `user_id`
- Plan inherits `user_id` from Goal at creation
- No cross-user Goal/Plan access is possible through repository
- DEM router already enforces RBAC via `require_role(INTERNAL_ROLES)`

**Enforcement:**
- `GoalRepository` and `PlanRepository` include `user_id` in all WHERE clauses
- `GoalManager` and `PlanManager` pass `user_id` from authenticated user
- No soft-delete or sharing mechanism in this WP

---

## 12. Testing Strategy

### 12.1 Unit tests

| Component | Tests |
|-----------|-------|
| Goal schema | Validation, immutable fields |
| GoalManager | Create, get, list, update, complete, abandon, ownership enforcement |
| GoalRepository | CRUD, queries (active goals, hierarchy) |
| Plan schema | Validation, immutable fields |
| PlanPlanner | Create plan from goal, decomposition, constraints inheritance |
| PlanManager | Create, activate, append_mission, complete, abandon, ownership enforcement |
| PlanRepository | CRUD, append_mission, get_active_plan, get_plan_missions |

### 12.2 Integration tests

| Scenario | Test |
|----------|------|
| Goal → Plan | Create Goal, create Plan, verify relationship |
| Plan → Mission | Create Plan, create Mission via TaskPlanner, append to Plan |
| Goal/Plan + Memory | Session enrichment includes goal_id/plan_id; no Goal/Plan state in Memory |
| Goal/Plan + Reasoning | Decision context includes goal_id/plan_id; ReasoningEngine does not mutate Goal/Plan |
| Ownership | User A cannot access User B's Goal/Plan |
| Lifecycle | Goal active → Plan draft → active → executing → completed; Goal completed |

### 12.3 DEM chain regression

- Run existing `test_digital_export_manager.py` — must pass without modification
- Run existing `test_mission_planner.py` — must pass without modification
- Run existing `test_execution_engine.py` — must pass without modification

### 12.4 Persistence tests

- Goal/Plan survive process restart (create → new connection → read)
- Plan.missions survive append_mission
- Foreign key integrity (Goal → Plan)

---

## 13. Acceptance Criteria

| # | Criterion | Verification |
|---|-----------|-------------|
| AC-1 | Goal schema matches contract | Schema diff |
| AC-2 | Plan schema matches contract | Schema diff |
| AC-3 | Goal lifecycle transitions work | Unit + integration tests |
| AC-4 | Plan lifecycle transitions work | Unit + integration tests |
| AC-5 | Goal → Plan relationship is enforced | Integration test |
| AC-6 | Plan.missions mutated only by PlanRepository.append_mission() | Code inspection + test |
| AC-7 | TaskPlanner does NOT mutate Plan state | Code inspection + test |
| AC-8 | Goal/Plan state is NOT stored in MemoryProvider | Code inspection + test |
| AC-9 | Goal/Plan state persists via Repository | Persistence test |
| AC-10 | Ownership enforced: user_id filter on all queries | Test |
| AC-11 | ReasoningEngine reads Goal/Plan context without redesign | Integration test |
| AC-12 | No changes to existing schemas (Decision, Mission, Task, ExecutionPlan) | Diff inspection |
| AC-13 | No database migration required | init_db() pattern verified |
| AC-14 | Existing DEM tests pass without modification | Regression test suite |
| AC-15 | Memory enrichment includes goal_id/plan_id only | Test |

---

## 14. Implementation Order

| Step | Component | Dependencies |
|------|-----------|--------------|
| 1 | Database tables in `init_db()` | None |
| 2 | Goal schema + GoalRepository | Step 1 (tables) |
| 3 | GoalManager | Step 2 |
| 4 | Plan schema + PlanRepository | Step 1 (tables) |
| 5 | PlanPlanner | Steps 2, 4 |
| 6 | PlanManager | Steps 4, 5 |
| 7 | TaskPlanner integration (read-only Plan context) | Step 6 |
| 8 | ReasoningEngine integration (context-only) | Steps 3, 6 |
| 9 | DEM router wiring | Steps 3, 6, 7 |
| 10 | Tests | All above |
| 11 | DEM chain regression | All above |

**Minimum viable sequence:** Steps 1 → 2 → 3 → 4 → 5 → 6 → 7 → 9 → 10 → 11

**Key dependency:** Database tables MUST be created before any repository is instantiated.

---

## 15. Out of Scope

- Reasoning depth / Reasoning redesign
- Autonomy Policy
- Business-facing AI response / Avatar
- Multi-agent coordination
- New external providers
- WP-34/WP-35 modifications
- Database migration / Alembic changes
- Reopening WP-30 through WP-35
- New public API endpoints
- Goal decomposition into sub-goals
- Superseded Plan retrieval (deferred to future WP)

---

## 16. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Goal/Plan state grows unbounded | Medium | Medium | Add cleanup policy in future WP; not a blocker for foundation |
| TaskPlanner coupling to Plan | Medium | High | Enforce via AC-6, AC-7 tests; PlanManager owns mutation |
| Ownership bypass | Low | High | user_id filter in all repository queries |
| Existing DEM tests break | Low | High | Regression suite in step 9 |
| MemoryProvider misuse | Medium | Medium | AC-8 test; contract invariant |

---

*Specification created: 2026-09-02*  
*Author: Architecture Planning*  
*Next step: Implementation WP execution*
