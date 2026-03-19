import discord
from discord.ext import commands
import os
from flask import Flask
import threading
from groq import Groq
import re

# 1. Webserver für Render
app = Flask(__name__)
@app.route('/')
def home(): return "VHA Translator - Trilingual Edition"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

# 2. KI Setup
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.3-70b-versatile"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# STATUS & SPEICHER
translate_active = True
processed_messages = set()

def detect_language_manually(text):
    t = text.lower()
    if any(re.search(rf'\b{w}\b', t) for w in ["c'est", "oui", "je", "suis", "pas", "le", "la", "et", "que", "pour", "est", "dans"]):
        return "FR"
    if any(re.search(rf'\b{w}\b', t) for w in ["ist", "ja", "ich", "bin", "nicht", "das", "die", "und", "dass", "für", "mit", "auch"]):
        return "DE"
    if any(re.search(rf'\b{w}\b', t) for w in ["is", "the", "and", "have", "you", "this", "with", "what"]):
        return "EN"
    return "UNKNOWN"

@bot.event
async def on_ready():
    print(f'--- {bot.user.name} TRILINGUAL READY ---')

# --- DREISPRACHIGES HILFE MENÜ ---
@bot.command(name="help")
async def custom_help(ctx):
    embed = discord.Embed(title="🤖 VHA Translator - Help / Aide / Hilfe", color=discord.Color.blue())
    
    # Deutsch
    embed.add_field(name="🇩🇪 Deutsch", value="`!translate on/off`: Automatik an/aus\n`!ai [Frage]`: KI direkt fragen", inline=False)
    
    # Französisch
    embed.add_field(name="🇫🇷 Français", value="`!translate on/off`: Activer/Désactiver la traduction\n`!ai [Question]`: Poser une question à l'IA", inline=False)
    
    # Englisch
    embed.add_field(name="🇬🇧 English", value="`!translate on/off`: Toggle translation\n`!ai [Question]`: Ask the AI directly", inline=False)
    
    embed.add_field(name="✨ Features", value="Translates DE ↔ FR ↔ EN. Automatically detects other languages (like Japanese) and replies in the original language when using the 'Reply' function.", inline=False)
    
    await ctx.send(embed=embed)

# --- DREISPRACHIGE AN/AUS AUSGABE ---
@bot.command(name="translate")
async def toggle_translate(ctx, status: str):
    global translate_active
    if status.lower() == "on":
        translate_active = True
        await ctx.send("✅ **Translation Active / Traduction activée / Übersetzung aktiviert.**")
    elif status.lower() == "off":
        translate_active = False
        await ctx.send("😴 **Translation Disabled / Traduction désactivée / Übersetzung deaktiviert.**")

@bot.event
async def on_message(message):
    global processed_messages, translate_active
    if message.author == bot.user or message.id in processed_messages:
        return

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    text = message.content.strip()
    if not translate_active or len(text) <= 2:
        return

    # Auto-Ignore
    if text.lower() in ["haha", "lol", "ok", "merci", "danke", "thanks", "top", "nice", "ja", "oui", "yes"]:
        return

    processed_messages.add(message.id)
    if len(processed_messages) > 150: processed_messages.clear()

    # Reply Check
    is_reply = False
    replied_text = ""
    if message.reference and message.reference.message_id:
        try:
            replied_to = await message.channel.fetch_message(message.reference.message_id)
            replied_text = replied_to.content
            is_reply = True
        except: pass

    input_lang = detect_language_manually(text)
    
    # SYSTEM PROMPT
    if is_reply:
        sys_msg = (f"Übersetze in DE (🇩🇪), FR (🇫🇷) und die Sprache von '{replied_text}'. "
                   "Regel: NUR Übersetzungen. KEINE Erklärungen.")
    elif input_lang == "FR":
        sys_msg = "Übersetze NUR ins Deutsche (🇩🇪) und Englische (🇬🇧)."
    elif input_lang == "DE":
        sys_msg = "Übersetze NUR ins Französische (🇫🇷) und Englische (🇬🇧)."
    elif input_lang == "EN":
        sys_msg = "Übersetze NUR ins Deutsche (🇩🇪) und Französische (🇫🇷)."
    else:
        sys_msg = "Übersetze in DE (🇩🇪), FR (🇫🇷) und EN (🇬🇧). NUR Ergebnisse."

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "system", "content": "Du bist ein stummer Übersetzer. Gib nur Zieltexte aus."},
                      {"role": "user", "content": f"{sys_msg}\n\nText: {text}"}],
            model=MODEL_NAME, temperature=0.0
        )
        result = completion.choices[0].message.content.strip()
        
        # Filter
        lines = result.split('\n')
        final_lines = []
        for line in lines:
            l_low = line.lower()
            if any(x in l_low for x in ["sprache ist", "identisch", "bleibt gleich", "original"]):
                continue
            clean = line.replace("🇩🇪", "").replace("🇫🇷", "").replace("🇬🇧", "").strip().lower()
            if clean != text.lower() and len(clean) > 0:
                final_lines.append(line)
        
        output = "\n".join(final_lines).strip()
        if output:
            await message.reply(output)
    except: pass

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(os.getenv("DISCORD_TOKEN"))
