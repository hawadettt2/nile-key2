# WP-02 Migration Infrastructure: Generic ensure_columns Helper

## Changes to backend/app/core/database.py

### 1. Add ensure_columns() helper (after line 60, before _ensure_users_schema)

```python
def ensure_columns(c: sqlite3.Cursor, table_name: str, expected_columns: dict[str, str]) -> None:
    existing = {row[1] for row in c.execute(f"PRAGMA table_info({table_name})").fetchall()}
    for col, col_type in expected_columns.items():
        if col not in existing:
            c.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {col_type}")
```

### 2. Refactor _ensure_users_schema() to use ensure_columns()

Replace existing `_ensure_users_schema()` (lines 62-75) with:

```python
def _ensure_users_schema(c: sqlite3.Cursor):
    ensure_columns(c, "users", {
        "username": "TEXT",
        "phone": "TEXT",
        "company": "TEXT",
        "updated_at": "TIMESTAMP"
    })
```

## WP-02B-H Usage Pattern

Each remaining sub-package will define its own `_ensure_<table>_schema()` calling `ensure_columns()`:

```python
def _ensure_suppliers_schema(c: sqlite3.Cursor):
    ensure_columns(c, "suppliers", {
        "name_en": "TEXT",
        "contact_person": "TEXT",
        "country": "TEXT",
        "commercial_registry": "TEXT"
    })
```

## Verification

1. Backend starts successfully (curl http://localhost:8001/health)
2. Login works (token returned)
3. Fresh DB and upgrade DB both work