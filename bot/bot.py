"""
DC86 Stream Toolkit - Twitch Chat-Bot
Hauptdatei: Verbindet sich mit Twitch IRC und lädt alle Cogs (Module).

Usage:
    python bot.py
"""

import os
import asyncio
from dotenv import load_dotenv
from twitchio.ext import commands
import redis.asyncio as aioredis

load_dotenv()

# ── Config ──
BOT_TOKEN = os.getenv("TWITCH_BOT_TOKEN", "")
BOT_PREFIX = os.getenv("BOT_PREFIX", "!")
CHANNEL_NAME = os.getenv("TWITCH_CHANNEL", "derchrist")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
API_URL = os.getenv("API_URL", "http://backend:8000")


class DC86Bot(commands.Bot):
    """
    DC86 Stream Toolkit Chat-Bot.
    Modularer Bot mit Cog-System für Commands, Games und Moderation.
    """

    def __init__(self):
        super().__init__(
            token=BOT_TOKEN,
            prefix=BOT_PREFIX,
            initial_channels=[CHANNEL_NAME],
        )
        self.redis = None
        self.api_url = API_URL
        self.channel_name = CHANNEL_NAME

    async def event_ready(self):
        """Bot ist verbunden und bereit."""
        print(f"""
╔═══════════════════════════════════════════════╗
║   DC86 Bot ist online! 🤖                     ║
║   User:    {self.nick:<35} ║
║   Channel: {self.channel_name:<35} ║
╚═══════════════════════════════════════════════╝
        """)

        # Redis verbinden
        try:
            self.redis = aioredis.from_url(REDIS_URL, decode_responses=True)
            await self.redis.ping()
            print("✅ Redis verbunden")
        except Exception as e:
            print(f"⚠️  Redis nicht erreichbar: {e}")
            print("   Bot läuft ohne Cooldowns/Persistenz")
            self.redis = None

        # Cogs laden
        cogs = ["cogs.basic", "cogs.wow_games", "cogs.moderation", "cogs.alerts"]
        for cog in cogs:
            try:
                self.load_module(cog)
                print(f"✅ Cog geladen: {cog}")
            except Exception as e:
                print(f"❌ Cog Fehler ({cog}): {e}")

    async def event_message(self, message):
        """Wird bei jeder Chat-Nachricht aufgerufen."""
        # Eigene Nachrichten ignorieren
        if message.echo:
            return

        # Commands verarbeiten
        await self.handle_commands(message)

    async def event_command_error(self, context, error):
        """Fehlerbehandlung für Commands."""
        if isinstance(error, commands.CommandNotFound):
            return  # Unbekannte Commands still ignorieren
        elif isinstance(error, commands.CommandOnCooldown):
            await context.send(
                f"⏳ {context.author.name}, warte noch {error.retry_after:.0f}s!"
            )
        else:
            print(f"Command-Fehler: {error}")

    # ── Cooldown Helper ──
    async def check_cooldown(self, key: str, seconds: int) -> bool:
        """
        Prüft ob ein Cooldown aktiv ist.
        Returns True wenn der Command ausgeführt werden darf.
        """
        if not self.redis:
            return True  # Ohne Redis: kein Cooldown

        exists = await self.redis.exists(f"cd:{key}")
        if exists:
            return False

        await self.redis.setex(f"cd:{key}", seconds, "1")
        return True

    # ── Counter Helper ──
    async def increment_counter(self, key: str) -> int:
        """Erhöht einen Counter in Redis und gibt den neuen Wert zurück."""
        if not self.redis:
            return 0
        return await self.redis.incr(f"counter:{key}")

    async def get_counter(self, key: str) -> int:
        """Liest einen Counter aus Redis."""
        if not self.redis:
            return 0
        val = await self.redis.get(f"counter:{key}")
        return int(val) if val else 0


# ── Start ──
def main():
    if not BOT_TOKEN:
        print("❌ TWITCH_BOT_TOKEN nicht gesetzt!")
        print("   Generiere einen Token: https://twitchtokengenerator.com/")
        print("   Oder nutz den OAuth Token vom Toolkit-Login.")
        print("   Trag ihn in die .env ein: TWITCH_BOT_TOKEN=oauth:xxxxx")
        return

    bot = DC86Bot()
    bot.run()


if __name__ == "__main__":
    main()
