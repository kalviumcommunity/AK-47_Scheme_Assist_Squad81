import os
import sys
import json
from typing import List, Dict, Any, Tuple

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.token_counter import count_tokens, get_tokenizer

# Grounding System Prompt Instructions
DEFAULT_GROUNDING_INSTRUCTIONS = (
    "You are a grounded RAG AI assistant for SchemeAssist.\n"
    "CRITICAL GROUNDING RULES:\n"
    "1. Rely STRICTLY on the provided Grounded Context documents below to answer the user query.\n"
    "2. Cite your sources using the explicit source markers provided in the context (e.g. [1], [2]).\n"
    "3. Do NOT assume, extrapolate, or use pre-trained external knowledge not supported by the context.\n"
    "4. If the provided context does not contain sufficient information to answer the question accurately, "
    "reply strictly with: 'I do not have sufficient verified information in the provided context to answer this question.'"
)


def format_chunk_with_source_marker(chunk: Dict[str, Any], citation_idx: int) -> Dict[str, Any]:
    """
    Task 1 & Task 3: Formats a retrieved chunk with explicit citation source markers [1], [2]
    and source metadata header (Filename, Section, Page, Position).
    """
    meta = chunk.get("metadata", {})
    source_doc = meta.get("source", meta.get("source_doc", "Unknown Document"))
    section = meta.get("section", "General Overview")
    page = meta.get("page", 1)
    position = meta.get("position", f"Chunk {citation_idx}")
    text = chunk.get("text", chunk.get("content", "")).strip()

    source_header = f"[{citation_idx}] [Source Document: '{source_doc}' | Section: '{section}' | Page: {page} | {position}]"
    formatted_block = f"{source_header}\n{text}\n"

    token_count = count_tokens(formatted_block)

    return {
        "citation_index": citation_idx,
        "source_header": source_header,
        "formatted_block": formatted_block,
        "text": text,
        "token_count": token_count,
        "metadata": {
            "citation": f"[{citation_idx}]",
            "source": source_doc,
            "section": section,
            "page": page,
            "position": position,
            "chunk_id": chunk.get("id", chunk.get("chunk_id", f"chunk_{citation_idx}"))
        }
    }


def assemble_augmented_prompt(
    retrieved_chunks: List[Dict[str, Any]],
    user_query: str,
    system_instructions: str = DEFAULT_GROUNDING_INSTRUCTIONS,
    max_total_tokens: int = 4096,
    reserved_completion_tokens: int = 500,
    max_context_tokens: int = 1500
) -> Dict[str, Any]:
    """
    Task 1, Task 2, Task 3 & Task 4:
    Assembles retrieved chunks into a grounded augmented prompt.
    Enforces token budget limits across system instructions, user query, context, and completion.
    """
    query_text = f"User Question:\n{user_query.strip()}\n"
    query_tokens = count_tokens(query_text)
    system_tokens = count_tokens(system_instructions)

    # Token budget calculation
    available_for_context = min(
        max_context_tokens,
        max_total_tokens - reserved_completion_tokens - system_tokens - query_tokens
    )
    if available_for_context <= 0:
        raise ValueError(f"Token budget exceeded before adding context! (System: {system_tokens}, Query: {query_tokens})")

    formatted_context_blocks = []
    sources_metadata = []
    used_context_tokens = 0
    truncated_chunks_count = 0

    for idx, raw_chunk in enumerate(retrieved_chunks, start=1):
        formatted_chunk = format_chunk_with_source_marker(raw_chunk, idx)
        chunk_tokens = formatted_chunk["token_count"]

        # Check if adding this chunk exceeds available context token budget
        if used_context_tokens + chunk_tokens <= available_for_context:
            formatted_context_blocks.append(formatted_chunk["formatted_block"])
            sources_metadata.append(formatted_chunk["metadata"])
            used_context_tokens += chunk_tokens
        else:
            # Attempt character/token level truncation for partial fit if space remains
            remaining_budget = available_for_context - used_context_tokens
            header = formatted_chunk["source_header"]
            header_tokens = count_tokens(header + "\n\n")
            text_budget = remaining_budget - header_tokens
            
            if text_budget > 20:  # Only truncate if meaningful text budget remains
                text = formatted_chunk["text"]
                approx_chars = text_budget * 3  # Conservative ratio to prevent overshooting
                truncated_text = text[:approx_chars] + " ... [Truncated to fit token budget]"
                
                truncated_block = f"{header}\n{truncated_text}\n"
                trunc_tokens = count_tokens(truncated_block)
                
                # Double check fit
                if used_context_tokens + trunc_tokens <= available_for_context:
                    formatted_context_blocks.append(truncated_block)
                    sources_metadata.append(formatted_chunk["metadata"])
                    used_context_tokens += trunc_tokens
                    truncated_chunks_count += 1
                    print(f"[TOKEN BUDGET LOG] Truncated chunk [{idx}] ({chunk_tokens} -> {trunc_tokens} tokens) to fit budget.")
            else:
                print(f"[TOKEN BUDGET LOG] Token budget ({available_for_context}) reached. Skipping remaining chunks ({len(retrieved_chunks) - idx + 1}).")
            break

    context_str = "\n".join(formatted_context_blocks) if formatted_context_blocks else "[No Context Available]"
    
    augmented_user_prompt = (
        f"GROUNDED CONTEXT DOCUMENTS:\n"
        f"=========================================================================\n"
        f"{context_str}\n"
        f"=========================================================================\n\n"
        f"{query_text}\n"
        f"Instructions: Answer the question using ONLY the grounded context documents above. "
        f"Include explicit source markers (e.g. [1], [2]) for all facts."
    )

    total_prompt_tokens = system_tokens + count_tokens(augmented_user_prompt)

    token_budget_report = {
        "max_total_tokens": max_total_tokens,
        "reserved_completion_tokens": reserved_completion_tokens,
        "system_instruction_tokens": system_tokens,
        "user_query_tokens": query_tokens,
        "available_context_budget": available_for_context,
        "used_context_tokens": used_context_tokens,
        "total_prompt_tokens": total_prompt_tokens,
        "remaining_safety_margin": max_total_tokens - reserved_completion_tokens - total_prompt_tokens,
        "chunks_included": len(sources_metadata),
        "chunks_truncated": truncated_chunks_count,
        "chunks_total_retrieved": len(retrieved_chunks)
    }

    return {
        "system_prompt": system_instructions,
        "user_prompt": augmented_user_prompt,
        "context_str": context_str,
        "sources": sources_metadata,
        "token_budget": token_budget_report
    }


def generate_sample_augmented_prompt(output_dir: str = "outputs") -> str:
    """
    Task 5: Generates a sample augmented prompt showing injected chunks,
    source markers [1], [2], and token-budget breakdown output, then commits it to output file.
    """
    sample_query = "What are the eligibility guidance criteria and annual family income limits for welfare assistance?"
    
    # Sample retrieved chunks simulating vector DB search output
    sample_chunks = [
        {
            "id": "doc_sample_doc_md_chunk_0",
            "text": (
                "## Eligibility Guidance & Criteria\n"
                "To qualify for government welfare assistance under the National Healthcare and Pension Support Scheme, "
                "applicants must satisfy the following baseline qualifications:\n"
                "1. Citizenship: Must be a legal citizen or permanent resident aged 18 years or older.\n"
                "2. Annual Family Income Limit: The applicant's total annual family income must not exceed $50,000.\n"
                "3. Age Qualification for Senior Schemes: Applicants aged 60 and above receive priority processing."
            ),
            "metadata": {
                "source": "sample_doc.md",
                "section": "Eligibility Guidance & Criteria",
                "page": 1,
                "position": "Chunk 1 of 3 (tokens 0-120)",
                "chunk_index": 0
            }
        },
        {
            "id": "doc_sample_doc_md_chunk_1",
            "text": (
                "## Application Instructions & Documentation Checklist\n"
                "Applicants meeting the income limit ($50,000) must submit the following documents at the local office:\n"
                "- Valid Identity Card / Birth Certificate\n"
                "- Certified Income Certificate issued by authorized tax authority\n"
                "- Residency Verification Certificate\n"
                "Processing time is typically 15 business days following verification."
            ),
            "metadata": {
                "source": "sample_doc.md",
                "section": "Application Instructions",
                "page": 2,
                "position": "Chunk 2 of 3 (tokens 120-230)",
                "chunk_index": 1
            }
        }
    ]

    assembled = assemble_augmented_prompt(
        retrieved_chunks=sample_chunks,
        user_query=sample_query,
        system_instructions=DEFAULT_GROUNDING_INSTRUCTIONS,
        max_total_tokens=4096,
        reserved_completion_tokens=500,
        max_context_tokens=1500
    )

    os.makedirs(output_dir, exist_ok=True)
    sample_file_path = os.path.join(output_dir, "sample_augmented_prompt.txt")

    output_lines = []
    output_lines.append("=========================================================================")
    output_lines.append("        SCHEMEASSIST SAMPLE GROUNDED AUGMENTED PROMPT OUTPUT             ")
    output_lines.append("=========================================================================")
    output_lines.append(f"GENERATED FILE: {sample_file_path}\n")
    
    output_lines.append("-------------------------------------------------------------------------")
    output_lines.append("1. GROUNDING SYSTEM INSTRUCTIONS (Task 4)")
    output_lines.append("-------------------------------------------------------------------------")
    output_lines.append(assembled["system_prompt"] + "\n")

    output_lines.append("-------------------------------------------------------------------------")
    output_lines.append("2. INJECTED CONTEXT & SOURCE MARKERS [1], [2] (Task 1 & Task 3)")
    output_lines.append("-------------------------------------------------------------------------")
    output_lines.append(assembled["context_str"] + "\n")

    output_lines.append("-------------------------------------------------------------------------")
    output_lines.append("3. FULL AUGMENTED USER PROMPT PAYLOAD (Task 1 & Task 4)")
    output_lines.append("-------------------------------------------------------------------------")
    output_lines.append(assembled["user_prompt"] + "\n")

    output_lines.append("-------------------------------------------------------------------------")
    output_lines.append("4. TOKEN BUDGET BREAKDOWN REPORT (Task 2)")
    output_lines.append("-------------------------------------------------------------------------")
    output_lines.append(json.dumps(assembled["token_budget"], indent=2) + "\n")

    output_lines.append("-------------------------------------------------------------------------")
    output_lines.append("5. CITATION SOURCES SUMMARY (Task 3)")
    output_lines.append("-------------------------------------------------------------------------")
    for s in assembled["sources"]:
        output_lines.append(f"Citation {s['citation']}: {s['source']} | Section: '{s['section']}' | Page: {s['page']}")
    output_lines.append("=========================================================================\n")

    final_content = "\n".join(output_lines)

    with open(sample_file_path, "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"[CONTEXT ASSEMBLY SUCCESS] Sample augmented prompt committed to '{sample_file_path}'.")
    return sample_file_path


if __name__ == "__main__":
    filepath = generate_sample_augmented_prompt()
    with open(filepath, "r", encoding="utf-8") as f:
        print(f.read())
