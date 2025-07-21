import discord
from discord.ext import commands
from discord import app_commands
from utils.db_manager import DBManager # Certifique-se de que a importação está correta

class Finance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()

    @app_commands.command(name="add_gasto", description="Adiciona um novo gasto.")
    @app_commands.describe(valor="Valor do gasto", categoria="Categoria do gasto", descricao="Descrição do gasto (opcional)")
    async def add_gasto(self, interaction: discord.Interaction, valor: float, categoria: str, descricao: str = None):
        await interaction.response.defer()
        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User
        
        # Opcional: Verificar se a categoria existe ou criar
        # Passa o objeto user_obj para add_category
        success, msg = self.db.add_category(user_obj, categoria) 
        if not success and "já existe" not in msg:
            await interaction.followup.send(f"Erro na categoria: {msg}")
            return

        # Passa o objeto user_obj para add_transaction
        transaction = self.db.add_transaction(user_obj, 'gasto', valor, category=categoria.lower(), description=descricao)
        if transaction:
            await interaction.followup.send(f"Gasto de R$ {valor:,.2f} em '{categoria}' registrado com sucesso!")
        else:
            await interaction.followup.send("Erro ao registrar o gasto.")

    @app_commands.command(name="add_renda", description="Adiciona uma nova renda.")
    @app_commands.describe(valor="Valor da renda", fonte="Fonte da renda", descricao="Descrição da renda (opcional)")
    async def add_renda(self, interaction: discord.Interaction, valor: float, fonte: str, descricao: str = None):
        await interaction.response.defer()
        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User
        
        # Passa o objeto user_obj para add_transaction
        transaction = self.db.add_transaction(user_obj, 'renda', valor, source=fonte, description=descricao)
        if transaction:
            await interaction.followup.send(f"Renda de R$ {valor:,.2f} de '{fonte}' registrada com sucesso!")
        else:
            await interaction.followup.send("Erro ao registrar a renda.")
    
    @app_commands.command(name="add_categoria", description="Adiciona uma nova categoria de gasto.")
    @app_commands.describe(nome="Nome da nova categoria")
    async def add_category_cmd(self, interaction: discord.Interaction, nome: str):
        await interaction.response.defer()
        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User
        success, message = self.db.add_category(user_obj, nome) # Passa o objeto user_obj
        await interaction.followup.send(message)

    @app_commands.command(name="ver_categorias", description="Lista suas categorias de gasto existentes.")
    async def view_categories(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User
        categories = self.db.get_categories(user_obj) # Passa o objeto user_obj
        
        if not categories:
            await interaction.followup.send("Você não tem nenhuma categoria registrada ainda.")
            return

        category_list = "\n".join([f"- {cat.name.capitalize()}" for cat in categories])
        embed = discord.Embed(
            title="Suas Categorias de Gasto",
            description=category_list,
            color=discord.Color.purple()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="del_categoria", description="Deleta uma categoria de gasto existente.")
    @app_commands.describe(nome="Nome da categoria a ser deletada")
    async def delete_category_cmd(self, interaction: discord.Interaction, nome: str):
        await interaction.response.defer()
        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User
        success, message = self.db.delete_category(user_obj, nome) # Passa o objeto user_obj
        await interaction.followup.send(message)

async def setup(bot):
    await bot.add_cog(Finance(bot))