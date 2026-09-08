import os
import sys

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag_pipeline import (
    embed_query,
    retrieve_chunks,
    assemble_context,
    generate_answer,
    run_rag_pipeline
)

def test_rag_pipeline_stages():
    print("=" * 75)
    print("  [TEST] Running End-to-End RAG Pipeline Automated Stage Tests")
    print("=" * 75)

    test_query = "What are the eligibility criteria and income limits?"

    # Stage 1 Test: Embed Query
    print("\n[TEST STAGE 1] embed_query...")
    query_vector = embed_query(test_query)
    assert isinstance(query_vector, list), "query_vector must be a list"
    assert len(query_vector) == 1536, f"Expected 1536 vector length, got {len(query_vector)}"
    print(f"--> [PASS] Stage 1 Query Vector generated (dim: {len(query_vector)}).")

    # Stage 2 Test: Retrieve Chunks
    print("\n[TEST STAGE 2] retrieve_chunks...")
    retrieved = retrieve_chunks(test_query, top_k=2)
    assert isinstance(retrieved, list), "retrieved must be a list"
    assert len(retrieved) > 0, "No chunks retrieved!"
    assert "text" in retrieved[0], "Retrieved chunk missing 'text'"
    assert "metadata" in retrieved[0], "Retrieved chunk missing 'metadata'"
    print(f"--> [PASS] Stage 2 Retrieved {len(retrieved)} chunk(s). Top chunk source: '{retrieved[0]['metadata'].get('source')}'")

    # Stage 3 Test: Assemble Context
    print("\n[TEST STAGE 3] assemble_context...")
    context_str, sources_summary = assemble_context(retrieved)
    assert isinstance(context_str, str), "context_str must be a string"
    assert len(context_str) > 0, "context_str is empty"
    assert len(sources_summary) == len(retrieved), "sources_summary length mismatch"
    assert "source" in sources_summary[0], "Source summary missing 'source' key"
    print(f"--> [PASS] Stage 3 Context assembled ({len(context_str)} chars, {len(sources_summary)} sources).")

    # Stage 4 Test: Generate Answer
    print("\n[TEST STAGE 4] generate_answer...")
    gen_result = generate_answer(test_query, context_str)
    assert "answer" in gen_result, "Result missing 'answer'"
    assert len(gen_result["answer"]) > 0, "Answer text is empty"
    assert "model" in gen_result, "Result missing 'model'"
    print(f"--> [PASS] Stage 4 Answer generated (Model: {gen_result['model']}).")

    # End-to-End Test: run_rag_pipeline
    print("\n[TEST END-TO-END] run_rag_pipeline...")
    full_result = run_rag_pipeline(test_query, top_k=3)
    assert full_result["query"] == test_query, "Query mismatch"
    assert len(full_result["answer"]) > 0, "E2E Answer is empty"
    assert len(full_result["sources"]) > 0, "E2E Sources list is empty"
    assert os.path.exists(os.path.join("outputs", "rag_pipeline_summary.txt")), "Summary log missing"
    print("--> [PASS] End-to-End RAG Pipeline executed successfully and verified.")

    print("\n" + "=" * 75)
    print("  [ALL RAG PIPELINE TESTS PASSED SUCCESSFULLY]")
    print("=" * 75)

if __name__ == "__main__":
    test_rag_pipeline_stages()
