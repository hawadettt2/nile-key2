# ADR-0001: Shipments Legacy Columns Handling

**Date:** 2026-06-30
**Status:** Accepted
**Deciders:** Engineering Team

---

## Context

WP-02D addresses the database contract alignment for the shipments entity. During implementation, the distinction between legacy columns and contract fields required an architectural decision.

## Decision

Shipments legacy columns are **NOT fallback pairs** and will be **excluded entirely** from the API contract.

---

## Analysis

### 1. Why Shipment Legacy Columns Are NOT Fallback Pairs

Unlike the customers entity where `company_name` → `name` and `contact_name` → `contact_person` represent the same semantic data with different column names, shipments legacy columns represent **entirely different data concepts**:

| Legacy Column | Contract Field | Relationship |
|---------------|--------------|------------|
| service_name | service_type | Different semantics |
| pickup_address | origin | Different semantics |
| delivery_address | destination | Different semantics |
| label_url | - | View-only metadata |
| cost | - | Derived field |
| provider | - | Implementation detail |
| parcels | - | Raw JSON data |
| raw_response | - | Raw integration data |

### 2. Why service_name != service_type

- `service_name`: Legacy column, appears to be a free-text field for service name
- `service_type`: Contract field per Shipment schema, represents service type (e.g., "Express", "Economy")
- **These are semantically distinct**: service_type is a controlled enumeration; service_name is undefined legacy data

### 3. Why pickup_address != origin

- `pickup_address`: Legacy column, appears to be a full address string
- `origin`: Contract field per Shipment schema, represents the origin location (typically country code)
- **Different granularity**: origin is higher-level (country/region), pickup_address is detailed address

### 4. Why delivery_address != destination

- `delivery_address`: Legacy column, full address string
- `destination`: Contract field per Shipment schema, represents destination location
- **Same reasoning as pickup_address vs origin**

### 5. Semantic Meaning of Legacy Columns vs Contract Fields

| Legacy Column | Contract Field | Semantic Meaning |
|---------------|--------------|----------------|
| service_name | service_type | "Express", "Economy" - user-selected service category |
| pickup_address | origin | Full pickup address string vs country code |
| delivery_address | destination | Full delivery address string vs country code |
| label_url | - | URL to PDF label - view-only, not user data |
| cost | - | Calculated shipping cost - derived, not input |
| provider | - | Carrier API provider name - implementation detail |
| parcels | - | Raw parcel definitions JSON - not normalized |
| raw_response | - | Raw carrier API response - not normalized |

### 6. Why Legacy Shipment Columns Are Intentionally Excluded

Per the Architecture Charter Section 9 (Source of Truth), Pydantic schemas define the authoritative contract. The legacy columns:

- Have no corresponding schema field
- Represent deprecated or implementation-specific data
- May contain stale or incompatible data
- Should not be exposed to API consumers

### 7. Why No Synchronization Layer Is Implemented

The synchronization pattern used for customers (where data flows from new columns to legacy columns for backward compatibility) is **NOT applicable** because:

1. Legacy columns are **not fallbacks** - they contain different data
2. Legacy columns are **deprecated** - no code depends on them
3. The `ensure_columns()` helper already added schema fields to the database
4. CREATE/UPDATE operations already use contract fields (verified in shipping.py)

### 8. Pydantic Schema as Authoritative Contract

The Pydantic schema in `backend/app/schemas/shipment.py` is the **authoritative contract** for the shipments entity. Legacy columns exist only for backward compatibility with existing SQLite data and will be removed during WP-10.

### 7. Future Migration Strategy

**Phase 1 (WP-10 - Database Migration):**
- Add Alembic migration to safely drop legacy columns
- Provide data migration script if legacy data needs preservation
- Coordinate with frontend team to verify no dependencies

**Phase 2 (WP-10 - Post Migration):**
- Remove legacy column references from codebase
- Clean up `_shipment_row_to_response()` compatibility layer
- Update documentation

**Phase 3 (WP-08 - Services Layer):**
- Ensure services layer uses contract fields only

---

## Consequences

- ✅ API responses contain only contract fields
- ✅ No data confusion between legacy and contract fields
- ✅ Clean separation for future removal
- ⚠️ Legacy column data will be permanently lost on WP-10 migration (intentional)

---

*Related: WP-02D, WP-10*
*Decided by: Implementation review on 2026-06-30*