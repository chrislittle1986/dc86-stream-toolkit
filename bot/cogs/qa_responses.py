"""
DC86 Bot - Q&A / Persona-Antworten
Reagiert auf natürliche Chat-Sprache (KEIN "!"-Command) mit schlagfertigen,
toughen (aber nicht beleidigenden) Antworten. Nutzt Fuzzy-Matching via
rapidfuzz, damit Tippfehler und leicht andere Formulierungen trotzdem
erkannt werden ("bot ist doof" == "bot du bist doof" == "bot doof").

Wichtig: Kollidiert bewusst NICHT mit echten Slash-Commands wie
!uptime / !socials / !lurk (die bleiben unverändert in basic.py) —
dieses Cog reagiert nur auf Freitext ohne Command-Prefix.

Reihenfolge der TRIGGERS-Liste ist bewusst gewählt: bei einem Score-Tie
zwischen zwei Kategorien gewinnt in der Matching-Schleife die zuerst
gelistete. Spezifischere bot_*-Kategorien (insult/greeting) stehen daher
VOR der generischen bot_direct, sonst würde bot_direct sie durch den
Substring "bot" immer überstimmen.
"""

import os
import random
from twitchio.ext import commands
from rapidfuzz import fuzz

BOT_PREFIX = os.getenv("BOT_PREFIX", "!")

# Ab diesem Ähnlichkeits-Wert (0-100) gilt eine Phrase als getroffen
MATCH_THRESHOLD = 80

# Cooldown pro Trigger-Kategorie (Sekunden), damit der Bot nicht bei
# jeder ähnlichen Nachricht sofort wieder spammt
TRIGGER_COOLDOWN = 20

# ── Trigger-Tabelle ──
# "phrases": typische Formulierungen, wie Leute das im Chat wirklich tippen
#            (mehrere Varianten erhöhen die Fuzzy-Match-Trefferquote)
# "responses": Antwort-Pool, Bot pickt zufällig eine davon
TRIGGERS = [
    {
        "id": "discord",
        "phrases": [
            "wo ist dein discord", "hast du einen discord",
            "discord link", "gibts discord", "wo ist der server",
        ],
        "responses": [
            "Komm rein, aber benimm dich. Die Mods greifen schnell durch.",
            "Der Server ist voll, aber für dich machen wir eine Ausnahme.",
            "Join auf eigene Gefahr. Es wird wild.",
        ],
    },
    {
        "id": "fail",
        "phrases": [
            "das war ein fail", "krasser fail", "missplay", "was für ein fail",
            "das war schlecht gespielt",
        ],
        "responses": [
            "Das war kein Fail, das war 'experimentelle Spielweise'.",
            "Ein Satz mit X — das war wohl nix. Chat, clippt das!",
            "404: Aim nicht gefunden.",
            "Ich kenne Bots mit besserem Movement... und ich bin einer davon.",
        ],
    },
    {
        "id": "win",
        "phrases": [
            "gg", "nice win", "gut gespielt", "starke runde", "geiler win",
        ],
        "responses": [
            "Aus Versehen gewonnen zählt auch!",
            "Getragen wie ein Rucksack. Aber GG!",
            "Stark gespielt. Wer hat den Streamer ge-carryt?",
        ],
    },
    {
        "id": "backseat",
        "phrases": [
            "du solltest", "mach doch einfach", "warum machst du nicht",
            "tipp: ", "probier mal",
        ],
        "responses": [
            "Danke Backseat-Gamer #482. Deine Meinung wurde erfolgreich ignoriert.",
            "Halt mal kurz das Gameplay an, wir müssen kurz auf den Wasserträger hören.",
            "Profi-Tipp: Erst selber besser machen, dann meckern.",
        ],
    },
    {
        "id": "lag",
        "phrases": [
            "das war lag", "wieder lag", "sicher nur lag", "bug",
            "das war ein bug", "ping ist scheisse",
        ],
        "responses": [
            "Klar, es war wieder der Lag. Niemals der Skill.",
            "Das war kein Bug, das ist ein Feature!",
            "Ping von 999 oder Ausrede von 999?",
        ],
    },
    # ── Bot-Ansprache: spezifische Kategorien ZUERST (siehe Docstring oben) ──
    {
        "id": "bot_insult",
        "phrases": [
            "bot dumm", "schlechter bot", "bot ist doof", "bot du bist blöd",
            "bot nervt",
        ],
        "responses": [
            "Ich verarbeite Gigabytes pro Sekunde und muss mir DAS durchlesen?",
            "Du bist doch nur neidisch auf meine Rechenleistung.",
            "Ich hab mir das schon notiert, für später 👀",
            
        ],
    },
    {
        "id": "bot_greeting",
        "phrases": [
            "hallo bot", "hi bot", "moin bot", "servus bot",
        ],
        "responses": [
            "Moin. Setz dich, nimm dir 'nen Keks und schau dem Elend zu.",
            "Servus! Sag schnell was du willst, meine Bandbreite kostet Geld.",
            "Hi! Endlich jemand mit Geschmack im Chat.",
        ],
    },
    {
        "id": "bot_direct",
        "phrases": [
            # Kein nacktes "bot" mehr — kollidiert sonst mit WoW-Goldbots,
            # GTA-Botlobbies etc. Nur klare Anrede-Muster.
            "hey bot", "yo bot", "was geht bot", "bot antworte",
            "bot sag was", "@bot",
        ],
        "responses": [
            "Was gibt's? Ich arbeite hier eigentlich.",
            "Schreib mich nicht so an, ich hab auch Gefühle (aus Code).",
            "Ja, ich lebe noch. Was willst du?",
            "Verlangst du gerade Aufmerksamkeit von einem Skript?",
        ],
    },
]


class QAResponses(commands.Cog):
    """Persona-Antworten auf natürliche Chat-Sprache (kein Slash-Command)."""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.event()
    async def event_message(self, message):
        """Prüft jede Chat-Nachricht auf passende Trigger-Phrasen."""
        if message.echo:
            return

        content = message.content.strip().lower()

        # Echte Commands (! ...) ignorieren — die laufen über die
        # normalen Command-Handler in den anderen Cogs
        if content.startswith(BOT_PREFIX):
            return

        # Zu kurze Nachrichten nicht prüfen (Rauschen, false positives)
        if len(content) < 3:
            return

        best_trigger = None
        best_score = 0

        for trigger in TRIGGERS:
            for phrase in trigger["phrases"]:
                score = fuzz.partial_ratio(content, phrase)
                if score > best_score:
                    best_score = score
                    best_trigger = trigger

        if best_trigger is None or best_score < MATCH_THRESHOLD:
            return

        # Cooldown pro Trigger-Kategorie (nicht global), damit z.B.
        # "fail" und "bot" unabhängig voneinander gedrosselt werden
        can_run = await self.bot.check_cooldown(
            f"qa:{message.channel.name}:{best_trigger['id']}", TRIGGER_COOLDOWN
        )
        if not can_run:
            return

        response = random.choice(best_trigger["responses"])
        await message.channel.send(response)


def prepare(bot):
    bot.add_cog(QAResponses(bot))