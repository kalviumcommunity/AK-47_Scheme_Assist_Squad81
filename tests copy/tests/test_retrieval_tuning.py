# -*- coding: utf-8 -*-
"""
test_retrieval_tuning.py - Unit Tests for 3.34 Retrieval Relevance Tuning
==========================================================================
Tests:
  1. evaluate() returns one row per test query
  2. hit and top1_hit columns are booleans
  3. hit_rate is in [0, 1]
  4. top1_hit_rate is in [0, 1]
  5. pick_best_setting() returns a valid setting name
  6. JSON output file is written with all expected top-level keys
  7. wider k=5 hit_rate >= k=3 hit_rate (monotonicity property)
  8. compute_metrics() hits + top1_hits <= total_queries
  9. evaluate() row schema has all required keys
 10. strict_threshold avg_kept <= wider_k5 avg_kept (filtering reduces results)
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_store import VectorStore
from src.embeddings import DeterministicSemanticVectorizer
from src.retrieval_relevance_tuning import (
    CORPUS,
    TEST_QUERIES,
    SETTINGS,
    evaluate,
    compute_metrics,
    pick_best_setting,
    run_tuning,
    embed_fn,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_vectorizer = DeterministicSemanticVectorizer(dimension=1536)


def _build_vs() -> VectorStore:
    """Builds a fresh in-memory VectorStore loaded with the full corpus."""
    vs = VectorStore(in_memory=True, collection_name="test_tuning_34", dimension=1536)
    vs.reset_collection()
    for doc in CORPUS:
        vs.upsert_record(
            record_id=doc["id"],
            vector=embed_fn(doc["text"]),
            text=doc["text"],
            metadata=doc["metadata"],
        )
    return vs


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestEvaluateFunction(unittest.TestCase):

    def setUp(self):
        self.vs = _build_vs()
        self.baseline = next(s for s in SETTINGS if s["name"] == "baseline_k3")
        self.wider = next(s for s in SETTINGS if s["name"] == "wider_k5")
        self.strict = next(s for s in SETTINGS if s["name"] == "strict_threshold")

    def test_evaluate_returns_one_row_per_query(self):
        """evaluate() must return exactly one row per entry in TEST_QUERIES."""
        rows = evaluate(self.baseline, self.vs)
        self.assertEqual(len(rows), len(TEST_QUERIES))

    def test_row_schema_has_required_keys(self):
        """Each evaluate() row must contain all required keys."""
        rows = evaluate(self.baseline, self.vs)
        required_keys = {
            "query", "expected_source", "returned_sources",
            "top1_source", "hit", "top1_hit", "kept_count", "scores",
        }
        for row in rows:
            self.assertTrue(required_keys.issubset(set(row.keys())),
                            f"Missing keys: {required_keys - set(row.keys())}")

    def test_hit_columns_are_boolean(self):
        """hit and top1_hit must be Python booleans (not int 0/1)."""
        rows = evaluate(self.baseline, self.vs)
        for row in rows:
            self.assertIsInstance(row["hit"], bool)
            self.assertIsInstance(row["top1_hit"], bool)

    def test_kept_count_matches_returned_sources_length(self):
        """kept_count must equal len(returned_sources) for every row."""
        rows = evaluate(self.baseline, self.vs)
        for row in rows:
            self.assertEqual(row["kept_count"], len(row["returned_sources"]))

    def test_strict_threshold_reduces_avg_kept(self):
        """strict_threshold (min_score=0.30) must keep <= results than wider_k5."""
        rows_strict = evaluate(self.strict, self.vs)
        rows_wider = evaluate(self.wider, self.vs)
        avg_strict = sum(r["kept_count"] for r in rows_strict) / len(rows_strict)
        avg_wider = sum(r["kept_count"] for r in rows_wider) / len(rows_wider)
        self.assertLessEqual(avg_strict, avg_wider,
                             "Score-gated setting should keep <= chunks than unfiltered wider_k5")


class TestComputeMetrics(unittest.TestCase):

    def test_hit_rate_in_range(self):
        """hit_rate must be in [0.0, 1.0]."""
        vs = _build_vs()
        for setting in SETTINGS:
            rows = evaluate(setting, vs)
            m = compute_metrics(rows)
            self.assertGreaterEqual(m["hit_rate"], 0.0)
            self.assertLessEqual(m["hit_rate"], 1.0)

    def test_top1_hit_rate_in_range(self):
        """top1_hit_rate must be in [0.0, 1.0]."""
        vs = _build_vs()
        for setting in SETTINGS:
            rows = evaluate(setting, vs)
            m = compute_metrics(rows)
            self.assertGreaterEqual(m["top1_hit_rate"], 0.0)
            self.assertLessEqual(m["top1_hit_rate"], 1.0)

    def test_hits_lte_total_queries(self):
        """hits and top1_hits must never exceed total_queries."""
        vs = _build_vs()
        for setting in SETTINGS:
            rows = evaluate(setting, vs)
            m = compute_metrics(rows)
            self.assertLessEqual(m["hits"], m["total_queries"])
            self.assertLessEqual(m["top1_hits"], m["total_queries"])

    def test_top1_hits_lte_hits(self):
        """top1_hits can never exceed hits (top-1 is a subset of all hits)."""
        vs = _build_vs()
        for setting in SETTINGS:
            rows = evaluate(setting, vs)
            m = compute_metrics(rows)
            self.assertLessEqual(m["top1_hits"], m["hits"],
                                 f"top1_hits > hits for setting '{setting['name']}'")

    def test_wider_k_hit_rate_gte_baseline(self):
        """wider_k5 hit_rate >= baseline_k3 hit_rate (monotonicity: more k = more recall)."""
        vs = _build_vs()
        baseline = next(s for s in SETTINGS if s["name"] == "baseline_k3")
        wider = next(s for s in SETTINGS if s["name"] == "wider_k5")
        m_base = compute_metrics(evaluate(baseline, vs))
        m_wider = compute_metrics(evaluate(wider, vs))
        self.assertGreaterEqual(
            m_wider["hit_rate"], m_base["hit_rate"],
            "Increasing k should not decrease hit_rate"
        )


class TestPickBestSetting(unittest.TestCase):

    def test_pick_best_returns_valid_setting_name(self):
        """pick_best_setting() must return a name present in SETTINGS."""
        vs = _build_vs()
        summary = []
        for setting in SETTINGS:
            rows = evaluate(setting, vs)
            metrics = compute_metrics(rows)
            summary.append({
                "setting": setting["name"],
                "description": setting["description"],
                "config": setting,
                "metrics": metrics,
                "details": rows,
            })
        best = pick_best_setting(summary)
        valid_names = {s["name"] for s in SETTINGS}
        self.assertIn(best["setting"], valid_names)

    def test_pick_best_has_highest_hit_rate(self):
        """The chosen best setting must have the highest hit_rate in the summary."""
        vs = _build_vs()
        summary = []
        for setting in SETTINGS:
            rows = evaluate(setting, vs)
            metrics = compute_metrics(rows)
            summary.append({
                "setting": setting["name"],
                "description": setting["description"],
                "config": setting,
                "metrics": metrics,
                "details": rows,
            })
        best = pick_best_setting(summary)
        max_hit_rate = max(s["metrics"]["hit_rate"] for s in summary)
        self.assertEqual(best["metrics"]["hit_rate"], max_hit_rate)


class TestRunTuning(unittest.TestCase):

    def test_json_output_written_with_expected_keys(self):
        """run_tuning() must create outputs/retrieval_tuning_results.json with required keys."""
        # Change to project root so output path resolves correctly
        orig_dir = os.getcwd()
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(project_root)
        try:
            run_tuning()
            output_path = os.path.join("outputs", "retrieval_tuning_results.json")
            self.assertTrue(os.path.exists(output_path), "JSON output file not created")
            with open(output_path, encoding="utf-8") as f:
                data = json.load(f)
            required_keys = {
                "experiment", "corpus_size", "test_query_count",
                "best_setting", "best_metrics", "summary", "details",
            }
            self.assertTrue(required_keys.issubset(set(data.keys())),
                            f"Missing keys: {required_keys - set(data.keys())}")
            self.assertEqual(data["corpus_size"], len(CORPUS))
            self.assertEqual(data["test_query_count"], len(TEST_QUERIES))
            self.assertEqual(len(data["summary"]), len(SETTINGS))
        finally:
            os.chdir(orig_dir)


if __name__ == "__main__":
    unittest.main()
