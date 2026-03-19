import discord
from discord.ext import commands
import os
from flask import Flask
import threading
import sys
from groq import Groq

app = Flask(__name__)
@app.route('/')
def home(): return "VHA Translator Stable"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

auto_translate = True
last_processed_id = 0

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="VHA | Übersetzer aktiv"))
    print(f'--- {bot.user.name} BEREIT ---')

@bot.event
async def on_message(message):
    global auto_translate, last_processed_id
    
    # 1. Sofort-Sperren
    if message.author == bot.user or message.id == last_processed_id:
        return
    
    # Ignoriere ganz kurze Sachen (Haha, Lol, Hi)
    if len(message.content) < 4 and not message.content.startswith("!"):
        return

    # 2. BEFEHLE
    if message.content.lower().startswith("!auto"):
        auto_translate = "on" in message.content.lower()
        status = "AN ✅" if auto_translate else "AUS 😴"
        await message.reply(f"🛰️ Automatische Übersetzung ist jetzt {status}")
        return

    # 3. KI-CHAT (!ai) - Hier darf er ausführlich sein
    if message.content.lower().startswith("!ai "):
        query = message.content[4:].strip()
        async with message.channel.typing():
            try:
                res = client.chat.completions.create(
                    messages=[{"role": "system", "content": "Antworte kurz und präzise in der Sprache des Nutzers."},
                              {"role": "user", "content": query}],
                    model=MODEL_NAME, temperature=0.5
                )
                last_processed_id = message.id
                await message.reply(res.choices[0].message.content)
            except: pass
        return

    # 4. REINE ÜBERSETZUNG (STRENGER MODUS)
    if auto_translate and not message.content.startswith("!"):
        # Blacklist für unnötige Übersetzungen
        if message.content.lower().strip() in ["haha", "lol", "ok", "danke", "merci"]:
            return

        try:
            # Der Prompt ist jetzt extrem minimalistisch
            t_prompt = (
                "Du bist ein 1:1 Übersetzer für einen Discord-Server. \n"
                "Regeln:\n"
                "1. Deutsch zu Französisch (🇫🇷).\n"
                "2. Französisch zu Deutsch (🇩🇪).\n"
                "3. Andere Sprachen zu DE (🇩🇪) UND FR (🇫🇷).\n"
                "4. ANTWORTE NUR MIT DER ÜBERSETZUNG. Kein 'Die Person sagt', keine Kommentare.\n"
                "5. Wenn der Text keinen Sinn macht oder nur aus Emojis besteht, antworte nur: SKIP\n"
                f"Text: {message.content}"
            )
            
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": t_prompt}],
                model=MODEL_NAME, 
                temperature=0.0  # Absolut keine Kreativität mehr!
            )
            result = completion.choices[0].message.content
            
            if result and "SKIP" not in result.upper():
                last_processed_id = message.id
                await message.reply(result)
        except: pass

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(os.getenv("DISCORD_TOKEN"))
