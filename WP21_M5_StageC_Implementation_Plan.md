# WP-21 Milestone 5
## Stage C — Implementation Plan

**Document Status:** APPROVED FOR IMPLEMENTATION
**Based On:** WP21_M5_StageB_Gap_Analysis_Remediation_Plan.md (approved)
**Authoritative Sources:** PLAN.md, Stage B Plan, Stage A Report
**Date:** 2026-07-14
**Baseline Commit:** c6d8fec7d97bf0b6a7187fbeca351e2d6aa9be78

---

## 1. Executive Summary

### Purpose

This document defines the implementation approach for the 5 approved remediation packages in WP-21 Milestone 5. It translates the governance-approved "WHAT" from Stage B into an actionable implementation plan organized into discrete, verifiable packages.

### Scope

- **In Scope:** M5-R1 through M5-R5 as approved in Stage B
- **Out of Scope:** Deferred items (G2, G5-G8, G11-G22, G25), Out-of-Scope items (G23-G24), and any new features
- **Boundary:** No architectural changes, no database schema redesign, no scope expansion

### Source Documents

1. `WP21_M5_StageB_Gap_Analysis_Remediation_Plan.md` - Approved remediation packages and acceptance criteria
2. `WP21_M5_StageA_Baseline_Verification_Report.md` - Evidence and gap analysis
3. `PLAN.md` - WP-21 acceptance criteria and architecture rules
4. `CURRENT_STATUS.md` - Implementation state
5. `TECH_DEBT.md` - Technical debt context

### Implementation Constraints

- Follow existing code patterns and conventions
- Preserve all existing API contracts
- No breaking changes to frontend or backend interfaces
- Minimal, targeted changes only
- Verify after each package before proceeding
- Keep repository clean throughout

---

## 2. Scope of Implementation

### Approved Packages

| Package | Objective | Category |
|---------|-----------|----------|
| M5-R1 | Dashboard must display live data without manual page reload | Software Defect |
| M5-R2 | Notification sends must be auditable | Software Defect |
| M5-R3 | Workflow state transitions must be validated; approved bypass preserved | Software Defect |
| M5-R4 | Search must enforce role-based access control | Software Defect |
| M5-R5 | `.env.example` must document all required environment variables | Documentation Issue |

### Explicitly Out of Scope

- G2 (SMTP deployment configuration) - operational/deployment task
- G5-G6 (SECRET_KEY management) - operational tasks
- G7 (Rate limiting expansion) - deferred technical debt
- G8 (Refresh token role claim) - deferred
- G11 (Alembic migration) - deferred
- G12-G18 (Search/Dashboard coverage expansion) - scope expansion
- G19-G22 (Additional audit coverage) - deferred
- G23-G24 (E2E/regression tests) - out of scope
- G25 (Documentation synchronization) - deferred to M5-T5

---

## 3. Remediation Packages

### Package M5-R1: Dashboard Live Data

**Gap:** G1 - Dashboard data loads only on page mount; no live update mechanism
**Evidence:** `frontend/src/pages/Dashboard.tsx` line 38: `useEffect(() => { loadDashboard(); }, [])` with no polling, WebSocket, or SSE.
**Current Behavior:** Dashboard loads once when component mounts. Users must manually refresh to see updated data.
**Required Behavior:** Dashboard data refreshes automatically without manual page reload.

**Approach:**
- Add auto-refresh polling to `Dashboard.tsx` using existing `loadDashboard()` function
- Preserve existing on-mount load
- Use a conservative polling interval
- No backend changes required

**Files to Modify:**
- `frontend/src/pages/Dashboard.tsx`

**Constraints:**
- No changes to Dashboard API (`backend/app/routers/dashboard.py`)
- No changes to Dashboard service (`backend/app/services/dashboard.py`)
- No changes to database schema
- No new dependencies

---

### Package M5-R2: Notification Audit Logging

**Gap:** G3 - Notification sending is not logged to `audit_logs` or `notification_logs`
**Evidence:** `backend/app/services/notification.py` lines 97-123 (`send_template_email`) contains no audit logging. `notification_logs` table exists at `backend/app/core/database.py` lines 390-401 but is unused.

**Current Behavior:** `send_template_email()` sends email but does not create any audit trail.

**Required Behavior:**
- Each notification send creates a record in `audit_logs`
- Each notification send creates a record in `notification_logs`
- Existing notification functionality unchanged

**Approach:**
- Modify `send_template_email()` in `backend/app/services/notification.py` to:
  1. Insert a record into `notification_logs` table after successful send
  2. Call `log_audit()` with appropriate parameters
- Follow existing audit patterns used in other services
- Preserve existing return value format

**Files to Modify:**
- `backend/app/services/notification.py`

**Constraints:**
- No changes to notification trigger logic
- No changes to `notification_templates` table schema
- No changes to frontend notification display
- No changes to `send_email()` function signature

---

### Package M5-R3: Workflow State Validation

**Gap:** G4 - `update_workflow()` allows arbitrary state updates without validating transitions
**Evidence:** `backend/app/services/workflow.py` lines 155-194 (`update_workflow`) accepts `data.state` and writes it directly. `transition_workflow()` at line 207 correctly validates, but `update_workflow` does not.

**Current Behavior:** Any client with PUT permission can set workflow to any state, bypassing the state machine.

**Required Behavior:**
- All workflow state updates must be validated against the approved state machine
- Invalid transitions must be rejected
- Approved CR-M4-001 Rev.1 bypass (`draft` -> `shipped`) must be preserved

**Approach:**
- Modify `update_workflow()` in `backend/app/services/workflow.py` to call `_validate_transition()` when `data.state` is provided
- Preserve all existing valid transitions
- Preserve approved bypass
- Maintain existing API contract

**Files to Modify:**
- `backend/app/services/workflow.py`

**Constraints:**
- Do not remove or modify the approved `draft` -> `shipped` bypass
- Do not change valid transition rules
- Do not modify workflow summary generation
- Do not change item handling logic

---

### Package M5-R4: Search Role-Based Access Control

**Gap:** G9 - Search endpoint has no role-based permission check
**Evidence:** `backend/app/routers/search.py` line 15: `current_user: dict = Depends(get_current_user)` - no `require_role` check.

**Current Behavior:** Any authenticated user can search all 9 entity types.

**Required Behavior:**
- Search endpoint must enforce role-based access control
- Follow existing RBAC patterns in the repository
- Preserve existing authentication requirement

**Approach:**
- Add `require_role()` dependency to search endpoint in `backend/app/routers/search.py`
- Follow the pattern used in other routers (e.g., `routers/auth.py` lines 54-59)
- Authorized roles: internal staff roles as defined by existing repository RBAC policy
- Preserve existing search logic, SQL, and results

**Files to Modify:**
- `backend/app/routers/search.py`

**Constraints:**
- No changes to `services/search.py`
- No changes to search SQL or ranking logic
- No changes to search API contract
- No changes to searchable entities

---

### Package M5-R5: Configuration Documentation

**Gap:** G10 - `.env.example` does not list `OWNER_PASSWORD` or SMTP variables
**Evidence:** `backend/.env.example` contains 16 variables. `OWNER_PASSWORD` is required at startup (`backend/app/core/database.py` line 746) but not documented. SMTP variables defined in `config.py` but not in `.env.example`.

**Current Behavior:** `.env.example` is missing required environment variables.

**Required Behavior:**
- `.env.example` must document all required environment variables
- No changes to developer-local `.env` files

**Approach:**
- Update `backend/.env.example` to add missing variables:
  - `OWNER_PASSWORD`
  - `SMTP_HOST`
  - `SMTP_PORT`
  - `SMTP_USER`
  - `SMTP_PASSWORD`
  - `SMTP_FROM`
  - `SMTP_USE_TLS`

**Files to Modify:**
- `backend/.env.example`

**Constraints:**
- Do not modify developer-local `.env` files
- Do not set or rotate actual secret values
- Do not change configuration validation logic

---

## 4. Implementation Order

**The following sequencing is suggested for verification efficiency only. All packages may be implemented in any order or in parallel, as no proven technical dependencies exist between them.**

1. **M5-R5 (Configuration Documentation)** - Documentation change with zero regression risk. Can be completed and verified immediately.
2. **M5-R3 (Workflow State Validation)** - Critical correctness fix. Should be resolved early to prevent invalid state transitions during other testing.
3. **M5-R2 (Notification Audit Logging)** - Independent backend change. Can be implemented and verified in isolation.
4. **M5-R1 (Dashboard Live Data)** - Independent frontend change. Can be implemented in parallel with backend packages.
5. **M5-R4 (Search RBAC)** - Independent backend change. Can be implemented in parallel with other packages.

### Sequencing Rationale

- **M5-R5 first** because it is documentation-only with zero regression risk, providing immediate progress.
- **M5-R3 second** because it addresses a critical correctness issue that should be resolved before broader testing.
- **M5-R2, M5-R1, M5-R4** can be implemented in any order or in parallel as they have no technical dependencies on each other or on preceding packages.

**Note:** This sequencing is a suggestion only. The implementation agent may reorder packages based on runtime priorities, as long as each package is verified independently before marking complete.

---

## 5. Dependencies

### External Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Stage B Approval | Required | This plan assumes Stage B is formally approved |
| Engineering Decisions | May be required | Dashboard live data approach (M5-R1) if it deviates from existing patterns |
| Change Requests | May be required | If any package introduces changes affecting API contracts or deployment procedures |
| Governance Documentation Sync | Required | PLAN.md, CURRENT_STATUS.md, TECH_DEBT.md must be updated before Stage C begins per Stage B Section 10 |

### Internal Dependencies

| Package | Depends On | Reason |
|---------|------------|--------|
| M5-R1 | None | Independent frontend change |
| M5-R2 | None | Independent backend change |
| M5-R3 | None | Independent backend change |
| M5-R4 | None | Independent backend change |
| M5-R5 | None | Independent documentation change |

### Prerequisites

- Baseline commit c6d8fec7d97bf0b6a7187fbeca351e2d6aa9be78 checked out
- Clean working tree
- Backend starts successfully with `uvicorn main:app`
- Frontend builds successfully with `npm run build`
- Test suite executes successfully

---

## 6. Verification Strategy

### Per-Package Verification

Each package must be verified independently before proceeding to the next. Verification includes:

1. **Compilation Check:** Backend and frontend compile without errors
2. **Test Execution:** Relevant tests pass
3. **Regression Check:** No existing tests broken
4. **Acceptance Criteria Check:** All acceptance criteria from Stage B are met
5. **Manual Verification:** Where applicable, manual confirmation of behavior

### Verification Sequence

For each package:
1. Implement changes
2. Run backend tests: `cd backend && pytest tests/ -v`
3. Run frontend build: `cd frontend && npm run build`
4. Verify acceptance criteria
5. If any check fails, rollback and revise
6. If all checks pass, mark package complete and proceed

### Final Verification

After all packages are complete:
1. Run full backend test suite
2. Run frontend build verification
3. Verify OpenAPI specification unchanged (where required)
4. Verify no database schema changes
5. Verify repository is clean
6. Confirm all acceptance criteria met

---

## 7. Testing Strategy

### Unit Tests

- Run existing unit tests after each package
- No new unit tests required for M5-R1, M5-R4, M5-R5
- M5-R2 may require new unit tests for notification audit logging
- M5-R3 may require new unit tests for workflow state validation in `update_workflow`

### Integration Tests

- Run existing integration tests after each package
- M5-R3: Verify workflow transition tests still pass
- M5-R4: Verify search endpoint returns 403 for unauthorized roles
- M5-R2: Verify notification audit records are created

### Regression Tests

- Full backend test suite must pass after all packages
- Frontend build must succeed
- No existing tests may be broken

### Test Commands

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend build
cd frontend
npm run build
```

### Test Count Baseline

- Current: 414 test functions (34 backend files + 2 frontend files)
- Expected after M5: Same count + any new tests added for M5-R2 and M5-R3

---

## 8. Rollback Strategy

### General Rollback Principle

Each package is implemented as a discrete change. If a package causes issues, it can be rolled back independently without affecting other packages.

### Per-Package Rollback

| Package | Rollback Method | Complexity |
|---------|-----------------|------------|
| M5-R1 | Remove polling code from `Dashboard.tsx`, revert to single on-mount load | Low |
| M5-R2 | Remove audit logging calls from `notification.py`, revert to original function | Low |
| M5-R3 | Remove `_validate_transition()` call from `update_workflow()`, revert to original behavior | Medium |
| M5-R4 | Remove `require_role()` dependency from `search.py`, revert to `get_current_user` only | Low |
| M5-R5 | Revert `.env.example` to original content | Very Low |

### Rollback Triggers

- Any existing test fails after package implementation
- API contract broken
- Frontend build fails
- Runtime error on backend startup
- Acceptance criteria cannot be verified

### Rollback Procedure

1. Stop implementation immediately
2. Revert the specific package changes using git
3. Document the issue in TECH_DEBT.md or incident report
4. Analyze root cause before re-attempting
5. Do not proceed to next package until rollback is complete and understood

---

## 9. Deliverables

### Code Changes

| Package | Files Modified | Type |
|---------|---------------|------|
| M5-R1 | `frontend/src/pages/Dashboard.tsx` | Frontend code |
| M5-R2 | `backend/app/services/notification.py` | Backend code |
| M5-R3 | `backend/app/services/workflow.py` | Backend code |
| M5-R4 | `backend/app/routers/search.py` | Backend code |
| M5-R5 | `backend/.env.example` | Documentation |

### Documentation Updates

After all packages are complete:
- Update `CURRENT_STATUS.md` with M5 completion status
- Update `TECH_DEBT.md` to reflect resolved items
- Update `PLAN.md` if required by governance

### Test Updates

- Existing tests must continue to pass
- New tests may be added for M5-R2 and M5-R3 if required by acceptance criteria

### Commit

- Single commit for all M5 packages (or one commit per package if preferred)
- Commit message must follow project convention: `feat(wp21-m5): complete milestone 5 remediation packages`
- No mixed-purpose commits

---

## 10. Completion Criteria

Stage C is complete when ALL of the following are true:

1. **All 5 packages implemented:** M5-R1 through M5-R5 are complete
2. **All acceptance criteria met:** Every criterion in Stage B Section 5 is verified
3. **All tests pass:** Full backend and frontend test suites pass
4. **No regressions:** No existing functionality broken
5. **Repository clean:** No uncommitted changes except those being committed
6. **Documentation updated:** CURRENT_STATUS.md and TECH_DEBT.md reflect M5 completion
7. **Governance cleared:** Stage B approval conditions are satisfied
8. **Commit created:** Changes committed with proper message

---

## 11. Definition of Done per Package

### M5-R1: Dashboard Live Data

- [ ] `Dashboard.tsx` contains auto-refresh mechanism
- [ ] Existing on-mount load preserved
- [ ] Dashboard data updates without manual page reload
- [ ] No API contract changes
- [ ] No database schema changes
- [ ] All existing tests pass
- [ ] Frontend build succeeds

### M5-R2: Notification Audit Logging

- [ ] `send_template_email()` inserts records into `notification_logs`
- [ ] `send_template_email()` calls `log_audit()` with `entity_type="notification"`
- [ ] Each send creates exactly one audit record and one notification log record
- [ ] No duplicate audit events
- [ ] Existing notification functionality unchanged
- [ ] All existing notification tests pass
- [ ] Backend test suite passes

### M5-R3: Workflow State Validation

- [ ] `update_workflow()` calls `_validate_transition()` when `data.state` is provided
- [ ] Invalid state transitions are rejected with `ValueError`
- [ ] Valid transitions succeed: `draft` -> `customs_ready`, `customs_ready` -> `shipped`, `shipped` -> `delivered`
- [ ] Approved CR-M4-001 Rev.1 bypass preserved: `draft` -> `shipped` succeeds
- [ ] All existing workflow tests pass
- [ ] Backend test suite passes

### M5-R4: Search RBAC

- [ ] `search.py` has `require_role()` dependency
- [ ] Unauthorized role requests receive 403
- [ ] Authorized roles can search successfully
- [ ] Unauthenticated requests receive 401
- [ ] Search results unchanged for authorized users
- [ ] `services/search.py` unchanged
- [ ] All existing search tests pass
- [ ] Backend test suite passes

### M5-R5: Configuration Documentation

- [ ] `OWNER_PASSWORD` is listed in `.env.example`
- [ ] `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS` are listed in `.env.example`
- [ ] No other repository files modified
- [ ] All existing tests pass

---

## 12. Expected Risks and Verification

### M5-R1: Dashboard Live Data

| Risk | Likelihood | Impact | Verification |
|------|------------|--------|--------------|
| Polling causes excessive API calls | Low | Medium | Monitor network requests during testing; verify interval is reasonable |
| Race condition on rapid data changes | Low | Low | Verify dashboard updates correctly on multiple rapid polls |
| Memory leak from uncleaned intervals | Low | Medium | Verify cleanup on component unmount |
| Frontend test failures | Low | Low | Run frontend test suite after implementation |

### M5-R2: Notification Audit Logging

| Risk | Likelihood | Impact | Verification |
|------|------------|--------|--------------|
| Duplicate audit records on retry | Medium | Low | Verify each send creates exactly one audit record |
| Performance impact on notification sends | Low | Low | Benchmark notification send latency before/after |
| Database connection leak | Low | Medium | Verify connections are properly closed |
| Existing notification tests fail | Low | Medium | Run full notification test suite |

### M5-R3: Workflow State Validation

| Risk | Likelihood | Impact | Verification |
|------|------------|--------|--------------|
| Existing tests rely on bypass behavior | Medium | High | Run full workflow test suite; identify and update any tests asserting invalid behavior |
| Valid transitions incorrectly rejected | Low | High | Test all valid transitions explicitly |
| CR-M4-001 Rev.1 bypass broken | Low | High | Explicitly test `draft` -> `shipped` transition |
| API contract changed | Low | Medium | Verify all workflow endpoints return same response structure |

### M5-R4: Search RBAC

| Risk | Likelihood | Impact | Verification |
|------|------------|--------|--------------|
| Authorized roles incorrectly blocked | Low | Medium | Test all authorized roles explicitly |
| Unauthorized roles still have access | Low | High | Test all unauthorized roles explicitly |
| Search results changed for authorized users | Low | Medium | Compare search results before/after for same queries |
| Authentication bypassed | Low | High | Verify unauthenticated requests still receive 401 |

### M5-R5: Configuration Documentation

| Risk | Likelihood | Impact | Verification |
|------|------------|--------|--------------|
| Missing variables not documented | Low | Low | Cross-check `.env.example` against `config.py` and `database.py` |
| Incorrect variable names | Low | Low | Verify variable names match code exactly |
| Documentation format inconsistency | Low | Low | Verify format matches existing `.env.example` style |

---

## 13. Expected Files to Modify

### M5-R1: Dashboard Live Data

| File | Change Type | Purpose |
|------|-------------|---------|
| `frontend/src/pages/Dashboard.tsx` | Modify | Add auto-refresh polling mechanism |

### M5-R2: Notification Audit Logging

| File | Change Type | Purpose |
|------|-------------|---------|
| `backend/app/services/notification.py` | Modify | Add audit logging and `notification_logs` insert in `send_template_email()` |

### M5-R3: Workflow State Validation

| File | Change Type | Purpose |
|------|-------------|---------|
| `backend/app/services/workflow.py` | Modify | Add `_validate_transition()` call in `update_workflow()` when `data.state` is provided |

### M5-R4: Search RBAC

| File | Change Type | Purpose |
|------|-------------|---------|
| `backend/app/routers/search.py` | Modify | Add `require_role()` dependency to search endpoint |

### M5-R5: Configuration Documentation

| File | Change Type | Purpose |
|------|-------------|---------|
| `backend/.env.example` | Modify | Add missing environment variables: `OWNER_PASSWORD`, SMTP variables |

---

## 14. Verification Checklist

### Pre-Implementation

- [ ] Stage B is formally approved
- [ ] Baseline commit c6d8fec7d97bf0b6a7187fbeca351e2d6aa9be78 is checked out
- [ ] Working tree is clean
- [ ] Backend starts successfully: `uvicorn main:app`
- [ ] Frontend builds successfully: `npm run build`
- [ ] Test suite passes: `pytest tests/ -v`

### Post-Implementation (Per Package)

- [ ] Package acceptance criteria verified
- [ ] Relevant tests pass
- [ ] No existing tests broken
- [ ] API contracts unchanged (where required)
- [ ] Database schema unchanged (where required)
- [ ] Frontend build succeeds (if frontend changed)
- [ ] Backend starts successfully (if backend changed)

### Final Verification

- [ ] All 5 packages complete
- [ ] Full backend test suite passes
- [ ] Frontend build succeeds
- [ ] No regressions
- [ ] Repository is clean
- [ ] Documentation updated
- [ ] Commit created with proper message

---

## 15. Post-Implementation Requirements

Per Stage B Section 10, after implementation:

1. **Governance documentation must be synchronized:**
   - Update `PLAN.md` if required
   - Update `CURRENT_STATUS.md` with M5 completion
   - Update `TECH_DEBT.md` to reflect resolved items

2. **No implementation details may be altered** without new Engineering Decision and Change Request

3. **Repository must remain clean** throughout implementation

4. **Any new issues discovered** must be documented and classified before being addressed

---

## 16. Out-of-Scope Reminders

The following are explicitly NOT part of this implementation plan:

- SMTP deployment configuration (G2)
- SECRET_KEY rotation (G5)
- Backend `.env` cleanup (G6)
- Rate limiting expansion (G7)
- Refresh token role claim fix (G8)
- Alembic migration fix (G11)
- Workflow in Search (G12)
- Workflow in Dashboard (G13)
- Notifications in Search (G14)
- ETA-Workflow integration (G15)
- Workflow notification triggers (G16)
- Reverse lookup endpoints (G17)
- Contacts/Addresses endpoints (G18)
- Auth event audit logging (G19)
- Search query audit logging (G20)
- ETA status/PDF audit logging (G21)
- Shipping track/label audit logging (G22)
- E2E testing infrastructure (G23)
- Dedicated regression suite (G24)
- Documentation synchronization (G25)

These items are deferred or out of scope per Stage B. Implementing any of them without a new Stage B approval would violate project governance rules.

---

**END OF STAGE C IMPLEMENTATION PLAN**

*This document is a planning artifact only. No implementation has been performed. No files have been modified. No commits have been created.*
