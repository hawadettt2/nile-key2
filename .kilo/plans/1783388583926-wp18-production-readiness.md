# WP-18: Production Bug Fixes and Deployment Readiness

**Version:** 1.4
**Generated:** 2026-07-05
**Baseline:** baseline-wp17b
**Goal:** Fix two pre-existing production bugs identified during WP-17A/WP-17B test expansion, then validate deployment artifacts to reach production-ready state.

---

## Priority Rationale

After WP-17B, the project has:
- 170 passing tests
- Full service-layer coverage
- Complete thin-router architecture
- Validated test infrastructure

The remaining work that has the **highest production-readiness impact** with **lowest risk** is:

1. **Fix Customs HS-code schema mismatch** — `created_at` column missing in `hs_codes` table causes `ResponseValidationError` (500) on list/get endpoints. This is a **runtime bug** affecting a production endpoint.

2. **Fix Document upload `type` NOT NULL omission** — `upload_document()` service omits the `type` column in its INSERT statement, causing `sqlite3.IntegrityError` at runtime. This is a **runtime bug** affecting a production endpoint.

3. **Docker deployment validation** — Docker artifacts exist but have never been validated. Deployment readiness verification is required per charter Phase 6 and PLAN.md "Stage 4".

These were chosen over architectural changes (PostgreSQL migration, rate limiting) because:
- They fix **real runtime errors** in production code paths
- They are **small, isolated changes** with clear rollback paths
- They maintain **full backward compatibility**
- They unblock complete API test coverage
- They directly increase **production readiness**

---

## Patch Breakdown

### Patch-1: Fix Customs HS-code Schema Mismatch

**Objective:** Add `created_at` column to `hs_codes` table so the `HSCode` response schema can serialize successfully.

**Root Cause:** `app/schemas/customs.py` defines `HSCode` with `created_at: datetime`, but `_create_tables()` in `database.py` creates `hs_codes` without this column, and `_ensure_hs_codes_schema()` only adds `description_ar` and `restrictions`.

**Files Expected to Change:**
- `backend/app/core/database.py` — add `created_at` to `_ensure_hs_codes_schema()`
- `backend/tests/test_customs.py` — enable previously excluded HS-code list/get tests
- `backend/tests/test_services/test_customs_service.py` — enable previously excluded HS-code tests

**Risk:** LOW
- Isolated to one table migration
- Backward compatible: `ALTER TABLE ... ADD COLUMN` with default
- No data loss risk
- Existing code paths unaffected

**Acceptance Criteria:**
1. `hs_codes` table has `created_at` column after `init_db()`
2. `GET /api/v1/customs/hs-codes` returns 200 with valid `HSCode` responses
3. `GET /api/v1/customs/hs-codes/{id}` returns 200 with valid `HSCode` response
4. Existing duty calculation and declaration tests still pass
5. Service-layer unit tests for HS code functions still pass

**Verification Steps:**
1. `cd backend && python -m pytest tests/test_customs.py -v`
2. `cd backend && python -m pytest tests/test_services/test_customs_service.py -v`
3. `cd backend && python -m pytest tests/ -v` (full suite)
4. Manual smoke test: `GET /api/v1/customs/hs-codes` returns list with `created_at` fields

**Rollback:** Revert `_ensure_hs_codes_schema()` change; remove re-enabled tests.

---

### Patch-2: Fix Document Upload `type` Column Omission

**Objective:** Fix `upload_document()` service to include the required `type` column in its INSERT statement.

**Root Cause:** `app/services/document.py` `upload_document()` inserts into `documents` with columns `(title, file_name, file_type, file_size, document_type, entity_type, entity_id, created_at, created_by)` but the `documents` table schema defines `type TEXT NOT NULL` as a required column. The service should include `type` with value `"uploaded"` to match the pattern used in `create_document()`.

**Files Expected to Change:**
- `backend/app/services/document.py` — add `type` column to INSERT statement
- `backend/tests/test_documents.py` — enable previously excluded upload test
- `backend/tests/test_services/test_document_service.py` — update or add test for upload return shape

**Risk:** LOW
- Single INSERT statement change
- Backward compatible: adds missing required column
- No data loss risk
- Existing code paths unaffected

**Acceptance Criteria:**
1. `POST /api/v1/documents/upload` returns 200 with valid `DocumentUploadResponse`
2. Uploaded document record has `type = "uploaded"` in database
3. Existing document CRUD tests still pass
4. Service-layer tests for upload validation still pass

**Verification Steps:**
1. `cd backend && python -m pytest tests/test_documents.py -v`
2. `cd backend && python -m pytest tests/test_services/test_document_service.py -v`
3. `cd backend && python -m pytest tests/ -v` (full suite)
4. Manual smoke test: upload a small PDF via `/api/v1/documents/upload` returns success

**Rollback:** Revert `upload_document()` INSERT change; disable upload test.

---

### Patch-3: Docker Deployment Validation

**Objective:** Validate Docker Compose setup by reviewing and verifying all Docker artifacts are correct and consistent.

**Rationale:** Docker files exist but have never been validated in any environment. Deployment readiness requires at minimum verified Docker artifacts.

**Files Expected to Change:**
- `docker-compose.yml` — minor fixes if inconsistencies found
- `backend/Dockerfile` — minor fixes if inconsistencies found
- `frontend/Dockerfile` — minor fixes if inconsistencies found
- `DEPLOYMENT.md` — update if artifacts change

**Risk:** LOW
- Read-only review first
- Only configuration changes, no application logic
- Backward compatible: changes are additive or config-only

**Acceptance Criteria:**
1. All Dockerfiles use consistent base images
2. `docker-compose.yml` service names, ports, and volumes are correct
3. Health checks are present where appropriate
4. Environment variable references match `config.py`
5. Documentation matches actual Docker setup

**Verification Steps:**
1. Review each Dockerfile for best practices
2. Review `docker-compose.yml` for service consistency
3. Cross-reference environment variables with `backend/app/core/config.py`
4. Update `DEPLOYMENT.md` if any fixes are applied
5. Note: `docker compose up` cannot be executed in this environment; validation is static only

**Rollback:** Revert any Dockerfile changes.

---

## Execution Order

1. **Patch-1:** Customs HS-code schema fix
2. **Patch-2:** Document upload type column fix
3. **Patch-3:** Docker deployment validation

Each patch is independently verifiable and reversible.

---

## Out of Scope for WP-18

- Rate limiting implementation (requires middleware architecture decision)
- PostgreSQL migration path (architectural change, deferred to future phase)
- Root `alembic.ini` cleanup (low priority)
- `__pycache__` cleanup (low priority)
- Frontend changes
- New features

---

## Dependencies

- Patch-1 depends on: WP-17A/WP-17B (test infrastructure exists)
- Patch-2 depends on: WP-17A/WP-17B (test infrastructure exists)
- Patch-3 depends on: WP-12 (Docker artifacts exist)

---

## Success Criteria for WP-18 Completion

- [ ] All HS-code endpoints return valid responses
- [ ] Document upload works end-to-end
- [ ] Docker artifacts validated and consistent
- [ ] Full pytest suite passes (170+ tests)
- [ ] No production regressions
- [ ] Documentation reflects any changes
