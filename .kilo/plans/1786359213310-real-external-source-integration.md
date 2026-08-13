# WP-38: Real External Source Integration — Knowledge Ingestion Pipeline Extension

**Work Package:** WP-38 — Knowledge Ingestion Pipeline Extension (Phase 2.2)  
**Status:** WP-38a Closed — WP-38b Approved — Ready for Execution  
**Authority:** `PLAN.md` (Master Roadmap v2.1) — Single Source of Truth  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Prerequisite:** WP-37 — File-based Regulations Ingestion Provider (`baseline-wp37-final`)  
**Date:** 2026-08-12  
**Plan Path:** `.kilo/plans/1786359213310-real-external-source-integration.md`  
**WP-38a First Provider:** Moaah API (closed 2026-08-13)  
**WP-38b First Provider Candidate:** TradeData API (approved 2026-08-13)  
**WP-38b Plan:** `.kilo/plans/1786559139127-wp38b-global-trade-intelligence-plan.md`

**Task 2 Deliverable:** `.kilo/plans/wp38-task2-moaah-adapter-spec.md`

---

## 1. Architectural Intent

WP-38 is the **parent Work Package** for introducing External Intelligence Sources into DEM's Knowledge Ingestion Pipeline. It is divided into four sequential Sub-WPs — **WP-38a, WP-38b, WP-38c, WP-38d** — each integrating a coherent group of sources. WP-38 itself preserves the Provider-Agnostic architecture, the existing `KnowledgeProviderRegistry`, and the `KNOWLEDGE_INGESTION_CONTRACT.md` boundaries established in WP-37.

**Goal:** Prove the Knowledge Ingestion Contract works end-to-end with real-world external data by implementing the first provider (WP-38a), then establish a **reusable integration pattern** that all subsequent Sub-WPs follow without re-architecting the Intelligence Layer.

**Important:** This WP does not prescribe a single specific provider across all Sub-WPs. The first provider in WP-38a is a decision to be made in Task 1 and approved by the Project Owner. Each Sub-WP has its own source selection, adapter design, and approval gates. No source is assumed to have an API without documented evidence.

---

## 2. Current State (Verified)

| Component | State | Evidence |
|-----------|-------|----------|
| `RegulationsKnowledgeProvider` | ✅ Implemented | `backend/app/agent/knowledge/regulations_provider.py` — reads local JSON |
| `KnowledgeProviderRegistry` | ✅ Existing | `backend/app/agent/knowledge/registry.py` — no changes |
| `KnowledgeProvider` ABC | ✅ Existing | `backend/app/agent/knowledge/provider.py` — no changes |
| Bootstrap wiring | ✅ Existing | `backend/main.py` — registers providers at startup |
| `config.py` pattern | ✅ Existing | `backend/app/core/config.py` — `REGULATIONS_FILE_PATH` added in WP-37 |
| `KNOWLEDGE_INGESTION_CONTRACT.md` | ✅ Approved | Governs ingestion boundaries and provider contract |
| WP-37 baseline | ✅ Closed | `baseline-wp37-final` — vertical slice verified |
| External source selection | ✅ Complete — G0/G1 Approved | Moaah approved as WP-38a First Provider by Project Owner in current work session |
| Moaah adapter spec | 📄 Created — Pending G2 Review | `.kilo/plans/wp38-task2-moaah-adapter-spec.md` |
| Moaah tests | ✅ Passing | `backend/tests/agent/test_mooadapter.py` — 9 tests passing |
| Moaah registration | ✅ Complete | `backend/main.py` — conditional registration in `lifespan()` |
| Moaah verification & evidence | 📄 Created — Pending G4 Review | `.kilo/plans/wp38-task7-verification-evidence-package.md` |

**Gap:** The Knowledge Ingestion Pipeline currently reads only local files. No external regulatory source is connected. The system cannot ingest live regulatory data.

### Approval Status

| Gate | Status | Evidence / Record |
|------|--------|-------------------|
| **G0 — WP-38 Plan Approval** | **Approved** | Project Owner approval obtained in current work session. |
| **G1 — Moaah Source Selection** | **Approved** | Project Owner approval obtained in current work session. Moaah is the WP-38a First Provider. |
| **G2 — Adapter Review** | **Approved** | Adapter specification approved: `.kilo/plans/wp38-task2-moaah-adapter-spec.md` |
| **G3 — Implementation Review** | **Approved** | Implementation matches adapter spec; Provider-Agnostic architecture verified. |
| **G4 — Verification** | **Approved** | Verification evidence package approved: `.kilo/plans/wp38-task7-verification-evidence-package.md` |
| **G5 — Closure** | **Approved** | Closure report created; baseline tagged `baseline-wp38a-final`; Owner Acceptance Certificate executed. |
| **G0 — WP-38b Plan Approval** | **Approved** | Project Owner approval of WP-38b plan obtained. |
| **G1 — TradeData Source Selection** | **Approved** | Project Owner approval obtained for TradeData API as WP-38b First Provider. |
| **G2 — Adapter Review** | **Pending** | Adapter specification not yet created. |
| **G3 — Implementation Review** | **Pending** | Implementation not yet started. |
| **G4 — Verification** | **Pending** | Verification not yet started. |
| **G5 — Closure** | **Pending** | Closure not yet started. |

**WP-38a Status:** Closed — All gates passed, baseline created, owner acceptance obtained.

**Next Sub-WP:** WP-38b — Global Trade Intelligence (approved; TradeData API first provider; G1 Approved)

---

## 3. External Intelligence Source Portfolio — Sub-WP Grouping

All twenty sources are retained. No source is deleted, downgraded, or merged. Each Sub-WP groups sources by functional domain to minimize duplication of evaluation effort while preserving architectural independence.

### WP-38a — Regulatory Core + Egypt

| # | Source | Role / Function | Data Type | Authority / Provenance | API / Access | Authentication | Cost / Licensing | Rate Limits | Reliability | Data Freshness | Coverage | Dependencies | Risks | Requirements | Tier | First / Future | Priority |
|---|--------|----------------|-----------|------------------------|--------------|----------------|------------------|-------------|-------------|----------------|----------|--------------|-------|--------------|------|----------------|----------|
| 1 | **Moaah API** (moaah.com) | Import/export regulations, HS codes, duty rates, licensing, restrictions | Regulations, HS codes, duties, restrictions, VAT | Aggregates official government sources | REST API, JSON | API key | Freemium — 100 calls/month free | Free tier: 100/month | Medium | Periodic | Global | Network access, Moaah account | Commercial product, rate limits on free tier, pricing TBD | `config.py` API key, retry logic, caching | A | **First Provider Candidate** | **1** |
| 2 | **Egypt Customs** (customs.gov.eg) | Egyptian customs regulations, ACID requirements, import/export procedures | Customs rules, procedures, restricted goods | Official Egyptian government | Web only (Arabic) | None | Free | N/A | Medium | Irregular | Egypt only | Network access, Arabic parsing | No documented REST API, political/organizational changes | Web scraping, translation, normalization | B | Future | 2 |
| 3 | **WTO TFA Database** (tfadatabase.org) | Trade Facilitation Agreement implementation, member commitments | TFA implementation categories, notifications, deadlines | Official WTO | Web portal + API portal | Free API key | Free | Generous | **High** | Monthly updates | WTO Members | Network access | Narrow scope (TFA only), limited REST automation | WTO API key, web scraping fallback | B | Future | 3 |
| 4 | **WTO Tariff & Trade Data** (ttd.wto.org) | Bound/applied tariffs, import data, trade statistics | Tariff lines, import notifications, trade stats | Official WTO | Web portal + downloads | Restricted terms | Free — restricted terms | N/A | **High** | Periodic | WTO Members | Network access, terms acceptance | Complex redistribution terms, primarily web UI | Manual download / scraping, licensing review | B | Future | 4 |
| 5 | **World Bank WITS** (wits.worldbank.org) | Trade statistics, tariffs, Egypt-specific trade indicators | Trade statistics, tariff profiles | World Bank | API + web portal | API key | Free | Unknown | Medium | Periodic | Egypt + global | Network access | Statistics focus not regulations, CSV/Excel primary format | CSV parsing, statistics normalization | A | Future | 5 |

### WP-38b — Global Trade Intelligence

| # | Source | Role / Function | Data Type | Authority / Provenance | API / Access | Authentication | Cost / Licensing | Rate Limits | Reliability | Data Freshness | Coverage | Dependencies | Risks | Requirements | Tier | First / Future | Priority |
|---|--------|----------------|-----------|------------------------|--------------|----------------|------------------|-------------|-------------|----------------|----------|--------------|-------|--------------|------|----------------|----------|
| 6 | **TradeData API** (tradedata.io) | Global trade statistics, shipment records, company intelligence | Trade flows, shipment records, company profiles | Commercial aggregator | REST API, JSON | API token | Paid — sandbox free | Unknown | High | Periodic | 200+ countries | Network access | Commercial dependency, pricing unknown | `config.py` token, retry logic | A | Future | 1 |
| 7 | **NBD Trade Data API** (data.nbd.ltd) | Global trade data, shipment records, company intelligence | Shipment records, company profiles, trade trends | Commercial aggregator | REST API, JSON | API key | Paid — pricing TBD | Unknown | Medium | Real-time claimed | 42+ countries | Network access, NBD account | Smaller coverage, commercial dependency | `config.py` API key, retry logic | A | Future | 2 |
| 8 | **PST.AG** (pst.ag) | Global customs tariffs, duty rates, trade agreements, sanctions, export control | Customs tariffs, FTAs, sanctions lists, export controls | Commercial global trade data provider | REST + SOAP + SFTP/FTP, JSON/XML/CSV/Excel | API key | Paid — enterprise sales | Unknown | Medium | Daily updates claimed | 160+ countries | Network access, PST.AG account | Large scope may be overkill, enterprise sales model, commercial dependency | `config.py` API key, multi-protocol client, caching | A | Future | 3 |
| 9 | **The Trade Hub** (thetradehub.eu) | EU customs intelligence, TARIC nomenclature, origin rules, CBAM | TARIC codes, origin rules, duty measures, EU regulations | Commercial EU customs platform | REST + SOAP, JSON/XML | API key | Paid — pricing TBD | Unknown | Medium | Periodic | EU / European trade | Network access, EU focus | EU-specific, complex API structure, commercial | `config.py` API key, SOAP client, REST client | A | Future | 4 |
| 10 | **USITC HTS** (hts.usitc.gov) | US Harmonized Tariff Schedule, export rules | Tariff schedule, export notices | Official US government | Web + JSON/CSV/Excel export | None | Free | N/A | **High** | Periodic updates | United States only | Network access | US-only scope, primarily tariff data not full regulations | JSON export parsing, US-only filter | B | Future | 5 |

### WP-38c — Jordan + UAE + Saudi

| # | Source | Role / Function | Data Type | Authority / Provenance | API / Access | Authentication | Cost / Licensing | Rate Limits | Reliability | Data Freshness | Coverage | Dependencies | Risks | Requirements | Tier | First / Future | Priority |
|---|--------|----------------|-----------|------------------------|--------------|----------------|------------------|-------------|-------------|----------------|----------|--------------|-------|--------------|------|----------------|----------|
| 11 | **Jordan Trade Portal** (tradeportal.customs.gov.jo) | Jordan trade regulations, import/export procedures, customs requirements | Customs rules, trade procedures, restricted goods | Official Jordanian government | Web portal — machine-readable access not documented | None | Free | N/A | Medium | Irregular | Jordan only | Network access | No documented REST API, political/organizational changes | Web scraping, translation, normalization | B | Future | 1 |
| 12 | **Jordan Customs — Integrated Tariff Inquiry** (customs.gov.jo) | Jordan customs tariff schedule, HS-based duties, customs classifications | Tariff schedule, HS codes, duty rates | Official Jordanian government | Web portal — machine-readable access not documented | None | Free | N/A | Medium | Periodic | Jordan only | Network access | No documented REST API, primarily web UI | Web scraping, HS mapping, normalization | B | Future | 2 |
| 13 | **UAE ICP — Central Customs Tariff System** (icp.gov.ae) | UAE customs regulations, tariffs, prohibited/restricted goods, import procedures | Customs rules, tariff schedule, restricted goods list | Official UAE government | Web portal — machine-readable access not documented | None | Free | N/A | Medium | Irregular | UAE only | Network access | No documented REST API, English/Arabic bilingual | Web scraping, translation, normalization | B | Future | 3 |
| 14 | **Saudi ZATCA — Open Data APIs** (zatca.gov.sa) | Saudi customs regulations, VAT, excise, trade procedures, e-invoicing | Customs rules, VAT rates, excise duties, trade notifications | Official Saudi government | Open data portals — API availability requires verification | API key (suspected) | Free (open data) | Unknown | Medium | Periodic | Saudi Arabia only | Network access, ZATCA account | API documentation not publicly verified, language (Arabic), rate limits unknown | API verification, Arabic parsing, normalization | A | Future | 4 |
| 15 | **Saudi ZATCA — Integrated Customs Tariff** (zatca.gov.sa) | Saudi customs tariff schedule, HS codes, duty rates, customs classifications | Tariff schedule, HS codes, duty rates | Official Saudi government | Web portal — machine-readable access not documented | None | Free | N/A | Medium | Periodic | Saudi Arabia only | Network access | No documented REST API, primarily web UI | Web scraping, HS mapping, normalization | B | Future | 5 |

### WP-38d — GCC Expansion

| # | Source | Role / Function | Data Type | Authority / Provenance | API / Access | Authentication | Cost / Licensing | Rate Limits | Reliability | Data Freshness | Coverage | Dependencies | Risks | Requirements | Tier | First / Future | Priority |
|---|--------|----------------|-----------|------------------------|--------------|----------------|------------------|-------------|-------------|----------------|----------|--------------|-------|--------------|------|----------------|----------|
| 16 | **GCC-Stat Data Portal / REST / SDMX APIs** (gccstat.org) | GCC-wide trade statistics, economic indicators, customs data, market intelligence | Trade statistics, economic indicators, customs aggregates | Official GCC statistical body | REST / SDMX APIs — availability requires verification | API key (suspected) | Free (open data) | Unknown | Medium | Periodic | GCC-wide | Network access | API documentation not publicly verified, multi-country aggregation | API verification, SDMX parsing, normalization | A | Future | 1 |
| 17 | **Qatar General Authority of Customs — Tariff & Restricted Goods** (customs.gov.qa) | Qatar customs regulations, tariff schedule, prohibited/restricted goods, import procedures | Customs rules, tariff schedule, restricted goods list | Official Qatari government | Web portal — machine-readable access not documented | None | Free | N/A | Medium | Irregular | Qatar only | Network access | No documented REST API, political/organizational changes | Web scraping, translation, normalization | B | Future | 2 |
| 18 | **Kuwait Customs — HS Tariff & Customs Rules** (customs.gov.kw) | Kuwait customs regulations, HS tariff schedule, duty rates, import/export procedures | Customs rules, tariff schedule, HS codes, duty rates | Official Kuwaiti government | Web portal — machine-readable access not documented | None | Free | N/A | Medium | Periodic | Kuwait only | Network access | No documented REST API, primarily web UI | Web scraping, HS mapping, normalization | B | Future | 3 |
| 19 | **Oman Customs — Bayan / Customs Tariff** (customs.gov.om) | Oman customs regulations, Bayan system, tariff schedule, import/export procedures | Customs rules, tariff schedule, Bayan data | Official Omani government | Web portal — machine-readable access not documented | None | Free | N/A | Medium | Irregular | Oman only | Network access | No documented REST API, primarily web UI | Web scraping, translation, normalization | B | Future | 4 |
| 20 | **Bahrain Customs Affairs — Ofoq / Seraj / HS & Regulations** (customs.gov.bh) | Bahrain customs regulations, Ofoq/Seraj systems, tariff schedule, HS codes | Customs rules, tariff schedule, HS codes, Ofoq/Seraj data | Official Bahraini government | Web portal — machine-readable access not documented | None | Free | N/A | Medium | Periodic | Bahrain only | Network access | No documented REST API, primarily web UI | Web scraping, HS mapping, normalization | B | Future | 5 |

### Tier Classification

| Tier | Criteria | Sources |
|------|----------|---------|
| **Tier A — Verified Machine-to-Machine / API** | REST/SOAP/SDMX API documented and accessible, or open data API portal with confirmed endpoints | 6 (TradeData), 7 (NBD), 8 (PST.AG), 9 (The Trade Hub), 14 (ZATCA Open Data — verification required), 16 (GCC-Stat REST/SDMX — verification required) |
| **Tier B — Official Structured / Queryable Source — API Verification Required** | Official government source with structured data but no documented REST API; access via web portal, download, or scraping | 2 (Egypt Customs), 3 (WTO TFA), 4 (WTO TTD), 5 (World Bank WITS — conditional API), 10 (USITC HTS), 11 (Jordan Trade Portal), 12 (Jordan Customs), 13 (UAE ICP), 15 (ZATCA Customs Tariff), 17 (Qatar Customs), 18 (Kuwait Customs), 19 (Oman Customs), 20 (Bahrain Customs) |

**Important:** Tier A/B classification is based on available public evidence. Sources marked "verification required" must have their API access confirmed during Source Evaluation (Task 1) of their respective Sub-WP before being treated as machine-readable. No source is assumed to have an API without documented evidence.

---

## 4. Source Coverage Matrices

### 4.1 Global Coverage Matrix (Sources 1–10)

| Functionality | TradeData | Moaah | WTO TFA | WTO TTD | Egypt Customs | USITC HTS | NBD | Trade Hub | WITS [Conditional] | PST.AG |
|---------------|-----------|-------|---------|---------|---------------|-----------|-----|-----------|-------------------|--------|
| **Regulations** | Partial | **Full** | Partial | Partial | **Full** | Partial | Partial | Partial | No | **Full** |
| **Tariffs / Duties** | Partial | **Full** | No | **Full** | Partial | **Full** | Partial | **Full** | Partial | **Full** |
| **Customs Procedures** | No | Partial | Partial | No | **Full** | No | No | Partial | No | **Full** |
| **HS Codes** | No | **Full** | No | No | No | **Full** | No | **Full** | No | **Full** |
| **Import/Export Restrictions** | No | **Full** | No | No | Partial | No | No | Partial | No | **Full** |
| **Licensing Requirements** | No | **Full** | No | No | Partial | No | No | No | No | **Full** |
| **Trade Agreements / FTAs** | No | Partial | **Full** | Partial | No | No | No | **Full** | No | **Full** |
| **Sanctions / Export Control** | No | No | No | No | No | No | No | No | No | **Full** |
| **Trade Statistics** | **Full** | Partial | No | Partial | No | No | **Full** | Partial | **Full** | Partial |
| **Company / Trader Intelligence** | **Full** | No | No | No | No | No | **Full** | No | No | Partial |
| **Provenance / Evidence** | High | **High** | **High** | **High** | **High** | **High** | High | Medium | High | **High** |
| **JSON API** | **Yes** | **Yes** | Partial | No | No | Partial | **Yes** | **Yes** | **Yes** | **Yes** |
| **Free Tier Available** | Yes | **Yes** | **Yes** | **Yes** | **Yes** | **Yes** | No | No | **Yes** | No |

> **[D] = Disqualified for WP-38a future provider consideration. Retained as future provider candidate.**

### 4.2 Regional Coverage Matrix — Middle East & GCC (Sources 11–20)

| Functionality | Jordan Trade Portal | Jordan Customs | UAE ICP | ZATCA Open Data | ZATCA Customs Tariff | GCC-Stat | Qatar Customs | Kuwait Customs | Oman Customs | Bahrain Customs |
|---------------|---------------------|----------------|---------|-----------------|----------------------|----------|---------------|----------------|--------------|-----------------|
| **Regulations** | **Full** | Partial | **Full** | Partial | No | No | **Full** | **Full** | **Full** | **Full** |
| **Customs Procedures** | **Full** | Partial | **Full** | Partial | No | No | **Full** | **Full** | **Full** | **Full** |
| **Tariffs** | Partial | **Full** | Partial | Partial | **Full** | Partial | Partial | **Full** | Partial | Partial |
| **HS Codes** | Partial | Partial | Partial | Partial | **Full** | Partial | Partial | Partial | Partial | Partial |
| **Restrictions / Prohibitions** | **Full** | Partial | **Full** | Partial | No | Partial | **Full** | Partial | Partial | **Full** |
| **Import/Export Procedures** | **Full** | Partial | **Full** | Partial | No | No | **Full** | **Full** | **Full** | **Full** |
| **Rules of Origin** | No | No | Partial | No | No | **Full** | No | No | No | No |
| **Trade Statistics** | Partial | No | Partial | No | No | **Full** | Partial | No | Partial | No |
| **Market Access** | Partial | No | Partial | Partial | No | Partial | Partial | No | Partial | Partial |
| **Provenance** | **High** | **High** | **High** | **High** | **High** | **High** | **High** | **High** | **High** | **High** |
| **Machine-Readable** | No | No | No | Requires verification | No | Requires verification | No | No | No | No |

---

## 5. Sub-WP Definitions

### 5.1 WP-38a — Regulatory Core + Egypt

**Scope:** Sources 1–5 (Moaah, Egypt Customs, WTO TFA, WTO TTD, World Bank WITS)  
**Domain:** Core regulatory intelligence for global export operations, with emphasis on Egypt and WTO frameworks.  
**First Provider:** Moaah API (approved by Project Owner in current work session). Moaah is the only candidate with verified Egypt coverage, a fully documented REST API, known licensing terms reviewed under DEM usage model, and a completed adapter implementation.  
**Tier Mix:** 1 Tier A (Moaah) + 4 Tier B (Egypt Customs, WTO TFA, WTO TTD, World Bank WITS conditional).  
**Sequencing within Sub-WP:** Moaah first. Remaining four are future providers evaluated sequentially after Moaah closure.  
**Shared Pattern Used:** Provider abstraction, Registry registration, provenance metadata, retry/backoff, config-driven settings — all established in WP-38a and reused by subsequent Sub-WPs.  
**Gates:** G0, G1, G2, G3, G4, G5 apply to WP-38a as the foundational Sub-WP.  
**Next Provider Gate (intra-WP-38a):** After Moaah closure, Egypt Customs evaluation begins; subsequent sources follow the same gate sequence.

### 5.2 WP-38b — Global Trade Intelligence

**Scope:** Sources 6–10 (TradeData, NBD, PST.AG, The Trade Hub, USITC HTS)  
**Domain:** Global trade statistics, shipment intelligence, sanctions/export control, EU customs intelligence, US tariff data.  
**First Provider Candidate:** TradeData API (highest practical value, confirmed JSON API, sandbox available).  
**Tier Mix:** 4 Tier A + 1 Tier B (USITC HTS).  
**Sequencing within Sub-WP:** TradeData first; remaining four follow after closure.  
**Dependency:** WP-38a must be fully closed before WP-38b begins.  
**Shared Pattern:** Reuses integration pattern from WP-38a; no re-architecture of Provider abstraction, Registry, provenance, or configuration.

### 5.3 WP-38c — Jordan + UAE + Saudi

**Scope:** Sources 11–15 (Jordan Trade Portal, Jordan Customs, UAE ICP, ZATCA Open Data, ZATCA Customs Tariff)  
**Domain:** Country-specific regulations and customs procedures for Jordan, UAE, and Saudi Arabia — DEM's highest-volume regional markets.  
**First Provider Candidate:** ZATCA Open Data (Tier A, pending API verification; if verification fails, reverts to Tier B and evaluation order is adjusted).  
**Tier Mix:** 1 Tier A (verification required) + 4 Tier B.  
**Sequencing within Sub-WP:** ZATCA Open Data first (if API verified); otherwise Jordan Trade Portal first. Remaining four follow after closure.  
**Dependency:** WP-38b must be fully closed before WP-38c begins.  
**Shared Pattern:** Reuses integration pattern from WP-38a/38b; web scraping adapters for Tier B sources follow the same provenance and graceful degradation rules.

### 5.4 WP-38d — GCC Expansion

**Scope:** Sources 16–20 (GCC-Stat, Qatar Customs, Kuwait Customs, Oman Customs, Bahrain Customs)  
**Domain:** GCC-wide trade statistics and country-specific regulations for Qatar, Kuwait, Oman, and Bahrain.  
**First Provider Candidate:** GCC-Stat (Tier A, pending API verification; if verification fails, reverts to Tier B and evaluation order is adjusted).  
**Tier Mix:** 1 Tier A (verification required) + 4 Tier B.  
**Sequencing within Sub-WP:** GCC-Stat first (if API verified); otherwise Qatar Customs first. Remaining four follow after closure.  
**Dependency:** WP-38c must be fully closed before WP-38d begins.  
**Shared Pattern:** Reuses integration pattern from previous Sub-WPs; SDMX parsing for GCC-Stat (if API verified) follows same adapter pattern as other structured formats.

---

## 6. Shared Integration Pattern (WP-38-Wide)

The following capabilities are designed **once** in WP-38a and reused by WP-38b, WP-38c, and WP-38d without modification:

1. **Provider Abstraction:** All external sources are accessed through `KnowledgeProvider` implementations. No source is accessed directly from routers, services, or DEM core.
2. **Registry-Only Registration:** All providers register in `KnowledgeProviderRegistry`. DEM core never references a specific provider.
3. **No DEM Core Coupling:** No modifications to `ReasoningEngine`, `TaskPlanner`, `ToolOrchestrator`, or any DEM component are permitted to accommodate a specific source.
4. **No Knowledge Graph Schema Changes:** External data is exposed via `KnowledgeProvider.query()` only. No direct writes to `knowledge_nodes` or `knowledge_edges`.
5. **No Contract Changes Without Independent Approval:** `KNOWLEDGE_INGESTION_CONTRACT.md` is immutable unless a separate Contract Amendment is approved by Project Owner.
6. **No Hardcoded Dependencies:** Provider implementations must not hardcode assumptions that prevent future source replacement (e.g., no hardcoded API endpoints, no source-specific logic in shared layers).
7. **Config-Driven:** All source-specific settings (endpoints, credentials, timeouts) are loaded from `config.py` or equivalent configuration.
8. **Replaceable:** Any provider can be replaced by a new implementation without redesigning the Intelligence Layer.
9. **Composable:** Multiple providers can coexist in the registry, each serving different functions or sources, without mutual dependency.
10. **Observable:** Each provider exposes its own provenance metadata, source ID, and health status through `get_sources()` and query responses.

**Standard Integration Pattern (applied uniformly across all Sub-WPs):**

```
Source Evaluation → Access Verification → Owner Approval → Adapter → Implementation → Verification → Evidence → Baseline
```

This pattern is executed once per provider within each Sub-WP. No Sub-WP modifies the pattern; it is reused as-is.

---

## 7. Target State

A new or extended provider that:
1. Connects to **one** real external regulatory source
2. Fetches data via HTTP/HTTPS or equivalent external mechanism
3. Transforms external records into the `KnowledgeProvider.query()` return shape
4. Maintains provenance/evidence/traceability per contract
5. Registers in `KnowledgeProviderRegistry` without DEM core changes
6. Degrades gracefully when the external source is unavailable
7. Is queryable by `ReasoningEngine` and `Trade Intelligence` without code changes

**WP-38 target state is achieved when:**
- WP-38a is fully closed with its first provider (Moaah) baselined.
- WP-38b, WP-38c, WP-38d are planned and approved but not yet executed.
- The reusable integration pattern is documented and proven.

---

## 8. Boundaries

### In Scope
- Selection and evaluation of sources within each Sub-WP
- Extension or creation of providers that fetch from chosen external sources (one provider per Sub-WP at a time)
- Transformation logic mapping external data → `query()` return shape
- Provenance/evidence/traceability metadata per `KNOWLEDGE_INGESTION_CONTRACT.md`
- Graceful degradation when external source is unavailable
- Configuration for external source endpoint/credentials via `config.py`
- Unit tests + integration tests + verification tests
- Documentation update after each provider implementation completion
- Definition and reuse of standard integration pattern in WP-38a

### Explicit Out of Scope
- Multiple external sources implemented simultaneously within a Sub-WP
- DEM core modifications
- Knowledge Graph schema changes
- Memory integration
- Avatar integration
- LLM orchestration
- Research/Retrieval lifecycle integration
- Frontend changes
- Database schema changes
- CSV support (JSON only, consistent with WP-37)
- Rate limiting or infrastructure work beyond provider-level retry/backoff
- PostgreSQL migration
- Multi-Agent Coordination
- Autonomous Export Operations
- Goal/Plan reasoning layers
- Creation of WP-39, WP-40, WP-41, or any new WP outside WP-38 Sub-WPs
- Modification of WP-40 or WP-41

---

## 9. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| WP-37 — File-based RegulationsProvider | ✅ Complete | `baseline-wp37-final`; provider pattern proven |
| `KnowledgeProvider` ABC | ✅ Existing | No changes |
| `KnowledgeProviderRegistry` | ✅ Existing | No changes |
| `KNOWLEDGE_INGESTION_CONTRACT.md` | ✅ Approved | Must not be modified |
| `config.py` pattern | ✅ Existing | New settings added for external source |
| External source availability | ⚠️ To be evaluated | Must be selected per Sub-WP |
| Network access in deployment | ⚠️ Environment-dependent | Must be handled gracefully |
| Project Owner approval | ⚠️ Required | Mandatory gate before each provider implementation |
| WP-38a closure | ⚠️ Required | WP-38b cannot start before WP-38a is closed |
| WP-38b closure | ⚠️ Required | WP-38c cannot start before WP-38b is closed |
| WP-38c closure | ⚠️ Required | WP-38d cannot start before WP-38c is closed |

**Blocking dependencies:** Project Owner approval at each Sub-WP's G1; sequential Sub-WP closure.

---

## 10. Preconditions

1. WP-37 is closed and baselined at `baseline-wp37-final`.
2. `KNOWLEDGE_INGESTION_CONTRACT.md` is approved and unchanged.
3. `KnowledgeProviderRegistry` is functional and tested.
4. No active technical or architectural blockers prevent adding a new provider.
5. Project Owner has approved the WP-38 plan itself before Task 1 begins.
6. Each Sub-WP's preceding Sub-WP is fully closed and baselined before the next Sub-WP begins.

---

## 11. Decision Gates

### WP-38-Level Gates

| Gate | Location | Requirement | Impact if Not Met |
|------|----------|-------------|-------------------|
| **G0 — WP Approval** | Before WP-38a Task 1 | Project Owner approves WP-38 plan | WP does not start |
| **WP-38 Closure** | After WP-38d completion | All Sub-WPs completed or explicitly deferred per approved roadmap | WP remains open |

### Per-Sub-WP Gates (applied to each provider within each Sub-WP)

| Gate | Location | Requirement | Impact if Not Met |
|------|----------|-------------|-------------------|
| **G1 — Source Selection** | After Sub-WP Task 1, before Task 2 | Project Owner approves selected external source | Sub-WP stops; no implementation begins |
| **G2 — Adapter Review** | After Sub-WP Task 2, before Task 3 | Adapter spec reviewed and approved | Sub-WP stops; implementation does not begin |
| **G3 — Implementation Review** | After Sub-WP Task 3, before Task 4 | Code review confirms Provider-Agnostic architecture and contract compliance | Sub-WP returns to Task 3 for fixes |
| **G4 — Verification** | After Sub-WP Task 7, before Closure | All tests pass, no regressions, evidence complete | Sub-WP returns to fix blockers |
| **G5 — Closure** | After Sub-WP Task 8 | All acceptance criteria met, baseline tagged | Sub-WP remains open |
| **Next Provider Gate** | After Sub-WP Closure | Project Owner approves next provider within same Sub-WP or next Sub-WP | Next provider/Sub-WP does not start |

**Next Provider Gate Principle:** No new provider may be introduced before the previous provider is fully closed, baselined, and approved by the Project Owner. No new Sub-WP may begin before the previous Sub-WP is fully closed. Each provider requires its own evaluation, approval, adapter design, implementation, verification, evidence, and baseline — following the standard integration pattern.

---

## 12. Provider-Agnostic Architecture Requirements

All external intelligence sources across all Sub-WPs must adhere to the following architectural constraints:

1. **Provider Abstraction:** All external sources are accessed through `KnowledgeProvider` implementations. No source is accessed directly from routers, services, or DEM core.
2. **Registry-Only Registration:** All providers register in `KnowledgeProviderRegistry`. DEM core never references a specific provider.
3. **No DEM Core Coupling:** No modifications to `ReasoningEngine`, `TaskPlanner`, `ToolOrchestrator`, or any DEM component are permitted to accommodate a specific source.
4. **No Knowledge Graph Schema Changes:** External data is exposed via `KnowledgeProvider.query()` only. No direct writes to `knowledge_nodes` or `knowledge_edges`.
5. **No Contract Changes Without Independent Approval:** `KNOWLEDGE_INGESTION_CONTRACT.md` is immutable unless a separate Contract Amendment is approved by Project Owner.
6. **No Hardcoded Dependencies:** Provider implementations must not hardcode assumptions that prevent future source replacement (e.g., no hardcoded API endpoints, no source-specific logic in shared layers).
7. **Config-Driven:** All source-specific settings (endpoints, credentials, timeouts) are loaded from `config.py` or equivalent configuration.
8. **Replaceable:** Any provider can be replaced by a new implementation without redesigning the Intelligence Layer.
9. **Composable:** Multiple providers can coexist in the registry, each serving different functions or sources, without mutual dependency.
10. **Observable:** Each provider exposes its own provenance metadata, source ID, and health status through `get_sources()` and query responses.

---

## 13. Tasks (Standard Integration Pattern — Applied Per Provider Per Sub-WP)

The following task sequence is applied uniformly to each provider within each Sub-WP. The pattern is defined once in WP-38a and reused by WP-38b, WP-38c, and WP-38d without modification.

### Task 1: Source Evaluation & Access Verification
- Evaluate the assigned source(s) against portfolio criteria: authority/provenance, regulatory relevance, machine-to-machine access, cost/licensing, rate limits, reliability, freshness, coverage, integration complexity.
- For Tier A sources: verify API access, document endpoints, test connectivity.
- For Tier B sources: verify web portal structure, identify scraping targets, document access constraints.
- Select **one** source as the recommended provider for this Sub-WP stage.
- **Gate G1:** Project Owner approval required before Task 2.
- **Deliverable:** Source Evaluation Report + Selected Source Specification + Access Verification Record

### Task 2: Define External Source Contract Adapter
- Define transformation rules from external source format → `KnowledgeProvider.query()` return shape
- Map external fields to internal metadata: `regulation_type`, `category`, `country`, `effective_date`, `source_url`, `version`
- Define confidence scoring rules for external data (may differ from WP-37 file-based rules)
- Define provenance metadata: source ID, fetch timestamp, record hash/version, retrieval status
- Define error handling strategy for each failure mode: network error, timeout, malformed data, auth failure, rate limit
- **Gate G2:** Adapter spec review and approval required before Task 3
- **Deliverable:** Adapter specification + confidence/provenance rules + error handling matrix

### Task 3: Implement External Source Provider
- **File:** `backend/app/agent/knowledge/regulations_external_provider.py` (new) or source-specific variant
- Implement HTTP client with retry/backoff (or web scraper for Tier B sources)
- Implement transformation logic per Task 2 spec
- Implement graceful degradation when source is unavailable
- Add configuration settings to `config.py` for endpoint/credentials
- Ensure Provider-Agnostic architecture per Section 12
- **Gate G3:** Code review confirms contract compliance and Provider-Agnostic architecture before Task 4
- **Deliverable:** New provider class, no DEM core changes

### Task 4: Bootstrap Registration
- **File:** `backend/main.py` (modification)
- Add import and registration call in `lifespan()` for external provider
- Wrap in try/except to match existing pattern
- **Deliverable:** Provider registered at startup

### Task 5: Unit Tests
- **File:** `backend/tests/agent/test_regulations_external_provider.py` (new) or source-specific test file
- Test cases:
  1. `get_sources()` returns expected structure with external source metadata
  2. `query()` transforms external data correctly per Task 2 spec
  3. `query()` handles network failure gracefully (returns empty results, no exception)
  4. `query()` handles malformed external data gracefully
  5. Confidence scores within 0.0–1.0 per Task 2 rules
  6. Provenance metadata populated correctly
  7. Configuration settings loaded correctly
  8. Retry/backoff behavior verified
- **Deliverable:** 8+ passing unit tests

### Task 6: Integration Tests
- **File:** `backend/tests/agent/test_regulations_external_integration.py` (new)
- Test cases:
  1. External provider registers successfully in `KnowledgeProviderRegistry`
  2. External provider is queryable via registry
  3. `ReasoningEngine` can query external provider through registry
  4. Existing providers still register after external provider
  5. Fallback to file-based provider when external source unavailable (if dual-mode)
  6. Graceful degradation does not crash application startup
- **Deliverable:** 6+ passing integration tests

### Task 7: Verification & Evidence
- Run full backend test suite
- Verify no regressions
- Verify no import cycles
- Capture evidence:
  - Test reports
  - Sample external data fetch logs (sanitized)
  - Transformation examples
  - Performance metrics
  - Source evaluation report
  - Access verification record (for Tier A sources)
- **Gate G4:** All verification criteria met before Task 8
- **Deliverable:** Verification report with evidence

### Task 8: Documentation
- Update `ENGINEERING_MEMORY.md` with provider completion entry
- Update `CURRENT_STATUS.md` with provider entry
- Update `CHANGELOG.md` with provider entry
- Update `.kilo/plans/` with provider closure report
- **Deliverable:** Updated docs

---

## 14. Sub-WP Sequencing & Scope

### Execution Model

| Sub-WP | Sources | First Provider | Execution Order | Prerequisite |
|--------|---------|----------------|-----------------|--------------|
| **WP-38a** | 1–5 | Moaah API | 1st | WP-37 closed |
| **WP-38b** | 6–10 | TradeData API | 2nd | WP-38a closed |
| **WP-38c** | 11–15 | ZATCA Open Data (if API verified; else Jordan Trade Portal) | 3rd | WP-38b closed |
| **WP-38d** | 16–20 | GCC-Stat (if API verified; else Qatar Customs) | 4th | WP-38c closed |

**Important:** 
- WP-38a is **Closed** — `baseline-wp38a-final` created.
- **WP-38b is the active next Sub-WP.** TradeData API is the approved first provider candidate. WP-38b becomes fully active after G0 plan approval and G1 TradeData source selection approval.
- WP-38c and WP-38d are **planned but deferred**. They become active only after WP-38b closure and explicit Project Owner approval to proceed.
- Within each Sub-WP, only **one** provider is implemented at a time. Remaining sources in the Sub-WP are future providers following the same gate sequence.
- If a Tier A source's API cannot be verified during Task 1, it reverts to Tier B and the evaluation order within the Sub-WP is adjusted accordingly.

---

## 15. Acceptance Criteria

### Per-Provider Acceptance Criteria (applied to each provider in each Sub-WP)

| ID | Criterion | Verification | Gate |
|----|-----------|--------------|------|
| AC-38.X.0 | Project Owner approved Sub-WP plan | Approval record | G0 |
| AC-38.X.1 | External source selected and documented | Source evaluation report approved | G1 |
| AC-38.X.2 | Adapter specification defined and approved | Adapter spec document approved | G2 |
| AC-38.X.3 | External provider implements `KnowledgeProvider` interface | Type check + tests | G3 |
| AC-38.X.4 | `get_sources()` returns valid metadata with provenance | Unit test | — |
| AC-38.X.5 | `query()` transforms external data to contract shape | Unit test | — |
| AC-38.X.6 | Confidence scores are within 0.0–1.0 per Task 2 rules | Unit test | — |
| AC-38.X.7 | Provider registers successfully in `KnowledgeProviderRegistry` | Integration test | — |
| AC-38.X.8 | Provider is queryable via registry without DEM core changes | Integration test | — |
| AC-38.X.9 | `ReasoningEngine` can query provider through registry | Integration test | — |
| AC-38.X.10 | Graceful degradation when external source unavailable | Integration test | — |
| AC-38.X.11 | All existing tests pass (no regressions) | Full pytest run | G4 |
| AC-38.X.12 | No DEM core files modified | Code review / git diff | G4 |
| AC-38.X.13 | No database schema changes | Code review / git diff | G4 |
| AC-38.X.14 | Documentation updated | Doc review | G5 |
| AC-38.X.15 | Baseline tagged | `baseline-wp38-{source}-final` exists | G5 |

*(X = Sub-WP letter: a, b, c, d)*

### WP-38-Level Acceptance Criteria

| ID | Criterion | Verification | Gate |
|----|-----------|--------------|------|
| AC-38.0 | Project Owner approved WP-38 plan | Approval record | G0 |
| AC-38.1 | WP-38a first provider implemented and baselined | Baseline `baseline-wp38a-final` exists | WP-38a G5 |
| AC-38.2 | Shared integration pattern documented and proven | Pattern document + WP-38a evidence | WP-38a G5 |
| AC-38.3 | WP-38b, WP-38c, WP-38d scoped and approved | Sub-WP plans approved | WP-38 Closure |
| AC-38.4 | No regressions in existing tests across all executed Sub-WPs | Full pytest run | Per-Sub-WP G4 |
| AC-38.5 | No DEM core, Knowledge Graph schema, or Contract modifications | Code review / git diff | Per-Sub-WP G4 |
| AC-38.6 | All executed Sub-WPs have complete evidence packages | Evidence review | Per-Sub-WP G5 |
| AC-38.7 | No new WPs created outside WP-38 Sub-WPs | Plan review | WP-38 Closure |
| AC-38.8 | WP-40 and WP-41 untouched | Plan review | WP-38 Closure |

---

## 16. Evidence Requirements

### Per-Provider Evidence (applied to each provider in each Sub-WP)

| Phase | Required Evidence |
|-------|-------------------|
| Task 1 | Source Evaluation Report with candidate comparison matrix (all sources in Sub-WP), selected source specification, access verification record (Tier A), Project Owner approval record |
| Task 2 | Adapter specification document, field mapping table, confidence/provenance rules, error handling matrix, Project Owner approval record |
| Task 3 | Code review record, Provider-Agnostic architecture checklist, configuration settings documented |
| Task 4 | Bootstrap registration code snippet, startup log confirmation |
| Task 5 | Unit test report (8+ tests passing), coverage for new provider |
| Task 6 | Integration test report (6+ tests passing), registry compatibility verified |
| Task 7 | Full test suite report (0 regressions), sample fetch logs (sanitized), transformation examples, performance metrics, access verification record |
| Task 8 | Updated docs: `ENGINEERING_MEMORY.md`, `CURRENT_STATUS.md`, `CHANGELOG.md`, closure report |

### WP-38-Level Evidence

| Phase | Required Evidence |
|-------|-------------------|
| WP-38a Closure | Complete evidence package for Moaah, shared integration pattern document |
| WP-38b–38d Planning | Sub-WP plans, source evaluation reports, approval records |
| WP-38 Closure | All Sub-WP evidence packages, confirmation that WP-40 and WP-41 are untouched |

---

## 17. Failure / Abort Conditions

| Condition | Action |
|-----------|--------|
| No suitable external source found in Sub-WP Task 1 | Sub-WP aborts; report to Project Owner; WP-38 continues with next Sub-WP if approved |
| Project Owner rejects selected source at G1 | Sub-WP stops; no implementation begins; WP-38 continues with next Sub-WP if approved |
| External source becomes unavailable during evaluation | Re-evaluate or abort Sub-WP |
| Adapter spec rejected at G2 | Return to Task 2 for revision |
| Code review fails at G3 | Return to Task 3 for fixes |
| Regressions detected at G4 | Fix blockers before proceeding |
| Contract modification requested | Sub-WP aborts; contract is immutable |
| DEM core modification requested | Sub-WP aborts; DEM core is out of scope |
| Multiple sources requested in single Sub-WP stage | Sub-WP aborts; additional sources require separate stages within same Sub-WP per standard pattern |
| Next Provider requested before previous closure | Blocked by Next Provider Gate; requires separate approval |
| Next Sub-WP requested before previous Sub-WP closure | Blocked by Sub-WP sequence gate; requires Project Owner approval to proceed |
| Tier A API verification fails | Source reverts to Tier B; evaluation order within Sub-WP adjusted; Project Owner informed |
| WP-39, WP-40, WP-41 creation requested | Blocked; WP-38 is the only WP for external intelligence sources |

---

## 18. Definition of Done

### Per-Sub-WP Definition of Done

A Sub-WP is done when:
1. All 8 Tasks completed for the first provider in that Sub-WP
2. All 5 Gates passed (G1–G5) for the first provider
3. All 15 Acceptance Criteria met (AC-38.X.0–AC-38.X.15) for the first provider
4. No regressions in existing tests
5. No DEM core, Knowledge Graph schema, or Contract modifications
6. Evidence package complete
7. Documentation updated
8. Baseline tagged: `baseline-wp38-{sub}-final`

### WP-38 Definition of Done

WP-38 is done when:
1. WP-38a is fully closed and baselined at `baseline-wp38a-final`
2. Shared integration pattern is documented and proven
3. WP-38b, WP-38c, WP-38d are scoped, planned, and approved by Project Owner (even if not yet executed)
4. All executed Sub-WPs have passed their gates
5. No regressions in existing tests across all executed Sub-WPs
6. No DEM core, Knowledge Graph schema, or Contract modifications
7. Evidence packages complete for all executed Sub-WPs
8. WP-40 and WP-41 remain untouched
9. No new WPs created outside WP-38 Sub-WPs

**Important:** WP-38 closure does not require execution of WP-38b, WP-38c, or WP-38d. It requires only that those Sub-WPs are properly scoped, planned, and approved for future execution. The remaining 15 sources remain future providers within their respective Sub-WPs.

---

## 19. Closure Criteria

### Per-Sub-WP Closure Criteria

| Criterion | Requirement |
|-----------|-------------|
| Implementation | External provider implemented and registered |
| Tests | 8+ unit tests + 6+ integration tests passing |
| Regression | 0 regressions in existing test suite |
| Evidence | Complete evidence package per Section 16 |
| Documentation | All governance docs updated |
| Baseline | `baseline-wp38-{sub}-final` tag created |
| Project Owner Acceptance | Formal acceptance of closure report |

### WP-38 Closure Criteria

| Criterion | Requirement |
|-----------|-------------|
| WP-38a | Closed and baselined at `baseline-wp38a-final` |
| Shared Pattern | Documented and proven |
| WP-38b–38d | Scoped, planned, and approved |
| Evidence | All executed Sub-WP evidence packages complete |
| WP-40/41 | Untouched |
| No New WPs | Confirmed |
| Project Owner Acceptance | Formal acceptance of WP-38 closure report |

---

## 20. Baseline

### Per-Sub-WP Baselines

| Sub-WP | Baseline Tag | Commit | Date |
|--------|-------------|--------|------|
| WP-38a | `baseline-wp38a-final` | To be created at closure | TBD |
| WP-38b | `baseline-wp38b-final` | To be created at closure | TBD |
| WP-38c | `baseline-wp38c-final` | To be created at closure | TBD |
| WP-38d | `baseline-wp38d-final` | To be created at closure | TBD |

### WP-38 Baseline

| Field | Value |
|-------|-------|
| Baseline Tag | `baseline-wp38-final` |
| Commit | To be created at WP-38 closure |
| Date | TBD |

---

## 21. Governance Notes

- **Contract preservation:** `KNOWLEDGE_INGESTION_CONTRACT.md` must not be modified.
- **Provider-Agnostic architecture:** New provider must not hardcode assumptions that prevent future source replacement.
- **No DEM core changes:** All integration must happen through `KnowledgeProviderRegistry`.
- **Source selection gate:** Each provider requires Project Owner approval before implementation begins. This is a hard gate, not a recommendation.
- **One provider at a time:** Each Sub-WP integrates exactly one provider at a time. Remaining sources in the Sub-WP are future providers requiring independent evaluation, approval, and implementation.
- **No foregone conclusions:** The specific external provider for each Sub-WP is NOT decided in this plan. It is a decision to be made in Task 1 of each Sub-WP and approved by the Project Owner.
- **Master Roadmap for External Intelligence:** This plan documents all 20 evaluated sources across 4 Sub-WPs. WP-38a implements only the first provider. Remaining sources are future providers within their respective Sub-WPs.
- **Next Provider Gate:** No subsequent provider may be introduced before the previous provider is fully closed and baselined.
- **Next Sub-WP Gate:** No subsequent Sub-WP may begin before the previous Sub-WP is fully closed and baselined.
- **Sub-WP Sequence:** WP-38a → WP-38b → WP-38c → WP-38d. This sequence is fixed unless Project Owner approves an explicit amendment.
- **Shared Pattern:** The integration pattern is defined once in WP-38a and reused by all subsequent Sub-WPs. No Sub-WP modifies the pattern.
- **Tier A/B Classification:** Tier A sources have verified or highly likely API access. Tier B sources are official government portals without documented REST APIs. Tier A/B status does not guarantee implementation order; practical value and regional relevance remain primary sequencing criteria.
- **API Verification Requirement:** Sources marked "verification required" in Tier A must have their API access confirmed during Task 1 evaluation of their respective Sub-WP before being treated as machine-readable. If API access cannot be verified, they revert to Tier B for implementation planning purposes.
- **WP-40/41 Preservation:** This plan does not modify, reference, or depend on WP-40 or WP-41. WP-40 and WP-41 remain unchanged.
- **No New WPs:** No WP-39, WP-40, WP-41, or any other WP is created as part of this plan. All external intelligence integration happens within WP-38 Sub-WPs.
- **WP-38 Scope:** WP-38 covers only External Intelligence Sources integration. It does not cover Avatar, Reasoning, Planning, Multi-Agent, Autonomous Export Operations, or Research lifecycle integration.

---

*Plan Status: Draft — G0/G1 Approved — G2 Pending Review — Moaah Approved as First Provider*
