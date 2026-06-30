# Engineering Memory

**Last Updated:** 2026-06-30
**Project:** Nile Key Platform
**Architecture Charter:** Governing document (must not be violated)

| WP | Status | Commit | Notes |
|----|--------|--------|-------|
| WP-01A | ✅ Complete | 3597c67 | Unicode emoji fix in main.py lifespan for Windows compatibility |
| WP-01B | ✅ Complete | d036c06 (recovery) | Reverted to bcrypt, installed bcrypt<4.0 for passlib compatibility |
| WP-02A | ✅ Complete | a0e87e7 | Added username, phone, company, updated_at columns to users table; fixed auth.py column reference |
| WP-02B | ✅ Complete | 6296d0a | Added name_en, contact_person, country, commercial_registry, updated_at, created_by columns to suppliers table |
| WP-02-Infra | ✅ Complete | 98838d1 | Added ensure_columns() helper for reusable schema migrations |
| Doc-01 | ✅ Complete | 9a1682d | Established ENGINEERING_MEMORY.md, WORK_PACKAGE_PLAN.md, PROJECT_BASELINE.md, REPOSITORY_INTELLIGENCE.md, ARCHITECTURE_CHARTER.md |

---

## Completed Commits

| Hash | Message | Date |
|------|---------|------|
| 98838d1 | infrastructure: add ensure_columns() helper for WP-02B-H schema migrations | 2026-06-30 |
| a0e87e7 | WP-02A: Align users schema with backend contract | 2026-06-30 |
| 8091764 | docs: update ENGINEERING_MEMORY with Doc-01 commit | 2026-06-30 |
| 9a1682d | docs: establish architecture documentation and engineering memory | 2026-06-30 |
| d036c06 | WP-01: Backend Runtime Stability completed | 2026-06-30 |
| 3597c67 | WP-01A: Backend runtime startup stabilized | 2026-06-30 |
| 25b9fd6 | chore: initialize AI governance structure | 2026-06-28 |

---

## Important Architectural Decisions

1. **SQLite is implementation detail** (per charter Section 9) - will change to PostgreSQL in production
2. **Pydantic schemas are Source of Truth** - database must follow schemas
3. **bcrypt is required password algorithm** - passlib[bcrypt] in requirements.txt
4. **No business logic in routers** (charter Section 10) - must move to services layer
5. **Code duplication prohibited** (charter Section 8) - must extract SQL helpers
6. **Legacy Compatibility Policy** - When a legacy database column is still required for compatibility, it may receive a temporary default value. New business logic must never depend on that column. Removal is deferred to the dedicated Database Cleanup phase.

---

## Rejected Approaches

| Approach | Reason |
|----------|--------|
| bcrypt 5.0.0 with passlib 1.7.4 | Incompatible: __about__ attribute removed in bcrypt 5.x |
| pbkdf2_sha256 for password hashing | Violates requirements.txt (bcrypt specified) |
| Keeping Unicode emojis in main.py | Causes UnicodeEncodeError on Windows cp1256 console |

---

## Recovery Checkpoints

| File | Change | Reason |
|------|--------|--------|
| backend/app/core/config.py | DEBUG: bool -> str | Pydantic-settings needs string for env vars |
| backend/app/core/database.py | Added get_db() | Required by router code (was missing) |
| backend/app/models/__init__.py | Removed imports | Was causing ImportError (modules don't exist) |

All recovery changes: **KEEP** (syntactically valid, functionally safe)

---

## Known Risks

| Risk Level | Issue | Status |
|------------|-------|--------|
| 🔴 CRITICAL | Database schema mismatch | WP-02A: users fixed; WP-02B: suppliers fixed; WP-02C-H: Pending customers-shipments-invoices-customs-resources-documents |
| 🔴 CRITICAL | Hardcoded SECRET_KEY | Pending WP-07 |
| 🔴 CRITICAL | Wildcard CORS | Pending WP-07 |
| 🟠 HIGH | Missing services layer | Pending WP-08 |
| 🟡 MEDIUM | No migrations | Pending WP-10 |

---

## Current Project Status

| Component | Status |
|-----------|--------|
| Backend | ✅ Running (port 8001) |
| Health endpoint | ✅ healthy |
| OpenAPI schema | ✅ Available |
| Users table schema | ✅ Complete (WP-02A) |
| Frontend build | ⚠️ Not verified |
| Docker | ❌ Not available |
| Tests | ❌ None |

---

## WP-02 Decomposition Status

| Sub-package | Status | Entity |
|-------------|--------|--------|
| WP-02A | ✅ Complete | users |
| WP-02B | ✅ Complete | suppliers |
| WP-02C | Pending | customers |
| WP-02D | Pending | shipments |
| WP-02E | Pending | invoices |
| WP-02F | Pending | customs_declarations |
| WP-02G | Pending | resources |
| WP-02H | Pending | documents |

---

## WP-02A Verification Results

| Test | Result |
|------|--------|
| Fresh DB init | ✅ Success - all columns present |
| Existing DB upgrade | ✅ Success - columns added, data preserved |
| Backend startup | ✅ Healthy (port 8001) |
| Login works | ✅ Token returned for owner user |
| Password hashes intact | ✅ bcrypt `$2b$12$` format preserved |
| User IDs intact | ✅ Auto-increment preserved |
| Authenticated routes work | ✅ `/api/v1/auth/me` accessible with token |

---

## WP-02B Verification Results

| Test | Result |
|------|--------|
| Fresh DB init | ✅ Success - all 22 columns present |
| Existing DB upgrade | ✅ Success - columns added, data preserved |
| Backend startup | ✅ Healthy (port 8001) |
| Login works | ✅ Token returned |
| Supplier CRUD | ✅ Create, Read, Update work |
| Legacy compatibility | ✅ `type` column receives default "general" value |

---

## Remaining Work Packages

WP-02C → WP-02D → WP-02E → WP-02F → WP-02G → WP-02H → WP-03 → WP-04 → WP-05 → WP-06 → WP-07 → WP-08 → WP-09 → WP-10 → WP-11 → WP-12

---

## Next Approved Work Package

**WP-02C: Customer Table Alignment**

- **Objective:** Align customers table with Customer schema
- **Files:** backend/app/core/database.py, backend/app/routers/customers.py
- **Risk:** High
- **Depends on:** WP-01

---

## Rules That Must Never Be Violated

1. **Source of Truth Order** (charter Section 3) - Never reverse: Pydantic Schemas -> API Contract -> Business Rules -> DB Schema -> Frontend Types -> Documentation
2. **Security Rules** (charter Section 12) - Never hardcode secrets, never trust client input, validate every request, hash passwords with approved algorithms, avoid wildcard CORS
3. **Architecture Cleanup First** (charter Section 16) - Minimize risk, preserve architecture
4. **One Logical Problem/Commit** (charter Section 17) - No mixed-purpose commits
5. **Quality Gates** (charter Section 18) - All must pass before completion

---

## Open Questions

| Question | Status |
|----------|--------|
| Should SQLite be replaced with PostgreSQL? | Answer: Yes (charter Section 9) |
| Is bcrypt<4.0 acceptable long-term? | Pending dependency review |
| Should services layer use repository pattern? | To decide during WP-08 |
| What test framework for integration? | Pending WP-06 planning |

---

*Memory Last Updated: WP-01, WP-02A, WP-02B complete, awaiting WP-02C approval.*
