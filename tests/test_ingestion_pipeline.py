import unittest
import os
import sys
import tempfile
import json
from pathlib import Path

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corpus_pipeline import (
    run_corpus_ingestion,
    compute_content_hash,
    extract_raw_text,
    persist_pipeline_artifacts,
    IngestionFailure
)
from src.ingestion import validate_corpus_ingestion


class TestIngestionPipeline(unittest.TestCase):

    def test_content_hash_idempotency(self):
        text = "Sample welfare policy text for hash test."
        hash1 = compute_content_hash(text)
        hash2 = compute_content_hash(text)
        self.assertEqual(hash1, hash2)
        self.assertEqual(len(hash1), 16)

    def test_completeness_reconciliation_on_corpus(self):
        files, docs, chunks, failures, summary = run_corpus_ingestion("data")
        self.assertEqual(len(files), len(docs) + len(failures))
        self.assertTrue(summary.completeness_reconciled)
        self.assertGreater(len(docs), 0)
        self.assertGreater(len(chunks), 0)
        self.assertGreater(len(failures), 0)

    def test_failure_recording_and_graceful_handling(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create one valid doc and one invalid doc
            valid_file = Path(tmpdir) / "valid_doc.md"
            with open(valid_file, "w", encoding="utf-8") as f:
                f.write("# Welfare Scheme Title\nValid content for testing.")

            invalid_file = Path(tmpdir) / "corrupt_data.xyz"
            with open(invalid_file, "w", encoding="utf-8") as f:
                f.write("Raw invalid unparseable format")

            files, docs, chunks, failures, summary = run_corpus_ingestion(tmpdir)
            self.assertEqual(len(files), 2)
            self.assertEqual(len(docs), 1)
            self.assertEqual(len(failures), 1)
            self.assertEqual(failures[0].filename, "corrupt_data.xyz")
            self.assertEqual(summary.total_files_discovered, 2)
            self.assertEqual(summary.total_documents_ingested, 1)
            self.assertEqual(summary.total_failures, 1)

    def test_nonexistent_directory_handling(self):
        files, docs, chunks, failures, summary = run_corpus_ingestion("nonexistent_directory_xyz")
        self.assertEqual(len(files), 0)
        self.assertEqual(len(docs), 0)
        self.assertEqual(len(failures), 0)
        self.assertTrue(summary.completeness_reconciled)

    def test_metadata_consistency_across_chunks(self):
        files, docs, chunks, failures, summary = run_corpus_ingestion("data")
        required_fields = {
            "source", "chunk_index", "position", "section",
            "token_count", "char_start", "char_end", "content_hash"
        }
        for chunk in chunks:
            self.assertIn("text", chunk)
            self.assertIn("metadata", chunk)
            meta = chunk["metadata"]
            for field in required_fields:
                self.assertIn(field, meta, f"Field '{field}' missing from chunk metadata!")
            self.assertGreater(meta["token_count"], 0)

    def test_validate_corpus_ingestion_api(self):
        chunks, summary_dict = validate_corpus_ingestion("data")
        self.assertGreater(len(chunks), 0)
        self.assertTrue(summary_dict["completeness_reconciled"])
        self.assertEqual(
            summary_dict["total_files_discovered"],
            summary_dict["total_documents_ingested"] + summary_dict["total_failures"]
        )

    def test_manifest_persistence(self):
        with tempfile.TemporaryDirectory() as tmp_out:
            files, docs, chunks, failures, summary = run_corpus_ingestion("data")
            persist_pipeline_artifacts(summary, chunks, output_dir=tmp_out)

            manifest_file = os.path.join(tmp_out, "ingestion_manifest.json")
            self.assertTrue(os.path.exists(manifest_file))
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)

            self.assertIn("processed_documents", manifest_data)
            self.assertIn("failed_files", manifest_data)
            self.assertEqual(len(manifest_data["processed_documents"]), len(docs))
            self.assertEqual(len(manifest_data["failed_files"]), len(failures))


if __name__ == "__main__":
    unittest.main()
