# -*- coding: utf-8 -*-
"""
test_vector_store.py - Unit Tests for 3.30 Vector Database Setup & Collection Design
===================================================================================
Tests:
  1. VectorStore initialization and database reachability
  2. Collection creation with dimension 1536 and cosine metric
  3. Record schema compliance: ID + 1536-dim Vector + Text + Metadata
  4. Exact record readback validation
  5. Dimension mismatch enforcement (rejecting wrong dimensions)
  6. Batch insertion and count tracking
  7. Semantic nearest-neighbor retrieval
  8. Metadata filtering capability
"""

import os
import sys
import unittest

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_store import VectorStore


class TestVectorDatabaseSetup(unittest.TestCase):

    def setUp(self):
        # Use ephemeral in-memory VectorStore for fast, isolated unit tests
        self.vs = VectorStore(
            in_memory=True,
            collection_name="test_scheme_chunks",
            dimension=1536,
            metric="cosine",
        )
        self.vs.reset_collection()

    def test_client_reachability_and_initialization(self):
        """Task 1: Confirms connection is established and client is reachable."""
        self.assertIsNotNone(self.vs.client)
        self.assertIsNotNone(self.vs.collection)
        self.assertEqual(self.vs.count(), 0)

    def test_collection_configuration(self):
        """Task 2: Verifies collection dimension and metric settings."""
        self.assertEqual(self.vs.dimension, 1536)
        self.assertEqual(self.vs.metric, "cosine")
        self.assertEqual(self.vs.collection_name, "test_scheme_chunks")

    def test_insert_and_readback_record(self):
        """Task 3 & 4: Verifies inserting and reading back a complete record."""
        record_id = "housing_welfare:chunk_0"
        vector = [0.05] * 1536
        text = "Pradhan Mantri Awas Yojana provides upfront interest subsidy of 6.5% on home loans."
        metadata = {
            "source": "housing_welfare_guidelines.html",
            "chunk_index": 0,
            "section": "Subsidy & Financial Assistance",
            "page": 1,
            "token_count": 25,
            "category": "housing_welfare"
        }

        # Insert record
        self.vs.upsert_record(
            record_id=record_id,
            vector=vector,
            text=text,
            metadata=metadata
        )

        # Read back record
        stored = self.vs.get_record(record_id)
        self.assertIsNotNone(stored, f"Record '{record_id}' should be found in collection.")

        # Assert schema fields
        self.assertEqual(stored["id"], record_id)
        self.assertEqual(len(stored["vector"]), 1536)
        self.assertEqual(stored["text"], text)
        self.assertEqual(stored["metadata"]["source"], "housing_welfare_guidelines.html")
        self.assertEqual(stored["metadata"]["section"], "Subsidy & Financial Assistance")
        self.assertEqual(stored["metadata"]["category"], "housing_welfare")

    def test_dimension_mismatch_rejection(self):
        """Verifies that inserting vectors with mismatched dimension raises ValueError."""
        invalid_vector_768 = [0.1] * 768
        with self.assertRaises(ValueError) as ctx:
            self.vs.upsert_record("bad:dim", invalid_vector_768, "Text", {})
        self.assertIn("DIMENSION MISMATCH", str(ctx.exception))

        invalid_vector_3 = [0.1, 0.2, 0.3]
        with self.assertRaises(ValueError) as ctx2:
            self.vs.upsert_record("bad:dim2", invalid_vector_3, "Text", {})
        self.assertIn("DIMENSION MISMATCH", str(ctx2.exception))

    def test_batch_upsert_and_count(self):
        """Verifies multi-record batch insertion and collection count."""
        records = [
            {
                "id": f"doc_{i}:chunk_{i}",
                "vector": [float(i) / 100.0] * 1536,
                "text": f"Sample policy chunk text #{i}",
                "metadata": {"source": f"doc_{i}.md", "chunk_index": i}
            }
            for i in range(1, 4)
        ]

        count_upserted = self.vs.upsert_batch(records)
        self.assertEqual(count_upserted, 3)
        self.assertEqual(self.vs.count(), 3)

        # Read back second record
        rec2 = self.vs.get_record("doc_2:chunk_2")
        self.assertIsNotNone(rec2)
        self.assertEqual(rec2["metadata"]["source"], "doc_2.md")

    def test_nearest_neighbor_query(self):
        """Verifies semantic retrieval returns top matches with valid scores."""
        # Insert target record
        target_vec = [1.0] + [0.0] * 1535
        other_vec = [0.0] * 1535 + [1.0]

        self.vs.upsert_record("target:1", target_vec, "Target document text", {"source": "target.md"})
        self.vs.upsert_record("other:1", other_vec, "Other document text", {"source": "other.md"})

        # Query vector close to target
        query_vec = [0.99] + [0.0] * 1535
        matches = self.vs.query_similar(query_vector=query_vec, top_k=1)

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["id"], "target:1")
        self.assertGreater(matches[0]["score"], 0.8)

    def test_metadata_filtering(self):
        """Verifies metadata where-clause filtering during semantic retrieval."""
        vec1 = [0.5] * 1536
        vec2 = [0.5] * 1536

        self.vs.upsert_record("rec:pmkisan", vec1, "PM KISAN text", {"scheme": "pmkisan"})
        self.vs.upsert_record("rec:pmjay", vec2, "Ayushman Bharat text", {"scheme": "pmjay"})

        # Search with filter restricted to pmjay
        matches = self.vs.query_similar(
            query_vector=vec1,
            top_k=2,
            where_filter={"scheme": "pmjay"}
        )
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["id"], "rec:pmjay")

    def test_nonexistent_record_returns_none(self):
        """Verifies graceful handling when record ID does not exist."""
        result = self.vs.get_record("nonexistent_id_xyz")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
