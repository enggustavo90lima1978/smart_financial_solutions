from pydantic_core import ValidationError

from src.agents import SupervisorAgent
from src.schemas import ApiKeyInput, JSONOutput
from src.settings import settings
from src.utils.exceptions import APIKeyNotFoundException, ModelNotFoundException

MODELS = {
    'qwen/qwen3-32b': 'groq',
    'llama-3.1-8b-instant': 'groq',
    'llama-3.3-70b-versatile': 'groq',
    'openai/gpt-oss-20b': 'groq',
    'openai/gpt-oss-120b': 'groq',
    'gemini-2.5-flash': 'google',
    'gemini-2.5-pro': 'google',
}


class Chat:
    """
    Represents the chat service that interacts with the Supervisor.
    This class should be managed as a singleton to maintain chat history.
    """

    def __init__(self, agent: SupervisorAgent):
        # Recebe uma instância do agente em vez de criar uma nova.
        self.agent = agent

    async def send_prompt(self, user_input: str):
        response: str = self.agent.run(user_input)

        content = response['output'].strip('`').replace('json', '', 1)

        # Tentar converter em JSON, algumas respostas não são geradas no formato certo.
        try:
            response = JSONOutput.model_validate_json(content)
        except ValidationError:
            response = {'response': content, 'graph_id': ''}

        return response

    async def change_model(self, model_name: str):
        provider = MODELS.get(model_name, None)

        if not provider:
            raise ModelNotFoundException(
                'Wrong model name received, try again with a valid model.'
            )

        if provider == 'google':
            self.agent.init_gemini_model(model_name=model_name, temperature=0)
        elif provider == 'groq':
            self.agent.init_groq_model(model_name=model_name, temperature=0)

        self.agent.initialize_agent(
            memory_key='chat_history', tools=self.agent.tools, prompt=self.agent.prompt
        )

        return {'detail': f'Model changed to {model_name} from {provider.upper()}'}

    async def update_api_key(self, input: ApiKeyInput):
        provider = MODELS.GET(input.model_name)

        if provider == 'google':
            settings.gemini_api_key = input.api_key
        elif provider == 'groq':
            settings.groq_api_key = input.api_key
        else:
            raise ModelNotFoundException(
                'Wrong model name received, try again with a valid model.'
            )
        return {
            'detail': f'API key registered successfully for {provider.capitalize()} models'
        }


# --- Implementação do Singleton ---

_chat_instance: Chat | None = None


def get_chat_service(force_recreate: bool = False) -> Chat | None:
    """
    Returns a singleton instance of the Chat service.
    This ensures that the same agent and memory are used across requests.
    """
    global _chat_instance
    if _chat_instance is None or force_recreate:
        if settings.gemini_api_key or settings.groq_api_key:
            agent = SupervisorAgent()
            _chat_instance = Chat(agent)

        else:
            raise APIKeyNotFoundException

    return _chat_instance
