# Technical Debt

**Last Updated:** 2026-07-04
**Branch:** wp-13

---

## Active Technical Debt

| Priority | Debt | Location | Notes |
|----------|------|----------|-------|
| HIGH | Empty services layer | `backend/app/services/__init__.py` | Charter Section 10 violation; business logic lives in routers |
| HIGH | Business logic in routers | All 8 router files | Hard to unit-test; violates charter preferred architecture |
| HIGH | Documentation drift | Multiple docs | Baseline, engineering memory, README, and deployment docs are stale |
| MEDIUM | Raw SQL everywhere | `database.py`, all routers | No ORM abstraction; schema changes require coordinated manual updates |
| MEDIUM | Manual frontend types | `frontend/src/types/api.d.ts` | Charter prefers OpenAPI-generated frontend types |
| MEDIUM | Docker deployment unverified | Dockerfiles, `docker-compose.yml` | `docker compose up` not yet validated |
| MEDIUM | No rate limiting | Missing entirely | Listed in PLAN.md as required but not implemented |
| MEDIUM | PostgreSQL migration path | Not started | Charter Section 9 notes SQLite is an implementation detail |
| LOW | Root `alembic.ini` exists | Project root | Real config is `backend/alembic.ini`; root copy is stale/untracked |
| LOW | `__pycache__` directories | Throughout Python tree | Mostly gitignored, but scattered `__pycache__` dirs remain |

## Resolved Technical Debt

| Debt | Resolution | Work Package |
|------|------------|--------------|
| Schema-database mismatch | `_create_tables()` and `_ensure_*_schema()` aligned | WP-02A–H |
| Hardcoded SECRET_KEY | Externalized to environment; fails fast when missing | WP-07 |
| Wildcard CORS default | Reads from `ALLOWED_ORIGINS` | WP-07 |
| Code duplication in UPDATE helpers | `execute_update()` extracted and integrated into 8 routers | WP-09 |
| Legacy column filtering in routers | Compatibility shims removed; response mapping simplified | WP-09, post-WP-10 |
| Missing Alembic migration system | Alembic initialized; migration chain present | WP-10 |
| Legacy `invoices.uuid` column | SQLite-safe table rebuild migration removes it | WP-10 |
| `.env.example` drift | Aligned with `config.py` variables and formats | WP-08 |
