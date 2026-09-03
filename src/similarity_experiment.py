"""Offline demonstration of embedding similarity ranking."""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieval import rank_by_embedding


def main() -> None:
    query = "How can a learner reset their password?"
    query_embedding = [1.0, 0.0]
    chunk_records = [
        {
            "text": "Password reset instructions for learner accounts.",
            "metadata": {"source": "account-guide.md", "chunk_index": 0},
            "embedding": [0.9, 0.1],
        },
        {
            "text": "The cafeteria menu changes every Friday.",
            "metadata": {"source": "campus-guide.md", "chunk_index": 3},
            "embedding": [0.0, 1.0],
        },
        {
            "text": "Learners can recover access using their registered email.",
            "metadata": {"source": "account-guide.md", "chunk_index": 1},
            "embedding": [1.0, 0.0],
        },
    ]

    ranked = rank_by_embedding(query_embedding, chunk_records)
    lines = [
        "Embedding Similarity Ranking (cosine similarity)",
        f"Query: {query}",
        "Metric: cosine similarity compares vector direction; higher scores are more similar.",
        "",
        "Ranked results:",
    ]
    for position, record in enumerate(ranked, start=1):
        lines.append(
            f"{position}. score={record['similarity_score']:.6f} | "
            f"source={record['metadata']['source']} | "
            f"chunk_index={record['metadata']['chunk_index']} | {record['text']}"
        )
    lines.extend(
        [
            "",
            f"Most similar: {ranked[0]['text']} ({ranked[0]['metadata']})",
            f"Least similar: {ranked[-1]['text']} ({ranked[-1]['metadata']})",
            "",
            "A high score indicates semantic closeness in embedding space.",
            "It does not guarantee factual correctness, freshness, completeness, or safety.",
        ]
    )

    output = "\n".join(lines)
    print(output)
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/similarity_ranking_results.txt", "w", encoding="utf-8") as file:
        file.write(output + "\n")


if __name__ == "__main__":
    main()