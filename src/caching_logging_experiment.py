"""
caching_logging_experiment.py - Experiment runner for Caching, Logging & Monitoring
====================================================================================
Executes sample queries to test:
  1. Cold-start query execution (Cache Miss).
  2. Identical repeated query execution (Cache Hit).
  3. Out-of-scope query execution (Refusal logging).
  4. Generation of outputs/rag_requests.jsonl and outputs/usage_summary_report.json.
"""

import json
import os
import sys

# Ensure sys.path includes project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.guardrails import guarded_answer
from src.observability import ObservableRAG, QueryCache, save_usage_report


# Mock retrieved chunk store for experiment
CHUNKS_DB = {
    "income": [
        {
            "score": 0.92,
            "text": "Applicants for the Scheme must provide an Income Certificate showing household income under Rs. 1.5 Lakh.",
            "metadata": {"source": "guidelines_sec2.pdf", "chunk_index": 4}
        }
    ]
}


def mock_rag_pipeline(question: str, filters: dict | None = None) -> dict:
    """Simulate retrieval and guarded generation pipeline."""
    q_lower = question.lower()
    if "income" in q_lower or "document" in q_lower:
        chunks = CHUNKS_DB["income"]
        return guarded_answer(
            question,
            chunks,
            lambda prompt: "Applicants must submit an Income Certificate showing household income below Rs. 1.5 Lakh [1]."
        )
    else:
        # Out-of-scope query returning low similarity scores
        weak_chunks = [
            {"score": 0.15, "text": "Unrelated cafeteria guide.", "metadata": {"source": "menu.pdf"}}
        ]
        return guarded_answer(
            question,
            weak_chunks,
            lambda prompt: "Unrelated text"
        )


def main() -> None:
    print("\n" + "=" * 75)
    print("  [SchemeAssist] Caching, Logging & Usage Monitoring Experiment")
    print("=" * 75)

    # Initialize fresh cache and clear log file for experiment run
    cache = QueryCache(ttl_seconds=900)
    log_file = "outputs/rag_requests.jsonl"
    report_file = "outputs/usage_summary_report.json"

    if os.path.exists(log_file):
        os.remove(log_file)

    rag = ObservableRAG(mock_rag_pipeline, cache=cache, log_file=log_file)

    queries = [
        ("What document is required for income verification?", None, "Query 1 (Cold Start - Cache Miss)"),
        ("What document is required for income verification?", None, "Query 2 (Repeated Query - Cache Hit)"),
        ("What is the cafeteria lunch menu today?", None, "Query 3 (Out-of-Scope Query - Refusal)"),
    ]

    results = []

    for question, filters, label in queries:
        print(f"\n---> Executing {label}: '{question}'")
        res = rag.query(question, filters)
        usage = res.get("usage", {})
        
        print(f"  [Status]: {res.get('status')}")
        print(f"  [Answer]: {res.get('answer')[:100]}...")
        print(f"  [Cache Hit]: {usage.get('cache_hit')}")
        print(f"  [Tokens]: In={usage.get('input_tokens')}, Out={usage.get('output_tokens')}")
        print(f"  [Cost]: ${usage.get('estimated_cost'):.6f}")
        print(f"  [Latency]: {usage.get('latency_ms')} ms")

        results.append({
            "label": label,
            "question": question,
            "response": res
        })

    # Save summary report
    summary = save_usage_report(log_file=log_file, report_file=report_file)

    print("\n" + "=" * 75)
    print("  [Usage Summary Report]")
    print("=" * 75)
    print(json.dumps(summary, indent=2))

    print(f"\n[OK] Logs written to '{log_file}'")
    print(f"[OK] Summary report written to '{report_file}'")


if __name__ == "__main__":
    main()
