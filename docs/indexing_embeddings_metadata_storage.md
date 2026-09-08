# 3.31 Indexing Embeddings & Metadata Storage

## 📌 Milestone Overview

In this milestone, we load the complete welfare scheme knowledge corpus into the persistent ChromaDB vector database collection (`schemeassist_chunks`). Indexing means inserting chunk embeddings into the vector database so they can be retrieved via approximate nearest-neighbor search, while keeping original source text and structured metadata attached for grounding, citations, and metadata filtering.

---

## 🎯 Key Objectives & Capabilities

1. **Insert All Corpus Embeddings**:
   - Bulk-insert all 18 embedded chunks across the 6 policy documents in the corpus.
   - Batch operations (batch size = 10) to avoid overloading client memory or database sockets.

2. **Store Vectors with Text & Metadata**:
   - Each record stores:
     - **`id`**: Deterministic stable identifier (`{source}:{chunk_index}`, e.g., `ayushman_bharat_healthcare.md:0`).
     - **`vector`**: 1536-dimensional float vector matching the embedding model (`text-embedding-3-small` / deterministic semantic model).
     - **`text`**: Complete chunk text injected into prompts during RAG retrieval.
     - **`metadata`**: Rich structured metadata (`source`, `chunk_index`, `section`, `page`, `token_count`, `content_hash`, `doc_format`).

3. **Confirm Indexed Count**:
   - Compare vector database count against expected chunk count:
     $$\text{indexed\_count} = \text{expected\_count} = 18$$
   - Enforce assertion that no chunks were dropped, duplicated, or silently lost.

4. **Spot-Check Stored Integrity**:
   - Read back stored records from the database using known IDs.
   - Assert exact text parity, source metadata match, chunk index match, and vector length equality ($1536$).

5. **Incremental Re-Indexing on Document Changes**:
   - Content hash diffing (`SHA-256` content hash per chunk).
   - Changed chunks are upserted with new vectors.
   - Unchanged chunks remain untouched to save compute and cost.
   - Deleted chunks from updated documents are pruned via `delete_record()`.

---

## 🏗️ Architecture & Record Schema

```
Embedded Chunk (JSON)
┌─────────────────────────────────────────────────────────────┐
│ id       : "ayushman_bharat_healthcare.md:0"                │
│ text     : "# Ayushman Bharat PM-JAY Policy Document..."    │
│ embedding: [-0.0449, 0.0, 0.0, ..., 0.0449] (1536 dims)    │
│ metadata : {                                                │
│   source      : "ayushman_bharat_healthcare.md",            │
│   chunk_index : 0,                                          │
│   section     : "Executive Summary",                        │
│   page        : 1,                                          │
│   token_count : 250,                                        │
│   content_hash: "d405c13b695d250b"                          │
│ }                                                           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                      to_vector_record()
                               │
                               ▼
               ChromaDB Persistent Collection
         (HNSW index on cosine metric, dimension 1536)
┌─────────────────────────────────────────────────────────────┐
│ ids        : ["ayushman_bharat_healthcare.md:0"]            │
│ embeddings : [[-0.0449, 0.0, ..., 0.0449]]                 │
│ documents  : ["# Ayushman Bharat PM-JAY Policy..."]         │
│ metadatas  : [{"source": "...", "chunk_index": 0, ...}]     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Indexing Reconciliation & Audit Summary

- **Vector Database**: ChromaDB (Persistent at `chroma_db/`)
- **Collection Name**: `schemeassist_chunks`
- **Expected Corpus Chunks**: 18
- **Inserted This Run**: 18 (in 2 batches of size 10)
- **Indexed Database Count**: 18
- **Count Match Status**: `MATCHED (PASS)`
- **Batch Failures**: 0

### Document Source Breakdown

| Source Document | Chunks Indexed | Primary Category |
|---|---|---|
| `ayushman_bharat_healthcare.md` | 2 | Healthcare Assurance |
| `housing_welfare_guidelines.html` | 2 | Housing & Interest Subsidy |
| `pmkisan_scheme_doc.md` | 3 | Agriculture & Income Support |
| `sample_doc.md` | 7 | Welfare Framework & Exclusions |
| `scholarship_welfare_circular.md` | 2 | Education & Scholarship |
| `senior_citizen_pension_scheme.txt` | 2 | Social Security & Pension |
| **Total** | **18** | **Corpus Complete** |

---

## 🧪 Spot-Check Readback Evidence

Three diverse records were read back and compared against raw source data:

1. **`ayushman_bharat_healthcare.md:0`**:
   - Status: `PASSED`
   - Section: `Ayushman Bharat Pradhan Mantri Jan Arogya Yojana (AB-PMJAY) Policy Document`
   - Vector Dimension: `1536`
   - Text & Metadata Parity: 100% exact match

2. **`sample_doc.md:2`**:
   - Status: `PASSED`
   - Section: `2.4 Exclusion Criteria`
   - Vector Dimension: `1536`
   - Text & Metadata Parity: 100% exact match

3. **`senior_citizen_pension_scheme.txt:1`**:
   - Status: `PASSED`
   - Section: `General Overview`
   - Vector Dimension: `1536`
   - Text & Metadata Parity: 100% exact match

---

## 🔄 How Re-Indexing Works When Documents Change

When source documents are updated, rebuilding the entire index is expensive and slow:
1. **Stable IDs**: Each chunk uses `{source}:{chunk_index}` so that updates map directly to existing records.
2. **Content Hash Comparison**: Every chunk stores a `content_hash` (SHA-256). During re-indexing, if the content hash matches the stored record, the chunk is skipped.
3. **Upsert Changed Chunks**: If text or metadata changed, only the modified chunk is embedded and upserted.
4. **Prune Orphaned Chunks**: If a document was shortened (e.g. from 5 chunks to 3), the obsolete chunk IDs are identified via source query and deleted via `delete_record(chunk_id)`.

---

## 🚀 Execution & Verification Commands

```powershell
# Run the complete indexing pipeline
python src/index_corpus.py

# Run unit tests for indexing
python -m unittest tests/test_indexing.py -v

# Run the complete repository test suite (81 tests)
python -m unittest discover tests -v
```
