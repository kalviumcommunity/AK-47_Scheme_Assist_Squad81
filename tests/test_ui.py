# -*- coding: utf-8 -*-
"""
tests/test_ui.py - Unit & Integration Tests for SchemeAssist Frontend & RAG API
=================================================================================
Verifies:
  1. GET /ui returns 200 OK with rich HTML5 UI containing required DOM identifiers.
  2. CORS headers are properly configured on RAG API routes to support React frontend (ports 3000 & 5173).
  3. GET / discovery includes 'ui_url' pointing to /ui.
  4. React + Vite application files (package.json, src/App.jsx, src/main.jsx, src/index.css, dist/index.html) exist.
  5. RAG AI Chat components implement askRagQuestion, SourceCitation, and error handling contracts.
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

    def test_cors_headers_enabled_for_frontend(self):
        """Verifies CORS preflight headers allow React client on http://localhost:3000."""
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

    def test_react_frontend_files_exist(self):
        """Verifies React + Vite project structure and configuration."""
        self.assertTrue((self.frontend_dir / "package.json").exists())
        self.assertTrue((self.frontend_dir / "src" / "App.jsx").exists())
        self.assertTrue((self.frontend_dir / "src" / "main.jsx").exists())
        self.assertTrue((self.frontend_dir / "src" / "index.css").exists())
        self.assertTrue((self.frontend_dir / "dist" / "index.html").exists())

    def test_react_page_and_api_contracts(self):
        """Verifies AI Assistant and API client implement RAG query and source citation contracts."""
        api_js = (self.frontend_dir / "src" / "services" / "api.js").read_text(encoding="utf-8")
        self.assertIn("askRagQuestion", api_js)
        self.assertIn("uploadDocument", api_js)
        self.assertIn("getSystemHealth", api_js)

        chat_page = (self.frontend_dir / "src" / "pages" / "citizen" / "AIAssistantPage.jsx").read_text(encoding="utf-8")
        self.assertIn("askRagQuestion", chat_page)
        self.assertIn("handleSend", chat_page)
        self.assertIn("UploadModal", chat_page)

        citation_component = (self.frontend_dir / "src" / "components" / "chat" / "SourceCitation.jsx").read_text(encoding="utf-8")
        self.assertIn("SourceCitation", citation_component)
        self.assertIn("sources", citation_component)
        self.assertIn("chunk_id", citation_component)


if __name__ == "__main__":
    unittest.main()
