# Backend API for the RAG Service (MSU 3.44)

## Overview
This document describes the design, architecture, and operational specifications of the **SchemeAssist RAG Backend API Service**. The service wraps the verified Retrieval-Augmented Generation (RAG) pipeline in a production-ready **FastAPI** web application. It acts as a stable, decoupled contract between the retrieval & LLM pipeline and external clients (web frontends, mobile applications, chat widgets, and partner microservices).

---

## 1. Why Expose the RAG Pipeline as an API?

1. **Decoupled Architecture**: Frontends and consumer services shouldn't manage vector stores, embedding models, tokenizers, or prompt orchestration.
2. **Stable API Contract**: Returning structured JSON with strict types ensures clients can rely on fields (`answer`, `sources`, `status`) without fragile parsing of natural language text.
3. **Centralized Governance & Guardrails**: Quality thresholds, rate-limiting, citation validation, and out-of-domain refusals run in one controlled service layer.
4. **Environment Isolation**: Vector database connections, OpenAI API keys, and model names are loaded from server environment variables rather than exposed to clients.

---

## 2. API Endpoints Specification

### 2.1 `GET /health`
Returns system liveness and dynamic configuration loaded from the environment.

- **Method**: `GET`
- **Response Shape**:
```json
{
  "status": "healthy",
  "embedding_model": "text-embedding-3-small",
  "chat_model": "gpt-4o-mini",
  "vector_db_url": "chroma_db",
  "collection_name": "schemeassist_chunks",
  "openai_configured": true,
  "indexed_chunks": 18
}
```

---

### 2.2 `POST /query`
Accepts a natural language question and returns a grounded answer backed by cited chunk metadata.

- **Method**: `POST`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "question": "What is the annual financial assistance provided under PM-KISAN?"
}
```

- **Validation Rules**:
  - `question` length: minimum 3 characters, maximum 1000 characters.
  - Whitespace-only strings: rejected with `400 Bad Request`.
  - Schema violations: rejected with `422 Unprocessable Content`.

- **Success Response (`200 OK`)**:
```json
{
  "answer": "Under the Scheme, an amount of Rs 6,000/- per year is released in three 4-monthly installments of Rs 2,000/- each directly into the bank accounts of the beneficiaries. Pradhan Mantri Kisan Samman Nidhi (PM-KISAN) Operational Guidelines",
  "sources": [
    {
      "source": "pmkisan_scheme_doc.md",
      "chunk_id": "pmkisan_scheme_doc.md:0",
      "score": 0.1936
    },
    {
      "source": "senior_citizen_pension_scheme.txt",
      "chunk_id": "senior_citizen_pension_scheme.txt:0",
      "score": 0.167
    },
    {
      "source": "scholarship_welfare_circular.md",
      "chunk_id": "scholarship_welfare_circular.md:1",
      "score": 0.1629
    }
  ],
  "status": "answered"
}
```

- **Out-of-Domain Refusal Response (`200 OK`)**:
```json
{
  "answer": "I do not have sufficient verified information in the official welfare scheme guidelines to answer this question. Please consult the official ministry portal or helpdesk.",
  "sources": [],
  "status": "refused_weak_context"
}
```

---

## 3. Environment Configuration

All configuration is loaded at runtime from environment variables using `src/config.py`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OPENAI_API_KEY` | `""` | OpenAI secret key (never committed to git) |
| `EMBED_MODEL` | `text-embedding-3-small` | Model name for vector embeddings |
| `CHAT_MODEL` | `gpt-4o-mini` | Chat completion LLM model |
| `VECTOR_DB_URL` | `chroma_db` | ChromaDB persistence path or connection URL |
| `COLLECTION_NAME`| `schemeassist_chunks` | Active vector collection name |
| `API_HOST` | `0.0.0.0` | API bind address |
| `API_PORT` | `8000` | API listener port |

---

## 4. Frontend Consumption Guide

A web or mobile frontend interacts with `/query` as follows:

```javascript
async function askSchemeQuestion(userQuestion) {
  try {
    const response = await fetch("http://localhost:8000/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: userQuestion })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "API request failed");
    }

    const data = await response.json();

    // 1. Display primary grounded answer
    renderChatBubble(data.answer, data.status);

    // 2. Render evidence cards / source badges
    if (data.status === "answered" && data.sources.length > 0) {
      renderSourceCitations(data.sources);
    }
  } catch (err) {
    showNotification("Unable to reach SchemeAssist service: " + err.message);
  }
}
```
