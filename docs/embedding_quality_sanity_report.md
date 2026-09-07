# 3.29 Embedding Quality Checks & Sanity Tests Report

## 📌 Executive Summary

Before trusting vector retrieval in **SchemeAssist**, we verify whether our embeddings behave sensibly. A broken pipeline can still generate vectors, but those vectors may originate from the wrong model, be misaligned with document chunk boundaries, or use an incorrect similarity metric. Sanity tests catch these vulnerabilities early by ensuring known-related texts consistently rank above unrelated ones.

### Pipeline Configuration
- **Embedding Model**: `text-embedding-3-small`
- **Provider**: `offline`
- **Indexed Corpus Chunks**: `18`
- **Vector Dimensionality**: `1536`
- **Evaluation Timestamp**: `2026-09-07T05:45:04.997351+00:00`

## 📊 Summary Scorecard

| Metric | Result | Target | Status |
| :--- | :--- | :--- | :--- |
| **Known Relevance Accuracy** | **100.0%** (8/8) | $\ge 80\%$ | ✅ PASS |
| **Average Separation Margin ($\Delta$)** | **+0.0575** | $> 0.0$ | ✅ PASS |
| **Borderline Diagnostic Cases** | **2** | Diagnostic | ⚠️ INSPECTED |
| **Model Mismatch Failure Detection** | **1** | Expected 1 | 🛡️ VERIFIED |

--- 

## 🧪 Task 1 & 2: Known Relevance Test Cases & Ranking Verification

For each known query, we assert that the expected source document ranks #1 and achieves a positive separation margin over the highest unrelated document:

$$\Delta = \text{score}_{\text{best\_related}} - \text{score}_{\text{best\_unrelated}} > 0$$

| Test ID | Query | Expected Source | Top Ranked Source | Top Score | Margin ($\Delta$) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | What is the annual hospitalisation health cover amount per family under Ayushman Bharat PM-JAY? | `ayushman_bharat_healthcare.md` | `ayushman_bharat_healthcare.md` | 0.2337 | +0.1227 | ✅ PASS |
| **TC-02** | Which treatment procedures and surgical specialties are covered in empanelled hospitals under PM-JAY? | `ayushman_bharat_healthcare.md` | `ayushman_bharat_healthcare.md` | 0.1730 | +0.0432 | ✅ PASS |
| **TC-03** | How much financial assistance is released to landholding farmer families in installments under PM-KISAN? | `pmkisan_scheme_doc.md` | `pmkisan_scheme_doc.md` | 0.2639 | +0.1058 | ✅ PASS |
| **TC-04** | Which farmer categories are in the exclusion list under PM-KISAN for institutional landholders or constitutional post holders? | `pmkisan_scheme_doc.md` | `pmkisan_scheme_doc.md` | 0.3031 | +0.0980 | ✅ PASS |
| **TC-05** | What is the upfront interest subsidy rate on home loans under Credit Linked Subsidy Scheme CLSS for PMAY? | `housing_welfare_guidelines.html` | `housing_welfare_guidelines.html` | 0.2079 | +0.0460 | ✅ PASS |
| **TC-06** | What is the minimum carpet area and mandatory toilet construction requirement for a pucca house? | `housing_welfare_guidelines.html` | `housing_welfare_guidelines.html` | 0.2197 | +0.0208 | ✅ PASS |
| **TC-07** | What is the monthly pension amount and age qualification for elderly citizens under senior citizen pension? | `senior_citizen_pension_scheme.txt` | `senior_citizen_pension_scheme.txt` | 0.2135 | +0.0214 | ✅ PASS |
| **TC-08** | What are the academic merit conditions and minimum 50% marks requirement for the pre-matric scholarship? | `scholarship_welfare_circular.md` | `scholarship_welfare_circular.md` | 0.2043 | +0.0024 | ✅ PASS |

--- 

## 🔍 Task 3: Surprising, Borderline, & Failing Cases Analysis

A useful sanity report looks for failures and risks, not just passes. We evaluated two critical failure modes:

### Case `EDGE-01`: ⚠️ BORDERLINE
- **Query**: *"What is the toll-free helpline number and portal for registering grievances and tracking support tickets?"*
- **Expected Source**: `pmkisan_scheme_doc.md`
- **Top Ranked Source**: `pmkisan_scheme_doc.md` (Score: `0.2243`, Margin: `0.0131`)
- **Diagnostic Insight**: Surprising/Borderline case: The query lacks scheme-specific terminology. Both 'pmkisan_scheme_doc.md' and 'ayushman_bharat_healthcare.md' share generic helpline and grievance portal boilerplate ('toll-free', 'helpline', 'grievance portal'). Causes tight score separation (borderline margin) or unexpected top rank.

### Case `EDGE-02`: ⚠️ BORDERLINE
- **Query**: *"Direct benefit transfer DBT funds credited to Aadhaar seeded bank accounts across milestone stages"*
- **Expected Source**: `housing_welfare_guidelines.html`
- **Top Ranked Source**: `housing_welfare_guidelines.html` (Score: `0.2544`, Margin: `0.0495`)
- **Diagnostic Insight**: Borderline case: High cross-scheme conceptual overlap. Both PMAY housing and PM-KISAN agriculture rely on DBT and Aadhaar-seeded accounts. Without scheme context, the embedding space cannot decisively separate the two programs.

### Case `EDGE-03`: 🛡️ EXPECTED FAILURE
- **Query**: *"What is the annual hospitalisation health cover amount per family under Ayushman Bharat PM-JAY?"*
- **Expected Source**: `ayushman_bharat_healthcare.md`
- **Top Ranked Source**: `senior_citizen_pension_scheme.txt` (Score: `0.0536`, Margin: `-0.0101`)
- **Diagnostic Insight**: Failing case: Simulated model mismatch. Corpus chunks were embedded in Space A, but this query is embedded in an incompatible vector space (Space B / alien model). Even though the query matches Ayushman Bharat perfectly, the vectors are in different spaces, destroying cosine ranking and causing retrieval failure.

### Case `EDGE-04`: FAILED
- **Query**: *"Who is excluded from receiving welfare benefits due to paying income tax?"*
- **Expected Source**: `pmkisan_scheme_doc.md`
- **Top Ranked Source**: `scholarship_welfare_circular.md` (Score: `0.1593`, Margin: `-0.0749`)
- **Diagnostic Insight**: Surprising risk: Generic exclusion query. Because multiple welfare policies (scholarship circular and pension guidelines) heavily mention 'income' ceilings, a query asking about income tax exclusion without specifying agriculture matches income-related educational/housing schemes with comparable similarity.

### 🚨 Critical Vulnerability: Mismatched Models Break Ranking
If documents are embedded with one model (e.g., `text-embedding-3-small`) and user queries are embedded with another (or an uncalibrated embedding space), the vectors do not share the same semantic coordinate system. As demonstrated in test `EDGE-03`:
- Cosine similarity still returns a mathematical floating point number between -1.0 and +1.0.
- However, the relative distance has **zero correlation with semantic relevance**.
- The expected document (`ayushman_bharat_healthcare.md`) failed to rank first, replaced by an unrelated document with negative separation margin.
- **Mitigation**: SchemeAssist enforces explicit embedding model metadata tags on indexed collections and validates model name parity before query execution.

--- 

## 💡 Architectural Recommendations for Production Retrieval

1. **Metadata Pre-Filtering**: For queries with high administrative overlap (helpline, portal, contact numbers), filter by `scheme_name` or `category` metadata prior to vector ranking.
2. **Hybrid Retrieval (Dense + BM25)**: Combine vector cosine similarity with BM25 keyword matching (reciprocal rank fusion) to preserve exact numerical matches (e.g. 'Rs 6,000' or '6.5%').
3. **Cross-Encoder Re-Ranking**: Use a secondary cross-encoder re-ranker (e.g., `bge-reranker-large`) on top-10 retrieved candidates to resolve tight borderline margins.
