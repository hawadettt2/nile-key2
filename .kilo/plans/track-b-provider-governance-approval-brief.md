# Track B — Governance Approval Brief

**Purpose:** Obtain Governance Approval for activation of inactive providers required to close Residual Gaps G3, G4, G5.  
**Status:** PENDING GOVERNANCE APPROVAL — NO APPROVAL GRANTED  
**Authority Required:** Business Question Authority / Project Owner / Governance Authority

---

## 1. TradeData

| Field | Value |
|-------|-------|
| **Required Gaps** | G1 (HS6 trade), G3 (Market Access — tariff/entry procedures) |
| **Business Need** | Provide HS-level bilateral trade data and tariff schedules for S1–S5. UN Comtrade is RESTRICTED/NOT CLEARED for commercial use; TradeData is the fallback provider for trade evidence. |
| **Expected Value** | HS6 trade flows with commercial-use clearance; tariff lookup per HS6 per destination |
| **Scope** | Global coverage; HS-level product granularity; bilateral Egypt↔Y |
| **Licensing Status** | Commercial — requires licensing review and commercial-use clearance |
| **Ceiling Impact** | +1 to operational count (from 2 to 3) if activated |
| **Required Credentials/Data** | TRADEDATA_API_KEY |
| **Activation Purpose** | Replace UN Comtrade for commercial-use-cleared trade data; provide market access tariff data |
| **Required Approval** | Governance Approval for activation + commercial-use clearance verification |

---

## 2. Moaah

| Field | Value |
|-------|-------|
| **Required Gaps** | G3 (Market Access — Saudi tariff/entry), G4 (Regulatory — Saudi/Egypt SPS-TBT), G5 (RoO — Agadir/EU-Egypt/COMESA if China scope proven) |
| **Business Need** | Provide Saudi tariff and regulatory data for S2; potential additional coverage for S1/S3/S4/S5 if China scope proven |
| **Expected Value** | Saudi-specific tariff lookup; Saudi/Egypt regulatory requirements; potential RoO data for multiple agreements |
| **Scope** | Egypt/Saudi Arabia focused; HS-level product granularity |
| **Licensing Status** | Commercial — requires licensing review and commercial-use clearance |
| **Ceiling Impact** | +1 to operational count (from 2 to 3) if activated |
| **Required Credentials/Data** | MOAAH_API_KEY + MOAAH_BASE_URL |
| **Activation Purpose** | Cover Saudi Arabia market access and regulatory requirements; potential RoO coverage |
| **Required Approval** | Governance Approval for activation + commercial-use clearance verification. **Note:** Moaah is excluded from China Zero-Tariff path unless China scope is explicitly proven. |

---

## 3. ZATCA

| Field | Value |
|-------|-------|
| **Required Gaps** | G3 (Market Access — Saudi tariff/entry for HS080410) |
| **Business Need** | Provide Saudi tariff data as alternative/fallback to Moaah for S2 |
| **Expected Value** | Saudi tariff lookup for dates (HS080410); open-data source |
| **Scope** | Saudi Arabia only; HS-level product granularity |
| **Licensing Status** | Open Data — requires verification of terms for commercial use |
| **Ceiling Impact** | +1 to operational count (from 2 to 3) if activated |
| **Required Credentials/Data** | ZATCA_API_KEY + ZATCA_BASE_URL |
| **Activation Purpose** | Alternative Saudi tariff source if Moaah insufficient; redundant coverage for S2 |
| **Required Approval** | Governance Approval for activation + open-data terms verification |

---

## 4. GCC-Stat

| Field | Value |
|-------|-------|
| **Required Gaps** | G3 (Market Access — GCC tariff), G5 (RoO — GAFTA eligibility for S2) |
| **Business Need** | Provide GCC tariff data and GAFTA RoO eligibility criteria for S2 (Egypt→Saudi dates) |
| **Expected Value** | GCC tariff schedules; GAFTA origin criteria and documentation requirements |
| **Scope** | GCC countries only; product-level granularity |
| **Licensing Status** | Open — requires verification of terms for commercial use |
| **Ceiling Impact** | +1 to operational count (from 2 to 3) if activated |
| **Required Credentials/Data** | GCCSTAT_API_KEY + GCCSTAT_BASE_URL |
| **Activation Purpose** | Cover GCC market access and GAFTA RoO for S2. **Note:** GCC-Stat is GCC-scoped only; NOT applicable for COMESA, EU-Egypt, Agadir, or China Zero-Tariff. |
| **Required Approval** | Governance Approval for activation + open-data terms verification |

---

## 5. Regulations Provider

| Field | Value |
|-------|-------|
| **Required Gaps** | G4 (Regulatory/SPS-TBT for S1–S5) |
| **Business Need** | Provide product-country-specific regulatory requirements from structured data file |
| **Expected Value** | SPS/TBT/MRL lookup per HS6 per jurisdiction; structured regulatory data for multiple countries |
| **Scope** | Global (data-dependent); HS-level product granularity; jurisdiction-specific |
| **Licensing Status** | Data-file dependent — depends on source of authoritative regulatory data |
| **Ceiling Impact** | +1 to operational count (from 2 to 3) if activated |
| **Required Credentials/Data** | REGULATIONS_FILE_PATH + regulations.json data file (currently missing) |
| **Activation Purpose** | Cover regulatory/SPS-TBT requirements for all scenarios. **Note:** Requires Regulations Decision Gate to determine if local file is needed and feasible. |
| **Required Approval** | Governance Approval for activation + Regulations Decision Gate outcome + data source licensing verification |

---

## Summary

| Provider | Gaps | Licensing | Ceiling | Status |
|----------|------|-----------|---------|--------|
| TradeData | G1, G3 | Commercial | +1 | PENDING APPROVAL |
| Moaah | G3, G4, G5 | Commercial | +1 | PENDING APPROVAL |
| ZATCA | G3 | Open Data | +1 | PENDING APPROVAL |
| GCC-Stat | G3, G5 | Open | +1 | PENDING APPROVAL |
| Regulations Provider | G4 | Data-file dependent | +1 | PENDING APPROVAL |

**Total ceiling impact if all approved:** 5 additional providers → operational count would be 7 (2 current + 5 activated), which is at the maximum ceiling of 7 external operational production providers.

**Important:** No provider activation proceeds without Governance Approval. This brief is for approval request only.

---

**Prepared by:** Kilo / DEM Team  
**Date:** 2026-09-19  
**Status:** READY FOR APPROVAL — NO APPROVAL GRANTED
