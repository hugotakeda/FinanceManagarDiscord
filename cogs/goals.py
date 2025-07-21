import discord
from discord.ext import commands
from discord import app_commands
from utils.db_manager import DBManager # Certifique-se de que a importação está correta
from datetime import datetime

class Goals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()

    @app_commands.command(name="criar_meta", description="Cria uma nova meta financeira.")
    @app_commands.describe(nome="Nome da meta", valor_alvo="Valor total que você deseja alcançar", data_limite="Data limite (DD/MM/AAAA, opcional)")
    async def create_goal(self, interaction: discord.Interaction, nome: str, valor_alvo: float, data_limite: str = None):
        await interaction.response.defer()
        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User
        
        parsed_date = None
        if data_limite:
            try:
                parsed_date = datetime.strptime(data_limite, '%d/%m/%Y')
            except ValueError:
                await interaction.followup.send("Formato de data inválido. Use DD/MM/AAAA.")
                return

        goal, message = self.db.create_goal(user_obj, nome, valor_alvo, parsed_date) # Passa o objeto user_obj
        if goal:
            await interaction.followup.send(f"Meta '{nome}' de R$ {valor_alvo:,.2f} criada com sucesso!")
        else:
            await interaction.followup.send(f"Erro ao criar meta: {message}")


    @app_commands.command(name="contribuir_meta", description="Adiciona valor a uma meta existente.")
    @app_commands.describe(id_meta="ID da meta", valor="Valor a adicionar")
    async def contribute_goal(self, interaction: discord.Interaction, id_meta: int, valor: float):
        await interaction.response.defer()
        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User
        
        success, message = self.db.contribute_to_goal(user_obj, id_meta, valor) # Passa o objeto user_obj
        if success:
            await interaction.followup.send(message)
        else:
            await interaction.followup.send(f"Erro: {message}")

    @app_commands.command(name="concluir_meta", description="Marca uma meta como 100% concluída.")
    @app_commands.describe(id_meta="ID da meta a ser concluída")
    async def complete_goal(self, interaction: discord.Interaction, id_meta: int):
        await interaction.response.defer()
        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User

        success, message = self.db.complete_goal(user_obj, id_meta) # Passa o objeto user_obj
        if success:
            await interaction.followup.send(message)
        else:
            await interaction.followup.send(f"Erro: {message}")

    @app_commands.command(name="deletar_meta", description="Deleta uma meta existente.")
    @app_commands.describe(id_meta="ID da meta a ser deletada")
    async def delete_goal(self, interaction: discord.Interaction, id_meta: int):
        await interaction.response.defer()
        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User

        success, message = self.db.delete_goal(user_obj, id_meta) # Passa o objeto user_obj
        if success:
            await interaction.followup.send(message)
        else:
            await interaction.followup.send(f"Erro: {message}")

async def setup(bot):
    await bot.add_cog(Goals(bot))