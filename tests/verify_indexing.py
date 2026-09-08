import os
import sys

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.indexing import run_indexing_pipeline, VectorIndexer
from src.ingestion import load_and_chunk_documents

def test_indexing_tasks():
    print("=" * 75)
    print("  [TEST] Running Vector DB Indexing Automated Verification")
    print("=" * 75)

    data_dir = "data"
    chunks = load_and_chunk_documents(data_dir)
    assert len(chunks) > 0, "Ingestion generated 0 chunks."

    indexer = VectorIndexer(db_dir="data/chroma_db", collection_name="scheme_assist_corpus")
    
    # Task 1 & Task 2: Insert chunks with embeddings, text, metadata
    index_res = indexer.index_chunks(chunks)
    assert index_res["inserted"] == len(chunks), f"Expected {len(chunks)} insertions, got {index_res['inserted']}"
    assert index_res["failures"] == 0, f"Expected 0 failures, got {index_res['failures']}"

    # Task 3: Confirm indexed count
    count_matches, expected_cnt, actual_cnt = indexer.verify_indexed_count(len(chunks))
    assert count_matches, f"Count mismatch! Expected: {expected_cnt}, Actual: {actual_cnt}"
    print(f"--> [PASS] Task 3 Count Match: {actual_cnt}/{expected_cnt} records stored.")

    # Task 4: Spot-check stored integrity
    sample_id = index_res["ids"][0]
    sample_chunk = chunks[0]
    spot_check = indexer.spot_check_record(sample_id, sample_chunk)

    assert spot_check["id_matched"], f"Spot check ID mismatch for {sample_id}"
    assert spot_check["text_matched"], "Spot check text content mismatch"
    assert spot_check["metadata_matched"], "Spot check metadata mismatch"
    assert spot_check["vector_length_valid"], "Spot check vector length invalid"
    assert spot_check["vector_length"] > 0, "Vector length is 0"
    print(f"--> [PASS] Task 4 Spot-Check Integrity Verified for ID '{sample_id}' (Vector Length: {spot_check['vector_length']}).")

    # Task 5: Pipeline & Summary file check
    res = run_indexing_pipeline(data_dir)
    assert os.path.exists(res["summary_path"]), f"Summary file not created at {res['summary_path']}"
    print(f"--> [PASS] Task 5 Indexing summary written to '{res['summary_path']}'.")

    print("\n" + "=" * 75)
    print("  [ALL VERIFICATION TESTS PASSED SUCCESSFULLY]")
    print("=" * 75)

if __name__ == "__main__":
    test_indexing_tasks()
