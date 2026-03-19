import discord
from discord.ext import commands
import google.generativeai as genai
import os
from flask import Flask
import threading
import sys

# 1. Webserver für Render
app = Flask(__name__)
@app.route('/')
def home(): 
    return "Bot Herzschlag: Aktiv!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. KI Setup - Gemini 2.5 Flash
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

# 3. Discord Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Status-Variable
auto_translate = True

@bot.event
async def on_ready():
    print(f'--- BOT MULTI-KULTI ONLINE ---')
    print(f'Eingeloggt als: {bot.user.name}')
    sys.stdout.flush()

@bot.event
async def on_message(message):
    global auto_translate
    if message.author == bot.user:
        return

    # BEFEHL: HILFE (Zweisprachig DE/FR)
    if message.content.lower() == "!help":
        help_text = (
            "**🌍 Universal Translator Bot**\n\n"
            "• `!auto on` : Übersetzung an / Traduction activée ✅\n"
            "• `!auto off`: Übersetzung aus / Traduction désactivée 😴\n"
            "• `!gemini [Text]`: KI-Chat / Discuter mit l'IA 🤖\n\n"
            "**Info:** Ich übersetze automatisch zwischen Deutsch, Französisch und allen anderen Sprachen (Türkisch, Englisch, etc.)!"
        )
        await message.reply(help_text)
        return

    # STATUS-BEFEHLE
    if message.content.lower() == "!auto on":
        auto_translate = True
        await message.reply("✅ **Aktiviert!** Ich übersetze jetzt alles für unsere Gruppe.")
        return

    if message.content.lower() == "!auto off":
        auto_translate = False
        await message.reply("😴 **Deaktiviert.** Ich reagiere nur noch auf Befehle.")
        return

    # DIREKTE KI-ANFRAGE
    if message.content.lower().startswith("!gemini"):
        query = message.content[7:].strip()
        async with message.channel.typing():
            try:
                response = model.generate_content(query)
                await message.reply(response.text)
            except Exception as e:
                await message.reply(f"Fehler: {e}")
        return

    # 4. MULTI-SPRACH-ÜBERSETZUNG (Universal)
    if auto_translate and len(message.content) > 2 and not message.content.startswith("!"):
        try:
            # Die Logik: Deutsch <-> Französisch, Alles andere -> DE & FR
            prompt = (
                f"Du bist ein Dolmetscher in einem Chat mit Deutschen, Franzosen und internationalen Gästen. "
                f"Regeln:\n"
                f"1. Wenn der Text DEUTSCH ist -> übersetze NUR ins FRANZÖSISCHE.\n"
                f"2. Wenn der Text FRANZÖSISCH ist -> übersetze NUR ins DEUTSCHE.\n"
                f"3. Wenn der Text eine ANDERE SPRACHE ist -> übersetze ihn in BEIDE (Deutsch & Französisch).\n"
                f"4. Antworte NUR mit 'SKIP', wenn keine Übersetzung nötig ist (z.B. Emojis, Namen).\n"
                f"Text: {message.content}"
            )
            
            async with message.channel.typing():
                response = model.generate_content(prompt)
                if response.text and "SKIP" not in response.text.upper():
                    await message.reply(f"🌍 {response.text}")
        except:
            pass

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
