from __future__ import annotations

from typing import Any


class MigrationRunner:
    """Simple versioned migration runner for schema changes."""

    def __init__(self, conn: Any) -> None:
        self._conn = conn
        self._ensure_migrations_table()

    def _ensure_migrations_table(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._conn.commit()

    def get_current_version(self) -> str | None:
        row = self._conn.execute(
            "SELECT version FROM schema_migrations ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else None

    def run_migrations(self, migrations: list[tuple[str, str]]) -> None:
        current = self.get_current_version()
        for version, sql in migrations:
            if current and version <= current:
                continue
            self._conn.execute(sql)
            self._conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)",
                (version,),
            )
            self._conn.commit()
