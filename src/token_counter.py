import os
import sys
import tiktoken

# Ensure imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Standard Pricing Rates for gpt-4o-mini (per 1,000,000 tokens)
INPUT_RATE_PER_1M = 0.15
OUTPUT_RATE_PER_1M = 0.60

def get_tokenizer(model_name: str = "gpt-4o-mini"):
    """
    Retrieves the appropriate tiktoken encoding.
    Falls back to cl100k_base if the specific model encoding is not available.
    """
    try:
        return tiktoken.encoding_for_model(model_name)
    except Exception:
        print(f"[TOKENIZER WARNING] Direct encoding for '{model_name}' not found. Falling back to 'cl100k_base'.")
        return tiktoken.get_encoding("cl100k_base")

def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Calculates cost based on input and output token counts and standard rates.
    """
    input_cost = (input_tokens / 1_000_000) * INPUT_RATE_PER_1M
    output_cost = (output_tokens / 1_000_000) * OUTPUT_RATE_PER_1M
    return input_cost + output_cost

def load_sample_document(filepath: str = "data/sample_doc.md") -> str:
    """
    Loads contents of the sample document dynamically.
    """
    # Try local path or relative to project root
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read().strip()
    
    # Fallback path logic
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fallback_path = os.path.join(root_dir, filepath)
    if os.path.exists(fallback_path):
        with open(fallback_path, "r", encoding="utf-8") as f:
            return f.read().strip()
            
    # Mock text if file is missing
    return (
        "# Knowledge Base Document: Government Welfare Schemes Overview\n\n"
        "## Overview\nThis knowledge base contains official notifications, circulars, and guidelines "
        "regarding government welfare assistance programs across departments.\n\n"
        "## Primary Objectives\n- Discoverability: Enable citizens and helpdesk executives to search and identify.\n"
        "- Eligibility Guidance: Explain specific age, income, occupation, category, and demographic qualifications.\n"
        "- Application Enablement: Provide clear documentation checklists, step-by-step application instructions."
    )

def main():
    # Setup output catching for reporting
    output_lines = []
    def log(msg: str = ""):
        print(msg)
        output_lines.append(msg)

    log("=" * 70)
    log("  [RAG App] SchemeAssist - Tokenization & Cost Estimation Utility")
    log("=" * 70)

    # 1. Initialize Tokenizer
    model_name = "gpt-4o-mini"
    encoding = get_tokenizer(model_name)
    encoding_name = encoding.name
    log(f"Loaded Tokenizer for model: {model_name} (Encoding: {encoding_name})\n")

    # ----------------------------------------------------
    # Task 2: Report counts for three samples of varying length
    # ----------------------------------------------------
    log("------------------------- PART 1: THREE SAMPLES REPORT -------------------------")
    
    short_query = "What is the eligibility criteria for the senior citizen welfare scheme?"
    
    paragraph_desc = (
        "The SchemeAssist RAG Assistant is an intelligent retrieval-augmented generation application "
        "designed to help citizens and administrators search, retrieve, and understand official government "
        "welfare scheme documentation. By separating system prompts, ingesting raw markdown files, "
        "and leveraging LLMs, it provides reliable eligibility guidance."
    )
    
    full_document = load_sample_document("data/sample_doc.md")

    samples = [
        ("Short Query", short_query),
        ("Paragraph", paragraph_desc),
        ("Full Document", full_document)
    ]

    for name, text in samples:
        char_len = len(text)
        word_count = len(text.split())
        token_count = len(encoding.encode(text))
        ratio_char = token_count / char_len if char_len > 0 else 0
        ratio_word = token_count / word_count if word_count > 0 else 0
        
        log(f"[{name}]")
        log(f"  Character Length : {char_len}")
        log(f"  Word Count       : {word_count}")
        log(f"  Token Count      : {token_count}")
        log(f"  Tokens / Char    : {ratio_char:.4f}")
        log(f"  Tokens / Word    : {ratio_word:.4f}\n")

    # ----------------------------------------------------
    # Task 3: Cost estimation from token counts
    # ----------------------------------------------------
    log("----------------------- PART 2: COST ESTIMATION MODEL -----------------------")
    log(f"Pricing Model: {model_name}")
    log(f"  Input Rate  : ${INPUT_RATE_PER_1M:.3f} per 1M tokens")
    log(f"  Output Rate : ${OUTPUT_RATE_PER_1M:.3f} per 1M tokens\n")

    # Let's model a typical request scenario:
    # System Prompt (approx 100 tokens) + Retrieved docs (approx 500 tokens) + Query = Input tokens
    # Model response (approx 150 tokens) = Output tokens
    system_prompt_mock = "You are a helpful assistant helping citizens access government schemes."
    query_mock = short_query
    retrieved_doc_mock = full_document
    response_mock = (
        "The senior citizen welfare scheme is available to citizens aged 60 and above, "
        "with an annual family income of less than $2,000. You need to submit a birth certificate, "
        "income proof, and residency card at the local welfare office. Processing takes 15 business days."
    )

    input_text = f"{system_prompt_mock}\n\nContext:\n{retrieved_doc_mock}\n\nQuestion:\n{query_mock}"
    output_text = response_mock

    input_tokens = len(encoding.encode(input_text))
    output_tokens = len(encoding.encode(output_text))
    total_tokens = input_tokens + output_tokens

    cost = calculate_cost(input_tokens, output_tokens)

    log("[Scenario: Single Query with Ingested Context]")
    log(f"  Input Tokens  (Prompt + Context) : {input_tokens}")
    log(f"  Output Tokens (Response)         : {output_tokens}")
    log(f"  Total Transaction Tokens         : {total_tokens}")
    log(f"  Estimated Transaction Cost       : ${cost:.8f}")
    
    # Scale simulation
    total_queries = 10_000
    total_cost_10k = cost * total_queries
    log(f"\n[Projection: 10,000 Transactions]")
    log(f"  Estimated Total Cost             : ${total_cost_10k:.4f}\n")

    # ----------------------------------------------------
    # Task 4: Character Length - Token Count Relationship Demonstration
    # ----------------------------------------------------
    log("------------------ PART 3: TEXT CHARACTERISTICS VS TOKENS ------------------")
    log("Different text structures scale differently due to the tokenizer's subword rules.\n")

    # Define diverse text types to show non-proportional relationships
    comparisons = [
        (
            "Standard English Prosaic Text",
            "This is standard, simple language that usually needs very few tokens per word."
        ),
        (
            "Dense Code Snippet (Python)",
            "def fn(x):\n    return [i * 2 for i in x if i % 2 == 0]"
        ),
        (
            "Repeated Special Characters",
            "!!!???===---###$$$^^^&&&***((()))"
        ),
        (
            "Non-ASCII Text (Hindi - Hindi script)",
            "नमस्ते, क्या आप मेरी मदद कर सकते हैं कल्याणकारी योजनाओं के साथ?"
        ),
        (
            "Long Non-Standard Compound Word Blocks",
            "Supercalifragilisticexpialidocious scheme-assist-system-integration-component-wrapper"
        )
    ]

    log(f"{'Text Category':<40} | {'Chars':<6} | {'Words':<5} | {'Tokens':<6} | {'Tokens/Char':<11} | {'Tokens/Word'}")
    log("-" * 88)
    for category, text in comparisons:
        chars = len(text)
        words = len(text.split())
        tokens = len(encoding.encode(text))
        t_per_c = tokens / chars if chars > 0 else 0
        t_per_w = tokens / words if words > 0 else 0
        log(f"{category:<40} | {chars:<6} | {words:<5} | {tokens:<6} | {t_per_c:<11.4f} | {t_per_w:.4f}")
    
    log("\nKey Observations:")
    log("1. Standard English words average ~4 characters and ~1 token or less, with low token/char ratios.")
    log("2. Code snippets and punctuation-heavy lines use more tokens per character due to syntax delimiters.")
    log("3. Non-ASCII languages (like Hindi) require multiple tokens per single character because tiktoken ")
    log("   encodes non-ASCII characters as multi-byte sequences, dramatically increasing costs.")
    log("4. Extremely long or compound words are split into subword fragments, yielding higher token counts.")
    log("=" * 70)

    # Save outputs to file
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    results_path = os.path.join(output_dir, "token_estimation_results.txt")
    with open(results_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines) + "\n")
    
    print(f"\n[SUCCESS] Tokenization and cost estimation run output saved to: {results_path}")

if __name__ == "__main__":
    main()
