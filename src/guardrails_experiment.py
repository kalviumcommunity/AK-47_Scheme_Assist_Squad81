"""Generate successful and refused hallucination-guardrail examples."""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.guardrails import guarded_answer


def main() -> None:
    strong_chunks = [
        {
            "score": 0.91,
            "text": "Applicants must submit an income certificate.",
            "metadata": {"source": "scheme-guidelines.md", "chunk_index": 2},
        }
    ]
    weak_chunks = [
        {
            "score": 0.21,
            "text": "The cafeteria menu changes every Friday.",
            "metadata": {"source": "campus-guide.md", "chunk_index": 3},
        }
    ]
    report = {
        "answer_case": guarded_answer(
            "What document is required?",
            strong_chunks,
            lambda prompt: "Applicants must submit an income certificate [1].",
        ),
        "refusal_case": guarded_answer(
            "What is the product refund policy?",
            weak_chunks,
            lambda prompt: "The product has a 30-day refund policy [1].",
        ),
    }
    print(json.dumps(report, indent=2))
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/guardrail_examples.json", "w", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
        output.write("\n")


if __name__ == "__main__":
    main()