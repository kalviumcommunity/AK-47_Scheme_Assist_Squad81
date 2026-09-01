import os
import sys

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import validate_environment, CHAT_MODEL
from src.ingestion import load_documents_from_data_dir, ingest_and_chunk_documents
from src.retrieval import SimpleRetriever


def load_system_prompt() -> str:
    prompt_path = os.path.join("prompts", "rag_system_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "You are an AI assistant."


def main():
    print("=" * 65)
    print("  [RAG App] SchemeAssist - Workspace Verification Test")
    print("=" * 65)
    
    # 1. Validate Environment & Secrets
    validate_environment()
    
    # 2. Ingest Documents & Generate Chunks
    chunks = ingest_and_chunk_documents("data", strategy="recursive")
    if not chunks:
        print("[ERROR] No chunks generated from ingested documents in data/ directory.")
        return

    # Count unique documents ingested
    unique_docs = {c.get("source_doc") for c in chunks if c.get("source_doc")}

    # 3. Build Retriever & Prompt
    retriever = SimpleRetriever(chunks)
    system_prompt = load_system_prompt()
    print(f"[PROMPT LOG] Loaded system prompt ({len(system_prompt)} chars).")

    # 4. Perform Verification Query
    test_query = "welfare schemes eligibility guidance"
    print(f"\n[QUERY]: '{test_query}'")
    
    results = retriever.search(test_query, top_k=1)
    if results:
        top_chunk = results[0]
        print(f"[RETRIEVED CHUNK]: {top_chunk.get('chunk_id', 'N/A')} (Source: {top_chunk.get('source_doc', 'N/A')})")
        print(f"[CHUNK METADATA]: Strategy: {top_chunk.get('strategy', 'N/A')} | Chars: {top_chunk.get('char_count', 'N/A')} | Score: {top_chunk.get('retrieval_score', 'N/A')}")
        print(f"[CONTENT PREVIEW]:\n{top_chunk.get('content', '')[:250]}...")
    
    # 5. Log verification run
    os.makedirs("outputs", exist_ok=True)
    output_log_path = os.path.join("outputs", "verification_run.log")
    with open(output_log_path, "w", encoding="utf-8") as f:
        f.write(
            f"Verification Run Successful.\n"
            f"Model: {CHAT_MODEL}\n"
            f"Documents Ingested: {len(unique_docs)}\n"
            f"Chunks Indexed: {len(chunks)}\n"
        )
    
    print(f"\n[OUTPUT LOG] Verification run logged to '{output_log_path}'.")
    print("=" * 65)
    print("  [SUCCESS] WORKSPACE REPRODUCIBILITY TEST PASSED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    main()
