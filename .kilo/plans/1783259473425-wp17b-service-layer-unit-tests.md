# WP-17B: Service Layer Unit Tests

**Status:** ☐ Not Started
**Generated:** 2026-07-05
**Baseline:** WP-16B (b4ff64f)
**Goal:** Add direct unit tests for business logic inside `backend/app/services/` without modifying production code.

---

## 1. Rationale

After WP-17A, endpoint coverage is comprehensive but still coupled to:
- Database state
- Router wiring
- FastAPI request/response serialization

WP-17B adds a second test tier (`tests/test_services/`) that calls service functions directly with mocked connections. This catches regressions in:
- Row-mapping compatibility logic
- JSON coercion and legacy fallbacks
- Pure calculations (tax, duty, numbering)
- State-transition guards
- Validation logic

---

## 2. Scope

**New test directory:** `backend/tests/test_services/`

**Target modules:**
- `backend/app/services/customer.py`
- `backend/app/services/resource.py`
- `backend/app/services/customs.py`
- `backend/app/services/document.py`
- `backend/app/services/shipping.py`
- `backend/app/services/invoice.py`
- `backend/app/services/supplier.py`

**Out of scope:**
- `backend/app/services/base.py` (infrastructure helpers; implicitly covered by integration tests)
- Any production code changes
- Router or schema tests

---

## 3. Shared Test Conventions

1. Use `unittest.mock.patch` to mock `app.services.base.connection` and `app.services.base.execute_update`.
2. Mock cursor methods (`execute`, `fetchone`, `fetchall`, `lastrowid`) as needed.
3. Prefer testing pure functions directly (`_customer_row_to_response`, `_invoice_row_to_response`, etc.).
4. Test both happy-path and error-path (ValueError raises).
5. Keep each test independent; use function-scoped fixtures or fresh mocks.
6. Do **not** modify any file inside `backend/app/`.

---

## 4. Patch Breakdown

### Patch-1: Customer Service Unit Tests

**New Files:**
- `backend/tests/test_services/test_customer_service.py`

**Acceptance Criteria:**
- `_customer_row_to_response` maps `company_name` → `name` and `contact_name` → `contact_person` when legacy columns are present
- `_customer_row_to_response` preserves mapped values when new columns are present
- `create_customer` inserts correct payload and returns expected dict shape
- `update_customer` raises `ValueError("Customer not found")` when record missing
- `delete_customer` calls `execute_update` with `extra_fields={"status": "inactive"}`
- `import_customers` rejects non-CSV filenames
- `import_customers` parses CSV rows and returns count

**Risk:** Low. Pure mapping and mocked DB calls.

**Estimated tests:** ~7

---

### Patch-2: Resource Service Unit Tests

**New Files:**
- `backend/tests/test_services/test_resource_service.py`

**Acceptance Criteria:**
- `_resource_row_to_response` falls back to `is_verified` when `is_active` is None
- `_resource_row_to_response` parses `metadata` from JSON string to dict
- `search_resources` builds query with 6 LIKE placeholders
- `create_resource` coerces metadata with `str()` before insert
- `update_resource` raises `ValueError("Resource not found")` when record missing

**Risk:** Low. Pure mapping and query-shape assertions.

**Estimated tests:** ~6

---

### Patch-3: Customs Service Unit Tests

**New Files:**
- `backend/tests/test_services/test_customs_service.py`

**Acceptance Criteria:**
- `calculate_duties` returns correct arithmetic for known HS code row
- `calculate_duties` raises `ValueError("HS Code not found")` when code missing
- `_customs_row_to_response` sets `destination_country` to `""` when None
- `create_declaration` generates declaration number matching `CD-YYYYMMDDHHMMSS`
- `submit_declaration` calls `execute_update` with `extra_fields={"status": "submitted", "submitted_at": ...}`

**Risk:** Low. Pure math and deterministic string formatting.

**Estimated tests:** ~6

---

### Patch-4: Document Service Unit Tests

**New Files:**
- `backend/tests/test_services/test_document_service.py`

**Acceptance Criteria:**
- `_document_row_to_response` maps legacy `type` column to `document_type` when `document_type` is None
- `_document_row_to_response` maps `description` column to `content`
- `upload_document` raises `ValueError` for non-PDF/JPG/PNG content types
- `upload_document` raises `ValueError` for files > 10MB
- `upload_document` returns expected dict shape for valid input
- `create_document` serializes metadata dict to JSON string before insert

**Risk:** Low. Pure mapping and validation logic.

**Estimated tests:** ~7

---

### Patch-5: Shipping Service Unit Tests

**New Files:**
- `backend/tests/test_services/test_shipping_service.py`

**Acceptance Criteria:**
- `get_rates` returns list of dicts with keys `carrier`, `service`, `estimated_days`, `cost`, `currency`
- `get_rates` cost formula is `base_rate * max(1, weight * 0.5) * distance_factor`
- `track_shipment` constructs `tracking_events` list with 3 entries
- `get_shipment` defaults `origin`/`destination` to `""` when None
- `create_shipment` generates tracking number matching `NK<YYYYMMDDHHMMSS><4 digits>`
- `get_label` returns deterministic URL using shipment_id

**Note:** `get_rates` uses `random.uniform`; tests should patch `random.uniform` to a fixed value for deterministic assertions.

**Risk:** Low. Deterministic with mocking.

**Estimated tests:** ~7

---

### Patch-6: Invoice Service Unit Tests

**New Files:**
- `backend/tests/test_services/test_invoice_service.py`

**Acceptance Criteria:**
- `_invoice_row_to_response` parses `items` from JSON string to list
- `_invoice_row_to_response` defaults `subtotal`, `total`, `tax_rate` when None
- `_invoice_row_to_response` falls back to `created_at` for `issue_date`
- `create_invoice` generates invoice number matching `INV-YYYYMMDD-XXXX`
- `create_invoice` calculates tax = `subtotal * (tax_rate / 100)` and total = `subtotal + tax`
- `validate_invoice` sets status to `validated`
- `cancel_invoice` raises `ValueError("Invoice already cancelled")` when already cancelled
- `cancel_invoice` raises `ValueError("Invoice not found")` when record missing

**Risk:** Low. Pure arithmetic and state guards.

**Estimated tests:** ~9

---

### Patch-7: Supplier Service Unit Tests

**New Files:**
- `backend/tests/test_services/test_supplier_service.py`

**Acceptance Criteria:**
- `_supplier_row_to_response` parses `certificates` from JSON string to list
- `_supplier_row_to_response` defaults `country` to `"Egypt"` when None
- `create_supplier` inserts with `type="general"` and coerces certificates
- `update_supplier` raises `ValueError("Supplier not found")` when record missing
- `delete_supplier` calls `execute_update` with `extra_fields={"status": "inactive"}`

**Risk:** Low. Pure mapping and mocked DB calls.

**Estimated tests:** ~6

---

## 5. Verification

After each patch:
- `cd backend && python -m pytest tests/test_services/ -v`
- Full suite: `cd backend && python -m pytest tests/ -v`
- Expected: all tests pass, total count increases by ~6–9 per patch.

After all patches:
- Total tests should be ~111–129 (69 existing + ~48–56 new).
- No production code changes; `git diff backend/app/` must be empty.

---

## 6. Execution Order

Apply patches sequentially:
1. Patch-1: Customer
2. Patch-2: Resource
3. Patch-3: Customs
4. Patch-4: Document
5. Patch-5: Shipping
6. Patch-6: Invoice
7. Patch-7: Supplier

Each patch is independently verifiable by running its test file alone.
