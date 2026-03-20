# ════════════════════════════════════════════════
#  Bild-Übersetzer Cog  •  VHA Alliance
#  Liest Text aus Bildern und übersetzt ihn
#  Befehl: !übersetze (als Reply auf ein Bild)
#  Französisch: !traduire
# ════════════════════════════════════════════════

import discord
from discord.ext import commands
import aiohttp
import base64

# Llama 4 Scout unterstützt Vision (Bilder lesen)
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


# ────────────────────────────────────────────────
# Hilfsfunktionen
# ────────────────────────────────────────────────

async def image_to_base64(url: str) -> tuple[str, str]:
    """Lädt ein Bild herunter und konvertiert es zu Base64."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return None, None
            data = await resp.read()
            content_type = resp.content_type or "image/png"
            b64 = base64.b64encode(data).decode("utf-8")
            return b64, content_type


async def extract_and_translate(groq_client, image_b64: str, content_type: str) -> dict:
    """
    Liest Text aus dem Bild und übersetzt ihn in einem Call.
    Gibt dict mit 'original', 'de', 'fr', 'lang' zurück.
    """
    resp = groq_client.chat.completions.create(
        model=VISION_MODEL,
        temperature=0.1,
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{content_type};base64,{image_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": (
                            "1. Read ALL text visible in this image exactly as written.\n"
                            "2. Detect the language of that text.\n"
                            "3. Translate the text into German AND French.\n\n"
                            "Reply in this exact format (no extra text):\n"
                            "ORIGINAL: [exact text from image]\n"
                            "LANG: [language code e.g. EN, DE, FR, JA]\n"
                            "DE: [German translation]\n"
                            "FR: [French translation]\n\n"
                            "If the text is already German, write the original for DE and only translate to FR.\n"
                            "If the text is already French, write the original for FR and only translate to DE.\n"
                            "If there is no text in the image, reply with: NOTEXT"
                        )
                    }
                ]
            }
        ]
    )

    result = resp.choices[0].message.content.strip()

    if "NOTEXT" in result.upper():
        return None

    parsed = {"original": "", "lang": "", "de": "", "fr": ""}
    for line in result.split("\n"):
        if line.startswith("ORIGINAL:"):
            parsed["original"] = line.replace("ORIGINAL:", "").strip()
        elif line.startswith("LANG:"):
            parsed["lang"] = line.replace("LANG:", "").strip()
        elif line.startswith("DE:"):
            parsed["de"] = line.replace("DE:", "").strip()
        elif line.startswith("FR:"):
            parsed["fr"] = line.replace("FR:", "").strip()

    return parsed if any(parsed.values()) else None


# ────────────────────────────────────────────────
# Cog
# ────────────────────────────────────────────────

class BildUebersetzerCog(commands.Cog):
    def __init__(self, bot, groq_client):
        self.bot = bot
        self.groq_client = groq_client

    @commands.command(name="übersetze", aliases=["uebersetze", "traduire", "translate_image", "ocr", "lese", "lire"])
    async def uebersetze_bild(self, ctx):
        """
        Liest Text aus einem Bild und übersetzt ihn.
        Nutzung: Als Reply auf eine Nachricht mit Bild tippen: !übersetze
        Français: !traduire (en réponse à un message avec image)
        """

        # Bild suchen — entweder in der Nachricht selbst oder in der Reply-Nachricht
        target_message = ctx.message
        image_url = None

        # Zuerst in der aktuellen Nachricht schauen
        if ctx.message.attachments:
            for att in ctx.message.attachments:
                if att.content_type and att.content_type.startswith("image"):
                    image_url = att.url
                    break

        # Dann in der Reply-Nachricht schauen
        if not image_url and ctx.message.reference:
            ref = ctx.message.reference.resolved
            if isinstance(ref, discord.Message) and ref.attachments:
                for att in ref.attachments:
                    if att.content_type and att.content_type.startswith("image"):
                        image_url = att.url
                        target_message = ref
                        break

        if not image_url:
            embed = discord.Embed(
                title="❓ Kein Bild gefunden / Aucune image trouvée",
                description=(
                    "**Nutzung / Utilisation:**\n"
                    "Antworte auf eine Nachricht mit Bild und tippe `!übersetze`\n"
                    "Réponds à un message avec image et tape `!traduire`"
                ),
                color=0xF39C12
            )
            await ctx.send(embed=embed)
            return

        # Lade-Nachricht
        thinking = await ctx.send("🔍 **Lese Bild...** / **Lecture de l'image...**")

        try:
            # Bild herunterladen und zu Base64 konvertieren
            image_b64, content_type = await image_to_base64(image_url)

            if not image_b64:
                await thinking.edit(content="❌ Bild konnte nicht geladen werden. / Impossible de charger l'image.")
                return

            # Text lesen und übersetzen
            result = await extract_and_translate(self.groq_client, image_b64, content_type)

            if not result:
                embed = discord.Embed(
                    title="🖼️ Kein Text gefunden / Aucun texte trouvé",
                    description=(
                        "Im Bild wurde kein Text erkannt.\n"
                        "Aucun texte n'a été détecté dans l'image."
                    ),
                    color=0xF39C12
                )
                await thinking.edit(content=None, embed=embed)
                return

            # Ergebnis als Embed
            lang = result.get("lang", "?")
            embed = discord.Embed(
                title=f"🖼️ Bildübersetzung / Traduction d'image",
                color=0x9B59B6
            )

            # Originaltext
            if result.get("original"):
                embed.add_field(
                    name=f"📝 Original ({lang})",
                    value=result["original"][:1000],
                    inline=False
                )

            # Deutsche Übersetzung (nur wenn nicht schon Deutsch)
            if result.get("de") and lang != "DE":
                embed.add_field(
                    name="🇩🇪 Deutsch",
                    value=result["de"][:1000],
                    inline=False
                )
            elif lang == "DE":
                embed.add_field(
                    name="🇩🇪 Deutsch (Original)",
                    value=result["original"][:1000],
                    inline=False
                )

            # Französische Übersetzung (nur wenn nicht schon Französisch)
            if result.get("fr") and lang != "FR":
                embed.add_field(
                    name="🇫🇷 Français",
                    value=result["fr"][:1000],
                    inline=False
                )
            elif lang == "FR":
                embed.add_field(
                    name="🇫🇷 Français (Original)",
                    value=result["original"][:1000],
                    inline=False
                )

            embed.set_footer(text="VHA Bild-Übersetzer / Traducteur d'images")
            await thinking.edit(content=None, embed=embed)

        except Exception as e:
            print(f"Bildübersetzungs-Fehler: {type(e).__name__} - {str(e)}")
            await thinking.edit(content=f"❌ Fehler beim Verarbeiten des Bildes. / Erreur lors du traitement de l'image.")


# ────────────────────────────────────────────────
# Setup
# ────────────────────────────────────────────────

async def setup(bot, groq_client):
    await bot.add_cog(BildUebersetzerCog(bot, groq_client))
