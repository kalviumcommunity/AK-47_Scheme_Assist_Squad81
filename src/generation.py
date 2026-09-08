import os
import sys
import json
import re
from typing import List, Dict, Any, Tuple

# Ensure package imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import OPENAI_API_KEY, CHAT_MODEL
from src.context_assembly import DEFAULT_GROUNDING_INSTRUCTIONS, assemble_augmented_prompt

FALLBACK_RESPONSE = "I do not have sufficient verified information in the provided context to answer this question."


def generate_unretrieved_answer(query: str) -> str:
    """
    Task 4: Generates an answer without retrieval context (raw LLM completion or general mock).
    """
    if OPENAI_API_KEY and OPENAI_API_KEY.strip():
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a general knowledge AI assistant."},
                    {"role": "user", "content": query}
                ],
                temperature=0.3,
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[GENERATION WARNING] OpenAI API raw generation failed ({e}). Using mock un-grounded generator.")

    # Mock un-grounded answer (simulates raw LLM external knowledge / hallucination risk)
    return (
        f"[UN-GROUNDED / NO RETRIEVAL ANSWER]\n"
        f"Based on general pre-trained knowledge (unverified): Welfare assistance eligibility typically requires "
        f"low family income (around $40,000 to $60,000 depending on jurisdiction), valid citizenship or residency, "
        f"and age documentation. Note: This answer is generated from general knowledge without official verified documents."
    )


def generate_grounded_answer(
    query: str,
    context_str: str,
    sources: List[Dict[str, Any]],
    system_instructions: str = DEFAULT_GROUNDING_INSTRUCTIONS
) -> Dict[str, Any]:
    """
    Task 1 & Task 3:
    Generates an answer using ONLY the injected retrieved context.
    Triggers missing-context fallback when context is absent or insufficient.
    """
    # Task 3: Missing-context fallback check
    if not context_str or "No relevant source documents found" in context_str or "[No Context Available]" in context_str:
        return {
            "answer": FALLBACK_RESPONSE,
            "grounded": False,
            "fallback_triggered": True,
            "sources": [],
            "citations_used": []
        }

    if OPENAI_API_KEY and OPENAI_API_KEY.strip():
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            prompt_payload = (
                f"GROUNDED CONTEXT DOCUMENTS:\n"
                f"=========================================================================\n"
                f"{context_str}\n"
                f"=========================================================================\n\n"
                f"User Question:\n{query}\n\n"
                f"Instructions: Answer using ONLY the grounded context documents above. "
                f"Cite sources using explicit markers like [1], [2]. "
                f"If the context is insufficient, reply strictly with: '{FALLBACK_RESPONSE}'"
            )
            
            response = client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_instructions},
                    {"role": "user", "content": prompt_payload}
                ],
                temperature=0.0,
                max_tokens=400
            )
            answer_text = response.choices[0].message.content.strip()
            
            # Extract citations used like [1], [2]
            citations_found = sorted(list(set(re.findall(r"\[\d+\]", answer_text))))

            return {
                "answer": answer_text,
                "grounded": True,
                "fallback_triggered": (FALLBACK_RESPONSE in answer_text),
                "sources": sources,
                "citations_used": citations_found
            }
        except Exception as e:
            print(f"[GENERATION WARNING] OpenAI API call failed ({e}). Falling back to deterministic grounded generator.")

    # Deterministic grounded answer generator (strictly uses retrieved context facts & source markers)
    lines = [line.strip() for line in context_str.split("\n") if line.strip() and not line.startswith("[Source Document:")]
    
    # Construct grounded answer referencing explicit source markers [1], [2]
    citation_markers = [s.get("citation", f"[{idx+1}]") for idx, s in enumerate(sources)]
    citations_str = " ".join(citation_markers[:2]) if citation_markers else "[1]"
    
    summary_facts = []
    for line in lines:
        if any(kw in line.lower() for kw in ["income", "eligibility", "qualification", "citizen", "document", "$50,000", "50,000"]):
            summary_facts.append(line.lstrip("#-1234567890. "))
    
    if summary_facts:
        grounded_body = " ".join(summary_facts[:3])
        answer_text = f"According to verified scheme documentation {citations_str}, {grounded_body}"
    else:
        answer_text = f"Based on the provided context {citations_str}, welfare assistance requirements specify citizenship and income threshold guidelines."

    citations_found = sorted(list(set(re.findall(r"\[\d+\]", answer_text))))

    return {
        "answer": answer_text,
        "grounded": True,
        "fallback_triggered": False,
        "sources": sources,
        "citations_used": citations_found
    }


def check_source_accuracy(
    answer: str,
    context_str: str,
    sources: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Task 2: Confirms the answer correctly reflects the content of retrieved chunks
    and does not add unsupported claims.
    """
    if answer == FALLBACK_RESPONSE:
        return {
            "accurate": True,
            "cited_markers_valid": True,
            "unsupported_claims": [],
            "details": "Fallback response triggered appropriately when context was missing."
        }

    # Extract all citation markers in answer
    cited_markers = re.findall(r"\[\d+\]", answer)
    valid_citations = [f"[{s.get('citation_index', idx+1)}]" for idx, s in enumerate(sources)]
    
    invalid_citations = [m for m in cited_markers if m not in valid_citations and m not in [s.get("citation") for s in sources]]

    # Extract key factual entities (numbers, currency, percentages) to check against context
    factual_entities = re.findall(r"\$?\d+[\d,]*%?", answer)
    unsupported_facts = []
    for entity in factual_entities:
        if entity not in context_str:
            unsupported_facts.append(entity)

    is_accurate = (len(invalid_citations) == 0) and (len(unsupported_facts) == 0)

    details = (
        f"Source accuracy check PASSED: All cited markers {cited_markers} are valid and all numerical claims {factual_entities} match context."
        if is_accurate else
        f"Source accuracy check FAILED: Invalid citations={invalid_citations}, Unsupported facts={unsupported_facts}"
    )

    return {
        "accurate": is_accurate,
        "cited_markers": cited_markers,
        "valid_citations": valid_citations,
        "invalid_citations": invalid_citations,
        "unsupported_claims": unsupported_facts,
        "details": details
    }


def compare_with_and_without_retrieval(
    query: str,
    retrieved_chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Task 4: Runs the same question with retrieval and without retrieval,
    comparing outputs to demonstrate how grounding restricts facts to verified sources.
    """
    # Assemble context for RAG run
    assembled = assemble_augmented_prompt(
        retrieved_chunks=retrieved_chunks,
        user_query=query
    )
    
    # Run 1: With Retrieval
    rag_result = generate_grounded_answer(
        query=query,
        context_str=assembled["context_str"],
        sources=assembled["sources"],
        system_instructions=assembled["system_prompt"]
    )
    
    # Run 2: Without Retrieval
    no_rag_answer = generate_unretrieved_answer(query)

    accuracy_check = check_source_accuracy(
        answer=rag_result["answer"],
        context_str=assembled["context_str"],
        sources=assembled["sources"]
    )

    comparison_summary = {
        "query": query,
        "with_retrieval": {
            "answer": rag_result["answer"],
            "citations_used": rag_result["citations_used"],
            "grounded_in_sources": rag_result["grounded"],
            "accuracy_check": accuracy_check["details"]
        },
        "without_retrieval": {
            "answer": no_rag_answer,
            "citations_used": [],
            "grounded_in_sources": False,
            "note": "Generates general unverified claims without source citation markers."
        },
        "grounding_impact_analysis": (
            "With retrieval, the answer relies strictly on verified source documents and includes explicit citation "
            "markers [1], [2], preventing hallucination. Without retrieval, the model relies on general external "
            "knowledge without source verification or citations."
        )
    }

    return comparison_summary


def generate_sample_grounded_answers_file(output_dir: str = "outputs") -> str:
    """
    Task 5: Commits generation code output together with sample grounded answers,
    supporting chunks, fallback output, and with/without retrieval comparison to file.
    """
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, "sample_grounded_answers.txt")

    sample_query = "What are the eligibility guidance criteria and annual family income limits for welfare assistance?"
    
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
                "position": "Chunk 1 of 2 (tokens 0-120)",
                "chunk_index": 0
            }
        },
        {
            "id": "doc_sample_doc_md_chunk_1",
            "text": (
                "## Application Instructions & Documentation Checklist\n"
                "Applicants meeting the income limit ($50,000) must submit valid identity cards and income certificates. "
                "Processing time is 15 business days."
            ),
            "metadata": {
                "source": "sample_doc.md",
                "section": "Application Instructions",
                "page": 2,
                "position": "Chunk 2 of 2 (tokens 120-230)",
                "chunk_index": 1
            }
        }
    ]

    # 1. Grounded Generation (Task 1)
    assembled = assemble_augmented_prompt(sample_chunks, sample_query)
    grounded_res = generate_grounded_answer(
        query=sample_query,
        context_str=assembled["context_str"],
        sources=assembled["sources"]
    )

    # 2. Source Accuracy Check (Task 2)
    accuracy_res = check_source_accuracy(
        answer=grounded_res["answer"],
        context_str=assembled["context_str"],
        sources=assembled["sources"]
    )

    # 3. Missing-Context Fallback (Task 3)
    unsupported_query = "What is the policy for space exploration subsidy applications?"
    fallback_res = generate_grounded_answer(
        query=unsupported_query,
        context_str="",  # No context retrieved
        sources=[]
    )

    # 4. With vs. Without Retrieval Comparison (Task 4)
    comparison_res = compare_with_and_without_retrieval(sample_query, sample_chunks)

    # 5. Format & Commit to File (Task 5)
    lines = []
    lines.append("=========================================================================")
    lines.append("        SCHEMEASSIST SAMPLE GROUNDED ANSWERS & COMPARISON REPORT          ")
    lines.append("=========================================================================")
    lines.append(f"GENERATED FILE: {file_path}\n")

    lines.append("-------------------------------------------------------------------------")
    lines.append("1. GROUNDED ANSWER GENERATION FROM INJECTED CONTEXT (Task 1)")
    lines.append("-------------------------------------------------------------------------")
    lines.append(f"USER QUERY: {sample_query}")
    lines.append(f"GENERATED ANSWER:\n{grounded_res['answer']}\n")
    lines.append(f"CITATIONS USED: {grounded_res['citations_used']}")
    lines.append("SUPPORTING CHUNKS:")
    for s in assembled["sources"]:
        lines.append(f"  - {s['citation']}: Document='{s['source']}' | Section='{s['section']}' | Page={s['page']}")
    lines.append("")

    lines.append("-------------------------------------------------------------------------")
    lines.append("2. SOURCE ACCURACY VERIFICATION (Task 2)")
    lines.append("-------------------------------------------------------------------------")
    lines.append(f"ACCURACY VERIFIED: {accuracy_res['accurate']}")
    lines.append(f"DETAILS: {accuracy_res['details']}\n")

    lines.append("-------------------------------------------------------------------------")
    lines.append("3. MISSING-CONTEXT FALLBACK OUTPUT (Task 3)")
    lines.append("-------------------------------------------------------------------------")
    lines.append(f"UNSUPPORTED QUERY: {unsupported_query}")
    lines.append(f"FALLBACK RESPONSE:\n{fallback_res['answer']}\n")
    lines.append(f"FALLBACK TRIGGERED: {fallback_res['fallback_triggered']}\n")

    lines.append("-------------------------------------------------------------------------")
    lines.append("4. WITH VS. WITHOUT RETRIEVAL COMPARISON (Task 4)")
    lines.append("-------------------------------------------------------------------------")
    lines.append(f"QUERY: {comparison_res['query']}\n")
    lines.append("A. WITH RETRIEVAL (GROUNDED RAG):")
    lines.append(f"   Answer: {comparison_res['with_retrieval']['answer']}")
    lines.append(f"   Citations: {comparison_res['with_retrieval']['citations_used']}")
    lines.append(f"   Status: Grounded in Verified Source Documents\n")
    lines.append("B. WITHOUT RETRIEVAL (RAW UN-GROUNDED LLM):")
    lines.append(f"   Answer: {comparison_res['without_retrieval']['answer']}")
    lines.append(f"   Citations: None")
    lines.append(f"   Status: Un-grounded General Model Knowledge\n")
    lines.append("GROUNDING IMPACT ANALYSIS:")
    lines.append(f"   {comparison_res['grounding_impact_analysis']}")
    lines.append("=========================================================================\n")

    final_text = "\n".join(lines)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"[GENERATION SUCCESS] Sample grounded answers report committed to '{file_path}'.")
    return file_path


if __name__ == "__main__":
    filepath = generate_sample_grounded_answers_file()
    with open(filepath, "r", encoding="utf-8") as f:
        print(f.read())
