# World Bank LPI Adapter Specification

**Work Package:** Portfolio Re-Evaluation — World Bank LPI Phase 1  
**Task:** 2 — Adapter Specification  
**Date:** 2026-08-18  
**Status:** Approved — G2 PASS — G3 PASS — G4 PASS — G5 Closure — Implemented Provider (7/7)  
**Authority:** `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` Section 27.3  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Provider:** World Bank Indicators API — Logistics Performance Index (LPI)  
**Prerequisite:** Section 27.3 — World Bank LPI Phase 1 Activated; G1/G2/G3/G4 PASS recorded; G5 Closure recorded

---



## 1. Adapter Boundary & Provider-Agnostic Architecture

### 1.1 Boundary

The World Bank LPI adapter consists of two files:

- `worldbank_lpi_client.py` — isolated HTTP client for World Bank Indicators API
- `worldbank_lpi_provider.py` — `KnowledgeProvider` implementation that transforms World Bank LPI responses into the DEM knowledge contract shape

The adapter does **not** modify:

- `ReasoningEngine`
- `TaskPlanner`
- `ToolOrchestrator`
- Any DEM core component
- `knowledge_nodes` or `knowledge_edges` tables
- `KNOWLEDGE_INGESTION_CONTRACT.md`

### 1.2 Provider-Agnostic Compliance

| Requirement | Implementation |
|-------------|----------------|
| Provider Abstraction | All World Bank LPI access is through `WorldBankLpiExternalSourceAdapter(KnowledgeProvider)` |
| Registry-Only Registration | Registered in `KnowledgeProviderRegistry` only; DEM core never references World Bank LPI directly |
| No DEM Core Coupling | No DEM core files modified except `config.py` (settings) and `main.py` (lifespan registration) |
| No Knowledge Graph Schema Changes | No writes to `knowledge_nodes` or `knowledge_edges` |
| No Contract Changes | `KNOWLEDGE_INGESTION_CONTRACT.md` unchanged |
| Config-Driven | All World Bank LPI-specific settings loaded from `config.py` |
| Replaceable | Adapter can be replaced without redesigning Intelligence Layer |
| Composable | Multiple providers coexist in registry without mutual dependency |
| Observable | `get_sources()` exposes source metadata; query responses include `source_id` and provenance |

---



## 2. KnowledgeProvider Contract Implementation

### 2.1 Interface Compliance

`WorldBankLpiExternalSourceAdapter` implements `KnowledgeProvider` with the following methods:

| Method | Signature | Return Shape |
|--------|-----------|--------------|
| `query()` | `async def query(self, query: str, context: Optional[Dict[str, Any]] = None, scope: Optional[str] = None, sources: Optional[List[str]] = None, limit: int = 10) -> Dict[str, Any]` | `{"results": [...], "confidence": float|None, "sources": [source_id]}` |
| `get_sources()` | `async def get_sources(self) -> List[Dict[str, Any]]` | `[{"id": str, "name": str, "type": str, "version": str, "updated_at": str}]` |

### 2.2 Query Behavior

- **Primary context parameters:** `country` (ISO 3-letter country code), `indicator` (LPI indicator code), `year` (optional)
- **Scope:** Mapped to World Bank indicator code selection; defaults to overall LPI score
- **Sources parameter:** Accepted but not used for filtering; returned in response as `[source_id]`
- **Limit:** Applied to transformed results after fetching; World Bank API `per_page` parameter used for pagination

### 2.3 Graceful Degradation

| Failure Mode | Behavior |
|--------------|----------|
| Missing `country` in context | Returns empty results with `confidence: None` |
| Network error / timeout | Returns empty results with `confidence: None` |
| HTTP 429 (rate limit) | Returns empty results; no retry unless policy is documented |
| HTTP error status | Returns empty results |
| Invalid JSON / non-dict response | Returns empty results |
| Unexpected exception | Returns empty results |

---



## 3. Source/API Definition

### 3.1 World Bank Indicators API

**Base URL:** `https://api.worldbank.org/v2/`

**Endpoint Pattern:** `/country/{country_code}/indicator/{indicator_code}?format=json&per_page={per_page}`

**G1 Evidence:** Live verification performed on 2026-08-18:
- `https://api.worldbank.org/v2/country/EGY/indicator/LP.LPI.OVRL.XQ?format=json&per_page=5`
- Response: HTTP 200, valid JSON array
- Sample data: Egypt 2022 overall LPI = 3.1

**Source:** World Bank Data Catalog — Logistics Performance Index (LPI)
- License: CC BY-4.0
- Attribution required
- Commercial use permitted per Data Catalog terms

### 3.2 LPI Indicator Codes

| Indicator Code | Description | Evidence |
|----------------|-------------|----------|
| `LP.LPI.OVRL.XQ` | Logistics performance index: Overall (1=low to 5=high) | **Evidence** — World Bank Data Catalog |
| `LP.LPI.CUST.XQ` | Efficiency of customs clearance process (1=low to 5=high) | **Evidence** — World Bank Data Catalog |
| `LP.LPI.INFR.XQ` | Quality of trade and transport-related infrastructure (1=low to 5=high) | **Evidence** — World Bank Data Catalog |
| `LP.LPI.ITRN.XQ` | Ease of arranging competitively priced shipments (1=low to 5=high) | **Evidence** — World Bank Data Catalog |
| `LP.LPI.LOGS.XQ` | Competence and quality of logistics services (1=low to 5=high) | **Evidence** — World Bank Data Catalog |
| `LP.LPI.TIME.XQ` | Frequency with which shipments reach consignee within scheduled or expected time (1=low to 5=high) | **Evidence** — World Bank Data Catalog |
| `LP.LPI.TRAC.XQ` | Ability to track and trace consignments (1=low to 5=high) | **Evidence** — World Bank Data Catalog |

**Note:** These indicator codes correspond to the traditional survey-based LPI methodology (2007–2022). The newer LPI 2.0 (2023–2024) uses shipment-level tracking data and is published separately via World Bank Data360; it is **not** the dataset evaluated in this G1 record.

### 3.3 Response Structure

**World Bank Indicators API v2 response (documented):**

```json
[
  {
    "indicator": {
      "id": "LP.LPI.OVRL.XQ",
      "value": "Logistics performance index: Overall (1=low to 5=high)"
    },
    "country": {
      "id": "EG",
      "value": "Egypt, Arab Rep."
    },
    "countryiso3code": "EGY",
    "date": "2022",
    "value": 3.1,
    "unit": "",
    "obs_status": "",
    "decimal": 2
  }
]
```

**Evidence:** Live API response verified on 2026-08-18.

**Pagination:** World Bank API returns paginated results. The adapter must handle `page` and `per_page` parameters to retrieve all available data.

---



## 4. Field Mapping & Transformation

### 4.1 World Bank LPI Response → DEM Knowledge Shape

| DEM Field | World Bank Source | Priority | Evidence |
|-----------|-------------------|----------|----------|
| `id` | `f"{countryiso3code}_{indicator_id}_{date}_{hash(str(entry))}"` | Computed | **Assumption/Unverified** — exact schema requires live API confirmation |
| `content` | Composite: `"{indicator_value} ({date}): {value} {unit}"` | Constructed | **Assumption/Unverified** — content format to be validated against actual API responses |
| `source_id` | Adapter config `source_id` | Config-driven | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `confidence` | Computed per Section 5 | — | **Evidence** — adapter-specific rules |
| `metadata.indicator_id` | `indicator.id` | Direct | **Evidence** — documented World Bank field |
| `metadata.indicator_name` | `indicator.value` | Direct | **Evidence** — documented World Bank field |
| `metadata.country_code` | `country.id` | Direct | **Evidence** — documented World Bank field |
| `metadata.country_name` | `country.value` | Direct | **Evidence** — documented World Bank field |
| `metadata.countryiso3code` | `countryiso3code` | Direct | **Evidence** — documented World Bank field |
| `metadata.year` | `date` | Direct | **Evidence** — documented World Bank field |
| `metadata.value` | `value` | Direct | **Evidence** — documented World Bank field |
| `metadata.unit` | `unit` | Direct | **Evidence** — documented World Bank field |
| `metadata.obs_status` | `obs_status` | Direct | **Evidence** — documented World Bank field |
| `metadata.decimal` | `decimal` | Direct | **Evidence** — documented World Bank field |
| `metadata.source_authority` | Adapter config `"World Bank"` | Config-driven | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.effective_date` | `date` mapped to `"{date}-12-31"` or retained as `"{date}"` | Derived | **Assumption/Unverified** — date mapping convention to be confirmed |
| `metadata.source_url` | Constructed World Bank data page URL | Constructed | **Evidence** — adapter-constructed provenance per contract |
| `metadata.updated_at` | Adapter config `updated_at` | Config-driven | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.version` | Adapter config `version` | Config-driven | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.record_hash` | `hash(frozenset(entry.items()))` | Computed | **Evidence** — adapter-side provenance per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.retrieval_status` | Constant `"success"` | Adapter-set | **Evidence** — adapter-side provenance per KNOWLEDGE_INGESTION_CONTRACT.md |

### 4.2 Content Construction

**Content format:**
- If value present: `"{indicator_name} ({year}): {value}"`
- If value missing: `"{indicator_name} ({year}): data not available"`

**Normalization:**
- Country codes: World Bank uses ISO 3-letter codes; adapter retains `countryiso3code` as provided
- Year: Retained as string from API response
- Value: Retained as numeric or null per API response

---



## 5. Confidence Rules

| Condition | Confidence | Evidence |
|-----------|------------|----------|
| Base (all fields present, `value` is not None) | `0.95` | **Assumption/Unverified** — World Bank LPI data quality indicators require documentation review |
| `value` is None or missing | `0.70` | **Assumption/Unverified** — confidence thresholds are adapter-specific |
| Missing `countryiso3code` or `indicator.id` | `0.60` | **Assumption/Unverified** — confidence thresholds are adapter-specific |
| `obs_status` indicates non-standard observation | `0.75` | **Assumption/Unverified** — obs_status semantics require World Bank metadata confirmation |

**Aggregation:** Average of all result confidences. If no results, returns `confidence: None`.

---



## 6. Provenance Metadata

### 6.1 Source Metadata (`get_sources()`)

```json
{
  "id": "worldbank-lpi",
  "name": "World Bank Logistics Performance Index",
  "type": "external_logistics_intelligence",
  "version": "1.0.0",
  "updated_at": "<fetch-timestamp-ISO8601>"
}
```

### 6.2 Per-Record Provenance

| Field | Type | Source | Purpose | Evidence |
|-------|------|--------|---------|----------|
| `source_id` | String | Adapter config | Fixed identifier for this provider | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.source_authority` | String | Adapter config `"World Bank"` | Attribution | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.effective_date` | String | `date` field | Data year | **Evidence** — documented World Bank field |
| `metadata.source_url` | String | Constructed URL | World Bank data page link | **Evidence** — adapter-constructed provenance per contract |
| `metadata.updated_at` | String | Adapter config | Adapter instantiation timestamp | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.version` | String | Adapter config | Adapter version | **Evidence** — SemVer per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.record_hash` | String | `hash(frozenset(entry.items()))` | Change detection | **Evidence** — adapter-side provenance per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.retrieval_status` | String | Constant `"success"` | Transformation status | **Evidence** — adapter-side provenance per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.indicator_id` | String | `indicator.id` | LPI indicator code | **Evidence** — documented World Bank field |
| `metadata.indicator_name` | String | `indicator.value` | LPI indicator description | **Evidence** — documented World Bank field |
| `metadata.country_code` | String | `country.id` | World Bank country code | **Evidence** — documented World Bank field |
| `metadata.country_name` | String | `country.value` | Country name | **Evidence** — documented World Bank field |
| `metadata.countryiso3code` | String | `countryiso3code` | ISO 3-letter country code | **Evidence** — documented World Bank field |
| `metadata.year` | String | `date` | Observation year | **Evidence** — documented World Bank field |
| `metadata.value` | Any | `value` | LPI score/value | **Evidence** — documented World Bank field |
| `metadata.unit` | String | `unit` | Unit of measurement | **Evidence** — documented World Bank field |
| `metadata.obs_status` | String | `obs_status` | Observation status flag | **Evidence** — documented World Bank field |
| `metadata.decimal` | Integer | `decimal` | Decimal places | **Evidence** — documented World Bank field |

### 6.3 Provenance Guarantees

- `source_id` is never omitted
- `updated_at` is always populated with adapter instantiation timestamp
- `source_authority` is always populated with `"World Bank"`
- `indicator_id` and `countryiso3code` are always populated when present in response
- Missing provenance fields do not block ingestion; they are logged and assigned lowest confidence tier

---



## 7. Error Handling & Retry/Backoff

### 7.1 HTTP Client Retry Policy

| Parameter | Value | Evidence |
|-----------|-------|----------|
| Max attempts | 1 (no retry) | **Evidence** — World Bank API Terms and Conditions prohibit excessive request volume; no documented retry guidance |
| Retry on | None by default | **Evidence** — no rate-limit documentation found; retry policy conservative to respect open data terms |
| Fail on | Any HTTP error | Returns empty results |

**Note:** If World Bank publishes rate-limit headers or terms permitting automated polling, retry policy may be revisited in a future spec revision.

### 7.2 Failure Mode Matrix

| Failure Mode | Detection | Adapter Response | Evidence |
|--------------|-----------|------------------|----------|
| Network timeout | `httpx.TimeoutException` | Returns empty results | **Evidence** — follows established adapter pattern |
| Connection error | `httpx.NetworkError` | Returns empty results | **Evidence** — follows established adapter pattern |
| HTTP 429 (rate limit) | HTTP 429 response | Returns empty results; no retry | **Evidence** — conservative approach; no documented retry policy |
| HTTP 4xx/5xx | `response.raise_for_status()` | Returns empty results | **Evidence** — follows established adapter pattern |
| Invalid JSON | `response.json()` exception | Returns empty results | **Evidence** — follows established adapter pattern |
| Non-list response | `isinstance(raw, list)` check | Returns empty results | **Evidence** — World Bank API returns JSON array |
| Missing `country` or `indicator` in context | `context.get("country")` or `context.get("indicator")` is None | Returns empty results immediately | **Evidence** — follows established adapter pattern |

---



## 8. Configuration & Registry Integration

### 8.1 Required Settings (`backend/app/core/config.py`)

| Setting | Type | Default | Purpose | Evidence |
|---------|------|---------|---------|----------|
| `WORLDBANK_LPI_BASE_URL` | `str` | `"https://api.worldbank.org/v2"` | World Bank Indicators API base URL | **Evidence** — live API verification |
| `WORLDBANK_LPI_TIMEOUT_SECONDS` | `float` | `30.0` | HTTP request timeout | **Evidence** — follows established adapter pattern |
| `WORLDBANK_LPI_SOURCE_ID` | `str` | `"worldbank-lpi"` | Registry source ID | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `WORLDBANK_LPI_SOURCE_NAME` | `str` | `"World Bank Logistics Performance Index"` | Display name | **Evidence** — adapter config pattern |
| `WORLDBANK_LPI_SOURCE_TYPE` | `str` | `"external_logistics_intelligence"` | Source type | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `WORLDBANK_LPI_SOURCE_VERSION` | `str` | `"1.0.0"` | Adapter version | **Evidence** — SemVer per KNOWLEDGE_INGESTION_CONTRACT.md |
| `WORLDBANK_LPI_UPDATED_AT` | `str` | `""` | Adapter instantiation timestamp | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |

**Note:** No API key or authentication token is required. World Bank Indicators API is open access per G1 evidence.

### 8.2 Bootstrap Registration (`backend/main.py`)

```python
if settings.WORLDBANK_LPI_BASE_URL:
    from app.agent.knowledge.worldbank_lpi_provider import WorldBankLpiExternalSourceAdapter
    worldbank_lpi_adapter = WorldBankLpiExternalSourceAdapter(
        config={
            "source_id": settings.WORLDBANK_LPI_SOURCE_ID,
            "name": settings.WORLDBANK_LPI_SOURCE_NAME,
            "type": settings.WORLDBANK_LPI_SOURCE_TYPE,
            "version": settings.WORLDBANK_LPI_SOURCE_VERSION,
            "updated_at": settings.WORLDBANK_LPI_UPDATED_AT,
            "base_url": settings.WORLDBANK_LPI_BASE_URL,
            "timeout_seconds": settings.WORLDBANK_LPI_TIMEOUT_SECONDS,
        }
    )
    await knowledge_provider_registry.register(worldbank_lpi_adapter)
```

**Behavior:**
- Registration is conditional on `WORLDBANK_LPI_BASE_URL` being set.
- Registration failures are caught and logged as warnings; do not crash startup.
- No credentials required; registration proceeds if base URL is configured.

**Evidence:** Follows established pattern from `1786559160142-faostat-adapter-spec.md` Section 7.2 and `wp38b-task2-tradedata-adapter-spec.md` Section 8.

---



## 9. Test Coverage Specification

### 9.1 Unit Tests

| # | Test Case | Specification Reference |
|---|-----------|------------------------|
| 1 | `get_sources()` returns expected structure with World Bank LPI metadata | Section 6.1 |
| 2 | `query()` transforms World Bank LPI data correctly per this spec | Section 4.1, 4.2 |
| 3 | `query()` handles network failure gracefully (returns empty results, no exception) | Section 7.2 |
| 4 | `query()` handles malformed World Bank LPI data gracefully | Section 7.2 |
| 5 | Confidence scores within 0.0–1.0 per Section 5 rules | Section 5 |
| 6 | Provenance metadata populated correctly | Section 6.2 |
| 7 | Configuration settings loaded correctly | Section 8.1 |
| 8 | `query()` handles missing `country` or `indicator` in context | Section 2.3 |

**Deliverable:** 8+ passing unit tests

### 9.2 Integration Tests

| # | Test Case | Specification Reference |
|---|-----------|------------------------|
| 1 | World Bank LPI provider registers successfully in `KnowledgeProviderRegistry` | Section 8 |
| 2 | World Bank LPI provider is queryable via registry | Section 8 |
| 3 | `ReasoningEngine` can query World Bank LPI provider through registry | Section 1.2 |
| 4 | Existing providers still register after World Bank LPI provider | Section 1.2 |
| 5 | Fallback to other providers when World Bank LPI is unavailable | Section 2.3 |
| 6 | Graceful degradation does not crash application startup | Section 8.2 |

**Deliverable:** 6+ passing integration tests

**Evidence:** Test patterns follow existing adapter test suites (Moaah: 9 tests, TradeData: 14 tests, ZATCA: 13 tests, GCC-Stat: 9 tests, FAOSTAT: 17 tests).

---



## 10. Open Items & Unverified Details

The following items are explicitly unresolved in this specification and must be addressed during Task 3 implementation or subsequent verification:

| Item | Status | Evidence |
|------|--------|----------|
| Exact pagination behavior for multi-year queries | **Unverified** — requires live API testing with multiple years | **Assumption** — World Bank API supports `page` parameter |
| `obs_status` field semantics and all possible values | **Unverified** — requires World Bank metadata documentation | **Assumption** — draft treats non-empty obs_status as lower confidence |
| Rate-limit policy under production load | **Unverified** — World Bank Terms mention "reasonable request volume" but no numeric limit | **Assumption** — conservative no-retry policy adopted |
| LPI 2.0 (2023–2024) availability via Indicators API | **Unverified** — LPI 2.0 is published via Data360 separately | **Evidence** — G1 record separates traditional LPI from LPI 2.0 |
| Exact `decimal` field behavior for score precision | **Unverified** — observed value `2` in G1 verification | **Assumption** — draft preserves numeric value as returned |
| `unit` field content for LPI indicators | **Unverified** — observed empty string in G1 verification | **Assumption** — draft retains empty string if present |
| Country code normalization edge cases | **Unverified** — World Bank uses ISO 3-letter codes; some aggregations may differ | **Assumption** — draft preserves World Bank codes as-is |

---



## 11. Gate Status

| Gate | Status | Evidence |
|------|--------|----------|
| G0 — Portfolio Evaluation Approval | Approved | Section 19 Owner Approval Record |
| G1 — World Bank LPI Source Selection | **PASS** | Section 27.3 — G1 PASS recorded; all Provider Admission Criteria satisfied |
| G2 — Adapter Specification Review | **PASS** | `.kilo/plans/1786559160142-worldbank-lpi-adapter-spec.md` |
| G3 — Implementation Review | **PASS** | Implementation complete; tests passing |
| G4 — Verification | **PASS** | Live API verification passed; Egypt 2022 LPI = 3.1 |
| G5 — Closure | **PASS** | This closure record |

---



## 12. Constraints Reminders

- `KNOWLEDGE_INGESTION_CONTRACT.md` is immutable
- No modifications to `ReasoningEngine`, `TaskPlanner`, `ToolOrchestrator`, or any DEM core component
- No changes to `knowledge_nodes` or `knowledge_edges`
- No database migrations
- No frontend changes
- No additional providers
- No commits or pushes during planning
- World Bank LPI is the 7th provider within the operational ceiling of 7; no further ceiling expansion is authorized

---



*Specification Status: Approved — G2 PASS — G3 PASS — G4 PASS — G5 Closure — World Bank LPI Implemented Provider (7/7) — Portfolio Ceiling Reached — No Further Expansion Without Owner Approval*
