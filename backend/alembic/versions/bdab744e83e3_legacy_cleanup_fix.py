"""legacy_cleanup_fix

Revision ID: bdab744e83e3
Revises: 0f82a20f2bb7
Create Date: 2026-07-04 16:37:02.577093
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'bdab744e83e3'
down_revision: Union[str, None] = '0f82a20f2bb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        _rebuild_invoices_without_uuid(bind)
    else:
        op.drop_column('invoices', 'uuid')


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        _rebuild_invoices_with_uuid(bind)
    else:
        op.add_column('invoices', sa.Column('uuid', sa.Text, unique=True))


def _rebuild_invoices_without_uuid(bind) -> None:
    op.execute('''
        CREATE TABLE invoices_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL,
            status TEXT DEFAULT 'draft',
            eta_status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            invoice_number TEXT,
            customer_id INTEGER,
            supplier_id INTEGER,
            shipment_id INTEGER,
            subtotal REAL,
            tax_rate REAL DEFAULT 14.0,
            tax_amount REAL,
            currency TEXT DEFAULT 'EGP',
            issue_date TIMESTAMP,
            due_date TIMESTAMP,
            items TEXT,
            notes TEXT,
            created_by INTEGER,
            updated_at TIMESTAMP,
            internal_id TEXT,
            eta_uuid TEXT
        )
    ''')
    op.execute('''
        INSERT INTO invoices_new (id, total, status, eta_status, created_at,
            invoice_number, customer_id, supplier_id, shipment_id, subtotal, tax_rate,
            tax_amount, currency, issue_date, due_date, items, notes, created_by,
            updated_at, internal_id, eta_uuid)
        SELECT id, total, status, eta_status, created_at,
            invoice_number, customer_id, supplier_id, shipment_id, subtotal, tax_rate,
            tax_amount, currency, issue_date, due_date, items, notes, created_by,
            updated_at, internal_id, eta_uuid
        FROM invoices
    ''')
    op.execute('DROP TABLE invoices')
    op.execute('ALTER TABLE invoices_new RENAME TO invoices')


def _rebuild_invoices_with_uuid(bind) -> None:
    op.execute('''
        CREATE TABLE invoices_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid TEXT UNIQUE,
            total REAL,
            status TEXT DEFAULT 'draft',
            eta_status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            invoice_number TEXT,
            customer_id INTEGER,
            supplier_id INTEGER,
            shipment_id INTEGER,
            subtotal REAL,
            tax_rate REAL DEFAULT 14.0,
            tax_amount REAL,
            currency TEXT DEFAULT 'EGP',
            issue_date TIMESTAMP,
            due_date TIMESTAMP,
            items TEXT,
            notes TEXT,
            created_by INTEGER,
            updated_at TIMESTAMP,
            internal_id TEXT,
            eta_uuid TEXT
        )
    ''')
    op.execute('''
        INSERT INTO invoices_new (id, uuid, total, status, eta_status, created_at,
            invoice_number, customer_id, supplier_id, shipment_id, subtotal, tax_rate,
            tax_amount, currency, issue_date, due_date, items, notes, created_by,
            updated_at, internal_id, eta_uuid)
        SELECT id, NULL, total, status, eta_status, created_at,
            invoice_number, customer_id, supplier_id, shipment_id, subtotal, tax_rate,
            tax_amount, currency, issue_date, due_date, items, notes, created_by,
            updated_at, internal_id, eta_uuid
        FROM invoices
    ''')
    op.execute('DROP TABLE invoices')
    op.execute('ALTER TABLE invoices_new RENAME TO invoices')
