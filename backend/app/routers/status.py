"""
DC86 Stream Toolkit - Status Router
Health-Check und System-Status Endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from app.config import get_settings
from app.database import get_db

settings = get_settings()
router = APIRouter(prefix="/api/status", tags=["Status"])


@router.get("/health")
async def health_check():
    """Einfacher Health-Check — gibt 200 zurück wenn API läuft."""
    return {
        "status": "online",
        "app": settings.app_name,
        "message": "DC86 Stream Toolkit läuft! 🎮",
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness-Check — prüft ob alle Services erreichbar sind.
    Checkt: PostgreSQL, Redis.
    """
    checks = {}

    # ── PostgreSQL Check ──
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = {"status": "connected", "type": "PostgreSQL"}
    except Exception as e:
        checks["database"] = {"status": "error", "error": str(e)}

    # ── Redis Check ──
    try:
        r = aioredis.from_url(settings.redis_url)
        await r.ping()
        await r.aclose()
        checks["cache"] = {"status": "connected", "type": "Redis"}
    except Exception as e:
        checks["cache"] = {"status": "error", "error": str(e)}

    # ── Twitch Config Check ──
    twitch_configured = bool(
        settings.twitch_client_id and settings.twitch_client_secret
    )
    checks["twitch"] = {
        "status": "configured" if twitch_configured else "not_configured",
        "hint": "TWITCH_CLIENT_ID und TWITCH_CLIENT_SECRET in .env setzen"
        if not twitch_configured
        else None,
    }

    all_ok = all(
        c.get("status") in ("connected", "configured")
        for c in checks.values()
    )

    return {
        "status": "ready" if all_ok else "degraded",
        "checks": checks,
    }
