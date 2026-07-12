# Technical Debt

**Last Updated:** 2026-07-12
**Branch:** main
**Phase:** 1.5 — ETA Engine In Progress

---

## Active Technical Debt

| Priority | Debt | Location | Notes |
|----------|------|----------|-------|
| HIGH | Documentation drift | Multiple docs | Resolved in WP-17A/WP-17B |
| MEDIUM | Raw SQL everywhere | `database.py`, all routers | No ORM abstraction; schema changes require coordinated manual updates |
| MEDIUM | Docker deployment unverified | Dockerfiles, `docker-compose.yml` | Static validation complete; runtime validation pending Docker daemon availability |
| MEDIUM | No rate limiting | Missing entirely | Listed in PLAN.md as required but not implemented |
| MEDIUM | PostgreSQL migration path | Not started | PLAN.md Section 9.9 notes SQLite is implementation detail |
| MEDIUM | ETA invoice payload builder incomplete | `backend/app/services/eta/__init__.py` | `_build_eta_invoice_payload` raises NotImplementedError; requires full issuer/receiver/line mapping |
| MEDIUM | ETA cancellation not implemented | `backend/app/services/eta/__init__.py` | `cancel_eta_invoice` raises NotImplementedError |
| MEDIUM | Receipt status tracking not implemented | `backend/app/services/eta/__init__.py` | `get_eta_invoice_status` and receipt status tracking raise NotImplementedError |
| MEDIUM | PDF download not implemented | `backend/app/services/eta/__init__.py` | `download_eta_pdf` raises NotImplementedError |
| MEDIUM | Batch submission not implemented | `backend/app/services/eta/__init__.py` | `submit_pending_batch` raises NotImplementedError |
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
| Empty services layer | Service modules implemented for all 7 non-auth domains with shared base infrastructure | WP-15, WP-16B |
| Business logic in routers | Migrated to service layer; routers now thin | WP-13A, WP-15 |
| Manual frontend types | Generated types via `openapi-typescript`; verified to match API | WP-12 |
| Customs HS-code created_at mismatch | Added `created_at` to `_ensure_hs_codes_schema()` with backfill | WP-18 |
| Document upload type omission | Fixed `upload_document()` INSERT to populate required `type` column | WP-18 |
| Docker deployment validation | Docker artifacts reviewed and validated against project configuration | WP-18 |
