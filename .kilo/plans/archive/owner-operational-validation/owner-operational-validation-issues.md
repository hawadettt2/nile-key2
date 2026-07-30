# OV-001 Issues Registry

**Phase:** Operational Readiness — Owner Perspective  
**Work Package:** OV-001  

**Issue ID Convention:** `OV-YYYYMMDD-NNN`

---

## Issue Template

| ID | Stage | Severity | Description | Evidence | Status | Owner |
|----|-------|----------|-------------|----------|--------|-------|
| OV-YYYYMMDD-001 | | Critical/Major/Minor | | | Open/Fixed/WontFix | |

---

## Open Issues

| ID | Stage | Severity | Description | Evidence | Owner |
|----|-------|----------|-------------|----------|-------|
| (none) | | | | | |

---

## Closed Issues

| ID | Stage | Severity | Description | Resolution | Owner |
|----|-------|----------|-------------|------------|-------|
| OV-20260727-001 | 3 | Minor | Shipment DELETE endpoint returns 405 Method Not Allowed | Test script deviated from governing spec; DELETE is not in UAT_CHECKLIST.md for Shipments | Implementation Engineer |
| OV-20260727-002 | 3 | Minor | Invoice DELETE endpoint returns 405 Method Not Allowed | Test script deviated from governing spec; DELETE is not in UAT_CHECKLIST.md for Invoices (Cancel is the official workflow) | Implementation Engineer |
| OV-20260727-003 | 3 | Minor | Customs Declaration GET returns 500 due to `documents` field stored as JSON string but expected as list in response schema | Fixed in `backend/app/services/customs.py` by adding JSON deserialization in `_customs_row_to_response` | Implementation Engineer |

---

**Last Updated:** 2026-07-27  
**Executor:** Kilo AI agent
