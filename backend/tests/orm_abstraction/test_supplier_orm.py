import sqlite3
from unittest.mock import patch

import pytest

from app.core.database import DatabaseSession, get_db, init_db
from app.services.supplier import (
    _supplier_row_to_response,
    create_supplier,
    delete_supplier,
    get_supplier,
    list_suppliers,
    update_supplier,
)
from app.schemas.supplier import SupplierCreate, SupplierUpdate


def _init_db(db_path):
    import os
    import tempfile
    from app.core.config import Settings
    from unittest.mock import patch

    settings = Settings()
    settings.DATABASE_URL = f"sqlite:///{db_path}"

    with patch("app.core.database.settings", settings):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
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
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    entity_type TEXT,
                    entity_id INTEGER,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()


def test_supplier_row_to_response():
    row = {"id": 1, "name": "S", "country": None, "certificates": "[]"}
    result = _supplier_row_to_response(row)
    assert result["country"] == "Egypt"


def test_create_and_get_supplier(tmp_path):
    db_path = str(tmp_path / "suppliers.db")
    _init_db(db_path)

    payload = SupplierCreate(
        name="Test Supplier",
        name_en="Test Supplier EN",
        contact_person="Contact",
        email="test@example.com",
        phone="01000000000",
        address="Cairo",
        city="Cairo",
        country="Egypt",
        tax_id="123",
        commercial_registry="456",
        certificates=["ISO"],
        notes="notes",
    )

    with patch("app.services.supplier.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        with patch("app.services.supplier.log_audit"):
            result = create_supplier(payload, {"id": 1})
    assert result["message"] == "Supplier created successfully"
    supplier_id = result["id"]

    with patch("app.services.supplier.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        fetched = get_supplier(supplier_id)
    assert fetched["name"] == "Test Supplier"
    assert fetched["certificates"] == ["ISO"]
    assert fetched["country"] == "Egypt"


def test_list_suppliers(tmp_path):
    db_path = str(tmp_path / "suppliers.db")
    _init_db(db_path)

    with patch("app.services.supplier.log_audit"):
        with patch("app.services.supplier.get_db") as mock_get_db:
            conn1 = sqlite3.connect(db_path)
            conn1.row_factory = sqlite3.Row
            conn1.execute("PRAGMA foreign_keys = ON")
            mock_get_db.return_value = conn1
            create_supplier(SupplierCreate(name="S1", email="s1@example.com"), {"id": 1})

        with patch("app.services.supplier.get_db") as mock_get_db:
            conn2 = sqlite3.connect(db_path)
            conn2.row_factory = sqlite3.Row
            conn2.execute("PRAGMA foreign_keys = ON")
            mock_get_db.return_value = conn2
            create_supplier(SupplierCreate(name="S2", email="s2@example.com"), {"id": 1})

        with patch("app.services.supplier.get_db") as mock_get_db:
            conn3 = sqlite3.connect(db_path)
            conn3.row_factory = sqlite3.Row
            conn3.execute("PRAGMA foreign_keys = ON")
            mock_get_db.return_value = conn3
            with patch("app.services.base.build_list_query", return_value=("SELECT * FROM suppliers", [])):
                rows = list_suppliers()
    assert len(rows) >= 2


def test_update_supplier(tmp_path):
    db_path = str(tmp_path / "suppliers.db")
    _init_db(db_path)

    with patch("app.services.supplier.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        with patch("app.services.supplier.log_audit"):
            result = create_supplier(SupplierCreate(name="Old", email="old@example.com"), {"id": 1})
    supplier_id = result["id"]

    with patch("app.services.supplier.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        with patch("app.services.supplier.log_audit"):
            update_result = update_supplier(supplier_id, SupplierUpdate(name="New"), {"id": 1})
    assert update_result["message"] == "Supplier updated successfully"


def test_delete_supplier(tmp_path):
    db_path = str(tmp_path / "suppliers.db")
    _init_db(db_path)

    with patch("app.services.supplier.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        with patch("app.services.supplier.log_audit"):
            result = create_supplier(SupplierCreate(name="Del", email="del@example.com"), {"id": 1})
    supplier_id = result["id"]

    with patch("app.services.supplier.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        with patch("app.services.supplier.log_audit"):
            delete_result = delete_supplier(supplier_id, {"id": 1})
    assert delete_result["message"] == "Supplier deactivated successfully"
