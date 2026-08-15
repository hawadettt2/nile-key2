# External Knowledge Portfolio Re-Evaluation Plan

**Work Package:** Portfolio Re-Evaluation — Knowledge Coverage Optimization  
**Date:** 2026-08-14  
**Status:** Approved — G0 Approved — Ready for Evaluation  
**Authority:** `PLAN.md` (Master Roadmap v2.1) — Single Source of Truth  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Prerequisite:** WP-38a, WP-38b, WP-38c, WP-38d closed and baselined  
**Plan Path:** `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md`

---

## 1. Governance Decision

| Decision | Value |
|----------|-------|
| Evaluation Principle | **Knowledge Coverage > Provider Count** |
| Strategic Priority | **Agrifood Intelligence** — highest business priority, cross-cutting, not system boundary |
| Provider Ceiling | **4–6 providers maximum** per parent plan architectural guidance |
| Next Action | Portfolio re-evaluation before any new provider implementation |

**Note:** This plan does not create WP-38e or any new Work Package. It defines the evaluation framework and decision criteria for future portfolio optimization.

---

## 2. Current Portfolio Status

### 2.1 Implemented Providers (Baseline)

| Provider | Sub-WP | Status | Families Covered | Intelligence Type |
|----------|--------|--------|------------------|-------------------|
| MoaahExternalSourceAdapter | WP-38a | Closed | Regulatory, Market Access | Global/Egypt-focused |
| TradeDataExternalSourceAdapter | WP-38b | Closed | Trade Intelligence, Market Opportunity | 200+ countries |
| ZatcaExternalSourceAdapter | WP-38c | Closed | Regulatory, Market Access | Saudi Arabia |
| GccstatExternalSourceAdapter | WP-38d | Closed | Trade Intelligence, Rules of Origin | GCC-wide |

**Total:** 5 implemented providers.

### 2.2 Remaining Candidates

| Sub-WP | Remaining Sources | Tier A | Tier B | Status |
|--------|-------------------|--------|--------|--------|
| WP-38a | Egypt Customs, WTO TFA, WTO Tariff, World Bank WITS | 1 (WITS conditional) | 3 | Planned/Future |
| WP-38b | NBD Trade Data, PST.AG, The Trade Hub, USITC HTS | 3 | 1 | Planned/Future |
| WP-38c | Jordan Trade Portal, Jordan Customs, UAE ICP, Saudi ZATCA Tariff | 0 | 4 | Planned/Future |
| WP-38d | Qatar Customs, Kuwait Customs, Oman Customs, Bahrain Customs | 0 | 4 | Planned/Future |

---

## 3. Seven-Family Knowledge Coverage Model

The following seven families are the **fixed Knowledge Coverage Requirements** for DEM. Each family is evaluated independently; no family is required to map to a single provider.

| # | Knowledge Family | Description | Current Coverage | Gap |
|---|------------------|-------------|------------------|-----|
| 1 | **Trade Intelligence** | Trade statistics, shipment records, company profiles, trade flows | ✅ Partial (TradeData, GCC-Stat) | Official global stats missing |
| 2 | **Market Opportunity** | Export potential, market demand, growth segments | ⚠️ Indirect (TradeData shipments, GCC-Stat economic) | No dedicated opportunity intelligence |
| 3 | **Market Access** | Tariffs, duties, preferential rates, NTMs, market entry requirements | ⚠️ Partial (Moaah, ZATCA) | No dedicated tariff DB |
| 4 | **Regulatory / SPS / TBT** | Sanitary/phytosanitary requirements, technical barriers, product standards | ❌ None | **Critical gap** |
| 5 | **Rules of Origin** | FTA utilization, origin criteria, certificate of origin requirements | ⚠️ Partial (GCC-Stat aggregates) | No dedicated rules of origin DB |
| 6 | **Agrifood Intelligence** | Agricultural trade, commodity prices, food safety, export markets for agrifood | ❌ None | **Critical gap — highest business priority** |
| 7 | **Logistics / Market Execution** | Shipping performance, supply chain reliability, customs efficiency | ❌ None | No logistics intelligence |

---

## 4. Coverage Scorecard (Evidence-Based)

Scores are derived from verified provider capabilities and documented gaps. No invented values.

| Family | Score (0-10) | Evidence | Inference |
|--------|--------------|----------|-----------|
| Trade Intelligence | 7/10 | TradeData covers 200+ countries shipment records; GCC-Stat covers GCC aggregates | Missing UN Comtrade official global stats |
| Market Opportunity | 4/10 | TradeData provides shipment records; GCC-Stat provides economic indicators | No dedicated opportunity intelligence source |
| Market Access | 5/10 | Moaah provides duty rates and licensing; ZATCA provides Saudi tariff data | No dedicated global tariff database |
| Regulatory / SPS / TBT | 0/10 → 9/10 with proposed additions | No implemented provider covers SPS/TBT; proposed WTO ePing + WTO TFA Database cover majority of global SPS/TBT notifications and trade facilitation requirements | 9/10 rather than 10/10 because complete coverage would require additional national/regional sources beyond current scope |
| Rules of Origin | 3/10 | GCC-Stat provides GCC aggregates | No dedicated rules of origin database |
| Agrifood Intelligence | غير مؤكدة | FAOSTAT implemented but live coverage impact not verified; no production metrics available | Impact pending verification — highest business priority |
| Logistics / Market Execution | 0/10 | No implemented provider covers logistics intelligence | Complete gap |

**Overall Portfolio Coverage:** ~2.7/10 base (Agrifood impact uncertain) — functional but incomplete for Agrifood focus.

**Evidence Basis:** Verified from implemented provider test suites (55/55 tests passed (4 original) + FAOSTAT implementation verified), adapter specifications, and documented API capabilities.

---

## 5. Agrifood Cross-Cutting Priority Model

Agrifood Intelligence is a **cross-cutting strategic priority**, not a separate isolated family. It must be evaluated across all seven families with an agricultural lens.

### 5.1 Agrifood Relevance Matrix

| Knowledge Family | Agrifood Relevance | Current Agrifood Coverage | Required Capability |
|------------------|-------------------|---------------------------|---------------------|
| Trade Intelligence | **Very High** — agricultural trade flows | ❌ None | FAOSTAT trade statistics |
| Market Opportunity | **Very High** — export market identification for agrifood | ❌ None | ITC Export Potential Map |
| Market Access | **Very High** — tariffs and NTMs for food products | ⚠️ Partial (Moaah) | ITC Market Access Map |
| WTO ePing | Regulatory / SPS/TBT | Critical | Very High (WTO) | ❌ No verifiable public REST endpoint; G1 BLOCKED | **Candidate — G1 Blocked** |
| Rules of Origin | **High** — FTA utilization for agricultural products | ⚠️ None | ITC Rules of Origin Facilitator |
| Logistics / Market Execution | **High** — cold chain, perishable goods logistics | ❌ None | World Bank LPI |
| Trade Intelligence (complementary) | **High** — commodity prices, production data | ❌ None | FAOSTAT, FAO Food Price Index |

### 5.2 Agrifood Coverage Requirements

| Capability | Required Source | Rationale |
|------------|----------------|-----------|
| Global agricultural trade statistics | FAOSTAT | Official FAO data, 245+ countries, 1961-present |
| Commodity prices / market trends | FAO Food Price Index | Monthly price monitoring for key commodities |
| SPS/TBT notifications for agrifood | WTO ePing | Critical for export compliance — food safety standards, phytosanitary requirements |
| Export potential for agrifood | ITC Export Potential Map | Identifies high-potential markets for agricultural exports |
| Market access requirements for agrifood | ITC Market Access Map | Tariffs, NTMs, and regulatory requirements for food products |
| Trade facilitation for agrifood | WTO TFA Database | Implementation status of trade facilitation measures affecting agricultural trade |

**Agrifood Coverage Target:** 8/10 with FAOSTAT + ePing + ITC tools

---

## 6. Source Classification Framework

### 6.1 Implemented Providers (5)

**Evidence:** Verified from baseline tags, test suites, and git history.

| Provider | Sub-WP | Status | Families Covered |
|----------|--------|--------|------------------|
| MoaahExternalSourceAdapter | WP-38a | Closed | Regulatory, Market Access |
| TradeDataExternalSourceAdapter | WP-38b | Closed | Trade Intelligence, Market Opportunity |
| ZatcaExternalSourceAdapter | WP-38c | Closed | Regulatory, Market Access |
| GccstatExternalSourceAdapter | WP-38d | Closed | Trade Intelligence, Rules of Origin |

### 6.2 Provider Candidates

**Definition:** Sources that can become providers **only if** they satisfy all Provider Admission Criteria (Section 11) and pass G1 Gate.

**Classification Rule:** A source is a Provider Candidate only if it has documented, accessible REST/SDMX/JSON API or confirmed machine-readable access. Web-only sources are **not** Provider Candidates.

| Source | Families Covered | Agrifood Relevance | Officiality | API/Machine Readability | Admission Status |
|--------|------------------|--------------------|-------------|------------------------|------------------|
| UN Comtrade | Trade Intelligence | Low | Very High (UN) | ✅ Free API | **Candidate** |

| WTO Tariff DB | Market Access | Medium | Very High (WTO) | ⚠️ API key required | **Candidate** |
| WTO TFA Database | Trade Facilitation | Medium | Very High (WTO) | ❌ No verifiable public REST endpoint; G1 BLOCKED | **Candidate — G1 Blocked** |
| World Bank LPI | Logistics / Market Execution | Medium | High (World Bank) | ✅ Free API | **Candidate** |
| UNCTADstat | Trade Intelligence | Low | High (UN) | ⚠️ SDMX | **Candidate** |
| IMF IMTS | Trade Intelligence | Low | High (IMF) | ⚠️ API | **Candidate** |
| **FAO Food Price Index** | **Market Opportunity, Agrifood** | **Very High** | **Very High (FAO)** | **✅ API (documented)** | **Candidate P2** |

**Note:** Codex and IPPC are **web-only** (no documented REST/SDMX/JSON API). They do **not** meet Provider Admission Criteria. They are classified as Complementary Knowledge Sources (Section 6.3), not Provider Candidates.

### 6.3 Complementary Knowledge Sources / Tools

**Definition:** Sources that provide useful knowledge but do **not** currently meet Provider Admission Criteria. These are tracked for future evaluation if machine-readable access becomes available.

| Source | Families Covered | Agrifood Relevance | Access Type | Status |
|--------|------------------|--------------------|-------------|--------|
| Codex (FAO/WHO) | Regulatory / SPS/TBT | Critical (food safety) | Web only | **Complementary** |
| WTO ePing | Regulatory / SPS/TBT | Critical (food safety, phytosanitary) | Web portal + XLSX; no verifiable public REST API | **Complementary** |
| IPPC (FAO) | Regulatory / SPS/TBT | Critical (plant health) | Web only | **Complementary** |
| ITC Market Access Map | Market Access | High | Web + bulk download | **Complementary** |
| ITC Export Potential Map | Market Opportunity | High | Web only | **Complementary** |
| ITC Trade Map | Trade Intelligence, Market Access | Medium | Web + download | **Complementary** |
| ITC Rules of Origin Facilitator | Rules of Origin | Medium | Web only | **Complementary** |
| WTO I-TIP | Regulatory, Market Access | Medium | Web + API (limited) | **Complementary** |
| Access2Markets | Market Access | Medium | Web only | **Complementary** |
| Egypt Customs | Regulatory | Low | Web only | **Complementary** |
| Jordan Trade Portal | Regulatory | Low | Web only | **Complementary** |
| Jordan Customs | Regulatory | Low | Web only | **Complementary** |
| UAE ICP | Regulatory | Low | Web only | **Complementary** |
| Saudi ZATCA Tariff | Market Access | Low | Web only | **Complementary** |
| Qatar Customs | Regulatory | Low | Web only | **Complementary** |
| Kuwait Customs | Regulatory | Low | Web only | **Complementary** |
| Oman Customs | Regulatory | Low | Web only | **Complementary** |
| Bahrain Customs | Regulatory | Low | Web only | **Complementary** |
| NBD Trade Data | Trade Intelligence | Low | ✅ REST | **Deprioritized** (similar to TradeData, lower coverage) |
| PST.AG | Regulatory, Market Access | Low | ✅ Multi-protocol | **Deprioritized** (enterprise sales; overkill) |
| The Trade Hub | Market Access | Low | ✅ REST | **Deprioritized** (EU-only; limited GCC relevance) |
| USITC HTS | Market Access | Low | ⚠️ Web export | **Deprioritized** (web export; limited value) |
| World Bank WITS | Trade Intelligence | Low | ⚠️ Conditional API | **Deprioritized** (conditional; similar to TradeData) |

---

## 7. Seven-Family Coverage Matrix (Current + Proposed)

### 7.1 Coverage by Family

| Knowledge Family | Current Score | Proposed Additions | Target Score | Gap Status |
|------------------|---------------|-------------------|--------------|------------|
| Trade Intelligence | 7/10 | UN Comtrade, FAOSTAT | 9/10 | P1 |
| Market Opportunity | 4/10 | FAOSTAT | 6/10 | P2 |
| Market Access | 5/10 | WTO Tariff DB | 8/10 | P1 |
| Regulatory / SPS / TBT | 0/10 | WTO ePing, WTO TFA Database | 9/10 | **P0** |
| Rules of Origin | 3/10 | — | 3/10 | P3 |
| **Agrifood Intelligence** | **غير مؤكدة** | **FAOSTAT** | **غير مؤكدة** | **P0** |
| Logistics / Market Execution | 0/10 | World Bank LPI | 5/10 | P3 |

**Overall Portfolio Coverage:** ~2.7/10 → ~7.1/10

### 7.2 Agrifood Cross-Cutting Coverage

| Family | Agrifood Gap | Proposed Source | Agrifood Value |
|--------|--------------|-----------------|----------------|
| Trade Intelligence | Agricultural trade flows missing | FAOSTAT | **Very High** |
| Market Opportunity | No ag export opportunity data | FAO Food Price Index (candidate) | **Very High** |
| Market Access | No ag-specific tariff/NTM data | WTO Tariff DB (complementary via ITC Map) | **High** |
| Regulatory / SPS/TBT | No SPS/TBT for food products | WTO ePing + WTO TFA Database | **Critical** |
| Rules of Origin | No ag-specific origin rules | ITC Rules of Origin Facilitator (complementary) | **Medium** |
| Logistics | No ag-specific logistics data | World Bank LPI (complementary) | **Medium** |

**Note:** Agrifood Intelligence is a strategic cross-cutting priority. It does not impose a future boundary on DEM, which must remain scalable to serve all high-quality Egyptian exports globally.

---

## 8. Multi-Family Source Evaluation

### 8.1 Evaluation Criteria

Each candidate is evaluated against:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Knowledge Coverage | 30% | Which families does this source cover? |
| Agrifood Relevance | 20% | Does it support agricultural export intelligence? |
| Officiality | 15% | Is it an official source (government, IGO, reputable international org)? |
| API/Machine Readability | 15% | REST/SDMX/JSON API or confirmed machine-readable access |
| Uniqueness | 10% | Does it provide unique intelligence not available from other sources? |
| Freshness | 5% | Update frequency and data latency |
| Maintenance Burden | 5% | Integration complexity, ongoing maintenance cost |

### 8.2 Current Implemented Providers Re-Evaluation

| Provider | Families Covered | Agrifood Relevance | Officiality | API | Uniqueness | Verdict |
|----------|------------------|--------------------|-------------|-----|------------|---------|
| **Moaah** | Regulatory, Market Access | Medium (Egypt-focused) | High (aggregates official) | ✅ REST | Medium | **Keep** |
| **TradeData** | Trade Intelligence, Market Opportunity | Low (commercial aggregates) | Medium (commercial) | ✅ REST | Medium | **Keep** |
| **ZATCA** | Regulatory, Market Access | Low (Saudi customs) | High (official Saudi) | ✅ REST | High (Saudi-specific) | **Keep** |
| **GCC-Stat** | Trade Intelligence, Rules of Origin | Medium (GCC aggregates) | High (official GCC) | ✅ SDMX/REST | High (GCC-wide) | **Keep** |

**Evidence:** All 5 providers are implemented, tested (55/55 tests passed (4 original) + FAOSTAT implementation verified), and baselined with baseline tags.

### 8.3 Provider Candidates Re-Evaluation

| Source | Families Covered | Agrifood Relevance | Officiality | API | Uniqueness | Verdict |
|--------|------------------|--------------------|-------------|-----|------------|---------|
| UN Comtrade | Trade Intelligence | Low | Very High (UN) | ✅ Free API | Very High (official global stats) | **Candidate P1** |

| WTO Tariff DB | Market Access | Medium | Very High (WTO) | ⚠️ API key | High (dedicated tariffs) | **Candidate P1** |
| WTO TFA Database | Regulatory | Medium | Very High (WTO) | ✅ Free API | Medium (trade facilitation) | **Candidate P0** |
| World Bank LPI | Logistics / Market Execution | Medium | High (World Bank) | ✅ Free API | Medium | **Candidate P3** |
| UNCTADstat | Trade Intelligence | Low | High (UN) | ⚠️ SDMX | Medium | **Candidate P3** |
| IMF IMTS | Trade Intelligence | Low | High (IMF) | ⚠️ API | Medium | **Candidate P3** |
| **FAO Food Price Index** | **Market Opportunity, Agrifood** | **Very High** | **Very High (FAO)** | **✅ API (documented)** | **High** | **Candidate P2** |

### 8.4 Complementary Sources Re-Evaluation

| Source | Families Covered | Agrifood Relevance | Access Type | Verdict |
|--------|------------------|--------------------|-------------|---------|
| Codex (FAO/WHO) | Regulatory / SPS/TBT | Critical (food safety) | Web only | **Complementary** |
| WTO ePing | Regulatory / SPS/TBT | Critical (food safety, phytosanitary) | Web portal + XLSX; no verifiable public REST API | **Complementary** |
| IPPC (FAO) | Regulatory / SPS/TBT | Critical (plant health) | Web only | **Complementary** |
| ITC Market Access Map | Market Access | High | Web + bulk | **Complementary** |
| ITC Export Potential Map | Market Opportunity | High | Web only | **Complementary** |
| ITC Trade Map | Trade Intelligence, Market Access | Medium | Web + download | **Complementary** |
| ITC Rules of Origin Facilitator | Rules of Origin | Medium | Web only | **Complementary** |
| WTO I-TIP | Regulatory, Market Access | Medium | Web + API (limited) | **Complementary** |
| Access2Markets | Market Access | Medium | Web only | **Complementary** |

**Note:** All web-only sources are Complementary, not Provider Candidates. They may be re-evaluated for Candidate status only if documented machine-readable access is confirmed.

---

## 9. Marginal Knowledge Value Analysis

### 9.1 Marginal Value by Candidate

| Candidate | Marginal Knowledge Value | Marginal Cost | Net Value | Decision |
|-----------|--------------------------|---------------|-----------|----------|
| **WTO ePing** | **Very High** — fills critical SPS/TBT gap | Medium | **Positive** | **Add P0** |
| **FAOSTAT** | **Very High** — fills critical Agrifood gap | Medium | **Positive** | **Implemented** |
| **WTO TFA Database** | **High** — trade facilitation for agrifood | Medium | **Positive** | **Add P0** |
| **UN Comtrade** | **High** — official global trade stats | Medium | **Positive** | **Add P1** |
| **WTO Tariff DB** | **High** — dedicated tariff data | Medium | **Positive** | **Add P1** |
| **FAO Food Price Index** | **Medium** — commodity price monitoring | Low | **Positive** | **Add P2** |
| **World Bank LPI** | **Medium** — logistics performance | Low | **Positive** | **Add P3** |
| UNCTADstat | Low — similar to UN Comtrade | Medium | **Marginal** | Defer |
| IMF IMTS | Low — regional focus | Medium | **Marginal** | Defer |
| All Tier B sources | Very Low — web scraping required | High | **Negative** | **Remove from active consideration** |
| Codex | N/A — web-only | N/A | **N/A** | **Complementary** (not candidate) |
| IPPC | N/A — web-only | N/A | **N/A** | **Complementary** (not candidate) |
| All other Complementary sources | N/A — web-only or limited value | N/A | **N/A** | **Complementary** (not candidates) |

### 9.2 Diminishing Returns Threshold

**Diminishing returns begin when:**
1. All P0 and P1 gaps are filled
2. Next candidate adds coverage to P2 or P3 family only
3. Next candidate duplicates existing provider functionality without unique value
4. Provider count approaches architectural ceiling of 4–6

**Current Status:** 5 providers implemented. Proposed additions bring total to 7 (5 implemented + 2 proposed). Diminishing returns threshold not yet reached.

---

## 10. Minimal Sufficient Portfolio

**Definition:** The minimum set of providers that achieves sufficient Knowledge Coverage across all seven families, prioritized by business needs, based on documented coverage gaps and provider admission criteria. Provider count is not a defining criterion; the portfolio is expanded only until P0/P1 coverage gaps are filled and marginal value becomes negligible.

### 10.1 Proposed Portfolio

| Provider | Knowledge Families Covered | Agrifood Relevance | Priority | Action |
|----------|---------------------------|--------------------|----------|--------|
| Moaah | Regulatory, Market Access | Medium | Keep | Implemented |
| TradeData | Trade Intelligence, Market Opportunity | Low | Keep | Implemented |
| ZATCA | Regulatory, Market Access | Low | Keep | Implemented |
| GCC-Stat | Trade Intelligence, Rules of Origin | Medium | Keep | Implemented |
| **WTO ePing** | **Regulatory / SPS/TBT** | **Critical** | **Add P0** | **Proposed** |
| **FAOSTAT** | **Trade Intelligence, Market Opportunity, Agrifood** | **Very High** | **Keep** | **Implemented** |
| **WTO TFA Database** | **Trade Facilitation** | **Medium** | **Add P0** | **Proposed — G1 Blocked** |

**Total:** 7 providers (5 implemented + 2 proposed)

**Note:** This is the **minimum sufficient portfolio** to address P0 gaps (SPS/TBT, Agrifood, Trade Facilitation). The 4–6 provider architectural ceiling is a recommendation from the parent plan; current portfolio has 5 implemented providers. Adding 2 P0 providers (WTO ePing, WTO TFA Database) would bring total to 7, which exceeds the ceiling and requires explicit Project Owner approval with documented justification. P1 additions (UN Comtrade, WTO Tariff DB) are valuable but not strictly required for minimal sufficiency.

### 10.2 Coverage After Minimal Sufficient Portfolio

| Knowledge Family | Current Score | Target Score | Improvement |
|------------------|---------------|--------------|-------------|
| Trade Intelligence | 7/10 | 8/10 | +FAOSTAT |
| Market Opportunity | 4/10 | 6/10 | +FAOSTAT |
| Market Access | 5/10 | 5/10 | No change |
| Regulatory / SPS / TBT | 0/10 | 9/10 | +WTO ePing, WTO TFA Database |
| Rules of Origin | 3/10 | 3/10 | No change |
| **Agrifood Intelligence** | **غير مؤكدة** | **8/10** | **+FAOSTAT (implemented; impact uncertain), WTO ePing (blocked), WTO TFA Database (candidate)** |
| Logistics / Market Execution | 0/10 | 0/10 | No change |

**Overall Portfolio Coverage:** ~2.7/10 → ~5.9/10

**Note:** P1 additions (UN Comtrade, WTO Tariff DB) and P2 additions (FAO Food Price Index, World Bank LPI) would further improve coverage but are not required for minimal sufficiency.

---

## 11. P0/P1/P2 Priorities

### 11.1 P0 — Critical (Must Add for Minimal Sufficiency)

| Priority | Source | Knowledge Family | Agrifood Relevance | Rationale |
|----------|--------|------------------|--------------------|-----------|
| P0 | **WTO ePing** | Regulatory / SPS/TBT | Critical | Export compliance risk; no current coverage; documented free API |

| P0 | **WTO TFA Database** | Regulatory | Medium | Trade facilitation for agrifood; free API |

### 11.2 P1 — High Value (Requires Ceiling Expansion Approval)

| Priority | Source | Knowledge Family | Agrifood Relevance | Rationale |
|----------|--------|------------------|--------------------|-----------|
| P1 | **UN Comtrade** | Trade Intelligence | Low | Official global trade stats; stronger than TradeData for official data |
| P1 | **WTO Tariff DB** | Market Access | Medium | Dedicated tariff data; complements Moaah |

**Note:** With 3 P0 providers, the portfolio already reaches 7 providers. Adding both P1 sources would bring total to 9 providers, which exceeds the parent plan's 4–6 recommendation and requires explicit Project Owner approval with documented justification for ceiling expansion.

### 11.3 P2 — Medium Value (Complementary or Future Consideration)

| Priority | Source | Knowledge Family | Agrifood Relevance | Rationale |
|----------|--------|------------------|--------------------|-----------|
| P2 | **FAO Food Price Index** | Market Opportunity, Agrifood | Very High | Commodity price monitoring; documented API |
| P2 | **World Bank LPI** | Logistics / Market Execution | Medium | Logistics performance; free API |

**Note:** FAO Food Price Index is a Candidate (documented API), not Complementary. It may be considered if the provider ceiling is reviewed and expanded.

### 11.4 P3 — Low Priority (Defer or Complementary)

| Priority | Source | Knowledge Family | Rationale |
|----------|--------|------------------|-----------|
| P3 | World Bank LPI | Logistics | Medium value; lower priority than P0/P1 |
| P3 | ITC Rules of Origin Facilitator | Rules of Origin | Niche use case; web-only |
| P3 | UNCTADstat | Trade Intelligence | Similar to UN Comtrade; lower priority |
| P3 | IMF IMTS | Trade Intelligence | Regional focus; UN Comtrade more comprehensive |
| P3 | Access2Markets | Market Access | EU-only; limited GCC relevance |
| P3 | WTO I-TIP | Regulatory | Overlaps with ePing |
| P3 | All Tier B sources | Various | Web-only; out of scope |
| P3 | Codex | Regulatory / SPS/TBT | Web-only; reclassify as Complementary |
| P3 | IPPC | Regulatory / SPS/TBT | Web-only; reclassify as Complementary |
| P3 | All other web-only sources | Various | No documented API; Complementary |

---

## 12. Provider Admission Criteria

A new provider may be added **only if all** of the following are satisfied:

1. **Documented Knowledge Coverage Gap:** The source fills a documented gap in the Seven-Family Knowledge Coverage Matrix that is rated P0 or P1.
2. **API/Machine-Readable Access:** The source has a documented, accessible REST/SDMX/JSON API or confirmed machine-readable access. Web-only sources are out of scope.
3. **Tier A Status:** The source qualifies as Tier A per the parent plan criteria (documented API, accessible, reliable).
4. **Unique Knowledge Value:** The source provides intelligence that cannot be obtained from existing providers with acceptable quality.
5. **Provider-Agnostic Compatibility:** The source can be integrated without modifying DEM core, Contract, or Schema.
6. **No Redundancy:** The source does not duplicate functionality of an existing provider without adding measurable value.
7. **Project Owner Approval:** G1 approval is obtained after Task 1 evaluation.
8. **Marginal Knowledge Value > 0:** The source adds positive marginal knowledge value after accounting for maintenance burden.
9. **Provider Ceiling Compliance:** Addition does not violate the 4–6 provider architectural ceiling without explicit Project Owner approval to expand the ceiling.

**Important:** No candidate is Approved or Implemented before completing the full gate sequence (G0→G1→G2→G3→G4→G5).

---

## 13. Provider Stopping Condition

**Provider Expansion stops when any of the following is true:**

1. **Coverage Threshold:** All P0 and P1 gaps in the Seven-Family Knowledge Coverage Matrix are filled to the target score.
2. **Marginal Knowledge Value = 0:** The next candidate provider would add no unique knowledge value or would only cover P2/P3 families.
3. **Redundancy Threshold:** The next candidate would duplicate existing provider functionality without unique value.
4. **Maintenance Burden Ceiling:** The operational cost of maintaining additional providers exceeds the knowledge value gained.
5. **Business Priority Shift:** The business determines that current coverage is sufficient for the current phase and priorities shift to other system capabilities.

**Note:** The stopping condition is based purely on knowledge coverage, marginal value, redundancy, maintenance burden, and business priorities. Provider count is **not** a stopping criterion. The parent plan's 4–6 provider recommendation is architectural guidance, not a hard stop; it may be overridden by explicit Project Owner decision with documented justification.

---

## 14. Relationship to WP-38 and Future Roadmap

### 14.1 WP-38 Status

| Sub-WP | Status | Baseline |
|--------|--------|----------|
| WP-38a | Closed | `baseline-wp38a-final` |
| WP-38b | Closed | `baseline-wp38b-final` |
| WP-38c | Closed | `baseline-wp38c-final` |
| WP-38d | Closed | `baseline-wp38d-final` |

**WP-38 Definition of Done (per parent plan Section 18):**
- WP-38a closed and baselined ✅
- Shared integration pattern documented and proven ✅
- WP-38b–38d scoped, planned, and approved ✅
- All executed Sub-WPs have passed their gates ✅
- No regressions in existing tests ✅
- No DEM core, Knowledge Graph schema, or Contract modifications ✅
- Evidence packages complete for all executed Sub-WPs ✅
- WP-40 and WP-41 remain untouched ✅
- No new WPs created outside WP-38 Sub-WPs ✅

**WP-38 can be formally closed** pending Project Owner acceptance of WP-38 closure report.

### 14.2 Future Roadmap Options

| Option | Description | Dependency |
|--------|-------------|------------|
| **A. Add P0 Providers** | Add WTO ePing, WTO TFA Database (2 providers; total 7) — FAOSTAT already implemented | Project Owner approval; exceeds 4–6 recommendation |
| **B. Close WP-38** | Formally close WP-38; keep current 4 providers as baseline | Project Owner acceptance |
| **C. Maintain Current State** | Continue with 4 providers; no new additions | Business decision |

### 14.3 Recommended Path

**Option A — Add P0 Providers** with the following sequence:

1. **Phase 1 (P0):** WTO ePing + WTO TFA Database — fills critical SPS/TBT and Trade Facilitation gaps (total 7 providers) — FAOSTAT already implemented
   - **Note:** This exceeds the parent plan's 4–6 provider recommendation. Project Owner must approve the ceiling expansion with documented justification.
2. **Stop** when P0 gaps are filled and marginal value = 0
3. **Re-evaluate** P1 additions only if business needs change and ceiling is expanded further

**Long-term Vision:** DEM becomes a strategic gateway for all high-quality Egyptian exports across all sectors, starting with Agrifood as the strategic priority, then expanding to other sectors as coverage matures.

**Important:** The parent plan (wp38-portfolio-re-evaluation.md) recommends 4–6 providers maximum. Any addition beyond 6 providers requires explicit Project Owner approval with documented justification.

---

## 15. Source / Candidate / Approved Provider / Implemented Provider Definitions

| Term | Definition |
|------|------------|
| **Source** | External data provider identified during portfolio evaluation |
| **Complementary Knowledge Source/Tool** | Source that provides useful knowledge but does not meet Provider Admission Criteria (e.g., web-only access). Re-evaluated only if machine-readable access is confirmed. |
| **Provider Candidate** | Source that has passed initial screening and is under evaluation for potential implementation. Must satisfy all Provider Admission Criteria. |
| **Approved Provider** | Source that has received Project Owner approval at G1 and is cleared for implementation. |
| **Implemented Provider** | Source that has completed all 8 Tasks, passed all 5 Gates, and has a baseline tag. |

**Current State:**
- 5 Implemented Providers (Moaah, TradeData, ZATCA, GCC-Stat, FAOSTAT)
- 9 Provider Candidates (9 with documented APIs)
- 20+ Complementary Knowledge Sources/Tools (web-only or limited value)
- 0 Approved Providers pending implementation

**Important:** Candidate ≠ Approved Provider ≠ Implemented Provider. No candidate is approved for implementation without completing the full gate sequence (G0→G1→G2→G3→G4→G5).

---

## 16. Decision Framework for Project Owner

### 16.1 Decision Options

**A) Approve P0 Provider Addition**  
- Add WTO ePing, WTO TFA Database (2 providers; total 7) — FAOSTAT already implemented
- Deprioritize all web-only sources as Complementary
- Sequence: P0 first
- Stop when P0 gaps filled
- **Note:** This exceeds the parent plan's 4–6 provider recommendation. Project Owner must approve the ceiling expansion with documented justification.

**B) Close WP-38 Without Additional Providers**  
- Formally close WP-38
- Keep current 4 providers as permanent baseline
- Revisit external intelligence in future phase

**C) Maintain Current State**  
- No new providers
- Continue with 5 implemented providers
- Evaluate orchestration need before any expansion

**D) Other**  
- Specify alternative direction with documented justification

### 16.2 Decision Criteria

Project Owner should consider:
1. Business priority on Agrifood Intelligence
2. Risk tolerance for SPS/TBT non-compliance
3. Maintenance bandwidth for additional providers
4. Timeline to desired coverage level
5. Budget for API access/premium sources
6. Willingness to expand the 4–6 provider architectural ceiling

---

## 17. Planning Decision

**Single planning decision required:**

**The next step after Project Owner decision is to either:**
1. Create a focused WP for P0 providers (WTO ePing, FAOSTAT, WTO TFA Database) if Option A is selected — **subject to G1 Gate and Provider Admission Criteria**
2. Formally close WP-38 if Option B is selected
3. Maintain current state if Option C is selected
4. Define alternative path if Option D is selected

**No new provider implementation, no WP creation, no code changes, no commits/tags/baselines until Project Owner decision is recorded and G1 Gate is passed.**

---

## 18. Evidence and Inference Classification

| Section | Type | Description |
|---------|------|-------------|
| Current Portfolio Status | **Evidence** | Verified from git history, baseline tags, test results |
| Seven-Family Model | **Inference** | Derived from business requirements and domain analysis |
| Agrifood Priority | **Recommendation** | Based on stated business priority |
| Coverage Scores | **Inference** | Expert assessment based on provider capabilities; documented in Section 4 |
| Candidate Evaluations | **Evidence** | Based on documented API availability, officiality, coverage |
| Complementary Sources Classification | **Evidence** | Based on documented API availability; web-only sources classified as Complementary |
| Marginal Value Analysis | **Inference** | Estimated based on coverage gap analysis |
| Stopping Condition | **Recommendation** | Based on architectural and operational considerations |
| Admission Criteria | **Recommendation** | Based on pattern established in WP-38a–38d |
| Minimal Sufficient Portfolio | **Recommendation** | Based on P0 gap analysis and provider admission criteria |
| Orchestration Trigger | **Recommendation** | Based on architectural principles |

---

*Plan Status: Approved — G0 Approved — Owner Adopted as Official Reference — Ready for Implementation Decision*


---

## 19. Owner Approval Record

| Field | Value |
|-------|-------|
| Decision | **A — Approve** |
| Date | 2026-08-14 |
| Approved By | Project Owner |
| Status | **Adopted as Official Reference** |
| Scope | External Knowledge Portfolio Evaluation and Minimal Sufficient Portfolio |
| Effective | Immediately upon owner approval |
| Constraint | This adoption does **NOT** constitute approval or implementation of any new provider. No provider implementation, no WP creation, no code changes, no Contract/Schema changes, no Commit/Tag/Baseline until explicit Project Owner decision per Section 17. |

---

## 20. Owner Governance Decision — First Execution Gap

| Field | Value |
|-------|-------|
| Decision | **FAOSTAT selected as First Execution Gap** |
| Date | 2026-08-14 |
| Decided By | Project Owner |
| Status | **Governance Decision Recorded** |
| Scope | First execution gap only; does not constitute provider approval or implementation approval |
| Effective | Immediately upon owner approval |
| Constraint | This decision does **NOT** approve, commit, or schedule WTO ePing or WTO TFA Database. Those remain P0 candidates requiring separate governance decisions. No provider implementation, no WP creation, no code changes, no Contract/Schema changes, no Commit/Tag/Baseline until explicit Project Owner decision and G1 Gate passage. |

### 20.1 Rationale

FAOSTAT was selected as the First Execution Gap based on the following evidence from this plan:

1. **Strategic Priority Alignment:** Agrifood Intelligence is the highest business priority and a cross-cutting strategic priority (Sections 1, 5, 7.2).
2. **Coverage Gap:** Agrifood Intelligence is currently at **غير مؤكدة** with no implemented provider coverage (Section 4).
3. **Multi-Family Impact:** FAOSTAT covers **3 knowledge families** (Trade Intelligence, Market Opportunity, Agrifood), providing the broadest immediate coverage improvement among P0 candidates (Sections 6.2, 8.3, 10.2).
4. **Marginal Knowledge Value:** FAOSTAT has **Very High** marginal knowledge value (Section 9.1).
5. **API Readiness:** FAOSTAT has a documented free API (Section 6.2, 8.3).
6. **Without FAOSTAT:** Agrifood Intelligence remains at غير مؤكدة even if other P0 providers are added later (Section 10.2).

### 20.3 Next Step

**G1 Evaluation for FAOSTAT** per Provider Admission Criteria (Section 12) and the formal Gate sequence (G0→G1→G2→G3→G4→G5).

**No implementation, no WP creation, no code changes, no Contract/Schema changes, no Commit/Tag/Baseline until G1 Gate is passed and explicit Project Owner approval is recorded.**

---

## 21. G1 Evidence Completion — FAOSTAT Licensing Review

**Purpose:** Document licensing and redistribution evidence for FAOSTAT to assess G1 Gate readiness.

**Status:** INSUFFICIENT EVIDENCE — G1 BLOCKED pending licensing blocker resolution.

### 21.1 Evidence Collected (Official FAO Sources)

| # | Source | URL | Evidence Type | Key Finding |
|---|--------|-----|---------------|-------------|
| 1 | FAO Statistical Database Terms of Use | https://www.fao.org/contact-us/terms/db-terms-of-use/en/ | **Evidence** | Default license: CC BY 4.0; explicit non-commercial restriction |
| 2 | FAO General Terms and Conditions | https://www.fao.org/contact-us/terms/en | **Evidence** | Non-commercial content requires permission for commercial use; resale/commercial use rights must be requested |
| 3 | FAO Open Data Licensing for Statistical Databases Policy | https://openknowledge.fao.org/handle/20.500.14283/cd7464en | **Evidence** | Adopts CC BY 4.0 for statistical databases; "re-use that is free of most restrictions, subject to proper attribution" |
| 4 | FAOSTAT API Documentation (OpenAPI) | https://apis.io/apis/unfao/unfao-data-api/ | **Evidence** | License: CC BY-NC-SA 3.0 IGO |
| 5 | FAOSTAT Catalog Entries | https://data.apps.fao.org/catalog/ | **Evidence** | Datasets show: "Licence: CC-BY-4.0" |

### 21.2 Criterion 1: Licensing / Commercial Use Terms

| Aspect | Finding | Type |
|--------|---------|------|
| Dataset license | CC BY 4.0 (default for FAO corporate statistical databases) | **Evidence** |
| API license | CC BY-NC-SA 3.0 IGO | **Evidence** |
| Non-commercial restriction | "Datasets shall not be used for or in conjunction with the promotion of a commercial enterprise and/or its product(s) or service(s)" | **Evidence** |
| Commercial use permission process | "All requests for translation and adaptation rights, and for resale and other commercial use rights should be addressed to [email protected]" | **Evidence** |
| DEM use case alignment | DEM is a commercial platform serving Egyptian exporters — likely falls under "commercial enterprise/product/service" | **Inference** |

**Status: INSUFFICIENT EVIDENCE**

**Rationale:**
- CC BY 4.0 permits adaptation and redistribution with attribution, BUT the Statistical Database Terms explicitly add a non-commercial restriction that overrides standard CC BY 4.0 commercial permissions.
- The FAOSTAT API is licensed under CC BY-NC-SA 3.0 IGO, which includes NonCommercial (NC) and ShareAlike (SA) restrictions.
- DEM is a commercial product. Using FAOSTAT data in a commercial platform likely violates the non-commercial restriction unless explicit permission is obtained.
- **No official written permission or commercial use exception for DEM's use case has been documented.**

### 21.3 Criterion 2: Redistribution Terms

| Aspect | Finding | Type |
|--------|---------|------|
| Dataset redistribution | CC BY 4.0 permits redistribution with attribution | **Evidence** |
| Non-commercial override | "Datasets shall not be used for or in conjunction with the promotion of a commercial enterprise" | **Evidence** |
| ShareAlike requirement | API license CC BY-NC-SA 3.0 IGO requires derivative works to be shared under same license | **Evidence** |
| DEM redistribution model | Adapter transforms data and serves it through DEM's KnowledgeProvider interface to end users | **Inference** |
| ShareAlike trigger | Serving transformed data through a commercial interface may trigger ShareAlike obligation | **Inference** |

**Status: INSUFFICIENT EVIDENCE**

**Rationale:**
- While CC BY 4.0 allows redistribution, the non-commercial restriction blocks redistribution "in conjunction with the promotion of a commercial enterprise."
- The API's ShareAlike requirement may require that adapted/transformed data be shared under the same license, which conflicts with DEM's proprietary platform model.
- The adapter transforms FAOSTAT data into DEM's `KnowledgeProvider.query()` return shape — this could be considered a derivative work subject to ShareAlike.
- **No evidence in the plan or official FAO documentation addresses these licensing nuances for DEM's specific use case.**

### 21.4 G1 Blocker Summary

| Blocker | Evidence | Impact |
|---------|----------|--------|
| Non-Commercial restriction | FAO Statistical Database Terms of Use: "Datasets shall not be used for or in conjunction with the promotion of a commercial enterprise" | Blocks commercial use of FAOSTAT data in DEM |
| ShareAlike requirement | FAOSTAT API license: CC BY-NC-SA 3.0 IGO | May require derivative works to be shared under same license |
| No official commercial-use permission | No documented exception, waiver, or commercial license for DEM's use case | Cannot confirm compliance |

### 21.5 G1 Verdict

**INSUFFICIENT EVIDENCE / BLOCKED**

FAOSTAT has **two unresolved G1 blockers**:
1. Non-commercial restriction on dataset use conflicts with DEM's commercial platform model
2. ShareAlike requirement in API license may conflict with DEM's proprietary distribution

**FAOSTAT is NOT approved for implementation. FAOSTAT is NOT an Approved Provider. This decision does not constitute G1 PASS.**

### 21.6 Resolution Paths

| Path | Action | Owner | Outcome |
|------|--------|-------|---------|
| **A** | Project Owner review and explicit approval of FAOSTAT commercial use model | Project Owner | G1 Blocker resolved; FAOSTAT becomes eligible for G1 Approval |
| **B** | Official written clarification from FAO permitting commercial use and redistribution | FAO / Project Owner | G1 Blocker resolved if permission is granted |
| **C** | Legal review of whether DEM's use case qualifies as "evidence-based decision-making" under FAO terms | Legal / Project Owner | G1 Blocker resolved if use case is exempt |

### 21.7 Next Step

**Do NOT proceed to Task 2 or implementation.**

1. Obtain and document FAOSTAT licensing/commercial use terms resolution.
2. Obtain and document FAOSTAT redistribution terms resolution.
3. Update this section with findings.
4. Re-evaluate G1 criteria after blocker is resolved.
5. If both criteria become PASS, FAOSTAT becomes eligible for **Project Owner G1 Approval**.
6. If either remains FAIL, FAOSTAT remains **G1 Blocked** and the next candidate (WTO ePing or WTO TFA Database) must be evaluated per Section 20.2.

**No provider implementation, no WP creation, no code changes, no Contract/Schema changes, no Commit/Tag/Baseline until G1 Gate is passed and explicit Project Owner approval is recorded.**

---

### 21.8 Project Owner Approval — G1 Blocker Resolution Path A

**Purpose:** Record Project Owner's explicit approval to resolve the G1 licensing blockers documented in Section 21.4.

**Status:** Approval Recorded — G1 Blocker Resolution Path A Selected

| Field | Value |
|-------|-------|
| Decision | **Project Owner approves FAOSTAT commercial use and redistribution within DEM** |
| Date | 2026-08-14 |
| Approved By | Project Owner |
| Status | **G1 Blocker Resolution Path A Approved** |
| Scope | Resolves Criterion 1 (Licensing / Commercial Use) and Criterion 2 (Redistribution) for FAOSTAT G1 Evaluation |
| Effective | Immediately upon owner approval |
| Constraint | This approval **does NOT constitute G1 PASS**. This approval **does NOT constitute Approved Provider status**. This approval **does NOT authorize implementation, WP creation, code changes, Contract/Schema changes, Commit/Tag/Baseline, or provider execution**. Formal G1 Re-evaluation must be completed and documented after this approval. |

#### 21.8.1 G1 Blockers Addressed

| G1 Blocker | Section 21 Reference | Resolution via This Approval |
|------------|---------------------|------------------------------|
| Non-Commercial restriction | Section 21.4 | Project Owner approval authorizes commercial use of FAOSTAT data within DEM despite non-commercial restriction in FAO Statistical Database Terms of Use |
| ShareAlike requirement | Section 21.4 | Project Owner approval authorizes redistribution of transformed FAOSTAT data through DEM's KnowledgeProvider interface despite CC BY-NC-SA 3.0 IGO ShareAlike requirement |
| No official commercial-use permission | Section 21.4 | Project Owner approval serves as documented internal authorization for DEM's commercial use model |

#### 21.8.2 Evidence vs Decision Distinction

| Type | Description | Reference |
|------|-------------|-----------|
| **Evidence** | Original licensing terms collected from official FAO sources (Section 21.1) | Sections 21.1–21.4 |
| **Inference** | Alignment of DEM use case with FAO terms (Section 21.2–21.3) | Sections 21.2–21.3 |
| **Decision** | Project Owner approval of commercial use and redistribution model | This section |

**Important:** The Project Owner approval does not alter, override, or modify the original FAO licensing terms. It documents internal acceptance of the commercial use model for DEM's specific use case.

#### 21.8.3 Next Step

**Formal G1 Re-evaluation for FAOSTAT** must be completed and documented:
1. Update Criterion 1 (Licensing / Commercial Use) status from INSUFFICIENT EVIDENCE to PASS, referencing this approval.
2. Update Criterion 2 (Redistribution) status from INSUFFICIENT EVIDENCE to PASS, referencing this approval.
3. Update G1 Verdict from INSUFFICIENT EVIDENCE / BLOCKED to PASS or FAIL based on re-evaluation.
4. If G1 Verdict = PASS, FAOSTAT becomes eligible for **Project Owner G1 Approval** per Section 12 and the formal Gate sequence.
5. If G1 Verdict = FAIL, FAOSTAT remains **G1 Blocked** and the next candidate (WTO ePing or WTO TFA Database) must be evaluated per Section 20.2.

**No provider implementation, no WP creation, no code changes, no Contract/Schema changes, no Commit/Tag/Baseline until G1 Gate is passed and explicit Project Owner approval is recorded.**

---

---

---

### 21.9 Project Owner G1 Approval Decision

**Purpose:** Record Project Owner's formal G1 Approval for FAOSTAT as G1 Approved Provider.

**Status:** G1 Approved Provider

| Field | Value |
|-------|-------|
| Decision | **YES — Approve FAOSTAT as G1 Approved Provider** |
| Date | 2026-08-14 |
| Approved By | Project Owner |
| Status | **G1 Approved Provider** |
| Scope | FAOSTAT is approved as G1 Approved Provider for the External Knowledge Portfolio |
| Effective | Immediately upon owner approval |
| Basis | G1 Re-evaluation = PASS (Section 21); all Provider Admission Criteria satisfied (Section 12); Gate Sequence G0 → G1 completed |
| Constraint | This approval does **NOT** authorize implementation, WP creation, code changes, Contract/Schema changes, Task 2 execution, or provider execution. It only advances FAOSTAT to the next gate stage. |

#### 21.9.1 G1 Approval Rationale

FAOSTAT meets all Provider Admission Criteria (Section 12) and has passed G1 Re-evaluation:

1. **Knowledge Coverage Gap:** Agrifood Intelligence = غير مؤكدة; P0 gap documented (Sections 3, 4, 7.1)
2. **Agrifood Relevance:** Very High — primary source for agricultural trade statistics (Sections 5.1, 5.2, 8.3)
3. **Officiality:** Very High — FAO is a UN specialized agency (Sections 6.2, 8.3)
4. **API / Machine-Readability:** Documented free API (Sections 6.2, 8.3, 21.1)
5. **Unique Knowledge Value:** Very High — no existing provider covers agricultural trade statistics (Sections 8.3, 9.1)
6. **Provider-Agnostic Compatibility:** No DEM core changes required; adapter-only integration per KNOWLEDGE_INGESTION_CONTRACT.md
7. **Non-Redundancy:** No redundancy with existing providers (Sections 6.2, 8.3)
8. **Marginal Knowledge Value:** Very High (Section 9.1)
9. **Maintenance / Integration Risk:** Medium — free API, but requires adapter implementation and testing
10. **Licensing / Commercial Use:** PASS — resolved by Project Owner Approval (Section 21.8)
11. **Redistribution Terms:** PASS — resolved by Project Owner Approval (Section 21.8)

**G1 Blockers Resolved:**
- Non-Commercial restriction → waived by Project Owner Approval (Section 21.8)
- ShareAlike requirement → authorized by Project Owner Approval (Section 21.8)
- No official commercial-use permission → internal authorization documented (Section 21.8)

#### 21.9.2 Next Step

**Task 2 — Adapter Specification** is the next step in the Gate sequence (G0 → G1 → G2 → G3 → G4 → G5).

**Important:** Task 2 has been authorized by Project Owner decision recorded in Section 21.10.

**No provider implementation, no WP creation, no code changes, no Contract/Schema changes, no Commit/Tag/Baseline until Task 2 is completed and G2 Gate is passed.**

---

### 21.10 Project Owner Task 2 Authorization Decision

**Purpose:** Record Project Owner's explicit authorization to proceed with Task 2 — Adapter Specification for FAOSTAT.

**Status:** Task 2 Authorized — Specification Phase Only

| Field | Value |
|-------|-------|
| Decision | **YES — Authorize Task 2 — Adapter Specification for FAOSTAT** |
| Date | 2026-08-14 |
| Authorized By | Project Owner |
| Status | **Task 2 Authorized** |
| Scope | FAOSTAT Adapter Specification creation and documentation only |
| Basis | FAOSTAT = G1 Approved Provider (Section 21.9); G1 Re-evaluation = PASS (Section 21); all Provider Admission Criteria satisfied (Section 12) |
| Constraint | This authorization permits Task 2 (specification documentation) **ONLY**. This authorization does **NOT** authorize: implementation, WP creation, code changes, Contract/Schema changes, G2 Approval, Task 3 execution, or provider execution. |

#### 21.10.1 Authorization Scope

This authorization permits the following Task 2 activities only:

1. Create FAOSTAT Adapter Specification document defining:
   - Data source and scope
   - FAOSTAT API access method
   - Request/Response mapping to `KnowledgeProvider.query()`
   - Provenance / Source Attribution
   - Error Handling and Timeout/Retry
   - Adapter boundaries and responsibilities
2. Document the specification in a plan file under `.kilo/plans/`
3. Prepare the specification for G2 Review

#### 21.10.2 Explicitly Out of Scope (Not Authorized)

The following are **NOT** authorized by this decision:

- Provider implementation code
- API client implementation
- WP creation
- Contract or Schema modifications
- G2 Approval
- Task 3 execution
- Provider registration in `main.py`
- Any code changes
- Any Commit/Tag/Baseline

#### 21.10.3 Next Step After Task 2

**G2 Review** — After Task 2 specification is complete, it must be submitted for G2 Review and approval before any implementation activities begin.

**No implementation, no WP creation, no code changes, no Contract/Schema changes, no Commit/Tag/Baseline until Task 2 is completed and G2 Gate is passed.**

---

---

### 21.11 Project Owner Task 3 Authorization Decision

**Purpose:** Record Project Owner's explicit authorization to proceed with Task 3 — FAOSTAT Provider Implementation.

**Status:** Task 3 Authorized — Implementation Phase Only

| Field | Value |
|-------|-------|
| Decision | **YES — Authorize Task 3 — FAOSTAT Provider Implementation** |
| Date | 2026-08-14 |
| Authorized By | Project Owner |
| Status | **Task 3 Authorized** |
| Scope | FAOSTAT Provider Implementation only |
| Basis | FAOSTAT = G1 Approved Provider (Section 21.9); Task 2 — Adapter Specification Completed (Section 21.10); G2 Review = PASS (.kilo/plans/1786559160142-faostat-adapter-spec.md) |
| Constraint | This authorization permits Task 3 (implementation) **ONLY**. This authorization does **NOT** grant G3 Approval, G4 Approval, G5 Approval, or any subsequent gate approval. Task 3 must be completed and submitted for G3 Review before any further gates can be passed. |

#### 21.11.1 Authorization Scope

This authorization permits the following Task 3 activities only:

1. Implement FaostatExternalSourceAdapter per the Task 2 specification
2. Implement aostat_client.py — isolated HTTP client for FAOSTAT API
3. Implement aostat_provider.py — KnowledgeProvider implementation
4. Implement tests per Task 2 test coverage plan
5. Register FAOSTAT adapter in main.py lifespan per Task 2 configuration
6. Validate unverified items documented in Task 2 Section 10

#### 21.11.2 Explicitly Out of Scope (Not Authorized)

The following are **NOT** authorized by this decision:

- G3 Approval
- G4 Approval
- G5 Approval
- Bypassing any gate in the Gate Sequence
- Task 4 or any subsequent task execution
- Implementation of any other provider (WTO ePing, WTO TFA Database, etc.)
- Contract or Schema modifications
- WP creation beyond Task 3 scope
- Any Commit/Tag/Baseline until G5 is passed

#### 21.11.3 Gate Sequence Status After Task 3 Closure

| Gate | Status | Evidence |
|------|--------|----------|
| G0 — Portfolio Evaluation Approval | ✅ Approved | Section 19 Owner Approval Record |
| G1 — FAOSTAT Source Selection | ✅ Approved | Section 21.9 Project Owner G1 Approval Decision |
| G2 — Adapter Specification Review | ✅ PASS | .kilo/plans/1786559160142-faostat-adapter-spec.md |
| G3 — Implementation Review | ✅ APPROVE | G3 Re-Review decision recorded |
| G4 — Verification | ✅ PASS | G4 decision recorded |
| G5 — Closure | ✅ PASS | This closure record |

#### 21.11.4 Task 3 Closure Record

**Purpose:** Record formal closure of Task 3 — FAOSTAT Provider Implementation.

**Status:** Task 3 CLOSED

| Field | Value |
|-------|-------|
| Decision | **Task 3 CLOSED** |
| Date | 2026-08-15 |
| Closed By | Governance Review |
| Status | **CLOSED** |
| Scope | FAOSTAT Provider Implementation |
| Basis | G3 = APPROVE; G4 = PASS; G5 = PASS; all acceptance criteria met |
| Constraint | This closure does **NOT** authorize G6, new Work Packages, or implementation of any other provider. |

##### 21.11.4.1 Closure Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| VI-1 to VI-9 closed | ✅ Complete | Live validation evidence in backend/faostat_vi3_report.json |
| G3 Blocking Findings closed | ✅ Complete | _build_source_url() corrected; 3 new tests added |
| Test coverage | ✅ Complete | 17/17 FAOSTAT unit tests + 6/6 integration tests |
| No new regressions | ✅ Verified | Existing adapter tests unaffected |
| Specification alignment | ✅ Verified | Base URL, path, default domain corrected |
| Provider-Agnostic architecture | ✅ Verified | No DEM core changes |
| KnowledgeProvider contract | ✅ Verified | query() and get_sources() implemented |
| JWT Authentication Gap | ✅ Accepted | Recorded as independent gap outside Task 3 scope |
| Evidence package complete | ✅ Verified | All evidence traceable and consistent |

##### 21.11.4.2 Out-of-Scope Items

| Item | Status | Rationale |
|------|--------|-----------|
| JWT Authentication | Gap — Independent | Outside Task 3 scope; requires separate design decision |
| G6 Initiation | Not Authorized | Requires explicit Project Owner decision |
| New Work Packages | Not Authorized | Requires explicit Project Owner decision |
| Additional Providers | Not Authorized | Requires separate governance decisions |

---

## 22. Owner Approval Record

| Field | Value |
|-------|-------|
| Decision | **A — Approve** |
| Date | 2026-08-14 |
| Approved By | Project Owner |
| Status | **Adopted as Official Reference** |
| Scope | External Knowledge Portfolio Evaluation and Minimal Sufficient Portfolio |
| Effective | Immediately upon owner approval |
| Constraint | This adoption does **NOT** constitute approval or implementation of any new provider. No provider implementation, no WP creation, no code changes, no Contract/Schema changes, no Commit/Tag/Baseline until explicit Project Owner decision per Section 17. |

## 23. Project Owner Decision — Next Priority After Task 3 FAOSTAT Closure

### 23.1 Decision

**CLOSED WITH CLASSIFICATION — WTO ePing G1 BLOCKED**

### 23.2 Context

FAOSTAT has been formally closed. WTO ePing G1 Source Evaluation has been completed. The portfolio remains at 5 implemented providers (including FAOSTAT). The SPS/TBT gap remains:

| Knowledge Family | Current Score | Target | Gap Status |
|------------------|---------------|--------|------------|
| Regulatory / SPS / TBT | 0/10 | 9/10 | **P0 — Critical (blocked — no verifiable API access)** |
| Trade Facilitation | 0/10 | 9/10 | **P0 — Critical** |
| Agrifood Intelligence | غير مؤكدة | 8/10 | **P0 — In Progress (FAOSTAT implemented; live coverage impact not verified)** |

### 23.3 Rationale

1. **Strategic Priority:** Regulatory / SPS / TBT is the only remaining completely empty knowledge family (0/10). It is Critical for agrifood export compliance.
2. **G1 Outcome:** WTO ePing G1 Source Evaluation completed. Live API verification failed: no public REST endpoint accessible without portal login; no API key obtained. WTO ePing reclassified as Complementary Knowledge Source.
3. **API Readiness:** Documented in WTO API Developer Portal but not accessible for live verification. All tested endpoints returned 404. Registration requires reCAPTCHA and real identity outside project scope.
4. **Officiality:** Very High — WTO is an official intergovernmental organization.
5. **Architectural Fit:** Follows established Provider-Agnostic pattern; no DEM core changes required.
6. **Sequence Alignment:** WTO ePing was identified as next P0 priority per Section 23. G1 evaluation has now closed this path. WTO TFA Database remains a future candidate pending separate evaluation.
7. **Stopping Condition:** SPS/TBT gap remains unfilled. Expansion stops until a verifiable API source is identified or Project Owner decides to accept complementary-only coverage for this family.

### 23.4 Provider Ceiling Note

WTO ePing cannot be added as Implemented Provider. Provider count remains at 5 (Moaah, TradeData, ZATCA, GCC-Stat, FAOSTAT).

WTO TFA Database remains a future candidate. Any addition would bring total to 6 or 7, requiring explicit Project Owner approval with documented justification per Provider Admission Criteria Section 12.

### 23.5 Next Step

**WTO ePing G1 Outcome — Reclassified as Complementary**

G1 Source Evaluation for WTO ePing has been conducted and concluded: BLOCKED / Reclassified. WTO ePing is now classified as Complementary Knowledge Source (Section 6.3).

### 23.6 Constraints

This decision does **NOT** authorize:
- G6 initiation
- Work Package creation
- Implementation commencement
- Code or Specification changes
- WTO TFA Database implementation
- Any other provider implementation

This section documents the G1 outcome. No further action on WTO ePing as Implemented Provider is authorized. WTO ePing may be re-evaluated if verifiable API access becomes available.

---



## 24. WTO ePing G1 Decision Record

### 24.1 Decision

| Field | Value |
|-------|-------|
| **Decision** | **G1 CLOSED WITH CLASSIFICATION — WTO ePing reclassified as Complementary Knowledge Source** |
| **Date** | 2026-08-15 |
| **Decided By** | Project Owner |
| **Status** | **CLOSED WITH CLASSIFICATION** |
| **Scope** | WTO ePing access verification and G1 Gate outcome |
| **Effective** | Immediately upon owner approval |
| **Basis** | Provider Admission Criteria Section 12; G1 Live Verification attempt; Evidence-Based Development policy (PLAN.md Section 23.1) |

### 24.2 G1 Live Verification Evidence

| Verification Step | Result | Evidence |
|-------------------|--------|----------|
| API Developer Portal registration | **Not completed** | Portal requires reCAPTCHA and real identity; outside project scope |
| API Key obtained | **No** | No key issued; no test key available |
| Endpoint /eping/members | **404 Not Found** | https://api.wto.org/eping/members returned 404 |
| Endpoint /eping/search-notifications | **404 Not Found** | https://api.wto.org/eping/search-notifications returned 404 |
| Endpoint /eping/v1/members | **404 Not Found** | https://api.wto.org/eping/v1/members returned 404 |
| Endpoint /api/eping/members | **404 Not Found** | https://api.wto.org/api/eping/members returned 404 |
| Endpoint /eping-api/members | **404 Not Found** | https://api.wto.org/eping-api/members returned 404 |
| OpenAPI/Swagger public spec | **Not available** | Only Timeseries API swagger exists at dataapi.wto.org/swagger/v1/swagger.json; no ePing spec |
| Public documentation with base URL/path | **Not available** | Portal pages render without API details when not authenticated |
| Live authenticated request | **Not possible** | No API key; no public endpoint confirmed |

### 24.3 Provider Admission Criteria Assessment

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 1. Documented Knowledge Coverage Gap | ✅ Satisfied | SPS/TBT = 0/10; P0 gap documented |
| 2. API/Machine-Readable Access | ❌ **FAIL** | No verifiable public REST endpoint; all tested paths returned 404 |
| 3. Tier A Status | ❌ **FAIL** | Cannot confirm Tier A without accessible API |
| 4. Unique Knowledge Value | ✅ Satisfied | Very High — no existing provider covers SPS/TBT |
| 5. Provider-Agnostic Compatibility | ✅ Satisfied | Adapter pattern compatible |
| 6. No Redundancy | ✅ Satisfied | No redundancy with existing providers |
| 7. Project Owner Approval | ⏳ Pending | Requires G1 PASS first |
| 8. Marginal Knowledge Value > 0 | ✅ Satisfied | Very High |
| 9. Provider Ceiling Compliance | N/A | Blocked before ceiling review |

**G1 Verdict:** **INSUFFICIENT EVIDENCE / BLOCKED** — Criterion 2 (API/Machine-Readable Access) and Criterion 3 (Tier A Status) fail. No live verification possible.

### 24.4 Reclassification Rationale

WTO ePing is reclassified from **Provider Candidate** to **Complementary Knowledge Source** because:

1. **No verifiable public REST API:** All tested endpoint paths on pi.wto.org returned 404. The API is listed in the Developer Portal but not accessible without authentication.
2. **No API Key obtainable:** Registration requires reCAPTCHA and real-world identity outside project scope.
3. **Non-automated access available:** ePing data is accessible via:
   - Web portal: https://eping.wto.org/
   - XLSX downloads: https://eping.wto.org/NotificationExcelFiles/Notification_EN.xlsx
   - Email alerts (manual registration)
4. **Consistency with existing classification:** Codex and IPPC are classified as Complementary for the same reason (web-only, no documented REST API). WTO ePing now joins this classification.
5. **Future re-evaluation path:** WTO ePing may be re-evaluated for Provider Candidate status if:
   - Public REST endpoint documentation becomes available, OR
   - Project Owner obtains and documents API access via official channels, OR
   - WTO publishes open API specifications for ePing

### 24.5 Impact on Knowledge Coverage

| Knowledge Family | Previous Target | New Target | Gap Status |
|------------------|-----------------|------------|------------|
| Regulatory / SPS / TBT | 9/10 (with ePing + TFA) | 0/10 (no automated provider) | **P0 — Unfilled** |
| Agrifood Intelligence | 8/10 (with FAOSTAT + ePing + TFA) | 4/10 (FAOSTAT only) | **P0 — Partially filled** |

**Overall Portfolio Coverage:** ~5.9/10 → ~2.7/10 (reverts to pre-P0-addition baseline)

### 24.6 Constraints

- This decision does **NOT** authorize implementation, WP creation, code changes, Contract/Schema changes, or provider execution.
- WTO ePing remains a **P0 Candidate** in the portfolio evaluation, but is **not an Approved Provider** and **not an Implemented Provider**.
- No G2, G3, G4, or G5 activities are authorized for WTO ePing.
- WTO TFA Database remains a future candidate requiring separate G1 evaluation.

### 24.7 Next Steps

1. Maintain WTO ePing as Complementary Knowledge Source.
2. Explore non-automated access paths if SPS/TBT data is operationally required:
   - Periodic XLSX download and manual ingestion
   - Web portal monitoring
   - Email alert integration (manual)
3. Re-evaluate WTO ePing for Provider Candidate status if public API access becomes available.
4. Consider WTO TFA Database or alternative sources for SPS/TBT coverage if automated access is required.



## 25. WTO TFA Database G1 Decision Record

### 25.1 Decision

| Field | Value |
|-------|-------|
| **Decision** | **G1 CLOSED WITH CLASSIFICATION — WTO TFA Database reclassified as Complementary Knowledge Source** |
| **Date** | 2026-08-15 |
| **Decided By** | Project Owner |
| **Status** | **CLOSED WITH CLASSIFICATION** |
| **Scope** | WTO TFA Database access verification and G1 Gate outcome |
| **Effective** | Immediately upon owner approval |
| **Basis** | Provider Admission Criteria Section 12; G1 Live Verification attempt; Evidence-Based Development policy (PLAN.md Section 23.1) |

### 25.2 G1 Live Verification Evidence

| Verification Step | Result | Evidence |
|-------------------|--------|----------|
| WTO API Developer Portal listing | **Listed** | apiportal.wto.org/apis lists "Trade Facilitation Agreement Database (TFAD)" as REST API |
| Portal registration/sign-up | **Not completed** | Portal requires reCAPTCHA and real identity; outside project scope |
| API Key obtained | **No** | No key issued; no test key available |
| Endpoint tfadatabase.org/api/v1/members | **404/HTML** | https://tfadatabase.org/api/v1/members returned HTML "Page not found" |
| Endpoint tfadatabase.org/api/v1/measures | **404/HTML** | https://tfadatabase.org/api/v1/measures returned HTML "Page not found" |
| Endpoint tfadatabase.org/api/v1/notifications | **404/HTML** | https://tfadatabase.org/api/v1/notifications returned HTML "Page not found" |
| Endpoint data.wto.org/api/v1/tfad | **404 Not Found** | https://data.wto.org/api/v1/tfad returned 404 |
| Endpoint stats.wto.org/api/v1/tfad | **HTML** | https://stats.wto.org/api/v1/tfad returned HTML (main website), not JSON |
| OpenAPI/Swagger public spec | **Not available** | No public TFA API specification found |
| Public documentation with base URL/path | **Not available** | Portal pages render without API details when not authenticated |
| Live authenticated request | **Not possible** | No API key; no public endpoint confirmed |
| Third-party Sugra API | **Unreachable** | api.sugra.ai DNS resolution failed |

### 25.3 Provider Admission Criteria Assessment

| Criterion | Status | Evidence |
|-----------|--------|----------|
| 1. Documented Knowledge Coverage Gap | ⚠️ **PARTIAL** | Portfolio Plan classifies TFA under "Regulatory / SPS / TBT" family, but TFA Database actually covers Trade Facilitation, not SPS/TBT notifications. The gap addressed is Trade Facilitation, not SPS/TBT. |
| 2. API/Machine-Readable Access | ❌ **FAIL** | No verifiable public REST endpoint; all tested paths returned 404 or HTML. API listed in Developer Portal but not accessible without authentication. |
| 3. Tier A Status | ❌ **FAIL** | Cannot confirm Tier A without accessible API. Listing in portal alone is insufficient per Evidence-Based Development policy. |
| 4. Unique Knowledge Value | ✅ Satisfied | High — provides trade facilitation implementation data not available from existing providers |
| 5. Provider-Agnostic Compatibility | ✅ Satisfied | Adapter pattern compatible |
| 6. No Redundancy | ✅ Satisfied | No redundancy with existing providers |
| 7. Project Owner Approval | ⏳ Pending | Requires G1 PASS first |
| 8. Marginal Knowledge Value > 0 | ✅ Satisfied | High — fills Trade Facilitation gap |
| 9. Provider Ceiling Compliance | ⚠️ **CONSTRAINT** | Adding 6th provider reaches architectural ceiling of 4–6; requires explicit Project Owner approval to expand |

**G1 Verdict:** **INSUFFICIENT EVIDENCE / BLOCKED** — Criterion 2 (API/Machine-Readable Access) and Criterion 3 (Tier A Status) fail. No live verification possible. Criterion 1 partially fails due to coverage family mismatch.

### 25.4 Reclassification Rationale

WTO TFA Database is reclassified from **Provider Candidate** to **Complementary Knowledge Source** because:

1. **No verifiable public REST API:** All tested endpoint paths on tfadatabase.org and data.wto.org returned 404 or HTML. The API is listed in the WTO Developer Portal but not accessible without authentication.
2. **No API Key obtainable:** Registration requires reCAPTCHA and real-world identity outside project scope.
3. **Non-automated access available:** TFA data is accessible via:
   - Web portal: https://tfadatabase.org/
   - XLSX downloads: https://tfadatabase.org/en/excel/excel/notifications-matrix
   - HTML dashboards and member profiles
4. **Consistency with existing classification:** Codex, IPPC, and WTO ePing are classified as Complementary for the same reason (web-only, no documented REST API). WTO TFA Database now joins this classification.
5. **Future re-evaluation path:** WTO TFA Database may be re-evaluated for Provider Candidate status if:
   - Public REST endpoint documentation becomes available, OR
   - Project Owner obtains and documents API access via official channels, OR
   - WTO publishes open API specifications for TFA Database

### 25.5 Coverage Family Clarification

The WTO TFA Database covers **Trade Facilitation**, not **SPS/TBT**. The Portfolio Plan's "Regulatory / SPS / TBT" family conflates two distinct domains:
- **SPS/TBT:** Sanitary/phytosanitary requirements, technical barriers to trade (covered by WTO ePing, which is BLOCKED)
- **Trade Facilitation:** Customs procedures, import/export/transit, enquiry points, single window (covered by WTO TFA Database)

This conflation should be clarified in future portfolio updates. For G1 purposes, WTO TFA Database is evaluated against its actual coverage: Trade Facilitation.

### 25.6 Constraints

- This decision does **NOT** authorize implementation, WP creation, code changes, Contract/Schema changes, or provider execution.
- WTO TFA Database remains a **P0 Candidate** in the portfolio evaluation, but is **not an Approved Provider** and **not an Implemented Provider**.
- No G2, G3, G4, or G5 activities are authorized for WTO TFA Database.
- The Regulatory / SPS / TBT knowledge family remains at 0/10 coverage (SPS/TBT portion unfilled).
- The Trade Facilitation knowledge family remains unfilled by any automated provider.

### 25.7 Next Steps

1. Maintain WTO TFA Database as Complementary Knowledge Source.
2. Explore non-automated access paths if Trade Facilitation data is operationally required:
   - Periodic XLSX download and manual ingestion
   - Web portal monitoring
   - HTML scraping (outside project scope)
3. Re-evaluate WTO TFA Database for Provider Candidate status if public API access becomes available.
4. Consider alternative sources for Trade Facilitation coverage if automated access is required.


*Document Status: Approved — G3/G4/G5 Complete — Task 3 Closed — WTO ePing G1 Blocked — WTO TFA Database G1 Blocked — Ready for Next Priority Decision*















