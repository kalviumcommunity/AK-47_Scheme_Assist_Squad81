"""
test_observability.py - Unit tests for Caching, Logging & Usage Monitoring
"""

import os
import json
import time
import unittest
import tempfile
from src.observability import (
    cache_key,
    QueryCache,
    estimate_cost,
    log_rag_request,
    summarize_usage,
    save_usage_report,
    ObservableRAG
)


class TestObservability(unittest.TestCase):

    def test_cache_key_generation(self):
        key1 = cache_key("What are the eligibility criteria?", {"category": "scholarship"})
        key2 = cache_key("  what are the ELIGIBILITY criteria?  ", {"category": "scholarship"})
        key3 = cache_key("What are the eligibility criteria?", {"category": "pension"})

        self.assertEqual(key1, key2, "Normalized question and filters should generate identical SHA-256 keys")
        self.assertNotEqual(key1, key3, "Different filters should generate distinct cache keys")

    def test_query_cache_hit_and_ttl(self):
        cache = QueryCache(ttl_seconds=1)
        q = "What document is required?"
        resp = {"answer": "Income certificate [1]", "status": "answered"}

        # Set cache
        cache.set(q, resp)
        self.assertEqual(cache.size(), 1)

        # Immediate get -> Hit
        cached = cache.get(q)
        self.assertIsNotNone(cached)
        self.assertEqual(cached["answer"], resp["answer"])

        # Wait for TTL expiration
        time.sleep(1.1)
        expired = cache.get(q)
        self.assertIsNone(expired, "Expired cache entry should return None")
        self.assertEqual(cache.size(), 0, "Expired entry should be purged automatically")

    def test_estimate_cost(self):
        # 1000 input tokens = 0.00015, 1000 output tokens = 0.00060 -> Total = 0.00075
        cost = estimate_cost(1000, 1000)
        self.assertEqual(cost, 0.00075)

        zero_cost = estimate_cost(0, 0)
        self.assertEqual(zero_cost, 0.0)

    def test_log_rag_request_and_summarize(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_file = os.path.join(tmp_dir, "test_requests.jsonl")
            
            rec1 = {
                "question": "Q1",
                "answer": "A1",
                "sources": ["doc1.pdf"],
                "cache_hit": False,
                "input_tokens": 100,
                "output_tokens": 50,
                "estimated_cost": 0.000045,
                "latency_ms": 250.0,
                "status": "answered"
            }

            rec2 = {
                "question": "Q1",
                "answer": "A1",
                "sources": ["doc1.pdf"],
                "cache_hit": True,
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost": 0.0,
                "latency_ms": 5.0,
                "status": "answered"
            }

            log_rag_request(rec1, log_file=log_file)
            log_rag_request(rec2, log_file=log_file)

            self.assertTrue(os.path.exists(log_file))

            with open(log_file, "r", encoding="utf-8") as f:
                lines = [json.loads(line) for line in f if line.strip()]
            
            self.assertEqual(len(lines), 2)
            self.assertEqual(lines[0]["question"], "Q1")
            self.assertTrue(lines[1]["cache_hit"])

            summary = summarize_usage(lines)
            self.assertEqual(summary["total_requests"], 2)
            self.assertEqual(summary["cache_hits"], 1)
            self.assertEqual(summary["cache_hit_rate"], 0.5)
            self.assertEqual(summary["total_input_tokens"], 100)
            self.assertEqual(summary["total_output_tokens"], 50)

    def test_observable_rag_orchestrator(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_file = os.path.join(tmp_dir, "observable_rag.jsonl")
            cache = QueryCache(ttl_seconds=300)

            def dummy_pipeline(q, filters=None):
                return {
                    "answer": "Dummy answer [1].",
                    "citations": {"[1]": {"source": "scheme.pdf"}},
                    "status": "answered",
                    "prompt": f"Context: dummy. Question: {q}"
                }

            rag = ObservableRAG(dummy_pipeline, cache=cache, log_file=log_file)

            # First call: Cache miss
            res1 = rag.query("How to apply?")
            self.assertFalse(res1["usage"]["cache_hit"])
            self.assertGreater(res1["usage"]["input_tokens"], 0)
            self.assertGreater(res1["usage"]["output_tokens"], 0)

            # Second call: Cache hit
            res2 = rag.query("How to apply?")
            self.assertTrue(res2["usage"]["cache_hit"])
            self.assertEqual(res2["usage"]["input_tokens"], 0)
            self.assertEqual(res2["usage"]["output_tokens"], 0)
            self.assertEqual(res2["answer"], res1["answer"])


if __name__ == "__main__":
    unittest.main()
