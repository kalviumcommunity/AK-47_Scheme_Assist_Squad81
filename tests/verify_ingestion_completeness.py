import os
import sys
import json

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.corpus_pipeline import run_corpus_ingestion, persist_pipeline_artifacts


def verify_ingestion_completeness():
    print("=" * 80)
    print("  [VERIFICATION SUITE] 3.24 Corpus Preparation & Ingestion Validation")
    print("=" * 80)

    data_dir = "data"
    output_dir = "outputs"

    # 1. Run End-to-End Pipeline
    print("\n[STEP 1] Running Full Pipeline over Corpus Directory ('data/')...")
    files, docs, chunks, failures, summary = run_corpus_ingestion(data_dir=data_dir)

    print(f"  * Files Discovered On Disk : {len(files)}")
    print(f"  * Successfully Ingested    : {len(docs)}")
    print(f"  * Total Chunks Created     : {len(chunks)}")
    print(f"  * Recorded Failures/Skips  : {len(failures)}")

    # 2. Strict Mathematical Completeness Assertion (No Silent Drops)
    print("\n[STEP 2] Validating Ingestion Completeness Equation...")
    print(f"  Equation Check: {len(files)} (files) == {len(docs)} (docs) + {len(failures)} (failures)")
    assert len(files) == len(docs) + len(failures), (
        f"CRITICAL FAILURE: Discovered files ({len(files)}) does not equal "
        f"ingested docs ({len(docs)}) + failures ({len(failures)})! A file was silently dropped."
    )
    print("  --> PASS: 100% of files accounted for. Zero silent drops detected!")

    # 3. Verify Failure Capture
    print("\n[STEP 3] Verifying Explicit Failure Detection & Logging...")
    assert len(failures) > 0, "Expected at least 1 controlled failure (unsupported_file.xyz)!"
    for f in failures:
        print(f"  * Caught Failed File : {f.filename} [{f.format}]")
        print(f"    Error Class        : {f.error_type}")
        print(f"    Error Details      : {f.error_message}")
        assert f.filename, "Failure record missing filename!"
        assert f.error_message, "Failure record missing error_message!"
    print("  --> PASS: All unparseable / unsupported files intercepted and recorded with full trace.")

    # 4. Inspect Sample Chunks and Metadata Integrity
    print("\n[STEP 4] Auditing Chunk Structure & Metadata Integrity...")
    required_tags = {"source", "chunk_index", "position", "section", "token_count", "char_start", "char_end", "content_hash"}
    
    assert len(chunks) > 0, "No chunks generated from corpus!"
    for idx, c in enumerate(chunks):
        assert "text" in c and len(c["text"].strip()) > 0, f"Chunk {idx} has empty text!"
        assert "metadata" in c, f"Chunk {idx} missing metadata!"
        meta = c["metadata"]
        missing = required_tags - set(meta.keys())
        assert not missing, f"Chunk {idx} missing mandatory tags: {missing}"
        assert meta["token_count"] > 0, f"Chunk {idx} token count must be positive!"

    print(f"  --> PASS: All {len(chunks)} chunks verified with complete, consistent metadata tags.")

    # 5. Persist Pipeline Artifacts and Verify on Disk
    print("\n[STEP 5] Persisting & Verifying Pipeline Artifacts on Disk...")
    persist_pipeline_artifacts(summary, chunks, output_dir=output_dir)

    expected_files = [
        "ingestion_validation_summary.json",
        "ingestion_validation_summary.txt",
        "ingestion_manifest.json",
        "sample_validated_chunks.json"
    ]

    for fname in expected_files:
        fpath = os.path.join(output_dir, fname)
        assert os.path.exists(fpath), f"Expected artifact '{fpath}' does not exist!"
        file_size = os.path.getsize(fpath)
        assert file_size > 0, f"Artifact '{fpath}' is empty (0 bytes)!"
        print(f"  * Verified Artifact : {fname} ({file_size} bytes)")

    print("\n" + "=" * 80)
    print("  [SUCCESS] All Corpus Preparation & Ingestion Validation Checks Passed!")
    print("=" * 80)


if __name__ == "__main__":
    verify_ingestion_completeness()
