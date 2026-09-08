import os
import sys
import tempfile
import unittest
from types import SimpleNamespace

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.batch_embedding import embed_chunks


class RetryableError(Exception):
    status_code = 429


class FakeEmbeddings:
    def __init__(self, failures=0):
        self.failures = failures
        self.calls = []

    def create(self, model, input):
        self.calls.append((model, input))
        if self.failures:
            self.failures -= 1
            raise RetryableError("rate limited")
        return SimpleNamespace(
            data=[SimpleNamespace(index=index, embedding=[float(index), 1.0]) for index in range(len(input))]
        )


class TestBatchEmbedding(unittest.TestCase):
    def test_batches_requests_and_skips_existing_vectors(self):
        chunks = [
            {"chunk_id": "already", "text": "skip me", "embedding": [1.0]},
            {"chunk_id": "one", "text": "first"},
            {"chunk_id": "two", "text": "second"},
            {"chunk_id": "three", "text": "third"},
        ]
        embeddings = FakeEmbeddings()
        summary = embed_chunks(chunks, SimpleNamespace(embeddings=embeddings), batch_size=2)

        self.assertEqual(len(embeddings.calls), 2)
        self.assertEqual([len(call[1]) for call in embeddings.calls], [2, 1])
        self.assertEqual(summary["skipped_existing"], 1)
        self.assertEqual(summary["embedded"], 3)
        self.assertEqual(summary["failed"], 0)
        self.assertTrue(all("embedding" in chunk for chunk in chunks))

    def test_retries_and_persists_checkpoint(self):
        chunks = [{"chunk_id": "one", "text": "first"}]
        embeddings = FakeEmbeddings(failures=2)
        waits = []
        with tempfile.TemporaryDirectory() as directory:
            checkpoint = os.path.join(directory, "chunks.json")
            summary = embed_chunks(
                chunks,
                SimpleNamespace(embeddings=embeddings),
                max_attempts=3,
                backoff_base=0.5,
                sleep=waits.append,
                checkpoint_path=checkpoint,
            )
            self.assertEqual(summary["api_requests"], 3)
            self.assertEqual(waits, [0.5, 1.0])
            self.assertEqual(summary["failed"], 0)
            self.assertTrue(os.path.exists(checkpoint))

    def test_failed_batches_are_reported(self):
        chunks = [{"chunk_id": "one", "text": "first"}]
        embeddings = FakeEmbeddings(failures=5)
        summary = embed_chunks(
            chunks,
            SimpleNamespace(embeddings=embeddings),
            max_attempts=2,
            sleep=lambda _: None,
        )

        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["failed_batches"], 1)
        self.assertEqual(summary["api_requests"], 2)
        self.assertEqual(summary["errors"][0]["chunk_ids"], ["one"])


if __name__ == "__main__":
    unittest.main()