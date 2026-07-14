# Current Status

**Last Updated:** 2026-07-14
**Branch:** main
**Commit:** 1bebd10 (feat(frontend): add vitest + RTL tests for Notifications and NotificationBell (M3-T8))
**Phase:** 1.5 — إعادة محاذاة منطق الأعمال (WP-19 + WP-20 + WP-21 M1-M3 مكتملة)
**Next Phase:** 2.0 — WP-21 Milestone 4: Export Operations Integration

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
| WP-19 | ✅ Complete | ETA Engine — full implementation with production-ready infrastructure |
| WP-20 | ✅ Complete | Shipping Engine — provider abstraction, LetMeShip + SendCloud clients, scheduler, 34+ tests |
| WP-21 M1 | ✅ Complete | Notification service + audit logging foundation; 52 tests |
| WP-21 M2 | ✅ Complete | Unified search + live dashboard; 10 tests |
| WP-21 M3 | ✅ Complete | Notification triggers + frontend integration; 34 tests (17 frontend + 17 backend triggers) |

## Current System State

- **Backend:** Starts successfully with `init_db()` and environment-based configuration
- **Database:** SQLite (`nile_key.db`) with cleaned schema; migrations present in `backend/alembic/`
- **ETA Tables Added:** `eta_connectors`, `eta_logs`, `eta_log_documents`; invoices table extended with ETA columns
- **Shipping Tables Added:** `shipping_providers`, `shipping_parcel_templates`, `shipping_labels`, `shipping_logs`, `contacts`, `addresses`; shipments table extended with shipping columns
- **Frontend:** Builds successfully with TypeScript + Vite + Tailwind CSS
- **Tests:** 373 passing, 8 skipped by design
- **Routers:** ETA router at `/api/v1/eta`; Shipping router at `/api/v1/shipping`; Search at `/api/v1/search`; Dashboard at `/api/v1/dashboard`; Notifications/Audit at `/api/v1/notifications` and `/api/v1/audit`
- **Shipping Schemas:** Pydantic schemas for RateRequest, CreateShipmentRequest, ShipmentResult, TrackingResponse, provider/template schemas
- **Shipping Clients:** LetMeShip + SendCloud HTTP clients with tenacity retry
- **Shipping Service Layer:** Complete business logic for rate aggregation, booking, labels, tracking, cancellation, provider/parcel-template CRUD
- **Shipping Scheduler:** APScheduler daily tracking poll job
- **Frontend Pages:** Dashboard (live widgets), Notifications (list with read/unread), NotificationBell component
- **Frontend Tests:** 17 Vitest + React Testing Library tests for Notifications and NotificationBell
- **Backend Notification Triggers:** ETA submit/receipt triggers + Shipping create/update triggers; 17 tests
- **Docker:** Dockerfiles and docker-compose.yml present and validated; artifacts consistent with project configuration

## WP-19 + WP-20 Implementation Summary

### WP-19: ETA Engine (Completed)
- **ETA Pydantic Schemas:** InvoiceSubmit (v1.0), ReceiptSubmit (v1.2), ETAAuthConfig
- **ETA HTTP Client (ETAClient):** OAuth2 with 3-minute token buffer, tenacity retry (3 attempts, exponential backoff), idempotency keys
- **Business Logic from Reference Repo:**
  - `eta_round` — tax rounding with 5 decimal places (from `utils.py`)
  - `eta_datetime_issued_format` — Cairo timezone → UTC conversion with Z suffix (from `utils.py`)
  - `delay_in_hours` logic in batch submission (from `main.py` get_batch_invoices)
  - `check_existing_eta_logs` — log existence check (from `main.py`)
  - Notification preparation functions (from `utils.py`)
- **Invoice Operations:** submit, cancel, status, PDF download
- **Receipt Operations:** submit e-receipts with POS-specific OAuth2 headers
- **Batch Operations:** batch submission with configurable batch size and delay
- **Status Polling:** scheduled polling for submitted invoices
- **Error Mapping:** user-friendly Arabic/English error messages
- **Idempotency:** daily idempotency keys and duplicate submission checks
- **Audit Logging:** `create_eta_log` and `update_eta_log_documents`
- **Database:** `eta_connectors`, `eta_logs`, `eta_log_documents` tables; invoices extended with ETA columns
- **Test Coverage:** 71 pytest tests (70 passing, 1 skipped by design)

### WP-20: Shipping Engine (Completed)
- **Shipping Pydantic Schemas:** RateRequest, ShippingRate, CreateShipmentRequest, ShipmentResult, TrackingResponse, provider/template schemas
- **Provider Abstraction:** Abstract `ShippingProvider` interface, registry, error hierarchy
- **LetMeShip Client:** Basic Auth, `/available`, `/shipments`, `/tracking`, `/documents` endpoints, tenacity retry
- **SendCloud Client:** API key/secret Basic Auth, `/v3/shipping-options`, `/v3/shipments/announce`, `/v2/labels`, `/v2/parcels`, `/v3/shipments/{id}/cancel`, tenacity retry
- **Business Logic:**
  - Rate aggregation across enabled providers with error isolation
  - Shipment booking with validation (phone E.164, address, parcel dimensions)
  - Label retrieval with filesystem storage + DB metadata
  - Tracking with provider status mapping to local state machine
  - Cancellation with provider rollback + local state update
- **Database:** `shipping_providers`, `shipping_parcel_templates`, `shipping_labels`, `shipping_logs`, `contacts`, `addresses` tables; shipments extended with shipping columns
- **Scheduler:** APScheduler daily tracking poll (`shipping_tracking_poll`)
- **Router:** Extended with provider CRUD, parcel template CRUD, cancel endpoint, POST `/rates`
- **Backward Compatibility:** Existing `app.services.shipping` imports preserved via shim
- **Secrets:** Loaded exclusively from environment variables (`LETME_API_ID`, `LETME_API_PASSWORD`, `SENDCLOUD_PUBLIC_KEY`, `SENDCLOUD_SECRET_KEY`)
- **Test Coverage:** 34 shipping-specific tests (9 router + 25 service), all passing

### Test Coverage
- 71 pytest tests (70 passing, 1 skipped by design) covering:
  - Schema validation (18 tests)
  - HTTP client with mocked httpx (8 tests)
  - Service layer (6 tests)
  - Database integration (4 tests)
  - Connector CRUD (6 tests)
  - Router structure (4 tests)
  - Integration lifecycle (1 test)
  - Additional schemas (13 tests)
  - Additional service tests (4 tests)
  - Additional router tests (2 tests)
  - Error handling (3 tests)
  - Receipt schemas (5 tests)
  - Additional database tests (3 tests)

## WP-21 Implementation Summary

### WP-21 Milestone 1: Foundation (Completed)
- **Notification Service:** SMTP email sending with template rendering
- **Audit Service:** Centralized audit logging with `log_audit()` and `list_audit_logs()`
- **Database:** `notification_templates`, `notification_logs`, `notification_preferences` tables; `audit_logs` extended
- **Integration:** Audit logging integrated into 8 services (customer, supplier, invoice, customs, document, resource, shipping, eta)
- **Routers:** `/api/v1/notifications/send`, `/api/v1/audit/logs`
- **Test Coverage:** 52 tests (notification service: 17, audit service: 14, notification router: 8, audit router: 13)

### WP-21 Milestone 2: Search + Dashboard (Completed)
- **Unified Search:** `/api/v1/search` endpoint aggregating results across all business entities
- **Live Dashboard:** `/api/v1/dashboard` endpoint with ETA + Shipping stats, recent activity, notification count
- **Frontend:** Dashboard page updated with live widgets
- **Test Coverage:** 10 tests (search service + dashboard service + router tests)

### WP-21 Milestone 3: Notification Triggers + Frontend (Completed)
- **ETA Notification Triggers:** `submit_invoice_to_eta` and `submit_receipt_to_eta` send template emails on success
- **Shipping Notification Triggers:** `create_shipment` and `update_shipment` send template emails on state changes
- **Notification Preferences:** Per-user opt-in/opt-out by notification type via `_is_notification_enabled()`
- **Frontend:** Notifications page with read/unread status, NotificationBell dropdown with unread count
- **Frontend API:** Updated `api.ts` with search, dashboard, notifications, audit endpoints
- **Frontend Tests:** 17 Vitest + React Testing Library tests
- **Backend Trigger Tests:** 17 tests verifying notification triggers in ETA and Shipping services
- **Test Coverage:** Full suite: 373 passed, 8 skipped, 0 failed

## Initialization Flow

1. FastAPI startup calls `init_db()`
2. `init_db()` creates tables via raw SQL if absent, applies incremental `_ensure_*_schema()` column additions, and inserts seed data
3. ETA scheduler initializes with APScheduler (hourly status polling + hourly batch submission)
4. Alembic runs afterward for destructive cleanup migrations

## Known Issues

- Frontend lint warnings exist in shadcn/ui generated components (not project-specific)
- Docker runtime validation pending Docker daemon availability (`docker compose up` not executed in this environment)
- `__pycache__` directories remain scattered throughout Python tree (mostly gitignored)

## Project Continuity Status

- All WP-01 through WP-18 closed successfully
- WP-19 completed — ETA Engine fully implemented with production-ready infrastructure
- WP-20 completed — Shipping Engine fully implemented with provider abstraction, LetMeShip + SendCloud clients, scheduler, and 34+ tests
- WP-21 M1-M3 completed — Notification service, audit logging, unified search, live dashboard, notification triggers, and frontend integration
- Next immediate task: WP-21 Milestone 4 (Export Operations Integration)
- Single Source of Truth: `PLAN.md` (Master Roadmap v2.1)
- Reference docs: `CURRENT_STATUS.md`, `TECH_DEBT.md` (both subordinate to PLAN.md)

## Session Recovery Point

If resuming after session interruption:
1. Read `PLAN.md` Section 12 (Project Continuity Protocol)
2. Read this file (`CURRENT_STATUS.md`)
3. Read `TECH_DEBT.md`
4. Resume WP-21: Platform Integration
