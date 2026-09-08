# 3.18 Prompt Templates & Reusable Prompt Design — Summary & Documentation

## 3–4 Line Short Summary
> We decoupled prompt strings from application business logic into a centralized `prompts/` module using a reusable `PromptTemplate` class and `render()` function with named placeholders. Dynamic values (context, citizen questions, and metadata) are injected at runtime across multiple features—including an interactive citizen chat assistant and a batch CLI compliance auditor. This eliminates inline prompt drift, enables seamless prompt versioning (`v1` vs `v2`), and ensures all wording or grounding updates occur in one single source of truth.

---

## 1. What We Implemented

### Task 1 — Define Templates with Named Placeholders & Render Function
- Created `prompts/templates.py` and `prompts/answer.py`.
- Implemented `PromptTemplate` encapsulating named placeholders (e.g. `{context}`, `{question}`, `{role_instruction}`), default values, placeholder validation, and extraction.
- Implemented `render(template, **values)` that validates all required variables at runtime before injecting values.

### Task 2 — Inject Dynamic Values at Runtime
- Dynamic inputs (retrieved scheme context chunks, citizen questions, applicant demographics, and evaluation parameters) are injected at runtime into the prompt templates to produce final, fully rendered prompt payloads.

### Task 3 — Reuse Across Multiple Features
- **Feature 1 (Interactive Citizen Chat Path)**: Ingests user questions, retrieves knowledge base guidelines, and renders `SCHEME_QA_TEMPLATE_V2` with strict grounding and citation instructions.
- **Feature 2 (Batch Scheme Evaluator & CLI Tool)**: Evaluates multiple scheme test cases in batch using `SCHEME_BATCH_EVAL_TEMPLATE` with identical grounding rules.
- **Feature 3 (Dynamic Applicant Profiler)**: Evaluates applicant eligibility against scheme rules using `SCHEME_ELIGIBILITY_TEMPLATE`.

### Task 4 — Separate Templates from Business Logic
- All prompt definitions, grounding rules, fallback messages, and templates reside strictly inside the `prompts/` package.
- Business logic in `src/` (`src/app.py`, `src/prompt_template_manager.py`) imports templates directly, allowing prompt engineers to refine prompts without editing application code.
- Added `TemplateRegistry` supporting safe template versioning (`v1.0.0` baseline vs `v2.0.0` production).

### Task 5 — Example Renders & Automated Verification
- Generated and saved sample filled prompts and evaluation logs to:
  - [`outputs/prompt_template_renders.txt`](../outputs/prompt_template_renders.txt)
  - [`outputs/prompt_template_renders.json`](../outputs/prompt_template_renders.json)
- Added 9 unit tests in [`tests/test_prompt_templates.py`](../tests/test_prompt_templates.py) verifying placeholder extraction, runtime rendering, missing variable error handling, default values, and cross-feature reuse.

---

## 2. Architecture & Code Highlights

### Centralized Template Definition (`prompts/answer.py` & `prompts/templates.py`)
```python
# prompts/answer.py — prompts kept OUT of business logic
ANSWER = (
    "You are a support assistant. Answer ONLY from the context.\n"
    "If the answer isn't there, say you don't know.\n\n"
    "Context:\n{context}\n\nQuestion: {question}"
)

def render(template, **values):
    return template.format(**values)
```

### Multi-Feature Reuse (`src/app.py` & `src/prompt_template_manager.py`)
```python
# Feature 1: Chat Path
from prompts.answer import ANSWER, render
msg_chat = render(ANSWER, context=retrieved_chunks, question=user_query)

# Feature 2: Batch / CLI Evaluator Path
from prompts.templates import SCHEME_BATCH_EVAL_TEMPLATE, render
msg_batch = render(
    SCHEME_BATCH_EVAL_TEMPLATE,
    batch_id=101,
    scheme_name="Pre-Matric Minority Scholarship",
    context=guidelines_text,
    query="Verify income cap <= Rs. 1.00 Lakh",
)
```

---

## 3. Video Walkthrough Script (3–5 Minutes)

Use the talking points below when recording your video presentation:

1. **Benefit of Templating Prompts vs. Inline Strings**:
   - *Explanation*: Inline prompts scatter strings across dozens of files, causing prompt drift where copies fall out of sync. Templating centralizes all prompt text in `prompts/`, providing a single source of truth for guidelines, grounding, and tone.
2. **How Values are Injected into a Template**:
   - *Explanation*: Templates define named placeholders (e.g. `{context}`, `{question}`). At runtime, `render(template, **values)` parses dynamic variables, validates that no required placeholders are missing, and injects runtime data seamlessly.
3. **How Templates Keep Prompts Consistent Across the App**:
   - *Explanation*: Both the interactive chat endpoint and the batch compliance evaluator share the exact same template structure and grounding constraints, ensuring identical behavioral standards across all features.
4. **How to Version or Update a Template Safely**:
   - *Explanation*: Using `TemplateRegistry`, we register versioned templates (e.g. `scheme_qa` `v1.0.0` vs `v2.0.0`). New features can adopt `v2.0.0` while existing consumers continue running on `v1.0.0` until upgraded, preventing breaking changes.
5. **Follow-up: How do templates help when prompts must change later?**:
   - *Explanation*: When a new rule (like requiring official circular citations or changing fallback wording) is mandated, developers update the prompt once in `prompts/templates.py`. Every downstream feature updates automatically without touching any business logic.
