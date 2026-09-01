import unittest
import os
import sys

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chunking import (
    fixed_size_chunks,
    fixed_size_overlap_chunks,
    paragraph_chunks,
    sentence_chunks,
    recursive_character_chunks,
    compare_all_strategies,
    analyze_chunks,
    count_mid_sentence_cuts,
    estimate_tokens,
    Chunk
)

SAMPLE_POLICY_TEXT = """# Welfare Scheme Guidelines

## Section 1: Overview
The welfare scheme provides income support to eligible citizens. Benefits are disbursed periodically.

## Section 2: Eligibility Rules
Applicants must satisfy the following criteria:
- Must be a permanent citizen.
- Household income must be below 300000 per annum.
- Must possess active bank account with direct benefit transfer linkage.

## Section 3: Grievance Redressal
Citizens can submit complaints on the official helpline 1800-111-5555. Issues are resolved in 15 days.
"""


class TestDocumentChunkingStrategies(unittest.TestCase):

    def test_estimate_tokens(self):
        self.assertEqual(estimate_tokens(""), 0)
        tokens = estimate_tokens("Hello world this is a test.")
        self.assertGreater(tokens, 0)

    def test_chunk_dataclass_properties(self):
        chunk = Chunk(
            chunk_id="test_001",
            text="This is a test paragraph for chunking verification.",
            source_doc="test.txt",
            strategy="Unit Test"
        )
        self.assertEqual(chunk.char_count, len(chunk.text))
        self.assertEqual(chunk.word_count, len(chunk.text.split()))
        self.assertGreater(chunk.token_count_estimate, 0)
        data = chunk.to_dict()
        self.assertEqual(data["chunk_id"], "test_001")
        self.assertEqual(data["source_doc"], "test.txt")

    def test_fixed_size_chunks_no_overlap(self):
        chunks = fixed_size_chunks(SAMPLE_POLICY_TEXT, size=200, overlap=0, source_doc="policy.md")
        self.assertGreater(len(chunks), 1)
        for c in chunks:
            self.assertLessEqual(c.char_count, 200)
            self.assertEqual(c.strategy, "Fixed-Size (Naive)")

    def test_fixed_size_overlap_chunks(self):
        chunks = fixed_size_overlap_chunks(SAMPLE_POLICY_TEXT, size=200, overlap=50, source_doc="policy.md")
        self.assertGreater(len(chunks), 1)
        for c in chunks:
            self.assertLessEqual(c.char_count, 200)
            self.assertEqual(c.strategy, "Fixed-Size (Overlap)")

    def test_paragraph_chunks(self):
        chunks = paragraph_chunks(SAMPLE_POLICY_TEXT, max_size=1000, source_doc="policy.md")
        self.assertGreater(len(chunks), 0)
        # Paragraphs in SAMPLE_POLICY_TEXT should correspond to sections/blocks
        for c in chunks:
            self.assertLessEqual(c.char_count, 1000)
            self.assertIn("Paragraph-Based", c.strategy)
            self.assertTrue(len(c.text.strip()) > 0)

    def test_sentence_chunks(self):
        chunks = sentence_chunks(SAMPLE_POLICY_TEXT, max_size=250, overlap_sentences=1, source_doc="policy.md")
        self.assertGreater(len(chunks), 0)
        for c in chunks:
            self.assertLessEqual(c.char_count, 350)  # Max size boundary allowing single longer sentence
            self.assertEqual(c.strategy, "Sentence-Based")

    def test_recursive_character_chunks(self):
        chunks = recursive_character_chunks(SAMPLE_POLICY_TEXT, chunk_size=250, chunk_overlap=50, source_doc="policy.md")
        self.assertGreater(len(chunks), 0)
        for c in chunks:
            self.assertEqual(c.strategy, "Recursive Character")
            self.assertLessEqual(c.char_count, 350)

    def test_empty_and_whitespace_input(self):
        self.assertEqual(fixed_size_chunks(""), [])
        self.assertEqual(fixed_size_overlap_chunks("   "), [])
        self.assertEqual(paragraph_chunks(""), [])
        self.assertEqual(sentence_chunks(""), [])
        self.assertEqual(recursive_character_chunks(""), [])

    def test_compare_all_strategies(self):
        results = compare_all_strategies(SAMPLE_POLICY_TEXT, source_doc="policy.md")
        self.assertEqual(len(results), 5)
        for name, stats in results.items():
            self.assertGreater(stats.chunk_count, 0)
            self.assertGreater(stats.avg_char_size, 0)
            self.assertGreater(stats.avg_token_size, 0)
            self.assertIsInstance(stats.mid_sentence_cuts, int)

    def test_mid_sentence_cut_detection(self):
        broken_chunk = [
            Chunk(chunk_id="c1", text="This is an unfinished thought that cuts mid sentence without"),
            Chunk(chunk_id="c2", text="punctuation at the end and continues here.")
        ]
        cuts = count_mid_sentence_cuts(broken_chunk)
        self.assertGreater(cuts, 0)


if __name__ == "__main__":
    unittest.main()
