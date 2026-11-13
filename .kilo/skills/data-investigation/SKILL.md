---
name: data-investigation
description: >-
  Investigate project data with evidence instead of assumptions: locate the
  live database, query it, inspect raw bytes and encodings, and prove a data
  claim before changing code. Use when a data value looks wrong, a count or
  serial does not match, Arabic text or JSON looks corrupted, or a claim about
  stored records needs verification.
---

# Data Investigation

Closes the gap between "the data looks wrong" and "here is the record, the
query, and the output that proves it."

## Notebook-first surface

The `data` agent works in a Jupyter notebook. If no notebook is active, create a
descriptive `<topic>.ipynb` in the workspace, then append and execute one
focused cell per investigation step. Preserve existing cells; after a failure,
append a diagnostic cell rather than rewriting history.

This skill is for the **investigation method**, not a replacement for the
notebook. Keep queries and their output in the notebook so the evidence travels
with the analysis.

## Step 1 — Locate the database that is actually running

Do not assume the database path. Two different databases exist in this project:

| Context | Path | Evidence |
|---|---|---|
| Host (local dev) | `sqlite:///./nile_key.db` → `backend/nile_key.db` | `backend/app/core/config.py:19`, `backend/.env.example:5` |
| Docker container | `DATABASE_URL=sqlite:////app/data/nile_key.db` | `docker-compose.yml:30` |
| Docker volume | `db-data:/app/data` | `docker-compose.yml:32` |

Consequences that must be respected:

- The host file and the container file are **different databases**. A query run
  on the host does not describe what the API serves.
- The container path is only reachable from inside the container.
- `environment:` in `docker-compose.yml:30` overrides `env_file: .env`, so the
  container always uses `/app/data/nile_key.db`.
- `docker compose down -v` deletes the `db-data` volume permanently.
- The `postgres` service (`docker-compose.yml:2-19`) is defined but is **not**
  referenced by `DATABASE_URL`. Do not treat it as the live store.

State which database you queried in every report.

## Step 2 — Query the container database the way the repo already does

The established pattern in this repo copies a script into the backend container
and runs it there (`dump_db.py:17-21`, `audit1.py:75-79`):

```bash
docker cp <local-script.py> nile-key22-backend-1:/tmp/<script>.py
docker exec nile-key22-backend-1 python /tmp/<script>.py
```

Inside that script, connect to the container path only:

```python
import sqlite3, json
c = sqlite3.connect('/app/data/nile_key.db').cursor()
```

Use the real container name (`nile-key22-backend-1` in the existing scripts).
Confirm it with `docker ps` before relying on it.

## Step 3 — Prove the claim with a query, not a guess

Every investigation ends in one of these shapes. Copy the shape that matches the
question.

**Does this value exist at all?**

```sql
SELECT id, source_serial, name FROM suppliers WHERE source_serial = '153';
```

**How many, and how are they distributed?**

```sql
SELECT COUNT(*) FROM suppliers;
SELECT facility_type, COUNT(*) FROM suppliers GROUP BY facility_type;
```

**Is the data internally consistent?**

```sql
-- duplicates
SELECT source_serial, COUNT(*) FROM suppliers
WHERE source_serial IS NOT NULL AND source_serial != ''
GROUP BY source_serial HAVING COUNT(*) > 1;

-- orphans
SELECT COUNT(*) FROM supplier_accreditations a
LEFT JOIN suppliers s ON a.supplier_id = s.id
WHERE s.id IS NULL;
```

**Why is a specific row empty?**

```sql
SELECT id, source_serial, name, phone, notes
FROM suppliers WHERE source_serial = '118';
```

These are the exact checks already used in `audit1.py:8-56` and
`audit3.py:3-9`. Reuse them before writing new SQL.

## Step 4 — Check the bytes before blaming the data

When text looks corrupted, the database is often innocent. Inspect encoding
explicitly, as `check_enc.py` does:

```python
name = row[0]
print("Raw:", repr(name))
print("Bytes:", name.encode('utf-8', errors='replace'))
print("Length:", len(name))
```

For JSON artifacts, inspect the raw file bytes rather than the parsed value
(`check_json_bytes.py`):

```python
with open("EXCEL_PARSED.json", "rb") as f:
    raw = f.read()
```

`repr()` and byte dumps distinguish three different failures that all look like
"garbled Arabic": double-encoding, escaped numeric entities (`&#1234;`), and a
file written in a non-UTF-8 encoding.

## Step 5 — Report evidence, not conclusions

A finding is only reportable when it names all three:

1. **The database** that was queried (host or container path).
2. **The query** that was run.
3. **The output** that was returned.

Never report a count, a missing record, or a corruption claim without those
three. If a step could not run, say which one and why — do not infer its result.

## Boundaries

- Read-only by default. Do not write to the database as part of investigation.
- Do not run `docker compose down -v`; it destroys `db-data`.
- Do not modify non-notebook files unless the task requires it.
- If a claim cannot be verified, report it as unverified rather than probable.