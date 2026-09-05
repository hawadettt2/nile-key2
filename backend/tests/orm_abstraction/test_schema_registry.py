import sqlite3

import pytest

from app.core.schema_registry import SchemaRegistry


def _make_registry():
    return SchemaRegistry()


def test_register_and_get_table():
    registry = _make_registry()
    registry.register_table("items", {"name": "TEXT", "value": "REAL"}, indexes=["idx_items_name"])
    table = registry.get_table("items")
    assert table is not None
    assert table.columns["name"] == "TEXT"
    assert table.indexes == ["idx_items_name"]


def test_get_table_missing_returns_none():
    registry = _make_registry()
    assert registry.get_table("missing") is None


def test_ensure_schema_adds_missing_columns(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()

    registry = _make_registry()
    registry.register_table("items", {"value": "REAL", "notes": "TEXT"})
    registry.ensure_schema(conn, "items")

    columns = {row[1] for row in conn.execute("PRAGMA table_info(items)").fetchall()}
    assert "value" in columns
    assert "notes" in columns
    assert "name" in columns
    conn.close()


def test_ensure_schema_is_idempotent(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()

    registry = _make_registry()
    registry.register_table("items", {"value": "REAL"})
    registry.ensure_schema(conn, "items")
    registry.ensure_schema(conn, "items")
    columns = {row[1] for row in conn.execute("PRAGMA table_info(items)").fetchall()}
    assert "value" in columns
    conn.close()


def test_ensure_schema_skips_unregistered_table(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS other_table (id INTEGER PRIMARY KEY)")
    conn.commit()

    registry = _make_registry()
    registry.register_table("items", {"value": "REAL"})
    registry.ensure_schema(conn, "other_table")
    columns = {row[1] for row in conn.execute("PRAGMA table_info(other_table)").fetchall()}
    assert columns == {"id"}
    conn.close()
