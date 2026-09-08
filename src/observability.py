"""
observability.py - Caching, Logging & Usage Monitoring Module
==============================================================
Provides:
  1. SHA-256 Query Cache with TTL validation for RAG queries.
  2. Structured JSON request/response logging.
  3. Token usage and financial cost estimation per request.
  4. Aggregated usage monitoring and summary reporting.
  5. ObservableRAG orchestrator wrapper.
"""

import hashlib
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Callable

# Ensure sys.path includes project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Standard cost constants (e.g. gpt-4o-mini rates)
MODEL_INPUT_COST_PER_1K: float = 0.00015
MODEL_OUTPUT_COST_PER_1K: float = 0.00060
DEFAULT_CACHE_TTL_SECONDS: int = 15 * 60  # 15 minutes

# Logger setup
logger = logging.getLogger("rag_app.observability")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


# ─── 1. Query Cache ─────────────────────────────────────────────────────────

def cache_key(question: str, filters: Optional[Dict[str, Any]] = None) -> str:
    """Generate a deterministic SHA-256 hash key for a question and filter set."""
    raw = {
        "question": (question or "").strip().lower(),
        "filters": filters or {}
    }
    encoded = json.dumps(raw, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


class QueryCache:
    """In-memory cache for RAG queries with TTL validation."""

    def __init__(self, ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, question: str, filters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Retrieve cached response if present and unexpired."""
        key = cache_key(question, filters)
        cached = self._cache.get(key)
        if not cached:
            return None

        # Check TTL expiration
        if time.time() - cached["created_at"] > self.ttl_seconds:
            self._cache.pop(key, None)
            return None

        # Return a copy of response marked with cache_hit = True
        res = dict(cached["response"])
        return res

    def set(self, question: str, response: Dict[str, Any], filters: Optional[Dict[str, Any]] = None) -> str:
        """Store a response in cache with creation timestamp."""
        key = cache_key(question, filters)
        self._cache[key] = {
            "created_at": time.time(),
            "response": dict(response)
        }
        return key

    def clear(self) -> None:
        """Purge all entries from cache."""
        self._cache.clear()

    def size(self) -> int:
        """Return count of cached entries."""
        return len(self._cache)


# Global default cache instance
query_cache = QueryCache()


def get_cached_answer(question: str, filters: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Helper wrapper around default query_cache instance."""
    return query_cache.get(question, filters)


def save_cached_answer(question: str, response: Dict[str, Any], filters: Optional[Dict[str, Any]] = None) -> str:
    """Helper wrapper around default query_cache instance."""
    return query_cache.set(question, response, filters)


# ─── 2. Usage & Cost Estimation ─────────────────────────────────────────────

def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculate approximate USD cost for token usage."""
    input_cost = (input_tokens / 1000.0) * MODEL_INPUT_COST_PER_1K
    output_cost = (output_tokens / 1000.0) * MODEL_OUTPUT_COST_PER_1K
    return round(input_cost + output_cost, 6)


def estimate_tokens_from_text(text: str) -> int:
    """Estimate token count for text using tiktoken or word heuristic fallback."""
    if not text:
        return 0
    try:
        from src.token_counter import count_tokens
        return count_tokens(text)
    except Exception:
        # Fallback estimation: ~4 chars per token or ~0.75 words per token
        return max(1, len(text) // 4)


def _extract_sources(response: Dict[str, Any]) -> List[str]:
    """Helper to extract list of sources safely from citations or metadata."""
    sources = response.get("sources")
    if isinstance(sources, list) and sources:
        return [str(s) for s in sources]

    citations = response.get("citations")
    extracted = []
    if isinstance(citations, dict):
        for cit in citations.values():
            if isinstance(cit, dict) and cit.get("source"):
                extracted.append(str(cit["source"]))
    elif isinstance(citations, list):
        for cit in citations:
            if isinstance(cit, dict) and cit.get("source"):
                extracted.append(str(cit["source"]))

    return list(dict.fromkeys(extracted))


# ─── 3. Structured Request Logging ──────────────────────────────────────────

def log_rag_request(record: Dict[str, Any], log_file: str = "outputs/rag_requests.jsonl") -> Dict[str, Any]:
    """
    Log a RAG request record as structured JSON to log file and logger.info.
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    log_entry = {
        "timestamp": record.get("timestamp") or datetime.now(timezone.utc).isoformat(),
        "request_id": record.get("request_id", f"req_{int(time.time()*1000)}"),
        "question": record.get("question", ""),
        "answer_preview": (record.get("answer") or "")[:180],
        "sources": record.get("sources", []),
        "cache_hit": bool(record.get("cache_hit", False)),
        "input_tokens": int(record.get("input_tokens", 0)),
        "output_tokens": int(record.get("output_tokens", 0)),
        "estimated_cost": float(record.get("estimated_cost", 0.0)),
        "latency_ms": round(float(record.get("latency_ms", 0.0)), 2),
        "status": record.get("status", "answered"),
        "error": record.get("error", None)
    }

    # Write JSON Line to log file
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    logger.info("RAG Request Logged: %s", json.dumps(log_entry))
    return log_entry


# ─── 4. Usage Summarization & Reporting ─────────────────────────────────────

def summarize_usage(log_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Summarize a collection of log records into an overall usage report.
    """
    total_requests = len(log_records)
    if total_requests == 0:
        return {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_hit_rate": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_estimated_cost": 0.0,
            "average_latency_ms": 0.0,
            "status_counts": {}
        }

    cache_hits = sum(1 for item in log_records if item.get("cache_hit"))
    cache_misses = total_requests - cache_hits
    total_cost = sum(item.get("estimated_cost", 0.0) for item in log_records)
    total_latency = sum(item.get("latency_ms", 0.0) for item in log_records)
    total_input = sum(item.get("input_tokens", 0) for item in log_records)
    total_output = sum(item.get("output_tokens", 0) for item in log_records)

    status_counts: Dict[str, int] = {}
    for item in log_records:
        st = item.get("status", "unknown")
        status_counts[st] = status_counts.get(st, 0) + 1

    return {
        "total_requests": total_requests,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "cache_hit_rate": round(cache_hits / total_requests, 2),
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_estimated_cost": round(total_cost, 6),
        "average_latency_ms": round(total_latency / total_requests, 2),
        "status_counts": status_counts
    }


def save_usage_report(
    log_file: str = "outputs/rag_requests.jsonl",
    report_file: str = "outputs/usage_summary_report.json"
) -> Dict[str, Any]:
    """Read log file records and write aggregated summary report JSON."""
    records = []
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

    summary = summarize_usage(records)
    os.makedirs(os.path.dirname(report_file), exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")

    return summary


# ─── 5. Observable RAG Orchestrator ─────────────────────────────────────────

class ObservableRAG:
    """
    Wrapper around RAG pipeline execution that automatically manages:
    - Query caching (hit/miss)
    - Execution timing (latency_ms)
    - Token counting & cost estimation
    - Request logging & usage metadata attachment
    """

    def __init__(
        self,
        rag_pipeline_fn: Callable[[str, Optional[Dict[str, Any]]], Dict[str, Any]],
        cache: Optional[QueryCache] = None,
        log_file: str = "outputs/rag_requests.jsonl"
    ):
        self.rag_pipeline_fn = rag_pipeline_fn
        self.cache = cache or query_cache
        self.log_file = log_file

    def query(self, question: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute query with caching, timing, token tracking, logging, and metadata."""
        start_time = time.time()
        req_id = f"req_{int(start_time * 1000)}"

        # 1. Check Query Cache
        cached_resp = self.cache.get(question, filters)
        if cached_resp is not None:
            latency_ms = (time.time() - start_time) * 1000.0
            sources = _extract_sources(cached_resp)

            usage_info = {
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost": 0.0,
                "cache_hit": True,
                "latency_ms": round(latency_ms, 2)
            }
            
            cached_resp["usage"] = usage_info
            
            # Log cache hit
            log_rag_request({
                "request_id": req_id,
                "question": question,
                "answer": cached_resp.get("answer", ""),
                "sources": sources,
                "cache_hit": True,
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost": 0.0,
                "latency_ms": latency_ms,
                "status": cached_resp.get("status", "answered")
            }, log_file=self.log_file)
            
            return cached_resp

        # 2. Cache Miss: Execute underlying RAG pipeline
        error_msg = None
        status = "answered"
        try:
            response = self.rag_pipeline_fn(question, filters)
        except Exception as exc:
            response = {
                "answer": "An error occurred while processing your query.",
                "citations": {},
                "status": "error"
            }
            status = "error"
            error_msg = str(exc)

        latency_ms = (time.time() - start_time) * 1000.0

        # Estimate input and output tokens
        prompt_text = response.get("prompt") or question
        answer_text = response.get("answer") or ""

        input_tokens = response.get("input_tokens") or estimate_tokens_from_text(prompt_text)
        output_tokens = response.get("output_tokens") or estimate_tokens_from_text(answer_text)
        cost = estimate_cost(input_tokens, output_tokens)
        sources = _extract_sources(response)

        usage_info = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": cost,
            "cache_hit": False,
            "latency_ms": round(latency_ms, 2)
        }
        response["usage"] = usage_info

        # Save to cache if response was successful / valid status
        if status != "error":
            self.cache.set(question, response, filters)

        # Log request
        log_rag_request({
            "request_id": req_id,
            "question": question,
            "answer": answer_text,
            "sources": sources,
            "cache_hit": False,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": cost,
            "latency_ms": latency_ms,
            "status": response.get("status", status),
            "error": error_msg
        }, log_file=self.log_file)

        return response
