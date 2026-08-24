# WP-35 Implementation Plan: External Research Provider Adapter & Routing Layer

**Work Package:** WP-35 â€” External Research Provider Adapter & Routing Layer  
**Status:** Closed â€” Completed  
**Date:** 2026-08-10  
**Authority:** `PLAN.md` + `.kilo/plans/WP-35-spec.md` + `.kilo/plans/WP-34-spec.md` + `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Path:** `\.kilo/plans/archive/WP-35-implementation-plan\.md`

---

## 1. ط§ظ„ط؛ط±ط¶

ط¨ظ†ط§ط، ط·ط¨ظ‚ط© طھظˆط¬ظٹظ‡/طھظƒظٹظ‘ظپ ظ„ظ„ط¨ط­ط« ط§ظ„ط®ط§ط±ط¬ظٹ طھط³ظ…ط­ ط¨ط¥ط¶ط§ظپط© ظˆطھط¨ط¯ظٹظ„ ظ…ط²ظˆط¯ط§طھ ط§ظ„ط¨ط­ط« ط¯ظˆظ† ط¥ط¹ط§ط¯ط© ط¨ظ†ط§ط، ظ…ط¹ظ…ط§ط±ظٹط© WP-34طŒ ظ…ط¹ ط§ظ„ط­ظپط§ط¸ ط¹ظ„ظ‰ ط®ط· ط§ظ„ط¨ط­ط« ظƒط§ظ…ظ„ط§ظ‹: Search â†’ Sources â†’ Retrieval â†’ Evidence â†’ Provenance â†’ Verification â†’ Result.

---

## 2. ظ†ط·ط§ظ‚ ط§ظ„ظ…ظ‡ط§ظ… ط§ظ„طھظ†ظپظٹط°ظٹط©

### Task 1: Provider Capability Model
**ط§ظ„ظ‡ط¯ظپ:** طھط¹ط±ظٹظپ ظ†ظ…ظˆط°ط¬ ظˆطµظپ ظ‚ط§ط¯ط±ط§طھ ط£ظٹ ظ…ط²ظˆط¯ ط¨ط­ط«طŒ ظ…ط³طھظ‚ظ„ ط¹ظ† ط§ط³ظ… ط§ظ„ظ…ط²ظˆط¯ ط£ظˆ ظˆط§ط¬ظ‡طھظ‡.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- `backend/app/research/retrieval/providers/capability.py`
- `ProviderCapability` dataclass/model
- ط§ط®طھط¨ط§ط±ط§طھ serialization ظˆظ‚ط¯ط±ط§طھ ط§ظپطھط±ط§ط¶ظٹط©

**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- `ProviderCapability` ظٹطµظپ: `supports_web_search`, `supports_source_urls`, `supports_snippets`, `requires_api_key`, `has_usage_limit`, `priority`, `enabled`
- ظ„ط§ ظٹط­طھظˆظٹ ط¹ظ„ظ‰ ط£ظٹ ط§ط³ظ… ظ…ط²ظˆط¯ ظ…ط­ط¯ط¯ ط£ظˆ ط¨ظٹط§ظ†ط§طھ ط§ط¹طھظ…ط§ط¯
- ظ‚ط§ط¨ظ„ ظ„ظ„طھظˆط³ط¹ط© ط¨ظ…ط¬ط±ط¯ ط¥ط¶ط§ظپط© ط­ظ‚ظˆظ„ ط¬ط¯ظٹط¯ط©
- ظ„ط§ ظٹط´ظٹط± ط¥ظ„ظ‰ ط£ظٹ ظ…ط²ظˆط¯ ظپط¹ظ„ظٹ ظƒظ€ primary ط£ظˆ ظ…ط«ط§ظ„ ظ…ظ„ط²ظ…

---

### Task 2: Search Provider Adapter Interface
**ط§ظ„ظ‡ط¯ظپ:** طھط¹ط±ظٹظپ ط§ظ„ظˆط§ط¬ظ‡ط© ط§ظ„طھظٹ ط³ظٹظ†ظپط°ظ‡ط§ ظƒظ„ ظ…ط²ظˆط¯.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- `backend/app/research/retrieval/providers/adapter.py`
- `SearchProviderAdapter` ABC ظ…ط¹: `capability`, `retrieve(source, query)`, `health_check()`

**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- `retrieve()` طھط±ط¬ط¹ `RetrievalResult` ط¨ط§ط³طھط®ط¯ط§ظ… `RetrievalStatus` ط§ظ„ط­ط§ظ„ظٹ ظ…ظ† WP-34
- ظ„ط§ طھظڈط¶ط§ظپ ط¹ظ‚ظˆط¯ ط¬ط¯ظٹط¯ط©
- `RetrievedContent` ظˆ `RetrievalResult` remains ط¨ط¯ظˆظ† طھط؛ظٹظٹط±
- ظ…ط«ط§ظ„ ظˆط§ط­ط¯ mock adapter ظٹط«ط¨طھ ط§ظ„ظˆط§ط¬ظ‡ط© ظپظ‚ط·

---

### Task 3: Search Provider Router
**ط§ظ„ظ‡ط¯ظپ:** ط¨ظ†ط§ط،/router ظٹط®طھط§ط± ط§ظ„طھظƒظٹظپ ط§ظ„ظ…ظ†ط§ط³ط¨ ط¨ظ†ط§ط،ظ‹ ط¹ظ„ظ‰ ط§ظ„ظ‚ط¯ط±ط§طھ ظˆط§ظ„ط­ط§ظ„ط©.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- `backend/app/research/retrieval/providers/router.py`
- `SearchProviderRouter` ظ…ط¹: `register_adapter()`, `unregister_adapter()`, `retrieve_with_fallback(source, query)`

**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ظٹط®طھط§ط±Adapter ط¨ظ†ط§ط،ظ‹ ط¹ظ„ظ‰ `capability.supports_web_search` ظˆ `capability.enabled` ظˆ `capability.priority`
- ط¹ظ„ظ‰ timeout/failure/invalid response: ظٹظ†طھظ‚ظ„ ظ„ظ„ظ€Adapter ط§ظ„طھط§ظ„ظٹ ط¨ط§ظ„ط£ظˆظ„ظˆظٹط©
- ط¥ط°ط§ ظپط´ظ„ ظƒظ„ ط§ظ„ظ€Adapters: ظٹط±ط¬ط¹ `RetrievalStatus.FAILED`
- ظ„ط§ ظٹط³طھط®ط¯ظ… `StubRetriever` ظƒط§ط­طھظٹط§ط· طھظ„ظ‚ط§ط¦ظٹ طµط§ظ…طھ
- ظٹظڈط³ط¬ظ„ ظƒظ„ طھط¨ط¯ظٹظ„/ظپط´ظ„ ظپظٹ ط§ظ„ط³ط¬ظ„ط§طھ

---

### Task 4: Optional Example Adapters
**ط§ظ„ظ‡ط¯ظپ:** طھظˆظپظٹط± ط£ظ…ط«ظ„ط© ط§ط®طھظٹط§ط±ظٹط© ظٹط«ط¨طھط§ظ† ظ‚ط§ط¨ظ„ظٹط© طھط´ط؛ظٹظ„ ط§ظ„ظˆط§ط¬ظ‡ط© ظ…ط¹ ظ…ط²ظˆط¯ط§طھ ظ…ط®طھظ„ظپط©.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- `backend/app/research/retrieval/providers/` (ظ…ظ„ظپط§طھ ط§ط®طھظٹط§ط±ظٹط©)

**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ظƒظ„ ظ…ط«ط§ظ„ ظٹط­ظˆظ„ ط§ط³طھط¬ط§ط¨ط© ط§ظ„ظ…ط²ظˆط¯ ط¥ظ„ظ‰ `RetrievedContent` ظˆ `RetrievalResult`
- ظƒظ„ ظ…ط«ط§ظ„ ظٹط·ط§ط¨ظ‚ ط­ط§ظ„ط§طھ ط§ظ„ط®ط·ط£ ط¥ظ„ظ‰ `RetrievalStatus`
- ط§ظ„ط£ظ…ط«ظ„ط© **ظ„ط§ طھظڈط¹طھط¨ط± ط§ظ„طھط²ط§ظ…ظ‹ط§ ط¨ط§ط®طھظٹط§ط± ظ…ط²ظˆط¯ ظ…ط¹ظٹظ†**
- ظٹظ…ظƒظ† طھط´ط؛ظٹظ„ ط§ط®طھط¨ط§ط±ط§طھظ‡ط§ ط¨ط¯ظˆظ† ط®ط¯ظ…ط§طھ ط®ط§ط±ط¬ظٹط© ط­ظ‚ظٹظ‚ظٹط©
- ظ„ط§ ظٹظڈط´طھط±ط· طھظ†ظپظٹط° ط£ظٹ ظ…ط«ط§ظ„ ظ…ط¹ظٹظ† ظ„ط¥ظƒظ…ط§ظ„ WP-35

---

### Task 5: Router Wiring in Production
**ط§ظ„ظ‡ط¯ظپ:** ط±ط¨ط· ط§ظ„ظ€Router ظپظٹ ظ…ط³ط§ط± ط§ظ„ط¨ط­ط« ط§ظ„ط­ط§ظ„ظٹ.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- طھط¹ط¯ظٹظ„ `backend/app/routers/research.py`

**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ظٹط³طھط¨ط¯ظ„ ط¥ظ†ط´ط§ط، `StubRetriever` ط§ظ„ظ…ط¨ط§ط´ط± ط¨ط¥ظ†ط´ط§ط، `SearchProviderRouter`
- ط¹ظ†ط¯ ط¹ط¯ظ… ظˆط¬ظˆط¯ ط£ظٹ adapter ظ…ط³ط¬ظ„: ظٹط³ط¬ظ„ طھط­ط°ظٹط±
- `StubRetriever` ظٹظڈط³طھط®ط¯ظ… ظپظ‚ط· ط¥ط°ط§ ظƒط§ظ† `SEARCH_STUB_FALLBACK=true` ط¨ط´ظƒظ„ طµط±ظٹط­
- ظ„ط§ ظٹطھط·ظ„ط¨ طھط¹ط¯ظٹظ„ `ResearchOrchestrator` ط£ظˆ `RetrievalOrchestrator` ط£ظˆ ط£ظٹ ظ…ط±ط­ظ„ط© ط¨ط­ط«
- ط¬ظ…ظٹط¹ ط§ط®طھط¨ط§ط±ط§طھ WP-34 ط§ظ„ط­ط§ظ„ظٹط© (103 ط§ط®طھط¨ط§ط±) طھط¸ظ„ ط³ظ„ظٹظ…ط©

---

### Task 6: Tests â€” Failover, Partial Degradation, Evidence Preservation
**ط§ظ„ظ‡ط¯ظپ:** ط§ظ„طھط­ظ‚ظ‚ ظ…ظ† ط³ظ„ظˆظƒ ط§ظ„ظ€Router ظˆط§ظ„ظ€Adapters.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- `backend/tests/test_research_search_router.py` (ط¬ط¯ظٹط¯)

**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ط§ط®طھط¨ط§ط±: Router ظٹط®طھط§ط±Adapter ط­ط³ط¨ ط§ظ„ط£ظˆظ„ظˆظٹط© ظˆط§ظ„ظ‚ط¯ط±ط§طھ
- ط§ط®طھط¨ط§ط±: ط¹ظ†ط¯ ظپط´ظ„AdapterطŒ ظٹظ†طھظ‚ظ„ ظ„ظ„طھط§ظ„ظٹ
- ط§ط®طھط¨ط§ط±: ط¹ظ†ط¯ ظپط´ظ„ ظƒظ„ ط§ظ„ظ€AdaptersطŒ ظٹط±ط¬ط¹ `FAILED`
- ط§ط®طھط¨ط§ط±: `EvidenceCaptureStage` ظٹظ„طھظ‚ط· ط§ظ„ط£ط¯ظ„ط© ظ…ظ† ط§ظ„ظ…طµط¯ط± ط§ظ„ظ†ط§ط¬ط­ ظپظ‚ط·
- ط§ط®طھط¨ط§ط±: `ProvenanceRecord` ظٹط­طھظˆظٹ ط¹ظ„ظ‰ `source_id` ظˆ `source_reference` ظˆ `retrieval_timestamp` طµط­ظٹط­ظٹظ†
- ط§ط®طھط¨ط§ط±: `VerificationStage` ظٹطھط­ظ‚ظ‚ ظ…ظ† ظˆط¬ظˆط¯ `source_id` ظپظٹ ط§ظ„ط£ط¯ظ„ط©
- ط§ط®طھط¨ط§ط±: ط³ظ„ظˆظƒ `StubRetriever` ظƒط§ط­طھظٹط§ط· طµط±ظٹط­ ظپظ‚ط·
- ط§ط®طھط¨ط§ط±: ط¹ط¯ظ… ط®ظ„ط· Search Provider ظ…ط¹ LLM Provider (ظ„ط§ imports ظ„ظ€ LLM routing)

---

### Task 7: Documentation
**ط§ظ„ظ‡ط¯ظپ:** طھظˆط«ظٹظ‚ ظƒظٹظپظٹط© ط¥ط¶ط§ظپط© ظ…ط²ظˆط¯ ط¬ط¯ظٹط¯.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- docstrings ظپظٹ `capability.py`, `adapter.py`, `router.py`
- ط¯ظ„ظٹظ„ ظ‚طµظٹط±: "How to add a new Search Provider"

**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ط®ط·ظˆط§طھ ظˆط§ط¶ط­ط©: ط£ظ†ط´ط¦ adapter â†’ ط¹ط±ظ‘ظپ capability â†’ ط³ط¬ظ‘ظ„ظ‡ ظپظٹ Router
- ظ„ط§ طھظˆط¬ط¯ ط£ط³ط±ط§ط± ظ…ظƒط´ظˆظپط©
- ظ„ط§ ط§ط®طھظٹط§ط± ظ…ط²ظˆط¯ ظ†ظ‡ط§ط¦ظٹ ظ…ظˆطµظ‰ ط¨ظ‡

---

## 3. طھط±طھظٹط¨ ط§ظ„طھظ†ظپظٹط°

```
Task 1 â†’ Task 2 â†’ Task 3 â†’ Task 4 â†’ Task 5 â†’ Task 6 â†’ Task 7
```

ظƒظ„ ظ…ظ‡ظ…ط© طھط¹طھظ…ط¯ ط¹ظ„ظ‰ ط³ط§ط¨ظ‚طھظ‡ط§. Task 4 ط§ط®طھظٹط§ط±ظٹط© ظˆظٹظ…ظƒظ† طھظ†ظپظٹط°ظ‡ط§ ط¨ط§ظ„طھظˆط§ط²ظٹ ظ…ط¹ Task 5.

---

## 4. ظ†ظ‚ط§ط· ط§ظ„طھط­ظ‚ظ‚ (Validation Gates)

| Gate | ط§ظ„ظ…ظ‡ط§ظ… ط§ظ„ظ…ظڈطھط­ظ‚ظ‚ ظ…ظ†ظ‡ط§ | ط§ظ„ط´ط±ط· ظ„ظ„ظ…طھط§ط¨ط¹ط© |
|------|---------------------|----------------|
| Gate 1 | Task 1 | `ProviderCapability` model working ظ…ط¹ ظپط­ظˆطµط§طھ serialization |
| Gate 2 | Task 1 + Task 2 | `SearchProviderAdapter` ABC ط«ط§ط¨طھ ظ…ط¹ mock adapter |
| Gate 3 | Task 3 | `SearchProviderRouter` ظٹط®طھط§ط± ظˆظٹظ†طھظ‚ظ„ ط¨ظٹظ† mock adapters |
| Gate 4 | Task 4 | ظ…ط«ط§ظ„ ط§ط®طھظٹط§ط±ظٹ ظˆط§ط­ط¯ ط¹ظ„ظ‰ ط§ظ„ط£ظ‚ظ„ ظٹط¹ظ…ظ„ ظ…ط¹ ط§ط³طھط¬ط§ط¨ط© ظˆظ‡ظ…ظٹط© |
| Gate 5 | Task 5 | Router ظ…ط±ط¨ظˆط· ظپظٹ `research.py` ظ…ط¹ ط³ظ„ظˆظƒ طµط­ظٹط­ ط¨ط¯ظˆظ†/ظ…ط¹ adapters |
| Gate 6 | Task 6 | ط§ط®طھط¨ط§ط±ط§طھ failover ظˆpartial degradation ظˆevidence preservation طھظ†ط¬ط­ |
| Gate 7 | Task 7 | documentation ظƒط§ظ…ظ„ط© + WP-34 tests regression (103) طھظ†ط¬ط­ |

---

## 5. Deliverables ط§ظ„ظ†ظ‡ط§ط¦ظٹط©

| # | Deliverable | ط§ظ„ظ…ظ‡ظ…ط© ط§ظ„ظ…ط³ط¤ظˆظ„ط© | ط§ظ„ظ…ظ„ظپ |
|---|-------------|-----------------|-------|
| 1 | Provider Capability Model | Task 1 | `backend/app/research/retrieval/providers/capability.py` |
| 2 | Search Provider Adapter Interface | Task 2 | `backend/app/research/retrieval/providers/adapter.py` |
| 3 | Search Provider Router | Task 3 | `backend/app/research/retrieval/providers/router.py` |
| 4 | Example Adapters (optional) | Task 4 | `backend/app/research/retrieval/providers/*.py` (ط§ط®طھظٹط§ط±ظٹ) |
| 5 | Router wiring | Task 5 | `backend/app/routers/research.py` (طھط¹ط¯ظٹظ„) |
| 6 | Failover & degradation tests | Task 6 | `backend/tests/test_research_search_router.py` |
| 7 | Documentation | Task 7 | docstrings + guide |

---

## 6. Acceptance Criteria Coverage

| AC | ط§ظ„ظ…ظ‡ظ…ط© ط§ظ„ظ…ط³ط¤ظˆظ„ط© |
|----|-----------------|
| AC-35.1: `ProviderCapability` model ظٹط¹ظ…ظ„ | Task 1 |
| AC-35.2: `SearchProviderAdapter` ABC ط«ط§ط¨طھ | Task 2 |
| AC-35.3: Router ظٹط®طھط§ط±Adapter ط­ط³ط¨ ط§ظ„ظ‚ط¯ط±ط§طھ ظˆط§ظ„ط£ظˆظ„ظˆظٹط© | Task 3 |
| AC-35.4: Failover ط¨ظٹظ† Adapters ط¹ظ†ط¯ timeout/failure | Task 3 + Task 6 |
| AC-35.5: `StubRetriever` ظƒط§ط­طھظٹط§ط· طµط±ظٹط­ ظپظ‚ط· | Task 5 |
| AC-35.6: Evidence/Provenance ظ…ط­ظپظˆط¸ط© ط¯ظˆظ† طھط¹ط¯ظٹظ„ | Task 6 |
| AC-35.7: Partial results طھط¹ظ…ظ„ | Task 6 |
| AC-35.8: ظ„ط§ ظƒط³ط± ظپظٹ ط§ط®طھط¨ط§ط±ط§طھ WP-34 | Gate 7 |
| AC-35.9: ظ„ط§ ط®ظ„ط· ط¨ظٹظ† Search Provider ظˆ LLM Provider | Task 6 |
| AC-35.10: ط¥ط¶ط§ظپط© ظ…ط²ظˆط¯ ط¬ط¯ظٹط¯ ظ„ط§ ظٹطھط·ظ„ط¨ طھط¹ط¯ظٹظ„ WP-34 | Architecture review + Task 2 design |
| AC-35.11: Provider-Agnostic architecture | Architecture review |

---

## 7. Exit Criteria

| # | Exit Criterion | Verification |
|---|---------------|--------------|
| EC-35.1 | ط¬ظ…ظٹط¹ ط§ظ„ظ…ظ‡ط§ظ… ظ…ظ† 1 ط¥ظ„ظ‰ 7 ظ…ظƒطھظ…ظ„ط© | Git diff + review |
| EC-35.2 | `ProviderCapability` model ظٹط¹ظ…ظ„ | Unit test |
| EC-35.3 | `SearchProviderAdapter` ABC ط«ط§ط¨طھ | Interface test |
| EC-35.4 | `SearchProviderRouter` ظٹط®طھط§ط± ظˆظٹظ†طھظ‚ظ„ ط¨ظٹظ† adapters | Integration test |
| EC-35.5 | ط¹ظ†ط¯ ظپط´ظ„ ظƒظ„ ط§ظ„ظ€Adapters: `FAILED` + partial handling | Integration test |
| EC-35.6 | `StubRetriever` ظƒط§ط­طھظٹط§ط· طµط±ظٹط­ ظپظ‚ط· | Integration test |
| EC-35.7 | Evidence/Provenance/Verification boundaries ظ…ط­ظپظˆط¸ط© | WP-34 test suite (103 tests) طھظ†ط¬ط­ |
| EC-35.8 | ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ `KNOWLEDGE_INGESTION_CONTRACT.md` | Git diff verification |
| EC-35.9 | ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ ط¹ظ‚ظˆط¯ WP-34 | Git diff verification |
| EC-35.10 | Router ظ…ط±ط¨ظˆط· ظپظٹ `research.py` | Manual + integration test |
| EC-35.11 | ط¥ط¶ط§ظپط© adapter ط¬ط¯ظٹط¯ ظ„ط§ ظٹطھط·ظ„ط¨ طھط¹ط¯ظٹظ„ WP-34 | Architecture review |
| EC-35.12 | ظ„ط§ ظ…ط²ظˆط¯ ظ…ط¹ظٹظ† ظ…ظڈط¹ظ„ظژظ‘ظ† ظƒظ€ primary ظپظٹ ط§ظ„ظ…ط¹ظ…ط§ط±ظٹط© ط£ظˆ ط§ظ„ط¥ط¹ط¯ط§ط¯ط§طھ | Architecture review |
| EC-35.13 | `.env.example` ظ…ط­ط¯ظ‘ط« ط¨ظ…طھط؛ظٹط±ط§طھ Router ظپظ‚ط· | Manual verification |

---

## 8. Open Architectural Decisions (Inherited from WP-34)

| # | Decision | Impact | Status |
|---|----------|--------|--------|
| OAD-1 | Source trust scoring algorithm | طھط±طھظٹط¨ ط§ظ„ظ†طھط§ط¦ط¬ ظˆط§ظ„ط«ظ‚ط© | Future work â€” NOT addressed |
| OAD-2 | Duplicate detection strategy | طھط¬ظ…ظٹط¹ ط§ظ„ظ†طھط§ط¦ط¬ | Future work â€” NOT addressed |
| OAD-3 | Content validation mechanism | ط¬ظˆط¯ط© ط§ظ„ظ†طھط§ط¦ط¬ | Future work â€” NOT addressed |

**WP-35 does NOT resolve OAD-1, OAD-2, or OAD-3.**

---

## 9. ط§ظ„ظ‚ط±ط§ط±ط§طھ ط§ظ„طھظٹ طھط­طھط§ط¬ ظ…ظˆط§ظپظ‚ط© ط§ظ„ظ…ط§ظ„ظƒ

| # | ط§ظ„ظ‚ط±ط§ط± | ظ„ظ…ط§ط°ط§ |
|---|--------|-------|
| D-1 | ط£ظٹ ظ…ط²ظˆط¯/ظ…ظˆظپط±ط§طھ ط³ظٹطھظ… طھظپط¹ظٹظ„ظ‡ط§ ظپط¹ظ„ظٹظ‹ط§ ظپظٹ ط§ظ„ط¥ظ†طھط§ط¬ | ط§ظ„ط®ط·ط© ظ„ط§ طھط®طھط§ط± ظ…ط²ظˆط¯ظ‹ط§ط› ط§ظ„ظ…ط§ظ„ظƒ ظٹط­ط¯ط¯ ط£ظٹ adapters طھط³ط¬ظژظ‘ظ„ |
| D-2 | ظ…ط§ ط¥ط°ط§ ظƒط§ظ† ط³ظٹطھظ… طھظپط¹ظٹظ„ `SEARCH_STUB_FALLBACK` ظپظٹ ط§ظ„ط¥ظ†طھط§ط¬ | ظٹط¤ط«ط± ط¹ظ„ظ‰ ط³ظ„ظˆظƒ ط§ظ„ظ†ط¸ط§ظ… ط¹ظ†ط¯ ط¹ط¯ظ… طھظˆظپط± ظ…ط²ظˆط¯ |
| D-3 | ظ…ط³ط¤ظˆظ„ظٹط© طھط´ط؛ظٹظ„ ظˆطµظٹط§ظ†ط© ط£ظٹ ط¨ظ†ظٹط© طھط­طھظٹط© ظ„ظ„ظ…ط²ظˆط¯ط§طھ ط§ظ„ظ…ط®طھط§ط±ط© | ط®ط§ط±ط¬ ظ†ط·ط§ظ‚ ط§ظ„ط®ط·ط© ط§ظ„ظ‡ظ†ط¯ط³ظٹط© |

---

## 10. Boundaries Verification Checklist

ظ‚ط¨ظ„ ط§ظ„طھظ†ظپظٹط°طŒ طھط£ظƒط¯ ظ…ظ†:

- [ ] ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ `backend/app/research/retrieval/contracts.py`
- [ ] ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ `backend/app/research/evidence/contracts.py`
- [ ] ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ `backend/app/research/quality.py`
- [ ] ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ `backend/app/research/orchestrator.py`
- [ ] ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ `backend/app/research/retrieval/orchestrator.py`
- [ ] ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`
- [ ] ظ„ط§ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ `PLAN.md` ط£ظˆ `CURRENT_STATUS.md` ط£ظˆ `CHANGELOG.md` (ظپظٹ ظ‡ط°ظ‡ ط§ظ„ظ…ط±ط­ظ„ط©)
- [ ] ظ„ط§ imports ط£ظˆ طھط¨ط¹ظٹط§طھ ظ…ظ† `Search Provider Router` ط¥ظ„ظ‰ `AI Provider Router`
- [ ] ظ„ط§ ظ…ط²ظˆط¯ ظ…ط¹ظٹظ† ظ…ظڈط¹ظ„ظژظ‘ظ† ظƒظ€ primary ظپظٹ ط§ظ„ظˆط«ط§ط¦ظ‚ ط£ظˆ ط§ظ„ظƒظˆط¯

---

## 11. Closure Record

**Closure Date:** 2026-08-10
**Closure Status:** Completed
**Baseline:** WP-35 Provider-Agnostic Search Provider Router/Adapter Layer

### 11.1 Completed Tasks

| Task | Status | Evidence |
|------|--------|----------|
| Task 1: Provider Capability Model | âœ… Completed | `backend/app/research/retrieval/providers/capability.py` + unit tests |
| Task 2: Search Provider Adapter Interface | âœ… Completed | `backend/app/research/retrieval/providers/adapter.py` + interface tests |
| Task 3: Search Provider Router | âœ… Completed | `backend/app/research/retrieval/providers/router.py` + failover tests |
| Task 4: Optional Example Adapters | âڈ¸ï¸ڈ Deferred | Mock adapters in tests are sufficient; deferred to first provider adoption |
| Task 5: Router Wiring in Production | âœ… Completed | `backend/app/routers/research.py` + `backend/app/core/config.py` |
| Task 6: Tests â€” Failover, Partial Degradation, Evidence Preservation | âœ… Completed | `backend/tests/test_research_search_router.py` + WP-34 regression tests |
| Task 7: Documentation | âœ… Completed | Docstrings + `.kilo/plans/WP-35-add-provider-guide.md` |

### 11.2 Exit Criteria Verification

All Exit Criteria EC-35.1 through EC-35.13 are satisfied. See sections 6 and 7 for mapping.

### 11.3 Deferred Decisions

| Decision | Original Reference | Deferred To |
|----------|-------------------|-------------|
| D-1: Select production search providers | WP-35 Decision D-1 | Future Work Package: "First Search Provider Implementation" |
| D-2: Enable `SEARCH_STUB_FALLBACK` in production | WP-35 Decision D-2 | Deployment/operations decision; not a WP-35 closure requirement |
| D-3: Provider infrastructure ownership | WP-35 Decision D-3 | Future operational planning |

**Note:** D-1 is explicitly **not** a closure requirement for WP-35. WP-35 delivers the abstraction layer; provider selection is a separate operational decision.

### 11.4 Boundary Verification

- âœ… No modifications to WP-34 contracts (`contracts.py`, `orchestrator.py`, `retrieval/orchestrator.py`, `quality.py`)
- âœ… No modifications to `KNOWLEDGE_INGESTION_CONTRACT.md`
- âœ… No mixing of Search Provider Router with AI/LLM Provider Router
- âœ… No provider designated as primary in architecture or config
- âœ… No external service/VPS/credits mandated as architectural dependency

### 11.5 Next Steps

1. Use WP-35 as the new baseline for External Research retrieval.
2. Create a separate Work Package for **First Search Provider Implementation** when a provider is selected.
3. Follow `.kilo/plans/WP-35-add-provider-guide.md` when implementing new adapters.

---

*Document Status: Closed â€” Completed*

