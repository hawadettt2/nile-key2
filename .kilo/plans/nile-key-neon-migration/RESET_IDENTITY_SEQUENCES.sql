DO $$
DECLARE r record; m bigint; v bigint;
BEGIN
  FOR r IN SELECT * FROM (VALUES
    ('roles',8),('users',1),('token_blacklist',0),('suppliers',163),
    ('supplier_accreditations',115),('supplier_accreditation_crops',325),
    ('customers',1),('customer_source_batches',1),('customer_raw_records',1),
    ('customer_products',0),('customer_evidence',0),('contacts',0),('addresses',0),
    ('shipments',0),('shipping_providers',0),('shipping_parcel_templates',0),
    ('shipping_labels',0),('shipping_logs',0),('invoices',0),('customs_declarations',0),
    ('hs_codes',13),('eta_connectors',0),('eta_logs',0),('eta_log_documents',0),
    ('documents',0),('resources',18),('notification_templates',0),('notification_logs',0),
    ('notification_preferences',0),('audit_logs',1),('export_workflows',0),
    ('export_workflow_items',0),('agent_audit_logs',2),('schema_migrations',1)
  ) AS t(tbl,seq)
  LOOP
    EXECUTE format('SELECT MAX(id) FROM %I', r.tbl) INTO m;
    v := GREATEST(COALESCE(m,0), r.seq);
    PERFORM setval(pg_get_serial_sequence(r.tbl,'id'), GREATEST(v,1), v > 0);
  END LOOP;
END $$;