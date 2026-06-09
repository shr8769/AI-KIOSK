"""
Application Configuration
Owner: Harsha (Engineering Lead)

All configuration is loaded from environment variables (via .env file).
Never hardcode secrets here.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # ─── LLM ────────────────────────────────────────────────────────────────
    OPENAI_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gpt-4o"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ─── Backend ─────────────────────────────────────────────────────────────
    BACKEND_HOST: str = "localhost"
    BACKEND_PORT: int = 8000
    SECRET_KEY: str = "change-me-to-random-string"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # ─── Database ────────────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite:///./vidyasahayak.db"
    REDIS_URL: str = "redis://localhost:6379"

    # ─── Vector Store ────────────────────────────────────────────────────────
    CHROMA_PERSIST_DIR: str = "./knowledge/vectorstore"
    CHROMA_COLLECTION_NAME: str = "vidyasahayak_kb"

    # ─── Speech ──────────────────────────────────────────────────────────────
    WHISPER_MODEL_SIZE: str = "medium"
    TTS_ENGINE: str = "coqui"

    # ─── Camera / Detection ──────────────────────────────────────────────────
    CAMERA_INDEX: int = 0
    DETECTION_CONFIDENCE: float = 0.6
    PRESENCE_DURATION_SEC: float = 1.5

    # ─── Feature Flags ───────────────────────────────────────────────────────
    # Set to false to use mocks during development
    USE_REAL_DETECTOR: bool = False
    USE_REAL_RIAR: bool = False
    USE_REAL_AGENTS: bool = False
    USE_REAL_ASR: bool = False
    USE_REAL_TTS: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
