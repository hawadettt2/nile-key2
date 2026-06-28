import sqlite3
import os
from datetime import datetime
from app.core.config import get_settings

settings = get_settings()
DB_PATH = settings.DATABASE_URL.replace("sqlite:///", "")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH) if os.path.dirname(DB_PATH) else ".", exist_ok=True)
    conn = get_db()
    cursor = conn.cursor()

    tables = [
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL, username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL, hashed_password TEXT NOT NULL, role TEXT NOT NULL DEFAULT 'Customer',
            is_active INTEGER NOT NULL DEFAULT 1, phone TEXT, company TEXT, created_at TEXT NOT NULL, updated_at TEXT)""",
        """CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL, description TEXT, permissions TEXT NOT NULL DEFAULT '[]')""",
        """CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, name_en TEXT, contact_person TEXT,
            email TEXT, phone TEXT, address TEXT, city TEXT, country TEXT DEFAULT 'Egypt', tax_id TEXT,
            commercial_registry TEXT, certificates TEXT DEFAULT '[]', status TEXT NOT NULL DEFAULT 'active',
            notes TEXT, created_at TEXT NOT NULL, updated_at TEXT, created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id))""",
        """CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, name_en TEXT, contact_person TEXT,
            email TEXT, phone TEXT, address TEXT, city TEXT, country TEXT NOT NULL, tax_id TEXT,
            import_license TEXT, category TEXT, status TEXT NOT NULL DEFAULT 'active', notes TEXT,
            created_at TEXT NOT NULL, updated_at TEXT, created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id))""",
        """CREATE TABLE IF NOT EXISTS shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, tracking_number TEXT UNIQUE, reference TEXT,
            supplier_id INTEGER, customer_id INTEGER, origin TEXT NOT NULL, destination TEXT NOT NULL,
            carrier TEXT, service_type TEXT, status TEXT NOT NULL DEFAULT 'pending', weight REAL,
            weight_unit TEXT DEFAULT 'kg', dimensions TEXT, value REAL, currency TEXT DEFAULT 'USD',
            items_count INTEGER DEFAULT 1, description TEXT, eta TEXT, shipped_at TEXT, delivered_at TEXT,
            created_at TEXT NOT NULL, updated_at TEXT, created_by INTEGER,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (created_by) REFERENCES users(id))""",
        """CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_number TEXT UNIQUE NOT NULL, internal_id TEXT,
            eta_uuid TEXT, eta_status TEXT, customer_id INTEGER, supplier_id INTEGER, shipment_id INTEGER,
            subtotal REAL NOT NULL, tax_rate REAL DEFAULT 14.0, tax_amount REAL, total REAL NOT NULL,
            currency TEXT DEFAULT 'EGP', issue_date TEXT NOT NULL, due_date TEXT, status TEXT NOT NULL DEFAULT 'draft',
            items TEXT NOT NULL DEFAULT '[]', notes TEXT, created_at TEXT NOT NULL, updated_at TEXT, created_by INTEGER,
            FOREIGN KEY (customer_id) REFERENCES customers(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (shipment_id) REFERENCES shipments(id),
            FOREIGN KEY (created_by) REFERENCES users(id))""",
        """CREATE TABLE IF NOT EXISTS customs_declarations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, declaration_number TEXT UNIQUE, shipment_id INTEGER,
            hs_code_id INTEGER, origin_country TEXT DEFAULT 'EG', destination_country TEXT NOT NULL,
            total_value REAL, currency TEXT DEFAULT 'USD', duty_amount REAL, tax_amount REAL,
            total_duties REAL, status TEXT NOT NULL DEFAULT 'draft', documents TEXT DEFAULT '[]',
            submitted_at TEXT, approved_at TEXT, created_at TEXT NOT NULL, updated_at TEXT, created_by INTEGER,
            FOREIGN KEY (shipment_id) REFERENCES shipments(id),
            FOREIGN KEY (created_by) REFERENCES users(id))""",
        """CREATE TABLE IF NOT EXISTS hs_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, description TEXT NOT NULL,
            description_ar TEXT, category TEXT, duty_rate REAL DEFAULT 0, tax_rate REAL DEFAULT 14.0,
            restrictions TEXT, created_at TEXT NOT NULL)""",
        """CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, file_name TEXT, file_path TEXT,
            file_type TEXT, file_size INTEGER, document_type TEXT NOT NULL DEFAULT 'uploaded', template_type TEXT,
            entity_type TEXT, entity_id INTEGER, content TEXT, metadata TEXT DEFAULT '{}',
            created_at TEXT NOT NULL, updated_at TEXT, created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id))""",
        """CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, title_ar TEXT, description TEXT,
            description_ar TEXT, resource_type TEXT NOT NULL, category TEXT, url TEXT, file_path TEXT,
            country TEXT, is_active INTEGER NOT NULL DEFAULT 1, metadata TEXT DEFAULT '{}',
            created_at TEXT NOT NULL, updated_at TEXT, created_by INTEGER,
            FOREIGN KEY (created_by) REFERENCES users(id))""",
        """CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, action TEXT NOT NULL, entity_type TEXT,
            entity_id INTEGER, details TEXT, ip_address TEXT, created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id))""",
        """CREATE TABLE IF NOT EXISTS system_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT, key TEXT UNIQUE NOT NULL, value TEXT, description TEXT,
            updated_at TEXT, updated_by INTEGER)""",
    ]
    for sql in tables:
        cursor.execute(sql)

    now = datetime.utcnow().isoformat()
    roles = [
        ("Owner", "Full access", '["*"]'),
        ("Manager", "Manage teams", '["suppliers.*", "customers.*", "shipments.*", "invoices.*"]'),
        ("Sales", "Manage customers", '["customers.*", "shipments.*"]'),
        ("Admin Staff", "Admin tasks", '["documents.*", "suppliers.read", "customers.read"]'),
        ("Accountant", "Financial ops", '["invoices.*", "reports.*"]'),
        ("Logistics", "Shipping ops", '["shipments.*", "customs.*"]'),
        ("Supplier", "Supplier portal", '["suppliers.own", "shipments.read"]'),
        ("Customer", "Customer portal", '["customers.own", "shipments.read", "invoices.read"]'),
    ]
    cursor.executemany("INSERT OR IGNORE INTO roles (name, description, permissions) VALUES (?, ?, ?)", roles)

    cursor.execute("""INSERT OR IGNORE INTO users (id, email, username, full_name, hashed_password, role, is_active, created_at)
        VALUES (1, 'admin@nile-key.com', 'admin', 'System Administrator',
                '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ/I1K', 'Owner', 1, ?)""", (now,))

    hs_codes = [
        ("0703.10", "Onions", "بصل", "Vegetables", 5.0, 14.0),
        ("0707.00", "Cucumbers", "خيار", "Vegetables", 5.0, 14.0),
        ("0804.10", "Dates", "تمر", "Fruits", 2.0, 14.0),
        ("0805.10", "Oranges", "برتقال", "Fruits", 10.0, 14.0),
        ("0806.10", "Grapes", "عنب", "Fruits", 8.0, 14.0),
        ("0808.10", "Apples", "تفاح", "Fruits", 10.0, 14.0),
        ("0902.10", "Green tea", "شاي أخضر", "Beverages", 5.0, 14.0),
        ("1905.90", "Bread & pastry", "خبز", "Food", 20.0, 14.0),
        ("2009.90", "Fruit juices", "عصائر", "Beverages", 15.0, 14.0),
        ("2201.10", "Mineral waters", "مياه معدنية", "Beverages", 20.0, 14.0),
    ]
    cursor.executemany("INSERT OR IGNORE INTO hs_codes (code, description, description_ar, category, duty_rate, tax_rate, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       [(c[0], c[1], c[2], c[3], c[4], c[5], now) for c in hs_codes])

    conn.commit()
    conn.close()
    print("Database initialized successfully.")
