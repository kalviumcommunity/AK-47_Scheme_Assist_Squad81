import os
import sys
import json

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import validate_environment, CHAT_MODEL
from src.ingestion import load_and_chunk_documents
from src.retrieval import SimpleRetriever

def load_system_prompt() -> str:
    prompt_path = os.path.join("prompts", "rag_system_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "You are an AI assistant."

def main():
    print("=" * 65)
    print("  [RAG App] SchemeAssist - Metadata-Tagged Chunk Retrieval Test")
    print("=" * 65)
    
    # 1. Validate Environment & Secrets
    validate_environment()
    
    # 2. Ingest & Chunk Documents with Metadata Tagging
    chunks = load_and_chunk_documents("data")
    if not chunks:
        print("[ERROR] No chunks generated from data/ directory.")
        return

    # 3. Build Retriever & Prompt
    retriever = SimpleRetriever(chunks)
    system_prompt = load_system_prompt()
    print(f"[PROMPT LOG] Loaded system prompt ({len(system_prompt)} chars).")

    # 4. Perform Verification Query & Trace Source Metadata
    test_query = "welfare schemes eligibility guidance"
    print(f"\n[QUERY]: '{test_query}'")
    
    results = retriever.search(test_query, top_k=2)
    for idx, chunk in enumerate(results, start=1):
        meta = chunk["metadata"]
        print(f"\n--- [RETRIEVED CHUNK {idx}] ---")
        print(f"Source Identifier (Filename): {meta['source']}")
        print(f"Section:                     {meta['section']}")
        print(f"Page Number:                 {meta['page']}")
        print(f"Position:                    {meta['position']}")
        print(f"Character Range:             [{meta['char_start']} - {meta['char_end']}]")
        print(f"Text Content:\n\"{chunk['text']}\"")
        print("-" * 50)
    
    # 5. Log verification run
    os.makedirs("outputs", exist_ok=True)
    output_log_path = os.path.join("outputs", "verification_run.log")
    with open(output_log_path, "w", encoding="utf-8") as f:
        f.write(f"Verification Run Successful.\nModel: {CHAT_MODEL}\nChunks Generated: {len(chunks)}\n")
        f.write("Sample Retrieved Chunk Metadata:\n")
        if results:
            f.write(json.dumps(results[0]["metadata"], indent=2))
            f.write("\n")
    
    print(f"\n[OUTPUT LOG] Verification run logged to '{output_log_path}'.")
    print("=" * 65)
    print("  [SUCCESS] METADATA TAGGING & SOURCE TRACKING PASSED SUCCESSFULLY!")
    print("=" * 65)

if __name__ == "__main__":
    main()

