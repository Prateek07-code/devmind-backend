import os
from google import genai
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from typing import AsyncGenerator

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers."""

    @abstractmethod
    def generate_stream(
        self,
        prompt: str,
        system_prompt: str = "",
    ) -> AsyncGenerator[str, None]:
        pass
    
    @abstractmethod
    async def generate_answer(
        self,
        prompt: str,
        system_prompt: str = "",
    ) -> str:
        """Generates a complete, single response string from the LLM."""
        pass

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("⚠️ WARNING: GEMINI_API_KEY not found in .env file!")

client = genai.Client(api_key=api_key) if api_key else None

def call_llm_stream(prompt: str):
    """
    Streams the RAG prompt to the LLM and yields chunks as they generate.
    """
    if not client:
        yield "Error: LLM API key not configured. Please check your .env file."
        return
        
    try:
        response_stream = client.models.generate_content_stream(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        
        for chunk in response_stream:
            # Yield each text chunk as it arrives from the API
            if chunk.text:
                yield chunk.text
                
    except Exception as e:
        yield f"\n❌ Error streaming LLM: {str(e)}"