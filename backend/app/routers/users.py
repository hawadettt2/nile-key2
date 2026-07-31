from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List

from app.core.database import get_db, execute_update
from app.core.security import get_password_hash
from app.routers.auth import get_current_user, require_role
from app.schemas.user import UserCreate, UserUpdate, User
from app.schemas.common import MessageResponse, IdResponse

router = APIRouter(prefix="/api/v1/users", tags=["Users Admin"])


@router.get("/", response_model=List[User])
def list_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(require_role(["owner", "manager"]))
):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE 1=1"
    params = []
    if search:
        query += " AND (username LIKE ? OR email LIKE ? OR full_name LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    if role:
        query += " AND role = ?"
        params.append(role)
    if status is not None:
        query += " AND is_active = ?"
        params.append(1 if status == "active" else 0)
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [_user_row_to_response(row) for row in rows]


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return _user_row_to_response(row)


@router.post("/", response_model=IdResponse)
def create_user(data: UserCreate, current_user: dict = Depends(require_role(["owner", "manager"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (data.email, data.username))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email or username already exists")
    hashed = get_password_hash(data.password)
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """INSERT INTO users (email, username, full_name, password_hash, role, phone, company, is_active, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (data.email, data.username, data.full_name, hashed, data.role, data.phone, data.company, 1, now)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return {"message": "User created successfully", "id": user_id}


@router.put("/{user_id}", response_model=MessageResponse)
def update_user(user_id: int, data: UserUpdate, current_user: dict = Depends(require_role(["owner", "manager"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    if not execute_update(conn=conn, table_name="users", record_id=user_id, data=data):
        conn.close()
        return {"message": "No changes"}
    conn.close()
    return {"message": "User updated successfully"}


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int, current_user: dict = Depends(require_role(["owner"]))):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "User deleted successfully"}


def _user_row_to_response(row) -> dict:
    return {
        "id": row["id"],
        "email": row["email"],
        "username": row["username"],
        "full_name": row["full_name"],
        "role": row["role"],
        "phone": row.get("phone"),
        "company": row.get("company"),
        "is_active": bool(row.get("is_active", 1)),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }
