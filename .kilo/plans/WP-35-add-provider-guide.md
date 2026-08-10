# WP-35 Task 7: How to Add a New Search Provider

## Purpose
Guide for adding a new search provider adapter to WP-35 without modifying WP-34 contracts, the research lifecycle, or any existing architecture.

---

## Prerequisites
- WP-35 Router and Adapter Layer is installed.
- No WP-34 contracts are changed during this process.
- The new provider is not declared as primary or mandatory in architecture or config.

---

## Concrete Example: SearXNG
SearXNG is the first concrete search provider implemented in this project. It is an example of how to implement a `SearchProviderAdapter` above the WP-35 abstraction layer. SearXNG is **not** an architectural primary; it is one pluggable adapter among potentially many future adapters.

### SearXNG-specific configuration
SearXNG is configured via environment variables:
- `SEARXNG_BASE_URL`: URL of the SearXNG instance
- `SEARXNG_API_KEY`: optional API key if the instance requires authentication
- `SEARXNG_TIMEOUT_SECONDS`: request timeout in seconds

### SearXNGAdapter registration in production
```python
from app.research.retrieval.providers.capability import ProviderCapability
from app.research.retrieval.providers.searxng_adapter import SearXNGAdapter
from app.research.retrieval.providers.router import SearchProviderRouter

router = SearchProviderRouter()
adapter = SearXNGAdapter(
    capability=ProviderCapability(
        provider_id="searxng",
        supports_web_search=True,
        supports_snippets=True,
        supports_source_urls=True,
        requires_api_key=bool(settings.SEARXNG_API_KEY),
        priority=10,
        enabled=True,
    ),
    base_url=settings.SEARXNG_BASE_URL,
    api_key=settings.SEARXNG_API_KEY,
    timeout=settings.SEARXNG_TIMEOUT_SECONDS,
)
router.register_adapter(adapter)
```

**Rules:**
- SearXNGAdapter is one concrete implementation. Other adapters can be added/registered alongside it.
- Do not declare SearXNG as the only or primary provider in architecture.
- `StubRetriever` remains an explicit fallback only when `SEARCH_STUB_FALLBACK=true` is set.

## Step 1: Define ProviderCapability
Create a capability descriptor in your new adapter file or a shared config module.

```python
from app.research.retrieval.providers.capability import ProviderCapability

MY_PROVIDER_CAPABILITY = ProviderCapability(
    provider_id="my_provider",
    supports_web_search=True,
    supports_source_urls=False,
    supports_snippets=True,
    requires_api_key=True,
    priority=50,
    enabled=True,
)
```

**Rules:**
- Use a unique `provider_id` string.
- Set `priority` lower than existing adapters if this provider should be tried first.
- Set `enabled=False` to disable without removing the adapter.
- Do not add provider-specific credentials here.

---

## Step 2: Implement SearchProviderAdapter
Create a new class extending `SearchProviderAdapter`.

```python
from abc import abstractmethod
from app.research.retrieval.providers.adapter import SearchProviderAdapter
from app.research.retrieval.contracts import RetrievedContent, RetrievalResult, RetrievalStatus
from app.schemas.research import Source

class MyProviderAdapter(SearchProviderAdapter):
    def __init__(self, capability: ProviderCapability):
        self._capability = capability

    @property
    def capability(self) -> ProviderCapability:
        return self._capability

    async def retrieve(self, source: Source, query: str) -> RetrievalResult:
        # Call the provider API here.
        # Map provider errors to existing RetrievalStatus values.
        pass

    async def health_check(self) -> bool:
        # Return True if the provider is reachable.
        pass
```

**Rules:**
- `retrieve()` must return `RetrievalResult` using **existing** `RetrievalStatus` enum only.
- Map provider-specific errors to: `SUCCESS`, `TIMEOUT`, `CONNECTION_FAILURE`, `INVALID_RESPONSE`, `UNSUPPORTED_SOURCE`, `PROCESSING_FAILURE`, or `FAILED`.
- Do not introduce new status types or contracts.

---

## Step 3: Register the Adapter
Register the adapter with `SearchProviderRouter` in your deployment/bootstrap code.

```python
from app.research.retrieval.providers.router import SearchProviderRouter
from app.research.retrieval.providers.adapter import SearchProviderAdapter

router = SearchProviderRouter()
adapter = MyProviderAdapter(MY_PROVIDER_CAPABILITY)
router.register_adapter(adapter)
```

**Rules:**
- Register adapters at startup or via explicit configuration.
- Do not hardcode provider-specific URLs, keys, or SDKs inside the Router.
- The Router selects adapters automatically by `capability.priority`, `capability.enabled`, and `capability.supports_web_search`.

---

## Step 4: Add Tests
Create unit tests for the new adapter in `tests/`.

```python
import pytest
from app.research.retrieval.providers.adapter import SearchProviderAdapter
from app.research.retrieval.providers.capability import ProviderCapability
from app.schemas.research import Source

def test_my_adapter_retrieve_success():
    adapter = MyProviderAdapter(MY_PROVIDER_CAPABILITY)
    source = Source(source_id="src_1", name="Test", source_type="market_data", status="active")
    result = asyncio.run(adapter.retrieve(source, "query"))
    assert result.status == RetrievalStatus.SUCCESS
```

**Required tests:**
- `retrieve()` success path returns `RetrievalStatus.SUCCESS`.
- `retrieve()` failure path maps to correct `RetrievalStatus`.
- `health_check()` returns `bool`.
- Adapter does not depend on AI/LLM routing.
- Adapter does not modify WP-34 contracts.

---

## Step 5: Verify Failover
If multiple adapters are registered, verify that the Router:
- Tries the next adapter on `TIMEOUT`, `CONNECTION_FAILURE`, `INVALID_RESPONSE`, or exception.
- Returns `RetrievalStatus.FAILED` when all adapters fail.
- Never uses `StubRetriever` as a silent fallback.

```python
# Example: verify failover manually in tests
router = SearchProviderRouter()
router.register_adapter(FailingAdapter(capability_a))
router.register_adapter(SucceedingAdapter(capability_b))
result = await router.retrieve_with_fallback(source, "query")
assert result.status == RetrievalStatus.SUCCESS
```

---

## Hard Boundaries
- **No WP-34 contract changes:** Do not edit `contracts.py`, `orchestrator.py`, `stubs.py`, or any Evidence/Provenance/Verification code.
- **No AI/LLM coupling:** Do not import or configure any LLM provider inside the adapter.
- **No primary provider:** Do not declare any provider as default or primary in code or config. Selection is runtime-driven by capability and priority.
- **StubRetriever is not a search provider:** It is a test placeholder only. It must not be registered as a real provider in production.

---

## Checklist Before Merging
- [ ] `ProviderCapability` is defined with `provider_id`, `priority`, `enabled`, and correct capability flags.
- [ ] Adapter extends `SearchProviderAdapter` and implements `capability`, `retrieve()`, `health_check()`.
- [ ] `retrieve()` returns `RetrievalResult` with existing `RetrievalStatus` only.
- [ ] Adapter is registered via `SearchProviderRouter.register_adapter()`.
- [ ] Unit tests cover success, failure, and `health_check()`.
- [ ] No WP-34 contracts modified.
- [ ] No LLM/AI imports in adapter code.
- [ ] `StubRetriever` is not treated as a real provider.

---

*Document Status: Final*
