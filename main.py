import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração do Intents para o bot
intents = discord.Intents.default()
intents.message_content = True # Permite que o bot leia o conteúdo das mensagens
intents.members = True # Necessário para alguns recursos, como obter membros do servidor

# Inicialização do bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Lista de cogs para carregar
initial_extensions = [
    "cogs.finance",
    "cogs.goals",
    "cogs.reports",
    "cogs.help",
    "cogs.admin" # <-- Adicione esta linha
]

@bot.event
async def on_ready():
    print(f"Bot {bot.user.name}#{bot.user.discriminator} está online e pronto!")
    print("Tentando carregar cogs...")
    for extension in initial_extensions:
        try:
            await bot.load_extension(extension)
            print(f"Cog {extension} carregado com sucesso.")
        except Exception as e:
            print(f"Falha ao carregar o cog {extension}: {type(e).__name__}: {e}")
    print("Cogs carregados (ou tentativa concluída).")

    # Sincroniza os comandos de barra com o Discord
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizados {len(synced)} comandos de barra.")
    except Exception as e:
        print(f"Falha ao sincronizar comandos de barra: {e}")

# Obtém o token do Discord das variáveis de ambiente
discord_token = os.getenv("DISCORD_TOKEN")

if discord_token:
    print("Token do Discord carregado: SIM")
    bot.run(discord_token)
else:
    print("Token do Discord não encontrado. Certifique-se de que DISCORD_TOKEN está configurado no arquivo .env")