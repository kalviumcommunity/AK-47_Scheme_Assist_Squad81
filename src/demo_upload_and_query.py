# -*- coding: utf-8 -*-
"""
src/demo_upload_and_query.py - 3.45 Document Upload & Indexing Demonstration
=============================================================================
Demonstrates the full end-to-end runtime lifecycle:
  1. Inspect baseline API health and indexed chunk count.
  2. Ask a question about an unindexed policy ("PM Surya Ghar") -> verify refusal.
  3. Upload the new policy document via POST /documents -> verify structured indexing summary.
  4. Confirm knowledge base grew at runtime via GET /health.
  5. Ask the same question again via POST /query -> verify grounded answer & citation without restarting.
  6. Ask a second specific question ("free electricity units") -> verify accurate retrieval.
  7. Exercise validation error handling (415 unsupported, 400 empty file, 413 oversized).
  8. Save structured results to outputs/sample_upload_run.json and outputs/sample_upload_run.txt.
"""

import io
import os
import sys
import json
from pathlib import Path

# Ensure root directory is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.api import app, UPLOAD_DIR, MAX_UPLOAD_SIZE_BYTES


def run_demo():
    print("=" * 80)
    print("  3.45 Document Upload & Indexing Endpoint - Runtime Demonstration")
    print("=" * 80)

    client = TestClient(app)
    results = {
        "experiment": "3.45 Document Upload & Indexing Endpoint",
        "steps": {},
    }

    # ──────────────────────────────────────────────────────────────────────────
    # Step 1: Health check before upload
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[Step 1] Checking baseline system health before upload...")
    resp_health_before = client.get("/health")
    health_before = resp_health_before.json()
    chunks_before = health_before["indexed_chunks"]
    print(f"  Status         : {health_before['status']}")
    print(f"  Indexed Chunks : {chunks_before}")
    results["steps"]["1_baseline_health"] = health_before

    # ──────────────────────────────────────────────────────────────────────────
    # Step 2: Query about new policy BEFORE upload
    # ──────────────────────────────────────────────────────────────────────────
    test_q1 = "What toolkit incentive and collateral-free loan support is provided under PM Vishwakarma Scheme?"
    print(f"\n[Step 2] Querying RAG before document upload:\n  Q: \"{test_q1}\"")
    resp_query_before = client.post("/query", json={"question": test_q1})
    q_before_data = resp_query_before.json()
    print(f"  Response Status: {q_before_data.get('status')}")
    print(f"  Answer Snippet : {q_before_data.get('answer')[:120]}...")
    print(f"  Sources Cited  : {q_before_data.get('sources')}")
    results["steps"]["2_query_before_upload"] = {
        "question": test_q1,
        "response": q_before_data,
    }

    # ──────────────────────────────────────────────────────────────────────────
    # Step 3: Upload new policy document via POST /documents
    # ──────────────────────────────────────────────────────────────────────────
    policy_path = Path("data") / "sample_new_policy.md"
    print(f"\n[Step 3] Uploading new policy document '{policy_path}' via POST /documents...")
    policy_bytes = policy_path.read_bytes()
    file_payload = ("sample_new_policy.md", io.BytesIO(policy_bytes), "text/markdown")

    resp_upload = client.post("/documents", files={"file": file_payload})
    upload_data = resp_upload.json()
    print(f"  HTTP Status Code : {resp_upload.status_code}")
    print(f"  Upload Status    : {upload_data.get('status')}")
    print(f"  Filename         : {upload_data.get('filename')}")
    print(f"  Stored Document  : {upload_data.get('summary', {}).get('document')}")
    print(f"  Chunks Created   : {upload_data.get('summary', {}).get('chunks')}")
    print(f"  Records Indexed  : {upload_data.get('summary', {}).get('indexed')}")
    results["steps"]["3_upload_document"] = {
        "status_code": resp_upload.status_code,
        "response": upload_data,
    }

    # ──────────────────────────────────────────────────────────────────────────
    # Step 4: Health check after upload (verify runtime vector store growth)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[Step 4] Checking system health after upload (runtime growth verification)...")
    resp_health_after = client.get("/health")
    health_after = resp_health_after.json()
    chunks_after = health_after["indexed_chunks"]
    growth = chunks_after - chunks_before
    print(f"  Previous Indexed Chunks : {chunks_before}")
    print(f"  Current Indexed Chunks  : {chunks_after} (+{growth} new records)")
    results["steps"]["4_health_after_upload"] = {
        "health": health_after,
        "delta_chunks": growth,
    }

    # ──────────────────────────────────────────────────────────────────────────
    # Step 5: Follow-up query AFTER upload (Runtime searchability proof)
    # ──────────────────────────────────────────────────────────────────────────
    print(f"\n[Step 5] Re-querying RAG AFTER document upload (without restart):\n  Q: \"{test_q1}\"")
    resp_query_after = client.post("/query", json={"question": test_q1})
    q_after_data = resp_query_after.json()
    print(f"  Response Status: {q_after_data.get('status')}")
    print(f"  Grounded Answer: {q_after_data.get('answer')}")
    print(f"  Sources Cited  :")
    for s in q_after_data.get("sources", []):
        print(f"    - Source: {s.get('source')} | Chunk ID: {s.get('chunk_id')} | Score: {s.get('score')}")
    results["steps"]["5_query_after_upload"] = {
        "question": test_q1,
        "response": q_after_data,
    }

    # ──────────────────────────────────────────────────────────────────────────
    # Step 6: Second specific query on newly indexed content
    # ──────────────────────────────────────────────────────────────────────────
    test_q2 = "What is the daily stipend during basic skill training under PM Vishwakarma Yojana?"
    print(f"\n[Step 6] Running second query on newly indexed content:\n  Q: \"{test_q2}\"")
    resp_query2 = client.post("/query", json={"question": test_q2})
    q2_data = resp_query2.json()
    print(f"  Response Status: {q2_data.get('status')}")
    print(f"  Grounded Answer: {q2_data.get('answer')}")
    print(f"  Sources Cited  :")
    for s in q2_data.get("sources", []):
        print(f"    - Source: {s.get('source')} | Chunk ID: {s.get('chunk_id')} | Score: {s.get('score')}")
    results["steps"]["6_second_query_after_upload"] = {
        "question": test_q2,
        "response": q2_data,
    }

    # ──────────────────────────────────────────────────────────────────────────
    # Step 7: Error handling validation
    # ──────────────────────────────────────────────────────────────────────────
    print("\n[Step 7] Validating error handling contracts:")

    # 7A: Unsupported format (.exe)
    resp_415 = client.post(
        "/documents",
        files={"file": ("malicious_payload.exe", io.BytesIO(b"binary_junk"), "application/octet-stream")},
    )
    print(f"  7A. Unsupported Format (.exe) -> HTTP {resp_415.status_code} ({resp_415.json().get('detail')})")

    # 7B: Empty file (0 bytes)
    resp_400 = client.post(
        "/documents",
        files={"file": ("empty_file.md", io.BytesIO(b""), "text/markdown")},
    )
    print(f"  7B. Empty File (0 bytes)       -> HTTP {resp_400.status_code} ({resp_400.json().get('detail')})")

    # 7C: Oversized file (>10MB)
    oversized_bytes = b"X" * (MAX_UPLOAD_SIZE_BYTES + 1024)
    resp_413 = client.post(
        "/documents",
        files={"file": ("oversized_file.txt", io.BytesIO(oversized_bytes), "text/plain")},
    )
    print(f"  7C. Oversized File (>10MB)     -> HTTP {resp_413.status_code} ({resp_413.json().get('detail')})")

    results["steps"]["7_error_handling"] = {
        "unsupported_format": {"status": resp_415.status_code, "detail": resp_415.json()},
        "empty_file": {"status": resp_400.status_code, "detail": resp_400.json()},
        "oversized_file": {"status": resp_413.status_code, "detail": resp_413.json()},
    }

    # ──────────────────────────────────────────────────────────────────────────
    # Step 8: Persist structured outputs
    # ──────────────────────────────────────────────────────────────────────────
    output_dir = Path("outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / "sample_upload_run.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    txt_path = output_dir / "sample_upload_run.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  3.45 Document Upload & Indexing Endpoint - Sample Run Summary\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"1. Baseline Health:\n   Indexed Chunks: {chunks_before}\n\n")
        f.write(f"2. Query Before Upload:\n   Q: {test_q1}\n   Status: {q_before_data.get('status')}\n\n")
        f.write(f"3. Upload Document:\n   Filename: {upload_data.get('filename')}\n   Stored Path: {upload_data.get('summary', {}).get('document')}\n   Chunks Created: {upload_data.get('summary', {}).get('chunks')}\n   Records Indexed: {upload_data.get('summary', {}).get('indexed')}\n\n")
        f.write(f"4. Health After Upload:\n   Indexed Chunks: {chunks_after} (+{growth})\n\n")
        f.write(f"5. Follow-Up Query After Upload:\n   Q: {test_q1}\n   Status: {q_after_data.get('status')}\n   Answer: {q_after_data.get('answer')}\n   Top Citation: {q_after_data.get('sources', [{}])[0].get('source')}\n\n")
        f.write(f"6. Second Query on New Document:\n   Q: {test_q2}\n   Status: {q2_data.get('status')}\n   Answer: {q2_data.get('answer')}\n   Top Citation: {q2_data.get('sources', [{}])[0].get('source')}\n\n")
        f.write("7. Error Handling Verification:\n")
        f.write(f"   Unsupported Format (.exe): HTTP {resp_415.status_code}\n")
        f.write(f"   Empty File (0 bytes): HTTP {resp_400.status_code}\n")
        f.write(f"   Oversized File (>10MB): HTTP {resp_413.status_code}\n")
        f.write("\n" + "=" * 80 + "\n")

    print(f"\n[Step 8] Artifacts written successfully:")
    print(f"  - {json_path}")
    print(f"  - {txt_path}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_demo()
