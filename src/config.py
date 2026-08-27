import os
from dotenv import load_dotenv

# Load secrets from local .env file
load_dotenv()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

def validate_environment():
    """Validates that environment configuration is present."""
    if not OPENAI_API_KEY:
        print("[CONFIG WARNING] OPENAI_API_KEY is not set in .env. Running in mock/offline mode.")
    else:
        print(f"[CONFIG LOG] Loaded model: {CHAT_MODEL} | Base URL: {OPENAI_BASE_URL}")
