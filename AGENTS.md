# Project Overview

Welcome to the project! This document establishes the foundational guidelines, context, and operational rules for AI agents and developers working in this repository.

## Project Context
- **Name:** Assignment 5 (Backend AI Engineering)
- **Purpose:** Backend engineering and AI service implementation / workflows.
- **Target Audience:** Developers, evaluators, and system integrators.

---

## Tech Stack
- **Language / Runtime:** Python / Node.js (Configure according to project requirements)
- **Frameworks:** FastAPI / Express / Modern Backend Frameworks
- **AI / ML Integration:** AI SDKs, LLM orchestration, or backend data pipelines
- **Testing & Tooling:** Pytest / Jest, ESLint / Ruff, Git

---

## Agent Operational Rules
1. **Context-First:** Before writing code, always check `docs/tasks/` for the active task brief and review relevant specs in `docs/specs/`.
2. **Strict Typing & Quality:** Write clean, modular, and strongly typed code. Avoid untyped placeholders (e.g., `any` or untyped `dict` where models can be defined).
3. **Preserve Integrity:** Never remove or overwrite existing documentation, comments, or docstrings unless explicitly instructed.
4. **Testing Required:** Add or update unit tests for any new features or bug fixes.
5. **Commands Reference:** If a command fails or you need instructions on how to build, test, or lint, check `docs/ai/commands.md`.

---

## Standard Workflow
1. **Plan:** Research the codebase and specify steps in `docs/plans/`.
2. **Implement:** Execute changes surgically according to the plan.
3. **Review & Test:** Run linters, type checks, and tests as defined in `docs/ai/commands.md`.
