# DEM Customers Domain Evolution — Final Work Package Plan

**Plan ID:** WP-CUSTOMERS-001  
**Plan File:** `.kilo/plans/1790175876138-dem-customers-domain-evolution.md`  
**Status:** Implementation-ready — corrected final plan  
**Branch:** main  
**Mode:** Plan-only — no application/database/test implementation in this turn

---

## 1. Objective

Evolve the existing Customers domain so it can safely store and use the current real-world importer/buyer datasets collected for DEM, while preserving the existing `Customer` entity and its current relationships.

The core business flow is:

**Country → Data Source → Buyer/Company → Products/HS → Contact Information → Activity/Evidence → Record Status → Later Enrichment**

The imported records are first-stage prospect/importer data. They are **not automatically verified customers, active importers, or current buyers** merely because they exist in a source.

The new work must make the Customers section fit the real datasets without forcing those datasets into the old six-column table.

---

## 2. Scope

### In scope

1. Extend the existing `Customer` domain rather than create a separate Importer domain.
2. Add first-class source/provenance and immutable raw-record preservation.
3. Support CSV and XLSX.
4. Support Excel workbooks with multiple data-bearing sheets and non-data sheets.
5. Provide import preview, table/header selection where needed, field mapping, validation, duplicate/conflict review, and explicit confirmation.
6. Store products/HS information without destructive flattening.
7. Store separate phone, mobile, WhatsApp, email, website, address, city, country values.
8. Preserve activity/evidence separately from CRM/customer status.
9. Provide country-first Customers browsing/filtering.
10. Provide a customer detail view with company, contacts, products, evidence, provenance, and raw source records.
11. Preserve Arabic/English UI through the existing i18n system.
12. Preserve existing Customer relationships with shipments, invoices, export workflows, contacts, and knowledge-graph references.
13. Keep a clean extension point for later verification, outreach, qualification, and enrichment, without implementing those workflows now.
14. Keep the legacy customer import route compatible only through the same new import pipeline; it must not remain a bypass that inserts unverified rows blindly.

### Out of scope

- Creating an `Importer`, `Buyer`, or `Prospect` SQL entity/domain as a second customer system.
- Rebuilding CRM architecture.
- WhatsApp automation.
- Outreach automation.
- Employee assignment/workflow automation.
- Qualification, scoring, ranking, lead scoring, or AI recommendations.
- Changes to DEM AI lifecycle, Knowledge Plane, reasoning, planning, orchestration, or agent architecture.
- Changes to Suppliers, Shipments, Invoices, Customs, Documents, or unrelated domains.
- Broad frontend modernization or a new design system.
- Automatic web research/enrichment of imported companies.
- Automatic claims that a company is currently active.
- Permanent storage of the uploaded binary workbook itself; the system stores source metadata and row-level raw data instead.
- Supporting legacy binary Excel formats such as `.xls` unless separately introduced later.

---

## 3. Current Repository Findings

### Backend

The existing `customers` table is a simple customer CRUD table with:

`name`, `name_en`, `contact_person`, `email`, `phone`, `address`, `city`, `country`, `tax_id`, `import_license`, `category`, `notes`, `status`, `created_at`.

The current customer service:

- imports CSV only;
- inserts every imported row directly;
- forces imported rows to `status="active"`;
- stores no source/provenance;
- stores no raw source row;
- performs no duplicate/conflict review;
- ignores important source fields that do not match the old schema.

The current router rejects non-CSV uploads.

The existing frontend Customers page is a small CRUD table with search, add/edit, and CSV import. It has no country selector, source display, product display, evidence display, raw-source view, or detail page.

An existing `contacts` table already supports `customer_id`, so it must not be replaced by another parallel contact architecture.

Existing operational relationships use `customers.id` and must remain unchanged.

### Database/migration finding

The project currently initializes SQLite schema through `_create_tables`, `ensure_columns`, `SchemaRegistry`, and `MigrationRunner`. The current migration runner already contains only the initial schema snapshot.

**Final rule:** one authoritative schema-definition path must be used for each new object.

The future implementation MUST NOT add the same `ALTER TABLE`/table-definition DDL both to `ensure_columns`/SchemaRegistry and to a versioned migration.

If a versioned migration is required for a data transformation/backfill, it must be data-only and idempotent. No duplicate DDL.

Alembic autogeneration is not to be introduced for this SQLite work package.

---

## 4. Data Model Principle

The model is divided into four layers:

**Source Batch → Raw Source Record → Normalized Customer/Children → Future Verification/Enrichment**

Important:

- Raw source data is immutable.
- Normalized values may be updated later.
- Verification/activity claims are separate from raw existence.
- Provenance belongs to the source/raw-record layer, not as a single source field on the Customer.

### Why provenance is not stored as a single source on `customers`

One customer can appear in multiple workbooks, sheets, sources, or later imports.

Therefore the Customer row must not contain a single `source_batch_id` that falsely implies one source is the complete origin.

The authoritative provenance is:

`customer_source_batches`
→ `customer_raw_records`
→ `normalized_customer_id`

A Customer may therefore have many raw source records and many source origins.

---

## 5. Target Database Model

### 5.1 Existing `customers` table

Retain all existing columns unchanged.

Add only the new fields that represent current Customer-level normalized information:

- `mobile`
- `whatsapp`
- `website`
- `data_status`
- `verification_status`
- `crm_status`
- `activity_status`
- `activity_window_start`
- `activity_window_end`
- `activity_window_label`

Do **not** add:

- `source_batch_id`
- duplicated `raw_data`
- `conflict_log`

Reason: source/raw/conflict history belongs to source/raw-record tables and must not be duplicated on the Customer row.

### 5.2 Status semantics

Existing `status` remains the legacy operational Customer status and MUST retain its current meaning.

New statuses have independent meanings:

#### `data_status`

Processing state only:

- `raw` — imported source row exists, but normalization is incomplete.
- `normalized` — source row was mapped into normalized Customer fields.
- `verified` — future verified state.
- `enriched` — future enriched state.

Import does not set `verified` or `enriched`.

#### `verification_status`

Truth/identity verification state:

- `unverified`
- `pending`
- `verified`
- `rejected`

Initial imported value: `unverified`.

#### `crm_status`

Commercial relationship state:

- `prospect`
- `active_customer`
- `inactive`

Initial imported value: `prospect`.

#### `activity_status`

Observed activity only:

- `unknown`
- `observed_active`
- `dormant`
- `not_observed`

Initial imported value: `unknown`.

**Critical rule:** absence of evidence MUST NOT be converted into `dormant` or `not_observed` unless the source explicitly supports that interpretation. Unknown remains unknown when no valid activity evidence is present.

### 5.3 Legacy/manual-record rule

Existing Customer records must retain their existing operational `status`.

The new status fields for legacy records MUST NOT be bulk-backfilled to values that make business claims.

For legacy records, new fields may remain NULL/unspecified until their semantics can be established safely.

Manual Customer creation must not be forced through the importer-specific prospect classification unless the user explicitly creates the record through the new prospect/import flow.

---

## 6. New Table: `customer_source_batches`

Purpose: one record for each ingestion/preview/import run.

Fields:

- `id` PK
- `source_type` — `file`, `web`, `api`, `manual`
- `source_format` — `xlsx`, `csv`, or NULL when not file-based
- `source_name` — e.g. Volza, official government dataset, company site
- `source_reference` — stable human/reference identifier
- `source_url` — optional
- `file_name` — optional
- `row_count`
- `success_count`
- `skip_count`
- `error_count`
- `status`
- `mapping_metadata` JSON
- `imported_at`
- `imported_by`
- `expires_at` for preview batches
- `created_at`

### Batch states

- `preview`
- `confirmed`
- `partial`
- `failed`
- `cancelled`
- `expired`

Preview batches MUST NOT remain indefinitely.

A cleanup path must remove/mark expired preview data so abandoned imports do not accumulate as active data.

---

## 7. New Table: `customer_raw_records`

Purpose: immutable preservation of every imported source row.

Fields:

- `id` PK
- `batch_id` FK
- `sheet_name` — NULL for CSV
- `row_number`
- `raw_data` JSON/TEXT — complete original row
- `normalized_customer_id` nullable FK
- `validation_errors` JSON/TEXT
- `conflict_resolution`
- `conflict_details` JSON/TEXT
- `created_at`

Rules:

1. `raw_data` is never overwritten by normalization.
2. Every selected input row is represented by one raw-record row.
3. Raw rows may exist without a Customer when validation or conflict review has not completed.
4. Raw records are retained even after the Customer becomes inactive.
5. Do not copy `raw_data` into `customers`; that creates two competing truths.

---

## 8. New Table: `customer_products`

Purpose: normalized product/import identity linked to a Customer.

Fields:

- `id` PK
- `customer_id` FK
- `raw_record_id` nullable FK
- `product_description`
- `hs_code`
- `hs_code_description`
- `quantity` nullable
- `unit` nullable
- `created_at`

Rules:

- A Customer may have multiple products/HS codes.
- Do not concatenate multiple products into one Customer text field when a source provides separable product records.
- Quantity/unit are stored only when they are explicitly attributable to the company/product observation; they are not inferred.
- Product records may be source-linked through `raw_record_id`.

---

## 9. New Table: `customer_evidence`

Purpose: preserve source-specific activity/evidence without turning evidence into a CRM status.

Fields:

- `id` PK
- `customer_id` FK
- `raw_record_id` nullable FK
- `evidence_type`
- `evidence_data` JSON/TEXT
- `observed_at` nullable
- `activity_window_start` nullable
- `activity_window_end` nullable
- `activity_window_label` nullable
- `created_at`

Allowed evidence types initially:

- `shipment`
- `activity`
- `source_specific`
- `verification`

Verification evidence may be stored for future use, but no verification workflow is implemented in this WP.

The system must preserve source wording/timeframes when available and MUST NOT rewrite a source's activity period into a claim of current 2026 activity.

---

## 10. Contacts

Use the existing Customer contact relationship.

For the common first-stage business-contact fields, store:

- `email`
- `phone`
- `mobile`
- `whatsapp`
- `website`

Do not assume:

- mobile = WhatsApp
- phone = mobile
- website = source of activity

Only populate the specific channel represented by the source.

The existing `contacts` table remains available for named people and later enrichment.

---

## 11. Provenance

The provenance chain is:

```
customer_source_batches
    └── customer_raw_records
            └── normalized_customer_id → customers
                    ├── customer_products
                    └── customer_evidence
```

The Customer detail view derives its source list from linked raw records and their batches.

Each imported Customer must be able to show:

- source name
- source type/format
- source URL when available
- source file name when applicable
- Excel sheet when applicable
- source row number
- imported by
- imported date
- original raw row

The source must remain visible even after normalization.

---

## 12. Raw vs Normalized Strategy

### Raw

Authoritative source representation.

### Normalized

Structured fields used by Customers UI and downstream business functions.

### Verified/Enriched

Future states only.

The importer may create a normalized Customer while retaining `data_status='normalized'`; that does NOT mean the company is verified, active, or currently importing.

When normalization cannot safely determine a value, the raw source value remains preserved and the normalized field remains empty rather than inventing a value.

---

## 13. Import Architecture

### Supported inputs

- CSV
- XLSX

Do not support `.xls` in this WP.

### File validation

The future implementation must:

- normalize and validate the file extension;
- reject unsupported formats;
- enforce a configurable maximum upload size;
- reject corrupted/unreadable workbooks;
- reject empty datasets;
- never trust filename/MIME type alone as proof of file format;
- never execute workbook formulas/macros.

For XLSX, use a real XLSX parser such as `openpyxl`. Do not rename/convert the file to CSV.

For CSV, preserve the existing CSV capability and make it robust to UTF-8 BOM/standard UTF-8.

---

## 14. Excel Workbook Handling

This is important because the existing country workbooks are not simple single-table files.

Some workbooks contain:

- market snapshots
- methodology/rules
- core buyer rows
- supplementary buyers
- conflict/anomaly sheets
- source lists
- multiple data sections

Therefore:

1. List workbook sheets before import.
2. Identify likely data-bearing sheets without automatically importing non-data sheets.
3. Allow the employee to select one or more data-bearing sheets.
4. For each selected sheet, allow the employee to choose/confirm the header row or table region when the sheet contains introductory metadata before the table.
5. Preserve sheet name and source row numbers.
6. Do not turn summary/methodology rows into Customers.
7. When a workbook contains several independent tables, each table must be mapped separately or explicitly skipped.

A preview must make this visible before confirmation.

---

## 15. Import Wizard

The new import path is a staged process:

### Step 1 — Upload

- CSV/XLSX file selection.
- File validation.
- Source metadata capture.
- For XLSX: sheet discovery.

### Step 2 — Select Data

- Select one or more data-bearing sheets.
- Confirm/choose table header/data region where required.

### Step 3 — Preview & Map

Show a small preview, not the whole file.

Mapping must support target categories:

- Customer field
- Product field
- Evidence field
- Contact field
- Ignore

The system may suggest mappings using an explicit alias dictionary, but the employee remains able to correct them.

No mapping suggestion may invent data.

### Step 4 — Validate

Validate:

- required identity fields
- country presence/consistency
- supported field formats
- malformed email when email exists
- obvious blank rows
- duplicate candidates
- unmapped source columns
- invalid/ambiguous product/HS values

Warnings are distinct from blocking errors.

### Step 5 — Review Conflicts

Show:

- rows matching existing Customers
- conflicting company information
- source/location contradictions
- duplicate candidates within the batch

The employee must be able to choose the resolution.

### Step 6 — Confirm

Commit the normalized records and child rows atomically as appropriate.

Update batch counts/status.

---

## 16. Preview/Staging Safety

The preview endpoint may create a `customer_source_batches` row and corresponding `customer_raw_records` so that the confirmation step can operate on the reviewed dataset.

However:

- preview data is not considered imported/confirmed Customer data;
- the batch remains `preview` until confirmation;
- abandoned previews expire/cancel;
- expiration cleanup removes or marks preview-only records inactive;
- confirmation is atomic for the selected batch;
- a failed confirmation must not leave half-created Customers/products/evidence.

The implementation must not rely on an in-memory Python object surviving between HTTP requests.

---

## 17. Duplicate & Conflict Strategy

The old rule of `name + country` as an automatic merge key is insufficient and must not be used as a silent merge rule.

Matching signals should be evaluated in this order:

1. exact stable business identifiers when available (e.g. tax/import identifier);
2. exact normalized email;
3. exact normalized phone/mobile;
4. exact normalized website/domain;
5. normalized company name + country as a duplicate candidate, not automatic identity proof.

### Default behavior

**Do not automatically merge a weak match.**

For a high-confidence match, the importer may link the raw record to the existing Customer while preserving the new raw evidence.

For ambiguous matches, require an explicit employee choice:

- Link to existing Customer
- Create new Customer
- Skip row

Never alter the legal/company name by appending `(2)`, `(3)`, etc.

Never silently overwrite existing non-null values.

When new source values conflict with existing values:

- retain the new source value in raw data;
- preserve the existing normalized value unless explicit resolution changes it;
- record the conflict on the raw-record resolution metadata;
- never erase either side.

There is no `conflict_log` column on Customer.

---

## 18. Import Idempotency

Re-importing the same source batch must not blindly create another copy of every company.

The implementation must distinguish:

- same source row already confirmed
- same company from a different source
- possible duplicate company
- genuinely new company

The batch/source identity and source row identity must be available for this purpose.

The system should not use the company name alone as a global unique key.

---

## 19. Country-First Customers UI

Customers page must provide:

### Primary controls

- Country selector
- Search
- Clear filters

Country filter is server-side.

The UI must show the selected country's records without requiring manual country text entry.

A lightweight country list endpoint or equivalent server-side distinct-country query may be added.

### List view

Show only lightweight summary fields, for example:

- Company
- Country
- Main contact channel(s)
- Product summary
- Data status
- CRM status
- Activity status
- Source

Do NOT load complete raw JSON/products/evidence for every row in the list endpoint.

The list endpoint must remain paginated.

---

## 20. Customer Detail View

Selecting a Customer opens a detail view/panel.

Sections:

### Company

- Name
- English name where available
- Contact person
- Category
- Address
- City
- Country
- Existing tax/import fields where available

### Contact

- Phone
- Mobile
- WhatsApp
- Email
- Website

### Products / Imports

- Product description
- HS/HSN
- HS description
- Quantity/unit only when source-supported

### Activity / Evidence

- evidence type
- source evidence
- observed date
- activity window
- source reference

### Provenance

- Source
- File
- Sheet
- Row
- Source URL
- Imported by
- Imported at

### Raw Source

Collapsible source-row viewer.

Raw values are displayed as stored; no fabricated normalized replacements are shown as if they were original source values.

---

## 21. Status Display Rules

The UI must clearly distinguish:

- Operational customer status
- Data status
- Verification status
- CRM status
- Activity status

Do not label an imported prospect simply as “Active” because the legacy `status` field defaults to active.

For imported prospects:

- legacy operational `status` must not be used to imply current import activity;
- `crm_status='prospect'`
- `verification_status='unverified'`
- `activity_status='unknown'` unless source evidence explicitly supports an observed state.

---

## 22. Manual Add/Edit

Keep the existing customer CRUD capabilities.

Extend add/edit only for the current data fields that are genuinely part of this WP:

- mobile
- WhatsApp
- website
- other existing customer fields as applicable

Source batch/raw fields are system-managed and must not be manually edited.

Future qualification/evaluation fields are not introduced now.

---

## 23. API Design

### Existing routes

Keep current routes for compatibility.

Extend responses without breaking old fields.

### New routes

`POST /api/v1/customers/import/preview`  
Create preview batch and return sheet/table candidates, sample rows, detected columns, and mapping suggestions.

`POST /api/v1/customers/import/confirm`  
Confirm a staged batch using the selected mapping/resolutions.

`POST /api/v1/customers/import/cancel`  
Cancel an unconfirmed preview batch.

`GET /api/v1/customers/countries`  
Return available customer countries for the country filter.

`GET /api/v1/customers/source-batches`  
List source/import batches.

`GET /api/v1/customers/{id}`  
Return full Customer detail plus products/evidence/provenance summary.

`GET /api/v1/customers/{id}/products`

`POST /api/v1/customers/{id}/products`

`DELETE /api/v1/customers/{id}/products/{product_id}`

`GET /api/v1/customers/{id}/evidence`

`POST /api/v1/customers/{id}/evidence`

### Important response separation

Do not use one oversized Pydantic `Customer` response model containing create models for Products/Evidence.

Use separate response models for:

- Customer list item
- Customer detail
- Product response
- Evidence response
- Source/batch response
- Raw record response
- Import preview response
- Import validation/confirmation response

Lists must remain lightweight; detail endpoints load children.

### File request schemas

Do not put `UploadFile` inside a normal Pydantic JSON request model.

The router receives `UploadFile`; the confirm request carries only staged-batch data such as batch ID, selected mapping, and explicit conflict resolutions.

---

## 24. Pydantic/Data Contract Rules

Use explicit response/input models.

Do not use mutable list defaults such as `=[]`.

Use safe default factories where lists are required.

Do not inherit `CustomerUpdate` from a required-field `CustomerBase`.

`CustomerUpdate` must remain independently optional for partial updates.

Raw JSON stored in SQLite TEXT must be serialized/deserialized consistently.

Enum-like statuses must have a single validated definition so router/service/schema values cannot diverge.

---

## 25. Service-Layer Structure

Refactor the current importer into focused service operations:

- parse source
- inspect workbook/sheets
- detect/validate table region
- suggest mapping
- create preview batch
- validate raw rows
- detect duplicate candidates
- apply explicit conflict resolutions
- create/link normalized Customer
- create product rows
- create evidence rows
- finalize/cancel/expire batch

The existing simplified import function must delegate to this pipeline or be removed only after its callers are migrated.

No second customer service architecture.

---

## 26. Authorization & Audit

Use the existing role model.

Read access follows the existing authenticated customer access behavior.

Create/update/import operations preserve current allowed roles.

Delete remains the existing soft-deactivation behavior and must not hard-delete the raw/provenance trail.

Audit events must cover:

- preview created
- import confirmed
- import cancelled/expired
- customer created by import
- customer updated
- product/evidence changes

Audit records must not copy the complete raw row or full contact dataset into audit details.

---

## 27. Database Implementation Strategy

### Authoritative schema path

Follow the project's existing SQLite startup/schema mechanism.

For each new table:

- define creation once in the table-creation path;
- register the schema once with `SchemaRegistry`;
- use `ensure_columns` for additive missing columns where required.

Do not repeat identical DDL in `INITIAL_MIGRATIONS`.

If a versioned migration is necessary for an actual data transformation, add only an idempotent data transformation and document why it cannot be handled by the existing additive schema mechanism.

### Indexes

Add appropriate indexes for:

- `customers.country`
- `customers.data_status`
- `customers.verification_status`
- `customers.crm_status`
- `customers.activity_status`
- `customer_raw_records.batch_id`
- `customer_raw_records.normalized_customer_id`
- `customer_products.customer_id`
- `customer_evidence.customer_id`

Do not add speculative indexes unrelated to this WP.

---

## 28. Legacy Compatibility

Existing rows must continue to load without errors.

Existing relationships through `customers.id` remain unchanged.

No existing customer/invoice/shipment relationship is migrated to a new entity.

No existing Customer name, status, contact, or relationship is rewritten during schema migration.

**No bulk backfill may demote or reinterpret existing Customers.**

---

## 29. i18n

Use the existing `react-i18next` system.

Add all new Customer labels/messages to both:

- `frontend/src/locales/en/translation.json`
- `frontend/src/locales/ar/translation.json`

Do not hard-code new user-facing text in Customers components.

Include translations for:

- source/provenance
- raw data
- products/HS
- evidence
- import wizard
- validation
- conflicts
- data/verification/CRM/activity statuses
- country selector
- sheet/table selection
- import results

Arabic layout must remain usable in RTL.

Do not invent Arabic company names where only an English source value exists.

---

## 30. Testing Strategy

### Backend service tests

Test:

- CSV parsing
- XLSX parsing
- multiple-sheet handling
- non-data sheet exclusion
- header/table-region selection
- raw row preservation
- mapping
- validation
- email validation
- duplicate candidate detection
- explicit link/create/skip resolution
- conflict preservation
- products/HS
- evidence/activity windows
- source/provenance
- preview lifecycle
- confirm lifecycle
- cancellation/expiry
- atomic failure behavior
- status separation
- lightweight list response vs detailed response

### API tests

Test:

- CSV preview
- XLSX preview
- confirmation
- cancellation
- country filter
- countries endpoint
- detail response
- product/evidence endpoints
- role authorization
- legacy import route delegation
- unsupported file rejection
- corrupted XLSX rejection

### Frontend tests

Test:

- country selector
- server-side filtering
- import wizard steps
- multi-sheet selection
- preview/mapping
- validation/conflict review
- detail view
- provenance display
- raw viewer
- Arabic/English rendering
- RTL layout
- no-data/loading/error states

### Fixtures

Use small synthetic CSV/XLSX fixtures that intentionally cover:

- multiple sheets
- metadata before a header
- supplementary/non-data sheet
- Arabic/English headers
- duplicate companies
- conflicting contact values
- product/HS rows
- activity windows
- blank/invalid rows

A test fixture must not depend on paid external Volza access.

---

## 31. Acceptance Criteria

1. Customer remains the only core entity.
2. Existing shipments/invoices/export workflows continue to reference the same `customers.id`.
3. Imported records can represent the current buyer/importer datasets without forcing them into the old six-field UI model.
4. CSV and XLSX both work.
5. XLSX supports multiple sheets and explicit data-region/header selection where required.
6. Non-data workbook sheets/summary rows are not silently converted into Customers.
7. Every imported source row is preserved immutably in `customer_raw_records`.
8. A Customer can have records from multiple source batches.
9. Provenance is queryable from the Customer detail view.
10. Products/HS codes are stored without destructive flattening.
11. Phone/mobile/WhatsApp/email/website remain distinct.
12. Activity evidence is separate from CRM status.
13. Missing activity evidence remains unknown rather than becoming a false negative.
14. Existing `active/inactive` status is not used as importer verification.
15. Duplicate matching never silently merges weak matches.
16. Company names are never modified with artificial suffixes for duplicate handling.
17. Conflicting source values are preserved rather than silently overwritten.
18. Preview data does not become confirmed Customer data until confirmation.
19. Abandoned previews expire/cancel and do not accumulate indefinitely.
20. Existing Customers are not bulk-demoted or reclassified.
21. List responses remain paginated/lightweight.
22. Detail responses expose full products/evidence/provenance/raw source.
23. All new UI strings work in Arabic and English.
24. No AI, scoring, qualification, outreach, or unrelated architectural changes are introduced.
25. All existing Customer tests remain green, with new tests covering the new behavior.

---

## 32. Future Code-Phase Sequence

### Phase 1 — Schema foundation

- Add only the required Customer-level fields.
- Create source batches, raw records, products, and evidence tables.
- Register schema once.
- Add indexes.
- Do not add duplicate migration DDL.

### Phase 2 — Import core

- Add XLSX parser.
- Implement workbook/sheet/table-region inspection.
- Implement preview/staging.
- Implement mapping/validation.
- Implement duplicate candidate detection and explicit resolution.
- Implement atomic confirmation/cancellation/expiry.

### Phase 3 — Customer APIs

- Extend Customer schemas.
- Add dedicated response models.
- Add country/source/product/evidence endpoints.
- Preserve existing route compatibility.

### Phase 4 — Customers UI

- Country-first browsing.
- Lightweight customer list.
- Import wizard.
- Detail view.
- Provenance/raw source display.
- Products/evidence display.
- Arabic/English.

### Phase 5 — Verification

- Run targeted backend tests.
- Run targeted frontend tests.
- Run existing Customer regression tests.
- Run relevant full suites.
- Verify no unrelated domain regressions.

### Phase 6 — Rollout gate

Only after the above passes should the first real country workbooks be imported.

The eight country datasets are **data onboarding after this WP**, not part of the code/schema design itself.

---

## 33. Final Architectural Guardrails

- Keep `Customer` as the sole core customer entity.
- No `Importer` table.
- No `Buyer` table.
- No parallel CRM.
- No second provenance system.
- No duplicate raw-data storage.
- No single-source column pretending to represent all provenance.
- No automatic verification.
- No automatic activity claim.
- No automatic weak-match merge.
- No destructive overwrite.
- No artificial company-name suffix for duplicates.
- No backfill that changes the meaning of existing Customers.
- No duplicate schema/migration DDL.
- No oversized list payloads.
- No `UploadFile` inside JSON Pydantic models.
- No mutable list defaults.
- No hard-coded new UI labels.
- No AI/decision/reasoning logic.
- No WhatsApp automation.
- No outreach automation.
- No broad frontend redesign.
- No unrelated domain changes.

---

## 34. Final Decision

This Work Package solves exactly one problem:

**Make the existing Customers domain capable of safely storing and using the importer/buyer datasets we are collecting now, while preserving source identity, raw evidence, contact/product information, country-first access, and future enrichment readiness — without falsely turning raw prospects into verified customers.**

This plan is implementation-ready only after the above rules are respected.

**No application implementation is performed by this plan-only artifact.**
