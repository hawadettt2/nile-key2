from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from typing import Optional

from app.core.database import get_db
from app.routers.auth import get_current_user, require_role
from app.schemas.resource import ResourceCreate, ResourceUpdate

router = APIRouter(prefix="/api/v1/resources", tags=["Resources"])


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
    query = "SELECT * FROM resources WHERE is_active = 1"
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
    return [dict(r) for r in rows]


@router.get("/search", response_model=list)
def search_resources(
    q: str,
    current_user: dict = Depends(get_current_user)
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT * FROM resources WHERE is_active = 1 AND 
           (title LIKE ? OR title_ar LIKE ? OR description LIKE ? OR description_ar LIKE ?
            OR category LIKE ? OR country LIKE ?)""",
        [f"%{q}%"] * 6
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/{resource_id}", response_model=dict)
def get_resource(resource_id: int, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Resource not found")
    return dict(row)


@router.post("/", response_model=dict)
def create_resource(data: ResourceCreate, current_user: dict = Depends(require_role(["Owner", "Manager", "Admin Staff"]))):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """INSERT INTO resources (title, title_ar, description, description_ar, resource_type, category,
           url, country, metadata, is_active, created_at, created_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (data.title, data.title_ar, data.description, data.description_ar, data.resource_type,
         data.category, data.url, data.country, str(data.metadata) if data.metadata else "{}", 1, now, current_user["id"])
    )
    conn.commit()
    res_id = cursor.lastrowid
    conn.close()
    return {"id": res_id, "message": "Resource created successfully"}


@router.put("/{resource_id}", response_model=dict)
def update_resource(resource_id: int, data: ResourceUpdate, current_user: dict = Depends(require_role(["Owner", "Manager", "Admin Staff"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM resources WHERE id = ?", (resource_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Resource not found")
    fields = []
    values = []
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            fields.append(f"{field} = ?")
            if field == "metadata" and isinstance(value, dict):
                values.append(str(value))
            else:
                values.append(value)
    if not fields:
        conn.close()
        return {"message": "No changes"}
    values.append(resource_id)
    cursor.execute(f"UPDATE resources SET {', '.join(fields)}, updated_at = ? WHERE id = ?",
                   (*values, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return {"message": "Resource updated successfully"}


@router.delete("/{resource_id}", response_model=dict)
def delete_resource(resource_id: int, current_user: dict = Depends(require_role(["Owner", "Manager"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE resources SET is_active = 0, updated_at = ? WHERE id = ?",
                   (datetime.utcnow().isoformat(), resource_id))
    conn.commit()
    conn.close()
    return {"message": "Resource deactivated successfully"}
