# Prompts Directory

This directory contains centralized prompt templates, rendering engines, and prompt engineering documentation kept strictly decoupled from application business logic:

- [`templates.py`](templates.py): Core modular prompt templating engine (`PromptTemplate`, `TemplateRegistry`, `render_template`) defining versioned templates (`SCHEME_QA_TEMPLATE_V1/V2`, `SCHEME_BATCH_EVAL_TEMPLATE`, `SCHEME_ELIGIBILITY_TEMPLATE`, `SYSTEM_SCHEME_ASSIST_TEMPLATE`).
- [`answer.py`](answer.py): Standalone prompt template module providing `ANSWER`, `ANSWER_V2`, and `render()` for direct feature imports.
- [`rag_system_prompt.txt`](rag_system_prompt.txt): Production system instruction guiding SchemeAssist with Role, Scope, Constraints, and Fallback.
- [`json_structured_prompt.txt`](json_structured_prompt.txt): JSON schema extraction prompt for structured outputs.
- [`PROMPT_ANALYSIS.md`](PROMPT_ANALYSIS.md): Comprehensive documentation covering System vs. User roles, Prompt Variation comparisons (Vague vs. Constrained vs. JSON), and the technical justification for the chosen prompt.

