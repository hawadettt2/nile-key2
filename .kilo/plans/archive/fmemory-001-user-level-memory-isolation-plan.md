# F-MEMORY-001 — User-Level Memory Isolation Plan

**Finding:** F-MEMORY-001
**Priority:** P1
**WP Strategy:** STANDALONE
**Status:** PLAN ONLY — No Implementation Authorized
**Date:** 2026-08-23
**Authority:** Lead Architect Repair Decision — APPROVE REPAIR

---

## 1. Purpose

تحديد وتنفيذ user-level memory isolation لـ `agent_memory` schema بحيث:

> **كل Memory Record صالحة للاستخدام في Production يجب أن تكون مرتبطة بـ `user_id` صالح وغير NULL.**

هذه الخطة **لا تعدّل schema** و**لا تنفذ migration** و**لا تعدّل code**.

## 2. Scope

### In Scope
- تحليل current `agent_memory` schema واستخداماتها
- تصميم إضافة `user_id` كـ NOT NULL column
- Legacy data migration strategy للبيانات التاريخية بدون `user_id`
- Ownership invariant enforcement
- Isolation rules للـ CRUD operations
- Access-control requirements
- Index strategy (composite index for user_id + session_id)
- Test strategy بما في ذلك cross-user isolation tests
- Rollback strategy with backup/snapshot
- Acceptance criteria
- Privacy/security verification plan
- Evidence required for closure
- Governance checkpoints

### Out of Scope
- تعديل `backend/app/core/database.py`
- تعديل `backend/app/agent/memory/sqlite_provider.py`
- تعديل أي application code
- تنفيذ schema change
- تنفيذ data migration
- إنشاء Work Package فعلي
- Commit / Push / Merge / Rebase
- Target Architecture changes
- External Research

## 3. Current Evidence

### Schema Evidence
**Current `agent_memory` schema** (`backend/app/core/database.py` lines 750-762):
```sql
CREATE TABLE IF NOT EXISTS agent_memory (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    memory_type TEXT DEFAULT 'context',
    importance INTEGER DEFAULT 5,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
)
```

**Current `agent_sessions` schema** (`backend/app/core/database.py` lines 737-747):
```sql
CREATE TABLE IF NOT EXISTS agent_sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    context TEXT,
    status TEXT DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

### Key Finding
- `agent_sessions` already has `user_id INTEGER NOT NULL`
- `agent_memory` has `session_id` only — no `user_id`
- `agent_memory` queries filter by `session_id` only
- This means memory isolation is currently at session level, not user level

### Usage Evidence
**Current memory provider queries** (`backend/app/agent/memory/sqlite_provider.py`):
- `recall(session_id, query, limit)` — filters by session_id
- `store(session_id, key, value, ...)` — stores by session_id
- `forget(session_id, key)` — deletes by session_id
- `summarize(session_id)` — summarizes by session_id
- `cleanup_expired(session_id)` — cleans by session_id

No query currently filters by `user_id`.

## 4. Schema Design

### Target Schema (Production End State)

```sql
CREATE TABLE IF NOT EXISTS agent_memory (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    memory_type TEXT DEFAULT 'context',
    importance INTEGER DEFAULT 5,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
);
```

### Index Strategy
```sql
-- Composite index for primary access pattern: user_id + session_id
CREATE INDEX IF NOT EXISTS idx_agent_memory_user_session ON agent_memory(user_id, session_id);

-- Supporting indexes for query patterns
CREATE INDEX IF NOT EXISTS idx_agent_memory_type ON agent_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_agent_memory_importance ON agent_memory(importance);
CREATE INDEX IF NOT EXISTS idx_agent_memory_expires_at ON agent_memory(expires_at);
```

### Key Design Decisions
1. `user_id NOT NULL` is the **Production End State**
2. `user_id` has FOREIGN KEY to `users(id)`
3. Composite index on `(user_id, session_id)` for primary access pattern
4. Ownership invariant enforced at database and application level

## 5. Ownership Invariant

### Rule
> `agent_memory.user_id` must always equal `agent_sessions.user_id` for the linked `session_id`.

### Enforcement Mechanisms

#### Database-Level
- `user_id` has FOREIGN KEY to `users(id)`
- `session_id` has FOREIGN KEY to `agent_sessions(id)`
- Composite index on `(user_id, session_id)` ensures query patterns align with ownership

#### Application-Level
- All memory operations validate `user_id` matches `agent_sessions.user_id` before executing
- `recall(user_id, session_id, ...)` — rejects if `user_id` mismatch
- `store(user_id, session_id, ...)` — rejects if `user_id` mismatch
- `forget(user_id, session_id, ...)` — rejects if `user_id` mismatch
- `cleanup_expired(user_id)` — scoped to user only

#### Test-Level
- Test: `memory.user_id != session.user_id` → operation fails
- Test: Memory operation without `user_id` → fails
- Test: Cross-user access → fails

## 6. SQLite Migration Mechanics

### Challenge
SQLite does not support `ALTER TABLE ... ALTER COLUMN ... SET NOT NULL` directly.

### Migration Approach

#### Step 1: Add Column (Nullable)
1. Add `user_id INTEGER` column to `agent_memory` (nullable initially)
2. This allows migration window without breaking existing data

#### Step 2: Backfill Eligible Records
1. For each record in `agent_memory`:
   - Look up `session_id` in `agent_sessions`
   - If found: set `user_id = agent_sessions.user_id`
   - If not found: mark for quarantine

#### Step 3: Validate Backfill
1. Verify all eligible records have `user_id` populated
2. Verify no orphaned records remain in main table
3. Generate migration report

#### Step 4: Rebuild Table with NOT NULL Constraint
1. Create new table with `user_id INTEGER NOT NULL`
2. Copy all valid records from old table
3. Drop old table
4. Rename new table
5. Recreate indexes

#### Step 5: Verification
1. Verify `user_id NOT NULL` constraint enforced
2. Verify all production records have valid `user_id`
3. Verify no orphaned records in production

### Rollback During Migration
1. Restore from backup/snapshot taken before migration
2. Original schema and data preserved
3. No data loss

## 7. Legacy Data Migration Strategy

### Step 1: Audit Legacy Records
1. Scan all `agent_memory` records
2. Identify records with `session_id` that maps to `agent_sessions.user_id`
3. Identify orphaned records (session_id not in agent_sessions)
4. Produce migration eligibility report

### Step 2: Migration Eligibility Rules
- **Eligible for migration:** Records where `session_id` exists in `agent_sessions` → set `user_id = agent_sessions.user_id`
- **Requires Governance decision:** Records where `session_id` does not exist in `agent_sessions` → cannot determine user_id
- **Never migrated without approval:** Orphaned records without determinable ownership

### Step 3: Migration Execution Plan
1. Add `user_id` column as nullable initially (for migration window)
2. Backfill eligible records from `agent_sessions`
3. Mark orphaned records in quarantine table
4. Validate migration completeness
5. Rebuild table with `user_id` as NOT NULL (only after all eligible records migrated)
6. Remove quarantine table after Governance approval

### Step 4: Orphaned Record Handling
- Do NOT delete orphaned records automatically
- Do NOT invent or guess `user_id`
- Move to `agent_memory_quarantine` table with original data
- Require explicit Governance decision for each orphaned record
- If no decision: records remain in quarantine, not accessible in production

### Step 5: Rollback
1. Restore from backup/snapshot
2. Original `agent_memory` data preserved
3. Orphaned records remain in quarantine for audit

## 8. Isolation Rules

### Read Isolation
- `recall(user_id, session_id, query, limit)` — must filter by `user_id` first
- Cross-user access must be prevented at query level
- session_id alone is insufficient for access

### Write Isolation
- `store(user_id, session_id, key, value, ...)` — must validate `user_id` matches session owner
- Cannot store memory for another user's session

### Delete Isolation
- `forget(user_id, session_id, key)` — must validate ownership
- `cleanup_expired(user_id)` — scoped to user only

### Access Control
- All memory operations require `user_id` parameter
- `user_id` is validated against `agent_sessions.user_id`
- No memory operation is allowed without user context

## 9. Backward Compatibility

### Transitional State
During migration window only:
- `user_id` column added as nullable
- Legacy records without `user_id` exist temporarily
- Application-level validation rejects operations on records without `user_id`

### Production Contract
After migration complete:
- **لا توجد Production Memory Operations بدون user_id**
- **لا توجد Production Memory Records بدون user_id**
- All queries require `user_id` parameter
- session-only access is not permitted in production

### API Contract
Final production API:
```
recall(user_id: int, session_id: str, ...) -> List[Memory]
store(user_id: int, session_id: str, ...) -> Memory
forget(user_id: int, session_id: str, ...) -> bool
summarize(user_id: int, session_id: str) -> Summary
cleanup_expired(user_id: int) -> int
```

No API method accepts session_id without user_id.

## 10. Test Strategy

### Unit Tests
1. `test_memory_provider_requires_user_id` — verify user_id is required
2. `test_recall_scoped_to_user` — verify recall only returns user's memories
3. `test_store_validates_user_ownership` — verify store validates session ownership
4. `test_forget_scoped_to_user` — verify forget only deletes user's memories
5. `test_cross_user_isolation` — verify User A cannot access User B's memories
6. `test_memory_user_id_mismatch` — verify operation fails when `memory.user_id != session.user_id`
7. `test_memory_operation_without_user_id` — verify operation fails without user_id

### Integration Tests
1. `test_memory_isolation_end_to_end` — full workflow with two users
2. `test_legacy_migration_eligibility` — verify migration rules
3. `test_quarantine_handling` — verify orphaned records go to quarantine
4. `test_not_null_constraint` — verify user_id cannot be NULL after migration

### Cross-User Isolation Tests (Critical)
1. **Test A:** User 1 stores memory → User 2 cannot recall it
2. **Test B:** User 1 forgets memory → User 2's memories unaffected
3. **Test C:** User 1 summarizes session → User 2's sessions not included
4. **Test D:** User 1 cleanup_expired → User 2's memories preserved
5. **Test E:** Mixed legacy/new records → isolation maintained
6. **Test F:** User A attempts to access User B's memory by guessing session_id → fails
7. **Test G:** Memory operation with mismatched user_id and session_id → fails

### Regression Tests
1. All existing memory provider tests must pass
2. All existing DEM tests must pass
3. No unintended breaking changes in DEM behavior/contracts
4. Any schema/API change must be documented and tested

## 11. Rollback Strategy

### Backup / Snapshot
1. Before any schema change: full backup of `agent_memory` table
2. Snapshot of current schema
3. Snapshot of current data

### Migration
1. Execute migration plan
2. Verify each step

### Verification
1. Verify new schema correct
2. Verify data integrity
3. Verify isolation rules enforced

### Restore Procedure
1. Restore `agent_memory` from backup
2. Verify original schema restored
3. Verify original data intact
4. No data loss confirmed

### Acceptance
- Backup/snapshot exists ✅
- Migration completed ✅
- Verification passed ✅
- Restore tested ✅
- No data loss ✅

## 12. Acceptance Criteria

| # | Acceptance Criterion | Verification Method |
|---|---------------------|---------------------|
| AC-MEM-1 | Production schema has `user_id NOT NULL` | Schema inspection |
| AC-MEM-2 | All production memory records have valid `user_id` | Database query |
| AC-MEM-3 | `memory.user_id == session.owner.user_id` invariant enforced | Database constraint + application validation |
| AC-MEM-4 | No cross-user memory access possible | Cross-user isolation tests |
| AC-MEM-5 | Legacy records migrated or quarantined | Migration report |
| AC-MEM-6 | No orphaned records in production memory | Database query |
| AC-MEM-7 | No memory operation possible without `user_id` | Code review + tests |
| AC-MEM-8 | Backup/snapshot exists before migration | File verification |
| AC-MEM-9 | Restore procedure tested successfully | Restore test + data integrity check |
| AC-MEM-10 | Privacy/security verification passed | Privacy review |
| AC-MEM-11 | Governance approval obtained | Governance record |

## 13. Privacy/Security Verification

### Privacy Requirements
1. No memory leakage between users
2. No memory leakage between sessions of different users
3. Orphaned records not exposed in production
4. Audit trail for all memory operations

### Security Requirements
1. `user_id` validated against `users` table
2. FOREIGN KEY constraint enforced
3. Ownership invariant enforced (`memory.user_id == session.user_id`)
4. No SQL injection vectors in new queries
5. Access control at query level

### Verification Steps
1. Penetration test: attempt cross-user memory access
2. Code review: verify all queries filter by `user_id`
3. Database audit: verify no NULL `user_id` in production
4. Ownership invariant test: verify `memory.user_id == session.user_id`
5. Privacy review: confirm compliance with data isolation requirements

## 14. Evidence Required for Closure

1. **Migration Report:**
   - Total legacy records count
   - Eligible records count
   - Migrated records count
   - Orphaned records count
   - Quarantine records count
   - Governance decision on orphaned records

2. **Test Results:**
   - Unit tests pass
   - Integration tests pass
   - Cross-user isolation tests pass
   - Ownership invariant tests pass
   - Regression tests pass

3. **Verification Evidence:**
   - Schema inspection showing `user_id NOT NULL`
   - Database query showing no NULL `user_id` in production
   - Code review confirming all queries use `user_id`
   - Ownership invariant verification

4. **Governance Evidence:**
   - Approval for orphaned record disposition
   - Privacy review sign-off
   - Security review sign-off

## 15. Governance Checkpoints

| Checkpoint | Gate | Decision |
|------------|------|----------|
| Schema Design Review | GATE-MEM-A | Approve/reject schema changes |
| Ownership Invariant Review | GATE-MEM-B | Approve invariant enforcement mechanism |
| Legacy Migration Strategy Review | GATE-MEM-C | Approve orphaned record handling |
| Test Strategy Review | GATE-MEM-D | Approve test coverage |
| Implementation Plan Review | GATE-MEM-E | Approve execution plan |
| Privacy/Security Review | GATE-MEM-F | Approve for production |
| Final Closure | GATE-MEM-G | Close finding |

## 16. Implementation Authorization Boundary

- **هذه الخطة معتمدة للتخطيط فقط.**
- **التنفيذ يحتاج Authorization منفصل.**
- **نجاح تنفيذ الخطة يحتاج Verification مستقل.**
- **الإغلاق يحتاج Lead Architect / Governance decision.**

لا يُسمح بـ:
- تعديل schema
- تنفيذ migration
- تعديل code
- حذف أو نقل بيانات
- Commit / Push / Merge

---

## References

| Source | Description |
|--------|-------------|
| `backend/app/core/database.py` | Current database schema (lines 750-762) |
| `backend/app/agent/memory/sqlite_provider.py` | Current memory provider implementation |
| `backend/app/agent/session/manager.py` | Session management (user_id context) |
| `CURRENT_STATUS.md` | Audit Gates B–G closures |
| `POST_AUDIT_HANDOFF.md` | Post-Audit Operating Rule |
| `POST_AUDIT_FINDINGS_VALIDATION.md` | Findings Validation report |
| Commit `fe474c398cfe2faae8ead221ebecf39b4632b490` | Final Audit Baseline |
