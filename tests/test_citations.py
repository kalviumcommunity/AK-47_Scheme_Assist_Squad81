import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.citations import (
    FALLBACK_ANSWER,
    answer_with_citations,
    build_citation_map,
    build_cited_prompt,
    verify_citation,
)


CHUNKS = [
    {
        "chunk_id": "policy-001",
        "text": "Applicants must submit an income certificate.",
        "metadata": {"source": "scheme-guidelines.md", "chunk_index": 2, "section": "Documents"},
    },
    {
        "chunk_id": "policy-002",
        "text": "Applications are accepted through the official portal.",
        "metadata": {"source": "scheme-guidelines.md", "chunk_index": 3, "page": 4},
    },
]


class TestCitations(unittest.TestCase):
    def test_maps_markers_to_metadata_and_text(self):
        citation_map = build_citation_map(CHUNKS)
        self.assertEqual(citation_map["[1]"]["source"], "scheme-guidelines.md")
        self.assertEqual(citation_map["[1]"]["chunk_id"], "policy-001")
        self.assertEqual(citation_map["[1]"]["section"], "Documents")
        self.assertEqual(citation_map["[2]"]["page"], 4)

    def test_prompt_requires_only_context_citations(self):
        prompt = build_cited_prompt("What document is required?", CHUNKS)
        self.assertIn("Only use source markers that appear in the context.", prompt)
        self.assertIn("[1] Applicants must submit", prompt)
        self.assertIn(FALLBACK_ANSWER, prompt)

    def test_cited_answer_returns_only_used_sources(self):
        result = answer_with_citations(
            "What document is required?",
            CHUNKS,
            lambda prompt: "Submit an income certificate [1].",
        )
        self.assertEqual(result["answer"], "Submit an income certificate [1].")
        self.assertEqual(list(result["citations"]), ["[1]"])
        self.assertEqual(result["citations"]["[1]"]["chunk_id"], "policy-001")

    def test_unknown_citations_are_rejected_with_fallback(self):
        result = answer_with_citations(
            "What document is required?",
            CHUNKS,
            lambda prompt: "Submit a passport [9].",
        )
        self.assertEqual(result["answer"], FALLBACK_ANSWER)
        self.assertEqual(result["citations"], {})

    def test_empty_sources_return_uncited_fallback(self):
        result = answer_with_citations("Anything?", [], lambda prompt: "An unsupported answer [1].")
        self.assertEqual(result, {"answer": FALLBACK_ANSWER, "citations": {}, "prompt": ""})

    def test_verify_citation_matches_original_chunk(self):
        citation_map = build_citation_map(CHUNKS)
        verified = verify_citation("[1]", citation_map, CHUNKS)
        self.assertTrue(verified["valid"])
        self.assertEqual(verified["source"], "scheme-guidelines.md")

        tampered = dict(CHUNKS[0], text="tampered text")
        invalid = verify_citation("[1]", citation_map, [tampered])
        self.assertFalse(invalid["valid"])


if __name__ == "__main__":
    unittest.main()