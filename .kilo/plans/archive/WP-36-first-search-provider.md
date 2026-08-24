# WP-36: First Search Provider Implementation

**Work Package:** WP-36 â€” First Search Provider Implementation  
**Status:** Closed â€” Completed  
**Date:** 2026-08-10  
**Authority:** `PLAN.md` (Master Roadmap v2.1) â€” Single Source of Truth  
**Governing Documents:** `.kilo/plans/WP-35-spec.md`, `.kilo/plans/WP-35-add-provider-guide.md`, `.kilo/plans/WP-34-spec.md`, `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Path:** `\.kilo/plans/archive/WP-36-first-search-provider\.md`

---

## 1. ط§ظ„ظ‡ط¯ظپ

طھظ†ظپظٹط° **SearXNG** ظƒط£ظˆظ„ Search Provider ظپط¹ظ„ظٹ ظˆط§ط­ط¯ ظپظˆظ‚ ط·ط¨ظ‚ط© WP-35 Provider-AgnosticطŒ ظˆطھط­ظˆظٹظ„ظ‡ط§ ظ…ظ† ط·ط¨ظ‚ط© ظ…ط¬ط±ط¯ط© ط¥ظ„ظ‰ ظ…ط²ظˆط¯ ط¨ط­ط« ظ‚ط§ط¨ظ„ ظ„ظ„طھط´ط؛ظٹظ„ ظپط¹ظ„ظٹظ‹ط§ ظپظٹ ط§ظ„ط¥ظ†طھط§ط¬.

## 2. ط§ظ„ظ†ط·ط§ظ‚

### 2.1 ط¯ط§ط®ظ„ ط§ظ„ظ†ط·ط§ظ‚
- طھظ†ظپظٹط° **SearXNG ظپظ‚ط·** ظƒظ€ `SearchProviderAdapter` ظپط¹ظ„ظٹ.
- طھط³ط¬ظٹظ„ `SearXNGAdapter` ظپظٹ `SearchProviderRouter` ظپظٹ ظ…ط³ط§ط± ط§ظ„ط¥ظ†طھط§ط¬.
- طھط­ظˆظٹظ„ ط§ط³طھط¬ط§ط¨ط© SearXNG ط¥ظ„ظ‰ `RetrievedContent` ظˆ `RetrievalResult` ط¨ط§ط³طھط®ط¯ط§ظ… `RetrievalStatus` ط§ظ„ط­ط§ظ„ظٹ.
- ط§ط®طھط¨ط§ط±ط§طھ ط§ظ„ظ€Adapter ظˆطھظƒط§ظ…ظ„ failover.
- طھظˆط«ظٹظ‚ ط§ظ„ظ€Adapter ط§ظ„ط¬ط¯ظٹط¯.

### 2.2 ط®ط§ط±ط¬ ط§ظ„ظ†ط·ط§ظ‚
- **ظ„ط§** طھظ†ظپظٹط° ط£ظƒط«ط± ظ…ظ† ظ…ط²ظˆط¯ ط¨ط­ط« ظˆط§ط­ط¯ ظپظٹ ظ‡ط°ظ‡ ط§ظ„ظ€WP.
- **ظ„ط§** طھظ†ظپظٹط° Brave Search API ظپظٹ ظ‡ط°ظ‡ ط§ظ„ظ€WP.
- **ظ„ط§** طھط¹ط¯ظٹظ„ WP-35 ط£ظˆ ط¥ط¹ط§ط¯ط© ظپطھط­ظ‡ط§.
- **ظ„ط§** طھط¹ط¯ظٹظ„ WP-34 ط£ظˆ Knowledge Ingestion Contract ط£ظˆ ط£ظٹ ط¹ظ‚ط¯ ظ…ط¹ظ…ط§ط±ظٹ.
- **ظ„ط§** ط®ظ„ط· Search Provider ظ…ط¹ AI/LLM Provider Router.
- **ظ„ط§** ط§ط¹طھظ…ط§ط¯ VPS ط£ظˆ ط®ط¯ظ…ط© ط®ط§ط±ط¬ظٹط© ط£ظˆ Credits ظƒط§ط¹طھظ…ط§ط¯ ظ…ط¹ظ…ط§ط±ظٹ ط¥ظ„ط²ط§ظ…ظٹ.
- **ظ„ط§** طھظ†ظپظٹط° web scraping ط£ظˆ crawling ظ…ط¨ط§ط´ط±.
- **ظ„ط§** طھط؛ظٹظٹط± Evidence/Provenance/Verification lifecycle.

## 3. ط§ظ„ط§ط¹طھظ…ط§ط¯ ط¹ظ„ظ‰ WP-35

| ط§ظ„ظ…ظƒظˆظ† | ط§ظ„ظ…ط³ط§ط± | ط§ظ„ط­ط§ظ„ط© |
|--------|--------|--------|
| `ProviderCapability` | `backend/app/research/retrieval/providers/capability.py` | âœ… ظ…ظˆط¬ظˆط¯ |
| `SearchProviderAdapter` | `backend/app/research/retrieval/providers/adapter.py` | âœ… ظ…ظˆط¬ظˆط¯ |
| `SearchProviderRouter` | `backend/app/research/retrieval/providers/router.py` | âœ… ظ…ظˆط¬ظˆط¯ |
| `SEARCH_STUB_FALLBACK` | `backend/app/core/config.py` | âœ… ظ…ظˆط¬ظˆط¯ |
| WP-35 Boundaries | ظ…ط­ظپظˆط¸ط© | ظ„ط§ طھط¹ط¯ظٹظ„ ط¹ظ„ظ‰ WP-35 |

WP-36 ظ‡ظٹ **ط£ظˆظ„ ظ…ط³طھظ‡ظ„ظƒ طھط´ط؛ظٹظ„ظٹ** ظ„ط·ط¨ظ‚ط© WP-35طŒ ظˆطھظ†ظپظ‘ط° **SearXNG** ظپظ‚ط· ظƒط£ظˆظ„ ظ…ط²ظˆط¯ ط¨ط­ط« ظپط¹ظ„ظٹ.

## 4. ط§ظ„ظ‚ط±ط§ط±ط§طھ ط§ظ„ظ…ط«ط¨طھط©

| # | ط§ظ„ظ‚ط±ط§ط± | ط§ظ„ظ‚ظٹظ…ط© |
|---|--------|--------|
| D-1 | **ط£ظˆظ„ Search Provider ظپط¹ظ„ظٹ ط³ظٹطھظ… طھظ†ظپظٹط°ظ‡ ظپظٹ WP-36** | âœ… **SearXNG** |
| D-2 | **ط®ظٹط§ط± ظ…ط³طھظ‚ط¨ظ„ظٹ/ط¨ط¯ظٹظ„ ظ„ط§ط­ظ‚** | âœ… **Brave Search API** â€” ظ„ظٹط³ ط¶ظ…ظ† ظ†ط·ط§ظ‚ WP-36 |

**طھظپطµظٹظ„ D-1:**  
SearXNG ظ‡ظˆ ط£ظˆظ„ ظ…ط²ظˆط¯ ط¨ط­ط« ظپط¹ظ„ظٹ ط³ظٹطھظ… طھظ†ظپظٹط°ظ‡ ظپظٹ WP-36.  
ظ†ظ‚ط·ط© ط§ظ„ط§طھطµط§ظ„/ط§ظ„ط¨ط­ط« ط³طھظƒظˆظ† ط¹ط¨ط± SearXNG instance ظ…ظڈط³طھط¶ط§ظپط© ط°ط§طھظٹظ‹ط§ ط£ظˆ ط¹ط§ظ…ط©طŒ ظˆظپظ‚ظ‹ط§ ظ„ظ…ظˆط§ظپظ‚ط© ط§ظ„ظ…ط§ظ„ظƒ ط¹ظ„ظ‰ ط§ظ„ط¨ظ†ظٹط© ط§ظ„طھط­طھظٹط©.  
ط§ظ„ط¨ظٹط§ظ†ط§طھ ط§ظ„ط§ط¹طھظ…ط§ط¯ظٹط© ط³طھظڈط¯ط§ط± ط¹ط¨ط± ظ…طھط؛ظٹط±ط§طھ ط§ظ„ط¨ظٹط¦ط© ط§ظ„طھط§ظ„ظٹط©:
- `SEARXNG_BASE_URL`: ط¹ظ†ظˆط§ظ† ط§ظ„ظ€instance
- `SEARXNG_API_KEY`: ظ…ظپطھط§ط­ API ط¥ط°ط§ ظƒط§ظ† ط§ظ„ظ€instance ظٹطھط·ظ„ط¨ ظ…طµط§ط¯ظ‚ط©
- `SEARXNG_TIMEOUT_SECONDS`: ظ…ظ‡ظ„ط© ط§ظ„ط§طھطµط§ظ„ ط¨ط§ظ„ط«ظˆط§ظ†ظٹ

ظ„ط§ طھظڈط®ط²ظ† ط£ط³ط±ط§ط± ط«ط§ط¨طھط© ظپظٹ ط§ظ„ظƒظˆط¯. ط¬ظ…ظٹط¹ ط§ظ„ظ‚ظٹظ… طھظڈظ‚ط±ط£ ظ…ظ† `.env` ط£ظˆ ظ…طھط؛ظٹط±ط§طھ ط§ظ„ط¨ظٹط¦ط©.

**طھظپطµظٹظ„ D-2:**  
Brave Search API ظ…ط±ط´ط­ ظ„ط§ط­ظ‚/ط¨ط¯ظٹظ„ ظ…ط³طھظ‚ط¨ظ„ظٹ ظپظ‚ط·.  
ظ„ط§ ظٹظڈظ†ظپظ‘ط° ظپظٹ WP-36طŒ ظˆظ„ط§ ظٹظڈط´طھط±ط· ط§ظ„طھط®ط·ظٹط· ظ„ظ‡ ط§ظ„ط¢ظ†.

## 5. ط§ظ„ظ…ظ‡ط§ظ… ط§ظ„طھظ†ظپظٹط°ظٹط©

```
Task 1: Implement SearXNG Adapter
Task 2: Register SearXNG Adapter in Production Router
Task 3: Tests â€” SearXNG Adapter + Failover + Regression
Task 4: Documentation Update
```

### Task 1: Implement SearXNG Adapter
**ط§ظ„ظ‡ط¯ظپ:** ط¥ظ†ط´ط§ط، `SearXNGAdapter` ظپط¹ظ„ظٹ ظٹظ…طھط¯ ظ…ظ† `SearchProviderAdapter`.
**ط§ظ„ظ…ظ„ظپ ط§ظ„ظ…طھظˆظ‚ط¹:** `backend/app/research/retrieval/providers/searxng_adapter.py`
**ط§ظ„ظ…طھط·ظ„ط¨ط§طھ:**
- `ProviderCapability` ظ…ط¹ `provider_id="searxng"`, `priority`, `enabled` ظˆط§ظ„ظ‚ط¯ط±ط§طھ ط§ظ„ظپط¹ظ„ظٹط© ظ„ظ€ SearXNG.
- `retrieve(source, query)` ظٹظ†ظپظ‘ط° ط·ظ„ط¨ ط¨ط­ط« HTTP ط¥ظ„ظ‰ SearXNG instance ظˆظٹط­ظˆظ„ ط§ظ„ط§ط³طھط¬ط§ط¨ط© ط¥ظ„ظ‰ `RetrievedContent` / `RetrievalResult`.
- `health_check()` ظٹطھط­ظ‚ظ‚ ظ…ظ† طھظˆظپط± SearXNG instance.
- ط£ط®ط·ط§ط، SearXNG طھظڈ mapped ط¥ظ„ظ‰ `RetrievalStatus` ط§ظ„ط­ط§ظ„ظٹ ظپظ‚ط·.
- ظ„ط§ new contracts.

**ظ…ط«ط§ظ„ ظ„ظ‡ظٹظƒظ„ ط§ظ„ظ€Adapter:**
```python
class SearXNGAdapter(SearchProviderAdapter):
    def __init__(self, capability: ProviderCapability, base_url: str, timeout: float = 10.0):
        self._capability = capability
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def capability(self) -> ProviderCapability:
        return self._capability

    async def retrieve(self, source: Source, query: str) -> RetrievalResult:
        # httpx post to {base_url}/search
        # Map JSON results to RetrievedContent
        # Map HTTP/network errors to RetrievalStatus
        pass

    async def health_check(self) -> bool:
        # Return True if SearXNG instance is reachable
        pass
```

**Acceptance Criteria:**
- AC-36.1: `retrieve()` ظٹط±ط¬ط¹ `RetrievalStatus.SUCCESS` ظ…ط¹ `RetrievedContent` طµط§ظ„ط­ ط¹ظ†ط¯ ط§ط³طھط¬ط§ط¨ط© ظ†ط§ط¬ط­ط© ظ…ظ† SearXNG.
- AC-36.2: `retrieve()` ظٹط±ط¬ط¹ `RetrievalStatus.TIMEOUT` ط¹ظ†ط¯ ط§ظ†طھظ‡ط§ط، ظ…ظ‡ظ„ط© ط§ظ„ط§طھطµط§ظ„ ط¨ظ€ SearXNG.
- AC-36.3: `retrieve()` ظٹط±ط¬ط¹ `RetrievalStatus.CONNECTION_FAILURE` ط¹ظ†ط¯ ط¹ط¯ظ… ط§ظ„ط§طھطµط§ظ„ ط¨ظ€ SearXNG.
- AC-36.4: `retrieve()` ظٹط±ط¬ط¹ `RetrievalStatus.INVALID_RESPONSE` ط¹ظ†ط¯ ط§ط³طھط¬ط§ط¨ط© ط؛ظٹط± ظ…طھظˆظ‚ط¹ط© ظ…ظ† SearXNG.
- AC-36.5: `health_check()` ظٹط±ط¬ط¹ `True` ط¹ظ†ط¯ طھظˆظپط± SearXNG ظˆ `False` ط¹ظ†ط¯ ط¹ط¯ظ… طھظˆظپط±ظ‡.
- AC-36.6: ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ `contracts.py` ط£ظˆ `RetrievalStatus` enum.

### Task 2: Register SearXNG Adapter in Production Router
**ط§ظ„ظ‡ط¯ظپ:** طھط³ط¬ظٹظ„ `SearXNGAdapter` ظپظٹ `SearchProviderRouter` ظپظٹ `research.py`.
**ط§ظ„ظ…طھط·ظ„ط¨ط§طھ:**
- طھط³ط¬ظٹظ„ طµط±ظٹط­ ط¹ظ†ط¯ bootstrap.
- `SEARCH_STUB_FALLBACK` ظٹط¨ظ‚ظ‰ ظƒط§ط­طھظٹط§ط· طµط±ظٹط­ ظپظ‚ط·.
- ظ„ط§ makes ط§ظ„ظ€Adapter ط§ظ„ط¬ط¯ظٹط¯ silent fallback.

**Acceptance Criteria:**
- AC-36.7: `SearXNGAdapter` ظ…ط³ط¬ظ„ ظپظٹ `SearchProviderRouter` ط¹ظ†ط¯ ط¨ط¯ط، ط§ظ„طھط·ط¨ظٹظ‚.
- AC-36.8: `SEARCH_STUB_FALLBACK=false` ط§ظپطھط±ط§ط¶ظٹظ‹ط§.
- AC-36.9: ط¹ظ†ط¯ ظپط´ظ„ `SearXNGAdapter`طŒ ظٹط­ط§ظˆظ„ Router ط§ظ„ظ…ط­ط§ظˆظ„ط© ظ…ط±ط© ط£ط®ط±ظ‰ ط£ظˆ ظٹط±ط¬ط¹ `FAILED` ط¯ظˆظ† ط§ط³طھط®ط¯ط§ظ… `StubRetriever` طھظ„ظ‚ط§ط¦ظٹظ‹ط§.

### Task 3: Tests
**ط§ظ„ظ‡ط¯ظپ:** ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط³ظ„ظˆظƒ `SearXNGAdapter` ظˆط§ظ„ظ€Router ظ…ط¹ظ‡.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- `tests/test_research_searxng_adapter.py`
**ط§ظ„ظ…طھط·ظ„ط¨ط§طھ:**
- ط§ط®طھط¨ط§ط± ظ†ط¬ط§ط­ `retrieve()` ظ…ط¹ ط§ط³طھط¬ط§ط¨ط© ظˆظ‡ظ…ظٹط©/mock ظ…ظ† SearXNG.
- ط§ط®طھط¨ط§ط± ظپط´ظ„ `retrieve()` ظٹظڈ mapped ط¥ظ„ظ‰ `RetrievalStatus` ط§ظ„طµط­ظٹط­.
- ط§ط®طھط¨ط§ط± `health_check()`.
- ط§ط®طھط¨ط§ط± failover ط¥ط°ط§ ظƒط§ظ† ظ‡ظ†ط§ظƒ ط£ظƒط«ط± ظ…ظ† adapter (ط­ط§ظ„ظٹظ‹ط§ ظˆط§ط­ط¯ ظپظ‚ط·).
- ط§ط®طھط¨ط§ط± ط£ظ† `StubRetriever` ظ„ط§ ظٹظڈط³طھط®ط¯ظ… طھظ„ظ‚ط§ط¦ظٹظ‹ط§.
- WP-34 regression tests طھط¸ظ„ ط³ظ„ظٹظ…ط©.

**Acceptance Criteria:**
- AC-36.10: Unit test ظٹط؛ط·ظٹ ط¬ظ…ظٹط¹ ط­ط§ظ„ط§طھ `retrieve()` ط§ظ„ظ…ط­ط¯ط¯ط© ظپظٹ Task 1.
- AC-36.11: Unit test ظٹط؛ط·ظٹ `health_check()`.
- AC-36.12: Integration test ظٹط«ط¨طھ ط£ظ† `SearXNGAdapter` ظٹط¹ظ…ظ„ ظ…ط¹ `SearchProviderRouter`.
- AC-36.13: WP-34 regression tests طھظ†ط¬ط­ (ظ„ط§ ظƒط³ط± ظپظٹ `test_research_retrieval.py`, `test_research.py`, `test_research_quality.py`, `test_research_evidence.py`).

### Task 4: Documentation Update
**ط§ظ„ظ‡ط¯ظپ:** طھط­ط¯ظٹط« ط§ظ„ظˆط«ط§ط¦ظ‚ ظ„طھط¹ظƒط³ SearXNG ظƒط£ظˆظ„ ظ…ط²ظˆط¯ ظپط¹ظ„ظٹ.
**ط§ظ„ظ…طھط·ظ„ط¨ط§طھ:**
- طھط­ط¯ظٹط« `.kilo/plans/WP-35-add-provider-guide.md` ط¥ط°ط§ ظ„ط²ظ… ط§ظ„ط£ظ…ط±.
- ظ„ط§ طھط¹ط¯ظٹظ„ WP-35 spec ط£ظˆ plan ط§ظ„ط£ط³ط§ط³ظٹط©.
- docstrings ظپظٹ `SearXNGAdapter`.

## 6. ظ‡ظٹظƒظ„ ط§ظ„ظ…ظ„ظپط§طھ ط§ظ„ظ…طھظˆظ‚ط¹

```
backend/app/research/retrieval/providers/
â”œâ”€â”€ __init__.py
â”œâ”€â”€ capability.py       (FROZEN â€” WP-35)
â”œâ”€â”€ adapter.py          (FROZEN â€” WP-35)
â”œâ”€â”€ router.py           (FROZEN â€” WP-35)
â””â”€â”€ searxng_adapter.py   (NEW â€” WP-36)

backend/app/core/config.py       (MODIFIED â€” add SEARXNG_* env vars)
backend/app/routers/research.py   (MODIFIED â€” register SearXNGAdapter)
backend/tests/
â””â”€â”€ test_research_searxng_adapter.py   (NEW â€” WP-36)
```

## 7. ظ‡ظٹظƒظ„ SearXNGAdapter ط§ظ„ظ…طھظˆظ‚ط¹

```python
from app.research.retrieval.providers.adapter import SearchProviderAdapter
from app.research.retrieval.providers.capability import ProviderCapability
from app.research.retrieval.contracts import RetrievedContent, RetrievalResult, RetrievalStatus
from app.schemas.research import Source

class SearXNGAdapter(SearchProviderAdapter):
    def __init__(self, capability: ProviderCapability, base_url: str, timeout: float = 10.0):
        self._capability = capability
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    @property
    def capability(self) -> ProviderCapability:
        return self._capability

    async def retrieve(self, source: Source, query: str) -> RetrievalResult:
        # httpx post to {base_url}/search
        # Map JSON results to RetrievedContent
        # Map HTTP/network errors to RetrievalStatus
        pass

    async def health_check(self) -> bool:
        # Return True if SearXNG instance is reachable
        pass
```

## 8. ط§ظ„ط§ط®طھط¨ط§ط±ط§طھ ظˆط§ظ„طھط­ظ‚ظ‚

| ط§ظ„ظ†ظˆط¹ | ط§ظ„ظˆطµظپ |
|--------|-------|
| Unit tests | `SearXNGAdapter` ظپظ‚ط·: success, failure, health_check |
| Integration tests | Router + `SearXNGAdapter` + WP-34 lifecycle |
| Regression | `tests/test_research_retrieval.py`, `tests/test_research.py`, `tests/test_research_quality.py`, `tests/test_research_evidence.py` |
| Boundary | ظ„ط§ طھط¹ط¯ظٹظ„ ط¹ظ„ظ‰ `contracts.py`, `orchestrator.py`, `quality.py`, `KNOWLEDGE_INGESTION_CONTRACT.md` |

## 9. ط­ط¯ظˆط¯ طµط§ط±ظ…ط©

| ط§ظ„ط­ط¯ | ط§ظ„طھط­ظ‚ظ‚ |
|-------|--------|
| ظ„ط§ طھط¹ط¯ظٹظ„ WP-34 contracts | `git diff` ط¹ظ„ظ‰ `contracts.py`, `orchestrator.py`, `retrieval/orchestrator.py`, `quality.py` |
| ظ„ط§ طھط¹ط¯ظٹظ„ Knowledge Ingestion Contract | `git diff` ط¹ظ„ظ‰ `KNOWLEDGE_INGESTION_CONTRACT.md` |
| ظ„ط§ ط®ظ„ط· Search Provider ظ…ط¹ AI/LLM | ظ„ط§ imports ظ…ظ† `app.agent.llm` ط£ظˆ ظ…ط§ ظٹط¹ط§ط¯ظ„ظ‡ ظپظٹ adapter |
| ظ„ط§ طھط¹ط¯ظٹظ„ WP-35 | ظ„ط§ طھط¹ط¯ظٹظ„ ط¹ظ„ظ‰ `capability.py`, `adapter.py`, `router.py` ط¥ظ„ط§ ط¥ط°ط§ ظƒط§ظ† bug ظپظٹ WP-35 |
| StubRetriever ط§ط­طھظٹط§ط· طµط±ظٹط­ ظپظ‚ط· | `SEARCH_STUB_FALLBACK` ظٹط¨ظ‚ظ‰ `false` ط§ظپطھط±ط§ط¶ظٹظ‹ط§ |
| Brave Search API ط؛ظٹط± ظ…ط¯ط±ط¬ ط§ظ„ط¢ظ† | ظ„ط§ ظ…ظ„ظپط§طھ ط£ظˆ طھظƒظˆظٹظ†ط§طھ ط®ط§طµط© ط¨ظ€ Brave ظپظٹ WP-36 |

## 10. Exit Criteria

| # | ط§ظ„ط´ط±ط· | ط§ظ„طھط­ظ‚ظ‚ |
|---|-------|--------|
| EC-36.1 | D-1 ظ…ط«ط¨طھ: SearXNG ظ‡ظˆ ط£ظˆظ„ Provider | Decision record ظپظٹ ط§ظ„ط®ط·ط© |
| EC-36.2 | `SearXNGAdapter` ظ…ظ†ظپظژظ‘ط° ظˆظ…ط³ط¬ظ„ | Code review + unit test |
| EC-36.3 | `retrieve()` ظٹط±ط¬ط¹ `RetrievalResult` طµط§ظ„ط­ | Unit test |
| EC-36.4 | `health_check()` ظٹط¹ظ…ظ„ | Unit test |
| EC-36.5 | failover ظٹط¹ظ…ظ„ ط¹ظ†ط¯ ظپط´ظ„ `SearXNGAdapter` | Integration test |
| EC-36.6 | WP-34 regression tests طھظ†ط¬ط­ | pytest suite |
| EC-36.7 | ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ WP-34 contracts | Git diff |
| EC-36.8 | ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ Knowledge Ingestion Contract | Git diff |
| EC-36.9 | `StubRetriever` ظ„ط§ ظٹظڈused ظƒظ€ silent fallback | Test + config review |

## 11. ط§ظ„ظ…ط®ط§ط·ط± ظˆط§ظ„ظ‚ط±ط§ط±ط§طھ ط§ظ„ظ…ظپطھظˆط­ط©

| # | ط§ظ„ظ…ط®ط§ط·ط± | ط§ظ„ط§ط­طھظ…ط§ظ„ | ط§ظ„طھط£ط«ظٹط± | ط§ظ„طھط®ظپظٹظپ |
|---|---------|---------|--------|---------|
| R-1 | ظˆط§ط¬ظ‡ط© ط¨ط±ظ…ط¬ط© SearXNG طھطھط؛ظٹط± | Low | Medium | ط¥طµط¯ط§ط±ط§طھ ط«ط§ط¨طھط© ظ…ظ† ط§ظ„ط§ط³طھط¹ظ„ط§ظ…/ط§ظ„ط§ط³طھط¬ط§ط¨ط©ط› ظˆط«ظ‘ظ‚ ط§ظ„ط§ط®طھظ„ط§ظپط§طھ |
| R-2 | Instance SearXNG ط؛ظٹط± ظ…ظˆط«ظˆظ‚ ط£ظˆ ط¨ط·ظٹط، | Medium | High | طھط£ظƒط¯ ظ…ظ† ظ…ظˆط§ظپظ‚ط© ط§ظ„ظ…ط§ظ„ظƒ ط¹ظ„ظ‰ ط§ظ„ط¨ظ†ظٹط© ط§ظ„طھط­طھظٹط© ظ‚ط¨ظ„ ط§ظ„طھظ†ظپظٹط° |
| R-3 | ظ†طھط§ط¦ط¬ SearXNG ط؛ظٹط± ظ…ظ†ط§ط³ط¨ط© ظ„ط§ط­طھظٹط§ط¬ط§طھ DEM | Medium | Medium | ط®ط±ظٹط·ط© ط§ظ„ط­ظ‚ظˆظ„ ظ‚ط§ط¨ظ„ط© ظ„ظ„طھط¹ط¯ظٹظ„ ط¨ط¯ظˆظ† طھط¹ط¯ظٹظ„ WP-35 |
| R-4 | StubRetriever ظٹظڈused ظƒظ€ fallback طµط§ظ…طھ | Low | Medium | ط§ط®طھط¨ط§ط± طµط±ظٹط­ + `SEARCH_STUB_FALLBACK=false` ط§ظپطھط±ط§ط¶ظٹظ‹ط§ |

| # | ط§ظ„ظ‚ط±ط§ط± ط§ظ„ظ…ظپطھظˆط­ | ط§ظ„ظ…ط§ظ„ظƒطں |
|---|---------------|---------|
| D-1 | ظ…ط«ط¨طھ: **SearXNG** ظƒط£ظˆظ„ Provider | âœ… ظ…ط«ط¨طھ |
| D-2 | Brave Search API ظƒط¨ط¯ظٹظ„ ظ„ط§ط­ظ‚ | âœ… ظ…ط¤ط¬ظ„ â€” ظ„ظٹط³ ط¶ظ…ظ† WP-36 |
| D-3 | ظ…ط§ ط¥ط°ط§ ظƒط§ظ† `SEARCH_STUB_FALLBACK` ظٹظڈظپط¹ظژظ‘ظ„ ظپظٹ ط§ظ„ط¥ظ†طھط§ط¬ | طھط´ط؛ظٹظ„ظٹ |
| D-4 | ظ…ط³ط¤ظˆظ„ظٹط© طھط´ط؛ظٹظ„ ظˆطµظٹط§ظ†ط© instance SearXNG | طھط´ط؛ظٹظ„ظٹ |

## 12. Closure Record

**Closure Date:** 2026-08-10
**Closure Status:** Completed
**Baseline:** WP-36 First Search Provider Implementation â€” SearXNG

### 12.1 Completed Tasks

| Task | Status | Evidence |
|------|--------|----------|
| Task 1: Select/Approve Provider | âœ… Completed | D-1 = SearXNG + SEARXNG_* env vars |
| Task 2: Implement SearXNG Adapter | âœ… Completed | `backend/app/research/retrieval/providers/searxng_adapter.py` |
| Task 3: Register in Production Router | âœ… Completed | `backend/app/routers/research.py` |
| Task 4: Tests | âœ… Completed | `tests/test_research_searxng_adapter.py` + regression |
| Task 5: Documentation Update | âœ… Completed | `WP-35-add-provider-guide.md` + docstrings |

### 12.2 Exit Criteria Verification

| # | Condition | Status | Evidence |
|---|-----------|--------|----------|
| EC-36.1 | D-1 fixed: SearXNG is first provider | âœ… PASS | Section 4 decision record |
| EC-36.2 | SearXNGAdapter implemented and registered | âœ… PASS | Code review + tests |
| EC-36.3 | `retrieve()` returns valid `RetrievalResult` | âœ… PASS | Unit tests |
| EC-36.4 | `health_check()` works | âœ… PASS | Unit tests |
| EC-36.5 | failover works when adapter fails | âœ… PASS | Integration test |
| EC-36.6 | WP-34 regression tests pass | âœ… PASS | pytest suite |
| EC-36.7 | No WP-34 contracts modified | âœ… PASS | Git diff clean |
| EC-36.8 | No Knowledge Ingestion Contract modified | âœ… PASS | Git diff clean |
| EC-36.9 | `StubRetriever` not used as silent fallback | âœ… PASS | Test + config review |

### 12.3 Boundary Verification

- âœ… WP-35 = **Closed â€” Completed**, not reopened
- âœ… WP-34 contracts unchanged
- âœ… Knowledge Ingestion Contract unchanged
- âœ… No mixing of Search Provider with AI/LLM Provider
- âœ… No architectural primary provider declared
- âœ… No hardcoded secrets or API keys
- âœ… Brave Search API deferred, not implemented

### 12.4 Final Forensic Audit

**Result:** PASS
**Findings:** None
**Remaining technical gaps:** None

---

*Document Status: Closed â€” Completed*

