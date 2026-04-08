"""
DC86 Stream Toolkit - User Model
Speichert Twitch-User-Daten und Auth-Tokens.
"""

from datetime import datetime
from sqlalchemy import String, DateTime, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    """Twitch-User mit OAuth2-Token-Daten."""

    __tablename__ = "users"

    # ── Identifikation ──
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    twitch_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100))
    display_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Twitch OAuth2 Tokens ──
    twitch_access_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    twitch_refresh_token: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Rollen ──
    is_broadcaster: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Timestamps ──
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<User {self.display_name} (twitch_id={self.twitch_id})>"
