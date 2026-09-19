# Commercial Readiness Completion — Final Master Plan

**Plan ID:** 1789733769109-commercial-readiness-completion
**Branch:** main
**Mode:** Plan Only — No Implementation
**Authority:** Master Remediation Commit 43d809e
**Prerequisite:** Master Remediation Phases 0-13 = Complete
**Purpose:** Final forensic hardening pass only.

---

# 0. Entry Integrity Gate

Entry Gate allows execution to proceed when:

1. `HEAD` is exactly `43d809e` OR a descendant of it with no unauthorized changes affecting governed truth.
2. Working tree / repository state is compatible with the Checkpoint.
3. No unauthorized application-code changes exist between `43d809e` and `HEAD`.
4. Known documentation drift is identified and recorded, but does NOT block entry.
5. No unproven capability claims are present in the repository.

**Critical:** Entry Gate does NOT require `CURRENT_STATUS.md` to already reflect Phase 0-13 closure.
Correcting `CURRENT_STATUS.md` is a Phase 0 activity, not a pre-condition for Phase 0.

Exit: Entry cleared for Phase 0.

## 0.1 Documentation Drift

Known Phase-13 documentation drift is an expected Phase-0 reconciliation item.

Known stale historical documents do NOT block entry when explicitly classified as historical/non-authoritative.

Entry Gate checks ACTIVE/CURRENT governance and capability claims, not every historical document.

Only NEW / UNCLASSIFIED / materially conflicting current claims block entry.

Fix once in Phase 0. Does not reopen Master Remediation.

## 0.2 Authority Priority
43d809e + phase-13-final-closure.md > CURRENT_STATUS.md (post-drift-fix) > older docs.

## 0.3 Blocking vs Non-Blocking
Documentation Drift only = fix once. Contract Conflict / Defect / Security = log + stop affected track only.

## 0.4 Domain-Scoped Authority Model

هذه الخطة تضيف **stricter commercial-readiness acceptance requirements** داخل نفس الحدود المعمارية لـMaster Remediation.

هي **لا تلغي** ولا **تعيد تعريف** الـarchitecture baseline، ولا تضعف أي governance أو ترخيص أو التزام قانوني موجود.

### Binding Precedence by Domain (من الأعلى إلى الأدنى)

```text
1. Applicable legal / licensing / contractual obligations
2. Master Remediation architecture + protected governance baseline (commit 43d809e)
3. Existing approved provider/source governance
4. Commercial Readiness Completion stricter acceptance rules
5. Historical baselines / scorecards = reference only
```

### Permissible Actions by Commercial Readiness Rules

Commercial Readiness rules MAY:
* Add stricter acceptance criteria within the same architectural boundaries.

Commercial Readiness rules MUST NOT:
* weaken
* override
* cancel
* reinterpret
* bypass
any:
* architecture governance
* provider admission governance
* source governance
* licensing constraint
* legal obligation
* closed-work-package contract

### Conflict Escalation Rule

Any real unresolved conflict between levels:
1. BLOCK the affected track
2. RECORD the conflict
3. ESCALATE to governance
4. AWAIT governance decision

Do not silently choose one rule over another.
Do not self-authorize governance changes inside this plan.

### Authority Documents

* `43d809e` = governance baseline authority
* `phase-13-final-closure.md` = closure evidence
* `CURRENT_STATUS.md` and similar documents = status mirrors, not higher authority

---

# 1. Objective

Move S1-S5 from Not Ready to READY through:
Business Question -> Required Inputs -> Required Evidence Set -> Proven Source -> Proven Evidence -> Scope Validation -> Freshness -> Provenance -> Minimum Sufficiency -> Business Question Ready -> Decision-Safe -> Response-Safe -> READY.

READY is not merely absence of errors. READY is not granted with missing Core Evidence.

---

# 2. Basic Rule

Complementary != Authoritative != Core Minimum Sufficiency.
Complementary sources can support context, show limitations, and support manual research. They do NOT close Core Commercial Readiness when the Business Question requires authoritative or proven equivalent evidence.

---

# 3. Current Truth

## 3.1 Providers

| Provider | Operational State | Capability Proven | Notes |
|----------|-------------------|-------------------|-------|
| UN Comtrade | Operational — Partial | Partial | Preview-limit constraints apply |
| World Bank LPI | Operational — Partial | Partial | Country-level only |
| Company Knowledge | Operational — Internal | Partial | Internal data only |
| FAOSTAT | Inactive | No | Credentials configured; runtime/data availability unverified |
| Moaah | Inactive | No | Credentials/runtime verification required |
| TradeData | Inactive | No | Credentials/runtime verification required |
| ZATCA | Inactive | No | Credentials/runtime verification required |
| GCC-Stat | Inactive | No | Credentials/runtime verification required |
| Regulations Provider | Inactive | No | Authoritative data source/file required |
| WTO ePing | Complementary | N/A | Complementary under existing governance decision |

**Operational ≠ Capability Proven.** A provider is Capability Proven ONLY after:
Credentials -> Runtime activation -> Reachable -> Returns Data -> Correct mapping -> Correct scope -> Commercial-use clearance -> Proven.

**Company Knowledge لا يُستخدم لإثبات External Market Facts إلا عندما يكون السؤال متعلقًا فعلًا ببيانات الشركة الداخلية.**

## 3.2 Current Family State

| Family | الحالة الحالية |
|--------|----------------|
| Trade Intelligence | Partial |
| Market Opportunity | Gap |
| Market Access | Gap |
| Regulatory/SPS-TBT | Gap |
| Rules of Origin | Gap |
| Agrifood | Gap / FAOSTAT Inactive (Capability Proven = No) |
| Logistics | Partial — Country level only |

الأرقام التاريخية لا تستخدم كـFinal Gate.

---

# 4. Commercial Readiness Contract

Two levels:
Family Readiness: Capability Proven -> Scope Ready -> Country/Product Ready
Scenario Readiness: Country/Product/Route Ready -> Business Question Ready -> Decision-Safe -> Response-Safe

Family Ready does NOT automatically mean Scenario Ready.

---

# 5. Scenario Contract

S1: Egypt -> Jordan / Vegetables / HS07
S2: Egypt -> Saudi Arabia / Dates / HS08
S3: Egypt -> Germany / Citrus / HS08
S4: Egypt -> Kenya / Coffee / HS09
S5: Egypt -> China / Textiles / HS61

These are Test Profiles, NOT licenses to use Chapter-level scope as substitute for Product-level evidence.

---

# 6. Scenario Input Sufficiency Gate

Before requesting Evidence, the Scenario must contain minimum inputs required by its sources.

Product: When Tariff, Regulation, SPS/TBT, or Rules of Origin are needed, the system must use the destination authority's effective tariff nomenclature at the granularity actually required by the authoritative source. HS4/HS6 may be sufficient for some evidence dimensions. Chapter-level evidence may support broad trade baselines only. Chapter-level evidence must never substitute for product/tariff-line evidence when the Business Question requires finer specificity. No assumptions allowed.

Record for each validated mapping:

* HS version / nomenclature
* mapping basis
* mapping evidence
* destination tariff-line level where applicable

Route: When Route-level Logistics is needed, define: Origin, Destination, Transport Mode, Relevant Port/Node, Cargo characteristics when materially required. Route Cost cannot be derived from Country LPI alone.

---

# 7. Scenario Evidence Model

For each Scenario, create one Evidence Matrix:

| Evidence | Required? | Minimum Evidence | Scope | Freshness | Authority | Proven? |
|----------|-----------|-----------------|-------|-----------|-----------|---------|
| Trade | per question | Verified bilateral trade | Product/HS + countries | Latest applicable | Authoritative preferred | |
| Opportunity | per question | Genuine opportunity signal | Market + product | Source-specific | Authoritative / validated composite | |
| Market Access | per question | Tariff + applicable procedures | Country + tariff line | Effective/current | Authoritative | |
| Regulatory | per question | Product-country technical requirements | Jurisdiction + product | Current/effective | Authoritative | |
| RoO | conditional | Agreement + eligibility + criteria + docs | Product + agreement | Current | Authoritative | |
| Agrifood | for agricultural products | Agriculture-specific evidence | Commodity + market | Question-specific | Authoritative / validated | |
| Logistics | when needed | Route cost + time + reliability | Exact route | Current/applicable | Route source | |

Required? is determined by Business Question, not by family name.

---

# 8. Minimum Sufficiency - Market Opportunity

Closing the gap requires ONE of two paths:

Path A: A source/method proven to deliver:
Opportunity / Potential / Untapped Demand / Market Attractiveness

Path B: A deterministic composition of independent evidence:
Demand + Growth / Import Dynamics + Relevant Opportunity Signal
with clear methodology, full provenance, and NO conversion of Trade alone into Opportunity.

No new formula is imposed if incompatible with current BI.

### Opportunity Terminology

Demand Gap:
A claim requiring a deterministic documented methodology.

Market Attractiveness:
A numeric score only if a governed scoring methodology exists.

Opportunity Quantification:
Quantitative only when a proven deterministic method and inputs exist.

Otherwise:
report evidence-backed indicators without inventing scores, formulas, or unsupported quantified gaps.

Keep the rule:
Trade alone MUST NOT become Opportunity.

### Opportunity Composite Rule (Path B)

A composite may be used only when:

* all required inputs are individually proven
* every input satisfies the Business Question evidence tier
* methodology is deterministic and documented
* provenance exists for every input
* no input is silently upgraded from Complementary to Authoritative
* the composite does not derive Opportunity from Trade alone

A complementary input may NOT elevate itself into authoritative evidence.

If the Business Question requires authoritative evidence, a composite containing only complementary evidence does NOT close the Core gap.

---

# 9. Minimum Sufficiency - Market Access

To close Core Market Access, prove:
Tariff / Duty + Relevant Entry Procedure + Permit/Licensing when applicable + Preferential treatment when applicable
with Exact tariff scope + Effective date + Target country + Product/HS.

Complementary does NOT close Core Sufficiency.

---

# 10. Minimum Sufficiency - Regulatory/SPS-TBT

Core Regulatory Evidence must be:
Current + Authoritative + Product-specific + Jurisdiction-specific + Effective

Includes when applicable: SPS, TBT, MRL, Conformity, Plant/food safety, Technical requirements, Effective validity.

WTO ePing / Codex / IPPC remain Complementary under current governance unless a new path meeting re-evaluation conditions emerges. ePing is NOT reopened simply because a gap exists.

---

# 11. Minimum Sufficiency - Rules of Origin

For conditional dimensions (RoO, permits/licenses, SPS/TBT sub-requirements, preferential treatment), the path must be:

Contract says Conditional -> Applicability Determination -> Applicability Evidence -> Required / Not Required decision

First prove: Is preferential treatment / origin proof actually relevant to the Business Question?
Then when applicable: Agreement + Eligibility + Origin Criterion + Required Documentation.

If proven Not Required for this Business Question: state "Not Required" with documented reason.
Absence of provider does NOT mean Not Required.
Source unavailable does NOT mean Not Required.

---

# 12. Minimum Sufficiency - Agrifood

Agrifood is Core only when the frozen Business Question Contract requires it.

For agricultural products:
do not automatically require the whole Agrifood family.

When Agrifood is Core, define exactly which dimensions are required:

* prices
* production/supply
* agricultural indicators
* events
  etc.

This must be contract-driven.

FAOSTAT must prove: Credentials -> Runtime activation -> Reachable -> Real Data -> Correct mapping -> Correct scope -> Commercial-use clearance -> Capability Proven. Historical validation alone is NOT current operational proof. FAOSTAT cannot be used for Market Opportunity unless explicitly proven as Opportunity evidence or part of an approved method.

---

# 13. Minimum Sufficiency - Logistics

World Bank LPI proves: Country-level Logistics Performance only.
It does NOT prove: Route Cost, Route Transit Time, Route Reliability.

Route-level closure requires evidence specific to the route itself.

### Route Contract Material Fields

When Logistics is Core, the Route Contract must explicitly include:

* exact origin node
* exact destination node
* transport mode
* cargo characteristics
* shipment weight/volume or material shipment assumptions
* Incoterm when materially required
* temperature/control requirements when relevant
* assessment date/time window when relevant
* reliability metric definition

Do not allow a frozen contract to contain "to be confirmed."

Country-level LPI can never satisfy route-level reliability.

---

# 14. Minimum Sufficiency - Trade Intelligence

UN Comtrade is NOT accepted or rejected based on the 500 limit alone.
Measure: Does the requested business query receive the complete evidence it needs?
If: Target Query -> Required rows -> Complete retrieval -> Correct filters -> Correct HS scope -> Correct period
Then: preview limit may be non-blocking.
If the limit prevents Business Question completion: Not Ready -> seek Existing Provider Enhancement or Alternative Provider.

---

# 15. Provider Strategy

## 15.1 Mandatory Closure Order

الترتيب الإجباري قبل Considering New Provider:

```text
1. Existing Provider Configuration
2. Existing Provider Activation
3. Existing Provider Repair
4. Scope Correction
5. Existing Provider Enhancement
6. Source Composition
7. New Provider Evaluation
8. Governance Approval
9. Admission
10. Implementation / Activation
11. Capability Proven
12. Scenario Revalidation
```

## 15.2 Ceiling Checkpoint

قبل الانتقال إلى New Provider Evaluation (الخطوة 7):

* تحقق من Provider Ceiling Rule (القسم 16)
* احسب العدد الحالي للـoperational production providers
* إذا كان العدد <= 7: ماشي
* إذا كان العدد > 7 أو سيصبح > 7: يتطلب Ceiling Expansion Governance Approval

لا يتم القفز إلى New Provider بلا حاجة.
لا يُضاف provider جديد تلقائيًا لمجرد وجود gap.

---

# 16. Provider Ceiling Rule

## 16.1 Ceiling Definition

Current Operational Production Provider Ceiling: **7 external operational providers**.

هذا هو **Governance Control** وليس **Commercial Readiness Target**.

## 16.2 Counting Rules

ما يُحتسب toward السقف:
* External operational production providers فقط

ما لا يُحتسب:
* Company Knowledge (internal)
* Knowledge Graph (infrastructure)
* Search infrastructure (Research only)
* Web-only manual sources (Complementary)

## 16.3 Activation vs Addition

* Activating an existing inactive provider = **لا يُحتسب** كإضافة جديدة
* Adding a NEW external provider = **يُحتسب** كإضافة واحدة

### Activation Ceiling Edge Case

Activating an existing inactive provider does NOT count as a NEW provider addition.

However, the resulting operational production portfolio MUST still comply with the ceiling.

Before activating an existing provider:

* calculate resulting operational provider count.

If activation causes count > 7:

* activation cannot proceed under ordinary activation flow;
* either deactivate/merge another provider;
* OR obtain Ceiling Expansion Governance Approval BEFORE activation.

This rule applies equally to: FAOSTAT, Moaah, TradeData, ZATCA, GCC-Stat, Regulations, and any future inactive existing provider.

"does not count as a new addition" does NOT mean "does not count toward the resulting operational ceiling."

## 16.4 Expansion Requirements

قبل تجاوز السقف 7، يجب إثبات **جميع** الشروط التالية:

1. **Documented Knowledge Need** مع تأثير قرار واضح
2. **Marginal Value > 0** مثبت
3. **Operational Justification** موثق
4. **No existing provider/composition/fallback** يمكنه تغطية الحاجة within governance
5. **Governance Approval** BEFORE admission/implementation

## 16.5 Expansion Decision Rules

* Expansion **لا يُرفض** بسبب الرقم 7 وحده إذا كانت الأدلة تثبت الضرورة
* Expansion **لا يُوافق** بسبب وجود gap وحده بدون الشروط أعلاه
* Expansion هو **قرار حوكمة** يُستند إلى Knowledge Coverage need، وليس شرط مسبق يعرقل Commercial Readiness

## 16.6 Counting Unit

Each distinct external operational production provider/source identity counts once, regardless of how many endpoints or evidence dimensions it serves.

A provider with code/configuration/inactive status does not count.

## 16.7 Approval Requirements

New provider within available slots:
* still requires Provider Admission Governance Approval
* does not require ceiling expansion if count remains <= 7

Provider that causes count > 7:
* requires all five expansion conditions PLUS explicit governance approval before admission/implementation
* approval authority must be explicit
* approval evidence must be recorded
* admission evidence must be recorded

Do not permit Kilo/local execution to approve ceiling expansion by itself.

## 16.8 Plan-Wide Application

هذه القاعدة تُطبق في:
* Provider Strategy (القسم 15)
* Source Admission (القسم 18)
* Execution Phases (القسم 26) حيث يظهر provider gap
* Acceptance / Exit Gate (القسم 29/30)

---

# 17. New Provider Rule

## 17.1 Pre-Candidate Evidence Gate

New Provider Evaluation may begin ONLY after ALL of the following are proven:

1. Required Core Evidence is proven necessary by the Scenario Contract
2. Existing-provider closure path exhausted
3. Existing composition exhausted
4. Existing equivalent fallback exhausted
5. Candidate class is admissible under current governance
6. Licensing/admission path can be assessed
7. Ceiling impact can be assessed
8. Required governance authority is identified

## 17.2 Candidate Evaluation and Capability Qualification

Pre-Candidate Evidence Gate -> Candidate Evaluation -> Candidate Capability Qualification -> Provider Ceiling / Governance Review -> Governance Approval -> Admission -> Implementation / Activation -> Capability Proven -> Scenario Revalidation

"New Provider adds material evidence capability" is determined during Candidate Capability Qualification, NOT before Candidate Evaluation.

## 17.3 New Provider Path

New Providers are allowed when actually needed.
If Commercial Readiness requires a new provider:
Knowledge Gap -> Candidate Evaluation -> Pre-Candidate Evidence Gate -> Candidate Capability Qualification -> Provider Ceiling / Governance Review -> Governance Approval -> Admission -> Provider Implementation/Activation -> Capability Proven

If count exceeds 7:
Documented Knowledge Need + Marginal Value + Operational justification -> Ceiling Expansion Governance Approval

---

# 18. Source Admission

Preferred: REST / SDMX / JSON
Also evaluate any reproducible machine-readable access including bulk datasets if integrable within current contracts without inventing Architecture.

## 18.1 Ceiling Checkpoint

أي admission لـexternal operational provider جديد يتطلب:
* تحقق من Provider Ceiling Rule (القسم 16)
* Ceiling Expansion Governance Approval إذا لزم الأمر
* Governance Approval قبل admission/implementation

## 18.2 Format Conflict Resolution

When access format conflicts with current Provider Admission rules:
1. Identify the conflict
2. Block the affected admission
3. Obtain explicit governance decision
4. Proceed only under the approved decision

A governance correction is NOT an implementation-side override.
No plan clause self-authorizes governance changes.

Web-only manual sources remain Complementary unless an automated/legal/reproducible path supported by current contracts exists.

---

# 19. Commercial Licensing Gate

Do NOT use: Likely Allowed, Free = Commercial, Open Data = Automatically Commercial.

Each source must document:
Current Official Terms + Commercial Use + Redistribution/Storage + Attribution + API/Data Usage Restrictions + Rate/Quota Restrictions + Derivative-use Restrictions when applicable.

Status: Cleared / Pending / Restricted / Not Cleared.
Not Cleared = does NOT enter Core Commercial Readiness.

Two use cases must be cleared separately where material:
- DEM Runtime Use
- User-facing / Redistribution Use

### Licensing Boundary

Complementary status does NOT waive:

* terms of use
* storage restrictions
* attribution obligations
* redistribution restrictions
* API/data restrictions
* derivative-use restrictions

Complementary ≠ License-Free.

No source may be used outside its legally/permissibly cleared use scope.

---

# 20. Data Integrity Gate

For each Core Evidence verify:
Schema, Country, Product, HS, HS Version, Time, Effective Date, Units, Currency, Geographic Scope, Granularity, Duplicates, Missingness, Aggregation, Transformation, Version, Source Identity.

HTTP 200 does NOT imply Valid Data.

---

# 21. Scope / Freshness / Provenance

For each Evidence:
Source -> Retrieval -> Evidence -> Scope -> Freshness -> Finding -> Business Fact -> Decision / Response

Freshness is NOT a fixed value like 12 months for all sources.
Evaluate based on: Data type, Business Question, Source update cycle, Effective period.
Regulatory evidence must prove currently effective when current validity is material.

---

# 22. Conflict Handling

For each Core Evidence Family, define:
* authoritative source class
* scope match requirement
* effective-date requirement
* freshness requirement
* tie-break rule

General rule: same-scope authoritative evidence takes precedence over lower-authority secondary/complementary evidence.

When Evidence conflicts: Authority + Scope Match + Freshness + Evidence Quality applied per documented rules.
No automatic averaging of conflicting values.
If no defensible authority resolution exists and the conflict affects Core: Scenario = NOT READY.
If conflict affects Core Decision and is resolved: Scenario = Not Ready until resolved or impact proven non-material.

---

# 22A. Core Evidence Authority Matrix

For each Core Evidence Family, the following authority attributes MUST be defined:

| Evidence Family | Authoritative Source Class | Scope Requirement | Freshness Requirement | Tie-Break Rule |
|-----------------|---------------------------|-------------------|----------------------|----------------|
| Trade | Official bilateral trade authority (e.g., UN Comtrade, national statistical agencies) | Product/HS + countries + period | Latest available period | Same-scope official source > secondary source |
| Market Opportunity | Proven opportunity source or governed deterministic composite | Market + product + time horizon | Source-specific | Authoritative/proven opportunity evidence > trade-only inference |
| Market Access | Destination tariff/customs authority | Exact tariff scope + target country + product/HS | Effective/current | Official tariff schedule > secondary source |
| Regulatory/SPS-TBT | Competent jurisdictional authority / applicable official instrument | Product + jurisdiction + specific requirement | Current/effective | Official instrument > secondary interpretation |
| Rules of Origin | Official agreement / competent authority | Product + agreement + origin criterion | Current validity | Official agreement text > secondary summary |
| Agrifood | Official agricultural/statistical source class | Commodity + market | Source-specific | Official source > secondary source |
| Logistics | Route-specific authoritative/licensed source | Exact route + mode + cargo | Current | Route-specific source > country-level proxy |

General rule: Same-scope authoritative evidence takes precedence over lower-authority secondary/complementary evidence.

If authority cannot be defensibly resolved and the conflict affects Core: Scenario = NOT READY.

---

# 23. Resilience

For each Core Evidence Path document:
Primary source, Failure behavior, Approved fallback (if any), Authentication dependency, Quota/rate limits, Operational availability, Licensing.

### Fallback Equivalence Rule

Fallback is equivalent only if it satisfies the same Business Question evidence contract for:
* same evidence dimension
* sufficient scope
* sufficient granularity
* valid freshness
* valid effective date where relevant
* acceptable authority tier
* complete provenance
* commercial-use clearance

Another source exists is not sufficient.

NOT allowed: Primary unavailable -> unrelated source -> fabricated completion.

### Fallback Safety

A fallback preserves Scenario READY only after the fallback itself is:

* Proven
* scope-valid
* freshness-valid
* authority-valid
* provenance-complete
* commercially cleared

"Fallback exists" alone is never sufficient.

---

# 24. Research / Evidence / BI Integration

## 24.1 Evidence Authority vs Access/Integration Tier

"Authoritative" describes the authority/quality of the evidence/source.

"Production / Complementary / Manual / Candidate" describes the integration/admission state.

These concepts are NOT interchangeable.

Examples:

* Official source can still be Complementary if it does not meet current integration/admission requirements.
* Complementary status does NOT elevate evidence to Core.
* Production integration does NOT automatically make every returned result authoritative.

## 24.2 Research / Evidence / BI Integration

Research: Business Question -> Required Evidence Dimensions -> Correct Source Discovery
Evidence: Provenance, Scope, Freshness, Source identity, Retrieval metadata
BI: Must distinguish Supported / Partial / Unsupported / Limitation.
Must NOT convert: Missing -> Empty -> Inferred Fact
Must NOT convert: Trade -> Opportunity unless Opportunity Evidence/Method is proven.

---

# 25. Decision / Strategic / Response Boundary

Current architecture remains: Knowledge Plane -> Evidence / BI -> Decision / Strategic Context

NO new Decision Engine, Reasoning Engine, or Planner.
Strategic Reasoning interprets evidence; does not create it.
ResponseBuilder does not create unsupported claims.
Avatar is interface only.

---

# 26. Execution Phases

## Phase 0 - Entry Truth Alignment
Reconcile repository/document truth with 43d809e. Close documentation drift once. Freeze Scenario SET (IDs + baseline scope).
Exit: Current Truth consistent.

## Phase 1 - Scenario Contract Completion
Normalize exact Product/HS scope. Normalize destination jurisdiction. Define route inputs where logistics is Core. Define Business Question for each Scenario per template in القسم 36. Build Business Question Contract per scenario.
Exit: Each Scenario has executable inputs and frozen Scenario Contract.

### Phase 0 vs Phase 1 Freeze Distinction

| Phase | Freeze |
|-------|--------|
| Phase 0 | Scenario SET (IDs + baseline scope) فقط |
| Phase 1 | Scenario Contract الكامل (بعد normalization و Business Question definition) |

NOT allowed: Phase 0 claims full Scenario Contract freeze.

## Phase 2 - Evidence & Gap Reassessment
For each Scenario: Question -> Required Evidence -> Current Source -> Proven? -> Gap
Exit: Evidence Matrix complete for all scenarios.

## Phase 3 - Existing Provider Closure

Existing providers follow their provider-specific approved closure path.

For Regulations: first execute the Regulations Decision Gate:

* determine whether Regulatory evidence is Required
* assess existing sources
* assess complementary alternatives
* determine whether local regulations data is actually needed
* determine source, update, validation, provenance, licensing requirements

Only then execute the approved activation/data path.

FAOSTAT, Moaah, TradeData, ZATCA, GCC-Stat, Regulations.
For each: Configure -> Activate -> Verify -> Prove
Note: Activating existing inactive providers does NOT count toward Provider Ceiling (القسم 16.3), but the resulting operational count must still comply with the ceiling (see Activation Ceiling Edge Case in القسم 16.3).
Exit: All closeable via existing sources are actually closed.

## Phase 4 - Market Opportunity Closure
Evaluate existing sources, dedicated opportunity sources, governed composite method.
If new provider needed: section 16 / applicable ceiling checkpoints BEFORE admission.
Admit new provider only if necessary.
Exit: Opportunity Core Evidence Proven for each Scenario needing it.

## Phase 5 - Market Access + Rules of Origin Closure
Tariff, Procedures, Preferential treatment, Agreement applicability, Origin criteria/documentation.
If new provider needed: section 16 / applicable ceiling checkpoints BEFORE admission.
Exit: All Core Market Access / RoO Evidence Proven or NOT_REQUIRED_PROVEN.

## Phase 6 - Regulatory / SPS-TBT Closure
Current, authoritative, product-specific, jurisdiction-specific, effective evidence. ePing remains Complementary-only under existing governance.
If new provider needed: section 16 / applicable ceiling checkpoints BEFORE admission.
Exit: Core Regulatory Evidence Proven for each Scenario needing it.

## Phase 7 - Agrifood + Logistics Closure
FAOSTAT/Agrifood activation and verification. Route-level logistics evidence.
If new provider needed: section 16 / applicable ceiling checkpoints BEFORE admission.
Exit: Agrifood and Route Evidence Proven where required.

## Phase 8 - Trade Intelligence + Knowledge Integration
Validate Comtrade sufficiency. Verify Research -> Evidence -> BI. Verify provenance/freshness/scope.
Exit: Required Knowledge Paths operational and coherent.

## Phase 9 - Scenario Commercial Revalidation

### Fixture Boundary

Fixtures may validate control-flow behavior only.
Fixtures must never be used as evidence that a production provider is operational, current, licensed, or capable.
Production readiness requires real proven evidence.

Re-run S1-S5 testing: positive path, missing evidence, provider failure, stale evidence, wrong scope, conflicting evidence, complementary-only, Trade->Opportunity anti-pattern, fixture->production anti-pattern.
Exit: Each Scenario achieves Minimum Sufficiency.

## Phase 10 - Decision-Safe / Response-Safe Acceptance
Test: Evidence -> BI -> Decision -> Strategic Reasoning -> ResponseBuilder -> IntentContent -> Avatar
Exit: No unsupported decision / strategic conclusion / response claim.

## Phase 11 - Final Commercial Readiness Closure

### Phase-Level Contract Amendment Control

After Phase 1 freezes a Scenario Contract, later phases may NOT silently alter:

* Business Question
* Core Evidence
* product identity
* jurisdiction
* route
* minimum sufficiency

unless a documented, governance-compatible Contract amendment is required and approved.

Any material amendment:

* is recorded
* cannot weaken readiness criteria merely to obtain READY
* re-triggers affected evidence/revalidation gates.

Final judgment: S1 = READY, S2 = READY, S3 = READY, S4 = READY, S5 = READY
If any Scenario remains Core Not Ready: PLAN = BLOCKED.

---

# 27. Scenario READY Definition

Scenario = READY only if:
Required Inputs Valid + Required Core Evidence Complete + Evidence Proven + Scope Valid + Freshness Valid + Provenance Valid + Commercial Use Cleared + Minimum Sufficiency Met + Business Question Ready + Decision-Safe + Response-Safe

Missing Core Evidence -> NOT READY. No exceptions.

Non-Core Limitations are allowed only if they do NOT change the commercial answer, reduce decision safety, or prevent user understanding of scope.

---

# 28. Final Commercial Readiness Definition

DEM Commercial Readiness = All Required Core Evidence + All 5 Scenarios READY + Decision-Safe + Response-Safe

NOT measured by: Provider Count, Portfolio Average Score, Family Score.

---

# 29. Acceptance Criteria

## Scenario Level (per S1-S5)
- [ ] Required Inputs valid
- [ ] Exact product/HS scope adequate
- [ ] Required Evidence identified
- [ ] Core Evidence Proven
- [ ] Country/Jurisdiction correct
- [ ] Route scope correct when applicable
- [ ] Freshness valid
- [ ] Provenance complete
- [ ] Commercial use cleared
- [ ] Minimum Sufficiency PASS
- [ ] Business Question Ready
- [ ] Decision-Safe
- [ ] Response-Safe
- [ ] Final status = READY

## Safety
- [ ] No overclaim
- [ ] No unsupported recommendation
- [ ] No trade->opportunity inference
- [ ] No complementary->authoritative conversion
- [ ] No fixture->production evidence
- [ ] No missing-source fabrication
- [ ] No stale evidence as current
- [ ] No wrong-scope evidence
- [ ] No fabricated fallback

## Architecture
- [ ] No new Decision Engine
- [ ] No new Reasoning Engine
- [ ] No new Planner
- [ ] No BI redesign
- [ ] No Avatar redesign
- [ ] No Multi-Agent
- [ ] No Knowledge Graph changes
- [ ] No reopening closed WPs
- [ ] Provider Ceiling Rule compliance
- [ ] No ceiling expansion without Governance Approval

---

# 30. Final Exit Gate

Repository Truth Consistent + Scenario Set Frozen + Full Scenario Contract Frozen for every scenario + Exact product identity resolved + Validated HS mapping/version + Customs/regulatory jurisdiction resolved + Route contract resolved where Logistics is Core + Business Question Contract frozen + Applicability decisions proven for all conditional dimensions + Core Evidence Proven + no unresolved evidence-state ambiguity + no unresolved scope ambiguity + no unresolved freshness/effective-date issue + no unresolved provenance issue + no unresolved licensing blocker + no unresolved Core provider failure + no unsupported composite methodology + no unresolved authority conflict + Decision-Safe + Response-Safe + Provider Ceiling Compliant + Governance Approvals recorded where required + S1 READY + S2 READY + S3 READY + S4 READY + S5 READY = COMMERCIAL READINESS COMPLETE

**إذا بقي Scenario واحد Core Not Ready → PLAN = BLOCKED**
**إذا كان هناك Ceiling Expansion بدون Governance Approval → PLAN = BLOCKED**
**إذا كان هناك unresolved governance conflict → PLAN = BLOCKED**

---

# 31. Definition of Done

Close only when: All 5 Scenarios = READY, and every Core Knowledge Gap is Closed or Proven Not Required, and no unresolved Provider Failure affecting any Required Core Evidence Path remains.

A failure in a non-required provider does not block readiness.
A failed primary with a fully equivalent governed fallback may remain as an operational incident without invalidating Scenario READY.

Complementary Accepted is NOT a substitute for Core Evidence.

---

# 32. Out of Scope

- Reopening Master Remediation
- Architecture redesign
- Multi-Agent
- Knowledge Graph
- Second Decision Engine / Reasoning Engine / Planner
- Avatar/BI redesign
- Changing Business Promise to reach READY
- Reducing Minimum Sufficiency
- Declaring Commercial Readiness with Scenario not ready
- Source Control / Commit during planning

---

# 33. Reporting Standard

Every Kilo report is in Arabic and contains only:
1. What was verified.
2. What was closed.
3. What needs execution.
4. Evidence used.
5. Status of each Scenario.
6. Required Governance Approval.
7. Exit Gate.
8. Status: PASS or BLOCKED.

No new phase is created automatically.

---

# 34. Principle of Completion

The goal is NOT: More Providers, Higher Coverage Score, More Sources.
The goal is: Can DEM answer the required business question with correct evidence, for correct scope, at correct time, safely, and without fabrication?

If YES for all 5 Scenarios -> Commercial Readiness Complete.
If NO -> do not change the meaning of READY; close the real reason until it becomes YES.

---

# 35. Scenario Contract Baselines — Pre-Freeze Profiles

S1-S5 shown in this section are baseline profiles only.

They are NOT frozen Contracts at plan-entry time.

Phase 0 freezes: Scenario Set only.

Phase 1 resolves and freezes:

* exact product identity
* exact product attributes materially required
* validated HS mapping
* HS nomenclature/version
* tariff-line granularity where applicable
* customs/regulatory jurisdiction
* route
* mode
* cargo/shipment assumptions
* Business Question Contract
* evidence dimensions
* Core/non-Core
* conditional applicability
* freshness/effective-date requirements
* output boundaries

Any unresolved material field:
Scenario = BLOCKED
and Scenario Contract is NOT frozen.

Never invent an exact product, HS code, route, or mode.

## Contract Template

Each Scenario Contract must include:
* Scenario ID
* Origin country / port / node
* Destination country / port / node
* Exact product identity (not chapter label)
* Product description
* Validated HS mapping (not chapter label alone)
* Required HS granularity per evidence dimension
* Business Question (operationally testable)
* Required evidence dimensions
* Core vs non-core evidence
* Country/jurisdiction scope
* Route/logistics scope
* Transport mode (where materially relevant)
* Relevant port/node (where materially relevant)
* Cargo characteristics (where materially relevant)
* Freshness requirements per dimension
* Effective-date requirements
* Product/jurisdiction specificity requirements
* Required output/finding boundaries
* Conditions under which a dimension is Not Required

chapter-level label alone (HS07/HS08/HS09/HS61) is NOT sufficient for product-specific commercial readiness when the question requires finer granularity.

---

## S1 - Egypt -> Jordan / Fresh Vegetables / HS07

**Scenario ID:** S1
**Origin:** Egypt — Alexandria Port
**Destination:** Jordan — Aqaba Port
**Exact Product Identity:** Fresh vegetables: tomatoes, cucumbers, peppers, onions
**Product Description:** Perishable agricultural produce requiring cold chain logistics
**Validated HS Mapping:** HS07 (chapter) — baseline; HS4/HS6 required for tariff/regulatory specificity
**HS Nomenclature / Version:** HS 2022 (latest available)
**HS Granularity per Dimension:**
* Trade: HS07 chapter acceptable for bilateral baseline
* Tariff/Market Access: HS4/HS6 required for exact duty rate
* Regulatory/SPS: HS4/HS6 required for product-specific SPS requirements
**Business Question:** What is the export feasibility for fresh Egyptian tomatoes (HS070200), cucumbers (HS070700), peppers (HS070960), and onions (HS070310) to Jordan (Aqaba), including: (a) current bilateral trade volume and 3-year trend for HS07 vegetables, (b) demand gap and import dynamics for fresh vegetables in Jordan, (c) Jordan tariff duty rate and entry procedures for HS070200/070700/070960/070310, (d) Jordan SPS requirements for fresh vegetables, (e) route logistics cost/time/reliability from Alexandria/Port Said to Aqaba?
**Required Evidence:** Trade, Opportunity, Market Access, Regulatory, Agrifood, Logistics
**Core Evidence:**
* HS-level bilateral trade (Egypt–Jordan vegetables, HS07)
* Jordan tariff/procedures for HS070200/070700/070960/070310 (product-specific)
* Jordan SPS requirements for fresh vegetables (product-specific)
* Route logistics: Alexandria/Port Said → Aqaba (sea primary, road alternative)
* Opportunity evidence: demand gap + import dynamics (deterministic composite or proven source)
**RoO:** Conditional — Agadir Agreement. Applicability: must be proven first. If applicable: agreement + eligibility + origin criterion + documentation. If not applicable: Not Required with documented reason.
**Route Contract:**
* Primary Route: Origin: Alexandria Port; Destination: Aqaba Port; Transport mode: Sea
* Fallback Route: Origin: Port Said Port; Destination: Aqaba Port; Transport mode: Road
* Cargo characteristics: Perishable, requires cold chain (0–4°C), ventilated containers for ethylene-sensitive produce
* Shipment assumptions: FCL or LCL; standard refrigerated container (reefer)
* Incoterm: FOB Alexandria Port (baseline); CIF Aqaba if cost includes freight
* Temperature/control requirements: Cold chain mandatory; temperature monitoring required
* Assessment time window: Q4 2026
* Reliability metric: On-time delivery rate; transit time variance; cold chain integrity (temperature excursion incidents)
**Freshness:** Trade: latest available annual; Opportunity: source-specific; Regulatory: current/effective; Logistics: current
**Effective Date:** Regulatory: must be current/effective at time of assessment (Q4 2026); Market Access: effective at time of assessment
**Output Boundaries:** Exact tariff line for each HS4/HS6 code; exact SPS requirements; exact route cost estimate; opportunity quantification with methodology; RoO eligibility determination
**Not Required Conditions:**
* Agrifood: if Business Question does not require agricultural market indicators beyond trade volume
* RoO: if no preferential arrangement applies to Egypt–Jordan vegetable trade (must be proven, not assumed)

---

## S2 - Egypt -> Saudi Arabia / Dates / HS08

**Scenario ID:** S2
**Origin:** Egypt — Alexandria Port
**Destination:** Saudi Arabia — Jeddah Port
**Exact Product Identity:** Dates: Siwa, Hayani, Sagaaee varieties
**Product Description:** Dried fruit with specific quality grades and packaging standards for GCC market
**Validated HS Mapping:** HS08 (chapter) — baseline; HS4/HS6 required for tariff/regulatory specificity
**HS Nomenclature / Version:** HS 2022 (latest available)
**HS Granularity per Dimension:**
* Trade: HS08 chapter acceptable for bilateral baseline
* Tariff/Market Access: HS4/HS6 required for exact duty rate
* Regulatory/SPS: HS4/HS6 required for product-specific SPS requirements
* RoO: HS4/HS6 for origin criterion application
**Business Question:** What is the export feasibility for Egyptian dates — Siwa (HS080410), Hayani (HS080410), Sagaaee (HS080410) — to Saudi Arabia (Jeddah/Dammam), including: (a) current bilateral trade volume and 3-year trend for HS0804, (b) demand gap and import dynamics for dates in Saudi Arabia, (c) Saudi tariff duty rate and entry procedures for HS080410, (d) Saudi SPS requirements for dates, (e) GAFTA RoO eligibility and documentation for Egyptian dates, (f) route logistics cost/time/reliability from Alexandria/Port Said to Jeddah/Dammam?
**Required Evidence:** Trade, Opportunity, Market Access, Regulatory, Agrifood, Logistics, RoO
**Core Evidence:**
* HS-level bilateral trade (Egypt–Saudi dates, HS08)
* Saudi tariff/procedures for HS080410 (product-specific)
* Saudi SPS requirements for dates (product-specific)
* GAFTA RoO: agreement + eligibility + origin criterion + documentation
* Route logistics: Alexandria/Port Said → Jeddah/Dammam (sea primary, road alternative)
* Opportunity evidence: demand gap + import dynamics
**RoO:** Core — GAFTA applicability must be proven first. If applicable: agreement + eligibility + origin criterion + documentation. If not applicable: Not Required with documented reason.
**Route Contract:**
* Primary Route: Origin: Alexandria Port; Destination: Jeddah Port; Transport mode: Sea
* Fallback Route: Origin: Port Said Port; Destination: Dammam Port; Transport mode: Road
* Cargo characteristics: Dried fruit, moisture-sensitive, requires humidity control (15–25°C, 50–70% RH), packaging grade relevant (Saudi SASO standards)
* Shipment assumptions: FCL or LCL; moisture-barrier packaging; palletized
* Incoterm: FOB Alexandria Port (baseline); CIF Jeddah/Dammam if cost includes freight
* Temperature/control requirements: Ambient with humidity control; no refrigeration required
* Assessment time window: Q4 2026
* Reliability metric: On-time delivery rate; transit time variance; cargo condition integrity (moisture/humidity incidents)
**Freshness:** Trade: latest available annual; Opportunity: source-specific; Regulatory: current/effective; Logistics: current
**Effective Date:** Regulatory: must be current/effective at time of assessment (Q4 2026); RoO: GAFTA current at time of export
**Output Boundaries:** Exact tariff line for HS080410; exact SPS requirements; GAFTA RoO eligibility determination with documentation checklist; exact route cost estimate; opportunity quantification with methodology
**Not Required Conditions:**
* Agrifood: if Business Question does not require agricultural market indicators beyond trade volume
* RoO: if GAFTA does not apply or dates are not eligible (must be proven, not assumed)

---

## S3 - Egypt -> Germany / Citrus / HS08

**Scenario ID:** S3
**Origin:** Egypt — Alexandria Port
**Destination Market:** Germany
**Customs / Regulatory Jurisdiction:** EU (Germany is the destination market; EU customs/regulatory jurisdiction applies — EU TARIC, EU SPS/MRL)
**Exact Product Identity:** Citrus fruits: oranges, lemons, grapefruits
**Product Description:** Perishable agricultural produce requiring phytosanitary compliance for EU market
**Validated HS Mapping:** HS08 (chapter) — baseline; HS4/HS6 required for tariff/regulatory specificity
**HS Nomenclature / Version:** HS 2022 / EU TARIC (latest available)
**HS Granularity per Dimension:**
* Trade: HS08 chapter acceptable for bilateral baseline
* Tariff/Market Access: HS4/HS6 required for EU TARIC
* Regulatory/SPS: HS4/HS6 required for product-specific EU SPS/MRL requirements
* RoO: HS4/HS6 for origin criterion application under EU–Egypt FTA
**Business Question:** What is the export feasibility for Egyptian oranges (HS080510), lemons (HS080550), grapefruits (HS080540) to Germany (EU), including: (a) current bilateral trade volume and 3-year trend for HS0805, (b) demand gap and import dynamics for citrus in Germany/EU, (c) EU TARIC tariff duty rate and entry procedures for HS080510/080550/080540, (d) EU SPS/MRL requirements for Egyptian citrus, (e) EU–Egypt FTA RoO eligibility and documentation for citrus, (f) route logistics cost/time/reliability from Alexandria/Port Said to Hamburg/Bremerhaven or Cairo to Frankfurt/Munich?
**Required Evidence:** Trade, Opportunity, Market Access, Regulatory, Agrifood, Logistics, RoO
**Core Evidence:**
* HS-level bilateral trade (Egypt–Germany citrus, HS08)
* EU TARIC tariff/procedures for HS080510/080550/080540 (product-specific)
* EU SPS/MRL for Egyptian citrus (product-specific)
* EU–Egypt FTA RoO: agreement + eligibility + origin criterion + documentation
* Route logistics: Alexandria/Port Said → Hamburg/Bremerhaven (sea primary) OR Cairo → Frankfurt/Munich (air alternative)
* Opportunity evidence: demand gap + import dynamics
**RoO:** Core — EU–Egypt FTA applicability must be proven first. If applicable: agreement + eligibility + origin criterion + documentation. If not applicable: Not Required with documented reason.
**Route Contract:**
* Primary Route: Origin: Alexandria Port; Destination: Hamburg Port; Transport mode: Sea
* Fallback Route: Origin: Cairo Airport; Destination: Frankfurt Airport; Transport mode: Air
* Cargo characteristics: Perishable, requires cold chain (0–4°C), phytosanitary certification for EU, ethylene-sensitive
* Shipment assumptions: FCL or LCL; refrigerated container (reefer) with temperature logging; phytosanitary certificate required
* Incoterm: FOB Alexandria Port (baseline); CIF Hamburg/Bremerhaven if cost includes freight
* Temperature/control requirements: Cold chain mandatory; temperature monitoring and logging; phytosanitary compliance for EU
* Assessment time window: Q4 2026
* Reliability metric: On-time delivery rate; transit time variance; cold chain integrity; EU customs clearance time
**Freshness:** Trade: latest available annual; Opportunity: source-specific; Regulatory: current/effective EU SPS/MRL; Logistics: current
**Effective Date:** Regulatory: must be current/effective at time of assessment (Q4 2026); Market Access: current EU TARIC; RoO: EU–Egypt FTA current at time of export
**Output Boundaries:** Exact tariff line for each HS4/HS6 code under EU TARIC; exact SPS/MRL requirements; EU–Egypt FTA RoO eligibility determination with documentation checklist; exact route cost estimate (sea vs air comparison if both modes considered); opportunity quantification with methodology
**Not Required Conditions:**
* Agrifood: if Business Question does not require agricultural market indicators beyond trade volume
* RoO: if EU–Egypt FTA does not apply to citrus or citrus is not eligible under the agreement (must be proven, not assumed)

---

## S4 - Egypt -> Kenya / Coffee / HS09

**Scenario ID:** S4
**Origin:** Egypt — Alexandria Port
**Destination:** Kenya — Mombasa Port
**Exact Product Identity:** Coffee: green coffee beans, roasted coffee
**Product Description:** Agricultural commodity with specific quality standards and grading for East African market
**Validated HS Mapping:** HS09 (chapter) — baseline; HS4/HS6 required for tariff/regulatory specificity
**HS Nomenclature / Version:** HS 2022 (latest available)
**HS Granularity per Dimension:**
* Trade: HS09 chapter acceptable for bilateral baseline
* Tariff/Market Access: HS4/HS6 required for exact duty rate
* Regulatory/SPS: HS4/HS6 required for product-specific SPS requirements
* RoO: HS4/HS6 if applicable
**Business Question:** What is the export feasibility for Egyptian green coffee beans (HS090111) and roasted coffee (HS090121) to Kenya (Mombasa/Nairobi), including: (a) current bilateral trade volume and 3-year trend for HS0901, (b) demand gap and import dynamics for coffee in Kenya, (c) Kenya tariff duty rate and entry procedures for HS090111/090121, (d) Kenya SPS requirements for coffee, (e) any applicable FTA RoO eligibility and documentation, (f) route logistics cost/time/reliability from Alexandria/Port Said to Mombasa or Cairo to Nairobi?
**Required Evidence:** Trade, Opportunity, Market Access, Regulatory, Agrifood, Logistics, RoO
**Core Evidence:**
* HS-level bilateral trade (Egypt–Kenya coffee, HS09)
* Kenya tariff/procedures for HS090111/090121 (product-specific)
* Kenya SPS requirements for coffee (product-specific)
* Route logistics: Alexandria/Port Said → Mombasa (sea primary) OR Cairo → Nairobi (air alternative)
* Opportunity evidence: demand gap + import dynamics
* RoO: Applicability determination first; if applicable: agreement + eligibility + origin criterion + documentation
**RoO:** Conditional — COMESA Free Trade Area / COMESA Rules of Origin. Applicability: must be proven first. If applicable: agreement + eligibility + origin criterion + documentation. If not applicable: Not Required with documented reason.
**Route Contract:**
* Primary Route: Origin: Alexandria Port; Destination: Mombasa Port; Transport mode: Sea
* Fallback Route: Origin: Cairo Airport; Destination: Jomo Kenyatta International Airport, Nairobi; Transport mode: Air
* Cargo characteristics: Agricultural commodity, moisture-sensitive, requires ventilation, packaging grade relevant
* Shipment assumptions: FCL or LCL; ventilated containers for green coffee; moisture-barrier packaging for roasted coffee
* Incoterm: FOB Alexandria Port (baseline); CIF Mombasa if cost includes freight
* Temperature/control requirements: Ambient temperature with humidity control (green coffee: 10–20°C, 60–70% RH; roasted coffee: 15–25°C, 50–60% RH)
* Assessment time window: Q4 2026
* Reliability metric: On-time delivery rate; transit time variance; cargo condition integrity (moisture/contamination incidents)
**Freshness:** Trade: latest available annual; Opportunity: source-specific; Regulatory: current/effective; Logistics: current
**Effective Date:** Regulatory: must be current/effective at time of assessment (Q4 2026); Market Access: effective at time of assessment; RoO: agreement current at time of export (if applicable)
**Output Boundaries:** Exact tariff line for each HS4/HS6 code; exact SPS requirements; RoO applicability determination (Required or Not Required with documented reason); exact route cost estimate; opportunity quantification with methodology
**Not Required Conditions:**
* Agrifood: if Business Question does not require agricultural market indicators beyond trade volume
* RoO: if no preferential arrangement applies to Egypt–Kenya coffee trade (must be proven, not assumed)

---

## S5 - Egypt -> China / Knitted Apparel / HS61

**Scenario ID:** S5
**Origin:** Egypt — Alexandria Port
**Destination:** China — Shanghai Port
**Exact Product Identity:** Knitted apparel: T-shirts (HS610990), sweaters/pullovers (HS611011), men's shirts (HS610510)
**Product Description:** Knitted or crocheted apparel articles for Chinese market
**Validated HS Mapping:** HS61 (chapter) — baseline; HS6 required for tariff/TBT specificity
**HS Nomenclature / Version:** HS 2022 (latest available)
**HS Granularity per Dimension:**
* Trade: HS61 chapter acceptable for bilateral baseline
* Tariff/Market Access: HS6 required for exact duty rate
* Regulatory/TBT: HS6 required for product-specific TBT requirements
**Business Question:** What is the export feasibility for Egyptian knitted apparel — T-shirts (HS610990), sweaters/pullovers (HS611011), men's shirts (HS610510) — to China (Shanghai/Shenzhen), including: (a) current bilateral trade volume and 3-year trend for HS61 knitted apparel, (b) demand gap and import dynamics for knitted apparel in China, (c) China tariff duty rate and entry procedures for HS610990/611011/610510, (d) China TBT requirements for knitted apparel, (e) route logistics cost/time/reliability from Alexandria/Port Said to Shanghai/Shenzhen?
**Required Evidence:** Trade, Opportunity, Market Access, Regulatory, Logistics
**Core Evidence:**
* HS-level bilateral trade (Egypt–China knitted apparel, HS61)
* China tariff/procedures for HS610990/611011/610510 (product-specific)
* China TBT requirements for knitted apparel (product-specific)
* Route logistics: Alexandria/Port Said → Shanghai/Shenzhen (sea primary) OR Cairo → Beijing/Shanghai (air alternative)
* Opportunity evidence: demand gap + import dynamics
**Agrifood:** NOT REQUIRED — non-agricultural product
**RoO:** Conditional — 
Preferential Regime: China Zero-Tariff Measure for 20 African Countries (1 May 2026 – 30 April 2028).
Origin Regime: China Customs Rules of Origin under the Zero-Tariff Measure.
Applicability: must be proven first. If applicable: agreement + eligibility + origin criterion + documentation. If not applicable: Not Required with documented reason.

**Material Contract Amendment:** S5 RoO classification updated from Non-Preferential Rules of Origin to Preferential Regime: China Zero-Tariff Measure for 20 African Countries; Origin Regime: China Customs Rules of Origin under the Zero-Tariff Measure, effective 1 May 2026 to 30 April 2028, based on China's zero-tariff preferential tariff rate for African countries including Egypt. This amendment does not affect S1–S4.
**Route Contract:**
* Primary Route: Origin: Alexandria Port; Destination: Shanghai Port; Transport mode: Sea
* Fallback Route: Origin: Cairo Airport; Destination: Beijing Capital Airport; Transport mode: Air
* Cargo characteristics: Knitted apparel, packaging requirements vary by product type (T-shirts: garment bags or cartons; sweaters: folded with protective wrapping; shirts: boxed or cartoned)
* Shipment assumptions: FCL or LCL; standard dry container; packaging per product type
* Incoterm: FOB Alexandria Port (baseline); CIF Shanghai/Shenzhen if cost includes freight
* Temperature/control requirements: Ambient temperature; no special temperature control
* Assessment time window: Q4 2026
* Reliability metric: On-time delivery rate; transit time variance; cargo integrity (damage/water incidents)
**Freshness:** Trade: latest available annual; Opportunity: source-specific; Regulatory: current/effective China TBT; Logistics: current
**Effective Date:** Regulatory: must be current/effective at time of assessment (Q4 2026); Market Access: effective at time of assessment; RoO: agreement current at time of export (if applicable)
**Output Boundaries:** Exact tariff line for each HS6 code; exact TBT requirements for knitted apparel; RoO applicability determination (Required or Not Required with documented reason); exact route cost estimate; opportunity quantification with methodology
**Not Required Conditions:**
* Agrifood: always NOT REQUIRED — non-agricultural product
* RoO: if no preferential arrangement applies (non-preferential origin applies) (must be proven, not assumed)

---

# 36. Business Question Contract Structure

## 36.1 Contract Definition

Each Scenario MUST have a formal Business Question Contract with the following fields:

| Field | Requirement |
|-------|-------------|
| Specific User Need | What exactly the user wants to know (not vague topic) |
| Evidence Dimensions | Which evidence families are required for the answer |
| Core Minimum Sufficiency | Which dimensions are mandatory (not optional) |
| Product Granularity | HS level required: chapter, HS4, HS6, or product-specific |
| Country/Jurisdiction Scope | Exact countries, customs zones, economic blocs |
| Route/Logistics Specificity | Origin node, destination node, mode, cargo requirements |
| Freshness/Effective-Date Threshold | Maximum data age; effective date for regulations |
| Sufficient Answer Definition | What exact output constitutes a complete answer |
| Decision-Safe Conditions | What evidence/absence thereof prevents safe decision |
| Response-Safe Conditions | what output/absence thereof prevents safe response |
| System Must NOT Infer | Explicit list of prohibited inferences |

## 36.2 Binding Acceptance Rules

* Business Question Contract **must be operationally testable**, not a vague topic description
* forbidden formulations: "assess market opportunity", "check market access", "evaluate potential"
* The Contract **must be frozen** before Evidence & Gap Reassessment (Phase 2)
* Any ambiguity in the Contract = **Scenario blocked** until resolved
* No Business-Question Evidence Collection begins before Contract is frozen
* Reference / validation lookups needed to construct and validate the Scenario Contract are allowed during Phase 1
* Such lookups do NOT count as Business-Question Evidence Collection

## 36.3 Example of Non-Compliant vs Compliant Business Question

**Non-Compliant (vague):**
"Assess market opportunity for Egyptian vegetables in Jordan"

**Compliant (testable):**
"What is the export feasibility for Egyptian fresh tomatoes (HS070200) to Jordan (Aqaba), including: (a) current bilateral trade volume and 3-year trend, (b) demand gap and import dynamics (deterministic composite, if used), (c) Jordan tariff duty rate and entry procedures for HS070200, (d) Jordan SPS requirements for fresh tomatoes, (e) route logistics cost/time/reliability from Port Said to Aqaba?"

The compliant example is illustrative only.

It does NOT define:

* S1's actual product
* S1's final HS code
* S1's final route
* S1's final transport mode
* S1's final evidence requirements

The actual S1 contract is determined only in Phase 1.

---

## 36.4 Business Question / Evidence Consistency Invariant

Required Evidence Dimensions MUST be derived from the frozen Business Question Contract.

The following must always be consistent:

* Business Question Contract
* Required Evidence Dimensions
* Core Minimum Sufficiency
* Scenario Evidence Matrix

No dimension may appear as Core evidence if the frozen Business Question Contract does not declare it.

Conditional dimensions must be explicitly represented as Conditional inside the frozen Contract.

A Scenario Evidence Matrix may not introduce a new Core obligation silently.

---

# 36A. Evidence State Semantics

## Binding Definitions

| State | Meaning | Can Support READY? |
|-------|---------|-------------------|
| **Proven** | Evidence retrieved, validated, scope-confirmed, freshness-verified, provenance-complete | YES (for Core) |
| **Partial** | Evidence retrieved but incomplete in scope, freshness, or granularity | NO (for Core) |
| **Unsupported** | Evidence exists but does not answer the Business Question | NO |
| **Unavailable** | Source unreachable or returns no data | NO |
| **Missing** | Evidence not yet retrieved or not attempted | NO |
| **Not Required** | Dimension is outside Business Question scope (proven by Contract) | N/A (not needed) |

## Binding Rules

* **Partial ≠ Proven** - Partial evidence does NOT close Core gap
* **Unsupported ≠ Proven** - Evidence that does not answer the question is NOT sufficient
* **Unavailable ≠ Not Required** - Source failure does NOT make dimension optional
* **Missing ≠ Not Required** - Unexplored dimension is NOT automatically excluded
* **Not Required ≠ Not Proven** - Proven Not Required requires documented Contract basis
* **Ready** requires ALL Core Evidence = Proven + ALL conditions met
* **Family Ready ≠ Scenario Ready** - Provider operational does NOT mean scenario complete

### Valid No-Result

A valid scoped query that returns zero matching records is NOT automatically:
* Unavailable
* Missing
* Unsupported

It may be a valid **No-Result** evidence outcome when:
* the source contract defines zero results as meaningful
* the query scope is proven
* provenance is complete

Never convert:
* valid no-result -> inferred zero
* source failure -> valid no-result

---

# 37. Generalized Not Required Rule

Not Required may be declared only when BOTH are true:

A. The Business Question / Scenario Contract defines the dimension as conditional or outside scope.

AND

B. When conditional, an explicit applicability determination has been proven.

### Frozen Core Dimension Protection

A dimension already classified as Core in the frozen Business Question Contract CANNOT later be changed to Not Required merely to obtain READY.

A Contract amendment may clarify genuine scope, but may not be used to:

* remove a real Core requirement
* lower Minimum Sufficiency
* bypass missing evidence
* convert a provider/source gap into Not Required

No applicability proof:
Not Required is forbidden.

Not Required is NOT allowed when based on:
- absence of provider
- source failure
- missing credentials
- inability to retrieve data
- licensing problem
- implementation limitation
- test fixture limitation
- source discovery failure
- dimension not appearing in current provider

Unavailable != Not Required
No Provider != Not Required
Not Proven != Not Required
No applicability proof != Not Required

This rule applies uniformly across: Evidence Matrix, Provider Closure, Scenario Revalidation, Decision-Safe Gate, Response-Safe Gate, Final Exit Gate.

---

# 38. Provider Ceiling Expansion Governance

Expansion beyond 7 requires:
1. Documented Knowledge Need with decision impact
2. Marginal Value > 0 proven
3. Operational Justification documented
4. No existing provider/composition/fallback can cover the need within governance
5. Governance Approval BEFORE admission/implementation

Expansion is NOT denied due to the number 7 alone if evidence proves necessity.
Expansion is NOT approved due to gap existence alone without the above criteria.

---

# 39. WTO Timeseries Status

WTO Timeseries API is Blocked / Pending Evidence until it passes the Pre-Candidate Evidence Gate.
WTO Timeseries != Current Core Market Access Evidence.
It does NOT enter readiness before actual capability is proven.

---

# 40. Search Provider Boundary

SearchProviderRouter / SearXNG are Research infrastructure, NOT automatic substitutes for Knowledge Providers.
Search Result != Authoritative Commercial Evidence even if from an official source.
Search may: Discover, Locate, Support Complementary Research.
Search does NOT close Core Commercial Evidence unless an Evidence path is built, proven, and governance-compliant.

---

# 41. Commercial Licensing Final Rule

For each source entering Core Commercial Readiness, document:
Current Official Terms + Commercial Use + Storage Rights + Redistribution Rights + Attribution + API/Data Usage Restrictions + Rate/Quota Restrictions + Derivative-use Restrictions when applicable.

Status must be: Cleared, Pending, Restricted, or Not Cleared.
Technical reachability alone does NOT prove commercial clearance.

---

# 42. Final Self-Audit Checklist

## Entry Gate
- [ ] Entry Gate does NOT require CURRENT_STATUS.md to already be corrected
- [ ] Phase 0 is allowed to correct documentation drift
- [ ] Known drift alone does NOT block entry
- [ ] Only NEW / UNCLASSIFIED / materially conflicting current claims block entry

## Authority Model
- [ ] Domain-scoped precedence explicit and binding (القسم 0.4)
- [ ] Legal/licensing/contractual obligations = highest precedence
- [ ] Commercial Readiness rules MUST NOT weaken/override/cancel/reinterpret/bypass any architecture/provider/licensing/legal/closed-WP rule
- [ ] Conflict escalation rule: BLOCK -> RECORD -> ESCALATE -> AWAIT governance decision
- [ ] 43d809e = governance baseline authority
- [ ] phase-13-final-closure.md = closure evidence
- [ ] CURRENT_STATUS.md = status mirror, not higher authority

## Current Truth
- [ ] FAOSTAT represented as Inactive with Capability Proven = No
- [ ] All inactive providers represented consistently
- [ ] Operational ≠ Capability Proven rule explicit

## Scenario Contracts
- [ ] No unresolved placeholders ("to be confirmed", "to be validated", "specific types to be validated")
- [ ] Exact product identity resolved for each scenario
- [ ] Validated HS mapping/version explicit
- [ ] Customs/regulatory jurisdiction resolved (Germany/EU distinction)
- [ ] Route contract resolved (no "to be confirmed" in frozen contract)
- [ ] Transport mode resolved
- [ ] Cargo characteristics resolved
- [ ] Shipment assumptions resolved where materially required
- [ ] Incoterm resolved where materially required
- [ ] Reliability metric defined
- [ ] Assessment date/time window defined where materially relevant

## HS / Tariff-Line Rule
- [ ] HS4/HS6 may be sufficient but not always final
- [ ] Destination authority's effective tariff nomenclature used
- [ ] Chapter-level evidence only for broad trade baselines
- [ ] Chapter-level never substitutes for product/tariff-line evidence when finer specificity required
- [ ] HS version/nomenclature/mapping evidence recorded

## Business Question Contracts
- [ ] Each scenario has formal Contract with all 11 fields (القسم 36.1)
- [ ] No vague formulations allowed
- [ ] Contracts frozen before Phase 2
- [ ] No methodology contradiction (no invented scores without governed methodology)
- [ ] Reference lookups allowed during Phase 1 (not counted as evidence collection)
- [ ] Illustrative example disclaimer present

## Opportunity Composite Rule
- [ ] Composite only when all inputs individually proven
- [ ] Methodology deterministic and documented
- [ ] Provenance complete for every input
- [ ] No silent upgrade from Complementary to Authoritative
- [ ] Composite does not derive Opportunity from Trade alone
- [ ] Opportunity terminology defined (Demand Gap, Market Attractiveness, Opportunity Quantification)

## Evidence State Semantics
- [ ] Partial ≠ Proven
- [ ] Unsupported ≠ Proven
- [ ] Unavailable ≠ Not Required
- [ ] Missing ≠ Not Required
- [ ] Family Ready ≠ Scenario Ready
- [ ] Valid No-Result rule explicit

## Not Required Rule
- [ ] Generalized and binding (القسم 37)
- [ ] Requires BOTH: Contract defines conditional/outside scope AND explicit applicability determination proven
- [ ] Unavailable ≠ Not Required
- [ ] No Provider ≠ Not Required
- [ ] Not Proven ≠ Not Required
- [ ] No applicability proof ≠ Not Required
- [ ] Frozen Core Dimension Protection present
- [ ] Applied uniformly across all gates

## Pre-Candidate Evidence Gate
- [ ] Formally defined (القسم 17.1)
- [ ] 8 criteria explicit
- [ ] New Provider Evaluation blocked until all criteria proven
- [ ] "New Provider adds material evidence capability" moved to Candidate Capability Qualification

## Provider Ceiling
- [ ] 7 is governance control, not target
- [ ] Counting unit explicit (each distinct external operational production provider/source identity counts once)
- [ ] Inactive/code/configuration status does not count
- [ ] Activation does not count as new addition
- [ ] Activation Ceiling Edge Case addressed
- [ ] Expansion requires all 5 conditions (القسم 16.4)
- [ ] Approval authority explicit
- [ ] Approval evidence must be recorded
- [ ] Admission evidence must be recorded
- [ ] Kilo/local execution cannot approve expansion by itself
- [ ] Ceiling check in Provider Strategy, Source Admission, Execution Phases, Exit Gate
- [ ] No expansion without Governance Approval

## Source Admission
- [ ] Governance correction is NOT implementation-side override
- [ ] Conflict identification -> block -> explicit governance decision -> proceed
- [ ] No plan clause self-authorizes governance changes

## Conflict Handling
- [ ] Source authority explicit per Core Evidence Family
- [ ] Authoritative source class defined
- [ ] Scope match requirement defined
- [ ] Effective-date requirement defined
- [ ] Freshness requirement defined
- [ ] Tie-break rule defined
- [ ] No automatic averaging
- [ ] No defensible authority resolution + Core conflict = Scenario NOT READY
- [ ] Core Evidence Authority Matrix present (القسم 22A)

## Fallback Equivalence
- [ ] Fallback equivalence formally defined (القسم 23)
- [ ] Same evidence dimension
- [ ] Sufficient scope
- [ ] Sufficient granularity
- [ ] Valid freshness
- [ ] Valid effective date
- [ ] Acceptable authority tier
- [ ] Complete provenance
- [ ] Commercial-use clearance
- [ ] "Another source exists" is NOT sufficient
- [ ] Fallback Safety rule present

## Provider Failure
- [ ] Definition of Done distinguishes required vs non-required provider failure
- [ ] Non-required provider failure does not block readiness
- [ ] Failed primary with equivalent fallback may remain as operational incident

## Phase 9 Fixture Boundary
- [ ] Fixtures validate control-flow only
- [ ] Fixtures never used as production evidence
- [ ] Production readiness requires real proven evidence

## Phase-Level Contract Amendment Control
- [ ] After Phase 1 freeze, later phases may NOT silently alter frozen Contract
- [ ] Material amendment requires documented, governance-compatible approval
- [ ] Amendment cannot weaken readiness criteria
- [ ] Amendment re-triggers affected evidence/revalidation gates

## Final Exit Gate
- [ ] Scenario Set frozen
- [ ] Full Scenario Contract frozen for every scenario
- [ ] Exact product identity resolved
- [ ] Validated HS mapping/version
- [ ] Customs/regulatory jurisdiction resolved
- [ ] Route contract resolved where Logistics is Core
- [ ] Business Question Contract frozen
- [ ] Applicability decisions proven for all conditional dimensions
- [ ] Required Core Evidence Proven
- [ ] No unresolved evidence-state ambiguity
- [ ] No unresolved scope ambiguity
- [ ] No unresolved freshness/effective-date issue
- [ ] No unresolved provenance issue
- [ ] No unresolved licensing blocker
- [ ] No unresolved Core provider failure
- [ ] No unsupported composite methodology
- [ ] No unresolved authority conflict
- [ ] Decision-safe
- [ ] Response-safe
- [ ] Provider ceiling compliant
- [ ] Governance approvals recorded where required
- [ ] All 5 Scenarios READY required
- [ ] Any Scenario NOT READY = PLAN BLOCKED
- [ ] Ceiling Expansion without Governance Approval = PLAN BLOCKED
- [ ] Unresolved governance conflict = PLAN BLOCKED

## Scope Integrity
- [ ] Country-level ≠ Route-level
- [ ] Chapter-level ≠ Product-specific
- [ ] Complementary ≠ Authoritative
- [ ] Historical ≠ Live proof
- [ ] Test fixture ≠ Production

## Architecture
- [ ] No new Decision Engine
- [ ] No new Reasoning Engine
- [ ] No new Planner
- [ ] No BI redesign
- [ ] No Avatar redesign
- [ ] No Multi-Agent
- [ ] No Knowledge Graph changes
- [ ] No reopening closed WPs
- [ ] Provider Ceiling Rule compliance
- [ ] No ceiling expansion without Governance Approval

---