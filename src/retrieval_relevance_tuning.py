# -*- coding: utf-8 -*-
"""
retrieval_relevance_tuning.py - 3.34 Retrieval Relevance Tuning
================================================================
Runs a structured tuning experiment that compares multiple retrieval
configurations against a fixed set of test queries with known expected
sources.  Works completely offline - no OpenAI API key is required.

Usage:
    python src/retrieval_relevance_tuning.py

What it does:
  1. Builds an in-memory VectorStore with 12 welfare-scheme chunks
     spanning 4 source documents (each with doc_type, scheme, section).
  2. Runs 8 test queries, each carrying a ground-truth expected_source.
  3. Evaluates 5 retrieval settings that vary k, min_score, and alpha/beta.
  4. Computes hit_rate (expected source in any result) and
     top1_hit_rate (expected source is rank-1).
  5. Picks the best-performing setting with written justification.
  6. Prints a formatted summary table and saves JSON to outputs/.

Settings compared
-----------------
  baseline_k3      k=3, no filter, min_score=0.0, alpha=0.7 beta=0.3
  wider_k5         k=5, no filter, min_score=0.0, alpha=0.7 beta=0.3
  strict_threshold k=5, no filter, min_score=0.30, alpha=0.7 beta=0.3
  keyword_heavy    k=5, no filter, min_score=0.0, alpha=0.4 beta=0.6
  vector_only      k=5, no filter, min_score=0.0, alpha=1.0 beta=0.0
"""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.vector_store import VectorStore
from src.retrieval import HybridRetriever, _keyword_score
from src.embeddings import DeterministicSemanticVectorizer

# ---------------------------------------------------------------------------
# Offline embedding setup (1536-dim, no API key needed)
# ---------------------------------------------------------------------------

_vectorizer = DeterministicSemanticVectorizer(dimension=1536)


def embed_fn(text: str):
    return _vectorizer.embed_text(text)


# ---------------------------------------------------------------------------
# Corpus  (12 chunks, 4 source documents)
# ---------------------------------------------------------------------------

CORPUS = [
    # -- pmkisan_guide.md --
    {
        "id": "pmkisan:elig:1",
        "text": (
            "PM-KISAN provides income support of Rs 6000 per year to all small and "
            "marginal farmer families who own cultivable land."
        ),
        "metadata": {
            "source": "pmkisan_guide.md",
            "scheme": "pmkisan",
            "section": "Eligibility",
            "doc_type": "guide",
        },
    },
    {
        "id": "pmkisan:pay:2",
        "text": (
            "PM-KISAN payment of Rs 6000 per year is released in three equal "
            "installments of Rs 2000 each directly to the farmer bank account."
        ),
        "metadata": {
            "source": "pmkisan_guide.md",
            "scheme": "pmkisan",
            "section": "Payment",
            "doc_type": "guide",
        },
    },
    {
        "id": "pmkisan:exclusion:3",
        "text": (
            "Institutional land holders, constitutional post holders, and income "
            "tax payers are excluded from PM-KISAN benefits."
        ),
        "metadata": {
            "source": "pmkisan_guide.md",
            "scheme": "pmkisan",
            "section": "Exclusions",
            "doc_type": "guide",
        },
    },
    # -- ayushman_guide.md --
    {
        "id": "pmjay:cover:1",
        "text": (
            "Ayushman Bharat PM-JAY covers up to Rs 5 lakh per family per year "
            "for secondary and tertiary hospitalisation across empanelled hospitals."
        ),
        "metadata": {
            "source": "ayushman_guide.md",
            "scheme": "pmjay",
            "section": "Coverage",
            "doc_type": "guide",
        },
    },
    {
        "id": "pmjay:elig:2",
        "text": (
            "Families identified as economically weaker sections through the SECC "
            "2011 database are eligible for PM-JAY Ayushman Bharat health scheme."
        ),
        "metadata": {
            "source": "ayushman_guide.md",
            "scheme": "pmjay",
            "section": "Eligibility",
            "doc_type": "guide",
        },
    },
    {
        "id": "pmjay:process:3",
        "text": (
            "Beneficiaries can avail cashless treatment at any empanelled hospital "
            "by showing the PM-JAY e-card or Ayushman Card issued by the government."
        ),
        "metadata": {
            "source": "ayushman_guide.md",
            "scheme": "pmjay",
            "section": "Process",
            "doc_type": "guide",
        },
    },
    # -- housing_guide.md --
    {
        "id": "pmay:subsidy:1",
        "text": (
            "Pradhan Mantri Awas Yojana provides an interest subsidy of 6.5 percent "
            "on home loans for economically weaker sections and low income groups."
        ),
        "metadata": {
            "source": "housing_guide.md",
            "scheme": "pmay",
            "section": "Subsidy",
            "doc_type": "guide",
        },
    },
    {
        "id": "pmay:elig:2",
        "text": (
            "Families eligible for PMAY Urban must not own a pucca house anywhere "
            "in India and must belong to EWS, LIG, or MIG categories."
        ),
        "metadata": {
            "source": "housing_guide.md",
            "scheme": "pmay",
            "section": "Eligibility",
            "doc_type": "guide",
        },
    },
    {
        "id": "pmay:component:3",
        "text": (
            "PMAY has four components: in-situ slum redevelopment, credit linked "
            "subsidy scheme, affordable housing in partnership, and beneficiary-led "
            "individual house construction."
        ),
        "metadata": {
            "source": "housing_guide.md",
            "scheme": "pmay",
            "section": "Components",
            "doc_type": "guide",
        },
    },
    # -- pension_guide.md --
    {
        "id": "nps:overview:1",
        "text": (
            "The National Pension System (NPS) is a voluntary retirement savings "
            "scheme that allows subscribers to contribute regularly during their "
            "working life and build a retirement corpus."
        ),
        "metadata": {
            "source": "pension_guide.md",
            "scheme": "nps",
            "section": "Overview",
            "doc_type": "reference",
        },
    },
    {
        "id": "nps:contribution:2",
        "text": (
            "NPS subscribers must contribute a minimum of Rs 1000 per year to Tier-I "
            "account. Government employees contribute 10 percent of basic salary and "
            "receive a matching 14 percent employer contribution."
        ),
        "metadata": {
            "source": "pension_guide.md",
            "scheme": "nps",
            "section": "Contribution",
            "doc_type": "reference",
        },
    },
    {
        "id": "nps:benefits:3",
        "text": (
            "At retirement, NPS subscribers can withdraw 60 percent of the corpus as "
            "a lump sum while the remaining 40 percent is used to purchase an annuity "
            "that provides a regular monthly pension."
        ),
        "metadata": {
            "source": "pension_guide.md",
            "scheme": "nps",
            "section": "Benefits",
            "doc_type": "reference",
        },
    },
]

# ---------------------------------------------------------------------------
# Test queries  (8 queries, known expected sources)
# ---------------------------------------------------------------------------

TEST_QUERIES = [
    {
        "query": "How do small farmers receive income support under PM-KISAN?",
        "expected_source": "pmkisan_guide.md",
    },
    {
        "query": "What is the annual payment amount and installment schedule under PM-KISAN?",
        "expected_source": "pmkisan_guide.md",
    },
    {
        "query": "Which families are covered under Ayushman Bharat health scheme?",
        "expected_source": "ayushman_guide.md",
    },
    {
        "query": "What is the hospitalisation coverage limit under PM-JAY?",
        "expected_source": "ayushman_guide.md",
    },
    {
        "query": "How does the housing loan interest subsidy work under PMAY?",
        "expected_source": "housing_guide.md",
    },
    {
        "query": "Who is eligible for the Pradhan Mantri Awas Yojana urban scheme?",
        "expected_source": "housing_guide.md",
    },
    {
        "query": "How does the National Pension System help build a retirement corpus?",
        "expected_source": "pension_guide.md",
    },
    {
        "query": "What are the minimum contribution rules for NPS subscribers?",
        "expected_source": "pension_guide.md",
    },
]

# ---------------------------------------------------------------------------
# Retrieval settings to compare
# ---------------------------------------------------------------------------

SETTINGS = [
    {
        "name": "baseline_k3",
        "k": 3,
        "filter": None,
        "min_score": 0.0,
        "alpha": 0.7,
        "beta": 0.3,
        "description": "Default: k=3, hybrid 0.7/0.3, no score gate",
    },
    {
        "name": "wider_k5",
        "k": 5,
        "filter": None,
        "min_score": 0.0,
        "alpha": 0.7,
        "beta": 0.3,
        "description": "Wider net: k=5, same hybrid weights",
    },
    {
        "name": "strict_threshold",
        "k": 5,
        "filter": None,
        "min_score": 0.30,
        "alpha": 0.7,
        "beta": 0.3,
        "description": "Score-gated: k=5, only keep hybrid_score >= 0.30",
    },
    {
        "name": "keyword_heavy",
        "k": 5,
        "filter": None,
        "min_score": 0.0,
        "alpha": 0.4,
        "beta": 0.6,
        "description": "Keyword-heavy: k=5, alpha=0.4 beta=0.6",
    },
    {
        "name": "vector_only",
        "k": 5,
        "filter": None,
        "min_score": 0.0,
        "alpha": 1.0,
        "beta": 0.0,
        "description": "Vector-only: k=5, alpha=1.0 beta=0.0",
    },
]

# ---------------------------------------------------------------------------
# Evaluation engine
# ---------------------------------------------------------------------------

def build_retriever(setting: dict, vs: VectorStore) -> HybridRetriever:
    """Creates a HybridRetriever with alpha/beta from the given setting."""
    return HybridRetriever(
        vector_store=vs,
        embed_fn=embed_fn,
        alpha=setting["alpha"],
        beta=setting["beta"],
    )


def evaluate(setting: dict, vs: VectorStore) -> list:
    """
    Runs all TEST_QUERIES against the given setting.

    Returns a list of row dicts, one per query, containing:
      query, expected_source, returned_sources, top1_source,
      hit (bool), top1_hit (bool), kept_count, scores
    """
    retriever = build_retriever(setting, vs)
    rows = []

    for item in TEST_QUERIES:
        results = retriever.retrieve(
            query=item["query"],
            top_k=setting["k"],
            metadata_filter=setting.get("filter"),
        )

        # Apply score threshold filter
        kept = [r for r in results if r["hybrid_score"] >= setting["min_score"]]

        sources = [r["metadata"].get("source", "") for r in kept]
        top1_source = sources[0] if sources else ""
        hit = item["expected_source"] in sources
        top1_hit = (top1_source == item["expected_source"])

        rows.append({
            "query": item["query"],
            "expected_source": item["expected_source"],
            "returned_sources": sources,
            "top1_source": top1_source,
            "hit": hit,
            "top1_hit": top1_hit,
            "kept_count": len(kept),
            "scores": [round(r["hybrid_score"], 4) for r in kept],
        })

    return rows


def compute_metrics(rows: list) -> dict:
    """Computes hit_rate and top1_hit_rate from evaluate() output."""
    total = len(rows)
    hits = sum(1 for r in rows if r["hit"])
    top1_hits = sum(1 for r in rows if r["top1_hit"])
    avg_kept = sum(r["kept_count"] for r in rows) / total if total else 0
    return {
        "hit_rate": round(hits / total, 3) if total else 0.0,
        "top1_hit_rate": round(top1_hits / total, 3) if total else 0.0,
        "avg_kept": round(avg_kept, 2),
        "total_queries": total,
        "hits": hits,
        "top1_hits": top1_hits,
    }


def pick_best_setting(summary: list) -> dict:
    """
    Selects the best setting by:
      1. Highest hit_rate
      2. Highest top1_hit_rate (tie-break)
      3. Highest avg_kept (second tie-break – more context is safer)
    Returns the winning summary entry.
    """
    return max(
        summary,
        key=lambda s: (
            s["metrics"]["hit_rate"],
            s["metrics"]["top1_hit_rate"],
            s["metrics"]["avg_kept"],
        ),
    )


# ---------------------------------------------------------------------------
# Report helpers
# ---------------------------------------------------------------------------

def _bar(rate: float, width: int = 20) -> str:
    filled = round(rate * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def print_summary(summary: list, best: dict):
    print()
    print("=" * 74)
    print("  3.34 Retrieval Relevance Tuning - Results")
    print("=" * 74)
    print(
        f"  {'Setting':<20} {'hit_rate':>9} {'top1_rate':>10} "
        f"{'avg_kept':>9}  {'bar (hit_rate)'}"
    )
    print("  " + "-" * 72)

    for row in sorted(summary, key=lambda s: -s["metrics"]["hit_rate"]):
        marker = " <-- BEST" if row["setting"] == best["setting"] else ""
        m = row["metrics"]
        print(
            f"  {row['setting']:<20} "
            f"{m['hit_rate']:>8.1%} "
            f"{m['top1_hit_rate']:>9.1%} "
            f"{m['avg_kept']:>9.1f}  "
            f"{_bar(m['hit_rate'])}"
            f"{marker}"
        )

    print()
    print(f"  Best setting : {best['setting']}")
    print(f"  Description  : {best['description']}")
    print()
    print("  Justification")
    print("  " + "-" * 50)
    _print_justification(best, summary)
    print()
    print("=" * 74)


def _print_justification(best: dict, summary: list):
    """Prints a written justification for the chosen setting."""
    m = best["metrics"]
    baseline = next(s for s in summary if s["setting"] == "baseline_k3")
    bm = baseline["metrics"]

    lines = [
        f"  '{best['setting']}' achieved the highest hit_rate of "
        f"{m['hit_rate']:.1%} ({m['hits']}/{m['total_queries']} queries).",
    ]

    if best["setting"] != "baseline_k3":
        delta_hit = m["hit_rate"] - bm["hit_rate"]
        delta_top1 = m["top1_hit_rate"] - bm["top1_hit_rate"]
        sign_hit = "+" if delta_hit >= 0 else ""
        sign_top1 = "+" if delta_top1 >= 0 else ""
        lines.append(
            f"  Compared to baseline_k3: hit_rate {sign_hit}{delta_hit:.1%}, "
            f"top1_hit_rate {sign_top1}{delta_top1:.1%}."
        )

    lines += [
        f"  top1_hit_rate of {m['top1_hit_rate']:.1%} means the correct source "
        "ranked first for that fraction of queries,",
        "  which directly reduces LLM hallucination by ensuring the best chunk",
        "  appears at the top of the context window.",
        f"  avg_kept={m['avg_kept']:.1f} chunks per query keeps context cost reasonable.",
    ]

    if best["setting"] == "strict_threshold":
        lines.append(
            "  The score gate (min_score=0.30) filters noisy low-confidence results"
            " that would otherwise dilute the context."
        )
    elif best["setting"] == "keyword_heavy":
        lines.append(
            "  Increasing beta to 0.6 rewards exact scheme name and term matches,"
            " which is important for welfare policy queries."
        )
    elif best["setting"] == "vector_only":
        lines.append(
            "  Pure vector scoring (alpha=1.0) works well here because the"
            " DeterministicSemanticVectorizer captures topic similarity reliably."
        )
    elif best["setting"] == "wider_k5":
        lines.append(
            "  Increasing k from 3 to 5 provides a wider recall net without"
            " significantly inflating context size."
        )
    else:
        lines.append(
            "  The default hybrid weights (0.7/0.3) balance semantic and lexical"
            " signals well for this welfare-scheme corpus."
        )

    for line in lines:
        print(line)


def print_per_query_detail(summary: list, setting_name: str):
    """Prints per-query detail rows for the chosen best setting."""
    entry = next(s for s in summary if s["setting"] == setting_name)
    print(f"\n  Per-query detail for '{setting_name}':")
    print("  " + "-" * 68)
    for row in entry["details"]:
        hit_icon = "[HIT]" if row["hit"] else "[---]"
        top1_icon = "[TOP1]" if row["top1_hit"] else "     "
        q_short = row["query"][:50] + "..." if len(row["query"]) > 50 else row["query"]
        print(f"  {hit_icon} {top1_icon}  {q_short}")
        print(f"           expected : {row['expected_source']}")
        print(f"           returned : {row['returned_sources']}")
    print()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_tuning():
    # Build in-memory VectorStore
    vs = VectorStore(in_memory=True, collection_name="tuning_34", dimension=1536)
    vs.reset_collection()
    for doc in CORPUS:
        vs.upsert_record(
            record_id=doc["id"],
            vector=embed_fn(doc["text"]),
            text=doc["text"],
            metadata=doc["metadata"],
        )

    print(f"[INFO] Indexed {vs.count()} chunks | {len(TEST_QUERIES)} test queries | "
          f"{len(SETTINGS)} settings")

    # Run evaluation across all settings
    summary = []
    for setting in SETTINGS:
        rows = evaluate(setting, vs)
        metrics = compute_metrics(rows)
        summary.append({
            "setting": setting["name"],
            "description": setting["description"],
            "config": {k: v for k, v in setting.items() if k not in ("name", "description")},
            "metrics": metrics,
            "details": rows,
        })

    best = pick_best_setting(summary)

    # Print results
    print_summary(summary, best)
    print_per_query_detail(summary, best["setting"])

    # Save JSON output
    os.makedirs("outputs", exist_ok=True)
    output_path = os.path.join("outputs", "retrieval_tuning_results.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "experiment": "3.34 Retrieval Relevance Tuning",
                "corpus_size": len(CORPUS),
                "test_query_count": len(TEST_QUERIES),
                "best_setting": best["setting"],
                "best_metrics": best["metrics"],
                "summary": [
                    {
                        "setting": s["setting"],
                        "description": s["description"],
                        "config": s["config"],
                        "metrics": s["metrics"],
                    }
                    for s in summary
                ],
                "details": {
                    s["setting"]: s["details"] for s in summary
                },
            },
            f,
            indent=2,
        )
    print(f"  [OK] Results saved to {output_path}")

    return summary, best


if __name__ == "__main__":
    run_tuning()
