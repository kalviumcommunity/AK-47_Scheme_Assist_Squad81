# -*- coding: utf-8 -*-
"""
tests/test_chat_api.py - Unit & Integration tests for /api/chat & /api/health
=============================================================================
Verifies:
  1. GET /api/health returns 200 and healthy status.
  2. POST /api/chat rejects empty questions with 400.
  3. POST /api/chat rejects questions failing length constraints (<3 chars) with 422.
  4. POST /api/chat handles out-of-domain questions with grounded refusal.
  5. POST /api/chat adheres strictly to OpenAI call & error contract without mock fallbacks.
  6. POST /api/chat formats JSON with required fields (answer, eligibility, benefits,
     application_process, documents_required, sources).
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Ensure root directory is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from openai import RateLimitError, AuthenticationError
import httpx

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

    @patch("src.api.OpenAI")
    def test_openai_success_returns_structured_json(self, mock_openai_cls):
        """Verifies successful OpenAI API call returns full structured JSON."""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(
                message=MagicMock(
                    content='''{
                        "answer": "PM-KISAN provides income support of Rs 6,000 per year.",
                        "eligibility": "Small and marginal landholding farmer families.",
                        "benefits": "Rs 6,000 annually in three equal installments of Rs 2,000.",
                        "application_process": ["Register on PM-KISAN portal", "Authenticate with Aadhaar"],
                        "documents_required": ["Aadhaar card", "Land ownership document", "Bank account details"],
                        "sources": [
                            {
                                "scheme": "PM-KISAN",
                                "source": "pmkisan_scheme_doc.md",
                                "section": "Financial Benefits"
                            }
                        ]
                    }'''
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_completion

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
        self.assertEqual(data["sources"][0]["scheme"], "PM-KISAN")

    @patch("src.api.OpenAI")
    def test_openai_rate_limit_error_returns_429(self, mock_openai_cls):
        """Verifies OpenAI rate limit / credit exhaustion returns 429 and does NOT return fake data."""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        fake_response = httpx.Response(
            status_code=429,
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
            json={"error": {"message": "You have no credits remaining.", "type": "insufficient_quota"}},
        )
        mock_client.chat.completions.create.side_effect = RateLimitError(
            message="Credit balance exhausted",
            response=fake_response,
            body=fake_response.json(),
        )

        response = self.client.post("/api/chat", json={"question": "Am I eligible for PM-KISAN?"})
        self.assertEqual(response.status_code, 429)
        self.assertIn("quota", response.json()["detail"].lower())

    @patch("src.api.OpenAI")
    def test_openai_auth_error_returns_401(self, mock_openai_cls):
        """Verifies invalid OpenAI API key returns 401 and does NOT return fake data."""
        mock_client = MagicMock()
        mock_openai_cls.return_value = mock_client

        fake_response = httpx.Response(
            status_code=401,
            request=httpx.Request("POST", "https://api.openai.com/v1/chat/completions"),
            json={"error": {"message": "Incorrect API key provided.", "type": "invalid_request_error"}},
        )
        mock_client.chat.completions.create.side_effect = AuthenticationError(
            message="Incorrect API key provided.",
            response=fake_response,
            body=fake_response.json(),
        )

        response = self.client.post("/api/chat", json={"question": "How do I apply for Ayushman Bharat?"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("invalid openai api key", response.json()["detail"].lower())


if __name__ == "__main__":
    unittest.main()
