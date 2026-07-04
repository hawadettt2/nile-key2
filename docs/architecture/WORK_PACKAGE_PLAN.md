# Work Package Plan (Software Lifecycle Order)

**Version:** 1.3
**Generated:** 2026-07-04
**Based on:** ARCHITECTURE_CHARTER.md, REPOSITORY_INTELLIGENCE.md, ENGINEERING_MEMORY.md

---

## WP-01: Backend Runtime Stability

**Status:** ✅ Complete

**Objective:** Ensure backend starts without runtime blockers.

**Why It Exists:** Recovery checkpoint requires verification before any changes.

**Scope:** Verify backend starts, health endpoint works, no import errors.

**Files In Scope:**
- backend/main.py
- backend/app/core/config.py
- backend/app/core/database.py
- backend/app/core/security.py
- backend/app/routers/__init__.py
- backend/app/routers/auth.py
- backend/app/routers/shipping.py
- backend/app/routers/invoice.py
- backend/app/routers/suppliers.py
- backend/app/routers/customers.py
- backend/app/routers/customs.py
- backend/app/routers/resources.py
- backend/app/routers/documents.py

**Dependencies:** None

**Validation:**
1. `uvicorn backend.main:app --port 8000` starts
2. GET /health returns {"status":"healthy"}
3. No import errors from core modules

**Rollback:** N/A

---

## WP-02: Database Contract Alignment

**Status:** ✅ Complete (WP-02A-H complete)

**Decomposition:**
| Sub-package | Status | Entity |
|-------------|--------|--------|
| WP-02A | ✅ Complete | users |
| WP-02B | ✅ Complete | suppliers |
| WP-02C | ✅ Complete | customers |
| WP-02D | ✅ Complete | shipments |
| WP-02E | ✅ Complete | invoices |
| WP-02F | ✅ Complete | customs_declarations |
| WP-02G | ✅ Complete | resources |
| WP-02H | ✅ Complete | documents |

**Dependencies:** WP-01

**Validation:**
1. `python -c "from app.core.database import init_db; init_db()"`
2. Verify all schema fields exist as DB columns
3. No missing columns (username, phone, address, etc.)

**Rollback:** 
- WP-02A: `git checkout a0e87e7 -- backend/app/core/database.py`
- WP-02B: `git checkout 94ae639 -- backend/app/core/database.py backend/app/routers/suppliers.py`
- WP-02C: `git checkout 5cec3ca -- backend/app/core/database.py backend/app/routers/customers.py`

---

## WP-03: Authentication Stability

**Status:** ✅ Complete

**Objective:** Ensure authentication system works with correct password algorithm.

**Why It Exists:** Security.py aligned to bcrypt and OAuth2 status codes verified.

**Scope:** Verify password hashing matches requirements.txt (bcrypt) and OAuth2 status codes.

**Files In Scope:**
- backend/app/core/security.py
- backend/app/schemas/user.py
- backend/app/routers/auth.py

**Dependencies:** WP-01

**Validation:**
1. Register user, verify password stored ✅
2. Login works with correct password ✅
3. Algorithm is bcrypt per requirements.txt ✅
4. OAuth2 status codes: 401 for missing auth, 403 for missing role ✅

**Rollback:** `git checkout dbe1ef4 -- backend/app/routers/auth.py`

---

## WP-04: CRUD Integrity

**Status:** ✅ Complete

**Objective:** Fix all CRUD operations to work with aligned schema.

**Why It Exists:** Routes use schema fields that must match DB columns.

**Scope:** Update router handlers to use correct column names after WP-02.

**Files In Scope:**
- backend/app/routers/suppliers.py
- backend/app/routers/customers.py
- backend/app/routers/shipping.py
- backend/app/routers/invoice.py
- backend/app/schemas/supplier.py
- backend/app/schemas/customer.py
- backend/app/schemas/shipment.py
- backend/app/schemas/invoice.py

**Dependencies:** WP-02

**Validation:**
1. All CRUD endpoints return data successfully
2. No SQLite errors on insert/select/update/delete
3. Data persists correctly

**Rollback:** `git checkout backend/app/routers/`

---

## WP-05: Frontend Build Stability

**Status:** ✅ Complete

**Objective:** Ensure frontend builds with current API contract.

**Why It Exists:** Frontend depends on backend; verify after schema changes.

**Scope:** Verify TypeScript compiles, dev server starts.

**Files In Scope:**
- frontend/package.json
- frontend/tsconfig.json
- frontend/vite.config.ts
- frontend/src/main.tsx
- frontend/src/App.tsx
- frontend/src/services/api.ts
- frontend/src/pages/Login.tsx
- frontend/src/pages/Dashboard.tsx
- frontend/src/pages/Suppliers.tsx
- frontend/src/pages/Customers.tsx
- frontend/src/pages/Shipments.tsx
- frontend/src/pages/Invoices.tsx
- frontend/src/pages/Customs.tsx
- frontend/src/pages/Documents.tsx
- frontend/src/pages/Resources.tsx

**Dependencies:** WP-02, WP-04

**Validation:**
1. `npm run build` in frontend completes
2. No TypeScript errors
3. Login page renders

**Rollback:** N/A

---

## WP-06: Integration Testing

**Status:** ✅ COMPLETED

**Objective:** Validate all API endpoints work end-to-end.

**Why It Exists:** Charter Section 18 requires core routes work.

**Scope:** Test each router endpoint with valid requests against running backend.

**Files In Scope:**
- backend/app/routers/auth.py
- backend/app/routers/shipping.py
- backend/app/routers/invoice.py
- backend/app/routers/suppliers.py
- backend/app/routers/customers.py
- backend/app/routers/customs.py
- backend/app/routers/resources.py
- backend/app/routers/documents.py
- backend/app/schemas/* (all schema files)

**Dependencies:** WP-04

**Validation:**
1. Auth endpoints work ✅
2. Suppliers/Customers CRUD work ✅
3. Shipments/Invoices CRUD work ✅
4. Customs endpoints work ✅
5. Resources/Documents endpoints work ✅

**Patch Execution Summary:**
| Patch | Entity | Status | Notes |
|-------|--------|--------|-------|
| Patch-1 | Authentication | ✅ Complete | Login returns JWT token |
| Patch-2 | Suppliers | ✅ Complete | CRUD verified |
| Patch-3 | Customers | ✅ Complete | CRUD verified |
| Patch-4 | Resources | ✅ Complete | CRUD verified |
| Patch-5 | Documents | ✅ Complete | Metadata repair applied |
| Patch-6 | Shipping | ✅ Complete | Router verified, ADR-0001 applied |
| Patch-7 | Invoices | ✅ Complete | Legacy schema compatibility verified |
| Patch-8 | Customs | ✅ Complete | All endpoints verified, DELETE absent by design |

**Rollback:** N/A

---

## WP-07: Security Hardening

**Status:** ✅ COMPLETED

**Objective:** Fix all security violations per charter Section 12.

**Why It Exists:** Hardcoded secrets and wildcard CORS are critical risks.

**Scope:** Externalize SECRET_KEY, fix CORS configuration.

**Files In Scope:**
- backend/app/core/config.py
- backend/.env.example
- backend/main.py

**Dependencies:** WP-01

**Validation:**
1. App fails without SECRET_KEY in production ✅
2. CORS restricts to ALLOWED_ORIGINS ✅
3. No hardcoded defaults in config ✅

**Rollback:** `git checkout backend/app/core/config.py backend/main.py backend/.env.example`

---

## WP-08: Architecture Cleanup

**Status:** ✅ COMPLETED

**Objective:** Prepare architecture for refactoring and migration system.

**Why It Exists:** Charter requires cleanup before refactoring (Sections 8, 10, 16).

**Scope:** Initialize services layer, create SQL helper, align .env.example.

**Files In Scope:**
- backend/app/services/__init__.py
- backend/app/core/database.py
- backend/.env.example

**Dependencies:** WP-01, WP-02

**Validation:**
1. `from app.services import *` imports cleanly ✅
2. Helper function works for UPDATE queries ✅
3. .env.example has all config variables ✅

**Rollback:** Remove added functions, revert .env.example

---

## WP-09: Refactoring

**Status:** ✅ COMPLETED

**Objective:** Extract duplicated logic into reusable components.

**Why It Exists:** Charter Section 8 prohibits code duplication.

**Scope:** Refactor 8 routers to use shared SQL query builder and remove legacy compatibility shims.

**Files In Scope:**
- backend/app/routers/auth.py
- backend/app/routers/shipping.py
- backend/app/routers/invoice.py
- backend/app/routers/suppliers.py
- backend/app/routers/customers.py
- backend/app/routers/customs.py
- backend/app/routers/resources.py
- backend/app/routers/documents.py
- backend/app/core/database.py

**Dependencies:** WP-08

**Validation:**
1. All endpoints still work ✅
2. No code duplication in UPDATE patterns ✅
3. Cleaner router code ✅
4. Legacy compatibility filters removed ✅

**Rollback:** `git checkout backend/app/routers/`

---

## WP-10: Database Migration System

**Status:** ✅ COMPLETED

**Objective:** Add Alembic migrations per charter Phase 3 and remove legacy columns.

**Why It Exists:** Charter requires migrations as legal evolution mechanism.

**Scope:** Initialize Alembic, capture current schema as initial migration, remove legacy columns.

**Files In Scope:**
- alembic.ini
- backend/alembic/ directory
- backend/app/core/database.py
- backend/app/routers/*.py

**Dependencies:** WP-02, WP-09

**Validation:**
1. `alembic upgrade head` applies migration on existing schema ✅
2. Migration reversible ✅
3. `invoices.uuid` removed ✅
4. Legacy columns dropped via SQLite-safe table rebuild where needed ✅

**Execution Notes:**
- `init_db()` owns initial schema creation
- Alembic migrations handle destructive post-init cleanup only
- Initial migration revision is empty (`pass`) because schema is created by `init_db()`

**Rollback:** Remove alembic directory and revert routers/models/config changes

---

## WP-11: Deployment Validation

**Status:** ⏳ In Progress

**Objective:** Validate deployment configuration.

**Why It Exists:** Charter Phase 6 requires deployment validation.

**Scope:** Add Dockerfiles, verify containerization.

**Files In Scope:**
- backend/Dockerfile
- frontend/Dockerfile
- docker-compose.yml
- .dockerignore
- backend/requirements.txt
- frontend/package.json
- backend/app/core/config.py

**Dependencies:** WP-10

**Validation:**
1. `docker compose up` starts both services
2. Health endpoint accessible in container
3. No volume/mount errors

**Rollback:** Remove Docker files

---

## WP-12: Production Readiness

**Status:** ☐ Not Started

**Objective:** Final production hardening per charter Phase 7.

**Why It Exists:** Charter requires production readiness before completion.

**Scope:** Generate frontend types, finalize documentation, verify quality gates.

**Files In Scope:**
- frontend/src/types/
- frontend/src/services/api.ts
- docs/architecture/REPOSITORY_INTELLIGENCE.md
- docs/architecture/WORK_PACKAGE_PLAN.md

**Dependencies:** WP-10, WP-11

**Validation:**
1. All quality gates pass (charter Section 18)
2. Frontend types match API
3. Documentation updated

**Rollback:** Remove generated types

---

## Execution Sequence

WP-01 → WP-02 → WP-03 → WP-04 → WP-05 → WP-06 → WP-07 → WP-08 → WP-09 → WP-10 → **WP-11** → WP-12

---

## WP-03 Rollback Points

| WP | Rollback Command |
|----|------------------|
| WP-03 | `git checkout dbe1ef4 -- backend/app/routers/auth.py` |

---

## WP-02 Rollback Points

| WP | Rollback Command |
|----|------------------|
| WP-02A-H | `git checkout 3219904 -- backend/app/core/database.py` |
| WP-02A | `git checkout a0e87e7 -- backend/app/core/database.py` |
| WP-02B | `git checkout 94ae639 -- backend/app/core/database.py backend/app/routers/suppliers.py` |
| WP-02C | `git checkout 5cec3ca -- backend/app/core/database.py backend/app/routers/customers.py` |

---

## WP-10 Rollback Points

| WP | Rollback Command |
|----|------------------|
| WP-10 | `git checkout 9f6e6d58ca0f` |

