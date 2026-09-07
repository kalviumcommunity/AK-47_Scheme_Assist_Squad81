# -*- coding: utf-8 -*-
"""
vector_store.py - 3.30 Vector Database Setup & Collection Design
================================================================
Encapsulates vector database connectivity, collection lifecycle management,
record schema enforcement, and semantic indexing for SchemeAssist.

Key Capabilities:
  1. Manages connection to ChromaDB (persistent disk store and ephemeral in-memory)
  2. Creates and configures collections with exact vector dimensionality (1536) and cosine metric
  3. Enforces unified record schema: ID + Vector + Text + Metadata
  4. Supports single and batch upsert operations with strict dimension validation
  5. Provides readback verification and approximate nearest-neighbor (ANN) retrieval
"""

import os
import sys
from typing import List, Dict, Any, Optional, Union

# Ensure imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings
from src.config import (
    CHROMA_PERSIST_DIR,
    COLLECTION_NAME,
    VECTOR_DIMENSION,
    SIMILARITY_METRIC,
)


class VectorStore:
    """
    Wrapper around ChromaDB managing connection, schema validation,
    and storage for SchemeAssist chunk embeddings.
    """

    def __init__(
        self,
        persist_dir: Optional[str] = None,
        in_memory: bool = False,
        collection_name: str = COLLECTION_NAME,
        dimension: int = VECTOR_DIMENSION,
        metric: str = SIMILARITY_METRIC,
    ):
        self.in_memory = in_memory
        self.persist_dir = persist_dir or CHROMA_PERSIST_DIR
        self.collection_name = collection_name
        self.dimension = dimension
        self.metric = metric

        # 1. Initialize Client
        if self.in_memory:
            self.client = chromadb.EphemeralClient()
        else:
            os.makedirs(self.persist_dir, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_dir)

        # 2. Initialize / Get Collection
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """
        Creates or retrieves the collection configured with the specified
        similarity metric (HNSW space) and dimension metadata.
        """
        # In ChromaDB, the distance function is passed via collection metadata
        # Supported spaces: 'cosine', 'l2', 'ip'
        hnsw_space = "cosine" if self.metric.lower() in ["cosine", "cos"] else "l2"
        metadata = {
            "hnsw:space": hnsw_space,
            "dimension": self.dimension,
            "description": "SchemeAssist welfare policy chunks with embedded vectors",
        }
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata=metadata,
        )

    def validate_vector_dimension(self, vector: List[float]) -> None:
        """
        Enforces strict dimension parity between input vector and collection schema.
        Raises ValueError early if dimensions do not match.
        """
        if len(vector) != self.dimension:
            raise ValueError(
                f"[DIMENSION MISMATCH] Input vector has dimension {len(vector)}, "
                f"but collection '{self.collection_name}' requires dimension {self.dimension}. "
                "Ensure documents and queries are embedded with the matching embedding model."
            )

    def upsert_record(
        self,
        record_id: str,
        vector: List[float],
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Inserts or updates a single record according to the required schema:
          - id: Unique stable chunk ID (string)
          - vector: Embedding float list of length `self.dimension`
          - text: Original chunk document text
          - metadata: Structured metadata dict (source, chunk_index, section, page, etc.)
        """
        self.validate_vector_dimension(vector)
        meta = metadata or {}

        # ChromaDB requires primitive types in metadata (str, int, float, bool)
        clean_meta = {}
        for k, v in meta.items():
            if isinstance(v, (str, int, float, bool)):
                clean_meta[k] = v
            else:
                clean_meta[k] = str(v)

        self.collection.upsert(
            ids=[record_id],
            embeddings=[vector],
            documents=[text],
            metadatas=[clean_meta],
        )

    def upsert_batch(
        self,
        records: List[Dict[str, Any]]
    ) -> int:
        """
        Batch-inserts multiple records into the collection.
        Each record must contain 'id', 'vector', 'text', and optional 'metadata'.
        Returns count of upserted records.
        """
        if not records:
            return 0

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for r in records:
            r_id = str(r["id"])
            vec = r.get("vector") or r.get("embedding")
            if vec is None:
                raise ValueError(f"Record '{r_id}' missing 'vector' or 'embedding' field.")
            self.validate_vector_dimension(vec)

            text = r.get("text") or r.get("document", "")
            raw_meta = r.get("metadata", {})

            clean_meta = {}
            for k, v in raw_meta.items():
                if isinstance(v, (str, int, float, bool)):
                    clean_meta[k] = v
                else:
                    clean_meta[k] = str(v)

            ids.append(r_id)
            embeddings.append(vec)
            documents.append(text)
            metadatas.append(clean_meta)

        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        return len(ids)

    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Reads back a record by ID, returning a structured dictionary:
          {
            "id": str,
            "vector": List[float],
            "text": str,
            "metadata": Dict[str, Any]
          }
        Returns None if not found.
        """
        result = self.collection.get(
            ids=[record_id],
            include=["embeddings", "documents", "metadatas"],
        )

        if not result or not result["ids"] or len(result["ids"]) == 0:
            return None

        # Extract record fields
        r_id = result["ids"][0]
        r_vector = result["embeddings"][0] if result.get("embeddings") is not None and len(result["embeddings"]) > 0 else []
        r_text = result["documents"][0] if result.get("documents") is not None and len(result["documents"]) > 0 else ""
        r_metadata = result["metadatas"][0] if result.get("metadatas") is not None and len(result["metadatas"]) > 0 else {}

        return {
            "id": r_id,
            "vector": list(r_vector) if r_vector is not None else [],
            "text": r_text,
            "metadata": r_metadata,
        }

    def query_similar(
        self,
        query_vector: List[float],
        top_k: int = 3,
        where_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Performs approximate nearest neighbor search for a given query vector.
        Returns a list of match dictionaries containing:
          - id: record ID
          - score: computed similarity (1.0 - distance for cosine)
          - distance: raw ChromaDB distance
          - text: stored chunk text
          - metadata: stored chunk metadata
        """
        self.validate_vector_dimension(query_vector)

        query_params: Dict[str, Any] = {
            "query_embeddings": [query_vector],
            "n_results": top_k,
            "include": ["embeddings", "documents", "metadatas", "distances"],
        }
        if where_filter:
            query_params["where"] = where_filter

        results = self.collection.query(**query_params)

        matches = []
        if not results or not results["ids"] or len(results["ids"][0]) == 0:
            return matches

        ids = results["ids"][0]
        distances = results["distances"][0] if results.get("distances") else [0.0] * len(ids)
        documents = results["documents"][0] if results.get("documents") else [""] * len(ids)
        metadatas = results["metadatas"][0] if results.get("metadatas") else [{}] * len(ids)

        for r_id, dist, doc, meta in zip(ids, distances, documents, metadatas):
            # For cosine distance, similarity = 1.0 - distance
            similarity = round(1.0 - float(dist), 4)
            matches.append({
                "id": r_id,
                "score": similarity,
                "distance": round(float(dist), 4),
                "text": doc,
                "metadata": meta,
            })

        return matches

    def delete_record(self, record_id: str) -> None:
        """Deletes a record by ID."""
        self.collection.delete(ids=[record_id])

    def count(self) -> int:
        """Returns total count of records stored in the collection."""
        return self.collection.count()

    def reset_collection(self) -> None:
        """Empties or deletes the current collection."""
        self.client.delete_collection(name=self.collection_name)
        self.collection = self._get_or_create_collection()
