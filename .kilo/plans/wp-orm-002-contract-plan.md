# Contract Plan: WP-ORM-002 — ORM Foundation Activation

**Work Package:** WP-ORM-002  
**Status:** Planned — awaiting approval  
**Priority:** HIGH  
**Phase:** Phase 3 — Production Readiness  
**Governing Documents:** `PLAN.md` (Master Roadmap v2.1) Section 9.9, `TECH_DEBT.md`, `CURRENT_STATUS.md`, `docs/architecture/ADR-0002-postgresql-migration-path.md`  
**Branch:** `main`  
**Target Baseline:** Post WP-ORM-001 closure (`72bc033`)  
**Depends On:** WP-ORM-001 CLOSED  

---







## 1. Gap / Problem

### 1.1 الحالة بعد WP-ORM-001
WP-ORM-001 أنشأ **الأساس** لكنه لم **يفعّله**:

| المكون | الحالة بعد WP-ORM-001 | المشكلة |
|--------|----------------------|---------|
| `DatabaseSession` | ✅ موجود ويعمل مع `supplier.py` | محجوز لـ supplier فقط |
| `SchemaRegistry` | ✅ موجود | **فارغ** — لا جدول مسجَّل |
| `MigrationRunner` | ✅ موجود | **لم يُشغّل أي migration فعلي** |
| `init_db()` | ✅ يعمل | لا يستخدم `SchemaRegistry` ولا `MigrationRunner` |
| `_ensure_*_schema()` | ✅ موجودة | لا تزال هي آلية schema evolution الفعلية |
| باقي services | ❌ 10+ خدمات على Raw SQL | لا تزال تعتمد على `connection()` + `build_list_query()` + `execute_update()` |

### 1.2 المشاكل المحددة
| # | المشكلة | التأثير | الخطورة |
|---|---------|---------|---------|
| 1 | **`SchemaRegistry` فارغ** | لا يمكن الاعتماد عليه كسجل مركزي للـschema | HIGH |
| 2 | **`MigrationRunner` لم يُختبر فعلياً** | لا يوجد دليل على أن آلية migrations تعمل | HIGH |
| 3 | **قاعدة `Migrations become the only legal way` غير مُفعَّلة** | أي schema change مستقبلي سيظل يتطلب تعديلات يدوية في 10+ ملفات | HIGH |
| 4 | **خدمة واحدة فقط مُرحَّلة** | النمط لم يُثبت على خدمة ثانية | MEDIUM |
| 5 | **`init_db()` لا يتكامل مع الطبقة الجديدة** | bootstrap لا يستفيد من `SchemaRegistry` أو `MigrationRunner` | MEDIUM |

### 1.3 المخاطر على Phase 3 Readiness
- **Schema Evolution:** بدون تفعيل `SchemaRegistry` + `MigrationRunner`، قاعدة PLAN.md Section 9.9 تبقى شكلاً.
- **Maintainability:** أي schema change يتطلب تعديل `_ensure_*_schema()` + `_create_tables()` يدوياً.
- **PostgreSQL Readiness:** المسار مُعَد لكن لم يُختبر حتى على SQLite.







## 2. Objective

تحويل الأساس الذي أُنشئ في `WP-ORM-001` إلى **مسار فعلي قابل للاستخدام** عبر:

1. **تسجيل الجداول الأساسية** في `SchemaRegistry` لجعله سجل schema مركزي حقيقي.
2. **إنشاء وتشغيل migration فعلية واحدة** عبر `MigrationRunner` لإثبات أن آلية migrations تعمل.
3. **ترحيل خدمة إضافية واحدة** (`customer.py`) لإثبات النمط على خدمة ثانية.
4. **إثبات أن schema evolution يمكن أن تمر عبر migration path** بدل التعديل اليدوي المتناثر.
5. **الحفاظ على SQLite** كـ runtime فعلي وعدم كسر أي سلوك حالي.







## 3. Scope

### 3.1 ما يُغطى في هذه المرحلة
| المكون | النطاق | الملفات المتأثرة |
|---------|--------|-----------------|
| **SchemaRegistry Registration** | تسجيل جداول `suppliers` و `customers` في `SchemaRegistry` | `backend/app/core/schema_registry.py` |
| **First Migration** | إنشاء وتشغيل migration فعلية واحدة عبر `MigrationRunner` | `backend/app/core/migrations.py` + migration SQL |
| **Service Layer Slice** | ترحيل `customer.py` إلى `DatabaseSession` | `backend/app/services/customer.py` |
| **Tests** | اختبارات الوحدة والتكامل والـRegression | `backend/tests/orm_abstraction/` |

### 3.2 ما يُستبعد من هذه المرحلة
- ترحيل باقي services (shipping, invoice, customs, documents, resources, eta, workflow)
- ترحيل routers
- PostgreSQL migration
- تغيير `DATABASE_URL` من SQLite
- Knowledge Graph / Providers / Multi-Agent / Avatar / Full Autonomy
- Business Workflow أو AI Memory
- data migration (مثل نقل بيانات بين جداول)







## 4. Out of Scope

- **لا** تُنشأ full ORM مثل SQLAlchemy — نستخدم `DatabaseSession` كـ thin wrapper فقط
- **لا** يُغيّر `MemoryProvider` interface
- **لا** يُغيّر DEM core أو Decision Engine أو Goal Evolution أو Outcome Feedback
- **لا** يُفتح PostgreSQL migration في هذه المرحلة
- **لا** يُغيّر routers أو API contracts
- **لا** تُضاف avatar أو knowledge graph أو multi-agent
- **لا** migration data transformation — الأولى schema-only







## 5. Architecture / Strategy

### 5.1 المبدأ الأساسي
> **لا تُعطّل ما يعمل.**  
> الـraw SQL الحالي يبقى functional طوال المرحلة. الطبقة الجديدة تُفعَّل **تدريجياً** مع الحفاظ على backward compatibility.

### 5.2 البنية المستهدفة بعد WP-ORM-002

```
                    ┌─────────────────────────────────────────┐
                    │         FastAPI Routers                 │
                    │  (لا تغيير — تبقى thin كما هي)          │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │         Service Layer                   │
                    │  ┌─────────────────────────────────┐    │
                    │  │  Legacy Path (RAW SQL)           │    │
                    │  │  connection() → get_db()         │    │
                    │  │  build_list_query()              │    │
                    │  │  execute_update()                │    │
                    │  └─────────────────────────────────┘    │
                    │  ┌─────────────────────────────────┐    │
                    │  │  New Path (ORM Abstraction)      │    │
                    │  │  DatabaseSession                 │    │
                    │  │  [supplier.py] ✅                │    │
                    │  │  [customer.py] 🔄 (WP-ORM-002)   │    │
                    │  └─────────────────────────────────┘    │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │    backend/app/core/database.py         │
                    │  - get_db() [موجود، يبقى]               │
                    │  - connection() [موجود، يبقى]           │
                    │  - DatabaseSession [موجود، يتوسع]       │
                    │  - SchemaRegistry [فارغ ← يُملأ]        │
                    │  - MigrationRunner [موجود، يُشغّل]      │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │         SQLite (nile_key.db)            │
                    │    (PostgreSQL لاحقاً عبر نفس Layer)     │
                    └─────────────────────────────────────────┘
```

### 5.3 تفاعل المكونات الجديدة

```
init_db() flow بعد WP-ORM-002:

1. إنشاء الجداول الأساسية عبر _create_tables() [موجود]
2. تسجيل الجداول في SchemaRegistry [جديد]
3. تشغيل MigrationRunner مع migration أولية [جديد]
4. Seed Data [موجود]
```

**المفتاح:** `MigrationRunner` يُشغَّل **بعد** `_create_tables()` لضمان أن الجداول موجودة قبل تطبيق migrations.







## 6. Migration Sequence

### الخطوة 1: تسجيل الجداول في `SchemaRegistry`
- تسجيل `suppliers` و `customers` في `SchemaRegistry` عند `init_db()`
- لا يُغيّر `_ensure_*_schema()` — يبقى كـ fallback
- `SchemaRegistry.ensure_schema()` يُستدعى بعد `_create_tables()` لضمان وجود الأعمدة

### الخطوة 2: إنشاء migration فعلية واحدة
- migration SQL: `v1_schema_snapshot` — يعيد إنشاء الجداول الأساسية (idempotent)
- الغرض: **إثبات أن MigrationRunner يعمل**، ليس إضافة بيانات
- لا تحتوي على data transformation

### الخطوة 3: ترحيل `customer.py`
- تحويل `customer.py` من Raw SQL إلى `DatabaseSession`
- نفس النمط المستخدم في `supplier.py`
- الحفاظ على `_customer_row_to_response()` كما هي







## 7. First Code Slice

### 7.1 الملفات المطلوبة
| الملف | الإجراء |
|--------|---------|
| `backend/app/core/database.py` | تعديل `init_db()` لتسجيل الجداول في `SchemaRegistry` وتشغيل `MigrationRunner` |
| `backend/app/core/schema_registry.py` | إضافة `register_table()` calls لـ `suppliers` و `customers` |
| `backend/app/core/migrations.py` | تعديل `__init__` لقبول migrations list أو تعديل `run_migrations()` ليقبل migrations |
| `backend/app/services/customer.py` | ترحيل إلى `DatabaseSession` |
| `backend/tests/orm_abstraction/test_customer_orm.py` | اختبارات تكامل جديدة |
| `backend/tests/orm_abstraction/test_schema_registry.py` | تحديث ليشمل suppliers و customers |
| `backend/tests/orm_abstraction/test_migrations.py` | تحديث ليشمل migration فعلية |

### 7.2 هيكل `init_db()` بعد التعديل
```python
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        _create_tables(cursor)
        _seed_data(cursor, conn)
        conn.commit()

        # WP-ORM-002: تفعيل SchemaRegistry و MigrationRunner
        _register_core_schemas(conn)
        _run_migrations(conn)
```

### 7.3 migration الأولى
```python
# backend/app/core/migrations.py

INITIAL_MIGRATIONS = [
    (
        "v1_schema_snapshot",
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_en TEXT,
            contact_person TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            country TEXT DEFAULT 'Egypt',
            tax_id TEXT,
            commercial_registry TEXT,
            certificates TEXT,
            status TEXT DEFAULT 'active',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER
        );
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_en TEXT,
            contact_person TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            country TEXT NOT NULL,
            tax_id TEXT,
            import_license TEXT,
            category TEXT,
            notes TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ),
]
```

**ملاحظة:** Migration الأولى هي **schema snapshot** فقط — لا تحتوي على data migration. الغرض هو إثبات أن `MigrationRunner` يمكنه تشغيل SQL فعلي وتسجيل الإصدار.

### 7.4 هيكل `customer.py` بعد الترحيل
```python
def list_customers(...):
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        query, params = build_list_query(...)
        rows = session.fetch_all(query, tuple(params))
        return [_customer_row_to_response(dict(r)) for r in rows]
    finally:
        conn.close()

def get_customer(customer_id: int) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        row = session.fetch_one("SELECT * FROM customers WHERE id = ?", (customer_id,))
        if not row:
            raise ValueError("Customer not found")
        return _customer_row_to_response(dict(row))
    finally:
        conn.close()

def create_customer(data: CustomerCreate, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        with session.transaction():
            customer_id = session.insert("customers", {
                "name": data.name,
                ...
                "created_at": now_iso(),
                "created_by": current_user["id"],
            })
        log_audit(...)
        return {"id": customer_id, "message": "Customer created successfully"}
    finally:
        conn.close()
```

**نفس النمط بالضبط المستخدم في `supplier.py` — لا تصميم جديد.**







## 8. Tests / Regression

### 8.1 اختبارات الوحدة الجديدة
| الملف | عدد الاختبارات | الغرض |
|--------|----------------|---------|
| `test_customer_orm.py` | 6 | اختبار `customer.py` مع `DatabaseSession` |
| `test_schema_registry.py` (تحديث) | +2 | اختبار تسجيل `suppliers` و `customers` |
| `test_migrations.py` (تحديث) | +2 | اختبار migration فعلية |

### 8.2 Regression المطلوب
| المجموعة | الشرط |
|----------|-------|
| `tests/test_services/test_supplier_service.py` | كلها تمر |
| `tests/test_suppliers.py` | كلها تمر |
| `tests/test_services/test_customer_service.py` | كلها تمر |
| `tests/test_customers.py` | كلها تمر |
| `tests/orm_abstraction/test_database_session.py` | كلها تمر |
| `tests/orm_abstraction/test_migrations.py` | كلها تمر |
| `tests/orm_abstraction/test_schema_registry.py` | كلها تمر |

### 8.3 شروط الفوز
- 0 breakage في اختبارات Regression
- `MigrationRunner` يُشغّل migration فعلية بنجاح
- `SchemaRegistry` يسجل `suppliers` و `customers`
- `customer.py` يعمل بنفس النتائج السابقة
- لا توجد `unawaited coroutine` warnings جديدة







## 9. Rollback Strategy

### 9.1 Rollback السريع
1. **git revert** للcommit الخاص بـ WP-ORM-002
2. `customer.py` يُرجع إلى `connection()` + raw SQL
3. `database.py` يُرجع إلى `init_db()` الأصلي بدون `SchemaRegistry` و `MigrationRunner`
4. لا يوجد data migration للتراجع عنها — migration الأولى schema-only

### 9.2 Rollback الجزئي
إذا فشل `customer.py` فقط:
1. إعادة `customer.py` إلى raw SQL
2. إبقاء `SchemaRegistry` registration و `MigrationRunner` للاستخدام المستقبلي
3. لا تأثير على `supplier.py`

### 9.3 Rollback البيانات
- migration الأولى هي `CREATE TABLE IF NOT EXISTS` — لا تحذف بيانات
- **لا حاجة لـ data migration rollback**







## 10. Acceptance Criteria

### AC-1: SchemaRegistry
- [ ] `suppliers` مسجَّل في `SchemaRegistry`
- [ ] `customers` مسجَّل في `SchemaRegistry`
- [ ] `ensure_schema()` يضيف الأعمدة الناقصة فقط
- [ ] يعمل مع SQLite ويمكن ترقيته لـ PostgreSQL لاحقاً

### AC-2: MigrationRunner
- [ ] `run_migrations()` يشغل `v1_schema_snapshot` بنجاح
- [ ] `get_current_version()` يرجع `v1_schema_snapshot`
- [ ] migration المُطبقة لا تُشغل مرة أخرى (idempotent)

### AC-3: customer.py Migration
- [ ] جميع دوال `customer.py` تعمل بنفس النتائج السابقة
- [ ] `list_customers` يرجع نفس البيانات
- [ ] `create_customer` يُنشئ سجل صالح
- [ ] `update_customer` يحدث السجل صحيحاً
- [ ] `delete_customer` يحذف السجل صحيحاً

### AC-4: Regression
- [ ] 0 breakage في اختبارات Phase 3 الحالية
- [ ] 0 breakage في اختبارات Memory/Goal/Outcome
- [ ] 0 breakage في اختبارات Services
- [ ] لا توجد warnings جديدة







## 11. Definition of Done

1. **Code:**
   - `SchemaRegistry` تسجل `suppliers` و `customers`
   - `MigrationRunner` يُشغَّل `v1_schema_snapshot` فعلياً
   - `customer.py` مُرحَّل بالكامل إلى `DatabaseSession`
   - باقي services تبقى على raw SQL القديم (بدون تغيير)

2. **Tests:**
   - 6+ اختبار تكامل لـ `customer.py` مع `DatabaseSession`
   - 2+ اختبار تحديث لـ `SchemaRegistry`
   - 2+ اختبار تحديث لـ `MigrationRunner`
   - Regression يمر (0 breakage)

3. **Documentation:**
   - `CURRENT_STATUS.md` يُحدَّث ليعكس WP-ORM-002
   - `TECH_DEBT.md` يُحدَّث لإزالة أي بند متعلق بالـORM من Active Debt

4. **Governance:**
   - Commit واحد: `feat(database): activate ORM foundation with customer slice`
   - Push إلى `origin/main`
   - `main == origin/main`

5. **No Side Effects:**
   - لا تغيير في routers
   - لا تغيير في API contracts
   - لا تغيير في Pydantic schemas
   - لا تغيير في DEM core أو AI Memory أو Knowledge Graph







## 12. Constraints & Guardrails

| القيد | السبب |
|--------|-------|
| لا PostgreSQL migration | الهدف هو تفعيل الأساس، ليس ترحيل قاعدة البيانات |
| لا تغيير routers | البنية الحالية thin routers صحيحة |
| لا تغيير API contracts | الخطة محصورة في data layer |
| لا تغيير MemoryProvider | خارج النطاق |
| لا تغيير DEM core | خارج النطاق |
| خدمة واحدة فقط | إثبات النمط قبل التوسع |
| migration واحدة فقط | schema snapshot فقط — لا data migration |
| Raw SQL يبقى functional | backward compatibility كاملة |
| لا تستخدم `execute_update()` في الخدمات المُرحَّلة | يجب استخدام `DatabaseSession.update()` مباشرة |







## 13. Post-WP-ORM-002 Path

بعد نجاح WP-ORM-002:
1. ترحيل باقي services تدريجياً (shipping, invoice, customs, documents, resources)
2. ترحيل `init_db()` بالكامل لاستخدام `SchemaRegistry` + `MigrationRunner`
3. إضافة migrations فعلية لكل schema change
4. **عندما تكون كل services مُرحَّلة:** تقييم PostgreSQL migration feasibility







## 14. Approval

| الدور | الاسم | القرار |
|-------|--------|--------|
| Lead Architect | | PENDING |
| Project Owner | | PENDING |
| Engineering | | PENDING |

**تاريخ الإنشاء:** 2026-09-05  
**تاريخ الانتهاء:** PENDING  
**Baseline:** Post WP-ORM-001 closure (`72bc033`)
