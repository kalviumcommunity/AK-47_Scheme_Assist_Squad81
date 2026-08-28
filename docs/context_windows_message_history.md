# Concept Guide: Context Windows & Message History Management

This guide details the challenges of growing chat history lengths in LLM completions and explores algorithms to enforce token limit budgets in multi-turn dialogues.

---

## 1. Context Window Constraints
A **Context Window** represents the total token limit a model can read and write in a single API transaction. 
In multi-turn chat loops, this constraint presents severe engineering challenges:
1. **Unchecked Scaling**: Each turn appends additional context (User instructions, Assistant replies, and retrieved search documents). Left unmanaged, the conversational buffer quickly saturates the model's capacity limit.
2. **Hard Crash Risks**: When the token count surpasses the model's threshold, the LLM will fail to respond, throwing billing or structural context overflow errors.

---

## 2. Token Overhead in OpenAI Chat Completion
Chat Completion APIs structure history as a structured JSON list:
`[{"role": "system", "content": "..." }, {"role": "user", "content": "..."}]`

Under the hood, these role frames are formatted into a single string using template tokens (like `<|im_start|>{role}\n{content}<|im_end|>`).
- For standard OpenAI models, this introduces a structured overhead of **3 tokens per message** plus **3 tokens** to prime the final assistant response wrapper.
- This formatting overhead must be accounted for mathematically to prevent budgeting truncation errors.

---

## 3. History Management Strategies
To keep conversations within bounds, we support two distinct strategies implemented in `src/history_manager.py`:

### A. The Trimming Strategy
- **Mechanism**: Automatically evicts the oldest user-assistant turn pairs when the total token count exceeds the budget threshold.
- **Constraints**:
  - Always **preserves the system prompt** (located at index `0`) to prevent losing the assistant's behavioral persona guidelines.
  - Deletes message logs in **User-Assistant pairs** (indices `1` and `2`) to keep the conversational chain alternating correctly.
- **Pros/Cons**: Zero API cost, extremely simple to compute. However, older factual context is lost forever.

### B. The Summarization Strategy
- **Mechanism**: Condenses older message turns into a single unified summary entry block.
- **Implementation**:
  - Isolates the core `system` prompt and the most recent `user`/`assistant` turn.
  - Extracts intermediate turns, formats them as a text transcript, and sends them to a summarizer utility (falling back to a deterministic topic-matching mock summarizer if offline).
  - Replaces all intermediate turns with a single consolidated statement: `{"role": "system", "content": "[Summary of earlier discussion: ...]"}`.
- **Pros/Cons**: Preserves the abstract narrative history of previous dialogue turns. However, it incurs additional token costs and latency during summarization API calls.

---

## 4. Run Instructions and Verification
To run the automated multi-turn simulation demonstrating context limit enforcement under both strategies:
```bash
python src/history_manager.py
```
This logs the detailed step-by-step memory eviction runs to `outputs/history_management_results.txt`.
