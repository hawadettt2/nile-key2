"""Database adapter for the SQLite -> PostgreSQL (Neon) migration.

Phase 1 (Adapter/Strangler):
- Keeps the existing facade (``get_db`` / ``get_db_connection`` /
  ``execute_update`` / ``DatabaseSession``) behaviour for SQLite.
- Adds a PostgreSQL connection path selected by ``DATABASE_URL``.
- Translates ``?`` placeholders to ``%s`` for PostgreSQL only, outside
  string literals, quoted identifiers and comments.
- Provides rows that support both name and numeric-index access.
- Does NOT create a PostgreSQL schema and does NOT change ``init_db``.

``lastrowid`` is intentionally not emulated for PostgreSQL. Consumers that
need the generated id must use ``RETURNING <column>`` explicitly (out of
scope for this phase).
"""

from __future__ import annotations

import os
import re
import sqlite3
from pathlib import Path
from typing import Any

SQLITE = "sqlite"
POSTGRES = "postgres"

_DOLLAR_TAG_RE = re.compile(r"\$[A-Za-z_0-9]*\$")


def get_backend(database_url: str) -> str:
    """Return the backend identifier for a SQLAlchemy-style URL."""
    if database_url.startswith("sqlite:///"):
        return SQLITE
    if database_url.startswith(("postgresql://", "postgres://")):
        return POSTGRES
    raise ValueError("Unsupported DATABASE_URL scheme: %r" % (database_url.split(":", 1)[0],))


def is_postgres(conn: Any) -> bool:
    """True when *conn* is an adapter PostgreSQL connection proxy."""
    return getattr(conn, "backend", None) == POSTGRES


def translate_query(sql: str, backend: str = POSTGRES, has_params: bool = False) -> str:
    """Translate SQLite ``?`` placeholders to psycopg2 ``%s``.

    Placeholders inside single-quoted strings, double-quoted identifiers,
    dollar-quoted strings and ``--`` / ``/* */`` comments are preserved.

    When *has_params* is true, literal ``%`` characters are doubled to ``%%``
    so psycopg2 does not treat them as parameter markers. The value that
    reaches PostgreSQL is still a single ``%``. The ``%s`` generated from a
    ``?`` placeholder is never doubled. When *has_params* is false, ``%`` is
    left untouched (no formatting is performed by psycopg2).
    """
    if backend != POSTGRES:
        return sql

    out: list[str] = []
    i = 0
    n = len(sql)
    state = "normal"
    dollar_tag = ""

    def emit_percent() -> None:
        out.append("%%" if has_params else "%")

    while i < n:
        ch = sql[i]

        if state == "normal":
            if ch == "'":
                state = "single"
                out.append(ch)
                i += 1
            elif ch == '"':
                state = "double"
                out.append(ch)
                i += 1
            elif ch == "-" and i + 1 < n and sql[i + 1] == "-":
                state = "line"
                out.append("--")
                i += 2
            elif ch == "/" and i + 1 < n and sql[i + 1] == "*":
                state = "block"
                out.append("/*")
                i += 2
            elif ch == "$":
                match = _DOLLAR_TAG_RE.match(sql, i)
                if match:
                    dollar_tag = match.group(0)
                    state = "dollar"
                    out.append(dollar_tag)
                    i = match.end()
                else:
                    out.append(ch)
                    i += 1
            elif ch == "?":
                out.append("%s")
                i += 1
            elif ch == "%":
                emit_percent()
                i += 1
            else:
                out.append(ch)
                i += 1

        elif state == "single":
            if ch == "%":
                emit_percent()
            else:
                out.append(ch)
            if ch == "'":
                if i + 1 < n and sql[i + 1] == "'":
                    out.append("'")
                    i += 2
                    continue
                state = "normal"
            i += 1

        elif state == "double":
            if ch == "%":
                emit_percent()
            else:
                out.append(ch)
            if ch == '"':
                state = "normal"
            i += 1

        elif state == "line":
            if ch == "%":
                emit_percent()
            else:
                out.append(ch)
            if ch == "\n":
                state = "normal"
            i += 1

        elif state == "block":
            if ch == "%":
                emit_percent()
            else:
                out.append(ch)
            if ch == "*" and i + 1 < n and sql[i + 1] == "/":
                out.append("/")
                i += 2
                state = "normal"
                continue
            i += 1

        elif state == "dollar":
            if sql.startswith(dollar_tag, i):
                out.append(dollar_tag)
                i += len(dollar_tag)
                state = "normal"
            else:
                if ch == "%":
                    emit_percent()
                else:
                    out.append(ch)
                i += 1

    return "".join(out)


class RowCompat:
    """Row supporting both string-key and numeric-index access.

    Used for PostgreSQL result sets. SQLite keeps returning ``sqlite3.Row``.
    """

    __slots__ = ("_values", "_keys")

    def __init__(self, values: tuple[Any, ...], keys: tuple[str, ...]):
        self._values = tuple(values)
        self._keys = tuple(keys)

    def __getitem__(self, key: int | str) -> Any:
        if isinstance(key, int):
            return self._values[key]
        if isinstance(key, str):
            try:
                return self._values[self._keys.index(key)]
            except ValueError:
                raise KeyError(key)
        raise TypeError("row indices must be integers or strings")

    def keys(self) -> list[str]:
        return list(self._keys)

    def values(self) -> tuple[Any, ...]:
        return self._values

    def items(self):
        return zip(self._keys, self._values)

    def dict(self) -> dict[str, Any]:
        return dict(self.items())

    def __iter__(self):
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RowCompat):
            return self._values == other._values and self._keys == other._keys
        return NotImplemented

    def __repr__(self) -> str:
        return "RowCompat(%r)" % (self.dict(),)


class CursorProxy:
    """Cursor wrapper that translates placeholders and normalises rows."""

    def __init__(self, cursor: Any, backend: str):
        self._cursor = cursor
        self.backend = backend

    def execute(self, query: str, params: Any = ()) -> "CursorProxy":
        try:
            has_params = params is not None and len(params) > 0
        except TypeError:
            has_params = params is not None
        translated = translate_query(query, self.backend, has_params)
        if has_params:
            self._cursor.execute(translated, params)
        else:
            # No params: call without a parameter sequence so psycopg2 does
            # not perform %-formatting on literal percent signs.
            self._cursor.execute(translated)
        return self

    def executemany(self, query: str, seq_of_params: Any) -> "CursorProxy":
        try:
            has_params = seq_of_params is not None and len(seq_of_params) > 0
        except TypeError:
            has_params = seq_of_params is not None
        self._cursor.executemany(translate_query(query, self.backend, has_params), seq_of_params)
        return self

    def _wrap(self, row: Any) -> Any:
        if row is None:
            return None
        keys = tuple(col[0] for col in (self._cursor.description or ()))
        return RowCompat(tuple(row), keys)

    def fetchone(self) -> Any:
        return self._wrap(self._cursor.fetchone())

    def fetchmany(self, size: int | None = None) -> list[Any]:
        rows = self._cursor.fetchmany(size) if size is not None else self._cursor.fetchmany()
        return [self._wrap(r) for r in rows]

    def fetchall(self) -> list[Any]:
        return [self._wrap(r) for r in self._cursor.fetchall()]

    def __iter__(self):
        for row in self._cursor:
            yield self._wrap(row)

    @property
    def description(self) -> Any:
        return self._cursor.description

    @property
    def rowcount(self) -> int:
        return self._cursor.rowcount

    @property
    def lastrowid(self) -> int:
        if self.backend != POSTGRES:
            return self._cursor.lastrowid
        raise NotImplementedError(
            "lastrowid is not available for PostgreSQL; use RETURNING <column> explicitly"
        )

    def close(self) -> None:
        self._cursor.close()


class ConnectionProxy:
    """Connection wrapper for PostgreSQL (SQLite returns the raw connection)."""

    backend = POSTGRES

    def __init__(self, conn: Any, backend: str = POSTGRES):
        self._conn = conn
        self.backend = backend

    def cursor(self) -> CursorProxy:
        return CursorProxy(self._conn.cursor(), self.backend)

    def execute(self, query: str, params: Any = ()) -> CursorProxy:
        cur = self.cursor()
        cur.execute(query, params)
        return cur

    def executemany(self, query: str, seq_of_params: Any) -> CursorProxy:
        cur = self.cursor()
        cur.executemany(query, seq_of_params)
        return cur

    def commit(self) -> None:
        self._conn.commit()

    def rollback(self) -> None:
        self._conn.rollback()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "ConnectionProxy":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        # Mirror psycopg2's connection context manager: commit on success,
        # roll back on exception, and never close the connection here.
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()
        return False

    def __getattr__(self, name: str) -> Any:
        return getattr(self._conn, name)


def create_connection(database_url: str, sqlite_base_dir: str | None = None) -> Any:
    """Create a connection for *database_url*.

    SQLite returns a raw ``sqlite3.Connection`` (unchanged behaviour).
    PostgreSQL returns a :class:`ConnectionProxy`.
    """
    backend = get_backend(database_url)

    if backend == SQLITE:
        db_path = database_url.replace("sqlite:///", "", 1)
        if not os.path.isabs(db_path):
            base = sqlite_base_dir or os.getcwd()
            db_path = str(Path(base) / db_path)
        conn = sqlite3.connect(db_path, check_same_thread=False, timeout=20.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    import psycopg2  # imported lazily; only needed for PostgreSQL

    conn = psycopg2.connect(database_url)
    return ConnectionProxy(conn, POSTGRES)