import discord
from discord.ext import commands
from discord import app_commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="apagar", description="Deleta um número específico de mensagens no canal.")
    @app_commands.describe(quantidade="Número de mensagens a serem deletadas (máx. 100)")
    @commands.has_permissions(manage_messages=True) # Requer permissão de "Gerenciar Mensagens"
    async def apagar(self, interaction: discord.Interaction, quantidade: int):
        await interaction.response.defer(ephemeral=True) # Resposta efêmera para o usuário que chamou

        if quantidade <= 0:
            await interaction.followup.send("Por favor, forneça um número positivo de mensagens para apagar.")
            return
        
        if quantidade > 100:
            await interaction.followup.send("Não posso apagar mais de 100 mensagens por vez devido a limitações do Discord.")
            return

        try:
            # Apaga as mensagens
            deleted = await interaction.channel.purge(limit=quantidade)
            await interaction.followup.send(f"Foram apagadas **{len(deleted)}** mensagens neste canal.")
        except discord.Forbidden:
            await interaction.followup.send("Eu não tenho permissão para apagar mensagens neste canal. Por favor, conceda a permissão 'Gerenciar Mensagens' para mim.")
        except discord.HTTPException as e:
            await interaction.followup.send(f"Ocorreu um erro ao apagar mensagens: {e}")

async def setup(bot):
    await bot.add_cog(Admin(bot))