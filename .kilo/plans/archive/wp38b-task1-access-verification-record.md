# WP-38b — Task 1: Access Verification Record

**Work Package:** WP-38b — Global Trade Intelligence (TradeData First Provider)  
**Task:** 1 — Access Verification Record  
**Date:** 2026-08-13  
**Status:** Verification Complete — Evidence Preserved  
**Evaluator:** Kilo Code Mode — Code  
**Scope:** Document TradeData API endpoints, authentication, connectivity, response schema, rate limits, and Egypt coverage verification method. No code execution, no live API calls.

---

## 1. API Base Information

| Field | Value | Evidence Source |
|-------|-------|-----------------|
| Provider | TradeData API | `tradedata.io` |
| Base URL | `https://api.tradedata.io` | Official docs `/docs/getting-started/introduction` |
| Authentication | Bearer token | Official docs `/docs/getting-started/authentication` |
| Request Format | JSON | Official docs `/docs/getting-started/introduction` |
| Response Format | JSON | Official docs `/docs/trade-data/detailed-transactions` |
| SDK / Code Samples | Available | Official homepage |

---

## 2. Documented Endpoints

### 2.1 Primary Data Endpoint

| Field | Value |
|-------|-------|
| Method | `POST` |
| Path | `/api/v1/tradeDetail` |
| Purpose | Detailed transaction-level trade records |
| Request Example | `{"data_coverage": 1, "date_range": [20220101, 20220130], "product_keyword": ["book"], "sort": "count", "order": "desc", "page_size": 10, "page": 1}` |
| Authentication | `Authorization: Bearer <token>` |
| Content-Type | `application/json` |

### 2.2 Supporting Endpoints

| Field | Value |
|-------|-------|
| Country Codes | `GET /api/getCountryISO2Code` |
| Purpose | Retrieve full list of supported ISO 3166-1 alpha-2 country codes |
| Notes | Used to confirm Egypt (EG) coverage |

### 2.3 Additional Product Endpoints (Documented)

| Product | Path Prefix | Notes |
|---------|-------------|-------|
| Customs Data API | `/api/v1/` | Customs and shipment records |
| Shipment Data API | `/api/v1/` | Shipment tracking |
| Import & Export Data API | `/api/v1/` | Aggregate trade statistics |
| Company Data API | `/api/v1/` | Company profiles and intelligence |
| Trade Analytics | `/api/v1/` | Market and trend analysis |
| Sanctions | `/api/v1/` | Sanctions screening |
| Business Contact | `/api/v1/` | Contact intelligence |

**Note:** Exact sub-paths for analytics, company, sanctions, and business contact endpoints are documented in the product-specific sections of the official docs. The primary integration path for WP-38b is `/api/v1/tradeDetail`.

---

## 3. Authentication Model

| Field | Value |
|-------|-------|
| Type | Bearer token |
| Header | `Authorization: Bearer <token>` |
| Key Provisioning | Sandbox key available via contact/sales; production keys provisioned within 24 hours |
| Security Note | Keep API tokens confidential; do not expose in public repositories or frontend code |

---

## 4. Request Parameters

### 4.1 Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `data_coverage` | `int` | Data coverage type (1 = Jan 2022–present, 2 = historical archive) | `1` |
| `date_range` | `array` | Date range as `[YYYYMMDD, YYYYMMDD]`, max span 3 years | `[20220101, 20221231]` |

### 4.2 Core Query Fields

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `hs_code` | `array` | HS Code (2–10 digits), multi-entry | `['01','02']` |
| `product_keyword` | `array` | Product keyword, fuzzy matching | `["car", "motor"]` |
| `exact_product_keyword` | `boolean` | Exact product description matching | `true` |
| `buyer_name` | `array` | Importer/buyer name | `["Walmart", "Amazon"]` |
| `supplier_name` | `array` | Exporter/supplier name | `["IKEA"]` |
| `origincl_country_code` | `array` | Origin country code (ISO 3166-1 alpha-2) | `['US', 'CN']` |
| `desti_country_code` | `array` | Destination country code | `['US', 'CN']` |
| `loading_port_name` | `string` | Port of loading | `NINGBO` |
| `discharge_port_name` | `string` | Port of discharge | `SINGAPORE` |

### 4.3 Range Filters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `amount_range` | `array` | Trade value range | `[1000, 5000]` |
| `weight_range` | `array` | Shipment weight range (kg) | `[200, 800]` |
| `quantity_range` | `array` | Goods quantity range | `[10, 100]` |
| `teu_range` | `array` | Container volume range (TEU) | `[2, 5]` |

### 4.4 Boolean Exclusion Filters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `excl_na_buyers` | `boolean` | Exclude buyers marked N.A. | `false` |
| `excl_logi_buyers` | `boolean` | Exclude logistics consignees | `true` |
| `excl_na_suppliers` | `boolean` | Exclude suppliers marked N.A. | `false` |
| `excl_logi_suppliers` | `boolean` | Exclude logistics shippers | `true` |

### 4.5 Pagination

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `page` | `int` | Page number (min 1, max 1000) | `10` |
| `page_size` | `int` | Page size (default 10, max 50) | `10` |
| `sort` | `string` | Field to sort by (`date`, `weight`) | `'date'` |
| `order` | `string` | Sort order (`asc`, `desc`) | `'desc'` |

---

## 5. Response Schema

### 5.1 Top-Level Structure

```json
{
  "code": 200,
  "success": true,
  "data": [ ... ],
  "msg": "success",
  "total": 137708,
  "pageSize": 10,
  "current": 1,
  "sumResult": {}
}
```

### 5.2 Transaction Record Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `dataSource` | `string` | Source of data | `"United States_Import"` |
| `date` | `string` | Transaction date | `"2025-08-22"` |
| `buyerName` | `string` | Importer/Buyer name | `"Target Corporation"` |
| `buyerAddress` | `string` | Importer/Buyer address | `"1000 Nicollet Mall, Minneapolis, MN, USA"` |
| `supplierName` | `string` | Exporter/Supplier name | `"Samsung Electronics"` |
| `supplierAddress` | `string` | Exporter/Supplier address | `"1 Samsung-ro, Suwon-si, South Korea"` |
| `originCountryCode` | `string` | Origin country code (ISO 3166-1 alpha-2) | `"KR"` |
| `destinationCountryCode` | `string` | Destination country code | `"US"` |
| `loadingPort` | `string` | Port of Loading/Origin | `"BUSAN"` |
| `dischargePort` | `string` | Port of Discharge/Destination | `"LOS ANGELES"` |
| `hsCode` | `string` | Harmonized System Code | `"854231"` |
| `hsCodeDesc` | `string` | HS code description | `"Electronic integrated circuits"` |
| `productKeyword` | `string` | Product keyword | `"smartphone"` |
| `brand` | `string` | Brand or trademark | `"SAMSUNG"` |
| `quantity` | `float` | Quantity of goods | `500` |
| `quantityUnit` | `string` | Unit of quantity | `"PCS"` |
| `weight` | `float` | Total weight (kg) | `120` |
| `price` | `float` | Unit price in USD | `199.99` |
| `tradeAmount` | `float` | Total trade amount | `999950.00` |
| `incoterms` | `string` | Incoterms | `"CIF"` |
| `transportMode` | `string` | Transport Mode | `"AIR"` |
| `masterBl` | `string` | Master Bill of Lading number | `"MAEU123456789"` |
| `customsOffice` | `string` | Customs name | `"SEOUL AIRPORT"` |
| `carrierName` | `string` | Carrier name | `"KOREAN AIR"` |
| `vesselName` | `string` | Vessel name | `"HMM ALGECIRAS"` |
| `containerNo` | `string` | Container number | `"SEGU1234567"` |
| `teu` | `float` | TEU | `3` |
| `otherInfo` | `json` | Additional information | `{...}` |
| `total` | `int` | Total number of results | `25489` |

---

## 6. Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| `200` | OK | Request was successful |
| `400` | Bad Request | Required parameter(s) missing or invalid |
| `403` | Forbidden | Invalid signature or insufficient access rights |
| `429` | Too Many Requests | Rate limit exceeded |
| `500` / `5**` | Server Errors | General server-side error; retry later |

---

## 7. Coverage Verification

### 7.1 Global Coverage

| Metric | Value | Evidence |
|--------|-------|----------|
| Total records | 10B+ | Official coverage page |
| Countries / regions | 200+ | Official coverage page |
| Customs sources | 80+ | Official coverage page |
| Companies profiled | 20M+ | Official coverage page |

### 7.2 Egypt Coverage

| Item | Status | Evidence |
|------|--------|----------|
| ISO 3166-1 alpha-2 code | `EG` | Standard; `/api/getCountryISO2Code` endpoint available |
| Explicit mention in public docs | Not found in `/coverage` or `/docs` examples | Gap — requires sandbox confirmation |
| 200+ country claim | Verified | Official coverage page |
| Verification method | `GET /api/getCountryISO2Code` | Official docs `/docs/general-pareameters/country-code` |

**Finding:** Egypt (EG) is a standard ISO 3166-1 alpha-2 code. TradeData API supports country code filtering via `origincl_country_code`, `desti_country_code`, and related parameters. The 200+ country coverage claim and the existence of `/api/getCountryISO2Code` strongly indicate Egypt coverage. Explicit confirmation requires sandbox access.

### 7.3 Data Freshness

| Market Type | Freshness | Evidence |
|-------------|-----------|----------|
| High-volume markets (USA, India, Southeast Asia) | Daily | Official docs `/docs/trade-data/detailed-transactions` |
| Other markets | Weekly or monthly | Official docs — depends on customs authority publication schedule |

---

## 8. Rate Limits

| Item | Status | Evidence |
|------|--------|----------|
| Rate limit signal | **Verified** | HTTP 429 documented in status codes |
| Exact numeric limits (RPM/RPS) | **Not publicly documented** | Pricing page states "Rate limits apply per API key" |
| Enterprise limits | **Custom** | Pricing page: "Enterprise plans add expanded coverage, higher limits and support" |
| Sandbox limits | **Unknown** | Not specified in public docs |
| Burst / excessive traffic | **Throttled** | Pricing FAQ: "High burst traffic may be throttled" |

**Finding:** Rate limits exist and are enforced (HTTP 429). Exact numeric limits are not publicly specified and must be confirmed during sandbox evaluation or via sales contact. This is acceptable for Task 1; exact limits are a Task 2/3 implementation detail.

---

## 9. Pricing & Commercial Model

| Item | Value | Evidence |
|------|-------|----------|
| Sandbox tier | Free | Official pricing page |
| Production plans | Contact sales | Official pricing page: "Plan tiers and prices are being finalised" |
| Usage measurement | API query volume + rate limits | Official pricing page |
| Enterprise options | Expanded coverage, higher limits, support | Official pricing page |
| Commercial use | Project Owner approved | WP-38b plan Section 5 + G1 approval |

---

## 10. Connectivity Verification

### 10.1 Verified via Public Documentation

| Check | Result | Evidence |
|-------|--------|----------|
| Base URL reachable | **Not tested** | No code execution per constraints |
| Authentication header format | **Verified** | `Authorization: Bearer <token>` documented |
| HTTPS enforced | **Verified** | Base URL uses `https://` |
| CORS / browser access | **Unknown** | Not documented; server-to-server integration assumed |
| SDK availability | **Verified** | Official homepage mentions SDKs and code samples |

### 10.2 Requires Sandbox Verification

| Check | Status | Notes |
|-------|--------|-------|
| API key provisioning | **Pending** | Sandbox key requires contact/sales |
| Live connectivity test | **Pending** | Requires actual API call with valid token |
| Egypt (EG) response sample | **Pending** | Requires live query with `desti_country_code: ["EG"]` |
| Rate limit threshold | **Pending** | Requires sustained requests to observe 429 |
| Response latency | **Pending** | Requires live measurement |
| Error response fidelity | **Pending** | Requires testing 400/403/429/500 scenarios |

---

## 11. Schema Mapping Readiness

| Contract Field | TradeData Source | Mapping Complexity |
|----------------|------------------|-------------------|
| `id` | Adapter-generated UUID | Low |
| `content` | `buyerName` + `supplierName` + `hsCodeDesc` + `productKeyword` | Low |
| `source_id` | Adapter-assigned (`tradedata`) | Low |
| `confidence` | Adapter-assigned per Task 2 rules | Low |
| `metadata.source_authority` | `dataSource` | Low |
| `metadata.effective_date` | `date` | Low |
| `metadata.country` | `originCountryCode` + `destinationCountryCode` | Low |
| `metadata.source_url` | `masterBl` or `containerNo` as reference | Low |
| `metadata.legal_act_reference` | `otherInfo` | Medium |
| `metadata.updated_at` | Fetch timestamp (adapter) | Low |

---

## 12. Evidence Index

| Evidence | Source | Location |
|----------|--------|----------|
| API base URL and intro | `tradedata.io/docs/getting-started/introduction` | Webrecords 2026-08-13 |
| Authentication model | `tradedata.io/docs/getting-started/authentication` | Webrecords 2026-08-13 |
| Detailed transactions schema | `tradedata.io/docs/trade-data/detailed-transactions` | Webrecords 2026-08-13 |
| Status codes | `tradedata.io/docs/getting-started/status-codes` | Webrecords 2026-08-13 |
| General parameters | `tradedata.io/docs/general-pareameters/general-pareameters` | Webrecords 2026-08-13 |
| Country code reference | `tradedata.io/docs/general-pareameters/country-code` | Webrecords 2026-08-13 |
| Coverage claims | `tradedata.io/coverage` | Webrecords 2026-08-13 |
| Pricing and sandbox | `tradedata.io/pricing` | Webrecords 2026-08-13 |
| Product catalog | `tradedata.io` homepage | Webrecords 2026-08-13 |

---

## 13. Verification Gaps

| Gap | Impact | Resolution Path |
|-----|--------|-----------------|
| Exact rate limit numeric values | Medium — affects retry/backoff configuration in Task 3 | Resolve during sandbox testing in Task 2/3 |
| Egypt (EG) explicit confirmation | Low — ISO code standard; 200+ coverage claim | Confirm via `/api/getCountryISO2Code` in sandbox |
| Live connectivity / latency | Low — expected to be acceptable for REST API | Measure during Task 3 implementation |
| Commercial terms detail | Low — Project Owner approved use model | Obtain written terms if required by legal |

---

## 14. Gate G1 Status

| Gate | Requirement | Status |
|------|-------------|--------|
| **G1 — TradeData Source Selection** | TradeData G1 blockers resolved; Project Owner approves TradeData | **Approved** |

**G1 Approval Record:** Project Owner approved TradeData API as WP-38b First Provider on 2026-08-13.

---

*Record Status: Verification Complete — Evidence Preserved*
