# WP-32 Specification: Knowledge Graph

**Work Package:** WP-32 — Knowledge Graph  
**Phase:** 2 — Intelligent Platform  
**Baseline:** bbd7abb0e68e06d97a977781ae7475f5145384fa  
**Authority:** PLAN.md (Master Roadmap v2.1) — Single Source of Truth  
**Engineering Decision:** ED-WP32-001 (Products Deferral)  
**Date:** 2026-07-20  
**Status:** Draft — Pending Approval  

---

## 1. Purpose

Implement the **Knowledge Graph** bounded context for the Digital Export Manager (DEM). The Knowledge Graph provides a structured representation of trade entities and their relationships, enabling the DEM to discover and traverse connections across the platform's data.

The Knowledge Graph answers the business need described in PLAN.md Section 6.2 Capability #10: "رسم معرفي - عملاء، موردين، منتجات، علاقات". Per ED-WP32-001, Products are deferred to a future Work Package. This Specification defines the Knowledge Graph for the remaining entities and relationships.

**Source:** PLAN.md Section 6.2 Capability #10, Section 7, Section 16.3, ED-WP32-001.

---

## 2. Scope

### 2.1 In Scope

| Component | Description | Source |
|-----------|-------------|--------|
| **Graph Node Types** | Customer, Supplier, Shipment, Invoice, Document, Resource, HSCode, CustomsDeclaration, ExportWorkflow | Repository evidence: existing entity tables, schemas, services, and relationship columns |
| **Graph Edge Types** | Relationships derived from existing entity reference columns plus explicit user-defined edges | Repository evidence: entity reference columns in `backend/app/core/database.py` |
| **Graph Persistence** | SQLite tables `knowledge_nodes` and `knowledge_edges` | PLAN.md Section 3.1: Database = SQLite MVP |
| **Service Layer** | `KnowledgeGraphService` with CRUD for nodes and edges, traversal logic, entity synchronization | PLAN.md Section 9.9: Database Rules; project service-layer pattern |
| **API Layer** | Thin FastAPI router exposing graph endpoints | PLAN.md Section 9.10: FastAPI is the public contract |
| **KnowledgeProvider Integration** | `KnowledgeGraphProvider` implementing `KnowledgeProvider` interface, registered in `KnowledgeProviderRegistry` | PLAN.md Section 7 execution order: WP-30F before WP-32 |
| **MemoryProvider Integration** | Graph context persistence via `MemoryProvider` interface with graceful degradation | PLAN.md Section 7 execution order: WP-31 before WP-32; PLAN.md Section 9.4 |
| **Audit Logging** | Graph mutations logged via existing `log_audit()` function | PLAN.md Section 9.12: Security Rules |
| **Pydantic Schemas** | Graph node, edge, and API response schemas | PLAN.md Section 9.3: Source of Truth = Backend Pydantic Schemas |

### 2.2 Out of Scope

| Item | Reason | Source |
|------|--------|--------|
| **Products** | Deferred to future Work Package per ED-WP32-001 | ED-WP32-001 |
| **New standalone products entity table** | No approved Product domain model exists | Repository evidence |
| **Graph visualization frontend** | Not mentioned in PLAN.md | PLAN.md |
| **LLM-powered graph reasoning or inference** | Not mentioned in PLAN.md; WP-33 covers intelligence | PLAN.md Section 6.2 Capability #9 |
| **Ingestion pipeline for external knowledge sources** | Deferred per KNOWLEDGE_INGESTION_CONTRACT.md Section 5 | KNOWLEDGE_INGESTION_CONTRACT.md |
| **Graph analytics or machine learning features** | Not mentioned in PLAN.md | PLAN.md |
| **Migration to graph-specific database** | PLAN.md Section 3.1 specifies SQLite | PLAN.md |
| **Modification of existing entity tables** | Graph layer reads existing entity data only | PLAN.md Section 9.9: Database Rules |

---

## 3. Objectives

1. Implement a Knowledge Graph that represents existing platform entities as nodes and their relationships as edges.
2. Enable the DEM to query and traverse entity relationships across the platform.
3. Integrate the Knowledge Graph with the existing Knowledge Layer (WP-30F) and Memory Layer (WP-31).
4. Maintain architectural boundaries: the Knowledge Graph is a separate bounded context that does not modify DEM core or existing entity tables.
5. Ensure all graph operations are auditable via the existing audit framework.

**Source:** PLAN.md Section 6.2 Capability #10, Section 7, Section 16.3.

---

## 4. Assumptions

1. **Entity IDs are stable:** Existing entity primary keys (customers.id, suppliers.id, shipments.id, etc.) are used as graph node identifiers. Changes to these IDs are managed by their respective services, not the Knowledge Graph.

2. **Knowledge Layer registry is available:** The `KnowledgeProviderRegistry` is initialized at application bootstrap and available for the Knowledge Graph provider to register.

3. **Memory Layer may be unavailable:** The Knowledge Graph functions without MemoryProvider; graph context is stored when available and skipped when unavailable.

4. **Existing entity reference columns define primary relationships:** The graph's initial edge set is derived from existing entity reference columns in the baseline database schema.

5. **Products are out of scope:** No Product domain model exists in the baseline. Products are deferred to a future Work Package per ED-WP32-001.

6. **Graph metadata is additive:** The Knowledge Graph stores metadata about existing entities without modifying the entity tables themselves.

---

## 5. Constraints

1. **No modification of existing entity tables:** The Knowledge Graph does not add columns to or modify existing entity tables (suppliers, customers, shipments, invoices, documents, resources, hs_codes, customs_declarations, export_workflows).

2. **SQLite persistence only:** The graph metadata is stored in SQLite, consistent with the project baseline (PLAN.md Section 3.1).

3. **No DEM core modification:** The Knowledge Graph does not modify DEM core logic, Decision Engine, Mission Planner, or Tool Orchestrator.

4. **FastAPI router only:** No direct database access from routers. All database operations occur in the service layer.

5. **No external graph database:** The graph is implemented as application-level metadata over SQLite tables.

6. **Pydantic schemas are the Source of Truth:** All API contracts and data validation use Pydantic schemas (PLAN.md Section 9.3).

7. **Graceful degradation:** The Knowledge Graph functions without MemoryProvider. Memory integration is optional.

8. **Audit all mutations:** All graph node and edge mutations are logged via `log_audit()`.

---

## 6. Knowledge Graph Model

### 6.1 Node Types

The Knowledge Graph models the following existing platform entities as nodes:

| Node Type | Entity Table | Pydantic Schema | Service | Router |
|-----------|--------------|-----------------|---------|--------|
| Customer | `customers` | `Customer` | `app/services/customer.py` | `app/routers/customers.py` |
| Supplier | `suppliers` | `Supplier` | `app/services/supplier.py` | `app/routers/suppliers.py` |
| Shipment | `shipments` | `Shipment` | `app/services/shipping.py` | `app/routers/shipping.py` |
| Invoice | `invoices` | `Invoice` | `app/services/invoice.py` | `app/routers/invoice.py` |
| Document | `documents` | `Document` | `app/services/document.py` | `app/routers/documents.py` |
| Resource | `resources` | `Resource` | `app/services/resource.py` | `app/routers/resources.py` |
| HSCode | `hs_codes` | `HSCode` | (part of customs service) | `app/routers/customs.py` |
| CustomsDeclaration | `customs_declarations` | `CustomsDeclaration` | `app/services/customs.py` | `app/routers/customs.py` |
| ExportWorkflow | `export_workflows` | `ExportWorkflow` | `app/services/workflow.py` | `app/routers/workflow.py` |

**Basis:** Each node type has a corresponding database table, Pydantic schema, service module, and router in the baseline repository. These are existing platform entities, not new additions.

**Source:** Repository evidence: `backend/app/core/database.py`, `backend/app/schemas/`, `backend/app/services/`, `backend/app/routers/`.

### 6.2 Edge Types

Edges represent relationships between nodes. The Knowledge Graph supports two categories of edges:

#### 6.2.1 Derived Edges (System-Generated)

Derived edges are automatically discoverable from existing entity reference columns in the baseline database:

| Source Node Type | Target Node Type | Relationship Column Source | Direction |
|------------------|------------------|-------------------|-----------|
| Shipment | Supplier | `shipments.supplier_id` | Shipment → Supplier |
| Shipment | Customer | `shipments.customer_id` | Shipment → Customer |
| Shipment | CustomsDeclaration | `shipments.customs_declaration_id` | Shipment → CustomsDeclaration |
| Invoice | Customer | `invoices.customer_id` | Invoice → Customer |
| Invoice | Supplier | `invoices.supplier_id` | Invoice → Supplier |
| Invoice | Shipment | `invoices.shipment_id` | Invoice → Shipment |
| CustomsDeclaration | Shipment | `customs_declarations.shipment_id` | CustomsDeclaration → Shipment |
| CustomsDeclaration | HSCode | `customs_declarations.hs_code_id` | CustomsDeclaration → HSCode |
| ExportWorkflow | Customer | `export_workflows.customer_id` | ExportWorkflow → Customer |
| ExportWorkflow | Supplier | `export_workflows.supplier_id` | ExportWorkflow → Supplier |
| ExportWorkflow | Invoice | `export_workflows.invoice_id` | ExportWorkflow → Invoice |
| ExportWorkflow | CustomsDeclaration | `export_workflows.customs_declaration_id` | ExportWorkflow → CustomsDeclaration |
| ExportWorkflow | Shipment | `export_workflows.shipment_id` | ExportWorkflow → Shipment |
| Document | Validated Entity | `documents.entity_type` + `documents.entity_id` | Document → {Customer, Supplier, Shipment, Invoice, etc.} — only when `entity_type` matches a supported graph node type |

**Source:** Repository evidence: entity reference columns in `backend/app/core/database.py` CREATE TABLE statements and `_ensure_*_schema()` functions.

#### 6.2.2 Explicit Edges (User-Defined)

Explicit edges are user-defined relationships not captured by entity reference columns. They are stored in the `knowledge_edges` table with:
- `relationship_type`: string label (e.g., "partner", "competitor", "alternative")
- `properties`: JSON metadata
- `created_by`: user ID

The set of allowed relationship types is defined in the WP-32 Implementation Plan. This Specification does not restrict the relationship type vocabulary.

### 6.3 Graph Metadata Tables

Two new SQLite tables store graph metadata:

```sql
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    label TEXT,
    properties TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_edges (
    id TEXT PRIMARY KEY,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    properties TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (source_node_id) REFERENCES knowledge_nodes(id),
    FOREIGN KEY (target_node_id) REFERENCES knowledge_nodes(id)
);
```

**Source:** Project convention: schema defined in Python, applied via `init_db()` (PLAN.md Section 9.9; repository pattern in `backend/app/core/database.py`).

### 6.4 Node Identity

Each graph node is identified by a composite key: `{entity_type}:{entity_id}` (e.g., `customer:1`, `supplier:2`, `shipment:5`). This identity is stable as long as the underlying entity exists.

**Basis:** Derived from repository pattern: existing entity tables use auto-increment integer primary keys; graph node identity combines entity type and ID for uniqueness across entity types.

---

## 7. Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-32.1 | The system shall create a graph node for any existing platform entity by entity type and entity ID | PLAN.md Section 6.2 Capability #10 |
| FR-32.2 | The system shall update graph node properties when the underlying entity data changes | PLAN.md Section 9.3: Source of Truth |
| FR-32.3 | The system shall delete graph nodes when the underlying entity is deleted | PLAN.md Section 9.9: Database Rules |
| FR-32.4 | The system shall expose derived edges based on existing entity reference columns between entities | PLAN.md Section 6.2 Capability #10: "علاقات" |
| FR-32.5 | The system shall allow creation of explicit edges between any two graph nodes with a user-defined relationship type | PLAN.md Section 6.2 Capability #10: "علاقات" |
| FR-32.6 | The system shall allow deletion of explicit edges | Repository pattern: CRUD completeness |
| FR-32.7 | The system shall query a node and return its connected relationships (both derived and explicit) | PLAN.md Section 16.3: "Knowledge Graph يعرض علاقات الكيانات" |
| FR-32.8 | The system shall traverse relationships up to a configurable depth | Repository pattern: graph traversal standard operation |
| FR-32.9 | The system shall integrate with the Knowledge Layer (WP-30F) by implementing `KnowledgeProvider` and exposing graph queries as a knowledge source | PLAN.md Section 7 execution order: WP-30F before WP-32 |
| FR-32.10 | The system shall integrate with the Memory Layer (WP-31) by storing and recalling graph context via `MemoryProvider` | PLAN.md Section 7 execution order: WP-31 before WP-32 |
| FR-32.11 | The system shall log all graph mutations (node create/update/delete, edge create/delete) via `log_audit()` | PLAN.md Section 9.12: Security Rules |
| FR-32.12 | The system shall function without MemoryProvider (graceful degradation) | PLAN.md Section 9.4: Architecture Philosophy |
| FR-32.13 | The system shall expose a FastAPI router following project conventions | PLAN.md Section 9.10: FastAPI is the public contract |
| FR-32.14 | The system shall not modify existing entity tables | PLAN.md Section 9.9: Database Rules |
| FR-32.15 | The system shall not modify DEM core logic | KNOWLEDGE_INGESTION_CONTRACT.md Principle: "Zero core changes" |
| FR-32.16 | The system shall not include Products in any form | ED-WP32-001 |

---

## 8. Non-Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| NFR-32.1 | Graph queries shall complete within acceptable latency for interactive use | Repository pattern: performance baseline for SQLite queries |
| NFR-32.2 | The graph layer shall not introduce circular imports or broken imports | PLAN.md Section 10.8 Quality Gates |
| NFR-32.3 | All graph operations shall handle missing entities gracefully (return empty results, not errors) | Repository pattern: defensive programming |
| NFR-32.4 | The implementation shall follow PEP 8 coding standards | PLAN.md Section 10.2 |
| NFR-32.5 | The Knowledge Graph provider shall register with `KnowledgeProviderRegistry` at application startup | WP-30F pattern: `KnowledgeProviderRegistry` |
| NFR-32.6 | Graph node and edge IDs shall be UUIDs or equivalent unique identifiers | Repository pattern: `agent_sessions.id` uses TEXT PRIMARY KEY |
| NFR-32.7 | The graph layer shall not introduce new environment variables or configuration dependencies | Repository pattern: minimal configuration |
| NFR-32.8 | All graph endpoints shall require authentication via `get_current_user` dependency | Repository pattern: `app/routers/customers.py` |
| NFR-32.9 | Graph mutations shall be restricted to authorized roles | Repository pattern: `require_role()` dependency |

---

## 9. Integration Points

### 9.1 KnowledgeProvider Interface (WP-30F)

| Aspect | Detail | Source |
|--------|--------|--------|
| Interface | `KnowledgeProvider` (abstract base class) | `backend/app/agent/knowledge/provider.py` |
| Methods | `query(query, context, scope, sources, limit)`, `get_sources()` | `backend/app/agent/knowledge/provider.py` |
| Registry | `KnowledgeProviderRegistry` with `register()`, `query()`, `list_providers()` | `backend/app/agent/knowledge/registry.py` |
| WP-32 Role | Implement `KnowledgeGraphProvider` as a concrete `KnowledgeProvider` | PLAN.md Section 7 |
| Registration | Register at application bootstrap or via dependency injection | Repository pattern: registry usage in WP-30F |

### 9.2 MemoryProvider Interface (WP-31)

| Aspect | Detail | Source |
|--------|--------|--------|
| Interface | `MemoryProvider` (abstract base class) | `backend/app/agent/memory/interface.py` |
| Methods | `recall(session_id, query, limit)`, `store(session_id, key, value, memory_type, importance, expires_at)`, `forget(session_id, key)`, `summarize(session_id)` | `backend/app/agent/memory/interface.py` |
| WP-32 Role | Store and recall graph context (e.g., frequent queries, traversal patterns) | PLAN.md Section 7 |
| Degradation | Graph functions without MemoryProvider; memory operations are skipped when unavailable | PLAN.md Section 9.4 |

### 9.3 Audit Framework

| Aspect | Detail | Source |
|--------|--------|--------|
| Function | `log_audit(current_user, data, ip_address, user_agent, session_id)` | `backend/app/services/audit.py` |
| Schema | `AuditLogCreate` with action, entity_type, entity_id, details | `backend/app/schemas/audit.py` |
| Table | `audit_logs` | `backend/app/core/database.py` |
| WP-32 Role | Log all graph mutations with `entity_type="knowledge_graph"` | PLAN.md Section 9.12 |

### 9.4 Service Layer Pattern

| Aspect | Detail | Source |
|--------|--------|--------|
| Base utilities | `connection()`, `build_list_query()`, `parse_json()`, `dumps_json()`, `now_iso()` | `backend/app/services/base.py` |
| Pattern | Service functions use `connection()` context manager, return dicts | Repository pattern: `app/services/customer.py` |
| WP-32 Role | `KnowledgeGraphService` follows same pattern | PLAN.md Section 9.9 |

### 9.5 Router Pattern

| Aspect | Detail | Source |
|--------|--------|--------|
| Registration | `app.include_router(knowledge_graph.router)` in `backend/main.py` | `backend/main.py` |
| Dependencies | `get_current_user`, `require_role()` | `backend/app/routers/customers.py` |
| Response models | Pydantic schemas from `backend/app/schemas/` | PLAN.md Section 9.3 |
| WP-32 Role | Thin router delegating to `KnowledgeGraphService` | PLAN.md Section 9.10 |

---

## 10. Data Sources

| Data Source | Description | Source |
|-------------|-------------|--------|
| `customers` table | Customer entity data | `backend/app/core/database.py` |
| `suppliers` table | Supplier entity data | `backend/app/core/database.py` |
| `shipments` table | Shipment entity data with `supplier_id`, `customer_id`, `customs_declaration_id` relationship columns | `backend/app/core/database.py` |
| `invoices` table | Invoice entity data with `customer_id`, `supplier_id`, `shipment_id` relationship columns | `backend/app/core/database.py` |
| `documents` table | Document entity data with `entity_type`, `entity_id` polymorphic reference | `backend/app/core/database.py` |
| `resources` table | Resource entity data | `backend/app/core/database.py` |
| `hs_codes` table | HS Code entity data | `backend/app/core/database.py` |
| `customs_declarations` table | Customs Declaration entity data with `shipment_id`, `hs_code_id` relationship columns | `backend/app/core/database.py` |
| `export_workflows` table | Export Workflow entity data with `customer_id`, `supplier_id`, `invoice_id`, `customs_declaration_id`, `shipment_id` relationship columns | `backend/app/core/database.py` |
| `knowledge_nodes` table | Graph node metadata (to be created) | This Specification |
| `knowledge_edges` table | Graph edge metadata (to be created) | This Specification |

**Note:** The Knowledge Graph does not modify any of the source entity tables. It reads from them to synchronize graph nodes and derives edges from their relationship columns.

---

## 11. API Requirements

### 11.1 Router Registration

| Requirement | Detail | Source |
|-------------|--------|--------|
| Prefix | `/api/v1/knowledge-graph` | Repository pattern: `app/routers/customers.py` uses `/api/v1/customers` |
| Tags | `["Knowledge Graph"]` | Repository pattern: FastAPI tag groups |
| Registration | `app.include_router(knowledge_graph.router)` in `backend/main.py` | `backend/main.py` |

### 11.2 Endpoints

| Method | Path | Description | Request Body | Response |
|--------|------|-------------|--------------|----------|
| GET | `/nodes/{entity_type}/{entity_id}` | Get a graph node | — | `KnowledgeGraphNode` |
| POST | `/nodes` | Create or update a graph node | `KnowledgeGraphNodeCreate` | `KnowledgeGraphNode` |
| DELETE | `/nodes/{entity_type}/{entity_id}` | Delete a graph node | — | `MessageResponse` |
| GET | `/nodes/{entity_type}/{entity_id}/relationships` | Get relationships for a node | — | `KnowledgeGraphRelationships` |
| POST | `/edges` | Create an explicit edge | `KnowledgeGraphEdgeCreate` | `KnowledgeGraphEdge` |
| DELETE | `/edges/{edge_id}` | Delete an explicit edge | — | `MessageResponse` |
| GET | `/traverse/{entity_type}/{entity_id}` | Traverse relationships from a node | Query params: `depth`, `direction` | `KnowledgeGraphTraversal` |
| GET | `/search` | Search graph nodes by label or properties | Query params: `query`, `entity_type` | `list[KnowledgeGraphNode]` |
| POST | `/sync` | Synchronize graph nodes from existing entity tables | — | `SyncResult` |

**Source:** Repository pattern: existing routers expose CRUD + specialized operations (e.g., `app/routers/customers.py`, `app/routers/shipping.py`).

### 11.3 Request/Response Schemas

| Schema | Purpose | Source |
|--------|---------|--------|
| `KnowledgeGraphNode` | Graph node representation | PLAN.md Section 9.3 |
| `KnowledgeGraphNodeCreate` | Create/update node input | PLAN.md Section 9.3 |
| `KnowledgeGraphEdge` | Graph edge representation | PLAN.md Section 9.3 |
| `KnowledgeGraphEdgeCreate` | Create edge input | PLAN.md Section 9.3 |
| `KnowledgeGraphRelationships` | Node with connected edges | PLAN.md Section 9.3 |
| `KnowledgeGraphTraversal` | Traversal result set | PLAN.md Section 9.3 |
| `SyncResult` | Synchronization operation result | Repository pattern: `IdResponse`, `MessageResponse` |

**Basis:** Derived from project Pydantic schema pattern (`backend/app/schemas/`).

---

## 12. Testing Strategy

### 12.1 Unit Tests

**Scope:** Service layer and schema validation in isolation.

| Test Area | Coverage Target | Files |
|-----------|-----------------|-------|
| Node CRUD | Create, read, update, delete for each node type | `backend/tests/test_services/test_knowledge_graph.py` |
| Edge CRUD | Create and delete explicit edges | `backend/tests/test_services/test_knowledge_graph.py` |
| Derived edge discovery | Correct edges derived from existing entity reference columns | `backend/tests/test_services/test_knowledge_graph.py` |
| Graph traversal | 1-hop, 2-hop, depth-limited queries | `backend/tests/test_services/test_knowledge_graph.py` |
| Entity synchronization | Nodes reflect existing platform entities | `backend/tests/test_services/test_knowledge_graph.py` |
| Memory integration | store/recall of graph context via MemoryProvider | `backend/tests/test_services/test_knowledge_graph.py` |
| Audit integration | `log_audit()` called for mutations | `backend/tests/test_services/test_knowledge_graph.py` |
| Graceful degradation | Service functions without MemoryProvider | `backend/tests/test_services/test_knowledge_graph.py` |

**Source:** PLAN.md Section 10.4: "كل خدمة MUST لها unit tests."

### 12.2 Integration Tests

**Scope:** End-to-end API behavior with test database.

| Test Area | Coverage Target | Files |
|-----------|-----------------|-------|
| Router endpoints | All graph endpoints return correct status codes and shapes | `backend/tests/test_knowledge_graph.py` |
| KnowledgeProvider registration | Graph provider registered and queryable via registry | `backend/tests/test_knowledge_graph.py` |
| Entity synchronization | Graph nodes reflect existing platform entities via API | `backend/tests/test_knowledge_graph.py` |
| Memory integration | Graph context persists across sessions via API | `backend/tests/test_knowledge_graph.py` |
| Audit logging | Graph operations produce audit log entries via API | `backend/tests/test_knowledge_graph.py` |
| Derived edge queries | API returns correct derived edges | `backend/tests/test_knowledge_graph.py` |
| Authentication | Endpoints require valid authentication | `backend/tests/test_knowledge_graph.py` |
| Authorization | Mutations require appropriate roles | `backend/tests/test_knowledge_graph.py` |

**Source:** PLAN.md Section 10.4: "كل router MUST لها integration tests."

### 12.3 Regression Tests

**Scope:** Ensure WP-32 does not break existing functionality.

| Test Area | Coverage Target | Method |
|-----------|-----------------|--------|
| Full backend test suite | 100% of existing tests pass | `pytest` |
| Frontend build | `npm run build` succeeds | CI check |
| Import integrity | No circular imports or broken imports | Static analysis |
| API contract stability | Existing endpoints unchanged | OpenAPI diff |

**Source:** PLAN.md Section 10.8 Quality Gates.

### 12.4 Performance Tests

**Scope:** Query latency and throughput under load.

| Test Area | Coverage Target | Files |
|-----------|-----------------|-------|
| Node lookup latency | Acceptable latency for single node retrieval | `backend/tests/test_knowledge_graph_performance.py` |
| Edge traversal latency | Acceptable latency for multi-hop traversal | `backend/tests/test_knowledge_graph_performance.py` |
| Bulk query | Handle 1000+ nodes without degradation | `backend/tests/test_knowledge_graph_performance.py` |

**Basis:** Derived from repository performance baseline and PLAN.md Section 10.8.

### 12.5 Security Tests

**Scope:** Authorization, data isolation, injection prevention.

| Test Area | Coverage Target | Files |
|-----------|-----------------|-------|
| Entity isolation | Users cannot access graph nodes from other tenants/users | `backend/tests/test_knowledge_graph_security.py` |
| Authorization | Graph endpoints require appropriate roles for mutations | `backend/tests/test_knowledge_graph_security.py` |
| SQL injection | Raw SQL queries in graph layer are parameterized | `backend/tests/test_knowledge_graph_security.py` |
| Audit completeness | All mutations produce audit entries | `backend/tests/test_knowledge_graph_security.py` |

**Source:** PLAN.md Section 9.12: Security Rules.

---

## 13. Acceptance Criteria

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| AC-32.1 | Graph nodes can be created for all 9 node types (Customer, Supplier, Shipment, Invoice, Document, Resource, HSCode, CustomsDeclaration, ExportWorkflow) | Integration test |
| AC-32.2 | Graph nodes reflect underlying entity data (name, status, key attributes) | Integration test |
| AC-32.3 | Derived edges are discoverable for all entity reference column relationships listed in Section 6.2.1 | Integration test |
| AC-32.4 | Explicit edges can be created between any two graph nodes | Unit + integration test |
| AC-32.5 | Explicit edges can be deleted | Unit + integration test |
| AC-32.6 | Querying a node returns its connected relationships (both derived and explicit) | Integration test |
| AC-32.7 | Traversing relationships returns connected entities within configurable depth | Integration test |
| AC-32.8 | KnowledgeGraphProvider is registered in KnowledgeProviderRegistry and queryable | Integration test |
| AC-32.9 | MemoryProvider integration stores and recalls graph context | Integration test |
| AC-32.10 | Graph operations are audited via `log_audit()` with `entity_type="knowledge_graph"` | Integration test |
| AC-32.11 | Graph functions without MemoryProvider (graceful degradation) | Integration test |
| AC-32.12 | All existing tests continue to pass (no regressions) | Regression test |
| AC-32.13 | Graph router endpoints return valid OpenAPI schema | Contract test |
| AC-32.14 | Graph endpoints require authentication | Integration test |
| AC-32.15 | Graph mutations require appropriate authorization | Integration test |
| AC-32.16 | Products are not represented in the Knowledge Graph in any form | Code review + test |

---

## 14. Implementation Boundaries

### 14.1 What the WP-32 Implementation Shall Do

1. Create `backend/app/schemas/knowledge_graph.py` with Pydantic schemas for nodes, edges, and API responses.
2. Create `backend/app/agent/knowledge/graph_provider.py` implementing `KnowledgeProvider` interface.
3. Create `backend/app/services/knowledge_graph.py` with `KnowledgeGraphService` implementing all CRUD and traversal operations.
4. Create `backend/app/routers/knowledge_graph.py` with FastAPI router exposing graph endpoints.
5. Add `knowledge_nodes` and `knowledge_edges` table creation to `backend/app/core/database.py` `init_db()`.
6. Register `KnowledgeGraphProvider` in `KnowledgeProviderRegistry` at application startup.
7. Write unit tests for service layer in `backend/tests/test_services/test_knowledge_graph.py`.
8. Write integration tests for router in `backend/tests/test_knowledge_graph.py`.
9. Write performance tests in `backend/tests/test_knowledge_graph_performance.py`.
10. Write security tests in `backend/tests/test_knowledge_graph_security.py`.

### 14.2 What the WP-32 Implementation Shall NOT Do

1. Modify existing entity tables (suppliers, customers, shipments, invoices, documents, resources, hs_codes, customs_declarations, export_workflows).
2. Modify DEM core logic (Decision Engine, Mission Planner, Tool Orchestrator).
3. Modify `KnowledgeProvider` interface.
4. Modify `MemoryProvider` interface.
5. Introduce new environment variables or configuration dependencies.
6. Include Products in any form.
7. Add business logic to routers.
8. Access databases directly from routers.
9. Create temporary or experimental code.

---

## 15. Out-of-Scope Items (Explicit)

| Item | Reason | Source |
|------|--------|--------|
| **Products** | Deferred to future Work Package per ED-WP32-001 | ED-WP32-001 |
| **New standalone products entity** | No approved Product domain model exists | Repository evidence |
| **Graph visualization frontend** | Not mentioned in PLAN.md | PLAN.md |
| **LLM-powered graph reasoning** | Not mentioned in PLAN.md; WP-33 covers intelligence | PLAN.md Section 6.2 Capability #9 |
| **Ingestion pipeline** | Deferred per KNOWLEDGE_INGESTION_CONTRACT.md Section 5 | KNOWLEDGE_INGESTION_CONTRACT.md |
| **Graph analytics or ML features** | Not mentioned in PLAN.md | PLAN.md |
| **External graph database** | PLAN.md Section 3.1 specifies SQLite | PLAN.md |
| **Real-time entity sync** | Not required by PLAN.md; on-demand sync sufficient | Repository pattern |

---

## 16. Traceability to PLAN.md

| PLAN.md Reference | WP-32 Requirement | Implementation Artifact |
|-------------------|-------------------|------------------------|
| Section 6.2 Capability #10 | Knowledge Graph for trade entities | All WP-32 artifacts |
| Section 7: WP-32 description | WP-32 execution order after WP-30F and WP-31 | Integration points with KnowledgeProvider and MemoryProvider |
| Section 9.3: Source of Truth | Pydantic schemas define API contracts | `backend/app/schemas/knowledge_graph.py` |
| Section 9.4: Architecture Philosophy | Graceful degradation without MemoryProvider | NFR-32.7, AC-32.11 |
| Section 9.9: Database Rules | No modification of existing entity tables | FR-32.14, Section 14.2 |
| Section 9.10: API Rules | FastAPI as public contract, thin routers | Section 11, FR-32.13 |
| Section 9.12: Security Rules | Audit all mutations | FR-32.11, AC-32.10 |
| Section 10.2: Coding Standards | PEP 8, Pydantic, pytest | NFR-32.4 |
| Section 10.3: Review Rules | PR review required | Implementation process |
| Section 10.4: Testing Rules | Unit tests for services, integration tests for routers | Section 12.1, 12.2 |
| Section 10.8: Quality Gates | Project builds, backend starts, tests pass | Section 12.3 |
| Section 10.11: Architecture Preservation | No architectural changes | ED-WP32-001 Section 4 |
| Section 14.1: Implementation Rules | All 10 implementation requirements met | Full Specification |
| Section 15.3: WP-32 status | WP-32 is next work package | This Specification |
| Section 16.3: Phase 2 exit criteria | Knowledge Graph displays entity relationships | AC-32.7 |
| Section 17.1: Traceability Matrix | Deliverable mapping | This Specification |
| Section 18: Branch Policy | Branch naming, PR requirements | Implementation process |
| ED-WP32-001 | Products deferred | AC-32.16, Section 2.2, Section 14.2 |

---

## 17. Dependencies

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

## 18. Risks

| Risk | Evidence | Likelihood | Impact | Mitigation |
|------|----------|------------|--------|------------|
| Business stakeholder expects Products in WP-32 | PLAN.md Capability #10 lists "products" | Medium | Medium | ED-WP32-001 documents deferral; future WP addresses products |
| Graph node set does not match future Product domain model | No Product schema exists | Low | Low | ED-WP32-001 allows future addition |
| Performance degradation with large graph | SQLite baseline; no graph DB | Medium | Medium | Performance tests validate thresholds |
| MemoryProvider unavailable in some deployments | WP-31 may be optional | Low | Low | Graceful degradation implemented |
| Circular imports between graph module and existing modules | New module integration | Low | Medium | Follow existing import patterns; static analysis in CI |
| Existing entity data inconsistency | Legacy data quality issues | Medium | Low | Graph sync handles missing/invalid references gracefully |

---

## 19. Self-Review Checklist

### 19.1 Internal Consistency

| Check | Status |
|-------|--------|
| Node types defined in Section 6.1 match acceptance criteria in Section 13 | ✅ Consistent |
| Edge types defined in Section 6.2 match functional requirements in Section 7 | ✅ Consistent |
| Integration points in Section 9 match assumptions in Section 4 | ✅ Consistent |
| API endpoints in Section 11 are covered by acceptance criteria in Section 13 | ✅ Consistent |
| Test strategy in Section 12 covers all functional requirements in Section 7 | ✅ Consistent |
| Out-of-scope items in Section 15 align with ED-WP32-001 | ✅ Consistent |
| Traceability matrix in Section 16 covers all PLAN.md references | ✅ Consistent |

### 19.2 Consistency with PLAN.md

| Check | Status |
|-------|--------|
| Purpose aligns with PLAN.md Section 6.2 Capability #10 | ✅ Consistent |
| Scope does not expand beyond PLAN.md | ✅ Consistent |
| Products deferred per ED-WP32-001 | ✅ Consistent |
| Node set based on existing entities (no new tables) | ✅ Consistent |
| FastAPI router pattern followed | ✅ Consistent |
| Pydantic schemas as Source of Truth | ✅ Consistent |
| Audit logging required | ✅ Consistent |
| Quality gates defined | ✅ Consistent |
| Testing rules followed | ✅ Consistent |
| Architecture preserved (no ADL needed) | ✅ Consistent |

### 19.3 Consistency with ED-WP32-001

| Check | Status |
|-------|--------|
| Products are out of scope | ✅ Consistent (Section 2.2, AC-32.16) |
| Node set defined in Specification, not ED | ✅ Consistent (Section 6) |
| No architectural changes required | ✅ Consistent (Section 14.2) |
| No ADL entry required | ✅ Consistent (Section 14.2) |

### 19.4 Scope Creep Check

| Potential Creep | Status | Disposition |
|-----------------|--------|-------------|
| New products entity | ❌ Not included | Out of scope per ED-WP32-001 |
| Graph visualization | ❌ Not included | Out of scope per PLAN.md |
| LLM reasoning | ❌ Not included | Out of scope per PLAN.md |
| Ingestion pipeline | ❌ Not included | Out of scope per KNOWLEDGE_INGESTION_CONTRACT.md |
| External graph DB | ❌ Not included | Out of scope per PLAN.md |
| Analytics/ML | ❌ Not included | Out of scope per PLAN.md |

### 19.5 Unsupported Assumptions Check

| Assumption | Evidence | Status |
|------------|----------|--------|
| Entity IDs are stable | Repository pattern: auto-increment integer PKs | ✅ Supported |
| KnowledgeProviderRegistry available | WP-30F complete per PLAN.md | ✅ Supported |
| MemoryProvider may be unavailable | PLAN.md Section 9.4 graceful degradation pattern | ✅ Supported |
| Entity reference columns define primary relationships | Repository evidence: database schema | ✅ Supported |
| Products are out of scope | ED-WP32-001 | ✅ Supported |
| Graph metadata is additive | PLAN.md Section 9.9 Database Rules | ✅ Supported |

---

## 20. Completion Criteria

All of the following must be true for WP-32 to be considered complete:

- [ ] All FR-32.1 through FR-32.16 implemented and verified
- [ ] All AC-32.1 through AC-32.16 verified
- [ ] All unit tests pass (Section 12.1)
- [ ] All integration tests pass (Section 12.2)
- [ ] All security tests pass (Section 12.5)
- [ ] Performance tests meet thresholds (Section 12.4)
- [ ] Full regression test suite passes (Section 12.3)
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] No broken imports or circular dependencies
- [ ] No hidden runtime errors
- [ ] No modifications to existing entity tables
- [ ] No modifications to DEM core
- [ ] `CHANGELOG.md` updated
- [ ] `CURRENT_STATUS.md` updated
- [ ] Engineering Decision recorded if any architectural deviation occurs

---

## 21. Implementation Notes

### 21.1 Node Synchronization Strategy

The Knowledge Graph maintains graph nodes as a lightweight metadata layer over existing entities. Node synchronization is **on-demand**, not real-time. The Implementation Plan shall define the synchronization triggers (e.g., on entity create/update/delete, on explicit sync API call, on graph query if node is stale).

### 21.2 Derived Edge Discovery

Derived edges are computed from existing entity reference columns at query time or precomputed and stored in `knowledge_edges` with a system-generated `relationship_type`. The Implementation Plan shall define the approach.

### 21.3 Memory Integration Depth

Graph context stored in MemoryProvider uses `memory_type="decision"` or `memory_type="context"` with `importance=7`. The Implementation Plan shall define the exact memory keys and values.

### 21.4 Authorization Model

The graph endpoints follow the existing authorization pattern: `get_current_user` for authentication, `require_role()` for mutation authorization. The Implementation Plan shall define the exact roles permitted for each operation.

---

**Document Status:** Draft — Pending Approval  
**Next Action:** Implementation Planning after Specification approval  
**Supersedes:** No prior WP-32 Specification exists
