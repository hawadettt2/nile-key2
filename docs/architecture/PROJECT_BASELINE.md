# Project Baseline

**Generated:** 2026-07-12
**Branch:** main
**Latest commit:** d6ba84a (docs) + WP-19 working tree
**Working tree:** Includes WP-19 ETA Engine implementation
**Baseline:** baseline-wp19 (ready for approval)

---

## 1. Current Repository Status

- **Modified files:** `backend/app/core/database.py`, `backend/main.py`, `backend/requirements.txt`, `PLAN.md`, `CURRENT_STATUS.md`, `TECH_DEBT.md`, `docs/architecture/*.md`, plus documentation files
- **New WP-19 files:** `backend/app/schemas/eta.py`, `backend/app/services/eta/__init__.py`, `backend/app/services/eta/eta_client.py`, `backend/app/routers/eta.py`, `backend/app/core/eta_scheduler.py`, `backend/tests/test_eta.py`
- **Branch status:** Latest work on `origin/main`
- **Tag:** `baseline-wp18` exists; `baseline-wp19` ready for approval

## 2. Current Git Status

Project is tracked in Git with committed work through WP-17A. Working tree includes WP-17B service-layer unit tests.

## 3. Current Backend Startup Status

- **Entry point:** `backend/main.py`
- **Config:** `SECRET_KEY` required from environment
- **Database:** SQLite via raw `sqlite3` module
- **Security:** JWT + bcrypt
- **Import status:** All modules import cleanly
- **Startup blockers:** None detected

## 4. Current Frontend Build Status

- **Entry point:** `frontend/src/main.tsx`
- **Framework:** React 18 + TypeScript + Vite + Tailwind CSS
- **Build status:** `npm run build` passes
- **Lint:** 3 warnings/errors in shadcn/ui generated components (not project code)

## 5. Current Deployment Status

- **Containerization:** Dockerfiles present for backend and frontend; `docker-compose.yml` present
- **Environment:** `.env.example` aligned with `config.py`
- **Hosting targets:** Docker Compose, GitHub Pages, PythonAnywhere Free
- **Frontend API types:** Generated at `frontend/src/types/api.d.ts` (matches current API)

## 6. Known Critical Blockers

| Blocker | Status | Impact |
|---------|--------|--------|
| Database schema mismatch | ✅ Resolved (WP-02A-H complete) | N/A |
| Hardcoded SECRET_KEY | ✅ Resolved (WP-07 complete) | N/A |
| Wildcard CORS | ✅ Resolved (WP-07 complete) | N/A |
| Services layer | ✅ Resolved (WP-15/WP-16B complete) | N/A |
| HS-code created_at mismatch | ✅ Resolved (WP-18 complete) | N/A |
| Document upload type omission | ✅ Resolved (WP-18 complete) | N/A |
| Docker validation | ⏳ Static validation complete; runtime validation pending environment | Low |
| Email notifications | ⏳ Deferred to WP-21 (SMTP integration) | Low |

## 7. Existing Architectural Debt

| Debt | Location | PLAN.md Reference | Status |
|------|----------|-------------------|--------|
| Raw SQL everywhere | `database.py`, routers | Section 9.9 (Database Rules) | Accepted |
| No rate limiting | Missing | Section 4 (الأمان) | Open |
| PostgreSQL migration path | Not started | Section 9.9 (SQLite is implementation detail) | Open |
| Root `alembic.ini` exists | Project root | N/A | Low |
| `__pycache__` directories | Throughout Python tree | N/A | Low |

## 8. Source of Truth

Per PLAN.md Section 9.3, priority must never be reversed:

1. **Pydantic Schemas** (`backend/app/schemas/`) — ✅ Defined
2. FastAPI API Contract — ✅ Generated
3. Business Rules — ✅ In services layer
4. **Database Schema** — ✅ Aligned after WP-02 + WP-10
5. Frontend Types — ✅ Generated from OpenAPI
6. Documentation — ✅ Aligned after WP-11/WP-12/WP-16B

## 9. Approved Architecture Documents

- `PLAN.md` — **Master Roadmap v2.1 — Single Source of Truth (Constitution)**
- `CURRENT_STATUS.md` — Project state (subordinate to PLAN.md)
- `TECH_DEBT.md` — Technical debt register (subordinate to PLAN.md)
- `DEPLOYMENT.md` — Deployment guide (derived from PLAN.md)
- `docs/architecture/REPOSITORY_INTELLIGENCE.md` — Phase 1.5 Intelligence Report
- `docs/architecture/WORK_PACKAGE_PLAN.md` — Lifecycle-ordered Work Packages
- `docs/architecture/ENGINEERING_MEMORY.md` — Project state and decisions
- `docs/architecture/PROJECT_BASELINE.md` — This file
- `.kilo/plans/` — Kilo session plans
- `ARCHITECTURE_CHARTER.md` — **Deprecated** — Content merged into PLAN.md; no independent authority

## 10. Success Criteria for Project Completion

Per PLAN.md Section 10.8 Quality Gates:

- [x] Backend builds and starts
- [x] Frontend builds
- [x] Core routes work
- [x] Authentication works
- [x] No broken imports
- [x] No circular dependencies
- [x] No hidden runtime errors
- [x] All WP-19 deliverables complete

Additional criteria:
- [x] Database schema matches Pydantic schemas
- [x] No hardcoded secrets
- [x] CORS restricts to configured origins
- [x] Services layer implemented
- [x] Code duplication eliminated
- [x] Migrations available (WP-10)
- [x] Docker deployment artifacts present (WP-12)
- [x] ETA Engine implemented (WP-19) — 71 tests (70 passing, 1 skipped by design)
