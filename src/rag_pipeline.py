import os
import sys
import json
from typing import List, Dict, Any, Tuple

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from src.config import validate_environment, OPENAI_API_KEY, CHAT_MODEL, EMBED_MODEL
from src.indexing import get_embeddings_for_texts, VectorIndexer
from src.token_counter import count_tokens


def load_system_prompt() -> str:
    """Loads default RAG system prompt from prompts directory."""
    prompt_path = os.path.join("prompts", "rag_system_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return (
        "You are an AI assistant for SchemeAssist. Answer the user's query accurately and concisely "
        "using ONLY the provided grounded context documents. Cite your source documents where applicable."
    )


# =====================================================================
# STAGE 1: QUERY EMBEDDING
# =====================================================================
def embed_query(query: str, embed_model: str = EMBED_MODEL) -> List[float]:
    """
    Stage 1 - Query Embedding:
    Converts a user search query into a dense 1536-dimensional embedding vector.
    """
    if not query or not query.strip():
        raise ValueError("Query string cannot be empty.")
    
    embeddings = get_embeddings_for_texts([query], embed_model=embed_model)
    return embeddings[0]


# =====================================================================
# STAGE 2: VECTOR RETRIEVAL
# =====================================================================
def retrieve_chunks(
    query: str,
    top_k: int = 3,
    db_dir: str = "data/chroma_db",
    collection_name: str = "scheme_assist_corpus"
) -> List[Dict[str, Any]]:
    """
    Stage 2 - Vector Retrieval:
    Embeds the user query and searches the ChromaDB vector collection for top_k
    semantically relevant document chunks with source metadata.
    """
    query_vector = embed_query(query)
    
    if not os.path.exists(db_dir):
        print(f"[RAG PIPELINE WARNING] Vector DB directory '{db_dir}' not found. Initializing empty collection.")
        os.makedirs(db_dir, exist_ok=True)

    client = chromadb.PersistentClient(path=db_dir)
    collection = client.get_or_create_collection(name=collection_name)
    
    total_in_db = collection.count()
    if total_in_db == 0:
        # Auto-index if collection is empty
        print("[RAG PIPELINE LOG] Vector collection is empty. Running indexer auto-population...")
        from src.indexing import run_indexing_pipeline
        run_indexing_pipeline()

    # Perform vector similarity query
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=min(top_k, max(1, total_in_db)),
        include=["documents", "metadatas", "distances"]
    )

    retrieved_chunks = []
    if results and results.get("ids") and len(results["ids"][0]) > 0:
        ids = results["ids"][0]
        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)

        for i in range(len(ids)):
            retrieved_chunks.append({
                "id": ids[i],
                "text": documents[i],
                "metadata": metadatas[i],
                "distance": float(distances[i])
            })

    print(f"[RETRIEVAL LOG] Retrieved {len(retrieved_chunks)} relevant chunk(s) for query: '{query}'")
    return retrieved_chunks


# =====================================================================
# STAGE 3: CONTEXT ASSEMBLY
# =====================================================================
def assemble_context(
    retrieved_chunks: List[Dict[str, Any]],
    max_context_tokens: int = 1500
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Stage 3 - Context Assembly:
    Formats retrieved chunks into a clean, structured context string with explicit
    source document, section, and page attribution headers via src.context_assembly.
    """
    from src.context_assembly import assemble_augmented_prompt
    assembled = assemble_augmented_prompt(
        retrieved_chunks=retrieved_chunks,
        user_query="Context Assembly Step",
        max_context_tokens=max_context_tokens
    )
    context_str = assembled["context_str"]
    sources_summary = [
        {
            "citation_index": s["citation"].replace("[", "").replace("]", ""),
            "source": s["source"],
            "section": s["section"],
            "page": s["page"],
            "position": s["position"],
            "chunk_id": s["chunk_id"]
        }
        for s in assembled["sources"]
    ]
    print(f"[CONTEXT ASSEMBLY LOG] Assembled context from {len(sources_summary)} chunk(s) ({count_tokens(context_str)} tokens).")
    return context_str, sources_summary


# =====================================================================
# STAGE 4: ANSWER GENERATION
# =====================================================================
def generate_answer(
    query: str,
    context_str: str,
    system_prompt: str = None
) -> Dict[str, Any]:
    """
    Stage 4 - Answer Generation:
    Generates a grounded answer using only the injected context via src.generation.
    """
    from src.generation import generate_grounded_answer
    gen_result = generate_grounded_answer(
        query=query,
        context_str=context_str,
        sources=[],
        system_instructions=system_prompt if system_prompt else load_system_prompt()
    )
    
    return {
        "answer": gen_result["answer"],
        "model": CHAT_MODEL,
        "token_usage": {
            "prompt_tokens": count_tokens(context_str + query),
            "completion_tokens": count_tokens(gen_result["answer"]),
            "total_tokens": count_tokens(context_str + query + gen_result["answer"])
        },
        "execution_mode": "Grounded Generation",
        "grounded": gen_result["grounded"],
        "fallback_triggered": gen_result["fallback_triggered"],
        "citations_used": gen_result.get("citations_used", [])
    }


# =====================================================================
# END-TO-END RAG PIPELINE ORCHESTRATION
# =====================================================================
def run_rag_pipeline(query: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Executes the complete query-to-answer RAG flow end-to-end:
    1. Query Embedding
    2. Vector Retrieval
    3. Context Assembly
    4. Answer Generation
    """
    print("=" * 75)
    print("  [RAG PIPELINE] Executing End-to-End Query-to-Answer Flow")
    print("=" * 75)
    print(f"[USER QUERY]: '{query}'")

    validate_environment()

    # Stage 1 & 2: Embed & Retrieve
    retrieved_chunks = retrieve_chunks(query, top_k=top_k)

    # Stage 3: Assemble Context
    context_str, sources_summary = assemble_context(retrieved_chunks)

    # Stage 4: Generate Answer
    generation_result = generate_answer(query, context_str)

    pipeline_result = {
        "query": query,
        "answer": generation_result["answer"],
        "sources": sources_summary,
        "retrieved_chunks": retrieved_chunks,
        "assembled_context": context_str,
        "generation_details": generation_result
    }

    # Automatically log summary to outputs/rag_pipeline_summary.txt
    os.makedirs("outputs", exist_ok=True)
    output_summary_path = os.path.join("outputs", "rag_pipeline_summary.txt")
    with open(output_summary_path, "w", encoding="utf-8") as f:
        f.write("=========================================================================\n")
        f.write("                SCHEMEASSIST END-TO-END RAG PIPELINE RUN                 \n")
        f.write("=========================================================================\n\n")
        f.write(f"USER QUERY:\n{query}\n\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write("1. RETRIEVED SOURCES & METADATA\n")
        f.write("-------------------------------------------------------------------------\n")
        for src in sources_summary:
            f.write(f"Source #{src['citation_index']}:\n")
            f.write(f"  - Document: {src['source']}\n")
            f.write(f"  - Section:  {src['section']}\n")
            f.write(f"  - Page:     {src['page']}\n")
            f.write(f"  - Position: {src['position']}\n\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write("2. ASSEMBLED GROUNDED CONTEXT\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write(context_str + "\n\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write("3. GENERATED ANSWER\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write(generation_result["answer"] + "\n\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write("4. EXECUTION METADATA\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write(json.dumps(generation_result, indent=2) + "\n")
        f.write("=========================================================================\n")

    return pipeline_result


if __name__ == "__main__":
    test_query = "What are the eligibility criteria and annual income limits for welfare schemes?"
    result = run_rag_pipeline(test_query, top_k=3)

    print("\n" + "=" * 75)
    print("  [GENERATED ANSWER]")
    print("=" * 75)
    print(result["answer"])
    
    print("\n" + "=" * 75)
    print("  [RETURNED SOURCES & CITATIONS]")
    print("=" * 75)
    for src in result["sources"]:
        print(f"[{src['citation_index']}] {src['source']} | Section: {src['section']} | Page: {src['page']} ({src['position']})")

    # Save summary report to outputs/rag_pipeline_summary.txt
    os.makedirs("outputs", exist_ok=True)
    output_summary_path = os.path.join("outputs", "rag_pipeline_summary.txt")
    
    with open(output_summary_path, "w", encoding="utf-8") as f:
        f.write("=========================================================================\n")
        f.write("                SCHEMEASSIST END-TO-END RAG PIPELINE RUN                 \n")
        f.write("=========================================================================\n\n")
        f.write(f"USER QUERY:\n{result['query']}\n\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write("1. RETRIEVED SOURCES & METADATA\n")
        f.write("-------------------------------------------------------------------------\n")
        for src in result["sources"]:
            f.write(f"Source #{src['citation_index']}:\n")
            f.write(f"  - Document: {src['source']}\n")
            f.write(f"  - Section:  {src['section']}\n")
            f.write(f"  - Page:     {src['page']}\n")
            f.write(f"  - Position: {src['position']}\n\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write("2. ASSEMBLED GROUNDED CONTEXT\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write(result["assembled_context"] + "\n\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write("3. GENERATED ANSWER\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write(result["answer"] + "\n\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write("4. EXECUTION METADATA\n")
        f.write("-------------------------------------------------------------------------\n")
        f.write(json.dumps(result["generation_details"], indent=2) + "\n")
        f.write("=========================================================================\n")

    print(f"\n[OUTPUT LOG] Pipeline run summary written to '{output_summary_path}'.")
    print("=" * 75)
