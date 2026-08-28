# SchemeAssist RAG Assistant — Development Environment & Workspace Setup

Welcome to the **SchemeAssist RAG Assistant** workspace repository. This repository establishes a clean, isolated, reproducible development workspace foundation following standard AI application engineering practices.

---

## 📁 Repository Structure

```
AK-47_Scheme_Assist_Squad81/
├── data/              # Source knowledge documents (git-ignored except sample/placeholders)
│   ├── .gitkeep
│   └── sample_doc.md
├── src/               # Application source code (ingestion, retrieval, config, main app)
│   ├── __init__.py
│   ├── config.py
│   ├── ingestion.py
│   ├── retrieval.py
│   └── main.py
├── prompts/           # Decoupled system prompts and templates
│   ├── .gitkeep
│   ├── README.md
│   └── rag_system_prompt.txt
├── outputs/           # Application logs, generated answers, evaluation outputs
│   └── .gitkeep
├── .env               # Local environment variables & secrets (GIT-IGNORED)
├── .env.example       # Template of required environment variables (COMMITTED)
├── .gitignore         # Strict exclusion rules for secrets, .venv, and data
├── requirements.txt   # Locked python dependencies for reproducible setup
└── README.md          # Setup instructions and verification documentation
```

---

## 🚀 Setup & Installation Instructions

Follow these exact steps to reproduce the environment and run the application on any fresh machine:

### Step 1: Clone the Repository
```bash
git clone https://github.com/kalviumcommunity/AK-47_Scheme_Assist_Squad81.git
cd AK-47_Scheme_Assist_Squad81
```

### Step 2: Create & Activate Virtual Environment
- **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\activate
  ```
- **macOS / Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### Step 3: Install Project Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to create your local `.env` file and populate your credentials:
- **Windows:**
  ```powershell
  copy .env.example .env
  ```
- **macOS / Linux:**
  ```bash
  cp .env.example .env
  ```

*Edit `.env` and insert your OpenAI API Key:*
```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_actual_openai_api_key_here
CHAT_MODEL=gpt-4o-mini
EMBED_MODEL=text-embedding-3-small
```

---

## 🧪 Reproducibility Verification Test

To verify that your workspace setup is completely functional, run the verification entrypoint:

```bash
python src/main.py
```

### Expected Output Log Confirmation
```text
=================================================================
  [RAG App] SchemeAssist - Workspace Verification Test
=================================================================
[CONFIG LOG] Loaded model: gpt-4o-mini | Base URL: https://api.openai.com/v1
[INGESTION LOG] Successfully ingested 1 document(s) from 'data/'.
[PROMPT LOG] Loaded system prompt (246 chars).

[QUERY]: 'welfare schemes eligibility guidance'
[RETRIEVED DOC]: sample_doc.md
[CONTENT PREVIEW]:
# Knowledge Base Document: Government Welfare Schemes Overview...

[OUTPUT LOG] Verification run logged to 'outputs/verification_run.log'.
=================================================================
  [SUCCESS] WORKSPACE REPRODUCIBILITY TEST PASSED SUCCESSFULLY!
=================================================================
```

---

## 🛠️ Implemented Core Concepts

To support robust RAG operation, we have added three core utilities evaluating token usage, context history, and execution control:

### 1. Token Estimation & Billing
- **Script**: `src/token_counter.py`
- **Output Report**: `outputs/token_estimation_results.txt`
- **Purpose**: Counts token usage locally using `tiktoken` (`gpt-4o-mini` / `o200k_base` model mapping) and profiles input/output costs at target rates ($0.15/1M input, $0.60/1M output).
- **Execution**:
  ```bash
  python src/token_counter.py
  ```

### 2. Context Window & History Manager
- **Script**: `src/history_manager.py`
- **Output Report**: `outputs/history_management_results.txt`
- **Purpose**: Enforces conversational token limits using two budget-preservation strategy handlers:
  - **Trimming**: Evicts older user-assistant conversation turn pairs while preserving the target system prompt.
  - **Summarization**: Compresses older middle turns into a concise single system summary block.
- **Execution**:
  ```bash
  python src/history_manager.py
  ```

### 3. Model Parameters & Output Control
- **Script**: `src/model_parameter_experiment.py`
- **Output Report**: `outputs/parameter_experiments_results.txt`
- **Purpose**: Demonstrates execution behavior when tuning generation controls (Temperature, `max_tokens` length truncation, and `stop` sequence halting filters), recommending deterministic settings needed for grounded, factual schemes matching.
- **Execution**:
  ```bash
  python src/model_parameter_experiment.py
  ```

---

## 🔒 Security & Secret Management

- **API Keys are strictly excluded from source code:** All secrets are loaded dynamically at runtime via `python-dotenv` from the `.env` file.
- **Git Protection:** `.gitignore` explicitly prevents `.env`, `.venv/`, and sensitive files in `data/` or `outputs/` from ever being pushed to remote repositories.
