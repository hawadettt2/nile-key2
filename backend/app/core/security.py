"""
أدوات الأمان:
- تشفير كلمات المرور (bcrypt)
- إنشاء وفك توكن JWT
- حماية هوية Project Owner
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from fastapi import HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# ========== إعدادات bcrypt ==========
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ========== دوال كلمات المرور ==========

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """التحقق من مطابقة كلمة المرور مع الـ Hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """إنشاء Hash لكلمة مرور جديدة"""
    return pwd_context.hash(password)


# ========== حماية Project Owner ==========

PROTECTED_OWNER_IDENTITY = {
    "username": "owner",
    "email": "owner@nile-key.com",
    "role": "owner",
}


def is_protected_owner(user: Optional[dict]) -> bool:
    """
    تحديد ما إذا كان المستخدم هو Project Owner المحمي.
    يعتمد على الهوية canonical (username + email + role) ولا يعتمد على user_id.
    """
    if not user:
        return False
    return (
        user.get("username") == PROTECTED_OWNER_IDENTITY["username"]
        and user.get("email") == PROTECTED_OWNER_IDENTITY["email"]
        and user.get("role") == PROTECTED_OWNER_IDENTITY["role"]
    )


def ensure_not_protected_owner(target_user: dict, current_user: Optional[dict] = None) -> None:
    """
    يرفع استثناء إذا كان المستخدم المستهدف هو Project Owner المحمي.
    - يُسمح للمالك نفسه بتعديل حسابه الشخصي.
    - لا يُسمح لأي شخص آخر (بما في ذلك المالك) بحذف حساب المالك.
    """
    if is_protected_owner(target_user):
        if current_user is None or not is_protected_owner(current_user):
            raise HTTPException(
                status_code=403,
                detail="Project Owner account is protected from this action"
            )


# ========== دوال JWT ==========

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    إنشاء Access Token (JWT)
    - المدة الافتراضية: 24 ساعة
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "iat": datetime.now(timezone.utc),  # issued at
    })
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    إنشاء Refresh Token
    - المدة: 7 أيام
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
    })
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """
    فك تشفير وفحص صحة التوكن
    - ترجع None إذا كان التوكن غير صالح أو منتهي
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True},
        )
        return payload
    except JWTError:
        return None
