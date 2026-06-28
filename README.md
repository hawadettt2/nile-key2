# Nile Key Platform v1.0

## منصة مفتاح النيل الرقمية

Digital platform for managing Egyptian exports — vegetables, fruits, and food products.

**Client:** شركة مفتاح النيل للاستثمار والتجارة الدولية ذ.م.م

---

## Structure

```
nile-key2/
├── PLAN.md              # Build plan
├── DEPLOYMENT.md        # Deployment guide
├── backend/             # FastAPI backend
│   ├── main.py          # Entry point
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── core/        # Config, Database, Security
│       ├── models/      # Data models
│       ├── schemas/     # Pydantic schemas
│       ├── routers/     # API endpoints (8 services)
│       └── services/    # Business logic
└── frontend/            # React frontend
    ├── src/
    │   ├── App.tsx
    │   ├── pages/       # Dashboard, Login, CRUD pages
    │   ├── components/  # Layout, UI
    │   ├── services/    # API client
    │   ├── store/       # Auth store (Zustand)
    │   ├── locales/     # i18n (ar/en)
    │   └── lib/         # i18n config
    ├── package.json
    └── vite.config.ts
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + TypeScript + Vite + Tailwind CSS + shadcn/ui |
| Backend | Python FastAPI + Uvicorn |
| Database | SQLite (MVP) |
| Auth | JWT (PyJWT) |
| i18n | i18next (Arabic/English RTL) |
| Charts | Recharts |

## Services (8)

1. **Auth & Roles** — JWT authentication, role-based access
2. **Suppliers** — CRUD + certificates
3. **Customers** — CRUD + CSV import
4. **Shipping** — Rates, tracking, shipments
5. **E-Invoicing** — Create, validate, cancel
6. **Customs** — HS codes, duty calculation, declarations
7. **Documents** — Upload, templates
8. **Resources** — Guides, regulations, opportunities



Backend (FastAPI) — 8 خدمات
Table
الخدمة	الملف	الوصف
🔐 Auth	routers/auth.py	تسجيل دخول، JWT، أدوار
🏭 Suppliers	routers/suppliers.py	CRUD + شهادات
👥 Customers	routers/customers.py	CRUD + استيراد CSV
🚢 Shipping	routers/shipping.py	أسعار، تتبع، شحنات
🧾 Invoices	routers/invoice.py	إنشاء، تحقق، إلغاء
🛃 Customs	routers/customs.py	HS Codes، حساب رسوم
📄 Documents	routers/documents.py	رفع، قوالب
🌐 Resources	routers/resources.py	أدلة، فرص
Frontend (React) — صفحات كاملة
📊 Dashboard — إحصائيات + رسوم بيانية
🔐 Login — تسجيل دخول/حساب جديد
🏭 Suppliers — إدارة الموردين
👥 Customers — إدارة العملاء + CSV
🚢 Shipments — شحنات + أسعار
🧾 Invoices — فواتير + أصناف
🛃 Customs — جمارك + HS Codes
📄 Documents — مستندات
🌐 Resources — موارد




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

### Default Login
- Username: `admin`
- Password: `admin123`

## Deployment

| Component | Platform | Cost |
|-----------|----------|------|
| Frontend | GitHub Pages | Free |
| Backend | PythonAnywhere | Free |

See `DEPLOYMENT.md` for details.

---

**Built:** 2026-06-28 | **Version:** 1.0.0-MVP
