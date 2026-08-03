print(">>> 2. CONFIG.PY IS RUNNING")

import os
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen2.5-coder:1.5b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

print(">>> 3. DOTENV LOADED")

if not GITHUB_TOKEN:
    print("WARNING: GITHUB_TOKEN is not set in the .env file.")
else:
    print("SUCCESS: GitHub Authentication Token loaded successfully.")