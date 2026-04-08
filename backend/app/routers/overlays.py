"""
DC86 Stream Toolkit - Overlays Router
Serviert die OBS Browser-Source Overlay-Dateien.
"""

from pathlib import Path
from fastapi import APIRouter, Query
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
import httpx
import os

from app.database import async_session
from app.models.user import User

router = APIRouter(prefix="/api/overlays", tags=["Overlays"])

# Overlay-Verzeichnis (gemountet via Docker Volume)
OVERLAYS_DIR = Path("/app/overlays")


@router.get("/followers")
async def get_followers(goal: int = Query(default=500, description="Follower-Ziel")):
    """
    Liefert den aktuellen Follower-Count von Twitch.
    Wird von der Goal Bar per ?api= Parameter automatisch gepollt.
    Holt den gespeicherten User-Token des Broadcasters aus der DB.
    Rückgabe: { "current": 123, "goal": 500 }
    """
    client_id = os.getenv("TWITCH_CLIENT_ID")
    channel   = os.getenv("TWITCH_CHANNEL", "derchrist86")

    if not client_id:
        return JSONResponse(status_code=500, content={"error": "TWITCH_CLIENT_ID fehlt"})

    # ── User-Token aus DB holen ──
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.username == channel)
        )
        user = result.scalar_one_or_none()

    if not user or not user.twitch_access_token:
        return JSONResponse(
            status_code=401,
            content={"error": f"Kein Token für '{channel}' — bitte einmal einloggen"}
        )

    access_token  = user.twitch_access_token
    broadcaster_id = user.twitch_id

    try:
        async with httpx.AsyncClient() as client:
            followers_res = await client.get(
                "https://api.twitch.tv/helix/channels/followers",
                params={"broadcaster_id": broadcaster_id},
                headers={
                    "Client-ID": client_id,
                    "Authorization": f"Bearer {access_token}",
                }
            )
            followers_res.raise_for_status()
            follower_count = followers_res.json().get("total", 0)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            return JSONResponse(
                status_code=401,
                content={"error": "Token abgelaufen — bitte neu einloggen"}
            )
        return JSONResponse(status_code=502, content={"error": f"Twitch API Fehler: {str(e)}"})
    except httpx.HTTPError as e:
        return JSONResponse(status_code=502, content={"error": f"Twitch API Fehler: {str(e)}"})

    return {"current": follower_count, "goal": goal}


@router.get("/")
async def list_overlays():
    """Listet alle verfügbaren Overlays mit ihren URLs."""
    overlays = {
        "goal-bar": {
            "name": "Goal Bar",
            "description": "Follower/Sub Goal Fortschrittsbalken",
            "url": "/api/overlays/goal-bar",
            "params": {
                "label": "Beschriftung (z.B. 'Follower Goal')",
                "goal": "Zielwert",
                "emoji": "Emoji vor dem Label",
                "color": "Farbschema: purple, mint, red, gold",
                "api": "API-Endpoint für Live-Daten",
            },
            "example": "/api/overlays/goal-bar?label=Follower%20Goal&goal=500&emoji=⭐&color=purple&api=http://localhost:8000/api/overlays/followers%3Fgoal%3D500",
        },
        "timer": {
            "name": "Countdown Timer",
            "description": "Countdown für Stream-Start, Events etc.",
            "url": "/api/overlays/timer",
            "params": {
                "minutes": "Countdown in Minuten",
                "label": "Überschrift",
                "finished": "Text wenn fertig",
                "mode": "default, compact, minimal",
            },
            "example": "/api/overlays/timer?minutes=10&label=Stream%20startet%20in&mode=default",
        },
        "alerts": {
            "name": "Alerts",
            "description": "Follow/Sub/Raid Alert-Animationen",
            "url": "/api/overlays/alerts",
            "params": {
                "duration": "Anzeigedauer in ms",
                "test": "Test-Alert: follow, sub, raid, bits, giftsub",
            },
            "example": "/api/overlays/alerts?test=follow&duration=5000",
        },
        "now-playing": {
            "name": "Now Playing",
            "description": "Aktuelle Musik von YouTube anzeigen",
            "url": "/api/overlays/now-playing",
            "params": {},
            "example": "/api/overlays/now-playing",
        },
    }
    return overlays


@router.get("/{overlay_name}")
async def get_overlay(overlay_name: str):
    """Serviert ein Overlay als HTML für OBS Browser-Source."""
    overlay_path = OVERLAYS_DIR / overlay_name / "index.html"

    if not overlay_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": f"Overlay '{overlay_name}' nicht gefunden"}
        )

    html = overlay_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html)
