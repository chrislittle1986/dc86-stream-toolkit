"""
DC86 Bot - Alerts & Events
Reagiert auf Follows, Subs, Raids und andere Twitch-Events.
"""

import random
from twitchio.ext import commands


# ── Willkommensnachrichten ──
WELCOME_MESSAGES = [
    "👋 Willkommen im Stream, {name}! Viel Spaß!",
    "🎮 Hey {name}, schön dass du da bist!",
    "⚔️ {name} betritt die Arena! Willkommen!",
    "🔥 {name} ist im Chat! Let's gooo!",
]

RAID_MESSAGES = [
    "🎉 RAID! {name} bringt {count} Viewer mit! Willkommen alle zusammen! 🎊",
    "⚔️ INCOMING RAID von {name}! {count} Krieger stürmen den Channel! 🏰",
    "🔥 {name} raidet uns mit {count} Leuten! HYPE! 🔥",
    "🐉 {name} schickt {count} Abenteurer in unseren Dungeon! Willkommen! 🐉",
]

SUB_MESSAGES = [
    "⭐ {name} hat gerade gesubbt! Willkommen im DC86 Club! 🎉",
    "💜 NEUER SUB! Danke {name} für den Support! Du bist der Hammer!",
    "🏆 {name} ist jetzt Subscriber! Ehre! 💎",
]

GIFTSUB_MESSAGES = [
    "🎁 {gifter} verschenkt {count}x Sub(s)! Absolute Legende! 💜",
    "✨ {gifter} ist großzügig und giftet {count} Sub(s)! Danke! 🎉",
]


class Alerts(commands.Cog):
    """Event-Alerts und automatische Begrüßungen."""

    def __init__(self, bot):
        self.bot = bot
        self.greeted_users = set()  # Pro Stream-Session: Wer wurde schon begrüßt
        self.auto_greet = False      # Standard: aus (kann per Command eingeschaltet werden)

    # ── Raid Event ──
    @commands.Cog.event()
    async def event_raw_usernotice(self, channel, tags):
        """Reagiert auf Raids, Subs und Gift-Subs."""
        msg_id = tags.get("msg-id", "")

        # ── Raid ──
        if msg_id == "raid":
            raider = tags.get("display-name", tags.get("login", "Jemand"))
            viewers = tags.get("msg-param-viewerCount", "?")
            msg = random.choice(RAID_MESSAGES).format(name=raider, count=viewers)
            await channel.send(msg)

            # Gold-Bonus für den Raider
            await self.bot.redis.hincrby("gold", raider.lower(), 100) if self.bot.redis else None

        # ── Sub ──
        elif msg_id in ("sub", "resub"):
            subber = tags.get("display-name", "Jemand")
            msg = random.choice(SUB_MESSAGES).format(name=subber)
            await channel.send(msg)

            # Gold-Bonus
            await self.bot.redis.hincrby("gold", subber.lower(), 200) if self.bot.redis else None

        # ── Gift Sub ──
        elif msg_id == "subgift":
            gifter = tags.get("display-name", "Anonym")
            count = tags.get("msg-param-mass-gift-count", "1")
            msg = random.choice(GIFTSUB_MESSAGES).format(gifter=gifter, count=count)
            await channel.send(msg)

            # Gold-Bonus für den Gifter
            gift_bonus = int(count) * 150 if count.isdigit() else 150
            await self.bot.redis.hincrby("gold", gifter.lower(), gift_bonus) if self.bot.redis else None

    # ── Auto-Greet bei erster Nachricht ──
    @commands.Cog.event()
    async def event_message(self, message):
        """Begrüßt User bei ihrer ersten Nachricht im Stream."""
        if message.echo or not self.auto_greet:
            return

        author = message.author.name.lower()
        if author not in self.greeted_users:
            self.greeted_users.add(author)
            # Keine Begrüßung für den Broadcaster selbst
            if not message.author.is_broadcaster:
                msg = random.choice(WELCOME_MESSAGES).format(name=message.author.name)
                await message.channel.send(msg)

    # ── !greet on/off ──
    @commands.command(name="greet", aliases=["begrüßung"])
    async def cmd_greet(self, ctx, state: str = None):
        """Schaltet Auto-Begrüßung an/aus (Mod-Only)."""
        if not (ctx.author.is_mod or ctx.author.is_broadcaster):
            return

        if state and state.lower() in ("on", "an", "true"):
            self.auto_greet = True
            self.greeted_users.clear()
            await ctx.send("👋 Auto-Begrüßung: AN")
        elif state and state.lower() in ("off", "aus", "false"):
            self.auto_greet = False
            await ctx.send("👋 Auto-Begrüßung: AUS")
        else:
            status = "AN" if self.auto_greet else "AUS"
            await ctx.send(f"👋 Auto-Begrüßung ist {status} — !greet on/off")

    # ── !resetgreet ──
    @commands.command(name="resetgreet")
    async def cmd_resetgreet(self, ctx):
        """Setzt die Begrüßungsliste zurück (für neuen Stream)."""
        if not (ctx.author.is_mod or ctx.author.is_broadcaster):
            return

        self.greeted_users.clear()
        await ctx.send("🔄 Begrüßungsliste zurückgesetzt!")

    # ── !hype ──
    @commands.command(name="hype")
    async def cmd_hype(self, ctx):
        """Startet einen Hype im Chat!"""
        can_run = await self.bot.check_cooldown(f"hype:{ctx.channel.name}", 120)
        if not can_run:
            await ctx.send("⏳ Hype-Cooldown! Warte noch...")
            return

        hype_messages = [
            "🔥🔥🔥 HYPE HYPE HYPE! 🔥🔥🔥",
            "LET'S GOOOOO! 🚀🚀🚀",
            "⚡ DER STREAM IST ON FIRE! ⚡",
        ]
        await ctx.send(random.choice(hype_messages))


def prepare(bot):
    bot.add_cog(Alerts(bot))
