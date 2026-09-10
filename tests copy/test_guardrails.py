import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.guardrails import (
    WEAK_CONTEXT_ANSWER,
    guarded_answer,
    retrieval_is_strong,
)


STRONG_CHUNKS = [
    {
        "score": 0.91,
        "text": "Applicants must submit an income certificate.",
        "metadata": {"source": "scheme-guidelines.md", "chunk_index": 2},
    },
    {
        "score": 0.78,
        "text": "Applications are accepted through the official portal.",
        "metadata": {"source": "scheme-guidelines.md", "chunk_index": 3},
    },
]


class TestGuardrails(unittest.TestCase):
    def test_empty_and_low_score_context_is_weak(self):
        self.assertFalse(retrieval_is_strong([]))
        self.assertFalse(retrieval_is_strong([{"score": 0.4}]))
        self.assertTrue(retrieval_is_strong(STRONG_CHUNKS))

    def test_threshold_and_support_count_are_configurable(self):
        self.assertTrue(retrieval_is_strong(STRONG_CHUNKS, min_top_score=0.75, min_supporting_chunks=2))
        self.assertFalse(retrieval_is_strong(STRONG_CHUNKS, min_top_score=0.8, min_supporting_chunks=2))

    def test_weak_context_refuses_before_generation(self):
        calls = []
        result = guarded_answer(
            "What is the refund policy?",
            [{"score": 0.2, "text": "Unrelated scheme text."}],
            lambda prompt: calls.append(prompt) or "Invented answer [1].",
        )

        self.assertEqual(result["status"], "refused_weak_context")
        self.assertEqual(result["answer"], WEAK_CONTEXT_ANSWER)
        self.assertEqual(calls, [])
        self.assertEqual(result["citations"], [])

    def test_strong_context_produces_grounded_answer(self):
        result = guarded_answer(
            "What document is required?",
            STRONG_CHUNKS,
            lambda prompt: "Submit an income certificate [1].",
        )

        self.assertEqual(result["status"], "answered")
        self.assertIn("[1]", result["answer"])
        self.assertEqual(result["citations"]["[1]"]["source"], "scheme-guidelines.md")
        self.assertEqual(result["supporting_chunks"], 2)

    def test_strong_context_without_citations_is_refused(self):
        result = guarded_answer(
            "What document is required?",
            STRONG_CHUNKS,
            lambda prompt: "Submit an income certificate.",
        )
        self.assertEqual(result["status"], "refused_uncited_answer")


if __name__ == "__main__":
    unittest.main()