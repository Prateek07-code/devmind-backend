import app.config as config
from app.services.llm.base import BaseLLMProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.services.llm.gemini_provider import GeminiCloudProvider  # <-- 1. Import it

def get_llm() -> BaseLLMProvider:
    """
    Reads the environment configuration and returns the appropriate LLM provider.
    The rest of the application never needs to know WHICH provider is running.
    """
    provider_name = config.LLM_PROVIDER.lower()
    
    if provider_name == "ollama":
        return OllamaProvider()
    elif provider_name == "gemini":
        return GeminiCloudProvider()  # <-- 2. Match the class name here!
    else:
        raise ValueError(f"Unsupported LLM provider: {provider_name}")