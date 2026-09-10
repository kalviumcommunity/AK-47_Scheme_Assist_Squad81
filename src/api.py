# -*- coding: utf-8 -*-
"""
src/api.py - SchemeAssist Backend API Service
================================================

SchemeAssist supports two answer modes:

1. VERIFIED RAG MODE
   - Searches ChromaDB
   - Uses uploaded / indexed scheme documents
   - Returns source citations

2. GENERAL SCHEME AI MODE
   - Used when the requested scheme is not available
     in the local ChromaDB knowledge base
   - Gemini answers general government scheme questions
   - Clearly marks the response as AI generated

Architecture:

Frontend
   |
   v
FastAPI
   |
   v
Scheme Query Detection
   |
   +----------------------------+
   |                            |
   v                            v
ChromaDB RAG               Gemini General Knowledge
   |                            |
   v                            v
Verified Answer             General Scheme Answer
   |                            |
   +-------------+--------------+
                 |
                 v
          Structured JSON
"""

import os
import re
import sys
import json
import logging
import hashlib
import datetime
import asyncio

from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

# ---------------------------------------------------------
# ROOT PATH
# ---------------------------------------------------------

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

# ---------------------------------------------------------
# FASTAPI
# ---------------------------------------------------------

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    UploadFile,
    File,
    status,
)

from fastapi.exceptions import RequestValidationError

from fastapi.responses import (
    JSONResponse,
    HTMLResponse,
    StreamingResponse,
)

from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field


# ---------------------------------------------------------
# SCHEMEASSIST IMPORTS
# ---------------------------------------------------------

from src.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    CHAT_MODEL,
    EMBED_MODEL,
    VECTOR_DB_URL,
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    API_HOST,
    API_PORT,
)

from src.embeddings import EmbeddingService

from src.vector_store import VectorStore

from src.retrieval import (
    SchemeRetriever,
    is_scheme_related_query,
    get_guardrail_response,
    is_retrieval_strong,
    MIN_RETRIEVAL_SCORE,
    WEAK_CONTEXT_MESSAGE,
)

from src.cleaning import clean_text

from src.ingestion import chunk_document_by_tokens

from src.llm_client import (
    build_client,
    make_completion,
)

from prompts.answer import (
    ANSWER_V2,
    render,
)

from prompts.templates import (
    SYSTEM_SCHEME_ASSIST_TEMPLATE,
)


# ---------------------------------------------------------
# LOGGER
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("schemeassist_api")


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

UPLOAD_DIR = Path("uploads")

SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".html",
    ".htm",
}

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


# ---------------------------------------------------------
# PIPELINE STATE
# ---------------------------------------------------------

pipeline_state: Dict[str, Any] = {

    "vector_store": None,

    "embedding_service": None,

    "retriever": None,

    "gemini_client": None,

}


# =========================================================
# PIPELINE INITIALIZATION
# =========================================================

def get_pipeline() -> Dict[str, Any]:

    # -----------------------------------------------------
    # EMBEDDINGS
    # -----------------------------------------------------

    if pipeline_state["embedding_service"] is None:

        logger.info(
            "Initializing embedding service..."
        )

        pipeline_state["embedding_service"] = EmbeddingService(

            model_name=EMBED_MODEL,

            force_offline=False,

        )


    # -----------------------------------------------------
    # VECTOR STORE
    # -----------------------------------------------------

    if pipeline_state["vector_store"] is None:

        logger.info(
            "Connecting to ChromaDB..."
        )

        candidates = [

            (
                CHROMA_PERSIST_DIR,
                COLLECTION_NAME,
            ),

            (
                "chroma_db",
                "scheme_assist_corpus",
            ),

            (
                "chroma_db",
                "schemeassist_chunks",
            ),

            (
                "data/chroma_db",
                "scheme_assist_corpus",
            ),

        ]

        vector_store = None


        for persist_dir, collection_name in candidates:

            try:

                if os.path.exists(persist_dir):

                    candidate = VectorStore(

                        persist_dir=persist_dir,

                        collection_name=collection_name,

                    )

                    count = candidate.count()


                    if count > 0:

                        vector_store = candidate

                        logger.info(

                            "Connected to ChromaDB '%s' collection '%s' with %d records.",

                            persist_dir,

                            collection_name,

                            count,

                        )

                        break


            except Exception as error:

                logger.warning(

                    "ChromaDB candidate failed: %s",

                    error,

                )


        # Create if nothing found

        if vector_store is None:

            vector_store = VectorStore(

                persist_dir=CHROMA_PERSIST_DIR,

                collection_name=COLLECTION_NAME,

            )


        pipeline_state["vector_store"] = vector_store


    # -----------------------------------------------------
    # RETRIEVER
    # -----------------------------------------------------

    if pipeline_state["retriever"] is None:

        try:

            pipeline_state["retriever"] = SchemeRetriever(

                db_dir=CHROMA_PERSIST_DIR,

                collection_name=COLLECTION_NAME,

            )

            logger.info(
                "SchemeRetriever initialized."
            )

        except Exception as error:

            logger.warning(

                "SchemeRetriever initialization warning: %s",

                error,

            )


    # -----------------------------------------------------
    # GEMINI
    # -----------------------------------------------------

    if pipeline_state["gemini_client"] is None:

        api_key = GEMINI_API_KEY or os.getenv(
            "GEMINI_API_KEY"
        )


        if api_key:

            try:

                pipeline_state["gemini_client"] = build_client()

                logger.info(
                    "Gemini client initialized."
                )

            except Exception as error:

                logger.warning(

                    "Gemini initialization warning: %s",

                    error,

                )


    return pipeline_state


# =========================================================
# GET RETRIEVER
# =========================================================

def get_retriever() -> SchemeRetriever:

    state = get_pipeline()


    if state["retriever"] is None:

        state["retriever"] = SchemeRetriever(

            db_dir=CHROMA_PERSIST_DIR,

            collection_name=COLLECTION_NAME,

        )


    return state["retriever"]


# =========================================================
# GET GEMINI CLIENT
# =========================================================

def get_gemini_client():

    state = get_pipeline()


    if state["gemini_client"] is None:

        state["gemini_client"] = build_client()


    return state["gemini_client"]


# =========================================================
# APPLICATION LIFESPAN
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info(
        "Starting SchemeAssist AI service..."
    )


    try:

        get_pipeline()

    except Exception as error:

        logger.warning(

            "Pipeline warmup warning: %s",

            error,

        )


    yield


    logger.info(
        "Shutting down SchemeAssist..."
    )


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(

    title="SchemeAssist API",

    description=(
        "AI powered Government Scheme Assistant "
        "using Gemini and ChromaDB RAG."
    ),

    version="2.0.0",

    lifespan=lifespan,

)


# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)


# =========================================================
# STATIC DIRECTORY
# =========================================================

STATIC_DIR = (
    Path(__file__).parent.parent
    / "static"
)


# =========================================================
# REQUEST MODELS
# =========================================================

class ChatRequest(BaseModel):

    question: str = Field(

        ...,

        min_length=3,

        max_length=2000,

        description="Government scheme question.",

    )


class QueryRequest(BaseModel):

    question: str = Field(

        ...,

        min_length=3,

        max_length=2000,

    )


# =========================================================
# SOURCE MODEL
# =========================================================

class ChatSource(BaseModel):

    scheme: str

    source: str

    section: Optional[str] = "General Overview"

    chunk_id: Optional[str] = None

    score: Optional[float] = None


# =========================================================
# CHAT RESPONSE
# =========================================================

class ChatResponse(BaseModel):

    answer: str

    eligibility: Optional[str] = ""

    benefits: Optional[str] = ""

    application_process: List[str] = Field(
        default_factory=list
    )

    documents_required: List[str] = Field(
        default_factory=list
    )

    sources: List[ChatSource] = Field(
        default_factory=list
    )

    status: str = "answered"

    answer_mode: str = "general_ai"


# =========================================================
# HEALTH RESPONSE
# =========================================================

class HealthResponse(BaseModel):

    status: str

    embedding_model: str

    chat_model: str

    collection_name: str

    indexed_chunks: int

    gemini_configured: bool

    openai_configured: bool = False


# =========================================================
# DOCUMENT MODELS
# =========================================================

class DocumentSummary(BaseModel):

    document: str

    chunks: int

    indexed: int


class DocumentUploadResponse(BaseModel):

    status: str

    filename: str

    summary: DocumentSummary


# =========================================================
# VALIDATION ERROR HANDLER
# =========================================================

@app.exception_handler(
    RequestValidationError
)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):

    return JSONResponse(

        status_code=422,

        content={

            "error": "Validation Error",

            "detail": exc.errors(),

            "status": "validation_error",

        },

    )


# =========================================================
# ROOT
# =========================================================

@app.get("/")

def root():

    return {

        "service": "SchemeAssist",

        "version": "2.0.0",

        "provider": "Google Gemini",

        "features": [

            "Government Scheme AI",

            "RAG Search",

            "ChromaDB",

            "Document Upload",

            "Hybrid Retrieval",

            "General Scheme Knowledge",

        ],

        "chat_url": "/api/chat",

        "health_url": "/api/health",

        "documents_url": "/api/documents",

        "docs_url": "/docs",

    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get(
    "/api/health",
    response_model=HealthResponse,
)

@app.get(
    "/health",
    response_model=HealthResponse,
)

def health_check():

    state = get_pipeline()


    vector_store = state.get(
        "vector_store"
    )


    indexed_chunks = 0


    if vector_store is not None:

        indexed_chunks = vector_store.count()


    retriever = state.get(
        "retriever"
    )


    if retriever:

        try:

            indexed_chunks = max(

                indexed_chunks,

                retriever.record_count,

            )

        except Exception:

            pass


    return {

        "status": "healthy",

        "embedding_model": EMBED_MODEL,

        "chat_model": (

            CHAT_MODEL
            or GEMINI_MODEL
        ),

        "collection_name": COLLECTION_NAME,

        "indexed_chunks": indexed_chunks,

        "gemini_configured": bool(
            GEMINI_API_KEY
            or os.getenv("GEMINI_API_KEY")
        ),

        "openai_configured": False,

    }


# =========================================================
# SCHEME QUESTION DETECTION
# =========================================================

def is_government_scheme_question(
    question: str
) -> bool:

    text = question.lower()


    # Clearly unrelated questions

    unrelated_keywords = [

        "javascript",

        "python",

        "react",

        "nextjs",

        "movie",

        "film",

        "song",

        "cricket score",

        "football score",

        "programming",

        "coding",

        "weather",

        "bitcoin",

    ]


    for keyword in unrelated_keywords:

        if keyword in text:

            return False


    # Scheme related keywords

    scheme_keywords = [

        "scheme",

        "yojana",

        "government",

        "govt",

        "benefit",

        "benefits",

        "subsidy",

        "subsidies",

        "eligibility",

        "eligible",

        "apply",

        "application",

        "financial assistance",

        "pension",

        "farmer",

        "agriculture",

        "student scholarship",

        "scholarship",

        "health insurance",

        "housing",

        "ration",

        "aadhaar",

        "dbt",

        "kisan",

        "pm-",

        "pm ",

        "pradhan mantri",

        "ayushman",

        "mudra",

        "ujjwala",

        "awas",

        "nrega",

        "mgnrega",

        "atal",

        "startup india",

        "digital india",

        "india",

    ]


    for keyword in scheme_keywords:

        if keyword in text:

            return True


    # Existing RAG detector

    try:

        if is_scheme_related_query(question):

            return True

    except Exception:

        pass


    return False


# =========================================================
# GENERAL GEMINI SCHEME ANSWER
# =========================================================

def generate_general_scheme_answer(
    question: str,
    client: Any,
) -> Dict[str, Any]:

    """
    Answers government scheme questions that are
    not available in the local ChromaDB database.
    """


    system_prompt = """

You are SchemeAssist, an AI assistant that helps citizens understand
government welfare schemes and public benefit programs.

You can answer questions about government schemes across India,
including central and state government schemes when information
is available.

Your responsibilities:

1. Explain government schemes clearly.
2. Explain eligibility criteria.
3. Explain benefits and financial assistance.
4. Explain application processes.
5. Explain required documents.
6. Mention official portals when you are confident.
7. Do not invent scheme details.
8. Do not make up financial amounts.
9. Do not present uncertain information as confirmed.
10. If a scheme has state-specific rules, clearly mention that.
11. If you are not sufficiently confident, say so.

IMPORTANT:

Return ONLY valid JSON.

Use exactly this format:

{
    "answer": "",
    "eligibility": "",
    "benefits": "",
    "application_process": [],
    "documents_required": []
}

If a field is unknown, use an empty string or empty array.

Use simple citizen-friendly language.

"""


    user_prompt = f"""

Citizen Question:

{question}

Provide accurate information about the government scheme.

Do not discuss unrelated topics.

Return JSON only.

"""


    messages = [

        {

            "role": "system",

            "content": system_prompt,

        },

        {

            "role": "user",

            "content": user_prompt,

        },

    ]


    reply = make_completion(
        client,
        messages,
    )


    if not reply:

        return {

            "answer": (
                "I am currently unable to generate "
                "a response. Please try again."
            ),

            "eligibility": "",

            "benefits": "",

            "application_process": [],

            "documents_required": [],

            "sources": [],

            "status": "error",

            "answer_mode": "general_ai",

        }


    # Remove markdown fences

    cleaned_reply = reply.strip()


    cleaned_reply = re.sub(

        r"^```json\s*",

        "",

        cleaned_reply,

        flags=re.IGNORECASE,

    )


    cleaned_reply = re.sub(

        r"^```\s*",

        "",

        cleaned_reply,

    )


    cleaned_reply = re.sub(

        r"\s*```$",

        "",

        cleaned_reply,

    ).strip()


    # Parse JSON

    try:

        parsed = json.loads(
            cleaned_reply
        )


        application_process = parsed.get(
            "application_process",
            [],
        )


        documents_required = parsed.get(
            "documents_required",
            [],
        )


        if isinstance(
            application_process,
            str,
        ):

            application_process = [
                application_process
            ]


        if isinstance(
            documents_required,
            str,
        ):

            documents_required = [
                documents_required
            ]


        return {

            "answer": str(

                parsed.get(
                    "answer",
                    "",
                )

            ),

            "eligibility": str(

                parsed.get(
                    "eligibility",
                    "",
                )

            ),

            "benefits": str(

                parsed.get(
                    "benefits",
                    "",
                )

            ),

            "application_process": [

                str(item)

                for item in application_process

                if str(item).strip()

            ],

            "documents_required": [

                str(item)

                for item in documents_required

                if str(item).strip()

            ],

            "sources": [

                {

                    "scheme": "General Government Scheme Information",

                    "source": "Google Gemini AI",

                    "section": "General Scheme Knowledge",

                    "chunk_id": None,

                    "score": None,

                }

            ],

            "status": "answered",

            "answer_mode": "general_ai",

        }


    except Exception:

        # Plain text fallback

        return {

            "answer": cleaned_reply,

            "eligibility": "",

            "benefits": "",

            "application_process": [],

            "documents_required": [],

            "sources": [

                {

                    "scheme": "General Government Scheme Information",

                    "source": "Google Gemini AI",

                    "section": "General Scheme Knowledge",

                    "chunk_id": None,

                    "score": None,

                }

            ],

            "status": "answered",

            "answer_mode": "general_ai",

        }


# =========================================================
# VERIFIED RAG ANSWER
# =========================================================

def generate_grounded_scheme_answer(

    question: str,

    retrieved_chunks: List[Dict[str, Any]],

    client: Any,

) -> Dict[str, Any]:


    context_blocks = []

    sources = []


    for index, chunk in enumerate(

        retrieved_chunks,

        start=1,

    ):

        metadata = chunk.get(
            "metadata",
            {},
        )


        source = (

            metadata.get("source")

            or chunk.get("source")

            or "Official Scheme Document"

        )


        section = metadata.get(

            "section",

            "General Overview",

        )


        scheme_name = metadata.get(
            "scheme_name"
        )


        if not scheme_name:

            scheme_name = (
                Path(source)
                .stem
                .replace("_", " ")
                .title()
            )


        text = (

            chunk.get("text")

            or chunk.get("content")

            or ""

        ).strip()


        score = (

            chunk.get("hybrid_score")

            or chunk.get("score")

        )


        context_blocks.append(

            f"""
--- SOURCE {index} ---

Scheme:
{scheme_name}

Document:
{source}

Section:
{section}

Content:
{text}
"""

        )


        sources.append(

            {

                "scheme": scheme_name,

                "source": source,

                "section": section,

                "chunk_id": (

                    chunk.get("id")

                    or chunk.get("chunk_id")

                ),

                "score": (

                    round(
                        float(score),
                        4,
                    )

                    if score is not None

                    else None

                ),

            }

        )


    context = "\n".join(
        context_blocks
    )


    system_prompt = """

You are SchemeAssist.

You are a government welfare scheme assistant.

Answer ONLY using the provided verified documents.

Rules:

1. Do not use outside knowledge.
2. Do not invent information.
3. Do not mix information from unrelated schemes.
4. If application steps are not provided,
   return an empty application_process array.
5. If documents are not provided,
   return an empty documents_required array.
6. Return JSON only.

"""


    user_prompt = f"""

VERIFIED SCHEME DOCUMENTS:

{context}


CITIZEN QUESTION:

{question}


Return ONLY JSON:

{{
    "answer": "",
    "eligibility": "",
    "benefits": "",
    "application_process": [],
    "documents_required": []
}}

"""


    messages = [

        {

            "role": "system",

            "content": system_prompt,

        },

        {

            "role": "user",

            "content": user_prompt,

        },

    ]


    reply = make_completion(
        client,
        messages,
    )


    if not reply:

        return {

            "answer": (
                "Unable to generate an answer "
                "at this moment."
            ),

            "eligibility": "",

            "benefits": "",

            "application_process": [],

            "documents_required": [],

            "sources": sources,

            "status": "error",

            "answer_mode": "verified_rag",

        }


    cleaned_reply = reply.strip()


    cleaned_reply = re.sub(

        r"^```json\s*",

        "",

        cleaned_reply,

        flags=re.IGNORECASE,

    )


    cleaned_reply = re.sub(

        r"^```\s*",

        "",

        cleaned_reply,

    )


    cleaned_reply = re.sub(

        r"\s*```$",

        "",

        cleaned_reply,

    ).strip()


    try:

        parsed = json.loads(
            cleaned_reply
        )


        application_process = parsed.get(
            "application_process",
            [],
        )


        documents_required = parsed.get(
            "documents_required",
            [],
        )


        if isinstance(
            application_process,
            str,
        ):

            application_process = [
                application_process
            ]


        if isinstance(
            documents_required,
            str,
        ):

            documents_required = [
                documents_required
            ]


        return {

            "answer": str(

                parsed.get(
                    "answer",
                    "",
                )

            ),

            "eligibility": str(

                parsed.get(
                    "eligibility",
                    "",
                )

            ),

            "benefits": str(

                parsed.get(
                    "benefits",
                    "",
                )

            ),

            "application_process": [

                str(item)

                for item in application_process

                if str(item).strip()

            ],

            "documents_required": [

                str(item)

                for item in documents_required

                if str(item).strip()

            ],

            "sources": sources,

            "status": "answered",

            "answer_mode": "verified_rag",

        }


    except Exception:

        return {

            "answer": cleaned_reply,

            "eligibility": "",

            "benefits": "",

            "application_process": [],

            "documents_required": [],

            "sources": sources,

            "status": "answered",

            "answer_mode": "verified_rag",

        }


# =========================================================
# MAIN CHAT ENDPOINT
# =========================================================

@app.post(

    "/api/chat",

    response_model=ChatResponse,

)

@app.post(

    "/chat",

    response_model=ChatResponse,

)

def chat_ai(
    request: ChatRequest
):

    question = request.question.strip()


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not question:

        raise HTTPException(

            status_code=400,

            detail="Question cannot be empty.",

        )


    logger.info(
        "CHAT QUESTION: %s",
        question,
    )


    # -----------------------------------------------------
    # CHECK QUESTION TYPE
    # -----------------------------------------------------

    if not is_government_scheme_question(
        question
    ):

        return {

            "answer": (
                "I can assist with government welfare schemes, "
                "eligibility, benefits, subsidies, pensions, "
                "scholarships, applications, and public schemes. "
                "Please ask a government scheme related question."
            ),

            "eligibility": "",

            "benefits": "",

            "application_process": [],

            "documents_required": [],

            "sources": [],

            "status": "refused_unrelated_query",

            "answer_mode": "guardrail",

        }


    try:

        client = get_gemini_client()


        # -------------------------------------------------
        # TRY RAG FIRST
        # -------------------------------------------------

        retriever = None

        results = []


        try:

            retriever = get_retriever()


            if retriever.record_count > 0:

                logger.info(
                    "Trying verified RAG search..."
                )


                results = retriever.search(

                    query=question,

                    top_k=4,

                )


        except Exception as error:

            logger.warning(

                "RAG search failed: %s",

                error,

            )


        # -------------------------------------------------
        # STRONG RAG RESULT
        # -------------------------------------------------

        if results:

            try:

                strong = is_retrieval_strong(

                    results,

                    min_score=MIN_RETRIEVAL_SCORE,

                )

            except Exception:

                strong = False


            if strong:

                logger.info(
                    "Using VERIFIED RAG mode."
                )


                return generate_grounded_scheme_answer(

                    question=question,

                    retrieved_chunks=results,

                    client=client,

                )


        # -------------------------------------------------
        # GENERAL AI FALLBACK
        # -------------------------------------------------

        logger.info(
            "Using GENERAL SCHEME AI mode."
        )


        return generate_general_scheme_answer(

            question=question,

            client=client,

        )


    except Exception as error:

        logger.exception(
            "Chat endpoint failed: %s",
            error,
        )


        raise HTTPException(

            status_code=500,

            detail=str(error),

        )


# =========================================================
# QUERY ENDPOINT
# =========================================================

@app.post(
    "/api/query"
)

@app.post(
    "/query"
)

def query_rag(
    request: QueryRequest
):

    """
    Query endpoint.

    Uses the same hybrid logic:

    RAG if verified documents exist
    ↓
    General Gemini answer if scheme is not indexed
    """

    chat_request = ChatRequest(
        question=request.question
    )


    return chat_ai(
        chat_request
    )


# =========================================================
# STREAMING ENDPOINT
# =========================================================

@app.post(
    "/api/query_stream"
)

@app.post(
    "/query_stream"
)

async def query_stream(
    request: QueryRequest
):

    question = request.question.strip()


    async def event_generator():

        try:

            # Run normal chat

            response = chat_ai(

                ChatRequest(
                    question=question
                )

            )


            # Metadata

            metadata = {

                "sources": response.get(
                    "sources",
                    [],
                ),

                "status": response.get(
                    "status",
                    "answered",
                ),

                "answer_mode": response.get(
                    "answer_mode",
                    "general_ai",
                ),

            }


            yield (

                "event: metadata\n"

                f"data: {json.dumps(metadata)}\n\n"

            )


            # Stream answer

            answer = response.get(
                "answer",
                "",
            )


            words = answer.split()


            for index, word in enumerate(
                words
            ):

                suffix = (
                    " "
                    if index < len(words) - 1
                    else ""
                )


                payload = {

                    "token": word + suffix

                }


                yield (

                    "event: token\n"

                    f"data: {json.dumps(payload)}\n\n"

                )


                await asyncio.sleep(
                    0.01
                )


            yield (

                "event: done\n"

                "data: {\"status\":\"complete\"}\n\n"

            )


        except Exception as error:

            logger.exception(
                "Streaming failed: %s",
                error,
            )


            yield (

                "event: error\n"

                f"data: {json.dumps({'error': str(error)})}\n\n"

            )


    return StreamingResponse(

        event_generator(),

        media_type="text/event-stream",

    )


# =========================================================
# DOCUMENT VALIDATION
# =========================================================

def validate_upload(
    file: UploadFile
) -> str:

    if not file.filename:

        raise HTTPException(

            status_code=400,

            detail="Invalid filename.",

        )


    extension = (
        Path(file.filename)
        .suffix
        .lower()
    )


    if extension not in SUPPORTED_EXTENSIONS:

        raise HTTPException(

            status_code=415,

            detail=(
                "Unsupported file type. "
                "Supported: "
                + ", ".join(
                    sorted(
                        SUPPORTED_EXTENSIONS
                    )
                )
            ),

        )


    return extension


# =========================================================
# STORE UPLOAD
# =========================================================

async def store_upload(
    file: UploadFile
) -> Path:

    validate_upload(file)


    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    filename = Path(
        file.filename
    ).name


    path = (
        UPLOAD_DIR
        / filename
    )


    content = await file.read()


    if not content:

        raise HTTPException(

            status_code=400,

            detail="Uploaded file is empty.",

        )


    if len(content) > MAX_UPLOAD_SIZE_BYTES:

        raise HTTPException(

            status_code=413,

            detail="File exceeds 10MB limit.",

        )


    path.write_bytes(
        content
    )


    return path


# =========================================================
# PROCESS DOCUMENT
# =========================================================

def process_uploaded_document(
    path: Path
) -> Dict[str, Any]:

    state = get_pipeline()


    vector_store = state.get(
        "vector_store"
    )


    embedding_service = state.get(
        "embedding_service"
    )


    if vector_store is None:

        raise HTTPException(

            status_code=503,

            detail="Vector database unavailable.",

        )


    extension = (
        path.suffix.lower()
    )


    raw_text = ""


    # -----------------------------------------------------
    # TXT / MD
    # -----------------------------------------------------

    if extension in [

        ".txt",

        ".md",

    ]:

        raw_text = path.read_text(

            encoding="utf-8",

            errors="replace",

        )


    # -----------------------------------------------------
    # HTML
    # -----------------------------------------------------

    elif extension in [

        ".html",

        ".htm",

    ]:

        html = path.read_text(

            encoding="utf-8",

            errors="replace",

        )


        try:

            from bs4 import BeautifulSoup


            soup = BeautifulSoup(

                html,

                "html.parser",

            )


            for tag in soup([

                "script",

                "style",

                "noscript",

            ]):

                tag.decompose()


            raw_text = soup.get_text(

                separator="\n"

            )


        except Exception:

            raw_text = re.sub(

                r"<[^>]+>",

                " ",

                html,

            )


    # -----------------------------------------------------
    # PDF
    # -----------------------------------------------------

    elif extension == ".pdf":

        try:

            from pypdf import PdfReader


            reader = PdfReader(
                str(path)
            )


            pages = []


            for page in reader.pages:

                text = page.extract_text()


                if text:

                    pages.append(
                        text
                    )


            raw_text = "\n".join(
                pages
            )


        except Exception as error:

            raise HTTPException(

                status_code=422,

                detail=f"PDF error: {error}",

            )


    else:

        raise HTTPException(

            status_code=415,

            detail="Unsupported document.",

        )


    # -----------------------------------------------------
    # CLEAN
    # -----------------------------------------------------

    cleaned_text = clean_text(
        raw_text
    )


    if not cleaned_text:

        raise HTTPException(

            status_code=422,

            detail="No readable text found.",

        )


    # -----------------------------------------------------
    # CHUNK
    # -----------------------------------------------------

    document = {

        "filename": path.name,

        "filepath": str(path),

        "content": cleaned_text,

    }


    chunks = chunk_document_by_tokens(

        doc=document,

        chunk_size_tokens=250,

        overlap_tokens=50,

    )


    if not chunks:

        chunks = [

            {

                "text": cleaned_text,

                "metadata": {

                    "source": path.name,

                    "section": "General Overview",

                },

            }

        ]


    # -----------------------------------------------------
    # METADATA
    # -----------------------------------------------------

    document_hash = hashlib.sha256(

        cleaned_text.encode()

    ).hexdigest()[:16]


    timestamp = (

        datetime.datetime.now(

            datetime.timezone.utc

        ).isoformat()

    )


    records = []


    for index, chunk in enumerate(
        chunks
    ):

        chunk_id = (

            f"{path.stem}:"
            f"chunk:"
            f"{index + 1}"
        )


        metadata = dict(

            chunk.get(
                "metadata",
                {},
            )

        )


        metadata.update({

            "source": path.name,

            "section": metadata.get(

                "section",

                "General Overview",

            ),

            "content_hash": document_hash,

            "ingestion_time": timestamp,

            "scheme_name": metadata.get(

                "scheme_name",

                path.stem.replace(
                    "_",
                    " "
                ).title(),

            ),

        })


        records.append({

            "id": chunk_id,

            "text": chunk["text"],

            "metadata": metadata,

        })


    # -----------------------------------------------------
    # EMBEDDINGS
    # -----------------------------------------------------

    texts = [

        record["text"]

        for record in records

    ]


    embeddings = embedding_service.embed_texts(
        texts
    )


    # -----------------------------------------------------
    # VECTOR RECORDS
    # -----------------------------------------------------

    vector_records = []


    for record, vector in zip(

        records,

        embeddings,

    ):

        vector_records.append({

            "id": record["id"],

            "vector": vector,

            "text": record["text"],

            "metadata": record["metadata"],

        })


    indexed = vector_store.upsert_batch(

        vector_records
    )


    logger.info(

        "Document indexed: %s | %d chunks",

        path.name,

        indexed,

    )


    # -----------------------------------------------------
    # REFRESH RETRIEVER
    # -----------------------------------------------------

    pipeline_state["retriever"] = None


    try:

        get_retriever()

    except Exception as error:

        logger.warning(

            "Retriever refresh warning: %s",

            error,

        )


    return {

        "document": str(path),

        "chunks": len(records),

        "indexed": indexed,

    }


# =========================================================
# UPLOAD DOCUMENT
# =========================================================

@app.post(

    "/api/documents",

    response_model=DocumentUploadResponse,

)

@app.post(

    "/documents",

    response_model=DocumentUploadResponse,

)

async def upload_document(

    file: UploadFile = File(...)

):

    path = await store_upload(
        file
    )


    summary = process_uploaded_document(
        path
    )


    return {

        "status": "indexed",

        "filename": file.filename,

        "summary": summary,

    }


# =========================================================
# LIST DOCUMENTS
# =========================================================

@app.get(
    "/api/documents"
)

@app.get(
    "/documents"
)

def list_documents():

    if not UPLOAD_DIR.exists():

        return {

            "documents": [],

            "total": 0,

        }


    documents = []


    for file in UPLOAD_DIR.iterdir():

        if file.is_file():

            documents.append({

                "filename": file.name,

                "size_bytes": file.stat().st_size,

                "path": str(file),

            })


    return {

        "documents": documents,

        "total": len(documents),

    }


# =========================================================
# START SERVER
# =========================================================

def start():

    import uvicorn


    logger.info(

        "Starting SchemeAssist on %s:%d",

        API_HOST,

        API_PORT,

    )


    uvicorn.run(

        "src.api:app",

        host=API_HOST,

        port=API_PORT,

        reload=False,

    )


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    start()