# FAOSTAT Adapter Specification

**Work Package:** Portfolio Re-Evaluation — FAOSTAT First Execution Gap  
**Task:** 2 — Adapter Specification  
**Date:** 2026-08-14  
**Status:** Draft — Pending G2 Review  
**Authority:** `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` Section 21.10  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Provider:** FAOSTAT API (`fao.org/faostat`)  
**Prerequisite:** Section 21.9 — FAOSTAT approved as G1 Approved Provider; Section 21.10 — Task 2 authorized by Project Owner

---

## 1. Adapter Boundary & Provider-Agnostic Architecture

### 1.1 Boundary

The FAOSTAT adapter consists of two files:

- `faostat_client.py` — isolated HTTP client for FAOSTAT API
- `faostat_provider.py` — `KnowledgeProvider` implementation that transforms FAOSTAT responses into the DEM knowledge contract shape

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
| Provider Abstraction | All FAOSTAT access is through `FaostatExternalSourceAdapter(KnowledgeProvider)` |
| Registry-Only Registration | Registered in `KnowledgeProviderRegistry` only; DEM core never references FAOSTAT directly |
| No DEM Core Coupling | No DEM core files modified except `config.py` (settings) and `main.py` (lifespan registration) |
| No Knowledge Graph Schema Changes | No writes to `knowledge_nodes` or `knowledge_edges` |
| No Contract Changes | `KNOWLEDGE_INGESTION_CONTRACT.md` unchanged |
| Config-Driven | All FAOSTAT-specific settings loaded from `config.py` |
| Replaceable | Adapter can be replaced without redesigning Intelligence Layer |
| Composable | Multiple providers coexist in registry without mutual dependency |
| Observable | `get_sources()` exposes source metadata; query responses include `source_id` and provenance |

---

## 2. KnowledgeProvider Contract Implementation

### 2.1 Interface Compliance

`FaostatExternalSourceAdapter` implements `KnowledgeProvider` with the following methods:

| Method | Signature | Return Shape |
|--------|-----------|--------------|
| `query()` | `async def query(self, query: str, context: Optional[Dict[str, Any]] = None, scope: Optional[str] = None, sources: Optional[List[str]] = None, limit: int = 10) -> Dict[str, Any]` | `{"results": [...], "confidence": float|None, "sources": [source_id]}` |
| `get_sources()` | `async def get_sources(self) -> List[Dict[str, Any]]` | `[{"id": str, "name": str, "type": str, "version": str, "updated_at": str}]` |

### 2.2 Query Behavior

- **Primary context parameters:** `area` (country code), `item` (commodity code), `element` (measurement type), `year` (optional)
- **Scope:** Mapped to FAOSTAT API domain/query parameters
- **Sources parameter:** Accepted but not used for filtering; returned in response as `[source_id]`
- **Limit:** Applied to transformed results after fetching

### 2.3 Graceful Degradation

| Failure Mode | Behavior |
|--------------|----------|
| Missing API credentials | Returns empty results with `confidence: None` |
| Network error / timeout | Returns empty results with `confidence: None` |
| HTTP 429 (rate limit) | Retries up to 3 times with exponential backoff (1s, 2s) |
| HTTP error status | Raises after retries exhausted; caught by outer handler → empty results |
| Invalid JSON / non-dict response | Returns empty results |
| Unexpected exception | Returns empty results |

---

## 3. Field Mapping & Transformation

### 3.1 FAOSTAT API → DEM Knowledge Shape

**FAOSTAT API request parameters (typical):**

| FAOSTAT Parameter | Source | Notes |
|-------------------|--------|-------|
| `domain` | `scope` argument or adapter config | e.g., "QCL" for crops/livestock |
| `area` | `context["area"]` | Country code (ISO 3-letter) |
| `item` | `context["item"]` | Commodity/item code |
| `element` | `context["element"]` | Measurement type |
| `year` | `context["year"]` | Optional year filter |

**FAOSTAT response structure (documented):**

```json
{
  "data": [
    {
      "area": "Egypt",
      "areaCode": "EGY",
      "item": "Wheat",
      "itemCode": "15",
      "element": "Production",
      "elementCode": "5510",
      "year": "2023",
      "unit": "Tonnes",
      "value": "1234567",
      "flag": "A"
    }
  ],
  "message": {
    "total": 100
  }
}
```

**Evidence:** FAOSTAT API documentation and OpenAPI spec referenced in Section 21.1.

### 3.2 Entry-Level Field Mapping

| DEM Field | FAOSTAT Source | Priority | Evidence |
|-----------|----------------|----------|----------|
| `id` | `f"{areaCode}_{itemCode}_{elementCode}_{year}_{hash}"` | Computed | **Assumption/Unverified** — exact FAOSTAT response schema requires live API confirmation |
| `content` | Composite: `"{item} {element} in {area} ({year}): {value} {unit}"` | Constructed | **Assumption/Unverified** — content format to be validated against actual API responses |
| `source_id` | Adapter config `source_id` | Config-driven | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `confidence` | Computed per Section 4 | — | **Evidence** — adapter-specific rules |
| `metadata.area` | `area` | Direct | **Evidence** — documented FAOSTAT field |
| `metadata.area_code` | `areaCode` | Direct | **Evidence** — documented FAOSTAT field |
| `metadata.item` | `item` | Direct | **Evidence** — documented FAOSTAT field |
| `metadata.item_code` | `itemCode` | Direct | **Evidence** — documented FAOSTAT field |
| `metadata.element` | `element` | Direct | **Evidence** — documented FAOSTAT field |
| `metadata.element_code` | `elementCode` | Direct | **Evidence** — documented FAOSTAT field |
| `metadata.year` | `year` | Direct | **Evidence** — documented FAOSTAT field |
| `metadata.unit` | `unit` | Direct | **Evidence** — documented FAOSTAT field |
| `metadata.source_authority` | Adapter config `"FAO"` | Config-driven | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.effective_date` | `year` mapped to `"{year}-12-31"` | Derived | **Assumption/Unverified** — date mapping convention to be confirmed |
| `metadata.source_url` | FAOSTAT API endpoint URL | Constructed | **Evidence** — adapter-constructed provenance per contract |
| `metadata.updated_at` | Adapter config `updated_at` | Config-driven | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.version` | Adapter config `version` | Config-driven | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `metadata.record_hash` | `hash(frozenset(entry.items()))` | Computed | **Evidence** — adapter-side provenance per Section 21.8 approval |
| `metadata.retrieval_status` | Constant `"success"` | Adapter-set | **Evidence** — adapter-side provenance per Section 21.8 approval |
| `metadata.flag` | FAOSTAT response `flag` field | Direct | **Evidence** — documented FAOSTAT field |

### 3.3 Content Construction

**Content format:**
- If all fields present: `"{item} {element} in {area} ({year}): {value} {unit}"`
- If value missing: `"{item} {element} in {area} ({year}): data not available"`
- If flag indicates estimated/footnote: append `" [estimated]"` or `" [footnote: {flag}]"`

**Evidence:** Content construction rules are adapter-specific and follow the pattern established in `wp38-task2-moaah-adapter-spec.md` Section 3.3.

---

## 4. Confidence Rules

| Condition | Confidence | Evidence |
|-----------|------------|----------|
| Base (all fields present, flag = "A" for official) | `0.95` | **Assumption/Unverified** — flag semantics require FAOSTAT metadata confirmation |
| `value` present but flag indicates estimate | `0.85` | **Assumption/Unverified** — flag value mapping requires FAOSTAT metadata confirmation |
| `value` missing or zero | `0.70` | **Assumption/Unverified** — confidence thresholds are adapter-specific |
| Missing `area_code` or `item_code` | `0.60` | **Assumption/Unverified** — confidence thresholds are adapter-specific |

**Aggregation:** Average of all result confidences. If no results, returns `confidence: None`.

**Note:** These rules are adapter-specific and align with FAOSTAT's official data quality indicators per Section 21.1 Evidence.

---

## 5. Provenance Metadata

| Field | Type | Source | Purpose | Evidence |
|-------|------|--------|---------|----------|
| `fetch_timestamp` | ISO-8601 string | `updated_at` config passed at bootstrap | When the adapter was instantiated/updated | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `record_hash` | String | `hash(frozenset(entry.items()))` | Change detection for individual records | **Evidence** — adapter-side provenance per Section 21.8 approval |
| `retrieval_status` | Constant `"success"` | Adapter-set | Indicates successful transformation | **Evidence** — adapter-side provenance per Section 21.8 approval |
| `source_authority` | Constant `"FAO"` | Adapter config | Attribution per FAO terms | **Evidence** — per Project Owner Approval Section 21.8 |
| `metadata.flag` | String | FAOSTAT response `flag` field | Data quality indicator (A=official, E=estimated, etc.) | **Evidence** — documented FAOSTAT field |

**Note:** All provenance fields comply with Project Owner Approval recorded in Section 21.8 for commercial use and redistribution.

---

## 6. Error Handling & Retry/Backoff Matrix

### 6.1 HTTP Client Retry Policy

| Parameter | Value | Evidence |
|-----------|-------|----------|
| Max attempts | 3 | **Evidence** — follows established adapter pattern from `wp38-task2-moaah-adapter-spec.md` |
| Initial backoff | 1.0 seconds | **Evidence** — follows established adapter pattern |
| Backoff multiplier | 2x | **Evidence** — follows established adapter pattern |
| Retry on | `httpx.TimeoutException`, `httpx.NetworkError`, HTTP 429 | **Evidence** — follows established adapter pattern |
| Fail on | Other HTTP errors after retries exhausted | **Evidence** — follows established adapter pattern |

### 6.2 Failure Mode Matrix

| Failure Mode | Detection | Adapter Response | Evidence |
|--------------|-----------|------------------|----------|
| Network timeout | `httpx.TimeoutException` | Retry up to 3x; then empty results | **Evidence** — follows established adapter pattern |
| Connection error | `httpx.NetworkError` | Retry up to 3x; then empty results | **Evidence** — follows established adapter pattern |
| Rate limit (429) | HTTP 429 response | Retry up to 3x with backoff; then raise | **Evidence** — follows established adapter pattern |
| HTTP 4xx/5xx | `response.raise_for_status()` | Raise after retries; outer handler returns empty results | **Evidence** — follows established adapter pattern |
| Invalid JSON | `response.json()` exception | Returns empty results | **Evidence** — follows established adapter pattern |
| Non-dict response | `isinstance(raw, dict)` check | Returns empty results | **Evidence** — follows established adapter pattern |
| Missing area/item codes | `context.get("area")` or `context.get("item")` is None | Returns empty results immediately | **Evidence** — follows established adapter pattern |
| Missing credentials | `base_url` or `api_key` empty | Returns empty results; registration skipped at startup | **Evidence** — follows established adapter pattern |

---

## 7. Configuration

### 7.1 Settings (`backend/app/core/config.py`)

| Setting | Type | Default | Purpose | Evidence |
|---------|------|---------|---------|----------|
| `FAOSTAT_BASE_URL` | `str` | `"https://faostatservices.fao.org/api/v1"` | FAOSTAT API base URL | **Assumption/Unverified** — requires live API documentation confirmation |
| `FAOSTAT_API_KEY` | `str` | `""` | API key if required (currently FAOSTAT is open) | **Evidence** — Section 21.1 documents open API access |
| `FAOSTAT_TIMEOUT_SECONDS` | `float` | `30.0` | HTTP request timeout | **Evidence** — follows established adapter pattern |
| `FAOSTAT_SOURCE_ID` | `str` | `"faostat"` | Registry source ID | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `FAOSTAT_SOURCE_NAME` | `str` | `"FAOSTAT External Knowledge"` | Display name | **Evidence** — adapter config pattern |
| `FAOSTAT_SOURCE_TYPE` | `str` | `"external"` | Source type | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| `FAOSTAT_SOURCE_VERSION` | `str` | `"1.0.0"` | Adapter version | **Evidence** — SemVer per KNOWLEDGE_INGESTION_CONTRACT.md |
| `FAOSTAT_DEFAULT_DOMAIN` | `str` | `"QCL"` | Default FAOSTAT domain (crops/livestock) | **Assumption/Unverified** — domain code requires FAOSTAT metadata confirmation |

### 7.2 Bootstrap Registration (`backend/main.py`)

```python
if settings.FAOSTAT_BASE_URL:
    from app.agent.knowledge.faostat_provider import FaostatExternalSourceAdapter
    faostat_adapter = FaostatExternalSourceAdapter(
        config={
            "source_id": settings.FAOSTAT_SOURCE_ID,
            "name": settings.FAOSTAT_SOURCE_NAME,
            "type": settings.FAOSTAT_SOURCE_TYPE,
            "version": settings.FAOSTAT_SOURCE_VERSION,
            "updated_at": "2026-08-14T00:00:00Z",
            "base_url": settings.FAOSTAT_BASE_URL,
            "api_key": settings.FAOSTAT_API_KEY,
            "timeout_seconds": settings.FAOSTAT_TIMEOUT_SECONDS,
            "default_domain": settings.FAOSTAT_DEFAULT_DOMAIN,
        }
    )
    await knowledge_provider_registry.register(faostat_adapter)
```

**Behavior:**  
- Registration is conditional on `FAOSTAT_BASE_URL` being set.
- Registration failures are caught and logged as warnings; do not crash startup.
- If credentials are missing, a warning is logged and registration is skipped.

**Evidence:** Follows established pattern from `wp38-task2-moaah-adapter-spec.md` Section 7.2.

---

## 8. Registry Integration

| Aspect | Detail | Evidence |
|--------|--------|----------|
| Registry | `KnowledgeProviderRegistry` | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| Registration | Conditional in `main.py` `lifespan()` | **Evidence** — follows established adapter pattern |
| Source ID | `settings.FAOSTAT_SOURCE_ID` (default: `"faostat"`) | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| Query path | `registry.query("faostat", ...)` | **Evidence** — per KNOWLEDGE_INGESTION_CONTRACT.md |
| Coexistence | FAOSTAT registers alongside existing providers | **Evidence** — registry supports multiple providers |
| Unregistration | Not implemented; adapter persists for application lifetime | **Evidence** — follows established adapter pattern |

---

## 9. Test Coverage

| Test File | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| `tests/agent/test_faostat_provider.py` | TBD | Contract, query transformation, error handling, graceful degradation | **Pending** |
| `tests/agent/test_faostat_integration.py` | TBD | Registry registration, queryability, coexistence, interface compliance, metadata shape | **Pending** |

**Note:** Tests are pending implementation; no regressions expected in existing knowledge layer tests.

**Evidence:** Test patterns follow existing adapter test suites (Moaah: 9 tests, TradeData: 14 tests, ZATCA: 13 tests, GCC-Stat: 9 tests).

---

## 10. Open Items & Unverified Details

| Item | Status | Evidence |
|------|--------|----------|
| Exact FAOSTAT API endpoint structure for bulk data | **Unverified** — requires live API documentation review | **Assumption** — draft uses documented API portal structure |
| Rate limit verification under load | **Unverified** — retry logic implemented but not load-tested | **Assumption** — follows established adapter pattern |
| Third-party data restrictions (UNSD/Eurostat sourced data within FAOSTAT) | **Unverified** — additional restrictions may apply per Section 21.1 | **Evidence** — Section 21.1 documents third-party data possibility |
| `flag` field semantics and all possible values | **Unverified** — requires FAOSTAT metadata documentation | **Assumption** — draft uses standard FAOSTAT flag interpretation |
| `element` and `item` code mappings for Agrifood focus | **Unverified** — requires domain-specific mapping review | **Assumption** — draft uses placeholder codes |
| FAOSTAT API authentication requirements | **Unverified** — open API suspected but not confirmed | **Assumption** — draft assumes open access based on Section 21.1 |
| `FAOSTAT_BASE_URL` exact value | **Unverified** — requires live API documentation confirmation | **Assumption** — draft uses documented developer portal URL |
| `FAOSTAT_DEFAULT_DOMAIN` code "QCL" | **Unverified** — requires FAOSTAT domain list confirmation | **Assumption** — draft uses crops/livestock domain as placeholder |

---

## 11. Gate Status

| Gate | Status | Evidence |
|------|--------|----------|
| G0 — Portfolio Evaluation Approval | Approved | Section 19 Owner Approval Record |
| G1 — FAOSTAT Source Selection | Approved | Section 21.9 Project Owner G1 Approval Decision |
| G2 — Adapter Specification Review | **Pending** | This document prepared for G2 review; approval pending |

---

*Document Status: Draft — Pending Task 2 Authorization and G2 Review*
