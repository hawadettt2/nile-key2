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
| Provider Ceiling | **Operational ceiling: 7 providers** (expanded from 6 by Project Owner approval for World Bank LPI). This is an operational limit, not a fixed architectural ceiling. Further expansion requires separate Project Owner approval with documented Knowledge Coverage justification. |
| Next Action | Portfolio re-evaluation before any new provider implementation |

**Note:** This plan does not create WP-38e or any new Work Package. It defines the evaluation framework and decision criteria for future portfolio optimization.

**Provider Ceiling Policy:** The number of providers is not a goal or target. Providers are added only when a documented Knowledge Coverage gap exists, marginal knowledge value is proven, and operational feasibility is confirmed. The ceiling of 7 is an operational checkpoint, not a fixed architectural limit. Future expansions beyond 7 require separate Project Owner approval with documented Knowledge Coverage justification.

---

## 2. Current Portfolio Status

### 2.1 Implemented Providers (Baseline)

| Provider | Sub-WP | Status | Families Covered | Intelligence Type |
|----------|--------|--------|------------------|-------------------|
| MoaahExternalSourceAdapter | WP-38a | Closed | Regulatory, Market Access | Global/Egypt-focused |
| TradeDataExternalSourceAdapter | WP-38b | Closed | Trade Intelligence, Market Opportunity | 200+ countries |
| ZatcaExternalSourceAdapter | WP-38c | Closed | Regulatory, Market Access | Saudi Arabia |
| GccstatExternalSourceAdapter | WP-38d | Closed | Trade Intelligence, Rules of Origin | GCC-wide |
| FaostatExternalSourceAdapter | Task 3 | Closed | Trade Intelligence, Market Opportunity, Agrifood | Global |
| UncomtradeExternalSourceAdapter | Task 4 | Closed | Trade Intelligence | Global |
| WorldbankLpiExternalSourceAdapter | Phase 1 | G5 Closed | Logistics / Market Execution | Global |

**Total:** 7 implemented providers (Moaah, TradeData, ZATCA, GCC-Stat, FAOSTAT, UN Comtrade, World Bank LPI).

### 2.2 Remaining Candidates

| Sub-WP | Remaining Sources | Tier A | Tier B | Status |
|--------|-------------------|--------|--------|--------|
| WP-38a | Egypt Customs, WTO TFA, WTO Tariff, World Bank WITS | 1 (WITS conditional) | 3 | Planned/Future |
| WP-38b | NBD Trade Data, PST.AG, The Trade Hub, USITC HTS | 3 | 1 | Planned/Future |
| WP-38c | Jordan Trade Portal, Jordan Customs, UAE ICP, Saudi ZATCA Tariff | 0 | 4 | Planned/Future |
| WP-38d | Qatar Customs, Kuwait Customs, Oman Customs, Bahrain Customs | 0 | 4 | Planned/Future |

---

## 3. Seven-Family Knowledge Coverage Model

**Status:** VALIDATED / BASELINED  
**Authority:** This section is the authoritative reference for Knowledge Family definitions, boundaries, and gap assignment rules. It shall not be reopened unless new evidence proves a Knowledge Capability required by DEM is not representable within this framework.

The following seven families are the **fixed Knowledge Coverage Requirements** for DEM. Each family is evaluated independently; no family is required to map to a single provider.

### 3.1 Family Definitions

| # | Knowledge Family | Definition | Purpose / Decision Questions for DEM | In-Scope | Out-of-Scope | Core Knowledge Capabilities | Coverage Boundary |
|---|------------------|------------|-------------------------------------|----------|--------------|----------------------------|-------------------|
| 1 | **Trade Intelligence** | Knowledge of actual, historical, and current trade flows and commercial transactions. | What was traded, by whom, in what volume, and to where? | Trade statistics, shipment records, company profiles, HS-code-level trade flows, bilateral trade data | Market potential, tariff rates, logistics performance, regulatory requirements, origin documentation | Verified trade flow data, company-level transaction data, customs statistics, multilateral trade databases | Strong coverage when DEM can answer trade flow questions for target markets/commodities with official or verified commercial data |
| 2 | **Market Opportunity** | Knowledge of potential demand, growth segments, and export market identification. | Where should Egyptian exporters sell next? What markets have unmet demand? | Export potential scores, market demand forecasts, growth segment analysis, untapped market identification | Actual historical trade (Trade Intelligence), tariff schedules (Market Access), logistics costs (Logistics), product standards (Regulatory) | Market opportunity analytics, demand gap analysis, export potential rankings, sector-specific opportunity mapping | Adequate when DEM can identify high-potential markets with evidence beyond current trade patterns |
| 3 | **Market Access** | Knowledge of the **conditions** required to enter a foreign market (costs and procedures), excluding the technical content of those requirements. | What does it cost and what administrative steps are required to export to a target market? | Tariff schedules, duty rates, preferential rates under FTAs, import licensing requirements, quotas, market entry procedures, customs duties, tariff-line-level access conditions | Technical product standards (Regulatory / SPS / TBT), origin criteria and documentation (Rules of Origin), actual trade flows (Trade Intelligence), market demand (Market Opportunity), logistics performance (Logistics) | Authoritative tariff database, FTA preference lookup, duty calculation, market entry requirement registry | Adequate when DEM can determine the cost and procedural conditions for any target HS code / country pair |
| 4 | **Regulatory / SPS / TBT** | Knowledge of the **technical content** of requirements that products must meet to enter foreign markets. | What specific standards, limits, and conformity assessments must the product satisfy? | SPS measures (maximum residue limits, animal/plant health requirements), TBT (technical regulations, standards, conformity assessment procedures), product-specific compliance requirements, regulatory change monitoring | Tariff rates (Market Access), origin documentation (Rules of Origin), trade flow data (Trade Intelligence), market demand (Market Opportunity), logistics performance (Logistics) | Authoritative regulatory text database, product-specific requirement lookup, SPS/TBT notification tracking, standard alignment data | Adequate when DEM can provide the specific technical compliance requirements for a product-target market combination |
| 5 | **Rules of Origin** | Knowledge of the criteria, documentation, and procedures required to claim preferential treatment under free trade agreements. | How must an exporter document and prove origin to benefit from preferential tariffs? | Origin criteria (CC/CTH/regional value content), FTA-specific rules of origin, certificate of origin requirements, origin verification procedures, FTA utilization data | Tariff rates themselves (Market Access), technical product standards (Regulatory), trade flows (Trade Intelligence), market demand (Market Opportunity) | FTA rule lookup, origin criterion database, certificate of origin guidance, FTA utilization analytics | Adequate when DEM can determine the exact origin requirements and documentation needed for any FTA-covered product |
| 6 | **Agrifood Intelligence** | Knowledge specific to agricultural and food commodities, including their trade, prices, market conditions, and regulatory environment. *(Cross-cutting thematic family)* | What is happening specifically in agricultural and food markets that affects Egyptian exporters? | Agricultural trade flows, commodity prices, food safety incidents and alerts, agrifood-specific market access conditions, agricultural production/consumption data, export market conditions for food products | Non-agricultural trade and commodities, non-food logistics, general market opportunities unrelated to agrifood | Agrifood commodity price monitoring, food safety alert tracking, agricultural trade flow analysis, agrifood-specific opportunity identification | Adequate when DEM can answer agrifood-specific questions across the full decision chain (trade → opportunity → access → regulatory) |
| 7 | **Logistics / Market Execution** | Knowledge of the physical and procedural execution of cross-border trade. | How reliably, quickly, and cheaply can goods reach the target market? | Shipping performance, supply chain reliability, customs efficiency, port performance, logistics costs, cold chain data, transport infrastructure quality | Trade values and volumes (Trade Intelligence), market potential (Market Opportunity), tariff rates (Market Access), product standards (Regulatory), origin documentation (Rules of Origin) | Logistics performance index, shipping time/cost data, customs clearance time, supply chain reliability metrics | Adequate when DEM can assess the logistics profile of any target market or route |

### 3.2 Boundary Matrix — Adjacent Families

| Boundary | Primary Distinction | Overlap Area | Resolution Rule |
|----------|---------------------|--------------|-----------------|
| **Market Access ↔ Regulatory / SPS / TBT** | Market Access = conditions/costs of entry. Regulatory = technical content of requirements. | A single source may list both tariff rates and SPS standards. | **Primary Purpose Rule:** If the source's primary value is "what must the product comply with" → Regulatory. If "what does it cost/which permits are needed" → Market Access. A source providing both contributes to BOTH families, but each family's coverage score is evaluated independently. |
| **Trade Intelligence ↔ Market Opportunity** | Trade Intelligence = what happened. Market Opportunity = what could happen. | Trade flow analysis can reveal growth segments; opportunity analytics may use historical trade data. | **Output Orientation Rule:** If the knowledge answers "what was the volume/destination" → Trade Intelligence. If "where should we expand next" → Market Opportunity. Historical trade data alone does not satisfy Market Opportunity. |
| **Market Access ↔ Rules of Origin** | Market Access = the preferential rate. Rules of Origin = the proof needed to claim it. | FTA documentation is required to access preferential tariffs. | **Capability Separation Rule:** Market Access provides the rate lookup; Rules of Origin provides the documentation/criteria lookup. A source covering both provides two distinct capabilities. |
| **Agrifood Intelligence ↔ Trade Intelligence** | Agrifood = agrifood-specific subset. Trade Intelligence = all commodities. | FAOSTAT covers both global agricultural trade (Agrifood) and contributes to overall trade intelligence. | **Scope Filtering Rule:** If a source covers all commodities → Trade Intelligence. If it provides agrifood-specific depth (commodity prices, food safety alerts) → Agrifood. A source can satisfy BOTH families simultaneously. |
| **Agrifood Intelligence ↔ Market Access** | Agrifood = ag market conditions. Market Access = general tariff/access conditions. | Agrifood export guidance may include tariff information for food products. | **Primary Value Rule:** If the knowledge is "tariff rate for HS 1001" → Market Access. If it is "agrifood export market conditions for wheat" → Agrifood. Agrifood does NOT replace Market Access; it consumes Market Access outputs. |
| **Agrifood Intelligence ↔ Regulatory / SPS / TBT** | Agrifood = market conditions for food. Regulatory = technical compliance requirements. | Food safety alerts are both ag market intelligence and regulatory information. | **Content Focus Rule:** If the knowledge is "EU banned Egyptian citrus" → Agrifood Intelligence (incident/impact). If "EU pesticide residue limits for citrus" → Regulatory (technical requirement). The same source can serve both, but the capability differs. |
| **Logistics / Market Execution ↔ Trade Intelligence** | Logistics = execution metrics. Trade Intelligence = commercial flows. | Shipping volume data may appear in trade statistics. | **Domain Separation Rule:** Trade Intelligence answers "what was traded"; Logistics answers "how was it moved." Shipping volume is Logistics; trade value/volume is Trade Intelligence. |
| **Logistics / Market Execution ↔ Market Opportunity** | Logistics = execution feasibility. Market Opportunity = demand identification. | Logistics costs affect market attractiveness. | **Decision Stage Rule:** Market Opportunity identifies the market; Logistics assesses feasibility of serving it. Logistics data alone does not identify opportunity. |
| **Logistics / Market Execution ↔ Market Access** | Logistics = border-to-border performance. Market Access = border procedures and costs. | Customs efficiency is both a logistics metric and a market access condition. | **Measurement Type Rule:** Market Access = stated requirements/costs. Logistics = actual measured performance. A source providing "customs clearance time averages" → Logistics. A source providing "import licensing requirements" → Market Access. |

### 3.3 Gap Assignment Rules

A Knowledge Gap belongs to a family if and only if the missing capability is a **Core Knowledge Capability** of that family AND the gap cannot be filled by repurposing capabilities from another family.

| Rule | Description |
|------|-------------|
| **R1 — Primary Purpose Test** | A gap is assigned to the family whose primary decision question it blocks. If DEM cannot answer "what was traded?" → Trade Intelligence gap. If DEM cannot answer "where should we sell?" → Market Opportunity gap. |
| **R2 — Capability Non-Substitution Test** | A gap in one family cannot be filled by a capability from another family, even if adjacent. Logistics data does not fill a Trade Intelligence gap. |
| **R3 — Cross-Cutting Exception** | Agrifood Intelligence gaps are gaps in agrifood-specific knowledge, regardless of which underlying family they touch. Lack of agrifood-specific price monitoring is an Agrifood Intelligence gap, even though commodity prices could theoretically come from Trade Intelligence. |
| **R4 — No Double-Counting** | A single source may satisfy multiple families, but each family's coverage is assessed independently. FAOSTAT contributes to Trade Intelligence AND Agrifood Intelligence; both coverage scores reflect this. |
| **R5 — Complementary ≠ Provider** | Complementary Sources may provide partial coverage for a family, but do not satisfy the Coverage Boundary unless explicitly accepted (e.g., SPS/TBT is accepted as Complementary-Only). |

### 3.4 Overlap Rules — Preventing Double-Counting and False Coverage

| Rule | Description |
|------|-------------|
| **OR1 — One Primary Family Per Capability** | Each Knowledge Capability is assigned to exactly one primary family. A source providing that capability contributes to that family's coverage. |
| **OR2 — Multi-Family Sources Are Expected** | A source may legitimately contribute to multiple families (e.g., ITC Trade Map → Trade Intelligence + Market Opportunity). This is not double-counting; it is accurate coverage. |
| **OR3 — Agrifood Is Additive** | Agrifood Intelligence coverage is ADDITIONAL to base family coverage. A source covering agricultural trade flows contributes to Trade Intelligence AND Agrifood Intelligence. The Agrifood score does not replace the Trade Intelligence score. |
| **OR4 — No Score Multiplication** | A single source does not multiply a family's coverage score. Coverage is assessed on whether the family's Core Knowledge Capabilities are satisfied, not on how many sources touch the family. |
| **OR5 — Blocked Sources Do Not Count** | A source classified as Blocked / Pending Evidence contributes ZERO to any family's coverage until it passes the Pre-Candidate Evidence Gate. |
| **OR6 — Complementary Limits** | Complementary Sources may be acknowledged in gap definitions, but do not count toward Provider-level Coverage Score unless explicitly documented (e.g., SPS/TBT Complementary-Only acceptance). |

### 3.5 Coverage Boundary Definitions — When Is a Family "Adequately Covered"?

| Family | Adequate Coverage Means |
|--------|------------------------|
| **Trade Intelligence** | DEM can retrieve verified trade flow data for target markets/commodities, with official or high-quality commercial sources, at a granularity sufficient for export decision-making. |
| **Market Opportunity** | DEM can identify and rank export market opportunities beyond current trade patterns, with evidence-based demand and growth signals. |
| **Market Access** | DEM can determine tariff rates, preferential treatment eligibility, and administrative entry requirements for any target HS code / country pair. |
| **Regulatory / SPS / TBT** | DEM can retrieve specific technical compliance requirements (product standards, MRLs, conformity assessments) for target products and markets. *Note: The current portfolio accepts this family as Complementary-Only; the boundary above defines theoretical completeness.* |
| **Rules of Origin** | DEM can determine origin criteria, documentation requirements, and FTA eligibility for any covered product under any relevant FTA. |
| **Agrifood Intelligence** | DEM can answer agrifood-specific questions about prices, food safety incidents, and market conditions for Egyptian agricultural exports, independent of general commodity coverage. |
| **Logistics / Market Execution** | DEM can assess logistics performance, costs, and reliability for target markets and routes. |

### 3.6 Gap Definition — What Constitutes a Real Knowledge Gap

A **Knowledge Gap** exists within a family when:

1. **Missing Capability:** One or more Core Knowledge Capabilities of the family are not provided by any Implemented Provider or accepted Complementary Source.
2. **Decision Impact:** The missing capability blocks a decision that DEM must make.
3. **Non-Substitutable:** The capability cannot be derived from another family's coverage.
4. **Evidence-Based:** The gap is documented with specific examples of questions DEM cannot answer.

A **P0 Gap** is a gap that:
- Blocks critical business decisions (e.g., export compliance),
- Has no acceptable Complementary fallback, AND
- Is required for Minimal Sufficiency Portfolio.

A **P1 Gap** is a gap that:
- Limits decision quality but has workarounds,
- May be partially covered by existing providers, OR
- Is important but not critical for current phase.

### 3.7 Specific Boundary Clarifications

#### Market Access ↔ Regulatory / SPS / TBT
| Question Type | Belongs To |
|---------------|------------|
| "What is the tariff rate for HS 1001 into EU?" | Market Access |
| "What is the MRL for pesticide X in EU for oranges?" | Regulatory / SPS / TBT |
| "Does the EU require import licensing for citrus?" | Market Access (procedural requirement) |
| "What are the EU's phytosanitary requirements for Egyptian citrus?" | Regulatory / SPS / TBT |
| "What NTMs apply to Egyptian agrifood exports?" | Market Access (registry of measures) |
| "What is the technical content of EU pesticide residue standards?" | Regulatory / SPS / TBT |

**Rule:** Market Access = the **registry and cost** of requirements. Regulatory / SPS / TBT = the **technical content** of requirements.

#### Trade Intelligence ↔ Market Opportunity
| Question Type | Belongs To |
|---------------|------------|
| "What did Egypt export to Jordan in 2024?" | Trade Intelligence |
| "Which markets show growing demand for Egyptian oranges?" | Market Opportunity |
| "What is Egypt's current market share in GCC dates?" | Trade Intelligence (current state) |
| "Which African markets have high import potential for dates?" | Market Opportunity |

**Rule:** Trade Intelligence = descriptive (what is/happened). Market Opportunity = prescriptive/analytical (what could be).

#### Agrifood Intelligence as Cross-Cutting Family
Agrifood Intelligence is the only family that does not map to a single decision domain. It is a **thematic lens** applied to other families:
- Agrifood Trade Intelligence = agricultural trade flows (subset of Trade Intelligence)
- Agrifood Market Opportunity = export potential for agrifood (subset of Market Opportunity)
- Agrifood Market Access = tariff/access conditions for food products (subset of Market Access)
- Agrifood Regulatory = SPS/TBT for food products (subset of Regulatory)

**Rule:** Agrifood Intelligence is satisfied when DEM has agrifood-specific depth across the other families. It is NOT satisfied by general (non-agrifood) coverage.

### 3.8 Open Points / Future Revisit Conditions

| # | Open Point | Condition to Revisit |
|---|------------|---------------------|
| 1 | **Agrifood Intelligence scoring methodology** | If Agrifood becomes a standalone provider (not cross-cutting), the scoring model must be revised. Current model assumes Agrifood is additive to other families. |
| 2 | **Regulatory / SPS / TBT Complementary-Only acceptance** | If a verifiable public REST API emerges, the family may transition from Complementary-Only to Provider coverage. The family boundary definition remains valid regardless of provider status. |
| 3 | **NTM classification** | If future sources treat NTMs as a unified concept (registry + content), the Market Access / Regulatory split may need a formal "NTM Registry vs. NTM Content" rule. Current boundary handles this implicitly. |
| 4 | **Rules of Origin overlap with Market Access** | If a future source provides both preferential rates AND origin criteria as an integrated workflow, the family boundary remains valid; the source simply contributes to both. No merge needed. |

---

## 4. Coverage Scorecard (Evidence-Based)

### 4.1 Scoring Methodology

Scores are derived from verified provider capabilities and documented gaps. No invented values.

**Scoring Scale:**
- **0/10:** No coverage; no provider addresses this family
- **1-3/10:** Minimal coverage; partial or indirect only
- **4-6/10:** Partial coverage; some capabilities exist but gaps remain
- **7-8/10:** Strong coverage; major gaps filled
- **9-10/10:** Comprehensive coverage; only minor gaps remain

**Methodology:**
1. Score reflects **current operational coverage**, not theoretical capability
2. Authentication dependencies reduce effective coverage score
3. Web-only/complementary sources do not count toward automated coverage score
4. Scores marked **غير مؤكدة** indicate live validation not yet completed
5. Scores marked **Estimate** or **Inference** are expert assessments based on documented provider capabilities

### 4.2 Scorecard

| Family | Score (0-10) | Evidence | Inference |
|--------|--------------|----------|-----------|
| Trade Intelligence | 7/10 | TradeData covers 200+ countries shipment records; GCC-Stat covers GCC aggregates; UN Comtrade provides official global stats | Missing comprehensive official global coverage |
| Market Opportunity | 4/10 | TradeData provides shipment records; GCC-Stat provides economic indicators | No dedicated opportunity intelligence source |
| Market Access | 5/10 | Moaah provides duty rates and licensing; ZATCA provides Saudi tariff data | No dedicated global tariff database |
| Regulatory / SPS / TBT | 0/10 | No implemented provider covers SPS/TBT; proposed WTO ePing covers majority of global SPS/TBT notifications | 9/10 rather than 10/10 because complete coverage would require additional national/regional sources beyond current scope |
| Rules of Origin | 3/10 | GCC-Stat provides GCC aggregates | No dedicated rules of origin database |
| Agrifood Intelligence | 8/10 | FAOSTAT + FPI extension implemented; live validation passed; price monitoring confirmed | Impact verified — highest business priority |
| Logistics / Market Execution | 5/10 | World Bank LPI implemented; G5 CLOSED | Gap closed for global logistics performance data |

**Overall Portfolio Coverage Calculation:**

**Formula:** Simple average of all seven family scores.

**Current baseline (pre-UN Comtrade, pre-FPI, pre-LPI):** ~2.7/10
- Calculation: (7 + 4 + 5 + 0 + 3 + 0 + 0) / 7 = 19/7 ≈ 2.7

**Current state (post-UN Comtrade, post-FPI, post-LPI):** ~4.6/10
- Calculation: (7 + 4 + 5 + 0 + 3 + 8 + 5) / 7 = 32/7 ≈ 4.6
- Note: This is an **Estimate** based on current scores. Actual score requires live validation of all providers.

**With minimal sufficient portfolio (if P0 gaps filled):** ~4.6/10 → ~5.9/10
- Would require WTO ePing (SPS/TBT) + verifiable public REST API
- Calculation with P0 filled: (7 + 4 + 5 + 9 + 3 + 8 + 5) / 7 = 41/7 ≈ 5.9

**Evidence Basis:** Verified from implemented provider test suites, adapter specifications, and documented API capabilities. Scores marked as Inference are explicitly labeled.

### 4.3 Resilience Matrix

Resilience is evaluated across four dimensions: authentication dependency, access dependency, operational independence, and provider diversity. Provider count alone does not indicate strong resilience.

| Knowledge Family | Primary Source | Auth Dependency | Access Dependency | Operational Independence | Fallback Exists? | Fallback Independence | Resilience Rating |
|------------------|----------------|-----------------|-------------------|---------------------------|------------------|----------------------|-------------------|
| Trade Intelligence | UN Comtrade + TradeData + GCC-Stat + FAOSTAT | Mixed (none/JWT/key) | Mixed (free/key/JWT) | High — 4 independent sources | Yes | High — multiple independent sources | ✅ Strong |
| Market Opportunity | TradeData (indirect) | API key required | Commercial API | Low — single provider | Partial | Low — GCC-Stat indirect only | ❌ Weak |
| Market Access | Moaah (primary), ZATCA (KSA only) | API key required | Commercial API | Medium — geographic gaps | Partial | Low — no global fallback | ⚠️ Moderate |
| Regulatory / SPS / TBT | None | N/A | N/A | None | **No** | N/A | ❌ None |
| Rules of Origin | GCC-Stat | API key required | SDMX/REST | Medium — GCC scope only | No | N/A | ❌ Weak |
| Agrifood Intelligence | FAOSTAT + FPI extension | JWT required | Authenticated API | Medium — FAO is stable | No direct equivalent | Medium — FAO is authoritative | ✅ Medium |
| Logistics / Market Execution | World Bank LPI | None | Free REST API | High — independent source | Yes | Medium — UNCTAD bulk fallback | ✅ Strong |

**Key Resilience Findings:**

1. **Three families have NO fallback:** Regulatory/SPS-TBT, Logistics, Rules of Origin
2. **Market Opportunity has single-provider dependency:** TradeData failure = zero opportunity intelligence
3. **Agrifood is most resilient:** Two sources (FAOSTAT + FPI) with different data types
4. **Trade Intelligence is most resilient:** Four providers across different scopes and authentication methods
5. **Authentication dependency reduces resilience:** Three providers require API keys, one requires JWT. Only UN Comtrade works without credentials.

---

## 5. Agrifood Cross-Cutting Priority Model

Agrifood Intelligence is a **cross-cutting strategic priority**, not a separate isolated family. It must be evaluated across all seven families with an agricultural lens.

### 5.1 Agrifood Relevance Matrix

| Knowledge Family | Agrifood Relevance | Current Agrifood Coverage | Required Capability |
|------------------|-------------------|---------------------------|---------------------|
| Trade Intelligence | **Very High** — agricultural trade flows | ❌ None | FAOSTAT trade statistics |
| Market Opportunity | **Very High** — export market identification for agrifood | ❌ None | ITC Export Potential Map |
| Market Access | **Very High** — tariffs and NTMs for food products | ⚠️ Partial (Moaah) | ITC Market Access Map |
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

**Agrifood Coverage Target:** 8/10 with FAOSTAT + FPI extension; current actual coverage = 8/10 (FAOSTAT implemented + FPI extension)

---

## 6. Source Classification Framework

### 6.1 Implemented Providers (7)

**Evidence:** Verified from baseline tags, test suites, and git history.

| Provider | Sub-WP | Status | Families Covered |
|----------|--------|--------|------------------|
| MoaahExternalSourceAdapter | WP-38a | Closed | Regulatory, Market Access |
| TradeDataExternalSourceAdapter | WP-38b | Closed | Trade Intelligence, Market Opportunity |
| ZatcaExternalSourceAdapter | WP-38c | Closed | Regulatory, Market Access |
| GccstatExternalSourceAdapter | WP-38d | Closed | Trade Intelligence, Rules of Origin |
| FaostatExternalSourceAdapter | Task 3 | Closed | Trade Intelligence, Market Opportunity, Agrifood |
| UncomtradeExternalSourceAdapter | Task 4 | Closed | Trade Intelligence |
| WorldbankLpiExternalSourceAdapter | Phase 1 | G5 Closed | Logistics / Market Execution |

### 6.2 Provider Candidates

**Definition:** Sources that can become providers **only if** they satisfy all Provider Admission Criteria (Section 11) and pass G1 Gate.

**Classification Rule:** A source is a Provider Candidate only if it has documented, accessible REST/SDMX/JSON API or confirmed machine-readable access AND has passed the Pre-Candidate Evidence Gate (Section 12.1). Web-only sources are **not** Provider Candidates. Sources that have not passed the Pre-Candidate Evidence Gate are classified as **Blocked / Pending Evidence**.

| Source | Families Covered | Agrifood Relevance | Officiality | API/Machine Readability | Admission Status |
|--------|------------------|--------------------|-------------|------------------------|------------------|
| WTO Timeseries API | Market Access, Trade Intelligence | Medium | Very High (WTO) | ⚠️ Free registration + subscription key required | **Blocked / Pending Evidence** |
| WTO Tariff & Trade Data (TTD) | Market Access | Medium | Very High (WTO) | Web platform + raw downloads; usage restrictions apply (CMA Annex 4) | **Complementary** |
| WTO TFA Database | Market Access | Medium | Very High (WTO) | ❌ No verifiable public REST endpoint; Blocked / Pending Evidence | **Blocked / Pending Evidence** |
| UNCTADstat | Trade Intelligence | Low | High (UN) | ⚠️ SDMX | **Blocked / Pending Evidence** |
| IMF IMTS | Trade Intelligence | Low | High (IMF) | ⚠️ API | **Blocked / Pending Evidence** |

**Note:** Codex and IPPC are **web-only** (no documented REST/SDMX/JSON API). They do **not** meet Provider Admission Criteria. They are classified as Complementary Knowledge Sources (Section 6.3), not Provider Candidates.

### 6.3 Complementary Knowledge Sources / Tools

**Definition:** Sources that provide useful knowledge but do **not** currently meet Provider Admission Criteria. These are tracked for future evaluation if machine-readable access becomes available.

| Source | Families Covered | Agrifood Relevance | Access Type | Status |
|--------|------------------|--------------------|-------------|--------|
| Codex (FAO/WHO) | Regulatory / SPS/TBT | Critical (food safety) | Web only | **Complementary** |
| WTO ePing | Regulatory / SPS/TBT | Critical (food safety, phytosanitary) | Web portal + XLSX; no verifiable public REST API | **Blocked / Pending Evidence** |
| IPPC (FAO) | Regulatory / SPS/TBT | Critical (plant health) | Web only | **Complementary** |
| ITC Export Potential Map | Market Opportunity | High | Web only | **Complementary** |
| ITC Market Access Map | Market Access | High | Web + bulk download | **Complementary** |
| ITC Trade Map | Trade Intelligence, Market Access | Medium | Web + download | **Complementary** |
| ITC Rules of Origin Facilitator | Rules of Origin | Medium | Web only | **Complementary** |
| WTO I-TIP | Regulatory, Market Access | Medium | Web + limited API | **Complementary** |
| Access2Markets | Market Access | Medium | Web only | **Complementary** |
| **UNCTAD LSCI** | **Logistics / Market Execution** | **Medium-High** | **❌ No documented public REST API; CSV/bulk download only** | **Complementary / Bulk-Only** |
| **UNCTAD PLSCI** | **Logistics / Market Execution** | **Medium** | **❌ No documented public REST API; CSV/bulk download only** | **Complementary / Bulk-Only** |
| UNCTADstat | Trade Intelligence | Low | ⚠️ SDMX | **Blocked / Pending Evidence** |
| IMF IMTS | Trade Intelligence | Low | ⚠️ API | **Blocked / Pending Evidence** |
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
| Trade Intelligence | 7/10 | — | 9/10 | P1 |
| Market Opportunity | 4/10 | — | 6/10 | P2 |
| Market Access | 5/10 | WTO Timeseries API (Blocked / Pending Evidence) / TTD platform (Complementary) | 8/10 | P1 |
| Regulatory / SPS / TBT | 0/10 | WTO ePing | 9/10 | **P0** |
| Rules of Origin | 3/10 | — | 3/10 | P3 |
| **Agrifood Intelligence** | **غير مؤكدة → 8/10** | **FAOSTAT + FPI extension** | **8/10** | **P0 — Implemented** |
| Logistics / Market Execution | 5/10 | — | 5/10 | **P1 — Implemented** |

**Overall Portfolio Coverage:** ~4.6/10 (current) → ~5.9/10 (with P0 gaps filled if WTO ePing becomes accessible)

### 7.2 Agrifood Cross-Cutting Coverage

| Family | Agrifood Gap | Proposed Source | Agrifood Value |
|--------|--------------|-----------------|----------------|
| Trade Intelligence | Agricultural trade flows missing | FAOSTAT | **Very High** |
| Market Opportunity | No ag export opportunity data | FAOSTAT FPI extension | **Very High** |
| Market Access | No ag-specific tariff/NTM data; no trade facilitation measures data | WTO Timeseries API (Blocked / Pending Evidence) / TTD (Complementary via ITC Map); WTO TFA Database (Blocked / Pending Evidence) | **High** |
| Regulatory / SPS/TBT | No SPS/TBT for food products | WTO ePing | **Critical** |
| Rules of Origin | No ag-specific origin rules | ITC Rules of Origin Facilitator (complementary) | **Medium** |
| Logistics | No ag-specific logistics data | World Bank LPI (Implemented) | **Medium** |

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
| **FAOSTAT** | Trade Intelligence, Market Opportunity, Agrifood | Very High | Very High (FAO) | JWT required | Very High | **Keep** |
| **UN Comtrade** | Trade Intelligence | Low | Very High (UN) | ✅ Free API | Very High (official global stats) | **Keep** |
| **World Bank LPI** | **Logistics / Market Execution** | **Medium** | **High (World Bank)** | **✅ Free REST API** | **Medium** | **Implemented** |

**Evidence:** All 7 providers are implemented, tested, and baselined with baseline tags. World Bank LPI G5 CLOSED.

### 8.3 Provider Candidates Re-Evaluation

| Source | Families Covered | Agrifood Relevance | Officiality | API | Uniqueness | Verdict |
|--------|------------------|--------------------|-------------|-----|------------|---------|
| WTO Timeseries API | Market Access, Trade Intelligence | Medium | Very High (WTO) | ⚠️ Free registration + subscription key required | High (tariff + trade data) | **Blocked / Pending Evidence** |
| WTO Tariff & Trade Data (TTD) | Market Access | Medium | Very High (WTO) | Web platform + raw downloads; CMA Annex 4 restrictions apply | High (official tariffs) | **Complementary** |
| WTO TFA Database | Market Access | Medium | Very High (WTO) | ❌ No verifiable public REST API; Blocked / Pending Evidence | High (trade facilitation measures) | **Blocked / Pending Evidence** |
| UNCTADstat | Trade Intelligence | Low | High (UN) | ⚠️ SDMX | Medium | **Blocked / Pending Evidence** |
| IMF IMTS | Trade Intelligence | Low | High (IMF) | ⚠️ API | Medium | **Blocked / Pending Evidence** |

### 8.4 Complementary Sources Re-Evaluation

| Source | Families Covered | Agrifood Relevance | Access Type | Verdict |
|--------|------------------|--------------------|-------------|---------|
| Codex (FAO/WHO) | Regulatory / SPS/TBT | Critical (food safety) | Web only | **Complementary** |
| WTO ePing | Regulatory / SPS/TBT | Critical (food safety, phytosanitary) | Web portal + XLSX; no verifiable public REST API | **Blocked / Pending Evidence** |
| IPPC (FAO) | Regulatory / SPS/TBT | Critical (plant health) | Web only | **Complementary** |
| ITC Market Access Map | Market Access | High | Web + bulk | **Complementary** |
| ITC Export Potential Map | Market Opportunity | High | Web only | **Complementary** |
| ITC Trade Map | Trade Intelligence, Market Access | Medium | Web + download | **Complementary** |
| ITC Rules of Origin Facilitator | Rules of Origin | Medium | Web only | **Complementary** |
| WTO I-TIP | Regulatory, Market Access | Medium | Web + limited API | **Complementary** |
| Access2Markets | Market Access | Medium | Web only | **Complementary** |
| **UNCTAD LSCI** | **Logistics / Market Execution** | **Medium-High** | **❌ No documented public REST API; CSV/bulk download only** | **Complementary / Bulk-Only** |
| **UNCTAD PLSCI** | **Logistics / Market Execution** | **Medium** | **❌ No documented public REST API; CSV/bulk download only** | **Complementary / Bulk-Only** |

**Note:** All web-only sources are Complementary, not Provider Candidates. They may be re-evaluated for Candidate status only if documented machine-readable access is confirmed.

**ITC Strategic Value Note:** ITC tools (Trade Map, Market Access Map, Export Potential Map, Rules of Origin Facilitator) have **Very High strategic value** for Egyptian agrifood exports. However, they have **no documented public REST API** and therefore **zero provider feasibility** under current integration patterns. They should be treated as **Strategic Complementary Sources** and may be accessed via bulk download or web automation in the future if API access becomes available.

**UNCTAD LSCI/PLSCI Note:** UNCTAD LSCI and PLSCI have **no documented public REST API**. Access is via CSV export per table and bulk download facility only. They are classified as **Complementary / Bulk-Only** and cannot be implemented as providers following the established adapter pattern without custom bulk-download + local parsing infrastructure.

---

## 9. Marginal Knowledge Value Analysis

### 9.1 Marginal Value by Candidate

| Candidate | Marginal Knowledge Value | Marginal Cost | Net Value | Decision |
|-----------|--------------------------|---------------|-----------|----------|
| **WTO ePing** | **Very High** — fills critical SPS/TBT gap | Medium | **Positive** | **Blocked / Pending Evidence** |
| **FAOSTAT** | **Very High** — fills critical Agrifood gap | Medium | **Positive** | **Implemented** |
| **WTO TFA Database** | **High** — trade facilitation for agrifood | Medium | **Positive** | **Blocked / Pending Evidence** |
| **UN Comtrade** | **High** — official global trade stats | Medium | **Positive** | **Implemented** |
| **WTO Timeseries API** | **High** — official tariff + trade data | Medium | **Positive** | **Blocked / Pending Evidence** |
| WTO Tariff & Trade Data (TTD) | High — official tariff data | Low | **Positive** | **Complementary** |
| **FAO Food Price Index** | **Medium** — commodity price monitoring | Low | **Positive** | **Implemented via FAOSTAT FPI extension** |
| **World Bank LPI** | **Medium** — logistics performance | Low | **Positive** | **Implemented** |
| UNCTADstat | Low — similar to UN Comtrade | Medium | **Marginal** | **Blocked / Pending Evidence** |
| IMF IMTS | Low — regional focus | Medium | **Marginal** | **Blocked / Pending Evidence** |
| All Tier B sources | Very Low — web scraping required | High | **Negative** | **Remove from active consideration** |
| Codex | N/A — web-only | N/A | **N/A** | **Complementary** (not candidate) |
| IPPC | N/A — web-only | N/A | **N/A** | **Complementary** (not candidate) |
| All other Complementary sources | N/A — web-only or limited value | N/A | **N/A** | **Complementary** (not candidates) |

### 9.2 Diminishing Returns Threshold

**Diminishing returns begin when:**
1. All P0 and P1 gaps are filled
2. Next candidate adds coverage to P2 or P3 family only
3. Next candidate duplicates existing provider functionality without unique value
4. Provider count approaches operational ceiling (currently 7, expanded by Project Owner approval for World Bank LPI)

**Current Status:** 7 implemented providers (Moaah, TradeData, ZATCA, GCC-Stat, FAOSTAT, UN Comtrade, World Bank LPI). Proposed additions bring total to 9 (7 implemented + 2 proposed). Diminishing returns threshold not yet reached.

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
| **World Bank LPI** | **Logistics / Market Execution** | **Medium** | **Keep** | **Implemented** |
| **WTO ePing** | **Regulatory / SPS/TBT** | **Critical** | **P0** | **Blocked / Pending Evidence** |
| **FAOSTAT** | **Trade Intelligence, Market Opportunity, Agrifood** | **Very High** | **Keep** | **Implemented** |
| **WTO TFA Database** | **Market Access** | **Medium** | **P0** | **Blocked / Pending Evidence** |

**Total:** 9 providers (7 implemented + 2 proposed). FAO Food Price Index is implemented via FAOSTAT FPI extension without creating a new provider.

**Note:** This is the **minimum sufficient portfolio** to address P0 gaps (SPS/TBT, Agrifood, Market Access Trade Facilitation). The current operational ceiling is 7 providers (expanded from 6 by Project Owner approval for World Bank LPI). Adding 2 P0 providers (WTO ePing, WTO TFA Database) would bring total to 8, which exceeds the current operational ceiling and requires explicit Project Owner approval with documented Knowledge Coverage justification. P1 additions: UN Comtrade is implemented; WTO Timeseries API is Blocked / Pending Evidence (Pre-Candidate Evidence Gate not passed). FAO Food Price Index is now implemented via FAOSTAT FPI extension without creating a new provider.

**Current Phase:** Phase 1 (World Bank LPI) is activated. World Bank LPI is the current execution path.

**WTO Clarification:** "WTO ePing" covers SPS/TBT notifications. "WTO TFA Database" covers trade facilitation measures classified under Market Access. These are separate capabilities. Both are currently Blocked / Pending Evidence (no verifiable public REST API). If either becomes accessible, it would be the primary candidate for its respective gap. The WTO Timeseries API is a separate offering requiring free registration + subscription key; it covers trade statistics and market access indicators including tariffs. It is currently Blocked / Pending Evidence (Pre-Candidate Evidence Gate not passed: commercial licensing unclear, Egypt data insufficient, HTTP-only).

### 10.2 Coverage After Minimal Sufficient Portfolio

| Knowledge Family | Current Score | Target Score | Improvement |
|------------------|---------------|--------------|-------------|
| Trade Intelligence | 7/10 | 8/10 | +FAOSTAT |
| Market Opportunity | 4/10 | 6/10 | +FAOSTAT |
| Market Access | 5/10 | 5/10 | No change |
| Regulatory / SPS / TBT | 0/10 | 9/10 | +WTO ePing (blocked) |
| Rules of Origin | 3/10 | 3/10 | No change |
| Agrifood Intelligence | 8/10 | 8/10 | +FAOSTAT (implemented) |
| Logistics / Market Execution | 5/10 | 5/10 | +World Bank LPI (implemented) |

**Overall Portfolio Coverage:** ~4.6/10 (current) → ~5.9/10 (with P0 gaps filled if WTO ePing becomes accessible)

**Note:** P1 additions: WTO Timeseries API is Blocked / Pending Evidence (Pre-Candidate Evidence Gate not passed). UN Comtrade is already implemented. World Bank LPI is implemented. P2 additions (FAO Food Price Index) would further improve coverage but are not required for minimal sufficiency.

---

## 11. P0/P1/P2 Priorities

### 11.1 P0 — Critical (Must Add for Minimal Sufficiency)

| Priority | Source | Knowledge Family | Agrifood Relevance | Rationale |
|----------|--------|------------------|--------------------|-----------|
| P0 | **WTO ePing** | Regulatory / SPS/TBT | Critical | Export compliance risk; no current coverage; **Blocked / Pending Evidence — Pre-Candidate Evidence Gate not passed** |
| P0 | **WTO TFA Database** | Market Access | Medium | Trade facilitation measures for agrifood; **Blocked / Pending Evidence — Pre-Candidate Evidence Gate not passed** |

**Note:** WTO ePing and WTO TFA Database are currently Blocked / Pending Evidence. They remain P0 priorities but cannot proceed to Candidate or implementation until Pre-Candidate Evidence Gate is passed (verifiable public REST API confirmed).

### 11.2 P1 — High Value (Requires Ceiling Expansion Approval)

| Priority | Source | Knowledge Family | Agrifood Relevance | Rationale |
|----------|--------|------------------|--------------------|-----------|
| P1 | **UN Comtrade** | Trade Intelligence | Low | Official global trade stats; stronger than TradeData for official data |
| P1 | **WTO Timeseries API** | Market Access, Trade Intelligence | Medium | Official tariff + trade data; free registration + subscription key required; complements Moaah; **Blocked / Pending Evidence — Pre-Candidate Evidence Gate not passed** |

**Note:** With 2 P0 providers blocked, the current portfolio has 7 implemented providers. WTO Timeseries API, UNCTADstat, and IMF IMTS are Blocked / Pending Evidence and cannot proceed to Candidate or implementation until Pre-Candidate Evidence Gate is passed. Any additional candidate would bring total to 8+, which exceeds the current operational ceiling of 7 and requires explicit Project Owner approval with documented justification for ceiling expansion.

### 11.3 P2 — Medium Value (Complementary or Future Consideration)

| Priority | Source | Knowledge Family | Agrifood Relevance | Rationale |
|----------|--------|------------------|--------------------|-----------|
| P2 | **FAO Food Price Index** | Market Opportunity, Agrifood | Very High | Commodity price monitoring; implemented via FAOSTAT FPI extension |

**Note:** FAO Food Price Index is now implemented via FAOSTAT FPI extension (no new provider created). It was previously a Candidate P2.

**ITC Strategic Value Note:** ITC tools (Export Potential Map, Market Access Map) have Very High strategic value for Egyptian agrifood exports but have no documented public REST API. They are classified as Strategic Complementary Sources and may be integrated via bulk download or web automation in the future if API access becomes available.

### 11.4 P3 — Low Priority (Defer or Complementary)

| Priority | Source | Knowledge Family | Rationale |
|----------|--------|------------------|-----------|
| P3 | UNCTAD LSCI | Logistics | Medium-High strategic value; **no documented public REST API; CSV/bulk download only** |
| P3 | UNCTAD PLSCI | Logistics | Medium strategic value; **no documented public REST API; CSV/bulk download only** |
| P3 | ITC Export Potential Map | Market Opportunity | Very High strategic value; web-only; no provider feasibility currently |
| P3 | ITC Market Access Map | Market Access | High strategic value; web + bulk download; no provider feasibility currently |
| P3 | ITC Trade Map | Trade Intelligence, Market Access | Medium strategic value; web + download; no provider feasibility currently |
| P3 | ITC Rules of Origin Facilitator | Rules of Origin | Medium strategic value; web-only; no provider feasibility currently |
| P3 | UNCTADstat | Trade Intelligence | Similar to UN Comtrade; lower priority; **Blocked / Pending Evidence** |
| P3 | IMF IMTS | Trade Intelligence | Regional focus; UN Comtrade more comprehensive; **Blocked / Pending Evidence** |
| P3 | Access2Markets | Market Access | EU-only; limited GCC relevance |
| P3 | WTO I-TIP | Regulatory, Market Access | Overlaps with ePing; limited API |
| P3 | All Tier B sources | Various | Web-only; out of scope |
| P3 | Codex | Regulatory / SPS/TBT | Web-only; Complementary |
| P3 | IPPC | Regulatory / SPS/TBT | Web-only; Complementary |
| P3 | All other web-only sources | Various | No documented API; Complementary |

---

## 12. Provider Admission Criteria

A new provider may be added **only if all** of the following are satisfied:

1. **Documented Knowledge Coverage Gap / Sufficiency Need:** The source addresses a documented gap or advance toward Knowledge Sufficiency / Knowledge Completion in the Seven-Family Knowledge Coverage Matrix. Priority is given to P0/P1 gaps, but P2/P3 additions are allowed when Coverage, Marginal Value, and Resilience justify the addition.
2. **API/Machine-Readable Access:** The source has a documented, accessible REST/SDMX/JSON API or confirmed machine-readable access. Web-only sources are out of scope.
3. **Tier A Status:** The source qualifies as Tier A per the parent plan criteria (documented API, accessible, reliable).
4. **Unique Knowledge Value:** The source provides intelligence that cannot be obtained from existing providers with acceptable quality.
5. **Provider-Agnostic Compatibility:** The source can be integrated without modifying DEM core, Contract, or Schema.
6. **No Redundancy:** The source does not duplicate functionality of an existing provider without adding measurable value.
7. **Project Owner Approval:** G1 approval is obtained after Task 1 evaluation, unless delegated per Owner Approval Delegation Principle (Section 28.1).
8. **Marginal Knowledge Value > 0:** The source adds positive marginal knowledge value after accounting for maintenance burden.
9. **Provider Ceiling Compliance:** Addition complies with the operational provider ceiling. The current operational ceiling is 7 providers, approved by Project Owner for World Bank LPI. Further expansion requires separate Project Owner approval with documented Knowledge Coverage justification. Provider count is not a goal; Knowledge Coverage is the primary driver.

**Important:** No candidate is Approved or Implemented before completing the full gate sequence (G0→G1→G2→G3→G4→G5).

### 12.1 Pre-Candidate Evidence Gate

A source must satisfy the following **before** being classified as a Provider Candidate. This gate verifies minimum viability and operational feasibility. It is distinct from G1/Implementation Readiness and does not require implementation-level detail.

**12.1.1 Mandatory Evidence — All Sources**

| # | Evidence Requirement | Purpose | Verification Method |
|---|----------------------|---------|---------------------|
| 1 | **Live Access Verified** | The source is actually reachable and returns data, not only listed on a portal or documentation site. | Live request/access test with documented result |
| 2 | **Knowledge Relevance Verified** | The source contains data relevant to the stated Knowledge Gap and target market(s), including Egypt/MENA when that is the stated scope. | Live query or sample retrieval for target indicator/market |
| 3 | **Operational Feasibility Confirmed** | The source can be accessed within DEM's operational constraints (authentication, format, rate limits, volume). | Documented test result showing successful retrieval |

**12.1.2 Mandatory Evidence — Machine-Readable Sources Only**

| # | Evidence Requirement | Purpose | Verification Method |
|---|----------------------|---------|---------------------|
| 4 | **Transport Security Verified** | If the source provides machine-readable access, it must support HTTPS/TLS, or a security team must have documented an acceptable risk mitigation strategy. | HTTPS/TLS test or documented risk acceptance |
| 5 | **Commercial Licensing Clarified** | If the source data will be used in a commercial product, commercial-use permission must be confirmed or legally cleared. | License review or written permission |

**12.1.3 Evidence Quality Rules**

- Evidence must come from **live testing or direct official documentation**, not from inferred assumptions.
- Evidence must include **actual query results** for the target market/indicator when that is the stated scope.
- If any mandatory item is **unverified or failed**, the source is classified as **Blocked / Pending Evidence**, not Candidate.
- Items that are **not applicable** to the source type (e.g., HTTPS for web-only sources) are marked **N/A** and do not block Candidate status.

**12.1.4 Status Definitions**

| Status | Meaning |
|--------|---------|
| **Candidate** | Has passed all applicable Pre-Candidate Evidence requirements. |
| **Blocked / Pending Evidence** | Has potential but one or more Pre-Candidate Evidence items are unverified or failed. Re-evaluation requires new evidence. |
| **Rejected** | Failed Pre-Candidate Evidence and is not viable for the stated gap under current constraints. |

**12.1.5 Gate Sequence**

```
Source → Pre-Candidate Evidence Gate → Candidate → G0 → G1 → G2 → G3 → G4 → G5 → Implemented Provider
```

**12.1.6 Scope Boundary**

The Pre-Candidate Evidence Gate verifies **viability**, not **implementation readiness**. The following are **deferred to G1** unless they are blocking for viability:
- Detailed schema mapping
- Pagination/rate-limit behavior under production load
- Full filtering capability matrix
- Error-handling contract details
- Performance benchmarking

**12.1.7 Exception**

Sources that are **web-only** and classified as Complementary do not pass through this gate. This gate applies only to sources that could become Provider Candidates (machine-readable access confirmed).

---

## 13. Provider Stopping Condition

**Provider Expansion stops when any of the following is true:**

1. **Knowledge Sufficiency / Knowledge Completion:** All Seven-Family Knowledge Coverage targets are achieved and no further knowledge value can be gained.
2. **Marginal Knowledge Value = 0:** The next candidate provider would add no unique knowledge value or would only cover P2/P3 families without sufficient justification.
3. **Redundancy Threshold:** The next candidate would duplicate existing provider functionality without unique value.
4. **Maintenance Burden Ceiling:** The operational cost of maintaining additional providers exceeds the knowledge value gained.
5. **Business Priority Shift:** The business determines that current coverage is sufficient for the current phase and priorities shift to other system capabilities.

**Completion Principle:** The portfolio does not end at a fixed provider count. The true end state is **Knowledge Sufficiency / Knowledge Completion** across all Seven Families. The portfolio follows a continuous cycle:

**Add Provider → Measure Coverage → Measure Marginal Value → Measure Resilience → Re-evaluate → Add again if justified.**

Provider count is **not** a stopping criterion. The parent plan's 4–6 provider recommendation was architectural guidance that has been operationally expanded to 7 by Project Owner approval for World Bank LPI. Further expansion beyond 7 requires separate Project Owner approval with documented Knowledge Coverage justification.

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
| **A. Phase 1 — World Bank LPI (Current)** | World Bank LPI is the 7th implemented provider (total 7) — fills empty Logistics / Market Execution family — **G5 CLOSED** | Current Operational State (7/7 providers; current ceiling = 7; expansion possible with justification) |
| **B. Add P0 Providers** | Add WTO ePing, WTO TFA Database (2 providers; total 8) — FAOSTAT + UN Comtrade already implemented — **both currently Blocked / Pending Evidence** | Project Owner approval + Ceiling Expansion Approval per Section 26.5.2; requires documented Knowledge Coverage justification |
| **C. Close WP-38** | Formally close WP-38; keep current providers as baseline | Project Owner acceptance |
| **D. Maintain Current State** | Continue with 7 implemented providers; no new additions at this time | Business decision; does not preclude future expansion if justified |

### 14.3 Recommended Path

**Current Path — Phase 1 (World Bank LPI)** with the following sequence:

1. **Phase 1 (Current):** World Bank LPI — fills empty Logistics / Market Execution family (total 7 providers) — FAOSTAT + UN Comtrade already implemented
   - **Note:** Provider ceiling expanded to 7 by Project Owner approval (Section 26). This is the current operational state, not a permanent portfolio end state.
   - **Note:** World Bank LPI has completed all gates (G1–G5) and is CLOSED as Implemented Provider. Current portfolio state is Maintain Current State (7/7 providers, current ceiling = 7).
2. **Phase 2 (Future — Blocked):** WTO Timeseries API — fills Market Access and Trade Intelligence gaps (requires API key registration; **Blocked / Pending Evidence — Pre-Candidate Evidence Gate not passed**)
3. **Phase 3 (Future):** ITC Strategic Complementary — maintain as strategic sources; no automated provider addition unless API access becomes available
4. **Phase 4 (Future):** UNCTAD LSCI/PLSCI — maintain as Complementary / Bulk-Only maritime logistics sources
5. **Phase 5 (Blocked):** WTO ePing / WTO TFA Database — SPS/TBT and Market Access trade facilitation gaps remain blocked until public REST API becomes available. If either becomes accessible, ceiling expansion review per Section 26.5.2 is triggered.
6. **Stop** when Knowledge Sufficiency / Knowledge Completion is achieved across all Seven Families
7. **Re-evaluate** continuously based on Coverage, Marginal Value, and Resilience

**Long-term Vision:** DEM becomes a strategic gateway for all high-quality Egyptian exports across all sectors, starting with Agrifood as the strategic priority, then expanding to other sectors as coverage matures.

**Important:** Provider count is not a goal; Knowledge Coverage is the primary driver. The operational ceiling of 7 is a current governance control, not a target and not a permanent portfolio end state. Further expansion requires Project Owner approval with documented Knowledge Coverage justification per Section 26.5.2.

---

## 15. Source / Candidate / Approved Provider / Implemented Provider Definitions

| Term | Definition |
|------|------------|
| **Source** | External data provider identified during portfolio evaluation |
| **Complementary Knowledge Source/Tool** | Source that provides useful knowledge but does not meet Provider Admission Criteria (e.g., web-only access). Re-evaluated only if machine-readable access is confirmed. |
| **Blocked / Pending Evidence** | Source that has potential value but has not passed the Pre-Candidate Evidence Gate (Section 12.1). One or more viability checks are unverified or failed. Re-evaluation requires new evidence. |
| **Provider Candidate** | Source that has passed the Pre-Candidate Evidence Gate (Section 12.1) and is under evaluation for potential implementation. Must satisfy all Provider Admission Criteria. |
| **Approved Provider** | Source that has received Project Owner approval at G1 and is cleared for implementation. |
| **Implemented Provider** | Source that has completed all 8 Tasks, passed all 5 Gates, and has a baseline tag. |

**Current State:**
- 7 Implemented Providers (Moaah, TradeData, ZATCA, GCC-Stat, FAOSTAT, UN Comtrade, World Bank LPI)
- FAOSTAT FPI extension implemented (no new provider)
- 0 Provider Candidates
- 4 Blocked / Pending Evidence (WTO Timeseries API, UNCTADstat, IMF IMTS)
- 2 Blocked / Pending Evidence — P0 (WTO ePing, WTO TFA Database)
- 20+ Complementary Knowledge Sources/Tools (web-only, bulk-only, or limited value)
- 0 Approved Providers pending implementation

**Important:** Candidate ≠ Approved Provider ≠ Implemented Provider. No candidate is approved for implementation without completing the full gate sequence (G0→G1→G2→G3→G4→G5).

---

## 16. Decision Framework for Project Owner

### 16.1 Decision Options

**A) Maintain Current State — World Bank LPI (Current)**  
- World Bank LPI is the 7th implemented provider (total 7) — FAOSTAT + UN Comtrade already implemented
- Fills empty Logistics / Market Execution family (0/10 → 5/10)
- Provider ceiling expanded to 7 by Project Owner approval (Section 26)
- Current step: Maintain Current State (7/7 providers; current operational ceiling = 7; expansion possible with justification)
- Sequence: Maintain current state, then monitor blocked phases

**B) Add P0 Providers (ePing / WTO TFA)**  
- Add WTO ePing, WTO TFA Database (2 providers; total 8) — FAOSTAT + UN Comtrade already implemented — **both currently Blocked / Pending Evidence**
- Deprioritize all web-only sources as Complementary
- Sequence: P0 first (SPS/TBT + Market Access trade facilitation)
- Stop when P0 gaps filled
- **Note:** This exceeds the current operational ceiling of 7. Project Owner must approve further ceiling expansion with documented Knowledge Coverage justification.

**C) Close WP-38 Without Additional Providers**  
- Formally close WP-38
- Keep current 7 providers as the current baseline (revisitable if Knowledge Coverage justification emerges)
- Revisit external intelligence in future phase

**D) Maintain Current State**  
- No new providers
- Continue with 7 implemented providers
- Evaluate orchestration need before any expansion

**E) Other**  
- Specify alternative direction with documented justification

### 16.2 Decision Criteria

Project Owner should consider:
1. Business priority on Agrifood Intelligence
2. Risk tolerance for SPS/TBT non-compliance
3. Maintenance bandwidth for additional providers
4. Timeline to desired coverage level
5. Budget for API access/premium sources
6. Willingness to expand the operational provider ceiling beyond 7 (currently 7, expanded from 6 for World Bank LPI)

---

## 17. Planning Decision

**Current State:** World Bank LPI is CLOSED as Implemented Provider (G5 PASS). Portfolio is in Maintain Current State (7/7 providers; current operational ceiling = 7). Knowledge Model is VALIDATED / BASELINED. No additional Owner approval is required for routine governance activities. Ceiling expansion remains possible with documented Knowledge Coverage justification per Section 26.5.2.

**The next execution step is:**
1. Maintain current 7-provider portfolio; no new provider implementation
2. Conduct Portfolio Gap Analysis per validated Seven-Family Knowledge Model
3. Monitor WTO ePing and WTO TFA Database for verifiable public REST API access
4. Annual portfolio re-evaluation

**No provider implementation, no WP creation, no code changes, no commits/tags/baselines until a P0 candidate becomes actionable and ceiling expansion is approved per Section 26.5.**

---

## 18. Evidence and Inference Classification

| Section | Type | Description |
|---------|------|-------------|
| Current Portfolio Status | **Evidence** | Verified from git history, baseline tags, test results |
| Seven-Family Model | **Inference** | Derived from business requirements and domain analysis |
| Coverage Score Methodology | **Evidence** | Documented scoring scale and methodology |
| Coverage Scores | **Inference/Estimate** | Expert assessment based on provider capabilities; methodology documented in Section 4 |
| Resilience Matrix (Section 4.3) | **Inference** | Based on provider authentication/access dependencies and operational analysis |
| Agrifood Priority | **Recommendation** | Based on stated business priority |
| Candidate Evaluations | **Evidence** | Based on documented API availability, officiality, coverage |
| Complementary Sources Classification | **Evidence** | Based on documented API availability; web-only/bulk-only sources classified as Complementary |
| ITC Strategic Value Assessment | **Inference** | Strategic value assessed separately from provider feasibility |
| WTO API Assessment | **Evidence** | Based on official WTO documentation and live verification attempts |
| UNCTAD API Assessment | **Evidence** | Based on official UNCTAD documentation; no public REST API confirmed |
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

> **Historical / Superseded Record**
> 
> This section documents the historical decision that selected FAOSTAT as the first execution gap. It is preserved for audit trail purposes only. The current portfolio state is documented in Section 27 (Phase 0 Baseline). World Bank LPI is now the current Phase 1 candidate.

| Field | Value |
|-------|-------|
| Decision | **FAOSTAT selected as First Execution Gap** |
| Date | 2026-08-14 |
| Decided By | Project Owner |
| Status | **Historical — Superseded by Current Phase Roadmap** |
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

> **Historical / Superseded Record**
> 
> This section documents the historical FAOSTAT G1 licensing review. It is preserved for audit trail purposes only. FAOSTAT has since passed G1, completed Task 2 and Task 3, and is now an Implemented Provider. Current implementation status is documented in Section 27 (Phase 0 Baseline).

**Purpose:** Document licensing and redistribution evidence for FAOSTAT to assess G1 Gate readiness.

**Status:** Historical — INSUFFICIENT EVIDENCE / G1 BLOCKED (licensing blockers resolved by Project Owner Approval; FAOSTAT subsequently passed G1 and is now Implemented)

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

**Status: Historical — INSUFFICIENT EVIDENCE**

**Rationale (Historical):**
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

**Status: Historical — INSUFFICIENT EVIDENCE**

**Rationale (Historical):**
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

**Historical — INSUFFICIENT EVIDENCE / BLOCKED**

FAOSTAT has **two unresolved G1 blockers** (historical):
1. Non-commercial restriction on dataset use conflicts with DEM's commercial platform model
2. ShareAlike requirement in API license may conflict with DEM's proprietary distribution

**FAOSTAT is NOT approved for implementation (historical). FAOSTAT is NOT an Approved Provider (historical). This decision does not constitute G1 PASS (historical).**

### 21.6 Resolution Paths

| Path | Action | Owner | Outcome |
|------|--------|-------|---------|
| **A** | Project Owner review and explicit approval of FAOSTAT commercial use model | Project Owner | G1 Blocker resolved; FAOSTAT becomes eligible for G1 Approval |
| **B** | Official written clarification from FAO permitting commercial use and redistribution | FAO / Project Owner | G1 Blocker resolved if permission is granted |
| **C** | Legal review of whether DEM's use case qualifies as "evidence-based decision-making" under FAO terms | Legal / Project Owner | G1 Blocker resolved if use case is exempt |

### 21.7 Next Step

**Historical — Do NOT proceed to Task 2 or implementation (superseded by G1 Approval in Section 21.9).**

1. Obtain and document FAOSTAT licensing/commercial use terms resolution.
2. Obtain and document FAOSTAT redistribution terms resolution.
3. Update this section with findings.
4. Re-evaluate G1 criteria after blocker is resolved.
5. If both criteria become PASS, FAOSTAT becomes eligible for **Project Owner G1 Approval**.
6. If either remains FAIL, FAOSTAT remains **G1 Blocked** (historical — FAOSTAT subsequently passed G1 and is now Implemented) and the next candidate (WTO ePing or WTO TFA Database) must be evaluated per Section 20.2.

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
5. If G1 Verdict = FAIL, FAOSTAT remains **G1 Blocked** (historical — FAOSTAT subsequently passed G1 and is now Implemented) and the next candidate (WTO ePing or WTO TFA Database) must be evaluated per Section 20.2.

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
2. Implement 
aostat_client.py — isolated HTTP client for FAOSTAT API
3. Implement 
aostat_provider.py — KnowledgeProvider implementation
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
| VI-1 to VI-9 closed | ✅ Complete | Live validation evidence in `backend/faostat_vi_validation_report.json`; all items PASS per Governance Review APPROVE — Close VI-1 to VI-9 (2026-08-19) |
| G3 Blocking Findings closed | ✅ Complete | _build_source_url() corrected; 3 new tests added |
| Test coverage | ✅ Complete | 17/17 FAOSTAT unit tests + 6/6 integration tests |
| No new regressions | ✅ Verified | Existing adapter tests unaffected |
| Specification alignment | ✅ Verified | Base URL, path, default domain corrected |
| Provider-Agnostic architecture | ✅ Verified | No DEM core changes |
| KnowledgeProvider contract | ✅ Verified | query() and get_sources() implemented |
| JWT Authentication Discrepancy | ✅ Resolved | Sections 7.1 and 7.2 updated to reflect JWT authentication; `FAOSTAT_API_KEY` removed; `FAOSTAT_USER`/`FAOSTAT_PASSWORD` documented; `POST /auth/login` → JWT Bearer token flow confirmed |
| Evidence package complete | ✅ Verified | All evidence traceable and consistent |

##### 21.11.4.2 Out-of-Scope Items

| Item | Status | Rationale |
|------|--------|-----------|
| JWT Authentication | Resolved | Sections 7.1 and 7.2 updated to reflect JWT authentication; discrepancy closed; no further action required within Task 3 scope |
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

> **Historical / Superseded Record**
> 
> This section documents the historical decision after FAOSTAT Task 3 closure. It is preserved for audit trail purposes only. The current portfolio state and next priority are documented in Section 27 (Phase 0 Baseline) and Section 27.3 (Phase 1 — World Bank LPI). WTO ePing and WTO TFA remain Complementary/Blocked.

### 23.1 Decision

**CLOSED WITH CLASSIFICATION — WTO ePing G1 BLOCKED**

### 23.2 Context

FAOSTAT has been formally closed. WTO ePing G1 Source Evaluation has been completed. UN Comtrade has been formally closed. **At that time, the portfolio had 6 implemented providers (Moaah, TradeData, ZATCA, GCC-Stat, FAOSTAT, UN Comtrade).** The current portfolio has 7 implemented providers (add World Bank LPI). The SPS/TBT gap remains:

> **Historical Record Note:** This section documents the historical state at the time of the G1 decision. "Trade Facilitation" appears here as a separate gap classification per the historical context. Under the current Seven-Family Knowledge Model (Section 3), trade facilitation capability is classified under Market Access. This record is preserved for audit trail purposes only.

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

WTO ePing cannot be added as Implemented Provider. Provider count remains at 6 (Moaah, TradeData, ZATCA, GCC-Stat, FAOSTAT, UN Comtrade).

WTO TFA Database remains a future candidate. Any addition would bring total to 7 or 8, requiring explicit Project Owner approval with documented justification per Provider Admission Criteria Section 12. The current operational ceiling is 7 providers, approved for World Bank LPI only. Further expansion requires separate approval.

**Note:** Provider count is not a goal. Expansion is driven by Knowledge Coverage gaps, not by reaching a target number of providers.

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

> **Historical / Superseded Record**
> 
> This section documents the historical G1 decision for WTO ePing. It is preserved for audit trail purposes only. WTO ePing is currently classified as Complementary Knowledge Source (Section 6.3) and remains G1 BLOCKED. Current classification is documented in Section 27.5 (Phase 5 — Regulatory / SPS / TBT).

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
| Agrifood Intelligence | 8/10 (with FAOSTAT + ePing + TFA) | 8/10 (FAOSTAT implemented) | **P0 — Implemented** |

**Overall Portfolio Coverage:** ~5.1/10 → ~3.9/10 (reverts to current baseline without P0 additions)

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

> **Historical / Superseded Record**
> 
> This section documents the historical G1 decision for WTO TFA Database. It is preserved for audit trail purposes only. WTO TFA Database is currently classified as Complementary Knowledge Source (Section 6.3) and remains G1 BLOCKED. Current classification is documented in Section 27.5 (Phase 5 — Regulatory / SPS / TBT).

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
| 9. Provider Ceiling Compliance | ⚠️ **CONSTRAINT** | **At the time of this decision,** the portfolio had 6 implemented providers. Adding this provider would have reached the operational ceiling of 7. The current portfolio has 7 implemented providers (World Bank LPI added). Requires explicit Project Owner approval with documented Knowledge Coverage justification. Further expansion beyond 7 requires separate approval. |

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

These are separate knowledge capabilities. For portfolio planning purposes:
- **Regulatory / SPS / TBT** = SPS/TBT notifications and requirements only
- **Trade Facilitation** = Customs procedures and trade facilitation implementation

This plan maintains the 7-Family model as defined in Section 3. Trade Facilitation is recognized as a distinct capability that may be addressed within the existing family structure or through future family refinement.

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

---

## 26. Provider Ceiling Expansion Approval — 6 → 7

### 26.1 Decision

| Field | Value |
|-------|-------|
| **Decision** | **Approve Provider Ceiling Expansion from 6 to 7** |
| **Date** | 2026-08-17 |
| **Approved By** | Project Owner |
| **Status** | **Approved — Ceiling Expanded to 7** |
| **Scope** | Authorizes addition of 1 additional provider beyond the current 6, bringing total to 7 implemented providers |
| **Effective** | Immediately upon owner approval |
| **Basis | World Bank LPI is the first candidate for ceiling expansion. It fills the empty Logistics / Market Execution family (0/10 → 5/10) with a free, open REST API and no authentication requirements. The expansion is justified by Knowledge Coverage gain, not provider count increase. |
| **Constraint | This approval authorizes ceiling expansion ONLY. It does NOT authorize WP creation, G1 initiation, implementation, code changes, or provider execution for World Bank LPI or any other source. |

### 26.2 Rationale

1. **Knowledge Coverage Justification:** Logistics / Market Execution is the only completely empty knowledge family (0/10). World Bank LPI is the only candidate with verified free, open REST API access.
2. **Resilience Justification:** Adding World Bank LPI introduces a new knowledge family with an independent source, increasing portfolio resilience.
3. **Marginal Value Justification:** World Bank LPI provides unique logistics performance data not available from any existing provider.
4. **Operational Feasibility:** World Bank LPI has no authentication requirements, free API, and 160+ country coverage.
5. **Strategic Alignment:** Logistics intelligence is critical for agrifood exports (cold chain, perishable goods).
6. **No Redundancy:** World Bank LPI does not duplicate any existing provider functionality.

### 26.3 Ceiling Expansion Conditions

| Condition | Status |
|-----------|--------|
| Knowledge Coverage gain documented | ✅ Logistics 0/10 → 5/10 |
| No redundancy with existing providers | ✅ No overlap |
| API feasibility verified | ✅ Free REST API, no auth |
| Licensing verified | ✅ Open / World Bank terms |
| Project Owner approval | ✅ Recorded in this section |
| Provider count after addition | 7 (within expanded ceiling) |

### 26.4 Constraints

- This approval does NOT authorize implementation of World Bank LPI.
- This approval does NOT authorize WP creation for World Bank LPI.
- This approval does NOT authorize G1 initiation for World Bank LPI.
- World Bank LPI must still pass full Provider Admission Criteria (Section 12) and Gate Sequence (G0→G1→G2→G3→G4→G5) before implementation.
- No further ceiling expansion is authorized without separate Project Owner approval.

### 26.5 Post-G5 Closure Governance Decision — Maintain Current State

**Decision:** Maintain current 7-provider portfolio. No ceiling expansion is approved at this time. No new provider implementation is approved at this time.

**Date:** 2026-08-18  
**Authority:** Governance Review  
**Status:** Approved — Current State Maintained

| Field | Value |
|-------|-------|
| Current Provider Count | 7 / 7 |
| Operational Ceiling | 7 (current governance control; not a permanent architectural limit) |
| Ceiling Status | Current — expansion possible with documented Knowledge Coverage justification per Section 26.5.2 |
| Next Action | Monitor WTO ePing and WTO TFA Database for verifiable public REST API access; conduct Portfolio Gap Analysis |
| Constraint | No provider implementation, no WP creation, no code changes, no Contract/Schema changes, no new Owner decisions until: (1) a P0 candidate becomes actionable AND (2) ceiling expansion is approved per Section 26.5.2 if required |

#### 26.5.1 Rationale

1. **P0 Gaps are currently blocked:** WTO ePing and WTO TFA Database are both Blocked / Pending Evidence due to lack of verifiable public REST API. No P0 candidate is currently actionable.
2. **P1 candidate does not justify expansion:** WTO Timeseries API is Blocked / Pending Evidence (Pre-Candidate Evidence Gate not passed) and does not fill a P0 gap; it would require ceiling expansion without documented Knowledge Coverage justification for critical gaps.
3. **Provider count is not a goal:** Per Section 1, providers are added only when a documented Knowledge Coverage gap exists, marginal knowledge value is proven, and operational feasibility is confirmed.
4. **Ceiling reached as current state:** The current operational ceiling of 7 was approved by Project Owner for World Bank LPI based on documented Knowledge Coverage justification. This is the current operational state, not a permanent portfolio end state. Further expansion requires separate approval per the governance process in Section 26.5.2.

#### 26.5.2 Governance Process for Ceiling Expansion

The operational provider ceiling is a **current governance control**, not a permanent architectural limit or portfolio end-state criterion. Expansion beyond the current ceiling of 7 is possible through the following governance process:

**Governance Trigger:** A material documented Knowledge Gap exists that cannot be addressed within the current ceiling without sacrificing Knowledge Sufficiency.

**Required Evidence for Expansion Request:**
1. **Knowledge Gap Documentation:** Specific gap identified in the Seven-Family Knowledge Coverage Matrix with evidence of decision impact
2. **Marginal Knowledge Value > 0:** The candidate adds unique knowledge value not available from existing providers
3. **Feasibility Confirmed:** Pre-Candidate Evidence Gate passed; implementation path viable
4. **No Adequate Alternative:** The gap cannot be filled by repurposing existing provider capabilities or accepting Complementary coverage
5. **Provider Count Impact:** Clear accounting of the new total and justification for why the increase is necessary

**Expansion Pathway:**
```
Documented Knowledge Gap → Candidate Source Research → Pre-Candidate Evidence Gate → Candidate → Governance Review → Ceiling Expansion Approval (if justified) → G0 → G1 → ... → Implemented
```

**Key Principle:** Ceiling expansion is a **governance decision triggered by Knowledge Coverage need**, not a **prerequisite that blocks Knowledge Coverage need**. The default state is "expansion possible with justification"; the current state is "no expansion approved at this time."
3. **API Verification Evidence:** Live API verification with confirmed endpoint structure, response format, and authentication requirements
4. **Explicit Owner Approval:** Separate Project Owner approval with documented justification before any implementation tasks begin
5. **Gate Sequence Completion:** Full G0→G1→G2→G3→G4→G5 sequence for the new provider

#### 26.5.3 Monitoring Requirements

| Source | Status | Monitoring Action |
|--------|--------|-------------------|
| WTO ePing | Blocked / Pending Evidence — Pre-Candidate Evidence Gate not passed | Monitor for API availability; re-evaluate if REST access confirmed and Pre-Candidate Evidence Gate passed |
| WTO TFA Database | Blocked / Pending Evidence — Pre-Candidate Evidence Gate not passed | Monitor for API availability; re-evaluate if REST access confirmed and Pre-Candidate Evidence Gate passed |

**Trigger for Re-Evaluation:** Either WTO ePing or WTO TFA Database publishes a verifiable public REST API.

---

## 27. 7-Family Implementation Master Roadmap

### 27.1 Roadmap Governance Rules

| Rule | Description |
|------|-------------|
| **Knowledge Coverage First** | Expansion is driven by coverage gap, not provider count |
| **Provider Count is Not a Goal** | Provider count is a constraint, not a target |
| **No Automated Provider Without Evidence** | API feasibility must be proven before G1 |
| **Licensing Before Implementation** | Licensing must be verified and approved before implementation |
| **No WP Without Gate Passage** | No WP is created until the phase entry gate is passed |
| **No Implementation From This Plan** | This plan defines the roadmap; implementation requires separate WP and gate passage |
| **Complementary ≠ Provider** | Complementary sources are not automatically converted to providers |
| **Re-Evaluation Trigger** | Each phase ends with re-evaluation trigger for next phase |

### 27.2 Phase 0 — Portfolio Baseline & Governance

**Purpose:** Formalize the current portfolio baseline and governance framework.

| Attribute | Value |
|-----------|-------|
| **Phase Status** | Complete — Baseline Established |
| **Scope** | Document current state of all 7 Knowledge Families |
| **Output** | This plan serves as the baseline reference |
| **Gate** | G0 — Portfolio Evaluation Approval (Section 19) |

**7-Family Baseline Snapshot:**

| Knowledge Family | Current Score | Target Score | Gap | Primary Source | Secondary/Fallback | Strategic Sources | Provider / Complementary | API / Machine Access | Licensing/Usage Constraints | Operational Independence | Resilience | Dependencies | Implementation Priority | Entry Gate | Exit/Acceptance Gate | Trigger for Re-Evaluation |
|------------------|---------------|--------------|-----|----------------|-------------------|-------------------|--------------------------|----------------------|----------------------------|--------------------------|-----------|--------------|------------------------|------------|----------------------|---------------------------|
| Trade Intelligence | 7/10 | 9/10 | P1 | UN Comtrade + TradeData + GCC-Stat + FAOSTAT | TradeData (commercial fallback) | FAOSTAT | Provider (4 implemented) | UN Comtrade: Free API; TradeData: Commercial API; GCC-Stat: SDMX/REST; FAOSTAT: JWT | FAO: CC BY-NC-SA 3.0 IGO (commercial use approved by PO) | High — 4 independent sources | ✅ Strong | None | P1 | G0 Complete | G1 PASS for each new provider | New source with verified API |
| Market Opportunity | 4/10 | 6/10 | P2 | TradeData (indirect) | GCC-Stat (economic indicators) | ITC Export Potential Map | Provider: TradeData; Complementary: ITC Export Potential Map | TradeData: Commercial API; ITC: Web only | TradeData: Commercial license; ITC: Free for developing countries | Low — single provider | ❌ Weak | ITC API availability | P2 | G0 Complete | G1 PASS for new provider | ITC API availability |
| Market Access | 5/10 | 8/10 | P1 | Moaah (primary), ZATCA (KSA only) | WTO Timeseries API (Blocked / Pending Evidence) / TTD platform | ITC Market Access Map | Provider: Moaah, ZATCA; Blocked / Pending Evidence: WTO Timeseries API; Complementary: WTO TTD, ITC Market Access Map | Moaah/ZATCA: Commercial API; WTO Timeseries: Free registration + key; WTO TTD: Web + raw downloads; ITC: Web + bulk | Moaah/ZATCA: Commercial; WTO: CMA Annex 4 restrictions; ITC: Free for developing countries | Medium — geographic gaps | ⚠️ Moderate | WTO Timeseries API Pre-Candidate Evidence Gate completion | P1 | G0 Complete | Pre-Candidate Evidence Gate PASS for WTO Timeseries API | WTO Pre-Candidate Evidence Gate completion |
| Regulatory / SPS / TBT | 0/10 | 9/10 | **P0** | None | None | WTO ePing (CLOSED), Codex, IPPC, WTO I-TIP (CLOSED for SPS/TBT) | Blocked / Pending Evidence: WTO ePing, WTO TFA Database; Complementary: Codex, IPPC, WTO I-TIP. No automated provider. No candidate currently qualifies for G1. | None (all web-only/XLSX). WTO ePing and WTO TFA Database have no verifiable public REST API; classified as Blocked / Pending Evidence. | WTO ePing: Unknown; Codex: Free; IPPC: Free | None | ❌ None | WTO ePing/TFA public REST API | **P0 — Complementary-Only Accepted** | G0 Complete | N/A — No provider entry without verifiable public REST API with current SPS/TBT data and server-side filtering | New machine-readable source with current SPS/TBT data + filtering + Provider Admission Criteria met + Project Owner approval |
| Rules of Origin | 3/10 | 3/10 | P3 | GCC-Stat | None | ITC Rules of Origin Facilitator | Provider: GCC-Stat; Complementary: ITC Rules of Origin Facilitator | GCC-Stat: SDMX/REST; ITC: Web only | GCC-Stat: Free; ITC: Free for developing countries | Medium — GCC scope only | ❌ Weak | None | P3 | G0 Complete | G1 PASS if new candidate emerges | New API source |
| Agrifood Intelligence | 8/10 | 8/10 | P0 — Implemented | FAOSTAT + FPI extension | None | FAO Food Price Index | Provider: FAOSTAT + FPI extension | FAOSTAT: JWT required | CC BY-NC-SA 3.0 IGO (commercial use approved by PO) | Medium — FAO is stable | ✅ Medium | JWT authentication maintained | P0 — Maintain | G0 Complete | G5 Closure (complete) | Licensing change |
| Logistics / Market Execution | 5/10 | 5/10 | **P1 — Implemented** | None | None | UNCTAD LSCI/PLSCI, World Bank LPI | Provider: World Bank LPI; Complementary: UNCTAD LSCI/PLSCI | World Bank LPI: Free REST API; UNCTAD: CSV/bulk download | World Bank: Open; UNCTAD: CC BY 3.0 IGO | Low — no current source | ✅ Strong | None | P1 — Complete | G0 Complete | G5 Closure (complete) | API availability |

### 27.3 Phase 1 — Logistics / Market Execution

**Purpose:** Add World Bank LPI as 7th implemented provider, filling the empty Logistics family.

| Attribute | Value |
|-----------|-------|
| **Phase Status** | Activated — G1/G2/G3/G4 PASS — G5 Closure ✅ |
| **Provider Ceiling** | 6 → 7 (approved by Project Owner, Section 26) |
| **Implemented Provider** | World Bank LPI |
| **Knowledge Family** | Logistics / Market Execution |
| **Current Coverage** | 0/10 |
| **Target Coverage** | 5/10 |
| **Gap** | Complete gap — no logistics intelligence |
| **Primary Source** | World Bank LPI |
| **Secondary/Fallback** | UNCTAD LSCI/PLSCI (Complementary / Bulk-Only) |
| **Strategic Sources** | UNCTAD LSCI/PLSCI for maritime-specific depth |
| **Provider vs Complementary** | World Bank LPI = Implemented Provider; UNCTAD LSCI/PLSCI = Complementary |
| **API / Machine Access** | World Bank LPI: Free REST API, no authentication, 160+ countries |
| **Licensing/Usage Constraints** | World Bank: Open access; verify specific terms before G1 |
| **Operational Independence** | High — independent source, no overlap with existing providers |
| **Resilience** | Adds new family coverage; fallback via UNCTAD bulk downloads |
| **Dependencies** | Provider Ceiling Expansion Approval (Section 26) |
| **Implementation Priority** | P1 — First Execution Candidate |
| **Entry Gate** | G0 Complete + Ceiling Expansion Approval + Phase Activation + G1 PASS |
| **Exit/Acceptance Gate** | G1 PASS → G2 PASS → G3 PASS → G4 PASS → G5 Closure ✅ |
| **Trigger for Re-Evaluation** | API changes, licensing changes, or if World Bank LPI becomes inaccessible |

**Phase 1 Constraints:**
- Phase 1 is complete. World Bank LPI has passed all gates (G1–G5) and is CLOSED as Implemented Provider.
- Current portfolio state: Maintain Current State (7/7 providers; current operational ceiling = 7; expansion possible with documented justification).
- No further execution steps for World Bank LPI within this phase.
- No implementation code changes from this plan.

**Data Version Note:** World Bank LPI data accessed via the World Bank Indicators API (`LP.LPI.*` indicators) corresponds to the traditional survey-based LPI methodology (2007–2022). The newer LPI 2.0 (2023–2024) uses shipment-level tracking data and is published separately via World Bank Data360; it is not the dataset evaluated in this G1 record.

### 27.3.1 G5 Closure Record — World Bank LPI

**Purpose:** Record formal closure of World Bank LPI Provider Implementation.

**Status:** World Bank LPI CLOSED — Implemented Provider

| Field | Value |
|-------|-------|
| Decision | **World Bank LPI G5 CLOSED** |
| Date | 2026-08-18 |
| Closed By | Governance Review |
| Status | **CLOSED — Implemented Provider** |
| Scope | World Bank LPI Provider Implementation (Phase 1) |
| Basis | G1 = PASS; G2 = PASS; G3 = PASS; G4 = PASS; all acceptance criteria met; live API verified |
| Provider Count | 7 / 7 (World Bank LPI is 7th implemented provider) |
| Operational Ceiling | 7 (approved by Project Owner, Section 26) |

#### 27.3.1.1 Gate Sequence Status

| Gate | Status | Evidence |
|------|--------|----------|
| G0 — Portfolio Evaluation Approval | ✅ Approved | Section 19 Owner Approval Record |
| G1 — World Bank LPI Source Selection | ✅ PASS | Section 27.3 — G1 PASS recorded; all Provider Admission Criteria satisfied |
| G2 — Adapter Specification Review | ✅ PASS | `.kilo/plans/1786559160142-worldbank-lpi-adapter-spec.md` |
| G3 — Implementation Review | ✅ PASS | Implementation complete; tests passing |
| G4 — Verification | ✅ PASS | Live API verification passed; Egypt 2022 LPI = 3.1 |
| G5 — Closure | ✅ PASS | This closure record |

#### 27.3.1.2 Closure Criteria Verification

| Criterion | Status | Evidence |
|-----------|--------|----------|
| G1 PASS | ✅ Complete | All 9 Provider Admission Criteria satisfied |
| G2 PASS | ✅ Complete | Adapter Specification approved |
| G3 PASS | ✅ Complete | Implementation complete; 19/19 tests passing |
| G4 PASS | ✅ Complete | Live API end-to-end verified; Egypt 2022 = 3.1; Egypt 2022 Customs = 2.8 |
| No open Blockers | ✅ Verified | No blocking findings |
| No open Corrections | ✅ Verified | All G4 findings resolved |
| Provider-Agnostic architecture | ✅ Verified | No DEM core changes |
| KnowledgeProvider contract | ✅ Verified | query() and get_sources() implemented |
| Live API verification | ✅ Verified | World Bank Indicators API v2 accessible; envelope handled correctly |
| Evidence package complete | ✅ Verified | All evidence traceable and consistent |

#### 27.3.1.3 Final Provider Status

| Attribute | Value |
|-----------|-------|
| Provider Name | World Bank Logistics Performance Index |
| Provider ID | `worldbank-lpi` |
| Source Type | `external_logistics_intelligence` |
| Knowledge Family | Logistics / Market Execution |
| Coverage Contribution | 0/10 → 5/10 |
| API Base URL | `https://api.worldbank.org/v2` |
| Authentication | None required (open access) |
| License | CC BY-4.0 (attribution required) |
| Implementation Files | `worldbank_lpi_client.py`, `worldbank_lpi_provider.py` |
| Config Settings | 7 settings in `config.py` |
| Registry Registration | Conditional in `main.py` lifespan |
| Test Coverage | 14 unit tests + 5 integration tests |
| Live Verification | Egypt 2022 Overall LPI = 3.1; Egypt 2022 Customs = 2.8 |

#### 27.3.1.4 Out-of-Scope Items

| Item | Status | Rationale |
|------|--------|-----------|
| LPI 2.0 (2023–2024) | Unverified / Out of Scope | Published via World Bank Data360 separately; not available via current Indicators API path |
| Multi-year pagination | Unverified | Single-year queries verified; multi-page pagination not tested |
| Rate-limit numeric limits | Unverified | World Bank Terms state "reasonable request volume"; no numeric limit documented |
| G6 Initiation | Not Authorized | Requires explicit Project Owner decision |
| New Work Packages | Not Authorized | Requires explicit Project Owner decision |
| Additional Providers | Not Authorized | Provider ceiling = 7; further expansion requires separate approval |

### 27.4 Phase 2 — Market Access

**Purpose:** Add WTO Timeseries API as provider candidate for Market Access and Trade Intelligence.

| Attribute | Value |
|-----------|-------|
| **Phase Status** | Blocked / Pending Evidence — Pre-Candidate Evidence Gate not passed |
| **Candidate** | WTO Timeseries API (Blocked / Pending Evidence) |
| **Knowledge Family** | Market Access, Trade Intelligence |
| **Current Coverage** | 5/10 |
| **Target Coverage** | 8/10 |
| **Gap** | No dedicated global tariff database; no official WTO trade statistics |
| **Primary Source** | WTO Timeseries API |
| **Secondary/Fallback** | WTO Tariff & Trade Data (TTD) platform (Complementary); ITC Market Access Map (Complementary) |
| **Strategic Sources** | ITC Market Access Map for ag-specific tariff/NTM data |
| **Provider vs Complementary** | WTO Timeseries API = Blocked / Pending Evidence; WTO TTD = Complementary; ITC Market Access Map = Complementary |
| **API / Machine Access** | WTO Timeseries API: Free registration + subscription key required |
| **Licensing/Usage Constraints** | WTO: CMA Annex 4 restrictions apply; verify terms before G1 |
| **Operational Independence** | Medium — requires subscription key; different from existing providers |
| **Resilience** | Adds WTO as independent source; fallback via ITC bulk downloads |
| **Dependencies** | WTO API key registration; licensing verification; ceiling compliance; Pre-Candidate Evidence Gate completion |
| **Implementation Priority** | P1 |
| **Entry Gate** | Pre-Candidate Evidence Gate PASS + G0 Complete + API key obtained + licensing verified |
| **Exit/Acceptance Gate** | G1 PASS → G2 PASS → G3 PASS → G4 PASS → G5 Closure |
| **Trigger for Re-Evaluation** | API key requirements change, CMA Annex 4 restrictions change, or WTO API deprecation |
| **Pre-Candidate Evidence Status** | ❌ BLOCKED — Commercial licensing unclear; Egypt data insufficient; HTTP-only; requires evidence completion before Candidate status |

**Phase 2 Constraints:**
- WTO Timeseries API requires free registration + subscription key.
- WTO Timeseries API has **not passed the Pre-Candidate Evidence Gate** (Section 12.1). It is classified as Blocked / Pending Evidence pending resolution of: commercial licensing, Egypt data sufficiency, and transport security.
- WTO Tariff & Trade Data (TTD) is NOT a provider candidate — it is web-only with raw downloads.
- No WP creation until Phase 1 is complete and this phase is activated.
- G1 initiation for Phase 2 is delegated to Governance after phase activation; no new Owner approval required.

### 27.5 Phase 3 — Market Opportunity

**Purpose:** Maintain ITC tools as Strategic Complementary Portfolio. No automated provider addition unless API access becomes available.

| Attribute | Value |
|-----------|-------|
| **Phase Status** | Strategic Complementary — No Provider Addition |
| **Sources** | ITC Export Potential Map, ITC Market Access Map, ITC Trade Map, ITC Rules of Origin Facilitator |
| **Knowledge Family** | Market Opportunity, Market Access, Trade Intelligence, Rules of Origin |
| **Current Coverage** | 4/10 |
| **Target Coverage** | 6/10 (with FAOSTAT FPI extension) |
| **Gap** | No dedicated opportunity intelligence source; ITC tools are web-only |
| **Primary Source** | TradeData (indirect) + FAOSTAT FPI extension |
| **Secondary/Fallback** | GCC-Stat economic indicators |
| **Strategic Sources** | ITC Export Potential Map (Very High strategic value), ITC Market Access Map (High strategic value) |
| **Provider vs Complementary** | All ITC tools = Strategic Complementary Sources; no provider feasibility currently |
| **API / Machine Access** | None — all ITC tools are web-only; bulk download available for Market Access Map |
| **Licensing/Usage Constraints** | ITC: Free for developing countries; registration required |
| **Operational Independence** | Low — no automated access; manual/bulk only |
| **Resilience** | No automated fallback; manual bulk download possible |
| **Dependencies** | ITC documented public REST API (not currently available) |
| **Implementation Priority** | P3 — Strategic value only |
| **Entry Gate** | N/A — No provider entry without documented public REST API |
| **Exit/Acceptance Gate** | N/A — Complementary status maintained |
| **Trigger for Re-Evaluation** | ITC publishes documented public REST API; or Project Owner approves bulk-download automation infrastructure |

**Phase 3 Constraints:**
- ITC tools are NOT provider candidates.
- ITC strategic value is Very High but provider feasibility is zero.
- No WP creation for ITC automation.
- Re-evaluation only if ITC API access becomes available.

### 27.6 Phase 4 — Logistics Resilience

**Purpose:** Evaluate UNCTAD LSCI/PLSCI as Complementary / Bulk-Only maritime logistics sources to deepen Logistics family coverage.

| Attribute | Value |
|-----------|-------|
| **Phase Status** | Complementary / Bulk-Only — No Provider Addition |
| **Sources** | UNCTAD LSCI, UNCTAD PLSCI |
| **Knowledge Family** | Logistics / Market Execution |
| **Current Coverage** | 5/10 (with World Bank LPI) |
| **Target Coverage** | 7/10 (with World Bank LPI + UNCTAD bulk) |
| **Gap** | Maritime-specific logistics data missing |
| **Primary Source** | World Bank LPI (Provider) |
| **Secondary/Fallback** | UNCTAD LSCI/PLSCI (Complementary / Bulk-Only) |
| **Strategic Sources** | UNCTAD LSCI for maritime connectivity depth |
| **Provider vs Complementary** | World Bank LPI = Provider; UNCTAD LSCI/PLSCI = Complementary / Bulk-Only |
| **API / Machine Access** | UNCTAD: No documented public REST API; CSV export per table + bulk download facility only |
| **Licensing/Usage Constraints** | UNCTAD: CC BY 3.0 IGO |
| **Operational Independence** | Medium — bulk download requires custom infrastructure |
| **Resilience** | Adds maritime-specific fallback; not a replacement for World Bank LPI |
| **Dependencies** | Custom bulk-download + local parsing infrastructure (not adapter-pattern compatible) |
| **Implementation Priority** | P3 — After World Bank LPI implementation |
| **Entry Gate** | N/A — No provider entry without documented public REST API |
| **Exit/Acceptance Gate** | N/A — Complementary status maintained |
| **Trigger for Re-Evaluation** | UNCTAD publishes documented public REST API; or Project Owner approves bulk-download automation infrastructure |

**Phase 4 Constraints:**
- UNCTAD LSCI/PLSCI are NOT provider candidates.
- They require custom bulk-download + local parsing infrastructure, which is outside the established adapter pattern.
- No WP creation for UNCTAD automation.
- Re-evaluation only if UNCTAD API access becomes available or bulk-download infrastructure is approved.

### 27.7 Phase 5 — Regulatory / SPS / TBT

**Purpose:** Accept Complementary-Only Coverage for SPS/TBT as the current operational state. No automated provider addition until a new machine-readable source meeting Provider Admission Criteria emerges. WTO ePing and WTO I-TIP are CLOSED as candidates for this gap under current conditions. This acceptance is not permanent; it is the current state pending a feasible source.

| Attribute | Value |
|-----------|-------|
| **Phase Status** | Complementary-Only Accepted — Gap Unfilled (Current State; revisitable if feasible source emerges) |
| **Sources** | WTO ePing (Blocked / Pending Evidence), WTO TFA Database (Blocked / Pending Evidence), Codex (Complementary), IPPC (Complementary), WTO I-TIP (Complementary — CLOSED for SPS/TBT) |
| **Knowledge Family** | Regulatory / SPS / TBT |
| **Current Coverage** | 0/10 (Automated Provider Coverage) |
| **Target Coverage** | 9/10 |
| **Gap** | Complete gap — no automated SPS/TBT provider. Trade Facilitation capability is classified under Market Access; WTO TFA Database (Blocked / Pending Evidence) could contribute to Market Access if it becomes accessible. |
| **Primary Source** | None (automated) |
| **Secondary/Fallback** | Manual/Complementary: WTO ePing web portal + XLSX downloads; Codex (FAO/WHO); IPPC (FAO) |
| **Strategic Sources** | WTO ePing (Very High strategic value), Codex (Critical), IPPC (Critical) |
| **Provider vs Complementary** | WTO ePing = Blocked / Pending Evidence; WTO TFA Database = Blocked / Pending Evidence; Codex, IPPC, WTO I-TIP = Complementary; no automated provider; no candidate currently qualifies for G1 |
| **API / Machine Access** | None — all sources are web-only or require authentication. WTO ePing and WTO TFA Database have no verifiable public REST API; classified as Blocked / Pending Evidence. Codex, IPPC, WTO I-TIP are web-only (Complementary). |
| **Licensing/Usage Constraints** | WTO: CMA Annex 4 restrictions; Codex: Free; IPPC: Free |
| **Operational Independence** | None — no automated source |
| **Resilience** | None — no fallback |
| **Dependencies** | No automated source currently exists; gap remains dependent on future API availability or Project Owner decision to accept complementary-only coverage as the current state (revisitable if feasible source emerges) |
| **Implementation Priority** | **P0 — Complementary-Only Accepted** |
| **Entry Gate** | N/A — No provider entry without documented public REST API providing current SPS/TBT data and server-side filtering |
| **Exit/Acceptance Gate** | N/A — Complementary status is the current accepted state for this phase; may be revisited if a feasible machine-readable source emerges and Governance approves ceiling expansion or replacement |
| **Trigger for Re-Evaluation** | A new machine-readable source emerges that: (1) provides current SPS/TBT data, (2) offers server-side filtering by SPS/TBT type, country, date, and product/HS, (3) meets all Provider Admission Criteria, AND (4) Project Owner approves ceiling expansion or replacement of an existing provider |

**Phase 5 Constraints:**
- WTO ePing is Blocked / Pending Evidence for this gap. No re-evaluation unless new evidence of verifiable public REST API with server-side filtering emerges and Pre-Candidate Evidence Gate is passed.
- WTO TFA Database is Blocked / Pending Evidence for this gap. No re-evaluation unless new evidence of verifiable public REST API emerges and Pre-Candidate Evidence Gate is passed.
- Codex and IPPC remain Complementary (web-only). No provider feasibility.
- No WP creation for any SPS/TBT automation until a verifiable public REST API with filtering is confirmed.
- **This is a P0 Critical Gap that remains unfilled under current operational conditions. It is accepted as Complementary-Only for now, not permanently.**

### 27.8 Phase 6 — Rules of Origin + Remaining Coverage

**Purpose:** Re-evaluate Rules of Origin and remaining families after Phases 1-5. Do NOT add providers just to increase count.

| Attribute | Value |
|-----------|-------|
| **Phase Status** | Deferred — After Phases 1-5 |
| **Sources** | GCC-Stat (Provider), ITC Rules of Origin Facilitator (Complementary) |
| **Knowledge Family** | Rules of Origin |
| **Current Coverage** | 3/10 |
| **Target Coverage** | 3/10 (no change required) |
| **Gap** | No dedicated rules of origin database |
| **Primary Source** | GCC-Stat |
| **Secondary/Fallback** | None |
| **Strategic Sources** | ITC Rules of Origin Facilitator (Medium strategic value) |
| **Provider vs Complementary** | GCC-Stat = Provider; ITC Rules of Origin Facilitator = Complementary |
| **API / Machine Access** | GCC-Stat: SDMX/REST; ITC: Web only |
| **Licensing/Usage Constraints** | GCC-Stat: Free; ITC: Free for developing countries |
| **Operational Independence** | Medium — GCC scope only |
| **Resilience** | Weak — no fallback |
| **Dependencies** | None |
| **Implementation Priority** | P3 — No action unless business need changes |
| **Entry Gate** | N/A — No new provider needed |
| **Exit/Acceptance Gate** | N/A — Maintain current state |
| **Trigger for Re-Evaluation** | New API source emerges; or business priority shifts; or GCC-Stat coverage becomes insufficient |

**Phase 6 Constraints:**
- Do NOT add provider just to increase provider count.
- Only add provider if documented API availability + unique knowledge value + Project Owner approval.
- ITC Rules of Origin Facilitator remains Complementary.

### 27.9 Phase 7 — Portfolio Re-Evaluation

**Purpose:** After each implementation phase closure, or when new dependencies/sources/APIs emerge, re-evaluate the portfolio.

| Attribute | Value |
|-----------|-------|
| **Phase Status** | Triggered — After Each Phase Closure |
| **Scope** | Full portfolio re-evaluation |
| **Trigger** | Phase closure; new API source; licensing change; business priority shift |
| **Output** | Updated coverage scores, resilience assessment, candidate ranking |
| **Gate** | G0 — Portfolio Evaluation Approval (if new candidates emerge) |

**Re-Evaluation Criteria:**

| Criterion | Threshold |
|-----------|-----------|
| Coverage Threshold | All P0 and P1 gaps filled OR new P0/P1 gap identified |
| Marginal Knowledge Value | Next candidate adds measurable value |
| Redundancy Threshold | No duplication with existing providers |
| Maintenance Burden | Operational cost < knowledge value gained |
| API Feasibility | Documented, accessible REST/SDMX/JSON API verified |
| Licensing | Verified and approved before G1 |
| Provider Ceiling | Compliance with operational ceiling (currently 7). Further expansion requires separate PO approval with documented Knowledge Coverage justification. Provider count is not a goal. |
| Business Priority | Alignment with stated business priorities |

**Re-Evaluation Cycle:**

1. **Trigger:** Phase closure OR new source/API/ licensing event
2. **Assessment:** Update Coverage Matrix + Resilience Matrix + Candidate Ranking
3. **Decision:** Project Owner decides next phase activation
4. **Documentation:** Update this plan with findings
5. **Execution:** Only after explicit Project Owner decision + gate passage

---

## 28. Governance Rules for Implementation

### 28.1 Mandatory Pre-Implementation Rules

| Rule | Description |
|------|-------------|
| **No Provider Without Knowledge Sufficiency Justification** | Every provider must advance Knowledge Sufficiency / Knowledge Completion across the Seven Families. P0/P1 gaps are prioritized, but P2/P3 additions are allowed when Coverage, Marginal Value, and Resilience justify the addition. |
| **Provider Count is Not a Goal** | Expansion stops when knowledge sufficiency is achieved or marginal value = 0 |
| **Knowledge Coverage is the Primary Goal** | All decisions prioritize knowledge coverage over provider count |
| **Complementary Sources are Not Automatic Providers** | Reclassification requires documented machine-readable access |
| **API Feasibility Must Be Proven Before G1** | Live verification required; portal listing alone is insufficient |
| **Licensing Must Be Verified Before Implementation** | Commercial use and redistribution terms must be clear |
| **No WP Creation Without Gate Passage** | WP is created only after phase entry gate is passed |
| **No Implementation Directly From This Plan** | Implementation requires separate WP and full gate sequence |
| **Each Phase Has Independent WP** | When a phase is activated, its WP is created independently |
| **Owner Approval Delegation** | After Master Plan adoption and Phase activation, routine gate transitions within approved Gates do not require new Owner approval. See Section 28.1.1. |

#### 28.1.1 Owner Approval Delegation Principle

After Master Plan adoption and Phase activation, routine execution transitions within approved Gates are **delegated** and do **not** require new Owner approval.

**Owner approval is required ONLY for:**

1. **New Strategic Decision** — Change in business priority, family target, or portfolio direction
2. **Scope or Family Target Change** — Adding/removing knowledge families or changing coverage targets
3. **Governance Ceiling Exceedance** — Adding providers beyond the operational ceiling without prior approval
4. **Gate Exception** — Bypassing or modifying a gate requirement
5. **Essential Commercial/Licensing Decision** — Commercial use approval, licensing waiver, or redistribution model change
6. **Architectural Change** — Change affecting DEM core, Contract, Schema, or system-wide architecture

**Delegated transitions include:**
- G1 → G2 → G3 → G4 → G5 progression within an approved phase
- Phase activation after Master Plan approval
- Re-evaluation and next-phase recommendation within approved scope
- Compliance with existing governance rules

**Important:** This delegation does NOT eliminate the Gates themselves. Each gate remains mandatory and independent. Delegation only removes the requirement for new Owner approval for routine transitions within the approved governance framework.

### 28.2 Gate Sequence for New Providers

| Gate | Purpose | Required Evidence |
|------|---------|-------------------|
| **G0** | Portfolio Evaluation Approval | Coverage gap documented; marginal value > 0 |
| **G1** | Source Selection | API feasibility verified; licensing verified; Tier A confirmed |
| **G2** | Adapter Specification Review | Specification documented and reviewed |
| **G3** | Implementation Review | Code complete; tests passing |
| **G4** | Verification | Live validation passed; no regressions |
| **G5** | Closure | Evidence package complete; baseline tag created |

### 28.3 Stopping Conditions

Provider expansion stops when ANY of the following is true:

1. **Knowledge Sufficiency / Knowledge Completion:** All Seven-Family Knowledge Coverage targets are achieved and no further knowledge value can be gained.
2. **Marginal Knowledge Value = 0:** Next candidate adds no unique value or only covers P2/P3 families without sufficient justification.
3. **Redundancy Threshold:** Next candidate duplicates existing provider functionality.
4. **Maintenance Burden Ceiling:** Operational cost exceeds knowledge value.
5. **Business Priority Shift:** Business determines current coverage is sufficient for current phase.
6. **API Feasibility Blocked:** No verifiable public REST API for remaining candidates; gap accepted as Complementary-Only by Governance decision.

**Governance Trigger — Not a Stopping Condition:**

When the operational provider ceiling is reached, this triggers a **Governance Review for Ceiling Expansion** if a documented Knowledge Gap exists. The ceiling itself does NOT stop expansion; the stopping conditions above do. Expansion beyond the current ceiling requires:
- Documented Knowledge Gap with decision impact
- Marginal Knowledge Value > 0
- Feasibility confirmed (Pre-Candidate Evidence Gate passed)
- No adequate alternative within current ceiling
- Project Owner approval per Section 26.5.2

**Note:** Provider count is a governance constraint, not a stopping criterion by itself. The parent plan's 4–6 provider recommendation has been operationally expanded to 7 by Project Owner approval for World Bank LPI. The portfolio end state is Knowledge Sufficiency / Knowledge Completion, not a fixed provider count.

---

## 29. Re-Evaluation Cycle

### 29.1 Re-Evaluation Triggers

| Trigger | Action |
|---------|--------|
| **Phase Closure** | Re-evaluate coverage, resilience, and next phase readiness |
| **New API Source** | Evaluate against Provider Admission Criteria |
| **API Changes** | Re-verify feasibility; update classification if needed |
| **Licensing Change** | Re-verify terms; update G1 status if needed |
| **Business Priority Shift** | Re-prioritize families and candidates |
| **Provider Failure** | Activate fallback; re-evaluate coverage |
| **Annual Review** | Full portfolio re-evaluation |

### 29.2 Re-Evaluation Process

1. **Collect Evidence:** Verify API access, licensing, and coverage
2. **Update Matrices:** Coverage Matrix, Resilience Matrix, Candidate Ranking
3. **Assess Gaps:** Identify new or changed gaps
4. **Recommend:** Next phase activation or continuation
5. **Document:** Update this plan with findings
6. **Decide:** Project Owner makes explicit decision

### 29.3 Re-Evaluation Outputs

| Output | Description |
|--------|-------------|
| **Updated Coverage Scores** | Recalculated based on current providers |
| **Updated Resilience Assessment** | Reassessed fallback and independence |
| **Updated Candidate Ranking** | Re-ranked based on new evidence |
| **Next Phase Recommendation** | Clear recommendation for next action |
| **Open Items** | Documented blockers and unresolved issues |

---

## 30. Open Items and Blockers

### 30.1 Current Open Items

| # | Open Item | Status | Resolution Path |
|---|-----------|--------|-----------------|
| 1 | **SPS/TBT Automated Coverage Gap (0/10)** | **P0 — Unfilled — Accepted as Complementary-Only** | No machine-readable source currently meets Provider Admission Criteria; complementary access via ePing/Codex/IPPC maintained |
| 2 | **Market Access Trade Facilitation Gap** | **P0 — Unfilled** | WTO TFA Database (Blocked / Pending Evidence) could contribute to Market Access if it becomes accessible; no alternative source identified |
| 3 | **World Bank LPI Implementation** | **P1 — G5 CLOSED** | Ceiling expanded; all gates passed; implemented provider |
| 4 | **WTO Timeseries API Implementation** | **P1 — Blocked / Pending Evidence** | Pre-Candidate Evidence Gate not passed; awaiting resolution of commercial licensing, Egypt data sufficiency, and transport security |
| 5 | **ITC API Availability** | **P3 — Monitor** | No documented public REST API; monitor for future availability |
| 6 | **UNCTAD API Availability** | **P3 — Monitor** | No documented public REST API; monitor for future availability |
| 7 | **SPS/TBT Re-evaluation Trigger** | **P0 — Monitor** | Re-open candidate evaluation only when a new source provides current SPS/TBT data with server-side filtering and meets Provider Admission Criteria |

### 30.2 Governance Blockers

| Blocker | Source | Resolution |
|---------|--------|------------|
| **SPS/TBT Automated Access** | None currently available | Accept Complementary-Only; re-evaluate only when a new source meets Provider Admission Criteria with current data and filtering |
| **Market Access Trade Facilitation Automated Access** | WTO TFA Database | Public REST API required; if accessible, contributes to Market Access family |
| **ITC Automation** | ITC Tools | Documented public REST API required |
| **UNCTAD Automation** | UNCTAD LSCI/PLSCI | Documented public REST API or bulk-download infrastructure approval |

### 30.3 Candidate Source Research — Governance Decision

**Decision:** Maintain Monitoring. Candidate Source Research is **Paused**, not Terminated.

**Status of P0/P1 Knowledge Gaps:**

| Knowledge Family | Gap | Priority | Status |
|------------------|-----|----------|--------|
| Regulatory / SPS / TBT | 0/10 → 9/10 | P0 Critical | Open + Material + Monitoring |
| Market Access | 5/10 → 8/10 | P1 High | Open + Material + Monitoring |
| Trade Intelligence | 7/10 → 9/10 | P1 High | Open + Material + Monitoring |

**Rationale:**
- Multiple Candidate Source Research cycles have been completed.
- No viable new candidates were discovered for P0/P1 gaps.
- Known blocked sources remain blocked with no evidence of change.
- Continuing open-ended research would produce diminishing returns without additional evidence.
- The gaps remain material and must stay open.

**Important:** These gaps are NOT closed. Knowledge Sufficiency is NOT achieved. Monitoring is NOT a substitute for Knowledge Coverage. Operational portfolio remains at 7 providers while Knowledge Sufficiency remains the governing criterion.

### 30.4 Re-triggers for Candidate Source Research

Candidate Source Research will be re-activated only when one or more of the following Evidence Triggers occur:

| Trigger | Applies To | Action |
|---------|-----------|--------|
| New machine-readable/API source discovered with verified public REST/SDMX/JSON access | All P0/P1 gaps | Re-initiate Candidate Source Research |
| Substantial change in API accessibility, licensing, or data freshness for a known blocked source | WTO ePing, WTO TFA Database, WTO Timeseries API, UNCTADstat, IMF IMTS | Re-evaluate source for Pre-Candidate Evidence Gate |
| Documented new research path emerges with reasonable expectation of viable candidate | All P0/P1 gaps | Governance Review → Decision to continue research |

**Governance Rule:** Re-activation requires documented Evidence Trigger, not speculative search. Ceiling expansion remains possible with documented Knowledge Coverage justification per Section 26.5.2 if a viable candidate emerges and the current ceiling becomes a constraint.

---

## 31. Plan Status and Next Actions

### 31.1 Current Plan Status

**Status:** Approved — G0 Approved — Owner Adopted as Official Reference — Phase 1 Activated — World Bank LPI G5 Closure — Current State Maintained (7/7 Providers; Current Operational Ceiling = 7)

**Authority:** `PLAN.md` (Master Roadmap v2.1) — Single Source of Truth

**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`

### 31.2 Next Actions (In Order)

| # | Action | Owner | Constraint |
|---|--------|-------|------------|
| 1 | **Current state: 7/7 providers implemented; current operational ceiling = 7** | — | No further provider addition without Owner Approval AND documented Knowledge Coverage justification per Section 26.5.2 |
| 2 | World Bank LPI G5 Closure — all gates passed | Governance | Delegated per Owner Approval Delegation Principle (Section 28.1.1); no further action required for World Bank LPI |
| 3 | Maintain Complementary SPS/TBT access via ePing/Codex/IPPC | Governance | No automated provider; manual/complementary access only |
| 4 | Monitor for new machine-readable SPS/TBT source with filtering | Governance | Re-evaluate only when source provides current data + filtering + meets Provider Admission Criteria |
| 5 | Maintain Monitoring for Market Access gap (WTO Timeseries API, WTO TFA Database) | Governance | No Candidate Source Research at this time; re-activate only when Evidence Trigger occurs per Section 30.4 |
| 6 | Maintain Monitoring for Trade Intelligence gap (UNCTADstat, IMF IMTS) | Governance | No Candidate Source Research at this time; re-activate only when Evidence Trigger occurs per Section 30.4 |
| 7 | Annual portfolio re-evaluation | Governance | Triggered by date or event |

### 31.3 Constraints Summary

- **No provider implementation** from this plan.
- **No WP creation** from this plan.
- **No code changes** from this plan.
- **No architecture changes** from this plan.
- **No new Owner decisions** from this plan.
- **No invented evidence or APIs** in this plan.
- **Provider ceiling reached:** Current operational ceiling is 7 providers. This is a current governance control, not the portfolio end state and not a permanent blocker to addressing documented Knowledge Gaps. Further expansion requires separate Project Owner approval with documented Knowledge Coverage justification per Section 26.5.2.
- **No ceiling expansion:** No expansion beyond 7 is authorized without explicit Project Owner approval per Section 26.5.2. This is the current approved state, not a permanent prohibition.
- **P0 gaps remain blocked:** WTO ePing and WTO TFA Database are Blocked / Pending Evidence (Pre-Candidate Evidence Gate not passed); no action until verifiable public REST API is confirmed and Pre-Candidate Evidence Gate is passed.
- **Provider count is not a goal:** Providers are added only when a documented Knowledge Coverage gap exists, marginal knowledge value is proven, and operational feasibility is confirmed.
- **Candidate Source Research is Paused, not Terminated:** P0/P1 Knowledge Gaps remain open and material. Re-activation requires documented Evidence Trigger per Section 30.4. Monitoring is NOT a substitute for Knowledge Coverage.

All implementation activities require separate Project Owner decisions and gate passage per the sequence defined in Section 28.2. World Bank LPI has completed all gates (G1–G5); no further gates required for this provider. Any future provider addition requires ceiling expansion approval per Section 26.5.

---

*Plan Status: Approved — G0 Approved — Owner Adopted as Official Reference — 7-Family Portfolio Implementation Master Plan / Governance Roadmap — Phase 1 Activated — World Bank LPI G5 Closure — Current State Maintained (7/7 Providers; Current Operational Ceiling = 7) — Candidate Source Research Paused — Knowledge Gaps Open*













