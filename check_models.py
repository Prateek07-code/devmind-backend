import os
from google import genai
from dotenv import load_dotenv

# Load your API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API Key not found.")
    exit()

client = genai.Client(api_key=api_key)

print("🔍 Querying Google for your available models...\n")
try:
    for model in client.models.list():
        # Filter for text-generation models
        if "gemini" in model.name:
            print(f"✅ {model.name}")
except Exception as e:
    print(f"Error fetching models: {e}")