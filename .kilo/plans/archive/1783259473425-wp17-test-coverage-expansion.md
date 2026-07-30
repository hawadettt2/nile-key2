# WP-17: Test Coverage Expansion

**Generated:** 2026-07-05
**Baseline:** WP-16B (b4ff64f)
**Goal:** Expand pytest coverage to all 6 untested business domains while preserving the existing test conventions and the current API behavior.

---

## 1. Current State Summary

After WP-16B the backend is healthy:
- 8 routers are thin and delegate to 7 service modules.
- `backend/app/services/base.py` centralizes shared helpers (`connection`, `build_list_query`, `now_iso`, `parse_json`, `dumps_json`, `execute_update`).
- 21 pytest tests pass, but they cover **only Auth and Suppliers**.
- Remaining domains with **zero tests**: Customers, Resources, Customs, Documents, Shipping, Invoices.
- Docker artifacts are committed but not validated (environment limitation).
- Frontend types are generated and match the OpenAPI contract.
- No rate limiting is implemented.

---

## 2. WP-17 Goal

Add comprehensive endpoint tests for the 6 untested domains using the same TestClient + registered-user pattern already established in `tests/test_suppliers.py`. Do **not** modify any production code, routers, or services.

---

## 3. Patch Breakdown

### Patch-1: Customer Domain Tests

**Objective:** Cover CRUD + CSV import for `/api/v1/customers`.

**New Files:**
- `backend/tests/test_customers.py`

**Acceptance Criteria:**
- `test_list_customers_authorized` — 200, returns list
- `test_list_customers_unauthorized` — 401
- `test_get_customer_authorized` — 200 with correct id
- `test_get_customer_not_found` — 404
- `test_create_customer_with_owner_role` — 200, id returned
- `test_create_customer_with_staff_role_forbidden` — 403
- `test_update_customer_with_manager_role` — 200, message returned
- `test_delete_customer_with_owner_role` — 200, soft-delete message returned
- `test_import_customers_with_sales_role` — 200, ImportResponse returned

**Risk:** Low. Only adds tests; no production changes.

---

### Patch-2: Resource Domain Tests

**Objective:** Cover CRUD + search for `/api/v1/resources`.

**New Files:**
- `backend/tests/test_resources.py`

**Acceptance Criteria:**
- `test_list_resources_authorized` — 200
- `test_search_resources_authorized` — 200
- `test_get_resource_authorized` — 200
- `test_get_resource_not_found` — 404
- `test_create_resource_with_owner_role` — 200
- `test_create_resource_with_staff_role_forbidden` — 403
- `test_update_resource_with_manager_role` — 200
- `test_delete_resource_with_owner_role` — 200

**Notes:** Resources use `resource_type`, `category`, `country` filters; search uses `q` query param.

**Risk:** Low.

---

### Patch-3: Customs Domain Tests

**Objective:** Cover HS codes, duty calculation, and declarations for `/api/v1/customs`.

**New Files:**
- `backend/tests/test_customs.py`

**Acceptance Criteria:**
- `test_list_hs_codes_authorized` — 200
- `test_get_hs_code_authorized` — 200
- `test_get_hs_code_not_found` — 404
- `test_calculate_duties_authorized` — 200
- `test_list_declarations_authorized` — 200
- `test_create_declaration_with_logistics_role` — 200
- `test_create_declaration_with_staff_role_forbidden` — 403
- `test_update_declaration_with_manager_role` — 200
- `test_submit_declaration_authorized` — 200
- `test_get_declaration_not_found` — 404

**Risk:** Low. Duty calculation and declaration submit have business logic; tests verify current behavior, not new behavior.

---

### Patch-4: Document Domain Tests

**Objective:** Cover document CRUD + upload for `/api/v1/documents`.

**New Files:**
- `backend/tests/test_documents.py`

**Acceptance Criteria:**
- `test_list_documents_authorized` — 200
- `test_get_document_authorized` — 200
- `test_get_document_not_found` — 404
- `test_create_document_authorized` — 200
- `test_upload_document_authorized` — 200, DocumentUploadResponse returned
- `test_update_document_authorized` — 200
- `test_delete_document_with_owner_role` — 200

**Risk:** Low. Uses `UploadFile` in tests via `bytes` content; no actual file system dependency.

---

### Patch-5: Shipping Domain Tests

**Objective:** Cover rates, tracking, labels, and shipment CRUD for `/api/v1/shipping`.

**New Files:**
- `backend/tests/test_shipping.py`

**Acceptance Criteria:**
- `test_get_rates_authorized` — 200
- `test_list_shipments_authorized` — 200
- `test_track_shipment_authorized` — 200
- `test_track_shipment_not_found` — 404
- `test_get_shipment_authorized` — 200
- `test_create_shipment_with_sales_role` — 200
- `test_create_shipment_with_staff_role_forbidden` — 403
- `test_update_shipment_with_manager_role` — 200
- `test_get_label_authorized` — 200

**Risk:** Low. Rate generation uses deterministic carrier map.

---

### Patch-6: Invoice Domain Tests

**Objective:** Cover invoice CRUD + validate/cancel/status for `/api/v1/invoices`.

**New Files:**
- `backend/tests/test_invoices.py`

**Acceptance Criteria:**
- `test_list_invoices_authorized` — 200
- `test_get_invoice_authorized` — 200
- `test_get_invoice_not_found` — 404
- `test_create_invoice_with_accountant_role` — 200, `InvoiceCreateResponse` returned
- `test_create_invoice_with_staff_role_forbidden` — 403
- `test_update_invoice_with_manager_role` — 200
- `test_validate_invoice_with_accountant_role` — 200
- `test_cancel_invoice_with_accountant_role` — 200
- `test_cancel_invoice_not_found` — 404
- `test_get_invoice_status_authorized` — 200

**Risk:** Low. Business rules (tax calc, numbering, state transitions) are preserved; tests validate current behavior only.

---

## 4. Shared Test Conventions

All new test files must follow the existing pattern established in `tests/test_suppliers.py` and `tests/conftest.py`:

1. Use the session-scoped `client` fixture from `conftest.py`.
2. Use `_unique_credentials()` with `uuid.uuid4()[:8]` to avoid email/username collisions.
3. Use `_register_and_login(client, role=...)` to obtain a bearer token.
4. Pass `Authorization: Bearer {token}` header for authenticated requests.
5. Assert `response.status_code` and inspect `response.json()` for expected keys/messages.
6. Keep each test independent; do not share state across tests.
7. Do **not** modify `conftest.py` or any production file.

---

## 5. Verification

After each patch:
- `cd backend && python -m pytest tests/test_<domain>.py -v`
- Full suite: `cd backend && python -m pytest tests/ -v`
- Expected: all tests pass, total count increases by ~8–10 per domain.

After all patches:
- Total tests should be ~69–77 (21 existing + ~48–56 new).
- `npm run build` in `frontend/` still passes (unchanged).
- No production code changes; `git diff` in `backend/app/` must be empty.

---

## 6. Exclusions (Out of Scope for WP-17)

- No rate limiting implementation.
- No Docker validation (Docker daemon unavailable in this environment).
- No PostgreSQL migration.
- No service-layer changes.
- No router or schema changes.
- No frontend changes.

---

## 7. Execution Order

Apply patches sequentially in this order:
1. Patch-1: Customers
2. Patch-2: Resources
3. Patch-3: Customs
4. Patch-4: Documents
5. Patch-5: Shipping
6. Patch-6: Invoices

Each patch is independently verifiable and reversible by removing its new test file.
