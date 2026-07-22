# Repository Intelligence Report

**Version:** 1.0  
**Generated:** 2026-06-30  
**Phases:** Architecture Audit (Phase 1) + Repository Intelligence (Phase 1.5)  
**Status:** Historical snapshot — Authority has moved to `PLAN.md` (Master Roadmap v2.1) and `docs/architecture/PROJECT_BASELINE.md`

> **Note:** This report reflects the state as of 2026-06-30. All critical and high-priority issues listed in this document have been resolved through subsequent Work Packages. For the current project state, refer to `docs/architecture/PROJECT_BASELINE.md` and `docs/architecture/ENGINEERING_MEMORY.md`.

---

## 1. Executive Summary

Nile Key is a production-grade digital platform for Egyptian exports with a FastAPI backend (SQLite) and React frontend. The codebase demonstrates a functional prototype but contains **critical architectural debt**:

- **CRITICAL:** Database schema does not match Pydantic schemas
- **CRITICAL:** Hardcoded default secrets in configuration
- **CRITICAL:** No business logic layer (violates architecture charter)
- **HIGH:** Massive code duplication across all routers
- **HIGH:** SQLite unsuitable for production workloads

> **Note:** This report reflects the state as of 2026-06-30. All issues listed have been resolved through WP-01 through WP-18. The current authority for all architectural decisions is `PLAN.md` (Master Roadmap v2.1).

---

## 2. Repository Structure

```
nile-key-project/
├── PLAN.md                          # Master Roadmap v2.1 — Single Source of Truth
├── ARCHITECTURE_CHARTER.md          # Deprecated — content merged into PLAN.md
├── backend/
│   ├── main.py                      # FastAPI entry point
│   ├── requirements.txt             # 12 dependencies
│   ├── .env.example                 # Incomplete env template
│   └── app/
│       ├── core/
│       │   ├── config.py            # Settings (insecure defaults)
│       │   ├── database.py          # SQLite init
│       │   └── security.py          # JWT + password hashing
│       ├── routers/                 # 8 routers
│       ├── schemas/                 # Pydantic models
│       ├── models/                  # Empty stub
│       └── services/                # Empty stub
├── docs/
│   └── architecture/
│       ├── PLAN.md                  # Master Roadmap v2.1 (moved from root)
│       ├── ADR-0001-shipments-legacy-columns.md  # Architecture decisions
│       ├── ENGINEERING_MEMORY.md    # Current state
│       ├── WORK_PACKAGE_PLAN.md     # Execution roadmap
│       ├── PROJECT_BASELINE.md      # Project snapshot
│       └── REPOSITORY_INTELLIGENCE.md  # This file
└── frontend/
    ├── package.json                 # 75 dependencies
    ├── vite.config.ts               # Vite + React
    └── src/
        ├── main.tsx                 # React entry point
        ├── App.tsx                  # Route definitions
        ├── pages/                   # 8 pages
        ├── services/api.ts          # Axios client
        └── store/authStore.ts       # Zustand auth state
```

---

## 3. Architecture Overview

Per PLAN.md Section 9.4: Refactor > Rewrite, Simplify > Expand, Reuse > Duplicate, Correctness > Speed

Source of Truth Priority (never reverse):
1. Backend Pydantic Schemas
2. FastAPI API Contract
3. Business Rules
4. Database Schema
5. Frontend Types
6. Documentation

> **Note:** At the time of this report (2026-06-30), architectural principles were governed by ARCHITECTURE_CHARTER.md. All principles from that document have been merged into PLAN.md Section 9 (Architecture Principles).

---

## 4. Dependency Map

- main.py → core/database, core/security, routers/*
- Each router → core/database, core/security, schemas/*

---

## 5. Module Relationship Graph

All routers depend on core/database (get_db) and core/security (for auth). No circular dependencies. Empty models/ and services/ packages.

---

## 6. Backend Architecture

Entry: backend/main.py | Core: config (insecure), database (schema mismatch), security (functional) | Routers: 8 modules (auth, shipping, invoice, suppliers, customers, customs, resources, documents)

Charter Violations:
- Section 10: Business logic in routers, not services layer
- Section 13: Wildcard CORS
- Section 16: Services layer empty

---

## 7. Frontend Architecture

Entry: frontend/src/main.tsx | React 18 + TypeScript | 8 pages consuming API endpoints

---

## 8. Database Analysis

**CRITICAL MISMATCHES:**

| Entity | Schema vs DB |
|--------|-------------|
| users | Missing: username, phone, company; password_hash vs hashed_password |
| suppliers | Missing: name_en, contact_person, country, commercial_registry |
| customers | name→company_name mismatch; missing: contact_person, address, city, tax_id, import_license, category |
| shipments | Missing: reference, supplier_id, customer_id, origin, destination, weight, weight_unit, dimensions, items_count, description, eta |
| invoices | Missing: invoice_number, customer_id, supplier_id, subtotal, tax_rate, items |
| customs_declarations | hs_code_id vs hs_code text |
| hs_codes | Missing: description_ar, restrictions |
| resources | Missing: title_ar, description_ar, metadata, is_active |
| documents | Missing: template_type, entity_type, entity_id, metadata |

---

## 9. API Contract

32 endpoints across 8 routers (auth, shipping, invoice, suppliers, customers, customs, resources, documents)

---

## 10. Frontend ↔ Backend Mapping

| Page | Router | Endpoints |
|------|--------|-----------|
| Suppliers | suppliers | GET/POST/PUT/DELETE |
| Customers | customers | GET/POST/PUT/DELETE + import |
| Shipments | shipping | GET/POST/PUT + rates |
| Invoices | invoice | GET/POST + validate/cancel |
| Customs | customs | hs-codes, calculate-duties, declarations |
| Documents | documents | GET/POST + upload/delete |
| Resources | resources | GET + search, POST/DELETE |
| Login | auth | login, register, me |
| Dashboard | all | stats aggregation |

---

## 11. Source of Truth

Database schema must follow Pydantic schemas (charter Section 9). Currently violates this.

---

## 12. Duplicate Logic

- Dynamic SQL query building: 8x duplication (all routers)
- Connection management: 16x duplication
- Timestamp handling: Repeated everywhere

---

## 13. Technical Debt

- Empty models/services packages
- Hardcoded SECRET_KEY
- Wildcard CORS
- Password algorithm mismatch (pbkdf2_sha256 vs bcrypt)
- SQLite production limitation
- No migrations
- Missing .env
- No Dockerfile

---

## 14. Security Review

| Issue | Risk |
|-------|------|
| Default SECRET_KEY | Critical |
| Wildcard CORS | Critical |
| No rate limiting | Medium |

---

## 15. Deployment Readiness

| Requirement | Status |
|-------------|--------|
| Build script | ✅ Frontend |
| Migrations | ❌ None |
| Containerization | ❌ None |
| Secrets | ❌ Hardcoded |

---

## 16. Risk Matrix

**P0 - CRITICAL:** Database Schema Mismatch, Hardcoded Secret, Wildcard CORS

**P1 - HIGH:** Missing Services Layer, Code Duplication, SQLite Limitation

**P2 - MEDIUM:** No Migrations, Env Mismatch, Password Algorithm

**P3 - LOW:** Debug Mode, No Rate Limiting

---

## 17. Unresolved Questions

- Replace SQLite with PostgreSQL? (Yes per charter)
- Password algorithm? (Verify bcrypt intended)

---

## 18. Execution Roadmap

Phase 2: Fix P0 | Phase 3: Services layer | Phase 4: SQL helpers | Phase 5: Tests | Phase 6-7: Production

*End of Report*