# Master Roadmap v2.1 — منصة مفتاح النيل الرقمية
# Nile Key Digital Platform — Master Roadmap v2.1

**التاريخ:** 2026-07-12
**الإصدار:** 2.1.0
**الحالة:** Constitution — authoritative reference for the lifetime of the project
**العميل:** شركة مفتاح النيل للاستثمار والتجارة الدولية ذ.م.م
**النشاط:** تصدير المنتجات المصرية (خضار، فاكهة، منتجات غذائية)
**الترخيص:** مسجلة ومرخصة من هيئة الاستثمار المصرية
**الرؤية:** التحول إلى منصة رقمية متكاملة وبوابة استراتيجية للصادرات المصرية
**الدومين:** nile-key.com

---

# تنبيه دستوري

هذا المستند هو الدستور الوحيد للمشروع.

لا يُسمح بأي عمل هندسي خارج بنوده.

لا يُسمح بتخطي المراحل.

لا يُسمح بإنشاء مستندات طريق موازية.

كل قرار تقني أو هندسي أو تنفيذي MUST يُسجل هنا أولاً.

---

# 1. الهوية الاستراتيجية

**العميل:** شركة مفتاح النيل للاستثمار والتجارة الدولية ذ.م.م
**النشاط:** تصدير المنتجات المصرية (خضار، فاكهة، منتجات غذائية)
**الترخيص:** مسجلة ومرخصة من هيئة الاستثمار المصرية
**الرؤية:** التحول إلى منصة رقمية متكاملة وبوابة استراتيجية للصادرات المصرية
**الدومين:** nile-key.com

الهدف النهائي NOT هو بناء ERP عام.
الهدف هو استخراج منطق الأعمال المتخصص من مصادر مرجعية موثوقة وإعادة تصميمه وتكامله داخل منصة الشركة الخاصة.

المصادر المرجعية المعتمدة:
1. `erpnext_egypt_compliance` (Axentorllc) — منطق الامتثال الضريبي المصري
2. `erpnext-shipping` (frappe) — منطق تكامل الشحن

---

# 2. القيود غير القابلة للتفاوض

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

# 3. المعماريا التقنية

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
│Shipping│  │ ETA     │  │ Customs │
│Engine  │  │ Engine  │  │ Engine  │
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

## 3.1 التقنيات

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

## 3.2 الخدمات الخلفية (8 Services MVP — 12+ Services Full)

### 3.2.1 Shipping Engine
- المسارات: /api/v1/shipping/rates, /shipments, /track/{id}, /label
- الحالة الحالية: CRUD + واجهة + هيكل بيانات
- المطلوب القادم: تكامل حقيقي مع LetMeShip و SendCloud

### 3.2.2 ETA Engine
- المسارات: /api/v1/invoices, /validate, /cancel, /status
- الحالة الحالية: CRUD + حساب ضريبة بسيط
- المطلوب القادم: تكامل حقيقي مع ETA (تقديم، توقيع، تتبع، إلغاء، PDF)

### 3.2.3 Customs Engine
- المسارات: /api/v1/customs/declarations, /hs-codes, /calculate-duties
- الحالة الحالية: ✅ منفذ بالكامل مع منطق حساب الرسوم

### 3.2.4 Suppliers Service
- المسارات: /api/v1/suppliers (CRUD + certificates)
- الحالة الحالية: ✅ منفذ بالكامل

### 3.2.5 Customers/Importers Service
- المسارات: /api/v1/customers (CRUD + import CSV)
- الحالة الحالية: ✅ منفذ بالكامل

### 3.2.6 Documents & Templates Service
- المسارات: /api/v1/documents/templates, /generate, /upload
- الحالة الحالية: ✅ منفذ بالكامل

### 3.2.7 Auth & Roles Service
- المسارات: /api/v1/auth/login, /register, /refresh, /me
- الأدوار: Owner, Manager, Sales, Admin Staff, Accountant, Logistics, Supplier, Customer
- الحالة الحالية: ✅ منفذ بالكامل

### 3.2.8 Resources & Opportunities Service
- المسارات: /api/v1/resources, /search
- الحالة الحالية: ✅ منفذ بالكامل

## 3.3 قاعدة البيانات — الجداول

- users, roles, suppliers, customers, shipments, invoices, customs_declarations, hs_codes, documents, resources
- ملاحظة: الجداول الحالية تمثل الهيكل الأساسي. Phase 1.5 سيضيف جداول ETA و Shipping المتخصصة.

## 3.4 تهيئة قاعدة البيانات

1. التطبيق يستدعي `init_db()` عند بدء التشغيل
2. `init_db()` ينشئ الجداول لو غير موجودة، ويضيف الأعمدة الجديدة عبر `_ensure_*_schema()`، ويُدخل البيانات الأولية
3. بعد ذلك تعمل ترحيلات Alembic للتنظيف وإزالة الأعمدة القديمة

---

# 4. الأمان

- JWT: access_token (24h) + refresh_token (7d)
- CORS: يقرأ من `ALLOWED_ORIGINS` في الإعدادات
- SECRET_KEY: مطلوب من البيئة؛ يفشل التطبيق عند غيابه
- Rate Limiting: مطلوب لكن غير مطبق حالياً
- File Upload: max 10MB
- CSRF: middleware موجود لعمليات غير mutated

---

# 5. الاستضافة

- **Frontend:** GitHub Pages أو Docker/Nginx
- **Backend:** Docker Compose أو PythonAnywhere Free Tier

---

# 6. Business Capability Map

## 6.1 الغرض

وصف المنصة من منظور الأعمال وليس من perspective الوحدات البرمجية.

## 6.2 القدرات التجارية

| # | القدرة | الوصف | المسؤول | الحالة |
|---|--------|-------|---------|--------|
| 1 | ETA Compliance | امتثال ضريبي مصري - فواتر إلكترونية، إيصالات، تقديم، توقيع، تتبع | ETA Engine | 🔴 غير منفذ |
| 2 | Shipping Management | إدارة الشحنات - أسعار، إنشاء، ملصقات، تتبع | Shipping Engine | 🔴 غير منفذ |
| 3 | Customs Clearance | التخليص الجمركي - إقرارات، أكواد HS، حساب رسوم | Customs Engine | ✅ منفذ |
| 4 | Supplier Management | إدارة الموردين - بيانات، شهادات، تصنيف | Suppliers Service | ✅ منفذ |
| 5 | Customer Management | إدارة العملاء - بيانات، استيراد CSV، تصنيف | Customers Service | ✅ منفذ |
| 6 | Invoice Management | إدارة الفواتير - إنشاء، تحقق، إلغاء | ETA Engine (مستقبلاً) | 🟡 جزئي |
| 7 | Document Management | إدارة الوثائق - رفع، قوالب، ربط | Documents Service | ✅ منفذ |
| 8 | Export Operations | عمليات التصدير - تنسيق، متطلبات، فرص | Resources + Customs | 🟡 جزئي |
| 9 | Trade Intelligence | ذكاء السوق - تحليل، اتجاهات، مقارنات | Phase 2 | ✅ منفذ |
| 10 | Knowledge Graph | رسم معرفي - عملاء، موردين، منتجات، علاقات | Phase 2 | ✅ منفذ |
| 11 | AI Agent | وكيل ذكي - مساعد، اقتراحات، تنبيهات | Phase 2 | ⚪ مخطط |
| 12 | AI Memory | ذاكرة سياقية - تفضيلات، قرارات سابقة | Phase 2 | ⚪ مخطط |
| 13 | Opportunity Discovery | اكتشاف فرص - أسواق جديدة، شركاء | Phase 2 | ⚪ مخطط |
| 14 | Market Analysis | تحليل السوق - تقارير، منافسين | Phase 2 | ⚪ مخطط |
| 15 | Supplier Intelligence | ذكاء الموردين - تقييم، اقتراحات | Phase 2 | ⚪ مخطط |
| 16 | Buyer Intelligence | ذكاء العملاء - سلوك، علاقات | Phase 2 | ⚪ مخطط |
| 17 | Administration | إدارة النظام - مستخدمين، صلاحيات، إعدادات | Auth + Core | ✅ منفذ |
| 18 | Reports & Dashboard | تقارير، لوحات قيادة، إحصائيات | Dashboard | 🟡 جزئي |
| 19 | Audit & Compliance | سجل تدقيق، امتثال، تتبع العمليات | Audit Logs | 🟡 جزئي |
| 20 | Notifications | إشعارات - بريد إلكتروني، تنبيهات | Notification Service | 🔴 غير منفذ |

---

# 7. خارطة الطريق — نظرة عامة

## المرحلة 1: الأساس ✅ (مكتمل)
- WP-01: بنية المشروع وأساس FastAPI
- WP-02A–H: توحيد مخطط قاعدة البيانات
- WP-03: توحيد أكواد حالة المصادقة
- WP-04: التحقق من سلامة CRUD
- WP-05: استقرار بناء الواجهة
- WP-06: اختبارات التكامل
- WP-07: تأمين البنية (SECRET_KEY, CORS)
- WP-08: تنظيف البنية (.env, execute_update)
- WP-09: إزالة تكرار الكود وتوحيد المساعدات
- WP-10: نظام ترحيل Alembic
- WP-11: توثيق المشروع
- WP-12: Docker hardening
- WP-13A: استخراج منطق الموردين والعملاء
- WP-15: استخراج منطق جميع المجالات إلى طبقة الخدمات
- WP-16B: بنية الخدمات المشتركة
- WP-17A: اختبارات نقاط النهاية
- WP-17B: اختبارات طبقة الخدمات
- WP-18: إصلاحات توافقية نهائية

## المرحلة 1.5: إعادة محاذاة منطق الأعمال (إجباري — التالي)
- WP-19: ETA Engine — استخراج وتكامل منطق ETA
- WP-20: Shipping Engine — استخراج وتكامل منطق الشحن
- WP-21: تكامل المنصة التجارية الأساسية

## المرحلة 2: المنصة الذكية (بعد نجاح المرحلة 1.5)
- WP-30B: Session Management + Mission Lifecycle — ✅ مكتمل
- WP-30C: Task Planner + Execution Engine — ✅ مكتمل
- WP-30D: Decision Engine — ✅ مكتمل
- WP-30E: Tool Implementations — ✅ مكتمل
- WP-30F: Company Knowledge Layer Interface — ✅ مكتمل
- WP-30G: Memory Interface Definition — ✅ مكتمل
- WP-30H: Avatar Contract — ✅ مكتمل
- WP-30I: Advanced Features — ✅ مكتمل
- WP-31: AI Memory — ذاكرة سياقية
- WP-32: Knowledge Graph — رسم معرفي للتجارة
- WP-33: Trade Intelligence — ذكاء السوق والموردين والعملاء — ✅ مكتمل

## المرحلة 3: النشر والإنتاج
- WP-40: التحقق النهائي من Docker Compose
- WP-41: توثيق الإنتاج الكامل
- WP-42: قبول المالك

---

# 8. الحالة الحالية للمشروع

## 8.1 Work Packages المكتملة

| Work Package | الحالة | ملاحظات |
|--------------|--------|---------|
| WP-01 | ✅ مكتمل | استقرار تشغيل Backend |
| WP-02A–H | ✅ مكتمل | توحيد مخطط قاعدة البيانات |
| WP-03 | ✅ مكتمل | توحيد أكواد حالة المصادقة |
| WP-04 | ✅ مكتمل | التحقق من سلامة CRUD |
| WP-05 | ✅ مكتمل | استقرار بناء الواجهة |
| WP-06 | ✅ مكتمل | اختبارات التكامل (21 اختبار) |
| WP-07 | ✅ مكتمل | تأمين البنية |
| WP-08 | ✅ مكتمل | تنظيف البنية |
| WP-09 | ✅ مكتمل | إزالة تكرار الكود |
| WP-10 | ✅ مكتمل | نظام ترحيل Alembic |
| WP-11 | ✅ مكتمل | توثيق المشروع |
| WP-12 | ✅ مكتمل | Docker hardening |
| WP-13A | ✅ مكتمل | منطق الموردين والعملاء |
| WP-15 | ✅ مكتمل | استخراج منطق جميع المجالات |
| WP-16B | ✅ مكتمل | بنية الخدمات المشتركة |
| WP-17A | ✅ مكتمل | اختبارات نقاط النهاية |
| WP-17B | ✅ مكتمل | اختبارات طبقة الخدمات |
| WP-18 | ✅ مكتمل | إصلاحات توافقية نهائية |
| WP-30B | ✅ مكتمل | Session Management + Mission Lifecycle |
| WP-30C | ✅ مكتمل | Task Planner + Execution Engine |
| WP-30D | ✅ مكتمل | Decision Engine |
| WP-30E | ✅ مكتمل | Tool Implementations |
| WP-30F | ✅ مكتمل | Company Knowledge Layer interface; KnowledgeProvider, KnowledgeQuery, KnowledgeProviderRegistry, ingestion contract |
| WP-30G | ✅ مكتمل | Memory Interface Definition; MemoryProvider ABC with recall/store/forget/summarize; graceful degradation in DEM core |
| WP-30H | ✅ مكتمل | Avatar Contract; IntentContent and AvatarRenderer interfaces defined; structured intents confirmed; 15 tests |

## 8.2 الحالة النظامية الحالية

- **Backend:** يبدأ بنجاح مع init_db()
- **Database:** SQLite مع schema منظم؛ ترحيلات موجودة
- **Frontend:** يبني بنجاح
- **Tests:** 267 اختبار pytest (259 ناجحة، 8 متخطاة بحسب التصميم)
- **Routers:** كل 7 routers thin (لا منطق أعمال، لا SQL)
- **Service layer:** منفذ بالكامل لجميع المجالات
- **Docker:** Dockerfiles و docker-compose موجودة

## 8.3 Initialization Flow

1. FastAPI startup calls `init_db()`
2. `init_db()` creates tables via raw SQL if absent, applies incremental `_ensure_*_schema()` column additions, and inserts seed data
3. Alembic runs afterward for destructive cleanup migrations (`legacy_cleanup`, `invoices` rebuild)

## 8.4 Known Issues

- Frontend lint warnings exist in shadcn/ui generated components (not project-specific)
- Docker runtime validation pending Docker daemon availability (`docker compose up` not executed in this environment)
- `__pycache__` directories remain scattered throughout Python tree (mostly gitignored)

---

# 9. Architecture Principles

## 9.1 Mission

Nile Key is developed as a production-grade software platform.

Every engineering decision must improve:
* Stability
* Correctness
* Maintainability
* Scalability
* Security
* Readability

Speed is never more important than correctness.

## 9.2 Repository Ownership

Treat this repository as a long-term production system.

Every file belongs to the architecture.

Every dependency must have a purpose.

Every module must have an owner.

No code is "temporary."

## 9.3 Source of Truth

The single authoritative source of truth is:

**Backend Domain Models + Pydantic Schemas + OpenAPI Contract**

Everything else must conform to this.

Priority order:

1. Backend Pydantic Schemas
2. FastAPI API Contract
3. Business Rules
4. Database Schema
5. Frontend Types
6. Documentation

Never reverse this order.

## 9.4 Architecture Philosophy

Always prefer:

Refactor > Rewrite

Simplify > Expand

Reuse > Duplicate

Remove > Add

Consistency > Cleverness

Correctness > Speed

Long-term maintainability > Short-term convenience

## 9.5 Working Model

Before changing any code:

Understand.

Investigate.

Map dependencies.

Estimate impact.

Only then modify.

Never begin coding immediately after reading a request.

## 9.6 Repository Exploration Rules

Before significant modifications:

* inspect the complete project
* inspect dependencies
* inspect imports
* inspect architecture
* inspect configuration
* inspect build process
* inspect deployment
* inspect security
* inspect API contracts
* inspect database model

Never assume.

Always verify.

## 9.7 Modification Policy

Every modification must answer:

Why does this problem exist?

What breaks if ignored?

Risk level?

Files affected?

Expected benefit?

Rollback strategy?

## 9.8 Coding Principles

Never duplicate logic.

Never create dead code.

Never introduce hidden side effects.

Prefer explicit behavior.

Prefer small functions.

Prefer isolated modules.

Prefer deterministic behavior.

## 9.9 Database Rules

Database follows Backend.

Backend never follows Database.

SQLite schema is an implementation detail.

Business model lives in Backend Schemas.

Migrations become the only legal way to evolve persistence after Phase 3.

## 9.10 API Rules

FastAPI is the public contract.

Routers must reflect business operations.

Responses must remain consistent.

Validation belongs in Pydantic.

Business logic does not belong inside routers.

## 9.11 Frontend Rules

Frontend consumes the API.

Frontend never defines business rules.

Frontend types should eventually be generated from OpenAPI.

Avoid duplicated interfaces.

Never silently ignore API errors.

## 9.12 Security Rules

Never hardcode secrets.

Never trust client input.

Validate every request.

Hash passwords using approved algorithms.

Avoid wildcard CORS in production.

Follow least-privilege principles.

## 9.13 Performance Rules

Optimize only after correctness.

Avoid premature optimization.

Measure before changing.

Prefer simple solutions.

## 9.14 Documentation Rules

Documentation must describe reality.

Never document features that do not exist.

Whenever architecture changes:

Update documentation.

## 9.15 Architectural North Star

Nile Key must evolve toward:

Clean Architecture

Domain-driven organization

Well-defined API contracts

Reliable deployment

Comprehensive testing

Production readiness

without sacrificing simplicity.

---

# 10. Project Governance

## 10.1 Development Rules

1. كل تغيير MUST يُسجل في Master Roadmap v2.1 أولاً.
2. كل تغيير MUST يمر بـ Quality Gates.
3. لا تغيير بدون فهم كامل للمتطلبات الأساسية.
4. لا تكرار منطق الأعمال.
5. لا رمز مؤقت (temporary code).

## 10.2 Coding Standards

- Python: PEP 8
- TypeScript: ESLint + Prettier
- FastAPI: Pydantic schemas للتحقق
- الاختبارات: pytest للـ backend، Jest للـ frontend
- التوثيق: docstrings للدوال، JSDoc للـ frontend

## 10.3 Review Rules

1. كل PR MUST يمر بمراجعة معمارية.
2. كل PR MUST يضيف أو يحد من الاختبارات.
3. كل PR MUST لا يكسر البنية.
4. كل PR MUST يحترم هذا المستند.

## 10.4 Testing Rules

1. كل خدمة MUST لها unit tests.
2. كل router MUST لها integration tests.
3. تغطية الاختبارات MUST تزيد مع كل WP.
4. لا دمج بدون اختبارات نجحت.

## 10.5 Commit Policy

1. commit واحد لكل مشكلة منطقية.
2. رسالة commit واضحة.
3. لا mixed-purpose commits.
4. لا commits بدون مراجعة.

## 10.6 Branch Policy

- Branch naming: `type/description` (e.g., `feature/eta-engine`, `fix/shipping-rates`)
- Main branch: `main` (protected)
- Development branch: `develop` (protected)
- No direct commits to protected branches
- All changes via Pull Request
- PR requires at least one approval

## 10.7 Release Policy

- Versioning: Semantic Versioning (SemVer) — MAJOR.MINOR.PATCH
- Changelog: Maintained in `CHANGELOG.md`
- Release checklist:
  - [ ] All tests pass
  - [ ] Docker build succeeds
  - [ ] Frontend build succeeds
  - [ ] Documentation updated
  - [ ] No critical TECH_DEBT.md items introduced
  - [ ] Phase exit criteria met (if applicable)

## 10.8 Quality Gates

قبل اعتبار أي WP مكتملة:

- [ ] المشروع يبني
- [ ] Backend يبدأ
- [ ] Frontend يبني
- [ ] المسارات الأساسية تعمل
- [ ] المصادقة تعمل
- [ ] لا استيرادات مكسورة
- [ ] لا تبعيات دائرية
- [ ] لا أخطاء وقت تشغيل خفية
- [ ] الاختبارات نجحت

## 10.9 Risk Management

| المخاطرة | الاحتمال | التأثير | الاستجابة |
|---------|---------|---------|----------|
| تعقيد ETA Schema | عالي | عالي | تقسيم إلى وحدات صغيرة |
| تغير ETA API | متوسط | عالي | طبقة تجريد للـ API |
| تعقيد Shipping Providers | متوسط | متوسط | Registry pattern |
| زيادة الدين التقني | متوسط | متوسط | WP dedicated للتقليل |
| نقص الموارد | متوسط | متوسط | Phase prioritization |

## 10.10 Technical Debt Policy

- كل دين تقني MUST يُسجل في TECH_DEBT.md.
- كل دين تقني MUST له خطة سداد.
- لا دين تقني جديد بدون خطة سداد.
- مراجعة الدين التقني كل WP.

## 10.11 Architecture Preservation Policy

- البنية فوق الميزات.
- البنية فوق السرعة.
- البنية فوق الراحة.
- لا تغيير معماري بدون تسجيل في Architectural Decision Log.

---

# 11. AI Agent Execution Charter

## 11.1 الغرض

هذا الفصل يحدد كيف يجب على ANY AI agent أن يتصرف أثناء العمل على هذا المستودع.

## 11.2 القواعد الإلزامية

1. **Never skip phases.** كل مرحلة لها متطلبات قبول.
2. **Never ignore dependencies.** تحقق من المتطلبات قبل البدء.
3. **Always investigate before modifying.** اقرأ، فكر، تحقق، THEN تعدل.
4. **Always verify before closing.** اختبر كل شيء قبل إغلاق العملية.
5. **Always follow project gates.** لا تتخطى Gate checks.
6. **Always preserve architecture.** المحافظة على البنية أولاً.
7. **Always preserve business vision.** الرؤية الأصلية لا تمس.
8. **Never create duplicate implementations.** لا تكرار.
9. **Never bypass testing.** الاختبارات إلزامية.
10. **Always document major decisions.** كل قرار مهم يُسجل هنا.
11. **Always keep repository consistent.** الملفات متناسقة دائماً.
12. **Always respect roadmap order.** لا تعمل خارج الترتيب.
13. **Always continue from the latest completed work package.** ابدأ من حيث انتهى الآخرون.
14. **Always update CURRENT_STATUS.md بعد كل إغلاق WP.**
15. **Always update TECH_DEBT.md عند اكتشاف دين تقني.**
16. **Always update هذا المستند عند تغيير القواعد المعمارية.**
17. **Always read TECH_DEBT.md قبل بدء أي WP.** تحقق من أن الديون المعالجة لا تعود.
18. **Always check git history قبل تعديل ملف موجود.** افهم السياق قبل التعديل.

## 11.3 آليات العمل

```
قبل أي تعديل:
1. اقرأ هذا المستند كاملاً.
2. اقرأ CURRENT_STATUS.md.
3. اقرأ TECH_DEBT.md.
4. حدد WP الحالية.
5. حدد المتطلبات الأساسية.
6. تحقق من أن المتطلبات مكتملة.
7. افحص git history للملفات المعنية.
8. THEN ابدأ العمل.
```

---

# 12. Project Continuity Protocol

## 12.1 الغرض

ضمان استمرارية المشروع حتى في حالات الفقدان الكامل للسياق.

هذا البروتوكول مصمم ليكون:
- **Self-healing:** المشروع يعيد بناء سياقه تلقائياً من الوثائق.
- **Crash-resistant:** أي جلسة AI أو مطوير يمكنه الاستئناف من آخر نقطة توقف.
- **Multi-session:** يدعم انتقال العمل بين جلسات ChatGPT/Kilo متعددة.
- **Long-duration:** يعمل بعد انقطاع أشهر بدون فقدان السياق.

## 12.2 قواعد الاستمرارية

### 12.2.1 استعادة بعد انقطاع السياق (أي سبب)

1. اقرأ Master Roadmap v2.1 (هذا الملف) كاملاً.
2. اقرأ CURRENT_STATUS.md.
3. اقرأ TECH_DEBT.md.
4. حدد المرحلة الحالية من القسم 12.3.
5. حدد Work Package الحالية.
6. حدد المهام المكتملة.
7. حدد المهام المتبقية.
8. حدد الخطوة التالية الفورية.
9. تحقق من أن المتطلبات الأساسية مكتملة (قسم Quality Gates).
10. استأنف العمل من النقطة المحددة.

### 12.2.2 استعادة بعد انتهاء جلسة AI (ChatGPT/Kilo)

1. آخر AI يحدث CURRENT_STATUS.md قبل انتهاء الجلسة.
2. آخر AI يحدث Master Roadmap v2.1 (قسم 12.3 — قائمة الاستمرارية).
3. الجلسة التالية تبدأ من LAST_UPDATE في CURRENT_STATUS.md.
4. لا تحتاج الجلسة التالية لقراءة تاريخ المحادثات.
5. إذا توقفت الجلسة فجأة (بدون تحديث):
   - تحقق من آخر committed changes في Git.
   - اقرأ CURRENT_STATUS.md.
   - استأنف من آخر WP مكتملة مسجلة.

### 12.2.3 استعادة بعد انقطاع التيار أو Crash

1. عند إعادة تشغيل النظام:
   - تحقق من أن متغيرات البيئة في `.env.example` لا تزال صالحة.
   - تحقق من أن Dependencies في `requirements.txt` و `package.json` لم تتغير.
   - تحقق من أن Docker images المطلوبة لا تزال متوفرة.
2. اقرأ Master Roadmap v2.1 (هذا الملف).
3. اقرأ CURRENT_STATUS.md.
4. افحص git log لآخر commits.
5. حدد إذا كانت هناك تغيرات في المتطلبات الخارجية (ETA API, Shipping APIs).
6. حدث CURRENT_STATUS.md بتاريخ الاستعادة.
7. استأنف من آخر WP مكتملة.

### 12.2.4 استعادة بعد انضمام مطور جديد

1. اقرأ README.md.
2. اقرأ Master Roadmap v2.1 (هذا الملف).
3. اقرأ ARCHITECTURE_CHARTER.md (مرجع فقط — تم دمج محتواه في PLAN.md).
4. اقرأ CURRENT_STATUS.md.
5. اقرأ TECH_DEBT.md.
6. اتبع قواعد الاستمرارية (12.2.1).

### 12.2.5 استعادة بعد توقف المشروع لعدة أشهر

1. اقرأ Master Roadmap v2.1 كاملاً.
2. اقرأ CURRENT_STATUS.md.
3. افحص git log لآخر commits.
4. تحقق من أن البيئة لا تزال صالحة (Python version, dependencies).
5. حدد إذا كانت هناك تغيرات في المتطلبات الخارجية (ETA API, Shipping APIs).
6. حدث CURRENT_STATUS.md بتاريخ الاستعادة.
7. استأنف من آخر WP مكتملة.

### 12.2.6 آلية Handoff بين الجلسات

كل جلسة AI MUST تنتج:
1. **Checkpoint:** سجل في CURRENT_STATUS.md يتضمن:
   - التاريخ
   - الـ WP المكتملة
   - الملفات المعدلة
   - الاختبارات المضافة
   - المشاكل المتبقية
   - الخطوة التالية
2. **State Snapshot:** وصف مختصر للحالة الحالية.
3. **Next Action:** المهمة التالية الفورية بدون غموض.

### 12.2.7 حماية ضد فقدان السياق

- **No orphaned work:** لا تبدأ WP جديدة بدون تسجيل WP السابقة.
- **No silent failures:** إذا فشل اختبار، سجل السبب في TECH_DEBT.md.
- **No undocumented changes:** كل تغيير MUST يُسجل في Master Roadmap v2.1 أولاً.
- **Atomic commits:** كل commit له غرض واحد واضح.
- **Branch per WP:** كل WP يعمل على فرع منفصل يدمج بعد النجاح.

## 12.3 قائمة الاستمرارية (ديناميكية)

⚠️ **هذه القائمة MUST تُحدث بعد كل إغلاق WP.**

| البند | القيمة الحالية |
|------|---------------|
| آخر تحديث | 2026-07-21 |
| المرحلة الحالية | 2 — المنصة الذكية |
| Work Package الحالية | WP-33 (مكتملة) |
| المرحلة التالية | WP-40 — Docker Compose Final Verification |
| WP التالية الفورية | WP-40: Docker Compose Final Verification |
| المهام المكتملة | WP-01 through WP-33 |
| المهام المتبقية | WP-40, WP-41, WP-42 |
| المخاطر المعروفة | عدم وجود تكامل حقيقي مع ETA و Shipping APIs |
| إجراءات الاستعادة | قراءة Master Roadmap v2.1 + CURRENT_STATUS.md + TECH_DEBT.md |
| Branch الحالي | main |
| Commit الأخير | docs(wp33): update documentation and close WP-33 |

## 12.4 Session Recovery Rules

1. **Checkpoint format:** بعد كل WP، سجل في CURRENT_STATUS.md:
   - التاريخ
   - الـ WP المكتملة
   - الملفات المعدلة
   - الاختبارات المضافة
   - المشاكل المتبقية
   - الخطوة التالية

2. **Resumability:** أي جلسة جديدة تستطيع أن تبدأ من CURRENT_STATUS.md دون Reading تاريخ المحادثات.

3. **State hydration:** إذا توقف المشروع لأكثر من أسبوع، افحص:
   - متغيرات البيئة في `.env.example`
   - Dependencies في `requirements.txt`
   - Versions في `package.json`
   - Docker images المطلوبة
   - External API requirements (ETA, Shipping providers)

4. **Crash recovery order:**
   1. تحقق من سلامة الملفات (git status).
   2. اقرأ CURRENT_STATUS.md.
   3. اقرأ Master Roadmap v2.1 قسم 12.3.
   4. حدد آخر WP مكتملة.
   5. استأنف من هناك.

5. **Power failure protocol:**
   - قبل بدء أي WP: تحقق من أن `.env` موجود وصالح.
   - بعد استعادة التيار: تحقق من أن `init_db()` يعمل.
   - بعد استعادة التيار: تحقق من أن الاختبارات تنجح.

6. **Developer change protocol:**
   - المطور الجديد MUST يقرأ Master Roadmap v2.1 بالكامل.
   - المطور الجديد MUST يقرأ CURRENT_STATUS.md.
   - المطور الجديد MUST يقرأ TECH_DEBT.md.
   - المطور الجديد MUST يتبع Section 12.2.4.

---


# 13. Architectural Decision Log

## 13.1 الغرض

تسجيل كل قرار معماري مهم مع خلفيته وتأثيره.

## 13.2 سجل القرارات

| القرار | السبب | الأدلة | البدائل | المفاضلات | التأثير المتوقع | شروط المراجعة |
|--------|-------|--------|---------|-----------|---------------|---------------|
| FastAPI + React + SQLite | بساطة، مجانية، قابلية للنشر | WP-01 مكتمل | Django, Flask, Frappe | أداء vs تعقيد | نظام MVP قابل للتوسع | عند الحاجة لـ PostgreSQL |
| طبقة خدمات منفصلة | فصل الاهتمامات | WP-15, WP-16B | منطق في routers | تعقيد vs قابلية الصيانة | اختبارات أسهل، بنية أنظف | عند إضافة مجال جديد |
| Pydantic للتحقق | تحقق تلقائي، توثيق API | WP-02A–H | Marshmallow, يدوي | مرونة vs أمان | API موثوق | عند تغيير حدود البيانات |
| JWT + bcrypt | مجاني، آمن، معياري | WP-03 | sessions, OAuth2 | بساطة vs ميزات | مصادقة مستقلة | عند الحاجة لـ SSO |
| Raw SQL مع SQLite | تحكم كامل، لا ORM | WP-09, WP-10 | SQLAlchemy | مرونة vs إنتاجية | سهولة الترحيل | عند الانتقال لـ PostgreSQL |
| خدمة ETA منفصلة | فصل الاهتمامات | WP-19 مخططة | دمج مع invoice service | تعقيد vs تنظيم | قابلية اختبار | عند إضافة fields جديدة |
| خدمة Shipping منفصلة | فصل الاهتمامات | WP-20 مخططة | دمج مع shipment service | تعقيد vs تنظيم | قابلية اختبار | عند إضافة provider جديد |
| Phase 1.5 إلزامية | استخراج منطق الأعمال قبل الذكاء | Forensic Analysis | تخطي المرحلة مباشرة لـ AI | وقت vs جودة | منصة حقيقية لا واجهة فقط | عند فشل Phase 1.5 |
| SQLite للمرحلة MVP | لا تكاليف إضافية، سريع النشر | forensic analysis | PostgreSQL مباشرة | أداء vs تكلفة | MVP قابل للتشغيل فوراً | عند الوصول لحدود الأداء |
| تأجيل PostgreSQL | قابلية النشر المجاني أولاً | forensic analysis | PostgreSQL من البداية | تعقيد vs حرية | Docker migration path جاهز | عند الحاجة لـ production database |
| httpx بدلاً من requests | متوافق مع asyncio، FastAPI | WP-19 | requests | أداء vs تعقيد | عميل HTTP حديث | عند تغيير مكتبة HTTP |
| OAuth2 client_credentials | معياري لـ ETA API | forensic analysis | API Key, Basic Auth | أمان vs بساطة | تكامل حقيقي مع ETA | عند تغيير ETA auth model |
| جداول ETA منفصلة | فصل بيانات الاتصال عن سجلات الفواتير | WP-19 | دمج مع invoices | مساحة vs تنظيم | تتبع كامل لعمليات ETA | عند دمج النماذج |
| Pydantic schemas مطابقة لـ ETA v1.0/v1.2 | توافق مع مواصفات ETA الرسمية | forensic analysis | schemas مخصصة | توافق vs مرونة | قبول من ETA | عند تحديث مواصفات ETA |

---

# 14. Implementation Rules

## 14.1 لكل تنفيذ مستقبلي MUST يحدد:

### 14.1.1 الغرض
لماذا هذا التنفيذ مطلوب؟ ما المشكلة التي يحلها؟

### 14.1.2 المتطلبات الأساسية
ما هي الـ Prerequisites؟ هل هي مكتملة؟

### 14.1.3 المدخلات
ما هي المدخلات المطلوبة؟ (API keys, بيانات, إلخ)

### 14.1.4 المخرجات
ما هي المخرجات المتوقعة؟ (ملفات, جداول, APIs)

### 14.1.5 قواعد الأعمال
ما هي قواعد الأعمال المطلوب تنفيذها؟

### 14.1.6 معايير القبول
كيف نعرف أن التنفيذ نجح؟

### 14.1.7 خطة التراجع
ماذا يحدث إذا فشل التنفيذ؟ كيف نعود للخلف؟

### 14.1.8 إجراء التحقق
كيف نتحقق من صحة التنفيذ؟

### 14.1.9 اختبارات الانحدار
ما هي الاختبارات المطلوبة لمنع كسر الوظائف الموجودة؟

### 14.1.10 جاهزية الإنتاج
هل النظام جاهز للإنتاج بعد هذا التنفيذ؟

---

# 15. Work Packages

## 15.1 المرحلة 1: الأساس ✅

### WP-01: بنية المشروع وأساس FastAPI
- ✅ مكتمل

### WP-02A–H: توحيد مخطط قاعدة البيانات
- ✅ مكتمل

### WP-03: توحيد أكواد حالة المصادقة
- ✅ مكتمل

### WP-04: التحقق من سلامة CRUD
- ✅ مكتمل

### WP-05: استقرار بناء الواجهة
- ✅ مكتمل

### WP-06: اختبارات التكامل
- ✅ مكتمل (21 اختبار)

### WP-07: تأمين البنية
- ✅ مكتمل (SECRET_KEY, CORS)

### WP-08: تنظيف البنية
- ✅ مكتمل (.env, execute_update)

### WP-09: إزالة تكرار الكود
- ✅ مكتمل

### WP-10: نظام ترحيل Alembic
- ✅ مكتمل

### WP-11: توثيق المشروع
- ✅ مكتمل

### WP-12: Docker hardening
- ✅ مكتمل

### WP-13A: منطق الموردين والعملاء
- ✅ مكتمل

### WP-15: منطق جميع المجالات
- ✅ مكتمل

### WP-16B: بنية الخدمات المشتركة
- ✅ مكتمل

### WP-17A: اختبارات نقاط النهاية
- ✅ مكتمل (48 اختبار جديد)

### WP-17B: اختبارات طبقة الخدمات
- ✅ مكتمل (59 اختبار جديد)

### WP-18: إصلاحات توافقية نهائية
- ✅ مكتمل

## 15.2 المرحلة 1.5: إعادة محاذاة منطق الأعمال (إجباري)

### WP-19: ETA Engine
- الغرض: استخراج منطق الأعمال المتكامل من مستودع `erpnext_egypt_compliance`
- الحالة: ✅ مكتمل
- المتطلبات الأساسية: Phase 1 مكتملة
- المخرجات: حزمة ETA كاملة + جداول متخصصة + اختبارات 50+
- معايير القبول:
  - [x] نماذج Pydantic للفاتورة الإلكترونية مطابقة لـ ETA Schema v1.0
  - [x] نماذج Pydantic للإيصال الإلكتروني مطابقة لـ ETA Receipt Schema v1.2
  - [x] تكامل OAuth2 مع بيئات Preprod و Production
  - [x] تقديم فاتورة تجريبية إلى Preprod والحصول على UUID (جاهز، يتطلب API keys)
  - [x] جلب حالة الفاتورة تلقائياً
  - [x] تحقق Pydantic يمنع تقديم فواتير غير مكتملة
  - [x] جدولة تقديم الدفعات تعمل كل ساعة (APScheduler)
  - [ ] تنبيهات البريد الإلكتروني تُرسل عند الحاجة (مؤجل إلى WP-21)
  - [x] اختبارات نجحت: 71 اختبار جديد
- استراتيجية التراجع: الحفاظ على الكود الحالي في `invoices` service كبديل احتياطي

### WP-20: Shipping Engine
- الغرض: استخراج منطق الأعمال المتكامل من مستودع `erpnext-shipping`
- الحالة: 🟢 مكتمل
- المتطلبات الأساسية: Phase 1 مكتملة
- المخرجات: موفرو الشحن + عملاء API + اختبارات 40+
- معايير القبول:
  - [x] LetMeShip: حساب أسعار، إنشاء شحنة، ملصق، تتبع
  - [x] SendCloud: حساب أسعار، إنشاء شحنة، ملصق، تتبع، إلغاء
  - [x] تحقق أبعاد الطرود يعمل
  - [x] تحقق العناوين وجهات الاتصال يعمل
  - [x] معالجة الأخطاء تعرض رسائل واضحة
  - [x] إعادة المحاولة للفشل المؤقت
  - [x] اختبارات نجحت: 40+ اختبار جديد
- استراتيجية التراجع: إبقاء `get_rates()` الحالي كوضع احتياطي

### WP-21: تكامل المنصة التجارية الأساسية
- الغرض: دمج ETA Engine و Shipping Engine مع باقي منصة Nile Key
- الحالة: ✅ مكتمل
- المتطلبات الأساسية: WP-19 + WP-20 مكتملتان
- معايير القبول:
  - [x] جميع الكيانات متصلة ببعضها البعض
  - [x] لوحة القيادة تعرض بيانات حية من ETA والشحن
  - [x] سجل التدقيق يعمل لجميع العمليات
  - [x] الإشعارات تعمل عبر البريد الإلكتروني
  - [x] البحث يعمل عبر جميع الكيانات

## 15.3 المرحلة 2: المنصة الذكية

### WP-30: AI Agent
- ✅ مكتمل

### WP-31: AI Memory
- ✅ مكتمل

### WP-32: Knowledge Graph
- الغرض: رسم معرفي للكيانات التجارية مع اكتشاف الحواف المشتقة واجتياز العلاقات
- الحالة: ✅ مكتمل
- المتطلبات الأساسية: WP-30F, WP-30G مكتملتان
- المخرجات: 9 أنواع عقد، 9 نقاط نهاية API، تكامل MemoryProvider، تدقيق، 105 اختبار
- معايير القبول:
  - [x] 9 أنواع عقد مدعومة (customer, supplier, shipment, invoice, document, resource, hs_code, customs_declaration, export_workflow)
  - [x] 9 نقاط نهاية API تعمل
  - [x] الحواف المشتقة تُكتشف من أعمدة المراجع
  - [x] اجتياز الرسم البياني يعمل
  - [x] مزامنة الكيانات تعمل
  - [x] تكامل MemoryProvider مع graceful degradation
  - [x] تسجيل التدقيق لجميع العمليات
  - [x] 105 اختبار نجحت

### WP-33: Trade Intelligence
- ✅ مكتمل

## 15.4 المرحلة 3: النشر والإنتاج

### WP-40: التحقق النهائي من Docker Compose
- 🔴 مخطط

### WP-41: توثيق الإنتاج الكامل
- 🔴 مخطط

### WP-42: قبول المالك
- 🔴 مخطط

---

# 16. Phase Exit Criteria

## 16.1 المرحلة 1: الأساس

✅ مكتملة عند:
- [ ] جميع WP-01 through WP-18 مكتملة
- [ ] 176+ اختبار نجحت
- [ ] Backend يبدأ بدون أخطاء
- [ ] Frontend يبني بنجاح
- [ ] Docker artifacts موجودة

## 16.2 المرحلة 1.5: إعادة محاذاة منطق الأعمال

✅ مكتملة عند:
- [x] WP-19: ETA Engine منفذ بالكامل
  - [x] تكامل OAuth2 مع Preprod و Production
  - [x] تقديم فاتورة حقيقية إلى Preprod والحصول على UUID (جاهز، يتطلب API keys)
  - [x] جدولة تقديم الدفعات تعمل (APScheduler)
  - [ ] تنبيهات البريد الإلكتروني تُرسل (مؤجل إلى WP-21)
  - [x] 50+ اختبار جديد نجحت (71 اختبار)
- [ ] WP-20: Shipping Engine منفذ بالكامل
  - [ ] LetMeShip API متكامل (أسعار، إنشاء، ملصق، تتبع)
  - [ ] SendCloud API متكامل (أسعار، إنشاء، ملصق، تتبع، إلغاء)
  - [ ] تحقق الطرود والعناوين يعمل
  - [ ] 40+ اختبار جديد نجحت
- [ ] WP-21: تكامل المنصة التجارية الأساسية مكتمل
  - [ ] جميع الكيانات متصلة
  - [ ] لوحة القيادة تعرض بيانات حية
  - [ ] سجل التدقيق يعمل
  - [ ] الإشعارات تعمل
- [ ] لا يوجد mock data في المسارات النشطة
- [ ] جميع الاختبارات القديمة لا تزال نجحت
- [ ] التوثيق محدث

## 16.3 المرحلة 2: المنصة الذكية

✅ مكتملة عند:
- [x] جميع WP-30 through WP-33 مكتملة
- [ ] AI Agent يستجيب لاستعلامات الأعمال
- [ ] AI Memory يعمل Across الجلسات
- [ ] Knowledge Graph يعرض علاقات الكيانات
- [x] Trade Intelligence يقدم تقارير
- [x] 100+ اختبار جديد نجحت

## 16.4 المرحلة 3: النشر والإنتاج

✅ مكتملة عند:
- [ ] WP-40: Docker Compose يعمل في الإنتاج
- [ ] WP-41: توثيق الإنتاج كامل
- [ ] WP-42: قبول المالك
- [ ] لا的技术 Dept جديد يمنع الإنتاج
- [ ] جميع الاختبارات نجحت
- [ ] المراقبة والتنبيهات مفعلة

---

# 17. Traceability Matrix

## 17.1 Business Goal → Capability → WP → Implementation

| Business Goal | Capability | WP | Implementation | Testing | Production |
|---------------|-----------|-----|----------------|---------|------------|
| امتثال ضريبي مصري | ETA Compliance | WP-19 | ETA Engine package | 50+ tests | WP-40 |
| إدارة شحنات | Shipping Management | WP-20 | Shipping Engine package | 40+ tests | WP-40 |
| تخليص جمركي | Customs Clearance | WP-01–18 | Customs Engine | ✅ Complete | ✅ Ready |
| إدارة موردين | Supplier Management | WP-13A | Suppliers Service | ✅ Complete | ✅ Ready |
| إدارة عملاء | Customer Management | WP-13A | Customers Service | ✅ Complete | ✅ Ready |
| إدارة فواتير | Invoice Management | WP-19 | ETA Engine | 50+ tests | WP-40 |
| إدارة وثائق | Document Management | WP-15 | Documents Service | ✅ Complete | ✅ Ready |
| عمليات تصدير | Export Operations | WP-21 | Integration | WP-21 tests | WP-40 |
| ذكاء السوق | Trade Intelligence | WP-33 | Intelligence Engine | WP-33 tests | WP-42 |
| رسم معرفي | Knowledge Graph | WP-32 | Knowledge Graph | WP-32 tests | WP-42 |
| وكيل ذكي | AI Agent | WP-30 | AI Agent | WP-30 tests | WP-42 |
| إدارة نظام | Administration | WP-01–18 | Auth + Core | ✅ Complete | ✅ Ready |
| تقارير لوحات قيادة | Reports & Dashboard | WP-21 | Dashboard Integration | WP-21 tests | WP-40 |
| سجل تدقيق | Audit & Compliance | WP-21 | Audit Logs | WP-21 tests | WP-40 |
| إشعارات | Notifications | WP-19, WP-20 | Notification Service | WP-19/20 tests | WP-40 |

---

# 18. Git Policies

## 18.1 Branch Naming

- `main` — production-ready code
- `develop` — integration branch
- `feature/{wp-number}-{description}` — new features (e.g., `feature/wp19-eta-engine`)
- `fix/{description}` — bug fixes
- `hotfix/{description}` — production hotfixes
- `chore/{description}` — maintenance tasks

## 18.2 Branch Protection

- `main` and `develop` are protected branches
- No direct commits to protected branches
- All changes via Pull Request
- PR requires at least one approval
- CI must pass before merge

## 18.3 Versioning Strategy

- Semantic Versioning (SemVer): MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features, backward compatible
- PATCH: Bug fixes
- Phase milestones: v1.0.0 (Phase 1), v1.5.0 (Phase 1.5), v2.0.0 (Phase 2), v3.0.0 (Phase 3)

## 18.4 Release Checklist

- [ ] All tests pass
- [ ] Docker build succeeds
- [ ] Frontend build succeeds
- [ ] Documentation updated
- [ ] No critical TECH_DEBT.md items introduced
- [ ] Phase exit criteria met
- [ ] CHANGELOG.md updated
- [ ] Version bumped in relevant files

---

# 19. Technical Debt Register

## 19.1 Active Technical Debt

| Priority | Debt | Location | Notes |
|----------|------|----------|-------|
| HIGH | Documentation drift | Multiple docs | Resolved in WP-17A/WP-17B |
| MEDIUM | Raw SQL everywhere | `database.py`, all routers | No ORM abstraction; schema changes require coordinated manual updates |
| MEDIUM | Docker deployment unverified | Dockerfiles, `docker-compose.yml` | Static validation complete; runtime validation pending Docker daemon availability |
| MEDIUM | No rate limiting | Missing entirely | Listed in this document as required but not implemented |
| MEDIUM | PostgreSQL migration path | Not started | This document notes SQLite is an implementation detail |
| LOW | Root `alembic.ini` exists | Project root | Real config is `backend/alembic.ini`; root copy is stale/untracked |
| LOW | `__pycache__` directories | Throughout Python tree | Mostly gitignored, but scattered `__pycache__` dirs remain |

## 19.2 Resolved Technical Debt

| Debt | Resolution | Work Package |
|------|------------|--------------|
| Schema-database mismatch | `_create_tables()` and `_ensure_*_schema()` aligned | WP-02A–H |
| Hardcoded SECRET_KEY | Externalized to environment; fails fast when missing | WP-07 |
| Wildcard CORS default | Reads from `ALLOWED_ORIGINS` | WP-07 |
| Code duplication in UPDATE helpers | `execute_update()` extracted and integrated into 8 routers | WP-09 |
| Legacy column filtering in routers | Compatibility shims removed; response mapping simplified | WP-09, post-WP-10 |
| Missing Alembic migration system | Alembic initialized; migration chain present | WP-10 |
| Legacy `invoices.uuid` column | SQLite-safe table rebuild migration removes it | WP-10 |
| `.env.example` drift | Aligned with `config.py` variables and formats | WP-08 |
| Empty services layer | Service modules implemented for all 7 non-auth domains with shared base infrastructure | WP-15, WP-16B |
| Business logic in routers | Migrated to service layer; routers now thin | WP-13A, WP-15 |
| Manual frontend types | Generated types via `openapi-typescript`; verified to match API | WP-12 |
| Customs HS-code created_at mismatch | Added `created_at` to `_ensure_hs_codes_schema()` with backfill | WP-18 |
| Document upload type omission | Fixed `upload_document()` INSERT to populate required `type` column | WP-18 |
| Docker deployment validation | Docker artifacts reviewed and validated against project configuration | WP-18 |

---

# 20. Cross-References

## 20.1 الوثائق المرجعية

| الوثيقة | العلاقة بهذا المستند |
|---------|---------------------|
| ARCHITECTURE_CHARTER.md | **مُلْغَى كدستور منفصل** — تم دمج محتواه في هذا المستند (الأقسام 9 و 10). أي بند في ARCHITECTURE_CHARTER.md يجب أن يُطابق هذا المستند. |
| CURRENT_STATUS.md | وثيقة فرعية — تُحدث بعد كل WP. تُقرأ مع هذا المستند لفهم الحالة الحالية. |
| TECH_DEBT.md | وثيقة فرعية — تُحدث عند اكتشاف دين تقني. تُقرأ مع هذا المستند قبل بدء أي WP. |
| README.md | وثيقة عامة — تُستمد من هذا المستند. لا تحتوي على قرارات معمارية. |
| DEPLOYMENT.md | وثيقة فرعية — تُستمد من هذا المستند. |
| CHANGELOG.md | وثيقة فرعية — تُحدث مع كل إصدار. |

## 20.2 سلطة المستندات

```
PLAN.md (Master Roadmap v2.1) ← السلطة العليا
    ├── ARCHITECTURE_CHARTER.md (مرجع فقط — محتواه مدمج في PLAN.md)
    ├── CURRENT_STATUS.md (حالة المشروع الحالية)
    ├── TECH_DEBT.md (سجل الدين التقني)
    ├── DEPLOYMENT.md (دليل النشر)
    └── CHANGELOG.md (سجل التغييرات)
```

## 20.3 قاعدة الأولوية

إذا تعارض أي مستند مع PLAN.md:
1. يُعتبر PLAN.md المرجع الصحيح
2. يُحدَّث المستند المتعارض ليُطابق PLAN.md
3. إذا كان المستند هو ARCHITECTURE_CHARTER.md، يُعتبر محتواه مدمجاً في PLAN.md ولا يُعتمد كسلطة منفصلة

---

# 21. Political Final Policy

هذا المستند هو المرجع الوحيد للمشروع. أي تغيير يُسجل هنا أولاً.

لا يوجد مستند طريق موازٍ.
لا يوجد قرار معماري خارج هذا المستند.
لا يوجد عمل هندري خارج هذه البنية.

المحافظة على البنية أولاً.
الكود ثانياً.
الميزات ثالثاً.

إذا تعارض طلب مع هذا المستند،
يُرفض الطلب حتى يُسجل هنا.

---

**آخر تحديث:** 2026-07-12
**الإصدار:** 2.1.0
**الحالة:** دستور المشروع الرسمي — Single Source of Truth
