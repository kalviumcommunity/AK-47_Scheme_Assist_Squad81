# SchemeAssist Core LLM Modules — Briefing Document

This document provides a concise overview of the three core LLM integration modules in the SchemeAssist application.

---

### 1. [`src/llm_client.py`](file:///c:/Users/msham/Desktop/AK-47_Scheme_Assist_Squad81/src/llm_client.py)
- **Role:** Handles baseline API connectivity and authentication using environment variables (`.env`).
- **Core Features:** Manages system/user chat completion calls, detailed payload logging, and token usage tracking.
- **Resilience:** Implements robust error handling for 401 (Authentication) and 429 (Rate Limits) with exponential backoff retries.
- **Purpose:** Serves as the primary entry point for secure, reliable communication with OpenAI-compatible LLM endpoints.

---

### 2. [`src/model_parameter_experiment.py`](file:///c:/Users/msham/Desktop/AK-47_Scheme_Assist_Squad81/src/model_parameter_experiment.py)
- **Role:** Evaluates and tunes model generation hyperparameters for grounded and factual RAG performance.
- **Core Features:** Tests temperature variations (0.0 vs. high), max token boundaries, stop sequences, and nucleus sampling (`top_p`).
- **Insights:** Proves that `temperature=0.0` eliminates hallucinations while stop sequences prevent runaway generation turns.
- **Purpose:** Establishes empirically tested parameter guidelines to ensure deterministic, cost-effective responses.

---

### 3. [`src/structured_output_handler.py`](file:///c:/Users/msham/Desktop/AK-47_Scheme_Assist_Squad81/src/structured_output_handler.py)
- **Role:** Enforces, parses, and validates strict JSON response schemas (`{"answer": ..., "source": ...}`) from the model.
- **Core Features:** Combines `json_object` response mode with a multi-tier defensive parser (native `json.loads` + regex cleaner).
- **Validation & Recovery:** Validates required fields using Pydantic models (`SchemeAnswerResponse`) and triggers automated self-healing retries on failure.
- **Purpose:** Provides machine-readable, crash-proof structured outputs ready for downstream app, database, and UI integration.
