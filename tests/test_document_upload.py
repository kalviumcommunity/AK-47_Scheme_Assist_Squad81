# -*- coding: utf-8 -*-
"""
tests/test_document_upload.py - Unit & Integration Tests for 3.45 Document Upload & Indexing
=============================================================================================
Tests all core upload & indexing capabilities:
  1. POST /documents accepts valid Markdown (.md) document and indexes chunks into VectorStore.
  2. POST /documents accepts valid plain text (.txt) document and indexes chunks.
  3. Runtime Searchability: Uploading a new policy document immediately enables POST /query
     to retrieve, cite, and answer questions from the new document without restarting the app.
  4. POST /documents returns 415 for unsupported file types (.exe, .zip).
  5. POST /documents returns 400 for empty files (0 bytes).
  6. POST /documents returns 413 for oversized files (> 10 MB).
  7. POST /documents returns 422 for documents with no readable content.
  8. Path traversal sanitization: malicious filenames (e.g. ../../test.md) are stored safely.
  9. GET /documents lists indexed documents.
"""

import io
import os
import sys
import shutil
from pathlib import Path
import unittest

# Ensure root directory is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from src.api import app, UPLOAD_DIR, MAX_UPLOAD_SIZE_BYTES


class TestDocumentUploadAndIndexing(unittest.TestCase):
    """Integration test suite for Document Upload & Runtime Indexing."""

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        # Clean up temporary test files from uploads/
        test_prefixes = ["test_", "evil_", "oversized_", "empty_", "runtime_"]
        if UPLOAD_DIR.exists():
            for item in UPLOAD_DIR.iterdir():
                if item.is_file() and any(item.name.startswith(p) for p in test_prefixes):
                    try:
                        item.unlink()
                    except Exception:
                        pass

    def test_upload_markdown_document_success(self):
        """Task 1 & 2: Valid Markdown document is stored, ingested, chunked, embedded, and indexed."""
        content = (
            "# National Green Hydrogen Mission\n\n"
            "## Mission Overview\n"
            "The National Green Hydrogen Mission aims to facilitate production of 5 MMT "
            "of Green Hydrogen per annum by 2030, with an associated renewable energy capacity "
            "addition of about 125 GW in India.\n\n"
            "## Financial Outlay\n"
            "The initial financial outlay for the Mission is Rs 19,744 crore, including Rs 17,490 "
            "crore for the Strategic Interventions for Green Hydrogen Transition (SIGHT) programme.\n"
        ).encode("utf-8")

        file_payload = ("test_green_hydrogen.md", io.BytesIO(content), "text/markdown")
        response = self.client.post("/documents", files={"file": file_payload})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["status"], "indexed")
        self.assertEqual(data["filename"], "test_green_hydrogen.md")
        self.assertIn("summary", data)
        self.assertEqual(data["summary"]["document"], "uploads/test_green_hydrogen.md")
        self.assertGreaterEqual(data["summary"]["chunks"], 1)
        self.assertGreaterEqual(data["summary"]["indexed"], 1)

        # Confirm file exists on disk
        stored_path = UPLOAD_DIR / "test_green_hydrogen.md"
        self.assertTrue(stored_path.exists())

    def test_upload_text_document_success(self):
        """Task 1 & 2: Valid .txt file is stored and indexed successfully."""
        content = (
            "Kisan Credit Card Scheme\n"
            "The Kisan Credit Card (KCC) scheme provides adequate and timely credit support "
            "from the banking system to farmers for cultivation and post-harvest expenses.\n"
            "Farmers are eligible for short-term credit limit of up to Rs 3 lakh with 7 percent "
            "interest rate and a 3 percent prompt repayment incentive."
        ).encode("utf-8")

        file_payload = ("test_kcc_guide.txt", io.BytesIO(content), "text/plain")
        response = self.client.post("/documents", files={"file": file_payload})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "indexed")
        self.assertEqual(data["filename"], "test_kcc_guide.txt")
        self.assertGreaterEqual(data["summary"]["indexed"], 1)

    def test_runtime_searchability_without_restart(self):
        """Task 3: Prove that newly uploaded document content becomes searchable at runtime."""
        # 1. New distinct policy document
        new_scheme_content = (
            "# PM Surya Ghar Muft Bijli Yojana Guidelines\n\n"
            "## Scheme Benefits and Free Units\n"
            "Under the PM Surya Ghar Muft Bijli Yojana, households receive up to 300 units "
            "of free electricity every month through rooftop solar systems.\n\n"
            "## Solar Subsidy Structure\n"
            "The central government provides a direct subsidy of Rs 30,000 for 1 kW systems, "
            "Rs 60,000 for 2 kW systems, and Rs 78,000 for 3 kW and higher rooftop solar systems.\n\n"
            "## Application Process\n"
            "Citizens can register on the national rooftop solar portal using their electricity "
            "consumer number and bank account details for direct benefit transfer.\n"
        ).encode("utf-8")

        # 2. Upload the new document via /documents
        file_payload = ("runtime_surya_ghar_policy.md", io.BytesIO(new_scheme_content), "text/markdown")
        upload_resp = self.client.post("/documents", files={"file": file_payload})
        self.assertEqual(upload_resp.status_code, 200)
        upload_data = upload_resp.json()
        self.assertEqual(upload_data["status"], "indexed")
        self.assertGreaterEqual(upload_data["summary"]["indexed"], 1)

        # 3. Query immediately through /query without restarting the server
        query_payload = {"question": "What is the maximum rooftop solar subsidy under PM Surya Ghar Muft Bijli Yojana?"}
        query_resp = self.client.post("/query", json=query_payload)

        self.assertEqual(query_resp.status_code, 200)
        query_data = query_resp.json()

        # 4. Verify answer is grounded in the newly uploaded document and cites it
        self.assertEqual(query_data["status"], "answered")
        self.assertTrue(len(query_data["answer"]) > 10)
        self.assertTrue(
            "78,000" in query_data["answer"] or "Surya Ghar" in query_data["answer"] or "300 units" in query_data["answer"]
        )

        sources = query_data.get("sources", [])
        self.assertGreater(len(sources), 0)
        top_source = sources[0]["source"]
        self.assertIn("runtime_surya_ghar_policy", top_source)

    def test_upload_unsupported_format_returns_415(self):
        """Task 4: Uploading unsupported formats (.exe, .zip) fails with HTTP 415."""
        dummy_binary = b"MZ\x90\x00\x03\x00\x00\x00"
        file_payload = ("test_malware.exe", io.BytesIO(dummy_binary), "application/octet-stream")
        response = self.client.post("/documents", files={"file": file_payload})

        self.assertEqual(response.status_code, 415)
        self.assertIn("Unsupported file type", response.json()["detail"])

    def test_upload_empty_file_returns_400(self):
        """Task 4: Uploading an empty 0-byte file fails with HTTP 400."""
        empty_content = b""
        file_payload = ("empty_document.md", io.BytesIO(empty_content), "text/markdown")
        response = self.client.post("/documents", files={"file": file_payload})

        self.assertEqual(response.status_code, 400)
        self.assertIn("empty", response.json()["detail"].lower())

    def test_upload_oversized_file_returns_413(self):
        """Task 4: Uploading file exceeding MAX_UPLOAD_SIZE_BYTES fails with HTTP 413."""
        # Create a payload larger than 10MB limit (10MB + 1024 bytes)
        oversized_bytes = b"A" * (MAX_UPLOAD_SIZE_BYTES + 1024)
        file_payload = ("oversized_doc.txt", io.BytesIO(oversized_bytes), "text/plain")
        response = self.client.post("/documents", files={"file": file_payload})

        self.assertEqual(response.status_code, 413)
        self.assertIn("exceeds", response.json()["detail"].lower())

    def test_upload_corrupt_or_unreadable_file_returns_422(self):
        """Task 4: Uploading file that produces no clean readable text returns HTTP 422."""
        whitespace_only = b"    \n\n\t\t\r\n   "
        file_payload = ("test_blank.txt", io.BytesIO(whitespace_only), "text/plain")
        response = self.client.post("/documents", files={"file": file_payload})

        self.assertEqual(response.status_code, 422)
        self.assertIn("no readable text", response.json()["detail"].lower())

    def test_filename_path_traversal_sanitization(self):
        """Task 1: Path traversal characters are stripped so files are safely kept in UPLOAD_DIR."""
        content = b"# Normal Title\n\nNormal content for safe upload path test."
        traversal_filename = "../../evil_outside.md"
        file_payload = (traversal_filename, io.BytesIO(content), "text/markdown")

        response = self.client.post("/documents", files={"file": file_payload})
        self.assertEqual(response.status_code, 200)

        # File must be stored inside UPLOAD_DIR, not in parent directories
        sanitized_path = UPLOAD_DIR / "evil_outside.md"
        self.assertTrue(sanitized_path.exists())

        # Parent directories must NOT contain evil_outside.md
        self.assertFalse((Path(".") / "evil_outside.md").exists())

    def test_list_documents_endpoint(self):
        """Verifies GET /documents returns list of stored documents and count."""
        response = self.client.get("/documents")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("documents", data)
        self.assertIn("total", data)
        self.assertIsInstance(data["documents"], list)


if __name__ == "__main__":
    unittest.main()
