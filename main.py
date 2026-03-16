import os
import sqlite3
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

DB_PATH = "bot.db"

PROFESSIONS = [
    "Alchemy",
    "Blacksmithing",
    "Enchanting",
    "Engineering",
    "Herbalism",
    "Jewelcrafting",
    "Leatherworking",
    "Mining",
    "Skinning",
    "Tailoring",
]

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS professions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        user_name TEXT NOT NULL,
        character TEXT NOT NULL,
        profession TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def add_profession(user_id: str, user_name: str, character: str, profession: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO professions (user_id, user_name, character, profession)
    VALUES (?, ?, ?, ?)
    """, (user_id, user_name, character, profession))
    conn.commit()
    conn.close()

def get_crafters_by_profession(profession: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    SELECT user_id, user_name, character
    FROM professions
    WHERE profession = ?
    ORDER BY character ASC
    """, (profession,))
    rows = cur.fetchall()
    conn.close()
    return rows

class CharacterModal(discord.ui.Modal, title="Cadastrar profissão"):
    character = discord.ui.TextInput(
        label="Nome do personagem",
        placeholder="Ex: Melnun",
        max_length=30
    )

    def __init__(self, profession: str):
        super().__init__()
        self.profession = profession

    async def on_submit(self, interaction: discord.Interaction):
        add_profession(
            user_id=str(interaction.user.id),
            user_name=str(interaction.user),
            character=str(self.character.value),
            profession=self.profession
        )

        await interaction.response.send_message(
            f"✅ Profissão cadastrada com sucesso.\n"
            f"**Personagem:** {self.character.value}\n"
            f"**Profissão:** {self.profession}",
            ephemeral=True
        )

class RegisterProfessionSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=p, value=p) for p in PROFESSIONS]
        super().__init__(
            placeholder="Escolha a profissão para cadastrar",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_modal(CharacterModal(self.values[0]))

class RegisterProfessionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(RegisterProfessionSelect())

class SearchProfessionSelect(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=p, value=p) for p in PROFESSIONS]
        super().__init__(
            placeholder="Escolha a profissão para buscar",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        profession = self.values[0]
        rows = get_crafters_by_profession(profession)

        if not rows:
            await interaction.response.send_message(
                f"❌ Nenhum crafter cadastrado em **{profession}**.",
                ephemeral=True
            )
            return

        linhas = [f"**{character}** — <@{user_id}>" for user_id, user_name, character in rows]

        await interaction.response.send_message(
            f"## Crafters de {profession}\n" + "\n".join(linhas),
            ephemeral=False
        )

class SearchProfessionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)
        self.add_item(SearchProfessionSelect())

@bot.tree.command(name="profissao_cadastrar", description="Abrir menu para cadastrar profissão")
async def profissao_cadastrar(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Escolha a profissão que deseja cadastrar:",
        view=RegisterProfessionView(),
        ephemeral=True
    )

@bot.tree.command(name="profissao_buscar", description="Abrir menu para procurar crafters")
async def profissao_buscar(interaction: discord.Interaction):
    await interaction.response.send_message(
        "Escolha a profissão que deseja procurar:",
        view=SearchProfessionView(),
        ephemeral=True
    )

@bot.event
async def on_ready():
    init_db()
    try:
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        print(f"✅ Bot online como {bot.user}")
        print("✅ Comandos globais antigos removidos e novos sincronizados")
    except Exception as e:
        print(f"❌ Erro ao sincronizar comandos: {e}")

bot.run(TOKEN)