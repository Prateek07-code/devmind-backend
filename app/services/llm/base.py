from abc import ABC, abstractmethod
from typing import Optional
class BaseLLMProvider(ABC):
    """
    The abstract base class for all LLM providers. 
    Any new provider (OpenAI, Anthropic, etc.) MUST implement these methods.
    """
    
    @abstractmethod
    async def generate_answer(self, prompt: str, system_prompt: Optional[str]) -> str:
        """
        Takes a fully augmented prompt and returns the AI's string response.
        """
        pass