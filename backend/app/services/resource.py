import json
from typing import Optional

from app.schemas.resource import ResourceCreate, ResourceUpdate
from app.services.base import connection, now_iso, execute_update
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate


def _validate_url(url: Optional[str]) -> None:
    if not isinstance(url, str):
        return
    trimmed = url.strip()
    if not trimmed:
        return
    if trimmed.lower().startswith("javascript:"):
        raise ValueError("Invalid resource URL: javascript: URLs are not allowed")


def _resource_row_to_response(row: dict) -> dict:
    is_active = row.get("is_active")
    if is_active is None:
        is_active = bool(row.get("is_verified", 0))
    metadata = row.get("metadata")
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
        except (json.JSONDecodeError, TypeError):
            metadata = {}
    elif metadata is None:
        metadata = {}
    return {
        "id": row.get("id"),
        "title": row.get("title"),
        "title_ar": row.get("title_ar"),
        "description": row.get("description"),
        "description_ar": row.get("description_ar"),
        "resource_type": row.get("resource_type") or row.get("category"),
        "category": row.get("category"),
        "url": row.get("url"),
        "country": row.get("country"),
        "metadata": metadata,
        "is_active": is_active,
        "file_path": row.get("file_path"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "created_by": row.get("created_by"),
    }


def list_resources(
    resource_type: Optional[str] = None,
    category: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    with connection() as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM resources WHERE (is_active = 1)"
        params = []
        if resource_type:
            query += " AND resource_type = ?"
            params.append(resource_type)
        if category:
            query += " AND category = ?"
            params.append(category)
        if country:
            query += " AND country = ?"
            params.append(country)
        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [_resource_row_to_response(dict(r)) for r in rows]


def search_resources(q: str) -> list[dict]:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM resources WHERE (is_active = 1) AND 
               (title LIKE ? OR title_ar LIKE ? OR description LIKE ? OR description_ar LIKE ?
                OR category LIKE ? OR country LIKE ?)""",
            [f"%{q}%"] * 6
        )
        rows = cursor.fetchall()
        return [_resource_row_to_response(dict(r)) for r in rows]


def get_resource(resource_id: int) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resources WHERE id = ? AND (is_active = 1)", (resource_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Resource not found")
        return _resource_row_to_response(dict(row))


def create_resource(data: ResourceCreate, current_user: dict) -> dict:
    _validate_url(data.url)
    with connection() as conn:
        cursor = conn.cursor()
        now = now_iso()
        cursor.execute(
            """INSERT INTO resources (title, title_ar, description, description_ar, resource_type, category,
               url, country, metadata, is_active, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (data.title, data.title_ar, data.description, data.description_ar, data.resource_type,
             data.category or "other", data.url, data.country, str(data.metadata) if data.metadata else "{}", 1, now, current_user["id"])
        )
        conn.commit()
        res_id = cursor.lastrowid
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="create", entity_type="resource", entity_id=res_id, details=data.title),
        )
        return {"id": res_id, "message": "Resource created successfully"}


def update_resource(resource_id: int, data: ResourceUpdate, current_user: dict) -> dict:
    _validate_url(data.url)
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM resources WHERE id = ?", (resource_id,))
        if not cursor.fetchone():
            raise ValueError("Resource not found")
        if not execute_update(
            conn=conn,
            table_name="resources",
            record_id=resource_id,
            data=data,
            coerce_fields={"metadata": lambda v: str(v) if isinstance(v, dict) else v},
        ):
            return {"message": "No changes"}
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="update", entity_type="resource", entity_id=resource_id),
        )
        return {"message": "Resource updated successfully"}


def delete_resource(resource_id: int, current_user: dict) -> dict:
    with connection() as conn:
        if not execute_update(
            conn=conn,
            table_name="resources",
            record_id=resource_id,
            data=None,
            extra_fields={"is_active": 0},
        ):
            return {"message": "No changes"}
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="delete", entity_type="resource", entity_id=resource_id),
        )
        return {"message": "Resource deactivated successfully"}
