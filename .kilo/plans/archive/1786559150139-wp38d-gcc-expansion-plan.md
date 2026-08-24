# WP-38d Plan: GCC Expansion â€” First Provider Implementation

**Work Package:** WP-38d â€” GCC Expansion (GCC-Stat First Provider)  
**Status:** Closed â€” Task 8 Completed â€” Ready for G5 Review  
**Date:** 2026-08-14  
**Authority:** `\.kilo/plans/archive/1786359213310-real-external-source-integration\.md` Section 5.4, Section 14, Section 15  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Prerequisite:** WP-38c closed and baselined at `baseline-wp38c-final` (`e10295d`)  
**Path:** `\.kilo/plans/archive/1786559150139-wp38d-gcc-expansion-plan\.md`

---

## 1. Governance Decision

| Decision | Value |
|----------|-------|
| WP-38a Status | **Closed** â€” `baseline-wp38a-final` at commit `13fb461b` |
| WP-38b Status | **Closed** â€” `baseline-wp38b-final` at commit `02bad55` |
| WP-38c Status | **Closed** â€” `baseline-wp38c-final` at commit `e10295d` |
| WP-38d Status | **Approved** â€” G0 Approved â€” Ready for Task 1 |
| First Provider Candidate | **GCC-Stat** (`gccstat.org`) â€” Proposed for WP-38d Task 1 evaluation |
| Approval Basis | Project Owner approval of WP-38d plan following WP-38c closure |
| Sequence Compliance | WP-38a â†’ WP-38b â†’ WP-38c â†’ WP-38d (fixed unless amended) |

**Note:** GCC-Stat is proposed as the **first provider candidate** for WP-38d. Final provider selection requires G1 approval after Task 1 evaluation and access verification. If GCC-Stat API verification fails, evaluation reverts to Qatar Customs (Source 17) per the unified source portfolio in the parent plan.

---

## 2. Objectives

1. Integrate **one first provider** for WP-38d GCC Expansion, extending the Knowledge Ingestion Pipeline to cover GCC-wide trade statistics and country-specific regulations for Qatar, Kuwait, Oman, and Bahrain.
2. Reuse the **shared integration pattern** proven in WP-38a, WP-38b, and WP-38c without modifying `KnowledgeProviderRegistry`, `KNOWLEDGE_INGESTION_CONTRACT.md`, or any DEM core component.
3. Maintain **Provider-Agnostic architecture**: provider access is exclusively through `KnowledgeProvider` implementations.
4. Establish the **reusable pattern** for any future Sub-WPs by repeating the same task/gate sequence without re-architecture.

---

## 3. Scope

### 3.1 In Scope

| Item | Description |
|------|-------------|
| Sources 16â€“20 evaluation | Evaluate all five sources against portfolio criteria during Task 1 |
| First provider adapter | Implement adapter for the selected first provider only |
| HTTP client | Isolated HTTP client with retry/backoff for timeouts, network errors, and HTTP 429 |
| Configuration | Add provider-specific settings to `config.py` for endpoint/credentials |
| Bootstrap registration | Conditional registration in `main.py` `lifespan()` wrapped in try/except |
| Unit tests | 8+ tests covering `get_sources()`, transformation, error handling, confidence, provenance, config |
| Integration tests | 6+ tests covering registry registration, queryability, DEM core coexistence, graceful degradation |
| Regression tests | Full pytest run with zero regressions |
| Documentation | Update `ENGINEERING_MEMORY.md`, `CURRENT_STATUS.md`, `CHANGELOG.md` |
| Closure artifacts | Closure report + Owner Acceptance Certificate + `baseline-wp38d-final` tag |

### 3.2 Out of Scope

| Item | Description |
|------|-------------|
| Multiple providers | Only one first provider is implemented in WP-38d. Sources 17â€“20 remain future providers. |
| DEM core changes | No modifications to `ReasoningEngine`, `TaskPlanner`, `ToolOrchestrator`, or any DEM core component. |
| Knowledge Graph schema | No changes to `knowledge_nodes` or `knowledge_edges`. |
| Contract changes | `KNOWLEDGE_INGESTION_CONTRACT.md` is immutable. |
| Database migrations | No new tables or schema changes. |
| Frontend changes | No frontend modifications. |
| New WPs | No creation of WP-39, WP-40, WP-41, or any other WP outside WP-38 Sub-WPs. |
| Web scraping for Tier A sources | If a Tier A source's API cannot be verified during Task 1, it reverts to Tier B and evaluation order is adjusted. |

---

## 4. Source Portfolio â€” WP-38d

| # | Source | Role / Function | Data Type | Authority / Provenance | API / Access | Authentication | Cost / Licensing | Rate Limits | Reliability | Data Freshness | Coverage | Dependencies | Risks | Requirements | Tier | First / Future | Priority |
|---|--------|----------------|-----------|------------------------|--------------|----------------|------------------|-------------|-------------|----------------|----------|--------------|-------|--------------|------|----------------|----------|
| 16 | **GCC-Stat Data Portal / REST / SDMX APIs** (gccstat.org) | GCC-wide trade statistics, economic indicators, customs data, market intelligence | Trade statistics, economic indicators, customs aggregates | Official GCC statistical body | REST / SDMX APIs â€” availability requires verification | API key (suspected) | Free (open data) | Unknown | Medium | Periodic | GCC-wide | Network access | API documentation not publicly verified, multi-country aggregation | API verification, SDMX parsing, normalization | A | **First Provider Candidate** | **1** |
| 17 | **Qatar General Authority of Customs â€” Tariff & Restricted Goods** (customs.gov.qa) | Qatar customs regulations, tariff schedule, prohibited/restricted goods, import procedures | Customs rules, tariff schedule, restricted goods list | Official Qatari government | Web portal â€” machine-readable access not documented | None | Free | N/A | Medium | Irregular | Qatar only | Network access | No documented REST API, political/organizational changes | Web scraping, translation, normalization | B | Future | 2 |
| 18 | **Kuwait Customs â€” HS Tariff & Customs Rules** (customs.gov.kw) | Kuwait customs regulations, HS tariff schedule, duty rates, import/export procedures | Customs rules, tariff schedule, HS codes, duty rates | Official Kuwaiti government | Web portal â€” machine-readable access not documented | None | Free | N/A | Medium | Periodic | Kuwait only | Network access | No documented REST API, primarily web UI | Web scraping, HS mapping, normalization | B | Future | 3 |
| 19 | **Oman Customs â€” Bayan / Customs Tariff** (customs.gov.om) | Oman customs regulations, Bayan system, tariff schedule, import/export procedures | Customs rules, tariff schedule, Bayan data | Official Omani government | Web portal â€” machine-readable access not documented | None | Free | N/A | Medium | Irregular | Oman only | Network access | No documented REST API, primarily web UI | Web scraping, translation, normalization | B | Future | 4 |
| 20 | **Bahrain Customs Affairs â€” Ofoq / Seraj / HS & Regulations** (customs.gov.bh) | Bahrain customs regulations, Ofoq/Seraj systems, tariff schedule, HS codes | Customs rules, tariff schedule, HS codes, Ofoq/Seraj data | Official Bahraini government | Web portal â€” machine-readable access not documented | None | Free | N/A | Medium | Periodic | Bahrain only | Network access | No documented REST API, primarily web UI | Web scraping, HS mapping, normalization | B | Future | 5 |

**Important:** Only one first provider will be implemented in WP-38d. The remaining sources 17â€“20 are future providers requiring independent evaluation, approval, adapter design, implementation, verification, and baseline following the same standard integration pattern.

---

## 5. GCC-Stat G1 Pre-Assessment

| Criterion | Evidence | Status |
|-----------|----------|--------|
| Machine-to-machine access | REST / SDMX APIs claimed â€” availability requires verification | **Pending Verification** |
| Data â†’ `KnowledgeProvider.query()` shape | Trade statistics, economic indicators, customs aggregates | **Pending Verification** |
| `source_id` | Not documented in public API docs | **Adapter-assigned** |
| `confidence` | Not documented in public API docs | **Adapter-assigned** |
| Provenance fields | Not documented in public API docs | **Adapter-assigned** |
| Commercial license | Free (open data) â€” internal use within terms | **Likely Approved** |
| Redistribution terms | GCC-Stat open data policy â€” requires verification | **Pending Verification** |
| GCC coverage | GCC-wide â€” covers Qatar, Kuwait, Oman, Bahrain | **Verified** |
| Rate limits | Unknown â€” not publicly documented | **Pending Verification** |
| SDMX parsing complexity | Medium â€” requires SDMX client library | **Technical Risk** |

**GCC-Stat G1 Verdict:** **G1 Approved**  
**Approval Basis:** Project Owner approval obtained for GCC-Stat as WP-38d First Provider per `\.kilo/plans/archive/wp38d-owner-acceptance-certificate\.md`.

**Fallback:** If GCC-Stat G1 blockers cannot be resolved, evaluate Qatar Customs (Source 17) as alternative first provider for WP-38d per the unified comparison matrix in `\.kilo/plans/archive/1786359213310-real-external-source-integration\.md`.

---

## 6. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| WP-38a closed and baselined | âœ… Complete | `baseline-wp38a-final` at `13fb461b` |
| WP-38b closed and baselined | âœ… Complete | `baseline-wp38b-final` at `02bad55` |
| WP-38c closed and baselined | âœ… Complete | `baseline-wp38c-final` at `e10295d` |
| `KnowledgeProvider` ABC | âœ… Existing | No changes |
| `KnowledgeProviderRegistry` | âœ… Existing | No changes |
| `KNOWLEDGE_INGESTION_CONTRACT.md` | âœ… Approved | Must not be modified |
| `config.py` pattern | âœ… Existing | New settings added for each provider |
| GCC-Stat API availability | âڑ ï¸ڈ To be verified | Must be verified during Task 1 |
| GCC-Stat commercial license | âڑ ï¸ڈ Pending | Requires Project Owner approval at G1 |
| Project Owner approval | âڑ ï¸ڈ Required | Mandatory gate before each provider implementation |

**Blocking dependencies:** Project Owner approval at G1; sequential Sub-WP closure.

---

## 7. Tasks (Standard Integration Pattern â€” Reused from WP-38a/WP-38b/WP-38c)

The following task sequence is applied uniformly to the first provider within WP-38d. The pattern is defined in WP-38a and reused without modification.

### Task 1: Source Evaluation & Access Verification

- Evaluate sources 16â€“20 against portfolio criteria: authority/provenance, regulatory relevance, machine-to-machine access, cost/licensing, rate limits, reliability, freshness, coverage, integration complexity.
- Select **one first provider** for WP-38d based on evaluation.
- Verify API access, document endpoints, test connectivity with sandbox if available.
- **Gate G1:** Project Owner approval required before Task 2.
- **Deliverable:** Source Evaluation Report + Selected Source Specification + Access Verification Record + G1 Approval Record

### Task 2: Define External Source Contract Adapter

- Define transformation rules from selected provider response format â†’ `KnowledgeProvider.query()` return shape
- Map provider fields to internal metadata: `regulation_type`, `category`, `country`, `effective_date`, `source_url`, `version`
- Define confidence scoring rules for provider data (may differ from WP-38a/WP-38b/WP-38c rules)
- Define provenance metadata: source ID, fetch timestamp, record hash/version, retrieval status
- Define error handling strategy for each failure mode: network error, timeout, malformed data, auth failure, rate limit
- **Gate G2:** Adapter spec review and approval required before Task 3
- **Deliverable:** Adapter specification + confidence/provenance rules + error handling matrix

### Task 3: Implement External Source Provider

- **File:** `backend/app/agent/knowledge/{provider}_provider.py` (new)
- Implement HTTP client with retry/backoff
- Implement transformation logic per Task 2 spec
- Implement graceful degradation when provider is unavailable
- Add configuration settings to `config.py` for endpoint/credentials
- Ensure Provider-Agnostic architecture per parent plan Section 12
- **Gate G3:** Code review confirms contract compliance and Provider-Agnostic architecture before Task 4
- **Deliverable:** New provider class, no DEM core changes

### Task 4: Bootstrap Registration

- **File:** `backend/main.py` (modification)
- Add import and registration call in `lifespan()` for provider
- Wrap in try/except to match existing pattern
- **Deliverable:** Provider registered at startup

### Task 5: Unit Tests

- **File:** `backend/tests/agent/test_{provider}_provider.py` (new)
- Test cases:
  1. `get_sources()` returns expected structure with provider metadata
  2. `query()` transforms provider data correctly per Task 2 spec
  3. `query()` handles network failure gracefully (returns empty results, no exception)
  4. `query()` handles malformed provider data gracefully
  5. Confidence scores within 0.0â€“1.0 per Task 2 rules
  6. Provenance metadata populated correctly
  7. Configuration settings loaded correctly
  8. Retry/backoff behavior verified
- **Deliverable:** 8+ passing unit tests

### Task 6: Integration Tests

- **File:** `backend/tests/agent/test_{provider}_integration.py` (new)
- Test cases:
  1. Provider registers successfully in `KnowledgeProviderRegistry`
  2. Provider is queryable via registry
  3. `ReasoningEngine` can query provider through registry
  4. Existing providers still register after provider
  5. Fallback to other providers when provider is unavailable
  6. Graceful degradation does not crash application startup
- **Deliverable:** 6+ passing integration tests

### Task 7: Verification & Evidence

- Run full backend test suite
- Verify no regressions
- Verify no import cycles
- Capture evidence:
  - Test reports
  - Sample provider fetch logs (sanitized)
  - Transformation examples
  - Performance metrics
  - Source evaluation report
  - Access verification record
- **Gate G4:** All verification criteria met before Task 8
- **Deliverable:** Verification report with evidence

### Task 8: Documentation

- Update `ENGINEERING_MEMORY.md` with provider completion entry
- Update `CURRENT_STATUS.md` with WP-38d entry
- Update `CHANGELOG.md` with WP-38d entry
- Update `.kilo/plans/` with WP-38d closure report
- **Deliverable:** Updated docs

---

## 8. Gates

| Gate | Requirement | Impact if Not Met |
|------|-------------|-------------------|
| **G0 â€” WP-38d Plan Approval** | Project Owner approves WP-38d plan | WP does not start |
| **G1 â€” Source Selection** | First provider selected and G1 blockers resolved; Project Owner approves provider | WP-38d stops; no implementation begins |
| **G2 â€” Adapter Review** | Adapter spec reviewed and approved | WP-38d stops; implementation does not begin |
| **G3 â€” Implementation Review** | Code review confirms Provider-Agnostic architecture and contract compliance | WP-38d returns to Task 3 for fixes |
| **G4 â€” Verification** | All tests pass, no regressions, evidence complete | WP-38d returns to fix blockers |
| **G5 â€” Closure** | All acceptance criteria met, baseline tagged | WP-38d remains open |

---

## 9. Acceptance Criteria

| ID | Criterion | Verification | Gate |
|----|-----------|--------------|------|
| AC-38d.0 | Project Owner approved WP-38d plan | Approval record | G0 |
| AC-38d.1 | First provider selected and G1 blockers resolved | Source evaluation report approved | G1 |
| AC-38d.2 | Adapter specification defined and approved | Adapter spec document approved | G2 |
| AC-38d.3 | Provider implements `KnowledgeProvider` interface | Type check + tests | G3 |
| AC-38d.4 | `get_sources()` returns valid metadata with provenance | Unit test | â€” |
| AC-38d.5 | `query()` transforms provider data to contract shape | Unit test | â€” |
| AC-38d.6 | Confidence scores are within 0.0â€“1.0 per Task 2 rules | Unit test | â€” |
| AC-38d.7 | Provider registers successfully in `KnowledgeProviderRegistry` | Integration test | â€” |
| AC-38d.8 | Provider is queryable via registry without DEM core changes | Integration test | â€” |
| AC-38d.9 | `ReasoningEngine` can query provider through registry | Integration test | â€” |
| AC-38d.10 | Graceful degradation when provider is unavailable | Integration test | â€” |
| AC-38d.11 | All existing tests pass (no regressions) | Full pytest run | G4 |
| AC-38d.12 | No DEM core files modified | Code review / git diff | G4 |
| AC-38d.13 | No database schema changes | Code review / git diff | G4 |
| AC-38d.14 | Documentation updated | Doc review | G5 |
| AC-38d.15 | Baseline tagged | `baseline-wp38d-final` exists | G5 |

---

## 10. Baseline

| Field | Value |
|-------|-------|
| Baseline Tag | `baseline-wp38d-final` |
| Commit | To be created at closure |
| Date | TBD |

---

## 11. Next Steps After This Approval

1. Create WP-38d plan document (this document)
2. Proceed to WP-38d Task 1 â€” Source Evaluation & Access Verification
3. Resolve remaining verification items (GCC-Stat API availability, SDMX parsing, rate limits) during Task 1
4. Project Owner approval of first provider â€” Required at G1
5. Proceed through Tasks 2â€“8 following the standard integration pattern
6. Tag `baseline-wp38d-final` upon closure

**No work on WP beyond WP-38 Sub-WPs until all Sub-WPs are fully closed and baselined.**

---

## 12. Governance Notes

- **Contract preservation:** `KNOWLEDGE_INGESTION_CONTRACT.md` must not be modified.
- **Provider-Agnostic architecture:** Provider must not hardcode assumptions that prevent future source replacement.
- **No DEM core changes:** All integration must happen through `KnowledgeProviderRegistry`.
- **Source selection gate:** First provider requires Project Owner approval before implementation begins. This is a hard gate.
- **One provider at a time:** WP-38d integrates exactly one first provider. Remaining sources 17â€“20 are future providers requiring independent evaluation, approval, and implementation.
- **Next Provider Gate:** No subsequent provider may be introduced before the first provider is fully closed and baselined.
- **Next Sub-WP Gate:** No subsequent Sub-WP may begin before WP-38d is fully closed and baselined.
- **Shared Pattern:** The integration pattern is defined in WP-38a and reused in WP-38d without modification.

---

*Plan Status: Approved â€” G0 Approved â€” Ready for Task 1*

