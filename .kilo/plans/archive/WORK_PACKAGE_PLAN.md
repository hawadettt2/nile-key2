# Work Package Plan (Software Lifecycle Order)

**Version:** 1.3
**Generated:** 2026-07-04
**Based on:** PLAN.md (Master Roadmap v2.1) — Single Source of Truth
**Note:** Originally based on ARCHITECTURE_CHARTER.md; content now merged into PLAN.md

---

## WP-01: Backend Runtime Stability

**Status:** ✅ Complete

**Objective:** Ensure backend starts without runtime blockers.

**Why It Exists:** Recovery checkpoint requires verification before any changes.

**Scope:** Verify backend starts, health endpoint works, no import errors.

**Files In Scope:**
- backend/main.py
- backend/app/core/config.py
- backend/app/core/database.py
- backend/app/core/security.py
- backend/app/routers/__init__.py
- backend/app/routers/auth.py
- backend/app/routers/shipping.py
- backend/app/routers/invoice.py
- backend/app/routers/suppliers.py
- backend/app/routers/customers.py
- backend/app/routers/customs.py
- backend/app/routers/resources.py
- backend/app/routers/documents.py

**Dependencies:** None

**Validation:**
1. `uvicorn backend.main:app --port 8000` starts
2. GET /health returns {"status":"healthy"}
3. No import errors from core modules

**Rollback:** N/A

---

## WP-02: Database Contract Alignment

**Status:** ✅ Complete (WP-02A-H complete)

**Decomposition:**
| Sub-package | Status | Entity |
|-------------|--------|--------|
| WP-02A | ✅ Complete | users |
| WP-02B | ✅ Complete | suppliers |
| WP-02C | ✅ Complete | customers |
| WP-02D | ✅ Complete | shipments |
| WP-02E | ✅ Complete | invoices |
| WP-02F | ✅ Complete | customs_declarations |
| WP-02G | ✅ Complete | resources |
| WP-02H | ✅ Complete | documents |

**Dependencies:** WP-01

**Validation:**
1. `python -c "from app.core.database import init_db; init_db()"`
2. Verify all schema fields exist as DB columns
3. No missing columns (username, phone, address, etc.)

**Rollback:** 
- WP-02A: `git checkout a0e87e7 -- backend/app/core/database.py`
- WP-02B: `git checkout 94ae639 -- backend/app/core/database.py backend/app/routers/suppliers.py`
- WP-02C: `git checkout 5cec3ca -- backend/app/core/database.py backend/app/routers/customers.py`

---

## WP-03: Authentication Stability

**Status:** ✅ Complete

**Objective:** Ensure authentication system works with correct password algorithm.

**Why It Exists:** Security.py aligned to bcrypt and OAuth2 status codes verified.

**Scope:** Verify password hashing matches requirements.txt (bcrypt) and OAuth2 status codes.

**Files In Scope:**
- backend/app/core/security.py
- backend/app/schemas/user.py
- backend/app/routers/auth.py

**Dependencies:** WP-01

**Validation:**
1. Register user, verify password stored ✅
2. Login works with correct password ✅
3. Algorithm is bcrypt per requirements.txt ✅
4. OAuth2 status codes: 401 for missing auth, 403 for missing role ✅

**Rollback:** `git checkout dbe1ef4 -- backend/app/routers/auth.py`

---

## WP-04: CRUD Integrity

**Status:** ✅ Complete

**Objective:** Fix all CRUD operations to work with aligned schema.

**Why It Exists:** Routes use schema fields that must match DB columns.

**Scope:** Update router handlers to use correct column names after WP-02.

**Files In Scope:**
- backend/app/routers/suppliers.py
- backend/app/routers/customers.py
- backend/app/routers/shipping.py
- backend/app/routers/invoice.py
- backend/app/schemas/supplier.py
- backend/app/schemas/customer.py
- backend/app/schemas/shipment.py
- backend/app/schemas/invoice.py

**Dependencies:** WP-02

**Validation:**
1. All CRUD endpoints return data successfully
2. No SQLite errors on insert/select/update/delete
3. Data persists correctly

**Rollback:** `git checkout backend/app/routers/`

---

## WP-05: Frontend Build Stability

**Status:** ✅ Complete

**Objective:** Ensure frontend builds with current API contract.

**Why It Exists:** Frontend depends on backend; verify after schema changes.

**Scope:** Verify TypeScript compiles, dev server starts.

**Files In Scope:**
- frontend/package.json
- frontend/tsconfig.json
- frontend/vite.config.ts
- frontend/src/main.tsx
- frontend/src/App.tsx
- frontend/src/services/api.ts
- frontend/src/pages/Login.tsx
- frontend/src/pages/Dashboard.tsx
- frontend/src/pages/Suppliers.tsx
- frontend/src/pages/Customers.tsx
- frontend/src/pages/Shipments.tsx
- frontend/src/pages/Invoices.tsx
- frontend/src/pages/Customs.tsx
- frontend/src/pages/Documents.tsx
- frontend/src/pages/Resources.tsx

**Dependencies:** WP-02, WP-04

**Validation:**
1. `npm run build` in frontend completes
2. No TypeScript errors
3. Login page renders

**Rollback:** N/A

---

## WP-06: Integration Testing

**Status:** ✅ COMPLETED

**Objective:** Validate all API endpoints work end-to-end.

**Why It Exists:** Charter Section 18 requires core routes work.

**Scope:** Test each router endpoint with valid requests against running backend.

**Files In Scope:**
- backend/app/routers/auth.py
- backend/app/routers/shipping.py
- backend/app/routers/invoice.py
- backend/app/routers/suppliers.py
- backend/app/routers/customers.py
- backend/app/routers/customs.py
- backend/app/routers/resources.py
- backend/app/routers/documents.py
- backend/app/schemas/* (all schema files)

**Dependencies:** WP-04

**Validation:**
1. Auth endpoints work ✅
2. Suppliers/Customers CRUD work ✅
3. Shipments/Invoices CRUD work ✅
4. Customs endpoints work ✅
5. Resources/Documents endpoints work ✅

**Patch Execution Summary:**
| Patch | Entity | Status | Notes |
|-------|--------|--------|-------|
| Patch-1 | Authentication | ✅ Complete | Login returns JWT token |
| Patch-2 | Suppliers | ✅ Complete | CRUD verified |
| Patch-3 | Customers | ✅ Complete | CRUD verified |
| Patch-4 | Resources | ✅ Complete | CRUD verified |
| Patch-5 | Documents | ✅ Complete | Metadata repair applied |
| Patch-6 | Shipping | ✅ Complete | Router verified, ADR-0001 applied |
| Patch-7 | Invoices | ✅ Complete | Legacy schema compatibility verified |
| Patch-8 | Customs | ✅ Complete | All endpoints verified, DELETE absent by design |

**Rollback:** N/A

---

## WP-07: Security Hardening

**Status:** ✅ COMPLETED

**Objective:** Fix all security violations per charter Section 12.

**Why It Exists:** Hardcoded secrets and wildcard CORS are critical risks.

**Scope:** Externalize SECRET_KEY, fix CORS configuration.

**Files In Scope:**
- backend/app/core/config.py
- backend/.env.example
- backend/main.py

**Dependencies:** WP-01

**Validation:**
1. App fails without SECRET_KEY in production ✅
2. CORS restricts to ALLOWED_ORIGINS ✅
3. No hardcoded defaults in config ✅

**Rollback:** `git checkout backend/app/core/config.py backend/main.py backend/.env.example`

---

## WP-08: Architecture Cleanup

**Status:** ✅ COMPLETED

**Objective:** Prepare architecture for refactoring and migration system.

**Why It Exists:** Charter requires cleanup before refactoring (Sections 8, 10, 16).

**Scope:** Initialize services layer, create SQL helper, align .env.example.

**Files In Scope:**
- backend/app/services/__init__.py
- backend/app/core/database.py
- backend/.env.example

**Dependencies:** WP-01, WP-02

**Validation:**
1. `from app.services import *` imports cleanly ✅
2. Helper function works for UPDATE queries ✅
3. .env.example has all config variables ✅

**Rollback:** Remove added functions, revert .env.example

---

## WP-09: Refactoring

**Status:** ✅ COMPLETED

**Objective:** Extract duplicated logic into reusable components.

**Why It Exists:** Charter Section 8 prohibits code duplication.

**Scope:** Refactor 8 routers to use shared SQL query builder and remove legacy compatibility shims.

**Files In Scope:**
- backend/app/routers/auth.py
- backend/app/routers/shipping.py
- backend/app/routers/invoice.py
- backend/app/routers/suppliers.py
- backend/app/routers/customers.py
- backend/app/routers/customs.py
- backend/app/routers/resources.py
- backend/app/routers/documents.py
- backend/app/core/database.py

**Dependencies:** WP-08

**Validation:**
1. All endpoints still work ✅
2. No code duplication in UPDATE patterns ✅
3. Cleaner router code ✅
4. Legacy compatibility filters removed ✅

**Rollback:** `git checkout backend/app/routers/`

---

## WP-10: Database Migration System

**Status:** ✅ COMPLETED

**Objective:** Add Alembic migrations per charter Phase 3 and remove legacy columns.

**Why It Exists:** Charter requires migrations as legal evolution mechanism.

**Scope:** Initialize Alembic, capture current schema as initial migration, remove legacy columns.

**Files In Scope:**
- alembic.ini
- backend/alembic/ directory
- backend/app/core/database.py
- backend/app/routers/*.py

**Dependencies:** WP-02, WP-09

**Validation:**
1. `alembic upgrade head` applies migration on existing schema ✅
2. Migration reversible ✅
3. `invoices.uuid` removed ✅
4. Legacy columns dropped via SQLite-safe table rebuild where needed ✅

**Execution Notes:**
- `init_db()` owns initial schema creation
- Alembic migrations handle destructive post-init cleanup only
- Initial migration revision is empty (`pass`) because schema is created by `init_db()`

**Rollback:** Remove alembic directory and revert routers/models/config changes

---

## WP-11: Deployment Validation

**Status:** ✅ Complete

**Objective:** Synchronize project documentation to align with current implementation state.

**Why It Exists:** Documentation must describe reality; drift accumulated after WP-10.

**Scope:** Update docs to reflect WP-10+ changes, updated baseline, resolved items.

**Files In Scope:**
- CURRENT_STATUS.md
- ENGINEERING_MEMORY.md
- PROJECT_BASELINE.md
- README.md
- PLAN.md

**Dependencies:** WP-10

**Validation:**
1. Docs reflect current implementation state
2. Baseline updated to latest commit

**Rollback:** Revert doc changes

---

## WP-12: Production Readiness

**Status:** ✅ Complete

**Objective:** Harden containerization artifacts and finalize Compose configuration for deployment.

**Why It Exists:** Charter Phase 6 requires validated deployment configuration.

**Scope:** Harden Docker deployment and finalize Compose configuration.

**Files In Scope:**
- backend/Dockerfile
- frontend/Dockerfile
- docker-compose.yml
- .dockerignore
- DEPLOYMENT.md

**Dependencies:** WP-10, WP-11

**Validation:**
1. All quality gates pass (charter Section 18)
2. Frontend types match API
3. Documentation updated
4. Docker artifacts hardened

**Rollback:** Remove Docker files

---

## WP-13A: Service Layer Extraction (Suppliers & Customers)

**Status:** ✅ Complete

**Objective:** Extract supplier and customer business logic from routers into services layer.

**Why It Exists:** Charter Section 10 prohibits business logic in routers; services layer must be populated before completing all domains.

**Scope:** Migrate supplier and customer router handlers to delegate to `app/services/supplier.py` and `app/services/customer.py`.

**Files In Scope:**
- backend/app/routers/suppliers.py
- backend/app/routers/customers.py
- backend/app/services/supplier.py
- backend/app/services/customer.py

**Dependencies:** WP-08, WP-09

**Validation:**
1. Supplier/Customer endpoints return identical responses
2. No raw SQL or DB imports in routers
3. Tests pass

**Rollback:** Revert routers to inline database logic

---

## WP-14: Service Layer Extraction (Resources, Customs, Documents, Shipping, Invoices)

**Status:** ☐ Not Started

**Note:** Executed as single combined WP-15 package.

---

## WP-15: Service Layer Extraction Complete

**Status:** ✅ Complete

**Objective:** Complete service layer extraction for all remaining domains.

**Why It Exists:** Complete charter Section 10 compliance for all 7 non-auth domains.

**Scope:** Extract business logic for resources, customs, documents, shipping, invoices into dedicated service modules.

**Files In Scope:**
- backend/app/services/resource.py
- backend/app/services/customs.py
- backend/app/services/document.py
- backend/app/services/shipping.py
- backend/app/services/invoice.py
- backend/app/routers/resources.py
- backend/app/routers/customs.py
- backend/app/routers/documents.py
- backend/app/routers/shipping.py
- backend/app/routers/invoice.py

**Dependencies:** WP-13A

**Validation:**
1. All 7 domains have thin routers
2. All service modules implement full CRUD + business rules
3. Tests pass
4. Behavior preserved

**Rollback:** Revert routers to inline database logic

---

## WP-16A: Router Thinness Verification

**Status:** ☐ Not Started

**Note:** Executed as part of WP-15/WP-16B verification.

---

## WP-16B: Shared Service Base Infrastructure

**Status:** ✅ Complete

**Objective:** Introduce shared base utilities and standardize service-layer implementations.

**Why It Exists:** Reduce duplication across service modules; centralize connection, JSON, and timestamp utilities.

**Scope:** Create `app/services/base.py` and refactor all service files to use shared helpers (`build_list_query`, `connection`, `now_iso`, `parse_json`, `dumps_json`, `execute_update`).

**Files In Scope:**
- backend/app/services/base.py
- backend/app/services/supplier.py
- backend/app/services/customer.py
- backend/app/services/customs.py
- backend/app/services/document.py
- backend/app/services/invoice.py
- backend/app/services/resource.py
- backend/app/services/shipping.py

**Dependencies:** WP-15

**Validation:**
1. All service modules import from base
2. No duplicated JSON/timestamp/connection logic
3. Tests pass
4. Behavior preserved identical to WP-15

**Rollback:** Revert service files to WP-15 state

---

## WP-17A: API Coverage Expansion

**Status:** ✅ Complete

**Objective:** Expand endpoint integration test coverage to previously untested business domains.

**Why It Exists:** Only Auth and Suppliers had automated endpoint coverage after WP-06; 6 domains remained untested.

**Scope:** Add pytest endpoint tests in `backend/tests/test_customers.py`, `test_resources.py`, `test_customs.py`, `test_documents.py`, `test_shipping.py`, `test_invoices.py`.

**Files In Scope:**
- backend/tests/test_customers.py
- backend/tests/test_resources.py
- backend/tests/test_customs.py
- backend/tests/test_documents.py
- backend/tests/test_shipping.py
- backend/tests/test_invoices.py

**Dependencies:** WP-16B

**Validation:**
1. 48 new endpoint tests added
2. Full suite passes
3. No production code modified

**Rollback:** Remove new endpoint test files

---

## WP-17B: Service Layer Unit Tests

**Status:** ✅ Complete

**Objective:** Add unit tests for business logic in service layer using `unittest.mock`.

**Why It Exists:** Endpoint tests alone do not isolate row-mapping, JSON coercion, or deterministic business logic paths.

**Scope:** Add pytest unit tests in `backend/tests/test_services/` for all 7 service modules.

**Files In Scope:**
- backend/tests/test_services/test_supplier_service.py
- backend/tests/test_services/test_customer_service.py
- backend/tests/test_services/test_customs_service.py
- backend/tests/test_services/test_document_service.py
- backend/tests/test_services/test_resource_service.py
- backend/tests/test_services/test_shipping_service.py
- backend/tests/test_services/test_invoice_service.py

**Dependencies:** WP-17A

**Validation:**
1. 59 new service-layer unit tests added
2. Full suite passes
3. No production code modified

**Rollback:** Remove `backend/tests/test_services/`

---

## WP-18: Production Bug Fixes and Deployment Readiness

**Status:** ✅ Complete

**Objective:** Fix two pre-existing production bugs and validate Docker deployment artifacts.

**Why It Exists:** Two runtime bugs were discovered during WP-17A/WP-17B test expansion that affect production endpoints. Docker artifacts existed but had not been validated.

**Scope:** 
1. Fix `hs_codes` missing `created_at` column
2. Fix `upload_document()` missing `type` column
3. Validate Docker artifacts against project configuration

**Files In Scope:**
- backend/app/core/database.py
- backend/app/services/document.py
- backend/tests/test_customs.py
- backend/tests/test_documents.py
- docker-compose.yml
- backend/Dockerfile
- frontend/Dockerfile
- DEPLOYMENT.md

**Dependencies:** WP-17B

**Validation:**
1. `hs_codes` table has `created_at` column after `init_db()`
2. `POST /api/v1/documents/upload` returns 200
3. Docker artifacts validated and consistent
4. Full suite passes (176 tests)

**Rollback:** Revert `database.py` and `document.py` changes; remove re-enabled tests

---

## WP-19: ETA Engine

**Status:** ✅ Complete

**Objective:** Extract complete ETA compliance business logic from `erpnext_egypt_compliance` and rebuild it within Nile Key architecture.

**Why It Exists:** Egyptian Tax Authority (ETA) e-invoicing/e-receipt compliance is mandatory for Nile Key platform. Business logic must be extracted from reference repo and rebuilt to match Nile Key patterns.

**Scope:** 
1. ETA Pydantic schemas matching ETA Schema v1.0 (invoices) and v1.2 (receipts)
2. OAuth2 client credentials HTTP client with retry and token refresh
3. Service layer: connector CRUD, invoice/receipt operations, batch submission, status polling, audit logging, error mapping, idempotency
4. Thin FastAPI router following Nile Key pattern
5. APScheduler integration for hourly status polling and batch submission
6. Database tables: `eta_connectors`, `eta_logs`, `eta_log_documents`
  7. 71 pytest tests (70 passing, 1 skipped by design)

**Files In Scope:**
- backend/app/schemas/eta.py
- backend/app/services/eta/__init__.py
- backend/app/services/eta/eta_client.py
- backend/app/routers/eta.py
- backend/app/core/eta_scheduler.py
- backend/app/core/database.py
- backend/main.py
- backend/requirements.txt
- backend/tests/test_eta.py

**Dependencies:** WP-18

**Validation:**
1. Pydantic schemas match ETA v1.0/v1.2 ✅
2. OAuth2 integration with Preprod/Production environments ✅
3. Invoice submission ready (requires API keys for live test) ✅
4. Invoice cancellation implemented ✅
5. Invoice status tracking implemented ✅
6. PDF download implemented ✅
7. Receipt submission implemented ✅
8. Batch submission with delay_in_hours logic ✅
9. Status polling implemented ✅
10. Retry strategy (tenacity, 3 attempts, exponential backoff) ✅
11. Idempotency keys implemented ✅
12. Error mapping to Arabic/English messages ✅
13. Audit logging (eta_logs + eta_log_documents) ✅
14. Token refresh with 3-minute buffer ✅
15. APScheduler integrated (hourly jobs) ✅
  16. 71 new pytest tests pass (70 passing, 1 skipped by design) ✅
17. No TODO/FIXME/Stub/Placeholder in WP-19 code ✅

**Rollback:** Remove ETA files and revert `database.py`, `main.py`, `requirements.txt`

---

## WP-20: Shipping Engine

**Status:** ✅ Complete

**Objective:** Extract complete shipping business logic with provider abstraction layer.

**Why It Exists:** Shipping integration requires multi-provider abstraction with unified interface.

**Scope:** Implement LetMeShip + SendCloud clients, rate aggregation, shipment booking, tracking, label retrieval, cancellation, provider/parcel-template CRUD.

**Files In Scope:**
- backend/app/schemas/shipping.py
- backend/app/services/shipping/base.py
- backend/app/services/shipping/letmeship_client.py
- backend/app/services/shipping/sendcloud_client.py
- backend/app/services/shipping/__init__.py
- backend/app/services/shipping.py
- backend/app/routers/shipping.py
- backend/app/core/shipping_scheduler.py
- backend/app/core/database.py
- backend/tests/test_shipping.py
- backend/tests/test_services/test_shipping_service.py

**Dependencies:** WP-18

**Validation:**
1. LetMeShip: rates, create shipment, label, tracking ✅
2. SendCloud: rates, create shipment, label, tracking, cancel ✅
3. Parcel dimension validation works ✅
4. Address validation works ✅
5. Error handling displays clear messages ✅
6. Retry for transient failures ✅
7. 34+ tests pass ✅

**Rollback:** Revert shipping service files and revert `database.py`, `main.py`

---

## WP-21: Platform Integration

**Status:** ✅ Complete

**Objective:** Integrate all platform components with notifications, audit, search, dashboard, workflows, and frontend.

**Why It Exists:** Phase 1.5 requires all systems connected and operational.

**Scope:** Notification service, audit logging, unified search, live dashboard, export workflows, frontend integration, notification triggers.

**Files In Scope:**
- backend/app/services/notification.py
- backend/app/services/audit.py
- backend/app/services/search.py
- backend/app/services/dashboard.py
- backend/app/services/workflow.py
- backend/app/schemas/notification.py
- backend/app/schemas/audit.py
- backend/app/schemas/search.py
- backend/app/schemas/dashboard.py
- backend/app/schemas/workflow.py
- backend/app/routers/notifications.py
- backend/app/routers/audit.py
- backend/app/routers/search.py
- backend/app/routers/dashboard.py
- backend/app/routers/workflow.py
- backend/app/core/database.py
- frontend/src/pages/Dashboard.tsx
- frontend/src/pages/Notifications.tsx
- frontend/src/components/NotificationBell.tsx
- frontend/src/services/api.ts

**Dependencies:** WP-19, WP-20

**Validation:**
1. All entities connected ✅
2. Dashboard shows live data ✅
3. Audit logging works for all operations ✅
4. Notifications work via email ✅
5. Search works across all entities ✅
6. Export workflows operational ✅
7. Frontend integrated ✅
8. Tests pass (373+ total) ✅

**Rollback:** Revert notification, audit, search, dashboard, workflow services and routers

---

## WP-30B: Session Management + Mission Lifecycle

**Status:** ✅ Complete

**Objective:** Implement persistent Digital Export Session with mission lifecycle.

**Scope:** Session management, mission lifecycle, DEM router registration.

**Files In Scope:**
- backend/app/agent/session/
- backend/app/routers/digital_export_manager.py
- backend/app/core/database.py
- backend/tests/agent/

**Dependencies:** WP-30

**Validation:**
1. Session CRUD works ✅
2. Mission lifecycle works ✅
3. 6 DEM endpoints registered ✅
4. Router registered in main.py ✅
5. Closure Review approved ✅

**Rollback:** Remove session files; revert router registration

---

## WP-30C: Task Planner + Execution Engine

**Status:** ✅ Complete

**Objective:** Implement structured mission execution with retry, idempotency, audit.

**Scope:** Task Planner, Execution Engine, mission orchestration.

**Files In Scope:**
- backend/app/agent/planner/
- backend/app/agent/execution_engine/
- backend/tests/agent/

**Dependencies:** WP-30B

**Validation:**
1. Task planning works ✅
2. Execution with retry works ✅
3. Idempotency enforced ✅
4. Audit logging integrated ✅

**Rollback:** Remove planner and execution engine files

---

## WP-30D: Decision Engine

**Status:** ✅ Complete

**Objective:** Implement reasoning loop with knowledge/memory graceful degradation.

**Scope:** Decision Engine with knowledge and memory integration.

**Files In Scope:**
- backend/app/agent/decision_engine/
- backend/tests/agent/test_decision_engine.py

**Dependencies:** WP-30C

**Validation:**
1. Reasoning loop works ✅
2. Knowledge graceful degradation works ✅
3. Memory graceful degradation works ✅

**Rollback:** Remove decision engine files

---

## WP-30E: Tool Implementations

**Status:** ✅ Complete

**Objective:** Implement 14 ERP tool wrappers with metadata.

**Scope:** Tool wrappers, ToolRegistry, legacy planner drift fix.

**Files In Scope:**
- backend/app/agent/tools/
- backend/tests/agent/test_erp_tools.py

**Dependencies:** WP-30D

**Validation:**
1. 14 tool wrappers implemented ✅
2. ToolRegistry populated ✅
3. Legacy planner drift fixed ✅

**Rollback:** Remove tool files; revert planner

---

## WP-30F: Company Knowledge Layer Interface

**Status:** ✅ Complete

**Objective:** Define company knowledge layer interface and registry.

**Scope:** KnowledgeProvider ABC, KnowledgeQuery contract, KnowledgeProviderRegistry, ingestion contract.

**Files In Scope:**
- backend/app/agent/knowledge/provider.py
- backend/app/agent/knowledge/registry.py
- backend/app/agent/knowledge/graph_provider.py
- backend/app/schemas/knowledge_graph.py
- .kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md
- backend/tests/agent/test_knowledge.py

**Dependencies:** WP-30E

**Validation:**
1. KnowledgeProvider ABC defined ✅
2. KnowledgeQuery contract defined ✅
3. KnowledgeProviderRegistry implemented ✅
4. 17 tests pass ✅
5. ED-WP30-002 recorded ✅

**Rollback:** Remove knowledge files; revert registry

---

## WP-30G: Memory Interface Definition

**Status:** ✅ Complete

**Objective:** Define memory provider interface for context persistence.

**Scope:** MemoryProvider ABC, memory contract, graceful degradation.

**Files In Scope:**
- backend/app/agent/memory/interface.py
- backend/app/agent/memory/sqlite_provider.py
- .kilo/plans/MEMORY_CONTRACT.md
- backend/tests/agent/test_memory.py

**Dependencies:** WP-30F

**Validation:**
1. MemoryProvider ABC defined ✅
2. SQLiteMemoryProvider implemented ✅
3. 12 tests pass ✅
4. Graceful degradation in DEM core ✅

**Rollback:** Remove memory files; revert DEM core usage

---

## WP-30H: Avatar Contract

**Status:** ✅ Complete

**Objective:** Define avatar rendering interface and intent content contract.

**Scope:** IntentContent Pydantic model, AvatarRenderer ABC, AVATAR_CONTRACT.md.

**Files In Scope:**
- backend/app/agent/avatar/interface.py
- .kilo/plans/AVATAR_CONTRACT.md
- backend/tests/agent/test_avatar.py

**Dependencies:** WP-30G

**Validation:**
1. IntentContent defined ✅
2. AvatarRenderer ABC defined ✅
3. 15 tests pass ✅
4. No regressions ✅

**Rollback:** Remove avatar files

---

## WP-30I: Advanced Features

**Status:** ✅ Complete

**Objective:** Implement advanced DEM features.

**Scope:** Multi-step workflow executor, proactive monitoring, training mode, approval gates.

**Files In Scope:**
- backend/app/agent/execution_engine/orchestrator.py
- backend/app/agent/monitoring/service.py
- backend/app/agent/training/service.py
- backend/tests/agent/test_execution_engine.py
- backend/tests/agent/test_monitoring.py
- backend/tests/agent/test_training.py

**Dependencies:** WP-30H

**Validation:**
1. Workflow executor with dependency resolution ✅
2. Proactive monitoring with alert thresholds ✅
3. Training mode implemented ✅
4. Approval gates for destructive operations ✅

**Rollback:** Remove monitoring and training files; revert orchestrator

---

## WP-31: AI Memory

**Status:** ✅ Complete

**Objective:** Implement concrete memory provider with session integration.

**Scope:** SQLiteMemoryProvider, memory injection, decision persistence, active recall biases.

**Files In Scope:**
- backend/app/agent/memory/sqlite_provider.py
- backend/app/agent/session/
- backend/app/schemas/mission.py
- backend/tests/agent/test_sqlite_provider.py
- backend/tests/agent/test_decision_engine.py

**Dependencies:** WP-30I

**Validation:**
1. SQLiteMemoryProvider implements recall/store/forget/summarize/cleanup_expired ✅
2. Memory injection into session context ✅
3. Decision persistence hook ✅
4. Active recall biases in ReasoningEngine ✅
5. 151 agent tests passing ✅
6. Scope creep reverted ✅

**Rollback:** Revert memory provider and session integration

---

## WP-32: Knowledge Graph

**Status:** ✅ Complete

**Objective:** Implement knowledge graph for trade entities.

**Scope:** 9 node types, 9 API endpoints, derived edges, traversal, entity sync, MemoryProvider integration, audit logging.

**Files In Scope:**
- backend/app/schemas/knowledge_graph.py
- backend/app/services/knowledge_graph.py
- backend/app/agent/knowledge/graph_provider.py
- backend/app/routers/knowledge_graph.py
- backend/app/core/database.py
- backend/tests/test_knowledge_graph.py
- backend/tests/test_services/test_knowledge_graph.py
- backend/tests/test_knowledge_graph_performance.py
- backend/tests/test_knowledge_graph_security.py

**Dependencies:** WP-30F, WP-30G, WP-31

**Validation:**
1. 9 node types supported ✅
2. 9 API endpoints work ✅
3. Derived edges discovered ✅
4. Graph traversal works ✅
5. Entity sync works ✅
6. MemoryProvider integration with graceful degradation ✅
7. Audit logging integrated ✅
8. 105 tests pass ✅
9. ED-WP32-001 recorded ✅

**Rollback:** Remove knowledge graph files; revert database.py

---

## WP-33: Trade Intelligence

**Status:** ✅ Complete

**Objective:** Implement trade intelligence analytical layer.

**Scope:** Supplier/buyer analysis, trend detection, entity comparisons, report generation, Memory and Knowledge Graph integration.

**Files In Scope:**
- backend/app/schemas/trade_intelligence.py
-backend/app/services/trade_intelligence.py
- backend/app/routers/trade_intelligence.py
- backend/tests/test_trade_intelligence.py
- backend/tests/test_services/test_trade_intelligence.py
- backend/tests/test_trade_intelligence_performance.py
- backend/tests/test_trade_intelligence_security.py

**Dependencies:** WP-32, WP-31, WP-30D

**Validation:**
1. Supplier analysis works ✅
2. Buyer analysis works ✅
3. Market trends detected ✅
4. Comparisons work ✅
5. Reports generated ✅
6. Memory integration works ✅
7. Knowledge Graph integration works ✅
8. Audit logging integrated ✅
9. 120 tests pass ✅
10. Runtime router bug fixed ✅

**Rollback:** Remove trade intelligence files; revert main.py router registration

---

## WP-40: Docker Compose Final Verification

**Status:** ✅ Complete

**Objective:** Final verification of Docker Compose setup for production deployment.

**Scope:** Validate both images build, services start healthy, API reachable, frontend served, database persistence confirmed, frontend TypeScript errors resolved.

**Files In Scope:**
- frontend/tsconfig.node.json
- frontend/src/components/NotificationBell.test.tsx
- frontend/src/pages/Notifications.test.tsx
- frontend/src/components/NotificationBell.tsx
- CURRENT_STATUS.md
- PLAN.md
- CHANGELOG.md
- TECH_DEBT.md
- docs/architecture/ENGINEERING_MEMORY.md
- .kilo/plans/wp33e-final-roadmap-verification.md
- .kilo/plans/1784644008165-wp40-planning-and-governance-report.md
- .kilo/plans/wp40f-final-closure-and-baseline-verification.md

**Dependencies:** WP-33

**Validation:**
1. Backend Docker image builds successfully ✅
2. Frontend Docker image builds successfully ✅
3. `docker compose up --build` completes with both services healthy ✅
4. Backend `/health` returns HTTP 200 ✅
5. Frontend served on port 3000 ✅
6. Backend API reachable on port 8000 ✅
7. Database persistence verified via Docker volume ✅
8. Frontend TypeScript build errors resolved ✅

**Rollback:** Revert frontend TypeScript fixes; revert governance documents

---

## Execution Sequence

WP-01 → WP-02 → WP-03 → WP-04 → WP-05 → WP-06 → WP-07 → WP-08 → WP-09 → WP-10 → **WP-11** → WP-12 → WP-13A → WP-15 → WP-16B → WP-17A → WP-17B → WP-18 → **WP-19** → WP-20 → WP-21 → WP-30B → WP-30C → WP-30D → WP-30E → WP-30F → WP-30G → WP-30H → WP-30I → WP-31 → WP-32 → WP-33 → **WP-40**

---

## Rollback Points

| WP | Rollback Command |
|----|------------------|
| WP-03 | `git checkout dbe1ef4 -- backend/app/routers/auth.py` |
| WP-10 | `git checkout 9f6e6d58ca0f` |
| WP-11 | `git checkout 08a9924 -- docs/` |
| WP-12 | `git checkout 54f7c49` |
| WP-13A | `git checkout c66087e` or `git checkout 3351a4d` |
| WP-15 | `git checkout 1d545b1` |
| WP-16B | `git checkout b4ff64f` |
| WP-17A | Remove `backend/tests/test_customers.py`, `backend/tests/test_resources.py`, `backend/tests/test_customs.py`, `backend/tests/test_documents.py`, `backend/tests/test_shipping.py`, `backend/tests/test_invoices.py` |
| WP-17B | Remove `backend/tests/test_services/` |
| WP-18 | Revert `backend/app/core/database.py` and `backend/app/services/document.py`; remove re-enabled tests in `backend/tests/test_customs.py` and `backend/tests/test_documents.py` |
| WP-19 | Remove ETA files; revert `backend/app/core/database.py`, `backend/main.py`, `backend/requirements.txt` |
| WP-20 | Revert shipping service files and `database.py` |
| WP-21 | Revert notification, audit, search, dashboard, workflow services and routers |
| WP-30B | Remove session files; revert router registration |
| WP-30C | Remove planner and execution engine files |
| WP-30D | Remove decision engine files |
| WP-30E | Remove tool files; revert planner |
| WP-30F | Remove knowledge files; revert registry |
| WP-30G | Remove memory files; revert DEM core usage |
| WP-30H | Remove avatar files |
| WP-30I | Remove monitoring and training files; revert orchestrator |
| WP-31 | Revert memory provider and session integration |
| WP-32 | Remove knowledge graph files; revert database.py |
| WP-33 | Remove trade intelligence files; revert main.py router registration |
| WP-40 | Revert frontend TypeScript fixes; revert governance documents |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.3 | 2026-07-04 | Based on PLAN.md (Master Roadmap v2.1) |
| 1.4 | 2026-07-21 | Extended through WP-40 |


## WP-10 Rollback Points

| WP | Rollback Command |
|----|------------------|
| WP-10 | `git checkout 9f6e6d58ca0f` |

