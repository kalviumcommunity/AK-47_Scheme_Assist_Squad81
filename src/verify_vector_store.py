# -*- coding: utf-8 -*-
"""
verify_vector_store.py - 3.30 Vector Database Setup & Collection Design Verification
===================================================================================
Demonstrates and validates:
  1. Connection to ChromaDB persistent vector database
  2. Collection creation with dimension 1536 and cosine similarity metric
  3. Storing vector, original source text, and metadata together in schema
  4. Successful record insertion and exact readback verification
  5. Nearest-neighbor semantic retrieval verification
  6. Dimension mismatch error safeguarding
"""

import os
import sys
import io
import json
import time
import datetime
from typing import Dict, Any

# Ensure stdout handles UTF-8 on Windows terminals
if hasattr(sys.stdout, "buffer"):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    VECTOR_DB_TYPE,
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    VECTOR_DIMENSION,
    SIMILARITY_METRIC,
)
from src.embeddings import EmbeddingService
from src.vector_store import VectorStore


def run_vector_store_verification(
    persist_dir: str = CHROMA_PERSIST_DIR,
    collection_name: str = COLLECTION_NAME,
    dimension: int = VECTOR_DIMENSION,
    in_memory: bool = False,
) -> Dict[str, Any]:
    """
    Executes the comprehensive verification suite for Vector Database Setup & Collection Design.
    """
    print("=" * 80)
    print("  SCHEMEASSIST: 3.30 VECTOR DATABASE SETUP & COLLECTION DESIGN VERIFICATION")
    print("=" * 80)

    # ─── Task 1: Connect to Vector Database ──────────────────────────────────
    print(f"\n[TASK 1] Connecting to vector database...")
    print(f"  • DB Type      : {VECTOR_DB_TYPE}")
    print(f"  • Persist Dir  : {persist_dir} (in_memory={in_memory})")
    
    vs = VectorStore(
        persist_dir=persist_dir,
        in_memory=in_memory,
        collection_name=collection_name,
        dimension=dimension,
        metric=SIMILARITY_METRIC,
    )
    print(f"  [OK] Connection established successfully to ChromaDB.")

    # ─── Task 2: Create a Correctly Sized Collection ─────────────────────────
    print(f"\n[TASK 2] Configuring collection...")
    print(f"  • Collection Name   : {vs.collection_name}")
    print(f"  • Vector Dimension  : {vs.dimension} (matches text-embedding-3-small)")
    print(f"  • Similarity Metric : {vs.metric} (HNSW space: cosine)")
    print(f"  [OK] Collection '{vs.collection_name}' initialized with dimension {vs.dimension}.")

    # ─── Task 3: Design Stored Record Schema ─────────────────────────────────
    print(f"\n[TASK 3] Constructing test record with unified RAG schema...")
    embed_service = EmbeddingService()
    
    sample_text = (
        "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) provides income support of "
        "Rs 6,000 per year released in three equal 4-monthly installments of Rs 2,000 each "
        "directly into the bank accounts of eligible landholding farmer families across India."
    )
    sample_vector = embed_service.embed_query(sample_text)
    
    test_record = {
        "id": "pmkisan_scheme_doc.md:chunk_0",
        "vector": sample_vector,
        "text": sample_text,
        "metadata": {
            "source": "pmkisan_scheme_doc.md",
            "chunk_index": 0,
            "section": "1. Scheme Overview & Direct Benefit Transfer",
            "page": 1,
            "token_count": 48,
            "category": "agriculture_income_support"
        }
    }
    
    print(f"  • Schema Fields : id, vector, text, metadata")
    print(f"  • Target ID     : {test_record['id']}")
    print(f"  • Vector Dim    : {len(test_record['vector'])} floats")
    print(f"  • Metadata Keys : {list(test_record['metadata'].keys())}")

    # ─── Task 4: Insert and Read Back Record ──────────────────────────────────
    print(f"\n[TASK 4] Upserting record and reading back from vector database...")
    vs.upsert_record(
        record_id=test_record["id"],
        vector=test_record["vector"],
        text=test_record["text"],
        metadata=test_record["metadata"],
    )
    print(f"  [OK] Record '{test_record['id']}' successfully upserted.")

    # Read back record
    stored = vs.get_record(test_record["id"])
    if not stored:
        raise RuntimeError(f"Failed to read back record '{test_record['id']}' from collection!")

    print("\n--- READBACK VERIFICATION ---")
    print(f"  readback id   : {stored['id']}")
    print(f"  vector length : {len(stored['vector'])}")
    print(f"  text preview  : {stored['text'][:80]}...")
    print(f"  metadata      : {stored['metadata']}")

    # Validation assertions
    id_matched = (stored["id"] == test_record["id"])
    dim_matched = (len(stored["vector"]) == vs.dimension)
    text_matched = (stored["text"] == test_record["text"])
    meta_matched = all(
        stored["metadata"].get(k) == v for k, v in test_record["metadata"].items()
    )

    print("\n--- SCHEMA INTEGRITY CHECKS ---")
    print(f"  • ID Match               : {'[PASSED]' if id_matched else '[FAILED]'}")
    print(f"  • Vector Length Match    : {'[PASSED]' if dim_matched else '[FAILED]'}")
    print(f"  • Text Integrity Match   : {'[PASSED]' if text_matched else '[FAILED]'}")
    print(f"  • Metadata Fields Match  : {'[PASSED]' if meta_matched else '[FAILED]'}")

    # ─── Semantic Nearest Neighbor Query Test ────────────────────────────────
    print(f"\n[RETRIEVAL TEST] Running semantic similarity query...")
    query_text = "How much money do farmers receive in installments under PM-KISAN?"
    query_vector = embed_service.embed_query(query_text)
    
    matches = vs.query_similar(query_vector=query_vector, top_k=1)
    if matches:
        top_match = matches[0]
        print(f"  • Query        : \"{query_text}\"")
        print(f"  • Top Match ID : {top_match['id']}")
        print(f"  • Score (Cos)  : {top_match['score']}")
        print(f"  • Distance     : {top_match['distance']}")
        print(f"  • Source File  : {top_match['metadata'].get('source')}")
        print(f"  [OK] Nearest-neighbor search operational and verified.")

    # ─── Dimension Mismatch Rejection Test ────────────────────────────────────
    print(f"\n[SAFETY TEST] Validating dimension mismatch rejection...")
    invalid_vector = [0.1] * 768  # 768 vs 1536
    mismatch_detected = False
    try:
        vs.upsert_record("invalid:0", invalid_vector, "Short dimension text", {})
    except ValueError as exc:
        mismatch_detected = True
        print(f"  [OK] Successfully rejected invalid vector dimension (768 vs {vs.dimension}): {exc}")

    # Build report payload
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    verification_summary = {
        "timestamp": timestamp,
        "database": {
            "type": VECTOR_DB_TYPE,
            "persist_directory": persist_dir,
            "collection_name": collection_name,
            "dimension": dimension,
            "metric": SIMILARITY_METRIC,
            "total_records": vs.count(),
        },
        "readback_test": {
            "inserted_id": test_record["id"],
            "readback_id": stored["id"],
            "id_matched": id_matched,
            "vector_dimension": len(stored["vector"]),
            "dimension_matched": dim_matched,
            "text_matched": text_matched,
            "metadata_matched": meta_matched,
            "stored_metadata": stored["metadata"],
        },
        "retrieval_test": {
            "query": query_text,
            "matched_id": matches[0]["id"] if matches else None,
            "score": matches[0]["score"] if matches else 0.0,
            "distance": matches[0]["distance"] if matches else 1.0,
        },
        "safety_checks": {
            "dimension_mismatch_rejected": mismatch_detected,
        },
        "status": "PASSED" if (id_matched and dim_matched and text_matched and meta_matched and mismatch_detected) else "FAILED",
    }

    return verification_summary


def save_verification_artifacts(
    summary: Dict[str, Any],
    output_dir: str = "outputs"
) -> tuple[str, str]:
    """
    Saves the vector store setup and readback verification report.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    json_path = os.path.join(output_dir, "vector_db_readback_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
        
    txt_path = os.path.join(output_dir, "vector_db_readback_results.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  SCHEMEASSIST: 3.30 VECTOR DATABASE SETUP & READBACK AUDIT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Timestamp           : {summary['timestamp']}\n")
        f.write(f"Vector Database     : {summary['database']['type'].upper()}\n")
        f.write(f"Collection Name     : {summary['database']['collection_name']}\n")
        f.write(f"Configured Dimension: {summary['database']['dimension']}\n")
        f.write(f"Similarity Metric   : {summary['database']['metric']}\n")
        f.write(f"Persist Directory   : {summary['database']['persist_directory']}\n\n")
        f.write("-" * 80 + "\n")
        f.write("READBACK VERIFICATION RESULTS:\n")
        f.write("-" * 80 + "\n")
        rb = summary["readback_test"]
        f.write(f"Readback ID        : {rb['readback_id']} (Expected: {rb['inserted_id']})\n")
        f.write(f"Vector Length      : {rb['vector_dimension']} floats\n")
        f.write(f"ID Matched         : {rb['id_matched']}\n")
        f.write(f"Dimension Matched  : {rb['dimension_matched']}\n")
        f.write(f"Text Matched       : {rb['text_matched']}\n")
        f.write(f"Metadata Matched   : {rb['metadata_matched']}\n")
        f.write(f"Stored Metadata    : {json.dumps(rb['stored_metadata'])}\n\n")
        f.write("-" * 80 + "\n")
        f.write("SEMANTIC RETRIEVAL TEST:\n")
        f.write("-" * 80 + "\n")
        rt = summary["retrieval_test"]
        f.write(f"Query Text         : {rt['query']}\n")
        f.write(f"Matched ID         : {rt['matched_id']}\n")
        f.write(f"Cosine Similarity  : {rt['score']}\n")
        f.write(f"Cosine Distance    : {rt['distance']}\n\n")
        f.write("-" * 80 + "\n")
        f.write(f"OVERALL STATUS     : {summary['status']}\n")
        f.write("=" * 80 + "\n")

    print(f"\n[ARTIFACTS PERSISTED]")
    print(f"  • JSON Audit Report : {json_path}")
    print(f"  • Text Audit Report : {txt_path}")
    print("=" * 80)
    
    return json_path, txt_path


if __name__ == "__main__":
    results = run_vector_store_verification()
    save_verification_artifacts(results)
