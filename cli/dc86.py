#!/usr/bin/env python3
"""
DC86 Stream Toolkit - CLI
Kommandozeilen-Tool für schnellen Zugriff auf Toolkit-Features.

Usage:
    python dc86.py status        # System-Status checken
    python dc86.py auth login    # Twitch Login starten
    python dc86.py channel info  # Channel-Infos anzeigen
    python dc86.py channel title "Neuer Titel"  # Titel ändern
"""

import os
import sys
import json
import httpx
from pathlib import Path

# ── Config ──
API_URL = os.getenv("DC86_API_URL", "http://localhost:8000")
CONFIG_DIR = Path.home() / ".dc86"
TOKEN_FILE = CONFIG_DIR / "token.json"

# ── Farben (ANSI) ──
PURPLE = "\033[35m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def banner():
    """Zeigt das DC86 ASCII-Banner."""
    print(f"""
{PURPLE}{BOLD}  ╔═══════════════════════════════════════╗
  ║   DC86 Stream Toolkit CLI  v0.1.0    ║
  ╚═══════════════════════════════════════╝{RESET}
""")


def load_token() -> str | None:
    """Lädt den gespeicherten JWT Token."""
    if TOKEN_FILE.exists():
        try:
            data = json.loads(TOKEN_FILE.read_text())
            return data.get("token")
        except Exception:
            return None
    return None


def save_token(token: str):
    """Speichert den JWT Token lokal."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(json.dumps({"token": token}))
    print(f"{GREEN}✓ Token gespeichert in {TOKEN_FILE}{RESET}")


def api_get(endpoint: str, auth: bool = False) -> dict:
    """GET-Request an die API."""
    headers = {}
    if auth:
        token = load_token()
        if not token:
            print(f"{RED}✗ Nicht eingeloggt! Zuerst: python dc86.py auth login{RESET}")
            sys.exit(1)
        headers["Authorization"] = f"Bearer {token}"

    try:
        r = httpx.get(f"{API_URL}{endpoint}", headers=headers, timeout=10)
        r.raise_for_status()
        return r.json()
    except httpx.ConnectError:
        print(f"{RED}✗ Backend nicht erreichbar ({API_URL})")
        print(f"  Läuft docker compose up?{RESET}")
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        print(f"{RED}✗ API-Fehler: {e.response.status_code}{RESET}")
        try:
            detail = e.response.json().get("detail", "Unbekannter Fehler")
            print(f"  {detail}")
        except Exception:
            pass
        sys.exit(1)


# ── Commands ──
def cmd_status():
    """Zeigt den System-Status."""
    print(f"{BOLD}System-Status{RESET}\n")

    # Health Check
    try:
        health = api_get("/api/status/health")
        print(f"  {GREEN}✓{RESET} API: {health.get('message', 'Online')}")
    except SystemExit:
        return

    # Readiness Check
    try:
        ready = api_get("/api/status/ready")
        for key, val in ready.get("checks", {}).items():
            status = val.get("status", "unknown")
            icon = f"{GREEN}✓" if status in ("connected", "configured") else f"{YELLOW}⚠" if status == "not_configured" else f"{RED}✗"
            info = val.get("type", val.get("hint", ""))
            print(f"  {icon}{RESET} {key}: {status} {DIM}({info}){RESET}")
    except SystemExit:
        pass

    print()


def cmd_auth_login():
    """Startet den Twitch OAuth2 Login."""
    print(f"{BOLD}Twitch Login{RESET}\n")
    url = f"{API_URL}/api/auth/login"
    print(f"  Öffne diesen Link in deinem Browser:\n")
    print(f"  {CYAN}{BOLD}{url}{RESET}\n")
    print(f"  {DIM}Nach dem Login bekommst du einen Token.")
    print(f"  Kopiere ihn und führe aus:{RESET}")
    print(f"  {PURPLE}python dc86.py auth token DEIN_TOKEN{RESET}\n")


def cmd_auth_token(token: str):
    """Speichert einen JWT Token."""
    save_token(token)
    # Verifizieren
    data = api_get("/api/auth/me", auth=True)
    print(f"{GREEN}✓ Eingeloggt als: {BOLD}{data['display_name']}{RESET}")


def cmd_auth_me():
    """Zeigt den aktuell eingeloggten User."""
    data = api_get("/api/auth/me", auth=True)
    print(f"{BOLD}Eingeloggt als:{RESET}\n")
    print(f"  Display Name:  {PURPLE}{data['display_name']}{RESET}")
    print(f"  Username:      {data['username']}")
    print(f"  Twitch ID:     {DIM}{data['twitch_id']}{RESET}")
    print(f"  Broadcaster:   {'Ja' if data.get('is_broadcaster') else 'Nein'}")
    print()


def cmd_channel_info():
    """Zeigt Channel-Infos."""
    data = api_get("/api/channel/info", auth=True)
    print(f"{BOLD}Channel-Info:{RESET}\n")
    print(f"  Name:     {PURPLE}{data.get('broadcaster_name', '?')}{RESET}")
    print(f"  Titel:    {data.get('title', '—')}")
    print(f"  Game:     {data.get('game_name', '—')}")
    tags = data.get("tags", [])
    if tags:
        print(f"  Tags:     {', '.join(tags)}")
    print()


def cmd_channel_live():
    """Zeigt den Live-Status."""
    data = api_get("/api/channel/live", auth=True)
    if data.get("is_live"):
        print(f"  {RED}{BOLD}🔴 LIVE{RESET}")
        print(f"  Titel:   {data.get('title', '—')}")
        print(f"  Game:    {data.get('game_name', '—')}")
        print(f"  Viewer:  {data.get('viewer_count', 0)}")
    else:
        print(f"  ⚫ {DIM}Offline{RESET}")
        print(f"  {DIM}{data.get('message', '')}{RESET}")
    print()


def cmd_help():
    """Zeigt die Hilfe."""
    banner()
    print(f"{BOLD}Verfügbare Commands:{RESET}\n")
    commands = [
        ("status", "System-Status checken"),
        ("auth login", "Twitch OAuth2 Login starten"),
        ("auth token <TOKEN>", "JWT Token speichern"),
        ("auth me", "Eingeloggten User anzeigen"),
        ("channel info", "Channel-Infos anzeigen"),
        ("channel live", "Live-Status checken"),
        ("help", "Diese Hilfe anzeigen"),
    ]
    for cmd, desc in commands:
        print(f"  {PURPLE}dc86 {cmd:<24}{RESET} {desc}")
    print()


# ── Main ──
def main():
    args = sys.argv[1:]

    if not args or args[0] == "help":
        cmd_help()
    elif args[0] == "status":
        cmd_status()
    elif args[0] == "auth":
        if len(args) < 2 or args[1] == "help":
            print(f"Usage: dc86 auth [login|token|me]")
        elif args[1] == "login":
            cmd_auth_login()
        elif args[1] == "token" and len(args) > 2:
            cmd_auth_token(args[2])
        elif args[1] == "me":
            cmd_auth_me()
        else:
            print(f"Unbekannter Auth-Command: {args[1]}")
    elif args[0] == "channel":
        if len(args) < 2 or args[1] == "help":
            print(f"Usage: dc86 channel [info|live]")
        elif args[1] == "info":
            cmd_channel_info()
        elif args[1] == "live":
            cmd_channel_live()
        else:
            print(f"Unbekannter Channel-Command: {args[1]}")
    else:
        print(f"{RED}Unbekannter Command: {args[0]}{RESET}")
        print(f"Versuch: python dc86.py help")


if __name__ == "__main__":
    main()
