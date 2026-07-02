"""Initial schema

Revision ID: 5659bcb3d3ae
Revises:
Create Date: 2026-07-02 10:31:12.809071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5659bcb3d3ae'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('email', sa.Text, unique=True, nullable=False),
        sa.Column('password_hash', sa.Text, nullable=False),
        sa.Column('full_name', sa.Text, nullable=False),
        sa.Column('username', sa.Text, unique=True, nullable=True),
        sa.Column('phone', sa.Text, nullable=True),
        sa.Column('company', sa.Text, nullable=True),
        sa.Column('role', sa.Text, nullable=False, server_default=sa.text("'staff'")),
        sa.Column('is_active', sa.Integer, nullable=False, server_default=sa.text("1")),
        sa.Column('created_at', sa.String, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('updated_at', sa.String, nullable=True),
    )
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.Text, unique=True, nullable=False),
        sa.Column('permissions', sa.Text, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
    )
    op.create_table(
        'suppliers',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('type', sa.Text, nullable=False, server_default=sa.text("'general'")),
        sa.Column('farm_code', sa.Text, nullable=True),
        sa.Column('tax_id', sa.Text, nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('city', sa.Text, nullable=True),
        sa.Column('governorate', sa.Text, nullable=True),
        sa.Column('phone', sa.Text, nullable=True),
        sa.Column('email', sa.Text, nullable=True),
        sa.Column('products', sa.Text, nullable=True),
        sa.Column('certificates', sa.Text, nullable=True),
        sa.Column('status', sa.Text, nullable=False, server_default=sa.text("'active'")),
        sa.Column('rating', sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_at', sa.String, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('name_en', sa.Text, nullable=True),
        sa.Column('contact_person', sa.Text, nullable=True),
        sa.Column('country', sa.Text, nullable=True),
        sa.Column('commercial_registry', sa.Text, nullable=True),
        sa.Column('updated_at', sa.String, nullable=True),
        sa.Column('created_by', sa.Integer, nullable=True),
    )
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('company_name', sa.Text, nullable=False),
        sa.Column('country', sa.Text, nullable=False),
        sa.Column('contact_name', sa.Text, nullable=True),
        sa.Column('email', sa.Text, nullable=True),
        sa.Column('phone', sa.Text, nullable=True),
        sa.Column('website', sa.Text, nullable=True),
        sa.Column('products_of_interest', sa.Text, nullable=True),
        sa.Column('source', sa.Text, nullable=False, server_default=sa.text("'manual'")),
        sa.Column('trust_score', sa.Integer, nullable=False, server_default=sa.text("5")),
        sa.Column('status', sa.Text, nullable=False, server_default=sa.text("'active'")),
        sa.Column('created_at', sa.String, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('name', sa.Text, nullable=True),
        sa.Column('name_en', sa.Text, nullable=True),
        sa.Column('contact_person', sa.Text, nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('city', sa.Text, nullable=True),
        sa.Column('tax_id', sa.Text, nullable=True),
        sa.Column('import_license', sa.Text, nullable=True),
        sa.Column('category', sa.Text, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('updated_at', sa.String, nullable=True),
        sa.Column('created_by', sa.Integer, nullable=True),
    )
    op.create_table(
        'shipments',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('tracking_number', sa.Text, nullable=True),
        sa.Column('carrier', sa.Text, nullable=True),
        sa.Column('service_name', sa.Text, nullable=True),
        sa.Column('status', sa.Text, nullable=False, server_default=sa.text("'pending'")),
        sa.Column('label_url', sa.Text, nullable=True),
        sa.Column('cost', sa.Float, nullable=True),
        sa.Column('currency', sa.Text, nullable=True),
        sa.Column('provider', sa.Text, nullable=True),
        sa.Column('pickup_address', sa.Text, nullable=True),
        sa.Column('delivery_address', sa.Text, nullable=True),
        sa.Column('parcels', sa.Text, nullable=True),
        sa.Column('raw_response', sa.Text, nullable=True),
        sa.Column('created_at', sa.String, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('reference', sa.Text, nullable=True),
        sa.Column('supplier_id', sa.Integer, nullable=True),
        sa.Column('customer_id', sa.Integer, nullable=True),
        sa.Column('origin', sa.Text, nullable=True),
        sa.Column('destination', sa.Text, nullable=True),
        sa.Column('service_type', sa.Text, nullable=True),
        sa.Column('weight', sa.Float, nullable=True),
        sa.Column('weight_unit', sa.Text, nullable=True),
        sa.Column('dimensions', sa.Text, nullable=True),
        sa.Column('value', sa.Float, nullable=True),
        sa.Column('items_count', sa.Integer, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('eta', sa.String, nullable=True),
        sa.Column('customs_declaration_id', sa.Integer, nullable=True),
        sa.Column('shipped_at', sa.String, nullable=True),
        sa.Column('delivered_at', sa.String, nullable=True),
        sa.Column('created_by', sa.Integer, nullable=True),
        sa.Column('updated_at', sa.String, nullable=True),
    )
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('uuid', sa.Text, unique=True, nullable=True),
        sa.Column('issuer_tax_id', sa.Text, nullable=True),
        sa.Column('receiver_tax_id', sa.Text, nullable=True),
        sa.Column('receiver_name', sa.Text, nullable=True),
        sa.Column('total', sa.Float, nullable=True),
        sa.Column('tax_total', sa.Float, nullable=True),
        sa.Column('status', sa.Text, nullable=False, server_default=sa.text("'draft'")),
        sa.Column('eta_status', sa.Text, nullable=True),
        sa.Column('signed_data', sa.Text, nullable=True),
        sa.Column('raw_response', sa.Text, nullable=True),
        sa.Column('created_at', sa.String, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('invoice_number', sa.Text, nullable=True),
        sa.Column('customer_id', sa.Integer, nullable=True),
        sa.Column('supplier_id', sa.Integer, nullable=True),
        sa.Column('shipment_id', sa.Integer, nullable=True),
        sa.Column('subtotal', sa.Float, nullable=True),
        sa.Column('tax_rate', sa.Float, nullable=True),
        sa.Column('tax_amount', sa.Float, nullable=True),
        sa.Column('currency', sa.Text, nullable=True),
        sa.Column('issue_date', sa.String, nullable=True),
        sa.Column('due_date', sa.String, nullable=True),
        sa.Column('items', sa.Text, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_by', sa.Integer, nullable=True),
        sa.Column('updated_at', sa.String, nullable=True),
        sa.Column('internal_id', sa.Text, nullable=True),
        sa.Column('eta_uuid', sa.Text, nullable=True),
    )
    op.create_table(
        'customs_declarations',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('shipment_id', sa.Integer, nullable=True),
        sa.Column('hs_code', sa.Text, nullable=True),
        sa.Column('origin_country', sa.Text, nullable=True),
        sa.Column('value', sa.Float, nullable=True),
        sa.Column('currency', sa.Text, nullable=True),
        sa.Column('duties_estimate', sa.Float, nullable=True),
        sa.Column('status', sa.Text, nullable=False, server_default=sa.text("'draft'")),
        sa.Column('documents', sa.Text, nullable=True),
        sa.Column('created_at', sa.String, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('declaration_number', sa.Text, nullable=True),
        sa.Column('hs_code_id', sa.Integer, nullable=True),
        sa.Column('destination_country', sa.Text, nullable=True),
        sa.Column('total_value', sa.Float, nullable=True),
        sa.Column('tax_amount', sa.Float, nullable=True),
        sa.Column('total_duties', sa.Float, nullable=True),
        sa.Column('created_by', sa.Integer, nullable=True),
        sa.Column('updated_at', sa.String, nullable=True),
        sa.Column('submitted_at', sa.String, nullable=True),
        sa.Column('approved_at', sa.String, nullable=True),
    )
    op.create_table(
        'hs_codes',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('code', sa.Text, unique=True, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.Text, nullable=True),
        sa.Column('duty_rate', sa.Float, nullable=False, server_default=sa.text("0.0")),
        sa.Column('vat_rate', sa.Float, nullable=False, server_default=sa.text("14.0")),
        sa.Column('description_ar', sa.Text, nullable=True),
        sa.Column('restrictions', sa.Text, nullable=True),
    )
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('type', sa.Text, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('file_path', sa.Text, nullable=True),
        sa.Column('template_id', sa.Integer, nullable=True),
        sa.Column('created_by', sa.Integer, nullable=True),
        sa.Column('created_at', sa.String, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('document_type', sa.Text, nullable=True),
        sa.Column('metadata', sa.Text, nullable=True),
        sa.Column('file_name', sa.Text, nullable=True),
        sa.Column('file_type', sa.Text, nullable=True),
        sa.Column('file_size', sa.Integer, nullable=True),
        sa.Column('entity_type', sa.Text, nullable=True),
        sa.Column('entity_id', sa.Integer, nullable=True),
        sa.Column('updated_at', sa.String, nullable=True),
        sa.Column('template_type', sa.Text, nullable=True),
    )
    op.create_table(
        'resources',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('title', sa.Text, nullable=False),
        sa.Column('url', sa.Text, nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.Text, nullable=False),
        sa.Column('country', sa.Text, nullable=True),
        sa.Column('tags', sa.Text, nullable=True),
        sa.Column('is_verified', sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column('created_at', sa.String, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('title_ar', sa.Text, nullable=True),
        sa.Column('description_ar', sa.Text, nullable=True),
        sa.Column('resource_type', sa.Text, nullable=True),
        sa.Column('metadata', sa.Text, nullable=True),
        sa.Column('is_active', sa.Integer, nullable=True),
        sa.Column('created_by', sa.Integer, nullable=True),
        sa.Column('updated_at', sa.String, nullable=True),
        sa.Column('file_path', sa.Text, nullable=True),
    )
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, nullable=True),
        sa.Column('action', sa.Text, nullable=False),
        sa.Column('entity_type', sa.Text, nullable=True),
        sa.Column('entity_id', sa.Integer, nullable=True),
        sa.Column('details', sa.Text, nullable=True),
        sa.Column('created_at', sa.String, nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('resources')
    op.drop_table('documents')
    op.drop_table('hs_codes')
    op.drop_table('customs_declarations')
    op.drop_table('invoices')
    op.drop_table('shipments')
    op.drop_table('customers')
    op.drop_table('suppliers')
    op.drop_table('roles')
    op.drop_table('users')
