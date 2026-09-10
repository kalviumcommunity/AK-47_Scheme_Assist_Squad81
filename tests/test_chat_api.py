# -*- coding: utf-8 -*-
"""
tests/test_chat_api.py - Unit & Integration tests for /api/chat & /api/health
=============================================================================
Verifies:
  1. GET /api/health returns 200 and healthy status.
  2. POST /api/chat rejects empty questions with 400.
  3. POST /api/chat rejects questions failing length constraints (<3 chars) with 422.
  4. POST /api/chat handles out-of-domain questions with grounded refusal.
  5. POST /api/chat returns structured JSON with required fields (answer, eligibility, benefits,
     application_process, documents_required, sources).
  6. Real Gemini API and SchemeRetriever integration.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure root directory is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.api import app


class TestChatApi(unittest.TestCase):
    """Test suite verifying SchemeAssist /api/chat and /api/health endpoints."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_api_health_endpoint(self):
        """Verifies GET /api/health returns 200 and operational stats."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("chat_model", data)
        self.assertIn("embedding_model", data)
        self.assertIn("indexed_chunks", data)
        self.assertGreaterEqual(data["indexed_chunks"], 20)

    def test_empty_question_returns_400(self):
        """Verifies POST /api/chat rejects empty/whitespace questions with 400."""
        response = self.client.post("/api/chat", json={"question": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.json()["detail"].lower())

    def test_too_short_question_returns_422(self):
        """Verifies POST /api/chat rejects question with < 3 characters with 422."""
        response = self.client.post("/api/chat", json={"question": "hi"})
        self.assertEqual(response.status_code, 422)

    def test_out_of_domain_returns_refusal(self):
        """Verifies POST /api/chat refuses out-of-domain topics without hallucination."""
        response = self.client.post("/api/chat", json={"question": "How do I become a supersonic jet pilot?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("I could not find this information", data["answer"])
        self.assertEqual(data["sources"], [])
        self.assertEqual(data["status"], "refused_weak_context")

    @patch("src.api.make_completion")
    def test_gemini_success_returns_structured_json(self, mock_make_completion):
        """Verifies successful Gemini API call returns full structured JSON."""
        mock_make_completion.return_value = '''{
            "answer": "PM-KISAN provides income support of Rs 6,000 per year.",
            "eligibility": "Small and marginal landholding farmer families.",
            "benefits": "Rs 6,000 annually in three equal installments of Rs 2,000.",
            "application_process": ["Register on PM-KISAN portal", "Authenticate with Aadhaar"],
            "documents_required": ["Aadhaar card", "Land ownership document", "Bank account details"]
        }'''

        response = self.client.post("/api/chat", json={"question": "What is PM-KISAN eligibility and benefits?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check required fields
        self.assertIn("answer", data)
        self.assertIn("eligibility", data)
        self.assertIn("benefits", data)
        self.assertIn("application_process", data)
        self.assertIn("documents_required", data)
        self.assertIn("sources", data)

        self.assertIn("6,000", data["answer"])
        self.assertIsInstance(data["application_process"], list)
        self.assertGreater(len(data["application_process"]), 0)
        self.assertIsInstance(data["documents_required"], list)
        self.assertGreater(len(data["documents_required"]), 0)
        self.assertIsInstance(data["sources"], list)
        self.assertGreater(len(data["sources"]), 0)

    @patch("src.api.make_completion")
    def test_gemini_error_returns_error_status(self, mock_make_completion):
        """Verifies Gemini generation failure returns error status without hallucination."""
        mock_make_completion.return_value = None

        response = self.client.post("/api/chat", json={"question": "What is PM-KISAN?"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("Unable to generate", data["answer"])


if __name__ == "__main__":
    unittest.main()
