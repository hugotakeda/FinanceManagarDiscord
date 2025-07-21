# 🤖 Bot Finance Manager

Bem-vindo ao repositório do **Bot Finance Manager**\! Este é um bot para Discord projetado para ajudar você e seus amigos a gerenciarem suas finanças pessoais diretamente dentro do servidor do Discord, de forma simples e intuitiva.

Com o Bot Finança, você pode registrar gastos e rendas, acompanhar seu saldo, definir e monitorar metas financeiras, organizar transações por categorias e gerar relatórios para uma visão clara da sua saúde financeira.

-----

## ✨ Funcionalidades

  * **Registro de Transações:** Adicione facilmente seus **gastos** e **rendas** com categorias/fontes e descrições.
  * **Gerenciamento de Categorias:** Crie, visualize e delete categorias personalizadas para seus gastos.
  * **Metas Financeiras:** Crie metas de economia, contribua para elas e acompanhe seu progresso.
  * **Relatórios Financeiros:**
      * **Resumo Mensal:** Visualize um balanço rápido de suas rendas, gastos e saldo, além de um gráfico de distribuição de gastos por categoria.
      * **Metas:** Veja o status de todas as suas metas financeiras.
      * **Exportar PDF:** Gere um relatório detalhado em PDF com todas as suas transações, resumos e metas.
  * **Moderação:** Um comando simples para apagar mensagens no canal (requer permissões de administrador).
  * **Ajuda Integrada:** Um comando `/ajuda` completo que lista e descreve todas as funcionalidades do bot.

-----

## 🚀 Como Usar o Bot no Discord

Todos os comandos são do tipo **Slash Commands** (`/`). Basta digitar `/` no seu canal do Discord e selecionar o comando desejado. O Discord irá guiá-lo com os parâmetros necessários.

### Exemplos de Comandos:

  * `/add_gasto 50.00 comida "Jantar com amigos"` - Registra um gasto.
  * `/add_renda 1500.00 salario "Salário do mês"` - Registra uma renda.
  * `/criar_meta "Viagem dos Sonhos" 3000.00 31/12/2025` - Cria uma meta.
  * `/contribuir_meta 1 100.00` - Adiciona R$ 100 à meta com ID 1.
  * `/resumo_mensal` - Vê seu resumo financeiro do mês atual.
  * `/exportar_pdf 7 2025` - Gera um PDF do seu relatório de Julho de 2025.
  * `/apagar 5` - Apaga as últimas 5 mensagens no canal (requer permissão).
  * `/ajuda` - Exibe a lista completa de comandos e suas descrições.

-----

## ⚙️ Configuração e Instalação (Para Desenvolvedores/Hosters)

Para rodar seu próprio Bot Finança 2.0, siga os passos abaixo:

### 1\. Pré-requisitos

  * **Python 3.8+** instalado.
  * Um **aplicativo Discord** criado no [Portal do Desenvolvedor](https://discord.com/developers/applications) com um bot associado e os **Intents** necessários ativados (especialmente `Message Content Intent` e `Members Intent`).

### 2\. Clonar o Repositório

Primeiro, clone este repositório para o seu ambiente local:

```bash
git clone https://github.com/SeuUsuario/Bot-Financa-2.0.git # Altere 'SeuUsuario' para o seu username/repo
cd Bot-Financa-2.0
```

### 3\. Criar e Ativar Ambiente Virtual

É altamente recomendável usar um ambiente virtual para gerenciar as dependências:

```bash
python3 -m venv venv
```

  * **No macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```
  * **No Windows (PowerShell):**
    ```powershell
    .\venv\Scripts\Activate.ps1
    ```
  * **No Windows (Command Prompt - CMD):**
    ```cmd
    venv\Scripts\activate.bat
    ```

### 4\. Instalar Dependências

Com o ambiente virtual ativado, instale todas as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

### 5\. Configurar Variáveis de Ambiente (`.env`)

Crie um arquivo chamado `.env` na pasta raiz do projeto (`Bot-Financa-2.0/`) e adicione seu **token do Discord Bot**:

```ini
DISCORD_TOKEN=SEU_TOKEN_DO_BOT_AQUI
# As chaves abaixo são para o dashboard web, não são estritamente necessárias se você não for usá-lo,
# mas podem ser mantidas para compatibilidade ou uso futuro.
DISCORD_CLIENT_ID=SEU_CLIENT_ID_DO_APLICATIVO_AQUI
DISCORD_CLIENT_SECRET=SEU_CLIENT_SECRET_DO_APLICATIVO_AQUI
SECRET_KEY=UMA_CHAVE_SECRETA_ALEATORIA_E_LONGA # Use 'python -c "import os; print(os.urandom(24).hex())"' para gerar
```

Substitua os valores pelos seus tokens e chaves reais.

### 6\. Rodar o Bot

Com o ambiente virtual ativado, execute o script principal:

```bash
python main.py
```

O bot deverá ficar online no seu servidor Discord\!

-----

## ⚠️ Permissões do Bot no Discord

Certifique-se de que seu bot tenha as seguintes permissões no servidor Discord para funcionar corretamente:

  * **Ler Mensagens/Ver Canais**
  * **Enviar Mensagens**
  * **Gerenciar Mensagens** (para o comando `/apagar`)
  * **Anexar Arquivos** (para enviar gráficos e PDFs)

-----

## 🤝 Contribuições

Contribuições são bem-vindas\! Se você tiver ideias para novas funcionalidades, melhorias ou correções de bugs, sinta-se à vontade para abrir uma `issue` ou enviar um `pull request`.

-----

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
