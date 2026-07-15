"""
DC86 Bot - Greetings
Begrüßt Zuschauer automatisch, wenn sie den Chat betreten.
"""

from twitchio.ext import commands

# ── Konfiguration ──
# Wie lange gilt ein User als "schon begrüßt" (in Sekunden).
# 6 Stunden = 21600s, reicht für eine normale Stream-Session.
GREET_TTL_SECONDS = 21600

# Bot-Accounts / andere Bots, die nicht begrüßt werden sollen.
IGNORE_LIST = {"nightbot", "streamelements", "moobot"}


class Greetings(commands.Cog):
    """Begrüßungs-Feature für neue Chat-Teilnehmer."""

    def __init__(self, bot):
        self.bot = bot

    # ── JOIN-Event ──
    @commands.Cog.event()
    async def event_join(self, channel, user):
        """Wird von twitchio automatisch aufgerufen, wenn jemand joint."""
        username = user.name.lower()

        # Eigenen Bot und andere Bots ignorieren
        if username in IGNORE_LIST:
            return

        # Ohne Redis: kein "schon begrüßt"-Tracking möglich, also lieber
        # gar nicht erst begrüßen (sonst Spam bei jedem Reconnect)
        if not self.bot.redis:
            return

        # Prüfen ob User in dieser Session schon begrüßt wurde
        key = f"greeted:{username}"
        already_greeted = await self.bot.redis.exists(key)
        if already_greeted:
            return

        # Begrüßung senden
        await channel.send(f"👋 Willkommen im Stream, {user.name}!")

        # Merken, damit nicht bei jedem Rejoin erneut begrüßt wird
        await self.bot.redis.setex(key, GREET_TTL_SECONDS, "1")

    # ── !greetings (Mod-Only) ──
    @commands.command(name="greetings", aliases=["begruessung"])
    async def cmd_greetings_test(self, ctx):
        """Test-Command: löst manuell eine Begrüßung für dich selbst aus."""
        if not (ctx.author.is_mod or ctx.author.is_broadcaster):
            return

        await ctx.send(f"👋 Willkommen im Stream, {ctx.author.name}! (Test)")


def prepare(bot):
    bot.add_cog(Greetings(bot))