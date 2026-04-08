"""
DC86 Stream Toolkit - Auth Service
JWT Token-Erstellung und Validierung für interne API-Auth.
"""

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.user import User

settings = get_settings()
security = HTTPBearer()

# ── JWT Config ──
ALGORITHM = "HS256"


def create_access_token(data: dict) -> str:
    """
    Erstellt einen JWT Access Token.
    Payload enthält user_id und twitch_id.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Dekodiert und validiert einen JWT Token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token ungültig oder abgelaufen",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI Dependency: Gibt den aktuellen User zurück.
    Wird in geschützten Routen als Dependency verwendet.

    Beispiel:
        @router.get("/me")
        async def me(user: User = Depends(get_current_user)):
            return user
    """
    payload = decode_token(credentials.credentials)
    twitch_id = payload.get("twitch_id")

    if not twitch_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Token-Payload",
        )

    result = await db.execute(
        select(User).where(User.twitch_id == twitch_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User nicht gefunden",
        )

    return user
