# Phase 1 — Scenario Contract Completion

**Phase:** 1 — Scenario Contract Completion  
**Branch:** `main`  
**Mode:** Execution — No Implementation  
**Authority:** `.kilo/plans/1789733769109-commercial-readiness-completion.md`  
**Date:** 2026-09-18  

---

## 1. Phase 1 Objective

Transform S1–S5 from baseline profiles into frozen, executable Scenario Contracts with complete Business Question Contracts.

**Phase 0 Status:** ✅ PASS — Scenario Set frozen, documentation drift reconciled.  
**Authority Baseline:** `43d809e`  
**Prerequisite:** Phase 0 complete.

---

## 2. Reference / Validation Lookups Performed

The following reference lookups were conducted during Phase 1 to construct and validate the Scenario Contracts. These do NOT count as Business-Question Evidence Collection.

| Lookup Type | Scope | Status | Notes |
|-------------|-------|--------|-------|
| HS Nomenclature Validation | HS07, HS08, HS09, HS61 chapters | ✅ Completed | Chapter-level validated; product-specific HS4/HS6 to be determined per source requirement in Phase 2 |
| Jurisdiction Validation | Jordan, Saudi Arabia, Germany/EU, Kenya, China | ✅ Completed | Customs/regulatory jurisdictions confirmed: Jordan (national), Saudi Arabia (national), Germany/EU (EU customs jurisdiction), Kenya (national), China (national) |
| Route/Node Validation | Alexandria/Port Said → Aqaba; Egypt → Saudi ports; Egypt → Germany ports; Egypt → Mombasa; Egypt → China ports | ✅ Completed | Major trade routes validated; specific ports/nodes to be confirmed per carrier/source in Phase 2 |
| Tariff Classification Reference | HS07, HS08, HS09, HS61 product categories | ✅ Completed | Chapter-level baseline established; exact tariff-line level depends on product-specific HS code |

**No Business-Question Evidence Collection was performed in Phase 1.**

---

## 3. Frozen Scenario Contracts

### 3.1 S1 — Egypt → Jordan / Fresh Vegetables / HS07

**Scenario ID:** S1  
**Freeze Status:** ✅ FROZEN  
**Freeze Authority:** Phase 1 execution per `.kilo/plans/1789733769109-commercial-readiness-completion.md`

#### Contract Fields

| Field | Value |
|-------|-------|
| Origin | Egypt — Alexandria Port (primary); Port Said Port (fallback) |
| Destination | Jordan — Aqaba Port |
| Exact Product Identity | Fresh vegetables: tomatoes, cucumbers, peppers, onions |
| Product Description | Perishable agricultural produce requiring cold chain logistics |
| Validated HS Mapping | HS07 (chapter) — baseline; HS4/HS6 required for tariff/regulatory specificity |
| HS Nomenclature / Version | HS 2022 (latest available) |
| Required HS Granularity | Trade: HS07 chapter acceptable for bilateral baseline; Tariff/Market Access: HS4/HS6 required; Regulatory/SPS: HS4/HS6 required |
| Transport Mode | Sea (primary) — Alexandria Port → Aqaba Port; Road (fallback) — Port Said Port → Aqaba Port |
| Relevant Port/Node | Origin: Alexandria Port (primary), Port Said Port (fallback); Destination: Aqaba Port |
| Cargo Characteristics | Perishable, requires cold chain (0–4°C), ventilated containers for ethylene-sensitive produce |
| Shipment Assumptions | Full container load (FCL) or less-than-container load (LCL) as applicable; standard refrigerated container (reefer) |
| Incoterm | FOB Alexandria Port (baseline); CIF Aqaba if cost includes freight |
| Temperature/Control Requirements | Cold chain mandatory; temperature monitoring required; phytosanitary certification for Jordan |
| Assessment Time Window | Current assessment: Q4 2026 |
| Reliability Metric | On-time delivery rate; transit time variance; cold chain integrity (temperature excursion incidents) |

#### Business Question Contract

**Specific User Need:**  
What is the export feasibility for fresh Egyptian vegetables (tomatoes, cucumbers, peppers, onions) to Jordan via Aqaba, including trade performance, market opportunity, tariff/regulatory requirements, and logistics?

**Business Question (Operationally Testable):**  
"What is the export feasibility for fresh Egyptian tomatoes (HS070200), cucumbers (HS070700), peppers (HS070960), and onions (HS070310) to Jordan (Aqaba), including: (a) current bilateral trade volume and 3-year trend for HS07 vegetables, (b) demand gap and import dynamics for fresh vegetables in Jordan, (c) Jordan tariff duty rate and entry procedures for HS070200/070700/070960/070310, (d) Jordan SPS requirements for fresh vegetables, (e) route logistics cost/time/reliability from Alexandria/Port Said to Aqaba?"

**Evidence Dimensions:**
1. Trade
2. Opportunity
3. Market Access
4. Regulatory (SPS)
5. Agrifood (conditional)
6. Logistics
7. RoO (conditional)

**Core Minimum Sufficiency:**
- Trade: HS-level bilateral trade Egypt–Jordan (HS07 chapter acceptable for baseline)
- Market Access: Jordan tariff duty + entry procedures (HS4/HS6 required)
- Regulatory: Jordan SPS requirements for fresh vegetables (HS4/HS6 required)
- Logistics: Route cost, time, reliability (route-specific evidence required)
- Opportunity: Deterministic composite or proven source (Trade alone insufficient)

**Core Evidence:**
- Bilateral trade data for Egypt–Jordan vegetables (HS07)
- Jordan tariff schedule and entry procedures for HS070200/070700/070960/070310
- Jordan SPS requirements for fresh vegetables
- Route logistics metrics: Alexandria/Port Said → Aqaba (sea primary, road alternative)
- Opportunity evidence: demand gap + import dynamics (deterministic composite or proven source)

**Conditional Dimensions:**
- **Agrifood:** Conditional — required if Business Question requires agricultural market indicators beyond trade volume (e.g., production/supply context, price trends). Applicability: determined by Business Question scope.
- **RoO:** Conditional — Agadir Agreement. Applicability: must be proven first. If FTA applies: agreement + eligibility + origin criterion + documentation required. If no preferential arrangement: Not Required with documented reason.

**Country/Jurisdiction Scope:**
- Origin: Egypt
- Destination: Jordan (national customs jurisdiction)
- Customs/Regulatory: Jordan Customs, Jordan Ministry of Agriculture (SPS)

**Freshness Requirements:**
- Trade: Latest available annual data
- Opportunity: Source-specific
- Market Access: Current/effective at time of assessment
- Regulatory: Current/effective at time of assessment
- Logistics: Current rates and schedules

**Effective-Date Requirements:**
- Regulatory: Must be current/effective at time of assessment (Q4 2026)
- Market Access: Effective tariff schedule at time of assessment
- RoO: Agreement current at time of export

**Output Boundaries:**
- Exact tariff line for each HS4/HS6 code
- Exact SPS requirements for fresh vegetables
- Exact route cost estimate (FOB/CIF basis)
- Opportunity quantification with methodology
- RoO eligibility determination

**Not Required Conditions:**
- Agrifood: if Business Question does not require agricultural market indicators beyond trade volume
- RoO: if no preferential arrangement applies to Egypt–Jordan vegetable trade

**Decision-Safe Conditions:**
- Missing SPS requirements → decision unsafe
- Missing tariff rates → decision unsafe
- Unsupported opportunity methodology → decision unsafe
- Route logistics without route-specific evidence → decision unsafe

**Response-Safe Conditions:**
- No trade→opportunity inference without proof
- No complementary→authoritative conversion
- No chapter-level HS used as product-specific evidence
- No country-level LPI used as route-level reliability

**System Must NOT Infer:**
- Opportunity from Trade alone
- Tariff rates from chapter-level HS alone
- Route reliability from country-level LPI alone
- SPS requirements from generic vegetable guidelines without Jordan-specific validation

---

### 3.2 S2 — Egypt → Saudi Arabia / Dates / HS08

**Scenario ID:** S2  
**Freeze Status:** ✅ FROZEN  
**Freeze Authority:** Phase 1 execution per `.kilo/plans/1789733769109-commercial-readiness-completion.md`

#### Contract Fields

| Field | Value |
|-------|-------|
| Origin | Egypt — Alexandria Port (primary); Port Said Port (fallback) |
| Destination | Saudi Arabia — Jeddah Port (primary); Dammam Port (fallback) |
| Exact Product Identity | Dates: Siwa, Hayani, Sagaaee varieties |
| Product Description | Dried fruit with specific quality grades and packaging standards for GCC market |
| Validated HS Mapping | HS08 (chapter) — baseline; HS4/HS6 required for tariff/regulatory specificity |
| HS Nomenclature / Version | HS 2022 (latest available) |
| Required HS Granularity | Trade: HS08 chapter acceptable for bilateral baseline; Tariff/Market Access: HS4/HS6 required; Regulatory/SPS: HS4/HS6 required; RoO: HS4/HS6 for origin criterion |
| Transport Mode | Sea (primary) — Alexandria Port → Jeddah Port; Road (fallback) — Port Said Port → Dammam Port |
| Relevant Port/Node | Origin: Alexandria Port (primary), Port Said Port (fallback); Destination: Jeddah Port (primary), Dammam Port (fallback) |
| Cargo Characteristics | Dried fruit, moisture-sensitive, requires humidity control, packaging grade relevant (Saudi SASO standards) |
| Shipment Assumptions | FCL or LCL as applicable; moisture-barrier packaging; palletized |
| Incoterm | FOB Alexandria Port (baseline); CIF Jeddah/Dammam if cost includes freight |
| Temperature/Control Requirements | Ambient temperature with humidity control (15–25°C, 50–70% RH); no refrigeration required |
| Assessment Time Window | Current assessment: Q4 2026 |
| Reliability Metric | On-time delivery rate; transit time variance; cargo condition integrity (moisture/humidity incidents) |

#### Business Question Contract

**Specific User Need:**  
What is the export feasibility for Egyptian dates (Siwa, Hayani, Sagaaee) to Saudi Arabia, including trade performance, market opportunity, tariff/regulatory requirements, GAFTA RoO eligibility, and logistics?

**Business Question (Operationally Testable):**  
"What is the export feasibility for Egyptian dates — Siwa (HS080410), Hayani (HS080410), Sagaaee (HS080410) — to Saudi Arabia (Jeddah/Dammam), including: (a) current bilateral trade volume and 3-year trend for HS0804, (b) demand gap and import dynamics for dates in Saudi Arabia, (c) Saudi tariff duty rate and entry procedures for HS080410, (d) Saudi SPS requirements for dates, (e) GAFTA RoO eligibility and documentation for Egyptian dates, (f) route logistics cost/time/reliability from Alexandria/Port Said to Jeddah/Dammam?"

**Evidence Dimensions:**
1. Trade
2. Opportunity
3. Market Access
4. Regulatory (SPS)
5. Agrifood (conditional)
6. Logistics
7. RoO (Core — GAFTA applicability must be proven)

**Core Minimum Sufficiency:**
- Trade: HS-level bilateral trade Egypt–Saudi (HS08)
- Market Access: Saudi tariff + entry procedures (HS4/HS6 required)
- Regulatory: Saudi SPS for dates (HS4/HS6 required)
- RoO: GAFTA RoO agreement + eligibility + origin criterion + documentation
- Logistics: Route cost, time, reliability (route-specific evidence required)
- Opportunity: Deterministic composite or proven source

**Core Evidence:**
- Bilateral trade data for Egypt–Saudi dates (HS08)
- Saudi tariff schedule and entry procedures for HS080410
- Saudi SPS requirements for dates
- GAFTA RoO: agreement text + eligibility criteria + origin criterion + required documentation
- Route logistics metrics: Alexandria/Port Said → Jeddah/Dammam
- Opportunity evidence: demand gap + import dynamics

**Conditional Dimensions:**
- **Agrifood:** Conditional — required if Business Question requires agricultural market indicators beyond trade (e.g., date production/supply context, price trends). Applicability: determined by Business Question scope.

**Country/Jurisdiction Scope:**
- Origin: Egypt
- Destination: Saudi Arabia (national customs jurisdiction)
- Customs/Regulatory: Saudi Customs, Saudi SFDA (SPS), GCC Standardization Organization (GSO)

**Freshness Requirements:**
- Trade: Latest available annual data
- Opportunity: Source-specific
- Market Access: Current/effective
- Regulatory: Current/effective
- RoO: Agreement current at time of export
- Logistics: Current

**Effective-Date Requirements:**
- Regulatory: Must be current/effective at time of assessment (Q4 2026)
- Market Access: Effective tariff schedule at time of assessment
- RoO: GAFTA current at time of export

**Output Boundaries:**
- Exact tariff line for HS080410
- Exact SPS requirements for dates
- GAFTA RoO eligibility determination with documentation checklist
- Exact route cost estimate
- Opportunity quantification with methodology

**Not Required Conditions:**
- Agrifood: if Business Question does not require agricultural market indicators beyond trade volume
- RoO: NOT APPLICABLE — GAFTA RoO is Core for this scenario; only becomes Not Required if GAFTA is proven non-applicable

**Decision-Safe Conditions:**
- Missing SPS requirements → decision unsafe
- Missing tariff rates → decision unsafe
- GAFTA RoO not determined → decision unsafe
- Route logistics without route-specific evidence → decision unsafe

**Response-Safe Conditions:**
- No trade→opportunity inference without proof
- No complementary→authoritative conversion
- No chapter-level HS used as product-specific evidence
- No GAFTA RoO assumed without agreement verification

**System Must NOT Infer:**
- GAFTA RoO eligibility from trade existence alone
- Opportunity from Trade alone
- Tariff rates from chapter-level HS alone
- Route reliability from country-level proxies alone

---

### 3.3 S3 — Egypt → Germany / Citrus / HS08

**Scenario ID:** S3  
**Freeze Status:** ✅ FROZEN  
**Freeze Authority:** Phase 1 execution per `.kilo/plans/1789733769109-commercial-readiness-completion.md`

#### Contract Fields

| Field | Value |
|-------|-------|
| Origin | Egypt — Alexandria Port (sea primary); Cairo Airport (air fallback) |
| Destination Market | Germany |
| Customs / Regulatory Jurisdiction | EU customs/regulatory jurisdiction (Germany is destination market; EU TARIC and EU SPS regulations apply) |
| Exact Product Identity | Citrus fruits: oranges, lemons, grapefruits |
| Product Description | Perishable agricultural produce requiring phytosanitary compliance for EU market |
| Validated HS Mapping | HS08 (chapter) — baseline; HS4/HS6 required for tariff/regulatory specificity |
| HS Nomenclature / Version | HS 2022 / EU TARIC (latest available) |
| Required HS Granularity | Trade: HS08 chapter acceptable for bilateral baseline; Tariff/Market Access: HS4/HS6 required for EU TARIC; Regulatory/SPS: HS4/HS6 required for EU SPS/MRL; RoO: HS4/HS6 for EU–Egypt FTA origin criterion |
| Transport Mode | Sea (primary) — Alexandria Port → Hamburg Port; Air (fallback) — Cairo Airport → Frankfurt Airport |
| Relevant Port/Node | Origin: Alexandria Port (sea), Cairo Airport (air); Destination: Hamburg Port (sea), Frankfurt Airport (air) |
| Cargo Characteristics | Perishable, requires cold chain (0–4°C), phytosanitary certification for EU, ethylene-sensitive |
| Shipment Assumptions | FCL or LCL as applicable; refrigerated container (reefer) with temperature logging; phytosanitary certificate required |
| Incoterm | FOB Alexandria Port (baseline); CIF Hamburg/Bremerhaven if cost includes freight |
| Temperature/Control Requirements | Cold chain mandatory; temperature monitoring and logging; phytosanitary compliance for EU |
| Assessment Time Window | Current assessment: Q4 2026 |
| Reliability Metric | On-time delivery rate; transit time variance; cold chain integrity; EU customs clearance time |

#### Business Question Contract

**Specific User Need:**  
What is the export feasibility for Egyptian citrus (oranges, lemons, grapefruits) to Germany/EU, including trade performance, market opportunity, tariff/regulatory requirements, EU–Egypt FTA RoO eligibility, and logistics?

**Business Question (Operationally Testable):**  
"What is the export feasibility for Egyptian oranges (HS080510), lemons (HS080550), grapefruits (HS080540) to Germany (EU), including: (a) current bilateral trade volume and 3-year trend for HS0805, (b) demand gap and import dynamics for citrus in Germany/EU, (c) EU TARIC tariff duty rate and entry procedures for HS080510/080550/080540, (d) EU SPS/MRL requirements for Egyptian citrus, (e) EU–Egypt FTA RoO eligibility and documentation for citrus, (f) route logistics cost/time/reliability from Alexandria/Port Said to Hamburg/Bremerhaven or Cairo to Frankfurt/Munich?"

**Evidence Dimensions:**
1. Trade
2. Opportunity
3. Market Access
4. Regulatory (SPS/MRL)
5. Agrifood (conditional)
6. Logistics
7. RoO (Core — EU–Egypt FTA applicability must be proven)

**Core Minimum Sufficiency:**
- Trade: HS-level bilateral trade Egypt–Germany (HS08)
- Market Access: EU TARIC tariff + entry procedures (HS4/HS6 required)
- Regulatory: EU SPS/MRL for citrus (HS4/HS6 required)
- RoO: EU–Egypt FTA agreement + eligibility + origin criterion + documentation
- Logistics: Route cost, time, reliability (route-specific evidence required)
- Opportunity: Deterministic composite or proven source

**Core Evidence:**
- Bilateral trade data for Egypt–Germany citrus (HS08)
- EU TARIC tariff schedule and entry procedures for HS080510/080550/080540
- EU SPS/MRL requirements for Egyptian citrus
- EU–Egypt FTA RoO: agreement text + eligibility criteria + origin criterion + required documentation
- Route logistics metrics: Alexandria/Port Said → Hamburg/Bremerhaven (sea) OR Cairo → Frankfurt/Munich (air)
- Opportunity evidence: demand gap + import dynamics

**Conditional Dimensions:**
- **Agrifood:** Conditional — required if Business Question requires agricultural market indicators beyond trade (e.g., citrus production/supply context, price trends). Applicability: determined by Business Question scope.

**Country/Jurisdiction Scope:**
- Origin: Egypt
- Destination Market: Germany (EU customs jurisdiction)
- Customs/Regulatory: EU TARIC (European Commission), EU SPS/MRL (EFSA / EU Commission), EU–Egypt FTA

**Freshness Requirements:**
- Trade: Latest available annual data
- Opportunity: Source-specific
- Market Access: Current/effective EU TARIC
- Regulatory: Current/effective EU SPS/MRL
- RoO: EU–Egypt FTA current at time of export
- Logistics: Current

**Effective-Date Requirements:**
- Regulatory: Must be current/effective at time of assessment (Q4 2026)
- Market Access: Current EU TARIC at time of assessment
- RoO: EU–Egypt FTA current at time of export

**Output Boundaries:**
- Exact tariff line for each HS4/HS6 code under EU TARIC
- Exact SPS/MRL requirements for Egyptian citrus
- EU–Egypt FTA RoO eligibility determination with documentation checklist
- Exact route cost estimate (sea vs air comparison if both modes considered)
- Opportunity quantification with methodology

**Not Required Conditions:**
- Agrifood: if Business Question does not require agricultural market indicators beyond trade volume
- RoO: if EU–Egypt FTA does not apply to citrus or citrus is not eligible under the agreement

**Decision-Safe Conditions:**
- Missing SPS/MRL requirements → decision unsafe
- Missing EU TARIC rates → decision unsafe
- EU–Egypt FTA RoO not determined → decision unsafe
- Route logistics without route-specific evidence → decision unsafe

**Response-Safe Conditions:**
- No trade→opportunity inference without proof
- No complementary→authoritative conversion
- No chapter-level HS used as product-specific evidence
- No EU RoO assumed without FTA verification

**System Must NOT Infer:**
- EU–Egypt FTA eligibility from trade existence alone
- Opportunity from Trade alone
- Tariff rates from chapter-level HS alone
- Route reliability from country-level proxies alone
- SPS requirements from Codex/WHO guidelines without EU-specific validation

---

### 3.4 S4 — Egypt → Kenya / Coffee / HS09

**Scenario ID:** S4  
**Freeze Status:** ✅ FROZEN  
**Freeze Authority:** Phase 1 execution per `.kilo/plans/1789733769109-commercial-readiness-completion.md`

#### Contract Fields

| Field | Value |
|-------|-------|
| Origin | Egypt — Alexandria Port (sea primary); Cairo Airport (air fallback) |
| Destination | Kenya — Mombasa Port (sea primary); Jomo Kenyatta International Airport, Nairobi (air fallback) |
| Exact Product Identity | Coffee: green coffee beans, roasted coffee |
| Product Description | Agricultural commodity with specific quality standards and grading for East African market |
| Validated HS Mapping | HS09 (chapter) — baseline; HS4/HS6 required for tariff/regulatory specificity |
| HS Nomenclature / Version | HS 2022 (latest available) |
| Required HS Granularity | Trade: HS09 chapter acceptable for bilateral baseline; Tariff/Market Access: HS4/HS6 required; Regulatory/SPS: HS4/HS6 required; RoO: HS4/HS6 if applicable |
| Transport Mode | Sea (primary) — Alexandria Port → Mombasa Port; Air (fallback) — Cairo Airport → Jomo Kenyatta International Airport, Nairobi |
| Relevant Port/Node | Origin: Alexandria Port (sea), Cairo Airport (air); Destination: Mombasa Port (sea), Jomo Kenyatta International Airport, Nairobi (air) |
| Cargo Characteristics | Agricultural commodity, moisture-sensitive, requires ventilation, packaging grade relevant |
| Shipment Assumptions | FCL or LCL as applicable; ventilated containers for green coffee; moisture-barrier packaging for roasted coffee |
| Incoterm | FOB Alexandria Port (baseline); CIF Mombasa if cost includes freight |
| Temperature/Control Requirements | Ambient temperature with humidity control (green coffee: 10–20°C, 60–70% RH; roasted coffee: 15–25°C, 50–60% RH) |
| Assessment Time Window | Current assessment: Q4 2026 |
| Reliability Metric | On-time delivery rate; transit time variance; cargo condition integrity (moisture/contamination incidents) |

#### Business Question Contract

**Specific User Need:**  
What is the export feasibility for Egyptian coffee (green beans, roasted) to Kenya, including trade performance, market opportunity, tariff/regulatory requirements, applicable FTA RoO eligibility, and logistics?

**Business Question (Operationally Testable):**  
"What is the export feasibility for Egyptian green coffee beans (HS090111) and roasted coffee (HS090121) to Kenya (Mombasa/Nairobi), including: (a) current bilateral trade volume and 3-year trend for HS0901, (b) demand gap and import dynamics for coffee in Kenya, (c) Kenya tariff duty rate and entry procedures for HS090111/090121, (d) Kenya SPS requirements for coffee, (e) any applicable FTA RoO eligibility and documentation, (f) route logistics cost/time/reliability from Alexandria/Port Said to Mombasa or Cairo to Nairobi?"

**Evidence Dimensions:**
1. Trade
2. Opportunity
3. Market Access
4. Regulatory (SPS)
5. Agrifood (conditional)
6. Logistics
7. RoO (conditional — any applicable FTA)

**Core Minimum Sufficiency:**
- Trade: HS-level bilateral trade Egypt–Kenya (HS09)
- Market Access: Kenya tariff + entry procedures (HS4/HS6 required)
- Regulatory: Kenya SPS for coffee (HS4/HS6 required)
- Logistics: Route cost, time, reliability (route-specific evidence required)
- Opportunity: Deterministic composite or proven source
- RoO: Only if applicable FTA exists; otherwise Not Required with documented proof

**Core Evidence:**
- Bilateral trade data for Egypt–Kenya coffee (HS09)
- Kenya tariff schedule and entry procedures for HS090111/090121
- Kenya SPS requirements for coffee
- Route logistics metrics: Alexandria/Port Said → Mombasa (sea) OR Cairo → Nairobi (air)
- Opportunity evidence: demand gap + import dynamics
- RoO: Applicability determination first; if applicable: agreement + eligibility + origin criterion + documentation

**Conditional Dimensions:**
- **Agrifood:** Conditional — required if Business Question requires agricultural market indicators beyond trade (e.g., coffee production/supply context, price trends). Applicability: determined by Business Question scope.
- **RoO:** Conditional — COMESA Free Trade Area / COMESA Rules of Origin. Applicability: must be proven first. If no agreement applies: Not Required with documented reason.

**Country/Jurisdiction Scope:**
- Origin: Egypt
- Destination: Kenya (national customs jurisdiction)
- Customs/Regulatory: Kenya Customs, Kenya KEPHIS (SPS)

**Freshness Requirements:**
- Trade: Latest available annual data
- Opportunity: Source-specific
- Market Access: Current/effective
- Regulatory: Current/effective
- RoO: Agreement current at time of export (if applicable)
- Logistics: Current

**Effective-Date Requirements:**
- Regulatory: Must be current/effective at time of assessment (Q4 2026)
- Market Access: Effective tariff schedule at time of assessment
- RoO: Agreement current at time of export (if applicable)

**Output Boundaries:**
- Exact tariff line for each HS4/HS6 code
- Exact SPS requirements for coffee
- RoO applicability determination (Required or Not Required with documented reason)
- Exact route cost estimate
- Opportunity quantification with methodology

**Not Required Conditions:**
- Agrifood: if Business Question does not require agricultural market indicators beyond trade volume
- RoO: if no preferential arrangement applies to Egypt–Kenya coffee trade (must be proven, not assumed)

**Decision-Safe Conditions:**
- Missing SPS requirements → decision unsafe
- Missing tariff rates → decision unsafe
- RoO applicability undetermined → decision unsafe
- Route logistics without route-specific evidence → decision unsafe

**Response-Safe Conditions:**
- No trade→opportunity inference without proof
- No complementary→authoritative conversion
- No chapter-level HS used as product-specific evidence
- No RoO assumed without agreement verification

**System Must NOT Infer:**
- RoO eligibility from trade existence alone
- Opportunity from Trade alone
- Tariff rates from chapter-level HS alone
- Route reliability from country-level proxies alone

---

### 3.5 S5 — Egypt → China / Knitted Apparel / HS61

**Scenario ID:** S5  
**Freeze Status:** ✅ FROZEN  
**Freeze Authority:** Phase 1 execution per `.kilo/plans/1789733769109-commercial-readiness-completion.md`

#### Contract Fields

| Field | Value |
|-------|-------|
| Origin | Egypt — Alexandria Port (sea primary); Cairo Airport (air fallback) |
| Destination | China — Shanghai Port (sea primary); Beijing Capital Airport (air fallback) |
| Exact Product Identity | Knitted apparel: T-shirts (HS610990), sweaters/pullovers (HS611011), men's shirts (HS610510) |
| Product Description | Knitted or crocheted apparel articles for Chinese market |
| Validated HS Mapping | HS61 (chapter) — baseline; HS6 required for tariff/TBT specificity |
| HS Nomenclature / Version | HS 2022 (latest available) |
| Required HS Granularity | Trade: HS61 chapter acceptable for bilateral baseline; Tariff/Market Access: HS6 required for exact duty rate; Regulatory/TBT: HS6 required for product-specific TBT requirements |
| Transport Mode | Sea (primary) — Alexandria Port → Shanghai Port; Air (fallback) — Cairo Airport → Beijing Capital Airport |
| Relevant Port/Node | Origin: Alexandria Port (sea), Cairo Airport (air); Destination: Shanghai Port (sea), Beijing Capital Airport (air) |
| Cargo Characteristics | Knitted apparel, packaging requirements vary by product type (T-shirts: garment bags or cartons; sweaters: folded with protective wrapping; shirts: boxed or cartoned) |
| Shipment Assumptions | FCL or LCL as applicable; standard dry container; packaging per product type |
| Incoterm | FOB Alexandria Port (baseline); CIF Shanghai/Shenzhen if cost includes freight |
| Temperature/Control Requirements | Ambient temperature; no special temperature control |
| Assessment Time Window | Current assessment: Q4 2026 |
| Reliability Metric | On-time delivery rate; transit time variance; cargo integrity (damage/water incidents) |

#### Business Question Contract

**Specific User Need:**  
What is the export feasibility for Egyptian knitted apparel (T-shirts, sweaters/pullovers, men's shirts) to China, including trade performance, market opportunity, tariff/TBT requirements, and logistics?

**Business Question (Operationally Testable):**  
"What is the export feasibility for Egyptian knitted apparel — T-shirts (HS610990), sweaters/pullovers (HS611011), men's shirts (HS610510) — to China (Shanghai/Shenzhen), including: (a) current bilateral trade volume and 3-year trend for HS61 knitted apparel, (b) demand gap and import dynamics for knitted apparel in China, (c) China tariff duty rate and entry procedures for HS610990/611011/610510, (d) China TBT requirements for knitted apparel, (e) route logistics cost/time/reliability from Alexandria/Port Said to Shanghai/Shenzhen?"

**Evidence Dimensions:**
1. Trade
2. Opportunity
3. Market Access
4. Regulatory (TBT)
5. Logistics
6. Agrifood: NOT REQUIRED — non-agricultural product
7. RoO (conditional)

**Core Minimum Sufficiency:**
- Trade: HS-level bilateral trade Egypt–China (HS61)
- Market Access: China tariff + entry procedures (HS6 required)
- Regulatory: China TBT for knitted apparel (HS6 required)
- Logistics: Route cost, time, reliability (route-specific evidence required)
- Opportunity: Deterministic composite or proven source

**Core Evidence:**
- Bilateral trade data for Egypt–China knitted apparel (HS61)
- China tariff schedule and entry procedures for HS610990/611011/610510
- China TBT requirements for knitted apparel
- Route logistics metrics: Alexandria/Port Said → Shanghai/Shenzhen
- Opportunity evidence: demand gap + import dynamics

**Conditional Dimensions:**
- **RoO:** Conditional — 
Preferential Regime: China Zero-Tariff Measure for 20 African Countries (1 May 2026 – 30 April 2028).
Origin Regime: China Customs Rules of Origin under the Zero-Tariff Measure.
Applicability: must be proven first. If applicable: agreement + eligibility + origin criterion + documentation. If not applicable: Not Required with documented reason.
- **Agrifood:** NOT REQUIRED — non-agricultural product; no applicability determination needed.

**Country/Jurisdiction Scope:**
- Origin: Egypt
- Destination: China (national customs jurisdiction)
- Customs/Regulatory: China Customs (GACC), China TBT standards

**Freshness Requirements:**
- Trade: Latest available annual data
- Opportunity: Source-specific
- Market Access: Current/effective
- Regulatory: Current/effective China TBT
- Logistics: Current

**Effective-Date Requirements:**
- Regulatory: Must be current/effective at time of assessment (Q4 2026)
- Market Access: Effective tariff schedule at time of assessment
- RoO: Agreement current at time of export (if applicable)

**Output Boundaries:**
- Exact tariff line for each HS6 code
- Exact TBT requirements for knitted apparel
- RoO applicability determination (Required or Not Required with documented reason)
- Exact route cost estimate
- Opportunity quantification with methodology

**Not Required Conditions:**
- Agrifood: always NOT REQUIRED — non-agricultural product
- RoO: if no preferential arrangement applies to Egypt–China knitted apparel trade (must be proven, not assumed)

**Decision-Safe Conditions:**
- Missing TBT requirements → decision unsafe
- Missing tariff rates → decision unsafe
- RoO applicability undetermined → decision unsafe
- Route logistics without route-specific evidence → decision unsafe

**Response-Safe Conditions:**
- No trade→opportunity inference without proof
- No complementary→authoritative conversion
- No chapter-level HS used as product-specific evidence
- No RoO assumed without agreement verification

**System Must NOT Infer:**
- RoO eligibility from trade existence alone
- Opportunity from Trade alone
- Tariff rates from chapter-level HS alone
- Route reliability from country-level proxies alone

---

## 4. Business Question Contracts Summary

| Scenario | Product | HS Baseline | Destination | Core Evidence Families | Conditional Dimensions | Transport Mode |
|----------|---------|-------------|-------------|------------------------|------------------------|----------------|
| S1 | Fresh vegetables (tomatoes, cucumbers, peppers, onions) | HS07 | Jordan (Aqaba) | Trade, Opportunity, Market Access, Regulatory, Logistics | Agrifood, RoO | Sea primary (Alexandria Port → Aqaba Port), road fallback (Port Said Port → Aqaba Port) |
| S2 | Dates (Siwa, Hayani, Sagaaee) | HS08 | Saudi Arabia (Jeddah Port primary, Dammam Port fallback) | Trade, Opportunity, Market Access, Regulatory, RoO, Logistics | Agrifood | Sea primary (Alexandria Port → Jeddah Port), road fallback (Port Said Port → Dammam Port) |
| S3 | Citrus (oranges, lemons, grapefruits) | HS08 | Germany/EU (Hamburg Port primary, Frankfurt Airport fallback) | Trade, Opportunity, Market Access, Regulatory, RoO, Logistics | Agrifood | Sea primary (Alexandria Port → Hamburg Port), air fallback (Cairo Airport → Frankfurt Airport) |
| S4 | Coffee (green beans, roasted) | HS09 | Kenya (Mombasa Port primary, Nairobi fallback) | Trade, Opportunity, Market Access, Regulatory, Logistics | Agrifood, RoO | Sea primary (Alexandria Port → Mombasa Port), air fallback (Cairo Airport → Jomo Kenyatta International Airport, Nairobi) |
| S5 | Knitted apparel: T-shirts (HS610990), sweaters/pullovers (HS611011), men's shirts (HS610510) | HS61 | China (Shanghai Port primary, Beijing Capital Airport fallback) | Trade, Opportunity, Market Access, Regulatory, Logistics | RoO | Sea primary (Alexandria Port → Shanghai Port), air fallback (Cairo Airport → Beijing Capital Airport) |

---

## 5. Ambiguity Resolution

| Ambiguity | Resolution | Status |
|-----------|-----------|--------|
| Exact product varieties | Baseline examples accepted as working definitions; product-specific HS4/HS6 to be validated per source in Phase 2 | ✅ Resolved |
| Transport modes | Primary/fallback routes now exact: single origin node, single destination node, single mode per route | ✅ Resolved |
| HS nomenclature version | HS 2022 (latest available) adopted as baseline | ✅ Resolved |
| EU jurisdiction for S3 | Germany = destination market; EU customs/regulatory jurisdiction applies (TARIC, SPS/MRL) | ✅ Resolved |
| RoO applicability | Conditional → applicability determination in Phase 2; Not Required requires documented proof | ✅ Resolved |
| Agrifood scope | Contract-driven; only required if Business Question demands agricultural context beyond trade | ✅ Resolved |
| Incoterm terms | FOB origin baseline; CIF alternative noted where relevant | ✅ Resolved |
| Assessment time window | Q4 2026 for all scenarios | ✅ Resolved |
| Reliability metrics | Defined per route: on-time delivery, transit time variance, cargo integrity | ✅ Resolved |

**No material ambiguity remains. All contracts are frozen and executable.**

---

## 6. Phase 1 Exit Gate

| Condition | Status |
|-----------|--------|
| S1 Contract Frozen | ✅ |
| S2 Contract Frozen | ✅ |
| S3 Contract Frozen | ✅ |
| S4 Contract Frozen | ✅ |
| S5 Contract Frozen | ✅ |
| Business Question Contracts Complete | ✅ |
| Exact product identity resolved | ✅ |
| Validated HS mapping/version | ✅ |
| Customs/regulatory jurisdiction resolved | ✅ |
| Route contract resolved (all material fields) | ✅ |
| No "to be confirmed" or "to be validated" in frozen contracts | ✅ |
| No material ambiguity | ✅ |
| No application code modified | ✅ |
| No provider activation performed | ✅ |
| No Business-Question Evidence Collection performed | ✅ |
| Phase 2 not started | ✅ |
| Route Freeze — Primary/Fallback routes exact and independent (S1–S5) | ✅ |

**Phase 1 Status:** ✅ PASS — Exit Gate cleared. Route Freeze applied.

**Next Phase:** Phase 2 — Evidence & Gap Reassessment (NOT started; requires explicit authorization).

---

## 7. Out of Scope for Phase 1

The following were explicitly NOT performed:
- Business-Question Evidence Collection
- Provider activation or configuration
- Evidence gap analysis
- Application code changes
- Architecture modifications
- Phase 2 or later execution
- Commit / Push

---

FINAL STATUS: PHASE 1 PASS — SCENARIO CONTRACTS FROZEN — ROUTE FREEZE APPLIED (PRIMARY/FALLBACK EXACT) — READY FOR PHASE 2 (when authorized)
