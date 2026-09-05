import io
import sqlite3
from unittest.mock import patch

import pytest

from app.core.database import DatabaseSession, get_db
from app.services.customer import (
    _customer_row_to_response,
    create_customer,
    delete_customer,
    get_customer,
    import_customers,
    list_customers,
    update_customer,
)
from app.schemas.customer import CustomerCreate, CustomerUpdate


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


def test_customer_row_to_response_prefers_new_name():
    row = {
        "id": 1,
        "company_name": "Legacy Co",
        "name": "New Name",
        "contact_name": "Legacy Contact",
        "contact_person": "New Contact",
        "email": "new@example.com",
        "country": "Egypt",
    }
    result = _customer_row_to_response(row)
    assert result["name"] == "New Name"
    assert result["contact_person"] == "New Contact"


def test_create_and_get_customer(tmp_path):
    db_path = str(tmp_path / "customers.db")
    _init_db(db_path)

    payload = CustomerCreate(
        name="Test Customer",
        name_en="Test Customer EN",
        contact_person="Contact",
        email="test@example.com",
        phone="01000000000",
        address="Cairo",
        city="Cairo",
        country="Egypt",
        tax_id="123",
        import_license="456",
        category="food",
        notes="notes",
    )

    with patch("app.services.customer.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        with patch("app.services.customer.log_audit"):
            result = create_customer(payload, {"id": 1})
    assert result["message"] == "Customer created successfully"
    customer_id = result["id"]

    with patch("app.services.customer.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        fetched = get_customer(customer_id)
    assert fetched["name"] == "Test Customer"
    assert fetched["country"] == "Egypt"


def test_list_customers(tmp_path):
    db_path = str(tmp_path / "customers.db")
    _init_db(db_path)

    with patch("app.services.customer.log_audit"):
        with patch("app.services.customer.get_db") as mock_get_db:
            conn1 = sqlite3.connect(db_path)
            conn1.row_factory = sqlite3.Row
            conn1.execute("PRAGMA foreign_keys = ON")
            mock_get_db.return_value = conn1
            create_customer(CustomerCreate(name="C1", email="c1@example.com", country="Egypt"), {"id": 1})

        with patch("app.services.customer.get_db") as mock_get_db:
            conn2 = sqlite3.connect(db_path)
            conn2.row_factory = sqlite3.Row
            conn2.execute("PRAGMA foreign_keys = ON")
            mock_get_db.return_value = conn2
            create_customer(CustomerCreate(name="C2", email="c2@example.com", country="Egypt"), {"id": 1})

    with patch("app.services.customer.get_db") as mock_get_db:
        conn3 = sqlite3.connect(db_path)
        conn3.row_factory = sqlite3.Row
        conn3.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn3
        with patch("app.services.base.build_list_query", return_value=("SELECT * FROM customers", [])):
            rows = list_customers()
    assert len(rows) >= 2


def test_update_customer(tmp_path):
    db_path = str(tmp_path / "customers.db")
    _init_db(db_path)

    with patch("app.services.customer.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        with patch("app.services.customer.log_audit"):
            result = create_customer(CustomerCreate(name="Old", email="old@example.com", country="Egypt"), {"id": 1})
    customer_id = result["id"]

    with patch("app.services.customer.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        with patch("app.services.customer.log_audit"):
            update_result = update_customer(customer_id, CustomerUpdate(name="New"), {"id": 1})
    assert update_result["message"] == "Customer updated successfully"


def test_delete_customer(tmp_path):
    db_path = str(tmp_path / "customers.db")
    _init_db(db_path)

    with patch("app.services.customer.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        with patch("app.services.customer.log_audit"):
            result = create_customer(CustomerCreate(name="Del", email="del@example.com", country="Egypt"), {"id": 1})
    customer_id = result["id"]

    with patch("app.services.customer.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        with patch("app.services.customer.log_audit"):
            delete_result = delete_customer(customer_id, {"id": 1})
    assert delete_result["message"] == "Customer deactivated successfully"


def test_import_customers(tmp_path):
    db_path = str(tmp_path / "customers.db")
    _init_db(db_path)

    csv_content = "name,email,phone,address,city,country,category\nC1,c1@example.com,010,addr,cai,Egypt,food\n"
    with patch("app.services.customer.get_db") as mock_get_db:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        mock_get_db.return_value = conn
        with patch("app.services.customer.log_audit"):
            result = import_customers(io.BytesIO(csv_content.encode()), "customers.csv", {"id": 1})
    assert result["count"] == 1
    assert "Imported 1 customers" in result["message"]
