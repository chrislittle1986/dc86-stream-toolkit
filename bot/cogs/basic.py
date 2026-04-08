"""
DC86 Bot - Basic Commands
Standard-Commands für Channel-Info, Socials, Uptime etc.
"""

import time
import random
from twitchio.ext import commands


class BasicCommands(commands.Cog):
    """Grundlegende Chat-Commands."""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    # ── !dc86 ──
    @commands.command(name="dc86")
    async def cmd_dc86(self, ctx):
        """Zeigt Info über das Toolkit."""
        await ctx.send(
            "🎮 DC86 Stream Toolkit v0.1.0 — "
            "Dashboard, Chat-Bot, Overlays & mehr! "
            "Alles selbst gebaut mit React + FastAPI + Python 🔥"
        )

    # ── !commands / !help ──
    @commands.command(name="commands", aliases=["help", "befehle"])
    async def cmd_commands(self, ctx):
        """Zeigt alle verfügbaren Commands."""
        await ctx.send(
            "📋 Commands: !dc86 | !uptime | !followage | !socials | "
            "!lurk | !unlurk | !shoutout @name | "
            "🎮 Games: !roll | !duel @name | !quiz | !loot | "
            "!gamble <amount> | !leaderboard"
        )

    # ── !uptime ──
    @commands.command(name="uptime")
    async def cmd_uptime(self, ctx):
        """Zeigt wie lange der Bot schon läuft."""
        elapsed = int(time.time() - self.start_time)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours > 0:
            time_str = f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            time_str = f"{minutes}m {seconds}s"
        else:
            time_str = f"{seconds}s"

        await ctx.send(f"⏱️ Bot läuft seit {time_str}")

    # ── !socials ──
    @commands.command(name="socials", aliases=["social", "links"])
    async def cmd_socials(self, ctx):
        """Zeigt Social-Media Links."""
        await ctx.send(
            "🔗 Twitch: twitch.tv/derchrist | "
            "Beats: soundtrap.com 🎵"
        )

    # ── !lurk ──
    @commands.command(name="lurk")
    async def cmd_lurk(self, ctx):
        """Lurk-Mode aktivieren."""
        lurk_messages = [
            f"👻 {ctx.author.name} schleicht sich in die Schatten... Guten Lurk!",
            f"🥷 {ctx.author.name} aktiviert Stealth-Modus. Bis später!",
            f"🌙 {ctx.author.name} geht afk. Der Stream läuft weiter!",
            f"💤 {ctx.author.name} lurkt jetzt. Viel Spaß im Hintergrund!",
        ]
        await ctx.send(random.choice(lurk_messages))

    # ── !unlurk ──
    @commands.command(name="unlurk")
    async def cmd_unlurk(self, ctx):
        """Lurk-Mode beenden."""
        unlurk_messages = [
            f"👋 {ctx.author.name} ist zurück aus den Schatten!",
            f"🎉 Willkommen zurück, {ctx.author.name}!",
            f"⚔️ {ctx.author.name} tritt wieder dem Schlachtfeld bei!",
            f"🔥 {ctx.author.name} ist wieder da! Let's go!",
        ]
        await ctx.send(random.choice(unlurk_messages))

    # ── !shoutout ──
    @commands.command(name="shoutout", aliases=["so"])
    async def cmd_shoutout(self, ctx, target: str = None):
        """Gibt einem anderen Streamer einen Shoutout."""
        # Nur Mods und Broadcaster
        if not (ctx.author.is_mod or ctx.author.is_broadcaster):
            return

        if not target:
            await ctx.send("Usage: !shoutout @username")
            return

        name = target.lstrip("@")
        await ctx.send(
            f"📣 Schaut mal bei {name} vorbei! "
            f"👉 twitch.tv/{name} — "
            f"Zeigt etwas Liebe! ❤️"
        )

    # ── !roll ──
    @commands.command(name="roll", aliases=["dice", "würfel"])
    async def cmd_roll(self, ctx, sides: str = "20"):
        """Würfelt einen Würfel (Standard: d20)."""
        try:
            max_val = int(sides)
            if max_val < 2:
                max_val = 20
            if max_val > 1000:
                max_val = 1000
        except ValueError:
            max_val = 20

        result = random.randint(1, max_val)

        if max_val == 20:
            if result == 20:
                msg = f"🎲 {ctx.author.name} würfelt eine d{max_val}... 🌟 NAT 20! KRITISCHER TREFFER! 🌟"
            elif result == 1:
                msg = f"🎲 {ctx.author.name} würfelt eine d{max_val}... 💀 NAT 1! Kritischer Fehlschlag!"
            else:
                msg = f"🎲 {ctx.author.name} würfelt eine d{max_val}: {result}"
        else:
            msg = f"🎲 {ctx.author.name} würfelt eine d{max_val}: {result}"

        await ctx.send(msg)

    # ── !flip ──
    @commands.command(name="flip", aliases=["coin", "münze"])
    async def cmd_flip(self, ctx):
        """Wirft eine Münze."""
        result = random.choice(["Kopf", "Zahl"])
        emoji = "👑" if result == "Kopf" else "🪙"
        await ctx.send(f"{emoji} {ctx.author.name} wirft eine Münze... {result}!")

    # ── !8ball ──
    @commands.command(name="8ball", aliases=["orakel"])
    async def cmd_8ball(self, ctx, *, question: str = None):
        """Magische 8-Ball Antwort."""
        if not question:
            await ctx.send(f"🎱 {ctx.author.name}, stell mir eine Frage! Usage: !8ball Wird es regnen?")
            return

        answers = [
            "🟢 Ja, definitiv!",
            "🟢 Alle Zeichen deuten auf Ja!",
            "🟢 Ohne Zweifel!",
            "🟢 Ja!",
            "🟡 Frag später nochmal...",
            "🟡 Kann ich jetzt nicht sagen...",
            "🟡 Konzentrier dich und frag nochmal.",
            "🟡 Besser nicht drüber nachdenken...",
            "🔴 Sieht nicht gut aus...",
            "🔴 Nein!",
            "🔴 Auf keinen Fall!",
            "🔴 Meine Quellen sagen Nein.",
        ]
        await ctx.send(f"🎱 {random.choice(answers)}")


def prepare(bot):
    bot.add_cog(BasicCommands(bot))
