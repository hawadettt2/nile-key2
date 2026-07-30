# Phase 5 — Frontend Pages Forensic Audit (Plan)

## Scope
All frontend page components only (`frontend/src/pages/*.tsx`):
Customers, Suppliers, Customs, Dashboard, Documents, Invoices, Login, Profile, Resources, Shipments.

Backend/OpenAPI (`openapi_current.json`) is the contract. API Layer is CERTIFIED (out of scope); `services/api.ts` signatures inspected only where needed to prove a page defect.

## Methodology
Reviewed one page at a time. For every page, compared:
- API function arguments against `services/api.ts` signatures.
- Request payload field names + required fields against the OpenAPI contract schemas.
- Response field names used in render against the OpenAPI response schemas.
- List endpoints confirmed to return raw arrays (pages use `res.data` directly — correct).

## VERIFIED FINDINGS

### F-P5-01 — Invoices create/update omit contract-required `total` field

- File: `frontend/src/pages/Invoices.tsx`
- Function: `handleSubmit` (create + update branch)
- Evidence:
  - `form` state initializer (line 19) contains `subtotal, tax_rate, currency, issue_date, due_date, notes, items` — **no `total`**.
  - Line 54: `await updateInvoice(editingId, { ...form, items: form.items.map(i => ({ ...i, total: i.quantity * i.unit_price })) });` — payload has no `total`.
  - Line 56: `await createInvoice({ ...form, items: form.items.map(i => ({ ...i, total: i.quantity * i.unit_price })) });` — payload has no `total`.
  - Contract `InvoiceCreate.required` (openapi_current.json) = `['subtotal', 'total', 'issue_date', 'items']`.
  - `services/api.ts:114` `createInvoice(data)` forwards `data` verbatim to `POST /api/v1/invoices`; `updateInvoice` likewise.
  - `total` is computed locally (line 72: `const total = form.items.reduce((s, i) => s + i.total, 0)`) and used only for display, never added to the payload.
- Execution path: user submits invoice form → `handleSubmit` → `createInvoice({...form, items})` (missing `total`) → `POST /api/v1/invoices` → backend returns **HTTP 422 Validation Error** (missing required `total`) → `catch` → `alert('Error')`. Invoice is not created/updated.
- Impact: The "Add Invoice" and "Edit Invoice" features are completely non-functional; every submission fails with 422.
- Confidence: VERIFIED
- Minimal fix (one file, non-architectural):
  - Line 54: `await updateInvoice(editingId, { ...form, total, items: form.items.map(i => ({ ...i, total: i.quantity * i.unit_price })) });`
  - Line 56: `await createInvoice({ ...form, total, items: form.items.map(i => ({ ...i, total: i.quantity * i.unit_price })) });`
  - (`total` is the already-computed local const from line 72; satisfies the contract's required `total`.)

## NOT VERIFIED (investigated, rejected)

- **Dashboard** — card label `t('dashboard.activeShipments')` displays `stats.shipments` (total count). Cosmetic wording mismatch, not a runtime/contract defect. Rejected.
- **Profile** — `updateProfile(form)` sends `email`; contract `UserUpdate` has no `email` prop, so the backend drops it. The update still succeeds for `full_name`/`phone`/`company`. This is a contract limitation surfaced by the page, not a page runtime-breaking defect. Rejected.
- **Customers, Suppliers, Customs, Documents, Login, Resources, Shipments** — all field names, required fields, and response shapes match the contract. No defect. (Shipments `getShippingRates` relies on the CERTIFIED API-Layer fix and passes `rateForm` matching `ShippingRateRequest` required fields `origin, destination, weight`.)

## Execution Plan (implementation-capable session)

1. Apply minimal fix F-P5-01 in `frontend/src/pages/Invoices.tsx` (lines 54 and 56).
2. Verify: `npm run lint` and `npm run build` (type check) pass; no frontend test suite exists.
3. Create ONE standalone commit, e.g. `fix: include required total field in invoice create/update`.
4. No other page requires changes. After F-P5-01 is fixed and committed, the Frontend Pages audit scope is CERTIFIED.

## Final Verdict
One verified defect (F-P5-01) remains in the Frontend Pages audit scope. All other pages conform to the contract. No new Phase may begin until F-P5-01 is fixed and the pages scope is certified.
