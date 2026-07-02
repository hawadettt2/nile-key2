"""
إعدادات التطبيق — تُحمل من متغيرات البيئة
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ========== App ==========
    APP_NAME: str = "Nile Key API"
    APP_VERSION: str = "1.0.0"
    DEBUG: str = "False"
    
    # ========== Security ==========
    SECRET_KEY: str
    
    # ========== Database ==========
    DATABASE_URL: str = "sqlite:///./nile_key.db"
    
    # ========== JWT ==========
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 ساعة
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7       # 7 أيام
    ALGORITHM: str = "HS256"
    
    # ========== LetMeShip API ==========
    LETME_API_ID: str = ""
    LETME_API_PASSWORD: str = ""
    
    # ========== SendCloud API ==========
    SENDCLOUD_PUBLIC_KEY: str = ""
    SENDCLOUD_SECRET_KEY: str = ""
    
    # ========== ETA (Egypt Tax Authority) ==========
    ETA_CLIENT_ID: str = ""
    ETA_CLIENT_SECRET: str = ""
    ETA_BASE_URL: str = "https://api.invoicing.eta.gov.eg"
    
    # ========== CORS ==========
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# نسخة وحيدة من الإعدادات (Singleton)
settings = Settings()
