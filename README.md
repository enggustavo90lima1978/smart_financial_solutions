
# Agente de Chat Inteligente com LangChain - Smartie

Este projeto apresenta uma **solução de Análise Exploratória de Dados (EDA) baseada em agentes**, permitindo que usuários interajam com seus arquivos CSV/ZIP por meio de um **chatbot inteligente**.

A arquitetura utiliza **LangChain** para orquestração de Agentes especializados, **FastAPI** para o backend de processamento de IA, **React e Js** para o frontend de chat intuitivo e **Plotly/SQLite** para visualização de dados eficiente e com pouco consumo de tokens.

Toda a aplicação é empacotada e executada através do **Docker Compose**, garantindo um *setup* rápido e confiável.

>  ! Projeto em desenvolvimento, README desatualizado e frontend não construído!

## 🚀 Instalação e Inicialização

### **Pré-requisitos**

Para executar este projeto, você só precisa ter o **Docker** e o **Docker Compose** instalados na sua máquina e 3 GB de armazenamento livre. Se ainda não os tem, você pode seguir os links abaixo para a instalação oficial:

  * [**Instalação do Docker no Windows**](https://docs.docker.com/desktop/install/windows-install/)
  * [**Instalação do Docker no Linux**](https://docs.docker.com/engine/install/ubuntu/)

### **Configuração do ambiente**

1.  **Clone o repositório do GitHub:**
    ```bash
    git clone https://github.com/Gabryel-Barboza/rag_chatbot_agent.git
    cd rag_chatbot_agent
    ```
    > Ou baixe o `.zip` clicando no botão **Code <>** acima.

2.  **Configurar variáveis de ambiente:**
    Dentro do diretório raiz do projeto, copie o arquivo de exemplo `.env.example` e renomeie-o para `.env`. Em seguida, preencha as variáveis com as suas credenciais.
    ```bash
    cp .env.example .env
    ```
    
    O arquivo `.env` deve conter, no mínimo, as seguintes variáveis:
    ```env
    # API Keys (necessário pelo menos uma)
    GROQ_API_KEY=sua-chave-api
    GEMINI_API_KEY=sua-chave-api
    # Adicione ou altere outras variáveis de ambiente necessárias para a sua aplicação
    ```

### **Inicialização da aplicação**

Para subir todos os serviços (**Frontend** e **FastAPI**), execute o seguinte comando (ainda no diretório raiz):

```bash
docker compose up --build
```

O argumento `--build` é opcional, incorporando quaisquer atualizações no código para o container.

-----

## ✨ Principais Funcionalidades

| Funcionalidade | Detalhe Técnico |
| :--- | :--- |
| **Análise Conversacional** | Chatbot que responde perguntas sobre os dados, chama ferramentas de análise e gera gráficos sob demanda. |
| **Arquitetura de Agentes** | Dois Agentes orquestrados (`AnswerAgent` e `DataAnalystAgent`) para separar a lógica de conversação da análise de dados. |
| **Eficiência de Tokens** | Agente especialista acessa o DataFrame apenas internamente nas ferramentas, otimizando o consumo de tokens. |
| **Visualização Inteligente** | Geração de gráficos Plotly dinâmicos (Histogramas, Scatter Plots, etc.) sob comando do usuário. |
| **Cache de Gráficos** | Gráficos são serializados como JSON e armazenados em um banco de dados **SQLite** para evitar o reprocessamento e o envio do JSON/imagem no contexto da LLM. |
| **Suporte a Arquivos** | Permite upload de arquivos **CSV** e **ZIP** (com descompactação automática). |

### Alguns Exemplos

----

TODO

----

### 🌐 Endpoints da Aplicação

| Serviço | URL |
| :--- | :--- |
| **Frontend (React)** | `http://localhost:8501` |
| **API Docs (FastAPI - Swagger UI)** | `http://localhost:8000/api/docs` |

----


### 📂 Estrutura de arquivos

A estrutura do projeto está organizada da seguinte forma:

```
.
├── .env.example              # Exemplo de arquivo com as variáveis de ambiente
├── compose.yml        # Orquestração dos serviços Docker
├── Dockerfile                # Dockerfile para o backend (FastAPI)
├── Dockerfile.frontend      # Dockerfile para o frontend (React)
├── backend/                  # Código fonte do backend (FastAPI)
│   ├── src/
|   |   ├── agents/
|   |   ├── controllers/
|   |   ├── tools/
│   │   ├── services/
│   │   ├── schemas/
|   |   ├── utils/
│   │   ├── main.py
│   │   └── settings.py       # Configurações recebidas das variáveis de ambiente
│   ├── requirements.txt      # Arquivo de instalação das dependências
│   └── ...                   # Arquivos de configurações do projeto
└── README.md                 # Esta documentação
```

### **Detalhes técnicos**

O projeto utiliza uma hierarquia de agentes para otimizar o fluxo de trabalho:

1.  **`AnswerAgent` (Orquestrador):** Recebe o *prompt* do usuário. Decide se a pergunta é geral (responde diretamente) ou de dados. Se for de dados, chama o `DataAnalystAgent` como uma **ferramenta**.
2.  **`DataAnalystAgent` (Especialista):** Usa ferramentas especializadas (como `create_histogram`, `create_scatter_plot`) que:
      * Chamada a função **`get_dataframe()`** internamente para acessar os dados.
      * Geram a figura Plotly (`fig`).
      * Calculam e geram um **`metadata`** (resumo textual da análise) e salvam o gráfico via **`_save_graph_to_db(fig, metadata)`**.
3.  **Processamento de Gráficos:** A resposta do `DataAnalystAgent` contém o **`graph_id`** e o **`metadata`**. O *metadata* é injetado no contexto do `AnswerAgent` para ele poder comentar o gráfico, enquanto o Frontend usa o `graph_id` para buscar o JSON do Plotly no SQLite e renderizá-lo.


Se precisar de ajuda ou tiver alguma dúvida, sinta-se à vontade para abrir uma **issue** no repositório do GitHub ou entrar em contato.
