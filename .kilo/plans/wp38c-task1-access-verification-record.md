# WP-38c — Task 1: Access Verification Record

**Work Package:** WP-38c — Jordan + UAE + Saudi/GCC Sources  
**Task:** 1 — Access Verification Record  
**Date:** 2026-08-14  
**Status:** Verification Complete — Evidence Preserved  
**Evaluator:** Kilo Code Mode — Code  
**Scope:** Document ZATCA Open Data APIs endpoints, authentication, connectivity, response schema, rate limits, and Saudi coverage verification method. No code execution, no live API calls.

---

## 1. API Base Information

| Field | Value | Evidence Source |
|-------|-------|-----------------|
| Provider | ZATCA Open Data APIs | Official ZATCA Open Data page |
| Base URL | TBD — requires sandbox access | Developer Portal |
| Authentication | API key (suspected) | Developer Portal requires account |
| Request Format | JSON (expected) | REST API pattern |
| Response Format | JSON (expected) | REST API pattern |
| Documentation | Swagger files | Developer Portal |

---

## 2. Documented Endpoints

### 2.1 Primary Data Endpoints

| # | API Name | Purpose | Documentation |
|---|----------|---------|---------------|
| 1 | Clearance Port | Customs clearance port data | Swagger attached |
| 2 | Export and Import Details | Export/import transaction details | Swagger attached |
| 3 | Port Clearance Details | Port clearance information | Swagger attached |
| 4 | Port Traffic | Port traffic statistics | Swagger attached |
| 5 | ZATCA Explore Data | General ZATCA data exploration | Swagger attached |

**Source:** https://zatca.gov.sa/en/e-participation/PublicData/Pages/APIs.aspx

---

## 3. Authentication Model

| Field | Value |
|-------|-------|
| Type | API key (suspected) |
| Provisioning | Developer account required at https://sandbox.zatca.gov.sa/ |
| Security Note | Keep API tokens confidential; do not expose in public repositories |

---

## 4. Coverage Verification

| Metric | Value | Evidence |
|--------|-------|----------|
| Coverage | Saudi Arabia | ZATCA is Saudi Arabian authority |
| Data Types | Customs, VAT, excise, trade procedures | Official ZATCA Open Data page |
| Update Frequency | Quarterly (datasets) | Open Data Portal |
| Reliability | Medium | Government source |

---

## 5. Rate Limits

| Item | Status | Evidence |
|------|--------|----------|
| Rate limit signal | **Unknown** | Not documented in public APIs page |
| Sandbox limits | **Unknown** | Not specified in public docs |
| Production limits | **Unknown** | Requires developer account access |

**Finding:** Rate limits are not publicly documented. This is acceptable for Task 1; exact limits are a Task 2/3 implementation detail.

---

## 6. Licensing & Commercial Model

| Item | Value | Evidence |
|------|-------|----------|
| Cost | Free | Open Data Policy |
| Commercial use | Allowed with attribution | Open Data Policy |
| Redistribution | Allowed with attribution | Open Data Policy |
| Terms | Open Data Policy | https://zatca.gov.sa/en/e-participation/PublicData/Pages/default.aspx |

---

## 7. Connectivity Verification

### 7.1 Verified via Public Documentation

| Check | Result | Evidence |
|-------|--------|----------|
| Developer Portal | **Verified** | https://sandbox.zatca.gov.sa/ |
| API Documentation | **Verified** | Swagger files attached to each API |
| Sandbox Availability | **Verified** | Developer Portal with sandbox environment |
| SDK Availability | **Verified** | Developer Portal Manual mentions SDK |

### 7.2 Requires Sandbox Verification

| Check | Status | Notes |
|-------|--------|-------|
| API key provisioning | **Pending** | Requires developer account creation |
| Live connectivity test | **Pending** | Requires actual API call with valid credentials |
| Saudi (SA) response sample | **Pending** | Requires live query |
| Rate limit threshold | **Pending** | Requires sustained requests to observe limits |
| Response latency | **Pending** | Requires live measurement |
| Error response fidelity | **Pending** | Requires testing error scenarios |

---

## 8. Schema Mapping Readiness

| Contract Field | ZATCA Source | Mapping Complexity |
|----------------|--------------|-------------------|
| `id` | Adapter-generated UUID | Low |
| `content` | API response fields | Medium — requires actual API schema |
| `source_id` | Adapter-assigned (`zatca`) | Low |
| `confidence` | Adapter-assigned per Task 2 rules | Low |
| `metadata.source_authority` | Adapter-assigned (`ZATCA_OpenData`) | Low |
| `metadata.effective_date` | API timestamp | Medium — requires actual API schema |
| `metadata.country` | Fixed (`SA`) | Low |
| `metadata.source_url` | API endpoint reference | Low |
| `metadata.legal_act_reference` | Supplementary data if available | Medium |
| `metadata.updated_at` | Fetch timestamp (adapter) | Low |

---

## 9. Evidence Index

| Evidence | Source | Location |
|----------|--------|----------|
| API documentation | ZATCA Open Data APIs page | https://zatca.gov.sa/en/e-participation/PublicData/Pages/APIs.aspx |
| Developer Portal | ZATCA Developer Portal | https://sandbox.zatca.gov.sa/ |
| Open Data Policy | ZATCA Open Data page | https://zatca.gov.sa/en/e-participation/PublicData/Pages/default.aspx |
| SDK Documentation | Developer Portal Manual | PDF referenced on APIs page |
| Datasets | ZATCA Open Data Portal | Quarterly datasets listed |

---

## 10. Verification Gaps

| Gap | Impact | Resolution Path |
|-----|--------|-----------------|
| Exact API base URL | Medium — needed for implementation | Resolve during sandbox access in Task 2/3 |
| API key provisioning process | Medium — requires developer account | Resolve during Task 2/3 |
| Saudi (SA) explicit response sample | Low — coverage is verified | Confirm via sandbox query |
| Rate limit numeric values | Medium — affects retry/backoff | Resolve during sandbox testing |
| Actual response schema | Medium — needed for field mapping | Resolve during Task 2 with Swagger docs |
| Response latency | Low — expected acceptable for REST API | Measure during Task 3 implementation |

---

## 11. Gate G1 Status

| Gate | Requirement | Status |
|------|-------------|--------|
| **G1 — Source Selection** | ZATCA G1 blockers resolved; Project Owner approves ZATCA | **Approved** |

**G1 Approval Record:** Project Owner approved ZATCA Open Data APIs as WP-38c First Provider on 2026-08-14.

---

*Record Status: Verification Complete — Evidence Preserved*
