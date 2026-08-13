# WP-38a Moaah Adapter Specification

**Work Package:** WP-38a — Regulatory Core + Egypt  
**Task:** 2 — Define External Source Contract Adapter  
**Date:** 2026-08-12  
**Status:** Draft — Pending G2 Review  
**Authority:** `.kilo/plans/1786359213310-real-external-source-integration.md`  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Provider:** Moaah API (`moaah.com`)  
**Implementation Reference:**  
- `backend/app/agent/knowledge/mooadapter.py`  
- `backend/app/agent/knowledge/mooadapter_client.py`  
- `backend/app/core/config.py`  
- `backend/main.py`

---

## 1. Adapter Boundary & Provider-Agnostic Architecture

### 1.1 Boundary

The Moaah adapter consists of two files:

- `mooadapter_client.py` — isolated HTTP client for Moaah API
- `mooadapter.py` — `KnowledgeProvider` implementation that transforms Moaah responses into the DEM knowledge contract shape

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
| Provider Abstraction | All Moaah access is through `MoaahExternalSourceAdapter(KnowledgeProvider)` |
| Registry-Only Registration | Registered in `KnowledgeProviderRegistry` only; DEM core never references Moaah directly |
| No DEM Core Coupling | No DEM core files modified except `config.py` (settings) and `main.py` (lifespan registration) |
| No Knowledge Graph Schema Changes | No writes to `knowledge_nodes` or `knowledge_edges` |
| No Contract Changes | `KNOWLEDGE_INGESTION_CONTRACT.md` unchanged |
| Config-Driven | All Moaah-specific settings loaded from `config.py` |
| Replaceable | Adapter can be replaced without redesigning Intelligence Layer |
| Composable | Multiple providers coexist in registry without mutual dependency |
| Observable | `get_sources()` exposes source metadata; query responses include `source_id` and provenance |

---

## 2. KnowledgeProvider Contract Implementation

### 2.1 Interface Compliance

`MoaahExternalSourceAdapter` implements `KnowledgeProvider` with the following methods:

| Method | Signature | Return Shape |
|--------|-----------|--------------|
| `query()` | `async def query(self, query: str, context: Optional[Dict[str, Any]] = None, scope: Optional[str] = None, sources: Optional[List[str]] = None, limit: int = 10) -> Dict[str, Any]` | `{"results": [...], "confidence": float|None, "sources": [source_id]}` |
| `get_sources()` | `async def get_sources(self) -> List[Dict[str, Any]]` | `[{"id": str, "name": str, "type": str, "version": str, "updated_at": str}]` |

### 2.2 Query Behavior

- **Required context:** `country` (from `context["country"]`)
- **Optional context:** `affected_country`, `start_date`, `end_date`
- **Scope:** Mapped to Moaah `type` parameter; defaults to `"keyword"`
- **Sources parameter:** Accepted but not used for filtering; returned in response as `[source_id]`
- **Limit:** Applied to transformed results after fetching

### 2.3 Graceful Degradation

| Failure Mode | Behavior |
|--------------|----------|
| Missing `country` in context | Returns empty results with `confidence: None` |
| Missing `base_url` or `api_key` | Returns empty results with `confidence: None` |
| Network error / timeout | Returns empty results with `confidence: None` |
| HTTP 429 (rate limit) | Retries up to 3 times with exponential backoff (1s, 2s) |
| HTTP error status | Raises after retries exhausted; caught by outer handler → empty results |
| Malformed JSON / non-dict response | Returns empty results |
| Unexpected exception | Returns empty results |

---

## 3. Field Mapping & Transformation

### 3.1 Moaah API → DEM Knowledge Shape

**Moaah `/regs-search` request parameters:**

| Moaah Parameter | Source | Notes |
|-----------------|--------|-------|
| `q` | `query` argument | Search query string |
| `type` | `scope` argument | Defaults to `"keyword"` |
| `country` | `context["country"]` | Required |
| `affected_country` | `context["affected_country"]` | Optional |
| `start_date` | `context["start_date"]` | Optional |
| `end_date` | `context["end_date"]` | Optional |
| `token` | `MOAAH_API_KEY` config | Passed as query parameter |

**Moaah response sections scanned:**

| Section Key | Type | Entries Transformed |
|-------------|------|---------------------|
| `antidumping` | dict or list | Yes |
| `importLicensing` | list | Yes |
| `pr` | dict or list | Yes |
| `qr` | dict with `data`/`dataOrigin` | Yes |
| `docs` | dict or list | Yes |
| `docs_origin` | dict or list | Yes |
| `matched_hs_codes` | list | Yes |

### 3.2 Entry-Level Field Mapping

| DEM Field | Moaah Source Fields | Priority |
|-----------|---------------------|----------|
| `id` | `entry["uuid"]` → `entry["id"]` → `id(entry)` | First non-null |
| `content` | `title - body` composite | See below |
| `source_id` | Adapter config `source_id` | Config-driven |
| `confidence` | Computed | See Section 4 |
| `metadata.section` | Section key name | e.g., `"antidumping"` |
| `metadata.effective_date` | `publication_date` → `initiation_dt` → `effective_date` | First non-null |
| `metadata.source_url` | `id_link` → `source_url` → `url` | First non-null |
| `metadata.country` | `country` | Direct |
| `metadata.hs_code` | `hs_code` → `HSCode` → `code` | First non-null |
| `metadata.regulation_type` | `regulation_type` → section label | Fallback to section |
| `metadata.category` | `category` | Direct |
| `metadata.version` | Adapter config `version` | Config-driven |
| `metadata.fetch_timestamp` | Adapter config `updated_at` | Config-driven |
| `metadata.record_hash` | `hash(frozenset(entry.items()))` | Computed at transform time |
| `metadata.retrieval_status` | Constant `"success"` | Set on successful transform |

### 3.3 Title & Content Construction

**Title priority:**
1. `subject_product`
2. `desc`
3. `title`
4. Section label fallback

**Content priority:**
1. `duty_measure_detail`
2. `summary`
3. `description`
4. `requirement`
5. `regulation_text`
6. Empty string

If content is a dict, it is flattened to `"k: v | k: v"` format.

**Final content format:**
- If title exists: `"{title} - {content}"`
- If no title: `str(content)`

---

## 4. Confidence Rules

| Condition | Confidence |
|-----------|------------|
| Base (no source_url, no effective_date) | `0.75` |
| `source_url` present | `0.85` |
| `effective_date` present | `0.90` |

**Aggregation:** Average of all result confidences. If no results, returns `confidence: None`.

**Note:** These rules are adapter-specific and differ from WP-37 file-based provider rules.

---

## 5. Provenance Metadata

| Field | Type | Source | Purpose |
|-------|------|--------|---------|
| `fetch_timestamp` | ISO-8601 string | `updated_at` config passed at bootstrap | When the adapter was instantiated/updated |
| `record_hash` | String | `hash(frozenset(entry.items()))` | Change detection for individual records |
| `retrieval_status` | Constant `"success"` | Adapter-set | Indicates successful transformation |

**Note:** The Moaah API does not return record-level provenance fields (`source_authority`, `legal_act_reference`) in documented regulatory response schemas. These fields are not mapped. Adapter-side provenance fields are assigned by transformation logic, which is an acceptable approach per `KNOWLEDGE_INGESTION_CONTRACT.md`.

---

## 6. Error Handling & Retry/Backoff Matrix

### 6.1 HTTP Client Retry Policy

| Parameter | Value |
|-----------|-------|
| Max attempts | 3 |
| Initial backoff | 1.0 seconds |
| Backoff multiplier | 2x |
| Retry on | `httpx.TimeoutException`, `httpx.NetworkError`, HTTP 429 |
| Fail on | Other HTTP errors after retries exhausted |

### 6.2 Failure Mode Matrix

| Failure Mode | Detection | Adapter Response |
|--------------|-----------|------------------|
| Network timeout | `httpx.TimeoutException` | Retry up to 3x; then empty results |
| Connection error | `httpx.NetworkError` | Retry up to 3x; then empty results |
| Rate limit (429) | HTTP 429 response | Retry up to 3x with backoff; then raise |
| HTTP 4xx/5xx | `response.raise_for_status()` | Raise after retries; outer handler returns empty results |
| Invalid JSON | `response.json()` exception | Returns empty results |
| Non-dict response | `isinstance(raw, dict)` check | Returns empty results |
| Missing country | `context.get("country")` is None | Returns empty results immediately |
| Missing credentials | `base_url` or `api_key` empty | Returns empty results; registration skipped at startup |

---

## 7. Configuration

### 7.1 Settings (`backend/app/core/config.py`)

| Setting | Type | Default | Purpose |
|---------|------|---------|---------|
| `MOAAH_BASE_URL` | `str` | `""` | Moaah API base URL |
| `MOAAH_API_KEY` | `str` | `""` | API key passed as `token` query param |
| `MOAAH_TIMEOUT_SECONDS` | `float` | `10.0` | HTTP request timeout |
| `MOAAH_SOURCE_ID` | `str` | `"moaah"` | Registry source ID |
| `MOAAH_SOURCE_NAME` | `str` | `"Moaah External Knowledge"` | Display name |
| `MOAAH_SOURCE_TYPE` | `str` | `"external"` | Source type |
| `MOAAH_SOURCE_VERSION` | `str` | `"1.0.0"` | Adapter version |

### 7.2 Bootstrap Registration (`backend/main.py`)

```python
if settings.MOAAH_API_KEY and settings.MOAAH_BASE_URL:
    from app.agent.knowledge.mooadapter import MoaahExternalSourceAdapter
    moaah_adapter = MoaahExternalSourceAdapter(
        config={
            "source_id": settings.MOAAH_SOURCE_ID,
            "name": settings.MOAAH_SOURCE_NAME,
            "type": settings.MOAAH_SOURCE_TYPE,
            "version": settings.MOAAH_SOURCE_VERSION,
            "updated_at": "2026-08-12T00:00:00Z",
            "base_url": settings.MOAAH_BASE_URL,
            "api_key": settings.MOAAH_API_KEY,
            "timeout_seconds": settings.MOAAH_TIMEOUT_SECONDS,
        }
    )
    await knowledge_provider_registry.register(moaah_adapter)
```

**Behavior:**  
- Registration is conditional on both `MOAAH_API_KEY` and `MOAAH_BASE_URL` being set.
- Registration failures are caught and logged as warnings; do not crash startup.
- If credentials are missing, a warning is logged and registration is skipped.

---

## 8. Registry Integration

| Aspect | Detail |
|--------|--------|
| Registry | `KnowledgeProviderRegistry` |
| Registration | Conditional in `main.py` `lifespan()` |
| Source ID | `settings.MOAAH_SOURCE_ID` (default: `"moaah"`) |
| Query path | `registry.query("moaah", ...)` |
| Coexistence | Moaah registers alongside existing providers (`graph_provider`, `company_knowledge_provider`, `regulations_provider`) |
| Unregistration | Not implemented; adapter persists for application lifetime |

---

## 9. Test Coverage

| Test File | Tests | Coverage |
|-----------|-------|----------|
| `tests/agent/test_mooadapter.py` | 9 | Contract, query transformation, error handling, graceful degradation |
| `tests/agent/test_mooadapter_integration.py` | 6 | Registry registration, queryability, coexistence, interface compliance, metadata shape |

**Note:** Tests are passing; no regressions in existing knowledge layer tests.

---

## 10. Open Items & Unverified Details

| Item | Status |
|------|--------|
| Moaah written clarification on internal-use scope, retention, and commercial/partner licensing | **Unverified** — documentation follow-up only, not a blocker for G2 |
| Actual API response sample for Egypt (country code 818) | **Unverified** — not required for G2; implementation uses documented endpoint structure |
| Rate limit verification under load | **Unverified** — retry logic implemented but not load-tested |
| `source_authority` and `legal_act_reference` fields from Moaah API | **Not available** — not present in documented regulatory response schemas; adapter uses computed provenance instead |

---

## 11. Gate Status

| Gate | Status | Evidence |
|------|--------|----------|
| G0 — WP-38 Plan Approval | Approved | Project Owner approval recorded in current work session |
| G1 — Moaah Source Selection | Approved | Project Owner approval recorded in current work session |
| G2 — Adapter Specification Review | **Pending** | This document created for G2 review; approval pending |

---

*Document Status: Draft — Pending G2 Review*
