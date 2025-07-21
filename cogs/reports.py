import discord
from discord.ext import commands
from discord import app_commands, File
from utils.db_manager import DBManager # <-- Apenas DBManager é importado agora
from utils.plot_generator import PlotGenerator
from datetime import datetime
import calendar
import io

# --- Importações para ReportLab ---
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle 
from reportlab.lib.utils import ImageReader 
# --- Fim das Importações para ReportLab ---

class Reports(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DBManager()
        self.plot_gen = PlotGenerator()
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Justify', alignment=1))

    @app_commands.command(name="resumo_mensal", description="Exibe um resumo financeiro do mês.")
    @app_commands.describe(mes="Mês (ex: 7 para Julho)", ano="Ano (ex: 2024)")
    async def monthly_summary(self, interaction: discord.Interaction, mes: int = None, ano: int = None):
        await interaction.response.defer()

        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User
        
        current_date = datetime.now()
        if mes is None:
            mes = current_date.month
        if ano is None:
            ano = current_date.year

        transactions = self.db.get_transactions_by_month(user_obj, ano, mes) # Passa o objeto user_obj

        total_gastos = sum(t.value for t in transactions if t.type == 'gasto')
        total_renda = sum(t.value for t in transactions if t.type == 'renda')
        saldo = total_renda - total_gastos

        gastos_por_categoria = {}
        for t in transactions:
            if t.type == 'gasto':
                gastos_por_categoria[t.category] = gastos_por_categoria.get(t.category, 0) + t.value
        
        chart_file = None
        if gastos_por_categoria:
            chart_buffer = self.plot_gen.generate_pie_chart(gastos_por_categoria, f"Distribuição de Gastos - {calendar.month_name[mes].capitalize()}/{ano}")
            chart_file = File(chart_buffer, filename="gastos_por_categoria.png")

        goals = self.db.get_goals(user_obj) # Passa o objeto user_obj
        goals_summary = []
        for goal in goals:
            progress = (goal.current_value / goal.target_value) * 100 if goal.target_value > 0 else 0
            status = "Concluída ✅" if progress >= 100 else f"{progress:.1f}% concluído"
            goals_summary.append(f"- {goal.name}: {status}")
        
        goals_text = "\n".join(goals_summary) if goals_summary else "Nenhuma meta registrada."

        embed = discord.Embed(
            title=f"Resumo Financeiro - {calendar.month_name[mes].capitalize()}/{ano}",
            description=f"Confira suas finanças para este período.",
            color=discord.Color.teal()
        )
        embed.add_field(name="Renda Total", value=f"R$ {total_renda:,.2f}", inline=True)
        embed.add_field(name="Gastos Totais", value=f"R$ {total_gastos:,.2f}", inline=True)
        embed.add_field(name="Saldo", value=f"R$ {saldo:,.2f}", inline=True)
        
        gastos_detalhe_str = ""
        if gastos_por_categoria:
            for cat, val in gastos_por_categoria.items():
                gastos_detalhe_str += f"- {cat.capitalize()}: R$ {val:,.2f}\n"
        else:
            gastos_detalhe_str = "Nenhum gasto registrado nesta categoria."
        embed.add_field(name="Gastos por Categoria", value=gastos_detalhe_str, inline=False)
        
        embed.add_field(name="Progresso de Metas", value=goals_text, inline=False)

        embed.set_footer(text="Dados fornecidos pelo seu bot financeiro.")

        if chart_file:
            await interaction.followup.send(embed=embed, file=chart_file)
        else:
            await interaction.followup.send(embed=embed)


    @app_commands.command(name="ver_metas", description="Visualiza suas metas financeiras.")
    async def view_goals(self, interaction: discord.Interaction):
        await interaction.response.defer()
        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User
        goals = self.db.get_goals(user_obj) # Passa o objeto user_obj

        if not goals:
            await interaction.followup.send("Você não tem nenhuma meta registrada ainda.")
            return

        embed = discord.Embed(
            title="Suas Metas Financeiras",
            color=discord.Color.blue()
        )

        for goal in goals:
            progress = (goal.current_value / goal.target_value) * 100 if goal.target_value > 0 else 0
            status = "Concluída ✅" if progress >= 100 else f"{progress:.1f}%"
            
            due_date_str = goal.due_date.strftime('%d/%m/%Y') if goal.due_date else "Não definida"

            embed.add_field(
                name=f"{goal.name} (ID: {goal.id})",
                value=(
                    f"Valor Alvo: R$ {goal.target_value:,.2f}\n"
                    f"Valor Atual: R$ {goal.current_value:,.2f}\n"
                    f"Progresso: {status}\n"
                    f"Prazo: {due_date_str}"
                ),
                inline=False
            )
        
        embed.set_footer(text="Use /contribuir_meta para adicionar valor, /concluir_meta para marcar como concluída, ou /deletar_meta para remover.")
        await interaction.followup.send(embed=embed)


    @app_commands.command(name="exportar_pdf", description="Gera um relatório financeiro em PDF.")
    @app_commands.describe(mes="Mês (ex: 7 para Julho)", ano="Ano (ex: 2024)")
    async def export_pdf(self, interaction: discord.Interaction, mes: int = None, ano: int = None):
        await interaction.response.defer()

        user_obj = self.db.get_or_create_user(str(interaction.user.id)) # Agora retorna o objeto User
        
        current_date = datetime.now()
        if mes is None:
            mes = current_date.month
        if ano is None:
            ano = current_date.year

        transactions = self.db.get_transactions_by_month(user_obj, ano, mes) # Passa o objeto user_obj
        goals = self.db.get_goals(user_obj) # Passa o objeto user_obj

        # --- Cálculos para o Resumo ---
        total_gastos = sum(t.value for t in transactions if t.type == 'gasto')
        total_renda = sum(t.value for t in transactions if t.type == 'renda')
        saldo = total_renda - total_gastos

        gastos_por_categoria = {}
        for t in transactions:
            if t.type == 'gasto':
                gastos_por_categoria[t.category] = gastos_por_categoria.get(t.category, 0) + t.value
        
        goals_summary = []
        for goal in goals:
            progress = (goal.current_value / goal.target_value) * 100 if goal.target_value > 0 else 0
            status = "Concluída ✅" if progress >= 100 else f"{progress:.1f}%"
            goals_summary.append(f"- {goal.name}: {status} (R$ {goal.current_value:,.2f} / R$ {goal.target_value:,.2f})")
        # --- Fim dos Cálculos ---

        # --- Geração do PDF com ReportLab ---
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter # Largura e altura da página
        
        # Estilos para o PDF
        styles = getSampleStyleSheet()
        style_normal = styles['Normal']
        style_heading1 = styles['h1']
        style_heading2 = styles['h2']
        style_body = styles['BodyText']

        y_position = height - inch # Posição inicial

        # Título do Relatório
        c.setFont("Helvetica-Bold", 18)
        c.drawString(inch, y_position, f"Relatório Financeiro - {calendar.month_name[mes].capitalize()}/{ano}")
        y_position -= 0.5 * inch

        # Resumo Financeiro
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y_position, "Resumo Financeiro")
        y_position -= 0.25 * inch

        c.setFont("Helvetica", 12)
        c.drawString(inch, y_position, f"Renda Total: R$ {total_renda:,.2f}")
        y_position -= 0.2 * inch
        c.drawString(inch, y_position, f"Gastos Totais: R$ {total_gastos:,.2f}")
        y_position -= 0.2 * inch
        c.drawString(inch, y_position, f"Saldo: R$ {saldo:,.2f}")
        y_position -= 0.4 * inch # Espaço extra

        # Gastos por Categoria (Texto)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y_position, "Gastos por Categoria")
        y_position -= 0.25 * inch

        if gastos_por_categoria:
            c.setFont("Helvetica", 12)
            for cat, val in gastos_por_categoria.items():
                line = f"- {cat.capitalize()}: R$ {val:,.2f}"
                c.drawString(inch + 0.2 * inch, y_position, line) # Indentação
                y_position -= 0.2 * inch
                if y_position < inch: # Nova página se necessário
                    c.showPage()
                    y_position = height - inch
                    c.setFont("Helvetica", 12) # Resetar fonte na nova página
        else:
            c.setFont("Helvetica", 12)
            c.drawString(inch, y_position, "Nenhum gasto registrado nesta categoria.")
        y_position -= 0.4 * inch # Espaço extra
        
        # --- Adicionar o gráfico de pizza ---
        if gastos_por_categoria:
            chart_buffer = self.plot_gen.generate_pie_chart(gastos_por_categoria, f"Distribuição de Gastos - {calendar.month_name[mes].capitalize()}/{ano}")
            
            img_reader = ImageReader(chart_buffer)
            
            chart_width = 300 
            chart_height = 300 
            
            if y_position < (inch + chart_height + 0.5 * inch): 
                c.showPage()
                y_position = height - inch
            
            y_position -= chart_height + 0.25 * inch 

            c.drawImage(
                img_reader, 
                inch, 
                y_position, 
                width=chart_width, 
                height=chart_height, 
                preserveAspectRatio=True 
            )
            y_position -= 0.4 * inch 
        else:
            c.setFont("Helvetica", 12)
            c.drawString(inch, y_position, "Gráfico de gastos não gerado por falta de dados.")
            y_position -= 0.4 * inch

        # Progresso de Metas
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y_position, "Progresso de Metas")
        y_position -= 0.25 * inch

        if goals_summary:
            c.setFont("Helvetica", 12)
            for goal_line in goals_summary:
                c.drawString(inch + 0.2 * inch, y_position, goal_line) # Indentação
                y_position -= 0.2 * inch
                if y_position < inch: # Nova página se necessário
                    c.showPage()
                    y_position = height - inch
                    c.setFont("Helvetica", 12) # Resetar fonte na nova página
        else:
            c.setFont("Helvetica", 12)
            c.drawString(inch, y_position, "Nenhuma meta registrada.") 
        y_position -= 0.4 * inch # Espaço extra

        # --- Tabela de Transações Detalhadas ---
        c.setFont("Helvetica-Bold", 14)
        c.drawString(inch, y_position, "Detalhes das Transações")
        y_position -= 0.25 * inch

        # Preparar dados para a tabela
        data = [["Data", "Tipo", "Valor", "Categoria/Fonte", "Descrição"]] # Cabeçalho da tabela
        
        if transactions:
            for t in transactions:
                type_label = "Gasto" if t.type == 'gasto' else "Renda"
                category_or_source = t.category if t.type == 'gasto' else t.source if t.source else "N/A"
                description_text = t.description if t.description else ""
                
                data.append([
                    t.date.strftime('%d/%m/%Y'),
                    type_label,
                    f"R$ {t.value:,.2f}",
                    category_or_source.capitalize(),
                    description_text
                ])
        else:
            data.append(["", "", "Nenhuma transação detalhada neste período.", "", ""])

        # Definir o estilo da tabela
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey), # Cabeçalho cinza
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'), 
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5DC')), # Cor primária
            ('BACKGROUND', (0, 2), (-1, -1), colors.HexColor('#F8F8F8')), # Cor secundária
            ('GRID', (0, 0), (-1, -1), 1, colors.black), # Bordas da grade
            ('BOX', (0, 0), (-1, -1), 1, colors.black), # Borda externa
        ])

        # Criar a tabela
        col_widths = [0.8*inch, 0.8*inch, 1.0*inch, 1.2*inch, 2.7*inch] 
        table = Table(data, colWidths=col_widths) 
        table.setStyle(table_style)

        # Calcular a altura da tabela para verificar se cabe na página
        table_width, table_height = table.wrapOn(c, width - 2 * inch, height) 

        # Se não houver espaço suficiente para a tabela, adicione uma nova página
        if y_position < (inch + table_height + 0.25 * inch): 
            c.showPage()
            y_position = height - inch
            c.setFont("Helvetica-Bold", 14)
            c.drawString(inch, y_position, "Detalhes das Transações (Continuação)")
            y_position -= 0.25 * inch

        # Desenhar a tabela
        table.drawOn(c, inch, y_position - table_height) 
        y_position -= table_height + 0.4 * inch 

        # Finaliza o PDF
        c.save()
        buffer.seek(0)
        
        await interaction.followup.send(content="Seu relatório PDF foi gerado!", file=File(buffer, filename=f"relatorio_financeiro_{ano}_{mes}.pdf"))
        

async def setup(bot):
    await bot.add_cog(Reports(bot))