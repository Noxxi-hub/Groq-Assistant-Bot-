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
# ERWEITERTE SPRACHERKENNUNG (für !ai und ggf. andere Teile)
# ────────────────────────────────────────────────

def detect_language_simple(text: str) -> str | None:
    if not text or len(text.strip()) < 4:
        return None

    t = text.lower()

    # Deutsch
    if any(re.search(rf'\b{w}\b', t) for w in ["ist", "ich", "du", "wir", "und", "der", "die", "das", "nicht", "für", "mit", "auf"]):
        return "DE"

    # Französisch
    if any(re.search(rf'\b{w}\b', t) for w in ["je", "tu", "nous", "vous", "est", "suis", "c'est", "oui", "pas", "le", "la", "les"]):
        return "FR"

    # Englisch
    if any(re.search(rf'\b{w}\b', t) for w in ["the", "is", "you", "i", "and", "to", "in", "of", "it", "that", "this", "what", "how"]):
        return "EN"

    # Spanisch
    if any(re.search(rf'\b{w}\b', t) for w in ["el", "la", "los", "las", "es", "estoy", "yo", "tu", "nosotros", "si", "no", "qué"]):
        return "ES"

    # Italienisch
    if any(re.search(rf'\b{w}\b', t) for w in ["il", "la", "i", "gli", "le", "è", "sono", "io", "tu", "noi", "sì", "no"]):
        return "IT"

    # Portugiesisch
    if any(re.search(rf'\b{w}\b', t) for w in ["o", "a", "os", "as", "é", "estou", "eu", "você", "nós", "sim", "não"]):
        return "PT"

    # Niederländisch
    if any(re.search(rf'\b{w}\b', t) for w in ["de", "het", "een", "ik", "je", "wij", "is", "en", "van", "in", "op"]):
        return "NL"

    # Polnisch
    if any(re.search(rf'\b{w}\b', t) for w in ["jest", "ja", "ty", "my", "i", "w", "na", "do", "nie", "tak", "co"]):
        return "PL"

    # Russisch
    if any(re.search(rf'\b{w}\b', t) for w in ["я", "ты", "мы", "и", "в", "на", "не", "что", "это", "как", "где"]):
        return "RU"

    # Japanisch
    if any(w in t for w in ["です", "ます", "は", "を", "が", "に", "の", "で", "か", "ね", "よ"]):
        return "JA"

    # Koreanisch
    if any(w in t for w in ["이다", "하다", "이", "가", "을", "를", "에", "에서", "요", "네", "아니요"]):
        return "KO"

    # Chinesisch (vereinfacht)
    if any(w in t for w in ["的", "是", "在", "我", "你", "他", "她", "我们", "和", "不", "什么"]):
        return "ZH"

    # Arabisch
    if any(w in t for w in ["في", "من", "على", "إلى", "أنا", "أنت", "هو", "هي", "نحن", "لا", "ما"]):
        return "AR"

    # Hindi
    if any(w in t for w in ["है", "मैं", "तुम", "हम", "और", "में", "से", "के", "को", "नहीं", "क्या"]):
        return "HI"

    # Türkisch
    if any(re.search(rf'\b{w}\b', t) for w in ["ve", "ile", "de", "da", "ben", "sen", "o", "biz", "evet", "hayır", "ne"]):
        return "TR"

    # Schwedisch
    if any(re.search(rf'\b{w}\b', t) for w in ["jag", "du", "vi", "är", "och", "i", "på", "det", "en", "ett"]):
        return "SV"

    # Dänisch / Norwegisch (sehr ähnlich)
    if any(re.search(rf'\b{w}\b', t) for w in ["jeg", "du", "vi", "er", "og", "i", "på", "det", "en", "et"]):
        return "DA/NO"

    # Finnisch
    if any(re.search(rf'\b{w}\b', t) for w in ["minä", "sinä", "me", "on", "ja", "ei", "että", "mutta", "jos", "kun"]):
        return "FI"

    # Tschechisch
    if any(re.search(rf'\b{w}\b', t) for w in ["je", "já", "ty", "my", "a", "v", "na", "do", "ne", "ano"]):
        return "CS"

    return None


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
        name="🇩🇪 Deutsch",
        value=(
            "`!translate on/off`: Automatik an/aus\n"
            "`!ai [Frage]`: KI direkt fragen"
        ),
        inline=False
    )
    embed.add_field(
        name="🇫🇷 Français",
        value=(
            "`!translate on/off`: Activer/Désactiver\n"
            "`!ai [Question]`: Poser une question"
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
            description="❓ Bitte eine Frage eingeben\nBeispiel: `!ai Was ist die VHA Alliance?`",
            color=discord.Color.orange()
        )
        embed.set_author(name="VHA ALLIANCE", icon_url=LOGO_URL)
        await ctx.send(embed=embed)
        return

    thinking = await ctx.send(embed=discord.Embed(
        description="**Denke nach …** 🧠",
        color=discord.Color.blurple()
    ))

    # ─── Sprache erkennen ───────────────────────────────
    lang_code = detect_language_simple(question)

    lang_map = {
        "DE":    ("Deutsch",       "auf Deutsch"),
        "FR":    ("Französisch",   "auf Französisch"),
        "EN":    ("Englisch",      "in English"),
        "ES":    ("Spanisch",      "en español"),
        "IT":    ("Italienisch",   "in italiano"),
        "PT":    ("Portugiesisch", "em português"),
        "NL":    ("Niederländisch","in het Nederlands"),
        "PL":    ("Polnisch",      "po polsku"),
        "RU":    ("Russisch",      "на русском языке"),
        "JA":    ("Japanisch",     "日本語で"),
        "KO":    ("Koreanisch",    "한국어로"),
        "ZH":    ("Chinesisch",    "用中文"),
        "AR":    ("Arabisch",      "بالعربية"),
        "HI":    ("Hindi",         "हिन्दी में"),
        "TR":    ("Türkisch",      "Türkçe"),
        "SV":    ("Schwedisch",    "på svenska"),
        "DA/NO": ("Skandinavisch", "på skandinavisk"),
        "FI":    ("Finnisch",      "suomeksi"),
        "CS":    ("Tschechisch",   "česky"),
    }

    if lang_code in lang_map:
        display_name, prompt_lang = lang_map[lang_code]
    else:
        display_name = "Deutsch (Fallback)"
        prompt_lang = "auf Deutsch"

    system_content = (
        f"Du bist ein hilfreicher, präziser und freundlicher Assistent der VHA Alliance. "
        f"Antworte klar, natürlich und **{prompt_lang}**."
    )

    try:
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        completion = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.75,
            max_tokens=1400,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user",   "content": question}
            ]
        )

        answer = completion.choices[0].message.content.strip()
        color = discord.Color.from_rgb(88, 101, 242)

    except Exception as e:
        answer = f"Fehler bei der KI-Anfrage:\n{type(e).__name__}: {str(e)}"
        color = discord.Color.red()

    embed = discord.Embed(
        title="VHA KI • Antwort",
        description=answer[:4000],
        color=color
    )
    embed.set_author(name="VHA ALLIANCE", icon_url=LOGO_URL)
    embed.set_thumbnail(url=LOGO_URL)
    embed.add_field(name="Deine Frage", value=f"→ {question[:1000]}", inline=False)
    embed.set_footer(
        text=f"VHA • Groq • {GROQ_MODEL} • Antwort auf {display_name}",
        icon_url=LOGO_URL
    )

    await thinking.edit(embed=embed)


# ────────────────────────────────────────────────
# AUTOMATISCHE ÜBERSETZUNG + REPLY-SUPPORT
# ────────────────────────────────────────────────

@bot.event
async def on_message(message: discord.Message):
    global processed_messages, translate_active

    if message.author.bot:
        return

    if message.id in processed_messages:
        return

    processed_messages.add(message.id)
    if len(processed_messages) > 250:
        processed_messages.clear()

    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    content = message.content.strip()
    if not translate_active or len(content) < 2:
        return

    lower = content.lower()
    if lower in {"ok", "lol", "xd", "haha", "oui", "ja", "nein", "danke", "merci", "?", "!", "😂", "😅", "gg"}:
        return

    targets = ["DE", "FR"]
    ref_lang = None
    ref_text = ""

    if message.reference and message.reference.message_id:
        try:
            ref_msg = await message.channel.fetch_message(message.reference.message_id)
            ref_text = ref_msg.content.strip()
            if ref_text and len(ref_text) > 3:
                ref_lang = detect_language_simple(ref_text)
                if not ref_lang:
                    ref_lang = "OTHER"
        except:
            pass

    if ref_lang == "OTHER":
        targets.append("ORIGINAL")

    lines = []

    for tgt in targets:
        if tgt == "DE":
            prompt = "Übersetze NUR ins Deutsche. Nur die Übersetzung. Kein Kommentar."
            flag = "🇩🇪"
        elif tgt == "FR":
            prompt = "Übersetze NUR ins Französische. Nur die Übersetzung. Kein Kommentar."
            flag = "🇫🇷"
        else:
            prompt = "Übersetze NUR in die Sprache des Originaltexts. Gib NUR die Übersetzung aus. Kein Kommentar."
            flag = "🌐"

        try:
            groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            completion = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                temperature=0.0,
                max_tokens=900,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": content}
                ]
            )
            tr = completion.choices[0].message.content.strip()
            if tr and tr.lower() != content.lower():
                lines.append(f"{flag} {tr}")
        except Exception as e:
            print(f"Übersetzungsfehler {tgt}: {e.__class__.__name__}")
            continue

    if lines:
        await message.reply("\n".join(lines), mention_author=False)


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
