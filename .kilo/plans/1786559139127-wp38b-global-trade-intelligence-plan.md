# WP-38b Plan: Global Trade Intelligence — First Provider Implementation

**Work Package:** WP-38b — Global Trade Intelligence (TradeData First Provider)  
**Status:** Approved — G1 Approved — Ready for Task 1  
**Date:** 2026-08-13  
**Authority:** `.kilo/plans/1786359213310-real-external-source-integration.md` Section 5.2, Section 14, Section 15  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Prerequisite:** WP-38a closed and baselined at `baseline-wp38a-final` (`13fb461b`)  
**Path:** `.kilo/plans/1786559139127-wp38b-global-trade-intelligence-plan.md`

---

## 1. Governance Decision

| Decision | Value |
|----------|-------|
| WP-38a Status | **Closed** — `baseline-wp38a-final` at commit `13fb461b0ae3944a0e0f0a3d55440d3463cf3697` |
| WP-38b Status | **Approved as next Sub-WP** |
| First Provider | **TradeData API** (`tradedata.io`) — Approved for WP-38b implementation |
| Approval Basis | Project Owner approval of WP-38b plan following WP-38a closure |
| Sequence Compliance | WP-38a → WP-38b → WP-38c → WP-38d (fixed unless amended) |

**Note:** TradeData is approved as the **first provider** for WP-38b. G1 approval has been obtained. Implementation may proceed through Tasks 2–8 following the standard integration pattern.

---

## 2. Objectives

1. Integrate **TradeData API** as the first provider for WP-38b Global Trade Intelligence, extending the Knowledge Ingestion Pipeline beyond Egypt-focused regulatory data to global trade statistics, shipment records, and company intelligence.
2. Reuse the **shared integration pattern** proven in WP-38a without modifying `KnowledgeProviderRegistry`, `KNOWLEDGE_INGESTION_CONTRACT.md`, or any DEM core component.
3. Maintain **Provider-Agnostic architecture**: TradeData access is exclusively through `TradeDataExternalSourceAdapter(KnowledgeProvider)`.
4. Establish the **reusable pattern** for WP-38c and WP-38d by repeating the same task/gate sequence without re-architecture.

---

## 3. Scope

### 3.1 In Scope

| Item | Description |
|------|-------------|
| Source 6 evaluation | TradeData API (`tradedata.io`) — full evaluation against portfolio criteria |
| TradeData adapter | `TradeDataExternalSourceAdapter` implementing `KnowledgeProvider` |
| HTTP client | Isolated `TradeDataApiClient` with retry/backoff for timeouts, network errors, and HTTP 429 |
| Configuration | `TRADEDATA_BASE_URL`, `TRADEDATA_API_KEY`, `TRADEDATA_TIMEOUT_SECONDS`, `TRADEDATA_SOURCE_ID`, `TRADEDATA_SOURCE_NAME`, `TRADEDATA_SOURCE_TYPE`, `TRADEDATA_SOURCE_VERSION` in `config.py` |
| Bootstrap registration | Conditional registration in `main.py` `lifespan()` wrapped in try/except |
| Unit tests | 8+ tests covering `get_sources()`, transformation, error handling, confidence, provenance, config |
| Integration tests | 6+ tests covering registry registration, queryability, DEM core coexistence, graceful degradation |
| Regression tests | Full pytest run with zero regressions |
| Documentation | Update `ENGINEERING_MEMORY.md`, `CURRENT_STATUS.md`, `CHANGELOG.md` |
| Closure artifacts | Closure report + Owner Acceptance Certificate + `baseline-wp38b-final` tag |

### 3.2 Out of Scope

| Item | Description |
|------|-------------|
| Multiple providers | Only TradeData is implemented in WP-38b. Sources 7–10 (NBD, PST.AG, The Trade Hub, USITC HTS) remain future providers. |
| DEM core changes | No modifications to `ReasoningEngine`, `TaskPlanner`, `ToolOrchestrator`, or any DEM core component. |
| Knowledge Graph schema | No changes to `knowledge_nodes` or `knowledge_edges`. |
| Contract changes | `KNOWLEDGE_INGESTION_CONTRACT.md` is immutable. |
| Database migrations | No new tables or schema changes. |
| Frontend changes | No frontend modifications. |
| WP-38c/38d | No work on Jordan/UAE/Saudi/GCC sources. |
| New WPs | No creation of WP-39, WP-40, WP-41, or any other WP outside WP-38 Sub-WPs. |
| Web scraping | TradeData is Tier A (documented REST API). Web scraping is not applicable. |

---

## 4. Source Portfolio — WP-38b

| # | Source | Role / Function | Data Type | Authority / Provenance | API / Access | Authentication | Cost / Licensing | Rate Limits | Reliability | Data Freshness | Coverage | Dependencies | Risks | Requirements | Tier | First / Future | Priority |
|---|--------|----------------|-----------|------------------------|--------------|----------------|------------------|-------------|-------------|----------------|----------|--------------|-------|--------------|------|----------------|----------|
| 6 | **TradeData API** (tradedata.io) | Global trade statistics, shipment records, company intelligence | Trade flows, shipment records, company profiles | Commercial aggregator | REST API, JSON | API token | Paid — sandbox free | Unknown | High | Periodic | 200+ countries | Network access | Commercial dependency, pricing unknown | `config.py` token, retry logic | A | **First Provider** | **1** |
| 7 | NBD Trade Data API (data.nbd.ltd) | Global trade data, shipment records, company intelligence | Shipment records, company profiles, trade trends | Commercial aggregator | REST API, JSON | API key | Paid — pricing TBD | Unknown | Medium | Real-time claimed | 42+ countries | Network access, NBD account | Smaller coverage, commercial dependency | `config.py` API key, retry logic | A | Future | 2 |
| 8 | PST.AG (pst.ag) | Global customs tariffs, duty rates, trade agreements, sanctions, export control | Customs tariffs, FTAs, sanctions lists, export controls | Commercial global trade data provider | REST + SOAP + SFTP/FTP, JSON/XML/CSV/Excel | API key | Paid — enterprise sales | Unknown | Medium | Daily updates claimed | 160+ countries | Network access, PST.AG account | Large scope may be overkill, enterprise sales model, commercial dependency | `config.py` API key, multi-protocol client, caching | A | Future | 3 |
| 9 | The Trade Hub (thetradehub.eu) | EU customs intelligence, TARIC nomenclature, origin rules, CBAM | TARIC codes, origin rules, duty measures, EU regulations | Commercial EU customs platform | REST + SOAP, JSON/XML | API key | Paid — pricing TBD | Unknown | Medium | Periodic | EU / European trade | Network access, EU focus | EU-specific, complex API structure, commercial | `config.py` API key, SOAP client, REST client | A | Future | 4 |
| 10 | USITC HTS (hts.usitc.gov) | US Harmonized Tariff Schedule, export rules | Tariff schedule, export notices | Official US government | Web + JSON/CSV/Excel export | None | Free | N/A | **High** | Periodic updates | United States only | Network access | US-only scope, primarily tariff data not full regulations | JSON export parsing, US-only filter | B | Future | 5 |

**Important:** Only Source 6 (TradeData) is in scope for WP-38b. Sources 7–10 are future providers within WP-38b and require independent evaluation, approval, adapter design, implementation, verification, and baseline following the same standard integration pattern.

---

## 5. TradeData G1 Pre-Assessment

| Criterion | Evidence | Status |
|-----------|----------|--------|
| Machine-to-machine access | REST API at `api.tradedata.io`, documented endpoints | **Verified** |
| Data → `KnowledgeProvider.query()` shape | Customs/shipment data available; schema fields require verification during WP-38b Task 1 | **Pending Verification** |
| `source_id` | Not documented in public API docs | **Adapter-assigned** |
| `confidence` | Not documented in public API docs | **Adapter-assigned** |
| Provenance fields | Not documented in public API docs | **Adapter-assigned** |
| Commercial license | Project Owner approved DEM use model for TradeData integration | **Approved** |
| Redistribution terms | Project Owner approved internal-use scope for DEM | **Approved** |
| Egypt coverage | API covers 200+ countries; Egypt not explicitly confirmed in docs | **Pending Verification** |
| Rate limits | Unknown — not documented publicly | **Pending Verification** |
| Retention/caching terms | Project Owner approved data handling model | **Approved** |

**TradeData G1 Verdict:** **G1 Approved**  
**Resolved Items:**
1. Commercial license terms — Project Owner approval obtained for DEM use model
2. Redistribution terms — Project Owner approved internal-use scope
3. Retention/caching terms — Project Owner approved data handling model

**G1 Actions Completed:**
1. Project Owner reviewed and approved TradeData commercial use model for DEM integration.
2. Egypt coverage and field mapping to be verified during Task 1 implementation.
3. Project Owner approval obtained — G1 Approved.

**Fallback:** If TradeData G1 blockers cannot be resolved, evaluate NBD (Source 7) as alternative first provider for WP-38b per the unified comparison matrix in `.kilo/plans/wp38-task1-source-evaluation-report.md`.

---

## 6. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| WP-38a closed and baselined | ✅ Complete | `baseline-wp38a-final` at `13fb461b` |
| `KnowledgeProvider` ABC | ✅ Existing | No changes |
| `KnowledgeProviderRegistry` | ✅ Existing | No changes |
| `KNOWLEDGE_INGESTION_CONTRACT.md` | ✅ Approved | Must not be modified |
| `config.py` pattern | ✅ Existing | New settings added for TradeData |
| TradeData API availability | ⚠️ To be verified | Must be verified during Task 1 |
| TradeData commercial license | ✅ Approved | Project Owner approved DEM use model |
| Project Owner approval | ✅ Approved | G1 approval obtained for TradeData as WP-38b First Provider |
| WP-38b closure | ⚠️ Required | WP-38c cannot start before WP-38b is closed |

---

## 7. Tasks (Standard Integration Pattern — Reused from WP-38a)

The following task sequence is applied uniformly to TradeData within WP-38b. The pattern is defined in WP-38a and reused without modification.

### Task 1: Source Evaluation & Access Verification

- Evaluate TradeData API against portfolio criteria: authority/provenance, regulatory relevance, machine-to-machine access, cost/licensing, rate limits, reliability, freshness, coverage, integration complexity.
- Verify API access, document endpoints, test connectivity with sandbox.
- Verify Egypt coverage in TradeData response schema.
- Select **TradeData** as the recommended provider for WP-38b.
- **Gate G1:** Project Owner approval required before Task 2.
- **Deliverable:** Source Evaluation Report + Selected Source Specification + Access Verification Record + G1 Approval Record

### Task 2: Define External Source Contract Adapter

- Define transformation rules from TradeData response format → `KnowledgeProvider.query()` return shape
- Map TradeData fields to internal metadata: `regulation_type`, `category`, `country`, `effective_date`, `source_url`, `version`
- Define confidence scoring rules for TradeData data (may differ from WP-38a rules)
- Define provenance metadata: source ID, fetch timestamp, record hash/version, retrieval status
- Define error handling strategy for each failure mode: network error, timeout, malformed data, auth failure, rate limit
- **Gate G2:** Adapter spec review and approval required before Task 3
- **Deliverable:** Adapter specification + confidence/provenance rules + error handling matrix

### Task 3: Implement External Source Provider

- **File:** `backend/app/agent/knowledge/tradedata_provider.py` (new)
- Implement HTTP client with retry/backoff
- Implement transformation logic per Task 2 spec
- Implement graceful degradation when TradeData is unavailable
- Add configuration settings to `config.py` for endpoint/credentials
- Ensure Provider-Agnostic architecture per Section 12 of parent plan
- **Gate G3:** Code review confirms contract compliance and Provider-Agnostic architecture before Task 4
- **Deliverable:** New provider class, no DEM core changes

### Task 4: Bootstrap Registration

- **File:** `backend/main.py` (modification)
- Add import and registration call in `lifespan()` for TradeData provider
- Wrap in try/except to match existing pattern
- **Deliverable:** Provider registered at startup

### Task 5: Unit Tests

- **File:** `backend/tests/agent/test_tradedata_provider.py` (new)
- Test cases:
  1. `get_sources()` returns expected structure with TradeData metadata
  2. `query()` transforms TradeData data correctly per Task 2 spec
  3. `query()` handles network failure gracefully (returns empty results, no exception)
  4. `query()` handles malformed TradeData data gracefully
  5. Confidence scores within 0.0–1.0 per Task 2 rules
  6. Provenance metadata populated correctly
  7. Configuration settings loaded correctly
  8. Retry/backoff behavior verified
- **Deliverable:** 8+ passing unit tests

### Task 6: Integration Tests

- **File:** `backend/tests/agent/test_tradedata_integration.py` (new)
- Test cases:
  1. TradeData provider registers successfully in `KnowledgeProviderRegistry`
  2. TradeData provider is queryable via registry
  3. `ReasoningEngine` can query TradeData provider through registry
  4. Existing providers still register after TradeData provider
  5. Fallback to other providers when TradeData is unavailable
  6. Graceful degradation does not crash application startup
- **Deliverable:** 6+ passing integration tests

### Task 7: Verification & Evidence

- Run full backend test suite
- Verify no regressions
- Verify no import cycles
- Capture evidence:
  - Test reports
  - Sample TradeData fetch logs (sanitized)
  - Transformation examples
  - Performance metrics
  - Source evaluation report
  - Access verification record
- **Gate G4:** All verification criteria met before Task 8
- **Deliverable:** Verification report with evidence
- **Status:** Completed — `.kilo/plans/wp38b-task7-verification-evidence-package.md`

### Task 8: Documentation

- Update `ENGINEERING_MEMORY.md` with TradeData completion entry
- Update `CURRENT_STATUS.md` with WP-38b entry
- Update `CHANGELOG.md` with WP-38b entry
- Update `.kilo/plans/` with WP-38b closure report
- **Deliverable:** Updated docs
- **Status:** Completed — `.kilo/plans/wp38b-final-closure-report.md`

---

## 8. Gates

| Gate | Requirement | Impact if Not Met |
|------|-------------|-------------------|
| **G0 — WP-38b Plan Approval** | Project Owner approves WP-38b plan | WP does not start |
| **G1 — TradeData Source Selection** | TradeData G1 blockers resolved; Project Owner approves TradeData | WP-38b stops; no implementation begins |
| **G2 — Adapter Review** | Adapter spec reviewed and approved | WP-38b stops; implementation does not begin |
| **G3 — Implementation Review** | Code review confirms Provider-Agnostic architecture and contract compliance | WP-38b returns to Task 3 for fixes |
| **G4 — Verification** | All tests pass, no regressions, evidence complete | WP-38b returns to fix blockers |
| **G5 — Closure** | All acceptance criteria met, baseline tagged | WP-38b remains open |

---

## 9. Acceptance Criteria

| ID | Criterion | Verification | Gate |
|----|-----------|--------------|------|
| AC-38b.0 | Project Owner approved WP-38b plan | Approval record | G0 |
| AC-38b.1 | TradeData source selected and G1 blockers resolved | Source evaluation report approved | G1 |
| AC-38b.2 | Adapter specification defined and approved | Adapter spec document approved | G2 |
| AC-38b.3 | TradeData provider implements `KnowledgeProvider` interface | Type check + tests | G3 |
| AC-38b.4 | `get_sources()` returns valid metadata with provenance | Unit test | — |
| AC-38b.5 | `query()` transforms TradeData data to contract shape | Unit test | — |
| AC-38b.6 | Confidence scores are within 0.0–1.0 per Task 2 rules | Unit test | — |
| AC-38b.7 | Provider registers successfully in `KnowledgeProviderRegistry` | Integration test | — |
| AC-38b.8 | Provider is queryable via registry without DEM core changes | Integration test | — |
| AC-38b.9 | `ReasoningEngine` can query provider through registry | Integration test | — |
| AC-38b.10 | Graceful degradation when TradeData is unavailable | Integration test | — |
| AC-38b.11 | All existing tests pass (no regressions) | Full pytest run | G4 |
| AC-38b.12 | No DEM core files modified | Code review / git diff | G4 |
| AC-38b.13 | No database schema changes | Code review / git diff | G4 |
| AC-38b.14 | Documentation updated | Doc review | G5 |
| AC-38b.15 | Baseline tagged | `baseline-wp38b-final` exists | G5 |

---

## 10. Baseline

| Field | Value |
|-------|-------|
| Baseline Tag | `baseline-wp38b-final` |
| Commit | To be created at closure |
| Date | TBD |

---

## 11. Next Steps After This Approval

1. Proceed to WP-38b Task 1 — TradeData Source Evaluation & Access Verification
2. Resolve remaining verification items (Egypt coverage, rate limits, schema mapping) during Task 1
3. Project Owner approval of TradeData as WP-38b First Provider — Already obtained (G1 Approved)
4. Proceed through Tasks 2–8 following the standard integration pattern
5. Tag `baseline-wp38b-final` upon closure

**No work on WP-38c or WP-38d until WP-38b is fully closed and baselined.**

---

## 12. Governance Notes

- **Contract preservation:** `KNOWLEDGE_INGESTION_CONTRACT.md` must not be modified.
- **Provider-Agnostic architecture:** TradeData provider must not hardcode assumptions that prevent future source replacement.
- **No DEM core changes:** All integration must happen through `KnowledgeProviderRegistry`.
- **Source selection gate:** TradeData requires Project Owner approval before implementation begins. This is a hard gate.
- **One provider at a time:** WP-38b integrates exactly one provider (TradeData). Sources 7–10 are future providers requiring independent evaluation, approval, and implementation.
- **Next Provider Gate:** No subsequent provider may be introduced before TradeData is fully closed and baselined.
- **Next Sub-WP Gate:** No subsequent Sub-WP (WP-38c) may begin before WP-38b is fully closed and baselined.
- **Shared Pattern:** The integration pattern is defined in WP-38a and reused in WP-38b without modification.

---

*Plan Status: Approved — G1 Approved — Ready for Task 1*
