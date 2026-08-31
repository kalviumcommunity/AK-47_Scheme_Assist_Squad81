# Concept Guide: Tokens, Tokenization & Cost Estimation

This guide details the role of tokens, how text tokenization operates in large language models, and how to estimate API costs within our RAG system.

---

## 1. The Role of Tokens in RAG Systems
Large Language Models (LLMs) do not process raw text strings directly. Instead, they digest text split into subword fragments called **tokens**. 
In a Retrieval-Augmented Generation (RAG) system, token management is critical because:
1. **Context Window Limits**: Models cap the max number of tokens they can read. If a prompt containing multiple retrieved chunks exceeds these limits, requests fail.
2. **Operational Billing**: Most API models (like OpenAI) charge per 1,000,000 tokens for both input (context + prompt) and output (response) fields separately.

---

## 2. Technical Stack and Usage

We utilize `tiktoken` (specifically the newer `o200k_base` encoding mapping used by `gpt-4o-mini`) to perform local token measurements without making network calls.

### Running the Utility
To compute token counts, analyze costs, and generate character-to-token comparisons, execute:
```bash
python src/token_counter.py
```
This script saves its execution outputs directly to `outputs/token_estimation_results.txt`.

---

## 3. Cost Billing Model
Pricing rates configured for our model `gpt-4o-mini`:
- **Input rate**: \$0.150 per 1M tokens ($0.000000150 per token).
- **Output rate**: \$0.600 per 1M tokens ($0.000000600 per token).

### Transaction Scenario Example
For a sample request (comprising a system prompt, a context chunk from `data/sample_doc.md`, and a short search question):
- **Input Tokens**: 123
- **Output Response Tokens**: 55
- **Transaction Cost**: 
  $$(123 \times 0.000000150) + (55 \times 0.000000600) = \$0.00005145$$
- **10k scale projection cost**: \$0.5145.

---

## 4. The Character-to-Token Discrepancy
Text length (characters or words) and token count track together but are not strictly proportional. This occurs because the tokenizer decomposes text into subwords based on frequency heuristics.

### Comparative Reference Table
Our simulation experiments measured the following ratios:

| Text Category | Chars | Words | Tokens | Tokens/Char | Tokens/Word |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Standard English Prose** | 78 | 13 | 15 | 0.1923 | 1.1538 |
| **Python Code Snippet** | 54 | 16 | 24 | 0.4444 | 1.5000 |
| **Repeated Delimiters** | 33 | 1 | 14 | 0.4242 | 14.0000 |
| **Hindi script Translation**| 63 | 12 | 21 | 0.3333 | 1.7500 |
| **Long Compound Words** | 85 | 2 | 18 | 0.2118 | 9.0000 |

### Key Takeaways
1. **Standard English**: Averaging ~4.5 letters per word, English text translates close to 1-1.3 tokens per word.
2. **Code Snippets**: Delimiters, tabs/spaces, and syntax characters are tokenized individually, yielding high token-to-character ratios.
3. **Non-ASCII Text**: Non-latin characters are represented using multi-byte UTF-8 encodings. Tiktoken encodes each byte sequence, causing Hindi text to run significantly more expensive than English equivalents.
4. **Delimiters and Formatting**: Repeating special characters or spaces are split into individual sub-tokens because they rarely appear combined in the tokenizer's pre-computed vocabulary dictionary.
