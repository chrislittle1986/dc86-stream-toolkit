"""
DC86 Stream Toolkit - FastAPI Backend
Hauptanwendung mit allen Routern und Middleware.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers.auth import router as auth_router
from app.routers.status import router as status_router
from app.routers.channel import router as channel_router
from app.routers.overlays import router as overlays_router
from app.routers.music import router as music_router

settings = get_settings()


# ── Startup / Shutdown ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle-Events: DB-Tabellen erstellen beim Start."""
    print("🚀 DC86 Stream Toolkit startet...")
    await init_db()
    print("✅ Datenbank initialisiert")
    print(f"🎮 API bereit: http://localhost:8000/docs")
    print(f"🎨 Overlays: http://localhost:8000/api/overlays")
    yield
    print("👋 DC86 Stream Toolkit fährt runter...")


# ── App erstellen ──
app = FastAPI(
    title="DC86 Stream Toolkit",
    description="Modulares Stream-Management-Toolkit für Twitch — by derchrist",
    version="0.2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Router einbinden ──
app.include_router(auth_router)
app.include_router(status_router)
app.include_router(channel_router)
app.include_router(overlays_router)
app.include_router(music_router)


# ── Root Endpoint ──
@app.get("/", tags=["Root"])
async def root():
    return {
        "app": "DC86 Stream Toolkit",
        "version": "0.2.0",
        "docs": "/docs",
        "status": "/api/status/health",
        "overlays": "/api/overlays",
        "message": "Willkommen beim DC86 Stream Toolkit! 🎮🔥",
    }
