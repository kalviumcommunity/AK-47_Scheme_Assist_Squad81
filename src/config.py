import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False


# Load .env
load_dotenv()


# ─── Gemini Configuration ─────────────────────────────────────

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

CHAT_MODEL = os.getenv(
    "CHAT_MODEL",
    GEMINI_MODEL
)


# ─── Gemini Embedding Configuration ───────────────────────────

EMBED_MODEL = os.getenv(
    "EMBED_MODEL",
    "gemini-embedding-001"
)


# ─── Vector Database Settings ─────────────────────────────────

VECTOR_DB_TYPE = os.getenv(
    "VECTOR_DB_TYPE",
    "chroma"
)

CHROMA_PERSIST_DIR = os.getenv(
    "CHROMA_PERSIST_DIR",
    "chroma_db"
)

VECTOR_DB_URL = os.getenv(
    "VECTOR_DB_URL",
    CHROMA_PERSIST_DIR
)

COLLECTION_NAME = os.getenv(
    "COLLECTION_NAME",
    "scheme_assist_corpus"
)

# Must match your embedding output dimension
VECTOR_DIMENSION = int(
    os.getenv(
        "VECTOR_DIMENSION",
        "3072"
    )
)

SIMILARITY_METRIC = os.getenv(
    "SIMILARITY_METRIC",
    "cosine"
)


# ─── Backend API Settings ─────────────────────────────────────

API_HOST = os.getenv(
    "API_HOST",
    "0.0.0.0"
)

API_PORT = int(
    os.getenv(
        "API_PORT",
        "8000"
    )
)


# ─── Validation ───────────────────────────────────────────────

def validate_environment():
    """Validate SchemeAssist configuration."""

    if GEMINI_API_KEY:

        print(
            f"[CONFIG LOG] Provider: Google Gemini | "
            f"Chat Model: {CHAT_MODEL}"
        )

        print(
            f"[CONFIG LOG] Embedding Model: "
            f"{EMBED_MODEL}"
        )

    else:

        print(
            "[CONFIG WARNING] GEMINI_API_KEY is not set. "
            "Running in offline/fallback mode."
        )

    print(
        f"[CONFIG LOG] Vector DB: {VECTOR_DB_TYPE} "
        f"(URL: {VECTOR_DB_URL})"
    )

    print(
        f"[CONFIG LOG] Collection: {COLLECTION_NAME} | "
        f"dim={VECTOR_DIMENSION} | "
        f"metric={SIMILARITY_METRIC}"
    )

    print(
        f"[CONFIG LOG] API Server: "
        f"host={API_HOST}, port={API_PORT}"
    )