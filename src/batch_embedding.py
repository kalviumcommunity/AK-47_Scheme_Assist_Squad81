"""Resumable batch embedding with retry and cost accounting."""

import argparse
import json
import os
import tempfile
import time
from typing import Any, Callable, Iterator, Sequence

from src.chunking import estimate_tokens

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
DEFAULT_OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

DEFAULT_BATCH_SIZE = 64
DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_PRICE_PER_1K_TOKENS = 0.00002


def batches(items: Sequence[dict[str, Any]], size: int) -> Iterator[list[dict[str, Any]]]:
    """Yield consecutive, non-empty batches of chunk records."""
    if size < 1:
        raise ValueError("batch size must be at least 1")
    for start in range(0, len(items), size):
        yield list(items[start : start + size])


def _has_embedding(chunk: dict[str, Any]) -> bool:
    embedding = chunk.get("embedding")
    return isinstance(embedding, (list, tuple)) and len(embedding) > 0


def _is_retryable(error: Exception) -> bool:
    status_code = getattr(error, "status_code", None)
    if status_code in {408, 409, 429} or (isinstance(status_code, int) and status_code >= 500):
        return True
    if isinstance(error, (TimeoutError, ConnectionError)):
        return True
    return error.__class__.__name__ in {
        "APIConnectionError",
        "APITimeoutError",
        "InternalServerError",
        "RateLimitError",
    }


def _embed_with_retry_details(
    client: Any,
    texts: list[str],
    model: str,
    max_attempts: int,
    backoff_base: float,
    sleep: Callable[[float], None],
) -> tuple[Any, int]:
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    for attempt in range(1, max_attempts + 1):
        try:
            return client.embeddings.create(model=model, input=texts), attempt
        except Exception as error:
            if not _is_retryable(error) or attempt == max_attempts:
                raise
            sleep(backoff_base * (2 ** (attempt - 1)))

    raise RuntimeError("embedding retry loop exited unexpectedly")


def embed_with_retry(
    client: Any,
    texts: list[str],
    model: str = EMBED_MODEL,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    backoff_base: float = 2.0,
    sleep: Callable[[float], None] = time.sleep,
) -> Any:
    """Create one embedding request, retrying only transient API failures."""
    response, _ = _embed_with_retry_details(
        client, texts, model, max_attempts, backoff_base, sleep
    )
    return response


def _response_embeddings(response: Any) -> list[list[float]]:
    data = list(getattr(response, "data", []))
    data.sort(key=lambda item: getattr(item, "index", 0))
    return [list(item.embedding) for item in data]


def _write_json_atomic(path: str, value: Any) -> None:
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, temporary_path = tempfile.mkstemp(prefix=".embedding-", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump(value, output, indent=2)
            output.write("\n")
        os.replace(temporary_path, path)
    except Exception:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)
        raise


def save_chunks(chunks: list[dict[str, Any]], path: str) -> None:
    """Persist chunks after a batch so an interrupted run can resume."""
    _write_json_atomic(path, chunks)


def load_chunks(path: str) -> list[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as source:
        payload = json.load(source)
    if isinstance(payload, dict):
        payload = payload.get("chunks")
    if not isinstance(payload, list) or not all(isinstance(item, dict) for item in payload):
        raise ValueError("input JSON must be a list of chunk objects or an object with a 'chunks' list")
    return payload


def embed_chunks(
    all_chunks: list[dict[str, Any]],
    client: Any,
    *,
    model: str = EMBED_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    backoff_base: float = 2.0,
    price_per_1k_tokens: float = DEFAULT_PRICE_PER_1K_TOKENS,
    checkpoint_path: str | None = None,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Embed missing vectors in batches and return a JSON-serializable run summary."""
    pending_chunks = [chunk for chunk in all_chunks if not _has_embedding(chunk)]
    summary: dict[str, Any] = {
        "total_chunks": len(all_chunks),
        "skipped_existing": len(all_chunks) - len(pending_chunks),
        "embedded": 0,
        "failed": 0,
        "failed_batches": 0,
        "input_tokens": 0,
        "api_requests": 0,
        "retries": 0,
        "batch_size": batch_size,
        "model": model,
        "errors": [],
    }

    for batch in batches(pending_chunks, batch_size):
        texts = [chunk.get("text", chunk.get("content", "")) for chunk in batch]
        batch_tokens = sum(estimate_tokens(text) for text in texts)
        try:
            response, attempts = _embed_with_retry_details(
                client, texts, model, max_attempts, backoff_base, sleep
            )
            vectors = _response_embeddings(response)
            if len(vectors) != len(batch):
                raise ValueError(
                    f"embedding response returned {len(vectors)} vectors for {len(batch)} chunks"
                )
            for chunk, vector in zip(batch, vectors):
                chunk["embedding"] = vector
            summary["embedded"] += len(batch)
        except Exception as error:
            attempts = max_attempts if _is_retryable(error) else 1
            summary["failed"] += len(batch)
            summary["failed_batches"] += 1
            summary["errors"].append({
                "chunk_ids": [chunk.get("chunk_id") for chunk in batch],
                "error": str(error),
            })
        summary["api_requests"] += attempts
        summary["retries"] += attempts - 1
        summary["input_tokens"] += batch_tokens * attempts
        if checkpoint_path:
            save_chunks(all_chunks, checkpoint_path)

    summary["estimated_cost_usd"] = round(
        summary["input_tokens"] / 1000 * price_per_1k_tokens, 6
    )
    return summary


def _build_client() -> Any:
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set; use an API key or inject a test client")
    return OpenAI(base_url=os.getenv("OPENAI_BASE_URL", DEFAULT_OPENAI_BASE_URL), api_key=api_key, max_retries=0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSON file containing chunk records")
    parser.add_argument("output", help="checkpoint/output JSON file")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max-attempts", type=int, default=DEFAULT_MAX_ATTEMPTS)
    parser.add_argument("--model", default=EMBED_MODEL)
    parser.add_argument("--price-per-1k-tokens", type=float, default=DEFAULT_PRICE_PER_1K_TOKENS)
    args = parser.parse_args()

    chunks = load_chunks(args.input)
    summary = embed_chunks(
        chunks,
        _build_client(),
        model=args.model,
        batch_size=args.batch_size,
        max_attempts=args.max_attempts,
        price_per_1k_tokens=args.price_per_1k_tokens,
        checkpoint_path=args.output,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()