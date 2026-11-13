---
description: Verify the current project state passes runtime checks before completion is declared.
agent: code
---

# Runtime Verification Workflow

## Purpose
Verify that the current project state passes all runtime checks before declaring completion. This workflow never commits.

## Commands (verified in this repository)

Run each from the directory that owns it.

| Check | Command | Scope | Evidence |
|---|---|---|---|
| Lint | `npm run lint` | `frontend/` | `frontend/package.json` → `"lint": "eslint ."` |
| Type check + build | `npm run build` | `frontend/` | `frontend/package.json` → `"build": "tsc -b && vite build"` |
| Frontend tests | `npm test` | `frontend/` | `frontend/package.json` → `"test": "vitest run"` |
| Backend tests | `pytest` | `backend/` | `backend/pytest.ini` → `testpaths = tests`, `pythonpath = .` |

`frontend/package.json` has no dedicated type-checking script. Use `npm run build`, which runs the TypeScript build (`tsc -b`) before bundling.
There is **no** root-level `package.json`; `npm` commands must be run inside `frontend/`.

## Steps
1. Identify which checks apply to the current change.
2. Run lint: `npm run lint` (in `frontend/`).
3. Run type check and build: `npm run build` (in `frontend/`).
4. Run frontend tests: `npm test` (in `frontend/`).
5. Run backend tests: `pytest` (in `backend/`).
6. Run runtime checks if applicable (API endpoint, dev server, container health).
7. Record all verification results.
8. Fail if any applicable verification step fails.
9. Report the result. Do not commit.

## Output
- Verification checklist
- Pass/fail status for each check
- Logs and error output if any
- Explicit statement that no commit was made