# 🤖 VHA Alliance Bot — Mecha Fire

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![discord.py](https://img.shields.io/badge/discord.py-latest-5865F2)](https://discordpy.readthedocs.io)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248)](https://mongodb.com/atlas)
[![Hosted on](https://img.shields.io/badge/Hosted-Render-46E3B7)](https://render.com)

Vollständiger Alliance-Management-Bot für den VHA Discord-Server (Mecha Fire).  
Multilingual · Persistent · KI-gestützt via Groq (LLaMA 3.3 70B + LLaMA 4 Scout)

---

## 📁 Projektstruktur

```
├── app.py               # Bot-Einstiegspunkt, Groq-Wrapper, Auto-Translation, Flask-Keepalive
├── server.py            # Server-Struktur Export/Import (Kategorien & Kanäle)
├── sprachen.py          # Globale Spracheinstellungen (Button-UI)
├── raumsprachen.py      # Raum-spezifische Spracheinstellungen (Button-UI)
├── bilduebersetzer.py   # OCR + Übersetzung von Spielscreenshots
├── event.py             # Event-Erkennung aus Screenshots + Timer-Setzung
├── timer.py             # Manueller Timer mit persistenter Speicherung
├── koordinaten.py       # Allianz-Koordinaten verwalten
├── koordinaten.json     # Initiale Koordinaten-Daten
├── svs.py               # Server vs Server Koordinaten
├── spieler.py           # Spieler-IDs verwalten
├── spieler.json         # Initiale Spieler-Daten
├── log.py               # Activity-Log (nur dev/Creator)
├── requirements.txt     # Python-Abhängigkeiten
```

---

## ⚙️ Setup & Deployment

### Umgebungsvariablen

| Variable | Beschreibung |
|---|---|
| `DISCORD_TOKEN` | Discord Bot Token |
| `GROQ_API_KEY` | Groq API Key (kostenlos auf groq.com) |
| `MONGODB_URI` | MongoDB Atlas Connection String |
| `PORT` | Server-Port (Standard: `10000`, von Render gesetzt) |

### Lokale Installation

```bash
pip install -r requirements.txt
python app.py
```

### Deployment auf Render

1. Repository auf GitHub pushen
2. Neuen **Web Service** auf [render.com](https://render.com) erstellen
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python app.py`
5. Umgebungsvariablen in den Render-Settings setzen
6. Der eingebaute Flask-Server (`/ping`) hält den Bot am Leben

### Requirements

```
discord.py
groq
flask
aiohttp
pymongo
```

---

## 🌐 Auto-Translation (Kern-Feature)

Der Bot übersetzt Nachrichten automatisch in alle aktivierten Sprachen.

**Funktionsweise:**
- Sprache wird zunächst regelbasiert per Unicode-Block erkannt (kein API-Call)
- Nur für lateinische Schriften wird ein LLaMA-Call ausgelöst
- Nachrichten unter 2 Zeichen, neutrale Wörter (ok, lol, gg…) und reine Links werden übersprungen
- Pro User gilt ein Cooldown von **8 Sekunden**
- Max. **2 gleichzeitige** Groq-Calls (Semaphore), mit automatischem Retry und Backoff bei Rate-Limits (429)
- GIFs, YouTube-Links und Sticker werden ignoriert
- Ein einziger API-Call übersetzt in **alle** Zielsprachen gleichzeitig (spart ~80% der Requests)

**Feste Sprachen (immer aktiv):** 🇩🇪 Deutsch · 🇫🇷 Français  
**Zuschaltbar:** 🇧🇷 Português · 🇬🇧 English · 🇯🇵 日本語 · 🇨🇳 中文 · 🇰🇷 한국어 · 🇪🇸 Español · 🇮🇹 Italiano · 🇷🇺 Русский · 🇸🇦 العربية · 🇹🇷 Türkçe

---

## 📋 Befehle

**Präfix:** `!`  
*(Aliase in Klammern)*

---

### 🌍 Sprachen

#### `!sprachen`
*(aliases: `!languages`, `!langues`, `!idiomas`, `!lang`)*

Öffnet ein interaktives Button-Menü zur globalen Sprachsteuerung.  
DE + FR sind immer aktiv. PT, EN, JA, ZH, KO können ein/ausgeschaltet werden.

**Berechtigung:** Administrator · R5 · R4 · dev

---

#### `!raumsprachen [Kanal-ID]`
*(aliases: `!roomlang`, `!chanallang`)*

Öffnet ein Button-Menü für raum-spezifische Spracheinstellungen.  
Überschreibt globale Einstellungen für den jeweiligen Kanal.

```
!raumsprachen 1234567890123456789
```

- ✅ Aktive Sprachen können einzeln ein/ausgeschaltet werden
- 🚫 **Übersetzung deaktivieren** — deaktiviert den Kanal dauerhaft (bleibt nach Neustart deaktiviert)
- 🌐 **Globale Einstellungen** — setzt den Kanal zurück auf globale Sprachen

**Nur im Bot-Log-Kanal nutzbar · Berechtigung:** R5 · DEV

**Tipp:** Mit `!kanalids` werden alle Kanal-IDs des Servers per DM zugeschickt.

---

### 🖼️ Bild-Übersetzer

#### `!übersetze`
*(aliases: `!uebersetze`, `!traduire`, `!traduzir`, `!ocr`, `!lese`, `!lire`)*

Liest Text aus einem Mecha-Fire-Screenshot (OCR) und übersetzt ihn in alle aktiven Sprachen.  
Unterstützt mehrere Bilder gleichzeitig (parallel verarbeitet).

**Verwendung:**
- Bild direkt mit dem Befehl hochladen
- Oder auf eine Nachricht mit Bild antworten und `!übersetze` eintippen

**Cooldown:** 15 Sekunden pro User  
**KI-Modell:** LLaMA 4 Scout 17B (Vision)

---

### ⏰ Event-Timer

#### `!event`
*(aliases: `!evenement`, `!evento`, `!ev`)*

Erkennt automatisch Event-Name und Countdown aus einem Mecha-Fire-Screenshot und setzt einen persistenten Timer.

**Verwendung:**
- Auf einen Event-Screenshot antworten und `!event` eintippen

**Ablauf:**
1. Bot analysiert das Bild (Vision-KI)
2. Event-Name wird auf DE · FR · PT übersetzt
3. Interaktives Menü zur Sprachauswahl für Erinnerungen erscheint
4. Timer wird in MongoDB gespeichert und feuert auch nach Bot-Neustart

**Vorwarnungen:**
- Event > 24h: 1 Stunde vorher
- Event > 1h: 15 Minuten vorher
- Event > 10min: 5 Minuten vorher

---

### ⏱️ Manuelle Timer

#### `!timer [DAUER] [EVENT]`
*(aliases: `!rappel`, `!erinnerung`, `!reminder`, `!lembrete`)*

Setzt einen manuellen, persistenten Timer.

```
!timer 2h Kriegsstart
!timer 30m Meeting
!timer 1h30m Alliance-Event
!timer 3d Saisonstart
```

**Zeitformate:** `30m` · `2h` · `1h30m` · `3d`

Nach dem Setzen öffnet sich ein Sprachauswahl-Menü (DE/FR immer aktiv, PT/EN/JA optional).  
Timer bleiben nach Bot-Neustart erhalten.

**Berechtigung:** Administrator · R5 · R4

---

#### `!timer list`
*(aliases: `!timer liste`, `!rappel list`)*

Zeigt alle aktiven Timer mit verbleibender Zeit und Delete-Buttons.

---

#### `!timer delete [EVENT]`
*(aliases: `!timer löschen`, `!rappel supprimer`, `!lembrete apagar`)*

Löscht einen Timer per Name.

---

#### `!timer help`
*(aliases: `!timer hilfe`, `!rappel aide`, `!lembrete ajuda`)*

Zeigt alle Timer-Befehle in DE · FR · PT.

---

### 📍 Koordinaten

#### `!koordinaten`
*(aliases: `!coord`, `!coords`, `!coordonnees`, `!coordenadas`)*

Zeigt alle gespeicherten Allianz-Koordinaten in Mecha Fire (Format: Name · R · X · Y).  
Für berechtigte User werden Delete-Buttons pro Koordinate angezeigt.

---

#### `!koordinaten add [NAME] [R] [X] [Y]`
*(aliases: `!koordinaten hinzufügen`, `!coordonnees ajouter`, `!coordenadas adicionar`)*

```
!koordinaten add VHA 75 217 802
```

**Berechtigung:** Administrator · R5 · R4

---

#### `!koordinaten delete [NAME]`
*(aliases: `!koordinaten löschen`, `!coordonnees supprimer`, `!coordenadas apagar`)*

```
!koordinaten delete VHA
```

---

#### `!koordinaten help`

Zeigt alle Koordinaten-Befehle in DE · FR · PT.

---

### ⚔️ SVS-Koordinaten (Server vs Server)

#### `!svs`
*(aliases: `!svs_koordinaten`, `!servervsserver`)*

Zeigt alle SVS-Koordinaten gruppiert nach Server.

```
!svs           # Alle Server
!svs R77       # Nur Server R77 (mit Delete-Buttons)
!svs server    # Liste aller verfügbaren Server
```

---

#### `!svs add [SERVER] [NAME] [R] [X] [Y]`

```
!svs add R77 "Centre gnz1" 77 244 574
```

**Berechtigung:** Administrator · R5 · R4

---

#### `!svs help`

Zeigt alle SVS-Befehle.

---

### 👥 Spieler-IDs

#### `!spieler`
*(aliases: `!joueur`, `!joueurs`, `!player`, `!players`, `!ids`)*

Zeigt alle gespeicherten Spieler-IDs.  
Für berechtigte User: paginierte Delete-Buttons (bis zu 20 pro Seite).

---

#### `!spieler add [NAME] [ID]`
*(aliases: `!spieler hinzufügen`, `!joueur ajouter`, `!player adicionar`)*

```
!spieler add Noxxi 3881385
```

**Berechtigung:** Administrator · R5 · R4

---

#### `!spieler delete [NAME]`
*(aliases: `!spieler löschen`, `!joueur supprimer`, `!player apagar`)*

---

#### `!spieler suche [SUCHE]`
*(aliases: `!spieler search`, `!spieler find`, `!joueur chercher`)*

Sucht nach Name oder ID.

```
!spieler suche Noxxi
!spieler suche 3881385
```

---

### 🏗️ Server-Struktur

#### `!server export`

Exportiert alle Kategorien und Kanäle des aktuellen Servers in MongoDB.

---

#### `!server preview`

Zeigt die zuletzt exportierte Server-Struktur an.

---

#### `!server import`

Erstellt Kategorien und Kanäle auf dem aktuellen Server basierend auf dem letzten Export.  
Bestehende Kanäle werden **nicht überschrieben**, nur fehlende werden erstellt.

**Berechtigung:** Administrator · R5

---

### 📋 Log

#### `!log [ANZAHL]`
*(aliases: `!logs`, `!verlauf`, `!historique`, `!historico`)*

Zeigt die letzten N Aktionen (Standard: 20, Max: 50).  
Nachricht löscht sich nach 120 Sekunden.

Erfasste Aktionen: Spieler/Koordinaten/SVS/Timer hinzugefügt oder gelöscht.

**Berechtigung:** dev · Administrator

---

#### `!log clear`
*(aliases: `!log leeren`, `!log vider`, `!log limpar`)*

Löscht alle Log-Einträge.

---

### 🔧 Sonstige Befehle

| Befehl | Funktion |
|---|---|
| `!kanalids` | Schickt alle Kanal-IDs des Servers als DM (für `!raumsprachen`) |
| `!translate on/off` | Schaltet die Auto-Translation global ein/aus |
| `!tokeninfo` | Zeigt heutigen Groq-Token-Verbrauch |

---

## 🗄️ MongoDB Datenstruktur

**Datenbank:** `vhabot`

| Collection | Inhalt |
|---|---|
| `sprachen` | Globale Spracheinstellungen (`_id: "settings"`) |
| `raumsprachen` | Raum-spezifische Sprachen (`_id: channel_id`) |
| `spieler` | Spieler-IDs (`name`, `id`) |
| `koordinaten` | Allianz-Koordinaten (`name`, `r`, `x`, `y`) |
| `svs` | SVS-Koordinaten (`server`, `name`, `r`, `x`, `y`) |
| `timers` | Aktive Timer inkl. mehrsprachiger Event-Namen und `end_timestamp` |
| `logs` | Activity-Log (max. 500 Einträge, älteste werden automatisch gelöscht) |
| `server_struktur` | Exportierte Server-Struktur (`_id: "export"`) |

---

## 🔐 Rollenberechtigungen

| Rolle | Berechtigungen |
|---|---|
| **Administrator** | Alle Befehle |
| **R5** | Timer, Koordinaten, SVS, Spieler, Sprachen, Raumsprachen, Server |
| **R4** | Timer, Koordinaten, SVS, Spieler |
| **dev** / **DEV** | Sprachen, Raumsprachen, Server, Log |
| **Creator** *(implizit dev)* | Log anzeigen & löschen |

---

## 🤖 KI-Modelle

| Modell | Verwendung |
|---|---|
| `llama-3.3-70b-versatile` | Spracherkennung, Text-Übersetzung, Event-Namen übersetzen |
| `meta-llama/llama-4-scout-17b-16e-instruct` | Vision: OCR aus Screenshots, Event-Erkennung |

**Rate-Limit-Handling:**
- Semaphore (max. 2 gleichzeitige Calls)
- Globale Pause bei 429 (exponentieller Backoff, max. 60s)
- Token-Verbrauch wird täglich per `groq_usage.log` geloggt

---

## 🌐 Flask Keep-Alive

Der Bot läuft auf Render als Web Service. Ein eingebetteter Flask-Server verhindert das Einschlafen:

- `GET /` → `"VHA Translator • Online"`
- `GET /ping` → `"pong"`

---

## 📝 Lizenz & Credits

Entwickelt für die **VHA Alliance** (Mecha Fire).  
Maintainer: **Noxxi-hub**
