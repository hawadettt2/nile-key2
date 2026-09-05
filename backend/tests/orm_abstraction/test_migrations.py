import sqlite3

import pytest

from app.core.migrations import MigrationRunner, INITIAL_MIGRATIONS


def _make_runner(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return MigrationRunner(conn), db_path


def test_get_current_version_returns_none_when_empty(tmp_path):
    runner, _ = _make_runner(tmp_path)
    assert runner.get_current_version() is None


def test_run_migrations_applies_new_migrations(tmp_path):
    runner, _ = _make_runner(tmp_path)
    migrations = [
        ("v1", "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY)"),
        ("v2", "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY)"),
    ]
    runner.run_migrations(migrations)
    assert runner.get_current_version() == "v2"


def test_run_migrations_is_idempotent(tmp_path):
    runner, _ = _make_runner(tmp_path)
    migrations = [
        ("v1", "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY)"),
    ]
    runner.run_migrations(migrations)
    runner.run_migrations(migrations)
    assert runner.get_current_version() == "v1"


def test_run_migrations_skips_already_applied(tmp_path):
    runner, _ = _make_runner(tmp_path)
    runner.run_migrations([("v1", "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY)")])
    runner.run_migrations([
        ("v1", "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY)"),
        ("v2", "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY)"),
    ])
    assert runner.get_current_version() == "v2"


def test_run_migrations_creates_migrations_table(tmp_path):
    runner, db_path = _make_runner(tmp_path)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'").fetchall()
    conn.close()
    assert len(rows) == 1


def test_initial_migrations_contains_suppliers_and_customers():
    versions = [version for version, _ in INITIAL_MIGRATIONS]
    assert "v1_schema_snapshot" in versions
    sql = " ".join(sql for _, sql in INITIAL_MIGRATIONS if _ == "v1_schema_snapshot")
    assert "CREATE TABLE IF NOT EXISTS suppliers" in sql
    assert "CREATE TABLE IF NOT EXISTS customers" in sql


def test_run_initial_migrations_creates_suppliers_and_customers(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    runner = MigrationRunner(conn)
    runner.run_migrations(INITIAL_MIGRATIONS)

    suppliers = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='suppliers'").fetchone()
    customers = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='customers'").fetchone()
    assert suppliers is not None
    assert customers is not None
    assert runner.get_current_version() == "v1_schema_snapshot"
    conn.close()


def test_run_initial_migrations_is_idempotent(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    runner = MigrationRunner(conn)
    runner.run_migrations(INITIAL_MIGRATIONS)
    runner.run_migrations(INITIAL_MIGRATIONS)
    assert runner.get_current_version() == "v1_schema_snapshot"
    conn.close()
