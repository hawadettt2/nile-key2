# WP-UN-Comtrade — Implementation Plan

**Work Package:** WP-UN-Comtrade — UN Comtrade External Source Adapter  
**Date:** 2026-08-15  
**Status:** Draft — Pending Implementation Authorization  
**Authority:** `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` Sections 6.2, 8.2, 10.1  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Provider:** UN Comtrade API (`comtradeapi.un.org`)  
**Prerequisite:** G1 = PASS; G2 = PASS; G3 Design Review = PASS; Project Owner Approval recorded

---

## 1. Scope & Deliverables

### 1.1 In Scope

| Deliverable | Description |
|-------------|-------------|
| `UnComtradeApiClient` | Isolated HTTP client for UN Comtrade API |
| `UnComtradeExternalSourceAdapter` | `KnowledgeProvider` implementation transforming UN Comtrade responses into DEM knowledge shape |
| Registry Integration | Registration in `KnowledgeProviderRegistry` via `main.py` lifespan |
| Tests | Unit tests for client, transformer, and adapter contract compliance |
| Documentation | Inline docstrings and adapter-level comments only |

### 1.2 Out of Scope

- DEM core modifications beyond `config.py` (settings) and `main.py` (lifespan registration)
- `KnowledgeProvider` interface changes
- `KnowledgeProviderRegistry` changes
- Knowledge Graph schema changes
- `knowledge_nodes` / `knowledge_edges` writes
- PLAN.md modifications
- New Knowledge Families
- WTO ePing or WTO TFA Database implementation
- HS Code extraction from free-text queries (deferred)

---

## 2. Adapter Boundary & Provider-Agnostic Architecture

### 2.1 Boundary

The UN Comtrade adapter consists of two files:

- `uncomtrade_client.py` — isolated HTTP client for UN Comtrade API
- `uncomtrade_provider.py` — `KnowledgeProvider` implementation that transforms UN Comtrade responses into DEM knowledge contract shape

The adapter does **not** modify:

- `ReasoningEngine`
- `TaskPlanner`
- `ToolOrchestrator`
- Any DEM core component
- `knowledge_nodes` or `knowledge_edges` tables
- `KNOWLEDGE_INGESTION_CONTRACT.md`

### 2.2 Provider-Agnostic Compliance

| Requirement | Implementation |
|-------------|----------------|
| Provider Abstraction | All UN Comtrade access is through `UnComtradeExternalSourceAdapter(KnowledgeProvider)` |
| Registry-Only Registration | Registered in `KnowledgeProviderRegistry` only; DEM core never references UN Comtrade directly |
| No DEM Core Coupling | No DEM core files modified except `config.py` (settings) and `main.py` (lifespan registration) |
| No Knowledge Graph Schema Changes | No writes to `knowledge_nodes` or `knowledge_edges` |
| No Contract Changes | `KNOWLEDGE_INGESTION_CONTRACT.md` unchanged |
| Config-Driven | All UN Comtrade-specific settings loaded from `config.py` |
| Replaceable | Adapter can be replaced without redesigning Intelligence Layer |
| Composable | Multiple providers coexist in registry without mutual dependency |
| Observable | `get_sources()` exposes source metadata; query responses include `source_id` and provenance |

---

## 3. KnowledgeProvider Contract Implementation

### 3.1 Interface Compliance

`UnComtradeExternalSourceAdapter` implements `KnowledgeProvider` with the following methods:

| Method | Signature | Return Shape |
|--------|-----------|--------------|
| `query()` | `async def query(self, query: str, context: Optional[Dict[str, Any]] = None, scope: Optional[str] = None, sources: Optional[List[str]] = None, limit: int = 10) -> Dict[str, Any]` | `{"results": [...], "confidence": float\|None, "sources": [source_id]}` |
| `get_sources()` | `async def get_sources(self) -> List[Dict[str, Any]]` | `[{"id": str, "name": str, "type": str, "version": str, "updated_at": str}]` |

### 3.2 Query Behavior

- **Required context:** None (all parameters optional; defaults to global exports)
- **Optional context:** `reporter`, `partner`, `flow`, `period`, `frequency`, `classification`, `type`
- **Scope:** Mapped to `typeCode` ("C" for commodities, "S" for services); defaults to "C"
- **Sources parameter:** Accepted but not used for filtering; returned in response as `["un-comtrade"]`
- **Limit:** Applied as `maxrecords`; capped at 500 for Preview API, 100,000 for authenticated API
- **Query text:** Used for HS code extraction if pattern matches; otherwise ignored

### 3.3 Graceful Degradation

| Failure Mode | Behavior |
|--------------|----------|
| Missing `base_url` | Returns empty results with `confidence: None` |
| Missing API key (when required) | Falls back to Preview API; if Preview also fails, returns empty results |
| Network error / timeout | Returns empty results with `confidence: None` |
| HTTP 429 (rate limit) | Retries up to 3 times with exponential backoff (1s, 2s, 4s) |
| HTTP error status | Raises after retries exhausted; caught by outer handler → empty results |
| Malformed JSON / non-dict response | Returns empty results |
| Unexpected exception | Returns empty results |

---

## 4. Context → UN Comtrade Parameter Mapping

### 4.1 Mapping Rules (G2 Approved)

| UN Comtrade Parameter | Source in `query()` | Default | Notes |
|-----------------------|---------------------|---------|-------|
| `typeCode` | `scope` or `context.get("type")` | `"C"` | "C" = commodities, "S" = services |
| `freqCode` | `context.get("frequency")` | `"A"` | "A" = annual, "M" = monthly |
| `clCode` | `context.get("classification")` | `"HS"` | HS, SITC, BEC |
| `reporterCode` | `context.get("reporter")` | `0` | UN numeric country code; 0 = all reporters |
| `partnerCode` | `context.get("partner")` | `0` | UN numeric country code; 0 = all partners |
| `flowCode` | `context.get("flow")` | `"X"` | "X" = exports, "M" = imports |
| `period` | `context.get("period")` | Latest available | Format: `YYYY` or `YYYYMM` |
| `cmdCode` | Extracted from `query` text | None | HS code pattern matching (deferred) |
| `maxrecords` | `limit` | `min(limit, 500)` | Preview API cap; 100,000 for authenticated |

### 4.2 HS Code Extraction (Deferred)

**Status:** Deferred / Non-blocking Gap

**Rationale:** UN Comtrade requires exact HS codes for precise queries. Extracting HS codes from free-text queries requires NLP/pattern matching not yet implemented in DEM. This is deferred to a future enhancement and does not block G3/G4/G5.

**Interim behavior:** If `cmdCode` cannot be extracted from `query`, the request proceeds without commodity filter, returning all commodities for the specified reporter/partner/period.

---

## 5. Response Transformation Rules

### 5.1 UN Comtrade Response → DEM Knowledge Shape

**UN Comtrade `/public/v1/preview` response schema:**

```json
{
  "dataset": [
    {
      "typeCode": "C",
      "freqCode": "A",
      "refYear": 2023,
      "reporterCode": 156,
      "reporterDesc": null,
      "partnerCode": 842,
      "partnerDesc": null,
      "classificationCode": "HS",
      "cmdCode": "090111",
      "cmdDesc": null,
      "flowCode": "X",
      "fobvalue": 12494.0,
      "netWgt": 8226.0,
      "qty": 0.0,
      "altQty": 23534.0,
      "isReported": true,
      "isAggregate": false
    }
  ]
}
```

**Transformation to `KnowledgeProvider.query()` return shape:**

```python
{
    "id": f"{reporterCode}_{partnerCode}_{cmdCode}_{refYear}",
    "content": f"{cmdDesc} ({cmdCode}) — {fobvalue} USD" if cmdDesc else f"HS {cmdCode} — {fobvalue} USD",
    "source_id": "un-comtrade",
    "confidence": 0.9 if isReported else 0.7,
    "metadata": {
        "reporter_code": reporterCode,
        "reporter_desc": reporterDesc,
        "partner_code": partnerCode,
        "partner_desc": partnerDesc,
        "flow_code": flowCode,
        "cmd_code": cmdCode,
        "cmd_desc": cmdDesc,
        "ref_year": refYear,
        "freq_code": freqCode,
        "classification_code": classificationCode,
        "fobvalue": fobvalue,
        "net_weight": netWgt,
        "quantity": qty,
        "alt_quantity": altQty,
        "is_reported": isReported,
        "source_authority": "UN",
        "source_url": "https://comtrade.un.org",
        "record_hash": str(hash(frozenset(entry.items()))) if entry else "",
        "retrieval_status": "success",
        "updated_at": self._updated_at,
        "version": self._version,
    }
}
```

### 5.2 Confidence Calculation

| Condition | Confidence |
|-----------|-----------|
| `isReported == True` | 0.9 |
| `isReported == False` or missing | 0.7 |
| No data returned | `None` |

### 5.3 Content Construction

- Primary: `f"{cmdDesc} ({cmdCode}) — {fobvalue} USD"`
- Fallback: `f"HS {cmdCode} — {fobvalue} USD"` if `cmdDesc` is null
- Units: USD for value; kg for weight if available

---

## 6. Authentication Design

### 6.1 Preview API (No Key)

- **Endpoint prefix:** `/public/v1/preview`
- **Authentication:** None required
- **Limits:** 500 records per request
- **Use case:** Default mode when no API key configured

### 6.2 Authenticated API (With Key)

- **Endpoint prefix:** `/data/v1/get`, `/data/v1/getDa`, `/data/v1/getMetadata`
- **Authentication:** `Ocp-Apim-Subscription-Key` header or `subscription-key` query parameter
- **Free tier limits:** 500 calls/day, 100,000 records/call, 5 calls/second
- **Premium tier limits:** 5,000 calls/day
- **Use case:** When `api_key` is provided in config

### 6.3 Fallback Behavior

| Scenario | Behavior |
|----------|----------|
| No API key configured | Use Preview API |
| API key configured | Use authenticated API |
| Authenticated API returns 401 | Fall back to Preview API (if feasible) |
| Both fail | Return empty results |

---

## 7. Error Handling, Retry/Backoff, Rate Limits

### 7.1 Retry Policy

| Error Type | Max Attempts | Backoff Strategy |
|------------|--------------|------------------|
| HTTP 429 (Rate Limit) | 3 | 1s → 2s → 4s (exponential) |
| HTTP 5xx (Server Error) | 2 | 2s → 4s |
| Network/Timeout | 2 | 2s → 4s |

### 7.2 Rate Limit Handling

- Preview API: No explicit rate limit documented; respect 1 request/second as precaution
- Free tier: 500 calls/day, 5 calls/second
- Premium tier: 5,000 calls/day
- If 429 received, back off and retry; if retries exhausted, return empty results

### 7.3 Error Response Mapping

| HTTP Status | UN Comtrade Behavior | Adapter Response |
|-------------|----------------------|------------------|
| 200 | Success | Transform and return results |
| 401/403 | Unauthorized | Return empty results with `confidence: None` |
| 404 | Not Found | Return empty results |
| 429 | Rate Limited | Retry with backoff; then empty results |
| 5xx | Server Error | Retry with backoff; then empty results |
| Timeout | Network error | Return empty results |

---

## 8. Provenance / Traceability

### 8.1 Metadata Fields

All transformed records include:

| Field | Value | Source |
|-------|-------|--------|
| `source_authority` | `"UN"` | Fixed |
| `source_url` | `"https://comtrade.un.org"` | Fixed |
| `record_hash` | `hash(frozenset(entry.items()))` | Computed |
| `retrieval_status` | `"success"` | Fixed |
| `updated_at` | From provider config | Config |
| `version` | From provider config | Config |
| `reporter_code` | From UN Comtrade response | API |
| `partner_code` | From UN Comtrade response | API |
| `cmd_code` | From UN Comtrade response | API |
| `ref_year` | From UN Comtrade response | API |
| `fobvalue` | From UN Comtrade response | API |
| `net_weight` | From UN Comtrade response | API |
| `is_reported` | From UN Comtrade response | API |

### 8.2 Source Metadata (`get_sources()`)

```python
[
    {
        "id": "un-comtrade",
        "name": "UN Comtrade",
        "type": "external_trade_intelligence",
        "version": "1.0.0",
        "updated_at": "2026-08-15",
    }
]
```

---

## 9. Test Strategy

### 9.1 Unit Tests

| Component | Test Focus |
|-----------|------------|
| `UnComtradeApiClient` | Request building, URL construction, retry logic, backoff timing |
| `UnComtradeExternalSourceAdapter._transform` | Response transformation, field mapping, confidence calculation |
| `UnComtradeExternalSourceAdapter._build_request` | Context → parameter mapping, defaults, edge cases |
| `UnComtradeExternalSourceAdapter.query()` | End-to-end adapter behavior with mocked client |

### 9.2 Integration Tests

| Test | Description |
|------|-------------|
| Preview API live call | Verify 200 OK with sample query |
| Registry registration | Verify adapter registers correctly in `KnowledgeProviderRegistry` |
| Contract compliance | Verify `query()` return shape matches `KnowledgeProvider` contract |

### 9.3 Test Data

- Use Preview API with known parameters for live integration tests
- Mock client responses for unit tests
- Do not rely on API key for test execution

---

## 10. Implementation Tasks

### Task 1: Create `uncomtrade_client.py`

- Implement `UnComtradeApiClient` with:
  - `__init__(base_url, api_key=None, timeout_seconds=30.0)`
  - `request(method, path, params)` — builds full URL and delegates to `_request_with_retry`
  - `_request_with_retry()` — implements retry/backoff for 429, 5xx, network errors
  - `_headers()` — returns `{"Accept": "application/json"}` plus `Ocp-Apim-Subscription-Key` if `api_key` provided
  - `close()` — placeholder for cleanup

### Task 2: Create `uncomtrade_provider.py`

- Implement `UnComtradeExternalSourceAdapter(KnowledgeProvider)` with:
  - `__init__(config)` — loads `source_id`, `name`, `type`, `version`, `updated_at`, `base_url`, `api_key`, `timeout_seconds`
  - `query(query, context, scope, sources, limit)` — builds request, calls client, transforms response
  - `_build_request(query, context, scope, limit)` — maps context to UN Comtrade parameters per Section 4
  - `_transform(raw, context, limit, scope)` — transforms API response to DEM knowledge shape
  - `_transform_entry(entry, scope)` — transforms single record
  - `_build_content(entry)` — constructs human-readable content string
  - `_compute_confidence(entry)` — calculates confidence score
  - `get_sources()` — returns source metadata

### Task 3: Register Adapter in `main.py`

- Import `UnComtradeExternalSourceAdapter`
- Instantiate with config from `config.py`
- Register in `knowledge_provider_registry` during lifespan startup

### Task 4: Add Configuration

- Add UN Comtrade config section to `config.py`:
  - `UN_COMTRADE_BASE_URL`
  - `UN_COMTRADE_API_KEY` (optional)
  - `UN_COMTRADE_TIMEOUT_SECONDS`
  - `UN_COMTRADE_SOURCE_ID`
  - `UN_COMTRADE_PROVIDER_NAME`
  - `UN_COMTRADE_PROVIDER_TYPE`
  - `UN_COMTRADE_VERSION`
  - `UN_COMTRADE_UPDATED_AT`

### Task 5: Write Tests

- `tests/agent/knowledge/test_uncomtrade_client.py`
- `tests/agent/knowledge/test_uncomtrade_provider.py`
- Target: Contract compliance, transformation accuracy, error handling, retry logic

---

## 11. Acceptance Criteria

| # | Criterion | Verification Method |
|---|-----------|---------------------|
| AC-1 | `UnComtradeApiClient` makes successful request to Preview API without API key | Live integration test |
| AC-2 | `UnComtradeApiClient` retries on 429 with exponential backoff | Unit test with mocked responses |
| AC-3 | `UnComtradeApiClient` retries on 5xx with backoff | Unit test with mocked responses |
| AC-4 | `UnComtradeExternalSourceAdapter.query()` returns contract-compliant shape | Unit test |
| AC-5 | `UnComtradeExternalSourceAdapter.get_sources()` returns valid source metadata | Unit test |
| AC-6 | Context parameters map correctly to UN Comtrade API parameters | Unit test for `_build_request` |
| AC-7 | Response transformation produces correct DEM knowledge shape | Unit test with sample API response |
| AC-8 | Confidence calculation follows defined rules | Unit test |
| AC-9 | Provenance metadata includes all required fields | Unit test |
| AC-10 | Adapter registers successfully in `KnowledgeProviderRegistry` | Integration test |
| AC-11 | `sources` parameter is accepted but not used for filtering | Unit test |
| AC-12 | Preview API limit (500 records) is respected | Unit test |
| AC-13 | Error conditions return empty results with `confidence: None` | Unit test |
| AC-14 | No DEM core files modified except `config.py` and `main.py` | Code review |
| AC-15 | No Knowledge Graph schema changes | Code review |
| AC-16 | All tests pass | Test suite execution |

---

## 12. Gate Sequence After Implementation

| Gate | Status After Implementation | Criteria |
|------|----------------------------|----------|
| G3 — Implementation Review | Pending | Code review, design compliance, test coverage |
| G4 — Verification | Pending | Live API verification, contract compliance, integration tests |
| G5 — Closure | Pending | Acceptance criteria met, documentation complete, Project Owner sign-off |

**Sequence:** Implementation → G3 → G4 → G5

---

## 13. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Preview API insufficient for production | Medium | High | Design supports API key upgrade; migration path clear |
| API schema changes | Low | Medium | Adapter boundary isolates changes; only `uncomtrade_client.py` affected |
| Rate limiting in production | Medium | Medium | Retry/backoff implemented; monitor call volume |
| HS code extraction gap | High (deferred) | Low | Documented as deferred; manual filter via context possible interim |
| API key availability | Low | Low | Preview API works without key; free tier registration straightforward |

---

## 14. Deferred Items

| Item | Rationale | Gate |
|------|-----------|------|
| HS Code extraction from free-text queries | Requires NLP/pattern matching not in current scope | Post-G5 enhancement |
| Premium tier bulk downloads | Not required for minimal sufficiency | Post-G5 if needed |
| Async/batch API | Not required for initial implementation | Post-G5 if needed |
| Monthly data frequency support | Default is annual; monthly can be added via `context["frequency"]="M"` | Post-G5 if needed |

---

## 15. References

- `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` — Portfolio Plan
- `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md` — Governing Contract
- `backend/app/agent/knowledge/provider.py` — KnowledgeProvider ABC
- `backend/app/agent/knowledge/registry.py` — KnowledgeProviderRegistry
- `backend/app/agent/knowledge/faostat_provider.py` — Reference implementation pattern
- `backend/app/agent/knowledge/faostat_client.py` — Reference client pattern
- `https://uncomtrade.org/docs/un-comtrade-api/` — UN Comtrade API documentation
- `https://comtradedeveloper.un.org/` — UN Comtrade Developer Portal

---

**Document Status:** Draft — Pending Implementation Authorization
