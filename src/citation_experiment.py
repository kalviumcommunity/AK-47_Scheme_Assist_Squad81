"""Generate sample cited answers and source verification evidence."""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.citations import answer_with_citations, verify_citation


def main() -> None:
    chunks = [
        {
            "chunk_id": "pmkisan-eligibility-001",
            "text": "Eligible farmers must be registered landholding farmer families.",
            "metadata": {
                "source": "pmkisan_scheme_doc.md",
                "chunk_index": 1,
                "section": "Eligibility",
            },
        },
        {
            "chunk_id": "pmkisan-application-002",
            "text": "Applications can be submitted through the official PM-KISAN portal.",
            "metadata": {
                "source": "pmkisan_scheme_doc.md",
                "chunk_index": 2,
                "page": 3,
                "section": "Application Process",
            },
        },
    ]
    cited = answer_with_citations(
        "Who can apply and where?",
        chunks,
        lambda prompt: (
            "Registered landholding farmer families can apply [1]. "
            "Applications are submitted through the official PM-KISAN portal [2]."
        ),
    )
    cited["verification"] = verify_citation("[1]", cited["citations"], chunks)

    fallback = answer_with_citations(
        "What is the scheme's internal approval password?",
        [],
        lambda prompt: "The password is SECRET-123 [1].",
    )
    report = {
        "cited_answer_example": cited,
        "no_source_fallback_example": fallback,
    }
    print(json.dumps(report, indent=2))
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/citation_examples.json", "w", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
        output.write("\n")


if __name__ == "__main__":
    main()