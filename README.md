# 🤖 VHA Alliance Bot • Mecha Fire

Ein mehrsprachiger Discord-Bot für die **VHA Alliance** im Spiel **Mecha Fire**.  
Automatische Übersetzung, Koordinaten-Verwaltung, Spieler-IDs, Timer, Event-Erkennung und KI-Assistent.

---

## 🌐 Übersetzung

Der Bot übersetzt automatisch alle Nachrichten — welche Sprachen aktiv sind lässt sich per Button steuern.

**Immer aktiv (nicht ausschaltbar):**
- 🇩🇪 Deutsch ↔ 🇫🇷 Français

**Ein/Ausschaltbar per `!sprachen`:**
- 🇧🇷 Português (Standard: aktiv)
- 🇬🇧 English (Standard: inaktiv)
- 🇯🇵 日本語 (Standard: inaktiv)

**Gastsprachen** (EN, JA, ES, ...):
- Werden automatisch auf alle aktiven Sprachen übersetzt
- Beim **Reply auf einen Gast** → übersetzt auch in die Gastsprache

---

## 📋 Befehle

### 🌐 Übersetzer
| Befehl | Beschreibung |
|--------|-------------|
| `!translate on/off` | Automatische Übersetzung ein/ausschalten |
| `!translate status` | Status anzeigen |
| `!sprachen` / `!languages` / `!idiomas` | Sprachen per Button ein/ausschalten 🔐 |
| `!ai [Text]` | KI-Assistent in jeder Sprache |
| `!übersetze` / `!traduire` / `!traduzir` | Text aus Bild(ern) übersetzen |

### 🎮 Events 🔐
| Befehl | Beschreibung |
|--------|-------------|
| `!event` | Event aus Screenshot erkennen + Timer per Button setzen |

### 📍 Koordinaten 🔐
| Befehl | Beschreibung |
|--------|-------------|
| `!koordinaten` / `!coordonnees` / `!coordenadas` | Alle Koordinaten anzeigen |
| `!koordinaten add NAME R X Y` | Neue Koordinate hinzufügen |
| `!koordinaten delete NAME` | Koordinate löschen |

### 👥 Spieler-IDs 🔐
| Befehl | Beschreibung |
|--------|-------------|
| `!spieler` / `!joueur` | Alle Spieler anzeigen |
| `!spieler add NAME ID` | Spieler hinzufügen |
| `!spieler delete NAME` | Spieler löschen |
| `!spieler suche NAME/ID` | Spieler suchen |

### ⏱️ Timer 🔐
| Befehl | Beschreibung |
|--------|-------------|
| `!timer DAUER EVENT` / `!rappel` / `!lembrete` | Timer setzen |
| `!timer list` | Aktive Timer anzeigen |
| `!timer delete NAME` | Timer löschen |

**Zeitformate:** `30m` • `2h` • `1h30m` • `3d`  
**Vorwarnung:** automatisch je nach Timer-Länge (5min / 15min / 1h vorher)  
**Erinnerung:** in 2 konfigurierten Kanälen mit @everyone auf allen aktiven Sprachen

### 📊 Status & Log
| Befehl | Beschreibung |
|--------|-------------|
| `!ping` | Bot-Status, Latenz und Token-Verbrauch heute |
| `!log` | Aktivitäts-Log anzeigen (nur dev) 🔐 |
| `!log clear` | Log löschen (nur dev) 🔐 |
| `!help` | Alle Befehle anzeigen |

🔐 = Nur für **Administrator**, **R5**, **R4** oder **dev**

---

## 📁 Dateistruktur

```
├── app.py                # Hauptbot
├── koordinaten.py        # Koordinaten-Cog (MongoDB)
├── timer.py              # Timer-Cog (MongoDB)
├── bilduebersetzer.py    # Bild-Übersetzer-Cog (mehrere Bilder)
├── event.py              # Event-Erkennung-Cog (MongoDB)
├── spieler.py            # Spieler-IDs-Cog (MongoDB)
├── sprachen.py           # Sprachen-Einstellungen-Cog (MongoDB)
├── log.py                # Aktivitäts-Log-Cog (MongoDB)
├── koordinaten.json      # Backup der Koordinaten
├── requirements.txt      # Python-Abhängigkeiten
└── README.md             # Diese Datei
```

---

## 🗄️ Datenbank (MongoDB Atlas)

Alle dynamischen Daten werden in MongoDB gespeichert und bleiben bei Bot-Neustart erhalten:

| Collection | Inhalt |
|------------|--------|
| `vhabot.timers` | Aktive Timer mit Event-Namen (alle Sprachen) |
| `vhabot.spieler` | Spieler-IDs |
| `vhabot.koordinaten` | Allianz-Koordinaten |
| `vhabot.sprachen` | Aktive Spracheinstellungen |
| `vhabot.logs` | Aktivitäts-Log (max. 500 Einträge) |

---

## ⚙️ Technische Details

- **Sprache:** Python 3.10+
- **Framework:** discord.py
- **KI:** Groq API (Llama 3.3 70B + Llama 4 Scout für Bilder)
- **Datenbank:** MongoDB Atlas (Free Tier)
- **Hosting:** Render (Free Tier)
- **Keep-Alive:** UptimeRobot + Flask
- **Optimierungen:**
  - Async Groq-Calls mit `asyncio` + `run_in_executor`
  - Semaphore (max. 4 gleichzeitige API-Calls)
  - Automatischer Retry bei Rate-Limit (3 Versuche)
  - Sprachcache für Token-Ersparnis
  - Parallele Übersetzungen mit `asyncio.gather`
  - Token-Logging via `!ping`
  - Mehrere Bilder gleichzeitig verarbeiten

---

## 🔑 Environment Variables (Render)

| Variable | Beschreibung |
|----------|-------------|
| `DISCORD_TOKEN` | Discord Bot Token |
| `GROQ_API_KEY` | Groq API Key |
| `MONGODB_URI` | MongoDB Connection String |

---

## 📦 Installation

```bash
pip install -r requirements.txt
python app.py
```

---

## 🗒️ Changelog

- **v4.0** – Sprachen per Button steuerbar (PT/EN/JA), Log-System, Timer nur 2 Kanäle
- **v3.0** – MongoDB für alle Daten, Event-Erkennung mit Buttons, PT als dritte Hauptsprache
- **v2.0** – Async Optimierungen, Token-Logging, Bild-Übersetzer, Spieler-IDs
- **v1.0** – Grundfunktionen: Übersetzung DE↔FR, Koordinaten, Timer

---

*VHA Alliance • Mecha Fire • Made with ❤️*
