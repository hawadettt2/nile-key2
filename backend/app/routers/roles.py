from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from app.core.database import get_db
from app.routers.auth import get_current_user, require_role
from app.schemas.role import RoleCreate, RoleUpdate, Role
from app.schemas.common import MessageResponse, IdResponse

router = APIRouter(prefix="/api/v1/roles", tags=["Roles Admin"])


@router.get("/", response_model=List[Role])
def list_roles(
    search: Optional[str] = None,
    current_user: dict = Depends(require_role(["owner", "manager"]))
):
    conn = get_db()
    cursor = conn.cursor()
    if search:
        cursor.execute("SELECT * FROM roles WHERE name LIKE ? OR description LIKE ? ORDER BY id DESC", (f"%{search}%", f"%{search}%"))
    else:
        cursor.execute("SELECT * FROM roles ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [_role_row_to_response(row) for row in rows]


@router.get("/{role_id}", response_model=Role)
def get_role(role_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roles WHERE id = ?", (role_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Role not found")
    return _role_row_to_response(row)


@router.post("/", response_model=IdResponse)
def create_role(data: RoleCreate, current_user: dict = Depends(require_role(["owner"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM roles WHERE name = ?", (data.name,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Role already exists")
    cursor.execute(
        "INSERT INTO roles (name, permissions, description) VALUES (?, ?, ?)",
        (data.name, data.permissions, data.description)
    )
    conn.commit()
    role_id = cursor.lastrowid
    conn.close()
    return {"message": "Role created successfully", "id": role_id}


@router.put("/{role_id}", response_model=MessageResponse)
def update_role(role_id: int, data: RoleUpdate, current_user: dict = Depends(require_role(["owner"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roles WHERE id = ?", (role_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Role not found")
    if data.name:
        cursor.execute("SELECT id FROM roles WHERE name = ? AND id != ?", (data.name, role_id))
        if cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=400, detail="Role name already exists")
    fields = []
    values = []
    if data.name is not None:
        fields.append("name = ?")
        values.append(data.name)
    if data.permissions is not None:
        fields.append("permissions = ?")
        values.append(data.permissions)
    if data.description is not None:
        fields.append("description = ?")
        values.append(data.description)
    if fields:
        values.append(role_id)
        cursor.execute(f"UPDATE roles SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
    conn.close()
    return {"message": "Role updated successfully"}


@router.delete("/{role_id}", response_model=MessageResponse)
def delete_role(role_id: int, current_user: dict = Depends(require_role(["owner"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM roles WHERE id = ?", (role_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Role not found")
    cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
    conn.commit()
    conn.close()
    return {"message": "Role deleted successfully"}


def _role_row_to_response(row) -> dict:
    return {
        "id": row["id"],
        "name": row["name"],
        "permissions": row["permissions"],
        "description": row.get("description"),
    }
