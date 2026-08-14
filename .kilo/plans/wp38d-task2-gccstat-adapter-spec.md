# WP-38d — Task 2: GCC-Stat Adapter Specification

**Work Package:** WP-38d — GCC Expansion (GCC-Stat First Provider)  
**Task:** 2 — Define External Source Contract Adapter  
**Date:** 2026-08-14  
**Status:** Draft — Pending G2 Review  
**Authority:** `.kilo/plans/1786559150139-wp38d-gcc-expansion-plan.md` Section 7  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Provider:** GCC-Stat Data Portal (`gccstat.org`)  
**Prerequisite:** Task 1 Source Evaluation completed; GCC-Stat approved as WP-38d First Provider; G1 Approved per `.kilo/plans/wp38d-owner-acceptance-certificate.md`

---

## 1. Adapter Boundary & Provider-Agnostic Architecture

### 1.1 Boundary

The GCC-Stat adapter consists of two files:

- `gccstat_client.py` — isolated HTTP client for GCC-Stat REST/SDMX APIs
- `gccstat_provider.py` — `KnowledgeProvider` implementation that transforms GCC-Stat responses into the DEM knowledge contract shape

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
| Provider Abstraction | All GCC-Stat access is through `GccstatExternalSourceAdapter(KnowledgeProvider)` |
| Registry-Only Registration | Registered in `KnowledgeProviderRegistry` only; DEM core never references GCC-Stat directly |
| No DEM Core Coupling | No DEM core files modified except `config.py` (settings) and `main.py` (lifespan registration) |
| No Knowledge Graph Schema Changes | No writes to `knowledge_nodes` or `knowledge_edges` |
| No Contract Changes | `KNOWLEDGE_INGESTION_CONTRACT.md` unchanged |
| Config-Driven | All GCC-Stat-specific settings loaded from `config.py` |
| Replaceable | Adapter can be replaced without redesigning Intelligence Layer |
| Composable | Multiple providers coexist in registry without mutual dependency |
| Observable | `get_sources()` exposes source metadata; query responses include `source_id` and provenance |

---

## 2. KnowledgeProvider Contract Implementation

### 2.1 Interface Compliance

`GccstatExternalSourceAdapter` implements `KnowledgeProvider` with the following methods:

| Method | Signature | Return Shape |
|--------|-----------|--------------|
| `query()` | `async def query(self, query: str, context: Optional[Dict[str, Any]] = None, scope: Optional[str] = None, sources: Optional[List[str]] = None, limit: int = 10) -> Dict[str, Any]` | `{"results": [...], "confidence": float\|None, "sources": [source_id]}` |
| `get_sources()` | `async def get_sources(self) -> List[Dict[str, Any]]` | `[{"id": str, "name": str, "type": str, "version": str, "updated_at": str}]` |

### 2.2 Query Behavior

- **Required context:** None strictly required; `query` is mapped to GCC-Stat dataflow or keyword search
- **Optional context:** `country` (GCC member state filter), `start_date`, `end_date`, `indicator_category`
- **Scope:** Mapped to GCC-Stat dataflow selection or dataset category; defaults to general trade/economic indicators
- **Sources parameter:** Accepted but not used for filtering; returned in response as `[source_id]`
- **Limit:** Applied to transformed results after fetching

### 2.3 Graceful Degradation

| Failure Mode | Behavior |
|--------------|----------|
| Missing `base_url` or API key | Returns empty results with `confidence: None` |
| Network error / timeout | Returns empty results with `confidence: None` |
| HTTP 429 (rate limit) | Retries up to 3 times with exponential backoff (1s, 2s, 4s) |
| HTTP error status | Raises after retries exhausted; caught by outer handler → empty results |
| SDMX parse error / malformed response | Returns empty results |
| Unexpected exception | Returns empty results |

---

## 3. Field Mapping & Transformation Rules

### 3.1 GCC-Stat API → DEM Knowledge Shape

**Note:** Detailed request/response schemas are TBD pending live API access and SDMX structure review during Task 3. The following represents the intended mapping pattern based on documented GCC-Stat capabilities.

**GCC-Stat API request parameters (intended):**

| GCC-Stat Parameter | Source | Notes |
|--------------------|--------|-------|
| `query` | `query` parameter | Keyword or dataflow reference |
| `start_period` | `context["start_date"]` | Optional; format TBD per SDMX spec |
| `end_period` | `context["end_date"]` | Optional; format TBD per SDMX spec |
| `ref_area` | `context["country"]` | Optional; GCC member state code |
| `indicator` | `context["indicator_category"]` | Optional; trade/economic indicator filter |
| `limit` | Derived from `limit` parameter | Default 10, max per API |
| `Authorization` | `GCCSTAT_API_KEY` config | API key if required |

**GCC-Stat API endpoints (intended mapping):**

| Access Mode | Endpoint / URL | Purpose |
|-------------|----------------|---------|
| SDMX REST Data | `https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest/data/{agency}/{dataflow}/{version}` | Structured statistical data |
| SDMX REST Structure | `https://sdmx.marsa.gccstat.org/FusionRegistry/ws/public/sdmxapi/rest/structure/{structure_type}` | Metadata and codelists |
| DKAN Dataset API | `https://dp.marsa.gccstat.org/api/dataset/node/{nid}` | Dataset metadata |
| DKAN Datastore API | `https://dp.marsa.gccstat.org/api/datastore/{resource_id}` | Tabular dataset access |

**Endpoint selection logic:** TBD — requires verification of available dataflows and dataset IDs during Task 3.

### 3.2 GCC-Stat Response Sections Mapped (Intended)

| GCC-Stat Field (TBD) | Contract Mapping | Notes |
|----------------------|------------------|-------|
| SDMX observation value / dataset value | `content` | To be defined based on actual SDMX/JSON structure |
| Series / dataset metadata | `metadata.source_authority` | e.g., "GCC-Stat" |
| Time period / reference date | `metadata.effective_date` | To be mapped from SDMX TIME_PERIOD or dataset date field |
| Country / ref_area code | `metadata.country` | ISO 3166-1 alpha-2 or GCC member state code |
| Dataset / dataflow ID | `metadata.source_url` | Reference to specific dataset or dataflow |
| Legal / methodology reference | `metadata.legal_act_reference` | If available in metadata |
| *Adapter-assigned* | `source_id` | e.g., `gccstat` |
| *Adapter-assigned* | `confidence` | Per Section 4 rules |

### 3.3 Result Construction (Intended)

Each transformed result must conform to:

```json
{
  "id": "<adapter-generated-uuid>",
  "content": "<summary-text-or-structured-data>",
  "source_id": "gccstat",
  "confidence": <float-0.0-to-1.0>,
  "metadata": {
    "source_authority": "GCC-Stat",
    "effective_date": "<date-from-api>",
    "country": "<ISO-country-code>",
    "source_url": "<dataset-or-dataflow-reference>",
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

Confidence is adapter-assigned. GCC-Stat API does not provide confidence or quality fields in documented responses.

### 4.1 Base Confidence Levels

| Condition | Confidence | Rationale |
|-----------|------------|-----------|
| Successful fetch with valid data fields and timestamp | **0.85** | Official GCC statistical source; high reliability |
| Missing timestamp but other core fields present | **0.75** | Partial record; still usable but lower certainty |
| Only minimal fields present | **0.65** | Sparse record; limited actionable value |
| Malformed or incomplete record after transformation | **0.50** | Marginal; include only if no other data available |
| Network/timeout/empty response | **N/A** | No results returned |

### 4.2 Context-Dependent Adjustments

| Condition | Adjustment | Rationale |
|-----------|------------|-----------|
| Record matches explicit `country` filter | **+0.05** (capped at 0.95) | Higher relevance to query |
| Record matches explicit `indicator_category` filter | **+0.05** (capped at 0.95) | Higher relevance to query |
| Record falls outside requested `date_range` | **-0.10** (floor 0.50) | Stale relative to query context |

**Note:** Confidence rules are initial values and may be refined during Task 3 implementation based on observed data quality and actual API response fields.

---

## 5. Provenance Metadata

### 5.1 Source Metadata (`get_sources()`)

```json
{
  "id": "gccstat",
  "name": "GCC-Stat Data Portal",
  "type": "external_trade_intelligence",
  "version": "1.0",
  "updated_at": "<fetch-timestamp-ISO8601>"
}
```

### 5.2 Per-Record Provenance

| Field | Source | Notes |
|-------|--------|-------|
| `source_id` | Adapter-assigned: `gccstat` | Fixed identifier for this provider |
| `metadata.source_authority` | Adapter-assigned: `GCC-Stat` | Official GCC statistical body |
| `metadata.effective_date` | API timestamp / TIME_PERIOD | To be mapped from actual SDMX/JSON response |
| `metadata.country` | Derived from `ref_area` or context | ISO 3166-1 alpha-2 or GCC member state code |
| `metadata.source_url` | Dataset / dataflow reference | e.g., `/api/dataset/node/123` or dataflow ID |
| `metadata.legal_act_reference` | Supplementary data if available | TBD per actual API |
| `metadata.updated_at` | Adapter fetch timestamp | ISO 8601 format |
| `metadata.version` | Adapter-assigned | e.g., `"1.0"` |
| `metadata.record_hash` | SHA-256 of response entry | For deduplication/versioning |
| `metadata.retrieval_status` | Adapter-calculated | `success`, `partial`, or `failed` |

### 5.3 Provenance Guarantees

- `source_id` is never omitted
- `updated_at` is always populated with fetch timestamp
- `source_authority` is always populated
- `effective_date` is populated when API provides timestamp or TIME_PERIOD
- `country` is populated when `ref_area` is present in response
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
| SDMX/JSON decode error | No retry | Immediate empty results |
| Unexpected exception | No retry | Immediate empty results |

**Note:** Exact retry counts and backoff intervals are initial values; they may be adjusted during Task 3 implementation based on observed behavior. Rate limit thresholds are unknown and TBD.

### 6.2 Timeout Configuration

| Setting | Default | Config Key | Notes |
|---------|---------|------------|-------|
| Connection timeout | 10s | `GCCSTAT_TIMEOUT_SECONDS` | Configurable |
| Read timeout | 30s | `GCCSTAT_TIMEOUT_SECONDS` | Configurable; SDMX queries may be slow |

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

All GCC-Stat-specific settings are defined in `config.py`:

| Setting | Type | Required | Description |
|---------|------|----------|-------------|
| `GCCSTAT_BASE_URL` | `str` | Yes | Base URL for GCC-Stat REST/SDMX APIs |
| `GCCSTAT_API_KEY` | `str` | No | API key if required by GCC-Stat |
| `GCCSTAT_TIMEOUT_SECONDS` | `int` | No | Connection/read timeout (default: 30) |
| `GCCSTAT_SOURCE_ID` | `str` | Yes | Adapter-assigned source identifier |
| `GCCSTAT_SOURCE_NAME` | `str` | Yes | Human-readable source name |
| `GCCSTAT_SOURCE_TYPE` | `str` | Yes | Source type classification |
| `GCCSTAT_SOURCE_VERSION` | `str` | Yes | Adapter version |

### 7.2 Default Values

| Setting | Default | Notes |
|---------|---------|-------|
| `GCCSTAT_BASE_URL` | **TBD** | Requires verification of production endpoint; candidates: `https://sdmx.marsa.gccstat.org` or `https://dp.marsa.gccstat.org` |
| `GCCSTAT_API_KEY` | No default | TBD — public SDMX API may not require key; confirm during Task 3 |
| `GCCSTAT_SOURCE_ID` | `gccstat` | Fixed identifier |
| `GCCSTAT_SOURCE_NAME` | `GCC-Stat Data Portal` | Human-readable name |
| `GCCSTAT_SOURCE_TYPE` | `external_trade_intelligence` | Classification per contract |
| `GCCSTAT_SOURCE_VERSION` | `1.0` | Adapter version |

**Note:** `GCCSTAT_BASE_URL` and `GCCSTAT_API_KEY` are TBD pending live API verification. Missing key or base URL triggers graceful degradation (empty results).

---

## 8. Registry Integration

### 8.1 Registration Pattern

GCC-Stat provider is registered in `KnowledgeProviderRegistry` during application startup via `main.py` `lifespan()`:

```python
# Pseudocode — implementation detail for Task 4
try:
    registry.register(GccstatExternalSourceAdapter(config=settings))
except Exception as e:
    logger.error(f"Failed to register GCC-Stat provider: {e}")
```

### 8.2 Registration Behavior

| Condition | Behavior |
|-----------|----------|
| Valid config + API key (if required) | Provider registers successfully |
| Missing API key (if required) | Registration skipped; logged warning; no crash |
| Network unreachable at startup | Registration succeeds; errors handled at query time |
| Exception during registration | Caught by outer handler; logged; application continues |

---

## 9. Test Requirements (Specification-Level)

These test requirements are derived from the WP-38d plan Section 7 and must be satisfied by the implementation:

### 9.1 Unit Tests (Task 5)

| # | Test Case | Specification Reference |
|---|-----------|------------------------|
| 1 | `get_sources()` returns expected structure with GCC-Stat metadata | Section 5.1 |
| 2 | `query()` transforms GCC-Stat data correctly per this spec | Section 3.1, 3.2, 3.3 |
| 3 | `query()` handles network failure gracefully (returns empty results, no exception) | Section 2.3 |
| 4 | `query()` handles malformed GCC-Stat data gracefully | Section 2.3 |
| 5 | Confidence scores within 0.0–1.0 per Section 4 rules | Section 4 |
| 6 | Provenance metadata populated correctly | Section 5 |
| 7 | Configuration settings loaded correctly | Section 7 |
| 8 | Retry/backoff behavior verified | Section 6.1 |

**Deliverable:** 8+ passing unit tests

### 9.2 Integration Tests (Task 6)

| # | Test Case | Specification Reference |
|---|-----------|------------------------|
| 1 | GCC-Stat provider registers successfully in `KnowledgeProviderRegistry` | Section 8 |
| 2 | GCC-Stat provider is queryable via registry | Section 8 |
| 3 | `ReasoningEngine` can query GCC-Stat provider through registry | Section 1.2 |
| 4 | Existing providers still register after GCC-Stat provider | Section 1.2 |
| 5 | Fallback to other providers when GCC-Stat is unavailable | Section 2.3 |
| 6 | Graceful degradation does not crash application startup | Section 8.2 |

**Deliverable:** 6+ passing integration tests

---

## 10. Open Items & TBD

The following items are explicitly unresolved in this specification and must be addressed during Task 3 implementation or subsequent verification:

| Item | Status | Resolution Path |
|------|--------|-----------------|
| Exact API base URL | **TBD** | Requires live API verification; candidates: `https://sdmx.marsa.gccstat.org` or `https://dp.marsa.gccstat.org` |
| API key requirement | **TBD** | Public SDMX API may not require key; confirm during Task 3 |
| Exact SDMX/JSON response schemas | **TBD** | Requires live API access and structure review during Task 3 |
| Available dataflows / dataset IDs | **TBD** | Requires Fusion Registry query during Task 3 |
| Rate limit numeric values | **TBD** | Not publicly documented; confirm during Task 3 testing |
| Actual response latency | **TBD** | Measure during Task 3 implementation |
| SDMX parsing library choice | **TBD** | Requires assessment during Task 3; options include `pandasdmx` or custom parser |
| Field mapping details | **TBD** | Requires actual API schema from live response |
| Confidence rule calibration | **TBD** | Initial rules in Section 4; refine after observing data quality |
| Retry count/backoff tuning | **TBD** | Initial values in Section 6.1; adjust based on observed behavior |
| Endpoint selection logic | **TBD** | Requires understanding of API capabilities during Task 3 |

---

## 11. Specification Review Checklist

This section enables later review of implementation against this specification:

| Area | Spec Section | Implementation File | Review Check |
|------|--------------|---------------------|--------------|
| Adapter boundary | 1.1 | `gccstat_provider.py`, `gccstat_client.py` | No DEM core modifications |
| Provider-Agnostic compliance | 1.2 | All adapter files | Registry-only; no hardcoded DEM references |
| `query()` signature | 2.1 | `gccstat_provider.py` | Matches `KnowledgeProvider` ABC |
| `get_sources()` signature | 2.1 | `gccstat_provider.py` | Returns required metadata fields |
| Field mapping | 3.1, 3.2, 3.3 | `gccstat_provider.py` | All mapped fields present in output |
| Confidence rules | 4 | `gccstat_provider.py` | Scores within 0.0–1.0; rules applied |
| Provenance metadata | 5 | `gccstat_provider.py` | All fields populated per rules |
| Error handling | 6 | `gccstat_client.py`, `gccstat_provider.py` | No exceptions leak to DEM core |
| Retry/backoff | 6.1 | `gccstat_client.py` | Exponential backoff on 429/5xx |
| Configuration | 7 | `config.py`, `gccstat_provider.py` | All settings loaded from config |
| Registry integration | 8 | `main.py` | Conditional registration in `lifespan()` |
| Unit tests | 9.1 | `tests/agent/test_gccstat_provider.py` | 8+ tests pass |
| Integration tests | 9.2 | `tests/agent/test_gccstat_integration.py` | 6+ tests pass |

---

## 12. Constraints Reminders

- `KNOWLEDGE_INGESTION_CONTRACT.md` is immutable
- No modifications to `ReasoningEngine`, `TaskPlanner`, `ToolOrchestrator`, or any DEM core component
- No changes to `knowledge_nodes` or `knowledge_edges`
- No database migrations
- No frontend changes
- No WP beyond WP-38d
- No additional providers in WP-38d
- No commits or pushes during planning

---

*Specification Status: Draft — Pending G2 Review*
