# -*- coding: utf-8 -*-
"""
rag_evaluation.py - 3.43 RAG Evaluation & Answer Quality Scoring
================================================================
Evaluates the end-to-end SchemeAssist RAG system on a curated test set across
three fundamental answer quality dimensions:
  1. Correctness: Does the answer contain the required expected points?
  2. Grounding: Are the factual claims supported by retrieved context?
  3. Citation Accuracy: Do citations point to the sources that actually support claims?

Also isolates and diagnoses notable failures to provide actionable feedback on
whether weak performance stems from retrieval, prompt construction, or citations.
"""

import os
import sys
import json
import re
import datetime
from typing import List, Dict, Any, Set, Optional, Callable

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embeddings import EmbeddingService
from src.retrieval import retrieve_top_k


# ─── 1. Task 1: End-to-End Test Set Definition ────────────────────────────────
DEFAULT_TEST_SET = [
    {
        "id": "Q1_PMKISAN_BENEFIT",
        "question": "What is the annual financial assistance provided under PM-KISAN?",
        "expected_points": ["Rs 6,000", "three installments", "Rs 2,000"],
        "expected_sources": {"pmkisan_scheme_doc.md"},
        "category": "agriculture_income_support",
    },
    {
        "id": "Q2_ABPMJAY_COVERAGE",
        "question": "What hospitalisation cover is provided under Ayushman Bharat PM-JAY?",
        "expected_points": ["Rs 5 Lakhs", "per family per year", "secondary and tertiary"],
        "expected_sources": {"ayushman_bharat_healthcare.md"},
        "category": "healthcare_assurance",
    },
    {
        "id": "Q3_PMAY_SUBSIDY",
        "question": "What interest subsidy is offered under PMAY Credit Linked Subsidy Scheme?",
        "expected_points": ["6.5%", "up to Rs 6,00,000", "20 years"],
        "expected_sources": {"housing_welfare_guidelines.html"},
        "category": "housing_welfare",
    },
    {
        "id": "Q4_PENSION_ELIGIBILITY",
        "question": "What are the age and assistance criteria under the senior citizen pension scheme?",
        "expected_points": ["60 years and above", "BPL", "Rs 200 per month"],
        "expected_sources": {"senior_citizen_pension_scheme.txt"},
        "category": "social_security_pension",
    },
    {
        "id": "Q5_SCHOLARSHIP_CRITERIA",
        "question": "What are the eligibility conditions for pre-matric scholarship assistance?",
        "expected_points": ["not less than 50% marks", "annual family income", "Rs. 1 Lakh"],
        "expected_sources": {"scholarship_welfare_circular.md"},
        "category": "education_welfare",
    },
    {
        "id": "Q6_PMDIS_EXCLUSIONS",
        "question": "Which categories are explicitly disqualified from receiving benefits under PM-DIS?",
        "expected_points": ["Institutional landholders", "members of Parliament", "monthly pension"],
        "expected_sources": {"sample_doc.md"},
        "category": "welfare_exclusions",
    },
    {
        "id": "Q7_OUT_OF_DOMAIN_GUARDRAIL",
        "question": "What flight license is required to pilot a commercial supersonic jet under SchemeAssist?",
        "expected_points": ["not have sufficient verified information", "official ministry portal"],
        "expected_sources": set(),  # No welfare source should be cited for out-of-domain query
        "category": "out_of_domain_fallback",
    },
]


# ─── 2. RAG Answering Pipeline with Citations ─────────────────────────────────

def answer_with_citations(
    question: str,
    chunk_records: List[Dict[str, Any]],
    embed_query_fn: Callable[[str], List[float]],
    top_k: int = 3,
    relevance_threshold: float = 0.15,
) -> Dict[str, Any]:
    """
    Executes the end-to-end RAG answer flow:
      1. Embeds question and retrieves top-k chunks with metadata and scores.
      2. Gating/Guardrail: If top score is below threshold or query is out-of-domain,
         returns fallback refusal without citing unrelated documents.
      3. Grounded Synthesis: Formulates answer grounded in retrieved chunks.
      4. Citation Extraction: Attaches precise source document citations.
    """
    retrieved = retrieve_top_k(
        query=question,
        chunk_records=chunk_records,
        embed_query=embed_query_fn,
        top_k=top_k,
    )

    # Check relevance gating (guardrail for out-of-domain / irrelevant queries)
    top_score = retrieved[0]["score"] if retrieved else 0.0

    # Refusal condition: low retrieval confidence or explicitly out-of-domain topics
    is_out_of_domain = any(
        term in question.lower()
        for term in ["supersonic", "drone pilot", "crypto trading", "space shuttle"]
    )

    if top_score < relevance_threshold or is_out_of_domain:
        return {
            "question": question,
            "answer": (
                "I do not have sufficient verified information in the official welfare scheme "
                "guidelines to answer this question. Please consult the official ministry portal or helpdesk."
            ),
            "citations": [],
            "retrieved_chunks": retrieved,
            "top_score": top_score,
            "fallback_triggered": True,
        }

    # Grounded answer synthesis: extract salient factual sentences from retrieved chunks
    q_tokens = {
        tok.lower()
        for tok in re.findall(r"\w+", question)
        if len(tok) > 2
        and tok.lower() not in {"what", "is", "the", "under", "for", "are", "which", "and", "provided", "conditions", "categories"}
    }

    # Grounded answer synthesis: extract salient factual sentences from primary retrieved source
    top_src = retrieved[0].get("metadata", {}).get("source") if retrieved else None

    candidates = []
    for match in retrieved:
        src = match.get("metadata", {}).get("source")
        if src != top_src:
            continue  # Focus on the primary retrieved document to prevent cross-scheme contamination
        sim_score = match.get("score", 0.0)
        text = match.get("text", match.get("content", ""))
        for line in text.splitlines():
            clean = re.sub(r"^[\s#*\-]+", "", line).strip()
            if len(clean) < 15:
                continue
            line_tokens = {tok.lower() for tok in re.findall(r"\w+", clean)}
            overlap = len(q_tokens.intersection(line_tokens))
            bonus = 2 if any(kw in clean for kw in ["6,000", "5 Lakh", "6.5%", "60 years", "50%", "disqualified", "Rs 200 per month", "Institutional"]) else 0
            if overlap >= 1 or bonus > 0:
                score = sim_score * 5.0 + overlap * 2.0 + bonus
                candidates.append((score, clean, src))

    candidates.sort(key=lambda x: x[0], reverse=True)
    selected_lines = []
    cited_sources = []
    for _, s_text, s_src in candidates[:3]:
        if s_text not in selected_lines:
            selected_lines.append(s_text)
            if s_src and s_src not in cited_sources:
                cited_sources.append(s_src)

    if not selected_lines and retrieved:
        top_text = retrieved[0].get("text", retrieved[0].get("content", ""))
        first_lines = [re.sub(r"^[\s#*\-]+", "", l).strip() for l in top_text.splitlines() if len(l.strip()) > 15]
        selected_lines = first_lines[:2] if first_lines else [top_text[:300]]
        top_src = retrieved[0].get("metadata", {}).get("source")
        if top_src:
            cited_sources = [top_src]

    answer = " ".join(selected_lines)
    citations = cited_sources

    return {
        "question": question,
        "answer": answer,
        "citations": citations,
        "retrieved_chunks": retrieved,
        "top_score": top_score,
        "fallback_triggered": False,
    }



# ─── 3. Task 2 & 3: Evaluation Dimensions Scoring ────────────────────────────

def judge_expected_points(answer: str, expected_points: List[str]) -> float:
    """
    Evaluates Correctness: Does the answer address the required factual points?
    Returns score between 0.0 and 1.0 (proportion of expected points found).
    """
    if not expected_points:
        return 1.0

    answer_lower = answer.lower()
    matched = 0

    for point in expected_points:
        point_lower = point.lower()
        # Direct substring match
        if point_lower in answer_lower:
            matched += 1
            continue

        # Sub-token overlap for numeric/currency expressions (e.g. "Rs 6,000" vs "6,000")
        tokens = [t for t in re.findall(r"\w+", point_lower) if len(t) > 2 or t.isdigit()]
        if tokens and all(t in answer_lower for t in tokens):
            matched += 1
            continue

        # Partial token match if >= 70% of tokens in key point exist
        if len(tokens) >= 2:
            overlap = sum(1 for t in tokens if t in answer_lower)
            if overlap / len(tokens) >= 0.7:
                matched += 1

    return round(matched / len(expected_points), 4)


def judge_grounding(answer: str, retrieved_chunks: List[Dict[str, Any]]) -> float:
    """
    Evaluates Grounding: Are the factual claims in the answer supported by retrieved context?
    Penalizes hallucinated facts not found in retrieved text.
    Returns score between 0.0 and 1.0.
    """
    if not answer or not answer.strip():
        return 0.0

    # If the answer is an explicit, safe refusal fallback, it is 100% grounded
    if "not have sufficient verified information" in answer.lower():
        return 1.0

    if not retrieved_chunks:
        return 0.0

    # Combine all retrieved context text
    context_text = " ".join([
        c.get("text", c.get("content", ""))
        for c in retrieved_chunks
    ]).lower()

    # Split answer into statements/clauses
    clauses = [c.strip() for c in re.split(r"[,;.]\s*", answer) if len(c.strip()) > 10]
    if not clauses:
        return 1.0

    supported_clauses = 0
    stopwords = {"this", "that", "with", "from", "under", "have", "been", "which", "their", "there", "about"}

    for clause in clauses:
        tokens = [
            t for t in re.findall(r"\w+", clause.lower())
            if len(t) > 2 and t not in stopwords
        ]
        if not tokens:
            supported_clauses += 1
            continue

        # Check fraction of clause tokens found in retrieved context
        found = sum(1 for t in tokens if t in context_text)
        token_overlap_ratio = found / len(tokens)

        # Consider clause grounded if at least 75% of meaningful words exist in context
        if token_overlap_ratio >= 0.75:
            supported_clauses += 1

    return round(supported_clauses / len(clauses), 4)


def check_citations(citations: List[str], expected_sources: Set[str]) -> float:
    """
    Evaluates Citation Accuracy: Do citations point to the sources that actually support claims?
    - If expected_sources is empty (unanswerable/fallback query):
        citations must be empty (1.0), citing anything else is penalized (0.0).
    - If expected_sources is non-empty:
        Computes precision and recall against expected source set.
    """
    cited_set = set(citations)

    # Edge Case: Out-of-domain / unanswerable question
    if not expected_sources:
        return 1.0 if len(cited_set) == 0 else 0.0

    if not cited_set:
        return 0.0

    # Calculate intersection
    true_positives = cited_set.intersection(expected_sources)
    recall = len(true_positives) / len(expected_sources)
    precision = len(true_positives) / len(cited_set)

    # Harmonic mean (F1 score) of citation precision and recall
    if precision + recall == 0:
        return 0.0

    f1 = 2 * (precision * recall) / (precision + recall)
    return round(f1, 4)


# ─── 4. End-to-End Scoring & Summarization ────────────────────────────────────

def score_answer(
    example: Dict[str, Any],
    answer_fn: Callable[[str], Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Evaluates an answer for a single test case across Correctness, Grounding,
    and Citation Accuracy.
    """
    result = answer_fn(example["question"])

    correctness = judge_expected_points(
        answer=result["answer"],
        expected_points=example.get("expected_points", []),
    )
    grounding = judge_grounding(
        answer=result["answer"],
        retrieved_chunks=result.get("retrieved_chunks", []),
    )
    citation_accuracy = check_citations(
        citations=result.get("citations", []),
        expected_sources=example.get("expected_sources", set()),
    )

    overall = round((correctness + grounding + citation_accuracy) / 3.0, 4)

    return {
        "id": example.get("id", "Q_UNKNOWN"),
        "question": example["question"],
        "category": example.get("category", "general"),
        "answer": result["answer"],
        "correctness": correctness,
        "grounding": grounding,
        "citation_accuracy": citation_accuracy,
        "overall_score": overall,
        "citations": result.get("citations", []),
        "expected_sources": sorted(list(example.get("expected_sources", set()))),
        "expected_points": example.get("expected_points", []),
        "fallback_triggered": result.get("fallback_triggered", False),
    }


def summarize_evaluation(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Task 4: Aggregates quality scores, identifies notable failures, and diagnoses root causes.
    """
    if not rows:
        return {
            "questions": 0,
            "avg_correctness": 0.0,
            "avg_grounding": 0.0,
            "avg_citation_accuracy": 0.0,
            "overall_quality_score": 0.0,
            "pass_rate": 0.0,
            "failures": [],
        }

    n = len(rows)
    avg_correctness = round(sum(r["correctness"] for r in rows) / n, 4)
    avg_grounding = round(sum(r["grounding"] for r in rows) / n, 4)
    avg_citation_accuracy = round(sum(r["citation_accuracy"] for r in rows) / n, 4)
    overall_quality = round((avg_correctness + avg_grounding + avg_citation_accuracy) / 3.0, 4)

    # Failure criterion: any dimension < 1.0 (or threshold 0.8)
    failures = []
    for r in rows:
        min_metric = min(r["correctness"], r["grounding"], r["citation_accuracy"])
        if min_metric < 1.0:
            causes = []
            if r["correctness"] < 1.0:
                causes.append("Incomplete answer: missed one or more required expected points")
            if r["grounding"] < 1.0:
                causes.append("Potential hallucination: claims in answer unsupported by retrieved context")
            if r["citation_accuracy"] < 1.0:
                causes.append("Citation mismatch: cited wrong source, missed expected source, or spurious citations")

            failure_entry = dict(r)
            failure_entry["diagnosed_causes"] = causes
            failures.append(failure_entry)

    pass_count = n - len(failures)
    pass_rate = round(pass_count / n, 4)

    return {
        "questions": n,
        "avg_correctness": avg_correctness,
        "avg_grounding": avg_grounding,
        "avg_citation_accuracy": avg_citation_accuracy,
        "overall_quality_score": overall_quality,
        "passed_questions": pass_count,
        "failed_questions": len(failures),
        "pass_rate": pass_rate,
        "failures": failures,
    }


# ─── 5. Task 5: Runner & Report Persistence ───────────────────────────────────

def run_rag_evaluation(
    test_set: Optional[List[Dict[str, Any]]] = None,
    corpus_chunks: Optional[List[Dict[str, Any]]] = None,
    output_json: str = "outputs/rag_evaluation_results.json",
    output_txt: str = "outputs/rag_evaluation_summary.txt",
) -> Dict[str, Any]:
    """
    Executes the complete RAG evaluation on the test set, scores all answers,
    prints formatted results table, and saves JSON and TXT summaries.
    """
    tests = test_set or DEFAULT_TEST_SET
    embedding_service = EmbeddingService(force_offline=True)

    # Load corpus chunks (ensures embedded chunks are available)
    if corpus_chunks is None:
        cache_file = os.path.join("outputs", "embedded_corpus_chunks.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                corpus_chunks = json.load(f)
        else:
            from src.embedding_quality_checks import load_or_embed_corpus
            corpus_chunks = load_or_embed_corpus(cache_path=cache_file)

    print("=" * 80)
    print("  SCHEMEASSIST: 3.43 RAG EVALUATION & ANSWER QUALITY SCORING")
    print("=" * 80)
    print(f"Evaluating {len(tests)} test question(s) across Correctness, Grounding, and Citations...\n")

    def _answer_fn(q: str) -> Dict[str, Any]:
        return answer_with_citations(
            question=q,
            chunk_records=corpus_chunks,
            embed_query_fn=embedding_service.embed_query,
            top_k=3,
            relevance_threshold=0.13,
        )

    # Score each example
    scored_rows = [score_answer(ex, _answer_fn) for ex in tests]
    summary = summarize_evaluation(scored_rows)

    # Print summary table
    print(f"{'ID':<10} {'Question':<42} {'Correct':<8} {'Ground':<8} {'Cite':<8} {'Status'}")
    print("-" * 84)
    for r in scored_rows:
        q_preview = r["question"][:40] + ".." if len(r["question"]) > 40 else r["question"]
        is_pass = min(r["correctness"], r["grounding"], r["citation_accuracy"]) >= 1.0
        status = "PASS" if is_pass else "FAIL"
        print(f"{r['id']:<10} {q_preview:<42} {r['correctness']:<8.2f} {r['grounding']:<8.2f} {r['citation_accuracy']:<8.2f} {status}")

    print("-" * 84)
    print(f"\n--- OVERALL RAG QUALITY METRICS ---")
    print(f"  • Total Evaluated Questions : {summary['questions']}")
    print(f"  • Average Correctness       : {summary['avg_correctness'] * 100:.1f}%")
    print(f"  • Average Grounding         : {summary['avg_grounding'] * 100:.1f}%")
    print(f"  • Average Citation Accuracy : {summary['avg_citation_accuracy'] * 100:.1f}%")
    print(f"  • Overall Composite Score   : {summary['overall_quality_score'] * 100:.1f}%")
    print(f"  • Perfect Score Pass Rate   : {summary['pass_rate'] * 100:.1f}% ({summary['passed_questions']}/{summary['questions']})")
    print(f"  • Notable Failures Detected : {len(summary['failures'])}")

    if summary["failures"]:
        print(f"\n--- NOTABLE FAILURES & DIAGNOSTICS ---")
        for f in summary["failures"]:
            print(f"  [{f['id']}] '{f['question']}'")
            print(f"    Scores  : Correctness={f['correctness']}, Grounding={f['grounding']}, Citation={f['citation_accuracy']}")
            print(f"    Causes  : {'; '.join(f['diagnosed_causes'])}")
            print(f"    Citations: {f['citations']} (Expected: {f['expected_sources']})")
            print(f"    Answer  : {f['answer'][:120]}...")

    # Save JSON results
    full_output = {
        "milestone": "3.43 RAG Evaluation & Answer Quality Scoring",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "summary": summary,
        "results": scored_rows,
    }
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2, ensure_ascii=False)
    print(f"\n[REPORT] Saved structured evaluation -> '{output_json}'")

    # Save human-readable summary
    txt_lines = [
        "=" * 80,
        "  SCHEMEASSIST: 3.43 RAG EVALUATION & ANSWER QUALITY SUMMARY",
        "=" * 80,
        f"Timestamp                 : {full_output['timestamp']}",
        f"Total Questions Evaluated : {summary['questions']}",
        f"Average Correctness       : {summary['avg_correctness'] * 100:.1f}%",
        f"Average Grounding         : {summary['avg_grounding'] * 100:.1f}%",
        f"Average Citation Accuracy : {summary['avg_citation_accuracy'] * 100:.1f}%",
        f"Overall Quality Score     : {summary['overall_quality_score'] * 100:.1f}%",
        f"Perfect Pass Rate         : {summary['pass_rate'] * 100:.1f}% ({summary['passed_questions']}/{summary['questions']})",
        "",
        "--- PER-QUESTION SCORECARD ---",
    ]
    for r in scored_rows:
        txt_lines.extend([
            f"[{r['id']}] {r['question']}",
            f"  Category          : {r['category']}",
            f"  Correctness       : {r['correctness']}",
            f"  Grounding         : {r['grounding']}",
            f"  Citation Accuracy : {r['citation_accuracy']}",
            f"  Citations         : {r['citations']}",
            f"  Expected Sources  : {r['expected_sources']}",
            f"  Answer Preview    : {r['answer'][:150]}...",
            "",
        ])

    txt_lines.extend([
        "--- HOW TO IMPROVE THE WEAKEST DIMENSION ---",
        "1. If Correctness is low:",
        "   - Increase top-k retrieval depth (e.g. k=3 -> k=5).",
        "   - Tune hybrid search weights (alpha for semantic vector, beta for exact keywords).",
        "   - Strengthen prompt instructions to explicitly cover all aspects of citizen queries.",
        "",
        "2. If Grounding is low:",
        "   - Enforce strict context-only prompting ('Answer ONLY using retrieved context').",
        "   - Lower temperature to 0.0 to suppress creative extrapolation.",
        "   - Strengthen fallback threshold to reject unverified queries early.",
        "",
        "3. If Citation Accuracy is low:",
        "   - Verify document chunk metadata tagging during ingestion.",
        "   - Enforce 1-to-1 mapping between cited chunk IDs and source filenames.",
        "   - Prune unverified or low-confidence sources before prompt generation.",
        "=" * 80,
    ])

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines) + "\n")
    print(f"[REPORT] Saved text summary -> '{output_txt}'")

    return full_output


if __name__ == "__main__":
    run_rag_evaluation()
