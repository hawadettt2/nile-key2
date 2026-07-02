from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional

from app.core.database import get_db, execute_update
from app.routers.auth import get_current_user, require_role
from app.schemas.resource import ResourceCreate, ResourceUpdate

router = APIRouter(prefix="/api/v1/resources", tags=["Resources"])


def _resource_row_to_response(row: dict) -> dict:
    """Compatibility layer: map DB row to API contract fields.
    
    LEGACY COMPATIBILITY:
    - Returns only backend contract fields
    - Legacy column `is_verified` maps to `is_active` when is_active is NULL
    - Legacy column `tags` maps to `metadata` as dict
    """
    is_active = row.get("is_active")
    if is_active is None:
        is_active = bool(row.get("is_verified", 0))
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
        "metadata": {"tags": row.get("tags")} if row.get("tags") else (row.get("metadata") if row.get("metadata") else {}),
        "is_active": is_active,
        "file_path": row.get("file_path"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
        "created_by": row.get("created_by"),
    }


@router.get("/", response_model=list)
def list_resources(
    resource_type: Optional[str] = None,
    category: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM resources WHERE (is_active = 1 OR is_verified = 1)"
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
    conn.close()
    return [_resource_row_to_response(dict(r)) for r in rows]


@router.get("/search", response_model=list)
def search_resources(
    q: str,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM resources WHERE (is_active = 1 OR is_verified = 1) AND 
           (title LIKE ? OR title_ar LIKE ? OR description LIKE ? OR description_ar LIKE ?
            OR category LIKE ? OR country LIKE ?)""",
        [f"%{q}%"] * 6
    )
    rows = cursor.fetchall()
    conn.close()
    return [_resource_row_to_response(dict(r)) for r in rows]


@router.get("/{resource_id}", response_model=dict)
def get_resource(resource_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resources WHERE id = ? AND (is_active = 1 OR is_verified = 1)", (resource_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Resource not found")
    return _resource_row_to_response(dict(row))


@router.post("/", response_model=dict)
def create_resource(data: ResourceCreate, current_user: dict = Depends(require_role(["owner", "manager", "admin_staff"]))):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """INSERT INTO resources (title, title_ar, description, description_ar, resource_type, category,
           url, country, metadata, is_active, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
(data.title, data.title_ar, data.description, data.description_ar, data.resource_type,
          data.category or "other", data.url, data.country, str(data.metadata) if data.metadata else "{}", 1, now, current_user["id"])
    )
    conn.commit()
    res_id = cursor.lastrowid
    conn.close()
    return {"id": res_id, "message": "Resource created successfully"}


@router.put("/{resource_id}", response_model=dict)
def update_resource(resource_id: int, data: ResourceUpdate, current_user: dict = Depends(require_role(["owner", "manager", "admin_staff"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM resources WHERE id = ?", (resource_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Resource not found")
    if not execute_update(
        conn=conn,
        table_name="resources",
        record_id=resource_id,
        data=data,
        coerce_fields={"metadata": lambda v: str(v) if isinstance(v, dict) else v},
    ):
        return {"message": "No changes"}
    return {"message": "Resource updated successfully"}


@router.delete("/{resource_id}", response_model=dict)
def delete_resource(resource_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE resources SET is_active = 0, updated_at = ? WHERE id = ?",
                   (datetime.utcnow().isoformat(), resource_id))
    conn.commit()
    conn.close()
    return {"message": "Resource deactivated successfully"}
