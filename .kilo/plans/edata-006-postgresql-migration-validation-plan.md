# E-DATA-006 — PostgreSQL Migration Validation Plan

**Finding:** E-DATA-006
**Priority:** P0
**WP Strategy:** STANDALONE
**Status:** PLAN ONLY — No Implementation Authorized
**Date:** 2026-08-23
**Authority:** Lead Architect Repair Decision — APPROVE REPAIR

---

## 1. Purpose

التحقق من أن مسار PostgreSQL migration الموجود فعليًا يعمل end-to-end قبل السماح بأي production migration.

هذه الخطة **لا تنفذ migration** على بيانات الإنتاج الحالية.

## 2. Scope

### In Scope
- التحقق من أن `backend/scripts/init_postgres_schema.sql` ينشئ schema كامل ومتطابق مع SQLite schema الحالي
- التحقق من أن `backend/scripts/migrate_sqlite_to_postgres.py` يعمل بشكل صحيح في وضعي `--dry-run` و `--verify`
- التحقق من أن Alembic migrations تعمل على PostgreSQL fresh database
- التحقق من data integrity بعد migration
- التحقق من rollback strategy حقيقية (snapshot/backup → migration → restore)
- التحقق من performance baseline على PostgreSQL كـ validation evidence فقط
- التحقق من أن جميع الجداول والعلاقات والبيانات محفوظة بشكل صحيح

### Out of Scope
- تنفيذ migration على بيانات الإنتاج الحالية
- تغيير `DATABASE_URL` الافتراضي من SQLite
- تعديل `backend/app/core/database.py`
- تعديل business logic
- database redesign
- إنشاء Work Package فعلي
- Commit / Push / Merge
- استخدام نتائج الأداء كسبب لتغيير التصميم

## 3. Current Evidence

### Existing Artifacts
| Artifact | Location | Status |
|----------|----------|--------|
| PostgreSQL schema script | `backend/scripts/init_postgres_schema.sql` | EXISTS |
| Migration utility | `backend/scripts/migrate_sqlite_to_postgres.py` | EXISTS |
| ADR | `docs/architecture/ADR-0002-postgresql-migration-path.md` | EXISTS |
| Alembic env | `backend/alembic/env.py` | EXISTS |
| Legacy cleanup migration | `backend/alembic/versions/0f82a20f2bb7_legacy_cleanup.py` | EXISTS |

### Current Runtime State
- **Runtime:** SQLite only
- **DATABASE_URL:** `sqlite:///./data/nile_key.db` (default)
- **PostgreSQL service:** Present in docker-compose.yml but not started
- **Alembic:** Configured for SQLite; PostgreSQL URL support exists in env.py

## 4. Validation Paths

### Path A: Fresh Schema Validation
1. إنشاء قاعدة بيانات PostgreSQL فارغة في بيئة اختبار
2. تنفيذ `backend/scripts/init_postgres_schema.sql`
3. التحقق من أن جميع الجداول تم إنشاؤها
4. التحقق من أنواع البيانات المناسبة PostgreSQL
5. التحقق من Foreign Keys موجودة
6. التحقق من Indexes مناسبة
7. مقارنة النتائج مع SQLite schema الحالي

### Path B: Alembic Compatibility Validation
1. إنشاء قاعدة بيانات PostgreSQL فارغة منفصلة في بيئة اختبار
2. تعيين `DATABASE_URL=postgresql://...` في بيئة اختبار فقط
3. تنفيذ `alembic upgrade head`
4. التحقق من أن جميع migrations تطبق بدون أخطاء
5. التحقق من أن `0f82a20f2bb7_legacy_cleanup` تعمل بشكل صحيح على PostgreSQL

### Path Comparison
- مقارنة النتائج بين Path A و Path B
- توثيق أي اختلاف في schema أو constraints
- تحديد أي تكرار أو تعارض بين المسارين

## 5. Data Migration Validation

### Phase 1: Dry Run
1. إنشاء sample SQLite database ببيانات اختبار
2. تنفيذ migration utility مع `--dry-run`
3. التحقق من أن الأعمدة محفوظة بشكل صحيح
4. التحقق من أن row counts متطابقة

### Phase 2: Verification Run
1. تنفيذ migration utility مع `--verify` على sample database
2. التحقق من أن جميع الجداول migrated بشكل صحيح
3. التحقق من data integrity (row counts + checksums)
4. التحقق من referential integrity

## 6. Rollback Strategy

### Snapshot / Backup
1. قبل أي migration test: إنشاء snapshot لقاعدة البيانات المصدر
2. حفظ backup من SQLite database
3. توثيق حالة قاعدة البيانات قبل التجربة

### Migration Test
1. تنفيذ migration على test database فقط
2. تسجيل جميع التغييرات

### Verification
1. التحقق من نجاح migration
2. التحقق من data integrity

### Restore Procedure
1. استعادة قاعدة البيانات من backup
2. التحقق من سلامة البيانات بعد restore
3. إثبات أن PostgreSQL يمكن استعادتها إلى حالة ما قبل التجربة
4. توثيق نجاح restore

### Acceptance
- Backup/snapshot موجود ✅
- Restore نجح ✅
- سلامة البيانات محفوظة ✅

## 7. Performance Baseline

### Scope
- قياس performance على PostgreSQL في بيئة اختبار
- مقارنة مع SQLite performance
- توثيق results كـ validation evidence فقط

### Constraints
- لا تستخدم نتائج الأداء تلقائيًا لإعادة تصميم قاعدة البيانات
- Performance issues تُسجل كـ E-DATA-001 (CONFIRMED + ACCEPTED / Deferred with Condition)
- لا تحويل Performance Baseline إلى Finding جديدة أو WP جديدة

## 8. Production Isolation Safeguards

### Test-Only Database
- جميع الاختبارات على test database فقط
- لا اتصال مباشر بقاعدة بيانات الإنتاج

### Credential Isolation
- منع استخدام credentials الخاصة بالإنتاج
- استخدام credentials اختبار منفصلة

### Environment Isolation
- بيئة اختبار منفصلة تمامًا
- لا shared services مع الإنتاج

### Connection Guard
- Connection string clearly marked as test
- Assertion / guard لمنع الاتصال بقاعدة بيانات الإنتاج

### Documentation
- توثيق واضح لعدم استخدام Production Data
- Audit trail لجميع Operations

## 9. Acceptance Criteria

| # | Acceptance Criterion | Verification Method |
|---|---------------------|---------------------|
| AC-006.1 | Path A: `init_postgres_schema.sql` ينشئ جميع الجداول بدون أخطاء | Manual execution + inspection |
| AC-006.2 | Path B: Alembic migrations تعمل على PostgreSQL | `alembic upgrade head` succeeds |
| AC-006.3 | Path A و Path B results متطابقة | Side-by-side comparison |
| AC-006.4 | Migration utility يعمل في `--dry-run` mode | Script execution + output inspection |
| AC-006.5 | Migration utility يعمل في `--verify` mode | Script execution + checksum validation |
| AC-006.6 | Row counts متطابقة بعد migration | Verification results |
| AC-006.7 | Referential integrity محفوظة | Foreign key checks |
| AC-006.8 | Snapshot/backup موجود قبل migration | File verification |
| AC-006.9 | Restore procedure يعمل و salmonة البيانات محفوظة | Restore test + data integrity check |
| AC-006.10 | Performance baseline documented | Performance test results |
| AC-006.11 | Test-only database used throughout | Connection string audit + environment verification |
| AC-006.12 | No production credentials used | Credential audit |
| AC-006.13 | No production data touched | Database query — zero production rows affected |

## 10. Test Matrix

| Component | Test | Expected Result |
|-----------|------|-----------------|
| Schema Path A | `init_postgres_schema.sql` execution | All tables created |
| Alembic Path B | `upgrade head` on PostgreSQL | All migrations apply |
| Path Comparison | Side-by-side schema comparison | No unexpected differences |
| Migration Utility | `--dry-run` | Counts printed, no writes |
| Migration Utility | `--verify` on sample DB | PASS for all tables |
| Data Integrity | Row count comparison | SQLite count == PostgreSQL count |
| Data Integrity | Checksum comparison | SQLite checksum == PostgreSQL checksum |
| Rollback | Snapshot before migration | Snapshot file exists |
| Rollback | Restore after migration | Data restored successfully |
| Rollback | Post-restore integrity check | All data intact |
| Performance | PostgreSQL performance test | Baseline documented |
| Production Isolation | Connection string audit | Test-only database confirmed |
| Production Isolation | Credential audit | No production credentials used |
| Production Isolation | Production data audit | Zero production rows affected |

## 11. Migration Safety

### Pre-Migration Checklist
- [ ] Test database created and isolated
- [ ] Production credentials not present in environment
- [ ] Snapshot/backup of source database completed
- [ ] All team members aware of test-only scope
- [ ] Rollback procedure tested and documented

### During Migration
- All operations on test database only
- No connection to production database
- All changes logged and auditable

### Post-Migration
- Verify data integrity
- Document results
- Restore source database to original state
- Confirm no production impact

## 12. Evidence Required for Closure

1. **Validation Report:**
   - Path A results (schema validation)
   - Path B results (Alembic compatibility)
   - Path comparison findings
   - Migration dry-run results
   - Migration verification results
   - Rollback test results
   - Performance baseline results

2. **Screenshots / Logs:**
   - PostgreSQL healthcheck
   - Alembic migration output
   - Migration utility output
   - Rollback test output
   - Performance test output

3. **Isolation Evidence:**
   - Connection strings used (test-only)
   - Credential audit report
   - Production data audit report (zero rows affected)

4. **Updated Documentation:**
   - ADR-0002 updates if needed
   - Any new findings or issues discovered

## 13. Governance Checkpoints

| Checkpoint | Gate | Decision |
|------------|------|----------|
| Path A Complete | GATE-006-A | Proceed to Path B |
| Path B Complete | GATE-006-B | Proceed to path comparison |
| Path Comparison Complete | GATE-006-C | Proceed to data migration |
| Data Migration Complete | GATE-006-D | Proceed to rollback test |
| Rollback Test Complete | GATE-006-E | Proceed to performance baseline |
| Performance Baseline Complete | GATE-006-F | Ready for production migration authorization |

## 14. Implementation Authorization Boundary

- **هذه الخطة معتمدة للتخطيط فقط.**
- **التنفيذ يحتاج Authorization منفصل.**
- **نجاح تنفيذ الخطة يحتاج Verification مستقل.**
- **الإغلاق يحتاج Lead Architect / Governance decision.**

لا يُسمح بـ:
- تنفيذ migration على بيانات الإنتاج
- تغيير `DATABASE_URL`
- تعديل schema
- تعديل business logic
- Commit / Push / Merge

---

## References

| Source | Description |
|--------|-------------|
| `docs/architecture/ADR-0002-postgresql-migration-path.md` | PostgreSQL migration path ADR |
| `backend/scripts/init_postgres_schema.sql` | PostgreSQL schema initialization |
| `backend/scripts/migrate_sqlite_to_postgres.py` | Migration utility |
| `backend/alembic/env.py` | Alembic configuration |
| `backend/alembic/versions/0f82a20f2bb7_legacy_cleanup.py` | Legacy cleanup migration |
| `CURRENT_STATUS.md` | Audit Gates B–G closures |
| `POST_AUDIT_HANDOFF.md` | Post-Audit Operating Rule |
