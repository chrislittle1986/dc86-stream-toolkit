"""
DC86 Stream Toolkit - Twitch API Service
Handles OAuth2 Flow und Twitch Helix API Calls.
"""

import httpx
from urllib.parse import urlencode

from app.config import get_settings

settings = get_settings()

# ── Twitch API URLs ──
TWITCH_AUTH_URL = "https://id.twitch.tv/oauth2/authorize"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_VALIDATE_URL = "https://id.twitch.tv/oauth2/validate"
TWITCH_REVOKE_URL = "https://id.twitch.tv/oauth2/revoke"
TWITCH_HELIX_URL = "https://api.twitch.tv/helix"

# ── OAuth2 Scopes ──
# Scopes die wir für das Toolkit brauchen
SCOPES = [
    "user:read:email",           # E-Mail lesen
    "channel:manage:broadcast",  # Titel/Game ändern
    "channel:read:subscriptions",# Sub-Daten lesen
    "clips:edit",                # Clips erstellen
    "moderator:read:chatters",   # Chatter-Liste lesen
    "chat:read",                 # Chat lesen (Bot)
    "chat:edit",                 # Chat schreiben (Bot)
]


def get_auth_url(state: str) -> str:
    """
    Generiert die Twitch OAuth2 Authorization URL.
    Der User wird hierhin redirected zum Einloggen.
    """
    params = {
        "client_id": settings.twitch_client_id,
        "redirect_uri": settings.twitch_redirect_uri,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "state": state,
        "force_verify": "true",
    }
    return f"{TWITCH_AUTH_URL}?{urlencode(params)}"


async def exchange_code(code: str) -> dict:
    """
    Tauscht den Authorization Code gegen Access + Refresh Token.
    Wird nach dem Callback aufgerufen.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TWITCH_TOKEN_URL,
            data={
                "client_id": settings.twitch_client_id,
                "client_secret": settings.twitch_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.twitch_redirect_uri,
            },
        )
        response.raise_for_status()
        return response.json()


async def refresh_access_token(refresh_token: str) -> dict:
    """
    Erneuert einen abgelaufenen Access Token mit dem Refresh Token.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TWITCH_TOKEN_URL,
            data={
                "client_id": settings.twitch_client_id,
                "client_secret": settings.twitch_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        response.raise_for_status()
        return response.json()


async def get_user_info(access_token: str) -> dict:
    """
    Holt User-Infos von der Twitch Helix API.
    Gibt das erste User-Objekt zurück.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TWITCH_HELIX_URL}/users",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": settings.twitch_client_id,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0] if data["data"] else None


async def get_channel_info(access_token: str, broadcaster_id: str) -> dict:
    """
    Holt Channel-Infos (Titel, Game, Tags etc.).
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TWITCH_HELIX_URL}/channels",
            params={"broadcaster_id": broadcaster_id},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": settings.twitch_client_id,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0] if data["data"] else None


async def update_channel_info(
    access_token: str,
    broadcaster_id: str,
    title: str | None = None,
    game_id: str | None = None,
    tags: list[str] | None = None,
) -> bool:
    """
    Aktualisiert Channel-Infos (Titel, Game, Tags).
    Gibt True zurück wenn erfolgreich.
    """
    body = {}
    if title is not None:
        body["title"] = title
    if game_id is not None:
        body["game_id"] = game_id
    if tags is not None:
        body["tags"] = tags

    if not body:
        return False

    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f"{TWITCH_HELIX_URL}/channels",
            params={"broadcaster_id": broadcaster_id},
            json=body,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": settings.twitch_client_id,
            },
        )
        return response.status_code == 204


async def get_stream_info(access_token: str, user_id: str) -> dict | None:
    """
    Prüft ob ein Stream live ist und gibt Stream-Infos zurück.
    None = nicht live.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{TWITCH_HELIX_URL}/streams",
            params={"user_id": user_id},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Client-Id": settings.twitch_client_id,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0] if data["data"] else None
