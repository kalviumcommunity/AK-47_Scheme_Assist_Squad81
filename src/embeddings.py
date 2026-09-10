# -*- coding: utf-8 -*-
"""
embeddings.py - Gemini Embeddings & Cosine Similarity Ranking
"""

import math
import os
import re
import sys
from typing import List, Dict, Any, Optional, Sequence

from dotenv import load_dotenv
from google import genai

# Ensure imports resolve correctly
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

load_dotenv()


# ─── Gemini Configuration ────────────────────────────────────────────────────

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gemini embedding model
EMBED_MODEL = os.getenv(
    "EMBED_MODEL",
    "gemini-embedding-001"
)


# ─── 1. Cosine Similarity ────────────────────────────────────────────────────

def cosine_similarity(
    vec_a: Sequence[float],
    vec_b: Sequence[float],
    eps: float = 1e-9
) -> float:

    if len(vec_a) != len(vec_b):
        raise ValueError(
            f"[DIMENSION MISMATCH] "
            f"{len(vec_a)} vs {len(vec_b)}"
        )

    dot_product = sum(
        a * b for a, b in zip(vec_a, vec_b)
    )

    norm_a = math.sqrt(
        sum(a * a for a in vec_a)
    )

    norm_b = math.sqrt(
        sum(b * b for b in vec_b)
    )

    if norm_a < eps or norm_b < eps:
        return 0.0

    similarity = dot_product / (norm_a * norm_b)

    return max(
        -1.0,
        min(1.0, float(similarity))
    )


# ─── 2. Offline Fallback ─────────────────────────────────────────────────────

class DeterministicSemanticVectorizer:

    def __init__(self, dimension: int = 768):
        self.dimension = dimension

    def _tokenize(self, text: str):

        cleaned = re.sub(
            r"[^\w\s]",
            " ",
            text.lower()
        )

        tokens = [
            word
            for word in cleaned.split()
            if len(word) > 1
        ]

        features = list(tokens)

        for i in range(len(tokens) - 1):

            features.append(
                f"{tokens[i]}_{tokens[i + 1]}"
            )

        return features

    def embed_text(self, text: str):

        tokens = self._tokenize(text)

        if not tokens:
            return [0.0] * self.dimension

        vector = [
            0.0
        ] * self.dimension

        for token in tokens:

            h = 2166136261

            for char in token:

                h = (
                    (h ^ ord(char))
                    * 16777619
                ) & 0xFFFFFFFF

            index = h % self.dimension

            sign = (
                1.0
                if ((h >> 16) & 1) == 0
                else -1.0
            )

            vector[index] += sign

        norm = math.sqrt(
            sum(x * x for x in vector)
        )

        if norm > 1e-9:

            vector = [
                x / norm
                for x in vector
            ]

        return vector

    def embed(self, texts):

        return [
            self.embed_text(text)
            for text in texts
        ]


# ─── 3. Gemini Embedding Service ─────────────────────────────────────────────

class EmbeddingService:

    def __init__(
        self,
        model_name: str = EMBED_MODEL,
        force_offline: bool = False
    ):

        self.model_name = model_name

        self.force_offline = force_offline

        self.client = None

        self.active_provider = "offline"

        # Fallback dimension
        self.offline_vectorizer = (
            DeterministicSemanticVectorizer(
                dimension=768
            )
        )

        if not force_offline and GEMINI_API_KEY:

            try:

                self.client = genai.Client(
                    api_key=GEMINI_API_KEY
                )

                self.active_provider = "gemini"

                print(
                    "[EMBEDDING CONFIG] "
                    "Using Gemini embeddings"
                )

            except Exception as error:

                print(
                    "[EMBEDDING WARNING] "
                    f"Gemini initialization failed: {error}"
                )

                self.active_provider = "offline"


    # ─── Embed Multiple Texts ────────────────────────────────────────────────

    def embed_texts(
        self,
        texts: List[str]
    ) -> List[List[float]]:

        if not texts:
            return []

        if (
            self.active_provider == "gemini"
            and self.client
        ):

            try:

                embeddings = []

                for text in texts:

                    response = (
                        self.client.models.embed_content(
                            model=self.model_name,
                            contents=text
                        )
                    )

                    vector = (
                        response.embeddings[0].values
                    )

                    embeddings.append(vector)

                print(
                    f"[EMBEDDING LOG] "
                    f"Generated {len(embeddings)} "
                    f"Gemini embeddings"
                )

                return embeddings

            except Exception as error:

                print(
                    "[EMBEDDING WARNING] "
                    f"Gemini embedding failed: {error}"
                )

                print(
                    "[EMBEDDING FALLBACK] "
                    "Using local embeddings"
                )

                self.active_provider = (
                    "offline_fallback"
                )

                return self.offline_vectorizer.embed(
                    texts
                )

        return self.offline_vectorizer.embed(texts)


    # ─── Embed Query ─────────────────────────────────────────────────────────

    def embed_query(
        self,
        query: str
    ) -> List[float]:

        results = self.embed_texts(
            [query]
        )

        if results:
            return results[0]

        return [
            0.0
        ] * 768


# ─── 4. Ranking Engine ───────────────────────────────────────────────────────

def rank_chunks(

    query: str,

    chunk_records: List[
        Dict[str, Any]
    ],

    query_embedding: Optional[
        List[float]
    ] = None,

    embedding_service: Optional[
        EmbeddingService
    ] = None,

) -> List[Dict[str, Any]]:

    if not chunk_records:
        return []

    if query_embedding is None:

        if embedding_service is None:

            embedding_service = (
                EmbeddingService()
            )

        query_embedding = (
            embedding_service.embed_query(
                query
            )
        )

    ranked = []

    for chunk in chunk_records:

        chunk_vector = chunk.get(
            "embedding"
        )

        if chunk_vector is None:
            continue

        try:

            score = cosine_similarity(
                query_embedding,
                chunk_vector
            )

        except ValueError:

            score = -1.0

        ranked_item = dict(chunk)

        ranked_item["score"] = score

        ranked.append(ranked_item)

    ranked.sort(

        key=lambda item:
        item["score"],

        reverse=True
    )

    for index, item in enumerate(
        ranked,
        start=1
    ):

        item["rank"] = index

    return ranked