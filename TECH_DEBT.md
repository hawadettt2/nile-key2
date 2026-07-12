# Technical Debt

**Last Updated:** 2026-07-12
**Branch:** main
**Phase:** 1.5 — ETA Engine Complete ✅

---

## Active Technical Debt

| Priority | Debt | Location | Notes |
|----------|------|----------|-------|
| MEDIUM | Raw SQL everywhere | `database.py`, all routers | No ORM abstraction; schema changes require coordinated manual updates |
| MEDIUM | Docker deployment unverified | Dockerfiles, `docker-compose.yml` | Static validation complete; runtime validation pending Docker daemon availability |
| MEDIUM | No rate limiting | Missing entirely | Listed in PLAN.md as required but not implemented |
| MEDIUM | PostgreSQL migration path | Not started | PLAN.md Section 9.9 notes SQLite is implementation detail |
| LOW | Root `alembic.ini` exists | Project root | Real config is `backend/alembic.ini`; root copy is stale/untracked |
| LOW | `__pycache__` directories | Throughout Python tree | Mostly gitignored, but scattered `__pycache__` dirs remain |
| LOW | Email notifications | `backend/app/services/eta/__init__.py` | Notification preparation functions ready; SMTP integration deferred to WP-21 |
| LOW | POS receipt building | `backend/app/schemas/eta.py` | Receipt schemas ready; full POS receipt builder deferred to WP-21 |
| LOW | Production CORS origins | `backend/main.py` | `ALLOWED_ORIGINS` configurable via settings; production origins (`nile-key.com`) to be set before deployment |

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
| ETA Engine missing | Full ETA Engine implemented: schemas, client, service layer, router, scheduler, 71 tests (70 passing, 1 skipped by design) | WP-19 |
| ETA retry strategy | Added tenacity retry with exponential backoff (3 attempts) to ETAClient | WP-19 |
| ETA idempotency | Implemented idempotency keys and duplicate submission checks | WP-19 |
| ETA error mapping | Implemented user-friendly error message mapping | WP-19 |
| ETA status polling | Implemented `poll_pending_invoice_statuses` for scheduled status updates | WP-19 |
| ETA audit logging | Implemented `create_eta_log` and `update_eta_log_documents` | WP-19 |
| ETA datetime conversion | Implemented `eta_datetime_issued_format` with Cairo timezone → UTC conversion | WP-19 |
| ETA tax rounding | Implemented `eta_round` with 5 decimal places precision | WP-19 |
| ETA batch delay logic | Implemented `delay_in_hours` logic in `submit_pending_batch` | WP-19 |
| ETA APScheduler | Integrated APScheduler with hourly status polling and batch submission jobs | WP-19 |
