"""Focused tests for insert_returning_id (Phase 3A).

Uses an isolated temporary SQLite database and a fake PostgreSQL connection.
Never uses NEON_DATABASE_URL and never connects to an external service.
"""

import os

import pytest

os.environ.setdefault("SECRET_KEY", "test-secret-key-0123456789abcdef0123456789abcdef")

from app.core import db_adapter  # noqa: E402
from app.core.database import (  # noqa: E402
    DatabaseSession,
    insert_returning_id,
)


def _sqlite_url(path) -> str:
    return "sqlite:///%s" % path


def _make_sqlite_conn(path):
    conn = db_adapter.create_connection(_sqlite_url(path))
    conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
    conn.commit()
    return conn


class _FakePGCursor:
    description = (("id",),)
    rowcount = 1

    def __init__(self, row=(42,)):
        self.executed = []
        self._row = row

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return self._row

    def close(self):
        pass


class _FakePGConnection:
    backend = "postgres"

    def __init__(self, row=(42,)):
        self.commits = 0
        self.rollbacks = 0
        self.closes = 0
        self.cur = _FakePGCursor(row)

    def cursor(self):
        return self.cur

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closes += 1


def test_sqlite_returns_id_and_does_not_commit(tmp_path):
    conn = _make_sqlite_conn(tmp_path / "a.db")
    try:
        new_id = insert_returning_id(conn, "INSERT INTO t (name) VALUES (?)", ("a",))
        assert new_id == 1

        # No auto-commit: rollback removes the row.
        conn.rollback()
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0

        new_id2 = insert_returning_id(conn, "INSERT INTO t (name) VALUES (?)", ("b",))
        conn.commit()
        assert new_id2 == 1
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1
    finally:
        conn.close()


def test_postgres_appends_returning_and_extracts_id():
    fake = _FakePGConnection((42,))
    conn = db_adapter.ConnectionProxy(fake)

    new_id = insert_returning_id(conn, "INSERT INTO t (name) VALUES (?)", ("x",))

    assert new_id == 42
    query, params = fake.cur.executed[0]
    assert query.endswith("RETURNING id")
    assert "%s" in query
    assert "?" not in query
    assert params == ("x",)
    assert fake.commits == 0
    assert fake.rollbacks == 0
    assert fake.closes == 0


def test_postgres_custom_pk_column():
    fake = _FakePGConnection((7,))
    conn = db_adapter.ConnectionProxy(fake)

    new_id = insert_returning_id(
        conn, "INSERT INTO t (goal_id) VALUES (?)", ("g",), "goal_id"
    )

    assert new_id == 7
    assert fake.cur.executed[0][0].endswith("RETURNING goal_id")


def test_invalid_pk_column_is_rejected(tmp_path):
    conn = _make_sqlite_conn(tmp_path / "bad.db")
    try:
        with pytest.raises(ValueError):
            insert_returning_id(
                conn, "INSERT INTO t (name) VALUES (?)", ("x",), "id; DROP TABLE t"
            )
        with pytest.raises(ValueError):
            insert_returning_id(conn, "INSERT INTO t (name) VALUES (?)", ("x",), "")
    finally:
        conn.close()


def test_database_session_insert_uses_helper_without_commit(tmp_path):
    conn = _make_sqlite_conn(tmp_path / "s.db")
    try:
        session = DatabaseSession(conn)
        new_id = session.insert("t", {"name": "x"})
        assert new_id == 1

        conn.rollback()
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0

        new_id2 = session.insert("t", {"name": "y"})
        conn.commit()
        assert new_id2 == 1
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1
    finally:
        conn.close()