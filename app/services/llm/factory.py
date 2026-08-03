import app.config as config
from app.services.llm.base import BaseLLMProvider
from app.services.llm.ollama_provider import OllamaProvider

def get_llm() -> BaseLLMProvider:
    """
    Reads the environment configuration and returns the appropriate LLM provider.
    The rest of the application never needs to know WHICH provider is running.
    """
    provider_name = config.LLM_PROVIDER.lower()
    
    if provider_name == "ollama":
        return OllamaProvider()
    # When you want to add OpenAI later, it is as simple as adding:
    # elif provider_name == "openai":
    #     return OpenAIProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")