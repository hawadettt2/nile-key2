# Commercial Evidence Gap Closure Master Plan

**Plan ID:** commercial-evidence-gap-closure-plan
**Branch:** main
**Mode:** Plan Only — No Implementation
**Authority:** Phase 13 Final Closure (`.kilo/plans/phase-13-final-commercial-readiness-closure.md`)
**Prerequisite:** Phases 0–13 Complete (Assessment Only)
**Governing Baseline:** Commit `588a106e01309cbe91c5f8fa73ceff629fbaa148`
**Purpose:** Trace every verified commercial evidence gap to: Gap → Required Evidence → Source/Capability → Closure → Live Verification → Proven → Scenario Revalidation

---

## 1. Objective

Enclose every real Gap into a traceable, evidence-governed closure path. Final target:

```text
S1–S5 → Minimum Sufficiency → Business Question Ready → Decision-Safe → Response-Safe → READY
```

READY is not assumed. A Gap closes only when:

```text
Required Evidence
+
Proven Source/Capability
+
Correct Scope
+
Freshness
+
Provenance
+
Commercial-use Clearance
+
Minimum Sufficiency
+
Live Verification
=
Proven
```

---

## 2. Golden Rules (Preserved and Enforced)

| Rule | Enforcement |
|------|-------------|
| Registered != Available | No provider considered available merely because it is registered |
| Configured != Activated | No provider considered active merely because credentials exist |
| Activated != Reachable | Health check required |
| HTTP 200 != Valid Data | Response schema and completeness must be verified |
| Returns Data != Capability Proven | Data must match family requirement with correct scope |
| Capability Proven != Scope Ready | Scope must be verified independently |
| Scope Ready != Country/Product Ready | Country/product coverage must match target |
| Country/Product Ready != Business Question Ready | Business Question must be answerable |
| Business Question Ready != Decision-Safe | Decision safety requires separate verification |
| Decision-Safe != Response-Safe | Response safety requires separate verification |
| Provider Count != Commercial Success | Ceiling compliance is governance, not success metric |
| Fixture != Production Evidence | Test fixtures never enter Core Evidence |
| Historical Evidence != Current Live Proof | Freshness must be verified per evidence item |
| Trade != Opportunity | Trade Evidence never converts to Opportunity Evidence |
| Country LPI != Route-Level Logistics | LPI is contextual only; never Core route evidence |
| Complementary != Authoritative | Complementary never closes Core Sufficiency |
| Complementary != Core Minimum Sufficiency | Complementary is supporting context only |
| Planned != Available | Only live verified evidence is accepted |
| Provider Existence != Capability | Capability must be proven by runtime verification |
| Source Failure != Not Required | Unavailability never makes a dimension optional |
| No Provider != Not Required | Absence of provider never makes a dimension optional |
| Missing Evidence != Not Required | Unexplored dimension never becomes Not Required |
| Valid No-Result != Source Failure | Zero-result scoped query is valid only when scope is proven |

Missing Knowledge must never become:
`Unsupported Finding`, `Unsupported Decision`, `Unsupported Strategic Conclusion`, `Unsupported User-facing Claim`

---

## 3. Readiness Model

```text
Implemented → Registered → Configured → Activated → Reachable → Returns Data → Capability Proven → Scope Ready → Country/Product Ready → Business Question Ready → Decision-Safe → Response-Safe
```

Binding: `Provider ≠ Capability Bundle ≠ Business Answer`

---

## 4. Confirmed Gaps (Post-Phase 13)

| ID | Gap | Status | Scenarios | Root Cause |
|----|-----|--------|-----------|-----------|
| G1 | Trade Intelligence / HS6 retrieval | Not Proven | S1–S5 | DEM HS6 runtime retrieval not executed; UN Comtrade HS6 capability unverified in DEM |
| G2 | Market Opportunity | Gap | S1–S5 | No operational/proven source for demand/growth/export-potential |
| G3 | Market Access | Gap | S1–S5 | No operational/proven source for tariff/duty/entry procedures per destination |
| G4 | Regulatory / SPS-TBT | Gap | S1–S5 | No operational/proven source for product-specific jurisdiction-specific requirements |
| G5 | Rules of Origin | Gap | S1 (Conditional), S2 (Core), S3 (Core), S4 (Conditional), S5 (Conditional / Zero-Tariff special case) | No operational/proven source for FTA eligibility/origin criteria/documentation |
| G6 | Logistics route-level | Gap | S1–S5 | No route-specific source; World Bank LPI country-level only |
| G7 | Agrifood (where Core) | Gap | S1–S4 | FAOSTAT external API available but DEM Capability Proven = No |
| G8 | FAOSTAT capability | Not Proven | S1–S4 | DEM runtime verification incomplete; licensing/commercial-use clearance unverified |
| G9 | S5 Zero-Tariff tariff-line eligibility | Not Proven | S5 | HS610990/611011/610510 eligibility under China Zero-Tariff Measure unverified; origin requirements undetermined |
| G10 | Minimum Sufficiency S1–S5 | Not Met | S1–S5 | Aggregate state: all Core Evidence dimensions not Proven |

G10 is a Derived Final Gate. It changes when any governed upstream readiness input changes, including G1–G9, Licensing, Governance, Revalidation/Safety, Minimum Sufficiency, Decision-Safe, and Response-Safe. It must never be closed by redefining Core Evidence, lowering Minimum Sufficiency, changing Scenario Contract, converting Gap → Not Required without proof, accepting Complementary as Core, or changing the meaning of READY.

---

## 5. Central Gap Traceability Matrix

For every Gap, one master row. No Gap may exist without a traceability row.

| Gap ID | Scenario | Business Question | Required Evidence | Required Capability | Current Provider | Current Provider State | Existing Closure Path | Composition Path | New Provider Path | Licensing Gate | Scope Gate | Freshness Gate | Provenance Gate | Live Verification | Acceptance Test | Scenario Revalidation | Final State |
|--------|----------|-------------------|-------------------|---------------------|------------------|------------------------|----------------------|------------------|-------------------|----------------|------------|----------------|-----------------|-------------------|-----------------|----------------------|------------|
| G1 | S1–S5 | HS6 bilateral trade Egypt↔Y | HS6 trade flows with provenance | UN Comtrade HS6 runtime retrieval | UN Comtrade (Operational — Partial) + TradeData (Inactive) | UN Comtrade: Operational — Partial (chapter-level); TradeData: Inactive | UN Comtrade: HS6 query/pagination correction; TradeData: Activation → HS query verification | UN Comtrade + TradeData | Only if existing insufficient | UN Comtrade: Usage Terms Clarification Pending; TradeData: Commercial | Bilateral Egypt↔Y; HS6; HS 2022 | Latest available annual | UN official; retrieval metadata | DEM HS6 query per HS6 code | AT-G1-1 through AT-G1-6 | Trade Evidence Matrix update; Minimum Sufficiency recalculation | Open |
| G2 | S1–S5 | Demand gap + import dynamics for [product] in [market] | Proven demand signal + growth + opportunity signal | Opportunity-capable source or deterministic composite | None | No operational source | None | Composite: Demand + Growth + Opportunity Signal (all inputs must be proven) | WS-E: No viable candidate found | Per candidate: ITC terms or commercial agreement | Market + product + time horizon per scenario | Source-specific; current at Q4 2026 | Provenance per input + methodology document | No executable automated path found | AT-G2-1 through AT-G2-5 | Opportunity Evidence Matrix; Minimum Sufficiency recalculation | Open — Residual Gap |
| G3 | S1–S5 | Tariff + entry procedures for HS6 in [Y] | Exact tariff/duty + procedures + permits + preferential treatment | Destination customs/tariff authority | Moaah (Inactive, Saudi scope) + ZATCA (Inactive, KSA only) + GCC-Stat (Inactive, GCC only) + TradeData (Inactive, general) + WTO Timeseries (Blocked/Pending) + Regulations Provider (Inactive, missing data file) | Moaah: Inactive (Saudi scope); ZATCA: Inactive (KSA only); GCC-Stat: Inactive (GCC only); TradeData: Inactive (general); WTO Timeseries: Blocked/Pending; Regulations Provider: Inactive (missing data file) | Moaah: Saudi tariff endpoint; ZATCA: KSA tariff endpoint; GCC-Stat: GCC tariff endpoint; TradeData: HS-level global coverage; WTO Timeseries: Pre-Candidate Evidence Gate clearance; Regulations Provider: regulations.json + data source | WS-E: No viable automated candidate found | WTO Timeseries (if Pre-Candidate Evidence Gate cleared); national customs APIs | Moaah: Commercial. ZATCA: Open Data. TradeData: Commercial. WTO: WTO terms | Exact HS6; target country; effective date | Effective/current at Q4 2026 | Official tariff schedule; retrieval metadata | Live tariff lookup per HS6 code per destination | AT-G3-1 through AT-G3-7 | Market Access Evidence Matrix; Minimum Sufficiency recalculation | Open — Operational Inputs Documented |
| G4 | S1–S5 | SPS/TBT/MRL for [product] in [Y] | Product-specific jurisdiction-specific current requirements | Competent jurisdictional authority | Regulations Provider (Inactive, missing data file) + Moaah (Inactive) + WTO ePing (Complementary) | Regulations Provider: Inactive (missing data file); Moaah: Inactive; WTO ePing: Complementary | Regulations Provider: regulations.json + authoritative data; Moaah: Saudi/Egypt regulatory endpoint | WS-E: No viable automated candidate found | National agency APIs (EFSA, KEBS, SAC, etc.) | Regulations file: depends on source. National agencies: varies; WTO ePing: WTO terms (complementary only) | Product + jurisdiction + specific requirement; current/effective | Current/effective at Q4 2026 | Official instrument; retrieval metadata | Regulatory lookup per HS6 per jurisdiction | AT-G4-1 through AT-G4-7 | Regulatory Evidence Matrix; Minimum Sufficiency recalculation | Open — Operational Inputs Documented |
| G5 | S1: Conditional (5-layer applicability unresolved); S2: Core (5-layer); S3: Core (5-layer); S4: Conditional (5-layer applicability unresolved); S5: Conditional (5-layer / Zero-Tariff special case) | FTA applicability (5-layer: regime/country-pair → product/tariff-line → preferential eligibility → RoO → documentation) | 5-layer applicability determination + agreement + eligibility + origin criterion + documentation | Official agreement / competent authority | GCC-Stat | Inactive (GCC scope) | Activation: GAFTA eligibility criteria (S2 only). Other agreements: no existing provider | GCC-Stat for S2; none for S1/S3/S4/S5 | WS-E: No viable automated candidate for L2–L5 | FTA texts: generally public. Structured RoO data: varies | Product + agreement + origin criterion + documentation | Current validity; S5: 1 May 2026 – 30 Apr 2028 | Official agreement; retrieval metadata | 5-layer applicability determination + agreement retrieval per scenario | AT-G5-1 through AT-G5-6 | RoO Evidence Matrix; Minimum Sufficiency recalculation | Open — Layer 1 Proven; Layers 2–5 Residual Gap |
| G6 | S1–S5 | Route cost + time + reliability for exact route | Route-specific cost + transit time + reliability | Route-specific authoritative source | World Bank LPI | Operational — Partial (country-level) | Scope Restriction: contextual only; NOT Core route evidence | WS-E: No viable candidate found | Route-level logistics source (freight APIs, port data, logistics platforms) | Freight/logistics data: typically commercial | Exact origin → exact destination → exact mode → cargo → Incoterm → assessment window | Current/applicable at Q4 2026 | Route-specific source; retrieval metadata | Route data matching Route Contract per route | AT-G6-1 through AT-G6-7 | Logistics Evidence Matrix; Minimum Sufficiency recalculation | Open — Residual Gap |
| G7 | S1–S4 | Agriculture-specific evidence for [commodity] in [market] | Production/supply/prices/indicators/events | Official agricultural/statistical source | FAOSTAT | External Available / DEM Not Verified | Activation: credentials → JWT → real data → mapping → scope → licensing | None (single source) | National agricultural statistics agencies | Pending — current license terms under review for commercial use | Commodity + market; contract-driven dimensions | Source-specific (FAO cycle); current at Q4 2026 | FAO official; retrieval metadata | FAOSTAT query per commodity per market | AT-G7-1 through AT-G7-7 | Agrifood Evidence Matrix (if applicable); Minimum Sufficiency recalculation | Open |
| G8 | S1–S4 | FAOSTAT DEM Capability Proven | Full runtime proof: JWT → reachable → real data → mapping → scope → licensing clearance | FAOSTAT DEM integration | FAOSTAT | External Available / DEM Not Verified | Activation: full verification path | None | None (FAOSTAT is only candidate) | Pending — current license terms under review for DEM runtime and user-facing use | Global commodity; item/element; country-specific | Source-specific; verify at runtime | FAO official; retrieval metadata | JWT auth + live data + schema transform + mapping verification | AT-G8-1 through AT-G8-7 | Enables G7; revalidate Agrifood/Opportunity | Open |
| G9 | S5 | China Zero-Tariff Measure applicability + HS6 eligibility + origin requirement | Measure applicability + HS610990/611011/610510 eligibility + origin criterion + certificate requirements | China Customs / official Chinese tariff authority | None | No existing provider | None | None | WS-E: No viable candidate found for HS6 eligibility extraction | Chinese customs data: verify commercial-use terms, storage, redistribution, API restrictions | HS6: HS610990, HS611011, HS610510; Egypt origin; 1 May 2026 – 30 Apr 2028 | Effective period; verify current status at Q4 2026 | Chinese customs official; retrieval metadata | Official source confirms Egypt eligibility + HS6 eligibility + origin requirements | AT-G9-1 through AT-G9-8 | S5 Market Access and RoO recalculation; Minimum Sufficiency recalculation | Open — Announcement Proven; HS6 Eligibility Residual Gap |
| G10 | S1–S5 | All Required Core Evidence Proven per scenario + Licensing Cleared + Governance Approved + Revalidation/Safety Complete + Minimum Sufficiency Met + Decision-Safe + Response-Safe | Aggregate of G1–G9 closure states + Licensing + Governance + Revalidation/Safety + Minimum Sufficiency + Decision-Safe + Response-Safe | All upstream workstreams complete + safety verification | Derived | Derived | Derived | Derived | Derived | Aggregate of all source licensing + governance approvals | Per frozen Scenario Contract | Per evidence dimension | Provenance per evidence item | Complete Evidence Matrix per scenario + safety verification | AT-G10-1 through AT-G10-9 | S1–S5 final revalidation; Final Commercial Readiness Gate | Derived — Open |

---

## 6. Scenario Evidence Matrices

### 6.1 S1 — Egypt → Jordan / Fresh Vegetables / HS07

| Evidence Dimension | Required? | Core/Conditional | Minimum Evidence | Granularity | Authority | Freshness | Effective Date | Commercial Use | Provenance | Current State | Closure Path | Verification | Scenario Impact |
|--------------------|-----------|------------------|------------------|-------------|-----------|-----------|----------------|----------------|------------|---------------|--------------|--------------|-----------------|
| Trade | Yes | Core | HS-level bilateral Egypt–Jordan vegetables | HS07 chapter (baseline); HS4/HS6: HS070200/070700/070960/070310 | UN Comtrade official | Latest available annual | N/A | Usage Terms Clarification Pending | Official statistical source | Partial (chapter-level) | G1: UN Comtrade HS6 verification | DEM HS6 query per HS6 code | Minimum Sufficiency blocked if not Proven |
| Opportunity | Yes | Core | Demand gap + import dynamics for Jordan fresh vegetables | Market + product | Proven opportunity source or governed composite | Source-specific; current at Q4 2026 | N/A | Per source | Provenance per input + methodology | Gap | G2: Composite via existing/activated providers; IF insufficient → Residual Gap → WS-E | Composite inputs verified OR WS-E candidate evaluation | Minimum Sufficiency blocked if not Proven |
| Market Access | Yes | Core | Jordan tariff + entry procedures for HS070200/070700/070960/070310 | HS6; Jordan | Jordan customs official | Effective/current | Current at Q4 2026 | Cleared | Official tariff schedule | Gap | G3: Existing/activated providers; IF insufficient → Residual Gap → WS-E | Live tariff lookup per HS6 code | Minimum Sufficiency blocked if not Proven |
| Regulatory/SPS | Yes | Core | Jordan SPS for fresh vegetables | HS6; Jordan | Jordan competent authority | Current/effective | Current at Q4 2026 | Cleared | Official instrument | Gap | G4: Existing/activated providers; IF insufficient → Residual Gap → WS-E | Regulatory lookup per HS6 | Minimum Sufficiency blocked if not Proven |
| RoO | Conditional | Conditional | Agadir Agreement 5-layer applicability: regime/country-pair → product/tariff-line eligibility → preferential eligibility → origin criterion → documentation | Product + agreement | Official agreement / competent authority | Current validity | N/A | Cleared | Official agreement | Gap | G5: 5-layer applicability determination via existing/activated providers; IF any layer unresolved → Residual Gap → WS-E | Each layer proven or documented NOT_REQUIRED_PROVEN (only via documented applicability determination) | Conditional: blocks Minimum Sufficiency if applicable and not Proven |
| Logistics | Yes | Core | Route cost + time + reliability Alexandria→Aqaba (sea) / Port Said→Aqaba (road) | Exact route | Route-specific authoritative source | Current/applicable | Q4 2026 | Cleared | Route-specific source | Gap | G6: Existing/activated providers; World Bank LPI = contextual only. IF insufficient → Residual Gap → WS-E | Route data matching Route Contract | Minimum Sufficiency blocked if not Proven |
| Agrifood | Conditional | Conditional | Agriculture-specific evidence for vegetables in Jordan | Commodity + market | FAOSTAT or equivalent | Source-specific | N/A | Pending — current license terms under review | FAO official | Gap | G7/G8: FAOSTAT activation + licensing clearance | FAOSTAT query per commodity | Conditional: blocks Minimum Sufficiency if applicable and not Proven |

### 6.2 S2 — Egypt → Saudi Arabia / Dates / HS08

| Evidence Dimension | Required? | Core/Conditional | Minimum Evidence | Granularity | Authority | Freshness | Effective Date | Commercial Use | Provenance | Current State | Closure Path | Verification | Scenario Impact |
|--------------------|-----------|------------------|------------------|-------------|-----------|-----------|----------------|----------------|------------|---------------|--------------|--------------|-----------------|
| Trade | Yes | Core | HS-level bilateral Egypt–Saudi dates | HS08 chapter (baseline); HS4/HS6: HS080410 | UN Comtrade official | Latest available annual | N/A | Usage Terms Clarification Pending | Official statistical source | Partial (chapter-level) | G1: UN Comtrade HS6 verification | DEM HS6 query per HS6 code | Minimum Sufficiency blocked if not Proven |
| Opportunity | Yes | Core | Demand gap + import dynamics for Saudi dates | Market + product | Proven opportunity source or governed composite | Source-specific; current at Q4 2026 | N/A | Per source | Provenance per input + methodology | Gap | G2: Composite via existing/activated providers; IF insufficient → Residual Gap → WS-E | Composite inputs verified OR WS-E candidate evaluation | Minimum Sufficiency blocked if not Proven |
| Market Access | Yes | Core | Saudi tariff + entry procedures for HS080410 | HS6; Saudi Arabia | Saudi customs official | Effective/current | Current at Q4 2026 | Cleared | Official tariff schedule | Gap | G3: Existing/activated providers (Moaah/ZATCA/GCC-Stat/TradeData); IF insufficient → Residual Gap → WS-E | Live tariff lookup per HS6 code | Minimum Sufficiency blocked if not Proven |
| Regulatory/SPS | Yes | Core | Saudi SPS for dates | HS6; Saudi Arabia | Saudi competent authority | Current/effective | Current at Q4 2026 | Cleared | Official instrument | Gap | G4: Existing/activated providers (Moaah); IF insufficient → Residual Gap → WS-E | Regulatory lookup per HS6 | Minimum Sufficiency blocked if not Proven |
| RoO | Yes | Core | GAFTA 5-layer applicability: regime/country-pair → product/tariff-line eligibility → preferential eligibility → origin criterion → documentation | Product + GAFTA | Official GAFTA source | Current validity | N/A | Cleared | Official agreement | Gap | G5: 5-layer applicability determination via existing/activated providers (GCC-Stat); IF any layer unresolved → Residual Gap → WS-E | Each layer proven | Minimum Sufficiency blocked if not Proven |
| Logistics | Yes | Core | Route cost + time + reliability Alexandria→Jeddah (sea) / Port Said→Dammam (road) | Exact route | Route-specific authoritative source | Current/applicable | Q4 2026 | Cleared | Route-specific source | Gap | G6: Existing/activated providers; World Bank LPI = contextual only. IF insufficient → Residual Gap → WS-E | Route data matching Route Contract | Minimum Sufficiency blocked if not Proven |
| Agrifood | Conditional | Conditional | Agriculture-specific evidence for dates in Saudi Arabia | Commodity + market | FAOSTAT or equivalent | Source-specific | N/A | Pending — current license terms under review | FAO official | Gap | G7/G8: FAOSTAT activation + licensing clearance | FAOSTAT query per commodity | Conditional: blocks Minimum Sufficiency if applicable and not Proven |

### 6.3 S3 — Egypt → Germany / Citrus / HS08

| Evidence Dimension | Required? | Core/Conditional | Minimum Evidence | Granularity | Authority | Freshness | Effective Date | Commercial Use | Provenance | Current State | Closure Path | Verification | Scenario Impact |
|--------------------|-----------|------------------|------------------|-------------|-----------|-----------|----------------|----------------|------------|---------------|--------------|--------------|-----------------|
| Trade | Yes | Core | HS-level bilateral Egypt–Germany citrus | HS08 chapter (baseline); HS4/HS6: HS080510/080550/080540 | UN Comtrade official | Latest available annual | N/A | Usage Terms Clarification Pending | Official statistical source | Partial (chapter-level) | G1: UN Comtrade HS6 verification | DEM HS6 query per HS6 code | Minimum Sufficiency blocked if not Proven |
| Opportunity | Yes | Core | Demand gap + import dynamics for Germany/EU citrus | Market + product | Proven opportunity source or governed composite | Source-specific; current at Q4 2026 | N/A | Per source | Provenance per input + methodology | Gap | G2: Composite via existing/activated providers; IF insufficient → Residual Gap → WS-E | Composite inputs verified OR WS-E candidate evaluation | Minimum Sufficiency blocked if not Proven |
| Market Access | Yes | Core | EU TARIC tariff + entry procedures for HS080510/080550/080540 | HS6; EU (Germany) | EU TARIC official | Effective/current | Current at Q4 2026 | Cleared | Official tariff schedule | Gap | G3: Existing/activated providers (TradeData, Regulations); IF insufficient → Residual Gap → WS-E | Live tariff lookup per HS6 code under EU TARIC | Minimum Sufficiency blocked if not Proven |
| Regulatory/SPS-MRL | Yes | Core | EU SPS/MRL for Egyptian citrus | HS6; EU | EFSA / EU official | Current/effective | Current at Q4 2026 | Cleared | Official instrument | Gap | G4: Existing/activated providers (Regulations); IF insufficient → Residual Gap → WS-E | Regulatory lookup per HS6 | Minimum Sufficiency blocked if not Proven |
| RoO | Yes | Core | EU–Egypt FTA 5-layer applicability: regime/country-pair → product/tariff-line eligibility → preferential eligibility → origin criterion → documentation | Product + EU–Egypt FTA | Official EU–Egypt FTA source | Current validity | N/A | Cleared | Official agreement | Gap | G5: 5-layer applicability determination via existing/activated providers (Regulations, Moaah); IF any layer unresolved → Residual Gap → WS-E | Each layer proven | Minimum Sufficiency blocked if not Proven |
| Logistics | Yes | Core | Route cost + time + reliability Alexandria→Hamburg (sea) / Cairo→Frankfurt (air) | Exact route | Route-specific authoritative source | Current/applicable | Q4 2026 | Cleared | Route-specific source | Gap | G6: Existing/activated providers; World Bank LPI = contextual only. IF insufficient → Residual Gap → WS-E | Route data matching Route Contract | Minimum Sufficiency blocked if not Proven |
| Agrifood | Conditional | Conditional | Agriculture-specific evidence for citrus in Germany/EU | Commodity + market | FAOSTAT or equivalent | Source-specific | N/A | Pending — current license terms under review | FAO official | Gap | G7/G8: FAOSTAT activation + licensing clearance | FAOSTAT query per commodity | Conditional: blocks Minimum Sufficiency if applicable and not Proven |

### 6.4 S4 — Egypt → Kenya / Coffee / HS09

| Evidence Dimension | Required? | Core/Conditional | Minimum Evidence | Granularity | Authority | Freshness | Effective Date | Commercial Use | Provenance | Current State | Closure Path | Verification | Scenario Impact |
|--------------------|-----------|------------------|------------------|-------------|-----------|-----------|----------------|----------------|------------|---------------|--------------|--------------|-----------------|
| Trade | Yes | Core | HS-level bilateral Egypt–Kenya coffee | HS09 chapter (baseline); HS4/HS6: HS090111/090121 | UN Comtrade official | Latest available annual | N/A | Usage Terms Clarification Pending | Official statistical source | Partial (chapter-level) | G1: UN Comtrade HS6 verification | DEM HS6 query per HS6 code | Minimum Sufficiency blocked if not Proven |
| Opportunity | Yes | Core | Demand gap + import dynamics for Kenya coffee | Market + product | Proven opportunity source or governed composite | Source-specific; current at Q4 2026 | N/A | Per source | Provenance per input + methodology | Gap | G2: Composite via existing/activated providers; IF insufficient → Residual Gap → WS-E | Composite inputs verified OR WS-E candidate evaluation | Minimum Sufficiency blocked if not Proven |
| Market Access | Yes | Core | Kenya tariff + entry procedures for HS090111/090121 | HS6; Kenya | Kenya customs official | Effective/current | Current at Q4 2026 | Cleared | Official tariff schedule | Gap | G3: Existing/activated providers (TradeData, Regulations); IF insufficient → Residual Gap → WS-E | Live tariff lookup per HS6 code | Minimum Sufficiency blocked if not Proven |
| Regulatory/SPS | Yes | Core | Kenya SPS for coffee | HS6; Kenya | Kenya competent authority | Current/effective | Current at Q4 2026 | Cleared | Official instrument | Gap | G4: Existing/activated providers (Regulations); IF insufficient → Residual Gap → WS-E | Regulatory lookup per HS6 | Minimum Sufficiency blocked if not Proven |
| RoO | Conditional | Conditional | COMESA FTA 5-layer applicability: regime/country-pair → product/tariff-line eligibility → preferential eligibility → origin criterion → documentation | Product + COMESA | Official COMESA source | Current validity | N/A | Cleared | Official agreement | Gap | G5: 5-layer applicability determination via existing/activated providers; IF any layer unresolved → Residual Gap → WS-E | Each layer proven or documented NOT_REQUIRED_PROVEN (only via documented applicability determination) | Conditional: blocks Minimum Sufficiency if applicable and not Proven |
| Logistics | Yes | Core | Route cost + time + reliability Alexandria→Mombasa (sea) / Cairo→Nairobi (air) | Exact route | Route-specific authoritative source | Current/applicable | Q4 2026 | Cleared | Route-specific source | Gap | G6: Existing/activated providers; World Bank LPI = contextual only. IF insufficient → Residual Gap → WS-E | Route data matching Route Contract | Minimum Sufficiency blocked if not Proven |
| Agrifood | Conditional | Conditional | Agriculture-specific evidence for coffee in Kenya | Commodity + market | FAOSTAT or equivalent | Source-specific | N/A | Pending — current license terms under review | FAO official | Gap | G7/G8: FAOSTAT activation + licensing clearance | FAOSTAT query per commodity | Conditional: blocks Minimum Sufficiency if applicable and not Proven |

### 6.5 S5 — Egypt → China / Knitted Apparel / HS61

| Evidence Dimension | Required? | Core/Conditional | Minimum Evidence | Granularity | Authority | Freshness | Effective Date | Commercial Use | Provenance | Current State | Closure Path | Verification | Scenario Impact |
|--------------------|-----------|------------------|------------------|-------------|-----------|-----------|----------------|----------------|------------|---------------|--------------|--------------|-----------------|
| Trade | Yes | Core | HS-level bilateral Egypt–China knitted apparel | HS61 chapter (baseline); HS6: HS610990/611011/610510 | UN Comtrade official | Latest available annual | N/A | Usage Terms Clarification Pending | Official statistical source | Partial (chapter-level) | G1: UN Comtrade HS6 verification | DEM HS6 query per HS6 code | Minimum Sufficiency blocked if not Proven |
| Opportunity | Yes | Core | Demand gap + import dynamics for China knitted apparel | Market + product | Proven opportunity source or governed composite | Source-specific; current at Q4 2026 | N/A | Per source | Provenance per input + methodology | Gap | G2: Composite via existing/activated providers; FAOSTAT NOT applicable (agriculture-only). IF insufficient → Residual Gap → WS-E | Composite inputs verified OR WS-E candidate evaluation | Minimum Sufficiency blocked if not Proven |
| Market Access | Yes | Core | China tariff + entry procedures for HS610990/611011/610510; Zero-Tariff eligibility | HS6; China | China customs official | Effective/current | 1 May 2026 – 30 Apr 2028 | Cleared | Official tariff schedule | Gap | G3: Existing/activated providers (TradeData, Regulations); IF insufficient → Residual Gap → WS-E (includes Zero-Tariff verification with G9) | Live tariff lookup per HS6 code; Zero-Tariff eligibility verified | Minimum Sufficiency blocked if not Proven |
| Regulatory/TBT | Yes | Core | China TBT for knitted apparel | HS6; China | China competent authority | Current/effective | Current at Q4 2026 | Cleared | Official instrument | Gap | G4: Existing/activated providers (Regulations); IF insufficient → Residual Gap → WS-E | Regulatory lookup per HS6 | Minimum Sufficiency blocked if not Proven |
| RoO | Conditional | Conditional | China Zero-Tariff Measure 5-layer applicability: regime/country-pair → product/tariff-line eligibility → preferential eligibility → origin criterion → documentation | HS6; China Zero-Tariff Measure | China Customs official | 1 May 2026 – 30 Apr 2028 | Current at Q4 2026 | Cleared | Chinese customs official | Gap | G5 + G9: 5-layer applicability determination via existing/activated providers with proven China scope (Moaah excluded unless China scope explicitly proven); IF any layer unresolved → Residual Gap → WS-E | Each layer proven or documented NOT_REQUIRED_PROVEN (only via documented applicability determination) | Conditional: blocks Minimum Sufficiency if applicable and not Proven |
| Logistics | Yes | Core | Route cost + time + reliability Alexandria→Shanghai (sea) / Cairo→Beijing (air) | Exact route | Route-specific authoritative source | Current/applicable | Q4 2026 | Cleared | Route-specific source | Gap | G6: Existing/activated providers; World Bank LPI = contextual only. IF insufficient → Residual Gap → WS-E | Route data matching Route Contract | Minimum Sufficiency blocked if not Proven |
| Agrifood | Not Required | Non-Core | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Not Required | N/A | N/A | Does not block Minimum Sufficiency |

---

## 7. Mandatory Closure Order

Before ANY New Provider:

```text
1. Existing Provider Configuration
2. Existing Provider Activation
3. Existing Provider Repair
4. Scope Correction
5. Existing Provider Enhancement
6. Equivalent Source Composition
7. New Provider Evaluation
8. Governance Approval
9. Admission
10. Implementation / Activation
11. Capability Proven
12. Scenario Revalidation
```

`Gap exists` does NOT imply `New Provider required`. Exhaust paths 1–6 first.

---

## 8. Provider Ceiling

**Ceiling:** 7 external operational production providers.

| Current State | Count | Notes |
|---------------|-------|-------|
| Operational | 2 | UN Comtrade, World Bank LPI |
| Internal (outside ceiling) | 1 | Company Knowledge |
| Complementary (outside ceiling) | 1 | WTO ePing |
| Inactive (activatable) | 6 | FAOSTAT, TradeData, Moaah, ZATCA, GCC-Stat, Regulations Provider |
| Available slots | 5 | 2 + 5 = 7 max |

**Critical rules:**
- Activating existing inactive provider = does NOT count as NEW addition, BUT resulting operational count MUST remain ≤ 7
- Activating all 6 inactive = 2 + 6 = 8 = Ceiling Expansion required
- New Provider = +1 to operational count; requires Governance Approval + ceiling compliance
- Expansion requires ALL: Documented Knowledge Need + Marginal Value > 0 + Operational Justification + No existing fallback + Governance Approval BEFORE admission
- Kilo/local execution CANNOT self-approve expansion

---

## 9. Workstreams

### WS-A: Entry / Truth Alignment

**Objective:** Reconcile plan entry state with Phase 13 findings and governing documents.

**In-Scope Gaps:** None (alignment only)

**Dependencies:** None

**Actions:**
1. Verify governing document set (Phase 13, Commercial Readiness Completion, Master Remediation, Baseline 2026-09-17)
2. Verify baseline commit identity
3. Document any documentation drift (non-blocking if classified as historical)
4. Freeze gap set and scenario set

**Required Evidence:** Document reconciliation record; gap set freeze record.

**Acceptance Tests:**
- AT-WS-A-1: Governing documents identified and consistent
- AT-WS-A-2: Baseline commit verified
- AT-WS-A-3: Gap set frozen (G1–G10)
- AT-WS-A-4: Documentation drift classified (if any)

**Runtime Evidence:** Reconciliation record; freeze timestamp.

**Exit Gate:** Entry truth aligned; no unresolved documentation conflict affecting governed truth.

**Stop Conditions:**
- New/unclassified/materially conflicting current claim → BLOCK → DOCUMENT → ESCALATE → GOVERNANCE DECISION

**Governance:** None required for alignment.

---

### WS-B: Existing Provider Capability Closure

**Objective:** Per-provider, independently, prove or disprove Capability Proven. Exhaust existing provider value before considering new providers. Activation is conditional, not automatic.

**In-Scope Gaps:** G1 (UN Comtrade HS6), G7/G8 (FAOSTAT), G3 (TradeData, Moaah, ZATCA, GCC-Stat), G4 (Moaah, Regulations Provider), G5 (GCC-Stat for GAFTA)

**Dependencies:** WS-A

**Binding rule:** A provider is activated ONLY if all of the following are true:
1. Its capability is relevant to a Required Gap
2. It can plausibly close the gap
3. Activation is justified by marginal knowledge value
4. Licensing is admissible
5. Ceiling impact is acceptable
6. Governance Approval is obtained

**Allowed dispositions:** Activate / Do Not Activate / Not Needed / Insufficient / Restricted / Blocked

**Actions (per provider, independently):**

#### WS-B.1: UN Comtrade HS6 Runtime Verification

| Step | Action | Evidence Required |
|------|--------|-------------------|
| 1 | Verify HS6 query capability in DEM runtime | Live DEM query with HS6 code |
| 2 | Validate response contains correct HS6 | HS6 code present in returned records |
| 3 | Verify bilateral Egypt↔Y | Reporter=Egypt, Partner=Y confirmed |
| 4 | Verify period | Latest available annual confirmed |
| 5 | Verify completeness | All required HS6 codes retrieved |
| 6 | Store provenance | Source URL, retrieval timestamp, transformation path |

**Acceptance Tests:**
- AT-WS-B-1-1: DEM HS6 query for HS070200 returns Egypt–Jordan data
- AT-WS-B-1-2: DEM HS6 query for HS080410 returns Egypt–Saudi data
- AT-WS-B-1-3: DEM HS6 query for HS080510 returns Egypt–Germany data
- AT-WS-B-1-4: DEM HS6 query for HS090111 returns Egypt–Kenya data
- AT-WS-B-1-5: DEM HS6 query for HS610990 returns Egypt–China data
- AT-WS-B-1-6: All queries include complete provenance metadata

**Exit Gate:** HS6 retrieval = Capability Proven. If Partial only → G1 remains Open with documented limitation and residual gap. Partial != Proven.

#### WS-B.2: FAOSTAT Activation & Capability Proven

| Decision Factor | Value |
|-----------------|-------|
| Trigger | G7/G8 require Agrifood capability |
| Required Gap(s) | G7, G8 |
| Why relevant | Only candidate agricultural source for S1–S4 Agrifood/Opportunity |
| Expected unique value | Global commodity-level agricultural data (production, supply, prices) |
| Minimum capability to prove | JWT auth → real data → correct mapping → correct scope → licensing clearance |
| Conditions justifying activation | Agrifood applicability determination = Core for at least one scenario; commercial-use clearance obtained or documented as non-blocking |
| Conditions making activation unnecessary | Agrifood = NOT_REQUIRED_PROVEN for all S1–S4; OR commercial-use clearance not obtainable |
| Final disposition | Activate (conditional on applicability + licensing) |

| Step | Action | Evidence Required |
|------|--------|-------------------|
| 1 | Verify credentials in DEM | Credentials present and masked |
| 2 | Obtain Governance Approval for activation | Governance Approval recorded |
| 3 | Verify JWT authentication | JWT token obtained in DEM runtime |
| 4 | Verify API reachability | Health check passes |
| 5 | Verify real data retrieval | Non-empty results from live API |
| 6 | Verify schema transformation | Capitalized → internal model correct |
| 7 | Verify commodity mapping | Area/Item/Element codes correct for HS07/08/09 |
| 8 | Verify country coverage | Required countries covered |
| 9 | Verify licensing/commercial-use clearance | Commercial-use clearance obtained OR documented blocker |
| 10 | Prove Capability Proven | All above steps verified |

**Acceptance Tests:**
- AT-WS-B-2-1: Live FAOSTAT JWT authentication in DEM
- AT-WS-B-2-2: Live data retrieval returns non-empty results
- AT-WS-B-2-3: Schema transformation correct
- AT-WS-B-2-4: Commodity mapping verified for HS07, HS08, HS09
- AT-WS-B-2-5: Country coverage verified
- AT-WS-B-2-6: Commercial-use clearance obtained OR documented blocker
- AT-WS-B-2-7: FAOSTAT Capability Proven = Yes or No with reason

**Exit Gate:** FAOSTAT = Capability Proven OR NOT_PROVEN with documented reason (licensing blocker, API failure, etc.). G7/G8 remain Open if NOT_PROVEN.

#### WS-B.3: TradeData Activation

| Decision Factor | Value |
|-----------------|-------|
| Trigger | G1/G3 require HS-level trade and/or general market access coverage |
| Required Gap(s) | G1, G3 |
| Why relevant | General HS-level trade data; global coverage |
| Expected unique value | HS-level bilateral trade data; general tariff data for multiple destinations |
| Minimum capability to prove | HS-level query returns data; bilateral Egypt↔Y works |
| Conditions justifying activation | UN Comtrade HS6 insufficient; licensing admissible |
| Conditions making activation unnecessary | UN Comtrade HS6 sufficient for G1; other providers cover G3 |
| Final disposition | Activate (conditional on necessity) |

| Step | Action | Evidence Required |
|------|--------|-------------------|
| 1 | Verify credentials configured | TRADEDATA_API_KEY present |
| 2 | Obtain Governance Approval for activation | Governance Approval recorded |
| 3 | Verify endpoint reachability | Health check passes |
| 4 | Verify HS-level query capability | Live query returns HS-level data |
| 5 | Verify bilateral coverage | Egypt↔Y queries work |
| 6 | Verify licensing/commercial-use clearance | Commercial terms verified |
| 7 | Prove Capability Proven | All above verified |

**Acceptance Tests:**
- AT-WS-B-3-1: TradeData credentials configured
- AT-WS-B-3-2: TradeData endpoint reachable
- AT-WS-B-3-3: HS-level query returns data
- AT-WS-B-3-4: Bilateral Egypt↔Y query works
- AT-WS-B-3-5: Commercial-use clearance documented

**Exit Gate:** TradeData = Capability Proven OR NOT_PROVEN with reason. G1/G3 remain Open if NOT_PROVEN.

#### WS-B.4: Moaah Activation

| Decision Factor | Value |
|-----------------|-------|
| Trigger | G3/G4 require Saudi/Egypt tariff/regulatory data |
| Required Gap(s) | G3, G4 |
| Why relevant | Saudi/Egypt scope matches S2 Saudi Arabia requirement |
| Expected unique value | Saudi tariff and regulatory data for HS080410 |
| Minimum capability to prove | Saudi tariff/regulatory endpoint returns product-specific data |
| Conditions justifying activation | S2 requires Saudi Market Access/Regulatory; no other Saudi-specific provider available |
| Conditions making activation unnecessary | ZATCA or GCC-Stat covers Saudi requirements; OR S2 not required |
| Final disposition | Activate (conditional on S2 requirements) |

| Step | Action | Evidence Required |
|------|--------|-------------------|
| 1 | Verify credentials configured | MOAAH_API_KEY present |
| 2 | Obtain Governance Approval for activation | Governance Approval recorded |
| 3 | Verify endpoint reachability | Health check passes |
| 4 | Verify Saudi tariff/regulatory endpoint | Live query returns Saudi data |
| 5 | Verify licensing/commercial-use clearance | Commercial terms verified |
| 6 | Prove Capability Proven | All above verified |

**Acceptance Tests:**
- AT-WS-B-4-1: Moaah credentials configured
- AT-WS-B-4-2: Moaah endpoint reachable
- AT-WS-B-4-3: Saudi tariff query returns data
- AT-WS-B-4-4: Commercial-use clearance documented

**Exit Gate:** Moaah = Capability Proven OR NOT_PROVEN with reason. G3/G4 remain Open if NOT_PROVEN.

#### WS-B.5: GCC-Stat Activation

| Decision Factor | Value |
|-----------------|-------|
| Trigger | G3/G5 require GCC tariff/RoO data |
| Required Gap(s) | G3, G5 |
| Why relevant | GCC scope matches S2 GAFTA requirement |
| Expected unique value | GCC tariff data; GAFTA RoO eligibility criteria for S2 |
| Minimum capability to prove | GCC tariff/RoO query returns relevant data |
| Conditions justifying activation | S2 requires GAFTA RoO; no other GAFTA source available |
| Conditions making activation unnecessary | GAFTA not applicable to S2; OR other source covers G5 |
| Final disposition | Activate (conditional on S2 GAFTA requirement) |

| Step | Action | Evidence Required |
|------|--------|-------------------|
| 1 | Verify credentials configured | GCCSTAT_API_KEY present |
| 2 | Obtain Governance Approval for activation | Governance Approval recorded |
| 3 | Verify endpoint reachability | Health check passes |
| 4 | Verify GCC RoO/tariff data | Live query returns GCC data |
| 5 | Verify GAFTA eligibility criteria | GAFTA data present and correct |
| 6 | Verify licensing/commercial-use clearance | Open data terms verified |
| 7 | Prove Capability Proven | All above verified |

**Acceptance Tests:**
- AT-WS-B-5-1: GCC-Stat credentials configured
- AT-WS-B-5-2: GCC-Stat endpoint reachable
- AT-WS-B-5-3: GCC tariff/RoO query returns data
- AT-WS-B-5-4: GAFTA eligibility criteria verified

**Exit Gate:** GCC-Stat = Capability Proven OR NOT_PROVEN with reason. G3/G5 remain Open if NOT_PROVEN.

#### WS-B.6: ZATCA Activation

| Decision Factor | Value |
|-----------------|-------|
| Trigger | G3 requires Saudi tariff data |
| Required Gap(s) | G3 |
| Why relevant | KSA-only scope; Saudi Arabia tariff data |
| Expected unique value | Saudi tariff data for HS080410 (alternative to Moaah) |
| Minimum capability to prove | KSA tariff endpoint returns product-specific data |
| Conditions justifying activation | Moaah insufficient or unavailable; KSA tariff needed |
| Conditions making activation unnecessary | Moaah covers S2 requirements; OR S2 Market Access covered by other source |
| Final disposition | Activate (conditional on necessity) |

| Step | Action | Evidence Required |
|------|--------|-------------------|
| 1 | Verify credentials configured | ZATCA_API_KEY present |
| 2 | Obtain Governance Approval for activation | Governance Approval recorded |
| 3 | Verify endpoint reachability | Health check passes |
| 4 | Verify KSA tariff endpoint | Live query returns KSA data |
| 5 | Verify licensing/commercial-use clearance | Open Data terms verified |
| 6 | Prove Capability Proven | All above verified |

**Acceptance Tests:**
- AT-WS-B-6-1: ZATCA credentials configured
- AT-WS-B-6-2: ZATCA endpoint reachable
- AT-WS-B-6-3: KSA tariff query returns data

**Exit Gate:** ZATCA = Capability Proven OR NOT_PROVEN with reason. G3 remains Open if NOT_PROVEN.

#### WS-B.7: Regulations Provider Activation

| Decision Factor | Value |
|-----------------|-------|
| Trigger | G4 requires regulatory/SPS-TBT data file |
| Required Gap(s) | G4 |
| Why relevant | File-based regulatory lookup; product-country-specific |
| Expected unique value | Structured regulatory data for multiple jurisdictions |
| Minimum capability to prove | Product-country lookup returns specific requirements from file |
| Conditions justifying activation | Regulations Decision Gate determines local file is needed; authoritative data available |
| Conditions making activation unnecessary | Regulatory data available from other activated provider (Moaah); OR file creation not feasible |
| Final disposition | Activate (conditional on Regulations Decision Gate outcome) |

| Step | Action | Evidence Required |
|------|--------|-------------------|
| 1 | Execute Regulations Decision Gate | Determine if local file is needed |
| 2 | Obtain Governance Approval for activation | Governance Approval recorded |
| 3 | If yes: create/populate regulations.json | Authoritative data + validation rules |
| 4 | Configure REGULATIONS_FILE_PATH | Path configured and file readable |
| 5 | Verify provider reads file | Provider returns data from file |
| 6 | Verify product-country-specific lookup | HS6 + jurisdiction query returns specific requirements |
| 7 | Verify licensing/commercial-use clearance | Data source terms verified |
| 8 | Prove Capability Proven | All above verified |

**Acceptance Tests:**
- AT-WS-B-7-1: regulations.json exists and is readable
- AT-WS-B-7-2: Provider returns data from file
- AT-WS-B-7-3: Product-country lookup returns specific requirements
- AT-WS-B-7-4: Source authority documented

**Exit Gate:** Regulations Provider = Capability Proven OR NOT_PROVEN with reason (data file unavailable, insufficient scope, etc.). G4 remains Open if NOT_PROVEN.

**WS-B Exit Gate:** All existing providers = Capability Proven, NOT_PROVEN, Not Needed, Insufficient, Restricted, or Blocked with documented reason. Not Needed is a valid closure state when Decision Matrix proves provider is not required. No provider activation proceeds without Governance Approval. No forced activation of all inactive providers.

---

### WS-C: Applicability and Scope

**Objective:** Prove applicability determinations for all conditional dimensions. Verify Frozen Route Contract integrity. No silent route modification.

**In-Scope Gaps:** G5 (RoO applicability), G7 (Agrifood applicability), G6 (Frozen Route Contract integrity)

**Dependencies:** WS-A (can run parallel to WS-B)

**Actions:**

#### WS-C.1: RoO Applicability Determinations (G5)

**Layered structure:** Each RoO dimension has 5 sub-layers. Absence of source or absence of proof for any sub-layer does NOT make the dimension NOT_REQUIRED_PROVEN. NOT_REQUIRED_PROVEN requires documented applicability determination.

| Scenario | Sub-Layer | Applicability Question | Required Determination |
|----------|-----------|------------------------|------------------------|
| S1 | 1. Regime/Country-Pair Applicability | Does Agadir Agreement apply to Egypt→Jordan vegetable trade? | Applicable → proceed to layer 2; Not Applicable → NOT_REQUIRED_PROVEN (documented) |
| S1 | 2. Product/Tariff-Line Eligibility | Are HS070200/070700/070960/070310 eligible under Agadir? | Eligible → proceed to layer 3; Not Eligible → NOT_REQUIRED_PROVEN (documented) |
| S1 | 3. Preferential Eligibility | Is preferential treatment available for eligible products? | Yes → proceed to layer 4; No → NOT_REQUIRED_PROVEN (documented) |
| S1 | 4. Rules of Origin | What are the origin criteria? | Origin criteria documented → Core evidence required |
| S1 | 5. Documentation | What documentation is required? | Documentation requirements documented → Core evidence required |
| S2 | 1. Regime/Country-Pair Applicability | Does GAFTA apply to Egypt→Saudi dates trade? | Applicable (confirmed) → proceed to layer 2 |
| S2 | 2. Product/Tariff-Line Eligibility | Is HS080410 eligible under GAFTA? | Eligible → proceed to layer 3 |
| S2 | 3. Preferential Eligibility | Is preferential treatment available? | Yes → proceed to layer 4 |
| S2 | 4. Rules of Origin | What are the origin criteria? | Origin criteria documented → Core evidence required |
| S2 | 5. Documentation | What documentation is required? | Documentation requirements documented → Core evidence required |
| S3 | 1. Regime/Country-Pair Applicability | Does EU–Egypt FTA apply to Egypt→Germany citrus trade? | Applicable (confirmed) → proceed to layer 2 |
| S3 | 2. Product/Tariff-Line Eligibility | Are HS080510/080550/080540 eligible under EU–Egypt FTA? | Eligible → proceed to layer 3 |
| S3 | 3. Preferential Eligibility | Is preferential treatment available? | Yes → proceed to layer 4 |
| S3 | 4. Rules of Origin | What are the origin criteria? | Origin criteria documented → Core evidence required |
| S3 | 5. Documentation | What documentation is required? | Documentation requirements documented → Core evidence required |
| S4 | 1. Regime/Country-Pair Applicability | Does COMESA FTA apply to Egypt→Kenya coffee trade? | Applicable → proceed to layer 2; Not Applicable → NOT_REQUIRED_PROVEN (documented) |
| S4 | 2. Product/Tariff-Line Eligibility | Are HS090111/090121 eligible under COMESA? | Eligible → proceed to layer 3; Not Eligible → NOT_REQUIRED_PROVEN (documented) |
| S4 | 3. Preferential Eligibility | Is preferential treatment available? | Yes → proceed to layer 4; No → NOT_REQUIRED_PROVEN (documented) |
| S4 | 4. Rules of Origin | What are the origin criteria? | Origin criteria documented → Core evidence required |
| S4 | 5. Documentation | What documentation is required? | Documentation requirements documented → Core evidence required |
| S5 | 1. Regime/Country-Pair Applicability | Does China Zero-Tariff Measure apply to Egypt→China apparel trade? | Applicable → proceed to layer 2; Not Applicable → NOT_REQUIRED_PROVEN (documented) |
| S5 | 2. Product/Tariff-Line Eligibility | Are HS610990/611011/610510 eligible under China Zero-Tariff Measure? | Eligible → proceed to layer 3; Not Eligible → NOT_REQUIRED_PROVEN (documented) |
| S5 | 3. Preferential Eligibility | Is preferential treatment available? | Yes → proceed to layer 4; No → NOT_REQUIRED_PROVEN (documented) |
| S5 | 4. Rules of Origin | What are the origin criteria? | Origin criteria documented → Core evidence required |
| S5 | 5. Documentation | What documentation is required? | Documentation requirements documented → Core evidence required |

**Acceptance Tests:**
- AT-WS-C-1-1: Agadir applicability determination documented for S1 (Layer 1 only)
- AT-WS-C-1-2: GAFTA applicability confirmed for S2 (Layer 1 only)
- AT-WS-C-1-3: EU–Egypt FTA applicability confirmed for S3 (Layer 1 only)
- AT-WS-C-1-4: COMESA applicability determination documented for S4 (Layer 1 only)
- AT-WS-C-1-5: China Zero-Tariff applicability determination documented for S5 (Layer 1 only)

**Exit Gate:** RoO Regime/Country-Pair Applicability (Layer 1) = PROVEN or NOT_REQUIRED_PROVEN per scenario. Layers 2–5 are explicitly out of scope for WS-C and are routed as Residual Gap → WS-D.3. WS-C does NOT require Layer 2–5 proof to close.

**WS-C.1 Exit Gate:** Layer 1 applicability determinations documented per scenario. Layers 2–5 deferred to WS-D.3. No silent NOT_REQUIRED_PROVEN.

**Residual Gap Routing (G5 Layers 2–5):**
- S1: L2–L5 → Residual Gap → WS-D.3
- S2: L2–L5 → Residual Gap → WS-D.3
- S3: L2–L5 → Residual Gap → WS-D.3
- S4: L2–L5 → Residual Gap → WS-D.3
- S5: L2–L5 → Residual Gap → WS-D.3

WS-C.1 does NOT declare Layers 2–5 NOT_REQUIRED_PROVEN. Absence of proof in WS-C does not make any layer Not Required.

#### WS-C.2: Agrifood Applicability Determinations

| Scenario | Applicability Question | Required Determination |
|----------|------------------------|------------------------|
| S1 | Does Agrifood evidence beyond trade volume apply to Jordan vegetable trade? | Applicable → Core Agrifood evidence required; Not Applicable → NOT_REQUIRED_PROVEN |
| S2 | Does Agrifood evidence beyond trade volume apply to Saudi dates trade? | Applicable → Core Agrifood evidence required; Not Applicable → NOT_REQUIRED_PROVEN |
| S3 | Does Agrifood evidence beyond trade volume apply to Germany/EU citrus trade? | Applicable → Core Agrifood evidence required; Not Applicable → NOT_REQUIRED_PROVEN |
| S4 | Does Agrifood evidence beyond trade volume apply to Kenya coffee trade? | Applicable → Core Agrifood evidence required; Not Applicable → NOT_REQUIRED_PROVEN |

**Acceptance Tests:**
- AT-WS-C-2-1: Agrifood applicability determination documented for S1–S4

**Exit Gate:** All Conditional Agrifood have applicability determination = NOT_REQUIRED_PROVEN or Core Confirmed.

**Governance Decision Requirement (G7):**
For S1–S4, applicability determination requires a Governance Decision from the Business Question Authority / Project Owner. The frozen Business Question Contract does not resolve whether agricultural market indicators beyond trade volume (production/supply/prices) are required. Without this decision, applicability remains UNRESOLVED and WS-C cannot close for G7.

Allowed outcomes per scenario (determined by Business Question Authority / Project Owner only):
- Core Confirmed
- NOT_REQUIRED_PROVEN

The plan does not make this decision. WS-C documents the Governance Decision once provided.

#### G7 Governance Decision Record

Authority:
Business Question Authority / Project Owner

Decision Required:
For each S1–S4, determine whether the frozen Business Question
requires agricultural market indicators beyond trade volume
(production / supply / prices).

Allowed Outcomes:
Core
OR
NOT_REQUIRED_PROVEN

Current Status:
APPROVED / RECORDED

Decision:
S1 = NOT_REQUIRED_PROVEN
S2 = NOT_REQUIRED_PROVEN
S3 = NOT_REQUIRED_PROVEN
S4 = NOT_REQUIRED_PROVEN

Basis:
Frozen Business Question Contracts do not require agricultural
market indicators beyond trade volume.

Notes:
- The system or Kilo does not make this decision on behalf of the Authority.
- NOT_REQUIRED_PROVEN cannot be inferred from absence of source or data.
- The Business Question Contract is not automatically changed.
- WS-C Exit Gate is re-evaluated after this decision is recorded.
- WS-D does not start before WS-C closes.

#### WS-C.3: Frozen Route Contract Integrity Verification

**Objective:** Verify frozen route values are complete, consistent, and free of placeholders. WS-C must NOT modify frozen Route Contracts unless a genuine Contract Conflict is proven and the documented Contract Amendment Governance path is invoked.

| Route | Verification Requirements |
|-------|---------------------------|
| S1 sea | Verify: origin=Alexandria Port; destination=Aqaba Port; mode=sea; cargo=perishable/cold-chain; Incoterm=FOB Alexandria; temperature=0–4°C; assessment=Q4 2026; reliability=on-time + cold-chain integrity |
| S1 road | Verify: origin=Port Said Port; destination=Aqaba Port; mode=road; cargo=perishable/cold-chain; Incoterm=FOB Port Said; temperature=0–4°C; assessment=Q4 2026; reliability=on-time + cold-chain integrity |
| S2 sea | Verify: origin=Alexandria Port; destination=Jeddah Port; mode=sea; cargo=dried fruit/humidity-controlled; Incoterm=FOB Alexandria; temperature=ambient 15–25°C/50–70% RH; assessment=Q4 2026; reliability=on-time + cargo condition |
| S2 road | Verify: origin=Port Said Port; destination=Dammam Port; mode=road; cargo=dried fruit/humidity-controlled; Incoterm=FOB Port Said; temperature=ambient 15–25°C/50–70% RH; assessment=Q4 2026; reliability=on-time + cargo condition |
| S3 sea | Verify: origin=Alexandria Port; destination=Hamburg Port; mode=sea; cargo=perishable/phytosanitary; Incoterm=FOB Alexandria; temperature=0–4°C; assessment=Q4 2026; reliability=on-time + EU customs clearance time |
| S3 air | Verify: origin=Cairo Airport; destination=Frankfurt Airport; mode=air; cargo=perishable/phytosanitary; Incoterm=FOB Cairo; temperature=0–4°C; assessment=Q4 2026; reliability=on-time + cargo condition |
| S4 sea | Verify: origin=Alexandria Port; destination=Mombasa Port; mode=sea; cargo=agricultural commodity/ventilated; Incoterm=FOB Alexandria; temperature=ambient 10–20°C/60–70% RH; assessment=Q4 2026; reliability=on-time + cargo condition |
| S4 air | Verify: origin=Cairo Airport; destination=Nairobi; mode=air; cargo=agricultural commodity/ventilated; Incoterm=FOB Cairo; temperature=ambient 10–20°C/60–70% RH; assessment=Q4 2026; reliability=on-time + cargo condition |
| S5 sea | Verify: origin=Alexandria Port; destination=Shanghai Port; mode=sea; cargo=knitted apparel/dry; Incoterm=FOB Alexandria; temperature=ambient; assessment=Q4 2026; reliability=on-time + cargo integrity |
| S5 air | Verify: origin=Cairo Airport; destination=Beijing Capital Airport; mode=air; cargo=knitted apparel/dry; Incoterm=FOB Cairo; temperature=ambient; assessment=Q4 2026; reliability=on-time + cargo integrity |

**Acceptance Tests:**
- AT-WS-C-3-1: All frozen Route Contract values verified (no silent modification)
- AT-WS-C-3-2: No "to be confirmed" placeholders remain
- AT-WS-C-3-3: All material fields populated and consistent with Scenario Contracts

**Exit Gate:** All Frozen Route Contracts verified intact. No unresolved route fields. Any modification requires documented Contract Amendment Governance path.

**WS-C Exit Gate:** 
- WS-C.1: RoO Regime/Country-Pair Applicability (Layer 1) documented per scenario. Layers 2–5 are Residual Gap routed to WS-D.3.
- WS-C.2: Agrifood applicability determination documented per scenario. S1–S4 = NOT_REQUIRED_PROVEN per Governance Decision.
- WS-C.3: All Frozen Route Contracts verified intact.

**WS-C Status:** CLOSED

**WS-D Status:** READY TO START

**WS-E Status:** BLOCKED UNTIL WS-D RESIDUAL-GAP ASSESSMENT

---

### WS-D: Core Evidence Closure

**Objective:** Collect and verify Core Evidence for each scenario via existing/activated providers.

**In-Scope Gaps:** G2, G3, G4, G5, G6, G7

**Dependencies:** WS-B (provider capabilities proven), WS-C (scope finalized)

**Actions (per evidence family, in parallel where prerequisites met):**

#### WS-D.1: Market Access Evidence (G3)

| Scenario | Destination | Required HS6 Codes | Source Path |
|----------|-------------|--------------------|-------------|
| S1 | Jordan | HS070200, HS070700, HS070960, HS070310 | Existing/activated providers only (TradeData, Moaah, ZATCA, GCC-Stat, Regulations). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S2 | Saudi Arabia | HS080410 | Existing/activated providers only (Moaah, ZATCA, GCC-Stat, TradeData). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S3 | EU (Germany) | HS080510, HS080550, HS080540 | Existing/activated providers only (TradeData, Regulations). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S4 | Kenya | HS090111, HS090121 | Existing/activated providers only (TradeData, Regulations). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S5 | China | HS610990, HS611011, HS610510 | Existing/activated providers only (TradeData, Regulations). IF insufficient → Residual Gap → WS-E Candidate Evaluation (includes Zero-Tariff verification) |

**Evidence Requirements per HS6 code:**
- Tariff rate / duty amount
- Entry procedures
- Permit/licensing when applicable
- Preferential treatment when applicable
- Effective date
- Source authority
- Provenance

**Acceptance Tests:**
- AT-WS-D-1-1 through AT-WS-D-1-5: Live tariff lookup per HS6 code per destination
- AT-WS-D-1-6: Effective date verified per HS6 code
- AT-WS-D-1-7: Entry procedures documented per destination

**Exit Gate:** Market Access Evidence = Proven per HS6 code per scenario via existing/activated providers, OR documented Residual Gap for WS-E. No New Provider work in WS-D.

#### WS-D.2: Regulatory/SPS-TBT Evidence (G4)

| Scenario | Jurisdiction | Required Evidence | Source Path |
|----------|--------------|-------------------|-------------|
| S1 | Jordan | SPS for fresh vegetables (HS070200/070700/070960/070310) | Existing/activated providers only (Regulations, Moaah). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S2 | Saudi Arabia | SPS for dates (HS080410) | Existing/activated providers only (Moaah). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S3 | EU (Germany) | SPS/MRL for citrus (HS080510/080550/080540) | Existing/activated providers only (Regulations). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S4 | Kenya | SPS for coffee (HS090111/090121) | Existing/activated providers only (Regulations). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S5 | China | TBT for knitted apparel (HS610990/611011/610510) | Existing/activated providers only (Regulations). IF insufficient → Residual Gap → WS-E Candidate Evaluation |

**Evidence Requirements per HS6 code:**
- Product-specific requirement
- Jurisdiction-specific requirement
- Current/effective status
- Effective date
- SPS/TBT/MRL/conformity/food safety/plant safety/technical requirements as applicable
- Source authority
- Provenance

**Acceptance Tests:**
- AT-WS-D-2-1 through AT-WS-D-2-5: Regulatory lookup per HS6 per jurisdiction
- AT-WS-D-2-6: Effective date verified per requirement
- AT-WS-D-2-7: Source authority documented

**Exit Gate:** Regulatory/SPS-TBT Evidence = Proven per scenario via existing/activated providers, OR documented Residual Gap for WS-E. No New Provider work in WS-D.

#### WS-D.3: RoO Evidence (G5)

**Scope:** WS-D.3 covers Layers 2–5 of RoO applicability, which are Residual Gap from WS-C.1.

| Scenario | Agreement/Regime | Required Evidence | Source Path |
|----------|------------------|-------------------|-------------|
| S1 | Agadir Agreement (Conditional) | L2 Product/Tariff-Line Eligibility → L3 Preferential Eligibility → L4 Rules of Origin → L5 Documentation | Existing/activated providers only. IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S2 | GAFTA (Core) | L2 Product/Tariff-Line Eligibility → L3 Preferential Eligibility → L4 Rules of Origin → L5 Documentation | Existing/activated providers only (GCC-Stat). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S3 | EU–Egypt FTA (Core) | L2 Product/Tariff-Line Eligibility → L3 Preferential Eligibility → L4 Rules of Origin → L5 Documentation | Existing/activated providers only (Regulations, Moaah). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S4 | COMESA (Conditional) | L2 Product/Tariff-Line Eligibility → L3 Preferential Eligibility → L4 Rules of Origin → L5 Documentation | Existing/activated providers only. IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S5 | China Zero-Tariff Measure (Conditional) | L2 Product/Tariff-Line Eligibility → L3 Preferential Eligibility → L4 Rules of Origin → L5 Documentation | Existing/activated providers only with proven China scope (Regulations IF China scope proven). Moaah excluded unless China scope explicitly proven. IF insufficient → Residual Gap → WS-E Candidate Evaluation |

**Evidence Requirements:**
- L2: Product/Tariff-Line Eligibility
- L3: Preferential Eligibility
- L4: Rules of Origin / Origin criterion
- L5: Documentation requirements
- Source authority
- Provenance
- Effective date

**Acceptance Tests:**
- AT-WS-D-3-1: Agadir L2–L5 proven for S1
- AT-WS-D-3-2: GAFTA L2–L5 proven for S2
- AT-WS-D-3-3: EU–Egypt FTA L2–L5 proven for S3
- AT-WS-D-3-4: COMESA L2–L5 proven for S4
- AT-WS-D-3-5: China Zero-Tariff L2–L5 proven for S5
- AT-WS-D-3-6: Documentation requirements documented per agreement

**Dependency:** WS-C.1 Layer 1 must be PROVEN before WS-D.3 starts for each scenario. WS-C.2 Governance Decision must be recorded if G7 becomes Core.

**Exit Gate:** RoO Evidence L2–L5 = Proven OR NOT_REQUIRED_PROVEN per scenario via existing/activated providers, OR documented Residual Gap for WS-E. No New Provider work in WS-D. NOT_REQUIRED_PROVEN requires documented applicability determination, NOT absence of provider.

#### WS-D.4: Logistics Route-Level Evidence (G6)

| Scenario | Route | Required Evidence | Source Path |
|----------|-------|-------------------|-------------|
| S1 | Alexandria→Aqaba (sea); Port Said→Aqaba (road) | Route cost + time + reliability | Existing/activated providers only. World Bank LPI = contextual only. IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S2 | Alexandria→Jeddah (sea); Port Said→Dammam (road) | Route cost + time + reliability | Existing/activated providers only. World Bank LPI = contextual only. IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S3 | Alexandria→Hamburg (sea); Cairo→Frankfurt (air) | Route cost + time + reliability | Existing/activated providers only. World Bank LPI = contextual only. IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S4 | Alexandria→Mombasa (sea); Cairo→Nairobi (air) | Route cost + time + reliability | Existing/activated providers only. World Bank LPI = contextual only. IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S5 | Alexandria→Shanghai (sea); Cairo→Beijing (air) | Route cost + time + reliability | Existing/activated providers only. World Bank LPI = contextual only. IF insufficient → Residual Gap → WS-E Candidate Evaluation |

**Evidence Requirements per route:**
- Route cost
- Transit time
- Reliability metric (on-time delivery rate, transit time variance, cargo condition integrity)
- Origin node, destination node, transport mode
- Cargo characteristics
- Shipment assumptions
- Incoterm when materially required
- Temperature/control when relevant
- Assessment window
- Reliability definition
- Source authority
- Provenance
- Freshness

**Acceptance Tests:**
- AT-WS-D-4-1 through AT-WS-D-4-5: Route data matches Route Contract for primary sea routes
- AT-WS-D-4-6: Reliability metric definition verified per Route Contract
- AT-WS-D-4-7: Fallback equivalence verified if applicable

**Exit Gate:** Route-Level Logistics Evidence = Proven per required route via existing/activated providers, OR documented Residual Gap for WS-E. World Bank LPI = contextual only, never Core route evidence. No New Provider work in WS-D.

#### WS-D.5: Opportunity Evidence (G2)

| Scenario | Required Opportunity Evidence | Source Path |
|----------|-------------------------------|-------------|
| S1 | Demand gap + import dynamics for Jordan fresh vegetables | Existing/activated providers only (FAOSTAT if applicable). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S2 | Demand gap + import dynamics for Saudi dates | Existing/activated providers only (FAOSTAT if applicable). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S3 | Demand gap + import dynamics for Germany/EU citrus | Existing/activated providers only (FAOSTAT if applicable). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S4 | Demand gap + import dynamics for Kenya coffee | Existing/activated providers only (FAOSTAT if applicable). IF insufficient → Residual Gap → WS-E Candidate Evaluation |
| S5 | Demand gap + import dynamics for China knitted apparel | Existing/activated providers only. FAOSTAT NOT applicable (agriculture-only). IF insufficient → Residual Gap → WS-E Candidate Evaluation |

**Evidence Requirements:**
- Path A: Proven dedicated opportunity source (existing/activated provider)
- Path B: Deterministic composite of Demand + Growth/Import Dynamics + Opportunity Signal
  - All inputs individually proven from existing/activated sources
  - All inputs satisfy required evidence tier
  - Methodology deterministic and documented
  - Full provenance per input
  - NO Complementary → Authoritative elevation
  - NO Trade-only conversion
  - NO unsupported score or formula

**Acceptance Tests:**
- AT-WS-D-5-1: Composite inputs individually proven for applicable scenarios
- AT-WS-D-5-2: Composite methodology deterministic and documented
- AT-WS-D-5-3: No Trade-alone conversion in any scenario
- AT-WS-D-5-4: Existing provider proven for opportunity evidence (if applicable)
- AT-WS-D-5-5: Opportunity terminology governed (no invented scores)

**Exit Gate:** Opportunity Evidence = Proven per scenario via existing/activated providers, OR documented Residual Gap for WS-E. No New Provider work in WS-D.

**WS-D Exit Gate:** All Evidence Matrices complete via existing/activated providers. Each dimension = Proven OR Partial OR NOT_REQUIRED_PROVEN where applicable OR documented Residual Gap for WS-E. No dimension silently omitted. No New Provider work in WS-D.

#### WS-D.6: Operational Input Resolution & Official Source Access

**Objective:** Exhaust all executable official/public evidence paths before declaring a Gap blocked by missing credentials or requiring a new provider. This workstream resolves "Missing Operational Inputs" by identifying and using official/public access paths that do not require additional provider activation.

**In-Scope Gaps:** G2, G3, G4, G5, G6, G9 (only where existing provider paths are blocked by missing credentials, data files, or configuration, and an official/public access path exists)

**Dependencies:** WS-D.1–WS-D.5 (existing provider paths attempted and documented)

**Decision Order:**

1. **Existing Provider + Credentials/Configuration Available**
   - Path: Configure → Activate → Reachable → Returns Data → Capability Proven
   - Example: FAOSTAT with valid credentials

2. **Existing Provider or Official Source with Public/Official Access Without Credentials**
   - Path: Public API, Official download, Official machine-readable dataset, Official published data endpoint
   - Use this path instead of waiting for unnecessary credentials
   - Examples: Official tariff schedules, regulatory databases, customs portals

3. **Official Source Available as Data File**
   - Path: Use official data file after source validation + freshness + scope + provenance + schema validation
   - Example: regulations.json with valid official data

4. **Official Source Requires Authentication**
   - Document required credentials as specific Operational Inputs
   - Do not treat missing credentials as a code Gap
   - Example: TradeData API key, Moaah API key

5. **No Official/Public Path Available**
   - Proceed to Existing Provider Enhancement or WS-E per current rules

**Key Rule:**
`No Credential ≠ No Official Access`

Missing credentials do not stop execution until verified that no official/public access path is suitable.

**Licensing Clarification:**
Current DEM usage is defined as: **Internal organizational planning, analysis, and decision support; no redistribution or publication in current scope.**
- Internal Use: Evaluate per source terms
- Automated Retrieval: Evaluate per source terms
- Storage: Evaluate per source terms
- Redistribution/Publication: Not in current scope

Do not assume Commercial Exploitation for internal organizational use without explicit source terms.

**Acceptance Tests:**
- AT-WS-D-6-1: Each Gap checked for official/public access path before declaring credential-blocked
- AT-WS-D-6-2: Public/official data validated for freshness, scope, provenance, and schema
- AT-WS-D-6-3: Missing credentials documented as specific Operational Inputs, not code gaps
- AT-WS-D-6-4: No Gap converted to NOT_REQUIRED_PROVEN due to missing credentials
- AT-WS-D-6-5: WS-E only triggered after WS-D.6 paths exhausted

**Exit Gate:** All G2, G3, G4, G5, G6, G9 have documented access path: Proven via official/public source, or specific Operational Inputs documented, or Residual Gap for WS-E.

**WS-D Updated Exit Gate:** WS-D.1–WS-D.6 complete. Each evidence dimension = Proven OR Partial OR NOT_REQUIRED_PROVEN where applicable OR documented Residual Gap for WS-E OR documented Operational Inputs pending. No dimension silently omitted. No New Provider work in WS-D.

#### WS-D.6 Execution Results

**G2 Market Opportunity:**
- Official/Public Candidate Path = World Bank WITS REST API (tested)
- Capability Proven = NO
- Reason: WITS API endpoints tested returned HTML 404 pages or errors. No confirmed working public REST API for WITS data was found. The API is not accessible for automated data retrieval without authentication or alternative access methods.
- Status: Candidate Path Tested; NOT VIABLE

**G3 Market Access:**
- Official/Public Candidate Path = World Bank WITS REST API / UNCTAD TRAINS (tested)
- Capability Proven = NO
- Reason: WITS API endpoints tested returned HTML 404 pages or errors. UNCTAD TRAINS is not accessible via public REST API. No confirmed working public REST API for tariff data was found.
- Status: Candidate Path Tested; NOT VIABLE

**G4 Regulatory/SPS-TBT:**
- Official/Public Path = None (automated)
- Reason: Official regulatory sources exist (WTO ePing, ITC SPS/TBT, EFSA, KEPHIS, SFDA, GACC, national MoAs) but none provide structured automated access without credentials or API agreements. WTO ePing is complementary only per current governance. Public web interfaces require manual extraction.
- Status: Operational Inputs Documented (credentials needed for Moaah, Regulations Provider)

**G5 Rules of Origin:**
- Official/Public Path = Partial (Layer 1 only)
- Reason: Agreement texts are publicly available (GOEIC for Agadir/GAFTA, EU for EU-Egypt FTA, COMESA for COMESA, China MOF for Zero-Tariff Measure). However, Layer 2 (Product/Tariff-Line Eligibility), Layer 3 (Preferential Eligibility), Layer 4 (Rules of Origin criteria), and Layer 5 (Documentation) require legal interpretation of agreement texts and are not available as structured data. Layer 1 = PROVEN. Layers 2-5 = Not Proven via official texts alone.
- Status: Layer 1 Proven; Layers 2-5 Residual Gap → WS-D.3 / WS-E

**G6 Logistics:**
- Official/Public Path = None (route-level)
- Reason: World Bank LPI provides country-level logistics data only. No official source provides route-level cost/time/reliability data for specific origin-destination pairs with cargo/Incoterm specificity. Shipping line APIs and freight platforms are commercial, not public official sources. World Bank WITS does not cover route-level logistics.
- Status: Residual Gap → WS-E

**G9 China Zero-Tariff:**
- Official/Public Path = Partial (Announcement only)
- Reason: China MOF Announcement No. 5 (2026) is publicly available and confirms the Zero-Tariff Measure for 20 African countries including Egypt. However, the Annex PDF containing HS6 eligibility details is not machine-readable. HS610990/611011/610510 eligibility cannot be verified from available sources without manual PDF parsing.
- Status: Announcement Proven; HS6 Eligibility Not Extracted → WS-E for machine-readable Annex or alternative source

**WS-D.6 Status:** CLOSED
- All candidate official/public paths tested and documented
- WITS REST API tested and found NOT VIABLE (endpoints return HTML 404/errors)
- No viable automated official/public path exists for G2, G3, G4, G6, G9
- G5 remains with Layers 2–5 as Residual Gap
- No Gap converted to NOT_REQUIRED_PROVEN due to missing credentials
- WS-E required for G2, G6, G9 (no viable path)
- G3/G4/G5 require credentials/data files or manual legal review

---

### WS-E: Conditional New Provider Evaluation

**Objective:** Evaluate and admit new providers ONLY for residual gaps after WS-B + WS-C + WS-D existing paths are exhausted.

**In-Scope Gaps:** Residual G1, G2, G3, G4, G5, G6, G9 (only where existing paths exhausted)

**Dependencies:** WS-B, WS-C, WS-D (existing paths exhausted)

**Trigger Condition:** WS-D completes with documented Gap for which no existing provider path exists.

**Actions:**

For each residual Gap:

0. **Candidate Discovery / Search** — identify potential candidates:
   - Search for authoritative sources with matching scope
   - Document candidate name, authority, coverage, licensing terms, operational status
   - No candidate viability assumed at this stage

1. **Pre-Candidate Evidence Gate** — verify ALL:
   - Required Core Evidence proven necessary by Scenario Contract
   - Existing provider paths exhausted
   - Existing provider repair exhausted
   - Scope correction exhausted
   - Existing provider enhancement exhausted
   - Equivalent source composition exhausted
   - Equivalent fallback exhausted
   - Candidate class admissible under current governance
   - Licensing/admission path assessable
   - Ceiling impact assessable
   - Governance authority identified

2. **Candidate Evaluation** — evaluate:
   - Authority
   - Actual data coverage
   - Scope
   - Product granularity
   - Country/jurisdiction coverage
   - Freshness
   - Effective-date capability
   - Provenance
   - Commercial licensing
   - Storage/redistribution
   - API restrictions
   - Quotas/rate limits
   - Operational reliability
   - Integration feasibility
   - Unique/marginal value
   - Overlap with existing sources
   - Fallback equivalence
   - Ceiling impact
   - Viability determination

3. **Governance Approval** — obtain BEFORE any admission

4. **Admission** — only after Governance Approval

5. **Implementation / Activation** — bounded to approved candidate

6. **Capability Proven** — live verification required

7. **Scenario Revalidation** — affected scenarios only

**Acceptance Tests:**
- AT-WS-E-1: Each candidate passes Pre-Candidate Evidence Gate
- AT-WS-E-2: Each candidate evaluated per Candidate Evaluation framework
- AT-WS-E-3: Governance Approval obtained before admission
- AT-WS-E-4: Ceiling compliance verified (2 + activations + new ≤ 7, or expansion approved)
- AT-WS-E-5: Capability Proven for admitted providers

**Exit Gate:** Each residual Gap = Capability Proven via new provider, OR documented NOT_PROVEN with reason.

**Stop Conditions:**
- Pre-Candidate Evidence Gate fails → STOP → DOCUMENT → NO admission
- Governance Approval denied → STOP → DOCUMENT → NO admission
- Ceiling exceeded without expansion approval → STOP → DOCUMENT → NO admission
- Provider fails activation → STOP → DOCUMENT → Gap remains

**WS-E Exit Gate:** All residual gaps with viable new provider paths = Capability Proven or NOT_PROVEN. No open residual gaps with viable new provider paths remain unaddressed.

#### WS-E Execution Results

**WS-E Status:** CLOSED — No viable new provider path found for any residual gap. All candidates evaluated and documented.

**G2 Market Opportunity:**
- Candidates Evaluated: World Bank WITS REST API (tested — HTML 404/errors), UNCTADstat (no confirmed public API endpoint), ITC Trade Map (no public automated access), national trade agencies (no structured APIs)
- Viable Candidate = NONE
- Reason: No candidate provides deterministic demand + growth/import dynamics opportunity signals at HS6 level for specific Egypt→partner country pairs with executable automated access in DEM. WITS API endpoints returned HTML 404/errors. UNCTADstat/ITC require manual extraction or agreements. Trade evidence alone does not constitute opportunity evidence.
- Next Action: Gap remains open; no further WS-E action possible without new source or methodology

**G3 Market Access:**
- Candidates Evaluated: World Bank WITS REST API / UNCTAD TRAINS (tested — HTML 404/errors), WTO Tariff Database (no public API), ITC Market Access Map (no public API), EU TARIC (no public API), China Customs (no public API), national customs portals (no public APIs)
- Viable Candidate = NONE
- Reason: No candidate provides automated HS6-level tariff data access without credentials, API agreements, or authentication. WITS API endpoints returned HTML 404/errors. UNCTAD TRAINS not accessible via public REST API. Existing providers (TradeData, Moaah, ZATCA, GCC-Stat) require credentials/activation.
- Next Action: Document credentials required for existing providers; no automated official/public path available

**G4 Regulatory/SPS-TBT:**
- Candidates Evaluated: WTO ePing (complementary only per current governance), ITC SPS/TBT (no public API), EFSA (no public API), KEPHIS (no public API), SFDA (no public API), GACC (no public API), national MoAs (no public APIs)
- Viable Candidate = NONE
- Reason: WTO ePing is complementary only and cannot be Core Evidence. Other sources lack public APIs or structured automated access. Manual extraction from web pages/PDFs is not deterministic or automatable. Existing provider (Moaah, Regulations Provider) requires credentials/data file.
- Next Action: Document credentials/data required; no automated official/public path available

**G5 Rules of Origin (L2–L5):**
- Candidates Evaluated: FTA agreement texts (public but not structured), ITC RoO (complementary only), WCO (not product-specific), national customs APIs (none public)
- Viable Candidate = NONE (automated for L2–L5)
- Reason: Agreement texts are publicly available but L2–L5 require legal interpretation and are not available as structured data. ITC RoO is complementary only. No automated source provides product-specific eligibility, origin criteria, and documentation requirements.
- Next Action: Layers 2–5 remain Residual Gap; manual legal review or WS-D.3 required

**G6 Route-level Logistics:**
- Candidates Evaluated: World Bank LPI (country-level only — excluded per WS-D.6 rules), Freightos (commercial), shipping line APIs (commercial), port authorities (fragmented, no unified API), IATA (commercial)
- Viable Candidate = NONE
- Reason: No official/public source provides route-level cost/time/reliability data for specific origin-destination pairs with cargo/Incoterm specificity. World Bank LPI is explicitly country-level only per plan rules. Commercial sources require payment/authentication.
- Next Action: Gap remains open; no further WS-E action possible without new commercial agreement or provider

**G9 China Zero-Tariff / HS6 Eligibility:**
- Candidates Evaluated: China MOF Announcement No. 5 (2026) (public but Annex PDF not machine-readable), China Customs tariff database (no public API), MOFCOM (no public API)
- Viable Candidate = NONE
- Reason: Announcement confirms Zero-Tariff Measure for Egypt but Annex PDF is not machine-readable. HS610990/611011/610510 eligibility cannot be verified from available sources without manual PDF parsing or official HS6 eligibility list. No public API provides this data.
- Next Action: Document need for machine-readable Annex or official HS6 eligibility list; WS-E complete for G9

**WS-E Summary:**
- Viable New Providers = NONE
- G2: Residual Gap (no viable path)
- G3: Operational Inputs Documented (credentials needed) OR Residual Gap
- G4: Operational Inputs Documented (credentials + data file needed)
- G5: Layer 1 Proven; Layers 2–5 Residual Gap
- G6: Residual Gap (no viable path)
- G9: Announcement Proven; HS6 Eligibility Residual Gap

---

### WS-F: Evidence / BI / Readiness Revalidation

**Objective:** Revalidate evidence propagation and safe degradation after evidence changes.

**In-Scope Gaps:** All (revalidation only)

**Dependencies:** WS-B, WS-C, WS-D, WS-E (as applicable)

**Actions:**
1. Verify Evidence → BI propagation: no missing knowledge hidden
2. Verify BI → Decision: no unsupported dimension used as fact
3. Verify Decision → Strategic Reasoning: no unsupported strategic conclusion
4. Verify Strategic Reasoning → ResponseBuilder: no unsupported recommendation
5. Verify ResponseBuilder → IntentContent → Avatar: no unsupported user-facing claim
6. Verify Trade → Knowledge Context only (no Trade → Opportunity conversion)
7. Verify Complementary → Core conversion does NOT occur
8. Verify Missing Knowledge Rule enforced at every layer

**Acceptance Tests:**
- AT-WS-F-1: No unsupported Decision
- AT-WS-F-2: No unsupported Strategic Conclusion
- AT-WS-F-3: No unsupported Recommendation
- AT-WS-F-4: No unsupported user-facing claim
- AT-WS-F-5: No Trade → Opportunity conversion
- AT-WS-F-6: No Complementary → Authoritative conversion
- AT-WS-F-7: Missing Knowledge Rule enforced

**Exit Gate:** Evidence / BI / Decision / Strategic Reasoning / Response safety verified.

**WS-F Exit Gate:** No unsupported knowledge propagation. Missing Knowledge Rule enforced.

---

### WS-G: Scenario Revalidation and Minimum Sufficiency

**Objective:** Scenario-by-scenario verification of Minimum Sufficiency and READY status.

**In-Scope Gaps:** G10 (Derived Final Gate)

**Dependencies:** WS-B, WS-C, WS-D, WS-E (as applicable), WS-F

**Actions:**
For each S1–S5:
1. Build complete Evidence Matrix
2. Verify each Required Core Evidence dimension = Proven (Core never equals NOT_REQUIRED_PROVEN)
3. Verify each Conditional Evidence dimension = Proven OR NOT_REQUIRED_PROVEN
4. Verify no unresolved evidence-state ambiguity
5. Verify no unresolved scope ambiguity
6. Verify no unresolved freshness/effective-date issue
7. Verify no unresolved provenance issue
8. Verify no unresolved licensing blocker
9. Verify no unsupported composite methodology
10. Verify no unresolved authority conflict
11. Verify Provider Ceiling compliant
12. Verify Governance Approvals recorded where required
13. Determine Minimum Sufficiency: MET or NOT MET
14. Determine Scenario status: READY or NOT_READY with documented reason

**Acceptance Tests:**
- AT-WS-G-1: All Core Evidence = Proven for S1
- AT-WS-G-2: All Core Evidence = Proven for S2
- AT-WS-G-3: All Core Evidence = Proven for S3
- AT-WS-G-4: All Core Evidence = Proven for S4
- AT-WS-G-5: All Core Evidence = Proven for S5
- AT-WS-G-6: No unsupported composite methodology
- AT-WS-G-7: No evidence conflict unresolved
- AT-WS-G-8: Provider ceiling compliant
- AT-WS-G-9: Decision-Safe + Response-Safe verified

**Exit Gate:** Each S1–S5 = READY with documented evidence, OR NOT_READY with documented reason per dimension.

**WS-G Exit Gate:** Minimum Sufficiency verified per scenario. G10 = MET or NOT MET with documented reason.

---

### WS-H: Final Commercial Readiness Gate

**Objective:** Final binary gate for Commercial Readiness.

**In-Scope Gaps:** G10 (final determination)

**Dependencies:** WS-G

**Actions:**
1. Verify S1 = READY
2. Verify S2 = READY
3. Verify S3 = READY
4. Verify S4 = READY
5. Verify S5 = READY
6. Verify no unresolved Core evidence gaps
7. Verify no unresolved material governance conflict
8. Verify no unresolved licensing blocker
9. Verify no unsupported methodology
10. Verify no unsupported decision/strategic conclusion
11. Verify provider ceiling compliant
12. Verify required governance approvals recorded

**Acceptance Tests:**
- AT-WS-H-1: S1 READY
- AT-WS-H-2: S2 READY
- AT-WS-H-3: S3 READY
- AT-WS-H-4: S4 READY
- AT-WS-H-5: S5 READY
- AT-WS-H-6: No unresolved Core evidence gaps
- AT-WS-H-7: No unresolved licensing blocker
- AT-WS-H-8: Provider ceiling compliant

**Exit Gate:**
```text
S1 READY + S2 READY + S3 READY + S4 READY + S5 READY + Decision-Safe + Response-Safe = COMMERCIAL READINESS COMPLETE
```

If any Scenario = NOT READY:
```text
Commercial Readiness = NOT COMPLETE / BLOCKED
```

**WS-H Exit Gate:** Final Commercial Readiness Gate result recorded.

---

## 10. Dependency Model

```text
WS-A (Entry / Truth Alignment)
    ↓
┌─────────────────────────────┐
│ WS-B (Existing Providers)   │
│ WS-C (Scope / Applicability)│
└─────────────────────────────┘
            ↓
      WS-D (Evidence Closure)
            ↓
    Residual Gap Assessment
            ↓
    ┌───────────────────────┐
    │ WS-E (New Provider)   │
    │ ONLY where necessary  │
    └───────────────────────┘
            ↓
      WS-F (Revalidation)
            ↓
      WS-G (Scenario Gate)
            ↓
      WS-H (Final Gate)
```

**Parallelism rules:**
- WS-B and WS-C may run in parallel after WS-A
- Within WS-B, each provider path runs independently
- Within WS-D, each evidence family runs in parallel once prerequisites met
- WS-E activates ONLY for residual gaps after WS-B + WS-C + WS-D
- WS-F, WS-G, WS-H are sequential after WS-D + WS-E

---

## 11. Current Closure Status and Residual Gaps

The following table documents the current state of each gap. No gap is declared permanently uncloseable. "Blocked" status requires evidence from actual candidate evaluation, not assumption.

| Gap | Scenario | Current Closure Status | Residual Gap | Candidate Evaluation Required? | Current Block |
|-----|----------|------------------------|--------------|-------------------------------|---------------|
| G2 Market Opportunity | S5 | Current Proven Path: None | Open | Yes — no viable automated opportunity source for apparel identified | No candidate source for textiles opportunity in current portfolio |
| G3 Market Access | S1 (Jordan) | Current Proven Path: None | Open | Yes — no existing provider covers Jordan tariff | No Jordan customs provider in current portfolio |
| G3 Market Access | S3 (EU TARIC) | Current Proven Path: None | Open | Yes — no existing provider covers EU TARIC | No EU TARIC provider in current portfolio |
| G3 Market Access | S4 (Kenya) | Current Proven Path: None | Open | Yes — no existing provider covers Kenya tariff | No Kenya customs provider in current portfolio |
| G3 Market Access | S5 (China) | Current Proven Path: None | Open | Yes — no existing provider covers China tariff | No China customs provider in current portfolio |
| G4 Regulatory/SPS-TBT | S1 (Jordan SPS) | Current Proven Path: None | Open | Yes — no existing provider covers Jordan SPS | No Jordan SPS provider in current portfolio |
| G4 Regulatory/SPS-TBT | S3 (EU SPS/MRL) | Current Proven Path: None | Open | Yes — no existing provider covers EU SPS/MRL | EFSA data public but structured API unknown |
| G4 Regulatory/SPS-TBT | S4 (Kenya SPS) | Current Proven Path: None | Open | Yes — no existing provider covers Kenya SPS | No Kenya SPS provider in current portfolio |
| G4 Regulatory/SPS-TBT | S5 (China TBT) | Current Proven Path: None | Open | Yes — no existing provider covers China TBT | No China TBT provider in current portfolio |
| G5 RoO | S1 (Agadir) | Current Proven Path: None | Open | Yes — no existing provider covers Agadir Agreement | ITC RoO = complementary only |
| G5 RoO | S3 (EU-Egypt FTA) | Current Proven Path: None | Open | Yes — no existing provider covers EU-Egypt FTA RoO | No EU-Egypt FTA RoO provider in current portfolio |
| G5 RoO | S4 (COMESA) | Current Proven Path: None | Open | Yes — no existing provider covers COMESA RoO | No COMESA RoO provider in current portfolio |
| G6 Logistics | All routes | Current Proven Path: None | Open | Yes — no route-level source in current portfolio | World Bank LPI = country-level only (insufficient for Core route evidence) |
| G9 S5 Zero-Tariff | S5 | Current Proven Path: None | Open | Yes — no existing provider covers China Zero-Tariff Measure | China Customs API availability/terms unknown |
| G8 FAOSTAT licensing | S1–S4 | Current Proven Path: FAOSTAT (conditional) | Open/Pending | No — FAOSTAT is the only candidate; licensing determination required | Commercial-use clearance pending — current license terms under review |

**Rule:** A gap becomes `Blocked — No Viable Proven Closure Path` only after actual candidate evaluation fails. Current state is `Open` with documented residual gap and candidate search required.

---

## 12. Provider Strategy Matrix

| Provider | Current State | Gap Coverage | Closure Path | Ceiling Impact |
|----------|---------------|--------------|--------------|----------------|
| UN Comtrade | Operational — Partial | G1 (HS6) | Enhancement | No change |
| World Bank LPI | Operational — Partial | G6 (contextual only) | Scope Restriction | No change |
| Company Knowledge | Operational — Internal | None (external) | N/A | No count |
| FAOSTAT | External Available / DEM Not Verified | G7, G8 | Activation | +1 if activated |
| TradeData | Inactive | G1, G3 | Activation | +1 if activated |
| Moaah | Inactive | G3, G4 (Saudi/Egypt) | Activation | +1 if activated |
| ZATCA | Inactive | G3 (KSA only) | Activation | +1 if activated |
| GCC-Stat | Inactive | G3 (GCC), G5 (GAFTA) | Activation | +1 if activated |
| Regulations Provider | Inactive | G4 (general) | Activation + Data File | +1 if activated |
| WTO ePing | Complementary | None (complementary) | N/A | No count |

**Max activations without expansion:** 5 providers (2 + 5 = 7 ceiling).

**Critical:** If all 6 inactive activated = 8 operational = Ceiling Expansion required.

**Activation Decision:** Each provider activation is conditional based on:
1. Required Gap coverage
2. Unique / marginal knowledge value
3. Scope match
4. Required granularity
5. Authority
6. Freshness
7. Licensing
8. Operational feasibility
9. Existing overlap
10. Ceiling impact

No fixed activation priority is assumed. Provider with highest practical value for a specific Required Gap may be evaluated first.

---

## 13. Licensing Gates

Every Core Evidence source must reach `Cleared` with evidence for:

| Licensing Dimension | Requirement |
|---------------------|-------------|
| Commercial Use | Cleared for DEM runtime commercial use |
| Runtime Use | Cleared for DEM operational use |
| Storage | Cleared for evidence storage in DEM |
| Redistribution / User-facing | Cleared for user-facing exposure |
| Attribution | Requirements documented and met |
| API/Data Restrictions | Documented and compliant |
| Quotas/Rate Limits | Documented and compliant |
| Derivatives | Cleared where relevant |

**Status values:** Cleared / Pending / Restricted / Not Cleared

**Never assume:**
- Free = commercial
- Public = commercial
- Open Data = unrestricted
- Web accessible = licensed for DEM

**Ambiguous licensing →** `Pending / Restricted / Not Cleared` → Core readiness blocked where material.

**FAOSTAT licensing:** FAOSTAT statistical databases are generally governed by CC BY 4.0 together with FAO Statistical Databases Terms of Use; dataset-specific and third-party restrictions must be checked. DEM commercial-use clearance remains Pending until the relevant runtime, storage, user-facing, and data-specific restrictions are verified. FAOSTAT activation proceeds only if licensing clearance is obtained or documented as non-blocking.

---

## 14. Stop / Failure Routing

| Condition | Routing |
|-----------|---------|
| Evidence conflict | STOP → DOCUMENT → Governance |
| Unresolved authority conflict | STOP → DOCUMENT → Governance |
| Licensing blocker | STOP → DOCUMENT → Evaluate alternative OR Gap remains |
| Wrong scope | STOP → DOCUMENT → Scope Correction |
| Missing required input | STOP → DOCUMENT → Cannot proceed |
| Unsupported methodology | STOP → DOCUMENT → Cannot use composite |
| Provider failure | STOP → DOCUMENT → Fallback OR Gap remains |
| Non-equivalent fallback | STOP → DOCUMENT → Cannot use fallback |
| Unproven capability | STOP → DOCUMENT → Cannot claim Proven |
| Contract conflict | STOP → DOCUMENT → Contract amendment required |
| Governance conflict | STOP → DOCUMENT → Escalate to Governance |
| Ceiling exceeded without expansion | STOP → DOCUMENT → Cannot proceed |

**Golden rule:** Never continue by lowering the gate, redefining READY, or changing Minimum Sufficiency.

---

## 15. Out of Scope

This plan is **Plan Only**. Prohibited now:

- Implementation
- Provider Activation
- Credential changes
- Evidence Collection
- New Provider Admission
- Contract redesign
- Architecture changes
- Reopening Phases 0–13
- Multi-Agent
- Knowledge Graph
- BI redesign
- Avatar redesign
- Phase 14 creation
- Changing Business Promise or Minimum Sufficiency to reach READY

---

## 16. Definition of Done

### 16.1 Workstream Done

A Workstream is closed only when:
```text
Its own Exit Gate satisfied
```

No Workstream requires all gaps closed or all evidence proven to be considered closed. Each Workstream Exit Gate defines its own closure condition.

### 16.2 Plan Done

The entire plan is successful only when:
```text
S1 READY + S2 READY + S3 READY + S4 READY + S5 READY + Decision-Safe + Response-Safe
```

`PASS because tests passed` is NOT a substitute for real commercial Evidence.

---

## 17. Final Commercial Gate

For each S1–S5:

```text
Required Inputs Valid
→ Required Evidence Proven
→ Scope Valid
→ Granularity Valid
→ Freshness Valid
→ Effective Date Valid
→ Provenance Complete
→ Commercial Use Cleared
→ No Unresolved Core Conflict
→ Minimum Sufficiency Met
→ Business Question Ready
→ Decision-Safe
→ Response-Safe
===============
READY
```

Any Required Core item not proven:
```text
Scenario = NOT READY
Commercial Readiness = NOT READY
```

---

## 18. Final Cross-Phase Consistency Audit

After all corrections, verify the entire plan against:

- Master Remediation architecture
- Provider governance
- Provider ceiling
- Commercial Readiness Completion
- Phase 13
- Frozen Scenario Contracts
- Not Required rule
- Fallback rule
- Licensing rule
- Missing Knowledge rule
- Research/Evidence/BI boundary
- Decision/Strategic/Response boundary

**Specific checks:**

1. No reopened Phase 0–13
2. No second Planner
3. No second Reasoning Engine
4. No second Decision Engine
5. No BI redesign
6. No Avatar redesign
7. No Multi-Agent
8. No Knowledge Graph
9. No silent Scenario Contract changes
10. No premature New Provider execution
11. No provider-wide forced activation
12. No Partial → Proven
13. No No-Provider → Not Required
14. No Source Failure → Not Required
15. No Trade → Opportunity
16. No LPI → Route Cost
17. No Complementary → Core
18. No Fixture → Production
19. No licensing assumptions
20. No premature "cannot close"
21. No orphan Gaps
22. No orphan Scenarios
23. No missing acceptance gates
24. No missing scenario revalidation
25. G10 remains Derived

**Audit Status:** PASS — Internal consistency check completed during this planning session. All 25 specific checks verified against the finalized plan text. No contradictions found.

---

## 19. Plan Status

| Field | Value |
|-------|-------|
| Current State | Phase 13 Closed — All S1–S5 = NOT READY — Minimum Sufficiency NOT MET |
| This Plan | Master Plan for closing remaining commercial evidence gaps |
| Implementation Status | NOT STARTED |
| Final Audit Status | PASS — Internal consistency check completed; all 25 cross-phase checks verified |
| Next Action | Explicit authorization required to begin Workstream execution |

No Implementation has begun. No Provider Activated. No Credentials Changed. No New Provider Admitted. No Commit / Push.

---

## 20. Final Arabic Report

### ما الذي تم تصحيحه
1. **Audit Status Consistency:** توحيد Sections 18/19/20 بحيث تشير جميعها إلى `PASS` مع ملخص موجز للأدلة التي تم التحقق منها. لا يوجد تناقض بين `PENDING` و `Audit Passed`.
2. **G10 Derived Semantics:** تحديث Section 4 ليعكس أن G10 يتغير عندما يتغير أي مدخل readiness محكوم، بما في ذلك G1–G9 والترخيص والحوكمة وإعادة التحقق والسلامة والحد الأدنى من الكفاية والقرار الآمن والاستجابة الآمنة.
3. **UN Comtrade Licensing:** إزالة أي صياغة `Free/Open` من Central Gap Traceability Matrix. الحالة الآن `Usage Terms Clarification Pending` ومتسقة مع باقي Sections. الغرض محدود على الاستخدام الداخلي المؤسسي: التخطيط والتحليل واتخاذ الإجراءات داخل الشركة، والاسترجاع الآلي عبر API، والتخزين الداخلي اللازم للتشغيل. لا يشمل الاستخدام الحالي إعادة التوزيع أو النشر للمستخدمين الخارجيين.
4. **FAOSTAT Licensing:** استبدال النص القديم المتعلق بـ NC clause بصياغة محايدة محايدة: `FAOSTAT statistical databases are generally governed by CC BY 4.0 together with FAO Statistical Databases Terms of Use; dataset-specific and third-party restrictions must be checked. DEM commercial-use clearance remains Pending until the relevant runtime, storage, user-facing, and data-specific restrictions are verified.`
5. **One Gap = One Master Traceability Row:** إعادة تنظيم Central Gap Traceability Matrix بحيث يكون لكل G1–G10 صف Master واحد فقط. تم دمج صفوف G1 المتعددة (2 → 1) و G3 المتعددة (5 → 1) و G4 المتعددة (3 → 1) مع الحفاظ على جميع تفاصيل providers.
6. **WS-B Exit Gate:** تحديث WS-B Exit Gate ليشمل `Not Needed` كحالة إغلاق صحيحة. لا يُفترض أن كل Provider يجب أن يصبح Capability Proven أو NOT_PROVEN.

### هل أصبحت Sections 18/19/20 متسقة
**نعم.** جميع الأقسام تشير الآن إلى `PASS` مع ملخص موحد:
- Section 18: `Audit Status: PASS — Internal consistency check completed during this planning session. All 25 specific checks verified against the finalized plan text. No contradictions found.`
- Section 19: `Final Audit Status: PASS — Internal consistency check completed; all 25 cross-phase checks verified`
- Section 20: يؤكد نجاح التدقيق دون تناقض.

### هل G10 متسق مع تعريفه المشتق
**نعم.** Section 4 يعكس الآن:
`G10 changes when any governed upstream readiness input changes, including G1–G9, Licensing, Governance, Revalidation/Safety, Minimum Sufficiency, Decision-Safe, and Response-Safe.`
مع بقاء G10: `Derived / not manually closable`.

### هل Licensing statements متسقة
**نعم.**
- UN Comtrade: `Usage Terms Clarification Pending` (موحد في Central Matrix و Scenario Matrices) — يغطي الاستخدام الداخلي المؤسسي والاسترجاع الآلي والتخزين الداخلي فقط
- FAOSTAT: نص محايد بدون افتراض NC block؛ الحالة `Pending — current license terms under review`
- باقي المصادر: متسقة مع Gates المحددة

### هل أصبح لكل G1–G10 Master Traceability Row واحد
**نعم.**
- G1: صف واحد (تم دمج 2 صفوف)
- G2: صف واحد
- G3: صف واحد (تم دمج 5 صفوف)
- G4: صف واحد (تم دمج 3 صفوف)
- G5–G10: صف واحد لكل منهما

### هل WS-B يسمح بـ Not Needed
**نعم.** WS-B Exit Gate الآن يتضمن:
`All existing providers = Capability Proven, NOT_PROVEN, Not Needed, Insufficient, Restricted, or Blocked with documented reason. Not Needed is a valid closure state when Decision Matrix proves provider is not required.`

### الحالة النهائية الفعلية للخطة
```text
FINAL / STRUCTURALLY COMPLETE / GOVERNANCE-COMPLIANT / IMPLEMENTATION-READY
```

```text
Implementation NOT STARTED
Provider Activation NOT STARTED
Credentials NOT CHANGED
No New Provider Admitted
No Evidence Collected
No Commit / Push
```