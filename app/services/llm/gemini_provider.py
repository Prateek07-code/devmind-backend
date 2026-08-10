import os
from google import genai

class GeminiCloudProvider:
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        
    async def generate_answer(self, prompt: str, system_prompt: str = None) -> str:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",  # <-- Fixed model name to a valid production version
            contents=full_prompt
        )
        return response.text