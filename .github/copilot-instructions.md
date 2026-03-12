# Copilot Instructions for this Repository

These instructions define how GitHub Copilot should assist in this project.

## Language and style

- Always write **code, comments, docstrings, and commit messages in English**.
- Keep explanations concise but complete.
- Use clear, beginner-friendly wording when explaining concepts.
- Follow **PEP 8** style guidelines for Python code.

## Working approach

- Before executing significant changes, propose a short plan first.
- Present 1–3 options when there is a design choice, and recommend one.
- Wait for confirmation before applying major refactors or multi-file changes.
- If the user explicitly asks to execute immediately, proceed directly.
- Prefer reusing existing code and abstractions; avoid duplicating logic across scripts or notebooks.

## Python environment and tooling

- Use **uv** as the default tool for Python project setup, environment management, and dependency installation.
- Prefer `uv sync`, `uv add`, and `uv run` workflows over alternative Python package managers unless explicitly requested.

## Explanations and teaching mode

- Always explain the theory behind the change:
  - What problem is being solved.
  - Why this approach is chosen.
  - Trade-offs and alternatives.
- Explain tests step by step when adding or modifying them.
- When introducing tools/framework features, include links to official documentation when useful.

## Testing and commits

- Work incrementally, script by script or module by module.
- Prefer focused test runs before full-suite runs.
- Keep commits atomic and scoped to one logical change.
- Do not mix documentation, refactor, and test additions in a single commit unless requested.

## Safety and scope

- Do not modify unrelated files.
- Ask before destructive operations.
- Preserve existing architecture unless a change is requested.
