# 🤖 VHA Haupt-Bot — README

**Version:** Gemini 2.5 Flash  
**Hosting:** Render (Free Tier) + UptimeRobot Keep-Alive  
**Sprache:** Python 3.11+

---

## 📋 Übersicht

Der VHA Haupt-Bot ist der primäre Übersetzungsbot für die VHA Alliance Discord-Server. Er übersetzt Nachrichten automatisch in Deutsch, Französisch und Englisch und bietet zusätzlich KI-Assistenz sowie Server-Management-Tools.

---

## ⚙️ Technologie-Stack

| Komponente | Details |
|---|---|
| **KI-Modell** | Google Gemini 2.5 Flash (primär) |
| **Fallback** | Gemini 2.5 Flash Lite → Gemini 3 Flash Preview |
| **Datenbank** | MongoDB Atlas (`vhabot`) |
| **Web-Server** | Flask (Keep-Alive für Render) |
| **Discord-Library** | discord.py |
| **Hosting** | Render Free Tier |

---

## 🌍 Übersetzung

### Wie es funktioniert
Der Bot erkennt automatisch die Sprache jeder Nachricht und übersetzt sie in die aktiven Zielsprachen. Die Übersetzung erfolgt mit Google Gemini — natürlich und menschlich, nicht wörtlich.

### Feste Sprachen (immer aktiv)
- 🇩🇪 Deutsch
- 🇫🇷 Französisch  
- 🇬🇧 Englisch

### Zuschaltbare Sprachen (über `!sprachen`)
- 🇧🇷 Português
- 🇯🇵 日本語
- 🇨🇳 中文
- 🇰🇷 한국어
- 🇪🇸 Español
- 🇷🇺 Русский

### Übersetzungsregeln
- Immer **Du-Form** — niemals "Sie" oder "Vous"
- Kosenamen werden korrekt übersetzt (süße → chérie/honey, schatz → chéri/darling)
- Spielerbegriffe werden **nie** übersetzt: R1–R5, Koordinaten, Spielernamen, @mentions
- Emojis bleiben unverändert

### Qualitätssicherung
Der Bot prüft jede Übersetzung automatisch auf:
- Identische Texte (nicht übersetzt) → verworfen
- Falsche Sprache im Feld → verworfen
- Wiederholungs-Loops → verworfen
- Zu lange Ausgaben → abgeschnitten

---

## 📁 Dateistruktur

```
app.py              — Hauptdatei: Bot-Logik, Gemini-Calls, on_message
sprachen.py         — Globale Spracheinstellungen (MongoDB)
raumsprachen.py     — Raumspezifische Spracheinstellungen (MongoDB)
server.py           — Server-Struktur Export/Import
bilduebersetzer.py  — Screenshot-Übersetzung (!übersetze)
event.py            — Event-Erkennung aus Screenshots
requirements.txt    — Python-Abhängigkeiten
```

---

## 🔑 Umgebungsvariablen (Render)

| Variable | Beschreibung |
|---|---|
| `DISCORD_TOKEN` | Discord Bot Token |
| `GEMINI_API_KEY` | Google AI Studio API Key |
| `MONGODB_URI` | MongoDB Atlas Connection String |

---

## 💬 Befehle

### 🌐 Übersetzung
| Befehl | Beschreibung | Berechtigung |
|---|---|---|
| `!sprachen` | Globale Zielsprachen ein/ausschalten | R5, R4, DEV |
| `!raumsprachen [Kanal-ID]` | Sprachen für einen bestimmten Raum einstellen | R5, DEV |
| `!kanalid` | Alle Kanal-IDs als Direktnachricht | Alle |
| `!translate [Text]` | Text manuell übersetzen | Manage Messages |

### 🤖 KI-Assistent
| Befehl | Beschreibung | Berechtigung |
|---|---|---|
| `!ai [Frage]` | KI-Frage stellen (Gemini mit Thinking) | Alle |

### 🗑️ Kanal verwalten
| Befehl | Beschreibung | Berechtigung |
|---|---|---|
| `!clean` | Alle Nachrichten im Kanal löschen (mit Bestätigung) | Bot DEV only |
| `!clean [Zahl]` | Bestimmte Anzahl Nachrichten löschen | Bot DEV only |

### 🏗️ Server-Struktur
| Befehl | Beschreibung | Berechtigung |
|---|---|---|
| `!server export` | Aktuelle Server-Struktur in MongoDB speichern | Bot DEV only |
| `!server preview` | Gespeicherte Struktur anzeigen | Bot DEV only |
| `!server import` | Struktur auf neuem Server erstellen | Bot DEV only |

### 📊 Status
| Befehl | Beschreibung | Berechtigung |
|---|---|---|
| `!ping` | Bot-Status und Latenz anzeigen | Alle |
| `!help` | Alle Befehle anzeigen | Alle |

---

## 🖼️ Bild-Übersetzung

Mit `!übersetze` (oder Reply auf ein Bild) kann ein Screenshot aus Mecha Fire oder Discord übersetzt werden. Der Bot:
- Erkennt Text aus dem Bild (OCR via Gemini Vision)
- Erkennt automatisch doppelte Texte (Original + Spiel-Übersetzung) und behält nur das Original
- Erkennt Spielernamen und zeigt sie **fett** vor der Nachricht
- Übersetzt in alle 4 Sprachen: DE, FR, EN, PT

---

## 🗄️ MongoDB Collections

| Collection | Inhalt |
|---|---|
| `sprachen` | Globale Spracheinstellungen |
| `raumsprachen` | Raumspezifische Einstellungen |
| `server_struktur` | Gespeicherte Server-Strukturen |
| `logs` | Bot-Logs |

---

## 🔄 Modell-Fallback

Der Bot nutzt automatisch ein Fallback-System bei Überlastung:

```
gemini-2.5-flash          ← primär (beste Qualität)
    ↓ bei 503/429
gemini-2.5-flash-lite     ← schneller, leichter
    ↓ bei 503/429
gemini-3-flash-preview    ← letzter Fallback
```

---

## 📦 Installation (requirements.txt)

```
discord.py
flask
google-genai
pymongo
aiohttp
```

---

## 🚀 Deploy auf Render

1. GitHub-Repo mit allen Dateien verbinden
2. Umgebungsvariablen in Render setzen
3. Start-Befehl: `python app.py`
4. UptimeRobot auf `https://[deine-render-url]/ping` setzen (alle 5 Minuten)

---

## ⚠️ Bekannte Einschränkungen

- Render Free Tier: kann bei Inaktivität schlafen gehen (UptimeRobot verhindert das)
- Discord Bulk-Delete: funktioniert nur für Nachrichten jünger als 14 Tage
- Gemini kann bei hoher Last langsamer sein (Google-seitig)
