# -*- coding: utf-8 -*-
"""
src/app.py - Reusable Prompt Template Application Entrypoint
============================================================
Demonstrates direct reuse of centralized prompt templates from prompts.answer / prompts.templates
without hardcoded inline prompt strings in business logic.
"""

import os
import sys
import io

# Ensure root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from prompts.answer import ANSWER, ANSWER_V2, render
from prompts.templates import (
    SCHEME_QA_TEMPLATE_V2,
    SCHEME_BATCH_EVAL_TEMPLATE,
    SYSTEM_SCHEME_ASSIST_TEMPLATE,
    registry,
)
from src.llm_client import build_client, make_completion
from src.retrieval import SimpleRetriever
from src.ingestion import load_documents_from_data_dir


def chat_path(question: str, context: str) -> str:
    """
    Feature 1: Interactive Chat Path
    Reuses the central ANSWER template with runtime dynamic values.
    """
    prompt = render(ANSWER, context=context, question=question)
    return prompt


def cli_eval_path(batch_id: int, scheme_name: str, query: str, context: str) -> str:
    """
    Feature 2: Batch / CLI Evaluation Path
    Reuses the central batch template with runtime dynamic values.
    """
    prompt = render(
        SCHEME_BATCH_EVAL_TEMPLATE,
        batch_id=batch_id,
        scheme_name=scheme_name,
        context=context,
        query=query,
    )
    return prompt


def main() -> None:
    if hasattr(sys.stdout, "buffer"):
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        except Exception:
            pass

    print("=" * 70)
    print("  [SchemeAssist] 3.18 - Prompt Templates & Reusable Prompt Design (app.py)")
    print("=" * 70)

    # 1. Load Knowledge Context
    docs = load_documents_from_data_dir("data")
    context_chunks = docs[0]["content"] if docs else "General government welfare scheme documentation guidelines."

    # 2. Dynamic Input
    user_q = "How do citizens verify eligibility for welfare schemes?"

    # 3. Render using decoupled template
    print("\n--- Feature 1: Chat Path (Runtime Injection) ---")
    msg_chat = render(ANSWER, context=context_chunks.strip()[:200] + "...", question=user_q)
    print(f"Rendered Prompt:\n{msg_chat}\n")

    # 4. Feature 2: Batch / CLI Path
    print("--- Feature 2: Batch / CLI Path (Runtime Injection) ---")
    msg_cli = render(
        SCHEME_BATCH_EVAL_TEMPLATE,
        batch_id=101,
        scheme_name="National Welfare Support Scheme",
        context=context_chunks.strip()[:200] + "...",
        query="Verify income threshold compliance (< Rs. 3.5 Lakh)",
    )
    print(f"Rendered Batch Prompt:\n{msg_cli}\n")

    print("[SUCCESS] App successfully rendered templates decoupled from business logic.")


if __name__ == "__main__":
    main()
