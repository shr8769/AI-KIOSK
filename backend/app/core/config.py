from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI-Kiosk Backend"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"

    # SQLite
    SQLITE_DB_PATH: str = "./data/kiosk.db"
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/kiosk.db"

    # Session
    SESSION_TTL_SECONDS: int = 1800  # 30 minutes

    # Service flags (toggle real vs mock)
    USE_MOCK_SERVICES: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
