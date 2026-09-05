from __future__ import annotations

from typing import Any


class TableDefinition:
    def __init__(self, name: str, columns: dict[str, str], indexes: list[str] | None = None):
        self.name = name
        self.columns = columns
        self.indexes = indexes or []


class SchemaRegistry:
    """Central registry for table schemas and column definitions."""

    _instance: SchemaRegistry | None = None

    def __new__(cls) -> SchemaRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._tables: dict[str, TableDefinition] = {}
        return cls._instance

    def register_table(self, name: str, columns: dict[str, str], indexes: list[str] | None = None) -> None:
        self._tables[name] = TableDefinition(name=name, columns=columns, indexes=indexes)

    def get_table(self, name: str) -> TableDefinition | None:
        return self._tables.get(name)

    def ensure_schema(self, conn: Any, table_name: str) -> None:
        table = self._tables.get(table_name)
        if not table:
            return
        existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}
        for column, col_type in table.columns.items():
            if column not in existing:
                conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {column} {col_type}")
