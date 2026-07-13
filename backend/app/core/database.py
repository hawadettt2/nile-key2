"""
إدارة قاعدة البيانات SQLite:
- إنشاء الجداول
- Seed Data (بيانات أولية)
"""

import json
import sqlite3
from datetime import datetime
from contextlib import contextmanager
from typing import Any

from app.core.config import settings


# ========== إدارة الاتصال ==========

@contextmanager
def get_db_connection():
    """
    سياق إدارة الاتصال بقاعدة البيانات
    - يفتح الاتصال تلقائياً
    - يغلقه تلقائياً حتى لو حدث خطأ
    """
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    conn = sqlite3.connect(
        db_path,
        check_same_thread=False,  # ضروري لـ FastAPI (multi-threaded)
        timeout=20.0,             # انتظار 20 ثانية قبل Timeout
    )
    conn.row_factory = sqlite3.Row  # للوصول للأعمدة بالاسم
    conn.execute("PRAGMA foreign_keys = ON")  # تفعيل المفاتيح الأجنبية
    
    try:
        yield conn
    finally:
        conn.close()


# ========== تهيئة قاعدة البيانات ==========

def get_db():
    """Return a raw SQLite connection for existing router code."""
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    conn = sqlite3.connect(
        db_path,
        check_same_thread=False,
        timeout=20.0,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def execute_update(conn, table_name: str, record_id, data, coerce_fields: dict | None = None, extra_fields: dict[str, Any] | None = None) -> bool:
    """Build SET clause from model_dump(exclude_unset=True), append updated_at, commit and close.

    Returns True if the row was updated, False if no fields were set (conn is still closed).
    """
    fields = []
    values = []
    coerce = coerce_fields or {}
    if data is not None:
        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                fields.append(f"{field} = ?")
                if field in coerce:
                    values.append(coerce[field](value))
                else:
                    values.append(value)
    if extra_fields:
        for field, value in extra_fields.items():
            fields.append(f"{field} = ?")
            values.append(value)
    if not fields:
        conn.close()
        return False
    cursor = conn.cursor()
    cursor.execute(
        f"UPDATE {table_name} SET {', '.join(fields)}, updated_at = ? WHERE id = ?",
        (*values, datetime.utcnow().isoformat(), record_id),
    )
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def init_db():
    """إنشاء الجداول وإدخال البيانات الأولية"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        _create_tables(cursor)
        _seed_data(cursor, conn)
        conn.commit()


def ensure_columns(c: sqlite3.Cursor, table_name: str, expected_columns: dict[str, str]) -> None:
    existing = {row[1] for row in c.execute(f"PRAGMA table_info({table_name})").fetchall()}
    for col, col_type in expected_columns.items():
        if col not in existing:
            c.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {col_type}")


def _ensure_users_schema(c: sqlite3.Cursor):
    ensure_columns(c, "users", {
        "username": "TEXT",
        "phone": "TEXT",
        "company": "TEXT",
        "updated_at": "TIMESTAMP"
    })


def _ensure_suppliers_schema(c: sqlite3.Cursor):
    ensure_columns(c, "suppliers", {
        "name_en": "TEXT",
        "contact_person": "TEXT",
        "country": "TEXT",
        "commercial_registry": "TEXT",
        "updated_at": "TIMESTAMP",
        "created_by": "INTEGER"
    })


def _ensure_customers_schema(c: sqlite3.Cursor):
    ensure_columns(c, "customers", {
        "name": "TEXT",
        "name_en": "TEXT",
        "contact_person": "TEXT",
        "address": "TEXT",
        "city": "TEXT",
        "tax_id": "TEXT",
        "import_license": "TEXT",
        "category": "TEXT",
        "notes": "TEXT",
        "updated_at": "TIMESTAMP",
        "created_by": "INTEGER"
    })


def _ensure_shipments_schema(c: sqlite3.Cursor):
    ensure_columns(c, "shipments", {
        "reference": "TEXT",
        "supplier_id": "INTEGER",
        "customer_id": "INTEGER",
        "origin": "TEXT",
        "destination": "TEXT",
        "service_type": "TEXT",
        "weight": "REAL",
        "weight_unit": "TEXT",
        "dimensions": "TEXT",
        "value": "REAL",
        "items_count": "INTEGER",
        "description": "TEXT",
        "eta": "TIMESTAMP",
        "customs_declaration_id": "INTEGER",
        "shipped_at": "TIMESTAMP",
        "delivered_at": "TIMESTAMP",
        "created_by": "INTEGER",
        "updated_at": "TIMESTAMP"
    })


def _ensure_invoices_schema(c: sqlite3.Cursor):
    ensure_columns(c, "invoices", {
        "invoice_number": "TEXT",
        "customer_id": "INTEGER",
        "supplier_id": "INTEGER",
        "shipment_id": "INTEGER",
        "subtotal": "REAL",
        "tax_rate": "REAL",
        "tax_amount": "REAL",
        "currency": "TEXT",
        "issue_date": "TIMESTAMP",
        "due_date": "TIMESTAMP",
        "items": "TEXT",
        "notes": "TEXT",
        "created_by": "INTEGER",
        "updated_at": "TIMESTAMP",
        "internal_id": "TEXT",
        "eta_uuid": "TEXT",
        "eta_status": "TEXT",
        "eta_submission_id": "TEXT",
        "eta_response": "TEXT",
        "eta_cancellation_reason": "TEXT",
    })


def _ensure_eta_connectors_schema(c: sqlite3.Cursor):
    ensure_columns(c, "eta_connectors", {
        "name": "TEXT",
        "client_id": "TEXT",
        "client_secret": "TEXT",
        "environment": "TEXT",
        "submission_mode": "TEXT",
        "batch_size": "INTEGER",
        "delay_in_hours": "INTEGER",
        "company_id": "INTEGER",
        "is_default": "INTEGER",
        "status": "TEXT",
        "updated_at": "TIMESTAMP",
        "created_by": "INTEGER",
    })


def _ensure_eta_logs_schema(c: sqlite3.Cursor):
    ensure_columns(c, "eta_logs", {
        "from_doctype": "TEXT",
        "submission_status": "TEXT",
        "submission_id": "TEXT",
        "eta_response": "TEXT",
        "documents": "TEXT",
    })


def _ensure_eta_log_documents_schema(c: sqlite3.Cursor):
    ensure_columns(c, "eta_log_documents", {
        "eta_log_id": "INTEGER",
        "reference_doctype": "TEXT",
        "reference_document": "INTEGER",
        "uuid": "TEXT",
        "long_id": "TEXT",
        "error": "TEXT",
        "eta_status": "TEXT",
    })


def _ensure_customs_declarations_schema(c: sqlite3.Cursor):
    ensure_columns(c, "customs_declarations", {
        "declaration_number": "TEXT",
        "hs_code_id": "INTEGER",
        "destination_country": "TEXT",
        "total_value": "REAL",
        "tax_amount": "REAL",
        "total_duties": "REAL",
        "created_by": "INTEGER",
        "updated_at": "TIMESTAMP",
        "submitted_at": "TIMESTAMP",
        "approved_at": "TIMESTAMP"
    })


def _ensure_hs_codes_schema(c: sqlite3.Cursor):
    ensure_columns(c, "hs_codes", {
        "description_ar": "TEXT",
        "restrictions": "TEXT",
        "created_at": "TIMESTAMP"
    })
    c.execute("UPDATE hs_codes SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")


def _ensure_resources_schema(c: sqlite3.Cursor):
    ensure_columns(c, "resources", {
        "title_ar": "TEXT",
        "description_ar": "TEXT",
        "resource_type": "TEXT",
        "metadata": "TEXT",
        "is_active": "INTEGER",
        "created_by": "INTEGER",
        "updated_at": "TIMESTAMP",
        "file_path": "TEXT"
    })


def _ensure_shipping_schema(c: sqlite3.Cursor):
    ensure_columns(c, "shipments", {
        "service_provider": "TEXT",
        "provider_shipment_id": "TEXT",
        "awb_number": "TEXT",
        "tracking_url": "TEXT",
        "tracking_status": "TEXT",
        "tracking_status_info": "TEXT",
        "shipment_amount": "REAL",
        "label_url": "TEXT",
        "pickup_contact_id": "INTEGER",
        "delivery_contact_id": "INTEGER",
        "pickup_address_name": "TEXT",
        "delivery_address_name": "TEXT",
        "pickup_from_type": "TEXT DEFAULT 'Company'",
        "delivery_to_type": "TEXT DEFAULT 'Customer'",
        "provider_response": "TEXT",
    })

    c.execute("""
        CREATE TABLE IF NOT EXISTS shipping_providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            provider_type TEXT NOT NULL,
            environment TEXT DEFAULT 'Pre-Production',
            enabled INTEGER DEFAULT 0,
            is_default INTEGER DEFAULT 0,
            config TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            created_by INTEGER
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS shipping_parcel_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            length REAL NOT NULL,
            width REAL NOT NULL,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS shipping_labels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shipment_id INTEGER NOT NULL,
            provider TEXT NOT NULL,
            provider_shipment_id TEXT NOT NULL,
            label_url TEXT NOT NULL,
            label_format TEXT DEFAULT 'PDF',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS shipping_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shipment_id INTEGER,
            provider TEXT NOT NULL,
            action TEXT NOT NULL,
            request_payload TEXT,
            response_payload TEXT,
            error_message TEXT,
            status_code INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def _ensure_contacts_addresses_schema(c: sqlite3.Cursor):
    c.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            mobile_no TEXT,
            gender TEXT,
            customer_id INTEGER,
            supplier_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            address_title TEXT NOT NULL,
            address_line1 TEXT NOT NULL,
            address_line2 TEXT,
            city TEXT NOT NULL,
            pincode TEXT NOT NULL,
            country TEXT NOT NULL,
            country_code TEXT,
            entity_type TEXT,
            entity_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def _ensure_notification_schema(c: sqlite3.Cursor):
    c.execute("""
        CREATE TABLE IF NOT EXISTS notification_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            variables TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS notification_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER,
            recipient TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            status TEXT NOT NULL,
            error TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS notification_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            notification_type TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)


def _ensure_documents_schema(c: sqlite3.Cursor):
    ensure_columns(c, "documents", {
        "document_type": "TEXT",
        "metadata": "TEXT",
        "file_name": "TEXT",
        "file_type": "TEXT",
        "file_size": "INTEGER",
        "entity_type": "TEXT",
        "entity_id": "INTEGER",
        "updated_at": "TIMESTAMP",
        "template_type": "TEXT"
    })


def _create_tables(c: sqlite3.Cursor):
    """إنشاء كل جداول المشروع"""
    
    # ========== جدول المستخدمين ==========
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            username TEXT UNIQUE,
            phone TEXT,
            company TEXT,
            role TEXT NOT NULL DEFAULT 'staff',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        )
    """)
    _ensure_users_schema(c)
    
    # ========== جدول الأدوار ==========
    c.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            permissions TEXT NOT NULL,
            description TEXT
        )
    """)
    
    # ========== جدول الموردين ==========
    c.execute("""
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _ensure_suppliers_schema(c)

    # ========== جدول العملاء (المستوردين) =======
    c.execute("""
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
        )
    """)
    _ensure_customers_schema(c)

    # ========== جدول الشحنات ==========
    c.execute("""
        CREATE TABLE IF NOT EXISTS shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT,
            carrier TEXT,
            status TEXT DEFAULT 'pending',
            currency TEXT,
            reference TEXT,
            supplier_id INTEGER,
            customer_id INTEGER,
            origin TEXT,
            destination TEXT,
            service_type TEXT,
            weight REAL,
            weight_unit TEXT DEFAULT 'kg',
            dimensions TEXT,
            value REAL,
            items_count INTEGER DEFAULT 1,
            description TEXT,
            eta TIMESTAMP,
            customs_declaration_id INTEGER,
            shipped_at TIMESTAMP,
            delivered_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _ensure_shipments_schema(c)
    
    c.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            customer_id INTEGER,
            supplier_id INTEGER,
            shipment_id INTEGER,
            subtotal REAL,
            tax_rate REAL DEFAULT 14.0,
            tax_amount REAL,
            total REAL,
            currency TEXT DEFAULT 'EGP',
            issue_date TIMESTAMP,
            due_date TIMESTAMP,
            status TEXT DEFAULT 'draft',
            items TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _ensure_invoices_schema(c)

    # ========== جدول موصلات ETA ==========
    c.execute("""
        CREATE TABLE IF NOT EXISTS eta_connectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            client_id TEXT NOT NULL,
            client_secret TEXT NOT NULL,
            environment TEXT DEFAULT 'Pre-Production',
            submission_mode TEXT DEFAULT 'Manual',
            batch_size INTEGER DEFAULT 10,
            delay_in_hours INTEGER DEFAULT 0,
            company_id INTEGER,
            is_default INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            created_by INTEGER
        )
    """)
    _ensure_eta_connectors_schema(c)

    # ========== جدول سجل عمليات ETA ==========
    c.execute("""
        CREATE TABLE IF NOT EXISTS eta_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_doctype TEXT NOT NULL,
            submission_status TEXT NOT NULL,
            submission_id TEXT,
            eta_response TEXT,
            documents TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _ensure_eta_logs_schema(c)

    # ========== جدول تفاصيل وثائق ETA (جدول فرعي) ==========
    c.execute("""
        CREATE TABLE IF NOT EXISTS eta_log_documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            eta_log_id INTEGER NOT NULL,
            reference_doctype TEXT,
            reference_document INTEGER,
            uuid TEXT,
            long_id TEXT,
            error TEXT,
            eta_status TEXT DEFAULT 'Submitted',
            FOREIGN KEY (eta_log_id) REFERENCES eta_logs(id)
        )
    """)
    _ensure_eta_log_documents_schema(c)

    # ========== جدول البيانات الجمركية ==========
    c.execute("""
        CREATE TABLE IF NOT EXISTS customs_declarations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            declaration_number TEXT,
            shipment_id INTEGER,
            hs_code_id INTEGER,
            origin_country TEXT DEFAULT 'EG',
            destination_country TEXT,
            total_value REAL,
            currency TEXT DEFAULT 'USD',
            status TEXT DEFAULT 'draft',
            documents TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _ensure_customs_declarations_schema(c)

    # ========== جدول أكواد HS ==========
    c.execute("""
        CREATE TABLE IF NOT EXISTS hs_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            description TEXT,
            category TEXT,
            duty_rate REAL DEFAULT 0.0,
            vat_rate REAL DEFAULT 14.0
        )
    """)
    _ensure_hs_codes_schema(c)

    # ========== جدول المستندات ==========
    c.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            type TEXT NOT NULL,
            description TEXT,
            file_path TEXT,
            template_id INTEGER,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _ensure_documents_schema(c)

    # ========== جدول الموارد ==========
    c.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            title_ar TEXT,
            description TEXT,
            description_ar TEXT,
            resource_type TEXT,
            category TEXT,
            url TEXT,
            country TEXT,
            metadata TEXT,
            is_active INTEGER DEFAULT 1,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    _ensure_resources_schema(c)
    
    _ensure_shipping_schema(c)
    _ensure_contacts_addresses_schema(c)
    _ensure_notification_schema(c)
    
    # ========== جدول سجل التدقيق ==========
    c.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            entity_type TEXT,
            entity_id INTEGER,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def _seed_data(c: sqlite3.Cursor, conn: sqlite3.Connection):
    """
    إدخال البيانات الأولية (Seed Data)
    - المستخدم الافتراضي (Owner)
    - الأدوار
    - أكواد HS
    - الموارد
    """
    
    # ===== استيراد داخلي لتجنب Circular Import =====
    from app.core.security import get_password_hash
    import os
    
    # ===== إنشاء المستخدم الافتراضي (Owner) =====
    c.execute("SELECT id, username FROM users WHERE email = ?", ("owner@nile-key.com",))
    owner_row = c.fetchone()
    if not owner_row:
        owner_password = os.environ.get("OWNER_PASSWORD")
        if not owner_password:
            raise RuntimeError(
                "OWNER_PASSWORD is not set. "
                "Set OWNER_PASSWORD environment variable before starting the application."
            )
        c.execute("""
            INSERT INTO users (email, password_hash, full_name, username, role)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "owner@nile-key.com",
            get_password_hash(owner_password),
            "Owner",
            "owner",
            "owner"
        ))
    elif not owner_row[1]:
        c.execute("UPDATE users SET username = ? WHERE email = ?", ("owner", "owner@nile-key.com"))
    
    # ===== إنشاء الأدوار =====
    roles = [
        ("owner", "all", "المالك — كل الصلاحيات بدون قيود"),
        ("manager", "users:read,users:write,suppliers:all,customers:all,shipments:all,invoices:all,documents:all,resources:all,customs:all", "المدير"),
        ("sales", "customers:read,customers:write,shipments:read,documents:read,invoices:read", "مندوب مبيعات"),
        ("admin_staff", "suppliers:read,suppliers:write,documents:all,resources:all,customs:read", "موظف إداري"),
        ("accountant", "invoices:all,documents:read,suppliers:read,customers:read", "محاسب"),
        ("logistics", "shipments:all,customs:all,suppliers:read,documents:read", "لوجستيك"),
        ("supplier", "profile:read,profile:write", "مورد"),
        ("customer", "profile:read,invoices:read,shipments:read", "عميل"),
    ]
    
    for name, permissions, description in roles:
        c.execute("SELECT id FROM roles WHERE name = ?", (name,))
        if not c.fetchone():
            c.execute("""
                INSERT INTO roles (name, permissions, description)
                VALUES (?, ?, ?)
            """, (name, permissions, description))
    
    # ===== أكواد HS للمنتجات المصرية =====
    hs_codes = [
        ("0701.90", "بطاطس طازجة أو مبردة", "خضار", 0.0, 14.0),
        ("0703.10", "بصل وكراث طازج أو مبرد", "خضار", 0.0, 14.0),
        ("0707.00", "خيار وكمثرى شائك (خيار) طازج أو مبرد", "خضار", 0.0, 14.0),
        ("0709.60", "فلفل حلو (فليفلة) طازج أو مبرد", "خضار", 0.0, 14.0),
        ("0804.50", "جوافة، مانجو ومنجوستين طازج أو مجفف", "فاكهة", 0.0, 14.0),
        ("0805.10", "برتقال طازج أو مجفف", "فاكهة", 0.0, 14.0),
        ("0805.21", "اليوسفي (ماندرين) طازج أو مجفف", "فاكهة", 0.0, 14.0),
        ("0805.50", "ليمون (ليمون حامض) طازج أو مجفف", "فاكهة", 0.0, 14.0),
        ("0806.10", "عنب طازج", "فاكهة", 0.0, 14.0),
        ("0808.10", "تفاح طازج", "فاكهة", 0.0, 14.0),
        ("0809.10", "موز طازج أو مجفف", "فاكهة", 0.0, 14.0),
        ("0810.10", "فراولة", "فاكهة", 0.0, 14.0),
        ("1211.90", "نباتات وأجزاؤها المستخدمة في الصناعات الدوائية", "زراعة", 0.0, 14.0),
    ]
    
    for code, description, category, duty_rate, vat_rate in hs_codes:
        c.execute("SELECT id FROM hs_codes WHERE code = ?", (code,))
        if not c.fetchone():
            c.execute("""
                INSERT INTO hs_codes (code, description, category, duty_rate, vat_rate, created_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (code, description, category, duty_rate, vat_rate))
    
    # ===== الموارد والفرص =====
    resources = [
        ("ITC Trade Map", "https://www.trademap.org", "منصة بيانات تجارية عالمية — إحصائيات الاستيراد والتصدير", "b2b_platform", None, "trade,data,export,statistics", 1),
        ("Egyptian Export Council", "https://www.eec.org.eg", "المجلس التصديري المصري — دعم المصدرين المصريين", "government", "Egypt", "export,government,support", 1),
        ("GAFI", "https://www.gafi.gov.eg", "الهيئة العامة للاستثمار والمناطق الحرة", "government", "Egypt", "investment,government,license", 1),
        ("GOEIC", "https://www.goeic.gov.eg", "الهيئة العامة للرقابة على الصادرات والواردات", "government", "Egypt", "export,inspection,certificate", 1),
        ("ETA Egypt", "https://invoicing.eta.gov.eg", "مصلحة الضرائب المصرية — الفاتورة الإلكترونية", "government", "Egypt", "tax,e-invoice,government", 1),
        ("Nafeza", "https://www.nafeza.gov.eg", "منظومة نافذة الجمركية المصرية", "government", "Egypt", "customs,clearance,government", 1),
        ("Alibaba B2B", "https://www.alibaba.com", "أكبر منصة B2B في العالم", "b2b_platform", None, "b2b,global,marketplace", 1),
        ("TradeKey", "https://www.tradekey.com", "منصة B2B للتصدير والاستيراد", "b2b_platform", None, "b2b,export,import", 1),
        ("Europages", "https://www.europages.com", "دليل الشركات الأوروبية B2B", "b2b_platform", "EU", "b2b,europe,directory", 1),
        ("Kompass", "https://www.kompass.com", "قاعدة بيانات الشركات العالمية", "b2b_platform", None, "b2b,database,companies", 1),
        ("Fruit Logistica", "https://www.fruitlogistica.com", "أكبر معرض عالمي للخضار والفاكهة — برلين", "trade_fair", "Germany", "fair,fruits,vegetables,berlin", 1),
        ("Gulfood", "https://www.gulfood.com", "أكبر معرض للأغذية في الشرق الأوسط — دبي", "trade_fair", "UAE", "fair,food,dubai,meat", 1),
        ("Anuga", "https://www.anuga.com", "معرض كولون الدولي للأغذية — ألمانيا", "trade_fair", "Germany", "fair,food,cologne,germany", 1),
        ("SIAL Paris", "https://www.sialparis.com", "معرض باريس الدولي للأغذية", "trade_fair", "France", "fair,food,paris,france", 1),
        ("Foodex Japan", "https://www.foodex.net", "معرض طوكيو للأغذية والمشروبات", "trade_fair", "Japan", "fair,food,tokyo,japan", 1),
        ("ICC Egypt", "https://icc-egypt.org", "الغرفة التجارية الدولية — مصر", "chamber_of_commerce", "Egypt", "chamber,trade,international", 1),
        ("Cairo Chamber", "https://www.cairochamber.org.eg", "الغرفة التجارية بالقاهرة", "chamber_of_commerce", "Egypt", "chamber,cairo,trade", 1),
        ("Alexandria Chamber", "https://www.alexcham.org", "الغرفة التجارية بالإسكندرية", "chamber_of_commerce", "Egypt", "chamber,alexandria,port", 1),
    ]
    
    for title, url, description, category, country, tags, is_verified in resources:
        c.execute("SELECT id FROM resources WHERE url = ?", (url,))
        if not c.fetchone():
            c.execute("""
                INSERT INTO resources (title, description, category, url, country, metadata, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, description, category, url, country, json.dumps({"tags": tags}) if tags else "{}", 1 if is_verified else 0))
