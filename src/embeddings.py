# -*- coding: utf-8 -*-
"""
embeddings.py - Embedding Generation & Cosine Similarity Ranking
===============================================================
Module supporting 3.29 Embedding Quality Checks & Sanity Tests.
Provides:
  1. OpenAI embedding integration (text-embedding-3-small) with graceful offline fallback
  2. Mathematical cosine similarity computation with dimensional integrity validation
  3. Chunk embedding and similarity-based ranking
  4. Mismatched model simulation for sanity diagnosis
"""

import math
import os
import re
import sys
from typing import List, Dict, Any, Optional, Sequence, Union

# Ensure imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import OPENAI_API_KEY, OPENAI_BASE_URL, EMBED_MODEL


# ─── 1. Cosine Similarity Computation ─────────────────────────────────────────

def cosine_similarity(
    vec_a: Sequence[float],
    vec_b: Sequence[float],
    eps: float = 1e-9
) -> float:
    """
    Computes the cosine similarity between two numeric vectors:
        cos(theta) = (vec_a . vec_b) / (||vec_a||_2 * ||vec_b||_2)

    Properties:
      - Returns 1.0 for identical non-zero vectors.
      - Returns 0.0 for orthogonal vectors.
      - Returns -1.0 for diametrically opposed vectors.
      - Bounds strictly clamped to [-1.0, 1.0].
      - Raises ValueError if vector dimensions do not match (e.g. mismatched models).
    """
    if len(vec_a) != len(vec_b):
        raise ValueError(
            f"[DIMENSION MISMATCH] Cannot compute cosine similarity between vectors "
            f"of different lengths: {len(vec_a)} vs {len(vec_b)}. "
            "Ensure queries and documents are embedded using identical models."
        )

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a < eps or norm_b < eps:
        # Zero-vector safeguard
        return 0.0

    sim = dot_product / (norm_a * norm_b)
    # Numerical clamping to avoid precision overflow (e.g. 1.0000000002)
    return max(-1.0, min(1.0, float(sim)))


# ─── 2. Deterministic Semantic Vectorizer (Offline / Fallback) ────────────────

class DeterministicSemanticVectorizer:
    """
    High-fidelity deterministic feature vectorizer used for testing, CI/CD,
    and offline operation when OpenAI API quota is unavailable.

    Constructs a dense normalized vector (dimension = 1536, identical to
    text-embedding-3-small) using subword n-gram frequency hashing and term
    weights, normalized to unit L2 length (||v|| = 1.0).
    """
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = [w for w in cleaned.split() if len(w) > 1]
        # Include unigrams and bigrams for phrase sensitivity
        features = list(tokens)
        for i in range(len(tokens) - 1):
            features.append(f"{tokens[i]}_{tokens[i+1]}")
        return features

    def embed_text(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        if not tokens:
            return [0.0] * self.dimension

        vector = [0.0] * self.dimension
        for token in tokens:
            # Deterministic FNV-style integer hash
            h = 2166136261
            for char in token:
                h = ((h ^ ord(char)) * 16777619) & 0xFFFFFFFF
            idx = h % self.dimension
            # Sign hash to reduce collisions
            sign = 1.0 if ((h >> 16) & 1) == 0 else -1.0
            vector[idx] += sign

        # Unit L2 normalization
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 1e-9:
            vector = [x / norm for x in vector]
        return vector

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]


# ─── 3. Embedding Service Interface ──────────────────────────────────────────

class EmbeddingService:
    """
    Production embedding service that attempts OpenAI API embeddings,
    falling back seamlessly to DeterministicSemanticVectorizer if the key is
    missing, rate-limited (429), or unauthorized (401).
    """
    def __init__(
        self,
        model_name: str = EMBED_MODEL,
        force_offline: bool = False
    ):
        self.model_name = model_name
        self.force_offline = force_offline
        self.offline_vectorizer = DeterministicSemanticVectorizer(dimension=1536)
        self.client = None
        self.active_provider = "offline"

        if not force_offline and OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    base_url=OPENAI_BASE_URL,
                    api_key=OPENAI_API_KEY,
                    max_retries=1,
                    timeout=10.0,
                )
                self.active_provider = "openai"
            except Exception as e:
                self.client = None
                self.active_provider = "offline"

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of texts using the active provider."""
        if not texts:
            return []

        if self.active_provider == "openai" and self.client is not None:
            try:
                response = self.client.embeddings.create(
                    input=texts,
                    model=self.model_name,
                )
                return [record.embedding for record in response.data]
            except Exception as exc:
                # Fall back gracefully to deterministic vectorizer on 429 quota or connection errors
                self.active_provider = "offline_fallback"
                return self.offline_vectorizer.embed(texts)

        return self.offline_vectorizer.embed(texts)

    def embed_query(self, query: str) -> List[float]:
        """Embeds a single search query."""
        results = self.embed_texts([query])
        return results[0] if results else [0.0] * 1536


# ─── 4. Mismatched Model Simulator ───────────────────────────────────────────

def generate_mismatched_embedding(
    text: str,
    dimension: int = 1536,
    seed_offset: int = 99991
) -> List[float]:
    """
    Generates an embedding from a simulated 'mismatched' model space.
    Used to demonstrate Task 3 and the core conceptual warning:
    'If documents are embedded with one model and queries with another,
    the vectors are not in the same space. Similarity scores may still
    be numbers, but the ranking cannot be trusted.'
    """
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    tokens = [w for w in cleaned.split() if len(w) > 1]
    if not tokens:
        return [0.0] * dimension

    vector = [0.0] * dimension
    for token in tokens:
        # Intentionally altered hash constants representing an alien vector space
        h = seed_offset
        for char in token:
            h = ((h ^ (ord(char) * 31)) * 1000003) & 0xFFFFFFFF
        idx = h % dimension
        sign = 1.0 if ((h >> 8) & 1) == 0 else -1.0
        vector[idx] += sign

    norm = math.sqrt(sum(x * x for x in vector))
    if norm > 1e-9:
        vector = [x / norm for x in vector]
    return vector


# ─── 5. Ranking Engine ───────────────────────────────────────────────────────

def rank_chunks(
    query: str,
    chunk_records: List[Dict[str, Any]],
    query_embedding: Optional[List[float]] = None,
    embedding_service: Optional[EmbeddingService] = None,
) -> List[Dict[str, Any]]:
    """
    Ranks chunk records against a user query using cosine similarity.

    Args:
        query: User input search text.
        chunk_records: List of chunk dictionaries containing 'embedding' and 'metadata'.
        query_embedding: Optional pre-computed query embedding vector.
        embedding_service: Optional EmbeddingService instance.

    Returns:
        List of chunk dictionaries sorted descending by 'score', each enriched
        with 'score' and 'rank'.
    """
    if not chunk_records:
        return []

    if query_embedding is None:
        if embedding_service is None:
            embedding_service = EmbeddingService()
        query_embedding = embedding_service.embed_query(query)

    ranked = []
    for chunk in chunk_records:
        chunk_vec = chunk.get("embedding")
        if chunk_vec is None:
            continue
        try:
            score = cosine_similarity(query_embedding, chunk_vec)
        except ValueError as err:
            score = -1.0
        
        ranked_item = dict(chunk)
        ranked_item["score"] = score
        ranked.append(ranked_item)

    # Sort descending by cosine similarity score
    ranked.sort(key=lambda item: item["score"], reverse=True)

    # Attach 1-based rank position
    for idx, item in enumerate(ranked, start=1):
        item["rank"] = idx

    return ranked
