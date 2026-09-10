import os
import sys
import re
from typing import List, Dict, Any

# Ensure package imports resolve correctly
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

from google import genai

from src.config import GEMINI_API_KEY, CHAT_MODEL
from src.context_assembly import (
    DEFAULT_GROUNDING_INSTRUCTIONS,
    assemble_augmented_prompt
)


FALLBACK_RESPONSE = (
    "I do not have sufficient verified information in the "
    "provided context to answer this question."
)


# ============================================================
# GEMINI CLIENT
# ============================================================

def get_gemini_client():
    """
    Creates and returns Gemini API client.
    """

    if not GEMINI_API_KEY or not GEMINI_API_KEY.strip():
        raise ValueError(
            "GEMINI_API_KEY is not configured. "
            "Please add it to your .env file."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# ============================================================
# GENERATE ANSWER WITHOUT RETRIEVAL
# ============================================================

def generate_unretrieved_answer(query: str) -> str:
    """
    Generates an answer using Gemini without RAG retrieval.
    This is only used for retrieval comparison/testing.
    """

    try:

        client = get_gemini_client()

        prompt = f"""
You are a general knowledge AI assistant.

Answer the following question using your general knowledge.

Question:
{query}
"""

        response = client.models.generate_content(
            model=CHAT_MODEL,
            contents=prompt
        )

        if response.text:
            return response.text.strip()

        return "Gemini did not return a response."

    except Exception as e:

        print(
            f"[GENERATION ERROR] "
            f"Gemini raw generation failed: {e}"
        )

        return (
            "Unable to generate an answer because the "
            "Gemini API request failed."
        )


# ============================================================
# GROUNDED RAG ANSWER GENERATION
# ============================================================

def generate_grounded_answer(
    query: str,
    context_str: str,
    sources: List[Dict[str, Any]],
    system_instructions: str = DEFAULT_GROUNDING_INSTRUCTIONS
) -> Dict[str, Any]:
    """
    Generates an answer using Gemini.

    IMPORTANT:
    Gemini must answer ONLY using the retrieved RAG context.
    """

    # --------------------------------------------------------
    # Missing Context Check
    # --------------------------------------------------------

    if (
        not context_str
        or "No relevant source documents found" in context_str
        or "[No Context Available]" in context_str
    ):

        return {
            "answer": FALLBACK_RESPONSE,
            "grounded": False,
            "fallback_triggered": True,
            "sources": [],
            "citations_used": []
        }


    try:

        client = get_gemini_client()


        # ----------------------------------------------------
        # COMPLETE RAG PROMPT
        # ----------------------------------------------------

        prompt_payload = f"""
SYSTEM INSTRUCTIONS:

{system_instructions}


============================================================
RETRIEVED VERIFIED CONTEXT
============================================================

{context_str}


============================================================
USER QUESTION
============================================================

{query}


============================================================
IMPORTANT RULES
============================================================

1. Answer ONLY using the retrieved context above.

2. Do NOT use outside knowledge.

3. Do NOT invent scheme names, eligibility criteria,
   income limits, benefits, documents, or application steps.

4. Use source citation markers when available.

5. Cite information using markers such as:
   [1]
   [2]
   [3]

6. If the retrieved context does not contain enough
   information to answer the question, respond EXACTLY:

{FALLBACK_RESPONSE}

7. Keep the answer clear and useful.

8. Never mention that you are an AI model.

Now answer the user's question.
"""


        # ----------------------------------------------------
        # GEMINI API CALL
        # ----------------------------------------------------

        response = client.models.generate_content(
            model=CHAT_MODEL,
            contents=prompt_payload
        )


        # ----------------------------------------------------
        # VALIDATE RESPONSE
        # ----------------------------------------------------

        answer_text = ""

        if response and response.text:
            answer_text = response.text.strip()


        if not answer_text:

            return {
                "answer": FALLBACK_RESPONSE,
                "grounded": False,
                "fallback_triggered": True,
                "sources": sources,
                "citations_used": []
            }


        # ----------------------------------------------------
        # EXTRACT CITATIONS
        # ----------------------------------------------------

        citations_found = sorted(
            list(
                set(
                    re.findall(
                        r"\[\d+\]",
                        answer_text
                    )
                )
            )
        )


        # ----------------------------------------------------
        # CHECK FALLBACK
        # ----------------------------------------------------

        fallback_triggered = (
            answer_text.strip() == FALLBACK_RESPONSE
        )


        return {
            "answer": answer_text,
            "grounded": not fallback_triggered,
            "fallback_triggered": fallback_triggered,
            "sources": sources,
            "citations_used": citations_found
        }


    except Exception as e:

        print(
            f"[GENERATION ERROR] "
            f"Gemini API call failed: {e}"
        )

        return {
            "answer": FALLBACK_RESPONSE,
            "grounded": False,
            "fallback_triggered": True,
            "sources": sources,
            "citations_used": []
        }


# ============================================================
# SOURCE ACCURACY CHECK
# ============================================================

def check_source_accuracy(
    answer: str,
    context_str: str,
    sources: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Checks whether answer citations and numerical claims
    are supported by the retrieved context.
    """

    if answer == FALLBACK_RESPONSE:

        return {
            "accurate": True,
            "cited_markers_valid": True,
            "unsupported_claims": [],
            "details": (
                "Fallback response triggered correctly "
                "because sufficient context was unavailable."
            )
        }


    # --------------------------------------------------------
    # Extract citations
    # --------------------------------------------------------

    cited_markers = re.findall(
        r"\[\d+\]",
        answer
    )


    valid_citations = []

    for index, source in enumerate(sources):

        citation_index = source.get(
            "citation_index",
            index + 1
        )

        valid_citations.append(
            f"[{citation_index}]"
        )


    # --------------------------------------------------------
    # Find invalid citations
    # --------------------------------------------------------

    invalid_citations = [

        marker

        for marker in cited_markers

        if marker not in valid_citations

    ]


    # --------------------------------------------------------
    # Check numerical facts
    # --------------------------------------------------------

    factual_entities = re.findall(
        r"\$?\d+[\d,]*%?",
        answer
    )


    unsupported_facts = []


    for entity in factual_entities:

        if entity not in context_str:

            unsupported_facts.append(
                entity
            )


    # --------------------------------------------------------
    # Final accuracy result
    # --------------------------------------------------------

    is_accurate = (

        len(invalid_citations) == 0

        and

        len(unsupported_facts) == 0

    )


    if is_accurate:

        details = (
            "Source accuracy check PASSED. "
            "All citations are valid and numerical claims "
            "are supported by the retrieved context."
        )

    else:

        details = (
            f"Source accuracy check FAILED. "
            f"Invalid citations: {invalid_citations}. "
            f"Unsupported facts: {unsupported_facts}"
        )


    return {

        "accurate": is_accurate,

        "cited_markers": cited_markers,

        "valid_citations": valid_citations,

        "invalid_citations": invalid_citations,

        "unsupported_claims": unsupported_facts,

        "details": details

    }


# ============================================================
# COMPARE RAG VS NO RAG
# ============================================================

def compare_with_and_without_retrieval(
    query: str,
    retrieved_chunks: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Compares Gemini response with RAG retrieval
    versus Gemini response without retrieval.
    """

    assembled = assemble_augmented_prompt(

        retrieved_chunks=retrieved_chunks,

        user_query=query

    )


    # --------------------------------------------------------
    # WITH RAG
    # --------------------------------------------------------

    rag_result = generate_grounded_answer(

        query=query,

        context_str=assembled["context_str"],

        sources=assembled["sources"],

        system_instructions=assembled["system_prompt"]

    )


    # --------------------------------------------------------
    # WITHOUT RAG
    # --------------------------------------------------------

    no_rag_answer = generate_unretrieved_answer(
        query
    )


    # --------------------------------------------------------
    # ACCURACY CHECK
    # --------------------------------------------------------

    accuracy_check = check_source_accuracy(

        answer=rag_result["answer"],

        context_str=assembled["context_str"],

        sources=assembled["sources"]

    )


    return {

        "query": query,


        "with_retrieval": {

            "answer": rag_result["answer"],

            "citations_used":
                rag_result["citations_used"],

            "grounded_in_sources":
                rag_result["grounded"],

            "accuracy_check":
                accuracy_check["details"]

        },


        "without_retrieval": {

            "answer": no_rag_answer,

            "citations_used": [],

            "grounded_in_sources": False,

            "note": (
                "Answer generated using Gemini general "
                "knowledge without retrieved source documents."
            )

        },


        "grounding_impact_analysis": (

            "With RAG retrieval, Gemini receives verified "
            "scheme documents and is instructed to answer "
            "only from those documents. Without retrieval, "
            "Gemini answers using general model knowledge."

        )

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "SCHEMEASSIST GEMINI GENERATION TEST"
    )

    print("=" * 60)


    test_query = (
        "What are the eligibility criteria "
        "for government welfare schemes?"
    )


    test_context = """
[1]

Source: sample_scheme.md

Eligibility:

Applicants must be citizens.

Annual family income must not exceed 500000 INR.

Applicants must provide identity documents.
"""


    result = generate_grounded_answer(

        query=test_query,

        context_str=test_context,

        sources=[

            {

                "citation_index": 1,

                "source": "sample_scheme.md"

            }

        ]

    )


    print("\nANSWER:\n")

    print(
        result["answer"]
    )


    print("\nCITATIONS:")

    print(
        result["citations_used"]
    )