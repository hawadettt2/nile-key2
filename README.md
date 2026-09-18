# Nile Key Platform

## منصة مفتاح النيل الرقمية

Digital platform for managing Egyptian exports — vegetables, fruits, and food products.

**Client:** شركة مفتاح النيل للاستثمار والتجارة الدولية ذ.م.م

Nile Key is an Intelligent Operating Platform with Digital Export Manager (DEM) as the Executive Intelligence Layer. The ERP and operational services are the execution layer; DEM is the executive intelligence layer that coordinates and orchestrates export operations autonomously.

---

## Structure

```
nile-key2/
├── PLAN.md                    # Build plan (Master Roadmap v2.1 — Single Source of Truth)
├── README.md                  # This file
├── CHANGELOG.md               # Version history
├── CURRENT_STATUS.md          # Live project status
├── TECH_DEBT.md               # Technical debt register
└── docs/
    └── appendices/
        ├── UAT_CHECKLIST.md   # Manual UAT checklist
        └── WORK_PACKAGE_PLAN.md # Historical archive: .kilo/plans/archive/WORK_PACKAGE_PLAN.md
├── TECH_DEBT.md               # Technical debt register
├── CURRENT_STATUS.md          # Project state
├── backend/                   # FastAPI backend
│   ├── main.py                # Entry point
│   ├── requirements.txt       # Python dependencies
│   ├── .env.example           # Environment template
│   ├── Dockerfile             # Backend container image
│   ├── Dockerfile.dev         # Backend development image
│   ├── alembic.ini            # Alembic migration config
│   ├── alembic/               # Migration scripts
│   └── app/
│       ├── core/              # Config, Database, Security, Schedulers
│       ├── models/            # SQLAlchemy target metadata
│       ├── schemas/           # Pydantic schemas (18 modules)
│       ├── routers/           # FastAPI routers (16 registered in main.py)
│       ├── services/          # Business logic (19 service modules excluding init files)
│       └── agent/             # DEM, Memory, Knowledge, Monitoring
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── main.tsx           # React entry point
│   │   ├── App.tsx            # Route definitions
│   │       ├── pages/             # 11 application pages
│   │   ├── components/        # Layout + UI components
│   │   ├── services/          # API client
│   │   ├── store/             # Auth store (Zustand)
│   │   ├── locales/           # i18n (ar/en)
│   │   └── lib/               # i18n config
│   ├── Dockerfile             # Frontend container image
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
├── docs/
│   └── architecture/          # Architecture documents
└── docker-compose.yml         # Docker Compose orchestration
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui |
| Backend | Python FastAPI + Uvicorn |
| Database | SQLite (MVP) |
| Auth | JWT (PyJWT) + bcrypt |
| i18n | i18next (Arabic/English RTL) |
| Charts | Recharts |
| Scheduling | APScheduler |
| Migrations | Alembic |
| Testing | pytest + Vitest |

## Registered API Routers (16)

1. **Auth** — JWT authentication, role-based access
2. **Suppliers** — CRUD + certificates
3. **Customers** — CRUD + CSV import
4. **Shipping** — Rates, tracking, shipments, provider abstraction
5. **Invoices** — Invoice management, validation, cancellation
6. **Customs** — HS codes, duty calculation, declarations
7. **Documents** — Upload, templates, metadata
8. **Resources** — Guides, regulations, opportunities
9. **ETA** — Egyptian Tax Authority e-invoicing, receipts, batch submission
10. **Notifications** — Email triggers, notification preferences
11. **Audit** — Centralized audit logging
12. **Workflow** — Export workflow lifecycle management
13. **Digital Export Manager** — Digital Export Manager
14. **Digital Export Manager** — Session management, missions, tools facade
15. **Knowledge Graph** — Entity relationship graph
16. **Trade Intelligence** — Supplier/buyer analysis, trends, comparisons

## Business Capabilities

| # | Capability | Status |
|---|-----------|--------|
| 1 | ETA Compliance | ✅ Implemented (WP-19) |
| 2 | Shipping Management | ✅ Implemented (WP-20) |
| 3 | Customs Clearance | ✅ Implemented |
| 4 | Supplier Management | ✅ Implemented |
| 5 | Customer Management | ✅ Implemented |
| 6 | Invoice Management | ✅ Implemented |
| 7 | Document Management | ✅ Implemented |
| 8 | Export Operations | ✅ Implemented (WP-21) |
| 9 | Trade Intelligence | ⚠️ Partial — UN Comtrade preview API only (500 records, HS-level bilateral) |
| 10 | Knowledge Graph | ✅ Implemented (WP-32) |
| 11 | Digital Export Manager | ✅ Implemented (WP-30) |
| 12 | AI Memory | ✅ Implemented (WP-31) |
| 13 | Market Opportunity | ❌ Not Available — No approved provider |
| 14 | Market Access | ❌ Not Available — WTO Timeseries pending governance approval |
| 15 | Regulatory / SPS-TBT | ❌ Not Available — Complementary only (WTO ePing) |
| 16 | Rules of Origin | ❌ Not Available — No approved provider |
| 17 | Administration | ✅ Implemented |
| 18 | Reports & Dashboard | ✅ Implemented (WP-21) |
| 19 | Audit & Compliance | ✅ Implemented (WP-21) |
| 20 | Notifications | ✅ Implemented (WP-21) |
| 21 | Logistics | ⚠️ Partial — World Bank LPI country-level scores only (not route-level) |
| 22 | Agrifood Intelligence | ❌ Not Available — FAOSTAT inactive |

**Note:** Capability status reflects proven operational evidence only. Registered ≠ Available. Complementary ≠ Authoritative. See `CURRENT_STATUS.md` for full provider truth model.

## Frontend Pages (22)

1. **Login** — Authentication page
2. **Dashboard** — Live statistics and widgets
3. **Suppliers** — Supplier management
4. **Customers** — Customer management + CSV import
5. **Shipments** — Shipment tracking and management
6. **Invoices** — Invoice management
7. **Customs** — HS codes and declarations
8. **Documents** — Document upload and management
9. **Resources** — Guides and regulations
10. **Notifications** — Notification list and management
11. **Profile** — User profile management
12. **Digital Export Manager** — DEM landing, connect/disconnect, session management
13. **DEM Sessions** — Session history and detail
14. **DEM Missions** — Mission dashboard and detail with execution progress
15. **DEM Mission Composer** — Submit new missions (8 types)
16. **DEM Approvals** — Manager approval inbox
17. **DEM Tools** — Tools registry viewer
18. **Knowledge Graph** — Entity search and relationship exploration
19. **Trade Intelligence** — Supplier analysis and trend detection

## Testing

- **876+ passing pytest tests** covering:
  - Auth and RBAC
  - API endpoint coverage for all 16 registered routers
  - Service-layer unit tests for all service modules
  - Digital Export Manager, Memory, Knowledge Graph, Trade Intelligence tests
  - Frontend: Vitest + React Testing Library
- Run backend tests: `cd backend && python -m pytest tests/ -v`
- Run frontend tests: `cd frontend && npm test`

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
API docs at `http://localhost:8000/docs`

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deployment

| Component | Platform | Cost |
|-----------|----------|------|
| Frontend | GitHub Pages / Docker | Free |
| Backend | Docker Compose / PythonAnywhere | Free |

See PLAN.md Section 24 for deployment instructions.

## Work Packages

| Phase | Work Packages | Status |
|-------|--------------|--------|
| Phase 0: Baseline Freeze + Security | Phase 0 | ✅ Complete |
| Phase 1: Honest Commercial Promise | Phase 1 | ✅ Complete |
| Phase 2: Capability Truth Model | Phase 2 | ✅ Complete |
| Phase 3: Source Reality Revalidation | Phase 3 | ✅ Complete |
| Phase 4: Semantic Integrity + Readiness Governance | Phase 4 | ✅ Complete |
| Phase 5: Existing Provider Activation & Repair | Phase 5 | ✅ Complete |
| Phase 6: Knowledge Gap Closure | Phase 6 | ✅ Complete |
| Phase 7: Source Candidate Evaluation | Phase 7 | ✅ Complete |
| Phase 8: Research + Evidence + BI Alignment | Phase 8 | ✅ Complete |
| Phase 9: Decision + Strategic Reasoning Integrity | Phase 9 | ✅ Complete |
| Phase 10: Country / Product / Route Readiness | Phase 10 | ✅ Complete |
| Phase 11: End-to-End Decision-Safe + Response-Safe Acceptance | Phase 11 | ✅ Complete |
| Phase 12: Governance / Documentation Reconciliation | Phase 12 | 🔄 In Progress |
| Phase 13: Final Closure | Phase 13 | ⏳ Pending |
| Legacy Work Packages | WP-01 through WP-42, WP-ORM-001/002, WP-DEM-001a/002 | ✅ Complete (Historical) |

---

**Built:** 2026-07-21 | **Version:** 1.1.0-MVP | **Baseline:** WP-40
