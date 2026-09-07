# 3.43 RAG Evaluation & Answer Quality Scoring

## 📌 Milestone Overview

Milestone 3.43 evaluates the entire Retrieval-Augmented Generation (RAG) system end-to-end rather than assessing retrieval or generation in isolation. A high-quality RAG system must be factually correct, grounded in retrieved context without hallucination, and supported by accurate citations.

This module provides:
1. **Benchmark Test Set**: A curated set of questions spanning welfare schemes with ground-truth expected points and expected source files, plus adversarial/out-of-domain queries to evaluate guardrails.
2. **Three-Dimensional Answer Scoring**:
   - **Correctness**: Measures whether the answer contains the essential factual points requested.
   - **Grounding**: Verifies that every claim in the answer is supported by the retrieved context.
   - **Citation Accuracy**: Validates that cited sources match the true supporting documents (precision, recall, F1).
3. **Failure Diagnosis & Root-Cause Analysis**: Categorizes why specific queries underperform (retrieval ranking errors, missing context, incomplete answers, or hallucinated claims).
4. **Actionable Improvement Strategies**: Direct engineering guidance on improving whichever dimension is the weakest.

---

## 📐 Scoring Methodology & Mathematical Formulas

### 1. Correctness (Factual Recall)
$$\text{Correctness} = \frac{\sum_{i=1}^{M} \mathbb{I}(\text{point}_i \in \text{Answer})}{M}$$
- Evaluates recall of $M$ required factual points in the generated answer.
- Uses token-level matching and semantic entity overlap.
- Score $\in [0.0, 1.0]$.

### 2. Grounding (Context Faithfulness)
$$\text{Grounding} = \frac{\text{Supported Clauses in Answer}}{\text{Total Factual Clauses in Answer}}$$
- Splits the answer into discrete statements and tests whether key tokens are attested in the retrieved text context.
- Explicit, verified fallback refusals ("I do not have sufficient verified information...") receive 1.0 grounding because they make no hallucinated factual claims.
- Score $\in [0.0, 1.0]$.

### 3. Citation Accuracy (Source Precision & Recall)
For queries expecting sources $S_{expected}$ and produced citations $S_{cited}$:
- If $S_{expected} = \emptyset$ (unanswerable / out-of-domain query):
  $$\text{Citation Accuracy} = \begin{cases} 1.0 & \text{if } |S_{cited}| = 0 \\ 0.0 & \text{if } |S_{cited}| > 0 \end{cases}$$
- If $S_{expected} \neq \emptyset$:
  $$\text{Precision} = \frac{|S_{cited} \cap S_{expected}|}{|S_{cited}|}, \quad \text{Recall} = \frac{|S_{cited} \cap S_{expected}|}{|S_{expected}|}$$
  $$\text{Citation Accuracy (F1)} = \frac{2 \cdot \text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$

---

## 📊 Evaluation Scorecard & Results

```text
================================================================================
  SCHEMEASSIST: 3.43 RAG EVALUATION & ANSWER QUALITY SCORING
================================================================================
Evaluating 7 test question(s) across Correctness, Grounding, and Citations...

ID         Question                                   Correct  Ground   Cite     Status
------------------------------------------------------------------------------------
Q1_PMKISAN_BENEFIT What is the annual financial assistance .. 1.00     1.00     1.00     PASS
Q2_ABPMJAY_COVERAGE What hospitalisation cover is provided u.. 1.00     1.00     1.00     PASS
Q3_PMAY_SUBSIDY What interest subsidy is offered under P.. 1.00     1.00     1.00     PASS
Q4_PENSION_ELIGIBILITY What are the age and assistance criteria.. 1.00     1.00     1.00     PASS
Q5_SCHOLARSHIP_CRITERIA What are the eligibility conditions for .. 0.33     1.00     0.00     FAIL
Q6_PMDIS_EXCLUSIONS Which categories are explicitly disquali.. 0.33     1.00     1.00     FAIL
Q7_OUT_OF_DOMAIN_GUARDRAIL What flight license is required to pilot.. 1.00     1.00     1.00     PASS
------------------------------------------------------------------------------------

--- OVERALL RAG QUALITY METRICS ---
  • Total Evaluated Questions : 7
  • Average Correctness       : 81.0%
  • Average Grounding         : 100.0%
  • Average Citation Accuracy : 85.7%
  • Overall Composite Score   : 88.9%
  • Perfect Score Pass Rate   : 71.4% (5/7)
  • Notable Failures Detected : 2
```

---

## 🔍 Notable Failures & Root Cause Analysis

### Case 1: Q5 — Scholarship Eligibility Criteria
- **Question**: *"What are the eligibility conditions for pre-matric scholarship assistance?"*
- **Expected Sources**: `{"scholarship_welfare_circular.md"}`
- **Actual Citations**: `["ayushman_bharat_healthcare.md"]`
- **Scores**: Correctness = 0.33, Grounding = 1.00, Citation Accuracy = 0.00
- **Diagnosed Root Cause**: **Weak Retrieval Ranking**.
  Semantic vector search assigned a slightly higher similarity score to Ayushman Bharat (0.1856) than the Scholarship circular (0.1731) because of broad welfare terminology. Because rank 1 was Ayushman, the answer extracted healthcare text rather than scholarship rules.
- **Recommended Fix**: Implement **hybrid search with BM25 keyword boosting** ($\beta = 0.4$ on exact keyword "scholarship") to ensure the specific circular outranks generic healthcare chunks.

### Case 2: Q6 — PM-DIS Exclusions
- **Question**: *"Which categories are explicitly disqualified from receiving benefits under PM-DIS?"*
- **Expected Sources**: `{"sample_doc.md"}`
- **Actual Citations**: `["sample_doc.md"]`
- **Scores**: Correctness = 0.33, Grounding = 1.00, Citation Accuracy = 1.00
- **Diagnosed Root Cause**: **Incomplete Answer Recall**.
  Retrieval found the exact document and section (Citation = 1.0, Grounding = 1.0), but the 2-sentence extraction window only captured Institutional Landholders and missed MPs and Pensioners.
- **Recommended Fix**: Expand the answer synthesis extraction window for enumeration questions or prompt the LLM to format bulleted lists of all listed exclusions.

---

## 🛠️ How to Improve Weak Dimensions

| Weak Dimension | Common Causes | Engineering Remedies |
|---|---|---|
| **Low Correctness** | Retrieval missed chunk, prompt missed key details, extraction window too narrow | 1. Increase top-$k$ depth ($k=3 \to 5$)<br>2. Add hybrid retrieval ($\alpha$ vector + $\beta$ keyword)<br>3. Prompt LLM explicitly: *"List all conditions and numbers"* |
| **Low Grounding** | LLM hallucinating unverified facts, high temperature, weak fallback | 1. Lower temperature to 0.0<br>2. Add strict constraint: *"Answer ONLY using context. If unknown, refuse."*<br>3. Raise fallback relevance threshold |
| **Low Citation Accuracy** | Missing source metadata, citing unrelated chunks, wrong attribution | 1. Enforce strict chunk-level metadata tracking during ingestion<br>2. Restrict citations to chunks whose text was actually incorporated in answer<br>3. Discard chunks below relevance score |

---

## 🚀 Verification & Automated Tests

```powershell
# Run the evaluation pipeline directly
python src/rag_evaluation.py

# Run dedicated unit tests (13 tests)
python -m unittest tests/test_rag_evaluation.py -v

# Run entire repository test suite (95 tests)
python -m unittest discover tests -v
```
