import os
import sys
import json
from fastapi.testclient import TestClient

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api import app, get_pipeline

def test_streaming_and_citations():
    print("=" * 75)
    print("  [TEST] Running SSE Answer Streaming & Citation Tests")
    print("=" * 75)

    # Initialize vector store & embeddings
    get_pipeline()

    client = TestClient(app)

    with TestClient(app) as client:
        # Test 1: Web Chat UI Endpoint (/ui)
        print("\n[TEST 1] Testing /ui static chat endpoint...")
        ui_resp = client.get("/ui")
        assert ui_resp.status_code == 200, f"Expected 200 OK for /ui, got {ui_resp.status_code}"
        assert "SchemeAssist RAG Assistant" in ui_resp.text, "UI HTML content mismatch"
        print("--> [PASS] Task 1 & 3: /ui Chat interface served successfully.")

        # Test 2: SSE Streaming Endpoint (/query_stream) - Task 1 & 2
        print("\n[TEST 2] Testing /query_stream SSE endpoint...")
        payload = {"question": "What is the annual income limit for welfare assistance?"}
        response = client.post("/query_stream", json=payload)
        
        assert response.status_code == 200, f"Expected 200 OK for /query_stream, got {response.status_code}"
        assert "text/event-stream" in response.headers.get("content-type", ""), "Content-Type must be text/event-stream"
        
        body_text = "".join([chunk for chunk in response.iter_text()])
        assert "event: metadata" in body_text, f"Missing 'event: metadata' in body: {body_text[:300]}"
        assert "event: token" in body_text, "Missing 'token' SSE event"
        assert "event: done" in body_text, "Missing 'done' SSE event"
        print("--> [PASS] Task 1: SSE Progressive token streaming verified.")

        # Test 3: Citation & Source Metadata Verification - Task 2 & 3
        print("\n[TEST 3] Verifying citations & metadata payload structure...")
        events = body_text.split("\n\n")
        metadata_event = None
        for evt in events:
            if "event: metadata" in evt:
                data_line = [l for l in evt.split("\n") if l.startswith("data:")][0]
                metadata_event = json.loads(data_line.replace("data:", "").strip())
                break

        assert metadata_event is not None, "Metadata event missing from stream"
        assert "sources" in metadata_event, "Sources missing from metadata event"
        assert len(metadata_event["sources"]) > 0, "No sources returned in metadata"
        
        first_src = metadata_event["sources"][0]
        assert "citation" in first_src, "Source citation marker missing"
        assert "source" in first_src, "Source filename missing"
        assert "chunk_id" in first_src, "Source chunk ID missing"
        assert "section" in first_src, "Source section missing"
        print(f"--> [PASS] Task 2 & 3: Citation metadata verified ({first_src['citation']} -> {first_src['source']}).")

        # Test 4: Streaming Error Handling - Task 4
        print("\n[TEST 4] Testing invalid request error handling...")
        invalid_payload = {"question": "ab"}  # Fails min 3 char requirement
        err_resp = client.post("/query_stream", json=invalid_payload)
        assert err_resp.status_code in [400, 422] or "event: error" in err_resp.text, "Error response missing from failed stream request"
        print("--> [PASS] Task 4: Streaming error handled gracefully.")

    print("\n" + "=" * 75)
    print("  [ALL SSE STREAMING & CITATION TESTS PASSED SUCCESSFULLY]")
    print("=" * 75)


if __name__ == "__main__":
    test_streaming_and_citations()
