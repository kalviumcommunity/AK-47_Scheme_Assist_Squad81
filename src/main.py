import os
import sys

# Ensure package imports resolve correctly
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from src.config import validate_environment, CHAT_MODEL

# Import document ingestion and token-based chunking
from src.ingestion import (
    load_and_chunk_documents
)

from src.rag_pipeline import run_rag_pipeline


def load_system_prompt() -> str:
    """
    Loads the SchemeAssist RAG system prompt.
    """

    prompt_path = os.path.join(
        "prompts",
        "rag_system_prompt.txt"
    )

    if os.path.exists(prompt_path):
        with open(
            prompt_path,
            "r",
            encoding="utf-8"
        ) as f:
            return f.read().strip()

    return "You are an AI assistant for SchemeAssist."


def main():

    print("=" * 65)
    print("  [RAG App] SchemeAssist - End-to-End RAG Pipeline Run")
    print("=" * 65)

    # --------------------------------------------------
    # 1. Validate Environment & Secrets
    # --------------------------------------------------

    validate_environment()

    print("\n[ENVIRONMENT LOG] Environment validation successful.")


    # --------------------------------------------------
    # 2. Ingest Documents & Generate Token-Based Chunks
    # --------------------------------------------------

    print("\n[INGESTION LOG] Starting document ingestion...")

    chunks = load_and_chunk_documents(
        data_dir="data",
        chunk_size_tokens=250,
        overlap_tokens=50
    )

    if not chunks:
        print(
            "[ERROR] No chunks generated from "
            "documents in data/ directory."
        )
        return


    # --------------------------------------------------
    # 3. Count Unique Documents
    # --------------------------------------------------

    unique_docs = {
        chunk.get(
            "metadata",
            {}
        ).get(
            "source",
            "unknown"
        )
        for chunk in chunks
    }

    print(
        f"\n[INGESTION SUCCESS] "
        f"Ingested {len(unique_docs)} document(s)"
    )

    print(
        f"[CHUNKING SUCCESS] "
        f"Generated {len(chunks)} token-based chunk(s)"
    )


    # --------------------------------------------------
    # 4. Display Chunk Configuration
    # --------------------------------------------------

    print("\n[CHUNK CONFIGURATION]")

    print(
        "Chunk Size: 250 tokens"
    )

    print(
        "Chunk Overlap: 50 tokens"
    )


    # --------------------------------------------------
    # 5. Load System Prompt
    # --------------------------------------------------

    system_prompt = load_system_prompt()

    print(
        f"\n[PROMPT LOG] "
        f"Loaded system prompt "
        f"({len(system_prompt)} characters)"
    )


    # --------------------------------------------------
    # 6. Perform End-to-End RAG Query
    # --------------------------------------------------

    test_query = (
        "welfare schemes eligibility guidance "
        "and income limits"
    )

    print("\n" + "-" * 65)

    print(
        f"[QUERY]: {test_query}"
    )

    print("-" * 65)


    # --------------------------------------------------
    # 7. Run RAG Pipeline
    # --------------------------------------------------

    result = run_rag_pipeline(
        test_query,
        top_k=3
    )


    # --------------------------------------------------
    # 8. Display Final Generated Answer
    # --------------------------------------------------

    print(
        "\n--- [FINAL GENERATED RAG ANSWER] ---"
    )

    print(
        result.get(
            "answer",
            "No answer generated."
        )
    )


    # --------------------------------------------------
    # 9. Display Retrieved Sources
    # --------------------------------------------------

    print(
        "\n--- [RETURNED SOURCES & CITATIONS] ---"
    )

    sources = result.get(
        "sources",
        []
    )

    if not sources:

        print(
            "No sources returned."
        )

    else:

        for index, src in enumerate(
            sources,
            start=1
        ):

            citation_index = src.get(
                "citation_index",
                index
            )

            source_name = src.get(
                "source",
                "Unknown Source"
            )

            section = src.get(
                "section",
                "General Overview"
            )

            page = src.get(
                "page",
                "N/A"
            )

            print(
                f"[{citation_index}] "
                f"{source_name} "
                f"(Section: {section}, "
                f"Page: {page})"
            )


    # --------------------------------------------------
    # 10. Create Verification Output Log
    # --------------------------------------------------

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    output_log_path = os.path.join(
        "outputs",
        "verification_run.log"
    )


    with open(
        output_log_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "SchemeAssist Verification Run Successful.\n\n"
        )

        f.write(
            f"Model: {CHAT_MODEL}\n"
        )

        f.write(
            f"Documents Ingested: "
            f"{len(unique_docs)}\n"
        )

        f.write(
            f"Chunks Generated: "
            f"{len(chunks)}\n"
        )

        f.write(
            "Chunking Strategy: Token Based\n"
        )

        f.write(
            "Chunk Size: 250 tokens\n"
        )

        f.write(
            "Chunk Overlap: 50 tokens\n"
        )


    print(
        f"\n[OUTPUT LOG] "
        f"Verification run logged to "
        f"'{output_log_path}'."
    )


    # --------------------------------------------------
    # Final Success Message
    # --------------------------------------------------

    print("\n" + "=" * 65)

    print(
        "  [SUCCESS] END-TO-END RAG PIPELINE EXECUTED!"
    )

    print("=" * 65)


if __name__ == "__main__":
    main()