# WP-34 Implementation Plan: External Research Capability

**Work Package:** WP-34 â€” External Research Capability  
**Status:** Draft â€” Pending Approval  
**Date:** 2026-08-09  
**Authority:** `PLAN.md` + `.kilo/plans/WP-34-spec.md` + `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Path:** `\.kilo/plans/archive/WP-34-implementation-plan\.md`

---

## 1. ط§ظ„ط؛ط±ط¶

طھظ†ظپظٹط° ظ‚ط¯ط±ط© ط§ظ„ط¨ط­ط« ط§ظ„ط®ط§ط±ط¬ظٹ ظƒظƒظٹط§ظ† ظ…ط³طھظ‚ظ„ ط¨ط­ط¯ظˆط¯ ظ…ط¹ظ…ط§ط±ظٹط© ظˆط§ط¶ط­ط©طŒ ظ…ط¹ ط¶ظ…ط§ظ† طھطھط¨ط¹ ط§ظ„ظ…طµط§ط¯ط± ظˆط§ظ„ط£ط¯ظ„ط© ظˆط¹ط¯ظ… ط§ط®طھظ„ط§ط·ظ‡ ط¨ظ€ Knowledge Ingestion ط£ظˆ Reasoning ط£ظˆ Planning.

---

## 2. ظ†ط·ط§ظ‚ ط§ظ„ظ…ظ‡ط§ظ… ط§ظ„طھظ†ظپظٹط°ظٹط©

### Task 1: Research Request Model & API Contract
**ط§ظ„ظ‡ط¯ظپ:** طھط¹ط±ظٹظپ ط§ظ„ظ†ظ…ظˆط°ط¬ ظˆط§ظ„ظˆط§ط¬ظ‡ط© ط§ظ„طھظٹ طھط³طھظ‚ط¨ظ„ ط·ظ„ط¨ط§طھ ط§ظ„ط¨ط­ط«.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- Research Request model
- Research Result model
- Evidence/Source metadata models
**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ظ†ظ…ط§ط°ط¬ ظ…ظ†ط¸ظ…ط© طھط؛ط·ظٹ: ط§ظ„ظ‡ط¯ظپطŒ ط§ظ„ظ†ط·ط§ظ‚طŒ ط§ظ„ط³ظٹط§ظ‚طŒ ط§ظ„ظ‚ظٹظˆط¯
- ظˆط§ط¬ظ‡ط© ظˆط§ط¶ط­ط© ظ„ظ„ط§ط³طھظ‡ظ„ط§ظƒ ظ…ظ† ط§ظ„ط·ط¨ظ‚ط§طھ ط§ظ„ط¹ظ„ظٹط§
- ظ„ط§ طھظˆط¬ط¯ dأ©pendances ط¹ظ„ظ‰ ظ…ط²ظˆط¯ظٹ ط¨ط­ط« ط®ط§ط±ط¬ظٹظٹظ† ظ…ط­ط¯ط¯ظٹظ†

---

### Task 2: Research Lifecycle Orchestration
**ط§ظ„ظ‡ط¯ظپ:** طھظ†ظپظٹط° ط§ظ„ظ€ lifecycle ظ…ظ† ط§ظ„ط·ظ„ط¨ ط¥ظ„ظ‰ ط§ظ„ظ†طھظٹط¬ط© ط§ظ„ظ…ظ†ط¸ظ…ط©.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- Research orchestrator
- Lifecycle stages (Planning â†’ Discovery â†’ Retrieval â†’ Processing â†’ Evidence Capture â†’ Structuring)
**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ظƒظ„ ظ…ط±ط­ظ„ط© ظ…ظ†ظپطµظ„ط© ظˆظ‚ط§ط¨ظ„ط© ظ„ظ„ط§ط®طھط¨ط§ط±
- ظپط´ظ„ ظ…طµط¯ط± ظˆط§ط­ط¯ ظ„ط§ ظٹظˆظ‚ظپ ط§ظ„ط¨ط­ط« ط¨ط§ظ„ظƒط§ظ…ظ„
- ظ†طھط§ط¦ط¬ ط¬ط²ط¦ظٹط© ظ…ظ…ظƒظ†ط©

---

### Task 3: Source Registry & Discovery
**ط§ظ„ظ‡ط¯ظپ:** ط¥ط¯ط§ط±ط© ظ…طµط§ط¯ط± ط®ط§ط±ط¬ظٹط© ظˆط§ظƒطھط´ط§ظپظ‡ط§.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- Source registry interface
- Source discovery mechanism
**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ط§ظ„ظ…طµط§ط¯ط± ظ…ط³ط¬ظ„ط© ط¨ظ…ط¹ط±ظ‘ظپ ظپط±ظٹط¯ ظˆط§ط³ظ… ظˆظ†ظˆط¹
- Discovery ظ‚ط§ط¯ط± ط¹ظ„ظ‰ ط§ط®طھظٹط§ط± ط§ظ„ظ…طµط§ط¯ط± ط§ظ„ظ…ظ†ط§ط³ط¨ط© ط­ط³ط¨ ط§ظ„ظ†ط·ط§ظ‚
- ظ„ط§ ظٹظˆط¬ط¯ ظ…ط²ظˆط¯ ظ…ط­ط¯ط¯ ظ…ط³ط¨ظ‚ظ‹ط§

---

### Task 4: Retrieval & Content Processing
**ط§ظ„ظ‡ط¯ظپ:** ط¬ظ„ط¨ ط§ظ„ظ…ط­طھظˆظ‰ ظ…ظ† ط§ظ„ظ…طµط§ط¯ط± ظˆطھط­ظˆظٹظ„ظ‡.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- Retrieval abstraction
- Content processor
**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ظ…ط¹ط§ظ„ط¬ط© ط§ظ„ط£ط®ط·ط§ط، ظˆط§ظ„ timeouts ظ„ظƒظ„ ظ…طµط¯ط±
- طھط­ظˆظٹظ„ ط§ظ„ظ…ط­طھظˆظ‰ ط§ظ„ط®ط§ظ… ط¥ظ„ظ‰ ظ‡ظٹظƒظ„ ظ…ظ†ط¸ظ…
- طھط³ط¬ظٹظ„ ط­ط§ظ„ط© ط§ظ„ط§ط³طھط±ط¬ط§ط¹ ظ„ظƒظ„ ظ…طµط¯ط±

---

### Task 5: Evidence & Provenance Capture
**ط§ظ„ظ‡ط¯ظپ:** ط§ظ„ط­ظپط§ط¸ ط¹ظ„ظ‰ طھطھط¨ط¹ ط§ظ„ظ…طµط¯ط± ظˆط§ظ„ط£ط¯ظ„ط©.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- Evidence model
- Provenance tracker
**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ظƒظ„ ظ†طھظٹط¬ط© ظ…ط±طھط¨ط·ط© ط¨ظ…طµط¯ط±ظ‡ط§ (ظ…ط¹ط±ظ‘ظپطŒ URL/ظ…ط±ط¬ط¹طŒ ظˆظ‚طھ ط§ظ„ط§ط³طھط±ط¬ط§ط¹)
- ظ‚ط§ط¨ظ„ظٹط© ط§ظ„طھطھط¨ط¹ ظ…ظ† ط§ظ„ظ†طھظٹط¬ط© ط¥ظ„ظ‰ ط§ظ„ظ…طµط¯ط±
- LLM-processed content ظ…ظڈط¹ظ„ظ‘ظ… ظˆظ…ط±طھط¨ط· ط¨ط§ظ„ظ…طµط¯ط±

---

### Task 6: Result Structuring & Output
**ط§ظ„ظ‡ط¯ظپ:** ط¥ط®ط±ط§ط¬ ظ†طھظٹط¬ط© ط¨ط­ط« ظ…ظ†ط¸ظ…ط© ظ„ظ„ط·ط¨ظ‚ط§طھ ط§ظ„ط¹ظ„ظٹط§.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- Research Result structure
- Reasoning layer interface contract
**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ط§ظ„ظ†طھظٹط¬ط© ظ…ظ†ط¸ظ…ط© ظˆظٹظ…ظƒظ† ط§ط³طھظ‡ظ„ط§ظƒظ‡ط§ ظ…ظ† Reasoning
- ط§ظ„ظ†طھظٹط¬ط© ظ„ط§ طھط­طھظˆظٹ ط¹ظ„ظ‰ ظ‚ط±ط§ط±ط§طھ طھط¬ط§ط±ظٹط©
- ط§ظ„ظ†طھظٹط¬ط© ظ„ط§ طھظ‚ظˆظ… ط¨ظ€ ERP mutations

---

### Task 7: Verification, Quality & Failure Handling
**ط§ظ„ظ‡ط¯ظپ:** ط¶ظ…ط§ظ† ط¬ظˆط¯ط© ط§ظ„ظ†طھط§ط¦ط¬ ظˆط§ظ„طھط¹ط§ظ…ظ„ ظ…ط¹ ط§ظ„ط£ط®ط·ط§ط،.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- Quality indicators
- Failure handling strategy
- Open Architectural Decisions log
**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- ظپط´ظ„ ط§ظ„ظ…طµط¯ط± ظ„ط§ ظٹظˆظ‚ظپ ط§ظ„ط¨ط­ط«
- ط§ظ„ظ†طھط§ط¦ط¬ ط§ظ„ط¬ط²ط¦ظٹط© ظ…ظ…ظƒظ†ط© ظ…ط¹ طھط­ط¯ظٹط¯ ط§ظ„ظ…طµط§ط¯ط± ط§ظ„ظپط§ط´ظ„ط©
- ظ‚ط±ط§ط±ط§طھ ظ…ط¹ظ…ط§ط±ظٹط© ظ…ظپطھظˆط­ط© ظ…ظˆط«ظ‚ط© ظ„ظ„طھطµظ…ظٹظ… ط§ظ„ظ„ط§ط­ظ‚

---

### Task 8: Governance & Documentation
**ط§ظ„ظ‡ط¯ظپ:** طھظˆط«ظٹظ‚ ط§ظ„ط­ط¯ظˆط¯ ظˆط§ظ„ط§ط¹طھظ…ط§ط¯ظٹط§طھ ظˆط§ظ„ظ‚ط±ط§ط±ط§طھ.
**ط§ظ„ظ…ط®ط±ط¬ط§طھ:**
- طھط­ط¯ظٹط« PLAN.md Section 15.3
- طھط­ط¯ظٹط« CURRENT_STATUS.md
- Changelog entry
**ظ…ط¹ط§ظٹظٹط± ط§ظ„ط¥ظ†ط¬ط§ط²:**
- PLAN.md ظٹظڈط­ط¯ظ‘ط« ط¨ط¥ط¶ط§ظپط© WP-34
- ظ„ط§ طھظˆط¬ط¯ طھط¹ط§ط±ط¶ط§طھ ظ…ط¹ Knowledge Ingestion Contract
- Exit Criteria ظ…ظˆط«ظ‚ط©

---

## 3. طھط±طھظٹط¨ ط§ظ„طھظ†ظپظٹط°

```
Task 1 â†’ Task 2 â†’ Task 3 â†’ Task 4 â†’ Task 5 â†’ Task 6 â†’ Task 7 â†’ Task 8
```

ظƒظ„ ظ…ظ‡ظ…ط© طھط¹طھظ…ط¯ ط¹ظ„ظ‰ ط¥ظ†ط¬ط§ط² ط§ظ„ظ…ظ‡ظ…ط© ط§ظ„ط³ط§ط¨ظ‚ط©.

---

## 4. ظ†ظ‚ط§ط· ط§ظ„طھط­ظ‚ظ‚ (Validation Gates)

| Gate | ط§ظ„ظ…ظ‡ط§ظ… ط§ظ„ظ…ظڈطھط­ظ‚ظ‚ ظ…ظ†ظ‡ط§ | ط§ظ„ط´ط±ط· ظ„ظ„ظ…طھط§ط¨ط¹ط© |
|------|---------------------|----------------|
| Gate 1 | Task 1 | ظ†ظ…ط§ط°ط¬ Request/Result/Evidence ظ…ط¹طھظ…ط¯ط© |
| Gate 2 | Task 2 | Lifecycle orchestrator ظٹط¹ظ…ظ„ ظ…ط¹ mock sources |
| Gate 3 | Task 3 + Task 4 | Source registry ظˆ retrieval ظٹط¹ظ…ظ„ط§ظ† |
| Gate 4 | Task 5 | Provenance capture ظٹط«ط¨طھ ط¹ظ„ظ‰ ظƒظ„ ظ†طھظٹط¬ط© |
| Gate 5 | Task 6 | Research Result interface ظ…ظ‚ط¨ظˆظ„ط© ظ…ظ† Reasoning |
| Gate 6 | Task 7 | Failure handling ظˆ quality indicators ظ…ط¹طھظ…ط¯ط© |
| Gate 7 | Task 8 | Governance docs ظ…ط­ط¯ظ‘ط«ط© ظˆExit Criteria ظ…ظڈط³طھظˆظپط§ط© |

---

## 5. Deliverables ط§ظ„ظ†ظ‡ط§ط¦ظٹط©

| # | Deliverable | ط§ظ„ظ…ظ‡ظ…ط© ط§ظ„ظ…ط³ط¤ظˆظ„ط© | ط§ظ„ظ…ظ„ظپ |
|---|-------------|-----------------|-------|
| 1 | Research Request/Result Models | Task 1 | `backend/app/research/models.py` |
| 2 | Research Lifecycle Orchestrator | Task 2 | `backend/app/research/orchestrator.py` |
| 3 | Source Registry & Discovery | Task 3 | `backend/app/research/sources/` |
| 4 | Retrieval Abstraction | Task 4 | `backend/app/research/retrieval/` |
| 5 | Evidence & Provenance Capture | Task 5 | `backend/app/research/evidence.py` |
| 6 | Result Structuring & Output | Task 6 | `backend/app/research/result.py` |
| 7 | Verification & Quality | Task 7 | `backend/app/research/quality.py` |
| 8 | Governance Updates | Task 8 | `PLAN.md`, `CURRENT_STATUS.md`, `CHANGELOG.md` |

---

## 6. Acceptance Criteria Coverage

| AC | ط§ظ„ظ…ظ‡ظ…ط© ط§ظ„ظ…ط³ط¤ظˆظ„ط© |
|----|-----------------|
| AC-34.1: ط¥ظ…ظƒط§ظ†ظٹط© ط¥ظ†ط´ط§ط، Research Request | Task 1 |
| AC-34.2: طھظ†ظپظٹط° Research Lifecycle ظƒط§ظ…ظ„ط© | Task 2 |
| AC-34.3: ط§ظƒطھط´ط§ظپ ظˆط§ط³طھط¹ظ„ط§ظ… ظ…طµط§ط¯ط± ط®ط§ط±ط¬ظٹط© | Task 3 + Task 4 |
| AC-34.4: ط§ط±طھط¨ط§ط· ط§ظ„ظ†طھط§ط¦ط¬ ط¨ظ…طµط§ط¯ط±ظ‡ط§ | Task 5 |
| AC-34.5: طھط³ط¬ظٹظ„ ط§ظ„ط£ط¯ظ„ط©/ط§ظ„ظ…ط±ط§ط¬ط¹ | Task 5 |
| AC-34.6: ط§ظ„طھط¹ط§ظ…ظ„ ظ…ط¹ ظپط´ظ„ ط§ظ„ظ…طµط¯ط± | Task 7 |
| AC-34.7: ط¹ط¯ظ… طھظ‚ط¯ظٹظ… LLM ظƒظ…طµط¯ط± ط­ظ‚ظٹظ‚ط© | Task 5 + Task 7 |
| AC-34.8: ط¥ط®ط±ط§ط¬ ظ†طھظٹط¬ط© ظ…ظ†ط¸ظ…ط© ظ„ظ€ Reasoning | Task 6 |
| AC-34.9: ط§ظ„ط­ظپط§ط¸ ط¹ظ„ظ‰ ط­ط¯ظˆط¯ ط§ظ„ظ…ط³ط¤ظˆظ„ظٹط§طھ | Task 2 + Task 6 + Task 7 |

---

## 7. Exit Criteria

| # | Exit Criterion | Verification |
|---|---------------|--------------|
| EC-34.1 | ط¬ظ…ظٹط¹ ط§ظ„ظ…ظ‡ط§ظ… ظ…ظ† 1 ط¥ظ„ظ‰ 7 ظ…ظƒطھظ…ظ„ط© | Git diff + review |
| EC-34.2 | Research Request model ظٹط«ط¨طھ ط¨ط§ط®طھط¨ط§ط±ط§طھ | Unit tests |
| EC-34.3 | Lifecycle ظٹط¹ظ…ظ„ end-to-end ظ…ط¹ mock sources | Integration tests |
| EC-34.4 | Provenance capture ظٹط«ط¨طھ ط¹ظ„ظ‰ ظƒظ„ ظ†طھظٹط¬ط© | Unit + integration tests |
| EC-34.5 | Source failure ظ„ط§ ظٹظˆظ‚ظپ ط§ظ„ط¨ط­ط« | Fault injection tests |
| EC-34.6 | Research Result interface ظ…ظ‚ط¨ظˆظ„ط© ظ…ظ† Reasoning | Contract test |
| EC-34.7 | ظ„ط§ طھظˆط¬ط¯ طھط¹ط¯ظٹظ„ط§طھ ط¹ظ„ظ‰ Knowledge Ingestion Contract | Git diff verification |
| EC-34.8 | PLAN.md ظˆ CURRENT_STATUS.md ظ…ط­ط¯ظ‘ط«ط© | Manual verification |

---

## 8. Open Architectural Decisions

| # | Decision | Impact | Decision Required By |
|---|----------|--------|---------------------|
| 1 | Source trust scoring algorithm | طھط±طھظٹط¨ ط§ظ„ظ†طھط§ط¦ط¬ ظˆط§ظ„ط«ظ‚ط© | Task 7 design |
| 2 | Duplicate detection strategy | طھط¬ظ…ظٹط¹ ط§ظ„ظ†طھط§ط¦ط¬ | Task 7 design |
| 3 | Content validation mechanism | ط¬ظˆط¯ط© ط§ظ„ظ†طھط§ط¦ط¬ | Task 7 design |
| 4 | Source registry format | ط¥ط¯ط§ط±ط© ط§ظ„ظ…طµط§ط¯ط± | Task 3 design |
| 5 | LLM provider selection for research assistance | ط§ظ„طھظƒظ„ظپط© ظˆط§ظ„ط¬ظˆط¯ط© | Task 2 design |

---

## 9. ط§ظ„ط§ط¹طھظ…ط§ط¯ظٹط§طھ

|ependency | Type | Status |
|------------|------|--------|
| WP-30F: Company Knowledge Layer Interface | Internal | âœ… Complete |
| WP-30G: Memory Interface Definition | Internal | âœ… Complete |
| WP-LLM-001: LLM Provider Integration | Internal | âœ… Complete |
| WP-31: AI Memory | Internal | âœ… Complete |
| WP-32: Knowledge Graph | Internal | âœ… Complete |
| WP-33: Trade Intelligence | Internal | âœ… Complete |
| WP-42: Owner Acceptance | Internal | âœ… Complete |
| Knowledge Ingestion Contract boundaries | Documentation | âœ… Clarified |

---

## 10. ط§ظ„ظ…ظ‡ظ…ط© ط§ظ„ط£ظˆظ„ظ‰ ظ„ظ„طھظ†ظپظٹط°

**Task 1: Research Request Model & API Contract**

ط§ظ„ط³ط¨ط¨: ظ‡ظٹ ط§ظ„ظ…ظ‡ظ…ط© ط§ظ„ط£ط³ط§ط³ظٹط© ط§ظ„طھظٹ طھط­ط¯ط¯ ط§ظ„ظ‡ظٹظƒظ„ ط§ظ„ظˆط«ط§ط¦ظ‚ظٹ ظ„ظ„ط¨ط­ط«. ط¨ط¯ظˆظ†ظ‡ط§ ظ„ط§ ظٹظ…ظƒظ† طھظ†ظپظٹط° ط§ظ„ظ€ lifecycle ط£ظˆ ط£ظٹ ظ…ظ‡ظ…ط© ظ„ط§ط­ظ‚ط©.

---

*Document Status: Draft â€” Pending Approval*

