# WP-38b — Task 2: TradeData Adapter Specification

**Work Package:** WP-38b — Global Trade Intelligence (TradeData First Provider)  
**Task:** 2 — Define External Source Contract Adapter  
**Date:** 2026-08-13  
**Status:** Draft — Pending G2 Review  
**Authority:** `.kilo/plans/1786559139127-wp38b-global-trade-intelligence-plan.md` Section 7  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Provider:** TradeData API (`tradedata.io`)  
**Prerequisite:** Task 1 Source Evaluation completed; TradeData approved as WP-38b First Provider; G1 Approved

---

## 1. Adapter Boundary & Provider-Agnostic Architecture

### 1.1 Boundary

The TradeData adapter consists of two files:

- `tradedata_client.py` — isolated HTTP client for TradeData API
- `tradedata_provider.py` — `KnowledgeProvider` implementation that transforms TradeData responses into the DEM knowledge contract shape

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
| Provider Abstraction | All TradeData access is through `TradeDataExternalSourceAdapter(KnowledgeProvider)` |
| Registry-Only Registration | Registered in `KnowledgeProviderRegistry` only; DEM core never references TradeData directly |
| No DEM Core Coupling | No DEM core files modified except `config.py` (settings) and `main.py` (lifespan registration) |
| No Knowledge Graph Schema Changes | No writes to `knowledge_nodes` or `knowledge_edges` |
| No Contract Changes | `KNOWLEDGE_INGESTION_CONTRACT.md` unchanged |
| Config-Driven | All TradeData-specific settings loaded from `config.py` |
| Replaceable | Adapter can be replaced without redesigning Intelligence Layer |
| Composable | Multiple providers coexist in registry without mutual dependency |
| Observable | `get_sources()` exposes source metadata; query responses include `source_id` and provenance |

---

## 2. KnowledgeProvider Contract Implementation

### 2.1 Interface Compliance

`TradeDataExternalSourceAdapter` implements `KnowledgeProvider` with the following methods:

| Method | Signature | Return Shape |
|--------|-----------|--------------|
| `query()` | `async def query(self, query: str, context: Optional[Dict[str, Any]] = None, scope: Optional[str] = None, sources: Optional[List[str]] = None, limit: int = 10) -> Dict[str, Any]` | `{"results": [...], "confidence": float\|None, "sources": [source_id]}` |
| `get_sources()` | `async def get_sources(self) -> List[Dict[str, Any]]` | `[{"id": str, "name": str, "type": str, "version": str, "updated_at": str}]` |

### 2.2 Query Behavior

- **Required context:** `country` (from `context["country"]`)
- **Optional context:** `affected_country`, `start_date`, `end_date`, `hs_code`, `product_keyword`, `buyer_name`, `supplier_name`
- **Scope:** Mapped to TradeData endpoint selection; defaults to `"tradeDetail"` for transaction-level data
- **Sources parameter:** Accepted but not used for filtering; returned in response as `[source_id]`
- **Limit:** Applied to transformed results after fetching

### 2.3 Graceful Degradation

| Failure Mode | Behavior |
|--------------|----------|
| Missing `country` in context | Returns empty results with `confidence: None` |
| Missing `base_url` or `api_key` | Returns empty results with `confidence: None` |
| Network error / timeout | Returns empty results with `confidence: None` |
| HTTP 429 (rate limit) | Retries up to 3 times with exponential backoff (1s, 2s, 4s) |
| HTTP error status | Raises after retries exhausted; caught by outer handler → empty results |
| Malformed JSON / non-dict response | Returns empty results |
| Unexpected exception | Returns empty results |

---

## 3. Field Mapping & Transformation Rules

### 3.1 TradeData API → DEM Knowledge Shape

**TradeData `/api/v1/tradeDetail` request parameters:**

| TradeData Parameter | Source | Notes |
|---------------------|--------|-------|
| `data_coverage` | Fixed to `1` | Jan 2022 to present |
| `date_range` | `context["start_date"]` / `context["end_date"]` | Optional; format `[YYYYMMDD, YYYYMMDD]` |
| `product_keyword` | `context["product_keyword"]` or `query` | Optional array |
| `hs_code` | `context["hs_code"]` | Optional array |
| `buyer_name` | `context["buyer_name"]` | Optional array |
| `supplier_name` | `context["supplier_name"]` | Optional array |
| `origincl_country_code` | `context["country"]` or `context["affected_country"]` | Optional array |
| `desti_country_code` | `context["country"]` or `context["affected_country"]` | Optional array |
| `page` | Derived from `limit` and pagination | Min 1, max 1000 |
| `page_size` | Derived from `limit` | Default 10, max 50 |
| `sort` | Fixed to `"date"` | Default sort by date |
| `order` | Fixed to `"desc"` | Default descending |
| `Authorization` | `TRADEDATA_API_KEY` config | Bearer token in header |

**TradeData response sections mapped:**

| TradeData Field | Contract Mapping | Notes |
|-----------------|------------------|-------|
| `dataSource` | `metadata.source_authority` | e.g., "United States_Import" |
| `date` | `metadata.effective_date` | Transaction date |
| `buyerName` / `supplierName` | `content` (summary) | Importer/exporter names |
| `originCountryCode` / `destinationCountryCode` | `metadata.country` | ISO codes |
| `hsCode` / `hsCodeDesc` | `content` (detail) | Product classification |
| `quantity` / `weight` / `tradeAmount` | `content` (metrics) | Transaction metrics |
| `masterBl` / `containerNo` | `metadata.source_url` (reference) | Shipment identifiers |
| `otherInfo` | `metadata.legal_act_reference` | Supplementary data |
| *Adapter-assigned* | `source_id` | e.g., `tradedata` |
| *Adapter-assigned* | `confidence` | Per Section 4 rules |
| *Adapter-assigned* | `metadata.updated_at` | Fetch timestamp |

### 3.2 Result Construction

Each transformed result must conform to:

```json
{
  "id": "<adapter-generated-uuid>",
  "content": "<summary-text-or-structured-data>",
  "source_id": "tradedata",
  "confidence": <float-0.0-to-1.0>,
  "metadata": {
    "source_authority": "<dataSource>",
    "effective_date": "<date>",
    "country": "<originCountryCode-or-destinationCountryCode>",
    "source_url": "<masterBl-or-containerNo>",
    "legal_act_reference": "<otherInfo-summary>",
    "updated_at": "<fetch-timestamp>",
    "version": "<source-version>"
  }
}
```

**Note:** `version` is adapter-assigned based on TradeData source metadata; TradeData API does not expose a per-record version field.

---

## 4. Confidence Scoring Rules

Confidence is adapter-assigned. TradeData API does not provide confidence or quality fields in documented responses.

### 4.1 Base Confidence Levels

| Condition | Confidence | Rationale |
|-----------|------------|-----------|
| Successful fetch with valid `dataSource`, `date`, and at least one country code | **0.85** | Commercial aggregator; high reliability; data sourced from customs authorities |
| Missing `dataSource` or `date` but other core fields present | **0.75** | Partial record; still usable but lower certainty |
| Only minimal fields present (e.g., `hsCode` only) | **0.65** | Sparse record; limited actionable value |
| Malformed or incomplete record after transformation | **0.50** | Marginal; include only if no other data available |
| Network/timeout/empty response | **N/A** | No results returned |

### 4.2 Context-Dependent Adjustments

| Condition | Adjustment | Rationale |
|-----------|------------|-----------|
| Record matches explicit `hs_code` filter | **+0.05** (capped at 0.95) | Higher relevance to query |
| Record matches explicit `buyer_name` or `supplier_name` filter | **+0.05** (capped at 0.95) | Higher relevance to query |
| Record falls outside requested `date_range` | **-0.10** (floor 0.50) | Stale relative to query context |
| `dataSource` indicates lower-priority customs source | **-0.05** (floor 0.50) | Source reliability variance |

**Note:** Confidence rules may be refined during Task 3 implementation based on observed data quality. These are initial rules subject to adjustment.

---

## 5. Provenance Metadata

### 5.1 Source Metadata (`get_sources()`)

```json
{
  "id": "tradedata",
  "name": "TradeData API",
  "type": "external_trade_intelligence",
  "version": "1.0",
  "updated_at": "<fetch-timestamp-ISO8601>"
}
```

### 5.2 Per-Record Provenance

| Field | Source | Notes |
|-------|--------|-------|
| `source_id` | Adapter-assigned: `tradedata` | Fixed identifier for this provider |
| `metadata.source_authority` | `dataSource` | e.g., "United States_Import" |
| `metadata.effective_date` | `date` | Transaction date as provided by API |
| `metadata.country` | `originCountryCode` / `destinationCountryCode` | ISO 3166-1 alpha-2 codes |
| `metadata.source_url` | `masterBl` or `containerNo` | Shipment identifier as reference |
| `metadata.legal_act_reference` | `otherInfo` summary | Supplementary JSON data |
| `metadata.updated_at` | Adapter fetch timestamp | ISO 8601 format |
| `metadata.version` | Adapter-assigned | e.g., `"1.0"`; TradeData API does not expose version |

### 5.3 Provenance Guarantees

- `source_id` is never omitted
- `updated_at` is always populated with fetch timestamp
- `source_authority` is populated when `dataSource` is present
- `effective_date` is populated when `date` is present
- Missing provenance fields do not block ingestion; they are logged and assigned lowest confidence tier

---

## 6. Error Handling & Retry/Backoff

### 6.1 Retry Policy

| Condition | Action | Backoff |
|-----------|--------|---------|
| HTTP 429 (Too Many Requests) | Retry up to 3 times | Exponential backoff: 1s, 2s, 4s |
| Network error (connection timeout, DNS failure) | Retry up to 2 times | Fixed 2s interval |
| HTTP 500 / 502 / 503 | Retry up to 2 times | Exponential backoff: 2s, 4s |
| HTTP 400 / 403 | No retry | Immediate empty results |
| Other HTTP 4xx | No retry | Immediate empty results |
| JSON decode error | No retry | Immediate empty results |
| Unexpected exception | No retry | Immediate empty results |

**Note:** Exact retry counts and backoff intervals are initial values; they may be adjusted during Task 3 implementation based on observed behavior.

### 6.2 Timeout Configuration

| Setting | Default | Config Key | Notes |
|---------|---------|------------|-------|
| Connection timeout | 10s | `TRADEDATA_TIMEOUT_SECONDS` | Configurable |
| Read timeout | 30s | `TRADEDATA_TIMEOUT_SECONDS` | Configurable; trade data queries may be slow |

**Note:** Timeout values are initial estimates; actual values to be validated during Task 3 sandbox testing.

### 6.3 Error Response Handling

| HTTP Status | Behavior |
|-------------|----------|
| 200 | Parse response; transform records |
| 400 | Log error details; return empty results |
| 403 | Log error details; return empty results |
| 429 | Retry per policy; if exhausted, log and return empty results |
| 500 / 502 / 503 | Retry per policy; if exhausted, log and return empty results |
| Other 4xx | Log error details; return empty results |

**No exceptions are propagated to DEM core.** All errors are handled within the adapter.

---

## 7. Configuration

### 7.1 Required Settings

All TradeData-specific settings are defined in `config.py`:

| Setting | Type | Required | Description |
|---------|------|----------|-------------|
| `TRADEDATA_BASE_URL` | `str` | Yes | Base URL for TradeData API |
| `TRADEDATA_API_KEY` | `str` | Yes | Bearer token for authentication |
| `TRADEDATA_TIMEOUT_SECONDS` | `int` | No | Connection/read timeout (default: 30) |
| `TRADEDATA_SOURCE_ID` | `str` | Yes | Adapter-assigned source identifier |
| `TRADEDATA_SOURCE_NAME` | `str` | Yes | Human-readable source name |
| `TRADEDATA_SOURCE_TYPE` | `str` | Yes | Source type classification |
| `TRADEDATA_SOURCE_VERSION` | `str` | Yes | Adapter version |

### 7.2 Default Values

| Setting | Default | Notes |
|---------|---------|-------|
| `TRADEDATA_BASE_URL` | `https://api.tradedata.io` | Official base URL |
| `TRADEDATA_SOURCE_ID` | `tradedata` | Fixed identifier |
| `TRADEDATA_SOURCE_NAME` | `TradeData API` | Human-readable name |
| `TRADEDATA_SOURCE_TYPE` | `external_trade_intelligence` | Classification per contract |
| `TRADEDATA_SOURCE_VERSION` | `1.0` | Adapter version |

**Note:** `TRADEDATA_API_KEY` has no default; it must be provided via environment variable or secrets management. Missing key triggers graceful degradation (empty results).

---

## 8. Registry Integration

### 8.1 Registration Pattern

TradeData provider is registered in `KnowledgeProviderRegistry` during application startup via `main.py` `lifespan()`:

```python
# Pseudocode — implementation detail for Task 4
try:
    registry.register(TradeDataExternalSourceAdapter(config=settings))
except Exception as e:
    logger.error(f"Failed to register TradeData provider: {e}")
```

### 8.2 Registration Behavior

| Condition | Behavior |
|-----------|----------|
| Valid config + API key | Provider registers successfully |
| Missing API key | Registration skipped; logged warning; no crash |
| Network unreachable at startup | Registration succeeds; errors handled at query time |
| Exception during registration | Caught by outer handler; logged; application continues |

---

## 9. Test Requirements (Specification-Level)

These test requirements are derived from the WP-38b plan Section 7 Task 5 and must be satisfied by the implementation:

### 9.1 Unit Tests (Task 5)

| # | Test Case | Specification Reference |
|---|-----------|------------------------|
| 1 | `get_sources()` returns expected structure with TradeData metadata | Section 8.1 |
| 2 | `query()` transforms TradeData data correctly per this spec | Section 3.1, 3.2 |
| 3 | `query()` handles network failure gracefully (returns empty results, no exception) | Section 6.3 |
| 4 | `query()` handles malformed TradeData data gracefully | Section 6.3 |
| 5 | Confidence scores within 0.0–1.0 per Section 4 rules | Section 4 |
| 6 | Provenance metadata populated correctly | Section 5 |
| 7 | Configuration settings loaded correctly | Section 7 |
| 8 | Retry/backoff behavior verified | Section 6.1 |

**Deliverable:** 8+ passing unit tests

### 9.2 Integration Tests (Task 6)

| # | Test Case | Specification Reference |
|---|-----------|------------------------|
| 1 | TradeData provider registers successfully in `KnowledgeProviderRegistry` | Section 8 |
| 2 | TradeData provider is queryable via registry | Section 8 |
| 3 | `ReasoningEngine` can query TradeData provider through registry | Section 1.2 |
| 4 | Existing providers still register after TradeData provider | Section 1.2 |
| 5 | Fallback to other providers when TradeData is unavailable | Section 2.3 |
| 6 | Graceful degradation does not crash application startup | Section 8.2 |

**Deliverable:** 6+ passing integration tests

---

## 10. Open Items & TBD

The following items are explicitly unresolved in this specification and must be addressed during Task 3 implementation or subsequent verification:

| Item | Status | Resolution Path |
|------|--------|-----------------|
| Exact numeric rate limits (RPM/RPS) | **TBD** | Public docs do not specify; confirm during sandbox testing |
| Sandbox API key provisioning process | **TBD** | Contact TradeData sales/support |
| Egypt (EG) explicit response sample | **TBD** | Requires live sandbox query with `desti_country_code: ["EG"]` |
| Actual response latency | **TBD** | Measure during Task 3 implementation |
| Commercial terms detail (written) | **TBD** | Project Owner approved use model; written terms optional |
| `otherInfo` structure variability | **TBD** | Schema is JSON; exact fields vary by record |
| `dataSource` value format consistency | **TBD** | Observed values vary by trade lane; normalization may be needed |
| Confidence rule calibration | **TBD** | Initial rules in Section 4; refine after observing data quality |
| Retry count/backoff tuning | **TBD** | Initial values in Section 6.1; adjust based on observed 429 behavior |

---

## 11. Specification Review Checklist

This section enables later review of implementation against this specification:

| Area | Spec Section | Implementation File | Review Check |
|------|--------------|---------------------|--------------|
| Adapter boundary | 1.1 | `tradedata_provider.py`, `tradedata_client.py` | No DEM core modifications |
| Provider-Agnostic compliance | 1.2 | All adapter files | Registry-only; no hardcoded DEM references |
| `query()` signature | 2.1 | `tradedata_provider.py` | Matches `KnowledgeProvider` ABC |
| `get_sources()` signature | 2.1 | `tradedata_provider.py` | Returns required metadata fields |
| Field mapping | 3.1, 3.2 | `tradedata_provider.py` | All mapped fields present in output |
| Confidence rules | 4 | `tradedata_provider.py` | Scores within 0.0–1.0; rules applied |
| Provenance metadata | 5 | `tradedata_provider.py` | All fields populated per rules |
| Error handling | 6 | `tradedata_client.py`, `tradedata_provider.py` | No exceptions leak to DEM core |
| Retry/backoff | 6.1 | `tradedata_client.py` | Exponential backoff on 429/5xx |
| Configuration | 7 | `config.py`, `tradedata_provider.py` | All settings loaded from config |
| Registry integration | 8 | `main.py` | Conditional registration in `lifespan()` |
| Unit tests | 9.1 | `tests/agent/test_tradedata_provider.py` | 8+ tests pass |
| Integration tests | 9.2 | `tests/agent/test_tradedata_integration.py` | 6+ tests pass |

---

## 12. Constraints Reminders

- `KNOWLEDGE_INGESTION_CONTRACT.md` is immutable
- No modifications to `ReasoningEngine`, `TaskPlanner`, `ToolOrchestrator`, or any DEM core component
- No changes to `knowledge_nodes` or `knowledge_edges`
- No database migrations
- No frontend changes
- No WP-38c/38d work
- No additional providers in WP-38b
- No commits or pushes during planning

---

*Specification Status: Draft — Pending G2 Review*
