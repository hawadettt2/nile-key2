from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime
import os
import sqlite3

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.database import get_db, execute_update
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.schemas.user import UserCreate, UserLogin, UserUpdate, User, Token, RegisterResponse
from app.schemas.common import MessageResponse
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


def _is_token_blacklisted(token: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM token_blacklist WHERE token = ?", (token,))
    row = cursor.fetchone()
    conn.close()
    return row is not None


def _rate_limit(limit_str: str):
    def decorator(func):
        db_url = os.environ.get("DATABASE_URL", "")
        if "test" in db_url.lower() or os.environ.get("DISABLE_RATE_LIMIT") == "true":
            return func
        return limiter.limit(limit_str)(func)
    return decorator


security = HTTPBearer(auto_error=False)


def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    if not token and credentials:
        token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if _is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="Token has been revoked")
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, username, full_name, phone, company, role, is_active, approval_status, created_at, updated_at "
        "FROM users WHERE id = ? AND is_active = 1",
        (int(user_id),),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return {
        "id": row["id"],
        "email": row["email"],
        "username": row["username"],
        "full_name": row["full_name"],
        "phone": row["phone"],
        "company": row["company"],
        "role": row["role"],
        "is_active": bool(row["is_active"]),
        "approval_status": row["approval_status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def require_role(allowed_roles: list):
    def checker(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return checker


@router.post("/register", response_model=RegisterResponse)
@_rate_limit("5/minute")
def register(user_data: UserCreate, request: Request):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (user_data.email, user_data.username))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Email or username already exists")
    hashed = get_password_hash(user_data.password)
    now = datetime.utcnow().isoformat()
    cursor.execute(
        """INSERT INTO users (email, username, full_name, password_hash, phone, company, is_active, approval_status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_data.email, user_data.username, user_data.full_name, hashed,
         user_data.phone, user_data.company, 0, 'pending', now)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return {"message": "Registration pending approval", "user_id": user_id}


@router.post("/login", response_model=Token)
@_rate_limit("5/minute")
def login(credentials: UserLogin, request: Request, response: Response):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, email, username, password_hash, full_name, phone, company, role, is_active, approval_status, created_at, updated_at "
        "FROM users WHERE username = ? OR email = ?",
        (credentials.username, credentials.username),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    user = dict(row)
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    if user.get("approval_status") == "pending":
        raise HTTPException(status_code=403, detail="Your account is pending approval. Please wait for an administrator to approve your registration.")
    if not user.get("is_active"):
        raise HTTPException(status_code=403, detail="Your account is inactive. Please contact an administrator.")
    access = create_access_token({"sub": str(user["id"]), "role": user["role"]})
    refresh = create_refresh_token({"sub": str(user["id"])})
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    return Token(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=Token)
@_rate_limit("5/minute")
def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security), request: Request = None, response: Response = None):
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    token = credentials.credentials
    payload = decode_token(token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = payload.get("sub")
    access = create_access_token({"sub": user_id})
    refresh = create_refresh_token({"sub": user_id})
    response.set_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        value=access,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        domain=settings.COOKIE_DOMAIN,
        path="/",
    )
    return Token(access_token=access, refresh_token=refresh)


@router.get("/me", response_model=User)
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "username": current_user["username"],
        "full_name": current_user["full_name"],
        "role": current_user["role"],
        "phone": current_user["phone"],
        "company": current_user["company"],
        "is_active": bool(current_user["is_active"]),
        "approval_status": current_user.get("approval_status"),
        "created_at": current_user.get("created_at"),
        "updated_at": current_user.get("updated_at"),
    }


@router.put("/me", response_model=MessageResponse)
def update_me(update: UserUpdate, current_user: dict = Depends(get_current_user)):
    conn = get_db()
    cursor = conn.cursor()
    if not execute_update(
        conn=conn,
        table_name="users",
        record_id=current_user["id"],
        data=update,
    ):
        return {"message": "No changes"}
    return {"message": "Profile updated successfully"}


@router.post("/logout", response_model=MessageResponse)
def logout(request: Request, response: Response, current_user: dict = Depends(get_current_user)):
    token = request.cookies.get(settings.ACCESS_TOKEN_COOKIE_NAME)
    if not token:
        auth_header = request.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:]
    if token:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO token_blacklist (token, user_id, reason) VALUES (?, ?, ?)",
            (token, current_user["id"], "logout"),
        )
        conn.commit()
        conn.close()
    response.delete_cookie(
        key=settings.ACCESS_TOKEN_COOKIE_NAME,
        domain=settings.COOKIE_DOMAIN,
        path="/",
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    response.delete_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        domain=settings.COOKIE_DOMAIN,
        path="/",
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    try:
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(action="logout", entity_type="auth", entity_id=current_user["id"], details="User logged out"),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
    except Exception:
        pass
    return {"message": "Logged out successfully"}
