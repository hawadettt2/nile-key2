# Nile Key — Forensic Repository Cleanup Implementation Plan

## Governing Principle

> **Project Safety > File Count Reduction**

No file is deleted solely because it is:
- Ignored
- Old
- Large
- Appears temporary
- Can be regenerated

Rule:

> **Evidence → Verification → Explicit Candidate List → Approval → Deletion**

---

## Baseline (Phase 0)

| Metric | Value |
|--------|-------|
| Current branch | `main` |
| Canonical branch | `main` |
| Working Tree | CLEAN |
| Git HEAD | `a8f179578d1f1f3113f1d64a4492ed76dbc5759c` |
| Total commits | 232 |
| Tracked files | 739 |
| Ignored files | ~37,815 |
| Total local files | 76,353 |
| Repo size | 1.27 GB |

Exit criteria: Baseline documented + Working Tree CLEAN. **Status: MET.**

Active context relevant to cleanup:
- **Kilo process active**: `kilo.exe` (PID 8276) running from VS Code extension.
- **Registered worktrees**: 6 active worktrees under `.kilo/worktrees/`.
- **Runtime database**: `backend/nile_key.db` (1,052,672 bytes) — active.
- **Root database**: `nile_key.db` (65,536 bytes) — active.

---

## Phase 1 — Forensic Discovery

Discover, do not delete.

Search for:
- caches
- logs
- test outputs
- build outputs
- temporary databases
- generated metadata
- local package dependencies
- Kilo worktrees
- Kilo local dependencies

Output: candidate list with metadata per item.

> **Discovery ≠ Deletion**

---

## Phase 2 — Verification of Candidates

Each candidate is verified across axes:

### A. Git
Tracked / ignored / untracked.

### B. Reference
imports / scripts / config / tests / docs.

### C. Runtime
processes / ports / active DB / active tooling.

### D. Build
Does current workflow depend on it?

### E. Governance
Does it represent evidence or historical artifact?

### F. Reproducibility
Can it be safely regenerated?

If any axis is unclear:

> **UNKNOWN / DO NOT DELETE**

---

## Phase 3 — Deletion Manifest Review

Create explicit list:

> **VERIFIED DELETION MANIFEST**

Only paths classified as **VERIFIED TEMPORARY** enter the manifest.

Wildcard patterns are NOT deletion commands. They are discovery tools only.

Example flow:

> Discover → `/path/a`, `/path/b`, `/path/c`
> Verify → `/path/a`, `/path/c` only Temporary
> Delete → `/path/a` and `/path/c` only

No deletion happens before the manifest is complete and reviewed.

---

## Phase 4 — Lead Architect Authorization Boundary

This plan does not grant deletion authority.

After the **VERIFIED DELETION MANIFEST** is created:

> **Lead Architect Review**

Then only:

> **APPROVE BATCH A**

or:

> **REVISE / REJECT**

---

## Phase 5 — Batch A Execution

Executed only after separate authorization.

Rules:
- Delete ONLY paths in the Verified Deletion Manifest.
- No wildcard deletion.
- No tracked file deletion.
- No code modification.
- No governance modification.
- No `.env`.
- No active database.
- No active Kilo dependency.
- No active worktree.
- No Commit.
- No Push.

---

## Phase 6 — Post-Deletion Verification

Verify across three independent layers.

### 6.1 Git State
- `git status` — CLEAN
- `git diff` — no output
- Tracked files unchanged

### 6.2 Filesystem State
- Verified candidates removed
- Protected assets remain
- No unexpected deletion

### 6.3 Runtime State
- Backend startup / import success
- Frontend build success
- Relevant tests pass
- Active configuration intact

Rule:

> **Git Clean ≠ Filesystem Clean ≠ Runtime Healthy**

If any layer fails:

> **STOP → REPORT → REVIEW**

Do not auto-fix. Do not delete additional files.

---

## Phase 7 — Tracked File Review

Separate phase from Batch A. No automatic deletion.

Decisions per file:

| Decision | Meaning |
|----------|---------|
| KEEP | Required, referenced, or governance-critical |
| ARCHIVE | Historical but must be preserved |
| DELETE | Obsolete with explicit evidence |
| UNKNOWN / DO NOT DELETE | Insufficient evidence; requires additional review |

Current tracked candidate decisions:

| File | Decision | Rationale |
|------|----------|-----------|
| `backend/uat_execution.py` | KEEP | Governance evidence of completed WP-42 UAT |
| `backend/uat_results.json` | KEEP | Governance evidence; referenced in plans |
| `openapi_current.json` | KEEP | Frontend `types:api` dependency; API contract |
| `.ai/architecture` | KEEP | Empty governance placeholder |
| `.ai/audit` | KEEP | Empty governance placeholder |
| `.ai/decisions` | KEEP | Empty governance placeholder |
| `.ai/memory` | KEEP | Empty governance placeholder |
| `.ai/reports` | KEEP | Empty governance placeholder |
| `.ai/reviews` | KEEP | Empty governance placeholder |
| `.ai/tasks` | KEEP | Empty governance placeholder |
| `frontend/vite.config.js` | UNKNOWN / DO NOT DELETE | Conflict in current plan; requires independent verification |

**No tracked deletions authorized in this plan revision.**

---

## Phase 8 — Git Persistence

Applies **only to tracked changes** if approved in a future plan revision.

- `git add` affected files
- Commit message: `chore(cleanup): <description>`
- Verify `git status` = CLEAN

**Not applicable to Batch A (local-only).**

---

## Phase 9 — Final Hygiene Verification

| Layer | Check | Expected |
|-------|-------|----------|
| Git | No unintended changes | CLEAN |
| Filesystem | Temporary verified artifacts removed | CLEAN |
| Filesystem | Protected assets remain | PRESENT |
| Runtime | No regression | HEALTHY |
| Governance | No evidence loss | INTACT |
| Architecture | No unintended changes | INTACT |

---

## Protected Assets

Never deleted in Batch A or any batch without explicit independent authorization:

- `.env`
- Active `nile_key.db`
- Active databases
- Source code
- Tests
- `.kilo` governance assets
- `.kilocode` governance assets
- `PLAN.md`
- `CURRENT_STATUS.md`
- `TECH_DEBT.md`
- `CHANGELOG.md`
- `README.md`
- `docs/`
- Docker configuration
- Dependency manifests
- Active Kilo dependencies
- Active worktrees
- Any UNKNOWN artifact

---

## Stop Conditions

HALT immediately if:
- Unknown reference discovered
- Dynamic loading or runtime dependency on deletion candidate found
- Test or build failure
- Governance reference found for planned deletion
- File ownership ambiguity
- Active process conflict
- Worktree with unsaved work detected

When stopped: **REPORT → REVIEW → Do not proceed without evidence.**

---

## Success Criteria

This plan is final only when:

1. No wildcard direct deletion.
2. No deletion before Verified Manifest.
3. `vite.config.js` is not a Batch A candidate.
4. Databases are individually verified.
5. `.kilo/worktrees` are inspected before any deletion.
6. Kilo `node_modules` are not deleted while in use.
7. Git / Filesystem / Runtime layers are separate.
8. Batch A is Local Only.
9. No tracked deletion is currently authorized.
10. Stop condition exists for any anomaly.

---

## Authorization Boundary

> **PLAN ONLY**

This revision does not authorize:
- File deletion
- Code modification
- Git persistence

Next step after plan update:

> **Lead Architect Review of Revised Cleanup Plan**

No execution until review is complete and separate authorization is granted.
