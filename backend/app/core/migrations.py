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
            for statement in sql.strip().split(";"):
                statement = statement.strip()
                if not statement:
                    continue
                self._conn.execute(statement)
            self._conn.execute(
                "INSERT INTO schema_migrations (version) VALUES (?)",
                (version,),
            )
            self._conn.commit()


INITIAL_MIGRATIONS: list[tuple[str, str]] = [
    (
        "v1_schema_snapshot",
        """
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_en TEXT,
            contact_person TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            country TEXT DEFAULT 'Egypt',
            tax_id TEXT,
            commercial_registry TEXT,
            certificates TEXT,
            status TEXT DEFAULT 'active',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by INTEGER
        );
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            name_en TEXT,
            contact_person TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            country TEXT NOT NULL,
            tax_id TEXT,
            import_license TEXT,
            category TEXT,
            notes TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
    ),
]
