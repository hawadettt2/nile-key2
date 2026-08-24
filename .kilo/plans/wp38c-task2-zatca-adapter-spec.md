# WP-38c â€” Task 2: ZATCA Adapter Specification

**Work Package:** WP-38c â€” Jordan + UAE + Saudi/GCC Sources  
**Task:** 2 â€” Define External Source Contract Adapter  
**Date:** 2026-08-14  
**Status:** Draft â€” Pending G2 Review  
**Authority:** `\.kilo/plans/archive/1786559140128-wp38c-jordan-uae-saudi-gcc-sources-plan\.md` Section 6  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Provider:** ZATCA Open Data APIs (`zatca.gov.sa`)  
**Prerequisite:** Task 1 Source Evaluation completed; ZATCA approved as WP-38c First Provider; G1 Approved

---

## 1. Adapter Boundary & Provider-Agnostic Architecture

### 1.1 Boundary

The ZATCA adapter consists of two files:

- `zatca_client.py` â€” isolated HTTP client for ZATCA Open Data APIs
- `zatca_provider.py` â€” `KnowledgeProvider` implementation that transforms ZATCA responses into the DEM knowledge contract shape

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
| Provider Abstraction | All ZATCA access is through `ZatcaExternalSourceAdapter(KnowledgeProvider)` |
| Registry-Only Registration | Registered in `KnowledgeProviderRegistry` only; DEM core never references ZATCA directly |
| No DEM Core Coupling | No DEM core files modified except `config.py` (settings) and `main.py` (lifespan registration) |
| No Knowledge Graph Schema Changes | No writes to `knowledge_nodes` or `knowledge_edges` |
| No Contract Changes | `KNOWLEDGE_INGESTION_CONTRACT.md` unchanged |
| Config-Driven | All ZATCA-specific settings loaded from `config.py` |
| Replaceable | Adapter can be replaced without redesigning Intelligence Layer |
| Composable | Multiple providers coexist in registry without mutual dependency |
| Observable | `get_sources()` exposes source metadata; query responses include `source_id` and provenance |

---

## 2. KnowledgeProvider Contract Implementation

### 2.1 Interface Compliance

`ZatcaExternalSourceAdapter` implements `KnowledgeProvider` with the following methods:

| Method | Signature | Return Shape |
|--------|-----------|--------------|
| `query()` | `async def query(self, query: str, context: Optional[Dict[str, Any]] = None, scope: Optional[str] = None, sources: Optional[List[str]] = None, limit: int = 10) -> Dict[str, Any]` | `{"results": [...], "confidence": float\|None, "sources": [source_id]}` |
| `get_sources()` | `async def get_sources(self) -> List[Dict[str, Any]]` | `[{"id": str, "name": str, "type": str, "version": str, "updated_at": str}]` |

### 2.2 Query Behavior

- **Required context:** `country` (from `context["country"]`)
- **Optional context:** `start_date`, `end_date`, `port_name`, `traffic_type`
- **Scope:** Mapped to ZATCA endpoint selection; defaults to `"export_import_details"` for trade transaction data
- **Sources parameter:** Accepted but not used for filtering; returned in response as `[source_id]`
- **Limit:** Applied to transformed results after fetching

### 2.3 Graceful Degradation

| Failure Mode | Behavior |
|--------------|----------|
| Missing `country` in context | Returns empty results with `confidence: None` |
| Missing `base_url` or `api_key` | Returns empty results with `confidence: None` |
| Network error / timeout | Returns empty results with `confidence: None` |
| HTTP 429 (rate limit) | Retries up to 3 times with exponential backoff (1s, 2s, 4s) |
| HTTP error status | Raises after retries exhausted; caught by outer handler â†’ empty results |
| Malformed JSON / non-dict response | Returns empty results |
| Unexpected exception | Returns empty results |

---

## 3. Field Mapping & Transformation Rules

### 3.1 ZATCA API â†’ DEM Knowledge Shape

**Note:** Detailed request/response schemas are TBD pending sandbox access and Swagger documentation review during Task 3. The following represents the intended mapping based on documented API names and standard customs data patterns.

**ZATCA API request parameters (intended):**

| ZATCA Parameter | Source | Notes |
|-----------------|--------|-------|
| `country` | `context["country"]` | Fixed to `SA` for Saudi Arabia |
| `start_date` | `context["start_date"]` | Optional; format TBD per Swagger |
| `end_date` | `context["end_date"]` | Optional; format TBD per Swagger |
| `port_name` | `context["port_name"]` | Optional; e.g., "Jeddah", "Dammam" |
| `traffic_type` | `context["traffic_type"]` | Optional; e.g., "import", "export" |
| `limit` | Derived from `limit` parameter | Default 10, max per API |
| `page` | Derived from pagination | Min 1 |
| `Authorization` | `ZATCA_API_KEY` config | API key in header |

**ZATCA API endpoints (intended mapping):**

| Scope Value | ZATCA API Endpoint | Purpose |
|-------------|-------------------|---------|
| `export_import_details` | Export and Import Details API | Export/import transaction details |
| `clearance_port` | Clearance Port API | Customs clearance port data |
| `port_clearance_details` | Port Clearance Details API | Port clearance information |
| `port_traffic` | Port Traffic API | Port traffic statistics |
| `explore_data` | ZATCA Explore Data API | General ZATCA data exploration |

### 3.2 ZATCA Response Sections Mapped (Intended)

| ZATCA Field (TBD) | Contract Mapping | Notes |
|-------------------|------------------|-------|
| API response fields | `content` | To be defined based on actual Swagger schema |
| API metadata | `metadata.source_authority` | e.g., "ZATCA_OpenData" |
| API timestamp | `metadata.effective_date` | To be mapped from API response |
| Country code | `metadata.country` | Fixed `SA` for Saudi Arabia |
| API endpoint | `metadata.source_url` | Reference to specific API endpoint |
| Supplementary data | `metadata.legal_act_reference` | If available |
| *Adapter-assigned* | `source_id` | e.g., `zatca` |
| *Adapter-assigned* | `confidence` | Per Section 4 rules |
| *Adapter-assigned* | `metadata.updated_at` | Fetch timestamp |

**Note:** Detailed field mapping requires access to actual Swagger schemas during Task 3. This section defines the intended mapping pattern only.

### 3.3 Result Construction (Intended)

Each transformed result must conform to:

```json
{
  "id": "<adapter-generated-uuid>",
  "content": "<summary-text-or-structured-data>",
  "source_id": "zatca",
  "confidence": <float-0.0-to-1.0>,
  "metadata": {
    "source_authority": "ZATCA_OpenData",
    "effective_date": "<date-from-api>",
    "country": "SA",
    "source_url": "<endpoint-reference>",
    "legal_act_reference": "<if-available>",
    "updated_at": "<fetch-timestamp>",
    "version": "<source-version>",
    "record_hash": "<sha256-of-entry>",
    "retrieval_status": "<success|partial|failed>"
  }
}
```

---

## 4. Confidence Scoring Rules

Confidence is adapter-assigned. ZATCA API does not provide confidence or quality fields in documented responses.

### 4.1 Base Confidence Levels

| Condition | Confidence | Rationale |
|-----------|------------|-----------|
| Successful fetch with valid data fields and timestamp | **0.85** | Official government source; high reliability |
| Missing timestamp but other core fields present | **0.75** | Partial record; still usable but lower certainty |
| Only minimal fields present | **0.65** | Sparse record; limited actionable value |
| Malformed or incomplete record after transformation | **0.50** | Marginal; include only if no other data available |
| Network/timeout/empty response | **N/A** | No results returned |

### 4.2 Context-Dependent Adjustments

| Condition | Adjustment | Rationale |
|-----------|------------|-----------|
| Record matches explicit `port_name` filter | **+0.05** (capped at 0.95) | Higher relevance to query |
| Record matches explicit `traffic_type` filter | **+0.05** (capped at 0.95) | Higher relevance to query |
| Record falls outside requested `date_range` | **-0.10** (floor 0.50) | Stale relative to query context |

**Note:** Confidence rules are initial values and may be refined during Task 3 implementation based on observed data quality and actual API response fields.

---

## 5. Provenance Metadata

### 5.1 Source Metadata (`get_sources()`)

```json
{
  "id": "zatca",
  "name": "ZATCA Open Data APIs",
  "type": "external_trade_intelligence",
  "version": "1.0",
  "updated_at": "<fetch-timestamp-ISO8601>"
}
```

### 5.2 Per-Record Provenance

| Field | Source | Notes |
|-------|--------|-------|
| `source_id` | Adapter-assigned: `zatca` | Fixed identifier for this provider |
| `metadata.source_authority` | Adapter-assigned: `ZATCA_OpenData` | Official Saudi government source |
| `metadata.effective_date` | API timestamp | To be mapped from actual response |
| `metadata.country` | Fixed: `SA` | Saudi Arabia ISO 3166-1 alpha-2 |
| `metadata.source_url` | API endpoint reference | e.g., `/api/v1/export-import-details` |
| `metadata.legal_act_reference` | Supplementary data if available | TBD per actual API |
| `metadata.updated_at` | Adapter fetch timestamp | ISO 8601 format |
| `metadata.version` | Adapter-assigned | e.g., `"1.0"` |
| `metadata.record_hash` | SHA-256 of response entry | For deduplication/versioning |
| `metadata.retrieval_status` | Adapter-calculated | `success`, `partial`, or `failed` |

### 5.3 Provenance Guarantees

- `source_id` is never omitted
- `updated_at` is always populated with fetch timestamp
- `source_authority` is always populated
- `effective_date` is populated when API provides timestamp
- `country` is always `SA` for ZATCA
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

**Note:** Exact retry counts and backoff intervals are initial values; they may be adjusted during Task 3 implementation based on observed behavior. Rate limit thresholds are unknown and TBD.

### 6.2 Timeout Configuration

| Setting | Default | Config Key | Notes |
|---------|---------|------------|-------|
| Connection timeout | 10s | `ZATCA_TIMEOUT_SECONDS` | Configurable |
| Read timeout | 30s | `ZATCA_TIMEOUT_SECONDS` | Configurable; API queries may be slow |

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

All ZATCA-specific settings are defined in `config.py`:

| Setting | Type | Required | Description |
|---------|------|----------|-------------|
| `ZATCA_BASE_URL` | `str` | Yes | Base URL for ZATCA Open Data APIs |
| `ZATCA_API_KEY` | `str` | Yes | API key for authentication |
| `ZATCA_TIMEOUT_SECONDS` | `int` | No | Connection/read timeout (default: 30) |
| `ZATCA_SOURCE_ID` | `str` | Yes | Adapter-assigned source identifier |
| `ZATCA_SOURCE_NAME` | `str` | Yes | Human-readable source name |
| `ZATCA_SOURCE_TYPE` | `str` | Yes | Source type classification |
| `ZATCA_SOURCE_VERSION` | `str` | Yes | Adapter version |

### 7.2 Default Values

| Setting | Default | Notes |
|---------|---------|-------|
| `ZATCA_BASE_URL` | **TBD** | Requires sandbox/production URL from ZATCA |
| `ZATCA_API_KEY` | No default | Must be provided via environment variable or secrets management |
| `ZATCA_SOURCE_ID` | `zatca` | Fixed identifier |
| `ZATCA_SOURCE_NAME` | `ZATCA Open Data APIs` | Human-readable name |
| `ZATCA_SOURCE_TYPE` | `external_trade_intelligence` | Classification per contract |
| `ZATCA_SOURCE_VERSION` | `1.0` | Adapter version |

**Note:** `ZATCA_BASE_URL` is TBD pending sandbox access. Missing key triggers graceful degradation (empty results).

---

## 8. Registry Integration

### 8.1 Registration Pattern

ZATCA provider is registered in `KnowledgeProviderRegistry` during application startup via `main.py` `lifespan()`:

```python
# Pseudocode â€” implementation detail for Task 4
try:
    registry.register(ZatcaExternalSourceAdapter(config=settings))
except Exception as e:
    logger.error(f"Failed to register ZATCA provider: {e}")
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

These test requirements are derived from the WP-38c plan Section 6 and must be satisfied by the implementation:

### 9.1 Unit Tests (Task 5)

| # | Test Case | Specification Reference |
|---|-----------|------------------------|
| 1 | `get_sources()` returns expected structure with ZATCA metadata | Section 5.1 |
| 2 | `query()` transforms ZATCA data correctly per this spec | Section 3.1, 3.2, 3.3 |
| 3 | `query()` handles network failure gracefully (returns empty results, no exception) | Section 2.3 |
| 4 | `query()` handles malformed ZATCA data gracefully | Section 2.3 |
| 5 | Confidence scores within 0.0â€“1.0 per Section 4 rules | Section 4 |
| 6 | Provenance metadata populated correctly | Section 5 |
| 7 | Configuration settings loaded correctly | Section 7 |
| 8 | Retry/backoff behavior verified | Section 6.1 |

**Deliverable:** 8+ passing unit tests

### 9.2 Integration Tests (Task 6)

| # | Test Case | Specification Reference |
|---|-----------|------------------------|
| 1 | ZATCA provider registers successfully in `KnowledgeProviderRegistry` | Section 8 |
| 2 | ZATCA provider is queryable via registry | Section 8 |
| 3 | `ReasoningEngine` can query ZATCA provider through registry | Section 1.2 |
| 4 | Existing providers still register after ZATCA provider | Section 1.2 |
| 5 | Fallback to other providers when ZATCA is unavailable | Section 2.3 |
| 6 | Graceful degradation does not crash application startup | Section 8.2 |

**Deliverable:** 6+ passing integration tests

---

## 10. Open Items & TBD

The following items are explicitly unresolved in this specification and must be addressed during Task 3 implementation or subsequent verification:

| Item | Status | Resolution Path |
|------|--------|-----------------|
| Exact API base URL | **TBD** | Requires sandbox access; obtain from Developer Portal |
| API key provisioning process | **TBD** | Requires developer account creation at https://sandbox.zatca.gov.sa/ |
| Exact request/response schemas | **TBD** | Requires Swagger documentation review during Task 3 |
| Saudi (SA) explicit response sample | **TBD** | Requires live sandbox query |
| Rate limit numeric values | **TBD** | Not publicly documented; confirm during sandbox testing |
| Actual response latency | **TBD** | Measure during Task 3 implementation |
| Authentication method details | **TBD** | API key suspected; confirm during sandbox access |
| Field mapping details | **TBD** | Requires actual API schema from Swagger docs |
| Confidence rule calibration | **TBD** | Initial rules in Section 4; refine after observing data quality |
| Retry count/backoff tuning | **TBD** | Initial values in Section 6.1; adjust based on observed 429 behavior |
| Endpoint selection logic | **TBD** | Requires understanding of API capabilities during Task 3 |

---

## 11. Specification Review Checklist

This section enables later review of implementation against this specification:

| Area | Spec Section | Implementation File | Review Check |
|------|--------------|---------------------|--------------|
| Adapter boundary | 1.1 | `zatca_provider.py`, `zatca_client.py` | No DEM core modifications |
| Provider-Agnostic compliance | 1.2 | All adapter files | Registry-only; no hardcoded DEM references |
| `query()` signature | 2.1 | `zatca_provider.py` | Matches `KnowledgeProvider` ABC |
| `get_sources()` signature | 2.1 | `zatca_provider.py` | Returns required metadata fields |
| Field mapping | 3.1, 3.2, 3.3 | `zatca_provider.py` | All mapped fields present in output |
| Confidence rules | 4 | `zatca_provider.py` | Scores within 0.0â€“1.0; rules applied |
| Provenance metadata | 5 | `zatca_provider.py` | All fields populated per rules |
| Error handling | 6 | `zatca_client.py`, `zatca_provider.py` | No exceptions leak to DEM core |
| Retry/backoff | 6.1 | `zatca_client.py` | Exponential backoff on 429/5xx |
| Configuration | 7 | `config.py`, `zatca_provider.py` | All settings loaded from config |
| Registry integration | 8 | `main.py` | Conditional registration in `lifespan()` |
| Unit tests | 9.1 | `tests/agent/test_zatca_provider.py` | 8+ tests pass |
| Integration tests | 9.2 | `tests/agent/test_zatca_integration.py` | 6+ tests pass |

---

## 12. Constraints Reminders

- `KNOWLEDGE_INGESTION_CONTRACT.md` is immutable
- No modifications to `ReasoningEngine`, `TaskPlanner`, `ToolOrchestrator`, or any DEM core component
- No changes to `knowledge_nodes` or `knowledge_edges`
- No database migrations
- No frontend changes
- No WP-38d work
- No additional providers in WP-38c
- No commits or pushes during planning

---

*Specification Status: Draft â€” Pending G2 Review*

