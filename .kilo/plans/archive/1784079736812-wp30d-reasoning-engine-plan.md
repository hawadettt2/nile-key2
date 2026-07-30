# WP-30D Implementation Plan — Reasoning Engine

**Version:** 1.0  
**Date:** 2026-07-16  
**Status:** Implementation-Ready  
**Prerequisite:** WP-30C Complete  

---

## 1. Executive Summary

**Goal:** Implement the `ReasoningEngine` to produce `Decision` objects from user requests by querying the Company Knowledge Layer and Memory Interface, evaluating options against company rules, and enforcing approval gates for destructive operations.

**Scope:**  
- Implement `ReasoningEngine.reason()` in `backend/app/agent/decision_engine/engine.py`  
- Extend `Decision` schema to carry approval metadata  
- Propagate approval requirements to `Mission` via `TaskPlanner`  
- Add unit tests for all new behavior  

**Out of Scope:**  
- Wiring `ReasoningEngine` into `AgentOrchestrator` or `routers/agent.py`  
- Implementing `KnowledgeProvider` or `MemoryProvider` concrete classes  
- UI/approval flow endpoints  
- Replacing the legacy `Planner` in `core/planner.py`  

---

## 2. Architecture Analysis

### 2.1 Current State

The `ReasoningEngine` exists as a Phase 1 stub:

```python
class ReasoningEngine:
    async def reason(self, session_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("ReasoningEngine.reason() is not implemented in Phase 1.")
```

### 2.2 Target Architecture

Per `ED-WP30-001` and the architecture document, the Reasoning Engine is a bounded context that:

1. **Receives** user requests (intent + parameters + session context)
2. **Queries** `KnowledgeProvider` for company rules, regulations, and procedures
3. **Queries** `MemoryProvider` for user preferences, standing orders, and historical decisions
4. **Evaluates** possible `chosen_path` options against retrieved rules and preferences
5. **Produces** a `Decision` object containing:
   - `decision_id`, `session_id`, `reasoning`, `chosen_path`, `alternatives`, `context`, `created_at`
   - `requires_approval: bool` (destructive operation flag)
   - `approval_status: str` (not_required | pending | approved | rejected)
6. **Handles** approval gates: flags destructive operations and defers execution until approval is granted

### 2.3 Integration Point

The `Decision` is consumed by `TaskPlanner.plan(decision, session_context)`, which already accepts decision dicts. The `ToolOrchestrator.execute()` already accepts `Mission` objects. WP-30D only implements the `ReasoningEngine`; wiring it into the existing `AgentOrchestrator` and `routers/agent.py` is deferred to a future work package.

---

## 3. Dependency Analysis

### 3.1 Upstream Dependencies (Already Satisfied)

| Dependency | Location | Status |
|------------|----------|--------|
| `Decision` schema | `backend/app/agent/schemas/decision.py` | ✅ Exists |
| `KnowledgeProvider` ABC | `backend/app/agent/knowledge/provider.py` | ✅ Exists |
| `MemoryProvider` ABC | `backend/app/agent/memory/interface.py` | ✅ Exists |
| `TaskPlanner` | `backend/app/agent/mission_planner/planner.py` | ✅ Exists |
| `ToolOrchestrator` | `backend/app/agent/execution_engine/orchestrator.py` | ✅ Exists |
| `Mission` schema | `backend/app/agent/schemas/mission.py` | ✅ Exists |
| `SessionContext` schema | `backend/app/agent/schemas/session.py` | ✅ Exists |

### 3.2 Downstream Consumers (Not Modified in WP-30D)

| Consumer | Relationship | Impact |
|----------|--------------|--------|
| `AgentOrchestrator` (`core/orchestrator.py`) | Would consume `ReasoningEngine` | No change in WP-30D |
| `routers/agent.py` | Would invoke `ReasoningEngine` | No change in WP-30D |
| `routers/digital_export_manager.py` | May use `Decision` in future | No change in WP-30D |

---

## 4. Files To Modify

### 4.1 Implementation Files

| File | Change | Reason |
|------|--------|--------|
| `backend/app/agent/decision_engine/engine.py` | Modify | Implement `ReasoningEngine.reason()` and helper methods |
| `backend/app/agent/schemas/decision.py` | Modify | Add `requires_approval` and `approval_status` fields |
| `backend/app/agent/mission_planner/planner.py` | Modify | Read `requires_approval` from Decision context and propagate to `Mission.approval_policy` |

### 4.2 Test Files

| File | Change | Reason |
|------|--------|--------|
| `backend/tests/agent/test_decision_engine.py` | Create | Unit tests for `ReasoningEngine` |

---

## 5. Phase Breakdown

### Phase 1: ReasoningEngine Core & Decision Production

**Tasks:** 4.1, 4.2, 4.5

**Objective:** Implement the `ReasoningEngine` class with a working `reason()` method that accepts user requests and produces `Decision` objects without external provider dependencies.

**Implementation Details:**

1. **Update `Decision` schema** (`schemas/decision.py`):
   - Add `requires_approval: bool = False`
   - Add `approval_status: str = "not_required"`

2. **Implement `ReasoningEngine.reason()`** (`decision_engine/engine.py`):
   - Accept `session_id: str` and `request: Dict[str, Any]`
   - Parse `request["intent"]`, `request.get("parameters", {})`, `request.get("context", {})`
   - Implement `_map_intent_to_candidates()`: deterministic keyword extraction from intent to produce candidate `chosen_path` values
   - Implement `_score_candidates()`: score candidates based on deterministic rules (keyword match confidence, parameter presence)
   - Implement `_select_best_option()`: pick highest-scoring candidate; include runners-up as `alternatives`
   - Implement `_build_decision()`: construct and return a `Decision` instance/model_dump()

3. **Deterministic Behavior:**
   - No random state
   - Same intent + parameters → same chosen_path and alternatives
   - Scoring is deterministic (no time-based or hash-based variation)

**Out of Scope for This Phase:**
- KnowledgeProvider and MemoryProvider integration
- Approval gate enforcement logic

### Phase 2: Knowledge & Memory Integration

**Tasks:** 4.3, 4.4

**Objective:** Integrate `KnowledgeProvider` and `MemoryProvider` into the reasoning flow and use retrieved data to influence option evaluation.

**Implementation Details:**

1. **Provider Querying** (`decision_engine/engine.py`):
   - Implement `_query_memory(session_id, intent)`: async recall from `MemoryProvider` with graceful degradation
   - Implement `_query_knowledge(intent, parameters)`: async query from `KnowledgeProvider` with graceful degradation
   - Both methods must catch exceptions and return empty results if providers are unavailable

2. **Option Evaluation** (`decision_engine/engine.py`):
   - Implement `_evaluate_options(candidates, memories, knowledge)`:
     - Adjust candidate scores using user preferences (e.g., preferred shipping method)
     - Adjust scores using standing orders (e.g., required documentation adds bonus to compliant paths)
     - Apply knowledge rules (e.g., restricted destinations penalize certain paths)
   - If providers are unavailable, fall back to deterministic scoring from Phase 1

3. **Decision Enrichment:**
   - Include retrieved memories and knowledge results in `Decision.context`
   - Include evaluation rationale in `Decision.reasoning`

### Phase 3: Approval Gates

**Task:** 4.6

**Objective:** Identify destructive operations and enforce synchronous approval gates per the architecture requirement: "For high-risk operations, oversight is synchronous (approval gates)."

**Implementation Details:**

1. **Destructive Operation Detection** (`decision_engine/engine.py`):
   - Implement `_is_destructive(chosen_path, parameters)`:
     - Match `chosen_path` against known destructive patterns (e.g., paths involving delete, cancel, modify)
     - Match parameters against destructive keywords (e.g., action="delete", operation="cancel")
   - If destructive, set `requires_approval: True` and `approval_status: "pending"`

2. **Approval State Check** (`decision_engine/engine.py`):
   - Implement `_check_approval_status(session_id, chosen_path)`:
     - Query `MemoryProvider` for stored approval grants
     - If approved, set `requires_approval: False` and `approval_status: "approved"`
     - If rejected, set `requires_approval: True` and `approval_status: "rejected"`
     - If no record, set `requires_approval: True` and `approval_status: "pending"`

3. **Propagation to Mission** (`mission_planner/planner.py`):
   - Update `_create_mission()` to read `requires_approval` from `decision.get("context", {}).get("requires_approval", False)`
   - Set `Mission.approval_policy = {"requires_approval": decision_requires_approval}`
   - Preserve backward compatibility: default remains `False`

### Phase 4: Testing & Validation

**Objective:** Add comprehensive unit tests and verify backward compatibility.

**Test Plan:**

| Test Category | Count | Description |
|---------------|-------|-------------|
| Core Decision Production | 6 | Valid/invalid requests, deterministic output, alternatives generation |
| Provider Integration | 4 | Memory recall, knowledge query, graceful degradation when providers unavailable |
| Approval Gates | 5 | Destructive detection, non-destructive pass-through, approval state checking, propagation to Mission |
| Edge Cases | 3 | Empty intent, missing providers, malformed requests |

**Validation:**
- All new tests pass
- All existing Phase 1/2/3/4 tests continue passing
- No regressions in `test_execution_engine.py` or `test_mission_planner.py`

---

## 6. Acceptance Criteria

### Phase 1

- [ ] `ReasoningEngine.reason()` accepts `session_id: str` and `request: Dict[str, Any]`
- [ ] Returns a dict conforming to the `Decision` schema
- [ ] `Decision.chosen_path` is deterministically derived from `request["intent"]`
- [ ] `Decision.alternatives` contains at least one alternative when multiple candidates exist
- [ ] `Decision.reasoning` explains the selection rationale
- [ ] Without providers, produces valid Decisions for all supported mission types
- [ ] Same input always produces identical output (deterministic)

### Phase 2

- [ ] `reason()` calls `knowledge_provider.query()` when provider is available
- [ ] `reason()` calls `memory_provider.recall()` when provider is available
- [ ] Provider results appear in `Decision.context["knowledge"]` and `Decision.context["memories"]`
- [ ] Graceful degradation: providers returning exceptions do not crash reasoning
- [ ] Candidate scoring adjusts based on user preferences and knowledge rules when providers return data
- [ ] Falls back to Phase 1 deterministic scoring when providers are unavailable

### Phase 3

- [ ] Destructive operations are flagged with `requires_approval: True`
- [ ] Non-destructive operations have `requires_approval: False`
- [ ] `approval_status` reflects pending/approved/rejected states
- [ ] `TaskPlanner._create_mission()` reads `requires_approval` from Decision context
- [ ] `Mission.approval_policy["requires_approval"]` matches the Decision flag
- [ ] Backward compatible: Missions created without Decision context default to `requires_approval: False`

### Phase 4

- [ ] All new tests pass
- [ ] All existing tests pass (no regressions)
- [ ] Code coverage for new `ReasoningEngine` methods ≥ 90%

---

## 7. Risk Analysis

| Risk | Severity | Likelihood | Impact | Mitigation | Status |
|------|----------|-----------|--------|------------|--------|
| ReasoningEngine produces incorrect Decisions due to heuristic-only fallback | MEDIUM | Medium | Wrong missions created | Document that production requires KnowledgeProvider implementation; heuristics are MVP only | ACCEPTED |
| Approval gate detection misses destructive patterns | MEDIUM | Medium | Unauthorized destructive operations | Maintain explicit allowlist/denylist of destructive paths and parameters; document extensibility | ACCEPTED |
| Decision schema changes break TaskPlanner consumers | LOW | Low | Runtime errors in mission creation | Additive schema changes only (new fields with defaults); backward compatible | MITIGATED |
| No real KnowledgeProvider/MemoryProvider available for testing | LOW | High | Cannot test provider integration paths | Use mock providers in tests; verify graceful degradation with None providers | MITIGATED |
| Scope creep into orchestrator/router integration | MEDIUM | Medium | Unplanned modifications to public APIs | Explicitly exclude integration from WP-30D scope; defer to future work package | MITIGATED |

---

## 8. Design Decisions

### 8.1 `requires_approval` Field Location

**Decision:** Add `requires_approval: bool` and `approval_status: str` directly to the `Decision` schema.

**Rationale:** The Decision is the contract between ReasoningEngine and TaskPlanner. Approval state is a property of the decision-making process, not just the mission. Storing it on Decision makes the intent explicit and traceable. The field is additive and backward-compatible.

### 8.2 Approval Gate Enforcement Level

**Decision:** The ReasoningEngine identifies and flags destructive operations but does not block execution. Blocking/prompting is the responsibility of the orchestrator or API layer.

**Rationale:** Separation of concerns. The ReasoningEngine produces Decisions; the orchestrator enforces workflow policies. This keeps WP-30D focused and avoids coupling decision logic with API session management.

### 8.3 Provider Availability

**Decision:** `ReasoningEngine` accepts optional `knowledge_provider` and `memory_provider`. When unavailable, it falls back to deterministic heuristics.

**Rationale:** WP-30D must be testable and functional without waiting for WP-30F (Knowledge Layer) and WP-31 (Memory Interface). Graceful degradation is an architecture requirement.

### 8.4 Integration Scope

**Decision:** WP-30D does NOT modify `AgentOrchestrator` or `routers/agent.py`.

**Rationale:** The implementation plan tasks 4.1–4.6 describe the ReasoningEngine component in isolation. Integration into the existing request flow is a separate concern that requires its own design review and testing. Deferring integration prevents scope expansion and architectural drift.

---

## 9. Final Readiness Verdict

**GO**

All prerequisites for WP-30D are satisfied:
- `ReasoningEngine` stub exists at the correct location
- `KnowledgeProvider` and `MemoryProvider` interfaces are defined
- `Decision` schema exists and is consumed by `TaskPlanner`
- `TaskPlanner` accepts decision dicts and creates Missions
- No pending Engineering Decisions or Change Requests block WP-30D
- Repository is clean, synchronized, and test infrastructure is in place

The plan is implementation-ready.
