import discord
from discord.ext import commands
import google.generativeai as genai
import os
from flask import Flask
import threading

# 1. Webserver für Render
app = Flask(__name__)
@app.route('/')
def home(): 
    return "Bot Herzschlag: Aktiv!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. KI Setup - Präzise Modell-Bezeichnung
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# Wir nutzen hier den vollen Pfad 'models/gemini-1.5-flash'
model = genai.GenerativeModel('models/gemini-1.5-flash')

# 3. Discord Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'--- ERFOLG ---')
    print(f'Eingeloggt als: {bot.user.name}')
    print(f'--------------')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # TEST-BEFEHL
    if message.content.lower().startswith("!test"):
        await message.reply("Ich höre dich! Der Bot kann antworten.")
        return

    # GEMINI-BEFEHL
    if message.content.lower().startswith("!gemini"):
        query = message.content[7:].strip()
        if not query:
            await message.reply("Bitte gib eine Frage ein.")
            return

        async with message.channel.typing():
            try:
                # Generierung mit dem neuen Modellnamen
                response = model.generate_content(query)
                if response and response.text:
                    await message.reply(response.text)
                else:
                    await message.reply("Die KI hat keine Textantwort geliefert.")
            except Exception as e:
                print(f"KI FEHLER: {e}")
                await message.reply(f"Fehler in der KI-Verarbeitung: {e}")
        return

    # AUTOMATISCHE ÜBERSETZUNG (DE <-> FR)
    if len(message.content) > 3 and not message.content.startswith("!"):
        try:
            async with message.channel.typing():
                prompt = f"Übersetze DE<->FR, sonst antworte NUR mit 'SKIP': {message.content}"
                response = model.generate_content(prompt)
                if response.text and "SKIP" not in response.text.upper():
                    await message.reply(f"🌍 {response.text}")
        except Exception:
            pass # Ignorieren bei Fehlern in der Automatik

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("FEHLER: Kein DISCORD_TOKEN gefunden!")
