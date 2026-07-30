# Minimal Refactor Plan - Stage 2

## Goal
Replace all `Record<string, never>` response types in `frontend/src/types/api.d.ts` with proper TypeScript types by reusing existing schemas and creating minimal new response schemas only when necessary.

## Current State
- **29 endpoints** generate `Record<string, never>` responses
- **0 endpoints** generate `Record<string, any>`
- All problematic endpoints use `response_model=dict` in FastAPI

## Analysis

### Response Patterns Found

#### Pattern A: Simple Message Response
**Structure:** `{"message": "..."}`
**Count:** 13 endpoints
**Endpoints:**
- PUT /api/v1/auth/me → `update_me`
- PUT /api/v1/shipping/shipments/{shipment_id} → `update_shipment`
- POST /api/v1/invoices/{invoice_id}/validate → `validate_invoice`
- POST /api/v1/invoices/{invoice_id}/cancel → `cancel_invoice`
- PUT /api/v1/suppliers/{supplier_id} → `update_supplier`
- DELETE /api/v1/suppliers/{supplier_id} → `delete_supplier`
- PUT /api/v1/customers/{customer_id} → `update_customer`
- DELETE /api/v1/customers/{customer_id} → `delete_customer`
- PUT /api/v1/customs/declarations/{declaration_id} → `update_declaration`
- POST /api/v1/customs/declarations/{declaration_id}/submit → `submit_declaration`
- PUT /api/v1/resources/{resource_id} → `update_resource`
- DELETE /api/v1/resources/{resource_id} → `delete_resource`
- PUT /api/v1/documents/{document_id} → `update_document`
- DELETE /api/v1/documents/{document_id} → `delete_document`

**Solution:** Create one reusable `MessageResponse` schema in a shared location (e.g., `app/schemas/common.py`)

#### Pattern B: ID + Message Response
**Structure:** `{"id": int, "message": "..."}`
**Count:** 6 endpoints
**Endpoints:**
- POST /api/v1/suppliers/ → `create_supplier`
- POST /api/v1/customers/ → `create_customer`
- POST /api/v1/customs/declarations → `create_declaration`
- POST /api/v1/resources/ → `create_resource`
- POST /api/v1/documents/ → `create_document`
- POST /api/v1/documents/upload → `upload_document`

**Solution:** Create one reusable `IdResponse` schema with generic `id: int` field

#### Pattern C: Shipment Create Response
**Structure:** `{"id": int, "tracking_number": str, "message": "..."}`
**Count:** 1 endpoint
**Endpoints:**
- POST /api/v1/shipping/shipments → `create_shipment`

**Solution:** Create `ShipmentCreateResponse` schema in `app/schemas/shipment.py`

#### Pattern D: Register Response
**Structure:** `{"message": str, "user_id": int}`
**Count:** 1 endpoint
**Endpoints:**
- POST /api/v1/auth/register → `register`

**Solution:** Create `RegisterResponse` schema in `app/schemas/user.py`

#### Pattern E: Get Me Response
**Structure:** User fields dict (subset of `User` schema without `password_hash`, `created_at`, `updated_at`)
**Count:** 1 endpoint
**Endpoints:**
- GET /api/v1/auth/me → `get_me`

**Solution:** Create `UserProfileResponse` schema in `app/schemas/user.py` OR reuse `User` schema with `from_attributes=True` (current implementation returns dict, not ORM model)

#### Pattern F: Track Shipment Response
**Structure:** Shipment fields + `tracking_events: list[dict]`
**Count:** 1 endpoint
**Endpoints:**
- GET /api/v1/shipping/track/{tracking_id} → `track_shipment`

**Solution:** Create `ShipmentTrackingResponse` schema in `app/schemas/shipment.py`

#### Pattern G: Get Label Response
**Structure:** `{"shipment_id": int, "label_url": str, "message": str}`
**Count:** 1 endpoint
**Endpoints:**
- GET /api/v1/shipping/shipments/{shipment_id}/label → `get_label`

**Solution:** Create `LabelResponse` schema in `app/schemas/shipment.py`

#### Pattern H: Invoice Create Response
**Structure:** `{"id": int, "invoice_number": str, "message": str}`
**Count:** 1 endpoint
**Endpoints:**
- POST /api/v1/invoices/ → `create_invoice`

**Solution:** Create `InvoiceCreateResponse` schema in `app/schemas/invoice.py`

#### Pattern I: Get Invoice Status Response
**Structure:** Invoice row dict (subset of `Invoice` schema)
**Count:** 1 endpoint
**Endpoints:**
- GET /api/v1/invoices/{invoice_id}/status → `get_invoice_status`

**Solution:** Reuse `Invoice` schema with `from_attributes=True`

#### Pattern J: Import Customers Response
**Structure:** `{"message": str, "count": int}`
**Count:** 1 endpoint
**Endpoints:**
- POST /api/v1/customers/import → `import_customers`

**Solution:** Create `ImportResponse` schema in `app/schemas/customer.py` OR reuse `MessageResponse` with additional `count` field

## Execution Plan

### Phase 1: Create Reusable Schemas (3 new files)
1. **`backend/app/schemas/common.py`** - Shared response schemas
   - `MessageResponse` (message: str)
   - `IdResponse` (id: int, message: str)

2. **`backend/app/schemas/user.py`** - Add auth response schemas
   - `RegisterResponse` (message: str, user_id: int)
   - `UserProfileResponse` (subset of User fields)

3. **`backend/app/schemas/shipment.py`** - Add shipping response schemas
   - `ShipmentCreateResponse` (id: int, tracking_number: str, message: str)
   - `ShipmentTrackingResponse` (Shipment fields + tracking_events: list[dict])
   - `LabelResponse` (shipment_id: int, label_url: str, message: str)

4. **`backend/app/schemas/invoice.py`** - Add invoice response schemas
   - `InvoiceCreateResponse` (id: int, invoice_number: str, message: str)

5. **`backend/app/schemas/customer.py`** - Add customer import response
   - `ImportResponse` (message: str, count: int)

### Phase 2: Update Router response_models (1 file per router)
Apply `response_model` changes to:
- `backend/app/routers/auth.py` (3 endpoints)
- `backend/app/routers/shipping.py` (4 endpoints)
- `backend/app/routers/invoice.py` (5 endpoints)
- `backend/app/routers/suppliers.py` (3 endpoints)
- `backend/app/routers/customers.py` (4 endpoints)
- `backend/app/routers/customs.py` (3 endpoints)
- `backend/app/routers/resources.py` (3 endpoints)
- `backend/app/routers/documents.py` (4 endpoints)

**Total: 29 endpoint changes across 8 router files**

### Phase 3: Regenerate Frontend Types
1. Delete `frontend/src/types/api.d.ts`
2. Run `npm run types:api`
3. Verify all `Record<string, never>` are replaced

### Phase 4: Validation
1. Run backend tests: `pytest backend/tests/`
2. Run frontend build: `npm run build` (from frontend directory)
3. Verify OpenAPI schema contains all new schemas in `components.schemas`

## Constraints
- **No new schema files** - reuse existing files per domain
- **Minimal changes** - only add response schemas, don't modify existing ones
- **Backward compatible** - all existing tests must pass
- **No frontend code changes** - only regenerate types

## Priority Order
1. **High:** MessageResponse and IdResponse (covers 19 endpoints)
2. **High:** RegisterResponse, UserProfileResponse (covers 2 auth endpoints)
3. **Medium:** Shipment-related responses (covers 4 shipping endpoints)
4. **Medium:** Invoice-related responses (covers 2 invoice endpoints)
5. **Low:** ImportResponse (covers 1 customer endpoint)

## Risks
- Some endpoints return dynamic dict keys (e.g., `tracking_events`) - may need `Dict[str, Any]`
- `get_me` returns dict, not ORM model - may need manual schema definition
- Backward compatibility: existing frontend code may break if it relies on `Record<string, never>` behavior

## Validation Criteria
- [ ] All 29 endpoints have proper TypeScript types in `api.d.ts`
- [ ] No `Record<string, never>` remains in response schemas
- [ ] All backend tests pass (21/21)
- [ ] Frontend build succeeds
- [ ] OpenAPI schema includes all new response schemas
