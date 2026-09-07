# -*- coding: utf-8 -*-
"""
test_embedding_quality.py - Unit Tests for 3.29 Embedding Quality & Sanity Tests
================================================================================
Validates:
  1. Cosine similarity mathematical correctness and boundary conditions
  2. Dimension mismatch detection
  3. Deterministic embedding generator properties (unit length, repeatability)
  4. Known query-chunk ranking accuracy (Task 1 & 2)
  5. Score separation margin (related ranks above unrelated)
  6. Surprising, borderline, and mismatched model diagnostic behavior (Task 3)
  7. Sanity report artifact generation (Task 4 & 5)
"""

import os
import sys
import json
import math
import unittest

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embeddings import (
    cosine_similarity,
    DeterministicSemanticVectorizer,
    EmbeddingService,
    generate_mismatched_embedding,
    rank_chunks,
)
from src.embedding_quality_checks import (
    KNOWN_TEST_CASES,
    DIAGNOSTIC_EDGE_CASES,
    load_or_embed_corpus,
    evaluate_test_case,
    run_all_sanity_tests,
    save_sanity_report_artifacts,
)


class TestEmbeddingQualityAndSanity(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.embed_service = EmbeddingService(force_offline=True)
        cls.vectorizer = DeterministicSemanticVectorizer(dimension=1536)
        cls.chunks = load_or_embed_corpus(embedding_service=cls.embed_service)

    # ─── 1. Cosine Similarity Correctness ─────────────────────────────────────

    def test_cosine_similarity_identity_and_bounds(self):
        vec_a = [1.0, 2.0, 3.0, 4.0]
        # Identical vector -> 1.0
        self.assertAlmostEqual(cosine_similarity(vec_a, vec_a), 1.0, places=5)

        # Opposite vector -> -1.0
        vec_neg = [-x for x in vec_a]
        self.assertAlmostEqual(cosine_similarity(vec_a, vec_neg), -1.0, places=5)

        # Orthogonal vectors -> 0.0
        vec_x = [1.0, 0.0, 0.0]
        vec_y = [0.0, 1.0, 0.0]
        self.assertAlmostEqual(cosine_similarity(vec_x, vec_y), 0.0, places=5)

        # Zero vector handling -> 0.0
        vec_zero = [0.0, 0.0, 0.0]
        self.assertAlmostEqual(cosine_similarity(vec_x, vec_zero), 0.0, places=5)

    def test_cosine_similarity_dimension_mismatch_raises(self):
        vec_1536 = [0.1] * 1536
        vec_768 = [0.1] * 768
        with self.assertRaises(ValueError) as ctx:
            cosine_similarity(vec_1536, vec_768)
        self.assertIn("DIMENSION MISMATCH", str(ctx.exception))

    # ─── 2. Embedding Vectorizer Properties ───────────────────────────────────

    def test_deterministic_vectorizer_properties(self):
        text = "Ayushman Bharat PM-JAY healthcare hospitalisation scheme."
        vec = self.vectorizer.embed_text(text)

        # Dimension must be 1536
        self.assertEqual(len(vec), 1536)

        # Unit length L2 norm ||v|| == 1.0
        norm = math.sqrt(sum(x * x for x in vec))
        self.assertAlmostEqual(norm, 1.0, places=4)

        # Deterministic: repeated call yields bit-identical values
        vec2 = self.vectorizer.embed_text(text)
        self.assertEqual(vec, vec2)

    def test_semantic_separation_toy_example(self):
        # Related sentence vs unrelated sentence
        query = "farmer direct income support installment"
        related = "PM-KISAN provides Rs 6000 annual income support to landholding farmers in installments."
        unrelated = "Ayushman Bharat provides secondary tertiary hospitalisation surgery coverage."

        v_q = self.vectorizer.embed_text(query)
        v_rel = self.vectorizer.embed_text(related)
        v_unrel = self.vectorizer.embed_text(unrelated)

        sim_rel = cosine_similarity(v_q, v_rel)
        sim_unrel = cosine_similarity(v_q, v_unrel)

        self.assertGreater(sim_rel, sim_unrel, "Related text must rank above unrelated text")
        self.assertGreater(sim_rel - sim_unrel, 0.1, "Margin should be clearly positive")

    # ─── 3. Known Relevance Tests (Task 1 & 2) ────────────────────────────────

    def test_known_query_chunk_ranking_all_pass(self):
        """Verifies that all curated test cases achieve rank #1 with positive margin."""
        for case in KNOWN_TEST_CASES:
            result = evaluate_test_case(case, self.chunks, self.embed_service)
            self.assertEqual(
                result["top_source"],
                case["expected_source"],
                f"Query '{case['query']}' failed to rank expected source '{case['expected_source']}' at #1. Got '{result['top_source']}'"
            )
            self.assertGreater(
                result["margin"],
                0.0,
                f"Margin for '{case['id']}' must be positive, got {result['margin']}"
            )

    # ─── 4. Surprising, Borderline & Mismatched Cases (Task 3) ────────────────

    def test_mismatched_model_space_fails_as_expected(self):
        """
        Simulates model mismatch (Task 3 / Lesson Warning):
        Corpus embedded in Space A, query embedded in Space B.
        Asserts that ranking degrades and margin drops below zero or fails top-1.
        """
        mismatch_case = [c for c in DIAGNOSTIC_EDGE_CASES if c["id"] == "EDGE-03"][0]
        result = evaluate_test_case(mismatch_case, self.chunks, self.embed_service)
        self.assertEqual(result["status"], "EXPECTED_FAILURE")
        self.assertLessEqual(result["margin"], 0.0)

    def test_borderline_cases_identified(self):
        """Validates that ambiguous cross-scheme queries are detected as borderline."""
        edge_01 = [c for c in DIAGNOSTIC_EDGE_CASES if c["id"] == "EDGE-01"][0]
        result = evaluate_test_case(edge_01, self.chunks, self.embed_service)
        self.assertIn(result["status"], ["PASSED", "BORDERLINE"])

    # ─── 5. Sanity Report Generation (Task 4 & 5) ─────────────────────────────

    def test_run_all_sanity_tests_report_structure(self):
        report = run_all_sanity_tests(self.chunks, self.embed_service)

        # Check top-level keys
        self.assertIn("metadata", report)
        self.assertIn("metrics", report)
        self.assertIn("results", report)

        metrics = report["metrics"]
        self.assertEqual(metrics["known_relevance_tests"], len(KNOWN_TEST_CASES))
        self.assertEqual(metrics["known_relevance_passed"], len(KNOWN_TEST_CASES))
        self.assertEqual(metrics["known_relevance_accuracy_pct"], 100.0)
        self.assertGreater(metrics["average_separation_margin"], 0.0)

    def test_save_sanity_report_artifacts(self):
        report = run_all_sanity_tests(self.chunks, self.embed_service)
        json_path, txt_path, md_path = save_sanity_report_artifacts(report)

        self.assertTrue(os.path.exists(json_path))
        self.assertTrue(os.path.exists(txt_path))
        self.assertTrue(os.path.exists(md_path))

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("metrics", data)
        self.assertEqual(data["metrics"]["known_relevance_accuracy_pct"], 100.0)


if __name__ == "__main__":
    unittest.main()
