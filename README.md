# DC86 Stream Toolkit

Mein eigenes Stream-Management-Toolkit fuer Twitch. Komplett selbst gebaut mit React, FastAPI, Python und Docker — und deployed auf AWS.

Das Ding kann alles was ich zum Streamen brauch — Dashboard, Chat-Bot mit WoW Mini-Games, OBS Overlays und mehr. Alles laeuft in Docker Containern und startet automatisch.

**Live:** https://dc86toolkit.duckdns.org

---

## Was kann das Toolkit?

### Stream Dashboard
Web-Dashboard mit Twitch OAuth2 Login. Zeigt Live-Status, Viewer-Count, Uptime und laesst mich Titel und Game direkt aendern. Dazu eine Go-Live Checklist damit ich vor dem Stream nix vergesse, und ein Bot-Control Panel.

### Twitch Chat-Bot
Custom Bot der in meinem Chat sitzt und auf Commands reagiert. Das Highlight: ein komplettes WoW Gold-System wo Viewer Gold verdienen, looten, gamblen und sich duellieren koennen.

**Basic Commands:** `!commands` `!dc86` `!uptime` `!socials` `!lurk` `!unlurk` `!shoutout` `!roll` `!flip` `!8ball`

**WoW Mini-Games:** `!loot` (zufaelliger WoW-Loot von grau bis legendaer), `!quiz` (WoW-Trivia), `!duel @name 50` (PvP mit Wetteinsatz), `!gamble` (Gold setzen), `!gold` (Balance checken), `!give` (Gold verschenken), `!leaderboard` (Top 5)

**Moderation:** `!permit` `!linkprotection` `!capsprotection` `!title` `!greet`

### OBS Overlays
Vier Browser-Source Widgets fuer OBS die ueber URL-Parameter konfiguriert werden:

- **Goal Bar** — Animierter Fortschrittsbalken fuer Follower/Sub Goals
- **Countdown Timer** — Stream-Start Countdown mit verschiedenen Modi
- **Now Playing** — Zeigt aktuelles Game und Live-Status
- **Alerts** — Follow/Sub/Raid Alerts mit Particle-Effekten

### CLI Tool
Terminal-Tool fuer schnellen Zugriff: `python dc86.py status`, `python dc86.py auth login`, `python dc86.py channel info`

---

## Tech Stack

| Was | Womit |
|-----|-------|
| Frontend | React 18, Tailwind CSS, Vite |
| Backend | FastAPI (Python) |
| Chat-Bot | twitchio (Python) |
| Datenbank | PostgreSQL |
| Cache | Redis |
| CLI | Python + httpx |
| Containerisierung | Docker Compose (6 Container) |
| Infrastruktur | AWS EC2, ECR, IAM (Terraform) |
| CI/CD | GitHub Actions |
| Reverse Proxy | nginx + Let's Encrypt (HTTPS) |
| DNS | DuckDNS |

---

## AWS Deployment

Das Toolkit laeuft produktiv auf AWS und wird automatisch deployed.

### Infrastruktur (Terraform)
- **EC2** — Ubuntu 24.04, t2.small, eu-central-1
- **ECR** — Private Container Registry fuer alle selbst gebauten Images
- **IAM Role** — EC2 darf ECR lesen ohne Access Keys
- **Security Groups** — Nur Port 22, 80, 443 offen

### CI/CD Pipeline (GitHub Actions)
Bei jedem Push auf `main`:
1. Docker Images bauen (Frontend, Backend, Bot)
2. Images in ECR pushen
3. Via SSH auf EC2 deployen
4. Container neu starten

### OBS Overlays (Production)
```
https://dc86toolkit.duckdns.org/api/overlays/goal-bar
https://dc86toolkit.duckdns.org/api/overlays/timer
https://dc86toolkit.duckdns.org/api/overlays/alerts
https://dc86toolkit.duckdns.org/api/overlays/now-playing
```

---

## Lokales Setup

### Voraussetzungen
- Docker + Docker Compose
- Twitch Developer Account mit registrierter App

### 1. Repo klonen

```bash
git clone https://github.com/chrislittle1986/dc86-stream-toolkit.git
cd dc86-stream-toolkit
```

### 2. Twitch App registrieren

Auf [dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps) eine neue App erstellen:
- Name: `DC86 Stream Toolkit`
- OAuth Redirect URL: `http://localhost:8000/api/auth/callback`
- Kategorie: Chat Bot
- Client-Typ: Vertraulich

### 3. Environment einrichten

```bash
cp .env.example .env
nano .env
```

Twitch Client ID, Client Secret und Bot Token eintragen. Bot Token gibt es auf [twitchtokengenerator.com](https://twitchtokengenerator.com/).

### 4. Starten

```bash
docker compose up -d
```

Das wars. Alle Container starten automatisch:
- **Frontend:** localhost:5173
- **Backend API:** localhost:8000
- **API Docs:** localhost:8000/docs
- **Overlays:** localhost:8000/api/overlays

### 5. OBS Overlays einbinden (lokal)

In OBS: Quellen > + > Browser, dann eine der URLs einfuegen:

```
http://localhost:8000/api/overlays/now-playing?game=World%20of%20Warcraft&channel=derchrist86
http://localhost:8000/api/overlays/goal-bar?label=Follower%20Goal&current=10&goal=50&emoji=⭐
http://localhost:8000/api/overlays/timer?minutes=10&label=Stream%20startet%20in
http://localhost:8000/api/overlays/alerts?duration=5000
```

---

## Projektstruktur

```
dc86-stream-toolkit/
├── .github/workflows/    # GitHub Actions CI/CD
├── terraform/            # AWS Infrastruktur als Code
├── docker-compose.yml         # Lokal
├── docker-compose.prod.yml    # Production (AWS)
├── nginx/                # Reverse Proxy Config
├── .env.example
├── backend/              # FastAPI Backend
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── routers/      # Auth, Channel, Status, Overlays
│   │   ├── models/       # User Model
│   │   └── services/     # Twitch API, JWT Auth
│   ├── Dockerfile
│   └── Dockerfile.prod
├── frontend/             # React + Tailwind
│   ├── src/
│   │   ├── components/
│   │   ├── pages/        # Home, Dashboard, Overlays, Status
│   │   └── hooks/        # Auth Hook
│   ├── Dockerfile
│   └── Dockerfile.prod
├── bot/                  # Twitch Chat-Bot
│   ├── bot.py
│   ├── cogs/             # Basic, WoW Games, Moderation, Alerts
│   └── Dockerfile
├── cli/                  # CLI Tool
│   └── dc86.py
└── overlays/             # OBS Browser-Source Widgets
    ├── goal-bar/
    ├── timer/
    ├── alerts/
    └── now-playing/
```

---

## Nuetzliche Befehle

```bash
# Lokal
docker compose up -d          # Alles starten
docker compose down           # Alles stoppen
docker compose ps             # Status checken
docker logs dc86-bot          # Bot-Logs anschauen
docker compose restart bot    # Nur Bot neustarten

# Production (auf EC2)
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml logs -f
```

---

## Roadmap

- [x] Phase 1 — Fundament (Twitch Auth, Docker, API)
- [x] Phase 2 — Chat-Bot (Commands, WoW Games, Moderation)
- [x] Phase 3 — Stream Dashboard (Live-Controls, Checklist)
- [x] Phase 4 — OBS Overlays (Goal Bar, Timer, Alerts, Now Playing)
- [x] Phase 5 — AWS Deployment (EC2, ECR, Terraform, GitHub Actions, HTTPS)
- [ ] Phase 6 — Clip-Manager (Auto-Clip, Export, Highlights)

---

Gebaut von **derchrist86** — React + FastAPI + Python + Docker + AWS