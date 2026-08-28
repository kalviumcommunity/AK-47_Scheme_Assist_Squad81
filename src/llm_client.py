# -*- coding: utf-8 -*-
"""
llm_client.py - 3.12 LLM API Access & First Completion Call
============================================================
Demonstrates how to:
  1. Configure an OpenAI-compatible client from .env (never hard-coded secrets)
  2. Send a chat completion request (system + user messages)
  3. Log the request and response payloads for debugging
  4. Handle 401 (AuthenticationError) and 429 (RateLimitError) clearly
"""

import os
import io
import sys
import time
import logging

from dotenv import load_dotenv
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError

# ─── 1. Environment Configuration ────────────────────────────────────────────
# All secrets and settings come from .env — nothing is hard-coded here
load_dotenv()

OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY: str  = os.getenv("OPENAI_API_KEY", "")
CHAT_MODEL: str      = os.getenv("CHAT_MODEL", "gpt-4o-mini")

# ─── 2. Logging Setup ────────────────────────────────────────────────────────
# Make sure outputs/ exists before logging to it
os.makedirs("outputs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("outputs/llm_client.log", mode="w", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)


# ─── 3. Client Factory ───────────────────────────────────────────────────────
def build_client() -> OpenAI:
    """Instantiate an OpenAI-compatible client from environment config."""
    if not OPENAI_API_KEY:
        log.error(
            "[CONFIG] OPENAI_API_KEY is not set in .env. "
            "Add it to your .env file and never commit real secrets to git."
        )
        sys.exit(1)

    log.info("[CONFIG] Base URL : %s", OPENAI_BASE_URL)
    log.info("[CONFIG] Model    : %s", CHAT_MODEL)

    return OpenAI(
        base_url=OPENAI_BASE_URL,
        api_key=OPENAI_API_KEY,
    )


# ─── 4. Chat Completion with Logging & Error Handling ────────────────────────
def make_completion(
    client: OpenAI,
    messages: list[dict],
    max_retries: int = 3,
) -> str | None:
    """
    Send a chat completion request and return the model's text reply.

    Logs the outgoing messages and incoming response/usage for debugging.
    Handles common API errors with clear, human-readable messages:
      - 401 AuthenticationError : bad/missing API key
      - 429 RateLimitError      : quota exceeded, backs off and retries

    Args:
        client:      Configured OpenAI client instance.
        messages:    List of {role, content} dicts forming the conversation.
        max_retries: Number of 429 retry attempts with exponential back-off.

    Returns:
        The assistant's reply text, or None on handled failure.
    """
    # Log the outgoing request payload so it can be inspected when debugging
    log.info("[REQUEST] Sending %d message(s) to model '%s':", len(messages), CHAT_MODEL)
    for msg in messages:
        log.info("  [%s] %s", msg["role"].upper(), msg["content"])

    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=messages,
            )

            reply: str = response.choices[0].message.content

            # Log the incoming response and token usage (cost lives here)
            log.info("[RESPONSE] %s", reply)
            if response.usage:
                log.info(
                    "[USAGE] prompt_tokens=%d | completion_tokens=%d | total_tokens=%d",
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens,
                    response.usage.total_tokens,
                )

            return reply

        except AuthenticationError:
            # 401 — API key is missing, revoked, or malformed
            log.error(
                "[ERROR 401] Authentication failed. "
                "Check that OPENAI_API_KEY in your .env is valid and not expired."
            )
            return None  # Not retryable

        except RateLimitError:
            # 429 — Rate limit or quota exhausted; back off and retry
            wait = 2 ** attempt  # exponential back-off: 2s, 4s, 8s
            if attempt < max_retries:
                log.warning(
                    "[ERROR 429] Rate limit hit (attempt %d/%d). "
                    "Retrying in %ds with exponential back-off...",
                    attempt, max_retries, wait,
                )
                time.sleep(wait)
            else:
                log.error(
                    "[ERROR 429] Rate limit hit. "
                    "All %d retry attempts exhausted. "
                    "You may have exceeded your quota — wait and try again later.",
                    max_retries,
                )
                return None

        except APIConnectionError as exc:
            # Network-level failure — common when using local endpoints (Ollama, LM Studio)
            log.error(
                "[ERROR] Could not connect to the API at '%s'. "
                "Verify the endpoint is running. Details: %s",
                OPENAI_BASE_URL,
                exc,
            )
            return None

    return None


# ─── 5. Main Entrypoint ──────────────────────────────────────────────────────
def main() -> None:
    # Ensure stdout handles UTF-8 on Windows terminals
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("=" * 65)
    print("  [SchemeAssist] 3.12 - LLM API First Completion Call")
    print("=" * 65)

    client = build_client()

    # Conversation: system role defines assistant behaviour,
    # user role provides the query — the core chat completion structure
    messages = [
        {
            "role": "system",
            "content": (
                "You are SchemeAssist, a concise AI assistant that helps "
                "citizens understand government welfare schemes. "
                "Keep every reply to two sentences or fewer."
            ),
        },
        {
            "role": "user",
            "content": (
                "What is one key thing a citizen should check before applying "
                "for a government welfare scheme?"
            ),
        },
    ]

    reply = make_completion(client, messages)

    print("\n" + "-" * 65)
    if reply:
        print(f"[ASSISTANT REPLY]\n{reply}")
        print("-" * 65)
        print("[SUCCESS] First completion call completed successfully.")
    else:
        print("[FAILURE] Completion call did not return a reply - see logs above.")
    print("=" * 65)


if __name__ == "__main__":
    main()
