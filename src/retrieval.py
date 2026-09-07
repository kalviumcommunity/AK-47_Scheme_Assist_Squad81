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

  SimpleRetriever  - Keyword-overlap ranked search over in-memory item lists.
                     Used for lightweight / offline operation (no vector DB required).

  HybridRetriever  - Semantic vector search backed by VectorStore (ChromaDB) with:
                       * Metadata filtering    – restrict search to a specific subset
                                                 (e.g. source file, scheme category, section)
                       * Keyword scoring boost – adds exact-term overlap to the raw
                                                 cosine similarity, controlled by alpha/beta
                         Final score = alpha * vector_score + beta * keyword_score
                       * Unfiltered comparison – convenience method to run the same query
                                                 with and without a metadata filter so the
                                                 caller can see the delta.

Both classes share a common output shape so callers can swap them transparently.
"""

import re
from typing import List, Dict, Any, Optional

from src.vector_store import VectorStore


# ---------------------------------------------------------------------------
# SimpleRetriever
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Keyword scoring helpers
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> List[str]:
    """
    Lowercases and splits text into tokens, stripping punctuation.
    Used for keyword overlap calculation inside HybridRetriever.
    """
    return re.findall(r"[a-z0-9']+", text.lower())


def _keyword_score(query: str, document: str) -> float:
    """
    Computes a normalised keyword overlap score in [0, 1].

    Score = |query_tokens ∩ doc_tokens| / |query_tokens|

    Returns 0.0 if query is empty.
    """
    q_tokens = set(_tokenize(query))
    if not q_tokens:
        return 0.0
    d_tokens = set(_tokenize(document))
    overlap = len(q_tokens & d_tokens)
    return overlap / len(q_tokens)


# ---------------------------------------------------------------------------
# HybridRetriever
# ---------------------------------------------------------------------------

class HybridRetriever:
    """
    Semantic + keyword hybrid retriever backed by VectorStore (ChromaDB).

    Parameters
    ----------
    vector_store : VectorStore
        Initialised VectorStore instance (in-memory or persistent).
    embed_fn : callable
        A function that accepts a plain string query and returns a
        List[float] embedding of length matching ``vector_store.dimension``.
        Example::

            from src.embeddings import embed_text
            retriever = HybridRetriever(vs, embed_fn=embed_text)

    alpha : float
        Weight applied to the vector similarity score (default 0.7).
    beta : float
        Weight applied to the keyword overlap score (default 0.3).
        alpha + beta should equal 1.0 for interpretable scores, but this is
        not enforced so callers can experiment freely.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embed_fn,
        alpha: float = 0.7,
        beta: float = 0.3,
    ):
        self.vs = vector_store
        self.embed_fn = embed_fn
        self.alpha = alpha
        self.beta = beta

    # ------------------------------------------------------------------
    # Core retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieves the top_k most relevant chunks for *query*.

        Steps
        -----
        1. Embed the query string via ``embed_fn``.
        2. Run vector similarity search against the VectorStore, optionally
           scoped to records matching ``metadata_filter``.
        3. For each returned chunk, compute keyword overlap score.
        4. Compute hybrid score = alpha * vector_score + beta * keyword_score.
        5. Re-rank by hybrid score (descending) and return.

        Parameters
        ----------
        query : str
            Natural-language user question.
        top_k : int
            Number of results to return.
        metadata_filter : dict, optional
            ChromaDB ``where`` filter, e.g. ``{"source": "housing.md"}``.
            Supports all ChromaDB filter operators ($eq, $in, $and, $or …).

        Returns
        -------
        List[dict] with keys:
            id            – record identifier
            text          – chunk text stored in the collection
            metadata      – stored metadata dict
            vector_score  – cosine similarity from ChromaDB  (0–1)
            keyword_score – normalised keyword overlap        (0–1)
            hybrid_score  – alpha*vector + beta*keyword      (0–1 approx)
        """
        if not query or not query.strip():
            return []

        # 1. Embed
        query_vector = self.embed_fn(query)

        # 2. Vector search (fetch more than top_k to allow re-ranking)
        fetch_k = max(top_k * 3, 10)
        raw_matches = self.vs.query_similar(
            query_vector=query_vector,
            top_k=fetch_k,
            where_filter=metadata_filter,
        )

        if not raw_matches:
            return []

        # 3 & 4. Score and re-rank
        scored = []
        for match in raw_matches:
            v_score = match.get("score", 0.0)
            k_score = _keyword_score(query, match.get("text", ""))
            h_score = self.alpha * v_score + self.beta * k_score
            scored.append({
                "id": match["id"],
                "text": match["text"],
                "metadata": match.get("metadata", {}),
                "vector_score": round(v_score, 4),
                "keyword_score": round(k_score, 4),
                "hybrid_score": round(h_score, 4),
            })

        scored.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return scored[:top_k]

    # ------------------------------------------------------------------
    # Convenience: filtered vs unfiltered comparison
    # ------------------------------------------------------------------

    def compare_filtered_unfiltered(
        self,
        query: str,
        metadata_filter: Dict[str, Any],
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        Runs the same query with and without the supplied metadata filter
        and returns both result sets for side-by-side comparison.

        Returns
        -------
        dict with keys:
            query           – original query string
            filter          – the metadata_filter that was applied
            filtered        – results restricted to filter
            unfiltered      – results from full corpus
            delta_ids       – IDs in unfiltered but absent from filtered
        """
        filtered = self.retrieve(query, top_k=top_k, metadata_filter=metadata_filter)
        unfiltered = self.retrieve(query, top_k=top_k, metadata_filter=None)

        filtered_ids = {r["id"] for r in filtered}
        unfiltered_ids = {r["id"] for r in unfiltered}

        return {
            "query": query,
            "filter": metadata_filter,
            "filtered": filtered,
            "unfiltered": unfiltered,
            "delta_ids": list(unfiltered_ids - filtered_ids),
        }
