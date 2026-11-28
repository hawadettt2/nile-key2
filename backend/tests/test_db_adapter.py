"""Focused tests for the Phase-1 database adapter.

These tests use an isolated temporary SQLite database only. They never use
NEON_DATABASE_URL and never connect to PostgreSQL or any external service.
"""

import os
import sqlite3

import pytest

os.environ.setdefault("SECRET_KEY", "test-secret-key-0123456789abcdef0123456789abcdef")

from app.core import db_adapter  # noqa: E402
from app.core.database import DatabaseSession, execute_update  # noqa: E402


def _sqlite_url(path) -> str:
    return "sqlite:///%s" % path


def test_translate_basic_placeholders():
    sql = "SELECT * FROM t WHERE a = ? AND b = ?"
    assert db_adapter.translate_query(sql, db_adapter.POSTGRES) == (
        "SELECT * FROM t WHERE a = %s AND b = %s"
    )


def test_translate_preserves_literals_and_comments():
    sql = "SELECT '?' AS a, \"?\" AS b FROM t -- ?\n/* ? */ WHERE c = ?"
    out = db_adapter.translate_query(sql, db_adapter.POSTGRES)
    assert out.count("%s") == 1
    assert "'?'" in out
    assert '"?"' in out
    assert "-- ?" in out
    assert "/* ? */" in out


def test_translate_preserves_dollar_quoted():
    sql = "SELECT $$?$$ AS a WHERE b = ?"
    out = db_adapter.translate_query(sql, db_adapter.POSTGRES)
    assert "$$?$$" in out
    assert out.endswith("%s")


def test_translate_sqlite_is_identity():
    sql = "SELECT ?"
    assert db_adapter.translate_query(sql, db_adapter.SQLITE) == sql


def test_sqlite_row_name_and_index_access(tmp_path):
    conn = db_adapter.create_connection(_sqlite_url(tmp_path / "rows.db"))
    try:
        conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        conn.commit()
        cur = conn.execute("INSERT INTO t (name) VALUES (?)", ("alpha",))
        assert cur.lastrowid == 1
        conn.commit()

        row = conn.execute("SELECT id, name FROM t").fetchone()
        assert isinstance(row, sqlite3.Row)
        assert row["name"] == "alpha"
        assert row[0] == 1
        assert row[1] == "alpha"
    finally:
        conn.close()


def test_sqlite_transaction_commit_and_rollback(tmp_path):
    conn = db_adapter.create_connection(_sqlite_url(tmp_path / "tx.db"))
    try:
        conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        conn.commit()

        conn.execute("INSERT INTO t (name) VALUES (?)", ("rollback",))
        conn.rollback()
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0

        conn.execute("INSERT INTO t (name) VALUES (?)", ("commit",))
        conn.commit()
        assert conn.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 1
    finally:
        conn.close()


def test_execute_update_sqlite(tmp_path):
    path = tmp_path / "eu.db"
    conn = db_adapter.create_connection(_sqlite_url(path))
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, updated_at TEXT)")
    conn.execute("INSERT INTO users (id, name) VALUES (?, ?)", (1, "old"))
    conn.commit()
    conn.close()

    class Model:
        def model_dump(self, exclude_unset=True):
            return {"name": "new"}

    conn = db_adapter.create_connection(_sqlite_url(path))
    updated = execute_update(conn, "users", 1, Model())
    assert updated is True

    conn2 = db_adapter.create_connection(_sqlite_url(path))
    try:
        row = conn2.execute("SELECT name FROM users WHERE id = ?", (1,)).fetchone()
        assert row["name"] == "new"
    finally:
        conn2.close()


def test_database_session_sqlite(tmp_path):
    conn = db_adapter.create_connection(_sqlite_url(tmp_path / "s.db"))
    try:
        conn.execute("CREATE TABLE t (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
        conn.commit()
        session = DatabaseSession(conn)

        new_id = session.insert("t", {"name": "x"})
        assert new_id == 1
        assert session.update("t", 1, {"name": "y"}) is True
        assert session.fetch_one("SELECT name FROM t WHERE id = ?", (1,))["name"] == "y"

        with session.transaction():
            session.insert("t", {"name": "z"})
        assert session.fetch_all("SELECT name FROM t ORDER BY id")[1]["name"] == "z"
    finally:
        conn.close()


class _FakeCursor:
    description = None
    rowcount = 1

    def __init__(self):
        self.queries = []

    def execute(self, query, params=None):
        self.queries.append((query, params))

    def close(self):
        pass


def test_postgres_proxy_translates_and_lastrowid_not_invented():
    fake = _FakeCursor()
    proxy = db_adapter.CursorProxy(fake, db_adapter.POSTGRES)
    proxy.execute("SELECT * FROM t WHERE id = ?", (7,))
    assert fake.queries[0][0] == "SELECT * FROM t WHERE id = %s"

    with pytest.raises(NotImplementedError):
        _ = proxy.lastrowid


def test_row_compat_name_and_index():
    row = db_adapter.RowCompat((10, "n"), ("id", "name"))
    assert row["id"] == 10
    assert row[0] == 10
    assert row["name"] == "n"
    assert row[1] == "n"
    assert row.keys() == ["id", "name"]


# ---------------------------------------------------------------------------
# Connection context manager (ConnectionProxy)
# ---------------------------------------------------------------------------

class FakeConnection:
    def __init__(self):
        self.commits = 0
        self.rollbacks = 0
        self.closes = 0

    def cursor(self):
        return _FakeCursor()

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closes += 1


def test_connection_proxy_context_commits_on_success():
    fake = FakeConnection()
    proxy = db_adapter.ConnectionProxy(fake)
    with proxy as entered:
        assert entered is proxy
    assert fake.commits == 1
    assert fake.rollbacks == 0
    assert fake.closes == 0


def test_connection_proxy_context_rolls_back_on_exception():
    fake = FakeConnection()
    proxy = db_adapter.ConnectionProxy(fake)
    with pytest.raises(ValueError):
        with proxy:
            raise ValueError("boom")
    assert fake.rollbacks == 1
    assert fake.commits == 0
    assert fake.closes == 0


def test_connection_proxy_context_does_not_close():
    fake = FakeConnection()
    proxy = db_adapter.ConnectionProxy(fake)
    with proxy:
        pass
    assert fake.closes == 0


# ---------------------------------------------------------------------------
# Literal percent handling
# ---------------------------------------------------------------------------

def test_translate_percent_with_params():
    sql = "SELECT * FROM t WHERE name LIKE '%x%' AND id = ?"
    out = db_adapter.translate_query(sql, db_adapter.POSTGRES, has_params=True)
    assert "LIKE '%%x%%'" in out
    assert out.endswith("id = %s")
    assert "%%s" not in out


def test_translate_percent_without_params_is_unchanged():
    sql = "SELECT '%' AS p -- %\n/* % */"
    assert db_adapter.translate_query(sql, db_adapter.POSTGRES, has_params=False) == sql


def test_translate_percent_and_question_in_literals_and_comments():
    sql = "SELECT '?' AS a, \"?\" AS b, '%' AS c -- ? %\n/* ? % */ WHERE d = ?"
    out = db_adapter.translate_query(sql, db_adapter.POSTGRES, has_params=True)
    assert out.count("%s") == 1
    assert "'?'" in out
    assert '"?"' in out
    assert "'%%'" in out
    assert "-- ? %%" in out
    assert "/* ? %% */" in out
    assert out.endswith("d = %s")


def test_generated_percent_s_is_not_doubled():
    out = db_adapter.translate_query("SELECT ?", db_adapter.POSTGRES, has_params=True)
    assert out == "SELECT %s"
    assert "%%s" not in out


_MISSING = object()


class RecordingCursor:
    description = None
    rowcount = 0

    def __init__(self):
        self.calls = []

    def execute(self, query, params=_MISSING):
        self.calls.append((query, params))

    def close(self):
        pass


def test_cursor_proxy_no_params_calls_without_parameter_sequence():
    cur = RecordingCursor()
    proxy = db_adapter.CursorProxy(cur, db_adapter.POSTGRES)

    proxy.execute("SELECT 1")
    assert cur.calls[0][1] is _MISSING

    proxy.execute("SELECT * FROM t WHERE name LIKE '%x%' AND id = ?", (5,))
    query, params = cur.calls[1]
    assert query == "SELECT * FROM t WHERE name LIKE '%%x%%' AND id = %s"
    assert params == (5,)