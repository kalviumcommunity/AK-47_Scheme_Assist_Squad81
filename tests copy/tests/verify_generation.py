import os
import sys

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.generation import (
    generate_grounded_answer,
    check_source_accuracy,
    compare_with_and_without_retrieval,
    generate_sample_grounded_answers_file,
    FALLBACK_RESPONSE
)

def test_generation_pipeline():
    print("=" * 75)
    print("  [TEST] Running Grounded Answer Generation & Comparison Tests")
    print("=" * 75)

    sample_chunks = [
        {
            "id": "doc_1_chunk_0",
            "text": "Eligibility guidelines specify an annual income limit of $50,000 for welfare grants.",
            "metadata": {"source": "guidelines.pdf", "section": "Income Limits", "page": 1, "chunk_index": 0}
        }
    ]
    sources = [{"citation_index": 1, "citation": "[1]", "source": "guidelines.pdf", "section": "Income Limits", "page": 1}]
    context_str = "[1] [Source Document: 'guidelines.pdf' | Section: 'Income Limits' | Page: 1]\n" + sample_chunks[0]["text"]

    # Test 1: Grounded Answer Generation from Injected Context (Task 1)
    print("\n[TEST 1] generate_grounded_answer...")
    query = "What is the annual income limit for welfare grants?"
    result = generate_grounded_answer(query, context_str, sources)
    assert result["grounded"] is True, "Answer should be marked grounded"
    assert result["fallback_triggered"] is False, "Fallback should not trigger when context is present"
    assert len(result["citations_used"]) > 0, "Citations should be present in grounded answer"
    print(f"--> [PASS] Task 1 Grounded Answer generated: '{result['answer'][:80]}...'")

    # Test 2: Source Accuracy Checking (Task 2)
    print("\n[TEST 2] check_source_accuracy...")
    accuracy = check_source_accuracy(result["answer"], context_str, sources)
    assert accuracy["accurate"] is True, "Accurate answer failed source accuracy check"
    
    # Test inaccurate claim
    inaccurate_accuracy = check_source_accuracy("The limit is $999,999 according to [99]", context_str, sources)
    assert inaccurate_accuracy["accurate"] is False, "Inaccurate answer was incorrectly marked accurate"
    print("--> [PASS] Task 2 Source Accuracy verification passed.")

    # Test 3: Missing-Context Fallback (Task 3)
    print("\n[TEST 3] Missing-context fallback mechanism...")
    unsupported_query = "How do I apply for space travel permits?"
    fallback_res = generate_grounded_answer(unsupported_query, context_str="", sources=[])
    assert fallback_res["fallback_triggered"] is True, "Fallback flag must be True"
    assert fallback_res["answer"] == FALLBACK_RESPONSE, "Fallback response string mismatch"
    print(f"--> [PASS] Task 3 Missing-context fallback triggered: '{fallback_res['answer']}'")

    # Test 4: Compare With vs. Without Retrieval (Task 4)
    print("\n[TEST 4] compare_with_and_without_retrieval...")
    comparison = compare_with_and_without_retrieval(query, sample_chunks)
    assert "with_retrieval" in comparison, "Missing 'with_retrieval' in comparison"
    assert "without_retrieval" in comparison, "Missing 'without_retrieval' in comparison"
    assert comparison["with_retrieval"]["grounded_in_sources"] is True, "RAG answer should be grounded"
    assert comparison["without_retrieval"]["grounded_in_sources"] is False, "Un-retrieved answer should not be grounded"
    print("--> [PASS] Task 4 Comparative analysis generated successfully.")

    # Test 5: Commit Sample Grounded Answers File (Task 5)
    print("\n[TEST 5] generate_sample_grounded_answers_file...")
    filepath = generate_sample_grounded_answers_file()
    assert os.path.exists(filepath), "Sample grounded answers file was not generated"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    assert FALLBACK_RESPONSE in content, "Fallback response missing from output file"
    assert "WITH VS. WITHOUT RETRIEVAL COMPARISON" in content, "Comparison missing from output file"
    print(f"--> [PASS] Task 5 Sample output committed and verified at '{filepath}'.")

    print("\n" + "=" * 75)
    print("  [ALL GROUNDED ANSWER GENERATION TESTS PASSED SUCCESSFULLY]")
    print("=" * 75)

if __name__ == "__main__":
    test_generation_pipeline()
