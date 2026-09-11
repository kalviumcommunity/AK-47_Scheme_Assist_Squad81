# -*- coding: utf-8 -*-

"""
SchemeAssist Backend API

Features:
- Verified RAG using ChromaDB
- AI fallback for schemes not available locally
- Document upload and indexing
- Source filtering
- Scheme-aware retrieval
- Removes sample/test documents from production answers
"""

import os
import re
import sys
import json
import logging
import hashlib
import datetime
import asyncio
import mimetypes

from pathlib import Path
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

# =========================================================
# ROOT PATH
# =========================================================

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))


# =========================================================
# FASTAPI
# =========================================================

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    UploadFile,
    File,
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.exceptions import RequestValidationError

from fastapi.responses import (
    JSONResponse,
    StreamingResponse,
    FileResponse,
)

from pydantic import BaseModel, Field


# =========================================================
# SCHEMEASSIST IMPORTS
# =========================================================

from src.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    CHAT_MODEL,
    EMBED_MODEL,
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
    is_retrieval_strong,
    MIN_RETRIEVAL_SCORE,
)

from src.cleaning import clean_text

from src.ingestion import chunk_document_by_tokens

from src.llm_client import (
    build_client,
    make_completion,
)


# =========================================================
# LOGGER
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger("schemeassist_api")


# =========================================================
# CONFIGURATION
# =========================================================

UPLOAD_DIR = ROOT_DIR / "uploads"

SUPPORTED_EXTENSIONS = {
    ".txt",
    ".md",
    ".pdf",
    ".html",
    ".htm",
}

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


# =========================================================
# DOCUMENTS TO EXCLUDE FROM PRODUCTION RAG
# =========================================================

EXCLUDED_DOCUMENTS = {
    "sample_doc.md",
    "sample_doc.txt",
    "test_doc.md",
    "test.txt",
    "demo.md",
}


# =========================================================
# PIPELINE STATE
# =========================================================

pipeline_state: Dict[str, Any] = {

    "vector_store": None,

    "embedding_service": None,

    "retriever": None,

    "gemini_client": None,

}


# =========================================================
# SCHEME DETECTION
# =========================================================

KNOWN_SCHEMES = {

    "pm-kisan": [
        "pm-kisan",
        "pm kisan",
        "kisan samman",
        "pradhan mantri kisan",
        "kisan samman nidhi",
    ],

    "ayushman_bharat": [
        "ayushman",
        "pmjay",
        "pm-jay",
        "ayushman bharat",
        "jan arogya",
    ],

    "pm_awas": [
        "pmay",
        "pm awas",
        "pradhan mantri awas",
        "awas yojana",
    ],

    "ujjwala": [
        "ujjwala",
        "pmuy",
        "gas subsidy",
    ],

    "mudra": [
        "mudra",
        "mudra loan",
        "pmmy",
    ],

    "mgnrega": [
        "mgnrega",
        "nrega",
        "mnrega",
        "mahatma gandhi employment",
    ],

}


def detect_scheme(question: str) -> Optional[str]:

    text = question.lower()

    for scheme, keywords in KNOWN_SCHEMES.items():

        for keyword in keywords:

            if keyword in text:
                return scheme

    return None


# =========================================================
# PIPELINE INITIALIZATION
# =========================================================

def get_pipeline() -> Dict[str, Any]:

    # -----------------------------------------------------
    # EMBEDDINGS
    # -----------------------------------------------------

    if pipeline_state["embedding_service"] is None:

        logger.info("Initializing embedding service...")

        pipeline_state["embedding_service"] = EmbeddingService(

            model_name=EMBED_MODEL,

            force_offline=False,

        )


    # -----------------------------------------------------
    # VECTOR STORE
    # -----------------------------------------------------

    if pipeline_state["vector_store"] is None:

        logger.info("Connecting to ChromaDB...")

        vector_store = VectorStore(

            persist_dir=CHROMA_PERSIST_DIR,

            collection_name=COLLECTION_NAME,

        )

        logger.info(
            "Connected to ChromaDB: %s | Collection: %s",
            CHROMA_PERSIST_DIR,
            COLLECTION_NAME,
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

            logger.info("SchemeRetriever initialized.")

        except Exception as error:

            logger.error(
                "Retriever initialization failed: %s",
                error,
            )


    # -----------------------------------------------------
    # GEMINI CLIENT
    # -----------------------------------------------------

    if pipeline_state["gemini_client"] is None:

        api_key = (
            GEMINI_API_KEY
            or os.getenv("GEMINI_API_KEY")
        )

        if not api_key:

            logger.warning(
                "GEMINI_API_KEY not configured."
            )

        else:

            try:

                pipeline_state["gemini_client"] = build_client()

                logger.info(
                    "AI client initialized successfully."
                )

            except Exception as error:

                logger.exception(
                    "AI client initialization failed: %s",
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
# GET AI CLIENT
# =========================================================

def get_ai_client():

    state = get_pipeline()

    if state["gemini_client"] is None:

        state["gemini_client"] = build_client()

    return state["gemini_client"]


# =========================================================
# LIFESPAN
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
            "Pipeline startup warning: %s",
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
        "AI Powered Government Scheme Assistant "
        "with Verified RAG"
    ),

    version="3.0.0",

    lifespan=lifespan,

)


# =========================================================
# CORS
# =========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:3000",

        "http://127.0.0.1:3000",

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)


# =========================================================
# MODELS
# =========================================================

class ChatRequest(BaseModel):

    question: str = Field(

        ...,

        min_length=3,

        max_length=2000,

    )


class QueryRequest(BaseModel):

    question: str = Field(

        ...,

        min_length=3,

        max_length=2000,

    )


class ChatSource(BaseModel):

    scheme: str

    source: str

    section: Optional[str] = "General Overview"

    chunk_id: Optional[str] = None

    score: Optional[float] = None


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


class HealthResponse(BaseModel):

    status: str

    embedding_model: str

    chat_model: str

    collection_name: str

    indexed_chunks: int

    gemini_configured: bool


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

        "version": "3.0.0",

        "chat_url": "/api/chat",

        "health_url": "/api/health",

        "documents_url": "/api/documents",

    }


# =========================================================
# HEALTH
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

    if vector_store:

        try:

            indexed_chunks = vector_store.count()

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

    }


# =========================================================
# GOVERNMENT SCHEME QUESTION DETECTION
# =========================================================

def is_government_scheme_question(
    question: str
) -> bool:

    text = question.lower()


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

        "bitcoin",

    ]


    for keyword in unrelated_keywords:

        if keyword in text:
            return False


    scheme_keywords = [

        "scheme",

        "yojana",

        "government",

        "benefit",

        "eligibility",

        "eligible",

        "subsidy",

        "pension",

        "farmer",

        "agriculture",

        "scholarship",

        "health insurance",

        "housing",

        "ration",

        "aadhaar",

        "dbt",

        "kisan",

        "pm-",

        "pradhan mantri",

        "ayushman",

        "mudra",

        "ujjwala",

        "awas",

        "nrega",

        "mgnrega",

    ]


    for keyword in scheme_keywords:

        if keyword in text:
            return True


    try:

        return is_scheme_related_query(question)

    except Exception:

        return False


# =========================================================
# FILTER RETRIEVAL RESULTS
# =========================================================

def filter_retrieval_results(
    results: List[Dict[str, Any]],
    question: str,
) -> List[Dict[str, Any]]:

    detected_scheme = detect_scheme(
        question
    )

    filtered = []

    seen_sources = set()


    for result in results:

        metadata = result.get(
            "metadata",
            {}
        )

        source = (

            metadata.get("source")

            or result.get("source")

            or ""

        )

        source_lower = source.lower()


        # ---------------------------------------------
        # REMOVE SAMPLE / TEST DOCUMENTS
        # ---------------------------------------------

        if source_lower in EXCLUDED_DOCUMENTS:

            logger.info(
                "Excluded test document: %s",
                source,
            )

            continue


        # ---------------------------------------------
        # GET TEXT
        # ---------------------------------------------

        text = (

            result.get("text")

            or result.get("content")

            or ""

        ).lower()


        scheme_name = (

            metadata.get("scheme_name")

            or ""

        ).lower()


        searchable = (

            source_lower
            + " "
            + text
            + " "
            + scheme_name

        )


        # ---------------------------------------------
        # SCHEME MATCH FILTER
        # ---------------------------------------------

        if detected_scheme:

            keywords = KNOWN_SCHEMES.get(
                detected_scheme,
                []
            )

            matches_scheme = any(

                keyword in searchable

                for keyword in keywords

            )


            if not matches_scheme:

                logger.info(

                    "Excluded unrelated source: %s",

                    source,

                )

                continue


        # ---------------------------------------------
        # DUPLICATE SOURCE + SECTION
        # ---------------------------------------------

        section = metadata.get(
            "section",
            "General Overview"
        )

        unique_key = (
            source,
            section
        )


        if unique_key in seen_sources:

            continue


        seen_sources.add(
            unique_key
        )


        filtered.append(
            result
        )


    # ---------------------------------------------
    # SORT BY SCORE
    # ---------------------------------------------

    filtered.sort(

        key=lambda item: float(

            item.get(
                "hybrid_score",

                item.get(
                    "score",
                    0
                )

            )

            or 0

        ),

        reverse=True,

    )


    logger.info(

        "Retrieval results: %d -> %d",

        len(results),

        len(filtered),

    )


    return filtered


# =========================================================
# SAFE JSON PARSER
# =========================================================

def parse_ai_response(
    reply: str
) -> Dict[str, Any]:

    if not reply:

        raise ValueError(
            "Empty AI response"
        )


    cleaned = reply.strip()


    cleaned = re.sub(

        r"^```json\s*",

        "",

        cleaned,

        flags=re.IGNORECASE,

    )


    cleaned = re.sub(

        r"^```\s*",

        "",

        cleaned,

    )


    cleaned = re.sub(

        r"\s*```$",

        "",

        cleaned,

    ).strip()


    try:

        return json.loads(
            cleaned
        )

    except Exception:

        # Try extracting JSON object

        match = re.search(

            r"\{.*\}",

            cleaned,

            flags=re.DOTALL,

        )


        if match:

            try:

                return json.loads(
                    match.group()
                )

            except Exception:

                pass


        return {

            "answer": cleaned,

            "eligibility": "",

            "benefits": "",

            "application_process": [],

            "documents_required": [],

        }


# =========================================================
# NORMALIZE RESPONSE
# =========================================================

def normalize_response(
    parsed: Dict[str, Any]
) -> Dict[str, Any]:

    application_process = parsed.get(

        "application_process",

        []

    )


    documents_required = parsed.get(

        "documents_required",

        []

    )


    if isinstance(
        application_process,
        str
    ):

        application_process = [

            application_process

        ]


    if isinstance(
        documents_required,
        str
    ):

        documents_required = [

            documents_required

        ]


    return {

        "answer": str(

            parsed.get(
                "answer",
                ""
            )

        ).strip(),

        "eligibility": str(

            parsed.get(
                "eligibility",
                ""
            )

        ).strip(),

        "benefits": str(

            parsed.get(
                "benefits",
                ""
            )

        ).strip(),

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

    }


# =========================================================
# GENERAL AI ANSWER
# =========================================================

def generate_general_scheme_answer(

    question: str,

    client: Any,

) -> Dict[str, Any]:


    system_prompt = """

You are SchemeAssist.

You help citizens understand Indian government schemes.

Provide clear and accurate information.

Rules:

1. Do not invent information.
2. Do not invent financial amounts.
3. Clearly mention uncertainty.
4. Mention state-specific differences where relevant.
5. Keep language simple.
6. Return ONLY valid JSON.

Required JSON:

{
    "answer": "",
    "eligibility": "",
    "benefits": "",
    "application_process": [],
    "documents_required": []
}

"""


    messages = [

        {

            "role": "system",

            "content": system_prompt,

        },

        {

            "role": "user",

            "content": question,

        },

    ]


    try:

        reply = make_completion(

            client,

            messages,

        )


        logger.info(
            "General AI response received: %s",
            bool(reply)
        )


        parsed = parse_ai_response(
            reply
        )


        result = normalize_response(
            parsed
        )


        return {

            **result,

            "sources": [],

            "status": "answered",

            "answer_mode": "general_ai",

        }


    except Exception as error:

        logger.exception(

            "General AI generation failed: %s",

            error,

        )


        return {

            "answer": (
                "I could not generate a verified answer "
                "at the moment. Please try again shortly."
            ),

            "eligibility": "",

            "benefits": "",

            "application_process": [],

            "documents_required": [],

            "sources": [],

            "status": "error",

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

            {}

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

SOURCE {index}

Scheme Name:
{scheme_name}

Document:
{source}

Section:
{section}

Verified Content:
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
                        4
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

You answer questions about government schemes using ONLY
the verified document context provided.

IMPORTANT RULES:

1. Use ONLY the provided verified context.
2. Never use external knowledge.
3. Never invent information.
4. Do not combine different schemes.
5. If eligibility is not available, return empty text.
6. If benefits are not available, return empty text.
7. If application steps are unavailable, return [].
8. If documents are unavailable, return [].
9. Return ONLY valid JSON.
10. Do not return markdown.
11. Do not return explanations outside JSON.

JSON FORMAT:

{
    "answer": "",
    "eligibility": "",
    "benefits": "",
    "application_process": [],
    "documents_required": []
}

"""


    user_prompt = f"""

VERIFIED DOCUMENT CONTEXT:

{context}


CITIZEN QUESTION:

{question}


Generate the answer strictly from the verified context.

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


    try:

        logger.info(
            "Generating verified RAG answer..."
        )


        reply = make_completion(

            client,

            messages,

        )


        logger.info(
            "RAG AI response received: %s",
            bool(reply)
        )


        # -----------------------------------------
        # EMPTY RESPONSE FALLBACK
        # -----------------------------------------

        if not reply:

            logger.error(
                "AI returned empty response."
            )


            return {

                "answer": (
                    "I found relevant verified government "
                    "documents, but the AI response service "
                    "did not return an answer. Please try again."
                ),

                "eligibility": "",

                "benefits": "",

                "application_process": [],

                "documents_required": [],

                "sources": sources,

                "status": "generation_error",

                "answer_mode": "verified_rag",

            }


        parsed = parse_ai_response(
            reply
        )


        result = normalize_response(
            parsed
        )


        # -----------------------------------------
        # CHECK EMPTY ANSWER
        # -----------------------------------------

        if not result["answer"]:

            result["answer"] = (

                "Relevant information was found in the "
                "verified scheme documents, but a complete "
                "answer could not be generated."

            )


        return {

            **result,

            "sources": sources,

            "status": "answered",

            "answer_mode": "verified_rag",

        }


    except Exception as error:

        logger.exception(

            "Verified RAG generation failed: %s",

            error,

        )


        return {

            "answer": (
                "I found relevant verified documents but "
                "could not process them into an answer."
            ),

            "eligibility": "",

            "benefits": "",

            "application_process": [],

            "documents_required": [],

            "sources": sources,

            "status": "generation_error",

            "answer_mode": "verified_rag",

        }


# =========================================================
# CHAT ENDPOINT
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


    logger.info(
        "QUESTION: %s",
        question
    )


    # -----------------------------------------------------
    # VALIDATE QUESTION
    # -----------------------------------------------------

    if not question:

        raise HTTPException(

            status_code=400,

            detail="Question cannot be empty."

        )


    # -----------------------------------------------------
    # GUARDRAIL
    # -----------------------------------------------------

    if not is_government_scheme_question(
        question
    ):

        return {

            "answer": (
                "I can help with Indian government schemes, "
                "eligibility, benefits, subsidies, pensions, "
                "scholarships and applications."
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

        client = get_ai_client()


        # -------------------------------------------------
        # DETECT SCHEME
        # -------------------------------------------------

        detected_scheme = detect_scheme(
            question
        )


        logger.info(

            "Detected scheme: %s",

            detected_scheme

        )


        # -------------------------------------------------
        # RAG SEARCH
        # -------------------------------------------------

        results = []


        try:

            retriever = get_retriever()


            if retriever.record_count > 0:

                logger.info(
                    "Searching verified documents..."
                )


                raw_results = retriever.search(

                    query=question,

                    top_k=10,

                )


                logger.info(

                    "Raw RAG results: %d",

                    len(raw_results)

                )


                # -----------------------------------------
                # FILTER RESULTS
                # -----------------------------------------

                results = filter_retrieval_results(

                    raw_results,

                    question,

                )


                # Limit final results

                results = results[:4]


        except Exception as error:

            logger.exception(

                "RAG search failed: %s",

                error,

            )


        # -------------------------------------------------
        # USE VERIFIED RAG
        # -------------------------------------------------

        if results:

            logger.info(

                "Verified relevant documents found: %d",

                len(results)

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
            "No verified scheme documents found."
        )

        logger.info(
            "Using General AI mode."
        )


        return generate_general_scheme_answer(

            question=question,

            client=client,

        )


    except Exception as error:

        logger.exception(

            "Chat failed: %s",

            error,

        )


        raise HTTPException(

            status_code=500,

            detail=str(error),

        )


# =========================================================
# QUERY ENDPOINT
# =========================================================

@app.post("/api/query")
@app.post("/query")

def query_rag(
    request: QueryRequest
):

    return chat_ai(

        ChatRequest(
            question=request.question
        )

    )


# =========================================================
# STREAMING
# =========================================================

@app.post("/api/query_stream")
@app.post("/query_stream")

async def query_stream(
    request: QueryRequest
):

    question = request.question.strip()


    async def event_generator():

        try:

            response = chat_ai(

                ChatRequest(
                    question=question
                )

            )


            metadata = {

                "sources": response.get(
                    "sources",
                    []
                ),

                "status": response.get(
                    "status",
                    "answered"
                ),

                "answer_mode": response.get(
                    "answer_mode",
                    "general_ai"
                ),

            }


            yield (

                "event: metadata\n"

                f"data: {json.dumps(metadata)}\n\n"

            )


            answer = response.get(
                "answer",
                ""
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


                yield (

                    "event: token\n"

                    f"data: {json.dumps({'token': word + suffix})}\n\n"

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
                error
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

            detail="Invalid filename."

        )


    extension = Path(

        file.filename

    ).suffix.lower()


    if extension not in SUPPORTED_EXTENSIONS:

        raise HTTPException(

            status_code=415,

            detail=(

                "Unsupported file type. "

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

    validate_upload(
        file
    )


    UPLOAD_DIR.mkdir(

        parents=True,

        exist_ok=True,

    )


    filename = Path(

        file.filename

    ).name


    path = UPLOAD_DIR / filename


    content = await file.read()


    if not content:

        raise HTTPException(

            status_code=400,

            detail="Uploaded file is empty."

        )


    if len(content) > MAX_UPLOAD_SIZE_BYTES:

        raise HTTPException(

            status_code=413,

            detail="File exceeds 10MB limit."

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

            detail="Vector database unavailable."

        )


    extension = path.suffix.lower()

    raw_text = ""


    # -----------------------------------------------------
    # TXT / MD
    # -----------------------------------------------------

    if extension in [
        ".txt",
        ".md"
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
        ".htm"
    ]:

        html = path.read_text(

            encoding="utf-8",

            errors="replace",

        )


        try:

            from bs4 import BeautifulSoup


            soup = BeautifulSoup(

                html,

                "html.parser"

            )


            for tag in soup([
                "script",
                "style",
                "noscript"
            ]):

                tag.decompose()


            raw_text = soup.get_text(

                separator="\n"

            )


        except Exception:

            raw_text = re.sub(

                r"<[^>]+>",

                " ",

                html

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

                detail=f"PDF error: {error}"

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

            detail="No readable text found."

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
    # DOCUMENT HASH
    # -----------------------------------------------------

    document_hash = hashlib.sha256(

        cleaned_text.encode()

    ).hexdigest()[:16]


    timestamp = datetime.datetime.now(

        datetime.timezone.utc

    ).isoformat()


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
                {}
            )

        )


        metadata.update({

            "source": path.name,

            "section": metadata.get(

                "section",

                "General Overview"

            ),

            "content_hash": document_hash,

            "ingestion_time": timestamp,

            "scheme_name": metadata.get(

                "scheme_name",

                path.stem
                .replace("_", " ")
                .replace("-", " ")
                .title()

            ),

        })


        records.append({

            "id": chunk_id,

            "text": chunk.get(
                "text",
                ""
            ),

            "metadata": metadata,

        })


    # -----------------------------------------------------
    # CREATE EMBEDDINGS
    # -----------------------------------------------------

    texts = [

        record["text"]

        for record in records

        if record["text"].strip()

    ]


    if not texts:

        raise HTTPException(

            status_code=422,

            detail="No valid chunks found."

        )


    embeddings = embedding_service.embed_texts(
        texts
    )


    # -----------------------------------------------------
    # VECTOR RECORDS
    # -----------------------------------------------------

    vector_records = []


    valid_records = [

        record

        for record in records

        if record["text"].strip()

    ]


    for record, vector in zip(

        valid_records,

        embeddings

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

        "Document indexed: %s | Chunks: %d",

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

        "chunks": len(valid_records),

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

@app.get("/api/documents")
@app.get("/documents")

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
# VIEW DOCUMENT
# =========================================================

@app.get("/api/documents/{filename}")
@app.get("/documents/{filename}")

def view_document(
    filename: str
):

    upload_root = UPLOAD_DIR.resolve()

    requested_file = (

        UPLOAD_DIR / filename

    ).resolve()


    if (

        upload_root not in requested_file.parents

        or not requested_file.is_file()

    ):

        raise HTTPException(

            status_code=404,

            detail="Document not found."

        )


    media_type = (

        mimetypes.guess_type(

            requested_file.name

        )[0]

        or "application/octet-stream"

    )


    return FileResponse(

        requested_file,

        media_type=media_type,

        content_disposition_type="inline",

    )


# =========================================================
# DELETE DOCUMENT
# =========================================================

@app.delete("/api/documents/{filename}")
@app.delete("/documents/{filename}")

def delete_document(
    filename: str
):

    upload_root = UPLOAD_DIR.resolve()

    requested_file = (

        UPLOAD_DIR / filename

    ).resolve()


    if (

        upload_root not in requested_file.parents

        or not requested_file.is_file()

    ):

        raise HTTPException(

            status_code=404,

            detail="Document not found."

        )


    vector_store = get_pipeline().get(
        "vector_store"
    )


    deleted_chunks = 0


    try:

        if vector_store is not None:

            records = vector_store.collection.get(

                where={

                    "source": requested_file.name

                }

            )


            record_ids = (

                records.get(
                    "ids",
                    []
                )

                if records

                else []

            )


            if record_ids:

                vector_store.collection.delete(

                    ids=record_ids

                )


                deleted_chunks = len(
                    record_ids
                )


    except Exception as error:

        logger.warning(

            "Vector deletion warning: %s",

            error,

        )


    requested_file.unlink()


    pipeline_state["retriever"] = None


    return {

        "status": "deleted",

        "filename": requested_file.name,

        "deleted_chunks": deleted_chunks,

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