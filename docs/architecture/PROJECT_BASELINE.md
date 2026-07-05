# Project Baseline

**Generated:** 2026-07-05
**Branch:** wp-13
**Latest commit:** b4ff64f refactor: introduce shared service base infrastructure (WP-16B)

---

## 1. Current Repository Status

- **Modified files:** Working tree clean
- **Untracked files:** None relevant
- **Branch status:** Latest work pushed to `origin/wp-13`
- **Tag:** `baseline-wp16b` points to current HEAD

## 2. Current Git Status

Project is tracked in Git with committed work through WP-16B.

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
| Docker validation local | ⏳ Pending environment | Deployment risk |

## 7. Existing Architectural Debt

| Debt | Location | Charter Violation | Status |
|------|----------|-------------------|--------|
| Raw SQL everywhere | `database.py`, routers | Maintainability | Accepted |
| No rate limiting | Missing | PLAN.md requirement | Open |
| PostgreSQL migration path | Not started | Charter Section 9 notes SQLite is implementation detail | Open |
| Root `alembic.ini` exists | Project root | N/A | Low |
| `__pycache__` directories | Throughout Python tree | N/A | Low |

## 8. Source of Truth

Per ARCHITECTURE_CHARTER.md Section 3, priority must never be reversed:

1. **Pydantic Schemas** (`backend/app/schemas/`) — ✅ Defined
2. FastAPI API Contract — ✅ Generated
3. Business Rules — ✅ In services layer
4. **Database Schema** — ✅ Aligned after WP-02 + WP-10
5. Frontend Types — ✅ Generated from OpenAPI
6. Documentation — ✅ Aligned after WP-11/WP-12/WP-16B

## 9. Approved Architecture Documents

- `ARCHITECTURE_CHARTER.md` — Official Engineering Constitution
- `docs/architecture/REPOSITORY_INTELLIGENCE.md` — Phase 1.5 Intelligence Report
- `docs/architecture/WORK_PACKAGE_PLAN.md` — Lifecycle-ordered Work Packages
- `docs/architecture/ENGINEERING_MEMORY.md` — Project state and decisions
- `docs/architecture/PROJECT_BASELINE.md` — This file
- `.kilo/plans/` — Kilo session plans

## 10. Success Criteria for Project Completion

Per ARCHITECTURE_CHARTER.md Section 18 Quality Gates:

- [x] Backend builds and starts
- [x] Frontend builds
- [x] Core routes work
- [x] Authentication works
- [x] No broken imports
- [x] No circular dependencies
- [x] No hidden runtime errors
- [x] All WP-16B deliverables complete

Additional criteria:
- [x] Database schema matches Pydantic schemas
- [x] No hardcoded secrets
- [x] CORS restricts to configured origins
- [x] Services layer implemented
- [x] Code duplication eliminated
- [x] Migrations available (WP-10)
- [x] Docker deployment artifacts present (WP-12)
