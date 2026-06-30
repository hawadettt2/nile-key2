# Engineering Memory

**Last Updated:** 2026-06-30
**Project:** Nile Key Platform
**Architecture Charter:** Governing document (must not be violated)

| WP | Status | Commit | Notes |
|----|--------|--------|-------|
| WP-01A | ✅ Complete | 3597c67 | Unicode emoji fix in main.py lifespan for Windows compatibility |
| WP-01B | ✅ Complete | d036c06 (recovery) | Reverted to bcrypt, installed bcrypt<4.0 for passlib compatibility |
| WP-02A | ✅ Complete | a0e87e7 | Added username, phone, company, updated_at columns to users table; fixed auth.py column reference |
| WP-02B | ✅ Complete | 94ae639 | Added suppliers schema + response compatibility + role case fixes |
| WP-02C | ✅ Complete | 5cec3ca | Added customers schema + response compatibility layer with legacy fallbacks |
| WP-02D | ✅ Complete | 547aa13 | Added shipments schema + response compatibility layer (ADR-0001) |
| WP-02E | ✅ Complete | 3219904 | Added invoices schema + response compatibility layer |
| WP-02F | ✅ Complete | 3219904 | Added customs_declarations schema + response compatibility layer |
| WP-02G | ✅ Complete | 3219904 | Added resources schema + response compatibility layer |
| WP-02H | ✅ Complete | 3219904 | Added documents schema + response compatibility layer |
| WP-03 | ✅ Complete | dbe1ef4 | Aligned OAuth2 status codes: 401 for missing auth, 403 for missing role |
| WP-02-Infra | ✅ Complete | 98838d1 | Added ensure_columns() helper for reusable schema migrations |
| Doc-01 | ✅ Complete | 9a1682d | Established ENGINEERING_MEMORY.md, WORK_PACKAGE_PLAN.md, PROJECT_BASELINE.md, REPOSITORY_INTELLIGENCE.md, ARCHITECTURE_CHARTER.md |

---

## Completed Commits

| Hash | Message | Date |
|------|---------|------|
| dbe1ef4 | WP-03: Align authentication status codes with OAuth2 standard | 2026-06-30 |
| 48e6e46 | chore(frontend): track npm package-lock.json | 2026-06-30 |
| b6510ab | Cleanup: Remove superseded .kilo/plans documentation | 2026-06-30 |
| 155b040 | WP-02: Finalize resources.py compatibility layer fix and completion report | 2026-06-30 |
| 5cec3ca | WP-02C: Align customers schema with backend contract + response compatibility | 2026-06-30 |
| 94ae639 | WP-02B: Add suppliers response compatibility + role case fixes | 2026-06-30 |
| 547aa13 | WP-02D: Align shipments schema + response compatibility | 2026-06-30 |
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
7. **ADR-0001: Shipments Legacy Columns** - Legacy columns are NOT fallback pairs; they are excluded entirely from API contract. Pydantic schema is authoritative. See docs/architecture/ADR-0001-shipments-legacy-columns.md

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
| 🔴 CRITICAL | Database schema mismatch | ✅ WP-02A-H complete - all entities aligned |
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
| Suppliers table schema | ✅ Complete (WP-02B) |
| Customers table schema | ✅ Complete (WP-02C) |
| Shipments table schema | ✅ Complete (WP-02D) |
| Invoices table schema | ✅ Complete (WP-02E) |
| Customs table schema | ✅ Complete (WP-02F) |
| Resources table schema | ✅ Complete (WP-02G) |
| Documents table schema | ✅ Complete (WP-02H) |
| Frontend build | ⚠️ Not verified |
| Docker | ❌ Not available |
| Tests | ❌ None |

---

## WP-02 Decomposition Status

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
| WP-02G-Correction | ✅ Complete | resources - fixed is_active fallback logic |

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
| Response compatibility | ✅ Legacy columns (type, farm_code, governorate, products, rating) filtered from API responses |
| Role compatibility | ✅ Role case fixed (Owner->owner, Manager->manager, Sales->sales) |

---

## WP-02C Verification Results

| Test | Result |
|------|--------|
| Fresh DB init | ✅ Success - all columns present |
| Existing DB upgrade | ✅ Success - columns added, data preserved |
| Backend startup | ✅ Healthy (port 8001) |
| Login works | ✅ Token returned |
| Customer CRUD | ✅ Create, Read, Update work |
| Legacy columns excluded | ✅ No `company_name`/`contact_name` in API responses |
| Fallback logic | ✅ `name` ← `company_name` when NULL, `contact_person` ← `contact_name` when NULL |

---

## WP-02D Verification Results

| Test | Result |
|------|--------|
| Fresh DB init | ✅ Success - all schema columns present |
| Existing DB upgrade | ✅ Success - columns added, data preserved |
| Backend startup | ✅ Healthy (port 8001) |
| Login works | ✅ Token returned |
| Shipment CRUD | ✅ Create, Read, Update work |
| Legacy columns excluded | ✅ No `service_name`, `label_url`, `cost`, `provider`, `pickup_address`, `delivery_address`, `parcels`, `raw_response` in API responses |
| ADR-0001 applied | ✅ Legacy columns are not fallback pairs, fully excluded |

---

## Remaining Work Packages

WP-03 → WP-04 → WP-05 → WP-06 → WP-07 → WP-08 → WP-09 → WP-10 → WP-11 → WP-12

---

*Memory Last Updated: WP-02A-H complete. All entities now aligned.*

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