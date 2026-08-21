"""legacy_cleanup

Revision ID: 0f82a20f2bb7
Revises: 9f6e6d58ca0f
Create Date: 2026-07-04 16:32:28.358308
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '0f82a20f2bb7'
down_revision: Union[str, None] = '9f6e6d58ca0f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        _drop_sqlite_columns(bind)
    else:
        _drop_standard_columns()


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'sqlite':
        _add_sqlite_columns(bind)
    else:
        _add_standard_columns()


def _drop_standard_columns() -> None:
    tables = {
        'suppliers': ['farm_code', 'governorate', 'products', 'rating'],
        'customers': ['website', 'products_of_interest', 'source', 'trust_score'],
        'shipments': ['service_name', 'label_url', 'cost', 'provider', 'pickup_address', 'delivery_address', 'parcels', 'raw_response'],
        'invoices': ['uuid', 'issuer_tax_id', 'receiver_tax_id', 'receiver_name', 'tax_total', 'raw_response', 'signed_data'],
        'customs_declarations': ['duties_estimate', 'raw_response'],
        'resources': ['tags', 'is_verified'],
    }
    for table, columns in tables.items():
        for column in columns:
            op.execute(f'ALTER TABLE {table} DROP COLUMN IF EXISTS {column}')


def _add_standard_columns() -> None:
    tables = {
        'suppliers': [
            sa.Column('farm_code', sa.Text),
            sa.Column('governorate', sa.Text),
            sa.Column('products', sa.Text),
            sa.Column('rating', sa.Float),
        ],
        'customers': [
            sa.Column('website', sa.Text),
            sa.Column('products_of_interest', sa.Text),
            sa.Column('source', sa.Text),
            sa.Column('trust_score', sa.Integer),
        ],
        'shipments': [
            sa.Column('service_name', sa.Text),
            sa.Column('label_url', sa.Text),
            sa.Column('cost', sa.Float),
            sa.Column('provider', sa.Text),
            sa.Column('pickup_address', sa.Text),
            sa.Column('delivery_address', sa.Text),
            sa.Column('parcels', sa.Text),
            sa.Column('raw_response', sa.Text),
        ],
        'invoices': [
            sa.Column('uuid', sa.Text, unique=True),
            sa.Column('issuer_tax_id', sa.Text),
            sa.Column('receiver_tax_id', sa.Text),
            sa.Column('receiver_name', sa.Text),
            sa.Column('tax_total', sa.Float),
            sa.Column('raw_response', sa.Text),
            sa.Column('signed_data', sa.Text),
        ],
        'customs_declarations': [
            sa.Column('duties_estimate', sa.Float),
            sa.Column('raw_response', sa.Text),
        ],
        'resources': [
            sa.Column('tags', sa.Text),
            sa.Column('is_verified', sa.Integer),
        ],
    }
    for table, columns in tables.items():
        for column in columns:
            try:
                op.add_column(table, column)
            except Exception:
                pass


def _drop_sqlite_columns(bind) -> None:
    tables = {
        'suppliers': ['farm_code', 'governorate', 'products', 'rating'],
        'customers': ['website', 'products_of_interest', 'source', 'trust_score'],
        'shipments': ['service_name', 'label_url', 'cost', 'provider', 'pickup_address', 'delivery_address', 'parcels', 'raw_response'],
        'invoices': ['uuid', 'issuer_tax_id', 'receiver_tax_id', 'receiver_name', 'tax_total', 'raw_response', 'signed_data'],
        'customs_declarations': ['duties_estimate', 'raw_response'],
        'resources': ['tags', 'is_verified'],
    }
    for table, columns in tables.items():
        for column in columns:
            try:
                op.execute(f'ALTER TABLE {table} DROP COLUMN {column}')
            except Exception:
                pass


def _add_sqlite_columns(bind) -> None:
    op.execute('ALTER TABLE suppliers ADD COLUMN farm_code TEXT')
    op.execute('ALTER TABLE suppliers ADD COLUMN governorate TEXT')
    op.execute('ALTER TABLE suppliers ADD COLUMN products TEXT')
    op.execute('ALTER TABLE suppliers ADD COLUMN rating REAL DEFAULT 0.0')
    op.execute('ALTER TABLE customers ADD COLUMN website TEXT')
    op.execute('ALTER TABLE customers ADD COLUMN products_of_interest TEXT')
    op.execute('ALTER TABLE customers ADD COLUMN source TEXT DEFAULT "manual"')
    op.execute('ALTER TABLE customers ADD COLUMN trust_score INTEGER DEFAULT 5')
    op.execute('ALTER TABLE shipments ADD COLUMN service_name TEXT')
    op.execute('ALTER TABLE shipments ADD COLUMN label_url TEXT')
    op.execute('ALTER TABLE shipments ADD COLUMN cost REAL')
    op.execute('ALTER TABLE shipments ADD COLUMN provider TEXT')
    op.execute('ALTER TABLE shipments ADD COLUMN pickup_address TEXT')
    op.execute('ALTER TABLE shipments ADD COLUMN delivery_address TEXT')
    op.execute('ALTER TABLE shipments ADD COLUMN parcels TEXT')
    op.execute('ALTER TABLE shipments ADD COLUMN raw_response TEXT')
    op.execute('ALTER TABLE invoices ADD COLUMN uuid TEXT UNIQUE')
    op.execute('ALTER TABLE invoices ADD COLUMN issuer_tax_id TEXT')
    op.execute('ALTER TABLE invoices ADD COLUMN receiver_tax_id TEXT')
    op.execute('ALTER TABLE invoices ADD COLUMN receiver_name TEXT')
    op.execute('ALTER TABLE invoices ADD COLUMN tax_total REAL')
    op.execute('ALTER TABLE invoices ADD COLUMN raw_response TEXT')
    op.execute('ALTER TABLE invoices ADD COLUMN signed_data TEXT')
    op.execute('ALTER TABLE customs_declarations ADD COLUMN duties_estimate REAL')
    op.execute('ALTER TABLE customs_declarations ADD COLUMN raw_response TEXT')
    op.execute('ALTER TABLE resources ADD COLUMN tags TEXT')
    op.execute('ALTER TABLE resources ADD COLUMN is_verified INTEGER DEFAULT 0')
