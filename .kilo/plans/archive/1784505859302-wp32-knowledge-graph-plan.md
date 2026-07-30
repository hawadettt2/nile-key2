# WP-32 — Knowledge Graph: Planning Package

**Work Package:** WP-32 — Knowledge Graph  
**Phase:** 2 — Intelligent Platform  
**Baseline:** bbd7abb0e68e06d97a977781ae7475f5145384fa  
**Authority:** PLAN.md (Master Roadmap v2.1) — Single Source of Truth  
**Date:** 2026-07-20  
**Status:** Planning — Pending Approval  

---

## 1. WP-32 Specification

### 1.1 Purpose

Implement the **Knowledge Graph** bounded context for the Digital Export Manager (DEM). The Knowledge Graph provides a structured representation of trade entities and their relationships, enabling the DEM to discover and traverse connections across the platform's data beyond the workflow-centric links already captured in `export_workflows`.

**Source:** PLAN.md Section 6.2 Capability #10: "رسم معرفي - عملاء، موردين، منتجات، علاقات" and Section 7: "WP-32: Knowledge Graph — رسم معرفي للتجارة".

### 1.2 Scope

**In Scope:**
- Knowledge Graph data model: nodes representing existing platform entities, edges representing relationships derived from existing foreign keys plus explicit graph edges
- Graph persistence layer using SQLite (consistent with project baseline)
- Service layer for graph operations: add/update nodes, create edges, query by node, traverse relationships
- Thin FastAPI router exposing graph endpoints
- Integration with existing Knowledge Layer (WP-30F) via `KnowledgeProvider` interface
- Integration with existing Memory Layer (WP-31) via `MemoryProvider` interface
- Pydantic schemas for graph entities and API contracts
- Database tables for graph metadata (`knowledge_nodes`, `knowledge_edges`)
- Audit logging for graph mutations via existing audit framework

**Out of Scope:**
- New standalone "products" entity table (no such entity exists in current baseline; product information is captured in existing entity fields)
- LLM-powered graph reasoning or inference
- Graph visualization frontend components
- Ingestion pipeline for external knowledge sources (deferred per KNOWLEDGE_INGESTION_CONTRACT.md Section 5)
- Graph analytics or machine learning features
- Migration to graph-specific database (Neo4j, etc.)
- Modification of existing entity tables

### 1.3 Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-32.1 | The system shall model existing platform entities as graph nodes: Customer, Supplier, Shipment, Invoice, Document, Resource, HsCode | PLAN.md Section 6.2: "عملاء، موردين، منتجات، علاقات" — "منتجات" here refers to product information already present in entity records, not a separate table |
| FR-32.2 | The system shall model relationships as graph edges between nodes, derived from existing foreign keys: supplier↔customer (via shipment), customer↔invoice, supplier↔invoice, shipment↔customs_declaration, shipment↔invoice, customs_declaration↔hs_code, workflow↔entities | PLAN.md Section 6.2: "علاقات"; existing database foreign keys |
| FR-32.3 | The system shall allow explicit edge creation for relationships not captured by foreign keys | PLAN.md Section 6.2: "علاقات" — implicit relationships beyond FK constraints |
| FR-32.4 | The system shall expose query operations to retrieve a node and its connected relationships | PLAN.md Section 16.3: "Knowledge Graph يعرض علاقات الكيانات" |
| FR-32.5 | The system shall support relationship traversal up to configurable depth | Derived Design Detail — standard graph operation |
| FR-32.6 | The system shall integrate with the Knowledge Layer (WP-30F) via `KnowledgeProvider` interface, exposing graph queries as a knowledge source | PLAN.md Section 7 execution order: WP-30F before WP-32 |
| FR-32.7 | The system shall integrate with the Memory Layer (WP-31) via `MemoryProvider` interface for graph context persistence | PLAN.md Section 7 execution order: WP-31 before WP-32 |
| FR-32.8 | The system shall maintain graph consistency with existing platform data without modifying entity tables | PLAN.md Section 9.9: Database Rules |
| FR-32.9 | The system shall expose a FastAPI router following project conventions | PLAN.md Section 9.10: FastAPI is the public contract |
| FR-32.10 | The system shall audit all graph mutations via existing audit framework | PLAN.md Section 9.12: Security Rules |

### 1.4 Non-Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| NFR-32.1 | Graph queries shall complete within acceptable latency for interactive use | Derived Design Detail |
| NFR-32.2 | The graph layer shall not modify existing entity tables | PLAN.md Section 9.9: Database Rules |
| NFR-32.3 | All graph operations shall be auditable via existing `log_audit()` function | PLAN.md Section 9.12: Security Rules; `app/services/audit.py` |
| NFR-32.4 | The implementation shall follow project coding standards (PEP 8, Pydantic schemas, thin routers) | PLAN.md Section 10.2 |
| NFR-32.5 | The Knowledge Graph shall function without Memory Layer (graceful degradation) | PLAN.md Section 9.4: Architecture Philosophy — graceful degradation pattern from WP-30/WP-31 |
| NFR-32.6 | The graph shall function as a separate bounded context without modifying DEM core | KNOWLEDGE_INGESTION_CONTRACT.md Principle: "Zero core changes" |

### 1.5 Constraints

1. **No new entity tables:** The graph layer does not add new business entity tables beyond graph metadata tables.
2. **SQLite persistence:** Consistent with project baseline (PLAN.md Section 3.1: Database = SQLite MVP).
3. **No DEM core modification:** Graph integration shall not modify DEM core logic.
4. **FastAPI router only:** No direct database access from routers (PLAN.md Section 9.10).
5. **No external graph database:** The graph is implemented as application-level metadata over existing SQLite tables.
6. **Existing entity tables immutable:** The graph layer reads existing entity data; it does not alter entity tables.
7. **KnowledgeProvider interface preserved:** The graph knowledge source shall implement the existing `KnowledgeProvider` interface without modification.

### 1.6 Assumptions

1. Existing entity IDs (customers, suppliers, shipments, invoices, documents, resources, hs_codes) are stable and used as graph node identifiers.
2. The Knowledge Layer registry (WP-30F) is available at application bootstrap.
3. The Memory Layer (WP-31) may be unavailable; the graph shall degrade gracefully.
4. Graph edges are derived from existing foreign keys in the baseline; explicit edges supplement but do not replace FK-derived edges.
5. "products" in PLAN.md Capability #10 refers to product information embedded in existing entity records (supplier.certificates, shipment.description, documents.metadata), not a separate entity table.

### 1.7 Acceptance Criteria

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| AC-32.1 | Graph nodes can be created/queried for all 7 baseline entity types (Customer, Supplier, Shipment, Invoice, Document, Resource, HsCode) | Unit test |
| AC-32.2 | FK-derived edges are automatically discoverable (supplier↔shipment↔customer, invoice↔shipment, customs_declaration↔shipment↔hs_code, export_workflow↔entities) | Integration test |
| AC-32.3 | Explicit edges can be created between any two graph nodes | Unit test |
| AC-32.4 | Querying a node returns its connected relationships (both FK-derived and explicit) | Integration test |
| AC-32.5 | Traversing relationships returns connected entities within configurable depth | Integration test |
| AC-32.6 | KnowledgeGraphProvider is registered in KnowledgeProviderRegistry and queryable | Integration test |
| AC-32.7 | MemoryProvider integration stores/recalls graph context | Integration test |
| AC-32.8 | Graph mutations are audited via `log_audit()` | Integration test |
| AC-32.9 | All existing tests continue to pass (no regressions) | Regression test |
| AC-32.10 | Graph router endpoints return valid OpenAPI schema | Contract test |
| AC-32.11 | Graceful degradation when MemoryProvider is unavailable | Integration test |

---

## 2. Implementation Plan

### 2.1 Phase 1: Specification & Data Model (WP-32A)

**Objective:** Define graph schema, Pydantic models, and database tables.

**Exit Criteria:**
- [ ] Graph node and edge schemas defined
- [ ] Graph metadata table schemas defined
- [ ] Schema review passed

#### Tasks

| Task | Description | Deliverable | Dependencies |
|------|-------------|-------------|--------------|
| 1.1 | Define graph node types and Pydantic schemas | `backend/app/schemas/knowledge_graph.py` | None |
| 1.2 | Define graph edge/relationship types and schemas | `backend/app/schemas/knowledge_graph.py` | Task 1.1 |
| 1.3 | Define `KnowledgeGraphProvider` implementing `KnowledgeProvider` interface | `backend/app/agent/knowledge/graph_provider.py` | WP-30F complete |
| 1.4 | Define `knowledge_nodes` and `knowledge_edges` table schemas | Schema definition | None |
| 1.5 | Add graph table creation to `init_db()` | `backend/app/core/database.py` | Task 1.4 |

### 2.2 Phase 2: Service Layer (WP-32B)

**Objective:** Implement graph business logic.

**Exit Criteria:**
- [ ] All CRUD operations for nodes and edges implemented
- [ ] Relationship traversal logic implemented
- [ ] FK-derived edge discovery implemented
- [ ] Service layer unit tests pass

#### Tasks

| Task | Description | Deliverable | Dependencies |
|------|-------------|-------------|--------------|
| 2.1 | Implement `KnowledgeGraphService` with node CRUD | `backend/app/services/knowledge_graph.py` | Phase 1 complete |
| 2.2 | Implement edge/relationship CRUD for explicit edges | `backend/app/services/knowledge_graph.py` | Task 2.1 |
| 2.3 | Implement FK-derived edge discovery from existing foreign keys | `backend/app/services/knowledge_graph.py` | Task 2.1 |
| 2.4 | Implement graph traversal (1-hop, 2-hop, depth-limited) | `backend/app/services/knowledge_graph.py` | Task 2.2, 2.3 |
| 2.5 | Implement entity synchronization from existing tables (on-demand, not real-time) | `backend/app/services/knowledge_graph.py` | Task 2.1 |
| 2.6 | Integrate MemoryProvider for graph context persistence | `backend/app/services/knowledge_graph.py` | WP-31 complete |
| 2.7 | Integrate audit logging via `log_audit()` for graph mutations | `backend/app/services/knowledge_graph.py` | Phase 1 complete |
| 2.8 | Unit tests for service layer | `backend/tests/test_services/test_knowledge_graph.py` | Tasks 2.1–2.7 |

### 2.3 Phase 3: API Layer (WP-32C)

**Objective:** Expose graph operations via FastAPI router.

**Exit Criteria:**
- [ ] Router registered in main.py
- [ ] All endpoints return valid responses
- [ ] OpenAPI schema generated

#### Tasks

| Task | Description | Deliverable | Dependencies |
|------|-------------|-------------|--------------|
| 3.1 | Create FastAPI router with graph endpoints | `backend/app/routers/knowledge_graph.py` | Phase 2 complete |
| 3.2 | Register router in `backend/main.py` | `backend/main.py` | Task 3.1 |
| 3.3 | Register `KnowledgeGraphProvider` in `KnowledgeProviderRegistry` | `backend/app/core/dependencies.py` or bootstrap | Phase 1 complete |
| 3.4 | Integration tests for router endpoints | `backend/tests/test_knowledge_graph.py` | Task 3.1 |

### 2.4 Phase 4: Testing & Validation (WP-32D)

**Objective:** Comprehensive testing and quality gate verification.

**Exit Criteria:**
- [ ] All tests pass
- [ ] No regressions in existing test suite
- [ ] Quality gates passed per PLAN.md Section 10.8

#### Tasks

| Task | Description | Deliverable | Dependencies |
|------|-------------|-------------|--------------|
| 4.1 | Integration tests for graph queries and traversals | `backend/tests/test_knowledge_graph_integration.py` | Phase 3 complete |
| 4.2 | Performance tests for graph queries with N entities | `backend/tests/test_knowledge_graph_performance.py` | Phase 3 complete |
| 4.3 | Security tests: entity isolation, authorization, SQL injection | `backend/tests/test_knowledge_graph_security.py` | Phase 3 complete |
| 4.4 | Regression test: full test suite passes | CI verification | All previous tasks |
| 4.5 | Quality gate verification | Checklist | Task 4.4 |

### 2.5 Phase 5: Documentation & Closure (WP-32E)

**Objective:** Document implementation and formally close WP-32.

**Exit Criteria:**
- [ ] `CURRENT_STATUS.md` updated
- [ ] `CHANGELOG.md` updated
- [ ] Closure review passed

#### Tasks

| Task | Description | Deliverable | Dependencies |
|------|-------------|-------------|--------------|
| 5.1 | Update `CURRENT_STATUS.md` with WP-32 summary | `CURRENT_STATUS.md` | Phase 4 complete |
| 5.2 | Update `CHANGELOG.md` with WP-32 entry | `CHANGELOG.md` | Phase 4 complete |
| 5.3 | Update `PLAN.md` Section 12.3 and Section 15.3 | `PLAN.md` | Phase 4 complete |
| 5.4 | Closure review | Review record | Tasks 5.1–5.3 |

### 2.6 WP-32 Completion Criteria

All of the following must be true:
- [ ] All Phase 1–5 exit criteria met
- [ ] All AC-32.1 through AC-32.11 verified
- [ ] Full test suite passes (no regressions)
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] No broken imports or circular dependencies
- [ ] No hidden runtime errors
- [ ] Documentation updated per PLAN.md Section 10.8
- [ ] `CHANGELOG.md` updated
- [ ] Engineering Decision recorded if any architectural deviation occurs

---

## 3. Traceability Matrix

| PLAN.md Reference | WP-32 Element | Task(s) | Deliverable | Acceptance Criteria |
|-------------------|---------------|---------|-------------|---------------------|
| Section 6.2 Capability #10 | Knowledge Graph capability | 1.1, 1.2, 2.1–2.5, 3.1 | `knowledge_graph.py` schemas, service, router | AC-32.1, AC-32.2, AC-32.4 |
| Section 7: WP-32 description | WP-32 execution | All | Full implementation | All AC-32.x |
| Section 12.3: WP التالية الفورية | Initiation trigger | Planning package | This document | Planning decision |
| Section 15.3: WP-32 status 🔴 مخطط | Closure target | 5.1–5.4 | Documentation updates | Completion criteria |
| Section 16.3: Phase 2 exit criteria | Phase 2 requirement | 2.1–2.8, 3.1–3.4, 4.1–4.5 | Knowledge Graph displaying entity relationships | AC-32.4 |
| Section 17.1: Traceability Matrix | Deliverable mapping | All | Knowledge Graph implementation, WP-32 tests | All AC-32.x |
| Section 9.3: Source of Truth | Schema authority | 1.1, 1.2 | Pydantic schemas | AC-32.10 |
| Section 9.10: API Rules | Router contract | 3.1, 3.2 | FastAPI router, OpenAPI schema | AC-32.10 |
| Section 9.12: Security Rules | Audit requirement | 2.7 | Audit integration | AC-32.8 |
| Section 10.8: Quality Gates | Completion requirements | 4.4, 4.5, 5.4 | Test suite, quality gate checklist | Completion criteria |
| Section 10.4: Testing Rules | Test coverage | 2.8, 4.1–4.3 | Test files | AC-32.9 |
| WP-30F (KnowledgeProvider interface) | Integration point | 1.3, 3.3 | `KnowledgeGraphProvider` | AC-32.6, AC-32.7 |
| WP-31 (MemoryProvider interface) | Integration point | 2.6 | Memory integration in service | AC-32.7, AC-32.11 |
| KNOWLEDGE_INGESTION_CONTRACT.md | Boundary rule | All | Zero DEM core changes | NFR-32.6 |

---

## 4. Testing Strategy

### 4.1 Unit Tests

**Scope:** Service layer and schema validation in isolation.

| Test Area | Coverage Target | Files |
|-----------|-----------------|-------|
| Graph node CRUD | All operations (create, read, update, delete) for each node type | `test_knowledge_graph.py` |
| Graph edge CRUD | All relationship types (FK-derived + explicit) | `test_knowledge_graph.py` |
| Graph traversal | 1-hop, 2-hop, depth-limited queries | `test_knowledge_graph.py` |
| FK-derived edge discovery | Correct edges derived from existing foreign keys | `test_knowledge_graph.py` |
| Schema validation | Invalid inputs rejected, defaults applied | `test_knowledge_graph.py` |
| Memory integration | store/recall of graph context via MemoryProvider | `test_knowledge_graph.py` |
| Audit integration | `log_audit()` called for mutations | `test_knowledge_graph.py` |

**Derived Design Detail:** Test count target is 30+ unit tests, consistent with WP-19 (71 tests) and WP-20 (34 tests) patterns.

### 4.2 Integration Tests

**Scope:** End-to-end API behavior with test database.

| Test Area | Coverage Target | Files |
|-----------|-----------------|-------|
| Router endpoints | All graph endpoints return correct status codes and shapes | `test_knowledge_graph_integration.py` |
| KnowledgeProvider registration | Graph provider registered and queryable via registry | `test_knowledge_graph_integration.py` |
| Entity sync | Graph nodes reflect existing platform entities | `test_knowledge_graph_integration.py` |
| Memory integration | Graph context persists across sessions | `test_knowledge_graph_integration.py` |
| Audit logging | Graph operations produce audit log entries | `test_knowledge_graph_integration.py` |
| FK-derived queries | Queries return correct FK-derived edges | `test_knowledge_graph_integration.py` |

**Derived Design Detail:** Test count target is 15+ integration tests.

### 4.3 Performance Tests

**Scope:** Query latency and throughput under load.

| Test Area | Coverage Target | Files |
|-----------|-----------------|-------|
| Node lookup latency | < 100ms for single node retrieval | `test_knowledge_graph_performance.py` |
| Edge traversal latency | < 200ms for 2-hop traversal | `test_knowledge_graph_performance.py` |
| Bulk query | Handle 1000+ nodes without degradation | `test_knowledge_graph_performance.py` |

**Derived Design Detail:** Performance thresholds are estimates based on project baseline; actual thresholds shall be validated during execution.

### 4.4 Security Tests

**Scope:** Authorization, data isolation, injection prevention.

| Test Area | Coverage Target | Files |
|-----------|-----------------|-------|
| Entity isolation | Users cannot access graph nodes from other tenants/users | `test_knowledge_graph_security.py` |
| Authorization | Graph endpoints require appropriate roles | `test_knowledge_graph_security.py` |
| SQL injection | Raw SQL queries in graph layer are parameterized | `test_knowledge_graph_security.py` |
| Audit completeness | All mutations produce audit entries | `test_knowledge_graph_security.py` |

### 4.5 Regression Tests

**Scope:** Ensure WP-32 does not break existing functionality.

| Test Area | Coverage Target | Method |
|-----------|-----------------|--------|
| Full backend test suite | 100% of existing tests pass | `pytest` |
| Frontend build | `npm run build` succeeds | CI check |
| Import integrity | No circular imports or broken imports | Static analysis |
| API contract stability | Existing endpoints unchanged | OpenAPI diff |

---

## 5. Governance & Scope Review

### 5.1 Scope Creep Check

| Potential Creep Item | Assessment | Disposition |
|---------------------|------------|-------------|
| New standalone "products" entity table | PLAN.md mentions "products" in Capability #10 description, but no product table exists in baseline; adding one exceeds documented scope | **Out of Scope** — "products" refers to product information embedded in existing entity records (supplier.certificates, shipment.description, documents.metadata) |
| Graph visualization frontend | Not mentioned in PLAN.md | **Out of Scope** |
| Neo4j or external graph database | PLAN.md Section 3.1 specifies SQLite; no graph DB mentioned | **Out of Scope** |
| LLM-powered graph inference | Not mentioned in PLAN.md; WP-33 covers intelligence | **Out of Scope** |
| Ingestion pipeline | KNOWLEDGE_INGESTION_CONTRACT.md Section 5 explicitly defers to future WP | **Out of Scope** |
| Real-time entity sync | Not required by PLAN.md; on-demand sync sufficient | **Out of Scope** |
| Graph analytics dashboard | Not mentioned in PLAN.md | **Out of Scope** |

### 5.2 Conflict Check with PLAN.md

| Check | Result |
|-------|--------|
| Execution order: WP-30F, WP-31 before WP-32 | ✅ Satisfied — both complete per PLAN.md Section 15.3 |
| Source of Truth priority | ✅ Preserved — Pydantic schemas defined before API |
| FastAPI as public contract | ✅ Preserved — thin router planned |
| No business logic in routers | ✅ Preserved — all logic in service layer |
| Database follows backend | ✅ Preserved — schema defined in Python, applied via init_db |
| Quality gates | ✅ Planned for Phase 4 |
| Branch policy | ✅ Will use `feature/wp32-knowledge-graph` per PLAN.md Section 18.1 |
| No new entity tables | ✅ Preserved — graph uses metadata tables only |

### 5.3 Conflict Check with WP-30 / WP-30F / WP-31

| Check | Result |
|-------|--------|
| WP-30 DEM core unchanged | ✅ Planned — graph is separate bounded context |
| WP-30F KnowledgeProvider interface unchanged | ✅ Planned — `KnowledgeGraphProvider` implements existing interface |
| WP-31 MemoryProvider interface unchanged | ✅ Planned — graph uses existing interface |
| Graceful degradation pattern | ✅ Planned — graph functions without MemoryProvider |
| Zero core changes principle | ✅ Planned — no DEM core modifications |

---

## 6. Derived Design Details

The following items are design decisions derived from project conventions and are NOT original requirements from PLAN.md:

1. **Graph persistence approach:** Application-level graph metadata over existing SQLite tables (no graph database).
2. **Node identity scheme:** Composite key `{entity_type}:{entity_id}` (e.g., `customer:1`, `supplier:2`, `shipment:5`) — derived from existing entity primary key patterns.
3. **Node type set:** Customer, Supplier, Shipment, Invoice, Document, Resource, HsCode — derived from existing entity tables in `backend/app/core/database.py`.
4. **FK-derived edges:** Derived from existing foreign keys in baseline tables:
   - shipments.supplier_id → suppliers
   - shipments.customer_id → customers
   - shipments.customs_declaration_id → customs_declarations
   - invoices.customer_id → customers
   - invoices.supplier_id → suppliers
   - invoices.shipment_id → shipments
   - customs_declarations.shipment_id → shipments
   - customs_declarations.hs_code_id → hs_codes
   - export_workflows.customer_id → customers
   - export_workflows.supplier_id → suppliers
   - export_workflows.invoice_id → invoices
   - export_workflows.customs_declaration_id → customs_declarations
   - export_workflows.shipment_id → shipments
   - export_workflow_items.workflow_id → export_workflows (polymorphic)
5. **Explicit edges:** User-defined relationships beyond FK constraints, stored in `knowledge_edges` with `relationship_type` and `metadata`.
6. **Traversal depth limit:** Default 2 hops, configurable — derived from typical graph query patterns.
7. **Performance thresholds:** <100ms node lookup, <200ms 2-hop traversal — estimated targets for validation.
8. **Test counts:** 30+ unit tests, 15+ integration tests — consistent with WP-19 (71 tests) and WP-20 (34 tests) patterns.
9. **Memory integration:** Graph context stored as `decision` type memory with importance 7 — derived from WP-31 memory types and importance scale.
10. **Audit integration:** Graph mutations logged via `log_audit()` with `entity_type="knowledge_graph"` — derived from existing audit pattern in `app/services/audit.py`.
11. **Router registration pattern:** `knowledge_graph.router` registered in `backend/main.py` alongside existing routers — derived from existing `routers/__init__.py` pattern.
12. **Graph metadata table schema:**
    - `knowledge_nodes`: id TEXT PK, entity_type TEXT NOT NULL, entity_id INTEGER NOT NULL, label TEXT, properties TEXT (JSON), created_at TIMESTAMP, updated_at TIMESTAMP
    - `knowledge_edges`: id TEXT PK, source_node_id TEXT NOT NULL, target_node_id TEXT NOT NULL, relationship_type TEXT NOT NULL, properties TEXT (JSON), created_at TIMESTAMP, created_by INTEGER, FOREIGN KEY (source_node_id) REFERENCES knowledge_nodes(id), FOREIGN KEY (target_node_id) REFERENCES knowledge_nodes(id)

---

## 7. Planning Decision

**GO**

**Evidence:**
1. `PLAN.md` Section 15.3: WP-32 is the immediate next work package after WP-31 (✅ مكتمل).
2. `PLAN.md` Section 12.3: `| المرحلة التالية | WP-32 — Knowledge Graph |` and `| المهام المكتملة | WP-01 through WP-31 |`.
3. Baseline is clean: `git status` = clean, HEAD = bbd7abb, synchronized with origin/main.
4. All prerequisites satisfied: WP-30, WP-30F, WP-31 complete per PLAN.md.
5. Scope is bounded and traceable to PLAN.md Section 6.2 Capability #10 and Section 7.
6. "products" ambiguity resolved: refers to product information in existing entity records, not a new table.
7. No scope creep identified in Section 5.1.
8. No conflicts with PLAN.md, WP-30, WP-30F, or WP-31 identified in Section 5.2 and 5.3.
9. Design details are explicitly marked as derived, not invented requirements.
10. Graph metadata table schemas are defined based on project conventions.

**Condition:** This decision approves WP-32 to enter the Execution phase. All derived design details in Section 6 are subject to validation during execution and may be adjusted without requiring a new Planning decision, provided scope and governance constraints are preserved.
