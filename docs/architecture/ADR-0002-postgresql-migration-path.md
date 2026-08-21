# ADR-0002: Bounded PostgreSQL Migration Path

**Date:** 2026-08-21
**Status:** Accepted
**Deciders:** Engineering Team
**Governing Decision:** Governance Decision Review — Bounded PostgreSQL Migration Path (APPROVED)

---

## Context

The project roadmap (`PLAN.md`) mandates SQLite for MVP and PostgreSQL for Production.
Current runtime is SQLite-only. A bounded, reversible, and verifiable path to PostgreSQL
is required without altering the current SQLite runtime or executing any data migration
in this phase.

---

## Decision

Adopt a bounded PostgreSQL migration path that adds PostgreSQL as a first-class
infrastructure target while keeping SQLite as the unchanged current runtime.

This decision does **not** execute any migration. It only prepares the path for a
future, explicitly approved migration window.

---

## Scope (Approved)

1. **Docker / Docker Compose**
   - Add `postgres` service to `docker-compose.yml`.
   - Add `postgres-data` named volume.
   - Add `pg_isready` healthcheck.
   - Mount `backend/scripts/init.sql` for first-run initialization.
   - Environment variables sourced from `.env` (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`).

2. **PostgreSQL Initialization**
   - `backend/scripts/init.sql`: timezone, optional extensions, no hardcoded secrets.
   - `backend/scripts/init_postgres_schema.sql`: creates all application tables in
     PostgreSQL syntax for fresh-database setup.

3. **Migration / Data Transition Mechanism**
   - `backend/scripts/migrate_sqlite_to_postgres.py`: bounded, verifiable utility.
   - Supports `--dry-run`, `--verify`, and explicit source/target arguments.
   - Does **not** run automatically. Must be invoked explicitly during an approved migration window.

4. **Data Integrity Verification**
   - Row count comparison per table.
   - SHA-256 checksum of exported row tuples.
   - Referential integrity preserved by ordered table migration and `TRUNCATE ... CASCADE`.

5. **Alembic Compatibility / Verification**
   - `backend/requirements.txt` includes `psycopg2-binary==2.9.9`.
   - `backend/alembic/versions/0f82a20f2bb7_legacy_cleanup.py` updated so
     `_drop_standard_columns()` and `_add_standard_columns()` are idempotent
     (wrap drops/adds in `try/except`), allowing `alembic upgrade head` to pass
     on a fresh PostgreSQL database initialized with the new schema.
   - `backend/alembic/env.py` already reads `DATABASE_URL` from settings; no change needed
     for PostgreSQL URLs.

6. **Rollback Procedure**
   - Revert `DATABASE_URL` to SQLite in `.env`.
   - Restart backend service.
   - PostgreSQL data remains in `postgres-data` volume for inspection; destroy volume
     only after confirming SQLite integrity.

7. **Documentation**
   - This ADR records the decision, path, verification steps, and rollback.

---

## Out of Scope (This Phase)

- Executing migration on current production data.
- Changing `DATABASE_URL` default from SQLite.
- Modifying `backend/app/core/database.py` or business logic.
- Database redesign.
- Provider changes, portfolio changes, coverage score changes.
- WTO ePing actions.
- Re-opening G1.
- Creating new Work Packages or commits.

---

## Implementation Summary

### Files Modified

| File | Change |
|------|--------|
| `docker-compose.yml` | Added `postgres` service, `postgres-data` volume, healthcheck, `init.sql` mount. |
| `.env` | Added `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`; `DATABASE_URL` remains SQLite. |
| `backend/.env.example` | Added commented PostgreSQL variables. |
| `backend/requirements.txt` | Added `psycopg2-binary==2.9.9`. |
| `backend/alembic/versions/0f82a20f2bb7_legacy_cleanup.py` | Made `_drop_standard_columns` and `_add_standard_columns` idempotent for fresh PostgreSQL databases. |

### Files Created

| File | Purpose |
|------|---------|
| `backend/scripts/init.sql` | PostgreSQL first-run initialization (timezone, extensions). |
| `backend/scripts/init_postgres_schema.sql` | Creates all application tables in PostgreSQL syntax. |
| `backend/scripts/migrate_sqlite_to_postgres.py` | Bounded migration utility with dry-run and verification. |

---

## Verification Procedure

### Prerequisites

```bash
# 1. Ensure PostgreSQL driver is installed
pip install psycopg2-binary==2.9.9

# 2. Start PostgreSQL service
docker compose up -d postgres

# 3. Wait for healthcheck
docker compose ps postgres
```

### Alembic Compatibility Test

```bash
# Create a test database URL
export DATABASE_URL=postgresql://nilekey:change-me-in-local-env@localhost:5432/nilekey_test

# Initialize schema (fresh database)
psql -U nilekey -d nilekey_test -f backend/scripts/init_postgres_schema.sql

# Run Alembic migrations
cd backend && alembic upgrade head

# Expected: all migrations apply without error
# Expected output: "Running upgrade 9f6e6d58ca0f -> 0f82a20f2bb7, legacy_cleanup"
# Expected output: "Running upgrade 0f82a20f2bb7 -> bdab744e83e3, legacy_cleanup_fix"
```

### Migration Utility Test (Dry Run)

```bash
# Create a temporary SQLite sample database
python -c "
import sqlite3, random
conn = sqlite3.connect('/tmp/sample.sqlite')
conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT, full_name TEXT)')
conn.execute('INSERT INTO users VALUES (1, \"a@b.com\", \"Test\")')
conn.commit()
conn.close()
"

# Dry run
python backend/scripts/migrate_sqlite_to_postgres.py \
  --sqlite-path /tmp/sample.sqlite \
  --pg-url postgresql://nilekey:change-me-in-local-env@localhost:5432/nilekey_test \
  --dry-run

# Expected: dry run prints counts and checksums without writing to PostgreSQL
```

### Data Integrity Verification

```bash
# Actual migration (sample database only)
python backend/scripts/migrate_sqlite_to_postgres.py \
  --sqlite-path /tmp/sample.sqlite \
  --pg-url postgresql://nilekey:change-me-in-local-env@localhost:5432/nilekey_test \
  --verify

# Expected: PASS for all tables with matching row counts and checksums
```

---

## Rollback Procedure

If the migration fails or needs to be aborted:

1. **Stop PostgreSQL service**
   ```bash
   docker compose stop postgres
   ```

2. **Revert `DATABASE_URL` to SQLite** in `.env`:
   ```
   DATABASE_URL=sqlite:///./data/nile_key.db
   ```

3. **Restart backend**
   ```bash
   docker compose up -d backend
   ```

4. **Verify SQLite integrity**
   ```bash
   curl http://localhost:8000/health
   ```

5. **Inspect PostgreSQL data** (optional, before destroying volume):
   ```bash
   docker compose up -d postgres
   docker compose exec postgres psql -U nilekey -d nilekey -c "SELECT COUNT(*) FROM users;"
   ```

6. **Destroy PostgreSQL volume** only after confirming SQLite is healthy:
   ```bash
   docker compose down -v
   ```

---

## Constraints

- **Default `DATABASE_URL` remains SQLite:** `sqlite:///./data/nile_key.db`
- **Current SQLite database is untouched** during this phase.
- **No automatic migration** occurs on startup or deployment.
- **No business logic changes** in this phase.

---

## Consequences

- ✅ PostgreSQL is available as a first-class production target.
- ✅ Migration path is documented, bounded, and verifiable.
- ✅ Rollback is straightforward because SQLite remains the default runtime.
- ✅ Existing SQLite data is not touched.
- ⚠️ A future explicit decision and migration window are still required to switch runtime.

---

*Related: PLAN.md Section 3.1, Governance Decision Review — Bounded PostgreSQL Migration Path*
*Decided by: Implementation on 2026-08-21*
