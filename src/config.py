import os
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

# Load secrets from local .env file
load_dotenv()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")

# Vector Database Settings (ChromaDB)
VECTOR_DB_TYPE = os.getenv("VECTOR_DB_TYPE", "chroma")
default_db_dir = "data/chroma_db" if os.path.exists("data/chroma_db") else "chroma_db"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", default_db_dir)
VECTOR_DB_URL = os.getenv("VECTOR_DB_URL", CHROMA_PERSIST_DIR)
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "scheme_assist_corpus")
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "1536"))
SIMILARITY_METRIC = os.getenv("SIMILARITY_METRIC", "cosine")

# Backend API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

def validate_environment():
    """Validates that environment configuration is present."""
    if not OPENAI_API_KEY:
        print("[CONFIG WARNING] OPENAI_API_KEY is not set in .env. Running in mock/offline mode.")
    else:
        print(f"[CONFIG LOG] Loaded model: {CHAT_MODEL} | Base URL: {OPENAI_BASE_URL}")
    print(f"[CONFIG LOG] Vector DB: {VECTOR_DB_TYPE} (URL: {VECTOR_DB_URL}) | Collection: {COLLECTION_NAME} (dim={VECTOR_DIMENSION}, metric={SIMILARITY_METRIC})")
    print(f"[CONFIG LOG] API Server: host={API_HOST}, port={API_PORT}")
