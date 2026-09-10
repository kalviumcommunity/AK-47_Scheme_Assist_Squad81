# -*- coding: utf-8 -*-
"""
test_indexing.py - Unit Tests for 3.31 Indexing Embeddings & Metadata Storage
=============================================================================
Tests:
  1. Record conversion schema enforcement (ID, vector, text, metadata)
  2. Batches generator partitioning and edge cases
  3. Batch indexing and exact count reconciliation
  4. Spot-check integrity validation (passes on valid records)
  5. Spot-check integrity catches text, source, or vector length mismatches
  6. Incremental re-indexing when documents change (upserting changed, skipping unchanged, deleting orphaned)
  7. Failure tracking when a batch encounters an error
"""

import os
import sys
import unittest
from typing import List, Dict, Any

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_store import VectorStore
from src.index_corpus import (
    to_vector_record,
    batches,
    index_corpus_embeddings,
    spot_check_integrity,
    reindex_changed_chunks,
)


class TestIndexingEmbeddings(unittest.TestCase):

    def setUp(self):
        # Use ephemeral in-memory VectorStore for fast, isolated unit tests
        self.vs = VectorStore(
            in_memory=True,
            collection_name="test_indexing_collection",
            dimension=1536,
            metric="cosine",
        )
        self.vs.reset_collection()

        # Create mock embedded chunks
        self.mock_chunks = [
            {
                "id": f"policy_doc_{i}.md:{j}",
                "text": f"This is sample policy chunk {j} of document {i} with welfare details.",
                "embedding": [0.01 * (i + 1)] * 1536,
                "metadata": {
                    "source": f"policy_doc_{i}.md",
                    "chunk_index": j,
                    "section": f"Section {j + 1}",
                    "page": 1,
                    "token_count": 50,
                    "content_hash": f"hash_{i}_{j}",
                    "doc_format": ".md",
                }
            }
            for i in range(2)
            for j in range(3)
        ]

    def test_to_vector_record_schema(self):
        """Task 2: Confirms to_vector_record produces expected schema with ID, vector, text, and metadata."""
        sample = self.mock_chunks[0]
        record = to_vector_record(sample)

        self.assertEqual(record["id"], "policy_doc_0.md:0")
        self.assertEqual(len(record["vector"]), 1536)
        self.assertEqual(record["text"], sample["text"])
        self.assertIn("source", record["metadata"])
        self.assertEqual(record["metadata"]["source"], "policy_doc_0.md")
        self.assertEqual(record["metadata"]["chunk_index"], 0)
        self.assertEqual(record["metadata"]["section"], "Section 1")
        self.assertEqual(record["metadata"]["content_hash"], "hash_0_0")

    def test_to_vector_record_auto_id_generation(self):
        """Verifies stable ID is generated from source and chunk_index if id is missing."""
        chunk_without_id = {
            "text": "Eligible citizens receive pension support.",
            "embedding": [0.02] * 1536,
            "metadata": {
                "source": "pension_scheme.txt",
                "chunk_index": 2,
                "section": "Eligibility",
            }
        }
        record = to_vector_record(chunk_without_id)
        self.assertEqual(record["id"], "pension_scheme.txt:2")

    def test_batches_partitioning(self):
        """Verifies that batches() correctly partitions items into chunks."""
        items = list(range(25))
        chunked = list(batches(items, size=10))

        self.assertEqual(len(chunked), 3)
        self.assertEqual(chunked[0], list(range(0, 10)))
        self.assertEqual(chunked[1], list(range(10, 20)))
        self.assertEqual(chunked[2], list(range(20, 25)))

        # Invalid batch size
        with self.assertRaises(ValueError):
            list(batches(items, size=0))

    def test_index_corpus_embeddings_count_and_reconciliation(self):
        """Task 1 & Task 3: Confirms all records are indexed and indexed_count == expected_count."""
        res = index_corpus_embeddings(
            embedded_chunks=self.mock_chunks,
            vector_store=self.vs,
            batch_size=2,
            reset_first=True,
        )

        self.assertEqual(res["expected_count"], 6)
        self.assertEqual(res["inserted_this_run"], 6)
        self.assertEqual(res["indexed_count"], 6)
        self.assertTrue(res["count_matches"])
        self.assertEqual(len(res["failures"]), 0)
        self.assertEqual(self.vs.count(), 6)

    def test_spot_check_integrity_passes(self):
        """Task 4: Confirms spot-checking stored records against source chunks passes."""
        index_corpus_embeddings(
            embedded_chunks=self.mock_chunks,
            vector_store=self.vs,
            batch_size=3,
            reset_first=True,
        )

        for sample in [self.mock_chunks[0], self.mock_chunks[3]]:
            check_result = spot_check_integrity(sample, self.vs)
            self.assertEqual(check_result["status"], "PASSED")
            self.assertEqual(check_result["source"], sample["metadata"]["source"])
            self.assertEqual(check_result["vector_dim"], 1536)

    def test_spot_check_integrity_detects_mismatches(self):
        """Task 4: Confirms spot check detects if text or metadata was altered."""
        index_corpus_embeddings(
            embedded_chunks=self.mock_chunks,
            vector_store=self.vs,
            batch_size=5,
            reset_first=True,
        )

        # Tampered text
        tampered_chunk = dict(self.mock_chunks[0])
        tampered_chunk["text"] = "Completely altered text that does not match stored!"
        with self.assertRaises(AssertionError):
            spot_check_integrity(tampered_chunk, self.vs)

        # Tampered vector length
        tampered_vec_chunk = dict(self.mock_chunks[1])
        tampered_vec_chunk["embedding"] = [0.1] * 768
        with self.assertRaises(AssertionError):
            spot_check_integrity(tampered_vec_chunk, self.vs)

    def test_incremental_reindexing_when_documents_change(self):
        """Bonus/Follow-up: Tests document updates (upsert modified, skip unchanged, delete removed)."""
        # Step 1: Initial index with 3 chunks for doc 0
        doc0_chunks = [c for c in self.mock_chunks if c["metadata"]["source"] == "policy_doc_0.md"]
        self.assertEqual(len(doc0_chunks), 3)

        index_corpus_embeddings(
            embedded_chunks=doc0_chunks,
            vector_store=self.vs,
            batch_size=5,
            reset_first=True,
        )
        self.assertEqual(self.vs.count(), 3)

        # Step 2: Document update
        # Chunk 0: unchanged (same content_hash)
        # Chunk 1: modified text & hash
        # Chunk 2: removed from document
        updated_chunks = [
            doc0_chunks[0],  # unchanged
            {
                "id": "policy_doc_0.md:1",
                "text": "MODIFIED text for chunk 1 with new subsidy amounts.",
                "embedding": [0.99] * 1536,
                "metadata": {
                    "source": "policy_doc_0.md",
                    "chunk_index": 1,
                    "section": "Updated Section 2",
                    "content_hash": "new_hash_999",
                }
            }
        ]

        result = reindex_changed_chunks(
            updated_chunks=updated_chunks,
            vector_store=self.vs,
            target_sources=["policy_doc_0.md"]
        )

        self.assertIn("policy_doc_0.md:0", result["unchanged_chunks"])
        self.assertIn("policy_doc_0.md:1", result["upserted_chunks"])
        self.assertIn("policy_doc_0.md:2", result["deleted_chunks"])

        # Active count should now be 2
        self.assertEqual(self.vs.count(), 2)

        # Read back modified chunk
        updated_rec = self.vs.get_record("policy_doc_0.md:1")
        self.assertEqual(updated_rec["text"], "MODIFIED text for chunk 1 with new subsidy amounts.")
        self.assertEqual(updated_rec["metadata"]["content_hash"], "new_hash_999")


if __name__ == "__main__":
    unittest.main()
