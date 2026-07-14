# WP-21 Milestone 5 — Stage A: Baseline Verification Report

**Project:** Nile Key Digital Platform  
**Baseline Commit:** c6d8fec7d97bf0b6a7187fbeca351e2d6aa9be78  
**Branch:** main  
**Verification Date:** 2026-07-14  
**Verifier:** Kilo (Automated Forensic Audit)  
**Scope:** Evidence-based baseline verification only. No implementation performed.

---

## 1. Entity Integration

### Evidence Summary

| Entity | Router | Service | Schema | DB Table | Integration Points |
|--------|--------|---------|--------|----------|-------------------|
| Customer | `routers/customers.py` (6 endpoints) | `services/customer.py` (6 functions) | `schemas/customer.py` | `customers` | Invoice, Shipping, Workflow, ETA, Search, Dashboard, Audit |
| Supplier | `routers/suppliers.py` (5 endpoints) | `services/supplier.py` (5 functions) | `schemas/supplier.py` | `suppliers` | Invoice, Shipping, Workflow, ETA, Search, Dashboard, Audit |
| Invoice | `routers/invoice.py` (7 endpoints) | `services/invoice.py` (7 functions) | `schemas/invoice.py` | `invoices` | Customer, Supplier, Shipping, ETA, Workflow, Search, Dashboard, Audit |
| Customs | `routers/customs.py` (8 endpoints) | `services/customs.py` (8 functions) | `schemas/customs.py` | `customs_declarations`, `hs_codes` | Shipping, Workflow, Search, Dashboard, Audit |
| ETA | `routers/eta.py` (11 endpoints) | `services/eta/__init__.py` (12+ functions) | `schemas/eta.py` | `eta_connectors`, `eta_logs`, `eta_log_documents` | Invoice, Customer, Supplier, Notifications, Audit, Search, Dashboard |
| Shipping | `routers/shipping.py` (17 endpoints) | `services/shipping/__init__.py` (15+ functions) | `schemas/shipping.py` | `shipments`, `shipping_providers`, `shipping_parcel_templates`, `shipping_labels`, `shipping_logs` | Customer, Supplier, Customs, Workflow, Notifications, Search, Dashboard, Audit |
| Workflow | `routers/workflow.py` (7 endpoints) | `services/workflow.py` (7 functions) | `schemas/workflow.py` | `export_workflows`, `export_workflow_items` | Customer, Supplier, Invoice, Customs, Shipping, Documents, Audit |
| Notifications | `routers/notifications.py` (1 endpoint) | `services/notification.py` (4 functions) | `schemas/notification.py` | `notification_templates`, `notification_logs`, `notification_preferences` | ETA, Shipping, Dashboard |
| Search | `routers/search.py` (1 endpoint) | `services/search.py` (1 main function) | `schemas/search.py` | Reads 9 tables | None (unidirectional) |
| Dashboard | `routers/dashboard.py` (1 endpoint) | `services/dashboard.py` (6 functions) | `schemas/dashboard.py` | Reads 10 tables | None (unidirectional) |
| Audit | `routers/audit.py` (1 endpoint) | `services/audit.py` (2 functions) | `schemas/audit.py` | `audit_logs` | Called by 10 of 11 entities |

### Missing Connections

1. **No enforced foreign keys** — Only `eta_log_documents.eta_log_id -> eta_logs.id` has an FK constraint. All other cross-entity references (`invoices.customer_id`, `shipments.supplier_id`, `export_workflows.*`, etc.) are unenforced integer columns.
2. **Workflow not in Search** — `export_workflows` table is not searchable.
3. **Workflow not in Dashboard** — No workflow count or status breakdown in dashboard stats.
4. **Notifications not in Search** — `notification_templates` and `notification_logs` are not searchable.
5. **ETA not integrated with Workflow** — Workflow transitions do not trigger ETA submission.
6. **Notifications not integrated with Workflow** — Workflow transitions do not send notifications.
7. **Notifications not audited** — `send_template_email` does not call `log_audit` and does not write to `notification_logs`.
8. **Reverse lookups missing** — No entity router provides endpoints to list related child entities (e.g., Customer → invoices).
9. **Orphaned tables** — `contacts` and `addresses` tables exist but have no router/service endpoints.

### Status

**PARTIALLY READY** — All 11 entities are implemented at router/service/schema level. Core integrations exist (Audit covers 10/11 entities, Workflow orchestrates 6 entities). However, critical structural gaps remain: no enforced referential integrity, Workflow excluded from Search/Dashboard, Notification audit trail missing, and no event-driven integration between Workflow, ETA, and Notifications.

---

## 2. Dashboard

### Evidence

| Component | File | Lines | Status |
|-----------|------|-------|--------|
| Router | `backend/app/routers/dashboard.py` | 7–12 | Implemented |
| Service | `backend/app/services/dashboard.py` | 5–93 | Implemented |
| Aggregation | `get_dashboard()` | 71–93 | Implemented |
| Data source | Direct SQLite queries | 8, 16–22, 38–45, 52–59, 66 | Implemented |
| Update mechanism | Frontend `Dashboard.tsx` | 38–48 | **Only on mount** |

### Key Finding

The dashboard is **not live**. The frontend loads data once via `useEffect(() => { loadDashboard(); }, [])` with no `setInterval`, WebSocket, or polling loop. The backend schedulers (ETA and Shipping) do not update dashboard data. Every page load issues 11 SQL queries synchronously with no caching.

### Status

**NOT READY** — The PLAN.md acceptance criterion for WP-21 requires "لوحة القيادة تعرض بيانات حية من ETA والشحن" (Dashboard displays live data from ETA and Shipping). Current evidence shows only on-demand page-load refresh. No live update mechanism exists.

---

## 3. Notifications

### Evidence

| Component | File | Lines | Classification |
|-----------|------|-------|----------------|
| Notification service | `backend/app/services/notification.py` | 1–123 | Implemented |
| SMTP integration | `smtplib.SMTP` | 84–89 | Implemented (code) |
| SMTP configuration | `backend/app/core/config.py` | 46–52 | Configured (schema) |
| SMTP runtime vars | `backend/.env` | — | **Not configured** (`SMTP_HOST=""`) |
| ETA trigger — submit invoice | `services/eta/__init__.py` | 449–453 | Implemented |
| ETA trigger — submit receipt | `services/eta/__init__.py` | 610–614 | Implemented |
| Shipping trigger — create shipment | `services/shipping/__init__.py` | 944–948 | Implemented |
| Shipping trigger — status update | `services/shipping/__init__.py` | 963–968 | Implemented |
| Manual endpoint | `routers/notifications.py` | 12–28 | Implemented |
| Notification preferences | `notification.py` | 50–60 | Implemented |
| Notification audit | `services/notification.py` | 97–123 | **Missing** — no `log_audit` call |
| Stub functions | `services/eta/__init__.py` | 940, 995, 1044 | Dead code — never invoked |

### Invocation Paths Verified

1. **Shipping create → notification** — `POST /shipments` → `create_shipment()` → `_send_shipping_notification(template_id=3)` → `send_template_email()` → `send_email()` → **blocked at SMTP layer** because `SMTP_HOST=""`.
2. **Shipping status update → notification** — `PUT /shipments/{id}` → `update_shipment()` → `_send_shipping_notification(template_id=4)` → same chain → **blocked**.
3. **ETA submit invoice → notification** — `POST /eta/invoices/{id}/submit` → `submit_invoice_to_eta()` → `_send_eta_notification(template_id=1)` → same chain → **blocked**.
4. **ETA submit receipt → notification** — `POST /eta/receipts` → `submit_receipt_to_eta()` → `_send_eta_notification(template_id=2)` → same chain → **blocked**.

### Status

**IMPLEMENTED BUT NOT OPERATIONAL** — The notification service, SMTP code, and trigger paths are fully implemented and traceable end-to-end. However, the runtime environment (`backend/.env`) lacks SMTP configuration. `SMTP_HOST` defaults to `""`, causing `send_email()` to raise `EmailSendError("SMTP host is not configured")` before any network call. Additionally, notification sends are not audited.

---

## 4. Search

### Evidence

| Component | File | Lines | Status |
|-----------|------|-------|--------|
| Router | `backend/app/routers/search.py` | 11–17 | Implemented |
| Service | `backend/app/services/search.py` | 1–200 | Implemented |
| SQL | `services/base.py` `build_list_query()` | 19–43 | Parameterized, safe |
| Permissions | `routers/search.py` | 15 | **No RBAC** — any authenticated user can search all entities |

### Supported Entities (9 total)

| Entity | Table | Search Fields | Evidence |
|--------|-------|---------------|----------|
| customer | `customers` | name, name_en, email, phone | `search.py` 130–134 |
| supplier | `suppliers` | name, name_en, email, phone | `search.py` 135–139 |
| shipment | `shipments` | tracking_number, origin, destination, reference, awb_number | `search.py` 140–144 |
| invoice | `invoices` | invoice_number, internal_id, eta_uuid, eta_submission_id, status, notes | `search.py` 145–149 |
| declaration | `customs_declarations` | declaration_number, origin_country, destination_country, status | `search.py` 150–154 |
| document | `documents` | title, file_name, file_type, entity_type | `search.py` 155–159 |
| resource | `resources` | title, title_ar, description, description_ar | `search.py` 160–164 |
| hs_code | `hs_codes` | code, description, description_ar | `search.py` 165–169 |
| eta_connector | `eta_connectors` | name, client_id, environment, status | `search.py` 170–174 |

### Not Searchable

`export_workflows`, `notification_templates`, `notification_logs`, `audit_logs`, `contacts`, `addresses`, `shipping_providers`, `shipping_parcel_templates`, `shipping_labels`, `shipping_logs`, `eta_logs`, `eta_log_documents`, `export_workflow_items`, `users`, `roles`.

### Status

**PARTIALLY READY** — Search is implemented with parameterized SQL for 9 entity types. However, it lacks role-based permission restrictions (any authenticated user can search all entities), excludes 14+ tables, and has no integration with Dashboard or Audit.

---

## 5. Audit Logging

### Evidence

| Area | Audited? | Evidence |
|------|----------|----------|
| Customer CRUD | Yes | `services/customer.py` lines 66, 86, 103 |
| Supplier CRUD | Yes | `services/supplier.py` lines 69, 90, 107 |
| Invoice CRUD + validate + cancel | Yes | `services/invoice.py` lines 75, 98, 120, 144 |
| Customs CRUD + submit | Yes | `services/customs.py` lines 129, 150, 168 |
| Shipping CRUD + provider/template CRUD | Yes | `services/shipping/__init__.py` lines 270, 607, 880, 637, 695, 709, 731, 782, 796 |
| ETA connector CRUD + submit/cancel/receipt/batch | Yes | `services/eta/__init__.py` lines 159, 190, 205, 445, 518, 606, 740, 759, 776 |
| Workflow CRUD + transition + add_item | Yes | `services/workflow.py` lines 142, 184, 233, 383 |
| Documents CRUD | Yes | `services/document.py` lines 86, 120, 141, 153 |
| Resources CRUD | Yes | `services/resource.py` lines 119, 139, 160 |
| Workflow transitions | Yes | `services/workflow.py` lines 233–241 |
| ETA operations | Mostly | submit/cancel/receipt/batch/logs audited; `get_eta_invoice_status` and `download_eta_pdf` NOT audited |
| Shipping operations | Mostly | create/cancel/update/provider/template audited; `track_shipment` and `get_label` NOT audited (only `shipping_logs`) |
| Authentication | **No** | `routers/auth.py` — register, login, refresh, me, profile update have no `log_audit` calls. No logout endpoint exists. |
| Notifications | **No** | `services/notification.py` — `send_template_email` does not call `log_audit`. Notification sends are invisible to audit. |
| Search queries | **No** | `services/search.py` — search queries are not logged. |

### Status

**PARTIALLY READY** — Audit logging covers CRUD for 10 of 11 entities and workflow transitions. Uncovered operations: authentication events, notification sends, search queries, ETA status polling/PDF download, and shipping track/label retrieval.

---

## 6. Workflow

### Evidence

| Component | File | Lines | Status |
|-----------|------|-------|--------|
| State machine | `services/workflow.py` | 15–27 | Implemented |
| States | draft, customs_ready, shipped, delivered | 16–21 | Implemented |
| Transition validation | `_validate_transition()` | 15–27 | Implemented |
| Validation called in `transition_workflow` | `services/workflow.py` | 207 | Implemented |
| Validation **bypassed** in `update_workflow` | `services/workflow.py` | 155–194 | **Gap** — `PUT` endpoint allows arbitrary state updates |
| Summary generation | `generate_workflow_summary()` | 275–363 | Implemented |
| Item handling | `add_workflow_item()` | 366–393 | Implemented |
| Database tables | `core/database.py` | 699–726 | Implemented |
| Router endpoints | `routers/workflow.py` | 28–111 | Implemented |

### Workflow State Machine

```
draft → customs_ready → shipped → delivered
draft → shipped (bypass approved via CR-M4-001 Rev.1)
```

### Gap

`update_workflow()` (`services/workflow.py` lines 155–194) allows direct state updates via `data.state` without calling `_validate_transition()`. This means a client with `PUT /api/v1/export-workflows/{id}` permission can bypass the state machine and set any state arbitrarily. The dedicated `transition_workflow()` correctly validates, but `update_workflow` does not.

### Status

**PARTIALLY READY** — State machine, transition validation, summary generation, and item handling are implemented. However, `update_workflow()` bypasses state validation, violating the approved CR and PLAN.md Section 9.12 ("Validate every request").

---

## 7. Security Baseline

### Evidence

| Control | File | Lines | Status |
|---------|------|-------|--------|
| JWT (python-jose) | `core/security.py` | 34–86 | Implemented |
| Access token (24h) | `security.py` | 34–52 | Implemented |
| Refresh token (7d) | `security.py` | 55–69 | Implemented |
| Token validation | `security.py` | 72–86 | Implemented |
| RBAC | `routers/auth.py` | 54–59 | Implemented |
| Pydantic validation | All `schemas/*.py` | — | Implemented |
| Parameterized SQL | All service files | — | Implemented |
| SQL injection risk | `services/base.py`, `dashboard.py`, `workflow.py`, `database.py` | — | Low (table/field names are code-controlled) |
| Secrets from env | `core/config.py` | 9–77 | Implemented |
| SECRET_KEY validation | `config.py` | 62–68 | Implemented (rejects weak keys) |
| **Hardcoded SECRET_KEY in root `.env`** | `.env` | 1 | **CRITICAL** — real secret on disk |
| **Placeholder SECRET_KEY in backend `.env`** | `backend/.env` | 1 | **CRITICAL** — `change-me-in-production` crashes app |
| CORS | `main.py` | 100–106 | Implemented |
| Wildcard CORS blocked | `config.py` | 69–73 | Implemented |
| Rate limiting | `routers/auth.py` | 7–8, 17, 20–26 | Partial (auth endpoints only) |
| CSRF middleware | `core/csrf.py` | 6–36 | Implemented |
| Security headers | `main.py` | 21–40 | Implemented |
| Password hashing (bcrypt) | `core/security.py` | 17, 22–29 | Implemented |
| Refresh token role gap | `routers/auth.py` | 129 | **Gap** — role claim omitted from refresh-issued access tokens |

### Status

**PARTIALLY READY** — Core security controls (JWT, RBAC, Pydantic, parameterized SQL, CORS, CSRF, bcrypt) are implemented. Critical gaps: hardcoded SECRET_KEY in root `.env`, placeholder key in backend `.env` that crashes startup, rate limiting only on auth endpoints, and refresh tokens not preserving role claims.

---

## 8. Production Readiness

### Evidence

| Area | File | Status | Classification |
|------|------|--------|----------------|
| Docker runtime | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml` | Verified | **Verified** |
| Configuration | `.env.example`, `config.py` | Verified | **Verified** |
| Environment variables | 31 variables documented | Verified | **Verified** |
| Startup | `main.py` lifespan + uvicorn | Verified | **Verified** |
| Migrations | `backend/alembic/` | Initial migration is empty (`pass`) | **Not Verified** |
| Scheduler | `core/eta_scheduler.py`, `core/shipping_scheduler.py` | 3 APScheduler jobs configured | **Verified** |
| Health checks | `main.py` `/health` + `docker-compose.yml` healthcheck | Verified | **Verified** |

### Additional Findings

- **OWNER_PASSWORD** — Required at startup (`database.py` line 746) but missing from `.env.example`.
- **SMTP vars** — Defined in `config.py` but missing from `.env.example`.
- **No CI/CD** — No GitHub Actions, GitLab CI, or Jenkinsfile found.
- **Empty Alembic initial migration** — Schema managed by raw SQL in `init_db()`, not by Alembic.

### Status

**PARTIALLY READY** — Docker, configuration, startup, scheduler, and health checks are verified. Migrations are not verified (empty initial migration). Missing `.env.example` entries for `OWNER_PASSWORD` and SMTP variables.

---

## 9. Test Coverage Baseline

### Evidence

| Category | Count | Files |
|----------|-------|-------|
| **Unit tests (service layer)** | 14 files / ~258 test functions | `backend/tests/test_services/*.py` |
| **Router/API tests** | 20 files / ~157 test functions | `backend/tests/test_*.py` |
| **Integration tests** | 1 file / 11 test functions | `backend/tests/test_integration_auth.py` |
| **End-to-end tests** | 0 files | None found |
| **Regression suite** | 0 files | None found |
| **Frontend tests** | 2 files | `frontend/src/components/NotificationBell.test.tsx`, `frontend/src/pages/Notifications.test.tsx` |
| **Total test functions** | 414 | 34 backend + 2 frontend files |

### Note

The total of 414 test functions matches the claimed 406 passing + 8 skipped = 414. However, runtime verification of test execution is blocked by a `pydantic_core.ValidationError: Extra inputs are not permitted` for `VITE_API_URL` in `config.py`, preventing independent confirmation of pass/fail breakdown.

### Status

**PARTIALLY READY** — 414 test functions exist across unit, router, and integration tests. No end-to-end or regression suites exist.

---

## 10. Documentation Baseline

### Evidence of Inconsistencies

| # | Severity | Discrepancy | Documents Affected |
|---|----------|-------------|-------------------|
| 1 | 🔴 HIGH | Phase numbering inconsistent: PLAN.md §12.3 says "Phase 1", WP-21 Roadmap says "Phase 1.5", CURRENT_STATUS.md and TECH_DEBT.md say "Phase 2.0" | PLAN.md, WP-21 Roadmap, CURRENT_STATUS.md, TECH_DEBT.md |
| 2 | 🔴 HIGH | PLAN.md §15.2 marks WP-21 as "🔴 غير مبدوط" (not started); CURRENT_STATUS.md and WP-21 Roadmap document M1–M4 as complete | PLAN.md, CURRENT_STATUS.md, WP-21 Roadmap |
| 3 | 🔴 HIGH | PLAN.md §12.3 Continuity List frozen at WP-18 (2026-07-12); does not reflect WP-19/20/21 | PLAN.md |
| 4 | 🔴 HIGH | CURRENT_STATUS.md claims current commit is `1bebd10` (M3); actual HEAD is `c6d8fec` (M4) | CURRENT_STATUS.md |
| 5 | 🔴 HIGH | CR-M4-001 Rev.1 referenced in 11 locations across 3 documents; standalone document does not exist in repository | CURRENT_STATUS.md, TECH_DEBT.md, WP-21 Roadmap |
| 6 | 🔴 HIGH | WORK_PACKAGE_PLAN.md ends at WP-19; omits WP-20 and WP-21 entirely | WORK_PACKAGE_PLAN.md |
| 7 | 🔴 HIGH | ENGINEERING_MEMORY.md ends at WP-19; does not document WP-20 or WP-21 | ENGINEERING_MEMORY.md |
| 8 | 🔴 HIGH | PROJECT_BASELINE.md describes WP-19 baseline; current state is WP-21 M4 | PROJECT_BASELINE.md |
| 9 | 🟡 MEDIUM | WP-21 Roadmap M2 claims "10 new tests"; actual test functions in M2 files = 32 | WP-21 Roadmap |
| 10 | 🟡 MEDIUM | WP-20 test count inconsistent: PLAN.md says "40+", CURRENT_STATUS.md says "34+", actual = 43 | PLAN.md, CURRENT_STATUS.md |
| 11 | 🟡 MEDIUM | TECH_DEBT.md last updated 2026-07-12; M4 closed 2026-07-14 | TECH_DEBT.md |
| 12 | 🟡 MEDIUM | M4 plan acceptance criteria references regression count "373 passed" (pre-M4); post-M4 count is 406 | `.kilo/plans/1784024628892-wp21-m4-export-operations.md` |
| 13 | 🟡 MEDIUM | Baseline documents (ENGINEERING_MEMORY.md, PROJECT_BASELINE.md, WORK_PACKAGE_PLAN.md, PLAN.md §8.2) reference 176–267 tests; actual count is 414 | Multiple |

### Status

**NOT READY** — Multiple high-severity inconsistencies exist between PLAN.md (Single Source of Truth), CURRENT_STATUS.md, TECH_DEBT.md, WORK_PACKAGE_PLAN.md, ENGINEERING_MEMORY.md, PROJECT_BASELINE.md, and the WP-21 Roadmap. The most critical issue is that PLAN.md itself claims WP-21 is "not started" while 4 milestones of WP-21 are documented as complete in other files. CR-M4-001 Rev.1 is referenced but its source document is missing.

---

## Final Summary

| Area | Status | Evidence |
|------|--------|----------|
| **Entity Integration** | PARTIALLY READY | All 11 entities implemented; missing FK constraints, reverse lookups, Workflow in Search/Dashboard, Notification audit trail |
| **Dashboard** | NOT READY | Data loads on page mount only; no live update mechanism (WebSocket/polling/scheduler) |
| **Notifications** | IMPLEMENTED BUT NOT OPERATIONAL | Service and triggers implemented; SMTP not configured (`SMTP_HOST=""`); notification sends not audited |
| **Search** | PARTIALLY READY | 9 entities searchable with parameterized SQL; no RBAC; 14+ tables excluded |
| **Audit Logging** | PARTIALLY READY | 10/11 entities audited; auth, notifications, search, ETA status/PDF, shipping track/label not audited |
| **Workflow** | PARTIALLY READY | State machine and validation implemented; `update_workflow()` bypasses state validation |
| **Security Baseline** | PARTIALLY READY | JWT, RBAC, Pydantic, CSRF, CORS implemented; hardcoded SECRET_KEY on disk, rate limiting partial, refresh token role gap |
| **Production Readiness** | PARTIALLY READY | Docker, startup, scheduler, health checks verified; migrations not verified; missing `.env.example` entries |
| **Test Coverage** | PARTIALLY READY | 414 test functions (unit + router + integration); no E2E or regression suites |
| **Documentation Baseline** | NOT READY | Phase numbering inconsistent; PLAN.md outdated; CR-M4-001 Rev.1 missing; multiple stale documents |

---

## Overall Baseline Status

**READY WITH LIMITATIONS**

### Rationale

The codebase is functionally implemented for all WP-21 acceptance criteria at the code level. All 11 entities exist with routers, services, schemas, and database tables. Search, Dashboard, Audit, and Notifications are implemented. Workflow has a state machine with validation. Security controls (JWT, RBAC, CORS, CSRF, bcrypt) are in place. Docker artifacts, startup flow, scheduler, and health checks are verified. 414 test functions exist.

However, the following evidence-based limitations prevent a "READY FOR M5 IMPLEMENTATION" verdict:

1. **Dashboard is not live** — PLAN.md acceptance criterion requires live dashboard data; current implementation only refreshes on page load.
2. **Notifications are not operational** — SMTP is not configured in the runtime environment; notification sends will fail.
3. **Workflow state validation is bypassable** — `update_workflow()` does not enforce the state machine.
4. **Critical security gaps** — Hardcoded SECRET_KEY in root `.env`; rate limiting only on auth endpoints.
5. **Documentation is inconsistent** — PLAN.md claims WP-21 is "not started" while it is complete; CR-M4-001 Rev.1 source document is missing.
6. **Migrations are not verified** — Initial Alembic migration is empty; schema evolution is managed by raw SQL.

These limitations must be resolved before Milestone 5 implementation can proceed with confidence.

---

*No implementation was performed during this verification.*
