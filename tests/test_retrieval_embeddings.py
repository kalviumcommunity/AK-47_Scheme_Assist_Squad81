import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval import cosine_similarity, rank_by_embedding


class TestEmbeddingSimilarity(unittest.TestCase):
    def test_cosine_similarity_uses_vector_direction(self):
        self.assertAlmostEqual(cosine_similarity([3, 0], [6, 0]), 1.0)
        self.assertAlmostEqual(cosine_similarity([1, 0], [0, 1]), 0.0)

    def test_ranks_chunks_and_preserves_metadata(self):
        query_embedding = [1.0, 0.0]
        records = [
            {
                "text": "Password reset instructions.",
                "metadata": {"source": "account-guide.md", "chunk_index": 0},
                "embedding": [0.9, 0.1],
            },
            {
                "text": "The cafeteria menu changes every Friday.",
                "metadata": {"source": "campus-guide.md", "chunk_index": 3},
                "embedding": [0.0, 1.0],
            },
            {
                "text": "Recover access using your registered email.",
                "metadata": {"source": "account-guide.md", "chunk_index": 1},
                "embedding": [1.0, 0.0],
            },
        ]

        ranked = rank_by_embedding(query_embedding, records)

        self.assertEqual(ranked[0]["metadata"]["chunk_index"], 1)
        self.assertEqual(ranked[-1]["metadata"]["source"], "campus-guide.md")
        self.assertAlmostEqual(ranked[0]["similarity_score"], 1.0)
        self.assertNotIn("similarity_score", records[0])

    def test_invalid_records_are_skipped(self):
        records = [{"text": "missing vector"}, {"embedding": [0.0, 0.0]}]
        self.assertEqual(rank_by_embedding([1.0, 0.0], records), [])


if __name__ == "__main__":
    unittest.main()