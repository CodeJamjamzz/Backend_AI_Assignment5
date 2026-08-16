# Project Commands Cheat Sheet

> **Important for AI Agents:** Always check this file before running commands or if a build/test/lint command fails.

## Setup & Dependencies
```bash
# Python setup
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# Install dependencies:
pip install -r requirements.txt

# Node.js setup (if applicable)
npm install
```

## Running the Application
```bash
# Start development server (e.g. FastAPI / Uvicorn)
uvicorn main:app --reload

# Start Node.js dev server (if applicable)
npm run dev
```

## Testing & Quality Assurance
```bash
# Run unit tests
pytest
# or
npm test

# Linting & Formatting
ruff check .
ruff format .
# or
npm run lint
npm run format
```
