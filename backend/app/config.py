"""
DC86 Stream Toolkit - Konfiguration
Alle Settings werden aus Environment-Variablen geladen.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Zentrale App-Konfiguration."""

    # ── App ──
    app_name: str = "DC86 Stream Toolkit"
    debug: bool = True

    # ── Twitch OAuth2 ──
    twitch_client_id: str = ""
    twitch_client_secret: str = ""
    twitch_redirect_uri: str = "http://localhost:8000/api/auth/callback"

    # ── Datenbank ──
    database_url: str = "postgresql+asyncpg://dc86:dc86secret@db:5432/dc86_toolkit"

    # ── Redis ──
    redis_url: str = "redis://redis:6379/0"

    # ── Security ──
    secret_key: str = "change-me-in-production-bitte"
    access_token_expire_minutes: int = 60 * 24  # 24 Stunden

    # ── Frontend ──
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached Settings-Instanz."""
    return Settings()
