import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval import (
    cosine_similarity,
    rank_by_embedding,
    retrieve_from_vector_store,
    retrieve_top_k,
)


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

    def test_retrieve_top_k_embeds_query_and_returns_citation_fields(self):
        records = [
            {
                "chunk_id": "account-0",
                "text": "Reset a learner password from account settings.",
                "metadata": {"source": "account.md", "chunk_index": 0},
                "embedding": [1.0, 0.0],
            },
            {
                "chunk_id": "campus-0",
                "text": "The campus cafeteria closes at 6 PM.",
                "metadata": {"source": "campus.md", "chunk_index": 0},
                "embedding": [0.0, 1.0],
            },
        ]
        seen_queries = []

        def embed_query(query):
            seen_queries.append(query)
            return [1.0, 0.0]

        results = retrieve_top_k("How do I reset my password?", records, embed_query, top_k=1)

        self.assertEqual(seen_queries, ["How do I reset my password?"])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["chunk_id"], "account-0")
        self.assertEqual(results[0]["metadata"]["source"], "account.md")
        self.assertAlmostEqual(results[0]["score"], 1.0)

    def test_vector_store_retrieval_preserves_top_k_and_metadata(self):
        class FakeVectorStore:
            def query_similar(self, query_vector, top_k, where_filter):
                self.request = (query_vector, top_k, where_filter)
                return [
                    {"id": "chunk-1", "score": 0.91, "text": "first", "metadata": {"source": "a.md"}},
                    {"id": "chunk-2", "score": 0.72, "text": "second", "metadata": {"source": "b.md"}},
                ][:top_k]

        store = FakeVectorStore()
        results = retrieve_from_vector_store(
            "query", store, lambda value: [0.5, 0.5], top_k=1, metadata_filter={"source": "a.md"}
        )

        self.assertEqual(store.request, ([0.5, 0.5], 1, {"source": "a.md"}))
        self.assertEqual(results[0]["id"], "chunk-1")
        self.assertEqual(results[0]["metadata"], {"source": "a.md"})


if __name__ == "__main__":
    unittest.main()