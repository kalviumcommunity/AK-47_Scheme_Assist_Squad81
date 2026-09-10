import os
import sys

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.context_assembly import (
    format_chunk_with_source_marker,
    assemble_augmented_prompt,
    generate_sample_augmented_prompt,
    DEFAULT_GROUNDING_INSTRUCTIONS
)

def test_context_assembly_pipeline():
    print("=" * 75)
    print("  [TEST] Running Grounded Context Assembly & Augmented Prompting Tests")
    print("=" * 75)

    # Test 1: Chunk Formatting with Source Markers (Task 1 & Task 3)
    print("\n[TEST 1] format_chunk_with_source_marker...")
    sample_chunk = {
        "text": "Senior citizens aged 60+ receive free healthcare passes.",
        "metadata": {
            "source": "welfare_policy.pdf",
            "section": "Senior Assistance",
            "page": 3,
            "position": "Chunk 1 of 2"
        }
    }
    formatted = format_chunk_with_source_marker(sample_chunk, citation_idx=1)
    assert formatted["citation_index"] == 1, "Citation index mismatch"
    assert "[1]" in formatted["source_header"], "Source marker '[1]' missing"
    assert "welfare_policy.pdf" in formatted["source_header"], "Filename missing from header"
    print("--> [PASS] Task 1 & Task 3 Source Marker formatting verified.")

    # Test 2: Token Budget & Prompt Assembly (Task 1, Task 2 & Task 4)
    print("\n[TEST 2] assemble_augmented_prompt token budget & grounding...")
    chunks = [
        sample_chunk,
        {
            "text": "Income eligibility threshold is set at $45,000 annually.",
            "metadata": {"source": "welfare_policy.pdf", "section": "Income Limits", "page": 4}
        }
    ]
    query = "What is the income threshold for senior citizens?"
    
    result = assemble_augmented_prompt(
        retrieved_chunks=chunks,
        user_query=query,
        system_instructions=DEFAULT_GROUNDING_INSTRUCTIONS,
        max_total_tokens=4096,
        reserved_completion_tokens=500,
        max_context_tokens=1500
    )
    
    assert "[1]" in result["context_str"], "Context missing citation [1]"
    assert "[2]" in result["context_str"], "Context missing citation [2]"
    assert result["token_budget"]["total_prompt_tokens"] < 4096, "Total prompt exceeded limit"
    assert len(result["sources"]) == 2, "Sources metadata count mismatch"
    print("--> [PASS] Task 2 Token Budget & Task 4 Grounding prompt assembled.")

    # Test 3: Budget Truncation Enforcement (Task 2)
    print("\n[TEST 3] Enforce strict token budget truncation...")
    long_chunk = {
        "text": "Very long text block. " * 500,  # ~2500 tokens
        "metadata": {"source": "long_doc.md", "section": "Detailed Rules", "page": 10}
    }
    trunc_result = assemble_augmented_prompt(
        retrieved_chunks=[long_chunk],
        user_query=query,
        max_total_tokens=2000,
        reserved_completion_tokens=500,
        max_context_tokens=300
    )
    assert trunc_result["token_budget"]["used_context_tokens"] <= 300, "Context budget exceeded limit!"
    assert trunc_result["token_budget"]["chunks_truncated"] == 1, "Truncated chunk count mismatch"
    print(f"--> [PASS] Task 2 Budget truncation enforced ({trunc_result['token_budget']['used_context_tokens']} tokens <= 300).")

    # Test 4: Sample Prompt File Persistence (Task 5)
    print("\n[TEST 4] generate_sample_augmented_prompt...")
    filepath = generate_sample_augmented_prompt()
    assert os.path.exists(filepath), "Sample augmented prompt file was not written!"
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    assert "[1]" in content, "Sample prompt file missing [1]"
    assert "[2]" in content, "Sample prompt file missing [2]"
    assert "TOKEN BUDGET BREAKDOWN" in content, "Sample prompt file missing token budget breakdown"
    print(f"--> [PASS] Task 5 Sample augmented prompt written and verified at '{filepath}'.")

    print("\n" + "=" * 75)
    print("  [ALL CONTEXT ASSEMBLY & AUGMENTED PROMPT TESTS PASSED SUCCESSFULLY]")
    print("=" * 75)

if __name__ == "__main__":
    test_context_assembly_pipeline()
