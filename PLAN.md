# خطة البناء — منصة مفتاح النيل الرقمية
# Nile Key Digital Platform — Build Plan

**التاريخ:** 2026-07-04
**الإصدار:** 1.1.0-MVP
**المعمار:** FastAPI Backend + React Frontend + SQLite
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
6. ✅ Backend قابل للنشر على Docker / PythonAnywhere Free
7. ✅ استخراج منطق HTTP/API من تطبيقات Frappe وإعادة كتابته
8. ✅ واجهة عربية/إنجليزية (RTL)
9. ✅ البنية تحتاج التحقق قبل الإنتاج (Docker + توثيق)

---

## 3. المعمارية التقنية

```
┌─────────────────────────────────────────┐
│         GitHub Pages / Docker            │
│     (React App - Static Hosting)         │
│           nile-key.com                   │
└──────────────────┬───────────────────────┘
                    │
         ┌──────────▼──────────┐
         │    API Gateway       │
         │   FastAPI Backend    │
         │   Docker / PA Free   │
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
| Frontend | React 18 + Vite + Tailwind CSS + shadcn/ui |
| Backend | Python FastAPI + Uvicorn |
| Database | SQLite (MVP) → PostgreSQL (Production) |
| Auth | JWT (PyJWT) + bcrypt |
| HTTP Client | httpx (Backend) + axios (Frontend) |
| Validation | Pydantic (Backend) |
| State | Zustand + React Query |
| i18n | i18next (ar/en) |
| Charts | Recharts |
| Tables | TanStack Table |
| Containerization | Docker + Docker Compose |

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

- users, roles, suppliers, customers, shipments, invoices, customs_declarations, hs_codes, documents, resources

---

## 7. تهيئة قاعدة البيانات

1. التطبيق يستدعي `init_db()` عند بدء التشغيل
2. `init_db()` ينشئ الجداول لو غير موجودة، ويضيف الأعمدة الجديدة عبر `_ensure_*_schema()`، ويُدخل البيانات الأولية
3. بعد ذلك تعمل ترحيلات Alembic للتنظيف وإزالة الأعمدة القديمة

---

## 8. خارطة الطريق (Roadmap)

### المرحلة 1: الأساس ✅
- ✅ إنشاء هيكل المشروع
- ✅ بناء Auth Service + Database Schema + Seed
- ✅ إعداد FastAPI main app + CORS
- ✅ ترحيلات Alembic + تنظيف الأعمدة القديمة

### المرحلة 2: الخدمات الأساسية ✅
- ✅ Shipping Service + E-Invoicing + Dashboard

### المرحلة 3: الخدمات الثانوية ✅
- ✅ Suppliers + Customers + Documents + Customs

### المرحلة 4: التكامل والنشر ⏳
- ⏳ التحقق من Docker Compose
- ⏳ تحديث التوثيق الكامل
- ⏳ التحقق النهائي قبل الإنتاج

---

## 9. الاستضافة
- **Frontend:** GitHub Pages أو Docker/Nginx
- **Backend:** Docker Compose أو PythonAnywhere Free Tier

---

## 10. الأمان
- JWT: access_token (24h) + refresh_token (7d)
- CORS: يقرأ من `ALLOWED_ORIGINS` في الإعدادات
- SECRET_KEY: مطلوب من البيئة؛ يفشل التطبيق عند غيابه
- Rate Limiting: مطلوب لكن غير مطبق حالياً
- File Upload: max 10MB

---

## 11. ملاحظة أخيرة
هذا الملف هو المرجع الوحيد للمشروع. أي تغيير يُسجل هنا أولاً.
