"""
ETA Service Layer
Business logic for ETA compliance operations.
"""

import json
import logging
from datetime import datetime
from typing import Optional

from app.core.database import get_db_connection
from app.schemas.eta import (
    ETAAuthConfig,
    InvoiceSubmit,
    ReceiptSubmit,
    IssuerAddress,
    Issuer,
    ReceiverAddress,
    Receiver,
    InvoiceLine,
    Discount,
    TaxableItem,
    TaxTotals,
    UnitValue,
    Payment,
    Delivery,
    Signature,
)
from app.services.eta.eta_client import ETAClient, ETAHttpError

logger = logging.getLogger("eta")


# ========== Business Rules from Reference Repo ==========

def eta_round(_value: float, decimal: int = 5) -> float:
    """
    Round value to the specified number of decimal places, with a maximum of 5 decimal places.
    Extracted from erpnext_egypt_compliance utils.py.
    """
    if not decimal:
        decimal = 5
    precision = min(decimal, 5)
    return round(_value, precision)


def eta_datetime_issued_format(posting_date: datetime, seconds: int = 0) -> str:
    """
    Convert Cairo timezone datetime to UTC with Z suffix.
    Extracted from erpnext_egypt_compliance utils.py.
    """
    from datetime import timedelta
    from pytz import timezone as pytz_timezone
    
    date_time = posting_date + timedelta(seconds=seconds)
    date_utc_with_z_suffix = (
        pytz_timezone("Africa/Cairo")
        .localize(date_time, is_dst=None)
        .astimezone(pytz_timezone("UTC"))
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    return date_utc_with_z_suffix


def _map_eta_status(status: Optional[str]) -> str:
    if status is None:
        return "Submitted"
    mapping = {
        "Valid": "Valid",
        "Invalid": "Invalid",
        "Rejected": "Rejected",
        "Cancelled": "Cancelled",
    }
    return mapping.get(status, status if status else "Submitted")


def list_connectors(status: Optional[str] = None, skip: int = 0, limit: int = 100) -> list:
    with get_db_connection() as conn:
        query = "SELECT * FROM eta_connectors WHERE 1=1"
        params = []
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]


def get_connector(connector_id: int) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM eta_connectors WHERE id = ?", (connector_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("ETA connector not found")
        return dict(row)


def create_connector(data: dict, current_user: dict) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        cursor.execute(
            """INSERT INTO eta_connectors 
               (name, client_id, client_secret, environment, submission_mode, batch_size, 
                delay_in_hours, company_id, is_default, status, created_at, updated_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data.get("name", ""),
                data.get("client_id", ""),
                data.get("client_secret", ""),
                data.get("environment", "Pre-Production"),
                data.get("submission_mode", "Manual"),
                data.get("batch_size", 10),
                data.get("delay_in_hours", 0),
                data.get("company_id"),
                1 if data.get("is_default") else 0,
                data.get("status", "active"),
                now,
                now,
                current_user.get("id") if current_user else None,
            ),
        )
        conn.commit()
        return {"id": cursor.lastrowid, "message": "Connector created successfully"}


def update_connector(connector_id: int, data: dict, current_user: dict) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM eta_connectors WHERE id = ?", (connector_id,))
        if not cursor.fetchone():
            raise ValueError("ETA connector not found")
        
        fields = []
        params = []
        allowed = ["name", "client_id", "client_secret", "environment", "submission_mode", 
                   "batch_size", "delay_in_hours", "company_id", "is_default", "status"]
        for key, value in data.items():
            if key in allowed:
                if key == "is_default":
                    value = 1 if value else 0
                fields.append(f"{key} = ?")
                params.append(value)
        
        if fields:
            fields.append("updated_at = ?")
            params.append(datetime.utcnow().isoformat())
            params.append(connector_id)
            cursor.execute(f"UPDATE eta_connectors SET {', '.join(fields)} WHERE id = ?", params)
            conn.commit()
        
        return {"message": "Connector updated successfully"}


def delete_connector(connector_id: int) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM eta_connectors WHERE id = ?", (connector_id,))
        if not cursor.fetchone():
            raise ValueError("ETA connector not found")
        cursor.execute("DELETE FROM eta_connectors WHERE id = ?", (connector_id,))
        conn.commit()
        return {"message": "Connector deleted successfully"}


def _get_default_connector() -> dict:
    """Get the default ETA connector."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM eta_connectors WHERE is_default = 1 LIMIT 1")
        row = cursor.fetchone()
        if not row:
            raise ValueError("No default ETA connector configured")
        return dict(row)


def _build_eta_auth_config(connector: dict) -> ETAAuthConfig:
    """Build ETAAuthConfig from connector DB row."""
    return ETAAuthConfig(
        client_id=connector["client_id"],
        client_secret=connector["client_secret"],
        environment=connector.get("environment", "Pre-Production"),
    )


def _build_eta_invoice_payload(invoice: dict, connector: dict) -> InvoiceSubmit:
    """Build ETA InvoiceSubmit payload from internal invoice record.
    
    Extracts business logic from erpnext_egypt_compliance:
    - Maps issuer/receiver from company/customer data
    - Builds invoice lines with tax items
    - Calculates totals
    - Applies discount rules
    """
    from app.services.supplier import get_supplier
    from app.services.customer import get_customer
    
    # Get supplier/company info for issuer
    supplier_id = invoice.get("supplier_id")
    supplier = get_supplier(supplier_id) if supplier_id else {}
    
    # Get customer info for receiver
    customer_id = invoice.get("customer_id")
    customer = get_customer(customer_id) if customer_id else {}
    
    # Build issuer address from supplier/company data
    issuer_address = IssuerAddress(
        branchId=str(supplier.get("id", "1")),
        country="EG",
        governate=supplier.get("governate", "Cairo"),
        regionCity=supplier.get("city", "Cairo"),
        street=supplier.get("address", "Unknown")[:100],
        buildingNumber=str(supplier.get("id", "1")),
    )
    
    issuer = Issuer(
        id=supplier.get("tax_id", "000000000"),
        type="B",
        name=supplier.get("name_en", supplier.get("name", "Nile Key")),
        address=issuer_address,
    )
    
    # Build receiver address from customer data
    receiver_address = ReceiverAddress(
        country=customer.get("country", "EG"),
        governate=customer.get("city", "Cairo"),
        regionCity=customer.get("city", "Cairo"),
        street=customer.get("address", "Unknown")[:100],
        buildingNumber="1",
    )
    
    receiver_type = "B"
    if customer.get("category") == "foreign":
        receiver_type = "F"
    elif not customer.get("tax_id"):
        receiver_type = "P"
    
    receiver = Receiver(
        type=receiver_type,
        id=customer.get("tax_id"),
        name=customer.get("name_en", customer.get("name", "Customer")),
        address=receiver_address,
    )
    
    # Parse items
    import json
    items = invoice.get("items", "[]")
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except (json.JSONDecodeError, TypeError):
            items = []
    
    # Build invoice lines
    subtotal = float(invoice.get("subtotal", 0.0) or 0.0)
    tax_rate = float(invoice.get("tax_rate", 14.0) or 14.0)
    total = float(invoice.get("total", 0.0) or 0.0)
    tax_amount = total - subtotal
    
    invoice_lines = []
    total_discount = 0.0
    for item in items:
        item_total = float(item.get("total", item.get("unit_price", 0.0) * item.get("quantity", 1.0)))
        item_qty = float(item.get("quantity", 1.0))
        unit_price = item_total / item_qty if item_qty > 0 else 0.0
        
        line = InvoiceLine(
            description=item.get("description", "Item")[:100],
            itemType="EGS",
            itemCode=item.get("itemCode", item.get("description", "001"))[:50],
            internalCode=str(item.get("id", "")),
            unitType="EA",
            quantity=item_qty,
            salesTotal=item_total,
            netTotal=item_total,
            total=item_total,
            discount=Discount(),
            taxableItems=[TaxableItem(taxType="T1", subType="V001", amount=tax_amount * (item_total / subtotal) if subtotal > 0 else 0.0, rate=tax_rate)],
            unitValue=UnitValue(currencySold="EGP", amountEGP=unit_price),
        )
        invoice_lines.append(line)
    
    # Build tax totals
    tax_totals = [TaxTotals(taxType="T1", amount=tax_amount)] if tax_amount > 0 else []
    
    # Build invoice
    issue_date = invoice.get("issue_date", datetime.utcnow().isoformat())
    if isinstance(issue_date, str):
        try:
            issue_date = datetime.fromisoformat(issue_date.replace("Z", "+00:00"))
        except (ValueError, TypeError):
            issue_date = datetime.utcnow()
    
    # Convert Cairo timezone to UTC with Z suffix (ETA requirement)
    formatted_date = eta_datetime_issued_format(issue_date)
    
    invoice_submit = InvoiceSubmit(
        issuer=issuer,
        receiver=receiver,
        documentType="I",
        documentTypeVersion="1.0",
        dateTimeIssued=formatted_date,
        taxpayerActivityCode=invoice.get("taxpayer_activity_code", "1234"),
        internalID=invoice.get("invoice_number", f"INV-{invoice['id']}"),
        invoiceLines=invoice_lines,
        totalDiscountAmount=total_discount,
        totalSalesAmount=subtotal,
        netAmount=subtotal,
        totalAmount=total,
        taxTotals=tax_totals,
        signatures=[],
    )
    
    return invoice_submit


def submit_invoice_to_eta(invoice_id: int, connector_id: int, current_user: dict) -> dict:
    """Submit an invoice to ETA via the specified connector.
    
    Includes idempotency check to prevent duplicate submissions.
    """
    # Idempotency check
    existing_submission = check_invoice_idempotency(invoice_id)
    if existing_submission:
        return {
            "message": "Invoice already submitted today (idempotent)",
            "submission_id": existing_submission,
            "status": "Submitted",
            "idempotent": True,
        }
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Load connector
        cursor.execute("SELECT * FROM eta_connectors WHERE id = ?", (connector_id,))
        conn_row = cursor.fetchone()
        if not conn_row:
            raise ValueError("ETA connector not found")
        connector = dict(conn_row)
        
        # Load invoice
        cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        inv_row = cursor.fetchone()
        if not inv_row:
            raise ValueError("Invoice not found")
        invoice = dict(inv_row)
        
        if invoice.get("eta_status") == "Valid":
            return {"message": "Invoice already submitted and valid", "status": "Valid"}
        
        # Idempotency check — if already submitted with UUID, return cached result
        if invoice.get("eta_uuid") and invoice.get("eta_status") == "Submitted":
            return {
                "message": "Invoice already submitted to ETA",
                "uuid": invoice["eta_uuid"],
                "submission_id": invoice.get("eta_submission_id"),
                "status": "Submitted",
            }
        
        # Build ETA client
        auth_config = _build_eta_auth_config(connector)
        idempotency_key = generate_idempotency_key(invoice_id, connector_id)
        client = ETAClient(auth_config)
        
        try:
            # Build invoice payload
            payload = _build_eta_invoice_payload(invoice, connector)
            result = client.submit_invoices([payload], idempotency_key=idempotency_key)
            
            # Update invoice with ETA response
            uuid = result.get("documents", [{}])[0].get("uuid")
            submission_id = result.get("submissionId")
            now = datetime.utcnow().isoformat()
            
            cursor.execute(
                """UPDATE invoices 
                   SET eta_uuid = ?, eta_status = ?, eta_submission_id = ?, eta_response = ?, updated_at = ?
                   WHERE id = ?""",
                (
                    uuid,
                    "Submitted",
                    submission_id,
                    str(result),
                    now,
                    invoice_id,
                ),
            )
            
            # Create ETA log
            log = create_eta_log(
                from_doctype="Sales Invoice",
                submission_status="Started",
                submission_id=submission_id or "",
                eta_response=str(result),
                documents=[{"uuid": uuid, "reference_document": invoice_id, "eta_status": "Submitted"}],
            )
            conn.commit()
            
            return {
                "message": "Invoice submitted to ETA successfully",
                "uuid": uuid,
                "submission_id": submission_id,
                "status": "Submitted",
                "eta_log_id": log["id"],
            }
        
        except ETAHttpError as exc:
            # Map error to user-friendly message
            user_message = map_eta_error_to_user_message(exc)
            
            # Update invoice with error
            cursor.execute(
                """UPDATE invoices 
                   SET eta_status = ?, eta_response = ?, updated_at = ?
                   WHERE id = ?""",
                (
                    "Invalid",
                    str({"error": exc.message, "details": exc.details, "user_message": user_message}),
                    datetime.utcnow().isoformat(),
                    invoice_id,
                ),
            )
            conn.commit()
            raise ValueError(user_message)
        finally:
            client.close()


def cancel_eta_invoice(invoice_id: int, reason: str, current_user: dict) -> dict:
    """Cancel a submitted invoice at ETA."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT eta_uuid, eta_status FROM invoices WHERE id = ?", (invoice_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Invoice not found")
        
        data = dict(row)
        uuid = data.get("eta_uuid")
        current_status = data.get("eta_status")
        
        if not uuid:
            raise ValueError("Invoice not submitted to ETA yet")
        if current_status == "Cancelled":
            raise ValueError("Invoice already cancelled")
        
        # Find default connector
        connector = _get_default_connector()
        auth_config = _build_eta_auth_config(connector)
        client = ETAClient(auth_config)
        
        try:
            result = client.cancel_document(uuid, reason)
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """UPDATE invoices 
                   SET eta_status = ?, eta_cancellation_reason = ?, updated_at = ?
                   WHERE id = ?""",
                ("Cancelled", reason, now, invoice_id),
            )
            conn.commit()
            return {"message": "Invoice cancelled at ETA successfully", "status": "Cancelled"}
        except ETAHttpError as exc:
            raise ValueError(f"ETA cancellation failed: {exc.message}")
        finally:
            client.close()


def get_eta_invoice_status(invoice_id: int) -> dict:
    """Fetch latest status from ETA and update local record."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT eta_uuid, eta_status FROM invoices WHERE id = ?", (invoice_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Invoice not found")
        
        data = dict(row)
        uuid = data.get("eta_uuid")
        if not uuid:
            raise ValueError("Invoice not submitted to ETA yet")
        
        # Find default connector
        connector = _get_default_connector()
        auth_config = _build_eta_auth_config(connector)
        client = ETAClient(auth_config)
        
        try:
            status_data = client.get_document_status(uuid)
            eta_status = _map_eta_status(status_data.get("status"))
            
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """UPDATE invoices 
                   SET eta_status = ?, eta_response = ?, updated_at = ?
                   WHERE id = ?""",
                (eta_status, str(status_data), now, invoice_id),
            )
            conn.commit()
            
            return {
                "id": invoice_id,
                "uuid": uuid,
                "eta_status": eta_status,
                "eta_response": status_data,
                "updated_at": now,
            }
        finally:
            client.close()


def submit_receipt_to_eta(receipt_data: dict, connector_id: int, current_user: dict) -> dict:
    """Submit an e-receipt to ETA."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM eta_connectors WHERE id = ?", (connector_id,))
        conn_row = cursor.fetchone()
        if not conn_row:
            raise ValueError("ETA connector not found")
        connector = dict(conn_row)
        
        auth_config = ETAAuthConfig(
            client_id=connector["client_id"],
            client_secret=connector["client_secret"],
            environment=connector.get("environment", "Pre-Production"),
            pos_serial=connector.get("pos_serial"),
            pos_os_version=connector.get("pos_os_version"),
        )
        client = ETAClient(auth_config)
        
        try:
            receipt = ReceiptSubmit(**receipt_data)
            result = client.submit_receipts([receipt])
            
            submission_id = result.get("submissionId")
            accepted = result.get("acceptedDocuments", 0)
            rejected = result.get("rejectedDocuments", 0)
            
            log = create_eta_log(
                from_doctype="POS Invoice",
                submission_status="Completed" if rejected == 0 else "Partially Succeeded",
                submission_id=submission_id or "",
                eta_response=str(result),
            )
            conn.commit()
            
            return {
                "message": "Receipt submitted to ETA",
                "submission_id": submission_id,
                "accepted": accepted,
                "rejected": rejected,
                "status": "Completed" if rejected == 0 else "Partially Succeeded",
                "eta_log_id": log["id"],
            }
        except ETAHttpError as exc:
            raise ValueError(f"Receipt submission failed: {exc.message}")
        finally:
            client.close()


def download_eta_pdf(invoice_id: int) -> bytes:
    """Download ETA PDF for an invoice."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT eta_uuid FROM invoices WHERE id = ?", (invoice_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Invoice not found")
        uuid = dict(row).get("eta_uuid")
        if not uuid:
            raise ValueError("Invoice not submitted to ETA yet")
        
        connector = _get_default_connector()
        auth_config = _build_eta_auth_config(connector)
        client = ETAClient(auth_config)
        
        try:
            return client.download_pdf(uuid)
        finally:
            client.close()


def submit_pending_batch(connector_id: int) -> dict:
    """Submit pending invoices in batch mode.
    
    Implements business logic from erpnext_egypt_compliance:
    - Filters invoices for today only
    - Respects delay_in_hours setting
    - Respects batch_size setting
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get connector settings
        cursor.execute("SELECT * FROM eta_connectors WHERE id = ?", (connector_id,))
        conn_row = cursor.fetchone()
        if not conn_row:
            raise ValueError("ETA connector not found")
        connector = dict(conn_row)
        
        batch_size = connector.get("batch_size", 10)
        delay_in_hours = connector.get("delay_in_hours", 0)
        
        # Get today's date for filtering
        today = datetime.utcnow().date().isoformat()
        
        # Query pending invoices for today
        query = """SELECT id, eta_uuid, eta_status, issue_date, created_at 
                   FROM invoices 
                   WHERE (eta_status IS NULL OR eta_status = '')
                   AND DATE(created_at) = ?
                   LIMIT ?"""
        params = [today, batch_size * 3]  # Get more than batch_size to account for filtering
        
        cursor.execute(query, params)
        pending = cursor.fetchall()
        
        if not pending:
            return {"message": "No pending invoices for today", "submitted": 0}
        
        auth_config = _build_eta_auth_config(connector)
        client = ETAClient(auth_config)
        
        try:
            submitted = 0
            for row in pending[:batch_size * 2]:  # Process up to 2x batch size
                inv = dict(row)
                invoice_id = inv["id"]
                
                # Idempotency check
                if inv.get("eta_uuid"):
                    continue
                
                # Delay logic: check if invoice is old enough
                if delay_in_hours > 0:
                    created_at = inv.get("created_at")
                    if created_at:
                        try:
                            created_dt = datetime.fromisoformat(created_at)
                            hours_old = (datetime.utcnow() - created_dt).total_seconds() / 3600
                            if hours_old < delay_in_hours:
                                continue  # Skip, not old enough
                        except (ValueError, TypeError):
                            pass
                
                try:
                    payload = _build_eta_invoice_payload(inv, connector)
                    result = client.submit_invoices([payload])
                    uuid = result.get("documents", [{}])[0].get("uuid")
                    submission_id = result.get("submissionId")
                    now = datetime.utcnow().isoformat()
                    cursor.execute(
                        """UPDATE invoices 
                           SET eta_uuid = ?, eta_status = ?, eta_submission_id = ?, eta_response = ?, updated_at = ?
                           WHERE id = ?""",
                        (
                            uuid,
                            "Submitted",
                            submission_id,
                            str(result),
                            now,
                            invoice_id,
                        ),
                    )
                    submitted += 1
                except ETAHttpError as exc:
                    logger.error("Failed to submit invoice %d: %s", invoice_id, exc.message)
                    continue
            
            conn.commit()
            return {"message": f"Batch submitted {submitted} invoices", "submitted": submitted}
        finally:
            client.close()


def create_eta_log(from_doctype: str, submission_status: str, submission_id: Optional[str] = None,
                   eta_response: Optional[str] = None, documents: Optional[str] = None) -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO eta_logs (from_doctype, submission_status, submission_id, eta_response, documents, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (from_doctype, submission_status, submission_id, eta_response, documents, now),
        )
        conn.commit()
        return {"id": cursor.lastrowid}


def update_eta_log_documents(eta_log_id: int, reference_doctype: str, reference_document: int,
                              uuid: str, long_id: Optional[str] = None, error: Optional[str] = None,
                              eta_status: str = "Submitted") -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO eta_log_documents (eta_log_id, reference_doctype, reference_document, uuid, long_id, error, eta_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (eta_log_id, reference_doctype, reference_document, uuid, long_id, error, eta_status),
        )
        conn.commit()
        return {"id": cursor.lastrowid}


# ========== Status Polling ==========

def poll_pending_invoice_statuses(connector_id: Optional[int] = None, limit: int = 100) -> dict:
    """Poll ETA for status updates on submitted invoices.
    
    Called by scheduler (APScheduler) to update local invoice statuses.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Find connector
        if connector_id:
            cursor.execute("SELECT * FROM eta_connectors WHERE id = ?", (connector_id,))
        else:
            cursor.execute("SELECT * FROM eta_connectors WHERE is_default = 1 LIMIT 1")
        conn_row = cursor.fetchone()
        if not conn_row:
            return {"message": "No ETA connector configured", "updated": 0}
        connector = dict(conn_row)
        
        # Find invoices with Submitted status that have UUIDs
        cursor.execute(
            """SELECT id, eta_uuid FROM invoices 
               WHERE eta_status = 'Submitted' AND eta_uuid IS NOT NULL 
               LIMIT ?""",
            (limit,),
        )
        pending = cursor.fetchall()
        
        if not pending:
            return {"message": "No pending invoices to poll", "updated": 0}
        
        auth_config = _build_eta_auth_config(connector)
        client = ETAClient(auth_config)
        
        updated = 0
        try:
            for row in pending:
                inv = dict(row)
                invoice_id = inv["id"]
                uuid = inv["eta_uuid"]
                
                try:
                    status_data = client.get_document_status(uuid)
                    eta_status = _map_eta_status(status_data.get("status"))
                    now = datetime.utcnow().isoformat()
                    
                    cursor.execute(
                        """UPDATE invoices 
                           SET eta_status = ?, eta_response = ?, updated_at = ?
                           WHERE id = ?""",
                        (eta_status, str(status_data), now, invoice_id),
                    )
                    
                    # Update ETA log if exists
                    cursor.execute(
                        "SELECT id FROM eta_logs WHERE submission_id LIKE ? AND from_doctype = 'Sales Invoice'",
                        (f"%{uuid}%",),
                    )
                    log_row = cursor.fetchone()
                    if log_row:
                        log_id = dict(log_row)["id"]
                        update_eta_log_documents(
                            eta_log_id=log_id,
                            reference_doctype="Sales Invoice",
                            reference_document=invoice_id,
                            uuid=uuid,
                            eta_status=eta_status,
                        )
                    
                    updated += 1
                except ETAHttpError as exc:
                    logger.error("Failed to poll invoice %d: %s", invoice_id, exc.message)
                    continue
            
            conn.commit()
            return {"message": f"Polled and updated {updated} invoices", "updated": updated}
        finally:
            client.close()


# ========== Error Mapping ==========

def map_eta_error_to_user_message(error: ETAHttpError) -> str:
    """Map ETA HTTP errors to user-friendly Arabic/English messages."""
    status_messages = {
        400: "بيانات الفاتورة غير صحيحة. يرجى مراجعة البيانات والمحاولة مرة أخرى.",
        401: "انتهت صلاحية بيانات الاعتماد. يرجى تحديث بيانات الاتصال بـ ETA.",
        403: "ليس لديك صلاحية للوصول إلى هذه الخدمة.",
        404: "الوثيقة غير موجودة في نظام ETA.",
        429: "تم تجاوز الحد المسموح من الطلبات. يرجى المحاولة لاحقاً.",
        500: "خطأ في خادم ETA. يرجى المحاولة لاحقاً.",
        503: "خدمة ETA غير متاحة حالياً. يرجى المحاولة لاحقاً.",
    }
    
    message = status_messages.get(error.status_code, f"خطأ غير متوقع: {error.message}")
    
    # Add detail from ETA response if available
    if error.details:
        for detail in error.details:
            if detail.get("message"):
                message = f"{message} (التفاصيل: {detail['message']})"
                break
    
    return message


# ========== Idempotency ==========

def generate_idempotency_key(invoice_id: int, connector_id: int) -> str:
    """Generate idempotency key for invoice submission.
    
    Format: eta-inv-{invoice_id}-{connector_id}-{date}
    This ensures the same invoice can only be submitted once per day per connector.
    """
    from datetime import date
    return f"eta-inv-{invoice_id}-{connector_id}-{date.today().isoformat()}"


def check_existing_eta_logs(reference_document: int, reference_doctype: str = "Sales Invoice") -> bool:
    """Check if there are existing ETA logs for a document.
    
    Extracted from erpnext_egypt_compliance main.py.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id FROM eta_log_documents 
               WHERE reference_doctype = ? AND reference_document = ? 
               LIMIT 1""",
            (reference_doctype, reference_document),
        )
        row = cursor.fetchone()
        return row is not None


def check_invoice_idempotency(invoice_id: int) -> Optional[str]:
    """Check if invoice was already submitted today.
    
    Returns the existing submission_id if found, None otherwise.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        today = datetime.utcnow().date().isoformat()
        cursor.execute(
            """SELECT eta_submission_id, eta_uuid FROM invoices 
               WHERE id = ? AND DATE(updated_at) = ? AND eta_status IN ('Submitted', 'Valid')""",
            (invoice_id, today),
        )
        row = cursor.fetchone()
        if row:
            return dict(row).get("eta_submission_id")
        return None


# ========== Email Notifications (stub for WP-21 integration) ==========

def check_unsigned_invoices_and_notify(company_id: Optional[int] = None) -> dict:
    """
    Check for submitted invoices that haven't been signed and prepare notifications.
    
    NOTE: Email sending is deferred to WP-21 (Platform Integration) which will add SMTP service.
    This function prepares the notification data only.
    
    Extracted from erpnext_egypt_compliance utils.py.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Find invoices with Submitted status older than 2 hours
        cutoff_time = (datetime.utcnow() - timedelta(hours=2)).isoformat()
        
        query = """SELECT id, invoice_number, customer_id, total, created_at 
                   FROM invoices 
                   WHERE eta_status = 'Submitted' 
                   AND created_at < ?
                   AND eta_uuid IS NOT NULL"""
        params = [cutoff_time]
        
        if company_id:
            # In production, join with suppliers/companies table
            pass
        
        cursor.execute(query, params)
        unsigned = cursor.fetchall()
        
        if not unsigned:
            return {"message": "No unsigned invoices found", "count": 0}
        
        # Prepare notification data (actual sending deferred to WP-21)
        notifications = []
        for inv in unsigned:
            inv_dict = dict(inv)
            notifications.append({
                "invoice_id": inv_dict["id"],
                "invoice_number": inv_dict.get("invoice_number"),
                "customer_id": inv_dict.get("customer_id"),
                "total": inv_dict.get("total"),
                "created_at": inv_dict.get("created_at"),
                "type": "unsigned_invoice",
                "message": f"Invoice {inv_dict.get('invoice_number')} submitted to ETA but not signed for over 2 hours",
            })
        
        logger.warning("Found %d unsigned invoices pending signature", len(notifications))
        return {
            "message": f"Found {len(notifications)} unsigned invoices",
            "count": len(notifications),
            "notifications": notifications,
            "status": "pending_smtp_integration",  # Deferred to WP-21
        }


def check_not_submitted_invoices_and_notify(company_id: Optional[int] = None) -> dict:
    """
    Check for invoices not submitted to ETA and prepare notifications.
    
    NOTE: Email sending is deferred to WP-21 (Platform Integration) which will add SMTP service.
    This function prepares the notification data only.
    
    Extracted from erpnext_egypt_compliance utils.py.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Find invoices not submitted to ETA
        query = """SELECT id, invoice_number, customer_id, total, created_at 
                   FROM invoices 
                   WHERE (eta_status IS NULL OR eta_status = '')
                   AND created_at < ?"""
        cutoff_time = (datetime.utcnow() - timedelta(hours=2)).isoformat()
        params = [cutoff_time]
        
        if company_id:
            pass
        
        cursor.execute(query, params)
        not_submitted = cursor.fetchall()
        
        if not_not_submitted := [dict(r) for r in not_submitted]:
            logger.warning("Found %d invoices not submitted to ETA", len(not_not_submitted))
            return {
                "message": f"Found {len(not_not_submitted)} invoices not submitted to ETA",
                "count": len(not_not_submitted),
                "notifications": [
                    {
                        "invoice_id": inv["id"],
                        "invoice_number": inv.get("invoice_number"),
                        "customer_id": inv.get("customer_id"),
                        "total": inv.get("total"),
                        "created_at": inv.get("created_at"),
                        "type": "not_submitted_invoice",
                        "message": f"Invoice {inv.get('invoice_number')} not submitted to ETA for over 2 hours",
                    }
                    for inv in not_not_submitted
                ],
                "status": "pending_smtp_integration",  # Deferred to WP-21
            }
        
        return {"message": "No pending invoices found", "count": 0}


def send_notification(notification_type: str, recipients: list, data: dict) -> dict:
    """
    Send email notification.
    
    NOTE: This is a stub. Actual email sending is implemented in WP-21 (Platform Integration)
    which will add the SMTP service integration.
    
    Extracted from erpnext_egypt_compliance utils.py.
    """
    logger.info(
        "Notification prepared (type=%s, recipients=%d, status=deferred_to_WP-21)",
        notification_type,
        len(recipients),
    )
    return {
        "status": "deferred",
        "notification_type": notification_type,
        "recipients_count": len(recipients),
        "message": "Email sending deferred to WP-21 (SMTP integration)",
    }
