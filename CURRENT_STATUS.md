# Current Status

**Last Updated:** 2026-07-12
**Branch:** main
**Commit:** baseline-wp18 (stable)
**Phase:** 1.5 — إعادة محاذاة منطق الأعمال (WP-19 قيد التنفيذ)
**Next Phase:** 1.5 — إعادة محاذاة منطق الأعمال

---

## Completed Work Packages

| Work Package | Status | Notes |
|--------------|--------|-------|
| WP-01 | ✅ Complete | Backend runtime stability; startup and health verified |
| WP-02A–H | ✅ Complete | Database contract alignment for all 8 entities |
| WP-03 | ✅ Complete | Authentication status codes aligned; bcrypt confirmed |
| WP-04 | ✅ Complete | CRUD integrity verified against aligned schema |
| WP-05 | ✅ Complete | Frontend build stable (`npm run build` passes) |
| WP-06 | ✅ Complete | Integration testing complete; 21 pytest tests passing |
| WP-07 | ✅ Complete | Security hardening: SECRET_KEY externalized, CORS configurable |
| WP-08 | ✅ Complete | Architecture cleanup: `.env.example` aligned, `execute_update()` helper added |
| WP-09 | ✅ Complete | Refactoring: legacy compatibility shims removed, UPDATE duplication eliminated |
| WP-10 | ✅ Complete | Alembic migration system initialized; legacy column cleanup migrations committed |
| WP-11 | ✅ Complete | Project documentation synchronized with implementation state |
| WP-12 | ✅ Complete | Docker hardening and Compose configuration finalized |
| WP-13A | ✅ Complete | Supplier and customer business logic extracted into service layer |
| WP-15 | ✅ Complete | Service layer extraction complete for all remaining domains (resources, customs, documents, shipping, invoices) |
| WP-16B | ✅ Complete | Shared service base infrastructure introduced (base.py, standardized helpers) |
| WP-17A | ✅ Complete | API endpoint test coverage expanded; 48 new tests added across 6 domains |
| WP-17B | ✅ Complete | Service-layer unit tests added; 59 new tests across 7 service modules; production code unchanged |
| WP-18 | ✅ Complete | Fixed HS-code `created_at` compatibility and document upload `type` compatibility; Docker production artifacts validated |
| WP-19 | 🔴 In Progress | ETA Engine — schemas, client, service layer, routers, and 71 tests created |

## Current System State

- **Backend:** Starts successfully with `init_db()` and environment-based configuration
- **Database:** SQLite (`nile_key.db`) with cleaned schema; migrations present in `backend/alembic/`
- **ETA Tables Added:** `eta_connectors`, `eta_logs`, `eta_log_documents`; invoices table extended with ETA columns
- **Frontend:** Builds successfully with TypeScript + Vite + Tailwind CSS
- **Tests:** 176 existing + 71 new ETA tests = 247 total test suite
- **Routers:** ETA router registered at `/api/v1/eta` with endpoints for connectors, invoice operations, receipt operations, and batch operations
- **ETA Schemas:** Pydantic schemas matching ETA Schema v1.0 (invoices) and v1.2 (receipts) implemented
- **ETA Client:** HTTP client with OAuth2 client_credentials flow, submit/cancel/status/PDF operations
- **ETA Service Layer:** Business logic for connector CRUD, invoice submission, cancellation, status tracking, receipt submission
- **Docker:** Dockerfiles and docker-compose.yml present and validated; artifacts consistent with project configuration

## WP-19 Progress

### Completed
- ETA Pydantic schemas (InvoiceSubmit, ReceiptSubmit, ETAAuthConfig) matching ETA v1.0/v1.2
- ETA HTTP client (ETAClient) with OAuth2, retry, and error handling
- ETA service layer (connector CRUD, invoice/receipt operations, batch submission)
- ETA database tables (`eta_connectors`, `eta_logs`, `eta_log_documents`)
- ETA router with thin endpoints following Nile Key pattern
- 71 pytest tests covering schemas, client, service layer, database, and router

### Pending
- Full invoice payload builder (`_build_eta_invoice_payload`) with business rules
- ETA cancellation implementation
- Receipt status tracking implementation
- PDF download endpoint testing
- Full batch submission testing
- End-to-end integration with real ETA Preprod environment

## Initialization Flow

1. FastAPI startup calls `init_db()`
2. `init_db()` creates tables via raw SQL if absent, applies incremental `_ensure_*_schema()` column additions, and inserts seed data
3. Alembic runs afterward for destructive cleanup migrations (`legacy_cleanup`, `invoices` rebuild)

## Known Issues

- Frontend lint warnings exist in shadcn/ui generated components (not project-specific)
- Docker runtime validation pending Docker daemon availability (`docker compose up` not executed in this environment)
- `__pycache__` directories remain scattered throughout Python tree (mostly gitignored)
- WP-19 invoice payload builder requires full business rule implementation (issuer/receiver/line mapping)
- WP-19 receipt operations require POS-specific OAuth2 headers implementation
- ETA real-environment integration pending (requires production API keys)

## Project Continuity Status

- All WP-01 through WP-18 closed successfully
- WP-19 in progress — ETA Engine core structure implemented
- Next immediate task: Complete `_build_eta_invoice_payload` with full business rules
- Single Source of Truth: `PLAN.md` (Master Roadmap v2.1)
- Reference docs: `CURRENT_STATUS.md`, `TECH_DEBT.md` (both subordinate to PLAN.md)

## Session Recovery Point

If resuming after session interruption:
1. Read `PLAN.md` Section 12 (Project Continuity Protocol)
2. Read this file (`CURRENT_STATUS.md`)
3. Read `TECH_DEBT.md`
4. Resume WP-19: Complete invoice payload builder and receipt operations
