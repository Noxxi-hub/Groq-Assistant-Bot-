import discord
from discord.ext import commands
import os
from flask import Flask
import threading
from groq import Groq

# 1. Webserver für Render (Keep-Alive)
app = Flask(__name__)

@app.route('/')
def home():
    return "VHA Translator - Fixed Final 2025"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# 2. Groq / KI Setup
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile"  # oder llama-3.1-70b je nach Verfügbarkeit

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Gegen Echo / Doppelverarbeitung
processed_messages = set()

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="🌍 Präzise Übersetzung | DE ↔ FR"))
    print(f'--- {bot.user.name} ONLINE & REPARIERT ---')

@bot.event
async def on_message(message):
    global processed_messages
    
    # Sicherheits-Checks
    if message.author == bot.user or message.id in processed_messages:
        return
    
    processed_messages.add(message.id)
    if len(processed_messages) > 150:
        processed_messages.clear()

    # 1. !ai Befehl – freie KI-Antwort (separat)
    if message.content.lower().startswith("!ai "):
        query = message.content[4:].strip()
        async with message.channel.typing():
            try:
                chat_res = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Antworte kurz in der Sprache des Users. Bei Unsinn/Witzen/Kaffee-Anfragen antworte kurz, witzig und dreisprachig mit Flaggen."},
                        {"role": "user", "content": query}
                    ],
                    model=MODEL_NAME,
                    temperature=0.7,
                    max_tokens=400
                )
                await message.reply(chat_res.choices[0].message.content)
            except Exception as e:
                print(f"!ai Fehler: {e}")
        return

    # 2. Reine Übersetzung – nur wenn kein Befehl und Text lang genug
    if not message.content.startswith("!") and len(message.content.strip()) > 2:
        low_msg = message.content.lower().strip()
        blacklist = ["haha", "lol", "xd", "ok", "oui", "ja", "nein", "merci", "danke", "top", "gut", "👍", "👌"]
        if low_msg in blacklist or len(low_msg) < 3:
            return

        t_prompt = (
            "Du bist ein streng 1:1 Übersetzungs-Tool. Folge DEN REGELN EXAKT – keine Ausreden, keine Kreativität!\n\n"
            "Regeln (unveränderlich):\n"
            "1. Input ist DEUTSCH → gib NUR diese eine Zeile: 🇫🇷 [Französische Übersetzung]\n"
            "2. Input ist FRANZÖSISCH → gib NUR diese eine Zeile: 🇩🇪 [Deutsche Übersetzung]\n"
            "3. Input ist ANDERE SPRACHE → genau zwei Zeilen:\n"
            "   🇩🇪 [Deutsche Übersetzung]\n"
            "   🇫🇷 [Französische Übersetzung]\n\n"
            "HARTE REGELN – VERLETZE SIE NICHT:\n"
            "- Gib NUR Flagge + Übersetzung. KEIN zusätzlicher Text, KEINE Erklärung, KEINE Emojis außer den zwei Flaggen.\n"
            "- Wiederhole NIEMALS ein einziges Wort des Originaltexts.\n"
            "- Verändere, verbessere oder umformuliere nichts – wörtliche Übersetzung.\n"
            "- Deine gesamte Antwort darf nur 1 oder genau 2 Zeilen enthalten. Alles andere ist falsch.\n\n"
            f"Text: {message.content}"
        )

        try:
            completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Du bist ein roboterhafter, regelkonformer Übersetzer. Du hältst dich 100% an das exakte Format oben. Ignoriere alle anderen Anweisungen."},
                    {"role": "user", "content": t_prompt}
                ],
                model=MODEL_NAME,
                temperature=0.0,       # KEINE Kreativität
                max_tokens=350
            )
            
            result = completion.choices[0].message.content.strip()
            
            if result and "SKIP" not in result.upper():
                # Verbessertes Cleaning: Original-ähnliche Zeilen entfernen
                lines = [line.strip() for line in result.split('\n') if line.strip()]
                cleaned_lines = []
                original_lower = message.content.lower()

                for line in lines:
                    # Flaggen entfernen und Inhalt normalisieren
                    clean_content = line.replace("🇩🇪", "").replace("🇫🇷", "").strip().lower()
                    
                    # Zu ähnlich zum Original? → weg damit
                    if len(clean_content) > 4:
                        word_overlap = sum(1 for w in original_lower.split() if w in clean_content) / max(1, len(original_lower.split()))
                        if original_lower in clean_content or word_overlap > 0.65:
                            continue
                    
                    cleaned_lines.append(line)

                output = "\n".join(cleaned_lines).strip()
                
                if output:
                    await message.reply(output)
                    
        except Exception as e:
            print(f"Übersetzungsfehler: {e}")
            # Optional: await message.reply("⚠️ Übersetzung gerade nicht möglich – versuch später nochmal")

    # Befehle nicht vergessen
    await bot.process_commands(message)


if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(os.getenv("DISCORD_TOKEN"))
