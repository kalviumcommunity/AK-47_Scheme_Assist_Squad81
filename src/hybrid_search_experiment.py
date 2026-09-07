# -*- coding: utf-8 -*-
"""
hybrid_search_experiment.py - 3.33 Metadata Filtering & Hybrid Search Demo
===========================================================================
Demonstrates SchemeAssist retrieval with and without metadata filters.

Run:
    python src/hybrid_search_experiment.py

What it does:
  1. Builds an in-memory VectorStore with sample welfare-scheme chunks.
  2. Registers a lightweight deterministic embed_fn (no API key needed).
  3. Runs four experiment cases:
       A. Unfiltered semantic search
       B. Filtered by scheme category  ("pmkisan")
       C. Filtered by source document  ("housing_guide.md")
       D. Combined filter using ChromaDB $and operator
  4. Prints side-by-side comparison for each case.
  5. Prints a summary table showing how filtering changed result sets.
"""

import os
import sys
import hashlib
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_store import VectorStore
from src.retrieval import HybridRetriever

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DIMENSION = 32  # Small dimension for offline demo (no real embeddings needed)


def _deterministic_embed(text: str, dim: int = DIMENSION) -> list:
    """
    Generates a deterministic pseudo-embedding from text using SHA-256.
    Produces a stable float vector in [-1, 1] without calling any external API.
    This is ONLY for experimentation; swap in a real embed_fn for production.
    """
    digest = hashlib.sha256(text.encode()).digest()
    # Repeat digest bytes to fill `dim` floats
    repeated = (digest * ((dim // 32) + 1))[:dim]
    vector = [(b / 127.5) - 1.0 for b in repeated]
    return vector


def embed_fn(query: str) -> list:
    return _deterministic_embed(query, DIMENSION)


# ---------------------------------------------------------------------------
# Sample corpus
# ---------------------------------------------------------------------------

CORPUS = [
    {
        "id": "pmkisan:eligibility:1",
        "text": "PM-KISAN provides income support of Rs 6000 per year to small and marginal farmers.",
        "metadata": {"scheme": "pmkisan", "source": "pmkisan_guide.md", "section": "Eligibility"},
    },
    {
        "id": "pmkisan:payment:2",
        "text": "PM-KISAN payment is released in three equal installments of Rs 2000 each.",
        "metadata": {"scheme": "pmkisan", "source": "pmkisan_guide.md", "section": "Payment"},
    },
    {
        "id": "pmjay:coverage:1",
        "text": "Ayushman Bharat PM-JAY covers up to Rs 5 lakh per family per year for secondary and tertiary hospitalisation.",
        "metadata": {"scheme": "pmjay", "source": "ayushman_guide.md", "section": "Coverage"},
    },
    {
        "id": "pmjay:eligibility:2",
        "text": "PM-JAY targets economically weaker sections identified through SECC database.",
        "metadata": {"scheme": "pmjay", "source": "ayushman_guide.md", "section": "Eligibility"},
    },
    {
        "id": "housing:subsidy:1",
        "text": "Pradhan Mantri Awas Yojana provides an interest subsidy of 6.5% on home loans for EWS and LIG categories.",
        "metadata": {"scheme": "pmay", "source": "housing_guide.md", "section": "Subsidy"},
    },
    {
        "id": "housing:eligibility:2",
        "text": "PMAY Urban benefits families who do not own a pucca house anywhere in India.",
        "metadata": {"scheme": "pmay", "source": "housing_guide.md", "section": "Eligibility"},
    },
    {
        "id": "pension:nps:1",
        "text": "National Pension System allows subscribers to contribute regularly to a pension account during their working life.",
        "metadata": {"scheme": "nps", "source": "pension_guide.md", "section": "Overview"},
    },
]


# ---------------------------------------------------------------------------
# Pretty print helpers
# ---------------------------------------------------------------------------

def _print_results(label: str, results: list):
    print(f"\n  [{label}] — {len(results)} result(s)")
    for r in results:
        print(
            f"    • [{r['hybrid_score']:.3f} hybrid | "
            f"{r['vector_score']:.3f} vec | "
            f"{r['keyword_score']:.3f} kw]  "
            f"{r['id']}"
        )
        print(f"      \"{r['text'][:80]}...\"" if len(r['text']) > 80 else f"      \"{r['text']}\"")


def _separator(title: str = ""):
    width = 72
    if title:
        pad = (width - len(title) - 2) // 2
        print("\n" + "-" * pad + f" {title} " + "-" * pad)
    else:
        print("\n" + "-" * width)


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment():
    print("=" * 72)
    print("  3.33 Metadata Filtering & Hybrid Search - Experiment")
    print("=" * 72)
    print(f"  Corpus size : {len(CORPUS)} chunks")
    print(f"  Embedding   : deterministic SHA-256 (offline, dim={DIMENSION})")
    print(f"  Weights     : alpha=0.7 (vector), beta=0.3 (keyword)")

    # -- Setup --------------------------------------------------------------
    vs = VectorStore(in_memory=True, collection_name="experiment_33", dimension=DIMENSION)
    vs.reset_collection()

    for doc in CORPUS:
        vs.upsert_record(
            record_id=doc["id"],
            vector=embed_fn(doc["text"]),
            text=doc["text"],
            metadata=doc["metadata"],
        )
    print(f"\n  [OK] Indexed {vs.count()} records into in-memory VectorStore.\n")

    retriever = HybridRetriever(vector_store=vs, embed_fn=embed_fn, alpha=0.7, beta=0.3)

    # -- Case A: Unfiltered search ------------------------------------------
    _separator("CASE A - Unfiltered search")
    query_a = "financial support for farmers income"
    print(f"\n  Query : \"{query_a}\"")
    print(f"  Filter: None (full corpus)")
    results_a = retriever.retrieve(query_a, top_k=3)
    _print_results("Unfiltered", results_a)

    # -- Case B: Filter by scheme -------------------------------------------
    _separator("CASE B - Filter by scheme = 'pmkisan'")
    query_b = "financial support for farmers income"
    filter_b = {"scheme": "pmkisan"}
    print(f"\n  Query : \"{query_b}\"")
    print(f"  Filter: {json.dumps(filter_b)}")
    comparison_b = retriever.compare_filtered_unfiltered(query_b, filter_b, top_k=3)
    _print_results("Filtered (pmkisan)", comparison_b["filtered"])
    _print_results("Unfiltered (full)", comparison_b["unfiltered"])
    if comparison_b["delta_ids"]:
        print(f"\n  [NOTE] IDs present in unfiltered but removed by filter: {comparison_b['delta_ids']}")

    # -- Case C: Filter by source document ---------------------------------
    _separator("CASE C - Filter by source = 'housing_guide.md'")
    query_c = "housing loan subsidy eligibility"
    filter_c = {"source": "housing_guide.md"}
    print(f"\n  Query : \"{query_c}\"")
    print(f"  Filter: {json.dumps(filter_c)}")
    results_c = retriever.retrieve(query_c, top_k=3, metadata_filter=filter_c)
    results_c_unfilt = retriever.retrieve(query_c, top_k=3)
    _print_results("Filtered (housing_guide.md)", results_c)
    _print_results("Unfiltered (full)", results_c_unfilt)

    # -- Case D: Combined $and filter --------------------------------------
    _separator("CASE D - Combined filter: scheme=pmjay AND section=Eligibility")
    query_d = "who is eligible for health insurance scheme"
    filter_d = {"$and": [{"scheme": {"$eq": "pmjay"}}, {"section": {"$eq": "Eligibility"}}]}
    print(f"\n  Query : \"{query_d}\"")
    print(f"  Filter: {json.dumps(filter_d)}")
    results_d = retriever.retrieve(query_d, top_k=3, metadata_filter=filter_d)
    _print_results("Filtered (pmjay + Eligibility)", results_d)

    # -- Summary -----------------------------------------------------------
    _separator("SUMMARY")
    print(f"\n  {'Case':<8} {'Query':<35} {'Filter scope':<22} {'Results'}")
    print(f"  {'-------'} {'----------------------------------'} {'---------------------'} {'-------'}")
    print(f"  {'A':<8} {query_a[:33]:<35} {'none':<22} {len(results_a)}")
    print(f"  {'B':<8} {query_b[:33]:<35} {'scheme=pmkisan':<22} {len(comparison_b['filtered'])}")
    print(f"  {'C':<8} {query_c[:33]:<35} {'source=housing_guide':<22} {len(results_c)}")
    print(f"  {'D':<8} {query_d[:33]:<35} {'pmjay+Eligibility':<22} {len(results_d)}")
    print()
    print("  [OK] Experiment complete.")
    print("=" * 72)


if __name__ == "__main__":
    run_experiment()
