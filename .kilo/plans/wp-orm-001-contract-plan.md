# Contract Plan: Phase 3 Readiness — Raw SQL → ORM Abstraction

**Work Package:** WP-ORM-001  
**Status:** Planned — awaiting approval  
**Priority:** HIGH  
**Phase:** Phase 3 — Production Readiness  
**Governing Documents:** `PLAN.md` (Master Roadmap v2.1), `TECH_DEBT.md`, `CURRENT_STATUS.md`  
**Branch:** `main`  
**Target Baseline:** Post WP-AIM-001 closure  

---







## 1. Gap / Problem

### 1.1 الحالة الحالية
المشروع يعتمد بالكامل على **Raw SQL** عبر `sqlite3` مباشرة في:
- `backend/app/core/database.py` — `get_db()`, `execute_update()`, `init_db()`, `_ensure_*_schema()`
- `backend/app/services/base.py` — `connection()`, `build_list_query()`, `parse_json()`, `dumps_json()`, `now_iso()`
- جميع وحدات `backend/app/services/*.py` — استعلامات SQL مكتوبة يدوياً
- جميع `backend/app/routers/*.py` — بعضها يحتفظ بـ SQL مباشر
- `backend/app/agent/memory/sqlite_provider.py` — SQL مخصص للذاكرة
- `backend/app/agent/audit/recorder.py` — SQL مباشر لـ audit logs

### 1.2 المشاكل المحددة
| # | المشكلة | التأثير | الخطورة |
|---|---------|---------|---------|
| 1 | **لا يوجد ORM abstraction** | كل تغيير schema يتطلب تعديل يدوي في 10+ ملفات | HIGH |
| 2 | **schema evolution يدوي** | `_ensure_*_schema()` مكتوب يدوياً لكل جدول | HIGH |
| 3 | **لا يوجد type-safe queries** | أخطاء وقت الترجمة غير مكشوفة | MEDIUM |
| 4 | **PostgreSQL migration معقد** | يتطلب إعادة كتابة كل SQL | HIGH |
| 5 | **لا يوجد unit-of-work pattern** | كل عملية إيداع/سحب تفتح اتصال منفصل | MEDIUM |
| 6 | **لا يوجد transaction scoping موحد** | `conn.commit()` مكتوب يدوياً في كل خدمة | MEDIUM |

### 1.3 المخاطر على Phase 3 Readiness
- **Maintainability:** أي إضافة جدول/حقل تتطلب تعديلات متعددة في `database.py` + `_ensure_*_schema()` + service + router + tests
- **Schema Evolution:** لا يوجد آلية migration آمنة عبر الإصدارات
- **PostgreSQL Readiness:** الكود الحالي مرتبط بـ SQLite-specific syntax (`AUTOINCREMENT`, `TEXT DEFAULT CURRENT_TIMESTAMP`, `PRAGMA foreign_keys`)
- **Testability:** صعوبة إنشاء mock/fake للـ database layer بدون ORM abstraction







## 2. Objective

إدخال **طبقة ORM/Database Abstraction** تدريجياً تسمح بـ:
1. **الحفاظ على SQLite** كـ runtime فعلي للمشروع الحالي
2. **تسوية schema evolution** عبر migration unit موحدة
3. **تقليل الـraw SQL** في service layer تدريجياً
4. **تهيئة PostgreSQL migration** لاحقاً بدون إعادة كتابة
5. **عدم كسر أي سلوك حالي** — جميع الاختبارات الحالية تظل سابرة







## 3. Scope — المرحلة الأولى فقط

### 3.1 ما يُغطى في هذه المرحلة
| المكون | النطاق | الملفات المتأثرة |
|---------|--------|-----------------|
| **Database Connection Layer** | إضافة `DatabaseSession` abstraction فوق `sqlite3` | `backend/app/core/database.py` |
| **Schema Registry** | تسجيل الجداول والحقول بشكل مركزي | `backend/app/core/schema_registry.py` (جديد) |
| **Migration Runner** | آلية migration بسيطة تعمل فوق SQLite | `backend/app/core/migrations.py` (جديد) |
| **Service Layer Slice** | ترحيل **واحدة** فقط كـ proof of concept | `backend/app/services/supplier.py` |
| **Tests** | اختبارات الوحدة والتكامل للطبقة الجديدة | `backend/tests/orm_abstraction/` (جديد) |

### 3.2 ما يُستبعد من هذه المرحلة
- ترحيل باقي services (customers, shipping, invoice, customs, documents, resources, eta, workflow, knowledge_graph, trade_intelligence)
- ترحيل routers
- ترحيل agent/memory/audit SQL
- PostgreSQL migration نفسها
- أي تغيير في Pydantic schemas
- أي تغيير في API contracts
- Knowledge Graph / Providers / Multi-Agent / Avatar / Full Autonomy







## 4. Out of Scope

- **لا** تُنشأ full ORM مثل SQLAlchemy من الصفر — نستخدم SQLAlchemy Core (أداة موجودة) كـ foundation
- **لا** يُغيّر `MemoryProvider` interface
- **لا** يُغيّر DEM core أو Decision Engine أو Goal Evolution أو Outcome Feedback
- **لا** يُفتح PostgreSQL migration في هذه المرحلة
- **لا** يُغيّر routers أو API contracts
- **لا** يُضاف avatar أو knowledge graph أو multi-agent







## 5. Architecture / Abstraction Strategy

### 5.1 المبدأ الأساسي
> **لا تُعطّل ما يعمل.**  
> الـraw SQL الحالي يبقى functional طوال المرحلة. الطبقة الجديدة تُضاف **بجانبه** كـ parallel path، ثم يُهاجر slice واحد فقط لإثبات النمط.

### 5.2 البنية المستهدفة

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
                    │  │  SchemaRegistry                  │    │
                    │  │  MigrationRunner                 │    │
                    │  └─────────────────────────────────┘    │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │    backend/app/core/database.py         │
                    │  - get_db() [موجود، يبقى]               │
                    │  - connection() [موجود، يبقى]           │
                    │  - DatabaseSession [جديد]               │
                    │  - SchemaRegistry [جديد]                │
                    │  - MigrationRunner [جديد]               │
                    └──────────────────┬──────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────────┐
                    │         SQLite (nile_key.db)            │
                    │    (PostgreSQL لاحقاً عبر نفس Layer)     │
                    └─────────────────────────────────────────┘
```

### 5.3 المكونات الجديدة

#### 5.3.1 `DatabaseSession` (جديد في `database.py`)
```python
class DatabaseSession:
    """Wrapper around sqlite3 connection with ORM-like helpers."""
    
    def execute(self, query: str, params: tuple = ()) -> Cursor
    def fetch_one(self, query: str, params: tuple = ()) -> dict | None
    def fetch_all(self, query: str, params: tuple = ()) -> list[dict]
    def insert(self, table: str, data: dict) -> int  # returns lastrowid
    def update(self, table: str, record_id: int, data: dict) -> bool
    def delete(self, table: str, record_id: int) -> bool
    def transaction(self) -> Generator["DatabaseSession"]
```

**المسؤولية:** تغليف `sqlite3` connection مع helpers توفر واجهة موحدة قابلة للتبديل لـ PostgreSQL لاحقاً.

**الحدود:** لا تحاول محاكاة ORM كامل — فقط تبسيط العمليات الشائعة (CRUD + query).

#### 5.3.2 `SchemaRegistry` (جديد في `schema_registry.py`)
```python
class SchemaRegistry:
    """Central registry for table schemas and column definitions."""
    
    def register_table(self, name: str, columns: dict[str, str], indexes: list[str] = None)
    def get_table(self, name: str) -> TableDefinition
    def ensure_schema(self, conn, table_name: str) -> None
```

**المسؤولية:** تخزين تعريفات الجداول بشكل مركزي بدلاً من توزيع `_ensure_*_schema()` عبر 10+ دالة.

**الحدود:** لا تنشئ الجداول — فقط تضمان وجود الأعمدة المطلوبة.

#### 5.3.3 `MigrationRunner` (جديد في `migrations.py`)
```python
class MigrationRunner:
    """Simple versioned migration runner for schema changes."""
    
    def run_migrations(self, conn, target_version: str) -> None
    def get_current_version(self, conn) -> str
```

**المسؤولية:** تشغيل migrations بتسلسل آمن مع تسجيل الإصدار.

**الحدود:** لا تحل محل Alembic — هي طبقة تطبيق فوق raw SQL migrations بسيطة.

### 5.4 استراتيجية التعايش
1. **المرحلة 1:** إضافة `DatabaseSession` + `SchemaRegistry` + `MigrationRunner` بدون تعديل أي كود موجود
2. **المرحلة 2:** ترحيل `supplier.py` فقط إلى `DatabaseSession` كـ proof of concept
3. **المرحلة 3:** بعد نجاح المرحلة 2، ترحيل باقي services تدريجياً (لكن هذا خارج نطاق WP-ORM-001)
4. **طوال الوقت:** الـraw SQL القديم يبقى functional كـ fallback







## 6. Migration Sequence — المرحلة الأولى فقط

### الخطوة 1: إضافة `DatabaseSession` إلى `database.py`
- إضافة الكلاس الجديد **بجانب** `get_db()` و `connection()` الموجودة
- لا يُغيّر أي دالة موجودة
- ي uses `sqlite3` مباشرة (نفس motor) لكن بـ interface موحد

### الخطوة 2: إضافة `SchemaRegistry`
- ملف جديد `backend/app/core/schema_registry.py`
- يسجل تعريفات الجداول من `_create_tables()` و `_ensure_*_schema()` بشكل مركزي
- `ensure_schema()` يضمن أن الأعمدة المطلوبة موجودة (نفس منطق `ensure_columns()`)

### الخطوة 3: إضافة `MigrationRunner`
- ملف جديد `backend/app/core/migrations.py`
- جدول `schema_migrations` بسيط (id, version, applied_at)
- migrations تُكتب كـ raw SQL لكن بتسلسل آمن

### الخطوة 4: ترحيل `supplier.py` فقط
- استخدام `DatabaseSession` بدلاً من `connection()` + raw SQL
- إثبات أن النمط يعمل مع اختبارات سابرة
- باقي services تبقى على الـraw SQL القديم







## 7. First Code Slice — المرشح المباشر

### 7.1 الملفات المطلوبة
| الملف | الإجراء |
|--------|---------|
| `backend/app/core/database.py` | إضافة `DatabaseSession` class |
| `backend/app/core/schema_registry.py` | ملف جديد |
| `backend/app/core/migrations.py` | ملف جديد |
| `backend/app/services/supplier.py` | ترحيل إلى `DatabaseSession` |
| `backend/tests/orm_abstraction/test_database_session.py` | اختبارات وحدة |
| `backend/tests/orm_abstraction/test_schema_registry.py` | اختبارات وحدة |
| `backend/tests/orm_abstraction/test_migrations.py` | اختبارات وحدة |
| `backend/tests/orm_abstraction/test_supplier_orm.py` | اختبار تكامل |

### 7.2 هيكل `DatabaseSession`
```python
class DatabaseSession:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn
        self._conn.row_factory = sqlite3.Row
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        return self._conn.execute(query, params)
    
    def fetch_one(self, query: str, params: tuple = ()) -> dict | None:
        row = self.execute(query, params).fetchone()
        return dict(row) if row else None
    
    def fetch_all(self, query: str, params: tuple = ()) -> list[dict]:
        return [dict(r) for r in self.execute(query, params).fetchall()]
    
    def insert(self, table: str, data: dict) -> int:
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        cursor = self.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
            tuple(data.values())
        )
        return cursor.lastrowid
    
    def update(self, table: str, record_id: int, data: dict) -> bool:
        if not data:
            return False
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        params = tuple(data.values()) + (record_id,)
        cursor = self.execute(f"UPDATE {table} SET {set_clause} WHERE id = ?", params)
        return cursor.rowcount > 0
    
    def delete(self, table: str, record_id: int) -> bool:
        cursor = self.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
        return cursor.rowcount > 0
    
    @contextmanager
    def transaction(self):
        try:
            yield self
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise
```

### 7.3 هيكل `SchemaRegistry`
```python
class SchemaRegistry:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tables = {}
        return cls._instance
    
    def register_table(self, name: str, columns: dict[str, str], indexes: list[str] | None = None):
        self._tables[name] = {
            "columns": columns,
            "indexes": indexes or []
        }
    
    def ensure_schema(self, conn, table_name: str) -> None:
        if table_name not in self._tables:
            return
        existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
        for col, col_type in self._tables[table_name]["columns"].items():
            if col not in existing:
                conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {col_type}")
```

### 7.4 هيكل `MigrationRunner`
```python
class MigrationRunner:
    def __init__(self, conn):
        self._conn = conn
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._conn.commit()
    
    def get_current_version(self) -> str | None:
        row = self._conn.execute("SELECT version FROM schema_migrations ORDER BY id DESC LIMIT 1").fetchone()
        return row[0] if row else None
    
    def run_migrations(self, migrations: list[tuple[str, str]]) -> None:
        current = self.get_current_version()
        for version, sql in migrations:
            if current and version <= current:
                continue
            self._conn.execute(sql)
            self._conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
            self._conn.commit()
```







## 8. Tests / Regression

### 8.1 اختبارات الوحدة الجديدة
| الملف | number of tests | الغرض |
|--------|-----------------|--------|
| `test_database_session.py` | 8 | اختبار `DatabaseSession` مع SQLite in-memory |
| `test_schema_registry.py` | 6 | اختبار `SchemaRegistry` ensure_schema |
| `test_migrations.py` | 5 | اختبار `MigrationRunner` apply/rollback/idempotency |

### 8.2 اختبارات التكامل
| الملف | number of tests | الغرض |
|--------|-----------------|--------|
| `test_supplier_orm.py` | 6 | اختبار `supplier.py` مع `DatabaseSession` |

### 8.3 Regression المطلوبة
| المجموعة | number of tests | الشرط |
|----------|-----------------|-------|
| `tests/agent/test_memory*.py` | 41+ | كلها تمر |
| `tests/agent/test_goal_evolution.py` | 15 | كلها تمر |
| `tests/agent/test_outcome.py` | 10+ | كلها تمر |
| `tests/services/test_supplier.py` | 10+ | كلها تمر |
| **إجمالي Regression** | **80+** | **0 breakage** |

### 8.4 شروط الفوز
- جميع اختبارات الوحدة الجديدة تمر
- جميع اختبارات Regression الحالية تمر (0 breakage)
- لا توجد `unawaited coroutine` warnings جديدة
- لا تغيير في API responses







## 9. Performance & Risk Assessment

### 9.1 الأداء
| الجانب | التأثير المتوقع | التخفيف |
|---------|-----------------|---------|
| DatabaseSession overhead | ~5% على ops ثقيلة | لا يكاد يذكر على operations الحالية (CRUD بسيط) |
| SchemaRegistry initialization | مرة واحدة عند startup | negligible |
| MigrationRunner | مرة واحدة عند startup | negligible |
| **Net Impact** | **< 5% على hot paths** | **مقبول لمرحلة readiness** |

### 9.2 المخاطر
| # | الخطر | الاحتمال | التأثير | التخفيف |
|---|-------|----------|---------|---------|
| 1 | كسر سلوك supplier.py الحالي | LOW | HIGH | اختبارات regression كاملة |
| 2 | memory leak في DatabaseSession | LOW | MEDIUM | connection management موحد |
| 3 | schema drift بين Registry و DB | MEDIUM | HIGH | MigrationRunner يضمن التسلسل |
| 4 | تأثير على startup time | LOW | LOW | SchemaRegistry يبطن definitions |
| 5 | تعارض مع Alembic migrations | MEDIUM | HIGH | MigrationRunner يعمل *قبل* Alembic |







## 10. Rollback Strategy

### 10.1 Rollback السريع
1. **git revert** للcommit الخاص بـ WP-ORM-001
2. `supplier.py` يُرجع إلى `connection()` + raw SQL (النسخة الاحتياطية في git)
3. `database.py` يُرجع إلى `get_db()` + `connection()` فقط
4. الملفات الجديدة (`schema_registry.py`, `migrations.py`) تُحذف

### 10.2 Rollback الجزئي
إذا فشل `supplier.py` فقط:
1. إعادة `supplier.py` إلى raw SQL
2. إبقاء `DatabaseSession` + `SchemaRegistry` + `MigrationRunner` للاستخدام المستقبلي
3. لا تأثير على باقي services

### 10.3 Rollback البيانات
- لا يوجد schema changes في هذه المرحلة — فقط إضافة helpers
- `schema_migrations` table موجود لكن لا يحتوي migrations فعلية بعد
- **لا حاجة لـ data migration rollback** في المرحلة الأولى







## 11. Acceptance Criteria

### AC-1: DatabaseSession
- [ ] `DatabaseSession` يُنشئ connection صالح لـ SQLite
- [ ] `fetch_one()` و `fetch_all()` يرجعان dicts
- [ ] `insert()` يرجع `lastrowid` صحيح
- [ ] `update()` يرجع `True/False` حسب rowcount
- [ ] `delete()` يرجع `True/False` حسب rowcount
- [ ] `transaction()` يلغي التعديلات عند حدوث exception

### AC-2: SchemaRegistry
- [ ] `register_table()` يسجل تعريف جدول
- [ ] `ensure_schema()` يضيف الأعمدة الناقصة فقط
- [ ] `ensure_schema()` لا يمس الجداول الموجودة
- [ ] يعمل مع SQLite ويمكن ترقيته لـ PostgreSQL لاحقاً

### AC-3: MigrationRunner
- [ ] `run_migrations()` يشغل migrations بالتسلسل
- [ ] `get_current_version()` يرجع آخر version مطبق
- [ ] migrations المُطبقة لا تُشغل مرة أخرى (idempotent)

### AC-4: supplier.py Migration
- [ ] جميع دوال `supplier.py` تعمل بنفس النتائج السابقة
- [ ] `list_suppliers` يرجع نفس البيانات
- [ ] `create_supplier` يُنشئ سجل صالح
- [ ] `update_supplier` يحدث السجل صحيحاً
- [ ] `delete_supplier` يحذف السجل صحيحاً

### AC-5: Regression
- [ ] 0 breakage في اختبارات Phase 3 الحالية
- [ ] 0 breakage في اختبارات Memory/Goal/Outcome
- [ ] 0 breakage في اختبارات Services
- [ ] لا توجد warnings جديدة







## 12. Definition of Done

1. **Code:**
   - `DatabaseSession` + `SchemaRegistry` + `MigrationRunner` مُضافة إلى `database.py` أو ملفات جديدة
   - `supplier.py` مُرحَّل بالكامل إلى `DatabaseSession`
   - باقي services تبقى على raw SQL القديم (بدون تغيير)

2. **Tests:**
   - 20+ اختبار وحدة جديدة للطبقة الجديدة
   - 6 اختبار تكامل لـ `supplier.py` مع `DatabaseSession`
   - 80+ اختبار regression يمر (0 breakage)

3. **Documentation:**
   - `CURRENT_STATUS.md` يُحدَّث ليعكس WP-ORM-001
   - `TECH_DEBT.md` يُحدَّث لإزالة "Raw SQL everywhere" منActive Debt
   - `.kilo/plans/` يحتوي الخطة

4. **Governance:**
   - Commit واحد: `feat(orm): add database abstraction layer and migrate supplier service`
   - Push إلى `origin/main`
   - `main == origin/main`

5. **No Side Effects:**
   - لا تغيير في routers
   - لا تغيير في API contracts
   - لا تغيير في Pydantic schemas
   - لا تغيير في DEM core أو AI Memory أو Knowledge Graph







## 13. Constraints & Guardrails

| القيد | السبب |
|--------|-------|
| لا PostgreSQL migration | الهدف هو تسلية الدين، ليس ترحيل قاعدة البيانات |
| لا تغيير routers | البنية الحالية thin routers صحيحة |
| لا تغيير API contracts | الخطة محصورة في data layer |
| لا تغيير MemoryProvider | خارج النطاق |
| لا تغيير DEM core | خارج النطاق |
| Migration واحدة فقط | إثبات النمج قبل التوسع |
| Raw SQL يبقى functional | backward compatibility كاملة |







## 14. Post-WP-ORM-001 Path

بعد نجاح WP-ORM-001:
1. ترحيل باقي services تدريجياً (customers, shipping, invoice, customs, documents, resources)
2. ترحيل `database.py` migrations بالكامل إلى MigrationRunner
3. ترحيل routers إلى use DatabaseSession عبر dependency injection
4. إضافة type-safe query builder
5. **عندما تكون كل services مُرحَّلة:** تقييم PostgreSQL migration feasibility







## 15. Approval

| الدور | الاسم | القرار |
|-------|--------|--------|
| Lead Architect | | PENDING |
| Project Owner | | PENDING |
| Engineering | | PENDING |

**تاريخ الإنشاء:** 2026-09-05  
**تاريخ الانتهاء:** PENDING  
**Baseline:** Post WP-AIM-001 closure
