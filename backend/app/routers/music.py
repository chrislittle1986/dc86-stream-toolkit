"""
DC86 Stream Toolkit - Music Router
Speichert die aktuelle YouTube URL in Redis und liefert
Titel + Thumbnail per oEmbed für das Now Playing Overlay.
"""

import httpx
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import redis.asyncio as aioredis
import os

router = APIRouter(prefix="/api/music", tags=["Music"])

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
REDIS_KEY  = "dc86:now_playing"


async def get_redis():
    return aioredis.from_url(REDIS_URL, decode_responses=True)


class MusicSet(BaseModel):
    url: str   # YouTube URL


async def fetch_oembed(url: str) -> dict:
    """Holt Titel + Thumbnail von YouTube oEmbed (kein API-Key nötig)."""
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    async with httpx.AsyncClient(timeout=5) as client:
        res = await client.get(oembed_url)
        res.raise_for_status()
        data = res.json()
        return {
            "title":      data.get("title", "Unbekannter Titel"),
            "author":     data.get("author_name", ""),
            "thumbnail":  data.get("thumbnail_url", ""),
            "url":        url,
        }


@router.post("/set")
async def set_now_playing(body: MusicSet):
    """
    Setzt den aktuellen Song. Wird vom Dashboard aufgerufen.
    Holt via oEmbed automatisch Titel + Thumbnail von YouTube.
    """
    if not body.url.strip():
        raise HTTPException(status_code=400, detail="URL darf nicht leer sein")

    try:
        info = await fetch_oembed(body.url)
    except Exception:
        # Fallback falls oEmbed nicht klappt
        info = {"title": "Lädt...", "author": "", "thumbnail": "", "url": body.url}

    r = await get_redis()
    await r.set(REDIS_KEY, json.dumps(info))
    await r.close()
    return {"status": "ok", **info}


@router.delete("/clear")
async def clear_now_playing():
    """Löscht den aktuellen Song (Overlay verschwindet)."""
    r = await get_redis()
    await r.delete(REDIS_KEY)
    await r.close()
    return {"status": "cleared"}


@router.get("/current")
async def get_now_playing():
    """
    Liefert den aktuellen Song für das Overlay.
    Rückgabe: { title, author, thumbnail, url } oder { active: false }
    """
    r = await get_redis()
    raw = await r.get(REDIS_KEY)
    await r.close()

    if not raw:
        return {"active": False}

    data = json.loads(raw)
    return {"active": True, **data}
