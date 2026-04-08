"""
DC86 Stream Toolkit - Channel Router
Stream-Infos abrufen, Titel/Game ändern, Live-Status checken.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.models.user import User
from app.services.auth import get_current_user
from app.services.twitch import get_channel_info, update_channel_info, get_stream_info

router = APIRouter(prefix="/api/channel", tags=["Channel"])


# ── Schemas ──
class ChannelUpdateRequest(BaseModel):
    """Request-Body für Channel-Update."""
    title: str | None = None
    game_id: str | None = None
    tags: list[str] | None = None


# ── Endpoints ──
@router.get("/info")
async def channel_info(user: User = Depends(get_current_user)):
    """Holt aktuelle Channel-Infos (Titel, Game, Tags)."""
    if not user.twitch_access_token:
        raise HTTPException(status_code=401, detail="Kein Twitch-Token vorhanden")

    info = await get_channel_info(user.twitch_access_token, user.twitch_id)
    if not info:
        raise HTTPException(status_code=404, detail="Channel nicht gefunden")

    return {
        "broadcaster_id": info.get("broadcaster_id"),
        "broadcaster_name": info.get("broadcaster_name"),
        "title": info.get("title"),
        "game_name": info.get("game_name"),
        "game_id": info.get("game_id"),
        "tags": info.get("tags", []),
        "broadcaster_language": info.get("broadcaster_language"),
    }


@router.patch("/update")
async def update_channel(
    body: ChannelUpdateRequest,
    user: User = Depends(get_current_user),
):
    """Aktualisiert Channel-Titel, Game und/oder Tags."""
    if not user.twitch_access_token:
        raise HTTPException(status_code=401, detail="Kein Twitch-Token vorhanden")

    success = await update_channel_info(
        access_token=user.twitch_access_token,
        broadcaster_id=user.twitch_id,
        title=body.title,
        game_id=body.game_id,
        tags=body.tags,
    )

    if not success:
        raise HTTPException(status_code=400, detail="Channel-Update fehlgeschlagen")

    return {"message": "Channel erfolgreich aktualisiert!", "updated": body.model_dump(exclude_none=True)}


@router.get("/live")
async def live_status(user: User = Depends(get_current_user)):
    """Prüft ob der Stream gerade live ist."""
    if not user.twitch_access_token:
        raise HTTPException(status_code=401, detail="Kein Twitch-Token vorhanden")

    stream = await get_stream_info(user.twitch_access_token, user.twitch_id)

    if stream:
        return {
            "is_live": True,
            "title": stream.get("title"),
            "game_name": stream.get("game_name"),
            "viewer_count": stream.get("viewer_count"),
            "started_at": stream.get("started_at"),
            "thumbnail_url": stream.get("thumbnail_url"),
        }
    else:
        return {
            "is_live": False,
            "message": "Stream ist offline. Zeit für eine Runde WoW? 🐉",
        }
