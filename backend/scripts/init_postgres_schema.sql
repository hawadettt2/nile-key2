-- PostgreSQL schema initialization for Nile Key Digital Platform.
-- This script creates all application tables in a fresh PostgreSQL database.
-- It is intended for initial setup only and does not perform data migration.

-- Users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    username TEXT UNIQUE,
    phone TEXT,
    company TEXT,
    role TEXT NOT NULL DEFAULT 'customer',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Roles
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    permissions TEXT NOT NULL,
    description TEXT
);

-- Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    id SERIAL PRIMARY KEY,
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
    updated_at TIMESTAMP,
    created_by INTEGER
);

-- Customers
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
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
    updated_at TIMESTAMP,
    created_by INTEGER
);

-- Shipments
CREATE TABLE IF NOT EXISTS shipments (
    id SERIAL PRIMARY KEY,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_at TIMESTAMP,
    service_provider TEXT,
    provider_shipment_id TEXT,
    awb_number TEXT,
    tracking_url TEXT,
    tracking_status TEXT,
    tracking_status_info TEXT,
    shipment_amount REAL,
    label_url TEXT,
    pickup_contact_id INTEGER,
    delivery_contact_id INTEGER,
    pickup_address_name TEXT,
    delivery_address_name TEXT,
    pickup_from_type TEXT DEFAULT 'Company',
    delivery_to_type TEXT DEFAULT 'Customer',
    provider_response TEXT
);

-- Invoices
CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_at TIMESTAMP,
    internal_id TEXT,
    eta_uuid TEXT,
    eta_status TEXT,
    eta_submission_id TEXT,
    eta_response TEXT,
    eta_cancellation_reason TEXT
);

-- ETA Connectors
CREATE TABLE IF NOT EXISTS eta_connectors (
    id SERIAL PRIMARY KEY,
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
);

-- ETA Logs
CREATE TABLE IF NOT EXISTS eta_logs (
    id SERIAL PRIMARY KEY,
    from_doctype TEXT NOT NULL,
    submission_status TEXT NOT NULL,
    submission_id TEXT,
    eta_response TEXT,
    documents TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ETA Log Documents
CREATE TABLE IF NOT EXISTS eta_log_documents (
    id SERIAL PRIMARY KEY,
    eta_log_id INTEGER NOT NULL,
    reference_doctype TEXT,
    reference_document INTEGER,
    uuid TEXT,
    long_id TEXT,
    error TEXT,
    eta_status TEXT DEFAULT 'Submitted',
    FOREIGN KEY (eta_log_id) REFERENCES eta_logs(id)
);

-- Customs Declarations
CREATE TABLE IF NOT EXISTS customs_declarations (
    id SERIAL PRIMARY KEY,
    declaration_number TEXT,
    shipment_id INTEGER,
    hs_code_id INTEGER,
    origin_country TEXT DEFAULT 'EG',
    destination_country TEXT,
    total_value REAL,
    currency TEXT DEFAULT 'USD',
    status TEXT DEFAULT 'draft',
    documents TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tax_amount REAL,
    total_duties REAL,
    created_by INTEGER,
    updated_at TIMESTAMP,
    submitted_at TIMESTAMP,
    approved_at TIMESTAMP
);

-- HS Codes
CREATE TABLE IF NOT EXISTS hs_codes (
    id SERIAL PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    category TEXT,
    duty_rate REAL DEFAULT 0.0,
    vat_rate REAL DEFAULT 14.0,
    description_ar TEXT,
    restrictions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    file_path TEXT,
    template_id INTEGER,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    document_type TEXT,
    metadata TEXT,
    file_name TEXT,
    file_type TEXT,
    file_size INTEGER,
    entity_type TEXT,
    entity_id INTEGER,
    updated_at TIMESTAMP,
    template_type TEXT
);

-- Resources
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_at TIMESTAMP
);

-- Shipping Providers
CREATE TABLE IF NOT EXISTS shipping_providers (
    id SERIAL PRIMARY KEY,
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
);

-- Shipping Parcel Templates
CREATE TABLE IF NOT EXISTS shipping_parcel_templates (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    length REAL NOT NULL,
    width REAL NOT NULL,
    height REAL NOT NULL,
    weight REAL NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Shipping Labels
CREATE TABLE IF NOT EXISTS shipping_labels (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER NOT NULL,
    provider TEXT NOT NULL,
    provider_shipment_id TEXT NOT NULL,
    label_url TEXT NOT NULL,
    label_format TEXT DEFAULT 'PDF',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Shipping Logs
CREATE TABLE IF NOT EXISTS shipping_logs (
    id SERIAL PRIMARY KEY,
    shipment_id INTEGER,
    provider TEXT NOT NULL,
    action TEXT NOT NULL,
    request_payload TEXT,
    response_payload TEXT,
    error_message TEXT,
    status_code INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contacts
CREATE TABLE IF NOT EXISTS contacts (
    id SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    mobile_no TEXT,
    gender TEXT,
    customer_id INTEGER,
    supplier_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Addresses
CREATE TABLE IF NOT EXISTS addresses (
    id SERIAL PRIMARY KEY,
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
);

-- Notification Templates
CREATE TABLE IF NOT EXISTS notification_templates (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    variables TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Notification Logs
CREATE TABLE IF NOT EXISTS notification_logs (
    id SERIAL PRIMARY KEY,
    template_id INTEGER,
    recipient TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    status TEXT NOT NULL,
    error TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notification Preferences
CREATE TABLE IF NOT EXISTS notification_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    notification_type TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    action TEXT NOT NULL,
    entity_type TEXT,
    entity_id INTEGER,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address TEXT,
    user_agent TEXT,
    session_id TEXT
);

-- Export Workflows
CREATE TABLE IF NOT EXISTS export_workflows (
    id SERIAL PRIMARY KEY,
    workflow_number TEXT UNIQUE NOT NULL,
    state TEXT NOT NULL DEFAULT 'draft',
    customer_id INTEGER NOT NULL,
    supplier_id INTEGER NOT NULL,
    invoice_id INTEGER,
    customs_declaration_id INTEGER,
    shipment_id INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    created_by INTEGER
);

-- Export Workflow Items
CREATE TABLE IF NOT EXISTS export_workflow_items (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES export_workflows(id)
);

-- Agent Sessions
CREATE TABLE IF NOT EXISTS agent_sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    context TEXT,
    status TEXT DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Agent Memory
CREATE TABLE IF NOT EXISTS agent_memory (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    memory_type TEXT DEFAULT 'context',
    importance INTEGER DEFAULT 5,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
);

-- Agent Audit Logs
CREATE TABLE IF NOT EXISTS agent_audit_logs (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    input_hash TEXT NOT NULL,
    output_status TEXT NOT NULL,
    result_ref TEXT,
    duration_ms INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT,
    FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
);

-- Knowledge Nodes
CREATE TABLE IF NOT EXISTS knowledge_nodes (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    label TEXT,
    properties TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Knowledge Edges
CREATE TABLE IF NOT EXISTS knowledge_edges (
    id TEXT PRIMARY KEY,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    properties TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (source_node_id) REFERENCES knowledge_nodes(id),
    FOREIGN KEY (target_node_id) REFERENCES knowledge_nodes(id)
);

-- Token Blacklist
CREATE TABLE IF NOT EXISTS token_blacklist (
    id SERIAL PRIMARY KEY,
    token TEXT NOT NULL,
    user_id INTEGER,
    reason TEXT DEFAULT 'logout',
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipments_customer ON shipments(customer_id);
CREATE INDEX IF NOT EXISTS idx_shipments_supplier ON shipments(supplier_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_user ON agent_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_nodes_entity ON knowledge_nodes(entity_type, entity_id);
