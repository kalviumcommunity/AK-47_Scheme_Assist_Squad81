# Team GitHub Repository & Workflow Guidelines

This document outlines the standard collaboration workflow, branching strategy, commit conventions, code review process, and issue tracking practices for the **SchemeAssist (AK-47_Scheme_Assist_Squad81)** project.

---

## 1. Branching Strategy

Our team enforces strict branch isolation to ensure the main codebase remains stable and releasable at all times.

- **Main Branch (`main`)**:
  - Contains production-ready, thoroughly tested, and peer-reviewed code.
  - Direct pushes to `main` are strictly prohibited.
- **Feature & Task Branches**:
  - All work (features, bug fixes, documentation, refactoring) must take place on dedicated branches created off `main`.
  - Naming Convention: `[type]/[short-description]`
    - `feature/[description]` - New analytical capabilities or data pipelines (e.g., `feature/data-ingestion`)
    - `fix/[description]` - Bug fixes or logic corrections (e.g., `fix/validation-logic`)
    - `docs/[description]` - Documentation additions or updates (e.g., `docs/data-dictionary`)
    - `refactor/[description]` - Code restructuring without behavioral changes (e.g., `refactor/pipeline-cleanup`)
    - `chore/[description]` - Dependency updates or build configuration (e.g., `chore/update-deps`)
- **Branch Lifecycle**:
  - Branches are created locally, pushed to GitHub, and merged only via Pull Requests.
  - Feature branches **must be deleted** immediately after merging into `main` to keep the repository clean.

---

## 2. Commit Message Conventions

We adhere to the **Conventional Commits** specification to maintain an explicit, searchable commit history and enable automated changelog generation.

### Message Format
```text
[type]: [short description in present imperative tense]

[optional body providing technical context and rationale]

[optional footer referencing issue numbers, e.g., Closes #123]
```

### Commit Types
- `feat`: A new feature or dataset processing capability added to the codebase.
- `fix`: A bug fix or correction to pipeline logic.
- `docs`: Documentation updates only (e.g., `README.md`, `WORKFLOW.md`).
- `refactor`: Code restructuring without modifying behavior or output.
- `test`: Adding missing unit tests or refactoring test suites.
- `chore`: Maintenance tasks such as dependency updates or configuration changes.

### Why This Matters
- Provides instant context for code reviews and git history inspection.
- Prevents vague commit messages (e.g., "fixed bug" or "updated code").
- Enables automated tools to generate release notes and semantic versioning.

---

## 3. Pull Request (PR) & Code Review Process

Pull Requests serve as mandatory quality gates before code reaches `main`.

- **PR Requirements**:
  - Every PR must have a clear, descriptive title explaining the high-level change.
  - PR description must follow the project template:
    - **Summary**: Concise overview of the purpose.
    - **What Changed**: Bulleted list of specific changes.
    - **Related Issues**: Keywords linking issues (e.g., `Closes #1`, `Fixes #2`).
    - **Testing**: Verification steps and test results.
- **Code Review Focus**:
  - **Correctness & Data Integrity**: Data schema validation, handling of missing/null values, and model outputs.
  - **Code Clarity**: Readability, modular structure, and compliance with project conventions.
  - **Test Coverage**: Appropriate unit/integration tests included.
  - **Commit Quality**: Commit messages reviewed for clarity and adherence to conventional format.
- **Approval Gate**:
  - PRs require **at least one peer approval** before merging.
  - Authors must address all feedback and request re-review before merging.

---

## 4. GitHub Issue Tracking & Sprint Management

All work items must originate from a tracked GitHub Issue to maintain complete traceability.

- **Issue Creation Rules**:
  - Every feature, bug fix, or task must have a corresponding GitHub Issue created prior to starting work.
  - **Title**: Action-oriented and specific (e.g., `feat: Ingest customer transaction data into pipeline`).
  - **Description**: Explains the background, technical rationale, and definition of "Done".
  - **Labels**: Categorize work type and domain (e.g., `feature`, `documentation`, `bug`, `data-pipeline`).
  - **Assignee**: Assigned to the team member responsible for execution.
- **Issue Lifecycle**:
  - Issues are linked to Pull Requests via closing keywords (`Closes #<issue-number>`).
  - When the Pull Request is merged into `main`, GitHub automatically closes the corresponding issue, maintaining a permanent audit trail.
