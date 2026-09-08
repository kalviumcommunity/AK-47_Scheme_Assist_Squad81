# -*- coding: utf-8 -*-
"""
index_corpus.py - 3.31 Indexing Embeddings & Metadata Storage
=============================================================
Loads the actual SchemeAssist corpus chunk records and embeddings into the
ChromaDB vector database collection.

Core Capabilities:
  1. Record Preparation: Converts each chunk into a vector record containing
     stable ID (`{source}:{chunk_index}`), 1536-dim vector, source text, and
     structured metadata for retrieval, citation, and filtering.
  2. Batched Bulk Upsert: Inserts records in safe batches (e.g., size 10-100)
     to avoid overloading database clients or memory.
  3. Count Reconciliation: Compares stored record count against expected chunk count,
     asserting exact parity and zero batch failures.
  4. Spot-Check Integrity: Validates stored records against original source chunks,
     checking ID, text, metadata parity, and vector dimensionality.
  5. Incremental Re-indexing: Handles document updates by comparing content hashes,
     upserting modified/new chunks, deleting orphaned chunks, and leaving unchanged chunks alone.
"""

import os
import sys
import io
import json
import datetime
from typing import List, Dict, Any, Optional, Generator



# Ensure imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    VECTOR_DIMENSION,
    SIMILARITY_METRIC,
)
from src.vector_store import VectorStore
from src.embedding_quality_checks import load_or_embed_corpus


def to_vector_record(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transforms an embedded corpus chunk into a standardized vector database record.
    Ensures:
      - Stable ID: Derived from source filename and chunk index, or explicit chunk ID
      - Vector: 1536-dimensional float embedding vector
      - Text: Original chunk text
      - Metadata: Preserves document source, chunk index, section, page, token count,
                  content hash, and format for filtering and citations.
    """
    meta = chunk.get("metadata", {})
    
    # Generate stable deterministic ID if not already present
    record_id = chunk.get("id")
    if not record_id:
        source_name = meta.get("source", "doc")
        chunk_idx = meta.get("chunk_index", 0)
        record_id = f"{source_name}:{chunk_idx}"

    vector = chunk.get("embedding") or chunk.get("vector")
    if vector is None:
        raise ValueError(f"Chunk '{record_id}' is missing embedding/vector data.")

    text = chunk.get("text", chunk.get("content", ""))

    # Prepare sanitized metadata with primitive values for ChromaDB
    record_metadata = {
        "source": str(meta.get("source", "unknown")),
        "chunk_index": int(meta.get("chunk_index", 0)),
        "section": str(meta.get("section", "") or "General"),
        "page": int(meta.get("page", 1)),
        "token_count": int(meta.get("token_count", 0)),
        "content_hash": str(meta.get("content_hash", "")),
        "doc_format": str(meta.get("doc_format", "")),
    }
    if "position" in meta:
        record_metadata["position"] = str(meta["position"])
    if "category" in meta:
        record_metadata["category"] = str(meta["category"])

    return {
        "id": str(record_id),
        "vector": vector,
        "text": text,
        "metadata": record_metadata,
    }


def batches(items: List[Any], size: int = 100) -> Generator[List[Any], None, None]:
    """
    Yields successive fixed-size batches from the input list.
    Prevents client timeouts and memory exhaustion on large corpora.
    """
    if size <= 0:
        raise ValueError(f"Batch size must be > 0, got {size}")
    for start in range(0, len(items), size):
        yield items[start : start + size]


def index_corpus_embeddings(
    embedded_chunks: List[Dict[str, Any]],
    vector_store: Optional[VectorStore] = None,
    batch_size: int = 10,
    reset_first: bool = True,
) -> Dict[str, Any]:
    """
    Batch-indexes all corpus embeddings into the vector database collection.
    Tracks inserted counts, captures any failures per batch, and validates that
    indexed_count matches expected_count.
    """
    if vector_store is None:
        vector_store = VectorStore()

    if reset_first:
        print(f"[INDEX LOG] Resetting collection '{vector_store.collection_name}' for clean run...")
        vector_store.reset_collection()

    records = [to_vector_record(chunk) for chunk in embedded_chunks]
    expected_count = len(records)
    inserted = 0
    failures = []

    print(f"[INDEX LOG] Starting bulk insert of {expected_count} records (batch_size={batch_size})...")

    batch_idx = 1
    for batch in batches(records, size=batch_size):
        try:
            # ChromaDB upsert via VectorStore
            count_added = vector_store.upsert_batch(batch)
            inserted += count_added
            print(f"  • Batch {batch_idx}: Upserted {count_added} records (IDs: {batch[0]['id']} -> {batch[-1]['id']})")
        except Exception as error:
            failed_id = batch[0]["id"] if batch else "unknown"
            print(f"  [ERROR] Batch {batch_idx} failed starting at ID '{failed_id}': {error}")
            failures.append({
                "batch_index": batch_idx,
                "batch_start_id": failed_id,
                "batch_size": len(batch),
                "error": str(error),
            })
        batch_idx += 1

    indexed_count = vector_store.count()

    print("\n--- INDEXING RECONCILIATION ---")
    print(f"expected chunks: {expected_count}")
    print(f"inserted this run: {inserted}")
    print(f"indexed count: {indexed_count}")
    print(f"failures: {failures}")

    # Validation assertion specified in MSU 3.31
    assert indexed_count == expected_count, (
        f"indexed count ({indexed_count}) does not match chunk count ({expected_count})"
    )
    assert len(failures) == 0, f"Encountered {len(failures)} failure(s) during batch upsert."

    return {
        "expected_count": expected_count,
        "inserted_this_run": inserted,
        "indexed_count": indexed_count,
        "count_matches": (indexed_count == expected_count),
        "failures": failures,
    }


def spot_check_integrity(
    sample_chunk: Dict[str, Any],
    vector_store: VectorStore,
) -> Dict[str, Any]:
    """
    Picks a known chunk ID and reads back stored record from vector store.
    Confirms stored text, metadata, and vector length match the original source chunk.
    """
    sample_id = sample_chunk.get("id")
    if not sample_id:
        source_name = sample_chunk["metadata"]["source"]
        chunk_idx = sample_chunk["metadata"]["chunk_index"]
        sample_id = f"{source_name}:{chunk_idx}"

    stored = vector_store.get_record(sample_id)
    assert stored is not None, f"Record '{sample_id}' not found in collection!"

    # Field-level integrity assertions
    assert stored["text"] == sample_chunk["text"], (
        f"Text mismatch for chunk '{sample_id}'"
    )
    assert stored["metadata"]["source"] == sample_chunk["metadata"]["source"], (
        f"Source metadata mismatch for chunk '{sample_id}'"
    )
    assert int(stored["metadata"]["chunk_index"]) == int(sample_chunk["metadata"]["chunk_index"]), (
        f"Chunk index mismatch for chunk '{sample_id}'"
    )
    assert len(stored["vector"]) == len(sample_chunk["embedding"]), (
        f"Vector dimension mismatch for '{sample_id}': stored={len(stored['vector'])}, expected={len(sample_chunk['embedding'])}"
    )

    print(f"\n[SPOT CHECK] spot check passed: {sample_id}")
    print(f"source: {stored['metadata']['source']}")
    print(f"section: {stored['metadata'].get('section')}")
    print(f"vector dimension: {len(stored['vector'])}")
    print(f"text preview: {stored['text'][:120]}...")

    return {
        "id": sample_id,
        "status": "PASSED",
        "source": stored["metadata"]["source"],
        "section": stored["metadata"].get("section"),
        "chunk_index": stored["metadata"].get("chunk_index"),
        "vector_dim": len(stored["vector"]),
        "text_preview": stored["text"][:120],
        "metadata_snapshot": stored["metadata"],
    }


def reindex_changed_chunks(
    updated_chunks: List[Dict[str, Any]],
    vector_store: VectorStore,
    target_sources: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Demonstrates incremental re-indexing when documents change:
      1. Uses stable chunk IDs ({source}:{chunk_index}) and content hashes.
      2. Reads existing records for target documents.
      3. Skips unchanged chunks (content hash matches).
      4. Upserts changed or new chunks.
      5. Deletes obsolete chunks that no longer exist in the updated document.
    Keeps the index completely fresh without re-embedding or rebuilding the whole database.
    """
    records = [to_vector_record(c) for c in updated_chunks]
    updated_map = {r["id"]: r for r in records}
    
    # Identify target document sources
    if not target_sources:
        target_sources = list(set(r["metadata"]["source"] for r in records))

    unchanged_ids = []
    upserted_ids = []
    deleted_ids = []

    # Check each record against stored version
    for r_id, record in updated_map.items():
        existing = vector_store.get_record(r_id)
        if existing:
            # Check content hash
            existing_hash = existing.get("metadata", {}).get("content_hash", "")
            new_hash = record["metadata"].get("content_hash", "")
            if existing_hash and new_hash and existing_hash == new_hash:
                unchanged_ids.append(r_id)
                continue

        # Needs upsert
        vector_store.upsert_record(
            record_id=record["id"],
            vector=record["vector"],
            text=record["text"],
            metadata=record["metadata"],
        )
        upserted_ids.append(r_id)

    # Check for deleted chunks in target documents (e.g. if document shrank from 5 chunks to 3)
    # ChromaDB query by source
    for source in target_sources:
        stored_source_docs = vector_store.collection.get(
            where={"source": source},
            include=["metadatas"]
        )
        if stored_source_docs and stored_source_docs.get("ids"):
            for s_id in stored_source_docs["ids"]:
                if s_id not in updated_map:
                    vector_store.delete_record(s_id)
                    deleted_ids.append(s_id)

    print(f"\n[INCREMENTAL REINDEX] Unchanged: {len(unchanged_ids)}, Upserted: {len(upserted_ids)}, Deleted: {len(deleted_ids)}")
    return {
        "unchanged_chunks": unchanged_ids,
        "upserted_chunks": upserted_ids,
        "deleted_chunks": deleted_ids,
        "total_active_count": vector_store.count(),
    }


def run_full_indexing_pipeline(
    cache_path: str = "outputs/embedded_corpus_chunks.json",
    batch_size: int = 10,
    output_json: str = "outputs/indexing_summary.json",
    output_txt: str = "outputs/indexing_summary.txt",
) -> Dict[str, Any]:
    """
    Orchestrates Task 1 to Task 5:
      1. Loads corpus chunks (and assigns stable IDs)
      2. Initializes VectorStore
      3. Bulk indexes in batches
      4. Validates count parity
      5. Performs spot-check integrity on multiple samples
      6. Writes comprehensive indexing summaries (JSON and TXT)
    """
    print("=" * 80)
    print("  SCHEMEASSIST: 3.31 INDEXING EMBEDDINGS & METADATA STORAGE")
    print("=" * 80)

    # Load embedded corpus chunks
    chunks = load_or_embed_corpus(cache_path=cache_path)
    print(f"[PIPELINE LOG] Loaded {len(chunks)} embedded chunk(s) from '{cache_path}'.")

    # Ensure stable IDs in memory and in JSON cache
    cache_modified = False
    for c in chunks:
        expected_id = f"{c['metadata']['source']}:{c['metadata']['chunk_index']}"
        if c.get("id") != expected_id:
            c["id"] = expected_id
            cache_modified = True

    if cache_modified and os.path.exists(cache_path):
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        print(f"[PIPELINE LOG] Synchronized stable IDs back to '{cache_path}'.")

    # Initialize VectorStore (persistent ChromaDB store)
    vector_store = VectorStore(
        persist_dir=CHROMA_PERSIST_DIR,
        collection_name=COLLECTION_NAME,
        dimension=VECTOR_DIMENSION,
        metric=SIMILARITY_METRIC,
    )

    # Task 1, 2, 3: Bulk insert, metadata storage, and count verification
    indexing_result = index_corpus_embeddings(
        embedded_chunks=chunks,
        vector_store=vector_store,
        batch_size=batch_size,
        reset_first=True,
    )

    # Task 4: Spot check multiple records across different documents
    spot_checks = []
    # Spot check 1: First chunk (Ayushman Bharat)
    sc1 = spot_check_integrity(chunks[0], vector_store)
    spot_checks.append(sc1)

    # Spot check 2: Middle chunk (from a different document if available)
    if len(chunks) > 5:
        mid_idx = len(chunks) // 2
        sc2 = spot_check_integrity(chunks[mid_idx], vector_store)
        spot_checks.append(sc2)

    # Spot check 3: Last chunk
    if len(chunks) > 1:
        sc3 = spot_check_integrity(chunks[-1], vector_store)
        spot_checks.append(sc3)

    # Summary payload
    summary = {
        "milestone": "3.31 Indexing Embeddings & Metadata Storage",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "vector_database": {
            "type": "ChromaDB (Persistent)",
            "persist_directory": CHROMA_PERSIST_DIR,
            "collection_name": COLLECTION_NAME,
            "dimension": VECTOR_DIMENSION,
            "similarity_metric": SIMILARITY_METRIC,
        },
        "reconciliation": {
            "expected_chunks": indexing_result["expected_count"],
            "inserted_this_run": indexing_result["inserted_this_run"],
            "indexed_count": indexing_result["indexed_count"],
            "count_matches": indexing_result["count_matches"],
            "failures": indexing_result["failures"],
        },
        "batch_configuration": {
            "batch_size": batch_size,
            "total_batches": (len(chunks) + batch_size - 1) // batch_size,
        },
        "spot_checks": spot_checks,
        "indexed_sources_breakdown": {},
    }

    # Count breakdown by source
    for c in chunks:
        src = c["metadata"]["source"]
        summary["indexed_sources_breakdown"][src] = (
            summary["indexed_sources_breakdown"].get(src, 0) + 1
        )

    # Task 5: Write indexing summary to JSON and TXT
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\n[REPORT] Saved structured summary -> '{output_json}'")

    # Generate readable text report
    lines = [
        "=" * 80,
        "  SCHEMEASSIST: 3.31 INDEXING EMBEDDINGS & METADATA STORAGE SUMMARY",
        "=" * 80,
        f"Timestamp          : {summary['timestamp']}",
        f"Vector DB Engine   : {summary['vector_database']['type']}",
        f"Persist Directory  : {summary['vector_database']['persist_directory']}",
        f"Collection Name    : {summary['vector_database']['collection_name']}",
        f"Vector Dimension   : {summary['vector_database']['dimension']}",
        f"Similarity Metric  : {summary['vector_database']['similarity_metric']}",
        "",
        "--- RECONCILIATION & COUNT VALIDATION ---",
        f"Expected Chunks    : {summary['reconciliation']['expected_chunks']}",
        f"Inserted This Run  : {summary['reconciliation']['inserted_this_run']}",
        f"Indexed DB Count   : {summary['reconciliation']['indexed_count']}",
        f"Count Match Status : {'MATCHED (PASS)' if summary['reconciliation']['count_matches'] else 'MISMATCH (FAIL)'}",
        f"Batch Failures     : {len(summary['reconciliation']['failures'])}",
        "",
        "--- SOURCES BREAKDOWN ---",
    ]
    for src, cnt in summary["indexed_sources_breakdown"].items():
        lines.append(f"  • {src:<36} : {cnt} chunks")

    lines.extend([
        "",
        "--- INTEGRITY SPOT CHECKS ---",
    ])
    for idx, sc in enumerate(spot_checks, 1):
        lines.extend([
            f"[Check {idx}] ID: {sc['id']}",
            f"  Status        : {sc['status']}",
            f"  Source Doc    : {sc['source']}",
            f"  Section       : {sc['section']}",
            f"  Chunk Index   : {sc['chunk_index']}",
            f"  Vector Dim    : {sc['vector_dim']}",
            f"  Text Preview  : {sc['text_preview']}...",
            "",
        ])

    lines.extend([
        "--- RE-INDEXING ON DOCUMENT CHANGE EXPLANATION ---",
        "When documents change:",
        "1. Chunks use stable IDs: {source}:{chunk_index}",
        "2. Content hashes (SHA-256) track whether chunk text has changed.",
        "3. Changed chunks are upserted with fresh embeddings.",
        "4. Unchanged chunks remain untouched, avoiding expensive re-embedding.",
        "5. Orphaned/removed chunks are pruned via delete_record(chunk_id).",
        "=" * 80,
    ])

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[REPORT] Saved human-readable summary -> '{output_txt}'")

    return summary


if __name__ == "__main__":
    run_full_indexing_pipeline()
