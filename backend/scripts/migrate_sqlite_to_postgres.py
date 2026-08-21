"""
SQLite -> PostgreSQL bounded migration utility.

This script is intentionally bounded:
- It does NOT migrate the current production SQLite database automatically.
- It is a verifiable, testable mechanism intended to be run explicitly
  during the approved migration window.

Usage examples:
  # Dry run against sample databases:
  python backend/scripts/migrate_sqlite_to_postgres.py --sqlite-path /tmp/sample.sqlite --pg-url postgresql://nilekey:password@localhost:5432/nilekey_test --dry-run

  # Actual migration (after explicit approval and backup):
  python backend/scripts/migrate_sqlite_to_postgres.py --sqlite-path /tmp/sample.sqlite --pg-url postgresql://nilekey:password@localhost:5432/nilekey --verify
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from typing import Any

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    psycopg2 = None  # type: ignore[assignment]


TABLES_IN_ORDER = [
    "roles",
    "users",
    "suppliers",
    "customers",
    "hs_codes",
    "documents",
    "resources",
    "shipments",
    "invoices",
    "eta_connectors",
    "eta_logs",
    "eta_log_documents",
    "customs_declarations",
    "shipping_providers",
    "shipping_parcel_templates",
    "shipping_labels",
    "shipping_logs",
    "contacts",
    "addresses",
    "notification_templates",
    "notification_logs",
    "notification_preferences",
    "audit_logs",
    "export_workflows",
    "export_workflow_items",
    "agent_sessions",
    "agent_memory",
    "agent_audit_logs",
    "knowledge_nodes",
    "knowledge_edges",
    "token_blacklist",
]


@dataclass
class VerificationResult:
    table: str
    sqlite_count: int
    pg_count: int
    sqlite_checksum: str
    pg_checksum: str
    passed: bool


def _checksum(rows: list[tuple[Any, ...]]) -> str:
    payload = json.dumps(rows, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _fetch_all(conn: sqlite3.Connection, table: str) -> list[tuple[Any, ...]]:
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table}")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return [tuple(row[col] for col in columns) for row in [dict(zip(columns, r)) for r in rows]]


def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    return [row[1] for row in cursor.fetchall()]


def migrate(
    sqlite_path: str,
    pg_url: str,
    dry_run: bool = False,
    verify: bool = False,
) -> list[VerificationResult]:
    if psycopg2 is None:
        raise RuntimeError(
            "psycopg2 is not installed. Install it with: pip install psycopg2-binary"
        )

    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"SQLite database not found: {sqlite_path}")

    if dry_run:
        print("[DRY RUN] No data will be written to PostgreSQL.")

    sqlite_conn = sqlite3.connect(sqlite_path, check_same_thread=False)
    sqlite_conn.row_factory = sqlite3.Row

    pg_conn = psycopg2.connect(pg_url)
    pg_conn.autocommit = False
    pg_cursor = pg_conn.cursor()

    results: list[VerificationResult] = []

    try:
        for table in TABLES_IN_ORDER:
            print(f"[MIGRATE] Processing table: {table}")

            columns = _table_columns(sqlite_conn, table)
            if not columns:
                print(f"[MIGRATE] Table {table} is empty or does not exist, skipping.")
                continue

            rows = _fetch_all(sqlite_conn, table)
            sqlite_count = len(rows)
            sqlite_checksum = _checksum(rows)

            if dry_run:
                print(f"[DRY RUN] {table}: {sqlite_count} rows, checksum {sqlite_checksum[:12]}...")
                results.append(VerificationResult(
                    table=table,
                    sqlite_count=sqlite_count,
                    pg_count=0,
                    sqlite_checksum=sqlite_checksum,
                    pg_checksum="",
                    passed=False,
                ))
                continue

            if not rows:
                print(f"[MIGRATE] {table}: 0 rows, skipping insert.")
                if verify:
                    pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    pg_count = pg_cursor.fetchone()[0]
                    results.append(VerificationResult(
                        table=table,
                        sqlite_count=0,
                        pg_count=pg_count,
                        sqlite_checksum=sqlite_checksum,
                        pg_checksum="",
                        passed=pg_count == 0,
                    ))
                continue

            column_list = ", ".join(columns)
            insert_sql = f"INSERT INTO {table} ({column_list}) VALUES %s"

            # Clear destination table to allow idempotent re-runs within the same migration window.
            pg_cursor.execute(f"TRUNCATE TABLE {table} CASCADE")

            execute_values(pg_cursor, insert_sql, rows, page_size=500)

            if verify:
                pg_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                pg_count = pg_cursor.fetchone()[0]

                pg_cursor.execute(f"SELECT * FROM {table}")
                pg_rows = pg_cursor.fetchall()
                pg_checksum = _checksum([tuple(r) for r in pg_rows])

                passed = (sqlite_count == pg_count) and (sqlite_checksum == pg_checksum)
                results.append(VerificationResult(
                    table=table,
                    sqlite_count=sqlite_count,
                    pg_count=pg_count,
                    sqlite_checksum=sqlite_checksum,
                    pg_checksum=pg_checksum,
                    passed=passed,
                ))

        if not dry_run:
            pg_conn.commit()
            print("[MIGRATE] Transaction committed.")

    except Exception:
        pg_conn.rollback()
        raise
    finally:
        sqlite_conn.close()
        pg_cursor.close()
        pg_conn.close()

    return results


def print_results(results: list[VerificationResult]) -> bool:
    all_passed = True
    print("\n[VERIFICATION] Results:")
    print(f"{'Table':<30} {'SQLite':>8} {'Postgres':>10} {'Checksum Match':>16} {'Status'}")
    print("-" * 80)
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        if not r.passed:
            all_passed = False
        checksum_match = "YES" if r.sqlite_checksum == r.pg_checksum else "NO"
        print(f"{r.table:<30} {r.sqlite_count:>8} {r.pg_count:>10} {checksum_match:>16} {status}")
    print("-" * 80)
    print(f"[VERIFICATION] Overall: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bounded SQLite -> PostgreSQL migration utility."
    )
    parser.add_argument(
        "--sqlite-path",
        required=True,
        help="Path to the source SQLite database file.",
    )
    parser.add_argument(
        "--pg-url",
        required=True,
        help="PostgreSQL connection URL (e.g. postgresql://user:pass@host:5432/dbname).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect counts and checksums without writing to PostgreSQL.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Enable post-migration verification against PostgreSQL.",
    )
    args = parser.parse_args()

    try:
        results = migrate(
            sqlite_path=args.sqlite_path,
            pg_url=args.pg_url,
            dry_run=args.dry_run,
            verify=args.verify or args.dry_run,
        )
    except Exception as exc:
        print(f"[ERROR] Migration failed: {exc}")
        return 1

    if results:
        passed = print_results(results)
        return 0 if passed else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
