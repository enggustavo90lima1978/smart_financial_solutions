from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.chains.conversation.memory import ConversationSummaryMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool
from langchain_core.language_models import BaseChatModel
from langchain_core.memory import BaseMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

from src.settings import settings
from src.utils.exceptions import APIKeyNotFoundException, ExecutorNotFoundException


# Agente base para reaproveitamento e herança
class BaseAgent:
    def __init__(
        self,
        llm: BaseChatModel | None = None,
    ):
        self._llm = llm
        self.agent = None
        self.prompt = ChatPromptTemplate(
            [
                (
                    'system',
                    'You are a helpful agent that answers questions, respond to the questions objectively and only when certain, use the tools available to create better answers',
                ),
                MessagesPlaceholder('input'),
                MessagesPlaceholder('agent_scratchpad'),
            ]
        )

    @property
    def tools(self):
        """Add tools to amplify the agent capabilities."""
        tools = []

        return tools

    # Criar modelo de chat do Gemini
    def init_gemini_model(self, model_name='gemini-1.5-pro', **kwargs) -> None:
        """Instantiate a Gemini chat model and register for the agent.

        Args:
            model_name (str, optional): Name of model to be used. Defaults to 'gemini-1.5-pro'.
            temperature (int, optional): Temperature used in the model.

        Raises:
            APIKeyNotFoundException: raised when no API key is present.
        """
        if not settings.gemini_api_key:
            raise APIKeyNotFoundException(
                'Your Gemini API key is null, add an API key to the environment to proceed.'
            )

        self._llm = ChatGoogleGenerativeAI(
            model=model_name, google_api_key=settings.gemini_api_key, **kwargs
        )
        self.model_name, self.provider = model_name, 'google'

        return

    # Criar modelo de chat do Groq
    def init_groq_model(self, model_name='qwen/qwen3-32b', **kwargs) -> None:
        """Instantiate a Groq chat model and register for the agent.

        Args:
            model_name (str, optional): Name of model to be used. Defaults to 'qwen/qwen3-32b'.
            temperature (int, optional): Temperature used in the model

        Raises:
            APIKeyNotFoundException: raised when no API key is present.
        """
        if not settings.groq_api_key:
            raise APIKeyNotFoundException(
                'Your Groq API key is null, add an API key to the environment to proceed.'
            )

        self._llm = ChatGroq(
            model_name=model_name, api_key=settings.groq_api_key, **kwargs
        )
        self.model_name, self.provider = model_name, 'groq'

        return

    def _init_default_llm(self):
        """Instantiate a LLM predefined model when needed, based off the API keys available."""

        if settings.groq_api_key:
            self.init_groq_model('qwen/qwen3-32b', temperature=0)
        elif settings.gemini_api_key:
            self.init_gemini_model('gemini-2.5-flash', temperature=0)
        else:
            raise APIKeyNotFoundException

    # instanciar um modelo com base na chave de API e um agente
    def initialize_agent(
        self,
        tools: list[BaseTool] = None,
        prompt: ChatPromptTemplate | None = None,
        *,
        memory: BaseMemory | None = None,
        memory_key: str | None = None,
        verbose: bool = True,
    ):
        """Instantiate an agent using the defined options. Should be used after modifying the LLM object.

        Args:
            tools (any, optional): Tools for the agent, if None the default toolset is used.
            prompt (ChatPromptTemplate | None, optional): Prompt template used in the agent, if None the default template is used.
            memory (BaseMemory | None, optional): Memory instance used for the agent, if None uses the default ConversationSummarizeMemory:

            ```memory = ConversationSummaryMemory(
                memory_key=memory_key,
                input_key='input',
                output_key='output',
                return_messages=True,
                llm=self._llm,
            )
            ```
            memory_key (str | None, optional): Memory key used in the prompt template for chat history, if None no memory will be added for the agent.
            verbose (bool, optional): If the agent will print it's actions in console.

        Raises:
            APIKeyNotFoundException: if no API key is provided for initiating a LLM.
        """
        if self._llm is None:
            self._init_default_llm()

        # Criar um agente com função de tool calling
        agent = create_tool_calling_agent(
            self._llm, tools=tools or self.tools, prompt=prompt or self.prompt
        )

        # Se chave para histórico da memória, adicionar memória de sumarização ao agente
        if memory_key:
            memory = ConversationSummaryMemory(
                memory_key=memory_key,
                input_key='input',
                output_key='output',
                return_messages=True,
                llm=self._llm,
            )

        # Criar um ciclo de execução para o agente executar suas ferramentas
        self.agent = AgentExecutor(
            agent=agent,
            tools=tools or self.tools,
            memory=memory,
            max_iterations=7,
            verbose=verbose,
        )

    def get_model_info(self):
        return (self.model_name, self.provider)

    def run(self, user_input):
        if not self.agent:
            raise ExecutorNotFoundException()

        return self.agent.invoke({'input': user_input})
