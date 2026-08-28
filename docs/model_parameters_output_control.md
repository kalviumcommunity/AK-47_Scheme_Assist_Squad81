# Concept Guide: Model Parameters & Output Control

This guide documents how hyperparameters impact large language model outputs and outlines recommended settings for building a grounded, factual RAG retrieval assistant.

---

## 1. Parameters Affecting Generation
When invoking LLM APIs, developers use several parameters to steer the style, length, and scope of responses.

### A. Temperature
- **Role**: Controls randomness and stochastic variety in text generation. The model converts raw word logits (likelihoods) into probability distributions.
  - **High Temperature (e.g., 1.0 to 1.5)**: Expands the selection span, including lower-probability words. This yields creative, fluid, or varied text but increases hallucination risks.
  - **Low Temperature (e.g., 0.0 to 0.2)**: Restricts token choices to the highest-probability options. At `0.0`, sampling becomes completely deterministic: the same input prompt always returns the exact same string output.

### B. Max Tokens (`max_tokens`)
- **Role**: Places a hard ceiling on the maximum length of model replies. It acts as an absolute quota safeguard, returning a `finish_reason` of `"length"` if generation exceeds the threshold.

### C. Stop Sequences (`stop`)
- **Role**: Instructs the model to immediately cease generating content if a specific string (e.g. a word, a newline, or formatting markup) is encountered. It returns a `finish_reason` of `"stop"`. Useful for preventing runaway chat iterations.

---

## 2. Experimental Verification

Our utility `src/model_parameter_experiment.py` performs empirical runs to test these settings, storing logs in `outputs/parameter_experiments_results.txt`.

### Running Verification
```bash
python src/model_parameter_experiment.py
```

### Key Experimental Findings
- **Temperature runs**: Run at `0.0` produced 100% duplicate outcomes (Uniqueness 1/3), whereas runs at `1.2` produced diverse, fluid creative titles (Uniqueness 2/3).
- **Max tokens runs**: Setting `max_tokens=15` successfully truncated the output mid-sentence and returned `finish_reason: length`.
- **Stop sequence runs**: Restricting text with stop sequence `["Office", "online"]` halted generation immediately before the word `"Office"`, returning a finish reason of `"stop"`.

---

## 3. Recommended Settings for Grounded RAG Tasks

When building an assistant like **SchemeAssist** designed to query government documentation factually, the following configuration is strongly recommended:

| Parameter | Recommended Value | Engineering Rationale |
| :--- | :--- | :--- |
| **Temperature** | `0.0` | Eliminates random word choices, forcing the model to rely solely on facts present in the retrieved context documents. |
| **Max Tokens** | `300` to `500` | Limits generation length for cost control while leaving ample headroom for detailed instructions. |
| **Top P** | `1.0` (or `0.1` if temp is >0) | Standard setup: do not restrict probabilities unless using a low temp fallback where limiting candidate vocabulary is useful. |
| **Stop Sequences**| `["\n\n", "User:", "Context:"]` | Acts as safety gates to prevent chat loop leakages or the model generating simulated dialog turns. |
