# WP-17A: API Endpoint Test Coverage Expansion

**Status:** ✅ Complete
**Generated:** 2026-07-05
**Baseline:** WP-16B (b4ff64f)
**Goal:** Expand pytest coverage to all 6 untested business domains via endpoint integration tests without modifying any production code.

---

## 1. Current State Summary

After WP-16B the backend is healthy:
- 8 routers are thin and delegate to 7 service modules.
- `backend/app/services/base.py` centralizes shared helpers (`connection`, `build_list_query`, `now_iso`, `parse_json`, `dumps_json`, `execute_update`).
- 21 pytest tests pass, covering only Auth and Suppliers.
- Remaining domains with **zero tests**: Customers, Resources, Customs, Documents, Shipping, Invoices.

---

## 2. WP-17A Goal

Add comprehensive endpoint tests for the 6 untested domains using the existing TestClient + registered-user pattern. Do **not** modify any production code, routers, or services.

---

## 3. Patch Breakdown

### Patch-1: Customer Domain Tests (`backend/tests/test_customers.py`)

**Objective:** Cover CRUD + CSV import for `/api/v1/customers`.

**New Files:**
- `backend/tests/test_customers.py` (9 tests)

**Acceptance Criteria:**
- `test_list_customers_authorized` — 200, returns list
- `test_list_customers_unauthorized` — 401
- `test_get_customer_authorized` — 200 with correct id
- `test_get_customer_not_found` — 404
- `test_create_customer_with_owner_role` — 200, id returned
- `test_create_customer_with_staff_role_forbidden` — 403
- `test_update_customer_with_manager_role` — 200, message returned
- `test_delete_customer_with_owner_role` — 200, deactivation message returned
- `test_import_customers_with_sales_role` — 200, ImportResponse returned

**Status:** ✅ Implemented (9 tests passing)

---

### Patch-2: Resource Domain Tests (`backend/tests/test_resources.py`)

**Objective:** Cover CRUD + search for `/api/v1/resources`.

**New Files:**
- `backend/tests/test_resources.py` (8 tests)

**Acceptance Criteria:**
- `test_list_resources_authorized` — 200
- `test_search_resources_authorized` — 200
- `test_get_resource_authorized` — 200
- `test_get_resource_not_found` — 404
- `test_create_resource_with_owner_role` — 200
- `test_create_resource_with_staff_role_forbidden` — 403
- `test_update_resource_with_manager_role` — 200
- `test_delete_resource_with_owner_role` — 200

**Status:** ✅ Implemented (8 tests passing)

---

### Patch-3: Customs Domain Tests (`backend/tests/test_customs.py`)

**Objective:** Cover duty calculation and declaration lifecycle for `/api/v1/customs`.

**New Files:**
- `backend/tests/test_customs.py` (6 tests)

**Acceptance Criteria:**
- `test_calculate_duties_authorized` — 200, duty/tax amounts present
- `test_create_declaration_with_logistics_role` — 200, declaration_number present
- `test_create_declaration_with_staff_role_forbidden` — 403
- `test_update_declaration_with_manager_role` — 200
- `test_submit_declaration_authorized` — 200
- `test_get_declaration_not_found` — 404

**Excluded from WP-17A due to pre-existing production issues:**
- HS code list/get endpoints: `ResponseValidationError` because `hs_codes` table lacks `created_at` column required by `HSCode` schema.
- Customs declarations list/get: same root cause (`documents` column serialized as `"[]"` but schema expects `list[str]`).

These exclusions are documented in the test file with comments. They will be addressed by future work packages.

**Status:** ✅ Implemented (6 tests passing)

---

### Patch-4: Document Domain Tests (`backend/tests/test_documents.py`)

**Objective:** Cover document CRUD for `/api/v1/documents`.

**New Files:**
- `backend/tests/test_documents.py` (6 tests)

**Acceptance Criteria:**
- `test_list_documents_authorized` — 200
- `test_get_document_authorized` — 200
- `test_get_document_not_found` — 404
- `test_create_document_authorized` — 200
- `test_update_document_authorized` — 200
- `test_delete_document_with_owner_role` — 200

**Excluded from WP-17A due to pre-existing production bug:**
- Document upload endpoint: `upload_document()` in `app/services/document.py` does not populate the required `type` column, causing `sqlite3.IntegrityError: NOT NULL constraint failed: documents.type`.
- Documented in test file; deferred to future fix.

**Status:** ✅ Implemented (6 tests passing)

---

### Patch-5: Shipping Domain Tests (`backend/tests/test_shipping.py`)

**Objective:** Cover rates, tracking, labels, and shipment CRUD for `/api/v1/shipping`.

**New Files:**
- `backend/tests/test_shipping.py` (9 tests)

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

**Note:** The `/rates` endpoint is implemented as `@router.get("/rates", ...)` but FastAPI 0.111 serializes `ShippingRateRequest` from the body for GET requests in this codebase; tests use `client.request("GET", ..., json=...)` to match actual behavior.

**Status:** ✅ Implemented (9 tests passing)

---

### Patch-6: Invoice Domain Tests (`backend/tests/test_invoices.py`)

**Objective:** Cover invoice CRUD + validate/cancel/status for `/api/v1/invoices`.

**New Files:**
- `backend/tests/test_invoices.py` (10 tests)

**Acceptance Criteria:**
- `test_list_invoices_authorized` — 200
- `test_get_invoice_authorized` — 200
- `test_get_invoice_not_found` — 404
- `test_create_invoice_with_accountant_role` — 200
- `test_create_invoice_with_staff_role_forbidden` — 403
- `test_update_invoice_with_manager_role` — 200
- `test_validate_invoice_with_accountant_role` — 200
- `test_cancel_invoice_with_accountant_role` — 200
- `test_cancel_invoice_not_found` — 404
- `test_get_invoice_status_authorized` — 200

**Status:** ✅ Implemented (10 tests passing)

---

## 4. Verification

After all patches:
- Total tests: **69 passed** (21 existing + 48 new)
- No production code modified
- Full suite command: `cd backend && python -m pytest tests/ -v`
