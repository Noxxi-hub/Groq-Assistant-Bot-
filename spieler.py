# ════════════════════════════════════════════════
#  Spieler-Cog  •  VHA Alliance  •  Mecha Fire
#  Spieler-IDs speichern, anzeigen, löschen
#  Erlaubte Rollen: Administrator, R5, R4
# ════════════════════════════════════════════════

import discord
from discord.ext import commands
import json
import os

DATA_FILE = "spieler.json"
ALLOWED_ROLES = {"R5", "R4"}


# ────────────────────────────────────────────────
# Hilfsfunktionen
# ────────────────────────────────────────────────

def load_data() -> list:
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("spieler", [])


def save_data(spieler: list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"spieler": spieler}, f, indent=2, ensure_ascii=False)


def has_permission(member: discord.Member) -> bool:
    if member.guild_permissions.administrator:
        return True
    member_roles = {r.name.upper() for r in member.roles}
    allowed_upper = {r.upper() for r in ALLOWED_ROLES}
    return bool(member_roles & allowed_upper)


# ────────────────────────────────────────────────
# Cog
# ────────────────────────────────────────────────

class SpielerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── !spieler ─────────────────────────────────
    @commands.group(name="spieler", aliases=["joueur", "joueurs", "player", "players", "ids"], invoke_without_command=True)
    async def spieler(self, ctx):
        """Zeigt alle gespeicherten Spieler-IDs an."""
        data = load_data()

        if not data:
            await ctx.send(
                "📭 Keine Spieler gespeichert.\n"
                "Aucun joueur enregistré."
            )
            return

        embed = discord.Embed(
            title="👥 Spieler-IDs • Mecha Fire",
            color=0x2ECC71
        )

        lines = []
        for s in sorted(data, key=lambda x: x["name"].lower()):
            lines.append(f"`{s['name']:<15}` ID: `{s['id']}`")

        chunk = ""
        field_num = 1
        for line in lines:
            if len(chunk) + len(line) + 1 > 1000:
                embed.add_field(
                    name=f"Spieler / Joueurs {field_num}" if field_num > 1 else "Spieler / Joueurs",
                    value=chunk,
                    inline=False
                )
                chunk = line + "\n"
                field_num += 1
            else:
                chunk += line + "\n"

        if chunk:
            embed.add_field(
                name=f"Spieler / Joueurs {field_num}" if field_num > 1 else "Spieler / Joueurs",
                value=chunk,
                inline=False
            )

        embed.set_footer(text=f"Gesamt / Total: {len(data)} • !spieler add/delete")
        await ctx.send(embed=embed)

    # ── !spieler add ──────────────────────────────
    @spieler.command(name="add", aliases=["hinzufügen", "ajouter"])
    async def spieler_add(self, ctx, name: str, spieler_id: str):
        """
        Fügt einen Spieler hinzu.
        Nutzung: !spieler add NAME ID
        Beispiel: !spieler add Noxxi 3881385
        """
        if not has_permission(ctx.author):
            embed = discord.Embed(
                title="❌ Keine Berechtigung / Pas d'autorisation",
                description=(
                    "Nur **Administrator**, **R5** und **R4** dürfen Spieler hinzufügen.\n"
                    "Seuls les **Administrateur**, **R5** et **R4** peuvent ajouter des joueurs."
                ),
                color=0xED4245
            )
            await ctx.send(embed=embed)
            return

        # Nur Zahlen als ID erlauben
        if not spieler_id.isdigit():
            await ctx.send(
                "❌ Die ID muss eine Zahl sein.\n"
                "L'ID doit être un nombre."
            )
            return

        data = load_data()

        # Prüfen ob Name oder ID schon existiert
        for s in data:
            if s["name"].lower() == name.lower():
                await ctx.send(
                    f"⚠️ `{name}` existiert bereits. Zuerst löschen mit `!spieler delete {name}`\n"
                    f"`{name}` existe déjà. Supprime d'abord avec `!spieler delete {name}`"
                )
                return
            if s["id"] == spieler_id:
                await ctx.send(
                    f"⚠️ ID `{spieler_id}` ist bereits **{s['name']}** zugeordnet.\n"
                    f"L'ID `{spieler_id}` est déjà attribuée à **{s['name']}**."
                )
                return

        data.append({"name": name, "id": spieler_id})
        save_data(data)

        embed = discord.Embed(
            title="✅ Spieler hinzugefügt / Joueur ajouté",
            color=0x57F287
        )
        embed.add_field(name="👤 Name", value=name, inline=True)
        embed.add_field(name="🆔 ID", value=spieler_id, inline=True)
        embed.set_footer(text=f"Hinzugefügt von / Ajouté par {ctx.author.display_name}")
        await ctx.send(embed=embed)

    @spieler_add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "❓ Nutzung: `!spieler add NAME ID`\n"
                "Exemple: `!spieler add Noxxi 3881385`"
            )

    # ── !spieler delete ───────────────────────────
    @spieler.command(name="delete", aliases=["löschen", "supprimer", "del", "remove"])
    async def spieler_delete(self, ctx, *, name: str):
        """
        Löscht einen Spieler.
        Nutzung: !spieler delete NAME
        """
        if not has_permission(ctx.author):
            embed = discord.Embed(
                title="❌ Keine Berechtigung / Pas d'autorisation",
                description=(
                    "Nur **Administrator**, **R5** und **R4** dürfen Spieler löschen.\n"
                    "Seuls les **Administrateur**, **R5** et **R4** peuvent supprimer des joueurs."
                ),
                color=0xED4245
            )
            await ctx.send(embed=embed)
            return

        data = load_data()
        original_len = len(data)
        data = [s for s in data if s["name"].lower() != name.lower()]

        if len(data) == original_len:
            await ctx.send(
                f"⚠️ `{name}` wurde nicht gefunden.\n"
                f"`{name}` n'a pas été trouvé."
            )
            return

        save_data(data)

        embed = discord.Embed(
            title="🗑️ Spieler gelöscht / Joueur supprimé",
            description=f"`{name}` wurde entfernt. / `{name}` a été supprimé.",
            color=0xED4245
        )
        embed.set_footer(text=f"Gelöscht von / Supprimé par {ctx.author.display_name}")
        await ctx.send(embed=embed)

    # ── !spieler suche ────────────────────────────
    @spieler.command(name="suche", aliases=["search", "chercher", "find", "id"])
    async def spieler_suche(self, ctx, *, suche: str):
        """
        Sucht einen Spieler nach Name oder ID.
        Nutzung: !spieler suche NAME oder !spieler suche ID
        """
        data = load_data()
        gefunden = [
            s for s in data
            if suche.lower() in s["name"].lower() or suche == s["id"]
        ]

        if not gefunden:
            await ctx.send(
                f"🔍 Kein Spieler mit `{suche}` gefunden.\n"
                f"Aucun joueur trouvé pour `{suche}`."
            )
            return

        embed = discord.Embed(
            title=f"🔍 Suchergebnis / Résultat • {suche}",
            color=0x3498DB
        )
        for s in gefunden:
            embed.add_field(
                name=f"👤 {s['name']}",
                value=f"🆔 `{s['id']}`",
                inline=False
            )
        await ctx.send(embed=embed)

    # ── !spieler help ─────────────────────────────
    @spieler.command(name="help", aliases=["hilfe", "aide"])
    async def spieler_help(self, ctx):
        embed = discord.Embed(
            title="👥 Spieler-IDs – Hilfe / Aide",
            color=0x3498DB
        )
        embed.add_field(
            name="🇩🇪 Befehle",
            value=(
                "`!spieler` – Alle Spieler anzeigen\n"
                "`!spieler add NAME ID` – Hinzufügen\n"
                "`!spieler delete NAME` – Löschen\n"
                "`!spieler suche NAME/ID` – Suchen\n\n"
                "**Beispiel:** `!spieler add Noxxi 3881385`"
            ),
            inline=False
        )
        embed.add_field(
            name="🇫🇷 Commandes",
            value=(
                "`!joueur` – Afficher tous les joueurs\n"
                "`!joueur ajouter NOM ID` – Ajouter\n"
                "`!joueur supprimer NOM` – Supprimer\n"
                "`!joueur chercher NOM/ID` – Rechercher\n\n"
                "**Exemple:** `!joueur ajouter Noxxi 3881385`"
            ),
            inline=False
        )
        embed.add_field(
            name="🔐 Berechtigung / Permission",
            value="Administrator, R5, R4",
            inline=False
        )
        await ctx.send(embed=embed)


# ────────────────────────────────────────────────
# Setup
# ────────────────────────────────────────────────

async def setup(bot):
    await bot.add_cog(SpielerCog(bot))
