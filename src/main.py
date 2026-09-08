import os
import sys
import json

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import validate_environment, CHAT_MODEL
from src.ingestion import load_documents_from_data_dir, ingest_and_chunk_documents
from src.rag_pipeline import run_rag_pipeline


def load_system_prompt() -> str:
    prompt_path = os.path.join("prompts", "rag_system_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "You are an AI assistant for SchemeAssist."


def main():
    print("=" * 65)
    print("  [RAG App] SchemeAssist - End-to-End RAG Pipeline Run")
    print("=" * 65)
    
    # 1. Validate Environment & Secrets
    validate_environment()
    
    # 2. Ingest Documents & Generate Chunks
    chunks = ingest_and_chunk_documents("data", strategy="recursive")
    if not chunks:
        print("[ERROR] No chunks generated from ingested documents in data/ directory.")
        return

    # Count unique documents ingested
    unique_docs = {c.get("metadata", {}).get("source", c.get("source_doc", "unknown")) for c in chunks}
    print(f"[INGESTION LOG] Ingested {len(unique_docs)} unique doc(s) into {len(chunks)} chunk(s).")

    # 3. Load System Prompt
    system_prompt = load_system_prompt()
    print(f"[PROMPT LOG] Loaded system prompt ({len(system_prompt)} chars).")

    # 4. Perform End-to-End RAG Query & Trace Source Metadata
    test_query = "welfare schemes eligibility guidance and income limits"
    print(f"\n[QUERY]: '{test_query}'")
    
    result = run_rag_pipeline(test_query, top_k=3)
    
    print("\n--- [FINAL GENERATED RAG ANSWER] ---")
    print(result["answer"])
    
    print("\n--- [RETURNED SOURCES & CITATIONS] ---")
    for src in result["sources"]:
        print(f"[{src['citation_index']}] {src['source']} (Section: {src['section']}, Page: {src['page']})")
    
    # 5. Log verification run log for workspace compatibility
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

    print("\n" + "=" * 65)
    print("  [SUCCESS] END-TO-END RAG PIPELINE EXECUTED PASSED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    main()
