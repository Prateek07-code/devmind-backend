from app.services.llm.base import BaseLLMProvider
from app.services.llm.gemini_provider import GeminiCloudProvider

def get_llm() -> BaseLLMProvider:
    """
    Hardcoded to strictly use Gemini in the cloud.
    Bypassing config to prevent Ollama fallback.
    """
    print("🚀 SYSTEM OVERRIDE: Forcing GeminiCloudProvider")
    return GeminiCloudProvider()