# Engineering Memory

**Last Updated:** 2026-07-12
**Project:** Nile Key Platform
**Authority:** `PLAN.md` (Master Roadmap v2.1) — Single Source of Truth

| WP | Status | Commit | Notes |
|----|--------|--------|-------|
| WP-01A | ✅ Complete | 3597c67 | Unicode emoji fix in main.py lifespan for Windows compatibility |
| WP-01B | ✅ Complete | d036c06 (recovery) | Reverted to bcrypt, installed bcrypt<4.0 for passport compatibility |
| WP-02A | ✅ Complete | a0e87e7 | Added username, phone, company, updated_at columns to users table; fixed auth.py column reference |
| WP-02B | ✅ Complete | 94ae639 | Added suppliers schema + response compatibility + role case fixes |
| WP-02C | ✅ Complete | 5cec3ca | Added customers schema + response compatibility layer with legacy fallbacks |
| WP-02D | ✅ Complete | 547aa13 | Added shipments schema + response compatibility layer (ADR-0001) |
| WP-02D | ✅ Complete | 3219904 | Added invoices schema + response compatibility layer |
| WP-02F | ✅ Complete | 3219904 | Added customs_declarations schema + response compatibility layer |
| WP-02G | ✅ Complete | 3219904 | Added resources schema + response compatibility layer |
| WP-02H | ✅ Complete | 3219904 | Added documents schema + response compatibility layer |
| WP-03 | ✅ Complete | dbe1ef4 | Aligned OAuth2 status codes: 401 for missing auth, 403 for missing role |
| WP-04 | ✅ Complete | - | All CRUD operations verified working against aligned schema |
| WP-02-Infra | ✅ Complete | 98838d1 | Added ensure_columns() helper for reusable schema migrations |
| Doc-01 | ✅ Complete | 9a1682d | Established ENGINEERING_MEMORY.md, WORK_PACKAGE_PLAN.md, PROJECT_BASELINE.md, REPOSITORY_INTELLIGENCE.md, ARCHITECTURE_CHARTER.md |
| WP-05 | ✅ Complete | - | Frontend builds successfully |
| WP-06 | ✅ Complete | - | Integration testing complete; 21 pytest tests pass |
| WP-07 | ✅ Complete | - | SECRET_KEY externalized, CORS configuration replaced with settings.ALLOWED_ORIGINS |
| WP-08 | ✅ Complete | - | .env.example aligned with config.py; execute_update() helper added |
| WP-09 | ✅ Complete | - | Extracted execute_update() helper; integrated into 8 routers; ~120 lines removed |
| WP-10 | ✅ Complete | 56fc391 | Alembic migrations initialized; legacy column cleanup committed; invoices.uuid removed |
| WP-11 | ✅ Complete | 08a9924 | Synchronize project documentation with current implementation |
| WP-12 | ✅ Complete | 54f7c49 | Harden Docker deployment and finalize Compose configuration |
| WP-13A | ✅ Complete | c66087e / 3351a4d | Extract supplier and customer business logic into service layer |
| WP-14 | ⏳ Integrated | — | Combined into WP-15 |
| WP-15 | ✅ Complete | 1d545b1 | Complete service layer extraction for resources, customs, documents, shipping, invoices |
| WP-16A | ⏳ Integrated | — | Executed as part of WP-15/WP-16B verification |
| WP-16B | ✅ Complete | b4ff64f | Introduce shared service base infrastructure (base.py, standardized helpers) |
| WP-17A | ✅ Complete | cdb8bb9 | Expand API endpoint coverage: 48 new tests across 6 domains |
| WP-17B | ✅ Complete | working tree | Add service-layer unit tests: 59 new tests across 7 modules; production code unchanged |
| WP-18 | ✅ Complete | working tree | Fix HS-code `created_at` schema mismatch; fix document upload `type` omission; validate Docker production artifacts |
| WP-19 | ✅ Complete | working tree | ETA Engine: schemas, client, service layer, router, scheduler, 71 tests (70 passing, 1 skipped); business logic extracted from erpnext_egypt_compliance |

---

## Completed Commits

| Hash | Message | Date |
|------|---------|------|
| b4ff64f | refactor: introduce shared service base infrastructure (WP-16B) | 2026-07-05 |
| 1d545b1 | refactor: complete service layer extraction (WP-15) | 2026-07-05 |
| 3351a4d | WP-13A: Extract customer business logic into service layer | 2026-07-05 |
| c66087e | WP-13A: Extract supplier business logic into service layer | 2026-07-05 |
| 54f7c49 | WP-12: Harden Docker deployment and finalize Compose configuration | 2026-07-05 |
| 08a9924 | WP-11: Synchronize project documentation with current implementation | 2026-07-05 |
| 56fc391 | WP-10: Repair Alembic migration history for invoices schema | 2026-07-04 |
| 87267d3 | refactor: align app-layer schema and router mappers with cleaned database structure | 2026-07-04 |
| dede827 | WP-09: Consolidate SQL UPDATE operations into execute_update helper | 2026-07-03 |
| 0465c6a | WP-08: Align architecture configuration and verify services layer | 2026-07-03 |
| 6710251 | WP-07: Complete typed API response models and stabilize backend | 2026-07-03 |
| 287de2f | test(suppliers): add suppliers router test suite | 2026-07-03 |
| 0ef8c0b | test(auth): add authenticated auth endpoint tests | 2026-07-03 |
| e52d674 | test(auth): add registration and login smoke tests | 2026-07-03 |
| 3e6fcc8 | test(backend): add pytest infrastructure and health smoke test | 2026-07-03 |
| a83228b | feat(frontend): profile, CRUD updates, detail views, token refresh | 2026-07-02 |
| cfd84bc | WP-11 Patch-2: Add Docker Compose orchestration | 2026-07-02 |
| dbe1ef4 | WP-03: Align authentication status codes with OAuth2 standard | 2026-06-30 |

---

## Important Architectural Decisions

1. **SQLite is implementation detail** (per PLAN.md Section 9.9) - will change to PostgreSQL in production
2. **Pydantic schemas are Source of Truth** - database must follow schemas (PLAN.md Section 9.3)
3. **bcrypt is required password algorithm** - passlib[bcrypt] in requirements.txt
4. **No business logic in routers** (PLAN.md Section 9.10) - must move to services layer
5. **Code duplication prohibited** (PLAN.md Section 9.8) - execute_update() extracted in WP-09
6. **Legacy Compatibility Policy** - Legacy columns are excluded from API responses, not used as fallbacks
7. **ADR-0001: Shipments Legacy Columns** - Legacy columns are NOT fallback pairs; excluded entirely from API contract. See docs/architecture/ADR-0001-shipments-legacy-columns.md
8. **Database initialization flow** - `init_db()` creates/maintains schema; Alembic handles destructive post-init cleanup

---

## WP-10 Migration System

### Database Initialization Flow

1. FastAPI startup calls `init_db()`
2. `init_db()` creates tables from scratch via raw SQL
3. `init_db()` applies incremental column additions via `_ensure_*_schema()`
4. `init_db()` inserts seed data
5. Alembic migrations run afterward for destructive schema cleanup

### Alembic Chain

- `9f6e6d58ca0f_initial` — empty revision chain start
- `0f82a20f2bb7_legacy_cleanup` — drops legacy columns via SQLite-safe patterns
- `bdab744e83e3_legacy_cleanup_fix` — rebuilds `invoices` without `uuid` for SQLite safety

### Key Migration Notes

- Initial migration is empty because `init_db()` owns schema creation
- Migrations are destructive cleanup only
- Non-SQLite backends use standard `op.drop_column()` / `op.add_column()`

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
| backend/app/core/database.py | Added get_db(), ensure_columns(), execute_update() | Required by router code and WP-02/09 |
| backend/app/models/__init__.py | Removed imports / added SQLAlchemy target_metadata | Was causing ImportError; supports Alembic autogenerate |
| backend/app/routers/*.py | Removed legacy compatibility filters | Legacy columns removed from schema in WP-10 |

All recovery changes: **KEEP** (syntactically valid, functionally safe)

---

## Known Risks

| Risk Level | Issue | Status |
|------------|-------|--------|
| 🔴 CRITICAL | Database schema mismatch | ✅ WP-02A-H complete - all entities aligned |
| 🟡 MEDIUM | Docker deployment unvalidated | ✅ RESOLVED — Both images build successfully; `docker compose up --build` verified with healthy services; database persistence confirmed via Docker volume |
| 🟢 LOW | Manual frontend types | ✅ Automatically generated types match API |

---

## Current Project Status

| Component | Status |
|-----------|--------|
| Backend | ✅ Starts; health endpoint healthy |
| Frontend | ✅ Builds (`npm run build` passes) |
| Tests | ✅ 267 pytest tests collected (259 passing, 8 skipped by design) |
| Alembic | ✅ Migration chain functional |
| Docker | ✅ Present; static validation complete in WP-18 |
| Services layer | ✅ Implemented (7 domains + ETA with shared base.py) |
| ETA Engine | ✅ Implemented (WP-19) |
| APScheduler | ✅ Integrated (hourly polling + batch submission) |

---

*Memory Last Updated: WP-19 verified - 267 tests collected (259 passing, 8 skipped), ETA Engine implemented with production-ready infrastructure. Final Acceptance Gate remediation complete.*
