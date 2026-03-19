import discord
from discord.ext import commands
import os
from flask import Flask
import threading
import sys
from groq import Groq

# 1. Webserver für Render (Uptime)
app = Flask(__name__)
@app.route('/')
def home(): 
    return "VHA Universal Translator Online"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# 2. Groq KI Setup
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile"

# 3. Discord Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

auto_translate = True
last_processed_msg = None

@bot.event
async def on_ready():
    activity = discord.Game(name="VHA Guard | !info", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print(f'--- {bot.user.name} ONLINE ---')
    sys.stdout.flush()

@bot.event
async def on_message(message):
    global auto_translate, last_processed_msg
    
    # 1. Grund-Sperren (Ignoriere Bots & Doppelnachrichten)
    if message.author == bot.user:
        return
    
    current_msg_fingerprint = f"{message.author.id}_{message.content}"
    if last_processed_msg == current_msg_fingerprint:
        return
    last_processed_msg = current_msg_fingerprint

    # 2. BEFEHLE (DREISPRACHIG)
    if message.content.lower() in ["!info", "!help"]:
        help_text = (
            "**🌍 VHA Universal Assistant**\n\n"
            "🇩🇪 **DE:** Automatische Übersetzung für alle Sprachen.\n"
            "🇫🇷 **FR:** Traduction automatique pour toutes les langues.\n"
            "🇺🇸 **EN:** Automatic translation for all languages.\n\n"
            "**Commands:** `!ai [Text]` | `!auto on/off` | `!status`"
        )
        await message.reply(help_text)
        return

    if message.content.lower() == "!status":
        s = "AKTIV ✅ / ACTIF ✅" if auto_translate else "OFF 😴"
        await message.reply(f"🛰️ **System Status:** {s}")
        return

    if message.content.lower() == "!auto on":
        auto_translate = True
        await message.reply("✅ **Universal Translator ON**")
        return
        
    if message.content.lower() == "!auto off":
        auto_translate = False
        await message.reply("😴 **Universal Translator OFF**")
        return

    # KI CHAT (!ai)
    if message.content.lower().startswith("!ai "):
        query = message.content[4:].strip()
        async with message.channel.typing():
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "system", "content": "You are the VHA Assistant. Answer in the user's language."},
                              {"role": "user", "content": query}],
                    model=MODEL_NAME,
                    temperature=0.6
                )
                await message.reply(chat_completion.choices[0].message.content)
            except:
                await message.reply("❌ Error.")
        return

    # 3. UNIVERSAL-ÜBERSETZUNG (MIT FILTER GEGEN SPAM/HAHA)
    if auto_translate and len(message.content) > 3 and not message.content.startswith("!"):
        
        # FILTER: Ignoriere Lacher und kurze Reaktionen (Blacklist)
        low_msg = message.content.lower().strip()
        blacklist = ["haha", "lol", "xd", "hi", "hey", "ok", "danke", "merci", "thanks", "gut", "bien", "nice"]
        if any(word == low_msg for word in blacklist):
            return

        try:
            context_info = ""
            if message.reference and message.reference.message_id:
                try:
                    ref_msg = await message.channel.fetch_message(message.reference.message_id)
                    context_info = f"\n(Note: This is a reply to: '{ref_msg.content}')"
                except:
                    pass

            t_prompt = (
                f"Task: Smart Translation for VHA.\n"
                f"Input: '{message.content}'{context_info}\n\n"
                f"Strict Rules:\n"
                f"1. ONLY translate if the content has actual meaning.\n"
                f"2. DO NOT translate laughs, greetings, or single-word reactions.\n"
                f"3. If Input is German -> Translate to French (start with 🇫🇷).\n"
                f"4. If Input is French -> Translate to German (start with 🇩🇪).\n"
                f"5. If Other -> Translate to BOTH German (🇩🇪) and French (🇫🇷).\n"
                f"6. If it's a reply, use context but translate the 'Input' only.\n"
                f"7. Answer ONLY with translation and flags. If unnecessary, answer 'SKIP'."
            )
            
            completion = client.chat.completions.create(
                messages=[{"role": "user", "content": t_prompt}],
                model=MODEL_NAME,
                temperature=0.1
            )
            result = completion.choices[0].message.content
            if result and "SKIP" not in result.upper() and len(result) > 2:
                await message.reply(result)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    token = os.getenv("DISCORD_TOKEN")
    if token:
        bot.run(token)
