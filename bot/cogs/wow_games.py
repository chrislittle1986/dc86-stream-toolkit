"""
DC86 Bot - WoW Mini-Games
Chat-Games im World of Warcraft Stil: Quiz, Duel, Loot, Gamble.
Viewer sammeln Gold (DC86-Coins) und steigen im Leaderboard auf.
"""

import random
import asyncio
import time
from twitchio.ext import commands


# ── WoW Quiz-Fragen ──
WOW_QUIZ = [
    {"q": "Welche Klasse kann NICHT heilen?", "a": "Schurke", "options": ["Schamane", "Schurke", "Paladin", "Mönch"]},
    {"q": "Wer ist der Lichkönig?", "a": "Arthas Menethil", "options": ["Arthas Menethil", "Illidan", "Thrall", "Sylvanas"]},
    {"q": "Welche Stadt ist die Hauptstadt der Horde?", "a": "Orgrimmar", "options": ["Orgrimmar", "Donnerfels", "Unterstadt", "Silbermond"]},
    {"q": "Welches Level ist das Classic-Max-Level?", "a": "60", "options": ["60", "70", "80", "50"]},
    {"q": "Welcher Raid hat 40 Spieler in Classic?", "a": "Alle Raids", "options": ["Alle Raids", "Nur MC", "Nur BWL", "Nur Naxx"]},
    {"q": "Wer droppt Thunderfury?", "a": "Baron Geddon & Garr", "options": ["Baron Geddon & Garr", "Ragnaros", "Onyxia", "Nefarian"]},
    {"q": "Welche Klasse hat 'Vanish'?", "a": "Schurke", "options": ["Schurke", "Magier", "Druide", "Jäger"]},
    {"q": "Was ist der erste Raid in Classic WoW?", "a": "Geschmolzener Kern", "options": ["Geschmolzener Kern", "Onyxias Hort", "BWL", "ZG"]},
    {"q": "Welches Volk hat 'Steingestalt'?", "a": "Zwerge", "options": ["Zwerge", "Menschen", "Gnome", "Nachtelfen"]},
    {"q": "Wer ist Warchief in Classic WoW?", "a": "Thrall", "options": ["Thrall", "Garrosh", "Sylvanas", "Vol'jin"]},
    {"q": "Welche Klasse nutzt Mana UND Rage?", "a": "Druide", "options": ["Druide", "Krieger", "Paladin", "Schamane"]},
    {"q": "Was braucht man für ein Epic Mount in Classic?", "a": "1000 Gold", "options": ["1000 Gold", "500 Gold", "100 Gold", "2000 Gold"]},
    {"q": "Welcher Boss ist am Ende von BWL?", "a": "Nefarian", "options": ["Nefarian", "Ragnaros", "C'Thun", "Kel'Thuzad"]},
    {"q": "Welches Tier-Set droppt in MC?", "a": "Tier 1", "options": ["Tier 1", "Tier 2", "Tier 3", "Tier 0"]},
    {"q": "Wo ist der Eingang zu Stratholme?", "a": "Östliche Pestländer", "options": ["Östliche Pestländer", "Westliche Pestländer", "Schergrat", "Winterquell"]},
]

# ── Loot-Tabelle ──
LOOT_TABLE = [
    {"name": "Kaputtes Schwert", "rarity": "grau", "gold": 1, "emoji": "🗡️"},
    {"name": "Leinenstoffbandagen", "rarity": "weiß", "gold": 3, "emoji": "🩹"},
    {"name": "Elixier der Weisheit", "rarity": "grün", "gold": 10, "emoji": "🧪"},
    {"name": "Eisenerz", "rarity": "grün", "gold": 8, "emoji": "⛏️"},
    {"name": "Seidenstoff", "rarity": "grün", "gold": 12, "emoji": "🧵"},
    {"name": "Trank des Feuerschutzes", "rarity": "grün", "gold": 15, "emoji": "🧴"},
    {"name": "Blaues Saphir-Amulett", "rarity": "blau", "gold": 35, "emoji": "💎"},
    {"name": "Arkanitbarren", "rarity": "blau", "gold": 50, "emoji": "✨"},
    {"name": "Klingen des Assassinen", "rarity": "blau", "gold": 45, "emoji": "⚔️"},
    {"name": "Auge von Sulfuras", "rarity": "episch", "gold": 200, "emoji": "🔥"},
    {"name": "Bindings of the Windseeker", "rarity": "episch", "gold": 500, "emoji": "⚡"},
    {"name": "Ashkandi", "rarity": "episch", "gold": 150, "emoji": "🗡️"},
    {"name": "Thunderfury", "rarity": "legendär", "gold": 2000, "emoji": "⚡🗡️"},
    {"name": "Sulfuras, Hand of Ragnaros", "rarity": "legendär", "gold": 1500, "emoji": "🔨🔥"},
]

# Loot-Gewichtung (häufiger → seltener)
LOOT_WEIGHTS = [20, 18, 15, 15, 14, 13, 8, 6, 7, 3, 2, 3, 0.5, 0.5]

RARITY_COLORS = {
    "grau": "⬜", "weiß": "⬜", "grün": "🟩",
    "blau": "🟦", "episch": "🟪", "legendär": "🟧",
}

# ── Duel Moves ──
DUEL_MOVES = [
    "{a} landet einen kritischen Treffer! 💥",
    "{b} weicht geschickt aus und kontert! ⚔️",
    "{a} castet einen Pyroblast! 🔥",
    "{b} nutzt Evasion und dodged alles! 🥷",
    "{a} ruft ein Totem und heilt sich! 💚",
    "{b} benutzt Kidney Shot — {a} ist stunned! 💫",
    "{a} trinkt einen Heiltrank mitten im Kampf! 🧪",
    "{b} benutzt Frostbolt und slowt {a}! ❄️",
]


class WoWGames(commands.Cog):
    """WoW-themed Chat Mini-Games mit Gold-System."""

    def __init__(self, bot):
        self.bot = bot
        self.active_quiz = None  # Aktives Quiz
        self.active_duels = {}  # Offene Duel-Anfragen
        self.duel_lock = asyncio.Lock()

    # ── Helper: Gold verwalten ──
    async def get_gold(self, username: str) -> int:
        """Gibt das Gold eines Users zurück."""
        if not self.bot.redis:
            return 0
        val = await self.bot.redis.hget("gold", username.lower())
        return int(val) if val else 100  # Startwert: 100 Gold

    async def add_gold(self, username: str, amount: int) -> int:
        """Fügt Gold hinzu (oder zieht ab). Gibt neuen Betrag zurück."""
        if not self.bot.redis:
            return 0
        current = await self.get_gold(username)
        new_amount = max(0, current + amount)
        await self.bot.redis.hset("gold", username.lower(), new_amount)
        return new_amount

    async def set_gold(self, username: str, amount: int):
        """Setzt Gold direkt."""
        if not self.bot.redis:
            return
        await self.bot.redis.hset("gold", username.lower(), max(0, amount))

    # ── !gold / !coins ──
    @commands.command(name="gold", aliases=["coins", "balance"])
    async def cmd_gold(self, ctx, target: str = None):
        """Zeigt das Gold eines Users."""
        name = (target or ctx.author.name).lstrip("@").lower()
        gold = await self.get_gold(name)
        if name == ctx.author.name.lower():
            await ctx.send(f"💰 {ctx.author.name}, du hast {gold}g")
        else:
            await ctx.send(f"💰 {name} hat {gold}g")

    # ── !quiz ──
    @commands.command(name="quiz", aliases=["trivia"])
    async def cmd_quiz(self, ctx):
        """Startet ein WoW-Quiz im Chat."""
        # Cooldown prüfen
        can_run = await self.bot.check_cooldown(f"quiz:{ctx.channel.name}", 30)
        if not can_run:
            await ctx.send("⏳ Quiz-Cooldown läuft noch... Warte kurz!")
            return

        if self.active_quiz:
            await ctx.send("❗ Es läuft bereits ein Quiz!")
            return

        # Frage auswählen
        question = random.choice(WOW_QUIZ)
        options = question["options"].copy()
        random.shuffle(options)

        self.active_quiz = {
            "answer": question["a"].lower(),
            "started_by": ctx.author.name,
            "time": time.time(),
        }

        options_str = " | ".join(f"{i+1}. {o}" for i, o in enumerate(options))
        await ctx.send(f"❓ WoW-Quiz! {question['q']}")
        await ctx.send(f"📝 {options_str} — Antworte mit der Antwort im Chat! (30s)")

        # Timeout nach 30 Sekunden
        await asyncio.sleep(30)
        if self.active_quiz:
            await ctx.send(f"⏰ Zeit abgelaufen! Die Antwort war: {question['a']}")
            self.active_quiz = None

    @commands.Cog.event()
    async def event_message(self, message):
        """Prüft Chat-Nachrichten auf Quiz-Antworten."""
        if not self.active_quiz or message.echo:
            return

        if message.content.lower().strip() == self.active_quiz["answer"]:
            winner = message.author.name
            elapsed = time.time() - self.active_quiz["time"]
            gold_reward = max(10, 50 - int(elapsed))  # Schneller = mehr Gold

            new_gold = await self.add_gold(winner, gold_reward)
            self.active_quiz = None

            await message.channel.send(
                f"🎉 {winner} hat es in {elapsed:.1f}s gewusst! "
                f"+{gold_reward}g (Gesamt: {new_gold}g) 🏆"
            )

    # ── !loot ──
    @commands.command(name="loot", aliases=["drop"])
    async def cmd_loot(self, ctx):
        """Lootet einen zufälligen Gegenstand."""
        can_run = await self.bot.check_cooldown(f"loot:{ctx.author.name}", 60)
        if not can_run:
            await ctx.send(f"⏳ {ctx.author.name}, du kannst nur alle 60s looten!")
            return

        # Gewichteter Loot
        item = random.choices(LOOT_TABLE, weights=LOOT_WEIGHTS, k=1)[0]
        rarity_icon = RARITY_COLORS.get(item["rarity"], "⬜")

        new_gold = await self.add_gold(ctx.author.name, item["gold"])

        msg = (
            f"{item['emoji']} {ctx.author.name} lootet: "
            f"{rarity_icon} [{item['name']}] ({item['rarity']}) "
            f"— +{item['gold']}g"
        )

        # Spezielle Messages für seltene Items
        if item["rarity"] == "legendär":
            msg = (
                f"🌟✨ LEGENDÄRER DROP! ✨🌟 "
                f"{ctx.author.name} lootet {item['emoji']} [{item['name']}]! "
                f"+{item['gold']}g! PogChamp"
            )
        elif item["rarity"] == "episch":
            msg = (
                f"🟪 EPISCHER DROP! {ctx.author.name} lootet "
                f"{item['emoji']} [{item['name']}] — +{item['gold']}g!"
            )

        await ctx.send(msg)

    # ── !duel ──
    @commands.command(name="duel", aliases=["pvp", "kampf"])
    async def cmd_duel(self, ctx, target: str = None, bet: str = "10"):
        """Fordert einen anderen Viewer zum Duel (mit Wetteinsatz)."""
        if not target:
            await ctx.send(f"Usage: !duel @username [einsatz] — z.B. !duel @spieler 50")
            return

        target_name = target.lstrip("@").lower()
        challenger = ctx.author.name.lower()

        if target_name == challenger:
            await ctx.send(f"🤦 {ctx.author.name}, du kannst dich nicht selbst duellieren!")
            return

        # Einsatz parsen
        try:
            bet_amount = max(0, min(int(bet), 500))
        except ValueError:
            bet_amount = 10

        # Gold prüfen
        challenger_gold = await self.get_gold(challenger)
        if challenger_gold < bet_amount:
            await ctx.send(f"💸 {ctx.author.name}, du hast nicht genug Gold! ({challenger_gold}g)")
            return

        # Duel-Anfrage speichern
        duel_key = f"{challenger}:{target_name}"
        self.active_duels[duel_key] = {
            "challenger": challenger,
            "target": target_name,
            "bet": bet_amount,
            "time": time.time(),
        }

        await ctx.send(
            f"⚔️ {ctx.author.name} fordert {target_name} zum Duel! "
            f"Einsatz: {bet_amount}g — "
            f"{target_name}, schreib !accept um anzunehmen! (60s)"
        )

        # Timeout
        await asyncio.sleep(60)
        if duel_key in self.active_duels:
            del self.active_duels[duel_key]

    # ── !accept ──
    @commands.command(name="accept", aliases=["annehmen"])
    async def cmd_accept(self, ctx):
        """Nimmt ein Duel an."""
        accepter = ctx.author.name.lower()

        # Offenes Duel finden
        duel_info = None
        duel_key = None
        for key, duel in self.active_duels.items():
            if duel["target"] == accepter:
                duel_info = duel
                duel_key = key
                break

        if not duel_info:
            await ctx.send(f"❗ {ctx.author.name}, niemand hat dich herausgefordert!")
            return

        # Gold prüfen
        target_gold = await self.get_gold(accepter)
        if target_gold < duel_info["bet"]:
            await ctx.send(f"💸 {ctx.author.name}, du hast nicht genug Gold! ({target_gold}g)")
            del self.active_duels[duel_key]
            return

        del self.active_duels[duel_key]

        # FIGHT!
        a = duel_info["challenger"]
        b = accepter
        bet = duel_info["bet"]

        await ctx.send(f"⚔️ DUEL: {a} vs {b} — Einsatz: {bet}g — FIGHT! ⚔️")
        await asyncio.sleep(2)

        # Zufällige Kampf-Narration
        move = random.choice(DUEL_MOVES).format(a=a, b=b)
        await ctx.send(move)
        await asyncio.sleep(2)

        # Gewinner bestimmen
        winner = random.choice([a, b])
        loser = b if winner == a else a

        await self.add_gold(winner, bet)
        await self.add_gold(loser, -bet)

        winner_gold = await self.get_gold(winner)

        await ctx.send(
            f"🏆 {winner} gewinnt das Duel gegen {loser}! "
            f"+{bet}g (Gesamt: {winner_gold}g) GG!"
        )

    # ── !gamble ──
    @commands.command(name="gamble", aliases=["bet", "wette"])
    async def cmd_gamble(self, ctx, amount: str = "10"):
        """Setze Gold — 50/50 Chance auf Verdopplung oder Verlust."""
        can_run = await self.bot.check_cooldown(f"gamble:{ctx.author.name}", 15)
        if not can_run:
            await ctx.send(f"⏳ Gamble-Cooldown! Warte kurz, {ctx.author.name}")
            return

        # Amount parsen
        current_gold = await self.get_gold(ctx.author.name)

        if amount.lower() == "all":
            bet = current_gold
        else:
            try:
                bet = max(1, min(int(amount), 1000))
            except ValueError:
                bet = 10

        if current_gold < bet:
            await ctx.send(f"💸 {ctx.author.name}, du hast nur {current_gold}g!")
            return

        if bet == 0:
            await ctx.send(f"🤔 {ctx.author.name}, du musst mindestens 1g setzen!")
            return

        # 50/50 Chance
        won = random.random() < 0.48  # Leicht unter 50% — the house always wins

        if won:
            new_gold = await self.add_gold(ctx.author.name, bet)
            await ctx.send(
                f"🎰 {ctx.author.name} setzt {bet}g... "
                f"🟢 GEWONNEN! +{bet}g (Gesamt: {new_gold}g)"
            )
        else:
            new_gold = await self.add_gold(ctx.author.name, -bet)
            await ctx.send(
                f"🎰 {ctx.author.name} setzt {bet}g... "
                f"🔴 Verloren! -{bet}g (Gesamt: {new_gold}g)"
            )

    # ── !leaderboard ──
    @commands.command(name="leaderboard", aliases=["lb", "top", "ranking"])
    async def cmd_leaderboard(self, ctx):
        """Zeigt die Top 5 reichsten Viewer."""
        if not self.bot.redis:
            await ctx.send("❗ Leaderboard braucht Redis!")
            return

        all_gold = await self.bot.redis.hgetall("gold")
        if not all_gold:
            await ctx.send("📊 Noch keine Daten! Spielt !loot, !quiz oder !gamble!")
            return

        # Sortieren nach Gold
        sorted_users = sorted(
            all_gold.items(),
            key=lambda x: int(x[1]),
            reverse=True
        )[:5]

        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        entries = []
        for i, (name, gold) in enumerate(sorted_users):
            entries.append(f"{medals[i]} {name}: {gold}g")

        await ctx.send(f"🏆 DC86 Leaderboard: {' | '.join(entries)}")

    # ── !give ──
    @commands.command(name="give", aliases=["trade", "geben"])
    async def cmd_give(self, ctx, target: str = None, amount: str = "10"):
        """Gibt einem anderen Viewer Gold."""
        if not target:
            await ctx.send("Usage: !give @username betrag")
            return

        target_name = target.lstrip("@").lower()
        giver = ctx.author.name.lower()

        if target_name == giver:
            await ctx.send("🤔 Du kannst dir nicht selbst Gold geben!")
            return

        try:
            give_amount = max(1, int(amount))
        except ValueError:
            give_amount = 10

        giver_gold = await self.get_gold(giver)
        if giver_gold < give_amount:
            await ctx.send(f"💸 Du hast nur {giver_gold}g!")
            return

        await self.add_gold(giver, -give_amount)
        new_target = await self.add_gold(target_name, give_amount)

        await ctx.send(
            f"💰 {ctx.author.name} gibt {target_name} {give_amount}g! "
            f"({target_name} hat jetzt {new_target}g)"
        )


def prepare(bot):
    bot.add_cog(WoWGames(bot))
