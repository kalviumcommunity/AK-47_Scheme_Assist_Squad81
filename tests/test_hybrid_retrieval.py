# -*- coding: utf-8 -*-
"""
test_hybrid_retrieval.py - Unit Tests for 3.33 Metadata Filtering & Hybrid Search
==================================================================================
Tests:
  1. Keyword scoring helper (_keyword_score)
  2. Tokenizer helper (_tokenize)
  3. HybridRetriever.retrieve – unfiltered returns results
  4. HybridRetriever.retrieve – metadata filter restricts by scheme
  5. HybridRetriever.retrieve – metadata filter restricts by source
  6. HybridRetriever.retrieve – combined $and filter
  7. HybridRetriever.retrieve – empty query returns empty list
  8. HybridRetriever.retrieve – hybrid score = alpha*vector + beta*keyword
  9. HybridRetriever.compare_filtered_unfiltered – returns both sets
 10. SimpleRetriever backward-compatibility (not broken by HybridRetriever)
"""

import os
import sys
import hashlib
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_store import VectorStore
from src.retrieval import HybridRetriever, SimpleRetriever, _keyword_score, _tokenize

# ---------------------------------------------------------------------------
# Shared test fixtures
# ---------------------------------------------------------------------------

DIMENSION = 32  # Small dim – no API calls needed


def _det_embed(text: str, dim: int = DIMENSION) -> list:
    """Deterministic SHA-256 pseudo-embedding for offline testing."""
    digest = hashlib.sha256(text.encode()).digest()
    repeated = (digest * ((dim // 32) + 1))[:dim]
    return [(b / 127.5) - 1.0 for b in repeated]


def embed_fn(query: str) -> list:
    return _det_embed(query, DIMENSION)


CORPUS = [
    {
        "id": "pmkisan:elig:1",
        "text": "PM-KISAN provides income support of Rs 6000 per year to small and marginal farmers.",
        "metadata": {"scheme": "pmkisan", "source": "pmkisan_guide.md", "section": "Eligibility"},
    },
    {
        "id": "pmkisan:pay:2",
        "text": "PM-KISAN payment is released in three equal installments of Rs 2000 each.",
        "metadata": {"scheme": "pmkisan", "source": "pmkisan_guide.md", "section": "Payment"},
    },
    {
        "id": "pmjay:cover:1",
        "text": "Ayushman Bharat PM-JAY covers up to Rs 5 lakh per family per year for hospitalisation.",
        "metadata": {"scheme": "pmjay", "source": "ayushman_guide.md", "section": "Coverage"},
    },
    {
        "id": "pmjay:elig:2",
        "text": "PM-JAY targets economically weaker sections identified through SECC database.",
        "metadata": {"scheme": "pmjay", "source": "ayushman_guide.md", "section": "Eligibility"},
    },
    {
        "id": "housing:subsidy:1",
        "text": "Pradhan Mantri Awas Yojana provides an interest subsidy of 6.5 percent on home loans.",
        "metadata": {"scheme": "pmay", "source": "housing_guide.md", "section": "Subsidy"},
    },
    {
        "id": "housing:elig:2",
        "text": "PMAY Urban benefits families who do not own a pucca house anywhere in India.",
        "metadata": {"scheme": "pmay", "source": "housing_guide.md", "section": "Eligibility"},
    },
]


def _build_retriever() -> HybridRetriever:
    """Creates a fresh in-memory VectorStore and HybridRetriever for each test."""
    vs = VectorStore(in_memory=True, collection_name="test_hybrid_33", dimension=DIMENSION)
    vs.reset_collection()
    for doc in CORPUS:
        vs.upsert_record(
            record_id=doc["id"],
            vector=embed_fn(doc["text"]),
            text=doc["text"],
            metadata=doc["metadata"],
        )
    return HybridRetriever(vector_store=vs, embed_fn=embed_fn, alpha=0.7, beta=0.3)


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------

class TestKeywordHelpers(unittest.TestCase):
    """Unit tests for the internal keyword scoring utilities."""

    def test_tokenize_lowercases_and_strips_punctuation(self):
        tokens = _tokenize("PM-KISAN: support for farmers!")
        self.assertIn("pm", tokens)
        self.assertIn("kisan", tokens)
        self.assertIn("farmers", tokens)
        self.assertNotIn("PM-KISAN:", tokens)

    def test_keyword_score_full_overlap(self):
        """Score should be 1.0 when all query tokens appear in document."""
        score = _keyword_score("farmers income", "PM-KISAN income support for farmers")
        self.assertAlmostEqual(score, 1.0, places=2)

    def test_keyword_score_no_overlap(self):
        """Score should be 0.0 when no query tokens appear in document."""
        score = _keyword_score("passport renewal fee", "housing loan subsidy")
        self.assertAlmostEqual(score, 0.0, places=2)

    def test_keyword_score_partial_overlap(self):
        """Score should be between 0 and 1 for partial matches."""
        score = _keyword_score("farmers subsidy income", "PM-KISAN income support")
        self.assertGreater(score, 0.0)
        self.assertLess(score, 1.0)

    def test_keyword_score_empty_query(self):
        """Empty query should return 0.0 without raising."""
        score = _keyword_score("", "some document text")
        self.assertEqual(score, 0.0)


class TestHybridRetriever(unittest.TestCase):

    def setUp(self):
        self.retriever = _build_retriever()

    # ------------------------------------------------------------------
    # Basic retrieval
    # ------------------------------------------------------------------

    def test_unfiltered_returns_results(self):
        """Unfiltered query should return top_k results from full corpus."""
        results = self.retriever.retrieve("financial support for farmers", top_k=3)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 3)
        self.assertGreater(len(results), 0)

    def test_result_schema(self):
        """Each result must contain required keys with correct types."""
        results = self.retriever.retrieve("income support farmers", top_k=2)
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertIn("id", r)
            self.assertIn("text", r)
            self.assertIn("metadata", r)
            self.assertIn("vector_score", r)
            self.assertIn("keyword_score", r)
            self.assertIn("hybrid_score", r)
            self.assertIsInstance(r["hybrid_score"], float)
            self.assertGreaterEqual(r["hybrid_score"], 0.0)

    def test_empty_query_returns_empty_list(self):
        """Empty string and whitespace-only query must return []."""
        self.assertEqual(self.retriever.retrieve(""), [])
        self.assertEqual(self.retriever.retrieve("   "), [])

    # ------------------------------------------------------------------
    # Metadata filtering
    # ------------------------------------------------------------------

    def test_filter_by_scheme_restricts_results(self):
        """Results must only contain records matching the scheme filter."""
        results = self.retriever.retrieve(
            "support scheme",
            top_k=5,
            metadata_filter={"scheme": "pmkisan"},
        )
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r["metadata"]["scheme"], "pmkisan")

    def test_filter_by_source_restricts_results(self):
        """Results must only contain records from the filtered source file."""
        results = self.retriever.retrieve(
            "housing loan benefits",
            top_k=5,
            metadata_filter={"source": "housing_guide.md"},
        )
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r["metadata"]["source"], "housing_guide.md")

    def test_combined_and_filter(self):
        """Combined $and filter must restrict to matching scheme AND section."""
        results = self.retriever.retrieve(
            "who qualifies for the health scheme",
            top_k=5,
            metadata_filter={
                "$and": [
                    {"scheme": {"$eq": "pmjay"}},
                    {"section": {"$eq": "Eligibility"}},
                ]
            },
        )
        self.assertGreater(len(results), 0)
        for r in results:
            self.assertEqual(r["metadata"]["scheme"], "pmjay")
            self.assertEqual(r["metadata"]["section"], "Eligibility")

    def test_impossible_filter_returns_empty(self):
        """Filter that matches nothing should return an empty list gracefully."""
        results = self.retriever.retrieve(
            "some query",
            top_k=3,
            metadata_filter={"scheme": "nonexistent_scheme_xyz"},
        )
        self.assertEqual(results, [])

    # ------------------------------------------------------------------
    # Hybrid score arithmetic
    # ------------------------------------------------------------------

    def test_hybrid_score_equals_weighted_sum(self):
        """hybrid_score must equal alpha*vector_score + beta*keyword_score (approx)."""
        alpha, beta = 0.7, 0.3
        results = self.retriever.retrieve("farmers income support", top_k=3)
        for r in results:
            expected = round(alpha * r["vector_score"] + beta * r["keyword_score"], 4)
            self.assertAlmostEqual(r["hybrid_score"], expected, places=3)

    def test_results_sorted_by_hybrid_score_descending(self):
        """Returned list must be sorted from highest to lowest hybrid_score."""
        results = self.retriever.retrieve("support scheme eligibility", top_k=5)
        scores = [r["hybrid_score"] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    # ------------------------------------------------------------------
    # compare_filtered_unfiltered
    # ------------------------------------------------------------------

    def test_compare_returns_both_sets(self):
        """compare_filtered_unfiltered must return filtered, unfiltered, and delta_ids."""
        comparison = self.retriever.compare_filtered_unfiltered(
            query="support scheme",
            metadata_filter={"scheme": "pmkisan"},
            top_k=3,
        )
        self.assertIn("query", comparison)
        self.assertIn("filter", comparison)
        self.assertIn("filtered", comparison)
        self.assertIn("unfiltered", comparison)
        self.assertIn("delta_ids", comparison)

    def test_filtered_results_are_subset_of_unfiltered_ids(self):
        """All filtered IDs should be compatible with the applied filter."""
        comparison = self.retriever.compare_filtered_unfiltered(
            query="farmers income",
            metadata_filter={"scheme": "pmkisan"},
            top_k=3,
        )
        for r in comparison["filtered"]:
            self.assertEqual(r["metadata"]["scheme"], "pmkisan")


class TestSimpleRetrieverBackwardCompat(unittest.TestCase):
    """Confirms that SimpleRetriever still works after HybridRetriever was added."""

    def test_simple_retriever_keyword_search(self):
        items = [
            {"text": "PM-KISAN income support for farmers"},
            {"text": "Ayushman Bharat health coverage"},
        ]
        sr = SimpleRetriever(items)
        results = sr.search("farmers income", top_k=2)
        self.assertGreater(len(results), 0)
        self.assertIn("retrieval_score", results[0])

    def test_simple_retriever_empty_query(self):
        items = [{"text": "some text"}]
        sr = SimpleRetriever(items)
        self.assertEqual(sr.search(""), [])


if __name__ == "__main__":
    unittest.main()
