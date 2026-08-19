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

    # ========== ZATCA External Source Adapter (WP-38c Task 2) ==========
    ZATCA_BASE_URL: str = ""
    ZATCA_API_KEY: str = ""
    ZATCA_TIMEOUT_SECONDS: float = 30.0
    ZATCA_SOURCE_ID: str = "zatca"
    ZATCA_SOURCE_NAME: str = "ZATCA Open Data APIs"
    ZATCA_SOURCE_TYPE: str = "external_trade_intelligence"
    ZATCA_SOURCE_VERSION: str = "1.0"

    # ========== FAOSTAT External Source Adapter (Portfolio Re-Evaluation Task 3) ==========
    FAOSTAT_BASE_URL: str = "https://faostatservices.fao.org/api/v1"
    FAOSTAT_USER: str = ""
    FAOSTAT_PASSWORD: str = ""
    FAOSTAT_TIMEOUT_SECONDS: float = 30.0
    FAOSTAT_SOURCE_ID: str = "faostat"
    FAOSTAT_SOURCE_NAME: str = "FAOSTAT External Knowledge"
    FAOSTAT_SOURCE_TYPE: str = "external_agrifood_intelligence"
    FAOSTAT_SOURCE_VERSION: str = "1.0.0"
    FAOSTAT_DEFAULT_DOMAIN: str = "QCL"
    FAOSTAT_FPI_DOMAIN: str = "CP"

    # ========== GCC-Stat External Source Adapter (WP-38d Task 2) ==========
    GCCSTAT_BASE_URL: str = ""
    GCCSTAT_API_KEY: str = ""
    GCCSTAT_TIMEOUT_SECONDS: float = 30.0
    GCCSTAT_SOURCE_ID: str = "gccstat"
    GCCSTAT_SOURCE_NAME: str = "GCC-Stat Data Portal"
    GCCSTAT_SOURCE_TYPE: str = "external_trade_intelligence"
    GCCSTAT_SOURCE_VERSION: str = "1.0"

    # ========== UN Comtrade External Source Adapter (WP-UN-Comtrade) ==========
    UN_COMTRADE_BASE_URL: str = "https://comtradeapi.un.org"
    UN_COMTRADE_API_KEY: str = ""
    UN_COMTRADE_TIMEOUT_SECONDS: float = 30.0
    UN_COMTRADE_SOURCE_ID: str = "un-comtrade"
    UN_COMTRADE_SOURCE_NAME: str = "UN Comtrade External Knowledge"
    UN_COMTRADE_SOURCE_TYPE: str = "external_trade_intelligence"
    UN_COMTRADE_SOURCE_VERSION: str = "1.0.0"
    UN_COMTRADE_UPDATED_AT: str = "2026-08-15"

    # ========== WTO ePing External Source Adapter (Evidence Verification) ==========
    WTO_EPING_BASE_URL: str = "https://api.wto.org/eping"
    WTO_EPING_API_KEY: str = ""
    WTO_EPING_TIMEOUT_SECONDS: float = 30.0
    WTO_EPING_SOURCE_ID: str = "wto-eping"
    WTO_EPING_SOURCE_NAME: str = "WTO ePing External Knowledge"
    WTO_EPING_SOURCE_TYPE: str = "external_regulatory_intelligence"
    WTO_EPING_SOURCE_VERSION: str = "1.0.0"
    WTO_EPING_UPDATED_AT: str = ""

    # ========== World Bank LPI External Source Adapter (Portfolio Re-Evaluation Phase 1) ==========
    WORLDBANK_LPI_BASE_URL: str = "https://api.worldbank.org/v2"
    WORLDBANK_LPI_TIMEOUT_SECONDS: float = 30.0
    WORLDBANK_LPI_SOURCE_ID: str = "worldbank-lpi"
    WORLDBANK_LPI_SOURCE_NAME: str = "World Bank Logistics Performance Index"
    WORLDBANK_LPI_SOURCE_TYPE: str = "external_logistics_intelligence"
    WORLDBANK_LPI_SOURCE_VERSION: str = "1.0.0"
    WORLDBANK_LPI_UPDATED_AT: str = ""

    # ========== Knowledge Orchestration / Fusion Layer ==========
    KNOWLEDGE_ORCHESTRATION_ENABLED: bool = True
    KNOWLEDGE_ORCHESTRATION_DEDUP_ENABLED: bool = True
    KNOWLEDGE_ORCHESTRATION_MIN_PRIMARY_RESULTS: int = 3  # Post-MVP: not wired in MVP implementation
    KNOWLEDGE_ORCHESTRATION_MAX_RESULTS: int = 10
    KNOWLEDGE_ORCHESTRATION_CONFLICT_STRATEGY: str = "latest_official_wins"

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


