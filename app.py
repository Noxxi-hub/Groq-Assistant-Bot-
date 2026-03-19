import discord
from discord.ext import commands
import os
import re
import threading
from flask import Flask
from groq import Groq

# ────────────────────────────────────────────────
# KONFIGURATION
# ────────────────────────────────────────────────

LOGO_URL = (
    "https://cdn.discordapp.com/attachments/1484252260614537247/"
    "1484253018533662740/Picsart_26-03-18_13-55-24-994.png"
    "?ex=69bd8dd7&is=69bc3c57&hm=de6fea399dd30f97d2a14e1515c9e7f91d81d0d9ea111f13e0757d42eb12a0e5&"
)

GROQ_MODEL = "llama-3.3-70b-versatile"

# ────────────────────────────────────────────────
# GLOBALS & FLASK
# ────────────────────────────────────────────────

app = Flask(__name__)
processed_messages = set()
translate_active = True


def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


@app.route("/")
def home():
    return "VHA Translator • Online"


# ────────────────────────────────────────────────
# SPRACHE ERKENNEN – für automatische Übersetzung
# ────────────────────────────────────────────────

def detect_language_simple(text: str) -> str:
    if not text or len(text.strip()) < 3:
        return "UNKNOWN"

    t = " " + text.lower().strip() + " "

    # Französisch
    fr_indicators = [
        " je ", " tu ", " il ", " elle ", " nous ", " vous ", " ils ", " elles ",
        " suis ", " es ", " est ", " êtes ", " sommes ", " sont ",
        " c'est ", " ça ", " qu' ", " qui ", " quoi ", " comment ", " pourquoi ",
        " quand ", " où ", " combien ", " merci ", " salut ", " bonjour ",
        " pardon ", " désolé ", " voilà ", " oui ", " non ",
        " le ", " la ", " les ", " un ", " une ", " des ", " du ", " au ", " aux "
    ]
    if any(ind in t for ind in fr_indicators):
        return "FR"

    # Deutsch
    de_indicators = [
        " ich ", " du ", " er ", " sie ", " es ", " wir ", " ihr ", " ist ",
        " bin ", " bist ", " sind ", " war ", " waren ", " haben ", " hast ", " hat ",
        " der ", " die ", " das ", " ein ", " eine ", " und ", " oder ", " aber ",
        " dass ", " was ", " wie ", " warum ", " bitte ", " danke ", " ja ", " nein "
    ]
    if any(ind in t for ind in de_indicators):
        return "DE"

    return "UNKNOWN"


# ────────────────────────────────────────────────
# BOT SETUP
# ────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
    case_insensitive=True
)


@bot.event
async def on_ready():
    print(f"→ {bot.user}  •  ONLINE  •  {discord.utils.utcnow():%Y-%m-%d %H:%M UTC}")


# ────────────────────────────────────────────────
# BEFEHLE
# ────────────────────────────────────────────────

@bot.command(name="help")
async def cmd_help(ctx):
    embed = discord.Embed(
        title="VHA Translator – Hilfe",
        color=discord.Color.blue()
    )
    embed.set_author(name="VHA ALLIANCE", icon_url=LOGO_URL)
    embed.set_thumbnail(url=LOGO_URL)

    embed.add_field(
        name="Befehle",
        value=(
            "`!translate on/off` → Automatische Übersetzung DE↔FR an/aus\n"
            "`!ai [Frage]` → KI antwortet in der Sprache deiner Frage"
        ),
        inline=False
    )

    embed.set_footer(text="VHA - Powering Communication", icon_url=LOGO_URL)
    await ctx.send(embed=embed)


@bot.command(name="translate")
async def cmd_toggle_translate(ctx, status: str = None):
    global translate_active

    if status is None:
        translate_active = not translate_active
    else:
        translate_active = status.lower() in ("on", "an", "ein", "true", "1", "aktiviert", "active")

    color = discord.Color.green() if translate_active else discord.Color.red()

    de_status = "Aktiviert" if translate_active else "Deaktiviert"
    fr_status = "Activée" if translate_active else "Désactivée"

    embed = discord.Embed(
        title="VHA System",
        description=f"**Übersetzung {de_status}**\n**Traduction {fr_status}**",
        color=color
    )
    embed.set_author(name="VHA System", icon_url=LOGO_URL)

    await ctx.send(embed=embed)


@bot.command(name="ai")
@commands.cooldown(1, 12, commands.BucketType.user)
async def cmd_ai(ctx, *, question: str = None):
    if not question or not question.strip():
        embed = discord.Embed(
            description="❓ Beispiel:\n`!ai Was ist die VHA?`\n`!ai Qui est la VHA ?`",
            color=discord.Color.orange()
        )
        embed.set_author(name="VHA ALLIANCE", icon_url=LOGO_URL)
        await ctx.send(embed=embed)
        return

    thinking = await ctx.send(embed=discord.Embed(
        description="**Denke nach …** 🧠",
        color=discord.Color.blurple()
    ))

    lang_code = detect_language_simple(question)

    lang_map = {
        "DE": ("Deutsch",    "auf Deutsch",     "Antwort auf Deutsch"),
        "FR": ("Französisch","auf Französisch", "Réponse en français"),
    }

    display_name, prompt_lang, footer_text = lang_map.get(lang_code, ("Deutsch", "auf Deutsch", "Antwort auf Deutsch"))

    system_content = f"""Du bist ein hilfreicher Assistent der VHA Alliance.

**WICHTIG – SPRACHE:**
- Antworte **ausschließlich** in der Sprache der gestellten Frage.
- Französische Frage → komplett französisch
- Deutsche Frage    → komplett deutsch
- Keine Sprachkommentare, kein Code-Switching
"""

    try:
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.75,
            max_tokens=1400,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user",   "content": question.strip()}
            ]
        )

        answer = completion.choices[0].message.content.strip()
        color = discord.Color.from_rgb(88, 101, 242)

    except Exception as e:
        answer = f"Fehler bei der KI-Anfrage:\n{type(e).__name__}: {str(e)}"
        color = discord.Color.red()
        footer_text = "Fehler"

    embed = discord.Embed(
        title="VHA KI • Antwort",
        description=answer[:4000],
        color=color
    )
    embed.set_author(name="VHA ALLIANCE", icon_url=LOGO_URL)
    embed.set_thumbnail(url=LOGO_URL)
    embed.add_field(name="Deine Frage", value=f"→ {question[:1000]}", inline=False)
    embed.set_footer(
        text=f"VHA • Groq • {GROQ_MODEL} • {footer_text}",
        icon_url=LOGO_URL
    )

    await thinking.edit(embed=embed)


# ────────────────────────────────────────────────
# AUTOMATISCHE ÜBERSETZUNG – NUR DE→FR oder FR→DE
# ────────────────────────────────────────────────

@bot.event
async def on_message(message: discord.Message):
    global processed_messages, translate_active

    if message.author.bot:
        return

    if message.id in processed_messages:
        return

    processed_messages.add(message.id)
    if len(processed_messages) > 300:
        processed_messages.clear()

    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    if not translate_active:
        return

    content = message.content.strip()
    if len(content) < 4:
        return

    low = content.lower()
    if low in {
        "ok", "lol", "xd", "haha", "ja", "nein", "oui", "non", "danke", "merci",
        "gg", "?", "!", "😂", "😅", "😭", "👍", "👌", "bruh", "wtf", "np", "kk"
    }:
        return

    lang = detect_language_simple(content)

    if lang == "DE":
        flag = "🇫🇷"
        system_prompt = (
            "Du bist ein sehr natürlicher, umgangssprachlicher Übersetzer. "
            "Übersetze den folgenden deutschen Text **locker, jugendlich und idiomatisch** ins Französische. "
            "Gib **ausschließlich** die französische Übersetzung aus – "
            "KEINEN einleitenden Satz, KEIN 'Voici la traduction:', KEIN 'En français:', "
            "KEIN Originaltext, KEIN Kommentar, KEINE Erklärung, nur den reinen französischen Text."
        )
    elif lang == "FR":
        flag = "🇩🇪"
        system_prompt = (
            "Du bist ein sehr natürlicher, umgangssprachlicher Übersetzer. "
            "Übersetze den folgenden französischen Text **locker, jugendlich und idiomatisch** ins Deutsche. "
            "Gib **ausschließlich** die deutsche Übersetzung aus – "
            "KEINEN einleitenden Satz, KEIN 'Voici la traduction:', KEIN 'Auf Deutsch:', "
            "KEIN Originaltext, KEIN Kommentar, KEINE Erklärung, nur den reinen deutschen Text."
        )
    else:
        return

    try:
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.15,           # sehr stabil & natürlich
            max_tokens=700,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content}
            ]
        )

        translation = completion.choices[0].message.content.strip()

        if not translation or len(translation) < 6:
            return

        # Sanfter Kopie-Filter (nicht 1:1)
        orig_clean = re.sub(r'[^a-zA-Z0-9äöüÄÖÜßéèêàâùûîôç ]', '', content.lower())
        trans_clean = re.sub(r'[^a-zA-Z0-9äöüÄÖÜßéèêàâùûîôç ]', '', translation.lower())

        if orig_clean == trans_clean or len(trans_clean) < len(orig_clean) * 0.45:
            # Vermutlich nur Kopie oder zu kurz → überspringen
            return

        await message.reply(f"{flag} {translation}", mention_author=False)

    except Exception as e:
        print(f"Übersetzungsfehler: {type(e).__name__} - {str(e)}")


# ────────────────────────────────────────────────
# START
# ────────────────────────────────────────────────

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True, name="Flask-KeepAlive").start()

    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("DISCORD_TOKEN fehlt!")
        exit(1)

    bot.run(token)
