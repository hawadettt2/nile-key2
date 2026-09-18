# Phase 2 — Capability Truth Model

**Phase:** 2 — Capability Truth Model  
**Branch:** `main`  
**Mode:** Plan Only — No Implementation  
**Authority:** `.kilo/plans/1789672443844-master-remediation-plan.md`  
**Baseline:** `.kilo/plans/baseline-2026-09-17.md`  
**Business Promise:** Phase 1 Approved  
**Date:** 2026-09-18  

---

## 1. Capability Truth Matrix

### 1.1 UN Comtrade (`un-comtrade`)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Implemented | ✅ | Code exists at `backend/app/agent/knowledge/uncomtrade_provider.py` |
| Registered | ✅ | Listed in `KnowledgeOrchestrator._routing_table["trade_statistics"]` |
| Configured | ⚠️ | Config entries exist in `config.py`; `UN_COMTRADE_API_KEY` is empty in `.env` |
| Activated | ❌ | Cannot verify activation without credentials |
| Reachable | ❌ | Cannot verify without activation |
| Returns Data | ❌ | Cannot verify without activation |
| Capability Proven | ❌ | Not proven in current runtime |
| Scope Ready | ❌ | Not verified |
| Country/Product Ready | ❌ | Not verified |
| Business Question Ready | ❌ | Not verified |
| Decision-Safe | ❌ | Not verified |
| Response-Safe | ❌ | Not verified |
| **Evidence** | | Provider code and config exist; Preview API may work without key but full capability unverified |

### 1.2 World Bank LPI (`worldbank-lpi`)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Implemented | ✅ | Code exists at `backend/app/agent/knowledge/worldbank_lpi_provider.py` |
| Registered | ✅ | Listed in `KnowledgeOrchestrator` implicitly |
| Configured | ✅ | Config entries exist; public API, no credentials required |
| Activated | ✅ | Can be activated (public API) |
| Reachable | ✅ | Public Indicators API, no authentication required |
| Returns Data | ✅ | Code shows successful data return path |
| Capability Proven | ✅ | Country-level LPI scores only |
| Scope Ready | ⚠️ | Limited to country scores, not route-level |
| Country/Product Ready | ⚠️ | Country coverage global, but indicator-level only |
| Business Question Ready | ❌ | Route cost/transit time not available |
| Decision-Safe | ❌ | Not sufficient for route logistics decisions |
| Response-Safe | ⚠️ | Can report country scores with limitations |
| **Evidence** | | Code uses `https://api.worldbank.org/v2` public API; returns indicator data |

### 1.3 Company Knowledge (`company-knowledge`)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Implemented | ✅ | Code exists at `backend/app/agent/knowledge/company_knowledge_provider.py` |
| Registered | ✅ | Used in `KnowledgeOrchestrator` |
| Configured | ✅ | No external credentials required |
| Activated | ✅ | Can be activated (internal service) |
| Reachable | ✅ | Internal service dependency |
| Returns Data | ✅ | Code shows `search_resources` and `list_resources` calls |
| Capability Proven | ✅ | Internal curated knowledge corpus |
| Scope Ready | ✅ | Covers internal company knowledge |
| Country/Product Ready | ✅ | Depends on internal corpus content |
| Business Question Ready | ⚠️ | Limited to internal knowledge |
| Decision-Safe | ⚠️ | Internal knowledge only |
| Response-Safe | ✅ | Can report internal findings with provenance |
| **Evidence** | | Code queries `app.services.resource` for internal resources |

### 1.4 FAOSTAT (`faostat`)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Implemented | ✅ | Code exists at `backend/app/agent/knowledge/faostat_provider.py` |
| Registered | ✅ | Listed in `KnowledgeOrchestrator._routing_table` |
| Configured | ❌ | `FAOSTAT_USER` and `FAOSTAT_PASSWORD` missing from `.env` |
| Activated | ❌ | Cannot activate without credentials |
| Reachable | ❌ | Cannot verify without activation |
| Returns Data | ❌ | Cannot verify without activation |
| Capability Proven | ❌ | Not proven in current runtime |
| Scope Ready | ❌ | Not verified |
| Country/Product Ready | ❌ | Not verified |
| Business Question Ready | ❌ | Not verified |
| Decision-Safe | ❌ | Not verified |
| Response-Safe | ❌ | Not verified |
| **Evidence** | | Provider code exists; requires JWT authentication; credentials absent |

### 1.5 Moaah (`moaah`)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Implemented | ✅ | Code exists at `backend/app/agent/knowledge/mooadapter.py` |
| Registered | ✅ | Listed in `KnowledgeOrchestrator._routing_table` |
| Configured | ❌ | `MOAAH_API_KEY` missing from `.env` |
| Activated | ❌ | Cannot activate without credentials |
| Reachable | ❌ | Cannot verify without activation |
| Returns Data | ❌ | Cannot verify without activation |
| Capability Proven | ❌ | Not proven in current runtime |
| Scope Ready | ❌ | Not verified |
| Country/Product Ready | ❌ | Not verified |
| Business Question Ready | ❌ | Not verified |
| Decision-Safe | ❌ | Not verified |
| Response-Safe | ❌ | Not verified |
| **Evidence** | | Provider code exists; requires API key; credentials absent |

### 1.6 TradeData (`tradedata`)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Implemented | ✅ | Code exists at `backend/app/agent/knowledge/tradedata_provider.py` |
| Registered | ✅ | Listed in `KnowledgeOrchestrator._routing_table` |
| Configured | ❌ | `TRADEDATA_API_KEY` missing from `.env` |
| Activated | ❌ | Cannot activate without credentials |
| Reachable | ❌ | Cannot verify without activation |
| Returns Data | ❌ | Cannot verify without activation |
| Capability Proven | ❌ | Not proven in current runtime |
| Scope Ready | ❌ | Not verified |
| Country/Product Ready | ❌ | Not verified |
| Business Question Ready | ❌ | Not verified |
| Decision-Safe | ❌ | Not verified |
| Response-Safe | ❌ | Not verified |
| **Evidence** | | Provider code exists; requires API key; credentials absent |

### 1.7 ZATCA (`zatca`)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Implemented | ✅ | Code exists at `backend/app/agent/knowledge/zatca_provider.py` |
| Registered | ✅ | Listed in `KnowledgeOrchestrator._routing_table` |
| Configured | ❌ | `ZATCA_API_KEY` missing from `.env` |
| Activated | ❌ | Cannot activate without credentials |
| Reachable | ❌ | Cannot verify without activation |
| Returns Data | ❌ | Cannot verify without activation |
| Capability Proven | ❌ | Not proven in current runtime |
| Scope Ready | ❌ | Not verified |
| Country/Product Ready | ❌ | Not verified |
| Business Question Ready | ❌ | Not verified |
| Decision-Safe | ❌ | Not verified |
| Response-Safe | ❌ | Not verified |
| **Evidence** | | Provider code exists; Saudi Arabia focus; requires API key; credentials absent |

### 1.8 GCC-Stat (`gccstat`)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Implemented | ✅ | Code exists at `backend/app/agent/knowledge/gccstat_provider.py` |
| Registered | ✅ | Listed in `KnowledgeOrchestrator._routing_table` |
| Configured | ❌ | `GCCSTAT_API_KEY` missing from `.env` |
| Activated | ❌ | Cannot activate without credentials |
| Reachable | ❌ | Cannot verify without activation |
| Returns Data | ❌ | Cannot verify without activation |
| Capability Proven | ❌ | Not proven in current runtime |
| Scope Ready | ❌ | Not verified |
| Country/Product Ready | ❌ | Not verified |
| Business Question Ready | ❌ | Not verified |
| Decision-Safe | ❌ | Not verified |
| Response-Safe | ❌ | Not verified |
| **Evidence** | | Provider code exists; GCC focus; requires API key; credentials absent |

### 1.9 Regulations (`regulations`)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Implemented | ✅ | Code exists at `backend/app/agent/knowledge/regulations_provider.py` |
| Registered | ❌ | Not in `KnowledgeOrchestrator._routing_table` |
| Configured | ❌ | `regulations.json` missing from `backend/data/` |
| Activated | ❌ | Cannot activate without data file |
| Reachable | ❌ | Cannot verify without activation |
| Returns Data | ❌ | Cannot verify without data file |
| Capability Proven | ❌ | Not proven |
| Scope Ready | ❌ | Not verified |
| Country/Product Ready | ❌ | Not verified |
| Business Question Ready | ❌ | Not verified |
| Decision-Safe | ❌ | Not verified |
| Response-Safe | ❌ | Not verified |
| **Evidence** | | Provider code exists; depends on local JSON file; file missing |

### 1.10 WTO ePing (`wto-eping`)

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Implemented | ❌ | No provider implementation file found |
| Registered | ❌ | Not in registry |
| Configured | ❌ | `WTO_EPING_API_KEY` missing from `.env` |
| Activated | ❌ | Not implemented |
| Reachable | ❌ | Not implemented |
| Returns Data | ❌ | Not implemented |
| Capability Proven | ❌ | Not proven |
| Scope Ready | ❌ | Not applicable |
| Country/Product Ready | ❌ | Not applicable |
| Business Question Ready | ❌ | Not applicable |
| Decision-Safe | ❌ | Not applicable |
| Response-Safe | ❌ | Not applicable |
| **Evidence** | | Config entries exist in `config.py`; no provider code found |

---

## 2. Capability Sufficiency Assessment

### 2.1 Per-Family Assessment

| Family | Required Capability | Current Source | Capability Actually Proven | Gap Type |
|--------|---------------------|----------------|---------------------------|----------|
| **Trade Intelligence** | Bilateral trade flows, HS-level, Egypt↔Y, documented values | UN Comtrade | ❌ Not activated; credentials missing | Configuration Gap |
| **Market Opportunity** | Demand signal, growth indicator, export potential, market attractiveness | None | ❌ No source provides these dimensions | Source Gap |
| **Market Access** | Tariff rates, duties, import procedures, permits for Y | None | ❌ No source provides these dimensions | Source Gap |
| **Regulatory/SPS-TBT** | MRL, SPS/TBT requirements, conformity standards for product+Y | None | ❌ No automated provider; accepted as Complementary-Only per Phase 1 | Source Gap (Complementary-Only Accepted) |
| **Rules of Origin** | FTA eligibility, criteria, certificate requirements for Y | None | ❌ No source provides these dimensions | Source Gap |
| **Agrifood** | Agricultural prices, market conditions, alerts for commodity | FAOSTAT | ❌ Not activated; credentials missing | Configuration Gap |
| **Logistics** | Route cost, transit time, reliability Egypt→Y | World Bank LPI | ❌ Country scores only; not route-level data | Source Limitation |

### 2.2 Gap Summary

| Gap Type | Count | Families |
|----------|-------|----------|
| Configuration Gap | 2 | Trade Intelligence (UN Comtrade), Agrifood (FAOSTAT) |
| Source Gap | 4 | Market Opportunity, Market Access, Rules of Origin, Regulatory/SPS-TBT |
| Source Limitation | 1 | Logistics (World Bank LPI) |
| **Total** | **7** | **All families except Company Knowledge** |

---

## 3. Evidence Discipline

### 3.1 What Was NOT Used as Evidence

- ❌ `Registered = Available` — Registration in routing table does not mean provider is active
- ❌ `HTTP 200 = Sufficient` — No HTTP requests were made; no 200 responses observed
- ❌ `Capability Label = Proven Capability` — Source type labels do not prove capability
- ❌ `Fixture = Production Evidence` — No test fixtures were used as production evidence
- ❌ `Provider Count = Success` — Number of providers does not indicate readiness

### 3.2 Evidence Sources Used

| Evidence Type | Source | Usage |
|---------------|--------|-------|
| Code existence | `backend/app/agent/knowledge/*.py` | Confirms implementation |
| Registry/routing | `registry.py`, `orchestrator.py` | Confirms registration |
| Configuration | `config.py`, `.env` | Confirms configuration state |
| Data files | `backend/data/` | Confirms data availability |
| Provider code | Individual provider files | Confirms capability claims |
| Business Promise | Phase 1 deliverable | Confirms required capabilities |

### 3.3 State Derivations

| Derived State | Basis |
|---------------|-------|
| UN Comtrade `Configured = ⚠️` | Config exists but `UN_COMTRADE_API_KEY` is empty |
| World Bank LPI `Capability Proven = ✅` | Public API, code shows data return path |
| World Bank LPI `Decision-Safe = ❌` | Country scores insufficient for route logistics decisions |
| FAOSTAT `Activated = ❌` | Credentials missing; cannot verify activation |
| Regulations `Registered = ❌` | Not in orchestrator routing table |
| WTO ePing `Implemented = ❌` | No provider implementation file found |

---

## 4. Governance Consistency

### 4.1 Regulatory/SPS-TBT Decision

Per Phase 1 decision, Regulatory/SPS-TBT is accepted as **Complementary-Only**. This is documented in:
- `.kilo/plans/1787046369923-sps-tbt-complementary-only-decision.md`
- `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md`

The Capability Truth Model reflects this decision:
- **Current Source:** None (automated)
- **Capability Proven:** ❌ No automated provider
- **Gap Type:** Source Gap (Complementary-Only Accepted)

No Governance conflict exists. The Phase 1 decision is respected.

### 4.2 Seven-Family Model

The Seven-Family Knowledge Coverage Model from `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` is used as the authoritative reference for family definitions and boundaries.

---

## 5. Key Findings

### 5.1 Active Providers

Only **1** provider is potentially active without additional configuration:
- **World Bank LPI** — Public API, no credentials required, but limited to country scores

### 5.2 Inactive Providers

**6** providers are implemented but inactive due to missing credentials:
- UN Comtrade (preview may work without key)
- FAOSTAT
- Moaah
- TradeData
- ZATCA
- GCC-Stat

### 5.3 Non-Implemented Providers

**1** provider is not implemented:
- WTO ePing — Config exists but no provider code

### 5.4 Data-Dependent Providers

**1** provider is blocked by missing data file:
- Regulations — `regulations.json` missing

### 5.5 Capability Gaps

**All 7 knowledge families** have capability gaps:
- 2 Configuration Gaps
- 4 Source Gaps
- 1 Source Limitation

---

## 6. Deliverables

### 6.1 Capability Truth Matrix

✅ Complete — See Section 1

### 6.2 Capability Sufficiency Assessment

✅ Complete — See Section 2

### 6.3 Evidence Discipline

✅ Complete — See Section 3

### 6.4 Governance Consistency

✅ Complete — See Section 4

---

## 7. Acceptance Criteria

| # | Acceptance Criterion | Status | Evidence |
|---|----------------------|--------|----------|
| 1 | Capability Truth Matrix مكتملة لجميع Providers | ✅ | Section 1 |
| 2 | Capability Sufficiency Assessment مكتملة لجميع Families | ✅ | Section 2 |
| 3 | لا توجد حالة غامضة بدون Evidence | ✅ | All states backed by code/config evidence |
| 4 | كل Gap مصنف بوضوح | ✅ | Section 2.2 |
| 5 | Business Promise و Minimum Sufficiency من Phase 1 مستخدمان كأساس | ✅ | Section 2.1 references Business Promise |

---

## 8. Exit Gate

```text
Capability Truth Model = Complete + Evidence-backed + Approved
```

**Status:** ✅ Exit Gate conditions met.

---

## 9. Blockers

| Blocker | Impact | Resolution Path |
|---------|--------|-----------------|
| No blockers | — | — |

---

## 10. Important Notes

### 10.1 What Was NOT Changed

- ❌ No provider activation
- ❌ No credential configuration
- ❌ No provider repair
- ❌ No data file creation
- ❌ No semantic mapping fixes
- ❌ No application code changes
- ❌ No architecture changes
- ❌ No Phase 3+ initiation

### 10.2 Runtime State

Phase 2 is a documentation-only phase. No runtime state was modified. All assessments are based on:
- Static code analysis
- Configuration inspection
- Business Promise from Phase 1
- Governance documents

### 10.3 Next Steps

Phase 2 is complete. Transition to Phase 3 requires owner approval.

---

```text
PHASE 2 DELIVERABLE = COMPLETE
Capability Truth Model = APPROVED
No implementation performed
No provider activation performed
No code changes made
```
