# WP-21 Milestone 4 — Export Operations Integration Implementation Plan

## Objective
Create the export workflow lifecycle service, schemas, router, database tables, and export summary generator.

## Authoritative Source
- `.kilo/plans/1783879837991-wp21-platform-integration-roadmap.md` (Milestone 4 section)
- M4 is a pure orchestration milestone: new service layer + schemas + router + tables, no changes to existing domain services.

## Milestone 4 Requirements (from roadmap)

### Deliverables
| File | Type | Description |
|------|------|-------------|
| `backend/app/core/database.py` | Modified | `export_workflows` + `export_workflow_items` tables |
| `backend/app/schemas/workflow.py` | New | Workflow schemas |
| `backend/app/services/workflow.py` | New | Workflow lifecycle service |
| `backend/app/routers/workflow.py` | New | Workflow CRUD endpoints |
| `backend/tests/test_services/test_workflow_service.py` | New | Workflow service tests |
| `backend/tests/test_workflow.py` | New | Workflow router tests |

### API Endpoints
| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/api/v1/export-workflows` | `get_current_user` | List workflows |
| POST | `/api/v1/export-workflows` | `get_current_user` | Create workflow |
| GET | `/api/v1/export-workflows/{id}` | `get_current_user` | Get workflow |
| PUT | `/api/v1/export-workflows/{id}` | `get_current_user` | Update workflow |
| POST | `/api/v1/export-workflows/{id}/submit` | `get_current_user` | Submit workflow |
| GET | `/api/v1/export-workflows/{id}/summary` | `get_current_user` | Generate summary |
| POST | `/api/v1/export-workflows/{id}/items` | `get_current_user` | Add workflow item |

### State Machine
`draft` → `customs_ready` → `shipped` → `delivered`

**Business rule:** A workflow in `draft` may transition directly to `shipped` when `shipment_id` is already set, bypassing `customs_ready`. This supports the case where shipping documentation is prepared before customs clearance is finalized. All other transitions follow the strict linear path.

### Testing Requirements
- Service tests: state transitions, validation, error paths
- Router tests: auth, CRUD, state transitions
- Integration tests: full export workflow lifecycle
- Regression: all existing tests must pass

## Design Decisions

### D1: Workflow Entity Model
An `export_workflow` represents a single export shipment lifecycle. It tracks:
- `id` (auto-increment PK)
- `workflow_number` (human-readable: `EW-YYYYMMDDHHMMSS`)
- `state` (enum: `draft`, `customs_ready`, `shipped`, `delivered`)
- `customer_id` (FK to customers)
- `supplier_id` (FK to suppliers)
- `invoice_id` (FK to invoices)
- `customs_declaration_id` (FK to customs_declarations)
- `shipment_id` (FK to shipments)
- `notes` (free text)
- `created_at`, `updated_at`
- `created_by` (user ID)

`export_workflow_items` tracks individual items/entities linked to the workflow:
- `id` (auto-increment PK)
- `workflow_id` (FK)
- `entity_type` (e.g., `invoice`, `customs_declaration`, `shipment`, `document`)
- `entity_id` (FK to the specific entity)
- `metadata` (JSON string for additional context)

**Rationale:** Workflow is an orchestration layer, not a replacement for existing domain entities. It holds references to existing entities.

### D2: State Machine Rules
Valid transitions:
- `draft` → `customs_ready` (requires `customs_declaration_id`)
- `draft` → `shipped` (requires `shipment_id`)
- `customs_ready` → `shipped` (requires `shipment_id`)
- `shipped` → `delivered`

Invalid transitions raise `ValueError("Invalid state transition")`.

### D3: Workflow Service Architecture
The workflow service:
1. Creates/reads/updates/deletes workflow records in the database
2. On state transitions, calls relevant domain services (e.g., `submit_declaration`, `create_shipment`)
3. Does NOT modify existing domain services — only orchestrates via existing service APIs
4. Logs audit events for all state changes

**Key services used:**
- `app.services.customs.submit_declaration()` — when transitioning to `customs_ready`
- `app.services.shipping.create_shipment()` — when transitioning to `shipped`
- `app.services.audit.log_audit()` — for all state changes

### D4: Export Summary Document
`GET /api/v1/export-workflows/{id}/summary` returns a JSON document containing:
- Workflow metadata (number, state, dates)
- Customer info (name, country)
- Supplier info (name, country)
- Invoice summary (number, total, currency, items)
- Customs declaration summary (declaration number, HS codes, duties)
- Shipment summary (tracking number, carrier, status)
- Linked documents list
- Audit log entries for this workflow

**Format:** JSON (not PDF) to match existing API patterns and avoid new dependencies.

### D5: Validation Rules
- `customer_id` and `supplier_id` required on creation
- `invoice_id` required before transitioning to `customs_ready`
- `customs_declaration_id` required before transitioning to `shipped`
- `shipment_id` required before transitioning to `delivered`
- Cannot modify `customer_id`, `supplier_id`, `invoice_id` after creation
- Only `state`, `notes`, `customs_declaration_id`, `shipment_id` are mutable

## Task Breakdown

### M4-T1: Define export workflow state machine and schemas
**Complexity:** Low
**Dependencies:** None

Create `backend/app/schemas/workflow.py` with:
- `ExportWorkflowState` enum
- `ExportWorkflowBase`
- `ExportWorkflowCreate`
- `ExportWorkflowUpdate`
- `ExportWorkflowItemCreate`
- `ExportWorkflowItem`
- `ExportWorkflow` (response model)
- `ExportWorkflowSummary` (response model for summary endpoint)
- `ExportWorkflowListResponse` (pagination wrapper)

### M4-T2: Create `export_workflows` and `export_workflow_items` tables
**Complexity:** Low
**Dependencies:** M4-T1

Add `_ensure_export_workflows_schema()` and `_ensure_export_workflow_items_schema()` to `backend/app/core/database.py`.

Tables:
- `export_workflows`: id, workflow_number, state, customer_id, supplier_id, invoice_id, customs_declaration_id, shipment_id, notes, created_at, updated_at, created_by
- `export_workflow_items`: id, workflow_id, entity_type, entity_id, metadata, created_at

### M4-T3: Create `app/services/workflow.py`
**Complexity:** High
**Dependencies:** M4-T2

Implement:
- `list_workflows()` — paginated list with filters
- `get_workflow(workflow_id)` — single workflow with joined data
- `create_workflow(data, current_user)` — create new workflow
- `update_workflow(workflow_id, data, current_user)` — update mutable fields
- `transition_workflow(workflow_id, new_state, current_user)` — state machine with validation
- `submit_workflow(workflow_id, current_user)` — convenience method to advance through states
- `generate_workflow_summary(workflow_id)` — assemble export summary JSON
- `_validate_transition(current_state, new_state)` — state machine rules
- `_build_workflow_number()` — generate human-readable number

### M4-T4: Create `app/routers/workflow.py`
**Complexity:** Medium
**Dependencies:** M4-T3

Implement 6 endpoints:
- `GET /api/v1/export-workflows` — list with filters
- `POST /api/v1/export-workflows` — create
- `GET /api/v1/export-workflows/{id}` — get one
- `PUT /api/v1/export-workflows/{id}` — update
- `POST /api/v1/export-workflows/{id}/submit` — advance state
- `GET /api/v1/export-workflows/{id}/summary` — generate summary
- `POST /api/v1/export-workflows/{id}/items` — add workflow item

### M4-T5: Create export summary document generator
**Complexity:** Medium
**Dependencies:** M4-T3

Implement `generate_workflow_summary()` in `workflow.py`:
- Fetch workflow core data
- Fetch related customer, supplier, invoice, customs declaration, shipment
- Fetch linked documents
- Assemble structured JSON response
- Include audit log entries for workflow actions

### M4-T6: Write tests for export workflow
**Complexity:** High
**Dependencies:** M4-T3

Create:
- `backend/tests/test_services/test_workflow_service.py` — 10+ tests:
  - Create workflow
  - List workflows with filters
  - Get workflow
  - Update workflow
  - Valid state transitions
  - Invalid state transitions
  - Submit workflow (full lifecycle)
  - Generate summary
  - Workflow with missing required fields
  - Workflow items CRUD

- `backend/tests/test_workflow.py` — 5+ tests:
  - Auth required
  - Create endpoint
  - Get endpoint
  - Update endpoint
  - Submit endpoint
  - Summary endpoint

Total: 15+ tests

## Dependency Graph

```
M4-T1 (schemas)
  └─→ M4-T2 (database tables)
        └─→ M4-T3 (service)
              ├─→ M4-T4 (router)
              ├─→ M4-T5 (summary generator — part of service)
              └─→ M4-T6 (tests)
```

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| State machine complexity | Medium | Medium | Implement strict validation; document valid transitions |
| Summary generation data volume | Low | Low | Paginate/limit related entity fetches |
| Cross-service orchestration errors | Medium | Medium | Wrap external service calls in try/except; propagate meaningful errors |
| Database schema migration | Low | Low | Use `_ensure_*_schema()` pattern (idempotent) |
| Existing domain service compatibility | Low | High | Do not modify existing services; only call them |

## Acceptance Criteria Checklist

- [ ] `export_workflows` table exists with correct schema
- [ ] `export_workflow_items` table exists with correct schema
- [ ] Workflow schemas validate correctly
- [ ] `POST /api/v1/export-workflows` creates workflows
- [ ] `GET /api/v1/export-workflows` lists workflows with filters
- [ ] `GET /api/v1/export-workflows/{id}` returns workflow with joined data
- [ ] `PUT /api/v1/export-workflows/{id}` updates mutable fields
- [ ] `POST /api/v1/export-workflows/{id}/submit` advances state machine
- [ ] `POST /api/v1/export-workflows/{id}/items` adds workflow items
- [ ] Invalid state transitions raise `ValueError`
- [ ] `GET /api/v1/export-workflows/{id}/summary` returns complete export summary
- [ ] All 15+ tests pass
- [ ] Regression tests pass (373 passed, 8 skipped)
- [ ] Backward compatibility preserved
- [ ] Router registered in `main.py`

## Recommended Implementation Sequence

1. **M4-T1** — Define schemas (foundation for everything else)
2. **M4-T2** — Create database tables (foundation for service)
3. **M4-T3** — Implement workflow service (core logic)
4. **M4-T4** — Create router (expose API)
5. **M4-T5** — Implement summary generator (part of service, can be done with M4-T3)
6. **M4-T6** — Write tests (after service is stable)

**Note:** M4-T5 is logically part of M4-T3 (same file), but can be developed/tested independently after M4-T3 is complete.
