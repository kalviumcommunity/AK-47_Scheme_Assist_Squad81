import os
import sys
import json

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chunking import (
    compare_all_strategies,
    format_comparison_table,
    fixed_size_chunks,
    fixed_size_overlap_chunks,
    paragraph_chunks,
    sentence_chunks,
    recursive_character_chunks,
)


# Ensure clean UTF-8 standard output if available
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_chunking_experiment():
    print("=" * 90)
    print("  [SchemeAssist RAG] Document Chunking Strategies & Boundary Benchmark Suite (3.21)")
    print("=" * 90)

    # 1. Load sample corpus document
    sample_doc_path = os.path.join("data", "sample_doc.md")
    if not os.path.exists(sample_doc_path):
        print(f"[ERROR] Sample document '{sample_doc_path}' not found!")
        return

    with open(sample_doc_path, "r", encoding="utf-8") as f:
        document_text = f.read()

    doc_chars = len(document_text)
    doc_words = len(document_text.split())
    print(f"[CORPUS LOADED] File: 'sample_doc.md' | Length: {doc_chars} chars | {doc_words} words\n")

    # 2. Run All Strategies Comparison
    results = compare_all_strategies(document_text, source_doc="sample_doc.md")

    # 3. Print Statistical Comparison Table
    table_str = format_comparison_table(results)
    print(table_str)

    # 4. Detailed Strategy Breakdown & Boundary Analysis
    boundary_notes = []
    boundary_notes.append("\n" + "=" * 90)
    boundary_notes.append("  [ANALYSIS] IN-DEPTH CHUNKING STRATEGY COMPARISON & BOUNDARY ANALYSIS")
    boundary_notes.append("=" * 90)

    for name, stats in results.items():
        boundary_notes.append(f"\n>> Strategy: {name}")
        boundary_notes.append(f"  * Total Chunks Generated: {stats.chunk_count}")
        boundary_notes.append(f"  * Average Chunk Size:     {stats.avg_char_size:.1f} chars ({stats.avg_word_size:.1f} words, ~{stats.avg_token_size:.1f} tokens)")
        boundary_notes.append(f"  * Chunk Size Range:       [{stats.min_char_size} - {stats.max_char_size}] chars")
        boundary_notes.append(f"  * Mid-Sentence Cut Rate:  {stats.mid_sentence_cuts}/{stats.chunk_count} chunks ({stats.mid_sentence_cuts/stats.chunk_count*100:.1f}%)")
        
        # Sample chunk preview
        if stats.chunks:
            first_chunk = stats.chunks[0]
            boundary_notes.append(f"  * Sample Chunk 1 Boundary Preview (First 160 chars):")
            boundary_notes.append(f"    \"{first_chunk.text[:160].replace(chr(10), ' ')}...\"")
            last_chunk = stats.chunks[-1]
            boundary_notes.append(f"  * Sample Chunk End Boundary Preview (Last 120 chars):")
            boundary_notes.append(f"    \"...{last_chunk.text[-120:].replace(chr(10), ' ')}\"")

    boundary_text = "\n".join(boundary_notes)
    print(boundary_text)

    # 5. Highlight Boundary Cut Vulnerabilities (Fixed vs Recursive / Paragraph)
    boundary_comparison_snippet = []
    boundary_comparison_snippet.append("\n" + "=" * 90)
    boundary_comparison_snippet.append("  [EVALUATION] BOUNDARY INTEGRITY COMPARISON (Fixed Naive vs Recursive Semantic)")
    boundary_comparison_snippet.append("=" * 90)

    fixed_naive = results["Fixed-Size (Naive 500 chars, no overlap)"].chunks
    recursive = results["Recursive Character (500 chars, 80 char overlap)"].chunks

    boundary_comparison_snippet.append("\n[CASE 1: Fixed-Size Naive Chunk Boundary]")
    if len(fixed_naive) >= 2:
        boundary_comparison_snippet.append(f"Chunk 1 Tail: \"{fixed_naive[0].text[-80:].replace(chr(10), ' ')}\"")
        boundary_comparison_snippet.append(f"Chunk 2 Head: \"{fixed_naive[1].text[:80].replace(chr(10), ' ')}\"")
        boundary_comparison_snippet.append("[!] NOTE: Fixed-size naive splits abruptly across word/clause boundaries without respecting list items.")

    boundary_comparison_snippet.append("\n[CASE 2: Recursive Character Chunk Boundary]")
    if len(recursive) >= 2:
        boundary_comparison_snippet.append(f"Chunk 1 Tail: \"{recursive[0].text[-80:].replace(chr(10), ' ')}\"")
        boundary_comparison_snippet.append(f"Chunk 2 Head: \"{recursive[1].text[:80].replace(chr(10), ' ')}\"")
        boundary_comparison_snippet.append("[+] NOTE: Recursive splitting prioritizes paragraph & sentence boundaries, preventing fractured eligibility criteria.")

    boundary_comp_str = "\n".join(boundary_comparison_snippet)
    print(boundary_comp_str)

    # 6. Strategic Justification for Welfare Schemes Corpus
    justification = """
==========================================================================================
  [JUSTIFICATION] WHY RECURSIVE / PARAGRAPH-AWARE CHUNKING FITS SCHEMEASSIST
==========================================================================================
1. Structure of Government Welfare Policies:
   Government policy documents (circulars, notifications, guidelines) are inherently 
   hierarchical: Titles -> Sections -> Eligibility Clauses -> Tables/Lists -> SLAs.
   - Naive fixed chunking slices across bullet points, separating qualification conditions 
     from exclusions (e.g., separating landholding limit from income tax disqualifications).
   - Paragraph chunking preserves cohesive policy clauses within atomic units.

2. Retrieval Precision vs. Context Window Trade-off:
   - Chunk Size: ~500 characters (~110-130 tokens) with 80 character overlap.
   - For Top-K = 3 retrieval, 3 chunks consume ~390 tokens.
   - This leaves >95% of standard LLM context windows (e.g., 8k-128k) available for system 
     instructions, conversation history, and multi-step reasoning without context exhaustion.

3. Answer Quality & Zero Mid-Sentence Hallucination:
   - Preserving full sentences and paragraph context ensures the LLM receives complete, 
     unambiguous factual premises, preventing truncation-induced hallucinations.
==========================================================================================
"""
    print(justification)

    # 7. Persist Outputs
    os.makedirs("outputs", exist_ok=True)

    # Save human-readable results report
    report_file = os.path.join("outputs", "chunking_comparison_results.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("SCHEMEASSIST RAG - DOCUMENT CHUNKING STRATEGIES COMPARISON REPORT\n")
        f.write(f"Source Document: sample_doc.md ({doc_chars} chars, {doc_words} words)\n\n")
        f.write(table_str + "\n\n")
        f.write(boundary_text + "\n\n")
        f.write(boundary_comp_str + "\n\n")
        f.write(justification + "\n")
    print(f"\n[OUTPUT SAVED] Comparison Report -> '{report_file}'")

    # Save visual sample chunks for human inspection
    sample_chunks_txt = os.path.join("outputs", "sample_chunks.txt")
    with open(sample_chunks_txt, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  SAMPLE CHUNKS VISUAL BOUNDARY INSPECTION (ALL STRATEGIES)\n")
        f.write("=" * 80 + "\n\n")
        for name, stats in results.items():
            f.write(f"\n################################################################################\n")
            f.write(f"### STRATEGY: {name}\n")
            f.write(f"### Total Chunks: {stats.chunk_count} | Avg Size: {stats.avg_char_size:.1f} chars\n")
            f.write(f"################################################################################\n\n")
            for c in stats.chunks:
                f.write(f"--- [CHUNK: {c.chunk_id}] (Chars: {c.char_count}, Tokens: {c.token_count_estimate}, Offset: {c.start_char}-{c.end_char}) ---\n")
                f.write(f"{c.text}\n")
                f.write("-" * 80 + "\n\n")
    print(f"[OUTPUT SAVED] Sample Chunks Text -> '{sample_chunks_txt}'")

    # Save machine-readable JSON representation
    sample_chunks_json = os.path.join("outputs", "sample_chunks.json")
    json_payload = {
        "source_document": "sample_doc.md",
        "document_stats": {"total_characters": doc_chars, "total_words": doc_words},
        "strategies_summary": {k: v.to_dict() for k, v in results.items()},
        "strategy_chunks": {
            k: [c.to_dict() for c in v.chunks] for k, v in results.items()
        }
    }
    with open(sample_chunks_json, "w", encoding="utf-8") as f:
        json.dump(json_payload, f, indent=2)
    print(f"[OUTPUT SAVED] Machine-Readable JSON -> '{sample_chunks_json}'")

    print("\n" + "=" * 90)
    print("  [SUCCESS] DOCUMENT CHUNKING BENCHMARK SUITE COMPLETED SUCCESSFULLY!")
    print("=" * 90)


if __name__ == "__main__":
    run_chunking_experiment()
