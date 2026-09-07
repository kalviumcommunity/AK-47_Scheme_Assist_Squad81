"""Citation utilities for verifiable, retrieval-grounded answers."""

import re
from typing import Any, Callable, Dict, Iterable, List

FALLBACK_ANSWER = "I do not have sufficient verified information to answer this question."
_CITATION_PATTERN = re.compile(r"\[(\d+)\]")


def _metadata(chunk: Dict[str, Any]) -> Dict[str, Any]:
    metadata = chunk.get("metadata")
    return metadata if isinstance(metadata, dict) else {}


def _source(chunk: Dict[str, Any], metadata: Dict[str, Any]) -> Any:
    return (
        metadata.get("source")
        or metadata.get("source_doc")
        or chunk.get("source")
        or chunk.get("source_doc")
        or chunk.get("filename")
    )


def build_citation_map(chunks: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Map stable answer markers to real retrieved chunk metadata and text."""
    citation_map: Dict[str, Dict[str, Any]] = {}
    for index, chunk in enumerate(chunks, start=1):
        metadata = _metadata(chunk)
        citation_map[f"[{index}]"] = {
            "source": _source(chunk, metadata),
            "chunk_id": metadata.get("chunk_id") or chunk.get("chunk_id") or chunk.get("id"),
            "chunk_index": metadata.get("chunk_index", chunk.get("chunk_index")),
            "page": metadata.get("page", chunk.get("page")),
            "section": metadata.get("section", chunk.get("section")),
            "text": chunk.get("text", chunk.get("content", "")),
        }
    return citation_map


def build_cited_prompt(question: str, chunks: Iterable[Dict[str, Any]]) -> str:
    """Build a prompt that restricts claims and citation markers to context."""
    citation_map = build_citation_map(chunks)
    context = "\n\n".join(
        f"{marker} {details['text']}"
        for marker, details in citation_map.items()
    )
    return (
        "Answer using only the context below.\n"
        "Cite every factual claim with one or more source markers such as [1] or [2].\n"
        "Only use source markers that appear in the context.\n"
        "If the context does not support an answer, say exactly: "
        f"{FALLBACK_ANSWER}\n\n"
        f"Context:\n{context}\n\nQuestion:\n{question}"
    )


def _valid_markers(answer: str, citation_map: Dict[str, Dict[str, Any]]) -> List[str]:
    return list(dict.fromkeys(
        f"[{marker}]" for marker in _CITATION_PATTERN.findall(answer)
        if f"[{marker}]" in citation_map
    ))


def verify_citation(
    marker: str,
    citation_map: Dict[str, Dict[str, Any]],
    source_chunks: Iterable[Dict[str, Any]],
) -> Dict[str, Any]:
    """Verify that a citation marker still points to the original chunk text."""
    citation = citation_map.get(marker)
    if not citation:
        return {"valid": False, "marker": marker, "reason": "unknown citation marker"}

    source_texts = {
        chunk.get("text", chunk.get("content", ""))
        for chunk in source_chunks
    }
    verified = citation.get("text", "") in source_texts and bool(citation.get("text"))
    return {
        "valid": verified,
        "marker": marker,
        "source": citation.get("source"),
        "chunk_id": citation.get("chunk_id"),
        "text": citation.get("text"),
        "reason": "matched original chunk text" if verified else "chunk text was not found",
    }


def answer_with_citations(
    question: str,
    chunks: Iterable[Dict[str, Any]],
    answer_fn: Callable[[str], str],
) -> Dict[str, Any]:
    """Generate an answer and return only citations grounded in retrieved chunks."""
    source_chunks = list(chunks)
    if not source_chunks:
        return {"answer": FALLBACK_ANSWER, "citations": {}, "prompt": ""}

    citation_map = build_citation_map(source_chunks)
    prompt = build_cited_prompt(question, source_chunks)
    candidate = answer_fn(prompt) or ""
    markers = _valid_markers(candidate, citation_map)

    if not markers:
        return {"answer": FALLBACK_ANSWER, "citations": {}, "prompt": prompt}

    citations = {marker: citation_map[marker] for marker in markers}
    return {"answer": candidate, "citations": citations, "prompt": prompt}