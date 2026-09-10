# -*- coding: utf-8 -*-
"""
llm_client.py - Gemini API Client for SchemeAssist
"""

import os
import io
import sys
import time
import logging

from dotenv import load_dotenv
from google import genai


# ─── 1. Environment Configuration ────────────────────────────────────────────

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-3.6-flash")


# ─── 2. Logging Setup ────────────────────────────────────────────────────────

os.makedirs("outputs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            "outputs/llm_client.log",
            mode="w",
            encoding="utf-8"
        ),
    ],
)

log = logging.getLogger(__name__)


# ─── 3. Client Factory ───────────────────────────────────────────────────────

def build_client():
    """Create Gemini client using API key from .env."""

    api_key = os.getenv("GEMINI_API_KEY") or GEMINI_API_KEY
    if not api_key:
        log.error(
            "[CONFIG ERROR] GEMINI_API_KEY is not set in .env"
        )
        raise RuntimeError("GEMINI_API_KEY is not set in .env or environment")

    log.info("[CONFIG] Provider : Google Gemini")
    log.info("[CONFIG] Model    : %s", CHAT_MODEL)

    return genai.Client(
        api_key=api_key
    )


# ─── 4. Gemini Completion ───────────────────────────────────────────────────

def make_completion(
    client,
    messages: list[dict],
    max_retries: int = 3,
) -> str | None:
    """
    Send messages to Gemini and return AI response.
    """

    # Convert OpenAI-style messages to a single prompt
    prompt = ""

    for msg in messages:
        role = msg["role"].upper()
        content = msg["content"]

        log.info(
            "[REQUEST] [%s] %s",
            role,
            content
        )

        prompt += f"{role}:\n{content}\n\n"

    for attempt in range(1, max_retries + 1):

        try:

            response = client.models.generate_content(
                model=CHAT_MODEL,
                contents=prompt,
            )

            reply = response.text

            log.info("[RESPONSE] %s", reply)

            return reply

        except Exception as exc:

            error_text = str(exc)

            log.error(
                "[GEMINI ERROR] Attempt %d/%d: %s",
                attempt,
                max_retries,
                error_text
            )

            if attempt < max_retries:

                wait = 2 ** attempt

                log.warning(
                    "[RETRY] Retrying in %d seconds...",
                    wait
                )

                time.sleep(wait)

            else:

                log.error(
                    "[FAILURE] All retry attempts exhausted."
                )

                return None

    return None


# ─── 5. Main Entrypoint ─────────────────────────────────────────────────────

def main():

    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding="utf-8",
        errors="replace"
    )

    print("=" * 65)
    print("  [SchemeAssist] Gemini API Completion")
    print("=" * 65)

    client = build_client()

    messages = [

        {
            "role": "system",
            "content": (
                "You are SchemeAssist, an AI assistant that helps "
                "citizens understand government welfare schemes. "
                "Provide clear, accurate and concise answers."
            ),
        },

        {
            "role": "user",
            "content": (
                "What is one key thing a citizen should check before "
                "applying for a government welfare scheme?"
            ),
        },

    ]

    reply = make_completion(
        client,
        messages
    )

    print("\n" + "-" * 65)

    if reply:

        print(f"[ASSISTANT REPLY]\n{reply}")

        print("-" * 65)

        print(
            "[SUCCESS] Gemini completion completed successfully."
        )

    else:

        print(
            "[FAILURE] Gemini completion did not return a reply."
        )

    print("=" * 65)


if __name__ == "__main__":
    main()