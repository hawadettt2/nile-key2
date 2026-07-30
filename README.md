# Nile Key Platform

## منصة مفتاح النيل الرقمية

Digital platform for managing Egyptian exports — vegetables, fruits, and food products.

**Client:** شركة مفتاح النيل للاستثمار والتجارة الدولية ذ.م.م

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
| 9 | Trade Intelligence | ✅ Implemented (WP-33) |
| 10 | Knowledge Graph | ✅ Implemented (WP-32) |
| 11 | Digital Export Manager | ✅ Implemented (WP-30) |
| 12 | AI Memory | ✅ Implemented (WP-31) |
| 17 | Administration | ✅ Implemented |
| 18 | Reports & Dashboard | ✅ Implemented (WP-21) |
| 19 | Audit & Compliance | ✅ Implemented (WP-21) |
| 20 | Notifications | ✅ Implemented (WP-21) |

## Frontend Pages (11)

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

## Testing

- **876+ passing pytest tests** covering:
  - Auth and RBAC
  - API endpoint coverage for all 16 registered routers
  - Service-layer unit tests for all service modules
  - Agent, Memory, Knowledge Graph, Trade Intelligence tests
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
| Phase 1: Foundation | WP-01 through WP-18 | ✅ Complete |
| Phase 1.5: Business Logic Alignment | WP-19, WP-20, WP-21 | ✅ Complete |
| Phase 2: Intelligent Platform | WP-30B through WP-30I, WP-31, WP-32, WP-33 | ✅ Complete |
| Phase 3: Production & Deployment | WP-40 | ✅ Complete |
| Phase 3: Production & Deployment | WP-41 (Documentation) | 🔴 Planned |
| Phase 3: Production & Deployment | WP-42 (Owner Acceptance) | 🔴 Planned |

---

**Built:** 2026-07-21 | **Version:** 1.1.0-MVP | **Baseline:** WP-40
