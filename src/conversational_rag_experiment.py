"""Generate a multi-turn conversational RAG sample dialogue."""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conversational_rag import ConversationalRAG


CHUNKS = {
    "project submission requirements": [
        {
            "score": 0.91,
            "text": "Project submission requires a public PR link and a video explanation.",
            "metadata": {"source": "submission-guidelines.md", "chunk_index": 1, "section": "Submission"},
        }
    ],
    "project submission video explanation": [
        {
            "score": 0.87,
            "text": "The video explanation should show the implementation and explain the evidence.",
            "metadata": {"source": "submission-guidelines.md", "chunk_index": 2, "section": "Video"},
        }
    ],
}


def main() -> None:
    def rewrite(prompt: str) -> str:
        if "What about the video?" in prompt:
            return "project submission video explanation"
        return "project submission requirements"

    def retrieve(query: str):
        return CHUNKS.get(query, [])

    rag = ConversationalRAG(
        rewrite,
        retrieve,
        lambda prompt: (
            "Submit a public PR link and video explanation [1]."
            if "requires a public PR link" in prompt
            else "The video should explain the implementation and evidence [1]."
        ),
    )
    dialogue = [
        rag.ask("What are the project submission requirements?"),
        rag.ask("What about the video?"),
    ]
    report = {
        "turns": dialogue,
        "history_after_dialogue": rag.history,
    }
    print(json.dumps(report, indent=2))
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/conversational_rag_dialogue.json", "w", encoding="utf-8") as output:
        json.dump(report, output, indent=2)
        output.write("\n")


if __name__ == "__main__":
    main()