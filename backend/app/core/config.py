"""
ط¥ط¹ط¯ط§ط¯ط§طھ ط§ظ„طھط·ط¨ظٹظ‚ â€” طھظڈط­ظ…ظ„ ظ…ظ† ظ…طھط؛ظٹط±ط§طھ ط§ظ„ط¨ظٹط¦ط©
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # ========== App ==========
    APP_NAME: str = "Digital Export Manager API"
    APP_VERSION: str = "1.0.0"
    DEBUG: str = "False"

    # ========== Security ==========
    SECRET_KEY: str

    # ========== Database ==========
    DATABASE_URL: str = "sqlite:///./nile_key.db"

    # ========== JWT ==========
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 ط³ط§ط¹ط©
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7       # 7 ط£ظٹط§ظ…
    ALGORITHM: str = "HS256"

    # ========== Cookies ==========
    ACCESS_TOKEN_COOKIE_NAME: str = "access_token"
    REFRESH_TOKEN_COOKIE_NAME: str = "refresh_token"
    COOKIE_SECURE: bool = False
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: Optional[str] = None

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

    # ========== SMTP ==========
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_USE_TLS: bool = True

    # ========== LLM ==========
    LLM_PROVIDER: str = "gemini"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gemini-2.0-flash"
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_MAX_RETRIES: int = 2

    # ========== Research Search Provider Router ==========
    SEARCH_STUB_FALLBACK: bool = False

    # ========== SearXNG (WP-36 â€” First Search Provider) ==========
    SEARXNG_BASE_URL: str = ""
    SEARXNG_API_KEY: str = ""
    SEARXNG_TIMEOUT_SECONDS: float = 10.0


    # ========== Moaah External Source Adapter (WP-38a Task 2) ==========
    MOAAH_BASE_URL: str = ""
    MOAAH_API_KEY: str = ""
    MOAAH_TIMEOUT_SECONDS: float = 10.0
    MOAAH_SOURCE_ID: str = "moaah"
    MOAAH_SOURCE_NAME: str = "Moaah External Knowledge"
    MOAAH_SOURCE_TYPE: str = "external"
    MOAAH_SOURCE_VERSION: str = "1.0.0"

    # ========== TradeData External Source Adapter (WP-38b Task 2) ==========
    TRADEDATA_BASE_URL: str = "https://api.tradedata.io"
    TRADEDATA_API_KEY: str = ""
    TRADEDATA_TIMEOUT_SECONDS: float = 30.0
    TRADEDATA_SOURCE_ID: str = "tradedata"
    TRADEDATA_SOURCE_NAME: str = "TradeData API"
    TRADEDATA_SOURCE_TYPE: str = "external_trade_intelligence"
    TRADEDATA_SOURCE_VERSION: str = "1.0"
    # ========== Knowledge Ingestion (WP-37) ==========
    REGULATIONS_FILE_PATH: str = "backend/data/regulations.json"

    # ========== CORS ==========
    ALLOWED_ORIGINS: List[str] = []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"

    def model_post_init(self, __context: object) -> None:
        if self.SECRET_KEY == "change-me-in-production" or len(self.SECRET_KEY) < 32:
            raise RuntimeError(
                "SECRET_KEY is not secure. "
                "Set a production-ready SECRET_KEY (at least 32 characters) "
                "and do not use 'change-me-in-production'."
            )
        if "*" in self.ALLOWED_ORIGINS:
            raise RuntimeError(
                "ALLOWED_ORIGINS must not contain '*'. "
                "Explicitly list allowed origins when allow_credentials=True."
            )


# ظ†ط³ط®ط© ظˆط­ظٹط¯ط© ظ…ظ† ط§ظ„ط¥ط¹ط¯ط§ط¯ط§طھ (Singleton)
settings = Settings()

