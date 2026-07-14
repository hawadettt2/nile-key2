# WP-21 — Platform Integration Implementation Roadmap

**Reference:** PLAN.md (Master Roadmap v2.1)  
**Phase:** 1.5 — Business Logic Re-alignment  
**Status:** Milestone 1, 2, 3 Complete — Ready for Milestone 4  
**Date:** 2026-07-14  
**Promoted from:** `.kilo/plans/wp21-platform-integration-plan.md`

---

## 1. Executive Summary

WP-21 transforms Nile Key from a collection of independent domain engines into an integrated export platform. It connects the ETA Engine (WP-19), Shipping Engine (WP-20), and existing Nile Key domains (customers, suppliers, customs, documents, resources) through four cross-cutting capabilities:

1. **Unified Search** — single entry point across all business entities
2. **Live Dashboard** — real-time operational visibility from ETA + Shipping
3. **Audit Logging** — tamper-evident compliance trail for all operations
4. **Email Notifications** — SMTP-based alerts for business events

**Core principle:** Integration must not break existing domain boundaries. Each domain remains independently testable and deployable. WP-21 adds cross-cutting infrastructure, not domain logic.

---

## 2. WP-21 Objective

Merge the ETA Engine (WP-19) and Shipping Engine (WP-20) with the existing Nile Key platform domains (customers, suppliers, customs, documents, resources) via:

- Centralized audit logging across all CRUD operations
- SMTP-based email notifications for business events
- Unified search across all business entities
- Live dashboard aggregating ETA + Shipping stats
- Export workflow lifecycle management

**Source:** PLAN.md §15.2 — WP-21 acceptance criteria.

---

## 3. Architecture Constraints

| Constraint | Source | Evidence |
|-----------|--------|----------|
| Router → Service → Database | PLAN.md §9.2 | All M1 routers contain zero persistence logic |
| No breaking changes to existing APIs | PLAN.md §14.1 | M1 added additive routes only |
| Raw SQL + `_ensure_*_schema()` | PLAN.md §3.4 | `database.py` extensions use same pattern |
| Secrets from environment only | PLAN.md §4 | SMTP fields in `config.py` |
| JWT + role-based access | PLAN.md §3.1 | `require_role` used in new routers |
| Pydantic v2 schemas | PLAN.md §3.1 | New schemas follow existing patterns |

---

## 4. Milestone Breakdown

### Milestone 1: Foundation (Notification Service + Audit Logging) — ✅ COMPLETE

**Commit:** `941efde`  
**Date:** 2026-07-14  
**Tests:** 52 new tests added (notification service: 17, audit service: 14, notification router: 8, audit router: 13)  
**Full suite:** 324 passed, 8 skipped, 0 failed

#### M1 Tasks — Execution Order and Status

| Task ID | Description | Status | Actual Output |
|---------|-------------|--------|---------------|
| M1-T1 | Add SMTP config to `app/core/config.py` | ✅ Done | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS` |
| M1-T2 | Create `app/schemas/notification.py` | ✅ Done | `NotificationTemplate`, `NotificationSend`, `NotificationResponse` |
| M1-T3 | Create `app/services/notification.py` | ✅ Done | `send_email()`, `send_template_email()`, `_render_template()`, `_load_template()` |
| M1-T4 | Add notification tables to `database.py` | ✅ Done | `notification_templates`, `notification_logs`, `notification_preferences` |
| M1-T5 | Create `app/routers/notifications.py` | ✅ Done | `POST /api/v1/notifications/send` |
| M1-T6 | Create `app/schemas/audit.py` | ✅ Done | `AuditLogCreate`, `AuditLogResponse` |
| M1-T7 | Extend `audit_logs` table | ✅ Done | Added `ip_address`, `user_agent`, `session_id` columns |
| M1-T8 | Create `app/services/audit.py` | ✅ Done | `log_audit()`, `list_audit_logs()` |
| M1-T9 | Integrate audit logging into 7 services | ✅ Done | customer, supplier, invoice, customs, document, resource, shipping, eta |
| M1-T10 | Create `app/routers/audit.py` | ✅ Done | `GET /api/v1/audit/logs` with filters |
| M1-T11 | Write tests for notification + audit | ✅ Done | 52 tests across 4 test files |

#### M1 Deliverables

| File | Type | Description |
|------|------|-------------|
| `backend/app/core/config.py` | Modified | SMTP configuration fields |
| `backend/app/core/database.py` | Modified | Notification tables + audit_logs extension |
| `backend/app/schemas/notification.py` | New | Notification Pydantic schemas |
| `backend/app/schemas/audit.py` | New | Audit log schemas |
| `backend/app/services/notification.py` | New | SMTP email service with template rendering |
| `backend/app/services/audit.py` | New | Audit logging service |
| `backend/app/routers/notifications.py` | New | Notification send endpoint |
| `backend/app/routers/audit.py` | New | Audit log query endpoint |
| `backend/app/services/customer.py` | Modified | Audit logging integration |
| `backend/app/services/supplier.py` | Modified | Audit logging integration |
| `backend/app/services/invoice.py` | Modified | Audit logging integration |
| `backend/app/services/customs.py` | Modified | Audit logging integration |
| `backend/app/services/document.py` | Modified | Audit logging integration |
| `backend/app/services/resource.py` | Modified | Audit logging integration |
| `backend/app/services/shipping/__init__.py` | Modified | Audit logging integration |
| `backend/app/services/eta/__init__.py` | Modified | Audit logging integration |
| `backend/main.py` | Modified | Router registration for notifications + audit |
| `backend/tests/test_services/test_notification_service.py` | New | 17 service tests |
| `backend/tests/test_services/test_audit_service.py` | New | 14 service tests |
| `backend/tests/test_notifications.py` | New | 8 router tests |
| `backend/tests/test_audit.py` | New | 13 router tests |

#### M1 Deviations from Plan

| # | Deviation | Plan Requirement | Actual Implementation | Impact |
|---|-----------|-----------------|----------------------|--------|
| 1 | Notification transport | ADR-WP21-001: `aiosmtplib` async | Synchronous `smtplib` | Functional but not async; acceptable for MVP |
| 2 | M1-T11 tests | Not in original plan | Added during implementation | Positive — test coverage exceeds plan |
| 3 | Router registration timing | M5-T1 | Done in M1 as compatibility fix | Required for router tests to execute |
| 4 | `send_template_email` error boundary | Router catches `EmailSendError` | Service returns failure dict; router handler unreachable for SMTP errors | Functional; error surfaced in response body |

#### M1 Architectural Observations

- **Router → Service → Database preserved:** All new routers delegate to service layer; zero persistence logic in routers.
- **Audit logging pattern:** `log_audit(current_user=current_user, data=AuditLogCreate(...))` placed immediately after successful `conn.commit()`.
- **System events:** `current_user=None` handled correctly for system-level events.
- **Backward compatibility:** No existing service, router, or schema modified in a breaking way.

#### M1 Exit Criteria

- All M1-T1 through M1-T11 tasks completed.
- All M1 tests passing (52/52).
- Regression tests PASS (324 passed, 8 skipped, 0 failed).
- Backward Compatibility PASS.
- Code Review PASS.
- Working Tree Clean.
- Git commit created for M1.
- Git push completed per project policy.
- CURRENT_STATUS.md updated to reflect M1 completion.
- This roadmap updated to reflect M1 actual status.

#### M1 Definition of Done

- All M1 deliverables complete (notification service, audit service, schemas, routers, database extensions, tests).
- All M1 acceptance criteria met: audit logging works, email notifications work.
- All tests passing; no known blockers.
- Architecture constraints preserved (Router → Service → Database).
- No scope creep introduced.

---

### Milestone 2: Search + Dashboard — ✅ COMPLETE

**Commit:** `adedc8e`  
**Date:** 2026-07-14  
**Tests:** 10 new tests added (search service + dashboard service + router tests)  
**Full suite:** 356 passed, 8 skipped, 0 failed

| Task ID | Description | Complexity | Dependencies | Expected Output |
|---------|-------------|------------|--------------|-----------------|
| M2-T1 | Create `app/schemas/search.py` | Low | None | `SearchRequest`, `SearchResponse`, `SearchResult` schemas |
| M2-T2 | Create `app/services/search.py` | High | M2-T1 | Unified search aggregating results from domain services using Business Search Keys |
| M2-T3 | Create `app/routers/search.py` | Medium | M2-T2 | `/api/v1/search` endpoint with filters |
| M2-T4 | Create `app/schemas/dashboard.py` | Low | None | `DashboardStats`, `DashboardTimeline`, `DashboardResponse` schemas |
| M2-T5 | Create `app/services/dashboard.py` | Medium | M2-T4 | Stats aggregation, timeline generation, notification count |
| M2-T6 | Create `app/routers/dashboard.py` | Medium | M2-T5 | `/api/v1/dashboard` endpoint with aggregated stats |
| M2-T7 | Write tests for search + dashboard | High | M2-T2, M2-T6 | Coverage for all search and dashboard functions |

#### M2 Deliverables

| File | Type | Description |
|------|------|-------------|
| `backend/app/schemas/search.py` | New | Search request/response schemas |
| `backend/app/services/search.py` | New | Unified search service |
| `backend/app/routers/search.py` | New | Search endpoint |
| `backend/app/schemas/dashboard.py` | New | Dashboard stats schemas |
| `backend/app/services/dashboard.py` | New | Dashboard aggregation service |
| `backend/app/routers/dashboard.py` | New | Dashboard endpoint |
| `backend/tests/test_services/test_search_service.py` | New | Search service tests |
| `backend/tests/test_services/test_dashboard_service.py` | New | Dashboard service tests |
| `backend/tests/test_search.py` | New | Search router tests |
| `backend/tests/test_dashboard.py` | New | Dashboard router tests |

#### M2 Architectural Impact

- New services follow existing Router → Service → Database pattern.
- Search service uses `build_list_query()` from `app/services/base.py`.
- Dashboard service uses read-only aggregation queries; no domain logic modification.

#### M2 Database Impact

- No new tables. Uses existing domain tables.

#### M2 API Impact

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/api/v1/search` | `get_current_user` | Global search |
| GET | `/api/v1/dashboard` | `get_current_user` | Aggregated stats |

#### M2 Testing Requirements

- Service tests: all public methods, error paths, edge cases
- Router tests: auth, validation, response format, error handling
- Regression: all existing tests must pass

#### M2 Search Design Policy

**Business Search Keys:** Each Domain Service is responsible for defining its own Business Search Keys. The Unified Search Service aggregates results from domain services and applies ranking; it does not define searchable fields.

- Search implementation uses SQL LIKE only.
- Results are ranked by relevance: Exact Match > Starts With > Contains.
- FTS5 is **out of scope** for WP-21. It may be evaluated in a future Work Package if performance requirements are not met.
- Specific searchable fields, result limits, and query construction are implementation decisions made during M2 Code Mode based on actual domain schemas. They are not specified in this roadmap.

#### M2 Exit Criteria

- All M2-T1 through M2-T7 tasks completed.
- All M2 tests passing.
- Regression tests PASS.
- Backward Compatibility PASS.
- Code Review PASS.
- Working Tree Clean.
- Git commit created for M2.
- Git push completed per project policy.
- CURRENT_STATUS.md updated to reflect M2 completion.
- This roadmap updated to reflect M2 actual status.

#### M2 Definition of Done

- All M2 deliverables complete (search service, dashboard service, schemas, routers, tests).
- All M2 acceptance criteria met: search works across entities, dashboard shows live data.
- All tests passing; no known blockers.
- Architecture constraints preserved (Router → Service → Database).
- No scope creep introduced.
- Business Search Keys defined and implemented per domain service policy.

---

### Milestone 3: Notification Triggers + Frontend — ✅ COMPLETE

**Commit:** `1bebd10`  
**Date:** 2026-07-14  
**Tests:** 17 new frontend tests added (Notifications: 9, NotificationBell: 8) + 17 new backend notification trigger tests  
**Full suite:** 373 passed, 8 skipped, 0 failed

| Task ID | Description | Complexity | Dependencies | Expected Output |
|---------|-------------|------------|--------------|-----------------|
| M3-T1 | Integrate notification triggers into ETA service | Medium | M1-T3 | ETA events send notifications |
| M3-T2 | Integrate notification triggers into Shipping service | Medium | M1-T3 | Shipping events send notifications |
| M3-T3 | Add `notification_preferences` table support | Low | M1-T4 | Per-user opt-in/opt-out by notification type |
| M3-T4 | Update frontend `api.ts` with new endpoints | Low | None | New API functions for search, dashboard, notifications, audit |
| M3-T5 | Update frontend `Dashboard.tsx` with live widgets | Medium | M3-T4 | ETA/Shipping stats, recent activity, notification count |
| M3-T6 | Create frontend Notifications page | Medium | M3-T4 | Notification list with read/unread status |
| M3-T7 | Add notification bell to layout | Low | M3-T6 | Icon with unread count dropdown |
| M3-T8 | Write frontend tests for new components | Medium | M3-T5, M3-T6 | Component tests |

#### M3 Deliverables

| File | Type | Description |
|------|------|-------------|
| `backend/app/services/eta/__init__.py` | Modified | Notification triggers on ETA state changes |
| `backend/app/services/shipping/__init__.py` | Modified | Notification triggers on Shipping state changes |
| `frontend/src/api.ts` | Modified | New API functions |
| `frontend/src/pages/Dashboard.tsx` | Modified | Live widgets |
| `frontend/src/pages/Notifications.tsx` | New | Notifications page |
| `frontend/src/components/NotificationBell.tsx` | New | Notification bell component |
| Frontend test files | New | Component tests |

#### M3 Architectural Impact

- Notification triggers added to existing ETA and Shipping services.
- Frontend follows existing React + Vite + Tailwind patterns.

#### M3 Database Impact

- `notification_preferences` table already created in M1-T4.

#### M3 API Impact

No new backend endpoints. Existing notification endpoints used by frontend.

#### M3 Testing Requirements

- Backend: verify notification triggers fire on ETA/Shipping state changes
- Frontend: component tests for new pages and widgets
- Regression: all existing tests must pass

#### M3 Exit Criteria

- All M3-T1 through M3-T8 tasks completed.
- All M3 tests passing.
- Regression tests PASS.
- Backward Compatibility PASS.
- Code Review PASS.
- Working Tree Clean.
- Git commit created for M3.
- Git push completed per project policy.
- CURRENT_STATUS.md updated to reflect M3 completion.
- This roadmap updated to reflect M3 actual status.

#### M3 Definition of Done

- All M3 deliverables complete (ETA/Shipping notification triggers, frontend updates, frontend tests).
- All M3 acceptance criteria met: notification triggers integrated, frontend components functional.
- All tests passing; no known blockers.
- Architecture constraints preserved.
- No scope creep introduced.

---

### Milestone 4: Export Operations Integration

**Status:** Complete  
**Prerequisites:** M1 Complete, M2 Complete, M3 Complete

| Task ID | Description | Complexity | Dependencies | Expected Output |
|---------|-------------|------------|--------------|-----------------|
| M4-T1 | Define export workflow state machine | Medium | None | States: draft → customs_ready → shipped → delivered (with conditional draft → shipped bypass when shipment_id exists; approved via CR-M4-001 Rev.1) |
| M4-T2 | Create `export_workflows` table | Low | None | Table for tracking export workflow instances |
| M4-T3 | Create `app/services/workflow.py` | High | M4-T2 | Service to manage export workflow lifecycle |
| M4-T4 | Create export workflow router | Medium | M4-T3 | CRUD endpoints for export workflows |
| M4-T5 | Create export summary document generator | Medium | M4-T3 | PDF or JSON export of all related entities |
| M4-T6 | Write tests for export workflow | High | M4-T3 | 15+ tests |

#### M4 Deliverables

| File | Type | Description |
|------|------|-------------|
| `backend/app/core/database.py` | Modified | `export_workflows` + `export_workflow_items` tables |
| `backend/app/schemas/workflow.py` | New | Workflow schemas |
| `backend/app/services/workflow.py` | New | Workflow lifecycle service |
| `backend/app/routers/workflow.py` | New | Workflow CRUD endpoints |
| `backend/tests/test_services/test_workflow_service.py` | New | Workflow service tests |
| `backend/tests/test_workflow.py` | New | Workflow router tests |

#### M4 Architectural Impact

- New service follows existing Router → Service → Database pattern.
- Workflow service orchestrates existing domain services (customer, invoice, customs, shipping).

#### M4 Database Impact

| Table | Purpose |
|-------|---------|
| `export_workflows` | Track export workflow instances |
| `export_workflow_items` | Items linked to export workflows |

#### M4 API Impact

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| GET | `/api/v1/export-workflows` | `get_current_user` | List workflows |
| POST | `/api/v1/export-workflows` | `get_current_user` | Create workflow |
| GET | `/api/v1/export-workflows/{id}` | `get_current_user` | Get workflow |
| PUT | `/api/v1/export-workflows/{id}` | `get_current_user` | Update workflow |
| POST | `/api/v1/export-workflows/{id}/submit` | `get_current_user` | Submit workflow |
| GET | `/api/v1/export-workflows/{id}/summary` | `get_current_user` | Generate summary |
| POST | `/api/v1/export-workflows/{id}/items` | `get_current_user` | Add workflow item (approved via CR-M4-001 Rev.1) |

#### M4 Testing Requirements

- Service tests: state transitions, validation, error paths
- Router tests: auth, CRUD, state transitions
- Integration tests: full export workflow lifecycle
- Regression: all existing tests must pass

#### M4 Exit Criteria

- All M4-T1 through M4-T6 tasks completed.
- All M4 tests passing.
- Regression tests PASS.
- Backward Compatibility PASS.
- Code Review PASS.
- Working Tree Clean.
- Git commit created for M4.
- Git push completed per project policy.
- CURRENT_STATUS.md updated to reflect M4 completion.
- This roadmap updated to reflect M4 actual status.

#### M4 Definition of Done

- All M4 deliverables complete (workflow service, workflow router, database tables, export summary generator, tests).
- All M4 acceptance criteria met: export workflow lifecycle functional, summary generation works.
- All tests passing; no known blockers.
- Architecture constraints preserved (Router → Service → Database).
- No scope creep introduced.

---

### Milestone 5: Polish + Integration Testing

**Status:** Complete  
**Prerequisites:** M1, M2, M3, M4 Complete  
**Commits:** `7efca3b` (M5-R5), `bee9f5b` (M5-R3), `9314fae` (M5-R2), `b8b2ecb` (M5-R1), `5957d2b` (M5-R4)  
**Tests:** 410 passed, 8 skipped, 0 failed

| Task ID | Description | Complexity | Dependencies | Expected Output | Status |
|---------|-------------|------------|--------------|-----------------|--------|
| M5-R5 | Update `.env.example` with missing variables | Low | None | `OWNER_PASSWORD`, SMTP vars documented | ✅ Done |
| M5-R3 | Enforce workflow state validation in `update_workflow()` | Medium | None | All transitions validated; CR-M4-001 Rev.1 bypass preserved | ✅ Done |
| M5-R2 | Add notification audit logging to `send_template_email()` | Medium | None | Audit + notification_log records created | ✅ Done |
| M5-R1 | Add live dashboard auto-refresh polling | Medium | None | Dashboard refreshes every 30s without manual reload | ✅ Done |
| M5-R4 | Enforce search RBAC with `require_role()` | Low | None | Search restricted to authorized roles | ✅ Done |

#### M5 Deliverables

| File | Type | Description |
|------|------|-------------|
| `backend/.env.example` | Modified | Added `OWNER_PASSWORD` and SMTP variables |
| `backend/app/services/workflow.py` | Modified | Added `_validate_transition()` call in `update_workflow()` |
| `backend/app/services/notification.py` | Modified | Added `_log_notification()` for audit + notification_logs |
| `backend/app/services/eta/__init__.py` | Modified | Pass `current_user` to notification triggers |
| `backend/app/services/shipping/__init__.py` | Modified | Pass `current_user` to notification triggers |
| `backend/app/routers/notifications.py` | Modified | Pass `current_user` to `send_template_email()` |
| `backend/app/routers/search.py` | Modified | Added `require_role()` dependency |
| `frontend/src/pages/Dashboard.tsx` | Modified | Added 30s auto-refresh polling |
| `backend/tests/test_services/test_workflow_service.py` | Modified | Updated mock for state validation |
| `backend/tests/test_services/test_notification_service.py` | Modified | Added 3 audit logging tests |
| `backend/tests/test_services/test_eta_notification_triggers.py` | Modified | Updated mock call assertions |
| `backend/tests/test_services/test_shipping_notification_triggers.py` | Modified | Updated mock call assertions |
| `backend/tests/test_search.py` | Modified | Added RBAC test |
| `PLAN.md` | Modified | WP-21 acceptance criteria marked complete |
| `CURRENT_STATUS.md` | Modified | Updated project state |
| `TECH_DEBT.md` | Modified | New debt items + resolution plan |

#### M5 Architectural Impact

- Router registration consolidation.
- Final verification of all cross-cutting concerns.

#### M5 Testing Requirements

- Full regression suite: all existing + new tests pass
- Notification audit tests pass
- Workflow state validation tests pass
- Search RBAC tests pass
- Frontend build verification

#### M5 Exit Criteria

- All M5-R1 through M5-R5 packages completed.
- All M5 tests passing.
- Regression tests PASS.
- Backward Compatibility PASS.
- Code Review PASS.
- Working Tree Clean.
- Git commits created for M5 packages.
- Git push completed per project policy.
- CURRENT_STATUS.md updated to reflect WP-21 completion.
- This roadmap updated to reflect WP-21 final status.
- All WP-21 acceptance criteria from PLAN.md §15.2 met.

#### M5 Definition of Done

- All M5 deliverables complete (env documentation, workflow validation, notification audit, dashboard live refresh, search RBAC).
- All M5 acceptance criteria met.
- All tests passing; no known blockers.
- Architecture constraints preserved.
- No scope creep introduced.
- Documentation updated (PLAN.md, CURRENT_STATUS.md, TECH_DEBT.md as needed).

---

## 5. Dependencies

### 5.1 Prerequisites

| Work Package | Status | Relevance |
|--------------|--------|-----------|
| WP-19 (ETA Engine) | ✅ Complete | ETA events trigger notifications; ETA data feeds dashboard |
| WP-20 (Shipping Engine) | ✅ Complete | Shipping events trigger notifications; Shipping data feeds dashboard |

### 5.2 Reused Modules

| Module | Reuse Pattern |
|--------|---------------|
| `app/core/database.py` | Extend with new tables via `_ensure_*_schema()` |
| `app/core/config.py` | Add SMTP configuration fields |
| `app/services/base.py` | Reuse utilities (`connection()`, `build_list_query()`, `now_iso()`) |
| `app/schemas/*.py` | Follow existing Pydantic patterns |
| `app/routers/*.py` | Follow existing thin-router pattern |
| Frontend `api.ts` | Add new API functions |
| Frontend `Dashboard.tsx` | Extend with new widgets |

### 5.3 New Modules Required

| Module | Purpose | Milestone |
|--------|---------|-----------|
| `app/services/notification.py` | SMTP email sending with template rendering | M1 ✅ |
| `app/services/audit.py` | Centralized audit logging | M1 ✅ |
| `app/services/search.py` | Unified search aggregation | M2 ✅ |
| `app/services/dashboard.py` | Dashboard stats aggregation | M2 ✅ |
| `app/services/workflow.py` | Export workflow lifecycle management | M4 |
| `app/schemas/notification.py` | Notification request/response schemas | M1 ✅ |
| `app/schemas/audit.py` | Audit log schemas | M1 ✅ |
| `app/schemas/search.py` | Search request/response schemas | M2 ✅ |
| `app/schemas/dashboard.py` | Dashboard stats schemas | M2 ✅ |
| `app/schemas/workflow.py` | Export workflow schemas | M4 |
| `app/routers/notifications.py` | Notification endpoints | M1 ✅ |
| `app/routers/audit.py` | Audit log endpoints | M1 ✅ |
| `app/routers/search.py` | Search endpoint | M2 ✅ |
| `app/routers/dashboard.py` | Dashboard endpoint | M2 ✅ |
| `app/routers/workflow.py` | Export workflow endpoints | M4 |

---

## 6. Deliverables

### 6.1 Milestone 1 — Complete

| Deliverable | Status |
|-------------|--------|
| Notification service with SMTP | ✅ Done |
| Audit logging service | ✅ Done |
| Notification schemas | ✅ Done |
| Audit schemas | ✅ Done |
| Notification router | ✅ Done |
| Audit router | ✅ Done |
| Database tables: `notification_templates`, `notification_logs`, `notification_preferences` | ✅ Done |
| Audit log extension: `ip_address`, `user_agent`, `session_id` | ✅ Done |
| Audit integration in 7 services | ✅ Done |
| Tests: 52 new tests | ✅ Done |

### 6.2 Milestone 2 — Complete

| Deliverable | Status |
|-------------|--------|
| Search service | ✅ Done |
| Search router + schemas | ✅ Done |
| Dashboard service | ✅ Done |
| Dashboard router + schemas | ✅ Done |
| Tests: search + dashboard | ✅ Done |

### 6.3 Milestone 3 — Complete

| Deliverable | Status |
|-------------|--------|
| ETA notification triggers | ✅ Done |
| Shipping notification triggers | ✅ Done |
| Notification preferences support | ✅ Done |
| Frontend: `api.ts` updates | ✅ Done |
| Frontend: `Dashboard.tsx` widgets | ✅ Done |
| Frontend: Notifications page | ✅ Done |
| Frontend: Notification bell | ✅ Done |
| Frontend tests | ✅ Done |
| Backend notification trigger tests | ✅ Done |

### 6.4 Milestone 4 — Complete (per CR-M4-001 Rev.1)

| Deliverable | Status |
|-------------|--------|
| Export workflow service | ✅ Complete |
| Export workflow router + schemas | ✅ Complete |
| Database: `export_workflows`, `export_workflow_items` | ✅ Complete |
| Export summary generator | ✅ Complete |
| Tests: workflow | ✅ Complete |
| `/items` endpoint | ✅ Complete (Engineering Decision, CR-M4-001 Rev.1) |
| `draft → shipped` bypass | ✅ Complete (Engineering Decision, CR-M4-001 Rev.1) |

### 6.5 Milestone 5 — Complete

| Deliverable | Status |
|-------------|--------|
| Dashboard live data auto-refresh | ✅ Complete (M5-R1) |
| Notification audit logging | ✅ Complete (M5-R2) |
| Workflow state validation | ✅ Complete (M5-R3) |
| Search RBAC enforcement | ✅ Complete (M5-R4) |
| Configuration documentation | ✅ Complete (M5-R5) |

---

## 7. Acceptance Criteria

**Source:** PLAN.md §15.2 — WP-21 acceptance criteria.

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | جميع الكيانات متصلة ببعضها البعض | ✅ Done | 8 services have audit logging; notification triggers integrated in ETA + Shipping; notification/audit services created; search RBAC enforced |
| 2 | لوحة القيادة تعرض بيانات حية من ETA والشحن | ✅ Done | Dashboard auto-refresh polling every 30s (M5-R1) |
| 3 | سجل التدقيق يعمل لجميع العمليات | ✅ Done | `audit.py` service + router + 8 service integrations + notification audit logging (M5-R2) |
| 4 | الإشعارات تعمل عبر البريد الإلكتروني | ✅ Done | `notification.py` service + router + ETA/Shipping triggers + notification audit logging + 17 backend trigger tests + frontend tests |
| 5 | البحث يعمل عبر جميع الكيانات | ✅ Done | `search.py` service + router + RBAC enforcement (M5-R4) + tests |

**Traceability Matrix:**

| PLAN.md Criterion | M1 Task | M2 Task | M3 Task | M4 Task | M5 Task |
|-------------------|---------|---------|---------|---------|---------|
| Audit logging works | M1-T8, M1-T9, M1-T10 | — | — | — | M5-R2 |
| Email notifications work | M1-T1, M1-T2, M1-T3, M1-T4, M1-T5 | — | M3-T1, M3-T2 | — | M5-R2 |
| Entities connected | M1-T9 | — | M3-T1, M3-T2 | M4-T3, M4-T4 | M5-R4 |
| Dashboard shows live data | — | M2-T4, M2-T5, M2-T6 | M3-T5 | — | M5-R1 |
| Search works across entities | — | M2-T1, M2-T2, M2-T3 | M3-T4 | — | M5-R4 |

---

## 8. Completion Status

### 8.1 Overall WP-21 Completion

| Milestone | Status | Completion |
|-----------|--------|------------|
| M1: Foundation | ✅ Complete | 100% |
| M2: Search + Dashboard | ✅ Complete | 100% |
| M3: Notification Triggers + Frontend | ✅ Complete | 100% |
| M4: Export Operations Integration | ✅ Complete (with conditions) | 100% |
| M5: Polish + Integration Testing | ✅ Complete | 100% |
| **WP-21 Total** | **Complete** | **100%** |

### 8.2 M2 Completion Details

| Metric | Value |
|--------|-------|
| New files created | 6 |
| Modified files | 1 (`frontend/src/App.tsx`) |
| Tests added | 10 |
| Test pass rate | 100% (10/10) |
| Regression tests | 356 passed, 8 skipped, 0 failed |
| Commit | `adedc8e` |
| Router endpoints | 2 (`/api/v1/search`, `/api/v1/dashboard`) |

### 8.3 M3 Completion Details

| Metric | Value |
|--------|-------|
| Modified files | 6 (`backend/app/services/eta/__init__.py`, `backend/app/services/shipping/__init__.py`, `backend/app/services/notification.py`, `frontend/src/services/api.ts`, `frontend/src/pages/Dashboard.tsx`, `frontend/src/components/layout/Layout.tsx`) |
| New files | 4 (`frontend/src/pages/Notifications.tsx`, `frontend/src/components/NotificationBell.tsx`, `frontend/src/test/setup.ts`, test files) |
| Frontend tests added | 17 |
| Backend notification trigger tests added | 17 |
| Test pass rate | 100% (frontend: 17/17, backend triggers: 17/17) |
| Regression tests | 373 passed, 8 skipped, 0 failed |
| Commits | `e3ae1db`, `df74ecc`, `cdaf29e`, `73bfc22`, `d53f1e0`, `cf27159`, `1fd2469`, `1bebd10` |
| Frontend pages added | 2 (`/notifications`, `/dashboard` live widgets) |
| Frontend components added | 1 (`NotificationBell`) |

### 8.4 M4 Completion Details

| Metric | Value |
|--------|-------|
| Modified files | 2 (`backend/app/core/database.py`, `backend/main.py`) |
| New files | 4 (`backend/app/schemas/workflow.py`, `backend/app/services/workflow.py`, `backend/app/routers/workflow.py`, test files) |
| Service tests added | 23 |
| Router tests added | 10 |
| Test pass rate | 100% (33/33) |
| Regression tests | 406 passed, 8 skipped, 0 failed |
| Commits | `f6aa5a4`, `5dcf72c` |
| Router endpoints added | 7 (`/api/v1/export-workflows`, `/export-workflows/{id}`, `/export-workflows/{id}/submit`, `/export-workflows/{id}/summary`, `/export-workflows/{id}/items`) |
| Database tables created | 2 (`export_workflows`, `export_workflow_items`) |
| Change Request | CR-M4-001 Rev.1 — Approved with conditions |
| Conditions | Business stakeholder notification of Engineering Decision required within 5 business days |

### 8.5 M5 Completion Details

| Metric | Value |
|--------|-------|
| Modified files | 12 |
| Tests added | 3 new tests (notification audit logging) |
| Test pass rate | 100% (410/410 passed, 8 skipped) |
| Regression tests | 410 passed, 8 skipped, 0 failed |
| Commits | `7efca3b` (M5-R5), `bee9f5b` (M5-R3), `9314fae` (M5-R2), `b8b2ecb` (M5-R1), `5957d2b` (M5-R4) |
| Frontend changes | Dashboard auto-refresh polling |
| Backend changes | Workflow validation, notification audit, search RBAC, env docs |
| Database schema changes | None |
| API contract changes | None |

### 8.6 M1 Completion Details

| Metric | Value |
|--------|-------|
| New files created | 8 |
| Modified files | 11 |
| Tests added | 52 |
| Test pass rate | 100% (52/52) |
| Regression tests | 324 passed, 8 skipped, 0 failed |
| Commit | `941efde` |
| Router endpoints | 2 (`/api/v1/notifications/send`, `/api/v1/audit/logs`) |
| Database tables created | 3 (`notification_templates`, `notification_logs`, `notification_preferences`) |
| Database tables extended | 1 (`audit_logs`) |
| Services with audit logging | 7 (customer, supplier, invoice, customs, document, resource, shipping, eta) |

---

## 9. Remaining Milestones

### 9.1 Milestone 2: Search + Dashboard

**Status:** Complete  
**Prerequisites:** M1 Complete

**Key tasks:**
- M2-T2: Unified search service (HIGH complexity) — aggregates across 8 entity types
- M2-T5: Dashboard aggregation service (MEDIUM complexity) — real-time stats from ETA + Shipping

**Deliverables:**
- `/api/v1/search` endpoint ✅
- `/api/v1/dashboard` endpoint ✅
- 10+ new tests ✅

### 9.2 Milestone 3: Notification Triggers + Frontend

**Status:** Complete  
**Prerequisites:** M1 Complete, M2 Complete (frontend depends on M2 API)

**Key tasks:**
- M3-T1, M3-T2: Notification triggers in ETA and Shipping services
- M3-T5, M3-T6: Frontend Dashboard + Notifications page

**Deliverables:**
- ETA + Shipping notification triggers ✅
- Backend notification preference support ✅
- Frontend: Dashboard widgets, Notifications page, Notification bell ✅
- Frontend tests ✅
- Backend notification trigger tests ✅

### 9.3 Milestone 4: Export Operations Integration

**Estimated effort:** High  
**Risk:** Medium (workflow state machine complexity)  
**Dependencies:** M1, M2 complete

**Key tasks:**
- M4-T3: Workflow service (HIGH complexity)
- M4-T5: Export summary generator

**Deliverables:**
- `/api/v1/export-workflows` endpoints
- 2 new database tables
- 15+ tests

### 9.4 Milestone 5: Polish + Integration Testing

**Status:** Complete  
**Prerequisites:** M1, M2, M3, M4 complete

**Key tasks:**
- M5-R1: Dashboard live data auto-refresh
- M5-R2: Notification audit logging
- M5-R3: Workflow state validation enforcement
- M5-R4: Search RBAC enforcement
- M5-R5: Configuration documentation

**Deliverables:**
- Dashboard auto-refresh polling ✅
- Notification audit logging ✅
- Workflow state validation ✅
- Search RBAC ✅
- `.env.example` documentation ✅

---

## 10. Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SMTP provider reliability | Medium | High | Use retry with backoff; log failures for manual retry |
| Search performance with large datasets | Medium | Medium | SQL LIKE acceptable for WP-21; FTS5 is out of scope and may be evaluated in a future Work Package |
| Notification spam / rate limiting | Low | Medium | Implement per-user cooldown and digest options |
| Audit log table growth | Medium | Low | Partition by month if table exceeds 1M rows |
| Frontend dashboard re-render performance | Low | Medium | Use React memo and virtualization for large lists |
| Breaking changes to existing API | Low | High | All changes additive; no endpoint modifications |
| Email template injection | Low | High | Sanitize template variables; use safe string formatting |
| **M2 search complexity** | **Medium** | **Medium** | **Business Search Keys must be defined per domain service during implementation** |
| **M4 workflow state machine** | **Medium** | **Medium** | **Define states clearly before implementation** |

---

## 11. Assumptions

1. SMTP provider will be selected by business owner (Open Question #1 in original plan)
2. Notification preferences table schema from M1 is sufficient for M3
3. Search uses SQL LIKE only in WP-21. FTS5 is out of scope and may be evaluated in a future Work Package.
4. Export workflow states are limited to: draft, customs_ready, shipped, delivered. Engineering Decision (CR-M4-001 Rev.1): `draft → shipped` bypass is permitted when `shipment_id` exists.
5. Frontend build environment remains stable (Vite + TypeScript + Tailwind)
6. No PostgreSQL migration during WP-21 (deferred to WP-40+)
7. Existing domain services remain unchanged during WP-21

---

## 12. Recommended Execution Order

1. **M2: Search + Dashboard** — highest value, lowest risk after M1
2. **M3: Notification Triggers + Frontend** — depends on M1 only; can run in parallel with M2 for frontend tasks
3. **M4: Export Operations Integration** — depends on M2 for dashboard context; highest complexity
4. **M5: Polish + Integration Testing** — final verification

**Parallelization opportunity:** M3 frontend tasks (M3-T4 through M3-T8) can proceed in parallel with M2 backend tasks.

---

## 13. Recommended Kilo Mode per Task

| Milestone | Recommended Mode |
|-----------|-----------------|
| M2 | **Code** — implementation of search and dashboard services |
| M3 | **Code** — notification triggers + frontend work |
| M4 | **Code** — workflow service and export operations |
| M5 | **Code** — integration tests, docs, final verification |

All remaining milestones are implementation tasks. No further planning mode required unless:
- M2 Business Search Keys definition requires domain service coordination
- M4 workflow state machine requires business rule clarification

---

## 14. Git Policy

All Git operations during WP-21 must comply with the following policy:

### 14.1 Commit Policy

- No commit is created before the task is fully completed and verified.
- Each task or logical group of tasks must be committed with a clear, single-purpose commit message.
- Commit message format: `feat(wp21): M{id}-T{id} - {description}` or `fix(wp21): M{id}-T{id} - {description}`.
- Working Tree must be clean before transitioning to the next milestone.

### 14.2 Push Policy

- Push is performed after milestone completion and verification.
- Milestone commit(s) are pushed to the remote repository before starting the next milestone.
- Branch protection rules from PLAN.md §18 apply: no direct commits to protected branches.

### 14.3 Rollback Policy

- Rollback is performed via `git revert` for committed changes.
- Database schema changes use `_ensure_*_schema()` which is idempotent; new tables/columns may remain or be manually removed.
- Rollback points are defined per milestone in the Rollback Strategy section of this roadmap.

### 14.4 Working Tree Policy

- Working Tree must be clean before starting a new milestone.
- No uncommitted changes are carried over between milestones.
- Untracked files that are part of deliverables must be added and committed before milestone closure.

---

## 15. Forensic Verification Checklist

This checklist must be completed and verified before approving any milestone closure.

□ **Architecture Verified** — All new code follows Router → Service → Database pattern; no persistence logic in routers.  
□ **Evidence Reviewed** — All implementation evidence inspected against plan requirements.  
□ **No Scope Creep** — No features, files, or logic outside the approved milestone scope.  
□ **Regression PASS** — All existing tests pass; no regressions introduced.  
□ **Backward Compatibility PASS** — No breaking changes to existing APIs, schemas, or services.  
□ **Tests PASS** — All new tests for the milestone pass.  
□ **Working Tree Clean** — No uncommitted changes; all deliverables committed.  
□ **Deliverables Verified** — All planned files, tables, and endpoints are present and functional.  
□ **Documentation Updated** — CURRENT_STATUS.md and this roadmap reflect actual status.  
□ **Commit Created** — Milestone commit(s) created with clear message.  
□ **Push Completed** — Commit(s) pushed to remote per project policy.  
□ **Milestone Approved** — Milestone is formally approved and ready for the next milestone.

---

## 16. Change History

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2026-07-13 | 1.0 | Initial WP-21 implementation plan created | Kilo |
| 2026-07-14 | 2.0 | Promoted to official roadmap; M1 completion verified; deviations documented | Kilo |
| 2026-07-14 | 2.1 | Added governance sections: Milestone Exit Criteria, Definition of Done, Git Policy, Forensic Verification Checklist | Kilo |
| 2026-07-14 | 2.2 | M2 and M3 completion verified; documentation updated to reflect actual implementation status | Kilo |
| 2026-07-15 | 2.3 | M4 and M5 completion verified; M5 remediation packages implemented and committed; WP-21 closure approved | Kilo |

---

## 17. Review Observations

### 17.1 Plan vs Actual M1 Implementation

| Aspect | Plan | Actual | Verdict |
|--------|------|--------|---------|
| Notification transport | `aiosmtplib` (async) | `smtplib` (sync) | Deviation — functional but not async per ADR |
| Test coverage | 20+ tests | 52 tests | Exceeds plan |
| Router registration | M5-T1 | M1 (compatibility fix) | Deviation — required for test execution |
| Error handling | Router catches `EmailSendError` | Service returns failure dict | Deviation — error surfaced in response body |
| Audit integration | 7 services | 8 services (including eta) | Exceeds plan |

### 17.2 Terminology Consistency

- PLAN.md uses Arabic/English mixed terms. This roadmap preserves PLAN.md terminology.
- "Notification Service" vs "Email Notifications": PLAN.md §15.2 criterion 4 uses "الإشعارات تعمل عبر البريد الإلكتروني". This roadmap uses "Email Notifications" for clarity.

### 17.3 Dependency Correctness

- M2 depends on M1: Correct (search/dashboard don't require notification triggers)
- M3 depends on M1: Correct (notification triggers use M1 service)
- M4 depends on M2: Correct (dashboard provides context for export workflows)
- M5 depends on M1-M4: Correct (final verification requires all features)

### 17.4 Architecture Consistency

- All M1 code follows Router → Service → Database pattern.
- No architectural changes required for M2-M5.
- New services will reuse `app/services/base.py` utilities.

### 17.5 Acceptance Criteria Mapping

- 4 of 5 PLAN.md acceptance criteria fully met (audit logging, email notifications, dashboard, search)
- 1 partially met (entity integration — all 8 services have audit logging; notification triggers integrated in ETA + Shipping)

---

## 18. Next Steps

1. **Begin M4:** Create export workflow service and related endpoints
2. **Update CURRENT_STATUS.md:** Reflect M2 and M3 completion
3. **Update TECH_DEBT.md:** Add M1 deviation notes (sync SMTP vs async ADR)
4. **No PLAN.md modification required:** PLAN.md remains the high-level vision document
