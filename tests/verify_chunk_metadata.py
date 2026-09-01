import os
import sys
import json

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion import load_and_chunk_documents
from src.retrieval import SimpleRetriever

REQUIRED_METADATA_FIELDS = {
    "source", "chunk_index", "position", "section",
    "page", "total_chunks", "char_start", "char_end"
}

def verify_chunk_metadata():
    print("=" * 75)
    print("  [VERIFICATION] Chunk Metadata & Source Tracking Verification")
    print("=" * 75)

    data_dir = "data"
    chunks = load_and_chunk_documents(data_dir)

    print(f"\n[1] Chunk Generation Check: Generated {len(chunks)} total chunks.")
    assert len(chunks) > 0, "No chunks were generated!"

    # Task 3 Check: Consistent Structure Across Corpus
    print("\n[2] Verifying Consistent Metadata Structure across all chunks...")
    for idx, chunk in enumerate(chunks):
        assert "text" in chunk, f"Chunk {idx} missing 'text' field!"
        assert "metadata" in chunk, f"Chunk {idx} missing 'metadata' field!"
        meta = chunk["metadata"]
        missing_fields = REQUIRED_METADATA_FIELDS - set(meta.keys())
        assert not missing_fields, f"Chunk {idx} ({meta.get('source')}) missing metadata fields: {missing_fields}"
        assert meta["source"], f"Chunk {idx} has empty source identifier!"
        assert isinstance(meta["chunk_index"], int), f"Chunk {idx} chunk_index must be int!"
        assert isinstance(meta["page"], int), f"Chunk {idx} page must be int!"

    print("  --> PASS: All chunks have identical, consistent metadata structure.")

    # Task 1 & 2 Check: Source Identifier & Additional Metadata
    print("\n[3] Inspection of Sample Chunks Metadata:")
    sample_file_sources = set()
    for chunk in chunks:
        sample_file_sources.add(chunk["metadata"]["source"])
    print(f"  Document Sources Represented in Chunks: {sorted(list(sample_file_sources))}")

    # Task 4 Check: Demonstrate Tracing a Retrieved Chunk to Exact Source
    print("\n[4] Demonstrating Source Traceability on Retrieval Query...")
    retriever = SimpleRetriever(chunks)
    test_query = "eligibility income criteria guidelines"
    results = retriever.search(test_query, top_k=3)

    print(f"  Search Query: '{test_query}'")
    print(f"  Retrieved Top {len(results)} Chunk(s):\n")

    for rank, chunk in enumerate(results, start=1):
        meta = chunk["metadata"]
        print(f"  Rank #{rank}:")
        print(f"    - Source Identifier: {meta['source']}")
        print(f"    - Section:          {meta['section']}")
        print(f"    - Position:         {meta['position']}")
        print(f"    - Page Number:      {meta['page']}")
        print(f"    - Char Range:       {meta['char_start']}..{meta['char_end']}")
        print(f"    - Text Preview:     \"{chunk['text'][:120]}...\"\n")

    # Task 5: Export Sample Chunks JSON
    os.makedirs("outputs", exist_ok=True)
    sample_output_path = os.path.join("outputs", "sample_chunks_metadata.json")
    with open(sample_output_path, "w", encoding="utf-8") as f:
        json.dump(chunks[:5], f, indent=2)
    print(f"[5] Saved sample chunks with metadata to '{sample_output_path}'.")

    trace_log_path = os.path.join("outputs", "chunk_traceability_demo.log")
    with open(trace_log_path, "w", encoding="utf-8") as f:
        f.write("CHUNK METADATA & SOURCE TRACKING DEMONSTRATION LOG\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Total Chunks Processed: {len(chunks)}\n")
        f.write(f"Sources Tagged: {', '.join(sorted(list(sample_file_sources)))}\n\n")
        f.write("Sample Retrieved Chunks with Traceable Metadata:\n")
        for idx, res in enumerate(results, start=1):
            f.write(f"\nResult {idx}:\n")
            f.write(json.dumps(res, indent=2))
            f.write("\n")
    print(f"[6] Saved traceability demonstration log to '{trace_log_path}'.")

    print("\n" + "=" * 75)
    print("  [SUCCESS] All Chunk Metadata & Source Tracking tasks verified successfully!")
    print("=" * 75)

if __name__ == "__main__":
    verify_chunk_metadata()
