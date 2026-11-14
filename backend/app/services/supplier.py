import json
from typing import Optional

from app.schemas.supplier import (
    SupplierCreate, SupplierUpdate, SupplierAccreditationCreate, SupplierAccreditationUpdate,
)
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate
from app.core.database import get_db, DatabaseSession
from app.services.base import now_iso


def _supplier_row_to_response(row: dict) -> dict:
    result = dict(row)
    if isinstance(result.get("certificates"), str):
        try:
            result["certificates"] = json.loads(result["certificates"])
        except (json.JSONDecodeError, TypeError):
            result["certificates"] = []
    if result.get("country") is None:
        result["country"] = "Egypt"
    return result


def _validate_supplier_fields(facility_type, parent_company_id, station_code, session, exclude_id=None, require_facility=True):
    if require_facility and facility_type is None:
        raise ValueError("facility_type is required")
    if facility_type is not None and facility_type not in ("company", "packing_station", "farm"):
        raise ValueError("Invalid facility_type")
    if parent_company_id is not None:
        parent = session.fetch_one("SELECT id, facility_type FROM suppliers WHERE id = ?", (parent_company_id,))
        if not parent:
            raise ValueError("Parent company not found")
        if parent["facility_type"] != "company":
            raise ValueError("Parent must be a company")
    if facility_type == "company" and parent_company_id is not None:
        raise ValueError("A company cannot have a parent company")
    if facility_type in ("packing_station", "farm") and parent_company_id is None:
        raise ValueError("Station or farm must belong to a company")
    if station_code:
        q = "SELECT id FROM suppliers WHERE station_code = ?"
        params = [station_code]
        if exclude_id is not None:
            q += " AND id != ?"
            params.append(exclude_id)
        existing = session.fetch_one(q, tuple(params))
        if existing:
            raise ValueError("Station code already exists")


def list_suppliers(
    search: Optional[str] = None,
    status: Optional[str] = None,
    city: Optional[str] = None,
    facility_type: Optional[str] = None,
    verification_status: Optional[str] = None,
    province: Optional[str] = None,
    crop: Optional[str] = None,
    season: Optional[str] = None,
    skip: int = 0,
    limit: int = 500,
) -> list[dict]:
    from app.services.base import build_list_query

    conn = get_db()
    try:
        filters = {"status": status, "city": city}
        if facility_type:
            filters["facility_type"] = facility_type
        if verification_status:
            filters["verification_status"] = verification_status
        if province:
            filters["province"] = province
        # crop filter: suppliers with an accreditation containing this crop
        crop_clause = ""
        crop_params = []
        if crop:
            crop_clause = " AND id IN (SELECT supplier_id FROM supplier_accreditations WHERE id IN (SELECT accreditation_id FROM supplier_accreditation_crops WHERE crop_name LIKE ?))"
            crop_params = [f"%{crop}%"]
        season_clause = ""
        season_params = []
        if season:
            season_clause = " AND id IN (SELECT supplier_id FROM supplier_accreditations WHERE season LIKE ?)"
            season_params = [f"%{season}%"]
        query, params = build_list_query(
            "suppliers",
            filters=filters,
            search_fields=["name", "name_en", "email", "phone", "station_code", "province"],
            search=search,
            limit=limit,
            offset=skip,
        )
        if crop_clause:
            query = query.replace("WHERE 1=1", "WHERE 1=1" + crop_clause, 1)
        if season_clause:
            query = query.replace("WHERE 1=1", "WHERE 1=1" + season_clause, 1)
        # Insert crop/season params before the trailing LIMIT/OFFSET params
        tail = params[-2:] if len(params) >= 2 else []
        head = params[:-2] if len(params) >= 2 else params
        params = head + crop_params + season_params + tail
        session = DatabaseSession(conn)
        rows = session.fetch_all(query, tuple(params))
        return [_supplier_row_to_response(dict(r)) for r in rows]
    finally:
        conn.close()


def get_supplier(supplier_id: int) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        row = session.fetch_one("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        if not row:
            raise ValueError("Supplier not found")
        return _supplier_row_to_response(dict(row))
    finally:
        conn.close()


def create_supplier(data: SupplierCreate, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        payload = data.model_dump()
        if payload.get("station_code") is not None:
            payload["station_code"] = payload["station_code"].strip() if isinstance(payload["station_code"], str) else payload["station_code"]
        _validate_supplier_fields(
            payload.get("facility_type"),
            payload.get("parent_company_id"),
            payload.get("station_code"),
            session,
        )
        with session.transaction():
            supplier_id = session.insert(
                "suppliers",
                {
                    "name": payload["name"],
                    "name_en": payload.get("name_en"),
                    "contact_person": payload.get("contact_person"),
                    "email": payload.get("email"),
                    "phone": payload.get("phone"),
                    "address": payload.get("address"),
                    "city": payload.get("city"),
                    "province": payload.get("province"),
                    "country": payload.get("country", "Egypt"),
                    "tax_id": payload.get("tax_id"),
                    "commercial_registry": payload.get("commercial_registry"),
                    "certificates": json.dumps(payload.get("certificates", [])) if payload.get("certificates") else "[]",
                    "notes": payload.get("notes"),
                    "status": "active",
                    "created_at": now_iso(),
                    "created_by": current_user["id"],
                    "facility_type": payload.get("facility_type"),
                    "station_code": payload.get("station_code"),
                    "parent_company_id": payload.get("parent_company_id"),
                    "data_status": payload.get("data_status", "raw"),
                    "verification_status": payload.get("verification_status", "unverified"),
                    "source_serial": payload.get("source_serial"),
                    "activity": payload.get("activity"),
                },
            )
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="create", entity_type="supplier", entity_id=supplier_id, details=payload["name"]),
        )
        return {"id": supplier_id, "message": "Supplier created successfully"}
    finally:
        conn.close()


def update_supplier(supplier_id: int, data: SupplierUpdate, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        existing = session.fetch_one("SELECT id FROM suppliers WHERE id = ?", (supplier_id,))
        if not existing:
            raise ValueError("Supplier not found")

        payload = data.model_dump(exclude_unset=True)
        if payload.get("station_code") is not None and isinstance(payload["station_code"], str):
            payload["station_code"] = payload["station_code"].strip()
        if payload:
            _validate_supplier_fields(
                payload.get("facility_type"),
                payload.get("parent_company_id"),
                payload.get("station_code"),
                session,
                exclude_id=supplier_id,
                require_facility="facility_type" in payload,
            )

        updates = {}
        for field, value in payload.items():
            if value is not None:
                if field == "certificates":
                    value = str(value) if isinstance(value, list) else value
                updates[field] = value
        if not updates:
            return {"message": "No changes"}

        with session.transaction():
            session.update("suppliers", supplier_id, updates)
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="update", entity_type="supplier", entity_id=supplier_id),
        )
        return {"message": "Supplier updated successfully"}
    finally:
        conn.close()


def delete_supplier(supplier_id: int, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        with session.transaction():
            updated = session.update("suppliers", supplier_id, {"status": "inactive"})
        if not updated:
            return {"message": "No changes"}
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="delete", entity_type="supplier", entity_id=supplier_id),
        )
        return {"message": "Supplier deactivated successfully"}
    finally:
        conn.close()


# ========== Supplier Accreditations ==========

def list_accreditations(supplier_id: int) -> list[dict]:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        row = session.fetch_one("SELECT id FROM suppliers WHERE id = ?", (supplier_id,))
        if not row:
            raise ValueError("Supplier not found")
        rows = session.fetch_all(
            "SELECT * FROM supplier_accreditations WHERE supplier_id = ? ORDER BY created_at DESC",
            (supplier_id,),
        )
        result = []
        for r in rows:
            d = dict(r)
            crop_rows = session.fetch_all(
                "SELECT crop_name FROM supplier_accreditation_crops WHERE accreditation_id = ?",
                (d["id"],),
            )
            d["crops"] = [cr["crop_name"] for cr in crop_rows]
            if not d.get("scope") and d["crops"]:
                d["scope"] = ", ".join(d["crops"])
            result.append(d)
        return result
    finally:
        conn.close()


def create_accreditation(supplier_id: int, data, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        row = session.fetch_one("SELECT id FROM suppliers WHERE id = ?", (supplier_id,))
        if not row:
            raise ValueError("Supplier not found")

        payload = data.model_dump() if hasattr(data, "model_dump") else dict(data)
        valid_statuses = ("unverified", "current", "previous", "expired")
        status = payload.get("status", "unverified")
        if status not in valid_statuses:
            raise ValueError("Invalid accreditation status")
        if status == "current":
            raise ValueError("Accreditation cannot be set to current on creation; use the verify endpoint")

        with session.transaction():
            acc_id = session.insert(
                "supplier_accreditations",
                {
                    "supplier_id": supplier_id,
                    "source_type": payload["source_type"],
                    "accrediting_body": payload.get("accrediting_body"),
                    "accreditation_number": payload.get("accreditation_number"),
                    "scope": payload.get("scope"),
                    "season": payload.get("season"),
                    "accreditation_date": payload.get("accreditation_date"),
                    "validity_date": payload.get("validity_date"),
                    "status": status,
                    "source_document": payload.get("source_document"),
                    "source_page": payload.get("source_page"),
                    "source_reference": payload.get("source_reference"),
                    "created_at": now_iso(),
                    "created_by": current_user["id"],
                },
            )
            # Insert structured crops
            crops = payload.get("crops")
            if crops:
                for crop in crops:
                    if crop and str(crop).strip():
                        session.insert(
                            "supplier_accreditation_crops",
                            {
                                "accreditation_id": acc_id,
                                "crop_name": str(crop).strip(),
                                "created_at": now_iso(),
                            },
                        )
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="create", entity_type="supplier_accreditation", entity_id=acc_id, details=payload.get("source_type")),
        )
        return {"id": acc_id, "message": "Accreditation created successfully"}
    finally:
        conn.close()


def update_accreditation(accreditation_id: int, data, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        existing = session.fetch_one("SELECT id FROM supplier_accreditations WHERE id = ?", (accreditation_id,))
        if not existing:
            raise ValueError("Accreditation not found")

        payload = data.model_dump(exclude_unset=True) if hasattr(data, "model_dump") else dict(data)
        if "status" in payload and payload.get("status") is not None:
            if payload["status"] not in ("unverified", "current", "previous", "expired"):
                raise ValueError("Invalid accreditation status")
            if payload["status"] == "current":
                raise ValueError("Cannot set accreditation to current via update; use the verify endpoint")

        updates = {}
        for field, value in payload.items():
            if value is not None and field != "crops":
                updates[field] = value
        if "crops" in payload and payload.get("crops") is not None:
            # replace crops
            session.execute("DELETE FROM supplier_accreditation_crops WHERE accreditation_id = ?", (accreditation_id,))
            for crop in payload["crops"]:
                if crop and str(crop).strip():
                    session.insert(
                        "supplier_accreditation_crops",
                        {
                            "accreditation_id": accreditation_id,
                            "crop_name": str(crop).strip(),
                            "created_at": now_iso(),
                        },
                    )
        if not updates and "crops" not in payload:
            return {"message": "No changes"}

        with session.transaction():
            session.update("supplier_accreditations", accreditation_id, updates)
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="update", entity_type="supplier_accreditation", entity_id=accreditation_id),
        )
        return {"message": "Accreditation updated successfully"}
    finally:
        conn.close()



def verify_accreditation(accreditation_id: int, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        existing = session.fetch_one("SELECT * FROM supplier_accreditations WHERE id = ?", (accreditation_id,))
        if not existing:
            raise ValueError("Accreditation not found")

        existing = dict(existing)
        # Check validity date
        validity = existing.get("validity_date")
        if validity:
            from datetime import datetime
            try:
                vdate = datetime.fromisoformat(validity.replace("Z", "+00:00"))
                if vdate < (datetime.now(vdate.tzinfo) if vdate.tzinfo else datetime.now()):
                    raise ValueError("Accreditation is expired; cannot verify")
            except ValueError:
                raise
            except Exception:
                pass

        # Require source reference or document
        if not existing.get("source_document") and not existing.get("source_reference"):
            raise ValueError("Accreditation requires a source document or source reference to be verified")

        with session.transaction():
            session.update("supplier_accreditations", accreditation_id, {"status": "current"})
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="verify", entity_type="supplier_accreditation", entity_id=accreditation_id, details="verified"),
        )
        return {"message": "Accreditation verified successfully"}
    finally:
        conn.close()


def delete_accreditation(accreditation_id: int, current_user: dict) -> dict:
    conn = get_db()
    try:
        session = DatabaseSession(conn)
        existing = session.fetch_one("SELECT id FROM supplier_accreditations WHERE id = ?", (accreditation_id,))
        if not existing:
            raise ValueError("Accreditation not found")
        with session.transaction():
            session.execute("DELETE FROM supplier_accreditation_crops WHERE accreditation_id = ?", (accreditation_id,))
            session.delete("supplier_accreditations", accreditation_id)
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="delete", entity_type="supplier_accreditation", entity_id=accreditation_id),
        )
        return {"message": "Accreditation deleted successfully"}
    finally:
        conn.close()
