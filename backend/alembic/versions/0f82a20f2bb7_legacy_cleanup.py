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
    op.drop_column('suppliers', 'farm_code')
    op.drop_column('suppliers', 'governorate')
    op.drop_column('suppliers', 'products')
    op.drop_column('suppliers', 'rating')
    op.drop_column('customers', 'website')
    op.drop_column('customers', 'products_of_interest')
    op.drop_column('customers', 'source')
    op.drop_column('customers', 'trust_score')
    op.drop_column('shipments', 'service_name')
    op.drop_column('shipments', 'label_url')
    op.drop_column('shipments', 'cost')
    op.drop_column('shipments', 'provider')
    op.drop_column('shipments', 'pickup_address')
    op.drop_column('shipments', 'delivery_address')
    op.drop_column('shipments', 'parcels')
    op.drop_column('shipments', 'raw_response')
    op.drop_column('invoices', 'uuid')
    op.drop_column('invoices', 'issuer_tax_id')
    op.drop_column('invoices', 'receiver_tax_id')
    op.drop_column('invoices', 'receiver_name')
    op.drop_column('invoices', 'tax_total')
    op.drop_column('invoices', 'raw_response')
    op.drop_column('invoices', 'signed_data')
    op.drop_column('customs_declarations', 'duties_estimate')
    op.drop_column('customs_declarations', 'raw_response')
    op.drop_column('resources', 'tags')
    op.drop_column('resources', 'is_verified')


def _add_standard_columns() -> None:
    op.add_column('suppliers', sa.Column('farm_code', sa.Text))
    op.add_column('suppliers', sa.Column('governorate', sa.Text))
    op.add_column('suppliers', sa.Column('products', sa.Text))
    op.add_column('suppliers', sa.Column('rating', sa.Float))
    op.add_column('customers', sa.Column('website', sa.Text))
    op.add_column('customers', sa.Column('products_of_interest', sa.Text))
    op.add_column('customers', sa.Column('source', sa.Text))
    op.add_column('customers', sa.Column('trust_score', sa.Integer))
    op.add_column('shipments', sa.Column('service_name', sa.Text))
    op.add_column('shipments', sa.Column('label_url', sa.Text))
    op.add_column('shipments', sa.Column('cost', sa.Float))
    op.add_column('shipments', sa.Column('provider', sa.Text))
    op.add_column('shipments', sa.Column('pickup_address', sa.Text))
    op.add_column('shipments', sa.Column('delivery_address', sa.Text))
    op.add_column('shipments', sa.Column('parcels', sa.Text))
    op.add_column('shipments', sa.Column('raw_response', sa.Text))
    op.add_column('invoices', sa.Column('uuid', sa.Text, unique=True))
    op.add_column('invoices', sa.Column('issuer_tax_id', sa.Text))
    op.add_column('invoices', sa.Column('receiver_tax_id', sa.Text))
    op.add_column('invoices', sa.Column('receiver_name', sa.Text))
    op.add_column('invoices', sa.Column('tax_total', sa.Float))
    op.add_column('invoices', sa.Column('raw_response', sa.Text))
    op.add_column('invoices', sa.Column('signed_data', sa.Text))
    op.add_column('customs_declarations', sa.Column('duties_estimate', sa.Float))
    op.add_column('customs_declarations', sa.Column('raw_response', sa.Text))
    op.add_column('resources', sa.Column('tags', sa.Text))
    op.add_column('resources', sa.Column('is_verified', sa.Integer))


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
