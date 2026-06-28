from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    SECRET_KEY: str = "nile-key-dev-secret-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATABASE_URL: str = "sqlite:///./nile_key.db"
    ALLOWED_ORIGINS: str = "http://localhost:5173,https://nile-key.com"
    RATE_LIMIT_PER_MINUTE: int = 100
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
