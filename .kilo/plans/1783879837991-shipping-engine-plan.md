# WP-20 — Shipping Engine Implementation Plan

**Reference:** PLAN.md (Master Roadmap v2.1)  
**Phase:** 1.5 — Business Logic Re-alignment  
**Status:** Ready for Implementation  
**Decisions:** All confirmed — 2026-07-12

---

## 1. Executive Summary

WP-20 transforms the existing Shipping Engine stub in Nile Key into a production-grade, provider-agnostic shipping integration platform. The design follows the **Extract → Redesign → Integrate** methodology, using `erpnext-shipping` as the functional reference and `WP-19 (ETA Engine)` as the architectural blueprint.

**Core principle:** Shipping Engine is a **Core Domain**, not a feature add-on.

**Target outcomes:**
- Real LetMeShip + SendCloud integrations (rates, booking, labels, tracking)
- Provider abstraction layer supporting future carriers
- Retry + error handling matching ETA Engine quality
- 40+ tests (unit + integration)
- Scheduler for automated tracking updates
- Full compatibility with existing Nile Key schemas and routers

---

## 2. Architecture Extraction Report (from erpnext-shipping)

### 2.1 Reference Architecture
```
erpnext-shipping (Frappe App)
├── erpnext_shipping/
│   ├── __init__.py
│   ├── hooks.py                 # Frappe hooks (scheduler, doc_events)
│   ├── utils.py                 # Shared utilities (address, contact, validation)
│   ├── shipping.py              # Core orchestration (rates, create, label, tracking)
│   ├── doctype/
│   │   ├── letmeship/
│   │   │   └── letmeship.py     # LetMeShip provider (Document + Utils)
│   │   ├── sendcloud/
│   │   │   └── sendcloud.py     # SendCloud provider (Document + Utils)
│   │   ├── parcel_service/
│   │   ├── parcel_service_type/
│   │   └── parcel_service_type_alias/
│   └── config/
└── ...
```

### 2.2 Key Architectural Patterns
1. **Provider Registry Pattern:** Enabled providers discovered via `frappe.db.get_single_value("LetMeShip", "enabled")`
2. **Orchestrator Function:** `fetch_shipping_rates()` and `create_shipment()` aggregate results from enabled providers
3. **Document-Centric:** Frappe DocType `Shipment` is the central aggregate root
4. **Side Effects on Related Docs:** Delivery Note fields updated via `db_set` after shipment creation/tracking
5. **Scheduled Tracking:** Daily `update_tracking_info_daily()` job polls all booked shipments
6. **Error Isolation:** Provider exceptions caught per-provider; other providers still return results
7. **Custom Fields Injection:** Shipping fields injected into Delivery Note via `custom_fields.py`
8. **Validation Hooks:** `validate_phone` hooked into Shipment DocType `validate` event

### 2.3 What We Do NOT Copy
- Frappe ORM / DocType / DocEvents
- `frappe.throw` / `frappe.msgprint` (replace with HTTP exceptions + logging)
- `frappe.get_single` (replace with `shipping_providers` table + registry)
- `frappe.db.get_value` (replace with SQL queries or service layer lookups)
- `File` attachment API (replace with file storage path or streaming endpoint)

---

## 3. Business Rules Report

### 3.1 Rate Calculation
- **Trigger:** User requests rates with origin, destination, weight, optional dimensions/value
- **Rule:** Each enabled provider returns its own rate list; results merged and sorted by total price
- **Validation:** Parcels must have length, width, height > 0 for LetMeShip; SendCloud warns on partial dimensions
- **Currency:** Provider returns its own currency (EUR for LetMeShip, varies for SendCloud)

### 3.2 Shipment Creation
- **Trigger:** User selects a rate and confirms shipment
- **Rule:** Exactly one provider creates the shipment based on selected `service_info`
- **Validation:**
  - Pickup contact required (Company or Individual)
  - Phone must be E.164 format (`+` followed by digits)
  - Parcel dimensions required for LetMeShip
  - Address title truncated to 30 chars for LetMeShip
- **Side Effect:** On success, local `shipments` record updated with `service_provider`, `carrier`, `shipment_id`, `awb_number`, `status = "Booked"`

### 3.3 Label Generation
- **Trigger:** User requests label print
- **Rule:** Provider-specific label retrieval; stored as attachment (reference) or returned as stream (Nile Key)
- **Multiple Parcels:** SendCloud supports multi-parcel labels; returns list of URLs

### 3.4 Tracking
- **Trigger:** Manual update or daily scheduler
- **Rule:** Poll provider for tracking data; update local `shipments` record and linked Delivery Notes
- **Status Mapping:** Provider-specific statuses mapped to local statuses (Delivered, Returned, Lost, In Progress)

### 3.5 Pickup Workflow
- **Company Pickup:** Contact resolved from `User` record
- **Individual Pickup:** Contact resolved from `Contact` record
- **Required Fields:** first_name, last_name, email, phone (E.164)

### 3.6 Cancellation
- **Trigger:** Partial failure in SendCloud multi-parcel creation, OR explicit user request
- **Rule:** If any parcel fails, successfully created shipments are cancelled automatically to maintain consistency
- **User-initiated cancel:** Allowed when shipment is in `booked` or `pending` state
- **Provider support:** SendCloud supports cancel; LetMeShip cancel not implemented in reference (handled gracefully)
- **Failure handling:** If provider cancel fails, mark locally as `cancellation_failed` for manual intervention (Confirmed: Option A)

---

## 4. Domain Model Report

### 4.1 Core Aggregates
| Aggregate | Responsibility |
|-----------|---------------|
| `Shipment` | Central record — origin, destination, weight, status, tracking, links to provider |
| `ShippingProvider` | Configuration for LetMeShip / SendCloud (API keys, environment, enabled flag) |
| `ParcelTemplate` | Reusable parcel dimension/weight templates |
| `ShippingLabel` | Generated label metadata (URL/path, provider, shipment_id) |
| `ShippingLog` | Audit log for provider API calls, errors, responses |

### 4.2 Entities
```
shipping_providers
├── id
├── name (unique, e.g., "LetMeShip", "SendCloud")
├── provider_type
├── environment (Pre-Production / Production)
├── enabled (bool)
├── is_default (bool)
├── config (JSON — non-sensitive settings only)
├── status
├── created_at / updated_at / created_by
```
**Note:** `api_key` and `api_secret` are NOT stored in this table. Credentials come exclusively from environment variables. The `config` column stores only non-sensitive metadata such as timeout, retry count, and display preferences.

### 4.3 Value Objects
- `Parcel`: length, width, height, weight, count, description
- `ShippingAddress`: title, line1, line2, city, pincode, country, country_code
- `ShippingContact`: first_name, last_name, email, phone, phone_prefix, title, gender
- `ShippingRate`: carrier, service, estimated_days, cost, currency, is_preferred
- `TrackingEvent`: status, location, timestamp

---

## 5. Shipment State Machine

```
pending ──→ booked ──→ in_transit ──→ delivered
   │           │            │
   │           │            ├──→ returned
   │           │            └──→ lost
   │           └──→ cancelled
   └──→ cancelled (before booking)
```

**States:**
- `pending`: Local record created, not yet booked with provider
- `booked`: Provider confirmed shipment, AWB assigned
- `in_transit`: Provider reports in transit
- `delivered`: Provider reports delivered
- `returned`: Provider reports returned
- `lost`: Provider reports lost
- `cancelled`: Cancelled locally or by provider

**Transitions:**
- `pending` → `booked`: Provider `create_shipment` success
- `booked` → `in_transit`: Tracking update shows in transit
- `booked` → `cancelled`: Local cancel or provider cancel
- `in_transit` → `delivered`: Tracking update shows delivered
- `in_transit` → `returned`: Tracking update shows returned
- `in_transit` → `lost`: Tracking update shows lost

---

## 6. Provider Abstraction

### 6.1 Abstract Provider Interface
```python
class ShippingProvider(ABC):
    @abstractmethod
    def get_available_services(self, request: RateRequest) -> list[ShippingRate]: ...
    
    @abstractmethod
    def create_shipment(self, request: CreateShipmentRequest) -> ShipmentResult: ...
    
    @abstractmethod
    def get_label(self, shipment_id: str) -> LabelResult: ...
    
    @abstractmethod
    def get_tracking_data(self, shipment_id: str) -> TrackingResult: ...
    
    @abstractmethod
    def cancel_shipment(self, shipment_id: str) -> CancelResult: ...
```

### 6.2 Registry
```python
PROVIDERS: dict[str, ShippingProvider] = {}

def register_provider(name: str, provider: ShippingProvider) -> None: ...
def get_provider(name: str) -> ShippingProvider: ...
def get_enabled_providers() -> list[ShippingProvider]: ...
```

### 6.3 Concrete Providers
- `LetMeShipProvider` — OAuth-like basic auth, JSON payloads, EUR currency
- `SendCloudProvider` — API key/secret auth, JSON payloads, multi-parcel support

---

## 7. Carrier Integrations

### 7.1 LetMeShip
- **Base URL:** `https://api.letmeship.com/v1` (prod) / `https://api.test.letmeship.com/v1` (test)
- **Auth:** Basic Auth (`api_id`, `api_password`)
- **Endpoints:**
  - `POST /available` — rates
  - `POST /shipments` — create shipment
  - `GET /shipments/{id}` — get AWB
  - `GET /shipments/{id}/documents?types=LABEL` — label
  - `GET /tracking?shipmentid={id}` — tracking
- **Special Rules:**
  - Address title max 30 chars
  - Phone prefix extracted (first 3 chars)
  - Phone alphanumeric stripped after prefix
  - Contact title derived from gender (`MR`/`MS`)
  - Parcel dimensions mandatory (length, width, height >= 1)

### 7.2 SendCloud
- **Base URL:** `https://panel.sendcloud.sc/api`
- **Auth:** API Key / Secret (Basic Auth)
- **Endpoints:**
  - `POST /v3/shipping-options` — rates
  - `POST /v3/shipments/announce` — create shipment
  - `GET /v2/labels/{id}` — label URL
  - `GET /v2/parcels/{id}` — tracking
  - `POST /v3/shipments/{id}/cancel` — cancel
- **Special Rules:**
  - House number extracted from address line 1 (regex)
  - If no house number, uses U+200A HAIR SPACE to bypass validation
  - Multi-parcel: each parcel announced individually; on partial failure, successful parcels cancelled
  - Weight decimals: 3; Currency decimals: 2

---

## 8. Rate Calculation

### 8.1 Request Model
```python
class RateRequest(BaseModel):
    origin: str                    # Country code or address name
    destination: str
    weight: float
    weight_unit: str = "kg"
    dimensions: Optional[str] = None  # JSON or formatted string
    value: Optional[float] = None
    parcels: Optional[list[Parcel]] = None
    pickup_date: Optional[date] = None
    description_of_content: Optional[str] = None
    pickup_from_type: str = "Company"
    delivery_to_type: str = "Customer"
    pickup_address_name: Optional[str] = None
    delivery_address_name: Optional[str] = None
    pickup_contact_name: Optional[str] = None
    delivery_contact_name: Optional[str] = None
    pickup_address: Optional[ShippingAddress] = None  # inline fallback
    delivery_address: Optional[ShippingAddress] = None  # inline fallback
    pickup_contact: Optional[ShippingContact] = None  # inline fallback
    delivery_contact: Optional[ShippingContact] = None  # inline fallback
```
Accepted forms:
1. `pickup_address_name` + `delivery_address_name` (resolved from `addresses` table)
2. Inline `pickup_address` + `delivery_address` objects (no DB lookup)
3. Mixed: IDs for one side, inline for the other

(Confirmed: Option B)

### 8.2 Response Model
```python
class ShippingRate(BaseModel):
    carrier: str
    service: str
    service_id: Optional[str] = None
    estimated_days: int
    cost: float
    currency: str
    is_preferred: bool = False
    provider: str
    raw: Optional[dict] = None
```

### 8.3 Business Rules
- Rates fetched from **all enabled providers** in parallel
- Results merged, deduplicated, and sorted by `cost` ascending
- Partial provider failures do not block other providers
- Error per provider logged to `shipping_logs`

---

## 9. Label Generation

### 9.1 Request
`GET /api/v1/shipping/shipments/{shipment_id}/label`

### 9.2 Response
```python
class LabelResponse(BaseModel):
    shipment_id: int
    label_url: str
    label_format: str = "PDF"
    message: str
```

### 9.3 Business Rules
- Label retrieved from provider using stored `provider_shipment_id`
- For SendCloud, all parcel IDs concatenated with `, ` are resolved
- Label stored as file in `/storage/labels/` (MVP) and metadata saved to `shipping_labels` table for audit (Confirmed: Option A)
- Label returned to frontend as URL/path; streaming endpoint available for direct download

---

## 10. Shipment Tracking

### 10.1 Manual Tracking
`GET /api/v1/shipping/track/{tracking_id}`

### 10.2 Automatic Tracking
- **Scheduler:** `shipping_tracking_poll` job runs daily
- **Filter:** `status = 'booked' AND tracking_status != 'delivered' AND provider_shipment_id IS NOT NULL`
- **Action:** Poll provider, update `shipments` record, create `shipping_logs` entries

### 10.3 Tracking Events
```python
class TrackingEvent(BaseModel):
    status: str
    location: Optional[str] = None
    timestamp: Optional[datetime] = None
    description: Optional[str] = None
```

### 10.4 Status Mapping
| Provider Status | Local Status |
|-----------------|--------------|
| `DELIVERED` | `delivered` |
| `RETURNED` | `returned` |
| `LOST` | `lost` |
| Default | `in_transit` |

---

## 11. Pickup Workflow

### 11.1 Contact Resolution
- **Company Pickup:** Resolved from `users` table (`pickup_contact_person` → user record)
- **Individual Pickup:** Resolved from `contacts` table (Confirmed: Option A — new dedicated `contacts` table)

### 11.2 Contact CRUD
- `contacts` table supports multiple contacts per `customer_id` / `supplier_id`
- Contact fields: first_name, last_name, email, phone, mobile_no, gender
- Phone validation: E.164 format enforced at service layer

### 11.3 Address Resolution
- Resolved from `addresses` table (Confirmed: Option A — new dedicated `addresses` table)
- Fields: title, line1, line2, city, pincode, country, country_code
- `pincode` required, stripped of spaces
- `country` required; `country_code` derived from `countries` table or hardcoded mapping
- Addresses linked to entity via `entity_type` + `entity_id` (customer, supplier, or standalone)

---

## 12. Validation Rules

| Rule | Enforcement |
|------|-------------|
| Parcel dimensions (L,W,H) >= 1 | Provider client validation |
| Phone E.164 format | Service layer validator |
| Address requires country + pincode | Service layer validator |
| Provider enabled before use | Registry check |
| Shipment exists before update | DB existence check |
| Tracking number format | Provider-specific (not enforced locally) |
| User role before create/update | Router dependency (`require_role`) |

---

## 13. Background Jobs

### 13.1 Shipping Scheduler
Analogous to `eta_scheduler.py`.

```python
# app/core/shipping_scheduler.py
def init_shipping_scheduler() -> AsyncIOScheduler:
    _scheduler = AsyncIOScheduler(job_defaults={...})
    _scheduler.add_job(
        _poll_tracking_job,
        "interval",
        hours=24,  # Daily
        id="shipping_tracking_poll",
        replace_existing=True,
    )
    return _scheduler
```

### 13.2 Jobs
| Job | Frequency | Action |
|-----|-----------|--------|
| `shipping_tracking_poll` | Daily | Poll booked shipments, update tracking |

---

## 14. Retry Strategy

Following ETA Engine pattern (`eta_client.py`):

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    before_sleep=lambda rs: logger.warning("Shipping request retry %d/%d", ...),
)
def _post_with_retry(self, url, json, headers): ...
def _get_with_retry(self, url, headers, params): ...
```

**Retryable:** Timeout, NetworkError  
**Non-retryable:** HTTP 400, 401, 403, 404, 422 (mapped to user error)  
**Provider isolation:** Retry per-provider; failure in one provider does not affect others

---

## 15. Scheduler

| Component | ETA Engine | Shipping Engine |
|-----------|------------|-----------------|
| File | `app/core/eta_scheduler.py` | `app/core/shipping_scheduler.py` |
| Init | `init_scheduler()` | `init_shipping_scheduler()` |
| Jobs | `eta_status_polling` (hourly), `eta_batch_submit` (hourly) | `shipping_tracking_poll` (daily) |
| Lifecycle | `main.py` lifespan startup/shutdown | `main.py` lifespan startup/shutdown |

---

## 16. Notifications

### 16.1 Current State
- WP-19 deferred email notifications to WP-21
- WP-20 follows same pattern: **prepare notification data, defer sending to WP-21**

### 16.2 Shipping Notification Events
| Event | Recipients | Data |
|-------|-----------|------|
| Shipment booked | Customer, Sales | tracking_number, carrier, label_url |
| In transit | Customer | tracking_url, estimated_delivery |
| Delivered | Customer, Sales | delivery confirmation |
| Exception (lost/returned) | Sales, Logistics | tracking_status, reason |

---

## 17. Audit Logging

### 17.1 Shipping Log Table
Every provider API call logged:
```python
shipping_logs = {
    "shipment_id": int,
    "provider": str,
    "action": str,  # rates, create, label, tracking, cancel
    "request_payload": str,  # JSON
    "response_payload": str,  # JSON
    "error_message": str,
    "status_code": int,
    "created_at": str,
}
```

### 17.2 Integration with Existing Audit
- `audit_logs` table (existing) records user actions (create shipment, update status)
- `shipping_logs` table records provider API interactions
- Both linked via `shipment_id`

---

## 18. Permissions & Security

### 18.1 Role Matrix (extends existing)
| Role | Rates | Create | Update | Label | Track | Provider Config |
|------|-------|--------|--------|-------|-------|-----------------|
| owner | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| manager | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| sales | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| logistics | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| admin_staff | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| accountant | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| supplier | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| customer | ✅ | ❌ | ❌ | ❌ | ✅ (own) | ❌ |

### 18.2 Security Rules
- API keys stored in `shipping_providers.config` as JSON or environment variables (never in logs)
- No secrets exposed in `shipping_logs`
- Phone validation enforces E.164
- CORS follows existing `ALLOWED_ORIGINS` policy
- Rate limiting to be implemented (existing tech debt, not WP-20 scope)

---

## 19. Database Design

### 19.1 New Tables
```sql
CREATE TABLE IF NOT EXISTS shipping_providers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    provider_type TEXT NOT NULL,
    environment TEXT DEFAULT 'Pre-Production',
    enabled INTEGER DEFAULT 0,
    is_default INTEGER DEFAULT 0,
    config TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by INTEGER
);
```

### 19.2 Extended Tables
```sql
-- shipments table additions
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS service_provider TEXT;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS provider_shipment_id TEXT;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS awb_number TEXT;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS tracking_url TEXT;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS tracking_status TEXT;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS tracking_status_info TEXT;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS shipment_amount REAL;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS label_url TEXT;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS pickup_contact_id INTEGER;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS delivery_contact_id INTEGER;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS pickup_address_name TEXT;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS delivery_address_name TEXT;
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS pickup_from_type TEXT DEFAULT 'Company';
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS delivery_to_type TEXT DEFAULT 'Customer';
ALTER TABLE shipments ADD COLUMN IF NOT EXISTS provider_response TEXT;
```

### 19.3 New Contacts/Addresses Tables (Confirmed: Option A)
```sql
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    mobile_no TEXT,
    gender TEXT,
    customer_id INTEGER,
    supplier_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS addresses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    address_title TEXT NOT NULL,
    address_line1 TEXT NOT NULL,
    address_line2 TEXT,
    city TEXT NOT NULL,
    pincode TEXT NOT NULL,
    country TEXT NOT NULL,
    country_code TEXT,
    entity_type TEXT,
    entity_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 20. API Structure

All routes prefixed with `/api/v1/shipping`. Existing routes remain backward-compatible.

### 20.1 Existing Routes (Preserved)
| Method | Path | Action |
|--------|------|--------|
| POST | `/api/v1/shipping/rates` | Get rates (enhanced, POST for nested payload) |
| GET | `/api/v1/shipping/shipments` | List shipments |
| POST | `/api/v1/shipping/shipments` | Create shipment |
| GET | `/api/v1/shipping/shipments/{id}` | Get shipment |
| PUT | `/api/v1/shipping/shipments/{id}` | Update shipment |
| GET | `/api/v1/shipping/track/{id}` | Track shipment |
| GET | `/api/v1/shipping/shipments/{id}/label` | Get label |

### 20.2 New Routes
| Method | Path | Action | Roles |
|--------|------|--------|-------|
| GET | `/api/v1/shipping/providers` | List providers | all |
| POST | `/api/v1/shipping/providers` | Create provider | owner, admin_staff |
| PUT | `/api/v1/shipping/providers/{id}` | Update provider | owner, admin_staff |
| DELETE | `/api/v1/shipping/providers/{id}` | Delete provider | owner |
| GET | `/api/v1/shipping/providers/{id}/test` | Test provider connection | owner, admin_staff |
| GET | `/api/v1/shipping/parcel-templates` | List parcel templates | all |
| POST | `/api/v1/shipping/parcel-templates` | Create parcel template | owner, manager, logistics |
| PUT | `/api/v1/shipping/parcel-templates/{id}` | Update parcel template | owner, manager, logistics |
| DELETE | `/api/v1/shipping/parcel-templates/{id}` | Delete parcel template | owner, manager, logistics |
| POST | `/api/v1/shipping/shipments/{id}/cancel` | Cancel shipment | owner, manager, logistics |

### 20.3 Request/Response Schemas
New schemas added to `app/schemas/shipping.py`:
- `ShippingProviderCreate`, `ShippingProviderUpdate`, `ShippingProviderResponse`
- `ParcelTemplateCreate`, `ParcelTemplateUpdate`, `ParcelTemplateResponse`
- `Parcel`, `ShippingContact`, `ShippingAddress`
- `RateRequest`, `RateResponse`
- `CreateShipmentRequest`, `ShipmentResult`
- `LabelResponse`, `TrackingEvent`, `TrackingResponse`

---

## 21. Extension Points

### 21.1 Adding a New Provider
1. Create `app/services/shipping/{provider_name}_client.py` implementing `ShippingProvider`
2. Register in `PROVIDERS` dict in `app/services/shipping/__init__.py`
3. Add provider type to `shipping_providers` table seed/config
4. Add provider-specific validation in client
5. Add tests in `backend/tests/test_services/test_shipping_service.py`

### 21.2 Adding a New Carrier
- Carriers are discovered dynamically from provider rate responses
- No code change required unless carrier-specific payload mapping is needed
- Carrier alias mapping can be added to provider client if needed

### 21.3 Custom Label Formats
- Label format stored in `shipping_labels.label_format`
- Provider client returns raw bytes/URL; format conversion can be added as middleware

---

## 22. Error Handling

### 22.1 Error Hierarchy
```python
class ShippingError(Exception): ...
class ProviderNotFoundError(ShippingError): ...
class RateFetchError(ShippingError): ...
class ShipmentBookingError(ShippingError): ...
class LabelGenerationError(ShippingError): ...
class TrackingError(ShippingError): ...
class ValidationError(ShippingError): ...
```

### 22.2 Error Mapping
| HTTP Status | User Message (AR) |
|-------------|-------------------|
| 400 | بيانات الشحن غير صحيحة. يرجى المراجعة. |
| 401 | بيانات اعتماد موفر الشحن غير صحيحة. |
| 403 | ليس لديك صلاحية لهذه العملية. |
| 404 | الشحنة أو الموفر غير موجود. |
| 422 | بيانات الطلب غير مكتملة. |
| 500 | خطأ في نظام الشحن. يرجى المحاولة لاحقاً. |
| 503 | خدمة الشحن غير متاحة حالياً. |

### 22.3 Partial Failure Handling
- Rate fetch: failed providers logged, other providers still return results
- Multi-parcel creation (SendCloud): failed parcels trigger cancel of successful ones; returns `None` to indicate full rollback needed
- Tracking: failed providers skipped; success logged

---

## 23. Configuration Model

### 23.1 Environment Variables (`config.py`)
```python
LETME_API_ID: str = ""
LETME_API_PASSWORD: str = ""
SENDCLOUD_PUBLIC_KEY: str = ""
SENDCLOUD_SECRET_KEY: str = ""
```
These are the **only** source of provider credentials. Provider clients read directly from `settings` at call time. No credential round-tripping through the database occurs.

### 23.2 Database Configuration (`shipping_providers` table)
- `name`: LetMeShip, SendCloud
- `provider_type`: letmeship, sendcloud
- `environment`: Pre-Production / Production
- `enabled`: bool
- `is_default`: bool
- `config`: JSON for non-sensitive settings only (timeout, retry count, display preferences)
- No credential fields in DB; secrets loaded exclusively from environment variables

**Confirmed:** Option B — Env vars hold secrets; DB holds enabled/disabled, environment, display name, and metadata only. No `api_key`/`api_secret` columns in `shipping_providers`.

### 23.3 Provider Selection Logic
```python
def get_default_provider() -> ShippingProvider:
    # 1. Check query parameter provider=name
    # 2. Check default provider in DB
    # 3. Fall back to first enabled provider
```

---

## 24. Gap Analysis: Nile Key vs ERPNext Shipping

| Capability | ERPNext Shipping | Nile Key Current | Nile Key Target (WP-20) |
|------------|------------------|------------------|-------------------------|
| Rate Calculation | ✅ Multi-provider, real API | ❌ Mock/random | ✅ Real LetMeShip + SendCloud |
| Shipment Booking | ✅ Provider APIs | ❌ Local only | ✅ Provider APIs |
| Label Generation | ✅ PDF download + attachment | ❌ Mock URL | ✅ Real PDF/ZPL + storage |
| Tracking | ✅ Daily scheduler | ❌ Mock events | ✅ Daily scheduler + real API |
| Provider Config | ✅ DocType settings | ❌ Env vars only | ✅ DB metadata table; env vars for credentials |
| Parcel Validation | ✅ LetMeShip dims + SendCloud warnings | ❌ None | ✅ Full validation |
| Address Validation | ✅ Pincode + country required | ❌ None | ✅ Pincode + country + phone |
| Contact Validation | ✅ Phone E.164, last name required | ❌ None | ✅ Same rules |
| Error Handling | ✅ Per-provider isolation, Error Log | ❌ Basic | ✅ Per-provider + logging |
| Retry Strategy | ❌ None (requests lib) | ❌ None | ✅ Tenacity (like ETA) |
| Audit Logging | ❌ Frappe Version + Error Log | ❌ None | ✅ shipping_logs + audit_logs |
| Cancellation | ✅ SendCloud cancel on partial failure | ❌ None | ✅ Provider cancel + local cancel |
| State Machine | ✅ Booked/In Progress/Delivered | ❌ Simple pending/in_transit | ✅ 7-state machine |
| Scheduler | ✅ Daily tracking | ❌ None | ✅ Daily tracking poll |
| Notifications | ❌ None | ❌ None | ⏸️ Deferred to WP-21 |
| Extensions | ✅ Parcel Service Type Alias | ❌ None | ⏸️ Parcel templates (MVP minimal) |

---

## 25. Required Components for Nile Key Shipping Engine

### 25.1 Backend Files (New)
```
backend/app/
├── schemas/
│   └── shipping.py              # Extend existing schemas
├── services/
│   └── shipping/
│       ├── __init__.py          # Registry + orchestrator (replaces shipping.py logic)
│       ├── letmeship_client.py  # LetMeShip HTTP client + retry
│       ├── sendcloud_client.py  # SendCloud HTTP client + retry
│       └── base.py              # Abstract base + shared types (optional)
├── core/
│   └── shipping_scheduler.py    # APScheduler daily tracking job
├── routers/
│   └── shipping.py              # Extend existing router with new routes
```

### 25.2 Backend Files (Modified)
- `backend/app/core/database.py` — Add `_ensure_shipping_schema()` + new table creation
- `backend/app/core/config.py` — Add shipping provider env vars (already present, verify)
- `backend/main.py` — Register `shipping_scheduler` in lifespan
- `backend/app/services/shipping.py` — Becomes thin compatibility shim re-exporting from new package (Confirmed: Option B)

### 25.3 Test Files (New)
```
backend/tests/
├── test_shipping.py             # Extend existing router tests
└── test_services/
    └── test_shipping_service.py # Extend existing service tests
```

### 25.4 Database Migrations
- Alembic migration for new tables + `shipments` column additions
- Seed data: default LetMeShip + SendCloud provider rows (disabled)

### 25.5 Frontend Files (Modified)
- `frontend/src/pages/Shipments.tsx` — Add provider selector, parcel input, address/contact forms, label download, tracking timeline
- `frontend/src/services/api.ts` — Add new API functions
- `frontend/src/types/api.d.ts` — Regenerate from OpenAPI after backend changes
- `frontend/src/locales/*/translation.json` — Add shipping provider translations

---

## 26. WP-20 Implementation Plan

### 26.1 Phase 1: Foundation (Days 1–3)
**Goal:** Provider abstraction + HTTP clients with retry

**Tasks:**
1. Create `app/schemas/shipping.py` with all new Pydantic models
2. Create `app/services/shipping/letmeship_client.py` (httpx + tenacity, auth, endpoints)
3. Create `app/services/shipping/sendcloud_client.py` (httpx + tenacity, auth, endpoints)
4. Create `app/services/shipping/__init__.py` with `PROVIDERS` registry + `get_enabled_providers()`
5. Add `_ensure_shipping_schema()` + new table DDL in `database.py`
6. Add Alembic migration for schema changes
7. Unit tests for both clients (mocked httpx)

**Acceptance:**
- [ ] `LetMeShipClient` and `SendCloudClient` instantiate with config
- [ ] `get_enabled_providers()` returns only enabled providers from DB
- [ ] All client methods wrapped with tenacity retry
- [ ] 15+ unit tests passing

### 26.2 Phase 2: Service Layer (Days 4–6)
**Goal:** Business logic for rates, booking, labels, tracking

**Tasks:**
1. Implement `fetch_rates(request)` — aggregates from all enabled providers
2. Implement `create_shipment(data, user)` — validates, calls provider, updates DB
3. Implement `get_label(shipment_id)` — retrieves from provider, stores file
4. Implement `track_shipment(tracking_id)` — polls provider, maps status
5. Implement `cancel_shipment(shipment_id)` — provider cancel + local state update
6. Implement provider CRUD (`create_provider`, `list_providers`, etc.)
7. Implement parcel template CRUD
8. Add validation helpers (phone, address, parcel dimensions)

**Acceptance:**
- [ ] Rates returned from real provider APIs (with API keys)
- [ ] Shipment creation updates DB with provider response
- [ ] Label stored and URL returned
- [ ] Tracking maps provider statuses to local states
- [ ] 20+ service tests passing

### 26.3 Phase 3: Router + Scheduler (Days 7–8)
**Goal:** Thin router exposing service layer + background tracking

**Tasks:**
1. Extend `app/routers/shipping.py` with new endpoints
2. Create `app/core/shipping_scheduler.py` with daily tracking job
3. Register scheduler in `main.py` lifespan
4. Add role-based access control to new endpoints
5. Add error handling middleware / exception mapping

**Acceptance:**
- [ ] All existing shipping routes still work (backward compatible)
- [ ] New provider routes protected by roles
- [ ] Scheduler starts on app startup
- [ ] 10+ router tests passing

### 26.4 Phase 4: Integration + Polish (Days 9–10)
**Goal:** End-to-end integration, frontend updates, documentation

**Tasks:**
1. Integrate with `customers` and `suppliers` for contact/address resolution
2. Add `shipping_logs` creation in all provider calls
3. Add `audit_logs` entries for user actions
4. Update `Shipments.tsx` with new fields (provider, parcel, contact)
5. Update translations (ar/en)
6. Regenerate `api.d.ts`
7. Run full test suite (`pytest`) — target 40+ shipping tests total
8. Update `CURRENT_STATUS.md` and `TECH_DEBT.md`

**Acceptance:**
- [ ] 40+ shipping tests passing (no regressions in other tests)
- [ ] Frontend builds without errors
- [ ] OpenAPI contract updated and types regenerated
- [ ] Manual end-to-end test with LetMeShip test env
- [ ] Manual end-to-end test with SendCloud test env

---

## 27. Future Integration Points

### 27.1 Export Operations (WP-21)
- `shipments.destination` → export market intelligence
- `shipments.supplier_id` → supplier performance analytics
- `shipments.customs_declaration_id` → link to customs clearance status
- Trigger: auto-create `customs_declarations` draft when shipment is booked

### 27.2 Customs Engine
- `customs_declarations.shipment_id` → existing FK
- Auto-populate HS code suggestions based on `shipments.description`
- Sync tracking status with customs approval status

### 27.3 ETA Engine
- `invoices.shipment_id` → existing FK
- Trigger: when shipment is delivered, prompt invoice submission to ETA
- Share `customer_id` / `supplier_id` between shipments and invoices

### 27.4 Documents Service
- `shipping_labels` linked to `documents` table
- Packing lists, commercial invoices attached to shipment
- Auto-generate shipping documents from templates

### 27.5 Warehouses (Future)
- `shipments.origin` → warehouse location
- Pickup scheduling linked to warehouse stock availability
- Inventory deduction on `booked` status

### 27.6 Orders (Future)
- Sales orders → shipment creation trigger
- Partial shipment support (multiple shipments per order)
- Backorder management

### 27.7 Notifications (WP-21)
- Shipment status changes → notification queue
- Email/SMS templates for tracking updates
- Integration with existing notification stub in ETA Engine

### 27.8 Audit System
- `shipping_logs` linked to `audit_logs` via `shipment_id`
- All provider API calls auditable
- User actions (create, cancel, update) in `audit_logs`

---

## 28. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| LetMeShip API access delayed | Medium | High | SendCloud primary for MVP; LetMeShip follows |
| Provider API schema changes | Medium | High | Versioned client classes; adapter layer |
| Multi-parcel cancellation complexity | Medium | Medium | Reference implementation copied verbatim (algorithm) |
| Label storage scaling | Low | Medium | MVP: local files; later: S3/MinIO |
| Tracking scheduler load | Low | Low | Daily batch, 100-record limit per run |
| Phone validation edge cases | Medium | Low | Strict E.164 + clear error messages |

---

## 29. Rollback Strategy

1. **Feature flag:** `SHIPPING_ENGINE_V2` env var; when `false`, old `shipping.py` stub handles routes
2. **Database:** New tables are additive; `shipments` columns are nullable; rollback = drop new tables + columns
3. **Router:** Old endpoints preserved alongside new ones until WP-20 complete
4. **Frontend:** Existing Shipments page unchanged; new page behind feature flag

---

## 30. Validation Plan

### 30.1 Automated Tests
- **Unit:** Client methods (mocked HTTP), validation helpers, registry
- **Service:** Rate aggregation, shipment creation, label, tracking, cancellation
- **Router:** Endpoint existence, role enforcement, status codes
- **Integration:** Full booking flow with mocked providers
- **Database:** Schema migrations, seed data, constraints

### 30.2 Manual Validation
- [ ] LetMeShip test environment: rates → create → label → track
- [ ] SendCloud test environment: rates → create → label → track → cancel
- [ ] Phone validation edge cases (missing +, spaces, etc.)
- [ ] Partial failure simulation (SendCloud multi-parcel)
- [ ] Scheduler runs and updates tracking

### 30.3 Quality Gates (per PLAN.md §10.8)
- [ ] Project builds
- [ ] Backend starts without errors
- [ ] Frontend builds
- [ ] Core routes work
- [ ] Auth works
- [ ] No broken imports
- [ ] No circular dependencies
- [ ] No hidden runtime errors
- [ ] Tests pass (40+ new)

---

## 31. Confirmed Decisions

All design decisions confirmed on 2026-07-12. The plan is implementation-ready.

| Decision | Chosen Option | Rationale |
|----------|--------------|-----------|
| Contacts & Addresses model | **Option A:** New `contacts` + `addresses` tables | Clean separation; reusable across domains; matches ERPNext reference |
| Rate endpoint HTTP method | **Option A:** Switch `/rates` to `POST` | Supports nested payload; aligns with provider APIs; minor breaking change accepted |
| Provider configuration source | **Option B:** Env vars for secrets; DB for enabled/environment/metadata | Simple; no encryption needed; consistent with ETA connector pattern |
| Label storage | **Option A:** Filesystem `/storage/labels/` + DB metadata | Fast; standard pattern; Docker volume can be added later |
| Shipment cancellation scope | **Option A:** User-initiated + automatic SendCloud rollback | Complete feature; matches user expectations; handles partial failures |
| Contacts/Addresses in rate request | **Option B:** ID references resolved from DB + inline fallback | Reuses data; supports both quick estimates and saved addresses |
| Existing `shipping.py` migration | **Option B:** Compatibility shim re-exporting from new package | Safe transition; zero risk to existing imports |

**Out of Scope for WP-20:**
- Customs domain logic (deferred to dedicated Customs Work Package)
- Credential encryption or secrets management in database (explicitly excluded; env vars only)
- Rate limiting (existing tech debt, not WP-20 scope)
- PostgreSQL migration (Phase 3)
- Webhook-based tracking push (pull-based scheduler for MVP)
- Email/SMS notifications (prepared in WP-20, sent in WP-21)
- Multi-language provider documentation (English only for MVP)

---

## 32. PLAN.md Alignment Check

| PLAN.md Requirement | WP-20 Plan Compliance |
|---------------------|----------------------|
| No Frappe Framework | ✅ No Frappe imports; pure FastAPI + SQLite |
| No ERPNext | ✅ No ERPNext dependencies |
| No MariaDB/Redis/Bench | ✅ SQLite for MVP; PostgreSQL path preserved |
| Extract → Redesign → Integrate | ✅ Reference logic extracted and redesigned; no copy-paste |
| Shipping Engine as Core Domain | ✅ Same treatment as ETA Engine (Phase 1.5) |
| Same quality as ETA Engine | ✅ Matching patterns: httpx + tenacity, Pydantic schemas, APScheduler, service layer |
| 40+ tests | ✅ Target 40+ shipping tests across unit/service/router/integration |
| Phase 1.5 gate | ✅ WP-20 is mandatory before Phase 2 |
| Backend-first API contract | ✅ Pydantic schemas define contract; frontend consumes |
| Thin routers | ✅ Routers delegate to service layer |
| No business logic in routers | ✅ All logic in `app/services/shipping/` |
| JWT auth + RBAC | ✅ Existing auth system used; roles enforced |
| Docker deployment | ✅ No changes to Docker setup; additive schema only |
| Documentation before code | ✅ This plan documents all decisions before implementation |

---

## 32. References

- PLAN.md — Master Roadmap v2.1 (Single Source of Truth)
- WP-19 Implementation — ETA Engine (architectural blueprint)
- `https://github.com/frappe/erpnext-shipping` — Functional reference
- `backend/app/services/eta/` — Nile Key ETA Engine implementation
- `backend/app/schemas/eta.py` — Nile Key schema patterns
- `backend/app/core/eta_scheduler.py` — Nile Key scheduler pattern
- `backend/app/services/eta/eta_client.py` — Nile Key HTTP client + retry pattern

---

*Plan confirmed and ready for implementation. All design decisions resolved. Credentials sourced exclusively from environment variables. No code changes until implementation agent is activated.*
