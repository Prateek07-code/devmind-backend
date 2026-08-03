import httpx
from app.services.llm.base import BaseLLMProvider
import app.config as config

class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = config.OLLAMA_BASE_URL
        self.model = config.LLM_MODEL_NAME

    async def generate_answer(self, prompt: str, system_prompt: str |None= None) -> str:
        """
        Communicates with the local Ollama API asynchronously.
        """
        # Ollama's /api/generate endpoint expects this exact JSON structure
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False # For now, we wait for the full response. We can stream later!
        }
        
        if system_prompt:
            payload["system"] = system_prompt

        # Use httpx to make a non-blocking request to the local Ollama server
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120.0 # CPU inference can take a minute, give it time so it doesn't crash
            )
            
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")