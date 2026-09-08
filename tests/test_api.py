# -*- coding: utf-8 -*-
"""
tests/test_api.py - Unit and Integration Tests for 3.44 Backend API for RAG Service
===================================================================================
Tests all five core API capabilities:
  1. GET /health returns 200 and loads configurations from environment.
  2. GET / returns 200 and discovery metadata.
  3. POST /query returns 200 with structured JSON (answer, sources, status) for valid questions.
  4. POST /query returns 'refused_weak_context' with empty sources for out-of-domain questions.
  5. POST /query returns 400 for empty or whitespace-only questions.
  6. POST /query returns 422 for questions failing length constraints (<3 chars).
  7. POST /query returns 422 for missing required body fields.
"""

import os
import sys
import unittest

# Ensure root directory is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.api import app
from src.config import EMBED_MODEL, VECTOR_DB_URL, COLLECTION_NAME


class TestRagBackendApi(unittest.TestCase):
    """Test suite verifying SchemeAssist RAG backend API endpoints and error contracts."""

    @classmethod
    def setUpClass(cls):
        """Instantiate FastAPI test client once for all tests."""
        cls.client = TestClient(app)

    def test_root_endpoint(self):
        """Verifies GET / returns 200 and discovery links."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("service", data)
        self.assertEqual(data["status"], "operational")
        self.assertEqual(data["query_url"], "/query")

    def test_health_endpoint_loads_env_config(self):
        """Verifies Task 4: config loaded from environment and health report."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["embedding_model"], EMBED_MODEL)
        self.assertEqual(data["vector_db_url"], VECTOR_DB_URL)
        self.assertEqual(data["collection_name"], COLLECTION_NAME)
        self.assertIn("indexed_chunks", data)
        self.assertGreaterEqual(data["indexed_chunks"], 0)

    def test_query_pmkisan_returns_structured_json(self):
        """Verifies Tasks 1 & 2: Valid question yields 200 and structured response."""
        payload = {"question": "What is the annual financial assistance provided under PM-KISAN?"}
        response = self.client.post("/query", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Verify contract fields
        self.assertIn("answer", data)
        self.assertIn("sources", data)
        self.assertIn("status", data)
        self.assertEqual(data["status"], "answered")

        # Verify answer quality
        self.assertTrue(len(data["answer"]) > 10)
        self.assertTrue("6,000" in data["answer"] or "PM-KISAN" in data["answer"])

        # Verify structured sources
        self.assertIsInstance(data["sources"], list)
        self.assertGreater(len(data["sources"]), 0)
        for src in data["sources"]:
            self.assertIn("source", src)
            self.assertIn("chunk_id", src)
            self.assertIn("score", src)
            self.assertIsNotNone(src["source"])

    def test_query_ayushman_bharat_returns_grounded_answer(self):
        """Verifies another welfare scheme query returns grounded answer."""
        payload = {"question": "What hospitalisation cover is provided under Ayushman Bharat PM-JAY?"}
        response = self.client.post("/query", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "answered")
        self.assertGreater(len(data["sources"]), 0)

    def test_query_out_of_domain_refusal(self):
        """Verifies guardrail refusal for queries outside verified context."""
        payload = {"question": "What flight license is required to pilot a commercial supersonic jet?"}
        response = self.client.post("/query", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "refused_weak_context")
        self.assertEqual(data["sources"], [])
        self.assertIn("not have sufficient verified information", data["answer"])

    def test_query_validation_whitespace_returns_400(self):
        """Verifies Task 3: Whitespace-only question returns 400 Bad Request."""
        payload = {"question": "      "}
        response = self.client.post("/query", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("detail", data)

    def test_query_validation_too_short_returns_422(self):
        """Verifies Task 3: Pydantic Field constraint (<3 chars) returns 422."""
        payload = {"question": "ab"}
        response = self.client.post("/query", json=payload)
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data.get("status"), "validation_error")

    def test_query_validation_missing_body_returns_422(self):
        """Verifies Task 3: Missing question attribute returns 422."""
        payload = {}
        response = self.client.post("/query", json=payload)
        self.assertEqual(response.status_code, 422)
        data = response.json()
        self.assertEqual(data.get("status"), "validation_error")


if __name__ == "__main__":
    unittest.main()
