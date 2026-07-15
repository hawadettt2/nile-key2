# PROJECT_BASELINE_AFTER_WP21.md

**Document Status:** Official Project Baseline  
**Purpose:** Defines the official project state after WP-21 Milestone 5 closure.  
**Authoritative Sources:** PLAN.md, CURRENT_STATUS.md, TECH_DEBT.md, git history  
**Date:** 2026-07-15  
**Baseline Commit:** 4bd7df8  
**Branch:** main  
**Working Tree:** Has untracked governance documents  

---

## 1. Executive Summary

WP-21 Milestone 5 has been officially closed. All 5 remediation packages (M5-R1 through M5-R5) have been implemented, tested, and committed. All WP-21 acceptance criteria from PLAN.md are satisfied. The repository is clean, all tests pass, and documentation is synchronized.

---

## 2. Current Repository State

| Property | Value |
|----------|-------|
| Branch | main |
| Latest Commit | 4bd7df8 |
| Working Tree | Has untracked governance documents |
| Untracked Files | Present (Stage A/B/C governance documents) |
| Remote Status | Not verified |

---

## 3. Completed Work Packages

All work packages from WP-01 through WP-21 are complete.

---

## 4. Completed Milestones

| Milestone | Status | Completion |
|-----------|--------|------------|
| WP-21 M1 | ✅ Complete | 100% |
| WP-21 M2 | ✅ Complete | 100% |
| WP-21 M3 | ✅ Complete | 100% |
| WP-21 M4 | ✅ Complete (with conditions) | 100% |
| WP-21 M5 | ✅ Complete | 100% |

---

## 5. Current Test Status

| Metric | Value |
|--------|-------|
| Backend Tests | 410 passed, 8 skipped, 0 failed |
| Frontend Tests | 17 passed, 0 failed |
| Total Test Functions | 414 |
| Last Test Run | 2026-07-15 |

---

## 6. Current Architecture Status

| Component | Status |
|-----------|--------|
| Frontend | React + TypeScript + Vite + Tailwind CSS |
| Backend | FastAPI (Python 3.11) |
| Database | SQLite (`nile_key.db`) |
| Migrations | Alembic initialized |
| Scheduler | APScheduler |
| Authentication | JWT + bcrypt |
| Authorization | RBAC |
| Docker | Dockerfiles + docker-compose.yml present |

---

## 7. Current API Status

| Router | Prefix | Endpoints | Auth |
|--------|--------|-----------|------|
| Auth | /api/v1/auth | 5 | JWT |
| Customers | /api/v1/customers | 6 | RBAC |
| Suppliers | /api/v1/suppliers | 5 | RBAC |
| Invoices | /api/v1/invoices | 7 | RBAC |
| Customs | /api/v1/customs | 8 | RBAC |
| Resources | /api/v1/resources | 6 | RBAC |
| Documents | /api/v1/documents | 6 | RBAC |
| ETA | /api/v1/eta | 11 | RBAC |
| Shipping | /api/v1/shipping | 18 | RBAC |
| Search | /api/v1/search | 1 | RBAC |
| Dashboard | /api/v1/dashboard | 1 | RBAC |
| Notifications | /api/v1/notifications | 1 | RBAC |
| Audit | /api/v1/audit | 1 | RBAC |
| Export Workflows | /api/v1/export-workflows | 7 | RBAC |

---

## 8. Current Database Status

| Category | Tables |
|----------|--------|
| Core | users, roles |
| Domain | customers, suppliers, invoices, customs_declarations, hs_codes, documents, resources |
| ETA | eta_connectors, eta_logs, eta_log_documents |
| Shipping | shipments, shipping_providers, shipping_parcel_templates, shipping_labels, shipping_logs, contacts, addresses |
| Workflow | export_workflows, export_workflow_items |
| Notification | notification_templates, notification_logs, notification_preferences |
| Audit | audit_logs |

Total: 20+ tables.

---

## 9. Current Documentation Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| PLAN.md | ✅ Current | 2026-07-15 |
| CURRENT_STATUS.md | ✅ Current | 2026-07-15 |
| TECH_DEBT.md | ✅ Current | 2026-07-15 |
| wp21-platform-integration-roadmap.md | ✅ Current | 2026-07-15 |
| wp21-platform-integration-plan.md | ✅ Current | 2026-07-15 |
| Stage A/B/C governance docs | ✅ Committed | 2026-07-15 |

---

## 10. Governance Status

| Item | Status |
|------|--------|
| Stage A | ✅ Complete |
| Stage B | ✅ Approved |
| Stage C | ✅ Complete |
| Final Closure Audit | ✅ Passed |
| Repository Consistency Audit | ✅ Passed |
| Open Change Requests | CR-M4-001 Rev.1 (closed with conditions) |

---

## 11. Technical Debt Summary

Active debt: Raw SQL, Docker runtime unverified, no rate limiting, PostgreSQL migration path, __pycache__, CORS origins, shipping alias complexity, workflow formalization.

Resolved in WP-21: Notification audit logging, dashboard live data, workflow state validation, search RBAC, .env.example variables.

---

## 12. Known Deferred Items

SMTP deployment, SECRET_KEY rotation, backend .env cleanup, rate limiting expansion, refresh token role claim, empty Alembic migration, workflow/search/dashboard/notification coverage expansion, ETA-workflow integration, reverse lookups, contacts/addresses endpoints, auth/search/ETA/shipping audit logging, E2E tests, regression suite, documentation sync.

---

## 13. Open Change Requests

| CR ID | Status |
|-------|--------|
| CR-M4-001 Rev.1 | Closed with conditions |

No open Change Requests.

---

## 14. Next Recommended Work Package

Phase 3 — Advanced Features (WP-30 through WP-42 per PLAN.md).

---

## 15. Risks

CR-M4-001 conditions, technical debt accumulation, no E2E coverage, Docker runtime unverified, frontend lint warnings.

---

## 16. Assumptions

1. All WP-01 through WP-21 complete.
2. Repository on main branch, with untracked governance documents.
3. All tests pass.
4. Database schema stable.
5. No breaking changes without new Change Request.
6. Future work follows Stage A → B → C governance.
7. PLAN.md is Single Source of Truth.

---

## 17. Baseline Commit References

| Commit | Description |
|--------|-------------|
| 4bd7df8 | Add governance documents |
| b75bcb8 | Fix planning docs references |
| e143840 | Update docs for M5 closure |
| b8b2ecb | M5-R1 Dashboard live refresh |
| 5957d2b | M5-R4 Search RBAC |
| 9314fae | M5-R2 Notification audit |
| bee9f5b | M5-R3 Workflow validation |
| 7efca3b | M5-R5 Config docs |
| c6d8fec | M4 closure |
| f6aa5a4 | M3 add backend notification trigger tests |
| 5dcf72c | Update milestone 2 and 3 completion status |
| 1bebd10 | Add vitest + RTL tests for Notifications and NotificationBell |
| d53f1e0 | Update dashboard with live widgets |
| adedc8e | M2-T7 add search and dashboard tests |
| 941efde | M1 complete notification/audit services, schemas, routers, tests |

---

## 18. Repository Readiness Statement

Repository is ready for the next Work Package. All WP-21 acceptance criteria met. All tests pass. Documentation synchronized. Working tree has untracked governance documents. No blocking issues.

**Baseline:** 4bd7df8  
**Date:** 2026-07-15  
**Status:** WP-21 CLOSED — READY FOR NEXT WORK PACKAGE

---

**END OF BASELINE DOCUMENT**
