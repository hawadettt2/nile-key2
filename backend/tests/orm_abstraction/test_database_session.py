import sqlite3

import pytest

from app.core.database import DatabaseSession


def _make_session(tmp_path):
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            value REAL
        )
        """
    )
    conn.commit()
    return DatabaseSession(conn), db_path


def test_fetch_one_returns_none_when_empty(tmp_path):
    session, _ = _make_session(tmp_path)
    assert session.fetch_one("SELECT * FROM items WHERE id = ?", (999,)) is None


def test_fetch_one_returns_row(tmp_path):
    session, _ = _make_session(tmp_path)
    session.insert("items", {"name": "A", "value": 1.0})
    row = session.fetch_one("SELECT * FROM items WHERE name = ?", ("A",))
    assert row is not None
    assert row["name"] == "A"
    assert row["value"] == 1.0


def test_fetch_all_returns_rows(tmp_path):
    session, _ = _make_session(tmp_path)
    session.insert("items", {"name": "A", "value": 1.0})
    session.insert("items", {"name": "B", "value": 2.0})
    rows = session.fetch_all("SELECT * FROM items ORDER BY name")
    assert len(rows) == 2
    assert rows[0]["name"] == "A"
    assert rows[1]["name"] == "B"


def test_insert_returns_lastrowid(tmp_path):
    session, _ = _make_session(tmp_path)
    row_id = session.insert("items", {"name": "X", "value": 9.0})
    assert row_id == 1


def test_update_returns_true_when_row_exists(tmp_path):
    session, _ = _make_session(tmp_path)
    session.insert("items", {"name": "X", "value": 1.0})
    assert session.update("items", 1, {"value": 2.0}) is True
    row = session.fetch_one("SELECT * FROM items WHERE id = ?", (1,))
    assert row["value"] == 2.0


def test_update_returns_false_when_no_fields(tmp_path):
    session, _ = _make_session(tmp_path)
    assert session.update("items", 1, {}) is False


def test_delete_returns_true_when_row_exists(tmp_path):
    session, _ = _make_session(tmp_path)
    session.insert("items", {"name": "X", "value": 1.0})
    assert session.delete("items", 1) is True
    assert session.fetch_one("SELECT * FROM items WHERE id = ?", (1,)) is None


def test_transaction_commits_on_success(tmp_path):
    session, _ = _make_session(tmp_path)
    with session.transaction():
        session.insert("items", {"name": "T", "value": 1.0})
    rows = session.fetch_all("SELECT * FROM items")
    assert len(rows) == 1


def test_transaction_rolls_back_on_exception(tmp_path):
    session, _ = _make_session(tmp_path)
    with pytest.raises(RuntimeError):
        with session.transaction():
            session.insert("items", {"name": "T", "value": 1.0})
            raise RuntimeError("fail")
    assert session.fetch_all("SELECT * FROM items") == []
