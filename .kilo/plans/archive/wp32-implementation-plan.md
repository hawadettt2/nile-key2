# WP-32 — Knowledge Graph: Implementation Plan

**Reference:** PLAN.md (Master Roadmap v2.1)  
**Specification:** `.kilo/plans/WP-32-spec.md`  
**Engineering Decision:** `.kilo/plans/ED-WP32-001.md`  
**Phase:** 2 — Intelligent Platform  
**Status:** Planned — implementation begins after Specification approval  
**Date:** 2026-07-20  

---

## 1. Executive Summary

WP-32 implements the **Knowledge Graph** bounded context for the Digital Export Manager (DEM). It provides a structured representation of existing platform entities as graph nodes and their relationships as graph edges, enabling the DEM to discover and traverse connections across the platform's data.

The Knowledge Graph is a separate bounded context that:
- Reads existing entity tables without modifying them
- Stores graph metadata in two new SQLite tables: `knowledge_nodes` and `knowledge_edges`
- Exposes a thin FastAPI router for graph operations
- Implements `KnowledgeProvider` interface for integration with WP-30F
- Integrates with `MemoryProvider` interface from WP-31 with graceful degradation
- Logs all mutations via the existing audit framework

Products are deferred to a future Work Package per ED-WP32-001.

---

## 2. Architectural Alignment

The Knowledge Graph follows the same bounded-context pattern as other DEM internal modules:

```
Human Employees
        │
        ▼
Digital Export Manager (Executive Intelligence)
        │
        ▼
Core Modules: (Reasoning Engine | Company Knowledge | Long-Term Memory | Knowledge Graph)
        │
        ▼
    Task Planner
        │
        ▼
  Execution Planner
        │
        ▼
  Tool Orchestrator
        │
        ▼
  ERP Services & Database
```

**Confirmed properties:**
- Knowledge Graph is a separate bounded context with its own data model, lifecycle, and ownership.
- It does not modify DEM core logic or existing entity tables.
- It integrates with existing interfaces (`KnowledgeProvider`, `MemoryProvider`) without modifying them.
- It uses SQLite for persistence, consistent with project baseline.

---

## 3. Dependencies

| Dependency | Type | Status | Source |
|------------|------|--------|--------|
| WP-30F: Knowledge Layer Interface | Must be complete | ✅ Complete per PLAN.md Section 15.3 | PLAN.md Section 7 |
| WP-31: AI Memory | Must be complete | ✅ Complete per PLAN.md Section 15.3 | PLAN.md Section 7 |
| WP-30: Digital Export Manager | Must be complete | ✅ Complete per PLAN.md Section 15.3 | PLAN.md Section 7 |
| Python FastAPI | Runtime | ✅ Available | Repository evidence |
| SQLite | Database | ✅ Available | PLAN.md Section 3.1 |
| Pydantic | Schema validation | ✅ Available | Repository evidence |
| pytest | Testing framework | ✅ Available | Repository evidence |

---

## 4. Implementation Phases

### Phase 1: Foundation (WP-32A)

**Goal:** Define schemas, database tables, and provider registration.

**Exit Criteria:**
- [ ] Pydantic schemas for graph nodes and edges defined
- [ ] `knowledge_nodes` and `knowledge_edges` tables created
- [ ] `KnowledgeGraphProvider` registered and queryable

#### Commit 1: Schemas + Database + Provider Registration

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 1.1 | Define graph node and edge Pydantic schemas | `backend/app/schemas/knowledge_graph.py` | None | `KnowledgeGraphNode`, `KnowledgeGraphNodeCreate`, `KnowledgeGraphEdge`, `KnowledgeGraphEdgeCreate`, `KnowledgeGraphRelationships`, `KnowledgeGraphTraversal`, `SyncResult` schemas | None | Schemas validate correctly; all fields match Section 6.3 and Section 11.3 of Specification | None (schema-only) | None |
| 1.2 | Add graph metadata tables to `init_db()` | None | `backend/app/core/database.py` | `knowledge_nodes` and `knowledge_edges` tables created | Task 1.1 | Tables created successfully on `init_db()`; no errors on existing databases | None (database migration) | Migration conflict with existing schema |
| 1.3 | Register `KnowledgeGraphProvider` at startup | `backend/app/agent/knowledge/graph_provider.py` | `backend/main.py` | Provider registered in `KnowledgeProviderRegistry` | Task 1.1, WP-30F complete | Provider is queryable via registry after app startup | None (registration only) | Registry not initialized yet |

**Commit Message:** `feat(wp32): add knowledge graph schemas, database tables, and provider registration`

---

### Phase 2: Service Layer Core (WP-32B)

**Goal:** Implement core CRUD operations for graph nodes and edges.

**Exit Criteria:**
- [ ] Node CRUD operations implemented
- [ ] Edge CRUD operations implemented
- [ ] Service layer unit tests pass

#### Commit 2: Node CRUD + Edge CRUD

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 2.1 | Implement `KnowledgeGraphService` with node CRUD | `backend/app/services/knowledge_graph.py` | None | `create_node()`, `get_node()`, `update_node()`, `delete_node()` functions | Phase 1 complete | Nodes can be created, read, updated, and deleted for all 9 entity types | Unit tests for each CRUD operation | Circular import with existing services |
| 2.2 | Implement edge CRUD operations | `backend/app/services/knowledge_graph.py` | None | `create_edge()`, `get_edge()`, `delete_edge()`, `list_edges_for_node()` functions | Task 2.1 | Edges can be created and deleted; edges can be listed for a node | Unit tests for edge CRUD | None |

**Commit Message:** `feat(wp32): implement knowledge graph service layer CRUD operations`

---

### Phase 3: Service Layer Advanced (WP-32C)

**Goal:** Implement derived edge discovery, graph traversal, and entity synchronization.

**Exit Criteria:**
- [ ] Derived edges discoverable from entity reference columns
- [ ] Graph traversal works up to configurable depth
- [ ] Entity synchronization functional

#### Commit 3: Derived Edges + Traversal + Sync

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 3.1 | Implement derived edge discovery from entity reference columns | `backend/app/services/knowledge_graph.py` | None | `_derive_edges_from_entity(entity_type, entity_id)` function | Task 2.2 | Derived edges correctly discovered for all 14 relationships in Section 6.2.1 | Unit tests for each derived edge type | Performance on large datasets |
| 3.2 | Implement graph traversal | `backend/app/services/knowledge_graph.py` | None | `traverse(entity_type, entity_id, depth, direction)` function | Task 3.1 | Traversal returns connected entities up to configurable depth | Unit tests for 1-hop, 2-hop, depth-limited traversal | Infinite loops on cyclic relationships |
| 3.3 | Implement entity synchronization | `backend/app/services/knowledge_graph.py` | None | `sync_entity(entity_type, entity_id)` and `sync_all()` functions | Task 2.1 | Graph nodes reflect existing entity data after sync | Unit tests for sync operations | Sync triggers undefined (deferred to Implementation Plan) |

**Commit Message:** `feat(wp32): implement derived edge discovery, graph traversal, and entity synchronization`

---

### Phase 4: Service Layer Integration (WP-32D)

**Goal:** Integrate MemoryProvider and audit logging.

**Exit Criteria:**
- [ ] MemoryProvider integration functional
- [ ] Audit logging functional for all mutations

#### Commit 4: Memory + Audit Integration

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 4.1 | Integrate MemoryProvider for graph context | `backend/app/services/knowledge_graph.py` | None | `_store_graph_context()`, `_recall_graph_context()` helper functions | Task 2.1, WP-31 complete | Graph context stored and recalled via MemoryProvider; graceful degradation when unavailable | Unit tests with mock MemoryProvider | MemoryProvider unavailable in some deployments |
| 4.2 | Integrate audit logging for all mutations | `backend/app/services/knowledge_graph.py` | None | `_audit_mutation()` helper function | Task 2.1 | All node/edge mutations logged via `log_audit()` with `entity_type="knowledge_graph"` | Unit tests verifying audit calls | None |

**Commit Message:** `feat(wp32): integrate MemoryProvider and audit logging`

---

### Phase 5: API Layer (WP-32E)

**Goal:** Expose graph operations via FastAPI router.

**Exit Criteria:**
- [ ] Router registered in main.py
- [ ] All endpoints return valid responses
- [ ] OpenAPI schema generated

#### Commit 5: Router + Registration

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 5.1 | Create FastAPI router with graph endpoints | `backend/app/routers/knowledge_graph.py` | None | 9 endpoints per Section 11.2 of Specification | Phase 2 complete | All endpoints return correct status codes and shapes | None (router wiring only) | None |
| 5.2 | Register router in `backend/main.py` | None | `backend/main.py` | Router registered with prefix `/api/v1/knowledge-graph` | Task 5.1 | Router appears in OpenAPI schema; endpoints accessible | None (registration only) | Import error or circular dependency |

**Commit Message:** `feat(wp32): expose knowledge graph API endpoints`

---

### Phase 6: Testing (WP-32F)

**Goal:** Comprehensive test coverage for all graph operations.

**Exit Criteria:**
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All security tests pass
- [ ] Performance tests meet thresholds
- [ ] Full regression test suite passes

#### Commit 6: Unit Tests

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 6.1 | Write service layer unit tests | `backend/tests/test_services/test_knowledge_graph.py` | None | 30+ unit tests covering node CRUD, edge CRUD, derived edges, traversal, sync, memory, audit, degradation | Phase 2-4 complete | All unit tests pass | pytest | Mock complexity for MemoryProvider |

#### Commit 7: Integration Tests

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 7.1 | Write router integration tests | `backend/tests/test_knowledge_graph.py` | None | 15+ integration tests covering all endpoints, auth, derived edges, memory, audit | Commit 5 complete | All integration tests pass | pytest with test client | Test database setup/teardown |
| 7.2 | Write KnowledgeProvider registration tests | `backend/tests/test_knowledge_graph.py` | None | Tests for provider registration and queryability | Commit 1 complete | Provider registered and queryable | pytest | None |

#### Commit 8: Performance + Security + Regression Tests

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 8.1 | Write performance tests | `backend/tests/test_knowledge_graph_performance.py` | None | Performance tests for node lookup, traversal, bulk queries | Commit 5 complete | Queries meet latency thresholds | pytest with timing assertions | Thresholds undefined (deferred to Implementation Plan) |
| 8.2 | Write security tests | `backend/tests/test_knowledge_graph_security.py` | None | Security tests for entity isolation, authorization, SQL injection, audit completeness | Commit 5 complete | All security tests pass | pytest | None |
| 8.3 | Verify regression test suite | None | None | Full test suite passes | All previous commits | 100% existing tests pass | pytest | Existing tests broken by changes |

**Commit Messages:**
- `test(wp32): add service layer unit tests`
- `test(wp32): add router integration tests`
- `test(wp32): add performance, security, and regression tests`

---

### Phase 7: Documentation & Closure (WP-32G)

**Goal:** Document implementation and formally close WP-32.

**Exit Criteria:**
- [ ] `CURRENT_STATUS.md` updated
- [ ] `CHANGELOG.md` updated
- [ ] `PLAN.md` updated
- [ ] Closure review passed

#### Commit 9: Documentation Updates

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 9.1 | Update `CURRENT_STATUS.md` | None | `CURRENT_STATUS.md` | WP-32 marked complete with summary | Phase 6 complete | Documentation reflects implementation | None | None |
| 9.2 | Update `CHANGELOG.md` | None | `CHANGELOG.md` | WP-32 entry added | Phase 6 complete | Changelog documents all changes | None | None |
| 9.3 | Update `PLAN.md` | None | `PLAN.md` | Section 12.3, Section 15.3 updated | Phase 6 complete | PLAN.md reflects WP-32 completion | None | None |

**Commit Message:** `docs(wp32): update documentation and close WP-32`

---

## 5. Commit Sequence

| Order | Commit | Phase | Tasks | Files Created | Files Modified | Build Risk | Test Risk |
|-------|--------|-------|-------|---------------|----------------|------------|-----------|
| 1 | `feat(wp32): add knowledge graph schemas, database tables, and provider registration` | 1 | 1.1, 1.2, 1.3 | 2 | 2 | Low | Low |
| 2 | `feat(wp32): implement knowledge graph service layer CRUD operations` | 2 | 2.1, 2.2 | 1 | 0 | Low | Low |
| 3 | `feat(wp32): implement derived edge discovery, graph traversal, and entity synchronization` | 3 | 3.1, 3.2, 3.3 | 0 | 1 | Low | Medium |
| 4 | `feat(wp32): integrate MemoryProvider and audit logging` | 4 | 4.1, 4.2 | 0 | 1 | Low | Medium |
| 5 | `feat(wp32): expose knowledge graph API endpoints` | 5 | 5.1, 5.2 | 1 | 1 | Medium | Medium |
| 6 | `test(wp32): add service layer unit tests` | 6 | 6.1 | 1 | 0 | Low | Low |
| 7 | `test(wp32): add router integration tests` | 6 | 7.1, 7.2 | 1 | 0 | Low | Medium |
| 8 | `test(wp32): add performance, security, and regression tests` | 6 | 8.1, 8.2, 8.3 | 1 | 0 | Low | Medium |
| 9 | `docs(wp32): update documentation and close WP-32` | 7 | 9.1, 9.2, 9.3 | 0 | 3 | Low | Low |

---

## 6. Dependency Analysis

### 6.1 Task Dependencies

```
Phase 1: Foundation (Commit 1)
├── Task 1.1: Schemas
├── Task 1.2: Database tables
└── Task 1.3: Provider registration
    └── Dependencies: Task 1.1, WP-30F complete

Phase 2: Service Layer Core (Commit 2)
├── Task 2.1: Node CRUD
│   └── Dependencies: Phase 1 complete
└── Task 2.2: Edge CRUD
    └── Dependencies: Task 2.1

Phase 3: Service Layer Advanced (Commit 3)
├── Task 3.1: Derived edges
│   └── Dependencies: Task 2.2
├── Task 3.2: Graph traversal
│   └── Dependencies: Task 3.1
└── Task 3.3: Entity sync
    └── Dependencies: Task 2.1

Phase 4: Service Layer Integration (Commit 4)
├── Task 4.1: MemoryProvider integration
│   └── Dependencies: Task 2.1, WP-31 complete
└── Task 4.2: Audit logging
    └── Dependencies: Task 2.1

Phase 5: API Layer (Commit 5)
├── Task 5.1: Create router
│   └── Dependencies: Phase 2 complete
└── Task 5.2: Register router
    └── Dependencies: Task 5.1

Phase 6: Testing (Commits 6-8)
├── Commit 6: Unit tests
│   └── Dependencies: Phase 2-4 complete
├── Commit 7: Integration tests
│   └── Dependencies: Commit 5 complete
└── Commit 8: Performance + Security + Regression
    └── Dependencies: All previous commits

Phase 7: Documentation (Commit 9)
└── Dependencies: Phase 6 complete
```

### 6.2 Circular Dependency Check

| Check | Result | Evidence |
|-------|--------|----------|
| Service layer imports schemas | ✅ Safe | `backend/app/services/customer.py` imports from `app/schemas/customer.py` — same pattern |
| Router imports service layer | ✅ Safe | `backend/app/routers/customers.py` imports from `app/services/customer.py` — same pattern |
| Service layer imports database | ✅ Safe | `backend/app/services/base.py` provides `connection()` — same pattern |
| Service layer imports audit | ✅ Safe | `backend/app/services/customer.py` imports `log_audit` — same pattern |
| Provider imports interfaces | ✅ Safe | `backend/app/agent/knowledge/provider.py` is ABC — no circular dependency |
| No DEM core imports | ✅ Safe | WP-32 does not modify DEM core per Specification Constraint 3 |

**No circular dependencies detected.**

### 6.3 Build Safety Check

| Check | Result | Evidence |
|-------|--------|----------|
| New modules follow existing naming conventions | ✅ Safe | `knowledge_graph.py` follows same pattern as `customer.py`, `shipping.py` |
| New schemas follow existing Pydantic patterns | ✅ Safe | `backend/app/schemas/document.py` pattern followed |
| New router follows existing registration pattern | ✅ Safe | `backend/main.py` includes `app.include_router(...)` for all routers |
| No modifications to existing entity tables | ✅ Safe | Only `init_db()` modified to add new tables |
| No modifications to DEM core | ✅ Safe | No DEM core files modified per Specification |

**Build safety maintained throughout all commits.**

### 6.4 Test Safety Check

| Check | Result | Evidence |
|-------|--------|----------|
| Unit tests run in isolation | ✅ Safe | Tests use mocks for MemoryProvider and database |
| Integration tests use test database | ✅ Safe | Follows existing `conftest.py` pattern |
| Regression tests run after all changes | ✅ Safe | Commit 8 runs full test suite |
| No existing tests modified | ✅ Safe | Only new test files created |

**Test safety maintained throughout all commits.**

---

## 7. File Inventory

### 7.1 Files Created

| File | Phase | Commit | Purpose |
|------|-------|--------|---------|
| `backend/app/schemas/knowledge_graph.py` | 1 | 1 | Pydantic schemas for graph nodes, edges, and API responses |
| `backend/app/agent/knowledge/graph_provider.py` | 1 | 1 | `KnowledgeGraphProvider` implementing `KnowledgeProvider` |
| `backend/app/services/knowledge_graph.py` | 2-4 | 2, 3, 4 | `KnowledgeGraphService` with all CRUD and traversal operations |
| `backend/app/routers/knowledge_graph.py` | 5 | 5 | FastAPI router exposing graph endpoints |
| `backend/tests/test_services/test_knowledge_graph.py` | 6 | 6 | Service layer unit tests |
| `backend/tests/test_knowledge_graph.py` | 6 | 7 | Router integration tests |
| `backend/tests/test_knowledge_graph_performance.py` | 6 | 8 | Performance tests |
| `backend/tests/test_knowledge_graph_security.py` | 6 | 8 | Security tests |

### 7.2 Files Modified

| File | Phase | Commit | Changes |
|------|-------|--------|---------|
| `backend/app/core/database.py` | 1 | 1 | Add `knowledge_nodes` and `knowledge_edges` table creation to `init_db()` |
| `backend/main.py` | 5 | 5 | Register `knowledge_graph.router` |
| `CURRENT_STATUS.md` | 7 | 9 | Update WP-32 status |
| `CHANGELOG.md` | 7 | 9 | Add WP-32 entry |
| `PLAN.md` | 7 | 9 | Update Section 12.3 and Section 15.3 |

---

## 8. Risk Register

| Risk | Likelihood | Impact | Mitigation | Phase |
|------|------------|--------|------------|-------|
| Circular import between graph module and existing modules | Low | Medium | Follow existing import patterns; static analysis in CI | 1-5 |
| MemoryProvider unavailable in some deployments | Low | Low | Graceful degradation implemented per Specification | 4 |
| Performance degradation with large graph | Medium | Medium | Performance tests validate thresholds; SQLite baseline | 3, 8 |
| Existing entity data inconsistency | Medium | Low | Graph sync handles missing/invalid references gracefully | 3 |
| Migration conflict with existing schema | Low | Low | Use `CREATE TABLE IF NOT EXISTS`; follow existing migration pattern | 1 |
| Test database setup/teardown issues | Medium | Medium | Follow existing `conftest.py` patterns | 6-8 |

---

## 9. Acceptance Criteria Summary

All acceptance criteria from WP-32 Specification Section 13 are covered:

| AC ID | Criterion | Covered In |
|-------|-----------|------------|
| AC-32.1 | Graph nodes for all 9 node types | Commit 2 (Task 2.1) |
| AC-32.2 | Graph nodes reflect underlying entity data | Commit 3 (Task 3.3) |
| AC-32.3 | Derived edges discoverable | Commit 3 (Task 3.1) |
| AC-32.4 | Explicit edges created | Commit 2 (Task 2.2) |
| AC-32.5 | Explicit edges deleted | Commit 2 (Task 2.2) |
| AC-32.6 | Querying node returns relationships | Commit 2 (Task 2.1, 2.2) |
| AC-32.7 | Traversing relationships | Commit 3 (Task 3.2) |
| AC-32.8 | KnowledgeGraphProvider registered | Commit 1 (Task 1.3) |
| AC-32.9 | MemoryProvider integration | Commit 4 (Task 4.1) |
| AC-32.10 | Audit logging | Commit 4 (Task 4.2) |
| AC-32.11 | Graceful degradation without MemoryProvider | Commit 4 (Task 4.1) |
| AC-32.12 | No regressions | Commit 8 (Task 8.3) |
| AC-32.13 | Valid OpenAPI schema | Commit 5 (Task 5.1) |
| AC-32.14 | Authentication required | Commit 5 (Task 5.1) |
| AC-32.15 | Authorization required | Commit 5 (Task 5.1) |
| AC-32.16 | Products not represented | Code review + Commit 1-5 |

---

## 10. Quality Gates

Per PLAN.md Section 10.8, the following quality gates must be passed before WP-32 closure:

| Gate | Verification | Phase |
|------|--------------|-------|
| Project builds | `npm run build` or equivalent | 5 |
| Backend starts | `uvicorn main:app --reload` succeeds | 5 |
| Core paths work | Graph endpoints return valid responses | 7 |
| Authentication works | Auth required for all endpoints | 7 |
| No broken imports | Static analysis passes | 5 |
| No circular dependencies | Static analysis passes | 5 |
| No hidden runtime errors | Full test suite passes | 8 |
| Tests pass | All unit + integration + security tests pass | 8 |

---

## 11. Implementation Notes

### 11.1 Node Synchronization Strategy

The Implementation Plan defers the exact synchronization triggers to the implementation team. Options:
- On entity create/update/delete via service layer hooks
- On explicit `/sync` API call
- On graph query if node is stale

The chosen approach must be documented in the Implementation Plan and must not modify existing entity services.

### 11.2 Derived Edge Discovery

The Implementation Plan may choose either:
- Query-time derivation: compute edges on-the-fly from entity reference columns
- Precomputed storage: compute edges once and store in `knowledge_edges`

Both approaches are acceptable. The choice must be documented in the Implementation Plan.

### 11.3 Memory Integration Depth

The exact memory keys and values stored by the Knowledge Graph are deferred to the Implementation Plan. Suggested approach:
- `memory_type="context"` for graph query history
- `memory_type="decision"` for traversal patterns
- `importance=7` for frequently accessed entities

### 11.4 Authorization Model

The exact roles permitted for each graph operation are deferred to the Implementation Plan. Suggested approach:
- Read operations: all authenticated users
- Node mutations: `manager`, `admin_staff`
- Edge mutations: `manager` only

---

## 12. Document Authority

This document defines the implementation plan for WP-32.

All implementation tasks, technical designs, and code changes for WP-32 MUST derive from this document and the referenced Specification and Engineering Decision.

Any deviation requires a documented architectural decision recorded in the Architectural Decision Log (PLAN.md Section 13) with explicit rationale.

**Status:** Planned — implementation begins after Specification approval.

---

## 13. References

- `PLAN.md` Section 6.2 — Capability #10: Knowledge Graph
- `PLAN.md` Section 7 — Work Package execution order
- `PLAN.md` Section 9.3 — Source of Truth: Pydantic Schemas
- `PLAN.md` Section 9.9 — Database Rules
- `PLAN.md` Section 9.10 — API Rules
- `PLAN.md` Section 9.12 — Security Rules
- `PLAN.md` Section 10.4 — Testing Rules
- `PLAN.md` Section 10.8 — Quality Gates
- `PLAN.md` Section 14.1 — Implementation Rules
- `PLAN.md` Section 15.3 — WP-32 status
- `PLAN.md` Section 16.3 — Phase 2 exit criteria
- `.kilo/plans/WP-32-spec.md` — WP-32 Specification
- `.kilo/plans/ED-WP32-001.md` — Products Deferral Engineering Decision
- `backend/app/agent/knowledge/provider.py` — `KnowledgeProvider` ABC
- `backend/app/agent/knowledge/registry.py` — `KnowledgeProviderRegistry`
- `backend/app/agent/memory/interface.py` — `MemoryProvider` ABC
- `backend/app/services/base.py` — Service layer utilities
- `backend/app/services/audit.py` — Audit logging
- `backend/app/core/database.py` — Database initialization pattern
- `backend/main.py` — Application entry point and router registration
- `backend/app/routers/auth.py` — `get_current_user`, `require_role` dependencies
- `.kilo/plans/wp31-implementation-plan.md` — WP-31 implementation pattern
