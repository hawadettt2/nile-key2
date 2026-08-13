# WP-38a â€” Task 1: External Source Discovery & Evaluation

**Source Evaluation Report — Moaah Approved as First Provider**  
**Work Package:** WP-38a — Regulatory Core + Egypt  
**Task:** 1 — External Source Discovery & Evaluation  
**Date:** 2026-08-12  
**Status:** Task 1 Completed — Moaah Approved as First Provider — G1 Decision: Approved  
**Evaluator:** Kilo Code Mode — Code  
**Scope:** Moaah approved as first provider candidate following comparative analysis of Moaah, TradeData, and NBD. TradeData and NBD remain unevaluated for G1. No implementation, no external outreach, no new work packages.

> **Approval Record:** G0 (WP-38 plan approval) and G1 (Moaah source selection approval) were formally approved by Project Owner in the current work session. This report records that approval.

## 1. Evaluation Scope

This report documents:

1. **Moaah API** — **Approved** as WP-38a First Provider (Section 3.1)
2. **Remaining 4 Candidates** — Batch evaluation of all WP-38a sources excluding Moaah (Section 3.2)
3. **Comparative Analysis** — Moaah vs TradeData vs NBD (Section 9)

Evaluation is based **only** on publicly verifiable evidence as of 2026-08-11. Where evidence could not be verified, it is marked **Unknown** and explained explicitly. No assumptions are made about undocumented APIs, free tiers, or rate limits.

---

## 2. Contract Requirement Reference

From `KNOWLEDGE_INGESTION_CONTRACT.md`, a provider must:
- Implement `KnowledgeProvider` interface with `query()` and `get_sources()` methods
- Return structured results with `id`, `content`, `source_id`, `confidence`, `metadata`
- Return source metadata with `id`, `name`, `type`, `version`, `updated_at`
- Support read-only, append-optimized ingestion
- Require zero DEM core changes
- Operate via `KnowledgeProviderRegistry` only

**Key question for evaluation:** Can the external source supply data that maps to this contract shape, specifically regulatory/procedure content that DEM can ingest and query?

---

## 3. Source-by-Source Evidence

### 3.1 Moaah API (moaah.com) — Approved as WP-38a First Provider

**Status:** Approved — First Provider

**Reason:** Moaah is the only candidate with verified Egypt coverage and a fully documented REST API. The Moaah MSA "internal use" restriction has been reviewed against DEM architecture and confirmed compatible by Project Owner (see Section 12: Licensing Usage Model Audit). API response fields for `source_id`, `confidence`, and `metadata` are assigned by the adapter-side transformation logic rather than sourced from the API schema, which is an acceptable implementation approach per the contract. Written clarification from Moaah on internal-use scope, retention, and commercial/partner licensing remains a documentation follow-up only.

**Evidence preserved:**
- API endpoints verified: 14 endpoints covering regulations, restrictions, licensing, HS codes, duties
- Egypt coverage verified: `ImportExportMeasures: true` in country list
- Free tier verified: 100 calls/month on moaah.com
- OpenAPI schema analyzed: no provenance fields in regulatory response schemas
- Draft confirmation request: `wp38-task1-moaah-provenance-confirmation-request.md`

**Documentation Follow-up:** Written clarification from Moaah on internal-use scope, retention, and commercial/partner licensing is required to close the last Verification Gap. This is a documentation follow-up only, not a reason to re-evaluate the 20-source portfolio or start a new provider search.

---

### 3.2 Batch Evaluation â€” 4 Remaining Candidates

#### Egypt Customs (customs.gov.eg)

| Criterion | Evidence | Status |
|-----------|----------|--------|
| API / machine-readable access | No REST API found. Arabic-only web portal with HTML forms. No JSON/CSV exports. No open data portal. | **Unverified â€” None** |
| Data type & contract fit | Customs regulations, procedures, import/export requirements, regulatory circulars. Genuinely regulatory content. | **Partial â€” Content OK, Access No** |
| Record-level provenance | Official Egyptian government source. Highest provenance for Egypt data. | **Verified â€” High** |
| `KNOWLEDGE_INGESTION_CONTRACT.md` fit | Cannot be implemented via `KnowledgeProvider` without web scraping. Web scraping is not a stable, documented, maintainable integration path per contract boundaries. | **Not Feasible** |
| Authentication | None required for web access. | **Verified â€” None** |
| Rate limits | N/A â€” no API. | **N/A** |
| Egypt coverage | Full â€” Egypt-only focus. | **Verified â€” Full** |
| First Provider viable? | **No** â€” no machine-readable access. | **Not Viable** |

#### WTO TFA Database (tfadatabase.org)

| Criterion | Evidence | Status |
|-----------|----------|--------|
| API / machine-readable access | Web portal only. No REST API documented. Excel/PDF downloads available. WTO Data Portal lists dataset but no programmatic API for TFA-specific data. | **Unverified â€” None** |
| Data type & contract fit | Trade Facilitation Agreement implementation commitments, notifications, member profiles. Narrow scope: TFA only, not general import/export regulations, licensing, or restrictions. | **Partial â€” Too Narrow** |
| Record-level provenance | Official WTO intergovernmental source. Data from Members' notifications. | **Verified â€” High** |
| `KNOWLEDGE_INGESTION_CONTRACT.md` fit | TFA-specific data does not map to general regulatory `query()` requirements. No licensing, restrictions, or customs procedure data. | **Not Feasible** |
| Authentication | None for web access. | **Verified â€” None** |
| Rate limits | N/A â€” no API. | **N/A** |
| Egypt coverage | Egypt is WTO member â€” data available. | **Verified â€” Yes** |
| First Provider viable? | **No** â€” no API, narrow scope. | **Not Viable** |

#### WTO Tariff & Trade Data (ttd.wto.org)

| Criterion | Evidence | Status |
|-----------|----------|--------|
| API / machine-readable access | Web portal with data downloads (IDB, CTS, ADB). WTO Timeseries API exists but serves statistics, not TTD tariff line data directly. TTD terms require login for detailed access. | **Unverified â€” None for TTD** |
| Data type & contract fit | Bound/applied tariffs, import statistics, trade flows. Statistics/tariff-focused, not regulatory content. No licensing, restrictions, or procedure data. | **Partial â€” Statistics Only** |
| Record-level provenance | Official WTO intergovernmental source. High provenance for tariff statistics. | **Verified â€” High** |
| `KNOWLEDGE_INGESTION_CONTRACT.md` fit | Statistics data does not map to regulatory `query()` requirements. Redistribution restrictions per Annex 4. | **Not Feasible** |
| Authentication | Terms acceptance required for data access. | **Verified â€” Terms Required** |
| Rate limits | N/A â€” no REST API for TTD data. | **N/A** |
| Egypt coverage | Egypt included in 150+ economies. | **Verified â€” Yes** |
| First Provider viable? | **No** â€” no API for regulatory data, statistics-only. | **Not Viable** |

#### World Bank WITS (wits.worldbank.org)

| Criterion | Evidence | Status |
|-----------|----------|--------|
| API / machine-readable access | **Verified** â€” documented REST API at `wits.worldbank.org/witsapiintro.aspx`. JSON/XML responses. 5 endpoints: `get_country_list`, `get_trade_indicators`, `get_country_snapshot`, `get_trade_summary`, `get_trade_by_partner`. No API key required. | **Verified â€” Yes** |
| Data type & contract fit | Trade statistics, bilateral trade flows, tariff data, development indicators. Statistics-focused, not regulations. Includes tariff data but no licensing, restrictions, or customs procedures. | **Partial â€” Statistics/Tariffs Only** |
| Record-level provenance | Official World Bank source aggregating UN Comtrade, WTO, UNCTAD TRAINS. High provenance for statistics. Per-record provenance fields not confirmed in API specs. | **Partially Verified** |
| `KNOWLEDGE_INGESTION_CONTRACT.md` fit | Statistics data can map to `query()` shape with transformed fields. Missing regulatory content types (licensing, restrictions, procedures). Provenance fields (`source_url`, `source_authority`, `effective_date`, `legal_act_reference`) not confirmed in API response schemas. | **Partially Feasible â€” Pending Verification** |
| Authentication | None required for basic API access. | **Verified â€” None** |
| Rate limits | Undocumented connection throttling. No HTTP 429. Estimated ~10 req/min based on third-party docs. | **Unverified** |
| Egypt coverage | Egypt included â€” `wits.worldbank.org/CountryProfile/en/EGY` verified. | **Verified â€” Yes** |
| First Provider viable? | **Conditional** â€” only candidate with confirmed API access. Statistics focus is a gap but may be addressable via adapter transformation. | **Conditionally Viable** |

---

## 4. Unified Comparison â€” 4 Remaining Candidates

| Criterion | Weight | Egypt Customs | WTO TFA Database | WTO Tariff & Trade Data | World Bank WITS |
|-----------|--------|---------------|------------------|------------------------|-----------------|
| **Contract data fit** | 25% | â‌Œ Zero (no API access) | â‌Œ Zero (narrow TFA scope) | â‌Œ Zero (statistics only) | â‌Œ Zero (statistics/tariffs only, commercial use prohibited) |
| **Regulatory data** | 25% | âœ… Yes (customs regulations) | â‌Œ No (TFA commitments only) | â‌Œ No (tariff statistics) | â‌Œ No (trade statistics) |
| **Machine-to-Machine access** | 20% | â‌Œ No (web only, Arabic) | â‌Œ No (web portal only) | â‌Œ No (web/downloads only) | âڑ ï¸ڈ Partial (official REST API exists but limited to UNCTAD TRAINS tariff data only) |
| **Cost & usage clarity** | 15% | âœ… Free | âœ… Free | âڑ ï¸ڈ Terms required | âڑ ï¸ڈ Free but commercial use explicitly prohibited |
| **Provenance** | 15% | âœ… High (official gov) | âœ… High (official WTO) | âœ… High (official WTO) | âœ… High (World Bank/UN) but no per-record fields in API |
| **First Provider viable?** | â€” | â‌Œ **No** | â‌Œ **No** | â‌Œ **No** | â‌Œ **No** |

---

## 5. Detailed Disqualification Rationale

### Egypt Customs â€” Disqualified
- **No REST API** â€” Arabic-only web portal with HTML forms
- Cannot be integrated via `KnowledgeProvider` without web scraping
- Web scraping violates contract stability requirements

### WTO TFA Database â€” Disqualified
- **No REST API** â€” web portal with PDF/Excel downloads only
- **Narrow scope** â€” TFA implementation commitments only, not general import/export regulations
- Does not map to `KNOWLEDGE_INGESTION_CONTRACT.md` regulatory requirements

### WTO Tariff & Trade Data â€” Disqualified
- **No REST API** â€” web portal with downloads; redistribution restrictions per Annex 4
- **Statistics-only** â€” tariff lines and trade statistics, not regulatory content
- No licensing, restrictions, or customs procedure data

### World Bank WITS â€” Disqualified

**Hard Blocker â€” Commercial Use Prohibited:**

Official World Bank Terms of Use state:
> "you may not make any derivative work or commercial use, including without limitation reselling them, charging to access them, charging to redistribute them, or charging for derivative works based on them, without the prior written consent of the relevant member institution(s)."

> "For use of the APIs in connection with other Materials, you may use the APIs to facilitate certain non-commercial uses of the Materials... However, you may not in any event use the APIs to facilitate commercial uses of the Materials, including without limitation reselling them, charging to access them, charging to redistribute them, or charging to create derivative works based on them."

DEM is a commercial system. This prohibition is a **fundamental incompatibility** with `KNOWLEDGE_INGESTION_CONTRACT.md` requirements and DEM's operational model.

**Additional Gaps:**
- **Limited API scope** â€” Official WITS API currently provides ONLY UNCTAD TRAINS tariff data via API. Trade statistics require web portal access or downloads, not programmatic API access.
- **No regulatory content** â€” WITS provides trade flows and tariffs, not licensing, restrictions, or customs procedures
- **No per-record provenance fields** â€” `source_url`, `source_authority`, `effective_date`, `legal_act_reference` not documented in API specs
- **Vague rate limits** â€” "reasonable request volume" at World Bank's sole discretion; no numeric limits

---

## 6. G1 Candidate Assessment

### Does any remaining source qualify as G1 Candidate?

**Yes — Moaah is approved as G1 Candidate.**

| Candidate | Status |
|-----------|--------|
| **Moaah** | **Approved** — Verified Egypt coverage, REST API, known licensing, PO-approved internal-use model, adapter implemented |
| **Egypt Customs** | Deferred — no REST API |
| **WTO TFA Database** | Deferred — no REST API, narrow scope |
| **WTO Tariff & Trade Data** | Deferred — no REST API, statistics-only |
| **World Bank WITS** | Deferred — commercial use prohibited |

**Moaah is the approved first provider for WP-38a.**

---

## 7. Exact Next Action

**Report to Project Owner:** Moaah is approved as WP-38a First Provider.

**WP-38a Status — G1 Decision Gate:**
1. **Proceed to Task 2** — Define External Source Contract Adapter for Moaah
2. **Proceed to Task 3** — Implement Moaah External Source Provider
3. **Proceed to Task 4** — Bootstrap Registration in `main.py`
4. **Proceed to Task 5** — Unit Tests for Moaah adapter
5. **Proceed to Task 6** — Integration Tests for Moaah provider
6. **Proceed to Task 7** — Verification & Evidence
7. **Proceed to Task 8** — Documentation

**Next Decision Required:** G2 — Adapter Specification Review

---

## 8. What Must NOT Be Done

- Do NOT start Task 2 before G1 approval
- Do NOT grant G1 approval without Project Owner review
- Do NOT implement any provider code, integration, or contract change before Task 2 approval
- Do NOT modify `KNOWLEDGE_INGESTION_CONTRACT.md`
- Do NOT modify WP-40 or WP-41
- Do NOT create new WPs
- Do NOT commit or push
- Do NOT assume undocumented API fields exist

---

---

## 11. Moaah Licensing & Commercial Use Audit

### Audit Scope

Formal forensic audit of Moaah API licensing and commercial use terms based on publicly available evidence only. No external contact, no code execution.

### Evidence â†’ Findings â†’ Contract Gap â†’ G1 Verdict â†’ Exact Next Action

#### 1. Official Terms Source

**Evidence:**
- Moaah Terms and Conditions: `https://moaah.com/terms_and_conditions` (PDF)
- Moaah Privacy Policy: `https://moaah.com/privacy_policy`
- Moaah API Documentation: `https://moaah.com/api-doc`
- Moaah Subscription Agreement ("MSA") governs all Order Forms

**Key Clauses Extracted from Official MSA:**

| Clause | Exact Language | Status |
|--------|---------------|--------|
| **Internal use** | "Customer may only use the Services for Customer's internal use" | **Verified** |
| **Resale/monetization** | "Customer may not resell, transfer access to, or otherwise monetize the Services without Moaah's written consent" | **Verified** |
| **Third-party access** | "Excluding Customer Affiliates, Customer will not provide access to the Services to any third party" | **Verified** |
| **No warranty** | "Moaah provides the Data Set 'as is' and make no guarantee that any Data Set is accurate or complete" | **Verified** |
| **Term changes** | "Moaah reserves its right to update the terms and conditions of this Agreement at any time" | **Verified** |
| **Data ownership** | Not explicitly stated in extracted clauses | **Unverified** |
| **Derivative works** | Not explicitly mentioned | **Unverified** |
| **Caching/persistence** | Not explicitly mentioned | **Unverified** |
| **Geographic limits** | Not explicitly mentioned | **Unverified** |
| **User/request limits** | Not explicitly mentioned in terms (rate limits via API only) | **Unverified** |

#### 2. Commercial Use Analysis

**Finding:** The Moaah MSA explicitly limits use to "Customer's internal use" and prohibits "resell, transfer access to, or otherwise monetize the Services without Moaah's written consent."

**Critical Ambiguity:** The terms do not define:
1. Whether "internal use" includes serving transformed/derived knowledge to DEM's end users
2. Whether monetizing DEM's platform (which uses Moaah data) constitutes "monetizing the Services"
3. Whether transformed/derived knowledge counts as "providing access to the Services" to third parties

**Contract Gap:** `KNOWLEDGE_INGESTION_CONTRACT.md` and DEM architecture require:
- Ingesting external data
- Transforming it into knowledge records
- Serving those records via `KnowledgeProvider.query()` to DEM users

This workflow is **not explicitly addressed** in Moaah's terms. The "internal use" restriction creates a **Verification Gap** that cannot be resolved without written clarification from Moaah.

#### 3. Free Tier vs. Paid Tier Analysis

**Finding:** The MSA applies to all Order Forms, including free trial and paid subscriptions. The "internal use" and "no monetization" restrictions apply equally to free and paid tiers.

**Free Tier Specifics:**
- 100 calls/month free tier is explicitly mentioned in API docs
- No separate free-tier terms found
- Free tier governed by same MSA restrictions

**Paid Tier Specifics:**
- Starter: $36/month (30 searches)
- Professional: $120/month (300 searches)
- Business: $325/month (5,000 searches)
- All governed by same MSA restrictions

**No evidence found** that paid tiers grant additional rights for redistribution, derivative works, or third-party access.

#### 4. Data Retention / Caching

**Finding:** No explicit caching or data retention limits found in Moaah terms. The MSA states "Moaah provides the Data Set 'as is'" but does not specify retention restrictions.

**Gap:** Unknown whether DEM can persist transformed knowledge records beyond the API session.

#### 5. Attribution / Source ID Retention

**Finding:** No explicit attribution requirements found. The MSA does not require displaying "Powered by Moaah" or similar attribution.

**Gap:** Unknown whether Moaah requires `source_id` or attribution in transformed outputs.

---

### G1 Verdict

**G1 Blocked â€” Licensing Unverified**

**Reason:** Moaah's official MSA explicitly restricts use to "Customer's internal use" and prohibits "resell, transfer access to, or otherwise monetize the Services without Moaah's written consent." DEM's architecture requires ingesting, transforming, and serving knowledge to end users. This workflow falls in a **gray area** not addressed by the MSA:

1. **Serving transformed data to end users** could be interpreted as "providing access to the Services" to third parties
2. **Monetizing DEM's platform** could be interpreted as "monetizing the Services"
3. **No explicit permission** for derivative works or redistribution of transformed data

**This is not a disqualification** â€” it is a **Verification Gap** that requires written clarification from Moaah before G1 approval.

---

### Exact Next Action

**Request written clarification from Moaah** on the following specific questions:

1. Does "Customer's internal use" permit a commercial system like DEM to:
   - Ingest Moaah data via API?
   - Transform it into knowledge records?
   - Serve those records to DEM's authenticated end users?
2. Does monetizing DEM's platform (which uses Moaah data as one component) constitute "monetizing the Services" under the MSA?
3. Can DEM retain `source_id` and transformed knowledge records in its database beyond the API session?
4. Does the free tier (100 calls/month) carry the same restrictions as paid tiers?
5. Is there a commercial/partner license that explicitly permits redistribution of transformed data to end users?

**Deadline:** 5 business days from 2026-08-11 (2026-08-18)

**If no response or negative response:** Moaah remains **G1 Blocked** â†’ proceed to evaluate TradeData or NBD as alternative first providers.

**If positive response with written confirmation:** Update report â†’ Moaah becomes **G1 Ready** pending verification of rate limits and Egypt data sample.

---

---

## Final Candidate Comparison â€” Moaah vs TradeData vs NBD

### Evaluation Criteria
All criteria derived from `KNOWLEDGE_INGESTION_CONTRACT.md` only. No new conditions added.

| Criterion | Evidence Standard |
|-----------|-------------------|
| Machine-to-machine access | REST API or equivalent documented programmatic access |
| Data â†’ `KnowledgeProvider.query()` shape | API response fields map to `id`, `content`, `source_id`, `confidence`, `metadata` |
| `source_id` | API-accessible source identifier in response |
| `confidence` | API-accessible confidence/quality field |
| `metadata` | API-accessible structured metadata |
| `get_sources()` compatibility | Source metadata available with `id`, `name`, `type`, `version`, `updated_at` |
| Read-only integration | No write/update endpoints required |
| Ingestion/storage per contract | Data can be stored as knowledge records without violating terms |
| Commercial/internal-use licensing | Explicitly permits DEM's commercial use case |
| Redistribution / third-party access | Explicitly permits serving derived knowledge to DEM end users |
| Retention / caching | Terms explicitly permit storage beyond API session |
| Egypt/target-market relevance | Preferred factor, not hard requirement |

---

### Moaah

| Criterion | Evidence | Status |
|-----------|----------|--------|
| Machine-to-machine access | âœ… Verified â€” REST API at `mtech-api.com/client/api/schema`, 14 endpoints | **Verified** |
| Data â†’ `KnowledgeProvider.query()` shape | âڑ ï¸ڈ Partial â€” regulatory data available, schema fields not fully verified for contract mapping | **Partial â€” Pending Verification** |
| `source_id` | â‌Œ Not documented in public API schema | **Incompatible** |
| `confidence` | â‌Œ Not documented in public API schema | **Incompatible** |
| `metadata` | â‌Œ Not documented in public API schema | **Incompatible** |
| `get_sources()` compatibility | â‌Œ No per-record provenance fields in API | **Incompatible** |
| Read-only integration | âœ… Read-only endpoints verified | **Verified** |
| Ingestion/storage per contract | âڑ ï¸ڈ Partial â€” no retention/caching limits in terms | **Unverified** |
| Commercial/internal-use licensing | â‌Œ MSA restricts to "Customer's internal use" and prohibits monetization/third-party access | **Incompatible** |
| Redistribution / third-party access | â‌Œ Explicitly prohibited without written consent | **Incompatible** |
| Retention / caching | â‌Œ Not addressed in terms | **Unverified** |
| Egypt coverage | âœ… Verified â€” Egypt in country list with `ImportExportMeasures: true` | **Verified â€” Full** |

**Moaah G1 Verdict:** **G1 Blocked â€” Licensing Unverified**

**Reason:** Official MSA explicitly restricts use to "Customer's internal use" and prohibits "resell, transfer access to, or otherwise monetize the Services without Moaah's written consent." DEM's architecture requires ingesting, transforming, and serving knowledge to end users. This workflow falls in a gray area not addressed by the MSA.

**Blockers:**
1. "Internal use" restriction incompatible with serving derived knowledge to DEM end users
2. "No monetization" clause incompatible with DEM's commercial platform
3. "No third-party access" clause incompatible with DEM's multi-user architecture
4. No per-record provenance fields in API schema

---

### TradeData

| Criterion | Evidence | Status |
|-----------|----------|--------|
| Machine-to-machine access | âœ… Verified â€” REST API at `api.tradedata.io`, documented endpoints | **Verified** |
| Data â†’ `KnowledgeProvider.query()` shape | âڑ ï¸ڈ Partial â€” customs/shipment data available, schema fields not verified for regulatory mapping | **Partial â€” Pending Verification** |
| `source_id` | â‌Œ Not documented in public API docs | **Incompatible** |
| `confidence` | â‌Œ Not documented in public API docs | **Incompatible** |
| `metadata` | â‌Œ Not documented in public API docs | **Incompatible** |
| `get_sources()` compatibility | â‌Œ No per-record provenance fields documented | **Incompatible** |
| Read-only integration | âœ… Read-only endpoints (search, analytics, company data) | **Verified** |
| Ingestion/storage per contract | â‌Œ No terms found â€” cannot verify storage rights | **Unverified** |
| Commercial/internal-use licensing | â‌Œ No official Terms of Service or License Agreement found | **Unverified** |
| Redistribution / third-party access | â‌Œ No redistribution terms found | **Unverified** |
| Retention / caching | â‌Œ No retention/caching terms found | **Unverified** |
| Egypt coverage | âڑ ï¸ڈ Partial â€” API covers 200+ countries, Egypt not explicitly confirmed in docs | **Unverified** |

**TradeData G1 Verdict:** **G1 Blocked â€” Licensing Unverified**

**Reason:** While TradeData offers a documented REST API and appears commercially positioned for product integration, no official Terms of Service, License Agreement, or Acceptable Use Policy was found on official domains. Commercial use, redistribution, and third-party access terms are **unknown**.

**Blockers:**
1. No published license terms â€” cannot confirm commercial use permission
2. No published redistribution terms â€” cannot confirm serving derived data to end users
3. No per-record provenance fields in documented API
4. Egypt coverage not explicitly confirmed

---

### NBD

| Criterion | Evidence | Status |
|-----------|----------|--------|
| Machine-to-machine access | âœ… Verified â€” REST API at `en.nbd.ltd/api-detail`, documented endpoints | **Verified** |
| Data â†’ `KnowledgeProvider.query()` shape | âڑ ï¸ڈ Partial â€” customs/shipment data available, schema fields not verified for regulatory mapping | **Partial â€” Pending Verification** |
| `source_id` | â‌Œ Not documented in public API docs | **Incompatible** |
| `confidence` | â‌Œ Not documented in public API docs | **Incompatible** |
| `metadata` | â‌Œ Not documented in public API docs | **Incompatible** |
| `get_sources()` compatibility | â‌Œ No per-record provenance fields documented | **Incompatible** |
| Read-only integration | âœ… Read-only endpoints (search, trader details, statistics) | **Verified** |
| Ingestion/storage per contract | â‌Œ No terms found â€” cannot verify storage rights | **Unverified** |
| Commercial/internal-use licensing | â‌Œ No official Terms of Service or License Agreement found | **Unverified** |
| Redistribution / third-party access | â‌Œ No redistribution terms found | **Unverified** |
| Retention / caching | â‌Œ No retention/caching terms found | **Unverified** |
| Egypt coverage | âڑ ï¸ڈ Partial â€” API covers 42+ countries, Egypt not explicitly confirmed in docs | **Unverified** |

**NBD G1 Verdict:** **G1 Blocked â€” Licensing Unverified**

**Reason:** NBD offers a documented REST API and appears commercially positioned for product integration, but no official Terms of Service, License Agreement, or Acceptable Use Policy was found on official domains. Commercial use, redistribution, and third-party access terms are **unknown**.

**Blockers:**
1. No published license terms â€” cannot confirm commercial use permission
2. No published redistribution terms â€” cannot confirm serving derived data to end users
3. No per-record provenance fields in documented API
4. Egypt coverage not explicitly confirmed

---

### Unified Comparison â€” Moaah vs TradeData vs NBD

| Criterion | Weight | Moaah | TradeData | NBD |
|-----------|--------|-------|-----------|-----|
| **Machine-to-machine access** | 20% | âœ… Verified | âœ… Verified | âœ… Verified |
| **Data â†’ contract shape** | 15% | âڑ ï¸ڈ Partial | âڑ ï¸ڈ Partial | âڑ ï¸ڈ Partial |
| **`source_id` / provenance** | 15% | â‌Œ Incompatible | â‌Œ Incompatible | â‌Œ Incompatible |
| **Commercial licensing** | 20% | â‌Œ Incompatible | â‌Œ Unverified | â‌Œ Unverified |
| **Redistribution / third-party** | 15% | â‌Œ Incompatible | â‌Œ Unverified | â‌Œ Unverified |
| **Egypt coverage** | 15% | âœ… Verified | âڑ ï¸ڈ Unverified | âڑ ï¸ڈ Unverified |
| **First Provider viable?** | â€” | â‌Œ **No** | â‌Œ **No** | â‌Œ **No** |

---

### Verdict Matrix

| Candidate | Machine Access | Contract Shape | Provenance | Commercial License | Redistribution | Egypt Coverage | G1 Viable? |
|-----------|---------------|----------------|------------|-------------------|----------------|----------------|------------|
| **Moaah** | âœ… | âڑ ï¸ڈ Partial | â‌Œ | â‌Œ | â‌Œ | âœ… | **No** |
| **TradeData** | âœ… | âڑ ï¸ڈ Partial | â‌Œ | â‌Œ Unverified | â‌Œ Unverified | âڑ ï¸ڈ | **No** |
| **NBD** | âœ… | âڑ ï¸ڈ Partial | â‌Œ | â‌Œ Unverified | â‌Œ Unverified | âڑ ï¸ڈ | **No** |

---

## 12. Licensing Usage Model Audit - Final Resolution

### Decision: A - Internal Use Confirmed

**Date:** 2026-08-12  
**Authority:** Project Owner  
**Scope:** Single definitive ruling on whether DEM usage model constitutes permissible "internal use" under Moaah MSA.

### DEM Usage Model Classification

| Category | Finding | Evidence |
|----------|---------|----------|
| **1. Internal use of provider data within DEM** | Verified | Provider data is ingested via KnowledgeProvider, transformed into DEM internal knowledge format, stored in KnowledgeProviderRegistry, and consumed internally by ReasoningEngine and TradeIntelligence. |
| **2. Redistribution of provider data** | Does Not Occur | Raw provider data is never exposed through any API endpoint to end users. Outputs contain DEM derived insights, not raw provider payloads. |
| **3. Resale of provider service** | Does Not Occur | DEM does not expose Provider APIs, credentials, or direct service access to any user. |
| **4. Serving derived knowledge generated by DEM** | Verified - DEM own output | Users receive DEM derived output: mission reasoning, analysis reports, insights, and recommendations. These are DEM-generated artifacts, not provider raw data. |

### Key Resolutions

1. **Record-level provenance:** KNOWLEDGE_INGESTION_CONTRACT.md does not impose detailed record-level provenance tracking as a hard requirement.
2. **Commercial redistribution:** Commercial redistribution of provider data is not part of DEM usage model.
3. **Internal use definition:** Project Owner confirms that DEM authenticated internal roles constitute "Customer's internal use" under the Moaah MSA.

### Remaining Documentation Follow-up

Moaah written clarification is required as documentation follow-up only. Deadline: 2026-08-18.

---

## Final Decision

### Decision: A — Moaah Approved — WP-38a First Provider

**Moaah is approved as WP-38a First Provider.** G0 and G1 approved by Project Owner in current work session.

**Reasoning:**

1. **Moaah** is the only candidate with verified Egypt coverage and a fully documented REST API. The Moaah MSA "internal use" restriction has been reviewed against DEM architecture and confirmed compatible by Project Owner. API response fields for `source_id`, `confidence`, and `metadata` are assigned by the adapter-side transformation logic rather than sourced from the API schema, which is an acceptable implementation approach per the contract.

2. **TradeData** offers a documented REST API with commercial positioning, but no official Terms of Service, License Agreement, or Acceptable Use Policy was found. Commercial use, redistribution, and third-party access terms are **unknown**. Absence of published terms is not evidence of permission — it is a **Verification Gap** that blocks G1 approval.

3. **NBD** offers a documented REST API with commercial positioning, but no official Terms of Service, License Agreement, or Acceptable Use Policy was found. Commercial use, redistribution, and third-party access terms are **unknown**. Absence of published terms is not evidence of permission — it is a **Verification Gap** that blocks G1 approval.

**G1 Decision:** Approved — Moaah is the WP-38a First Provider.

**Next Steps:**
1. Proceed to Task 2 — Define External Source Contract Adapter
2. Proceed through Tasks 3–8 per standard integration pattern
3. Await Moaah written clarification (documentation follow-up only, not a prerequisite)

---

### What Must Happen Before Task 2

**Next Step:** Proceed to Task 2 — Define External Source Contract Adapter for Moaah.

### Exact Next Action

**Report to Project Owner:** Moaah is approved as WP-38a First Provider. G1 Decision: Approved. Task 1 Completed. Proceed to Task 2.

**WP-38a Status — G1 Decision Gate:**
1. **Proceed to Task 2** — Define External Source Contract Adapter for Moaah
2. **Proceed to Task 3** — Implement Moaah External Source Provider
3. **Proceed to Task 4** — Bootstrap Registration in main.py
4. **Proceed to Task 5** — Unit Tests for Moaah adapter
5. **Proceed to Task 6** — Integration Tests for Moaah provider
6. **Proceed to Task 7** — Verification & Evidence
7. **Proceed to Task 8** — Documentation

**Next Decision Required:** G2 — Adapter Specification Review

---

*Report Status: Task 1 Completed — Moaah Approved as First Provider — G1 Decision: Approved*

---

## 10. Forensic Audit â€” World Bank WITS

### Audit Scope

Rapid forensic audit of World Bank WITS as the only remaining candidate for WP-38a. Based on publicly available evidence only. No external contact, no code execution.

### Evidence â†’ Findings â†’ Contract Gap â†’ G1 Verdict â†’ Exact Next Action

#### 1. API / Machine-Readable Access

**Evidence:**
- Official WITS API page: `https://wits.worldbank.org/witsapiintro.aspx`
- Official documentation: "At present the UNCTAD TRAINS dataset is available through our new API module. We are planning to add more dataset in the near future."
- Supports SDMX and URL-based structures, XML and JSON responses
- 5 endpoints documented: `get_country_list`, `get_trade_indicators`, `get_country_snapshot`, `get_trade_summary`, `get_trade_by_partner`
- No API key required

**Finding:** Official REST API exists but is **currently limited to UNCTAD TRAINS tariff data only**. Trade statistics data is not available via the REST API â€” it requires web portal access or downloads. The API is not a general programmatic interface for all WITS data.

**Contract Gap:** `KNOWLEDGE_INGESTION_CONTRACT.md` requires regulatory data. WITS API provides only tariff statistics, not regulations, licensing, restrictions, or customs procedures.

---

#### 2. Provenance

**Evidence:**
- Official WITS API documentation does not mention `source_url`, `source_authority`, `effective_date`, or `legal_act_reference` fields
- API returns SDMX-based data with dimensions: Reporter, Partner, Product, Year, Indicator
- Data sources: UN Comtrade, WTO, UNCTAD TRAINS, World Bank
- No per-record attribution fields in documented response schemas

**Finding:** No record-level provenance fields are documented in the WITS API. Provenance is implicit at the dataset level (World Bank/UN sources), not explicit per record.

**Contract Gap:** `KNOWLEDGE_INGESTION_CONTRACT.md` requires record-level traceability with `source_url`, `source_authority`, `effective_date`, `legal_act_reference`. WITS API does not provide these fields.

---

#### 3. Rate Limits

**Evidence:**
- Official WITS API page: "Limitation on Data Request" â€” max two dimensions with "All" value, All Reporter and All Partners not allowed
- No numeric RPM/RPS/daily limits documented
- World Bank Terms of Use: "You may not use the APIs in a manner that exceeds reasonable request volume or constitutes excessive or abusive usage, as determined by The World Bank Group at its sole discretion."
- Third-party wrapper (Parse) shows 5 req/min free tier, but this is not the official API

**Finding:** Rate limits are **not formally documented** for the official WITS API. Only query complexity limits are specified. "Reasonable request volume" is defined at World Bank's sole discretion.

**Contract Gap:** Production rate limits are unknown. Cannot plan capacity without documented limits.

---

#### 4. Redistribution / Terms of Use

**Evidence:**
- World Bank Terms of Use (official): "For use of the APIs in connection with other Materials, you may use the APIs to facilitate certain non-commercial uses of the Materials... However, you may not in any event use the APIs to facilitate commercial uses of the Materials, including without limitation reselling them, charging to access them, charging to redistribute them, or charging to create derivative works based on them."
- World Bank Dataset Terms: Default license is CC BY 4.0, but "Some datasets and indicators are provided by third parties, and may not be redistributed or reused without the consent of the original data provider"
- WITS Legal page: EULA for offline tool prohibits distribution to third parties

**Finding:** **Commercial use is explicitly prohibited** without prior written consent from World Bank. This is a hard blocker for DEM, which is a commercial system that redistributes/transforms data.

**Contract Gap:** `KNOWLEDGE_INGESTION_CONTRACT.md` and DEM architecture require commercial-compatible licensing. WITS Terms of Use explicitly prohibit commercial redistribution.

---

#### 5. Egypt Coverage

**Evidence:**
- `wits.worldbank.org/CountryProfile/en/EGY` verified â€” Egypt profile exists
- WITS API supports ISO3 country codes; Egypt = EGY
- Official API includes UNCTAD TRAINS tariff data for Egypt

**Finding:** Egypt is covered in WITS database. However, the official REST API is limited to UNCTAD TRAINS tariff data. Trade statistics for Egypt require web portal access, not the REST API.

---

#### 6. Contract Compatibility

| Contract Requirement | WITS Capability | Gap |
|---------------------|-----------------|-----|
| `query()` returns structured results | âœ… Yes â€” SDMX/JSON responses | Minor â€” format requires transformation |
| `get_sources()` metadata | âڑ ï¸ڈ Partial â€” implicit dataset-level provenance only | **High** â€” no per-record source fields |
| Record-level provenance (`source_url`, `source_authority`, `effective_date`, `legal_act_reference`) | â‌Œ No | **Critical** â€” not provided |
| Regulatory content (licensing, restrictions, procedures) | â‌Œ No | **Critical** â€” statistics/tariffs only |
| Commercial use / redistribution | â‌Œ No | **Critical** â€” explicitly prohibited |
| Machine-to-machine access | âڑ ï¸ڈ Partial â€” API limited to tariff data only | **High** â€” trade statistics not API-accessible |
| Rate limits for production | â‌Œ Unverified | **High** â€” no documented numeric limits |
| Egypt coverage | âœ… Yes | Minor â€” tariff data only via API |

**Contract Gap Summary:**
1. **Commercial use prohibition** â€” fundamental incompatibility with DEM's operational model
2. **No regulatory content** â€” WITS provides trade flows and tariffs, not licensing, restrictions, or customs procedures
3. **No per-record provenance** â€” implicit dataset-level only, not record-level traceability
4. **Limited API scope** â€” only tariff data via API; statistics require manual download

---

### G1 Verdict

**WITS Disqualified**

**Reason:** World Bank Terms of Use explicitly prohibit commercial use of WITS data via API, including "charging to redistribute them, or charging to create derivative works based on them." DEM is a commercial system. This is a fundamental incompatibility that cannot be resolved without explicit written permission from World Bank.

**Secondary disqualifiers:**
- No regulatory content (statistics/tariffs only)
- No per-record provenance fields in API responses
- API limited to tariff data; trade statistics not programmatically accessible

---

### Exact Next Action

**Report to Project Owner:** All 5 evaluated candidates for WP-38a are disqualified. No viable first provider remains.

**Project Owner must decide:**
1. Expand search to external regulatory sources beyond the original 20-source portfolio
2. Seek written commercial-use exception from World Bank for WITS (low probability of success)
3. Revise `KNOWLEDGE_INGESTION_CONTRACT.md` scope to accept trade statistics as valid External Intelligence
4. Accept web scraping for official government sources despite stability concerns
5. Defer WP-38a until a viable candidate emerges

**Next Decision Required:** G2 — Adapter Specification Review. No Task 2 implementation until G2 approval is recorded.













