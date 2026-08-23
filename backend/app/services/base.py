import json
from contextlib import contextmanager
from datetime import datetime
from typing import Any

from app.core.database import get_db, execute_update


@contextmanager
def connection():
    """Provide a managed SQLite connection for service-layer use."""
    conn = get_db()
    try:
        yield conn
    except Exception:
        try:
            conn.rollback()
        except Exception:
            pass
        raise
    finally:
        conn.close()


def build_list_query(
    table: str,
    filters: dict[str, Any] | None = None,
    search_fields: list[str] | None = None,
    search: str | None = None,
    order_by: str = "created_at DESC",
    limit: int = 100,
    offset: int = 0,
) -> tuple[str, list[Any]]:
    """Build a parameterized list query for the given table."""
    query = f"SELECT * FROM {table} WHERE 1=1"
    params: list[Any] = []
    if search and search_fields:
        like = f"%{search}%"
        clauses = [f"{field} LIKE ?" for field in search_fields]
        query += " AND (" + " OR ".join(clauses) + ")"
        params.extend([like] * len(search_fields))
    if filters:
        for field, value in filters.items():
            if value is not None:
                query += f" AND {field} = ?"
                params.append(value)
    query += f" ORDER BY {order_by} LIMIT ? OFFSET ?"
    params.extend([limit, offset])
    return query, params


def parse_json(value: str | None, default=None):
    """Safely parse a JSON string from a database row."""
    if default is None:
        default = {}
    if not value:
        return default
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return default
    return value


def dumps_json(value):
    """Safely serialize a value to a JSON string for database storage."""
    return json.dumps(value) if value else "{}"


def now_iso() -> str:
    """Return the current UTC timestamp as an ISO-8601 string."""
    return datetime.utcnow().isoformat()
