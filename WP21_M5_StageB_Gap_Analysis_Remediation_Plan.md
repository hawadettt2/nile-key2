# WP-21 Milestone 5
## Stage B — Gap Analysis & Remediation Plan

**Document Status:** DRAFT FOR APPROVAL  
**Based On:** WP-21 Milestone 5 Stage A Baseline Verification Report (`WP21_M5_StageA_Baseline_Verification_Report.md`)  
**Authoritative Sources:** PLAN.md, CURRENT_STATUS.md, TECH_DEBT.md, Stage A Report  
**Date:** 2026-07-14  
**Baseline Commit:** c6d8fec7d97bf0b6a7187fbeca351e2d6aa9be78

---

## 1. Executive Summary

### Purpose

This document translates the evidence-based findings from Stage A Baseline Verification into an approved remediation plan for WP-21 Milestone 5. It defines which gaps are approved for remediation, the remediation packages, acceptance criteria, suggested implementation sequencing, and verification methods.

### Scope

- **In Scope:** Gaps that block WP-21 acceptance criteria satisfaction or represent critical correctness/security issues requiring software or repository-artifact changes
- **Out of Scope:** New features, architectural redesign, database redesign, scope expansion
- **Deferred:** Items that are valid improvements or operational concerns but are not required for M5 acceptance criteria or are outside software remediation scope

### Evidence Sources

1. `WP21_M5_StageA_Baseline_Verification_Report.md` — Stage A findings
2. `PLAN.md` — WP-21 acceptance criteria (Section 15.2) and architecture rules
3. `CURRENT_STATUS.md` — Implementation state and governance notes
4. `TECH_DEBT.md` — Active and resolved technical debt
5. Repository source code — verified file paths and line numbers

### Governance Status

This document is **required** before Stage C implementation may begin per project governance rules. Stage A findings are observations only and do not constitute approved implementation scope. This document defines WHAT must be remediated; Stage C determines HOW.

---

## 2. Gap Inventory

| Gap ID | Description | Evidence | Category | Severity | Impact | Risk | Affected Modules |
|--------|-------------|----------|----------|----------|--------|------|------------------|
| G1 | Dashboard data loads only on page mount; no live update mechanism | `frontend/src/pages/Dashboard.tsx` line 38: `useEffect(() => { loadDashboard(); }, [])` with no polling, WebSocket, or SSE. Backend schedulers do not update dashboard data. | Software Defect | HIGH | Users must manually refresh to see updated data | Low | Frontend Dashboard, Backend Dashboard |
| G2 | Email notifications fail at runtime because SMTP is not configured in deployment environment | `backend/.env` contains no SMTP variables. `backend/app/core/config.py` lines 46-52 define SMTP settings with defaults `SMTP_HOST=""`. `backend/app/services/notification.py` line 72 raises `EmailSendError("SMTP host is not configured")` before any network call. | Configuration Issue | HIGH | All notification sends fail | Low | Notification service, ETA service, Shipping service |
| G3 | Notification sending is not logged to `audit_logs` or `notification_logs` | `backend/app/services/notification.py` lines 97-123 (`send_template_email`) contains no audit logging. `notification_logs` table exists at `backend/app/core/database.py` lines 390-401 but is unused. | Software Defect | MEDIUM | Notification sends are invisible to audit trail | Low | Notification service, Audit service |
| G4 | `update_workflow()` allows arbitrary state updates without validating transitions | `backend/app/services/workflow.py` lines 155-194 (`update_workflow`) accepts `data.state` and writes it directly. `transition_workflow()` at line 207 correctly validates, but `update_workflow` does not. | Software Defect | HIGH | Any client with PUT permission can set workflow to any state | Low | Workflow service, Workflow router |
| G5 | Root `.env` file contains a real SECRET_KEY value on disk | `F:\nilekey\nile-key-project\nile-key2\.env` line 1 contains `SECRET_KEY=ZkpJqi3KbOQ5m26hZmW2Ypr3-yHlXLQ_4owIIpqW_-PWTtbPx0g6sr3E-Dc2Whah`. File is gitignored. | Operational Issue | CRITICAL | Secret sprawl risk if repository is shared/backed up | Medium | Security, Configuration |
| G6 | `backend/.env` contains `SECRET_KEY=change-me-in-production` which fails startup validation | `backend/.env` line 1. `backend/app/core/config.py` lines 63-68 validates SECRET_KEY and raises `RuntimeError` if value is `"change-me-in-production"` or length < 32. | Operational Issue | CRITICAL | Backend crashes on startup when `backend/.env` is present with placeholder value | Medium | Security, Configuration, Startup |
| G7 | Rate limiting implemented only on auth endpoints | `backend/app/routers/auth.py` lines 7-8, 17, 20-26 apply rate limiting to 3 endpoints. No other routers have rate limiting. TECH_DEBT.md line 15 lists "No rate limiting | Missing entirely" as MEDIUM priority debt. | Software Defect | MEDIUM | Other endpoints vulnerable to brute-force/abuse | Low | All routers except auth |
| G8 | Refresh-issued access tokens omit the `role` claim | `backend/app/routers/auth.py` line 129: `create_access_token({"sub": user_id})` — role is omitted. Login-issued tokens at line 98 include role. | Software Defect | LOW | Role lost after token refresh if downstream depends on JWT claim | Low | Auth router, Security |
| G9 | Search endpoint has no role-based permission check | `backend/app/routers/search.py` line 15: `current_user: dict = Depends(get_current_user)` — no `require_role` check. | Software Defect | MEDIUM | Any authenticated user can search all entities including sensitive ones | Low | Search router |
| G10 | `.env.example` does not list `OWNER_PASSWORD` or SMTP variables | `backend/.env.example` contains 16 variables. `OWNER_PASSWORD` is required at startup (`backend/app/core/database.py` line 746) but not documented. SMTP variables defined in `config.py` but not in `.env.example`. | Documentation Issue | MEDIUM | New deployments may miss required environment variables | Low | Configuration, Documentation |
| G11 | Initial Alembic migration is empty (`pass` in upgrade/downgrade) | `backend/alembic/versions/9f6e6d58ca0f_initial.py` — upgrade/downgrade are both `pass`. Schema managed by raw SQL in `init_db()`. | Software Defect | LOW | Alembic cannot track schema history | Low | Migrations |
| G12 | `export_workflows` table is not searchable | `backend/app/services/search.py` lines 129-175 (`_ENTITY_SEARCH` dict) does not include `workflow` or `export_workflows`. | Software Defect | LOW | Users cannot search for workflows via global search | Low | Search service |
| G13 | Dashboard does not include workflow count or status breakdown | `backend/app/services/dashboard.py` lines 71-93 counts 8 entity types. No workflow count. | Software Defect | LOW | Dashboard lacks visibility into export workflow status | Low | Dashboard service |
| G14 | `notification_templates` and `notification_logs` are not searchable | `backend/app/services/search.py` lines 129-175 does not include notification entities. | Software Defect | LOW | Users cannot search notifications via global search | Low | Search service |
| G15 | Workflow transitions do not trigger ETA submission | `backend/app/services/workflow.py` `transition_workflow()` lines 197-243 calls `submit_declaration` and `update_shipment` but does not call ETA submission functions. | Software Defect | LOW | Users must manually submit invoices to ETA after workflow transition | Medium | Workflow service, ETA service |
| G16 | Workflow transitions do not send notifications | `backend/app/services/workflow.py` `transition_workflow()` lines 197-243 has no notification trigger calls. | Software Defect | LOW | Users are not notified of workflow state changes | Low | Workflow service, Notification service |
| G17 | No entity router provides endpoints to list related child entities | No endpoints like `GET /customers/{id}/invoices` or `GET /suppliers/{id}/shipments` exist. | Software Defect | LOW | Users must use search or separate queries to find related entities | Low | All entity routers |
| G18 | `contacts` and `addresses` tables exist but have no router/service endpoints | `backend/app/core/database.py` lines 343-373 define tables. No router or service files exist for these tables. | Software Defect | LOW | Data cannot be managed via API | Low | None |
| G19 | Login, register, refresh, and profile updates are not logged to audit | `backend/app/routers/auth.py` lines 62-179 — no `log_audit` calls in any auth endpoint. | Software Defect | LOW | Authentication events are not traceable in audit log | Low | Auth router, Audit service |
| G20 | Search queries are not logged to audit | `backend/app/services/search.py` lines 178-200 (`search_all`) contains no `log_audit` call. | Software Defect | LOW | Search activity is not traceable | Low | Search service, Audit service |
| G21 | `get_eta_invoice_status` and `download_eta_pdf` do not create audit logs | `backend/app/services/eta/__init__.py` lines 529-569 and lines 630-649 contain no `log_audit` calls. | Software Defect | LOW | ETA status checks and PDF downloads are not audited | Low | ETA service, Audit service |
| G22 | `track_shipment` and `get_label` do not create audit logs | `backend/app/services/shipping/__init__.py` lines 484-513 and lines 438-477 log to `shipping_logs` but not to `audit_logs`. | Software Defect | LOW | Tracking and label retrieval are not in central audit log | Low | Shipping service, Audit service |
| G23 | No Playwright, Cypress, or Selenium tests exist | Glob search for `**/*e2e*`, `**/*playwright*`, `**/*cypress*` returned no results. Only 2 frontend Vitest component tests exist. | Testing Gap | LOW | No browser automation coverage | N/A | Frontend |
| G24 | No dedicated regression test suite exists | No files matching `*regression*` pattern found. Existing 414 test functions serve as regression coverage implicitly. | Testing Gap | LOW | No formal regression test execution | N/A | Testing |
| G25 | Multiple documents contain inconsistent phase numbers, WP status, test counts, and commit references | See Stage A Report Section 10 (18 specific inconsistencies documented). | Documentation Issue | MEDIUM | Confusion about project state; PLAN.md claims WP-21 is "not started" while it is complete | Low | Documentation |

---

## 3. Scope Classification

| Gap ID | Classification | Rationale |
|--------|---------------|-----------|
| G1 | **Approved for M5** | Explicit acceptance criterion: "لوحة القيادة تعرض بيانات حية" (Dashboard displays live data). Current implementation loads once on mount only. |
| G2 | **Deferred — Deployment/Configuration** | Notification software is implemented and correct. The gap is that SMTP is not configured in the deployment environment. This is an operational/deployment task, not a software defect. The PLAN.md acceptance criterion "الإشعارات تعمل عبر البريد الإلكتروني" will be satisfied through deployment environment configuration and operational runbook completion. `.env.example` documentation (G10) addresses the configuration reference. |
| G3 | **Approved for M5** | Part of acceptance criterion "سجل التدقيق يعمل لجميع العمليات" (Audit log works for all operations). Notification sends are currently invisible to audit. |
| G4 | **Approved for M5** | Correctness/security fix. Workflow state transitions must be validated. Violates PLAN.md Section 9.12 "Validate every request." Approved CR-M4-001 Rev.1 bypass must be preserved. |
| G5 | **Deferred — Operational** | Developer-local `.env` file is gitignored and not a repository artifact. The software correctly validates SECRET_KEY and rejects weak values. The CRITICAL severity rating refers to operational risk (secret sprawl) rather than a software blocking issue for M5. Remediation is operational secret management (key rotation, file cleanup), not a software change. |
| G6 | **Deferred — Operational** | Developer-local `.env` file with placeholder value. The software correctly detects and rejects this value at startup. The CRITICAL severity rating refers to operational risk (startup failure) rather than a software blocking issue for M5. Remediation is developer-local configuration cleanup, not a software change. |
| G7 | **Deferred** | Rate limiting exists on auth endpoints. Expanding to all routers is valid technical debt (TECH_DEBT.md) but not explicitly in M5 acceptance criteria. |
| G8 | **Deferred** | Current RBAC does not depend on JWT role claim (uses DB query via `get_current_user()`). Not blocking for M5 acceptance criteria. |
| G9 | **Approved for M5** | Security review item (M5-T4 scope). Search must enforce role-based access control consistent with existing repository RBAC patterns. |
| G10 | **Approved for M5** | Configuration documentation completeness. `.env.example` is a repository artifact and must document all required environment variables. |
| G11 | **Deferred** | Schema works correctly via `init_db()`. Empty Alembic migration is technical debt but not blocking for M5. |
| G12 | **Deferred** | Adding Workflow to search is scope expansion. Current search "works across entities" with 9 types. |
| G13 | **Deferred** | Adding Workflow to Dashboard is scope expansion. Dashboard provides core operational stats. |
| G14 | **Deferred** | Adding Notifications to search is scope expansion. |
| G15 | **Deferred** | Automatic ETA submission from Workflow is a new business process integration requiring Engineering Decision. |
| G16 | **Deferred** | Workflow notification triggers are a new feature. Notifications already work for ETA and Shipping. |
| G17 | **Deferred** | Reverse lookup endpoints are new functionality not in acceptance criteria. |
| G18 | **Deferred** | Adding endpoints for `contacts` and `addresses` is new functionality. Tables exist but were not part of WP-21 scope. |
| G19 | **Deferred** | Auth event audit logging is a valid improvement but not explicitly in M5 acceptance criteria. |
| G20 | **Deferred** | Search query audit is a valid improvement but not explicitly in M5 acceptance criteria. |
| G21 | **Deferred** | ETA status/PDF audit is a valid improvement but not explicitly in M5 acceptance criteria. |
| G22 | **Deferred** | Shipping track/label audit is a valid improvement but not explicitly in M5 acceptance criteria. |
| G23 | **Out of Scope** | M5-T2 specifies "integration tests" not "end-to-end tests". E2E testing infrastructure is a Phase 3 activity. |
| G24 | **Out of Scope** | Existing 414 test functions serve as regression coverage. Dedicated regression suite is not in M5 scope. |
| G25 | **Deferred** | Documentation synchronization is important but should follow implementation (M5-T5). Historical inconsistencies do not block M5 acceptance criteria. |

---

## 4. Remediation Packages

### Package M5-R1: Dashboard Live Data

**Objective:** Dashboard must display live data from ETA and Shipping without requiring manual page reload, satisfying the PLAN.md acceptance criterion.

**Included Work:**
- Implement a mechanism for Dashboard data to refresh automatically
- Preserve existing on-mount data load
- No changes to Dashboard API contracts or database schema

**Explicit Exclusions:**
- Specific refresh mechanism (polling, WebSocket, SSE, or alternative) is not prescribed; implementation technique is determined during Stage C
- No backend data pre-computation or caching
- No new dashboard entities or metrics
- No changes to existing Dashboard API responses

**Dependencies:** None

---

### Package M5-R2: Notification Audit Logging

**Objective:** Notification sends must be auditable, satisfying the audit coverage requirement.

**Included Work:**
- Notification send events must be recorded in the audit system
- Notification send events must be recorded in `notification_logs`
- Existing notification triggers and send logic must remain unchanged

**Explicit Exclusions:**
- Changing notification trigger logic
- Adding new notification types
- Modifying `notification_templates` table schema
- Changing frontend notification display
- Specific audit field names or log table structures are not prescribed; implementation follows existing audit patterns

**Dependencies:** None

---

### Package M5-R3: Workflow State Validation

**Objective:** All workflow state transitions must be validated according to the approved state machine, satisfying the correctness requirement.

**Included Work:**
- Enforce state transition validation for all workflow state updates
- Preserve the approved state machine rules
- Preserve the approved CR-M4-001 Rev.1 bypass (`draft` → `shipped`)
- Block invalid state transitions

**Explicit Exclusions:**
- Removing or modifying the approved `draft` → `shipped` bypass
- Changing valid transition rules
- Modifying workflow summary generation
- Changing item handling logic
- Specific implementation function names or call sequences are not prescribed

**Dependencies:** None

---

### Package M5-R4: Search Role-Based Access Control

**Objective:** Search must enforce role-based access control consistent with the repository's existing RBAC policy.

**Included Work:**
- Add role-based permission check to search endpoint
- Follow existing RBAC patterns implemented in other routers
- Preserve existing authentication requirement
- No changes to search logic, SQL, query structure, or results

**Explicit Exclusions:**
- Changing searchable entities
- Modifying search SQL or ranking logic
- Adding search filters or pagination changes
- Changing search API contract
- Specific role lists are not prescribed; role selection follows existing repository authorization policy

**Dependencies:** None

---

### Package M5-R5: Configuration Documentation

**Objective:** Ensure `.env.example` documents all required environment variables as a repository artifact.

**Included Work:**
- Update `backend/.env.example` to include all required environment variables currently missing from the file
- Variables to document: `OWNER_PASSWORD`, `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS`
- This is a repository documentation change only

**Explicit Exclusions:**
- Modifying developer-local `.env` files (these are gitignored and not repository artifacts)
- Setting or rotating actual secret values
- Changing configuration validation logic
- Deployment environment configuration

**Dependencies:** None

---

## 5. Acceptance Criteria

### M5-R1: Dashboard Live Data

| Criterion | Verification Method |
|-----------|---------------------|
| Dashboard data refreshes automatically without manual page reload | Verify Dashboard displays updated data after source data changes without user-initiated page reload |
| Existing on-mount load behavior is preserved | Verify Dashboard loads data correctly on initial page mount |
| No API contract changes | OpenAPI specification is unchanged |
| No database schema changes | Database schema is unchanged |
| Existing tests pass | Full backend and frontend test suites pass |

### M5-R2: Notification Audit Logging

| Criterion | Verification Method |
|-----------|---------------------|
| Notification send events are recorded in audit system | Verify audit trail includes notification send events |
| Notification send events are recorded in `notification_logs` | Verify `notification_logs` table receives records for each send |
| Existing notification functionality is unchanged | All existing notification tests pass |
| No duplicate audit events | Each send creates exactly one audit record and one notification log record |
| Existing API contracts are preserved | OpenAPI specification is unchanged |

### M5-R3: Workflow State Validation

| Criterion | Verification Method |
|-----------|---------------------|
| Workflow state transitions are validated | Verify invalid state transitions are rejected |
| Approved state machine rules are enforced | Verify valid transitions succeed: `draft` → `customs_ready`, `customs_ready` → `shipped`, `shipped` → `delivered` |
| Approved CR-M4-001 Rev.1 bypass is preserved | Verify `draft` → `shipped` transition succeeds |
| Existing API contracts are preserved | All existing workflow router tests pass |
| No breaking changes to workflow summary or item handling | Workflow summary and item endpoints function identically |

### M5-R4: Search Role-Based Access Control

| Criterion | Verification Method |
|-----------|---------------------|
| Search endpoint enforces role-based access control | Verify unauthorized role requests receive appropriate error response |
| Authorized roles can search | Verify users with authorized roles receive search results |
| Authentication is still required | Verify unauthenticated requests receive 401 |
| Search results are unchanged for authorized users | Verify search results are identical for authorized roles before and after change |
| Search SQL and logic are unchanged | `services/search.py` is unchanged |
| Existing API contracts are preserved | OpenAPI specification is unchanged |

### M5-R5: Configuration Documentation

| Criterion | Verification Method |
|-----------|---------------------|
| `.env.example` documents `OWNER_PASSWORD` | Verify `OWNER_PASSWORD` is listed in `.env.example` |
| `.env.example` documents all SMTP variables | Verify `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS` are listed in `.env.example` |
| No repository artifact changes beyond `.env.example` | Verify no other repository files are modified |
| Existing tests pass | All existing tests pass |

---

## 6. Risk Assessment

### M5-R1: Dashboard Live Data

| Risk Type | Assessment | Mitigation |
|-----------|------------|------------|
| Technical | Low — Well-understood pattern | Implementation preserves existing on-mount load |
| Business | Low — Improves user experience | No data model changes |
| Regression | Very Low — Frontend change only | Existing tests unaffected; no API changes |
| Rollback | Easy — Remove auto-refresh mechanism | Revert to single on-mount load |

### M5-R2: Notification Audit Logging

| Risk Type | Assessment | Mitigation |
|-----------|------------|------------|
| Technical | Low — Additive logging only | No changes to notification send logic |
| Business | Low — Improves audit compliance | No user-facing changes |
| Regression | Very Low — Existing tests unaffected | Test that audit records are created |
| Rollback | Easy — Remove logging calls | Revert logging additions |

### M5-R3: Workflow State Validation

| Risk Type | Assessment | Mitigation |
|-----------|------------|------------|
| Technical | Medium — Changes state update behavior | Preserve all valid transitions including approved bypass |
| Business | Medium — May reject previously accepted invalid state changes | This is the intended fix; invalid transitions were bugs |
| Regression | Medium — Existing tests may rely on bypass behavior | Run full workflow test suite; update tests if they assert invalid behavior |
| Rollback | Medium — Requires reverting validation logic | Git history preserves original code |

### M5-R4: Search Role-Based Access Control

| Risk Type | Assessment | Mitigation |
|-----------|------------|------------|
| Technical | Low — Standard RBAC pattern | Follow existing RBAC patterns in repository |
| Business | Low — Restricts search to authorized roles | Aligns with existing role definitions |
| Regression | Low — Only affects unauthorized users | Authorized users see identical results |
| Rollback | Easy — Remove role restriction | Revert router change |

### M5-R5: Configuration Documentation

| Risk Type | Assessment | Mitigation |
|-----------|------------|------------|
| Technical | Very Low — Documentation change only | No code changes |
| Business | Low — Improves deployment clarity | No functional changes |
| Regression | None — No code changes | No tests affected |
| Rollback | Easy — Revert documentation change | Git history preserves original |

---

## 7. Traceability Matrix

| Stage A Gap | Approved Package | Acceptance Criteria | Verification Method |
|-------------|------------------|---------------------|---------------------|
| G1: Dashboard not live | M5-R1 | AC1-AC5 | Code review, test suite, OpenAPI diff |
| G2: Notifications not operational | Deferred — Deployment/Configuration | N/A | N/A |
| G3: Notification sends not audited | M5-R2 | AC1-AC5 | Code review, test for audit record creation |
| G4: Workflow state validation bypass | M5-R3 | AC1-AC5 | Code review, transition validation tests |
| G5: Hardcoded SECRET_KEY in root .env | Deferred — Operational | N/A | N/A |
| G6: Placeholder SECRET_KEY in backend .env | Deferred — Operational | N/A | N/A |
| G7: Rate limiting only on auth | Deferred | N/A | N/A |
| G8: Refresh token role gap | Deferred | N/A | N/A |
| G9: Search has no RBAC | M5-R4 | AC1-AC5 | Code review, integration tests |
| G10: Missing .env.example entries | M5-R5 | AC1-AC3 | File content review |
| G11: Empty Alembic migration | Deferred | N/A | N/A |
| G12: Workflow not in Search | Deferred | N/A | N/A |
| G13: Workflow not in Dashboard | Deferred | N/A | N/A |
| G14: Notifications not in Search | Deferred | N/A | N/A |
| G15: ETA not integrated with Workflow | Deferred | N/A | N/A |
| G16: Notifications not integrated with Workflow | Deferred | N/A | N/A |
| G17: Reverse lookups missing | Deferred | N/A | N/A |
| G18: Orphaned tables | Deferred | N/A | N/A |
| G19: Auth events not audited | Deferred | N/A | N/A |
| G20: Search queries not audited | Deferred | N/A | N/A |
| G21: ETA status/PDF not audited | Deferred | N/A | N/A |
| G22: Shipping track/label not audited | Deferred | N/A | N/A |
| G23: No E2E tests | Out of Scope | N/A | N/A |
| G24: No regression suite | Out of Scope | N/A | N/A |
| G25: Documentation inconsistencies | Deferred | N/A | N/A |

---

## 8. Suggested Implementation Sequencing

**The following sequencing is suggested for verification efficiency only. All packages may be implemented in any order or in parallel, as no proven technical dependencies exist between them.**

1. **M5-R5 (Configuration Documentation)** — Documentation change with no technical dependencies. Can be completed independently.
2. **M5-R3 (Workflow State Validation)** — Critical correctness fix with no dependencies.
3. **M5-R2 (Notification Audit Logging)** — Independent software change.
4. **M5-R1 (Dashboard Live Data)** — Independent software change.
5. **M5-R4 (Search RBAC)** — Independent software change.

### Sequencing Rationale

- **M5-R5 first** is suggested because it is a documentation-only change with zero regression risk, allowing immediate progress.
- **M5-R3 second** is suggested because it addresses a critical correctness issue that should be resolved early.
- **M5-R2, M5-R1, M5-R4** can be implemented in any order or in parallel as they have no technical dependencies on each other or on the preceding packages.

---

## 9. Non-approved Items

The following Stage A findings are **NOT approved for M5 implementation**:

| Gap ID | Classification | Reason for Non-approval |
|--------|---------------|------------------------|
| G2 | Deferred — Deployment/Configuration | Notification software is implemented and correct. The gap is SMTP configuration in the deployment environment. This is an operational task, not a software defect. The PLAN.md acceptance criterion "الإشعارات تعمل عبر البريد الإلكتروني" will be satisfied through deployment environment configuration. `.env.example` documentation (M5-R5) addresses the configuration reference. |
| G5 | Deferred — Operational | Developer-local `.env` file is gitignored and not a repository artifact. The software correctly validates SECRET_KEY and rejects weak values. The CRITICAL severity rating refers to operational risk (secret sprawl) rather than a software blocking issue for M5. Remediation is operational secret management (key rotation, file cleanup), not a software change. |
| G6 | Deferred — Operational | Developer-local `.env` file with placeholder value. The software correctly detects and rejects this value at startup. The CRITICAL severity rating refers to operational risk (startup failure) rather than a software blocking issue for M5. Remediation is developer-local configuration cleanup, not a software change. |
| G7 | Deferred | Rate limiting expansion is valid technical debt (TECH_DEBT.md) but not in M5 acceptance criteria. |
| G8 | Deferred | Current RBAC does not depend on JWT role claim. Not blocking for M5 acceptance criteria. |
| G12 | Deferred | Adding Workflow to search is scope expansion. Current search covers 9 business entities. |
| G13 | Deferred | Adding Workflow to Dashboard is scope expansion. Dashboard provides core operational stats. |
| G14 | Deferred | Adding Notifications to search is scope expansion. |
| G15 | Deferred | ETA-Workflow integration is a new business process integration requiring Engineering Decision. |
| G16 | Deferred | Workflow notification triggers are a new feature. Notifications already work for ETA and Shipping. |
| G17 | Deferred | Reverse lookup endpoints are new functionality not in acceptance criteria. |
| G18 | Deferred | Adding endpoints for `contacts` and `addresses` is new functionality. Tables exist but were not part of WP-21 scope. |
| G19 | Deferred | Auth event audit logging is a valid improvement but not in M5 acceptance criteria. |
| G20 | Deferred | Search query audit is a valid improvement but not in M5 acceptance criteria. |
| G21 | Deferred | ETA status/PDF audit is a valid improvement but not in M5 acceptance criteria. |
| G22 | Deferred | Shipping track/label audit is a valid improvement but not in M5 acceptance criteria. |
| G23 | Out of Scope | M5-T2 specifies "integration tests" not "end-to-end tests". E2E testing infrastructure is a Phase 3 activity. |
| G24 | Out of Scope | Existing 414 test functions serve as regression coverage. Dedicated regression suite is not in M5 scope. |
| G25 | Deferred | Documentation synchronization should follow implementation (M5-T5). Historical inconsistencies do not block M5 acceptance criteria. |

### Why These Are Not Approved

The WP-21 acceptance criteria in PLAN.md Section 15.2 are:
- [ ] جميع الكيانات متصلة ببعضها البعض
- [ ] لوحة القيادة تعرض بيانات حية من ETA والشحن
- [ ] سجل التدقيق يعمل لجميع العمليات
- [ ] الإشعارات تعمل عبر البريد الإلكتروني
- [ ] البحث يعمل عبر جميع الكيانات

The non-approved items either:
1. Expand scope beyond these criteria (G12-G18, G23-G24)
2. Are valid improvements or operational concerns but not blocking for acceptance (G2, G5-G8, G19-G22)
3. Are documentation issues that should follow implementation (G25)

Implementing non-approved items would violate the "Smallest possible change" and "No scope expansion" rules.

**Note on G2, G5, G6:** These are configuration or operational issues, not software defects. The software correctly handles these cases (SMTP code exists, SECRET_KEY validation exists). The actual remediation (SMTP deployment configuration, SECRET_KEY rotation, `.env` file cleanup) is outside the scope of a software remediation plan and must be addressed through deployment and operational procedures.

---

## 10. Final Governance Decision

**Stage C implementation MAY BEGIN only after ALL of the following conditions are met:**

1. **This document is formally approved** by the designated governance authority.
2. **Any required Engineering Decisions are approved.** Specifically:
   - The approach for Dashboard live data (M5-R1) is an Engineering Decision if it deviates from existing patterns.
   - The role selection for Search RBAC (M5-R4) follows existing repository RBAC policy; if deviation is required, it must be approved as an Engineering Decision.
3. **Any required Change Requests are approved.** If approved packages introduce changes that affect existing API contracts, database schemas, or deployment procedures, the corresponding Change Requests must be approved before implementation.
4. **Governance documentation is synchronized.** PLAN.md, CURRENT_STATUS.md, and TECH_DEBT.md must be updated to reflect the approved M5 scope before Stage C begins.
5. **The governance gate is officially cleared.** The project governance authority must formally clear the gate for Stage C implementation.

### Post-Approval Requirements

- Stage C must implement packages according to the governance requirements defined in this document
- Each package must be verified independently before proceeding to the next
- All tests must pass after each package
- No implementation details prescribed in this document may be altered without a new Engineering Decision and Change Request
- Repository must remain clean throughout implementation
- Any new issues discovered during implementation must be documented and classified before being addressed

### What This Document Does NOT Approve

- New features beyond the 5 packages defined above
- Architectural changes
- Database schema redesign
- Expansion of search, dashboard, or notification coverage beyond specified criteria
- Modification of developer-local `.env` files
- Implementation of deferred or out-of-scope items
- Any deviation from the approved packages without a new Engineering Decision and Change Request

**This document does not constitute approval for Stage C implementation. Stage C may begin only after the conditions listed above are formally satisfied and documented.**

---

## Appendix A: Approved Package Summary

| Package ID | Objective | Gaps Addressed | Category |
|------------|-----------|----------------|----------|
| M5-R1 | Dashboard must display live data without manual page reload | G1 | Software Defect |
| M5-R2 | Notification sends must be auditable | G3 | Software Defect |
| M5-R3 | Workflow state transitions must be validated; approved bypass preserved | G4 | Software Defect |
| M5-R4 | Search must enforce role-based access control | G9 | Software Defect |
| M5-R5 | `.env.example` must document all required environment variables | G10 | Documentation Issue |

## Appendix B: Deferred and Out-of-Scope Items Summary

| Gap ID | Classification | Recommended Future Action |
|--------|---------------|---------------------------|
| G2 | Deferred — Deployment/Configuration | Address through deployment environment configuration and operational runbook |
| G5 | Deferred — Operational | Address through secret management procedures and key rotation |
| G6 | Deferred — Operational | Address through developer-local configuration cleanup |
| G7 | Deferred | Add to TECH_DEBT.md; address in Phase 2 security hardening |
| G8 | Deferred | Add to TECH_DEBT.md; fix when JWT claims are standardized |
| G11 | Deferred | Add to TECH_DEBT.md; address when schema evolution requires Alembic management |
| G12 | Deferred | Add to roadmap as enhancement task |
| G13 | Deferred | Add to roadmap as enhancement task |
| G14 | Deferred | Add to roadmap as enhancement task |
| G15 | Deferred | Requires Engineering Decision on business process |
| G16 | Deferred | Add to roadmap as enhancement task |
| G17 | Deferred | Add to roadmap as API enhancement |
| G18 | Deferred | Add to roadmap as new feature or remove tables |
| G19 | Deferred | Add to TECH_DEBT.md; address in audit coverage expansion |
| G20 | Deferred | Add to TECH_DEBT.md; address in audit coverage expansion |
| G21 | Deferred | Add to TECH_DEBT.md; address in audit coverage expansion |
| G22 | Deferred | Add to TECH_DEBT.md; address in audit coverage expansion |
| G23 | Out of Scope | Address in Phase 3 |
| G24 | Out of Scope | Existing tests serve as regression coverage |
| G25 | Deferred | Address in M5-T5 after implementation is complete |

---

**END OF STAGE B DOCUMENT**

*This document is a governance artifact only. No implementation was performed. No files were modified. No commits were created.*
