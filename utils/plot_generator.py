import matplotlib.pyplot as plt
import io
import matplotlib.ticker as mtick

class PlotGenerator:
    def __init__(self):
        plt.style.use('seaborn-v0_8-darkgrid') # Estilo mais agradável

    def generate_pie_chart(self, data: dict, title: str):
        """
        Gera um gráfico de pizza a partir de um dicionário de dados.
        Args:
            data (dict): Dicionário com {categoria: valor}.
            title (str): Título do gráfico.
        Returns:
            io.BytesIO: Objeto BytesIO contendo a imagem do gráfico.
        """
        labels = data.keys()
        sizes = data.values()

        # Cores customizadas (opcional, mas melhora a visual)
        colors = plt.cm.Paired(range(len(labels)))

        fig1, ax1 = plt.subplots(figsize=(8, 8)) # Aumenta o tamanho para melhor visualização
        wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                                           startangle=90, colors=colors,
                                           pctdistance=0.85, textprops=dict(color="w"))

        # Estilizar o texto de porcentagem
        for autotext in autotexts:
            autotext.set_color('black') # Cor do texto da porcentagem
            autotext.set_fontsize(12)
        for text in texts:
            text.set_color('black') # Cor do texto do label
            text.set_fontsize(12)

        ax1.axis('equal')  # Garante que o gráfico de pizza seja desenhado como um círculo.
        ax1.set_title(title, fontsize=16, pad=20) # Aumenta o título e adiciona padding

        # Salva o gráfico em um buffer de memória
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150) # Aumenta DPI para melhor qualidade
        plt.close(fig1) # Fecha a figura para liberar memória
        buffer.seek(0)
        return buffer

    def generate_bar_chart_comparison(self, data: dict, title: str, ylabel: str):
        """
        Gera um gráfico de barras para comparação mensal.
        Args:
            data (dict): Dicionário com {mês/ano: valor}.
            title (str): Título do gráfico.
            ylabel (str): Rótulo do eixo Y.
        Returns:
            io.BytesIO: Objeto BytesIO contendo a imagem do gráfico.
        """
        months = list(data.keys())
        values = list(data.values())

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(months, values, color='skyblue')

        ax.set_title(title, fontsize=16)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_xlabel('Período', fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('R$%.2f')) # Formato monetário

        # Adicionar valores nas barras
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval + 0.05, f'R${yval:,.2f}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout() # Ajusta o layout para evitar sobreposição
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        plt.close(fig)
        buffer.seek(0)
        return buffer