# خطة البناء — منصة مفتاح النيل الرقمية
# Nile Key Digital Platform — Build Plan

**التاريخ:** 2026-06-28  
**الإصدار:** 1.0.0-MVP  
**المعمار:** Microservices + Static Frontend  
**المنصة الأساسية:** FastAPI + React + SQLite

---

## 1. الهوية الاستراتيجية

**العميل:** شركة مفتاح النيل للاستثمار والتجارة الدولية ذ.م.م  
**النشاط:** تصدير المنتجات المصرية (خضار، فاكهة، منتجات غذائية)  
**الترخيص:** مسجلة ومرخصة من هيئة الاستثمار المصرية  
**الرؤية:** التحول إلى منصة رقمية متكاملة وبوابة استراتيجية للصادرات المصرية  
**الدومين:** nile-key.com

---

## 2. القيود غير القابلة للتفاوض

1. ❌ لا Frappe Framework
2. ❌ لا ERPNext
3. ❌ لا MariaDB/Redis/Bench
4. ❌ لا بطاقة فيزا دولية
5. ✅ Frontend مجاني 100% على GitHub Pages
6. ✅ Backend بتكلفة صفرية على PythonAnywhere Free
7. ✅ استخراج منطق HTTP/API من تطبيقات Frappe وإعادة كتابته
8. ✅ واجهة عربية/إنجليزية (RTL)
9. ⏰ الوقت حرج — MVP فوري

---

## 3. المعمارية التقنية

```
┌─────────────────────────────────────────┐
│         GitHub Pages                     │
│     (React App - Static Hosting)         │
│           nile-key.com                   │
└──────────────────┬───────────────────────┘
                   │
        ┌──────────▼──────────┐
        │    API Gateway       │
        │   FastAPI Backend    │
        │    PythonAnywhere    │
        └──────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼────┐  ┌────▼────┐  ┌────▼────┐
│Shipping│  │E-Invoice│  │Customs  │
│Service │  │Service  │  │Service  │
│(SQLite)│  │(SQLite) │  │(SQLite) │
└────────┘  └─────────┘  └─────────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
        ┌──────────▼──────────┐
        │   Core Services      │
        │  - Auth/Roles        │
        │  - Suppliers         │
        │  - Customers         │
        │  - Documents         │
        │  - Resources         │
        └──────────────────────┘
```

---

## 4. التقنيات

| الطبقة | التقنية |
|--------|---------|
| Frontend | React 18 + Vite + Tailwind CSS |
| Backend | Python FastAPI + Uvicorn |
| Database | SQLite (MVP) → PostgreSQL (Production) |
| Auth | JWT (PyJWT) |
| HTTP Client | httpx (Backend) + axios (Frontend) |
| Validation | Pydantic (Backend) + Zod (Frontend) |
| State | Zustand + React Query |
| i18n | i18next (ar/en) |
| Charts | Recharts |
| Tables | TanStack Table |

---

## 5. الخدمات الخلفية (8 Services)

### 5.1 Shipping Service
- المسارات: /api/v1/shipping/rates, /shipments, /track/{id}, /label

### 5.2 E-Invoicing Service
- المسارات: /api/v1/invoices, /validate, /cancel, /status

### 5.3 Customs Service
- المسارات: /api/v1/customs/declarations, /hs-codes, /calculate-duties

### 5.4 Suppliers Service
- المسارات: /api/v1/suppliers (CRUD + certificates)

### 5.5 Customers/Importers Service
- المسارات: /api/v1/customers (CRUD + interactions + import CSV)

### 5.6 Documents & Templates Service
- المسارات: /api/v1/documents/templates, /generate, /upload

### 5.7 Auth & Roles Service
- المسارات: /api/v1/auth/login, /register, /refresh, /me
- الأدوار: Owner, Manager, Sales, Admin Staff, Accountant, Logistics, Supplier, Customer

### 5.8 Resources & Opportunities Service
- المسارات: /api/v1/resources, /search

---

## 6. قاعدة البيانات — الجداول

- users, roles, suppliers, customers, shipments, invoices, customs_declarations, hs_codes, documents, resources, audit_logs, system_settings

---

## 7. خارطة الطريق (Roadmap)

### المرحلة 1: الأساس ✅
- ✅ إنشاء هيكل المشروع
- ✅ بناء Auth Service + Database Schema + Seed
- ✅ إعداد FastAPI main app + CORS

### المرحلة 2: الخدمات الأساسية ✅
- ✅ Shipping Service + E-Invoicing + Dashboard

### المرحلة 3: الخدمات الثانوية ✅
- ✅ Suppliers + Customers + Documents + Customs

### المرحلة 4: التكامل والنشر ⏳
- ☐ GitHub Pages + PythonAnywhere + Domain

---

## 8. الاستضافة
- **Frontend:** GitHub Pages (مجاني)
- **Backend:** PythonAnywhere Free Tier (مجاني)

---

## 9. الأمان
- JWT: access_token (24h) + refresh_token (7d)
- CORS: مسموح فقط لـ nile-key.com و localhost
- Rate Limiting: 100 طلب/دقيقة
- File Upload: max 10MB

---

## 10. ملاحظة أخيرة
هذا الملف هو المرجع الوحيد للمشروع. أي تغيير يُسجل هنا أولاً.
