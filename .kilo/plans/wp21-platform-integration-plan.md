# WP-21 — Platform Integration Implementation Plan

**Reference:** PLAN.md (Master Roadmap v2.1)  
**Phase:** 1.5 — Business Logic Re-alignment  
**Status:** Ready for Implementation  
**Date:** 2026-07-13

---

## 1. Executive Summary

WP-21 transforms Nile Key from a collection of independent domain engines into an integrated export platform. It connects the ETA Engine (WP-19), Shipping Engine (WP-20), and existing Nile Key domains (customers, suppliers, customs, documents, resources) through four cross-cutting capabilities:

1. **Unified Search** — single entry point across all business entities
2. **Live Dashboard** — real-time operational visibility from ETA + Shipping
3. **Audit Logging** — tamper-evident compliance trail for all operations
4. **Email Notifications** — SMTP-based alerts for business events

**Core principle:** Integration must not break existing domain boundaries. Each domain remains independently testable and deployable. WP-21 adds cross-cutting infrastructure, not domain logic.

---

## 1.1 Forensic Validation Summary

This plan is based on a complete forensic audit of the existing project state. Below is the verified baseline:

| Component | Count | Status |
|-----------|-------|--------|
| Existing Database Tables | 20 | ✅ Stable |
| Existing Services | 12 | ✅ Stable |
| Existing Routers | 9 | ✅ Stable |
| Existing Schemas | 11 modules | ✅ Stable |
| Existing Frontend Pages | 9 routes | ✅ Stable |
| ETA Engine | Complete | ✅ Reusable |
| Shipping Engine | Complete | ✅ Reusable |
| Auth/RBAC | Complete | ✅ Reusable |
| Notification Service | 0 | ❌ Must be created |
| Audit Service | 0 | ❌ Must be created |
| Search Service | 0 | ❌ Must be created |
| Dashboard Service | 0 | ❌ Must be created |
| Workflow Service | 0 | ❌ Must be created |
| Notification Tables | 0 | ❌ Must be created |
| Workflow Tables | 0 | ❌ Must be created |
| Audit Tables | 1 (`audit_logs`) | ⚠️ Exists but unused |

**Forensic Conclusion:** WP-21 is architecturally compatible, but requires creating 5 new services, 5 new routers, 5 new schema modules, 5 new database tables, and significant frontend work from scratch. Only the ETA/Shipping engines, domain services, and auth system are reusable. The `audit_logs` table exists but is empty and must be extended with new columns and an active logging service.

---

## 2. Requirements Analysis

### 2.1 Objectives

| # | Objective |
|---|-----------|
| 1 | Connect all business entities through shared search, audit, and notification infrastructure |
| 2 | Provide live dashboard visibility into ETA and Shipping operations |
| 3 | Implement email notifications for business-critical events |
| 4 | Ensure complete audit trail for compliance and operational tracking |
| 5 | Enable unified search across all entities without breaking existing domain boundaries |

### 2.2 Scope

**IN SCOPE:**
- Unified search API across all entities (suppliers, customers, shipments, invoices, customs declarations, resources, ETA logs, shipping logs)
- Dashboard data aggregation endpoints for live stats
- Audit log service + centralized audit trail
- SMTP email notification service with template support
- Frontend notifications UI component
- Extend `audit_logs` table with additional columns (`ip_address`, `user_agent`, `session_id`)
- Create new database tables: `notification_templates`, `notification_logs`, `notification_preferences`, `export_workflows`, `export_workflow_items`
- Frontend search UI component

**OUT OF SCOPE:**
- Changes to existing domain service logic (ETA, Shipping, Customs, etc.)
- POS receipt building (deferred to WP-21 per TECH_DEBT.md — requires POS integration)
- AI/ML features (WP-30+)
- PostgreSQL migration (WP-40+)
- Rate limiting (listed in PLAN.md but not in WP-21 scope)
- WebSocket real-time updates (future consideration)

### 2.3 Deliverables

| Deliverable | Description |
|-------------|-------------|
| `app/services/notification.py` | **Create New** — SMTP email service with template rendering |
| `app/services/search.py` | **Create New** — Unified search service aggregating across entities |
| `app/services/audit.py` | **Create New** — Centralized audit logging service |
| `app/schemas/notification.py` | **Create New** — Pydantic schemas for notifications |
| `app/schemas/search.py` | **Create New** — Pydantic schemas for search requests/responses |
| `app/schemas/audit.py` | **Create New** — Pydantic schemas for audit entries |
| `app/routers/notifications.py` | **Create New** — Notification CRUD + send endpoints |
| `app/routers/search.py` | **Create New** — Global search endpoint |
| `app/routers/audit.py` | **Create New** — Audit log query endpoints |
| `app/routers/dashboard.py` | **Create New** — Dashboard stats aggregation endpoints |
| `backend/app/core/database.py` extensions | **Create New** notification/workflow tables + **Extend** `audit_logs` with new columns |
| Frontend: Dashboard updates | Live ETA/Shipping data widgets |
| Frontend: Notifications page | Notification list + settings |
| Tests: New test suite | Unit + service + router + integration + regression |

---

## 3. Functional Requirements

### 3.1 Unified Search

| Requirement | Description |
|-------------|-------------|
| FR-SEARCH-1 | Global search endpoint accepts query string and optional entity filters |
| FR-SEARCH-2 | Searches across: suppliers, customers, shipments, invoices, customs declarations, resources, ETA logs, shipping logs |
| FR-SEARCH-3 | Returns ranked results with entity type, relevance score, and deep link |
| FR-SEARCH-4 | Supports pagination (limit/offset) |
| FR-SEARCH-5 | Respects user role permissions (users only see entities they have access to) |
| FR-SEARCH-6 | Minimum query length: 2 characters |
| FR-SEARCH-7 | Maximum results per entity: 20 |

### 3.2 Live Dashboard

| Requirement | Description |
|-------------|-------------|
| FR-DASH-1 | Dashboard returns aggregated stats: total suppliers, customers, shipments, invoices, customs declarations |
| FR-DASH-2 | Dashboard returns ETA-specific stats: pending submissions, submitted, signed, cancelled, failed |
| FR-DASH-3 | Dashboard returns Shipping-specific stats: pending bookings, booked, in_transit, delivered, returned, lost, cancelled |
| FR-DASH-4 | Dashboard returns recent activity timeline (last 10 cross-entity events) |
| FR-DASH-5 | Dashboard returns notification count for current user |
| FR-DASH-6 | All stats are computed in real-time from database (no cache) |
| FR-DASH-7 | Dashboard endpoint is cached for 60 seconds (server-side) |

### 3.3 Audit Logging

| Requirement | Description |
|-------------|-------------|
| FR-AUDIT-1 | All CRUD operations on business entities log to `audit_logs` |
| FR-AUDIT-2 | Authentication events log to `audit_logs` (login, logout, refresh, failed attempts) |
| FR-AUDIT-3 | ETA and Shipping operations continue logging to their domain-specific tables (`eta_logs`, `shipping_logs`) |
| FR-AUDIT-4 | Audit entries include: user_id, action, entity_type, entity_id, details (JSON), timestamp |
| FR-AUDIT-5 | Audit log is append-only (no UPDATE/DELETE allowed) |
| FR-AUDIT-6 | Audit log query endpoints support filtering by user, entity_type, date range |
| FR-AUDIT-7 | Audit log returns paginated results |

### 3.4 Email Notifications

| Requirement | Description |
|-------------|-------------|
| FR-NOTIF-1 | System sends email for: ETA invoice submitted, ETA invoice signed, ETA invoice failed, Shipment booked, Shipment delivered, Shipment cancelled |
| FR-NOTIF-2 | Recipients determined by business rules: invoice notifications → supplier/owner; shipment notifications → customer/owner |
| FR-NOTIF-3 | Email templates stored in database (`notification_templates` table) |
| FR-NOTIF-4 | Templates support variable substitution (e.g., `{invoice_number}`, `{tracking_number}`) |
| FR-NOTIF-5 | Notification service is asynchronous (background task or queue) |
| FR-NOTIF-6 | Failed emails are logged with error details for retry/manual intervention |
| FR-NOTIF-7 | Notification preferences can be configured per user (opt-in/opt-out by type) |
| FR-NOTIF-8 | SMTP configuration loaded from environment variables only |

### 3.5 Export Operations Integration

| Requirement | Description |
|-------------|-------------|
| FR-EXPORT-1 | Export workflow connects: Customer → Invoice → Customs Declaration → Shipping |
| FR-EXPORT-2 | System can generate export summary document linking all related entities |
| FR-EXPORT-3 | Export status tracked per workflow instance |

---

## 4. Non-Functional Requirements

| Requirement | Description |
|-------------|-------------|
| NFR-1 | All new endpoints follow existing FastAPI patterns (thin routers, service layer, Pydantic validation) |
| NFR-2 | No breaking changes to existing API contracts |
| NFR-3 | Database schema changes use `_ensure_*_schema()` incremental approach (no destructive migrations in WP-21) |
| NFR-4 | Secrets loaded from environment variables only (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`) |
| NFR-5 | Email sending is non-blocking (async or background) |
| NFR-6 | Search response time < 500ms for queries with results |
| NFR-7 | Dashboard response time < 1000ms |
| NFR-8 | Audit log writes are synchronous but batched where possible |
| NFR-9 | Frontend follows existing TypeScript + Vite + Tailwind patterns |
| NFR-10 | All new code passes existing lint/typecheck standards |

---

## 5. Architecture Review

### 5.1 Current Architecture Compatibility

**Verdict: NO ARCHITECTURAL CHANGES REQUIRED**

WP-21 fits cleanly into the existing architecture:

| Aspect | Current State | WP-21 Impact |
|--------|---------------|--------------|
| Layering | Thin routers → service layer → database | New services follow same pattern |
| Schemas | Pydantic v2 with `field_validator` | New schemas use same patterns |
| Database | Raw SQL with `_ensure_*_schema()` | New tables added via same mechanism; `audit_logs` extended with new columns |
| Schedulers | APScheduler for ETA + Shipping | Notification sending may use scheduler for batch digests |
| Auth | JWT with role-based access | New endpoints use same `get_current_user` + `require_role` |
| Error handling | Custom exceptions per domain | New `NotificationError`, `SearchError` follow same pattern |
| Logging | Python `logging` module | Same pattern for new services |

### 5.2 Proposed New Modules

```
backend/app/
├── services/
│   ├── notification.py          # NEW — SMTP service
│   ├── search.py                # NEW — unified search
│   ├── audit.py                 # NEW — audit logging service
│   ├── dashboard.py             # NEW — dashboard aggregation service
│   └── existing modules...
├── schemas/
│   ├── notification.py          # NEW — notification schemas
│   ├── search.py                # NEW — search schemas
│   ├── audit.py                 # NEW — audit schemas
│   ├── dashboard.py             # NEW — dashboard schemas
│   └── existing schemas...
├── routers/
│   ├── notifications.py         # NEW — notification endpoints
│   ├── search.py                # NEW — search endpoints
│   ├── audit.py                 # NEW — audit endpoints
│   ├── dashboard.py             # NEW — dashboard endpoints
│   └── existing routers...
└── core/
    └── database.py              # MODIFIED — new tables
```

### 5.3 ADR Recommendation

**ADR-WP21-001: Notification Transport**

**Context:** Need to send email notifications for ETA and Shipping events.

**Decision:** Use SMTP with `aiosmtplib` for async email sending. Store templates in database. Render with Jinja2-style string formatting.

**Impact:** 
- Adds new dependency: `aiosmtplib`
- Requires SMTP environment variables
- Non-blocking: emails sent in background

**Alternatives considered:**
- Webhook-based notifications (rejected: requires external endpoint)
- In-app notifications only (rejected: PLAN.md explicitly requires email)
- Third-party service (SendGrid, etc.) (rejected: adds external dependency cost)

---

## 6. Dependency Analysis

### 6.1 Prerequisites

| Work Package | Status | Relevance |
|--------------|--------|-----------|
| WP-19 (ETA Engine) | ✅ Complete | ETA events trigger notifications; ETA data feeds dashboard |
| WP-20 (Shipping Engine) | ✅ Complete | Shipping events trigger notifications; Shipping data feeds dashboard |

### 6.2 Reused Modules

| Module | Reuse Pattern |
|--------|---------------|
| `app/core/database.py` | Extend with new tables via `_ensure_*_schema()` |
| `app/core/config.py` | Add SMTP configuration fields |
| `app/services/base.py` | Reuse utilities (`connection()`, `build_list_query()`, `now_iso()`) |
| `app/schemas/*.py` | Follow existing Pydantic patterns |
| `app/routers/*.py` | Follow existing thin-router pattern |
| Frontend `api.ts` | Add new API functions |
| Frontend `Dashboard.tsx` | Extend with new widgets |

### 6.3 New Modules Required

| Module | Purpose |
|--------|---------|
| `app/services/notification.py` | SMTP email sending with template rendering |
| `app/services/search.py` | Unified search aggregation |
| `app/services/audit.py` | Centralized audit logging |
| `app/schemas/notification.py` | Notification request/response schemas |
| `app/schemas/search.py` | Search request/response schemas |
| `app/schemas/audit.py` | Audit log schemas |
| `app/routers/notifications.py` | Notification endpoints |
| `app/routers/search.py` | **Create New** — Global search endpoint |
| `app/routers/audit.py` | Audit log endpoints |
| `app/services/dashboard.py` | Dashboard stats aggregation |
| `app/services/workflow.py` | Export workflow lifecycle management |
| `app/schemas/dashboard.py` | Dashboard stats schemas |
| `app/schemas/workflow.py` | Export workflow schemas |
| `app/routers/workflow.py` | Export workflow endpoints |
| `app/routers/dashboard.py` | Dashboard aggregation endpoints |

---

## 7. Implementation Breakdown

### Milestone 1: Foundation (Notification Service + Audit Logging)

| Task ID | Description | Complexity | Dependencies | Expected Output |
|---------|-------------|------------|--------------|-----------------|
| M1-T1 | Add SMTP config to `app/core/config.py` | Low | None | `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`, `SMTP_USE_TLS` |
| M1-T2 | Create `app/schemas/notification.py` | Low | None | `NotificationTemplate`, `NotificationSend`, `NotificationResponse` schemas |
| M1-T3 | Create `app/services/notification.py` | Medium | M1-T1, M1-T2 | SMTP service with template rendering, async send |
| M1-T4 | Add `notification_templates` table to `database.py` | Low | None | Table with id, name, subject, body, variables, is_active |
| M1-T5 | Create `app/routers/notifications.py` | Medium | M1-T3 | CRUD for templates, send endpoint |
| M1-T6 | Create `app/schemas/audit.py` | Low | None | `AuditLogCreate`, `AuditLogResponse` schemas |
| M1-T7 | Extend `audit_logs` table with additional fields | Low | None | `ip_address`, `user_agent`, `session_id` |
| M1-T8 | Create `app/services/audit.py` | Low | M1-T6 | `log_audit()` helper with context enrichment |
| M1-T9 | Integrate audit logging into existing services (ETA, Shipping, Customs, etc.) | Medium | M1-T8 | All CRUD operations log to `audit_logs` |
| M1-T10 | Create `app/routers/audit.py` | Medium | M1-T8 | Query audit logs with filters |
| M1-T11 | Write tests for notification service + audit service | High | M1-T3, M1-T8 | 20+ tests |

### Milestone 2: Search + Dashboard

| Task ID | Description | Complexity | Dependencies | Expected Output |
|---------|-------------|------------|--------------|-----------------|
| M2-T1 | Create `app/schemas/search.py` | Low | None | `SearchRequest`, `SearchResponse`, `SearchResult` schemas |
| M2-T2 | Create `app/services/search.py` | High | M2-T1 | Unified search aggregating across all entities with ranking |
| M2-T3 | Create `app/routers/search.py` | Medium | M2-T2 | `/api/v1/search` endpoint with filters |
| M2-T4 | Create `app/schemas/dashboard.py` | Low | None | `DashboardStats`, `DashboardTimeline`, `DashboardResponse` schemas |
| M2-T5 | Create `app/services/dashboard.py` | Medium | M2-T4 | Stats aggregation, timeline generation, notification count |
| M2-T6 | Create `app/routers/dashboard.py` | Medium | M2-T5 | `/api/v1/dashboard` endpoint with aggregated stats |
| M2-T7 | Write tests for search + dashboard | High | M2-T2, M2-T6 | Coverage for all search and dashboard functions |

### Milestone 3: Notification Triggers + Frontend

| Task ID | Description | Complexity | Dependencies | Expected Output |
|---------|-------------|------------|--------------|-----------------|
| M3-T1 | Integrate notification triggers into ETA service | Medium | M1-T3 | ETA events send notifications |
| M3-T2 | Integrate notification triggers into Shipping service | Medium | M1-T3 | Shipping events send notifications |
| M3-T3 | Add `notification_preferences` table | Low | None | Per-user opt-in/opt-out by notification type |
| M3-T4 | Update frontend `api.ts` with new endpoints | Low | None | New API functions for search, dashboard, notifications, audit |
| M3-T5 | Update frontend `Dashboard.tsx` with live widgets | Medium | M3-T4 | ETA/Shipping stats, recent activity, notification count |
| M3-T6 | Create frontend Notifications page | Medium | M3-T4 | Notification list with read/unread status |
| M3-T7 | Add notification bell to layout | Low | M3-T6 | Icon with unread count dropdown |
| M3-T8 | Write frontend tests for new components | Medium | M3-T5, M3-T6 | Component tests |

## 7.1 File Inventory

### New Files

| Category | Files | Count |
|----------|-------|-------|
| Backend Services | 
`notification.py`, `search.py`, `audit.py`, `dashboard.py`, `workflow.py` | 5 |
| Backend Schemas | 
`notification.py`, `search.py`, `audit.py`, `dashboard.py`, `workflow.py` | 5 |
| Backend Routers | 
`notifications.py`, `search.py`, `audit.py`, `dashboard.py`, `workflow.py` | 5 |
| Backend Tests | `test_notification_service.py`, `test_search_service.py`, `test_audit_service.py`, `test_dashboard_service.py`, `test_workflow_service.py`, `test_notifications.py`, `test_search.py`, `test_audit.py`, `test_dashboard.py`, `test_workflow.py`, `test_integration/test_wp21_integration.py` | 11 |
| Frontend | Notification page, Notification Bell component, Search page/component (filenames TBD) | 3 |
| **Total New Files** | | **29** |

### Modified Files

| Category | Files | Count |
|----------|-------|-------|
| Backend Core | config.py, database.py | 2 |
| Backend Services | customer.py, supplier.py, invoice.py, customs.py, document.py, 
resource.py, shipping/__init__.py, eta/__init__.py | 8 |
| Frontend | `api.ts`, `Dashboard.tsx`, App.tsx | 3 |
| Documentation | PLAN.md, CURRENT_STATUS.md, TECH_DEBT.md | 3 |
| **Total Modified Files** | | **16** |

> **Note:** `backend/app/routers/__init__.py` and `backend/app/services/__init__.py` may need updates depending on whether they are used for module aggregation. Verify whether updates are required during implementation.

### Milestone 4: Export Operations Integration

| Task ID | Description | Complexity | Dependencies | Expected Output |
|---------|-------------|------------|--------------|-----------------|
| M4-T1 | Define export workflow state machine | Medium | None | States: draft → customs_ready → shipped → delivered |
| M4-T2 | Create `export_workflows` table | Low | None | Table for tracking export workflow instances |
| M4-T3 | Create `app/services/workflow.py` | High | M4-T2 | Service to manage export workflow lifecycle |
| M4-T4 | Create export workflow router | Medium | M4-T3 | CRUD endpoints for export workflows |
| M4-T5 | Create export summary document generator | Medium | M4-T3 | PDF or JSON export of all related entities |
| M4-T6 | Write tests for export workflow | High | M4-T3 | 15+ tests |

### Milestone 5: Polish + Integration Testing

| Task ID | Description | Complexity | Dependencies | Expected Output |
|---------|-------------|------------|--------------|-----------------|
| M5-T1 | Register new routers in `backend/main.py` | Low | All M1-M4 | All new routers accessible under /api/v1 |
| M5-T2 | End-to-end integration tests | High | All M1-M4 | Tests covering full user workflows |
| M5-T3 | Performance testing for search | Medium | M2-T2 | Search < 500ms with 10k records |
| M5-T4 | Security review | Medium | All M1-M4 | Verify auth, input validation, rate limiting |
| M5-T5 | Documentation updates | Low | All M1-M4 | Update PLAN.md, CURRENT_STATUS.md, TECH_DEBT.md |
| M5-T6 | Final acceptance gate | Low | All M1-M5 | Sign-off on all acceptance criteria |

---

## 8. Database Changes

### 8.1 New Tables

| Table | Purpose | Source |
|-------|---------|--------|
| `notification_templates` | Email templates with subject, body, variables | Engineering Decision — required by FR-NOTIF-3 |
| `notification_logs` | Sent notification history | Engineering Decision — required by FR-NOTIF-6 |
| `notification_preferences` | Per-user notification preferences | Engineering Decision — required by FR-NOTIF-7 |
| `export_workflows` | Export workflow instances | Engineering Decision — required by FR-EXPORT-1 |
| `export_workflow_items` | Items linked to export workflows | Engineering Decision — required by FR-EXPORT-1 |

### 8.2 Extended Tables

| Table | New Columns | Source |
|-------|-------------|--------|
| `audit_logs` | `ip_address`, `user_agent`, `session_id` | Derived Requirement — §15.2 criterion 3 |

### 8.3 Migration Strategy

All changes use `_ensure_*_schema()` incremental approach. No destructive migrations. Alembic reserved for Phase 3+.

---

## 9. API Requirements

### 9.1 New Endpoints

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/v1/search` | Global search across all entities | `get_current_user` |
| GET | `/api/v1/dashboard` | Aggregated dashboard stats | `get_current_user` |
| GET | `/api/v1/audit/logs` | Query audit logs | `require_role(["owner", "manager", "admin_staff"])` |
| GET | `/api/v1/notifications` | List user notifications | `get_current_user` |
| POST | `/api/v1/notifications/send` | Send notification (admin) | `require_role(["owner", "admin_staff"])` |
| GET | `/api/v1/notifications/templates` | List notification templates | `require_role(["owner", "admin_staff"])` |
| POST | `/api/v1/notifications/templates` | Create notification template | `require_role(["owner", "admin_staff"])` |
| PUT | `/api/v1/notifications/templates/{id}` | Update notification template | `require_role(["owner", "admin_staff"])` |
| DELETE | `/api/v1/notifications/templates/{id}` | Delete notification template | `require_role(["owner"])` |
| GET | `/api/v1/export-workflows` | List export workflows | `get_current_user` |
| POST | `/api/v1/export-workflows` | Create export workflow | `get_current_user` |
| GET | `/api/v1/export-workflows/{id}` | Get export workflow | `get_current_user` |
| PUT | `/api/v1/export-workflows/{id}` | Update export workflow | `get_current_user` |
| POST | `/api/v1/export-workflows/{id}/submit` | Submit export workflow | `get_current_user` |
| GET | `/api/v1/export-workflows/{id}/summary` | Generate export summary | `get_current_user` |

### 9.2 Modified Endpoints

| Endpoint | Modification |
|----------|--------------|
| All CRUD endpoints | Add audit logging via `audit.log_audit()` |
| ETA submit/cancel/status | Trigger notifications on state changes |
| Shipping create/cancel/track | Trigger notifications on state changes |

---

## 10. UI Requirements

### 10.1 Dashboard Updates

| Component | Description | Status |
|-----------|-------------|--------|
| ETA Stats Widget | Pending, submitted, signed, failed invoice counts | **Create New** |
| Shipping Stats Widget | Pending, booked, in_transit, delivered shipment counts | **Create New** |
| Recent Activity Timeline | Last 10 cross-entity events with timestamps | **Create New** |
| Notification Bell | Unread notification count with dropdown | **Create New** |

### 10.2 Notifications Page

| Component | Description | Status |
|-----------|-------------|--------|
| Notification List | Paginated list with read/unread status | **Create New** |
| Notification Settings | Per-type opt-in/opt-out preferences | **Create New** |
| Template Management | Admin-only CRUD for email templates | **Create New** |

> **Note:** Frontend component and page filenames for notifications and search are **to be determined after repository verification**.

### 10.3 Search

| Component | Description | Status |
|-----------|-------------|--------|
| Global Search Bar | Top navigation search with entity type filters | **Create New** |
| Search Results Page | Grouped by entity type with deep links | **Create New** |

> **Note:** Frontend component and page filenames for search are **to be determined after repository verification**.

---

## 11. Security Requirements

| Requirement | Description |
|-------------|-------------|
| SEC-1 | SMTP credentials loaded from environment variables only |
| SEC-2 | Notification send endpoints restricted to owner/admin_staff roles |
| SEC-3 | Audit log query restricted to owner/manager/admin_staff roles |
| SEC-4 | Search results filtered by user role permissions |
| SEC-5 | No sensitive data exposed in search results |
| SEC-6 | Email templates sanitized against injection |
| SEC-7 | Rate limiting applied to search endpoint (existing slowapi) |
| SEC-8 | CORS and CSRF protection unchanged |

---

## 12. Performance Considerations

| Consideration | Strategy |
|---------------|----------|
| Search performance | Full-table scan acceptable for MVP; add FTS5 if needed |
| Dashboard aggregation | Simple COUNT queries; add caching layer if >1s |
| Notification sending | Async via `asyncio.create_task` or APScheduler batch job |
| Audit logging | Synchronous writes to SQLite; acceptable for current load |
| Email delivery | Non-blocking; failures logged for retry |

---

## 13. Business Rules

| Rule | Description |
|------|-------------|
| BR-NOTIF-1 | ETA invoice submitted → notify supplier/owner |
| BR-NOTIF-2 | ETA invoice signed → notify supplier |
| BR-NOTIF-3 | ETA invoice failed → notify owner + supplier |
| BR-NOTIF-4 | Shipment booked → notify customer |
| BR-NOTIF-5 | Shipment delivered → notify customer + owner |
| BR-NOTIF-6 | Shipment cancelled → notify customer + owner |
| BR-AUDIT-1 | All authentication events logged |
| BR-AUDIT-2 | All state transitions on business entities logged |
| BR-SEARCH-1 | Search respects role-based access control |
| BR-EXPORT-1 | Export workflow requires linked customer, invoice, and shipping |

---

## 14. Validation Rules

| Rule | Description |
|------|-------------|
| VR-SEARCH-1 | Query minimum length: 2 characters |
| VR-SEARCH-2 | Maximum results per entity: 20 |
| VR-NOTIF-1 | Email addresses validated against RFC 5322 |
| VR-NOTIF-2 | Template variables must be alphanumeric + underscore |
| VR-AUDIT-1 | entity_type must be one of: user, supplier, customer, shipment, invoice, customs_declaration, document, resource, eta_log, shipping_log |
| VR-DASH-1 | Dashboard date range limited to last 90 days for timeline |

---

## 15. Error Handling

| Error | HTTP Status | User Message |
|-------|-------------|--------------|
| Search query too short | 400 | "Query must be at least 2 characters" |
| SMTP connection failed | 500 | "Email service temporarily unavailable" |
| Template not found | 404 | "Notification template not found" |
| Audit log access denied | 403 | "Insufficient permissions" |
| Export workflow not found | 404 | "Export workflow not found" |

---

## 16. Logging Requirements

| Component | Log Level | Format |
|-----------|-----------|--------|
| Notification service | INFO (sent), ERROR (failed) | JSON with template_id, recipient, status |
| Search service | DEBUG (queries) | Standard Python logging |
| Audit service | INFO (all events) | Structured JSON |
| Dashboard | INFO | Aggregated stats |

---

## 17. Audit Requirements

| Requirement | Description |
|-------------|-------------|
| AR-1 | All authentication events logged to `audit_logs` |
| AR-2 | All CRUD on business entities logged to `audit_logs` |
| AR-3 | Domain-specific logs (`eta_logs`, `shipping_logs`) retained alongside `audit_logs` |
| AR-4 | Audit logs are immutable (no UPDATE/DELETE) |
| AR-5 | Audit logs queryable by admin/owner roles only |
| AR-6 | Retention: indefinite (compliance requirement) |

---

## 18. Testing Strategy

### 18.1 Coverage Requirements

| Area | Requirement |
|------|-------------|
| New services | Unit tests covering all public methods, error paths, and edge cases |
| New routers | Integration tests covering auth, validation, response format, and error handling |
| New schemas | Validation tests for required fields, field validators, and edge cases |
| Notification triggers | E2E tests verifying ETA and Shipping events enqueue notifications |
| Export workflows | E2E tests covering state transitions and summary generation |
| Frontend components | Component tests for new pages and UI elements |
| Regression | All existing backend and frontend tests must continue to pass |

### 18.2 Performance Targets

| Test | Target |
|------|--------|
| Search with 10k records | < 500ms |
| Dashboard aggregation | < 1000ms |
| Notification send (async) | < 5s including SMTP handshake |

## 19. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| SMTP provider reliability | Medium | High | Use retry with backoff; log failures for manual retry |
| Search performance with large datasets | Medium | Medium | Add FTS5 if simple LIKE queries become slow |
| Notification spam / rate limiting | Low | Medium | Implement per-user cooldown and digest options |
| Audit log table growth | Medium | Low | Partition by month if table exceeds 1M rows |
| Frontend dashboard re-render performance | Low | Medium | Use React memo and virtualization for large lists |
| Breaking changes to existing API | Low | High | All changes additive; no endpoint modifications |
| Email template injection | Low | High | Sanitize template variables; use safe string formatting |

---

## 20. Acceptance Criteria

WP-21 is considered complete when ALL of the following are true:

### 20.1 Functional Acceptance

- [ ] Unified search returns results from at least 7 entity types
- [ ] Dashboard displays live stats from ETA and Shipping engines
- [ ] Audit log captures all CRUD operations across all domains
- [ ] Email notifications are sent for all defined business events
- [ ] Export workflow links Customer → Invoice → Customs → Shipping
- [ ] No mock data in active routes

### 20.2 Technical Acceptance

- [ ] All new tests pass (sufficient coverage to verify all acceptance criteria)
- [ ] All existing tests still pass (no regressions)
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] No new critical TECH_DEBT.md items introduced
- [ ] All secrets loaded from environment variables
- [ ] No hardcoded credentials or API keys

### 20.3 Documentation Acceptance

- [ ] PLAN.md updated with WP-21 completion status
- [ ] CURRENT_STATUS.md updated
- [ ] TECH_DEBT.md updated with any new debt + resolution plan
- [ ] API documentation (OpenAPI) reflects new endpoints

### 20.4 Security Acceptance

- [ ] SMTP credentials externalized
- [ ] Notification endpoints role-protected
- [ ] Audit log endpoints restricted to admin roles
- [ ] Search results filtered by permissions
- [ ] No sensitive data in logs or error messages

---

## 21. Open Questions

| # | Question | Owner | Status |
|---|----------|-------|--------|
| 1 | Which SMTP provider should be used for production? | Owner | Open — needs business decision |
| 2 | Should notifications support SMS in addition to email? | Owner | Open — PLAN.md mentions "البريد الإلكتروني" only |
| 3 | What is the retention policy for notification_logs? | Owner | Open — compliance question |
| 4 | Should search support fuzzy matching / transliteration for Arabic? | Technical | Open — MVP uses LIKE; FTS5 later |
| 5 | Should export workflows support multi-currency? | Technical | Open — depends on invoice currency handling |

---

## 22. Readiness Assessment

### 22.1 Prerequisites Check

| Prerequisite | Status |
|--------------|--------|
| WP-19 (ETA Engine) | ✅ Complete |
| WP-20 (Shipping Engine) | ✅ Complete |
| Existing domain services | ✅ Complete |
| Database schema | ✅ Ready for extension (audit_logs extended, 5 new tables to be created) |
| Frontend build | ✅ Stable (requires extensions for WP-21) |

### 22.2 Architecture Compatibility

**WP-21 is FULLY COMPATIBLE with current architecture.** No architectural changes required. New modules follow existing patterns:
- Thin routers → service layer → database
- Pydantic v2 schemas with `field_validator`
- Raw SQL with `_ensure_*_schema()` incremental approach
- Context-managed SQLite connections
- Existing auth/role system for access control

### 22.3 Risk Level

**LOW-MEDIUM.** WP-21 adds cross-cutting infrastructure without modifying existing domain logic. Primary risks are:
- SMTP provider selection and reliability (mitigated by async + retry)
- Search performance (mitigated by simple LIKE for MVP, FTS5 path forward)
- Notification spam (mitigated by user preferences + cooldown)

### 22.4 Recommendation

**WP-21 is READY to enter the implementation phase.**

All requirements are clearly defined. Prerequisites are met. Architecture is compatible. No blocking open questions — the 5 open questions are either business decisions (Q1, Q2, Q3) or technical enhancements for later phases (Q4, Q5).

**Next step:** Begin Milestone 1 (Notification Service + Audit Logging).

---

## 23. Rollback Strategy

All changes are additive and follow Git-based rollback principles aligned with PLAN.md §18 Git Policies.

### Per-Task Rollback

| Change Type | Rollback Method |
|-------------|-----------------|
| New files | git rm <file> after reverting dependent commits |
| Modified files | git revert <commit> |
| Database schema | _ensure_*_schema() is idempotent; new tables/columns can remain or be manually removed |
| Frontend changes | git revert <commit> |

### Recommended Workflow

1. After each task, commit changes with message format: eat(wp21): M1-T3 - Create notification service
2. If a task introduces issues, use git revert <commit> to undo
3. For database-only changes, verify _ensure_*_schema() idempotency before proceeding
4. Frontend route and component additions should be committed together to avoid broken UI states

### Rollback Points

| Milestone | Rollback Command |
|-----------|-----------------|
| M1 complete | git revert --no-commit <M1-last-commit>..HEAD or milestone-specific revert |
| M2 complete | Revert M2 commits, keeping M1 |
| M3 complete | Revert M3 commits, keeping M1-M2 |
| M4 complete | Revert M4 commits, keeping M1-M3 |
| M5 complete | Full revert to pre-WP-21 state if required |

---

## 24. Evidence Appendix

### 23.1 Existing Database Tables

| Table | Purpose | Reusable | Notes |
|-------|---------|----------|-------|
| `users` | User accounts | Yes | Core auth table |
| `roles` | Role definitions | Yes | 8 roles seeded |
| `suppliers` | Supplier records | Yes | Domain table |
| `customers` | Customer records | Yes | Domain table |
| `shipments` | Shipment records | Yes | Extended by WP-20 |
| `invoices` | Invoice records | Yes | Extended by WP-19 |
| `eta_connectors` | ETA API connectors | Yes | WP-19 |
| `eta_logs` | ETA operation logs | Yes | WP-19 |
| `eta_log_documents` | ETA document details | Yes | WP-19 |
| `customs_declarations` | Customs declarations | Yes | Domain table |
| `hs_codes` | HS code master | Yes | Domain table |
| `documents` | Document records | Yes | Domain table |
| `resources` | Resource links | Yes | Domain table |
| `shipping_providers` | Shipping provider config | Yes | WP-20 |
| `shipping_parcel_templates` | Parcel templates | Yes | WP-20 |
| `shipping_labels` | Shipping label metadata | Yes | WP-20 |
| `shipping_logs` | Shipping operation logs | Yes | WP-20 |
| `contacts` | Contact records | Yes | WP-20 |
| `addresses` | Address records | Yes | WP-20 |
| `audit_logs` | Audit trail | Extend | Exists but empty; needs columns + active logging |

### 23.2 Existing Services

| Service | Responsibility | Reusable | Notes |
|---------|----------------|----------|-------|
| `base.py` | DB utilities, JSON helpers | Yes | `connection()`, `build_list_query()`, `now_iso()` |
| `customer.py` | Customer CRUD | Yes | Add audit logging |
| `supplier.py` | Supplier CRUD | Yes | Add audit logging |
| `invoice.py` | Invoice CRUD + ETA ops | Yes | Add audit logging + notification triggers |
| `customs.py` | HS codes, declarations | Yes | Add audit logging |
| `document.py` | Document CRUD | Yes | Add audit logging |
| `resource.py` | Resource CRUD + search | Yes | Add audit logging |
| `shipping/__init__.py` | Shipping orchestrator | Yes | Add notification triggers |
| `eta/__init__.py` | ETA operations | Yes | Contains notification stubs; replace with real SMTP |
| `shipping/base.py` | Provider abstraction | Yes | WP-20 |
| `shipping/letmeship_client.py` | LetMeShip HTTP client | Yes | WP-20 |
| `shipping/sendcloud_client.py` | SendCloud HTTP client | Yes | WP-20 |

### 23.3 Existing Routers

| Router | Prefix | Reusable | Notes |
|--------|--------|----------|-------|
| `auth.py` | `/api/v1/auth` | Yes | JWT, RBAC, rate limiting |
| `shipping.py` | `/api/v1/shipping` | Yes | WP-20 |
| `invoice.py` | `/api/v1/invoices` | Yes | Add audit logging |
| `suppliers.py` | `/api/v1/suppliers` | Yes | Add audit logging |
| `customers.py` | `/api/v1/customers` | Yes | Add audit logging |
| `customs.py` | `/api/v1/customs` | Yes | Add audit logging |
| `resources.py` | `/api/v1/resources` | Yes | Add audit logging |
| `documents.py` | `/api/v1/documents` | Yes | Add audit logging |
| `eta.py` | `/api/v1/eta` | Yes | Add audit logging + notification triggers |

### 23.4 Existing Schemas

| Schema | Module | Reusable | Notes |
|--------|--------|----------|-------|
| `MessageResponse` | `common.py` | Yes | Generic response |
| `IdResponse` | `common.py` | Yes | Generic ID response |
| User schemas | `user.py` | Yes | Auth domain |
| Supplier schemas | `supplier.py` | Yes | Supplier domain |
| Customer schemas | `customer.py` | Yes | Customer domain |
| Shipment schemas | `shipment.py` | Yes | Shipping domain |
| Invoice schemas | `invoice.py` | Yes | Invoice domain |
| Customs schemas | `customs.py` | Yes | Customs domain |
| Document schemas | `document.py` | Yes | Document domain |
| Resource schemas | `resource.py` | Yes | Resource domain |
| ETA schemas | `eta.py` | Yes | ETA domain |
| Shipping schemas | `shipping.py` | Yes | Shipping domain |

### 23.5 Existing Frontend Pages

| Page | Route | Reusable | Notes |
|------|-------|----------|-------|
| `Login.tsx` | `/login` | Yes | Auth page |
| `Dashboard.tsx` | `/` | Extend | Add ETA/Shipping widgets, notification bell |
| `Suppliers.tsx` | `/suppliers` | Yes | Supplier management |
| `Customers.tsx` | `/customers` | Yes | Customer management |
| `Shipments.tsx` | `/shipments` | Yes | Shipping management |
| `Invoices.tsx` | `/invoices` | Yes | Invoice management |
| `Customs.tsx` | `/customs` | Yes | Customs management |
| `Documents.tsx` | `/documents` | Yes | Document management |
| `Resources.tsx` | `/resources` | Yes | Resource management |
| `Profile.tsx` | `/profile` | Yes | User profile |

### 23.6 Existing Frontend Components

| Component | Location | Reusable | Notes |
|-----------|----------|----------|-------|
| `Layout` | `components/layout/Layout.tsx` | Yes | Main layout wrapper |
| `LanguageSwitcher` | `components/layout/LanguageSwitcher.tsx` | Yes | i18n support |
| `PrivateRoute` | `App.tsx` | Yes | Auth guard |

### 23.7 Existing API Functions

| Function | Endpoint | Reusable | Notes |
|----------|----------|----------|-------|
| `login` | `POST /api/v1/auth/login` | Yes | Authentication |
| `register` | `POST /api/v1/auth/register` | Yes | Authentication |
| `getMe` | `GET /api/v1/auth/me` | Yes | Authentication |
| `listSuppliers` | `GET /api/v1/suppliers` | Yes | Supplier domain |
| `listCustomers` | `GET /api/v1/customers` | Yes | Customer domain |
| `listShipments` | `GET /api/v1/shipping/shipments` | Yes | Shipping domain |
| `listInvoices` | `GET /api/v1/invoices` | Yes | Invoice domain |
| `listDeclarations` | `GET /api/v1/customs/declarations` | Yes | Customs domain |
| `listDocuments` | `GET /api/v1/documents` | Yes | Document domain |
| `listResources` | `GET /api/v1/resources` | Yes | Resource domain |
| `searchResources` | `GET /api/v1/resources/search` | Extend | Only searches resources; needs unification |

