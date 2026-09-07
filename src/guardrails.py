"""Retrieval-quality guardrails that refuse unsupported questions."""

from typing import Any, Callable, Dict, Iterable, List

from src.citations import FALLBACK_ANSWER, answer_with_citations

DEFAULT_MIN_TOP_SCORE = 0.72
DEFAULT_MIN_SUPPORTING_CHUNKS = 1
WEAK_CONTEXT_ANSWER = "I don't have enough reliable context to answer that."


def _score(chunk: Dict[str, Any]) -> float:
    """Read the common score names emitted by the retrieval pipeline."""
    for key in ("score", "similarity_score", "hybrid_score", "vector_score"):
        value = chunk.get(key)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0
    return 0.0


def retrieval_is_strong(
    chunks: Iterable[Dict[str, Any]],
    min_top_score: float = DEFAULT_MIN_TOP_SCORE,
    min_supporting_chunks: int = DEFAULT_MIN_SUPPORTING_CHUNKS,
) -> bool:
    """Return true only when enough retrieved chunks meet the score threshold."""
    chunk_list = list(chunks)
    if min_supporting_chunks < 1:
        raise ValueError("min_supporting_chunks must be at least 1")
    if min_top_score < -1.0 or min_top_score > 1.0:
        raise ValueError("min_top_score must be between -1.0 and 1.0")
    strong_chunks = [chunk for chunk in chunk_list if _score(chunk) >= min_top_score]
    return bool(chunk_list) and len(strong_chunks) >= min_supporting_chunks


def guarded_answer(
    question: str,
    chunks: Iterable[Dict[str, Any]],
    answer_fn: Callable[[str], str],
    *,
    min_top_score: float = DEFAULT_MIN_TOP_SCORE,
    min_supporting_chunks: int = DEFAULT_MIN_SUPPORTING_CHUNKS,
) -> Dict[str, Any]:
    """Refuse weak retrieval before generation and cite only strong answers."""
    source_chunks: List[Dict[str, Any]] = list(chunks)
    strong = retrieval_is_strong(
        source_chunks,
        min_top_score=min_top_score,
        min_supporting_chunks=min_supporting_chunks,
    )
    if not strong:
        return {
            "answer": WEAK_CONTEXT_ANSWER,
            "citations": [],
            "status": "refused_weak_context",
            "top_score": max((_score(chunk) for chunk in source_chunks), default=None),
            "supporting_chunks": sum(_score(chunk) >= min_top_score for chunk in source_chunks),
            "threshold": min_top_score,
        }

    result = answer_with_citations(question, source_chunks, answer_fn)
    if not result["citations"]:
        return {
            "answer": FALLBACK_ANSWER,
            "citations": [],
            "status": "refused_uncited_answer",
            "top_score": max(_score(chunk) for chunk in source_chunks),
            "supporting_chunks": sum(_score(chunk) >= min_top_score for chunk in source_chunks),
            "threshold": min_top_score,
        }

    return {
        **result,
        "status": "answered",
        "top_score": max(_score(chunk) for chunk in source_chunks),
        "supporting_chunks": sum(_score(chunk) >= min_top_score for chunk in source_chunks),
        "threshold": min_top_score,
    }