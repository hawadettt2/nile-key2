"""
أدوات الأمان:
- تشفير كلمات المرور (bcrypt)
- إنشاء وفك توكن JWT
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

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
