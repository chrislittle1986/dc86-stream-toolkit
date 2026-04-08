"""
DC86 Bot - Moderation
Auto-Mod Regeln und Mod-Commands.
"""

import re
from twitchio.ext import commands


# ── Spam-Patterns ──
LINK_PATTERN = re.compile(
    r"(https?://|www\.)[^\s]+",
    re.IGNORECASE,
)

CAPS_THRESHOLD = 0.7  # 70% Großbuchstaben = Caps-Spam
CAPS_MIN_LENGTH = 15  # Mindestens 15 Zeichen für Caps-Check

# ── Erlaubte Domains (keine Warnung) ──
ALLOWED_DOMAINS = [
    "twitch.tv", "clips.twitch.tv",
    "youtube.com", "youtu.be",
    "twitter.com", "x.com",
]


class Moderation(commands.Cog):
    """Chat-Moderation und Auto-Mod Features."""

    def __init__(self, bot):
        self.bot = bot
        self.link_protection = True    # Links von Nicht-Mods warnen
        self.caps_protection = True    # Caps-Spam erkennen
        self.permit_list = set()       # Temporär erlaubte User für Links

    # ── Auto-Mod: Chat-Nachrichten prüfen ──
    @commands.Cog.event()
    async def event_message(self, message):
        """Prüft jede Nachricht auf Spam/Regelverstöße."""
        if message.echo:
            return

        # Mods und Broadcaster sind ausgenommen
        if message.author.is_mod or message.author.is_broadcaster:
            return

        author = message.author.name
        content = message.content

        # ── Link-Check ──
        if self.link_protection and author.lower() not in self.permit_list:
            links = LINK_PATTERN.findall(content)
            if links:
                # Prüfen ob erlaubte Domain
                is_allowed = any(
                    domain in content.lower()
                    for domain in ALLOWED_DOMAINS
                )
                if not is_allowed:
                    await message.channel.send(
                        f"🔗 {author}, Links sind nur für Mods erlaubt! "
                        f"Frag einen Mod für !permit"
                    )
                    return

        # ── Caps-Check ──
        if self.caps_protection and len(content) >= CAPS_MIN_LENGTH:
            alpha_chars = [c for c in content if c.isalpha()]
            if alpha_chars:
                caps_ratio = sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)
                if caps_ratio >= CAPS_THRESHOLD:
                    await message.channel.send(
                        f"🔇 {author}, bitte weniger CAPS! 📢"
                    )
                    return

    # ── !permit ──
    @commands.command(name="permit", aliases=["erlauben"])
    async def cmd_permit(self, ctx, target: str = None):
        """Erlaubt einem User temporär Links zu posten (Mod-Only)."""
        if not (ctx.author.is_mod or ctx.author.is_broadcaster):
            return

        if not target:
            await ctx.send("Usage: !permit @username")
            return

        name = target.lstrip("@").lower()
        self.permit_list.add(name)
        await ctx.send(f"✅ {name} darf jetzt Links posten!")

        # Permit nach 5 Minuten entfernen
        import asyncio
        await asyncio.sleep(300)
        self.permit_list.discard(name)

    # ── !linkprotection ──
    @commands.command(name="linkprotection", aliases=["lp"])
    async def cmd_linkprotection(self, ctx, state: str = None):
        """Schaltet Link-Schutz an/aus (Mod-Only)."""
        if not (ctx.author.is_mod or ctx.author.is_broadcaster):
            return

        if state and state.lower() in ("on", "an", "true"):
            self.link_protection = True
            await ctx.send("🔗 Link-Schutz: AN")
        elif state and state.lower() in ("off", "aus", "false"):
            self.link_protection = False
            await ctx.send("🔗 Link-Schutz: AUS")
        else:
            status = "AN" if self.link_protection else "AUS"
            await ctx.send(f"🔗 Link-Schutz ist {status} — !linkprotection on/off")

    # ── !capsprotection ──
    @commands.command(name="capsprotection", aliases=["cp"])
    async def cmd_capsprotection(self, ctx, state: str = None):
        """Schaltet Caps-Schutz an/aus (Mod-Only)."""
        if not (ctx.author.is_mod or ctx.author.is_broadcaster):
            return

        if state and state.lower() in ("on", "an", "true"):
            self.caps_protection = True
            await ctx.send("🔇 Caps-Schutz: AN")
        elif state and state.lower() in ("off", "aus", "false"):
            self.caps_protection = False
            await ctx.send("🔇 Caps-Schutz: AUS")
        else:
            status = "AN" if self.caps_protection else "AUS"
            await ctx.send(f"🔇 Caps-Schutz ist {status} — !capsprotection on/off")

    # ── !title (Mod-Only) ──
    @commands.command(name="title", aliases=["titel"])
    async def cmd_title(self, ctx, *, new_title: str = None):
        """Zeigt oder ändert den Stream-Titel über die API."""
        if not new_title:
            await ctx.send("Usage: !title Neuer Stream-Titel hier")
            return

        if not (ctx.author.is_mod or ctx.author.is_broadcaster):
            return

        # Titel über Backend-API ändern
        try:
            import httpx
            r = httpx.patch(
                f"{self.bot.api_url}/api/channel/update",
                json={"title": new_title},
                headers={"Authorization": f"Bearer {self.bot.api_token}"}
                if hasattr(self.bot, "api_token") else {},
                timeout=10,
            )
            if r.status_code == 200:
                await ctx.send(f"✅ Titel geändert: {new_title}")
            else:
                await ctx.send(f"❌ Titel-Update fehlgeschlagen (API: {r.status_code})")
        except Exception as e:
            await ctx.send(f"❌ Fehler: Konnte API nicht erreichen")


def prepare(bot):
    bot.add_cog(Moderation(bot))
