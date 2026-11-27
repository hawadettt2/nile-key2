"""
SQLite -> PostgreSQL (Neon) bounded migration utility.

Reads the approved SQLite backup (read-only), creates the approved schema from
POSTGRES_SCHEMA.sql, copies all 40 tables with explicit column lists inside a
single PostgreSQL transaction, verifies schema/data/relationships, then (only
after successful verification) applies RESET_IDENTITY_SEQUENCES.sql and commits.

Safety:
- Never uses TRUNCATE / DROP / DELETE / upsert.
- Never prints the connection URL or password.
- Rolls back on any failure before commit.
- setval is applied last (sequence changes are non-transactional in PostgreSQL).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
from decimal import Decimal
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    psycopg2 = None  # type: ignore[assignment]

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_FILE = PROJECT_ROOT / ".kilo" / "plans" / "nile-key-neon-migration" / "POSTGRES_SCHEMA.sql"
SEQ_FILE = PROJECT_ROOT / ".kilo" / "plans" / "nile-key-neon-migration" / "RESET_IDENTITY_SEQUENCES.sql"

# FK-safe insertion order (all 40 tables).
TABLE_ORDER = [
    "roles", "users", "suppliers", "supplier_accreditations",
    "supplier_accreditation_crops", "customers", "hs_codes",
    "customer_source_batches", "customer_raw_records", "customer_products",
    "customer_evidence", "contacts", "addresses", "shipments",
    "shipping_providers", "shipping_parcel_templates", "shipping_labels",
    "shipping_logs", "invoices", "customs_declarations", "eta_connectors",
    "eta_logs", "eta_log_documents", "notification_templates",
    "notification_logs", "notification_preferences", "audit_logs",
    "export_workflows", "export_workflow_items", "documents", "resources",
    "knowledge_nodes", "knowledge_edges", "agent_sessions", "agent_memory",
    "agent_audit_logs", "agent_goals", "agent_plans", "token_blacklist",
    "schema_migrations",
]

# 19 foreign keys (child, child_col, parent, parent_col)
FKS = [
    ("token_blacklist", "user_id", "users", "id"),
    ("agent_sessions", "user_id", "users", "id"),
    ("agent_memory", "user_id", "users", "id"),
    ("agent_memory", "session_id", "agent_sessions", "id"),
    ("agent_audit_logs", "session_id", "agent_sessions", "id"),
    ("agent_goals", "user_id", "users", "id"),
    ("agent_goals", "session_id", "agent_sessions", "id"),
    ("agent_plans", "user_id", "users", "id"),
    ("agent_plans", "session_id", "agent_sessions", "id"),
    ("agent_plans", "goal_id", "agent_goals", "goal_id"),
    ("customer_raw_records", "batch_id", "customer_source_batches", "id"),
    ("customer_products", "customer_id", "customers", "id"),
    ("customer_products", "raw_record_id", "customer_raw_records", "id"),
    ("customer_evidence", "customer_id", "customers", "id"),
    ("customer_evidence", "raw_record_id", "customer_raw_records", "id"),
    ("eta_log_documents", "eta_log_id", "eta_logs", "id"),
    ("export_workflow_items", "workflow_id", "export_workflows", "id"),
    ("knowledge_edges", "source_node_id", "knowledge_nodes", "id"),
    ("knowledge_edges", "target_node_id", "knowledge_nodes", "id"),
]

EXPECTED_SEQ = {
    "roles": 8, "users": 1, "token_blacklist": 0, "suppliers": 163,
    "supplier_accreditations": 115, "supplier_accreditation_crops": 325,
    "customers": 1, "customer_source_batches": 1, "customer_raw_records": 1,
    "customer_products": 0, "customer_evidence": 0, "contacts": 0,
    "addresses": 0, "shipments": 0, "shipping_providers": 0,
    "shipping_parcel_templates": 0, "shipping_labels": 0, "shipping_logs": 0,
    "invoices": 0, "customs_declarations": 0, "hs_codes": 13,
    "eta_connectors": 0, "eta_logs": 0, "eta_log_documents": 0,
    "documents": 0, "resources": 18, "notification_templates": 0,
    "notification_logs": 0, "notification_preferences": 0, "audit_logs": 1,
    "export_workflows": 0, "export_workflow_items": 0, "agent_audit_logs": 2,
    "schema_migrations": 1,
}


def qident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def norm(v):
    if v is None:
        return None
    if isinstance(v, Decimal):
        return round(float(v), 6)
    if isinstance(v, float):
        return round(v, 6)
    if isinstance(v, bytes):
        return v.decode("utf-8", "replace")
    return v


def table_columns_sqlite(cur, table: str):
    cur.execute("PRAGMA table_info(%s)" % qident(table))
    return [r[1] for r in cur.fetchall()]


def pk_columns_sqlite(cur, table: str):
    cur.execute("PRAGMA table_info(%s)" % qident(table))
    rows = [r for r in cur.fetchall() if r[5]]
    rows.sort(key=lambda r: r[5])
    return [r[1] for r in rows]


def checksum(cur, table: str, cols, pkcols) -> str:
    select = ", ".join(qident(c) for c in cols)
    cur.execute("SELECT %s FROM %s" % (select, qident(table)))
    rows = cur.fetchall()
    norm_rows = [[norm(x) for x in r] for r in rows]
    idx = [cols.index(c) for c in pkcols] if pkcols else list(range(len(cols)))
    norm_rows.sort(key=lambda r: tuple("" if r[i] is None else str(r[i]) for i in idx))
    payload = json.dumps(norm_rows, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sqlite-path", required=True)
    args = ap.parse_args()

    if psycopg2 is None:
        print("RESULT ERROR psycopg2 not available")
        return 1
    url = os.environ.get("NEON_DATABASE_URL")
    if not url:
        print("RESULT ERROR NEON_DATABASE_URL missing")
        return 1

    sqlite_path = args.sqlite_path
    if not os.path.exists(sqlite_path):
        print("RESULT ERROR sqlite backup not found")
        return 1
    sha = hashlib.sha256(open(sqlite_path, "rb").read()).hexdigest()
    print("SOURCE_SHA256", sha)

    src = sqlite3.connect("file:%s?mode=ro" % sqlite_path, uri=True)
    src.execute("PRAGMA query_only=ON")
    scur = src.cursor()
    integrity = scur.execute("PRAGMA integrity_check").fetchall()
    fkcheck = scur.execute("PRAGMA foreign_key_check").fetchall()
    print("SOURCE_INTEGRITY", integrity)
    print("SOURCE_FKCHECK", fkcheck)
    if integrity != [("ok",)] or fkcheck:
        print("RESULT ROLLBACK source integrity failed")
        src.close()
        return 1

    src_tables = [r[0] for r in scur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    if len(src_tables) != 40 or set(src_tables) != set(TABLE_ORDER):
        print("RESULT ROLLBACK source table set mismatch", len(src_tables))
        src.close()
        return 1
    src_counts = {}
    for t in src_tables:
        src_counts[t] = scur.execute("SELECT COUNT(*) FROM %s" % qident(t)).fetchone()[0]

    pg = psycopg2.connect(url, connect_timeout=20)
    pg.autocommit = False
    pcur = pg.cursor()
    try:
        ddl = SCHEMA_FILE.read_text(encoding="utf-8")
        pcur.execute(ddl)

        for table in TABLE_ORDER:
            cols = table_columns_sqlite(scur, table)
            collist = ", ".join(qident(c) for c in cols)
            pcur.execute("SELECT COUNT(*) FROM %s" % qident(table))
            existing = pcur.fetchone()[0]
            if existing != 0:
                raise RuntimeError("destination table %s not empty (%d)" % (table, existing))
            if src_counts.get(table, 0) == 0:
                continue
            scur.execute("SELECT %s FROM %s" % (collist, qident(table)))
            rows = scur.fetchall()
            insert_sql = "INSERT INTO %s (%s) VALUES %%s" % (qident(table), collist)
            execute_values(pcur, insert_sql, rows, page_size=500)

        # ---- verification before commit ----
        pg_tables = [r[0] for r in pcur.execute(
            "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename") or pcur.fetchall()]
        pg_col_count = pcur.execute(
            "SELECT count(*) FROM information_schema.columns WHERE table_schema='public'") or pcur.fetchone()[0]
        pk_count = pcur.execute(
            "SELECT count(*) FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace "
            "WHERE c.contype='p' AND n.nspname='public'") or pcur.fetchone()[0]
        fk_count = pcur.execute(
            "SELECT count(*) FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace "
            "WHERE c.contype='f' AND n.nspname='public'") or pcur.fetchone()[0]
        idx_total = pcur.execute("SELECT count(*) FROM pg_indexes WHERE schemaname='public'") or pcur.fetchone()[0]
        print("VERIFY_TABLES", len(pg_tables))
        print("VERIFY_COLUMNS", pg_col_count)
        print("VERIFY_PK", pk_count)
        print("VERIFY_FK", fk_count)
        print("VERIFY_INDEXES_TOTAL", idx_total)

        if len(pg_tables) != 40 or pg_col_count != 481 or pk_count != 40 or fk_count != 19:
            raise RuntimeError("schema verification failed")

        # data counts + checksums
        mismatches = []
        for table in TABLE_ORDER:
            cols = table_columns_sqlite(scur, table)
            pkcols = pk_columns_sqlite(scur, table)
            pcur.execute("SELECT COUNT(*) FROM %s" % qident(table))
            pg_count = pcur.fetchone()[0]
            if pg_count != src_counts[table]:
                mismatches.append((table, src_counts[table], pg_count))
                continue
            if src_counts[table] == 0:
                continue
            sc = checksum(scur, table, cols, pkcols)
            pc = checksum(pcur, table, cols, pkcols)
            if sc != pc:
                mismatches.append((table, "checksum", sc[:12], pc[:12]))
        print("VERIFY_COUNT_MISMATCHES", mismatches)
        if mismatches:
            raise RuntimeError("data verification failed")

        # orphan checks
        orphans = []
        for child, ccol, parent, pcol in FKS:
            pcur.execute(
                "SELECT count(*) FROM %s c LEFT JOIN %s p ON c.%s = p.%s "
                "WHERE c.%s IS NOT NULL AND p.%s IS NULL"
                % (qident(child), qident(parent), qident(ccol), qident(pcol), qident(ccol), qident(pcol)))
            n = pcur.fetchone()[0]
            if n:
                orphans.append((child, ccol, n))
        print("VERIFY_ORPHANS", orphans)
        if orphans:
            raise RuntimeError("orphan rows detected")

        # partial index definition
        pcur.execute("SELECT indexdef FROM pg_indexes WHERE indexname='idx_suppliers_station_code'")
        row = pcur.fetchone()
        print("VERIFY_PARTIAL_INDEX", row[0] if row else None)

        # ---- sequences last (non-transactional) ----
        seq_sql = SEQ_FILE.read_text(encoding="utf-8")
        pcur.execute(seq_sql)
        seq_bad = []
        for table, expected in EXPECTED_SEQ.items():
            pcur.execute("SELECT pg_get_serial_sequence(%s, 'id')", (table,))
            seqname = pcur.fetchone()[0]
            pcur.execute("SELECT last_value, is_called FROM %s" % seqname)
            last_value, is_called = pcur.fetchone()
            want_last = max(expected, 1)
            want_called = expected > 0
            if last_value != want_last or is_called != want_called:
                seq_bad.append((table, last_value, is_called, want_last, want_called))
        print("VERIFY_SEQUENCES_BAD", seq_bad)
        if seq_bad:
            raise RuntimeError("sequence verification failed")

        pg.commit()
        print("TRANSACTION COMMIT")
    except Exception as exc:
        pg.rollback()
        print("RESULT ROLLBACK", type(exc).__name__, str(exc)[:300])
        src.close()
        return 1

    src.close()

    # post-commit read-only persistence check
    try:
        pg2 = psycopg2.connect(url, connect_timeout=20)
        pg2.autocommit = True
        c2 = pg2.cursor()
        c2.execute("SELECT count(*) FROM pg_tables WHERE schemaname='public'")
        tcount = c2.fetchone()[0]
        c2.execute("SELECT count(*) FROM information_schema.columns WHERE table_schema='public'")
        ccount = c2.fetchone()[0]
        c2.execute("SELECT count(*) FROM pg_constraint WHERE contype='f'")
        fcount = c2.fetchone()[0]
        c2.execute("SELECT count(*) FROM pg_indexes WHERE schemaname='public'")
        icount = c2.fetchone()[0]
        c2.execute("SELECT COUNT(*) FROM suppliers")
        sup = c2.fetchone()[0]
        c2.execute("SELECT COUNT(*) FROM supplier_accreditations")
        acc = c2.fetchone()[0]
        c2.execute("SELECT COUNT(*) FROM supplier_accreditation_crops")
        crops = c2.fetchone()[0]
        print("POSTCOMMIT_TABLES", tcount, "COLUMNS", ccount, "FK", fcount, "INDEXES", icount)
        print("POSTCOMMIT_SUPPLIERS", sup, "ACCREDITATIONS", acc, "CROPS", crops)
        pg2.close()
    except Exception as exc:
        print("POSTCOMMIT_ERROR", type(exc).__name__, str(exc)[:200])
        return 1

    print("MIGRATION_RESULT SUCCESS")
    return 0


if __name__ == "__main__":
    sys.exit(main())