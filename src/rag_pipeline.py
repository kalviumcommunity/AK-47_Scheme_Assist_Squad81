import os
import sys
import json
from typing import List, Dict, Any, Tuple

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb

# Gemini configuration
from src.config import (
    validate_environment,
    GEMINI_API_KEY,
    CHAT_MODEL,
    EMBED_MODEL,
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME
)

from src.indexing import get_embeddings_for_texts
from src.token_counter import count_tokens


def load_system_prompt() -> str:
    """Load the SchemeAssist RAG system prompt."""

    prompt_path = os.path.join("prompts", "rag_system_prompt.txt")

    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    return """
You are SchemeAssist, an AI assistant for government welfare schemes.

Answer the user's question using ONLY the retrieved context provided to you.

Rules:
1. Do not invent scheme information.
2. Do not use mock data.
3. If the answer is not available in the context, clearly say so.
4. Provide accurate eligibility information when available.
5. Mention benefits when available.
6. Explain application steps when available.
7. Mention required documents when available.
8. Reference the source documents used.
9. Keep answers clear and easy to understand.
"""


# ============================================================
# STAGE 1: QUERY EMBEDDING
# ============================================================

def embed_query(
    query: str,
    embed_model: str = EMBED_MODEL
) -> List[float]:
    """
    Convert user query into Gemini embedding vector.
    """

    if not query or not query.strip():
        raise ValueError("Query string cannot be empty.")

    embeddings = get_embeddings_for_texts(
        [query],
        embed_model=embed_model
    )

    return embeddings[0]


# ============================================================
# STAGE 2: VECTOR RETRIEVAL
# ============================================================

def retrieve_chunks(
    query: str,
    top_k: int = 3,
    db_dir: str = CHROMA_PERSIST_DIR,
    collection_name: str = COLLECTION_NAME
) -> List[Dict[str, Any]]:
    """
    Embed user query and retrieve relevant chunks from ChromaDB.
    """

    print("\n[STAGE 1] Creating Gemini query embedding...")

    query_vector = embed_query(query)

    print("[STAGE 1 SUCCESS] Query embedding generated.")

    # Create DB directory if missing
    if not os.path.exists(db_dir):

        print(
            f"[RAG WARNING] Vector DB directory "
            f"'{db_dir}' not found."
        )

        os.makedirs(
            db_dir,
            exist_ok=True
        )

    print("\n[STAGE 2] Connecting to ChromaDB...")

    client = chromadb.PersistentClient(
        path=db_dir
    )

    collection = client.get_or_create_collection(
        name=collection_name
    )

    total_in_db = collection.count()

    print(
        f"[VECTOR DB] Collection: {collection_name}"
    )

    print(
        f"[VECTOR DB] Indexed chunks: {total_in_db}"
    )

    # Auto indexing if empty
    if total_in_db == 0:

        print(
            "\n[RAG PIPELINE] Vector collection is empty."
        )

        print(
            "[RAG PIPELINE] Starting automatic indexing..."
        )

        from src.indexing import run_indexing_pipeline

        run_indexing_pipeline()

        # Reconnect after indexing
        client = chromadb.PersistentClient(
            path=db_dir
        )

        collection = client.get_or_create_collection(
            name=collection_name
        )

        total_in_db = collection.count()

        print(
            f"[VECTOR DB] Indexed chunks after indexing: "
            f"{total_in_db}"
        )

    # No data available
    if total_in_db == 0:

        print(
            "[RAG WARNING] No documents available "
            "in vector database."
        )

        return []

    # Determine safe number of results
    results_count = min(
        top_k,
        total_in_db
    )

    print(
        f"\n[STAGE 2] Retrieving top "
        f"{results_count} relevant chunks..."
    )

    results = collection.query(

        query_embeddings=[
            query_vector
        ],

        n_results=results_count,

        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_chunks = []

    if (
        results
        and results.get("ids")
        and len(results["ids"]) > 0
        and len(results["ids"][0]) > 0
    ):

        ids = results["ids"][0]

        documents = results["documents"][0]

        metadatas = results["metadatas"][0]

        distances = (
            results["distances"][0]
            if results.get("distances")
            else [0.0] * len(ids)
        )

        for i in range(len(ids)):

            retrieved_chunks.append({

                "id": ids[i],

                "text": documents[i],

                "metadata": metadatas[i] or {},

                "distance": float(
                    distances[i]
                )

            })

    print(
        f"[RETRIEVAL SUCCESS] Retrieved "
        f"{len(retrieved_chunks)} chunk(s)."
    )

    return retrieved_chunks


# ============================================================
# STAGE 3: CONTEXT ASSEMBLY
# ============================================================

def assemble_context(
    retrieved_chunks: List[Dict[str, Any]],
    max_context_tokens: int = 1500
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Assemble retrieved chunks into grounded context.
    """

    print(
        "\n[STAGE 3] Assembling retrieved context..."
    )

    if not retrieved_chunks:

        return (
            "",
            []
        )

    from src.context_assembly import (
        assemble_augmented_prompt
    )

    assembled = assemble_augmented_prompt(

        retrieved_chunks=retrieved_chunks,

        user_query="SchemeAssist RAG Query",

        max_context_tokens=max_context_tokens

    )

    context_str = assembled.get(
        "context_str",
        ""
    )

    sources_summary = []

    for source in assembled.get(
        "sources",
        []
    ):

        citation = source.get(
            "citation",
            ""
        )

        sources_summary.append({

            "citation_index": (
                citation
                .replace("[", "")
                .replace("]", "")
            ),

            "source": source.get(
                "source",
                "Unknown Document"
            ),

            "section": source.get(
                "section",
                "General Overview"
            ),

            "page": source.get(
                "page",
                1
            ),

            "position": source.get(
                "position",
                ""
            ),

            "chunk_id": source.get(
                "chunk_id",
                ""
            )

        })

    print(
        f"[CONTEXT SUCCESS] "
        f"Assembled {len(sources_summary)} source(s)."
    )

    print(
        f"[CONTEXT TOKENS] "
        f"{count_tokens(context_str)} tokens."
    )

    return (
        context_str,
        sources_summary
    )


# ============================================================
# STAGE 4: GEMINI ANSWER GENERATION
# ============================================================

def generate_answer(
    query: str,
    context_str: str,
    system_prompt: str = None
) -> Dict[str, Any]:
    """
    Generate grounded answer using Gemini API.
    """

    print(
        "\n[STAGE 4] Generating answer using Gemini..."
    )

    if not GEMINI_API_KEY:

        raise ValueError(
            "GEMINI_API_KEY is not configured. "
            "Please add it to your .env file."
        )

    if not context_str.strip():

        return {

            "answer": (
                "I could not find enough relevant "
                "information in the uploaded scheme "
                "documents to answer this question."
            ),

            "model": CHAT_MODEL,

            "token_usage": {

                "prompt_tokens": count_tokens(query),

                "completion_tokens": 0,

                "total_tokens": count_tokens(query)

            },

            "execution_mode": "No Context",

            "grounded": False,

            "fallback_triggered": True,

            "citations_used": []

        }

    from src.generation import (
        generate_grounded_answer
    )

    gen_result = generate_grounded_answer(

        query=query,

        context_str=context_str,

        sources=[],

        system_instructions=(
            system_prompt
            if system_prompt
            else load_system_prompt()
        )

    )

    answer = gen_result.get(
        "answer",
        ""
    )

    print(
        "[GENERATION SUCCESS] Gemini response generated."
    )

    return {

        "answer": answer,

        "model": CHAT_MODEL,

        "token_usage": {

            "prompt_tokens": count_tokens(
                context_str + query
            ),

            "completion_tokens": count_tokens(
                answer
            ),

            "total_tokens": count_tokens(
                context_str + query + answer
            )

        },

        "execution_mode": (
            "Gemini Grounded Generation"
        ),

        "grounded": gen_result.get(
            "grounded",
            True
        ),

        "fallback_triggered": gen_result.get(
            "fallback_triggered",
            False
        ),

        "citations_used": gen_result.get(
            "citations_used",
            []
        )

    }


# ============================================================
# END-TO-END RAG PIPELINE
# ============================================================

def run_rag_pipeline(
    query: str,
    top_k: int = 3
) -> Dict[str, Any]:
    """
    Complete SchemeAssist RAG pipeline.

    Flow:

    User Question
        ↓
    Gemini Embedding
        ↓
    ChromaDB Retrieval
        ↓
    Context Assembly
        ↓
    Gemini Generation
        ↓
    Answer + Sources
    """

    print("\n")

    print("=" * 75)

    print(
        " SCHEMEASSIST - END-TO-END GEMINI RAG PIPELINE"
    )

    print("=" * 75)

    print(
        f"\n[USER QUERY]: {query}"
    )

    # Validate configuration
    validate_environment()

    # ----------------------------------------
    # Stage 1 & 2
    # ----------------------------------------

    retrieved_chunks = retrieve_chunks(

        query=query,

        top_k=top_k

    )

    # ----------------------------------------
    # Stage 3
    # ----------------------------------------

    context_str, sources_summary = assemble_context(

        retrieved_chunks

    )

    # ----------------------------------------
    # Stage 4
    # ----------------------------------------

    generation_result = generate_answer(

        query=query,

        context_str=context_str

    )

    # ----------------------------------------
    # Final Result
    # ----------------------------------------

    pipeline_result = {

        "query": query,

        "answer": generation_result[
            "answer"
        ],

        "sources": sources_summary,

        "retrieved_chunks": retrieved_chunks,

        "assembled_context": context_str,

        "generation_details": generation_result

    }

    # ----------------------------------------
    # Save Pipeline Report
    # ----------------------------------------

    save_pipeline_report(
        pipeline_result
    )

    print("\n")

    print("=" * 75)

    print(
        " RAG PIPELINE COMPLETED SUCCESSFULLY"
    )

    print("=" * 75)

    return pipeline_result


# ============================================================
# SAVE PIPELINE REPORT
# ============================================================

def save_pipeline_report(
    result: Dict[str, Any]
):

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    output_summary_path = os.path.join(

        "outputs",

        "rag_pipeline_summary.txt"

    )

    with open(

        output_summary_path,

        "w",

        encoding="utf-8"

    ) as f:

        f.write(
            "=" * 75 + "\n"
        )

        f.write(
            "SCHEMEASSIST END-TO-END GEMINI RAG PIPELINE\n"
        )

        f.write(
            "=" * 75 + "\n\n"
        )

        # Query

        f.write(
            "USER QUERY:\n"
        )

        f.write(
            result["query"] + "\n\n"
        )

        # Sources

        f.write(
            "-" * 75 + "\n"
        )

        f.write(
            "1. RETRIEVED SOURCES\n"
        )

        f.write(
            "-" * 75 + "\n"
        )

        if result["sources"]:

            for src in result["sources"]:

                f.write(

                    f"Source "
                    f"#{src['citation_index']}:\n"

                )

                f.write(

                    f"  Document: "
                    f"{src['source']}\n"

                )

                f.write(

                    f"  Section: "
                    f"{src['section']}\n"

                )

                f.write(

                    f"  Page: "
                    f"{src['page']}\n"

                )

                f.write(

                    f"  Position: "
                    f"{src['position']}\n\n"

                )

        else:

            f.write(
                "No relevant sources found.\n\n"
            )

        # Context

        f.write(
            "-" * 75 + "\n"
        )

        f.write(
            "2. ASSEMBLED CONTEXT\n"
        )

        f.write(
            "-" * 75 + "\n"
        )

        f.write(

            result["assembled_context"]

            + "\n\n"

        )

        # Answer

        f.write(
            "-" * 75 + "\n"
        )

        f.write(
            "3. GEMINI GENERATED ANSWER\n"
        )

        f.write(
            "-" * 75 + "\n"
        )

        f.write(

            result["answer"]

            + "\n\n"

        )

        # Metadata

        f.write(
            "-" * 75 + "\n"
        )

        f.write(
            "4. EXECUTION METADATA\n"
        )

        f.write(
            "-" * 75 + "\n"
        )

        f.write(

            json.dumps(

                result["generation_details"],

                indent=2

            )

        )

        f.write("\n")

        f.write(
            "=" * 75
        )

    print(

        f"\n[OUTPUT LOG] Pipeline summary saved to: "

        f"{output_summary_path}"

    )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    test_query = (
        "What are the eligibility criteria "
        "and annual income limits for welfare schemes?"
    )

    result = run_rag_pipeline(

        test_query,

        top_k=3

    )

    print("\n")

    print("=" * 75)

    print(
        " GENERATED ANSWER"
    )

    print("=" * 75)

    print(
        result["answer"]
    )

    print("\n")

    print("=" * 75)

    print(
        " RETURNED SOURCES"
    )

    print("=" * 75)

    for src in result["sources"]:

        print(

            f"[{src['citation_index']}] "

            f"{src['source']} "

            f"| Section: {src['section']} "

            f"| Page: {src['page']}"

        )