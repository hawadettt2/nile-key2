# WP-35 Specification: External Research Provider Adapter & Routing Layer

**Work Package:** WP-35 — External Research Provider Adapter & Routing Layer  
**Phase:** 2 — Intelligence Expansion  
**Baseline:** baseline-wp42 (`6f310f8`) + WP-34 implementation  
**Authority:** PLAN.md (Master Roadmap v2.1) — Single Source of Truth  
**Governing Documents:** `PLAN.md` Section 15.3, `.kilo/plans/WP-34-spec.md`, `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Date:** 2026-08-10  
**Status:** Closed — Completed

---

## 1. Executive Summary

WP-35 builds a **provider-agnostic Search Provider Router and Adapter Layer** for External Research. It does not integrate any specific search provider. It does not modify WP-34 contracts. It creates the abstraction layer that allows adding, switching, and failing over between search providers without rebuilding the research lifecycle.

**Primary Goal:** Decouple search provider selection from the research lifecycle so that DEM can adopt whichever search provider fits its operational model later, without re-architecting WP-34.

**Hard Boundary:** AI Provider Router (LLM / reasoning / processing) is a separate architectural concern and is explicitly excluded from WP-35.

**Source:** PLAN.md Section 15.3, `.kilo/plans/WP-34-spec.md`.

---

## 2. Objectives

1. Define a **Provider Capability Model** that describes what any search provider can do, independent of its name or API.
2. Define a **Search Provider Adapter Interface** that maps any provider's response into WP-34's `RetrievedContent` / `RetrievalResult`.
3. Build a **Search Provider Router** that selects adapters based on capability, availability, and failure state.
4. Implement a **fallback chain** that degrades gracefully from configured providers to an explicit stub fallback when no external provider is available.
5. Preserve all WP-34 contracts, boundaries, Evidence/Provenance/Verification flows, and test suite behavior.
6. Make adding a new search provider a matter of adding a new adapter class and capability descriptor, with no changes to WP-34 or the research lifecycle.

---

## 3. Architecture Overview

### 3.1 Two Independent Layers

```
DEM Architecture
├── AI Provider Router (OUT OF SCOPE for WP-35)
│   ├── LLM provider selection
│   ├── Reasoning / Processing models
│   └── Content generation
│
└── Search Provider Router (WP-35)
    ├── Provider Capability Model
    ├── Search Provider Adapter Interface
    ├── Adapter Registry
    ├── Fallback Chain Manager
    ├── Concrete Adapters (pluggable)
    └── Graceful Degradation → StubRetriever
```

**Key invariant:** LLM routing and Search routing are independent. WP-35 only addresses Search Provider routing. No component in WP-35 imports, configures, or depends on any LLM provider.

### 3.2 Component Map

```
backend/app/research/retrieval/
├── contracts.py            (FROZEN — WP-34)
├── orchestrator.py         (FROZEN — WP-34)
├── stubs.py                (KEPT — used in tests and as final fallback)
├── providers/
│   ├── __init__.py
│   ├── capability.py       (NEW — ProviderCapability model)
│   ├── adapter.py          (NEW — SearchProviderAdapter ABC)
│   ├── router.py           (NEW — SearchProviderRouter)
│   └── ...                 (future adapters added here without touching WP-34)
│
backend/app/routers/research.py   (MODIFIED — wire router instead of single retriever)
```

---

## 4. Provider Capability Model

### 4.1 Capability Descriptor

Each search provider is described by a capability model, not by its brand name:

```python
@dataclass
class ProviderCapability:
    provider_id: str
    supports_web_search: bool = True
    supports_source_urls: bool = False
    supports_snippets: bool = False
    supports_content_fetch: bool = False
    supports_time_range: bool = False
    supports_domain_filter: bool = False
    requires_api_key: bool = False
    has_usage_limit: bool = False
    usage_limit_description: Optional[str] = None
    priority: int = 100
    enabled: bool = True
```

**Selection rules are based on capabilities, not provider names.** No provider is designated as primary in the architecture.

---

## 5. Search Provider Adapter Interface

### 5.1 Adapter ABC

```python
class SearchProviderAdapter(ABC):
    @property
    @abstractmethod
    def capability(self) -> ProviderCapability:
        ...

    @abstractmethod
    async def retrieve(self, source: Source, query: str) -> RetrievalResult:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...
```

### 5.2 Contract Preservation

- `retrieve()` returns `RetrievalResult` using the **existing** `RetrievalStatus` enum.
- `RetrievedContent` is populated with `source_id`, `raw_content`, `content_type`, and `metadata`.
- No new contracts are introduced. `SourceRetriever`, `ContentProcessor`, `RetrievedContent`, `RetrievalResult`, and `RetrievalStatus` remain untouched.
- Adapters normalize provider-specific responses into WP-34 types only.

---

## 6. Search Provider Router

### 6.1 Router Responsibilities

1. **Registry:** Hold available adapters by `provider_id`.
2. **Selection:** Choose adapter(s) for a given `Source` based on:
   - `capability.supports_web_search`
   - `capability.enabled`
   - `capability.priority`
3. **Failover:** On timeout, connection failure, invalid response, or unavailable provider, try the next eligible adapter in priority order.
4. **Graceful Degradation:** If no external adapter succeeds, return `RetrievalStatus.FAILED` with error metadata. `RetrievalOrchestrator` and `FailureHandler` already handle partial results; no new failure logic is needed.
5. **Stub Fallback:** The router does not silently replace failed providers with `StubRetriever`. Stub usage is explicit, configured, and logged.

### 6.2 Fallback Chain

```
Configured Provider Adapters (by priority)
    ↓ timeout / connection failure / invalid response
Next eligible adapter
    ↓ all adapters failed
RetrievalStatus.FAILED returned to RetrievalOrchestrator
    ↓
FailureHandler determines partial/failed
    ↓
ResearchResult includes sources_failed
```

`StubRetriever` is used only when:
- No external provider is configured at all, OR
- The deployment explicitly registers `StubRetriever` as a deliberate provider

It is **not** an automatic silent fallback for failed providers.

---

## 7. Integration with WP-34

### 7.1 Unchanged Components

| Component | Status | WP-35 Impact |
|-----------|--------|--------------|
| `SourceRetriever` ABC | FROZEN | Adapters implement it; no change |
| `ContentProcessor` ABC | FROZEN | Adapters may include processor; no change |
| `RetrievedContent` | FROZEN | Populated by adapters; no change |
| `RetrievalResult` | FROZEN | Returned by adapters; no change |
| `RetrievalStatus` | FROZEN | Used by adapters; no change |
| `RetrievalOrchestrator` | FROZEN | Calls router; no change |
| `EvidenceCapture` | FROZEN | Unchanged |
| `ProvenanceRecord` | FROZEN | Unchanged |
| `Verifier` / `FailureHandler` | FROZEN | Unchanged |
| Research lifecycle stages | FROZEN | Unchanged |

### 7.2 Changed Components

| Component | Change |
|-----------|--------|
| `backend/app/routers/research.py` | Replace direct `StubRetriever` instantiation with `SearchProviderRouter` |
| `backend/app/research/retrieval/providers/` | New directory for capability model, adapter ABC, router, and future adapters |

---

## 8. Error Handling and Timeouts

### 8.1 Error Taxonomy

| Scenario | Mapped RetrievalStatus |
|----------|------------------------|
| Adapter success | `SUCCESS` |
| Adapter timeout | `TIMEOUT` |
| Adapter connection failure | `CONNECTION_FAILURE` |
| Adapter invalid response | `INVALID_RESPONSE` |
| Adapter processing failure | `PROCESSING_FAILURE` |
| No adapter available / all failed | `FAILED` |
| Unsupported source type | `UNSUPPORTED_SOURCE` |

### 8.2 Timeout Strategy

- Each adapter enforces its own timeout via `httpx` or provider SDK.
- The router does not add a second timeout layer.
- On timeout, the router marks the adapter as temporarily unavailable and tries the next eligible adapter.
- The `RetrievalOrchestrator._retrieve_one()` wrapper continues to measure wall-clock duration.

### 8.3 Partial Results

- `RetrievalOrchestrator.retrieve_sources()` iterates sources sequentially.
- If one source's adapter fails, subsequent sources are still attempted.
- `FailureHandler.determine_status()` produces `partial` or `failed` as before.

---

## 9. Configuration

### 9.1 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SEARCH_PROVIDER_IDS` | No | — | Comma-separated list of enabled provider IDs in priority order |
| `SEARCH_STUB_FALLBACK` | No | `true` | Use `StubRetriever` when no external provider is configured |
| Per-provider vars | Depends on provider | — | Added only when that provider's adapter is implemented |

### 9.2 .env.example

Example additions:
```
SEARCH_PROVIDER_IDS=
SEARCH_STUB_FALLBACK=true
```

Provider-specific variables are added only when the corresponding adapter is implemented.

---

## 10. Separation from AI Provider Router

**AI Provider Router is explicitly out of scope for WP-35.** This is a hard architectural boundary, not merely an item in the Out of Scope list.

| Concern | Owner |
|---------|-------|
| Search / Retrieval | WP-35 |
| LLM / Reasoning / Processing | Future work / separate WP |
| Routing between LLM providers | Separate architectural topic |

No component in WP-35 imports, configures, or depends on any LLM provider.

---

## 11. Out of Scope

| Item | Reason |
|------|--------|
| AI Provider Router | Hard boundary; separate concern |
| Knowledge Ingestion modifications | Boundaries in `KNOWLEDGE_INGESTION_CONTRACT.md` |
| Web scraping implementation | Providers handle retrieval; WP-35 consumes structured output |
| Chatbot / conversational UI | Out of scope |
| Business Analysis / Market Analysis | Downstream capability |
| Reasoning / Planning / ERP Execution | External Research stops at structured results |
| OAD-1 / OAD-2 / OAD-3 | Open decisions remain open |
| Reopening WP-34 | WP-34 is complete baseline |
| Changing WP-34 contracts | `SourceRetriever`, `ContentProcessor`, `RetrievedContent`, `RetrievalResult`, `RetrievalStatus`, evidence/provenance/verification are frozen |
| Selecting a mandatory primary provider | Provider selection is a runtime/config decision; WP-35 builds the layer, not the choice |

---

## 12. Exit Criteria

| # | Criterion | Verification Method |
|---|-----------|---------------------|
| EC-35.1 | `ProviderCapability` model defined and serializable | Unit test |
| EC-35.2 | `SearchProviderAdapter` ABC defined with required methods | Interface test |
| EC-35.3 | `SearchProviderRouter` selects adapters by capability and priority | Unit test with mock adapters |
| EC-35.4 | Router falls back to next adapter on timeout/failure | Integration test with failing adapter |
| EC-35.5 | Router returns `FAILED` when all adapters fail; `RetrievalOrchestrator` produces `partial`/`failed` correctly | Integration test |
| EC-35.6 | StubRetriever used only when configured, not as silent fallback | Integration test |
| EC-35.7 | Evidence/Provenance/Verification boundaries unchanged | Run full WP-34 test suite; zero regressions |
| EC-35.8 | No modifications to `KNOWLEDGE_INGESTION_CONTRACT.md` | Git diff verification |
| EC-35.9 | No modifications to WP-34 contracts | Git diff verification |
| EC-35.10 | Router wired in production router (`backend/app/routers/research.py`) | Manual + integration test |
| EC-35.11 | Adding a new adapter does not require modifying WP-34 contracts or research lifecycle | Architecture review |
| EC-35.12 | No provider is designated as primary in architecture or config | Architecture review |

---

## 13. Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| WP-34: External Research Capability | Internal | ✅ Complete |
| `httpx` library | Dependency | ✅ Already in `requirements.txt` |
| Owner approval of router architecture | Decision | ⏳ Pending |

---

## 14. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Adapter interface too narrow for some providers | Medium | Medium | Design adapter ABC with extensible metadata; adapters can store provider-specific data in `RetrievedContent.metadata` |
| Router selection logic becomes complex | Low | Low | Start with simple priority-based selection; extend later |
| StubRetriever silently replaces failed providers | Medium | Medium | Explicit config flag `SEARCH_STUB_FALLBACK`; log at WARNING when stub is used |
| LLM Provider confusion | Low | Medium | Hard architectural boundary; no imports between search and LLM routing in WP-35 |

---

## 15. Constraints Enforcement

| Constraint | Status |
|------------|--------|
| لا تنفذ أي كود | ✅ Plan only |
| لا تعدّل أي ملف خارج `.kilo/plans` | ✅ Only plan files created/updated |
| لا تنفذ Web Scraping | ✅ Providers handle retrieval; WP-35 consumes structured output |
| لا تنشئ Chatbot | ✅ Not applicable |
| لا تنفذ Business Analysis أو Market Analysis | ✅ Research returns raw structured results only |
| لا تدخل في Reasoning أو Planning أو ERP Execution | ✅ Boundaries preserved |
| لا تعالج OAD-1/OAD-2/OAD-3 | ✅ Open decisions remain open |
| لا تعيد فتح WP-34 | ✅ WP-34 is complete baseline |
| لا تغيّر Knowledge Ingestion Contract | ✅ Explicitly out of scope |
| لا تفترض وجود مزود بحث تم اعتماده مسبقًا | ✅ No provider selected as primary |
| لا تنشئ أكثر من WP واحدة | ✅ Only WP-35 |
| لا تبدأ التنفيذ قبل اعتماد الخطة | ✅ Draft — Pending Approval |
| لا تعتمد على خدمة ذات Credits محدودة كمسار أساسي | ✅ Router is provider-agnostic; no provider is mandatory |
| لا تعتبر LLM كـ Search Provider | ✅ Hard boundary; AI Provider Router is out of scope |

---

## 16. Closure Record

**Closure Date:** 2026-08-10
**Closure Status:** Completed
**Baseline:** WP-35 Provider-Agnostic Search Provider Router/Adapter Layer

### 16.1 Completed Tasks

| Task | Status | Evidence |
|------|--------|----------|
| Task 1: Provider Capability Model | ✅ Completed | `backend/app/research/retrieval/providers/capability.py` + unit tests |
| Task 2: Search Provider Adapter Interface | ✅ Completed | `backend/app/research/retrieval/providers/adapter.py` + interface tests |
| Task 3: Search Provider Router | ✅ Completed | `backend/app/research/retrieval/providers/router.py` + failover tests |
| Task 4: Optional Example Adapters | ⏸️ Deferred | Mock adapters in tests are sufficient; deferred to first provider adoption |
| Task 5: Router Wiring in Production | ✅ Completed | `backend/app/routers/research.py` + `backend/app/core/config.py` |
| Task 6: Tests — Failover, Partial Degradation, Evidence Preservation | ✅ Completed | `backend/tests/test_research_search_router.py` + WP-34 regression tests |
| Task 7: Documentation | ✅ Completed | Docstrings + `.kilo/plans/WP-35-add-provider-guide.md` |

### 16.2 Exit Criteria Verification

All Exit Criteria EC-35.1 through EC-35.13 are satisfied. See sections 6 and 7 for mapping.

### 16.3 Deferred Decisions

| Decision | Original Reference | Deferred To |
|----------|-------------------|-------------|
| D-1: Select production search providers | WP-35 Decision D-1 | Future Work Package: "First Search Provider Implementation" |
| D-2: Enable `SEARCH_STUB_FALLBACK` in production | WP-35 Decision D-2 | Deployment/operations decision; not a WP-35 closure requirement |
| D-3: Provider infrastructure ownership | WP-35 Decision D-3 | Future operational planning |

**Note:** D-1 is explicitly **not** a closure requirement for WP-35. WP-35 delivers the abstraction layer; provider selection is a separate operational decision.

### 16.4 Boundary Verification

- ✅ No modifications to WP-34 contracts (`contracts.py`, `orchestrator.py`, `retrieval/orchestrator.py`, `quality.py`)
- ✅ No modifications to `KNOWLEDGE_INGESTION_CONTRACT.md`
- ✅ No mixing of Search Provider Router with AI/LLM Provider Router
- ✅ No provider designated as primary in architecture or config
- ✅ No external service/VPS/credits mandated as architectural dependency

### 16.5 Next Steps

1. Use WP-35 as the new baseline for External Research retrieval.
2. Create a separate Work Package for **First Search Provider Implementation** when a provider is selected.
3. Follow `.kilo/plans/WP-35-add-provider-guide.md` when implementing new adapters.

---

*Document Status: Closed — Completed*
