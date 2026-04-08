"""
DC86 Stream Toolkit - Datenbank-Setup
Async SQLAlchemy Engine + Session-Management.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# ── Async Engine ──
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # SQL-Logging im Debug-Modus
    pool_size=10,
    max_overflow=20,
)

# ── Session Factory ──
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Base Model ──
class Base(DeclarativeBase):
    """Basis-Klasse für alle SQLAlchemy Models."""
    pass


# ── Dependency für FastAPI ──
async def get_db() -> AsyncSession:
    """Liefert eine DB-Session pro Request."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ── Tabellen erstellen (Dev-Modus) ──
async def init_db():
    """Erstellt alle Tabellen. Nur für Development!"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
