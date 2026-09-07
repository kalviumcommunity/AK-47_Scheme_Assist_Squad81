# -*- coding: utf-8 -*-
"""
test_rag_evaluation.py - Unit Tests for 3.43 RAG Evaluation & Answer Quality Scoring
===================================================================================
Tests:
  1. Correctness scoring: judge_expected_points (full, partial, zero match)
  2. Grounding scoring: judge_grounding (grounded vs hallucinated claims, fallback)
  3. Citation accuracy: check_citations (exact match, spurious citation, fallback)
  4. Single answer scoring: score_answer dictionary shape and metrics
  5. Evaluation summarizer: macro averages, failure detection, root cause diagnosis
  6. End-to-end RAG answering: answer_with_citations (in-domain vs out-of-domain guardrail)
"""

import os
import sys
import unittest

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_evaluation import (
    DEFAULT_TEST_SET,
    judge_expected_points,
    judge_grounding,
    check_citations,
    score_answer,
    summarize_evaluation,
    answer_with_citations,
)


class TestRAGEvaluation(unittest.TestCase):

    def setUp(self):
        self.sample_chunks = [
            {
                "chunk_id": "pmkisan-0",
                "text": "Under PM-KISAN, an amount of Rs 6,000 per year is released in three 4-monthly installments of Rs 2,000 each.",
                "metadata": {"source": "pmkisan_scheme_doc.md", "chunk_index": 0},
                "embedding": [0.9, 0.1],
            },
            {
                "chunk_id": "ayushman-0",
                "text": "Ayushman Bharat PM-JAY provides health cover of Rs 5 Lakhs per family per year for secondary and tertiary care hospitalization.",
                "metadata": {"source": "ayushman_bharat_healthcare.md", "chunk_index": 0},
                "embedding": [0.1, 0.9],
            },
        ]

    # ─── 1. Correctness Tests ───────────────────────────────────────────────────
    def test_judge_expected_points_full_match(self):
        """Verifies 1.0 score when all expected key points appear in the answer."""
        answer = "Eligible farmers receive Rs 6,000 per year in three installments of Rs 2,000 each."
        expected = ["Rs 6,000", "three installments", "Rs 2,000"]
        score = judge_expected_points(answer, expected)
        self.assertEqual(score, 1.0)

    def test_judge_expected_points_partial_match(self):
        """Verifies fractional score when only some points appear."""
        answer = "Eligible farmers receive Rs 6,000 per year."
        expected = ["Rs 6,000", "three installments", "Rs 2,000"]
        score = judge_expected_points(answer, expected)
        self.assertAlmostEqual(score, 0.33, places=1)

    def test_judge_expected_points_zero_match(self):
        """Verifies 0.0 score when none of the expected points match."""
        answer = "This scheme provides solar pumps to rural areas."
        expected = ["Rs 6,000", "three installments", "Rs 2,000"]
        score = judge_expected_points(answer, expected)
        self.assertEqual(score, 0.0)

    def test_judge_expected_points_empty_points(self):
        """Verifies empty expected points default to 1.0."""
        self.assertEqual(judge_expected_points("Any answer", []), 1.0)

    # ─── 2. Grounding Tests ─────────────────────────────────────────────────────
    def test_judge_grounding_grounded_answer(self):
        """Verifies high grounding score when claims are supported by retrieved context."""
        answer = "Under PM-KISAN, Rs 6,000 per year is released in three installments of Rs 2,000."
        score = judge_grounding(answer, self.sample_chunks)
        self.assertEqual(score, 1.0)

    def test_judge_grounding_hallucinated_answer(self):
        """Verifies low grounding score when answer contains fabricated claims."""
        answer = "Beneficiaries receive cryptocurrency tokens and electric helicopter subsidies in Zurich."
        score = judge_grounding(answer, self.sample_chunks)
        self.assertLess(score, 0.5)

    def test_judge_grounding_fallback_answer(self):
        """Verifies safe fallback refusal is treated as fully grounded (not hallucinated)."""
        answer = "I do not have sufficient verified information in the official guidelines to answer this question."
        score = judge_grounding(answer, self.sample_chunks)
        self.assertEqual(score, 1.0)

    # ─── 3. Citation Accuracy Tests ─────────────────────────────────────────────
    def test_check_citations_exact_match(self):
        """Verifies 1.0 score when citations match expected sources exactly."""
        citations = ["pmkisan_scheme_doc.md"]
        expected = {"pmkisan_scheme_doc.md"}
        score = check_citations(citations, expected)
        self.assertEqual(score, 1.0)

    def test_check_citations_wrong_source(self):
        """Verifies 0.0 score when citations point to an unrelated document."""
        citations = ["campus_guide.md"]
        expected = {"pmkisan_scheme_doc.md"}
        score = check_citations(citations, expected)
        self.assertEqual(score, 0.0)

    def test_check_citations_fallback_out_of_domain(self):
        """Verifies empty citations for out-of-domain query yield 1.0."""
        score = check_citations([], set())
        self.assertEqual(score, 1.0)

        # Spurious citation when no sources expected yields 0.0
        score_spurious = check_citations(["pmkisan_scheme_doc.md"], set())
        self.assertEqual(score_spurious, 0.0)

    # ─── 4. score_answer & summarize_evaluation Tests ───────────────────────────
    def test_score_answer_structure(self):
        """Verifies score_answer returns all required evaluation fields."""
        example = DEFAULT_TEST_SET[0]

        def mock_answer_fn(q):
            return {
                "question": q,
                "answer": "PM-KISAN provides Rs 6,000 in three installments of Rs 2,000.",
                "citations": ["pmkisan_scheme_doc.md"],
                "retrieved_chunks": self.sample_chunks,
            }

        row = score_answer(example, mock_answer_fn)
        self.assertIn("correctness", row)
        self.assertIn("grounding", row)
        self.assertIn("citation_accuracy", row)
        self.assertIn("overall_score", row)
        self.assertEqual(row["correctness"], 1.0)
        self.assertEqual(row["grounding"], 1.0)
        self.assertEqual(row["citation_accuracy"], 1.0)

    def test_summarize_evaluation_metrics_and_diagnostics(self):
        """Verifies summarizer computes averages and correctly categorizes failure causes."""
        rows = [
            {
                "id": "Q1",
                "question": "Q1?",
                "correctness": 1.0,
                "grounding": 1.0,
                "citation_accuracy": 1.0,
            },
            {
                "id": "Q2",
                "question": "Q2?",
                "correctness": 0.5,
                "grounding": 0.5,
                "citation_accuracy": 0.0,
            },
        ]
        summary = summarize_evaluation(rows)
        self.assertEqual(summary["questions"], 2)
        self.assertAlmostEqual(summary["avg_correctness"], 0.75)
        self.assertAlmostEqual(summary["avg_grounding"], 0.75)
        self.assertAlmostEqual(summary["avg_citation_accuracy"], 0.50)
        self.assertEqual(summary["passed_questions"], 1)
        self.assertEqual(summary["failed_questions"], 1)

        failure = summary["failures"][0]
        self.assertEqual(failure["id"], "Q2")
        self.assertEqual(len(failure["diagnosed_causes"]), 3)

    # ─── 5. answer_with_citations Guardrail Test ────────────────────────────────
    def test_answer_with_citations_out_of_domain_guardrail(self):
        """Verifies out-of-domain questions trigger refusal with no citations."""
        res = answer_with_citations(
            question="What supersonic space shuttle license is needed?",
            chunk_records=self.sample_chunks,
            embed_query_fn=lambda q: [1.0, 0.0],
            top_k=2,
        )
        self.assertTrue(res["fallback_triggered"])
        self.assertEqual(res["citations"], [])
        self.assertIn("not have sufficient verified information", res["answer"])


if __name__ == "__main__":
    unittest.main()
