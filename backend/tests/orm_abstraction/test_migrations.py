import sqlite3

import pytest

from app.core.migrations import MigrationRunner


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
