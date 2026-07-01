# Kilo Environment

- **Kilo Version**: Latest
- **Provider**: poolside
- **Default Model**: poolside/malibu-2:free
- **Small Model**: poolside/malibu-2:free
- **Sub-Agent Model**: poolside/malibu-2:free
- **Auto Completion Model**: poolside/malibu-2:free
- **Mode Overrides**: Code / Ask / Debug / Plan / Orchestrator

---

# Required Rule Files

Current:

- NILE_KEY_RULES.md
- PATCH_WORKFLOW.md
- SESSION_STATE.md

---

# VS Code

- **Required Extensions**: Python, ESLint, Tailwind CSS, GitLens
- **Workspace Trust**: Enabled
- **Recommended Settings**: Format on save, ESLint auto-fix on save

---

# Backend

- **Python Version**: 3.11+
- **Virtual Environment**: backend/.venv
- **Startup Command**: uvicorn main:app --reload
- **Database Location**: SQLite at backend/nile_key.db

---

# Frontend

- **Package Manager**: npm
- **Startup Command**: npm run dev

---

# Recovery Procedure

If VS Code or Kilo is reinstalled:

1. Install Kilo.
2. Open the repository.
3. Verify the Provider.
4. Verify the Models.
5. Verify the Rules.
6. Start Backend.
7. Resume from SESSION_STATE.md.

---

# Engineering Notes

- Never rely on memory.
- Repository is the single source of truth.
- Keep this document updated whenever environment settings change.