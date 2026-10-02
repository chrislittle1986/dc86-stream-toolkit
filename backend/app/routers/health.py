"""
DC86 Stream Toolkit - Health Router
Erweiterter Health-Check für externes Monitoring (DB, Redis, Bot).
"""

import time

from fastapi import APIRouter, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
import redis.asyncio as aioredis

from app.config import get_settings
from app.database import get_db

settings = get_settings()
router = APIRouter(tags=["Health"])

# Bot schreibt alle 30s einen Heartbeat — nach 3 verpassten Intervallen gilt er als tot.
BOT_HEARTBEAT_MAX_AGE = 90


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db), response: Response = None):
    """
    Zentraler Health-Check für Monitoring (Uptime-Kuma, Prometheus, etc.).
    Prüft Datenbank, Redis und ob der Bot noch einen aktuellen Heartbeat liefert.
    Gibt 200 wenn alles ok ist, sonst 503.
    """
    checks = {}

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"

    redis_client = None
    try:
        redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
        await redis_client.ping()
        checks["redis"] = "ok"

        heartbeat = await redis_client.get("bot:heartbeat")
        if heartbeat is None:
            checks["bot"] = "no heartbeat yet"
        else:
            age = time.time() - float(heartbeat)
            checks["bot"] = "ok" if age <= BOT_HEARTBEAT_MAX_AGE else f"stale ({age:.0f}s)"
    except Exception as e:
        checks["redis"] = f"error: {e}"
        checks["bot"] = "unknown (redis unreachable)"
    finally:
        if redis_client:
            await redis_client.aclose()

    all_ok = all(v == "ok" for v in checks.values())
    response.status_code = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ok" if all_ok else "degraded",
        "checks": checks,
    }
