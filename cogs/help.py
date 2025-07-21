import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ajuda", description="Exibe todos os comandos do bot.")
    async def ajuda(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False) # Visível para todos

        embed = discord.Embed(
            title="Guia de Comandos do Bot Financeiro 📈",
            description="Aqui estão todos os comandos que você pode usar para gerenciar suas finanças e o servidor. Use `/` no Discord para ver a lista de comandos e clique para usar um comando.",
            color=discord.Color.blue()
        )

        # Usando crases para formatar os comandos como código inline
        # Finance
        finance_commands = (
            "`/add_gasto <valor> <categoria> [descricao]` - Registra um novo gasto.",
            "`/add_renda <valor> <fonte> [descricao]` - Registra uma nova renda.",
            "`/add_categoria <nome>` - Adiciona uma nova categoria de gasto.",
            "`/ver_categorias` - Lista todas as suas categorias de gasto.",
            "`/del_categoria <nome>` - Deleta uma categoria de gasto e suas transações associadas."
        )
        embed.add_field(name="💰 Gerenciamento Financeiro", value="\n".join(finance_commands), inline=False)

        # Goals
        goals_commands = (
            "`/criar_meta <nome> <valor_alvo> [data_limite]` - Cria uma nova meta financeira.",
            "`/contribuir_meta <id_meta> <valor>` - Adiciona um valor a uma meta existente.",
            "`/concluir_meta <id_meta>` - Marca uma meta como concluída.",
            "`/deletar_meta <id_meta>` - Deleta uma meta existente."
        )
        embed.add_field(name="🎯 Metas Financeiras", value="\n".join(goals_commands), inline=False)

        # Reports
        reports_commands = (
            "`/resumo_mensal [mes] [ano]` - Exibe um resumo financeiro do mês (e um gráfico de gastos).",
            "`/ver_metas` - Lista todas as suas metas financeiras e progresso.",
            "`/exportar_pdf [mes] [ano]` - Gera um relatório financeiro detalhado em PDF."
        )
        embed.add_field(name="📊 Relatórios e Análises", value="\n".join(reports_commands), inline=False)
        
        # Admin (novo cog)
        admin_commands = (
            "`/apagar <quantidade>` - Deleta um número específico de mensagens no canal (máx. 100).",
        )
        embed.add_field(name="🛠️ Administração", value="\n".join(admin_commands), inline=False)

        embed.set_footer(text="Sinta-se à vontade para explorar e gerenciar suas finanças!")
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else discord.Embed.Empty)

        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Help(bot))