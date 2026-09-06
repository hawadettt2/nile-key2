# Technical Debt

**Last Updated:** 2026-09-05
**Branch:** main
**Phase:** 3 — Phase 3 Readiness (WP-ORM-001 CLOSED)
**Authority:** PLAN.md (Master Roadmap v2.1) — Single Source of Truth

---
## Active Technical Debt

| Priority | Debt | Location | Notes |
|----------|------|----------|-------|
| MEDIUM | Rate limiting — auth endpoints only | `backend/app/routers/auth.py`, `main.py` | Implemented on auth endpoints via `slowapi`; non-auth endpoint coverage is a separate design decision |
| LOW | Root `alembic.ini` exists | Project root | Real config is `backend/alembic.ini`; root copy is stale/untracked |
| LOW | `__pycache__` directories | Throughout Python tree | Mostly gitignored, but scattered `__pycache__` dirs remain |
| LOW | Email notifications | `backend/app/services/eta/__init__.py` | Notification preparation functions ready; SMTP integration deferred to WP-21 |
| LOW | Production CORS origins | `backend/main.py` | `ALLOWED_ORIGINS` configurable via settings; production origins (`nile-key.com`) to be set before deployment |
| LOW | Shipping backward-compat alias complexity | `app/services/shipping/__init__.py` | Shim pattern resolves circular imports; can be simplified after full migration to new package |

| LOW | Engineering Decision formalization | `app/services/workflow.py` | `draft ? shipped` bypass approved via CR-M4-001 Rev.1; optional business requirement formalization pending |

| LOW | Email notifications operational | ackend/app/services/notification.py | SMTP code implemented; notification audit logging added in M5-R2 |
| LOW | Dashboard live data | rontend/src/pages/Dashboard.tsx | Auto-refresh polling added in M5-R1 |
| MEDIUM | Workflow state validation bypass | ackend/app/services/workflow.py | update_workflow() now validates transitions in M5-R3 |
| MEDIUM | Search missing RBAC | ackend/app/routers/search.py | 
equire_role() added in M5-R4 |
| MEDIUM | .env.example missing variables | ackend/.env.example | OWNER_PASSWORD and SMTP vars added in M5-R5 |
| LOW | Notification audit logging missing | ackend/app/services/notification.py | udit_logs + 
otification_logs integration added in M5-R2 |
| MEDIUM | Router ? main coupling | `backend/app/routers/digital_export_manager.py` ? `main.py` | `get_reasoning_engine()` deferred import; accepted as architectural coupling; monitored |
| LOW | Module-level application state | `trade_intelligence.py`, `knowledge_graph.py`, `agent.py`, `research.py`, `eta_scheduler.py`, `shipping_scheduler.py` | Controlled initialization in `main.py` lifespan; accepted as controlled application state; no immediate action |
| MEDIUM | Shallow health endpoints | `backend/app/routers/agent.py`, `backend/app/routers/digital_export_manager.py` | Health endpoints return hardcoded `healthy` without verifying DB/schedulers/external services; accepted as controlled technical debt; deferred to Phase 4/Audit C2 |
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
| Docker deployment validation | Both images build successfully; `docker compose up --build` verified with healthy services; database persistence confirmed via Docker volume | WP-18 |
| ETA Engine missing | Full ETA Engine implemented: schemas, client, service layer, router, scheduler, 71 tests (70 passing, 1 skipped by design) | WP-19 |
| ETA retry strategy | Added tenacity retry with exponential backoff (3 attempts) to ETAClient | WP-19 |
| ETA idempotency | Implemented idempotency keys and duplicate submission checks | WP-19 |
| ETA error mapping | Implemented user-friendly error message mapping | WP-19 |
| ETA status polling | Implemented `poll_pending_invoice_statuses` for scheduled status updates | WP-19 |
| ETA audit logging | Implemented `create_eta_log` and `update_eta_log_documents` | WP-19 |
| ETA datetime conversion | Implemented `eta_datetime_issued_format` with Cairo timezone ? UTC conversion | WP-19 |
| ETA tax rounding | Implemented `eta_round` with 5 decimal places precision | WP-19 |
| ETA batch delay logic | Implemented `delay_in_hours` logic in `submit_pending_batch` | WP-19 |
| ETA APScheduler | Integrated APScheduler with hourly status polling and batch submission jobs | WP-19 |
| POS receipt building | Receipt schemas (`ReceiptSubmit`, `ReceiptHeader`, `ReceiptSeller`, `ReceiptBuyer`, `SingleItemData`, `SingleTaxableItems`, `SingleTaxTotal`) implemented in `backend/app/schemas/eta.py`; POS receipt builder `submit_receipt_to_eta()` implemented in `backend/app/services/eta/__init__.py` | WP-19 |
| Shipping engine missing | Full Shipping Engine implemented: schemas, provider abstraction, LetMeShip + SendCloud clients, service layer, router, scheduler, 34+ tests | WP-20 |
| Shipping retry strategy | Added tenacity retry with exponential backoff (3 attempts) to provider clients | WP-20 |
| Shipping audit logging | Implemented `shipping_logs` table for provider API call audit trail | WP-20 |
| Shipping state machine | Implemented 7-state shipment state machine (pending, booked, in_transit, delivered, returned, lost, cancelled) | WP-20 |
| Shipping contacts/addresses | Implemented dedicated `contacts` and `addresses` tables | WP-20 |
| Shipping scheduler | Integrated APScheduler with daily tracking poll job | WP-20 |
| Raw SQL everywhere | Introduced `DatabaseSession`, `SchemaRegistry`, `MigrationRunner`; migrated `supplier.py` to ORM abstraction layer; PostgreSQL migration path prepared | WP-ORM-001 |
| PostgreSQL migration path | `MigrationRunner` and schema registry introduced; PostgreSQL readiness path established without migration | WP-ORM-001 |
| Delivery confirmation capability missing | Implemented `delivery_confirmed` business event in `shipping_logs`, atomic workflow link via `export_workflows.delivery_confirmed_at`, duplicate prevention, history API, 16 shipping tests + 14 workflow regression tests; no new tables, no PostgreSQL migration | WP-DEM-002 |
