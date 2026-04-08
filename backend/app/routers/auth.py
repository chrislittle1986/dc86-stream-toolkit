"""
DC86 Stream Toolkit - Auth Router
Twitch OAuth2 Login-Flow: Login → Twitch → Callback → JWT Token.
"""

import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.services.auth import create_access_token, get_current_user
from app.services.twitch import get_auth_url, exchange_code, get_user_info

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["Auth"])

# ── State-Storage (in Produktion: Redis verwenden) ──
_oauth_states: set[str] = set()


@router.get("/login")
async def login():
    """
    Startet den Twitch OAuth2 Flow.
    Redirected den User zur Twitch-Login-Seite.
    """
    state = secrets.token_urlsafe(32)
    _oauth_states.add(state)
    auth_url = get_auth_url(state)
    return RedirectResponse(url=auth_url)


@router.get("/callback")
async def callback(
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """
    Twitch OAuth2 Callback.
    Empfängt den Authorization Code und tauscht ihn gegen Tokens.
    """
    # ── Fehler von Twitch? ──
    if error:
        return RedirectResponse(
            url=f"{settings.frontend_url}/auth/error?error={error}"
        )

    # ── State validieren (CSRF-Schutz) ──
    if not state or state not in _oauth_states:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ungültiger OAuth State - möglicher CSRF-Angriff",
        )
    _oauth_states.discard(state)

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kein Authorization Code erhalten",
        )

    # ── Code gegen Tokens tauschen ──
    try:
        token_data = await exchange_code(code)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Twitch Token-Exchange fehlgeschlagen: {str(e)}",
        )

    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")

    # ── User-Info von Twitch holen ──
    try:
        twitch_user = await get_user_info(access_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Twitch User-Info fehlgeschlagen: {str(e)}",
        )

    if not twitch_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Twitch-User nicht gefunden",
        )

    # ── User in DB anlegen oder aktualisieren ──
    result = await db.execute(
        select(User).where(User.twitch_id == twitch_user["id"])
    )
    user = result.scalar_one_or_none()

    if user:
        # User existiert → Update
        user.username = twitch_user["login"]
        user.display_name = twitch_user["display_name"]
        user.email = twitch_user.get("email")
        user.profile_image_url = twitch_user.get("profile_image_url")
        user.twitch_access_token = access_token
        user.twitch_refresh_token = refresh_token
    else:
        # Neuer User → Erstellen
        user = User(
            twitch_id=twitch_user["id"],
            username=twitch_user["login"],
            display_name=twitch_user["display_name"],
            email=twitch_user.get("email"),
            profile_image_url=twitch_user.get("profile_image_url"),
            twitch_access_token=access_token,
            twitch_refresh_token=refresh_token,
        )
        db.add(user)

    await db.flush()

    # ── JWT Token erstellen ──
    jwt_token = create_access_token({
        "user_id": user.id,
        "twitch_id": user.twitch_id,
        "username": user.username,
    })

    # ── Redirect zum Frontend mit Token ──
    return RedirectResponse(
        url=f"{settings.frontend_url}/auth/success?token={jwt_token}"
    )


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    """
    Gibt den aktuell eingeloggten User zurück.
    Braucht einen gültigen JWT Token im Authorization Header.
    """
    return {
        "id": user.id,
        "twitch_id": user.twitch_id,
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
        "profile_image_url": user.profile_image_url,
        "is_broadcaster": user.is_broadcaster,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.post("/logout")
async def logout(user: User = Depends(get_current_user)):
    """
    Loggt den User aus (invalidiert den Token client-seitig).
    Server-seitig: In Produktion Token auf Blacklist setzen (Redis).
    """
    return {"message": f"Tschüss {user.display_name}! Bis zum nächsten Stream."}
