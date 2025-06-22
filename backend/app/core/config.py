# app/core/config.py
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# <repo‑root>/backend/app/core/config.py  →  repo root is three parents up
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # ------------------------------------------------------------------ #
    # Application
    # ------------------------------------------------------------------ #
    APP_NAME: str = "Ontario RRIF Planner API"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    TAX_YEARS_FILE: Path = Field(
        default=BASE_DIR / "data" / "tax_years.yml", env="TAX_YEARS_FILE"
    )

    # ------------------------------------------------------------------ #
    # FastAPI / CORS
    # ------------------------------------------------------------------ #
    API_PREFIX: str = Field(default="/api/v1", env="API_PREFIX")
    ALLOWED_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:5173"], env="ALLOWED_CORS_ORIGINS"
    )

    @field_validator("ALLOWED_CORS_ORIGINS", mode="before")
    @classmethod
    def _parse_origins(cls, v):
        """Parse CORS origins from environment."""
        if not v:
            return ["http://localhost:5173"]
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return ["http://localhost:5173"]
            if v.startswith("["):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    # ------------------------------------------------------------------ #
    # Database
    # ------------------------------------------------------------------ #
    SQLALCHEMY_DATABASE_URI: str = Field(
        default=f"sqlite+aiosqlite:///{BASE_DIR / 'rrif_dev.db'}", env="DB_URL"
    )
    SESSION_DATA_TTL_HOURS: int = Field(24, env="SESSION_DATA_TTL_HOURS")

    # ------------------------------------------------------------------ #
    # Security
    # ------------------------------------------------------------------ #
    CSRF_SECRET_KEY: str = Field("super‑dev‑csrf‑key", env="CSRF_SECRET_KEY")
    JWT_SECRET_KEY: str = Field("super‑dev‑jwt‑key", env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    API_KEY_SECRET_FOR_HMAC: Optional[str] = Field(
        default=None, env="API_KEY_SECRET_FOR_HMAC"
    )

    # ------------------------------------------------------------------ #
    # Email Configuration
    # ------------------------------------------------------------------ #
    RESEND_API_KEY: Optional[str] = Field(default=None, env="RESEND_API_KEY")
    SENDGRID_API_KEY: Optional[str] = Field(default=None, env="SENDGRID_API_KEY")
    FROM_EMAIL: str = Field(default="noreply@example.com", env="FROM_EMAIL")
    FROM_NAME: str = Field(default="RRIF Strategy Calculator", env="FROM_NAME")

    # ------------------------------------------------------------------ #
    # LLM
    # ------------------------------------------------------------------ #
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = Field("claude-3-haiku-20240307", env="ANTHROPIC_MODEL")
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    GEMINI_MODEL: str = Field("gemini-pro", env="GEMINI_MODEL")
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = Field("openai/o4-mini", env="OPENROUTER_MODEL")
    OPENROUTER_BASE_URL: str = Field("https://openrouter.ai/api/v1", env="OPENROUTER_BASE_URL")

    # ------------------------------------------------------------------ #
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
