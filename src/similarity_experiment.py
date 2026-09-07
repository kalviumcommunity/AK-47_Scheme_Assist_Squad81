"""Demonstrate same-model query embedding and changing-k retrieval."""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.embeddings import EmbeddingService
from src.retrieval import retrieve_top_k


def main() -> None:
    query = "How can a learner reset their password?"
    embedding_service = EmbeddingService(force_offline=True)
    chunk_texts = [
        "Password reset instructions for learner accounts.",
        "The cafeteria menu changes every Friday.",
        "Learners can recover access using their registered email.",
        "Course enrollment requires a verified learner account.",
        "Contact campus support for account recovery assistance.",
    ]
    metadata = [
        {"source": "account-guide.md", "chunk_index": 0},
        {"source": "campus-guide.md", "chunk_index": 3},
        {"source": "account-guide.md", "chunk_index": 1},
        {"source": "enrollment-guide.md", "chunk_index": 2},
        {"source": "account-guide.md", "chunk_index": 4},
    ]
    vectors = embedding_service.embed_texts(chunk_texts)
    chunk_records = [
        {
            "chunk_id": f"sample-{index}",
            "text": text,
            "metadata": record_metadata,
            "embedding": vector,
        }
        for index, (text, record_metadata, vector) in enumerate(zip(chunk_texts, metadata, vectors))
    ]
    results_by_k = {
        str(k): retrieve_top_k(query, chunk_records, embedding_service.embed_query, top_k=k)
        for k in (1, 3, 5)
    }
    report = {
        "query": query,
        "embedding_model": embedding_service.model_name,
        "metric": "cosine similarity",
        "results_by_k": results_by_k,
    }
    print(json.dumps(report, indent=2))
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/top_k_retrieval_results.json", "w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)
        file.write("\n")


if __name__ == "__main__":
    main()