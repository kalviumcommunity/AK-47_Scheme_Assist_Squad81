# -*- coding: utf-8 -*-
"""
tests/test_ui.py - Unit & Integration Tests for 3.46 Chat Interface & Query UI (Next.js & API)
=================================================================================================
Verifies:
  1. GET /ui returns 200 OK with rich HTML5 UI containing required DOM identifiers.
  2. CORS headers are properly configured on RAG API routes to support Next.js frontend (port 3000).
  3. GET / discovery includes 'ui_url' pointing to /ui.
  4. Next.js application files (package.json, app/page.js, app/layout.js, app/globals.css) exist and are complete.
  5. Next.js page component contains the required askQuestion, AnswerSources, and error handling contracts.
"""

import os
import sys
import unittest
from pathlib import Path

# Ensure root directory is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.api import app


class TestChatInterfaceAndQueryUI(unittest.TestCase):
    """Test suite for Chat Interface & Query UI."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.frontend_dir = Path(__file__).parent.parent / "frontend"

    def test_ui_endpoint_returns_html_and_200(self):
        """Task 1 & 2: GET /ui serves the interactive web application."""
        response = self.client.get("/ui")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("text/html" in response.headers.get("content-type", ""))

        html = response.text
        # Check required UI elements and DOM IDs
        self.assertIn("SchemeAssist", html)
        self.assertIn("queryInput", html)
        self.assertIn("submitBtn", html)
        self.assertIn("chatContainer", html)
        self.assertIn("systemStatusBadge", html)
        self.assertIn("suggestionChips", html)
        self.assertIn("uploadModal", html)

    def test_cors_headers_enabled_for_nextjs(self):
        """Verifies CORS preflight headers allow Next.js client on http://localhost:3000."""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        }
        response = self.client.options("/query", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access-control-allow-origin", response.headers)

    def test_root_includes_ui_url(self):
        """Verifies GET / discovery lists /ui route."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("ui_url", data)
        self.assertEqual(data["ui_url"], "/ui")

    def test_nextjs_frontend_files_exist(self):
        """Verifies Next.js project structure."""
        self.assertTrue((self.frontend_dir / "package.json").exists())
        self.assertTrue((self.frontend_dir / "app" / "page.js").exists())
        self.assertTrue((self.frontend_dir / "app" / "layout.js").exists())
        self.assertTrue((self.frontend_dir / "app" / "globals.css").exists())

    def test_nextjs_page_contracts(self):
        """Verifies Next.js page component implements question answering and source inspection."""
        page_js = (self.frontend_dir / "app" / "page.js").read_text(encoding="utf-8")
        self.assertIn("askQuestion", page_js)
        self.assertIn("AnswerSources", page_js)
        self.assertIn("sources-container", page_js)
        self.assertIn("handleSubmit", page_js)
        self.assertIn("handlePresetClick", page_js)
        self.assertIn("handleDocumentUpload", page_js)


if __name__ == "__main__":
    unittest.main()
