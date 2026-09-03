from math import sqrt
from typing import List, Dict, Any, Sequence


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    """Return cosine similarity for two equal-length, non-zero vectors."""
    if len(a) != len(b):
        raise ValueError("Vectors must have the same dimensions")

    dot_product = sum(left * right for left, right in zip(a, b))
    norm_a = sqrt(sum(value * value for value in a))
    norm_b = sqrt(sum(value * value for value in b))
    if norm_a == 0 or norm_b == 0:
        raise ValueError("Cosine similarity is undefined for a zero vector")
    return dot_product / (norm_a * norm_b)


def rank_by_embedding(
    query_embedding: Sequence[float],
    chunk_records: Sequence[Dict[str, Any]],
    top_k: int | None = None,
) -> List[Dict[str, Any]]:
    """Rank chunk records by cosine similarity to a query embedding."""
    ranked = []
    for record in chunk_records:
        embedding = record.get("embedding")
        if embedding is None:
            continue
        try:
            score = cosine_similarity(query_embedding, embedding)
        except (TypeError, ValueError):
            continue
        enriched_record = dict(record)
        enriched_record["similarity_score"] = score
        ranked.append(enriched_record)

    ranked.sort(key=lambda item: item["similarity_score"], reverse=True)
    return ranked if top_k is None else ranked[:max(top_k, 0)]


class SimpleRetriever:
    """
    Lightweight document and chunk retriever for SchemeAssist RAG.
    Supports both full document dictionaries and chunk dictionaries.
    """
    def __init__(self, items: List[Dict[str, Any]]):
        self.items = items

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Performs keyword overlap ranking across indexed documents or chunks.
        Returns top_k most relevant items augmented with retrieval score.
        """
        if not self.items or not query:
            return []

        query_words = set(query.lower().split())
        scored_items = []

        for item in self.items:
            content = item.get("content") or item.get("text", "")
            item_words = set(content.lower().split())
            score = len(query_words.intersection(item_words))

            # Store score without modifying original dict
            enriched_item = dict(item)
            enriched_item["retrieval_score"] = score
            scored_items.append((score, enriched_item))

        scored_items = [pair for pair in scored_items if pair[0] > 0]
        if not scored_items:
            return []
        scored_items.sort(key=lambda x: x[0], reverse=True)
        return [item for score, item in scored_items[:top_k]]
