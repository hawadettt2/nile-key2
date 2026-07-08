# Project Stabilization — Execution Plan

## Context
Phase 5 (Frontend Pages Audit) is CERTIFIED (defect F-P5-01 fixed in commit `5b132a6`). The working tree currently carries unrelated pending changes and the branch topology needs reconciliation so the repository is clean and `main` becomes the authoritative branch for Phase 6.

This is an administrative stabilization phase, NOT development and NOT an audit. This plan is READ-ONLY analysis + an execution sequence for a separate implementation session. Nothing in this plan is to be executed now.

## 1- Current Git Status (read-only capture)

- **Current branch**: `wp-13`
- **Ahead of origin/wp-13 by 3 commits** (local `wp-13` = `5b132a6`, `origin/wp-13` = `5764a92`).
- **Modified (unstaged)**:
  - `CURRENT_STATUS.md` (5 insertions, 3 deletions)
  - `frontend/package-lock.json` (187 insertions)
- **Untracked**:
  - `.kilo/kilo.jsonc`
  - `.kilo/plans/1783355240374-manual-uat-execution-package.md`
  - `.kilo/plans/1783388583927-project-closure-recovery-plan-v1.2.md`
  - `.kilo/plans/phase5-frontend-pages-audit.md`
  - `docs/PROJECT_EXECUTION_RULES.md`
  - `docs/UAT_CHECKLIST.md`
  - `tools/` (contains `NileKeyToolkit.ps1`, `start-all.bat`, `start-backend.bat`, `start-frontend.bat`, `stop-all.bat`, `nile-key.log`)

## 2- Pending Files Analysis (fate per file)

| File | State | Recommended Fate | Rationale (evidence only) |
|------|-------|------------------|---------------------------|
| `CURRENT_STATUS.md` | modified | KEEP + COMMIT | Project status doc; real content change (5/3). Excluded from F-P5-01 commit intentionally. Preserve. |
| `frontend/package-lock.json` | modified +187 | KEEP + COMMIT | npm lockfile drift; legitimate artifact. Commit to avoid future install drift. |
| `.kilo/kilo.jsonc` | untracked | DECISION: keep+commit OR gitignore | Local Kilo config. If machine-specific, add to `.gitignore`; otherwise commit. Flag for user choice. |
| `.kilo/plans/phase5-frontend-pages-audit.md` | untracked | KEEP + COMMIT | Phase 5 evidence/plan. Audit record. |
| `.kilo/plans/1783355240374-manual-uat-execution-package.md` | untracked | KEEP + COMMIT or gitignore | Historical plan artifact. Minor. Recommend commit as record or gitignore `.kilo/plans/`. |
| `.kilo/plans/1783388583927-project-closure-recovery-plan-v1.2.md` | untracked | KEEP + COMMIT or gitignore | Historical plan artifact. Same as above. |
| `docs/PROJECT_EXECUTION_RULES.md` | untracked | KEEP + COMMIT | Project rules documentation. |
| `docs/UAT_CHECKLIST.md` | untracked | KEEP + COMMIT | UAT documentation. |
| `tools/*.ps1`, `tools/*.bat` | untracked | KEEP + COMMIT | Useful startup scripts; legitimate repo assets. |
| `tools/nile-key.log` | untracked (inside tools/) | EXCLUDE (gitignore) or DELETE | Transient runtime log; must NOT be committed. Add `tools/*.log` (or `tools/nile-key.log`) to `.gitignore`, or delete the file. |

Proposed `.gitignore` additions (only if adopting the "ignore local config/logs" path):
```
.kilo/kilo.jsonc
tools/*.log
```
(Optional) `tools/` transient logs only; scripts themselves remain tracked.

## 3- Branch Analysis

| Branch | Tip | Relation |
|--------|-----|----------|
| `main` (local) | `a83228b` | Equals `origin/main` (`a83228b`) — fully in sync. |
| `origin/main` | `a83228b` | Authoritative remote main. |
| `wp-13` (local) | `5b132a6` | 3 commits ahead of `main`; contains `main` history fully (merge-base `wp-13` ↔ `main` = `a83228b`). |
| `origin/wp-13` | `5764a92` | 3 commits BEHIND local `wp-13` (merge-base = `5764a92`). Safe to fast-forward on push. |
| `incongruous-table` (local) | `f06f300` | Unrelated branch. |
| `origin/update` | `f06f300` | Same tip as `incongruous-table`; unrelated to wp-13/main. Leave untouched. |

Commit graph (relevant): `main`(a83228b) → 5764a92 → ec4958d → 2cd24b0 → 5b132a6(wp-13 HEAD). `main` is an ancestor of `wp-13`.

## 4- Merge Readiness

- `wp-13` → `main` is a **fast-forward** merge (no divergent commits on `main`; `main` is fully contained in `wp-13`). No conflict expected.
- `origin/wp-13` is behind local by 3 commits only; pushing `wp-13` is a clean fast-forward (no remote divergence).
- The 3 pending working-tree changes (section 2) are NOT yet committed, so they are independent of the merge and must be resolved on `wp-13` BEFORE merging into `main` to avoid carrying uncommitted state across the checkout/merge.

## 5- Execution Plan (separate implementation session — DO NOT RUN NOW)

1. **Resolve pending files on `wp-13`** (current branch):
   - Decide `.kilo/kilo.jsonc` / `.kilo/plans/*` fate per section 2.
   - Add `tools/*.log` (or `nile-key.log`) to `.gitignore`; optionally remove the log file.
   - Stage and commit the approved files in one or more commits, e.g.:
     - `chore: capture project status and lockfile updates`
     - `docs: add UAT checklist and execution rules`
     - `chore: add tooling scripts`
     - (phase5 audit plan commit if decided to keep)
   - Ensure `CURRENT_STATUS.md` and `frontend/package-lock.json` are committed (no data loss).
2. **Verify `wp-13` is clean**: `git status` shows nothing pending.
3. **Switch to `main`**: `git checkout main`.
4. **Merge `wp-13` into `main`**: `git merge wp-13` (fast-forward). No conflicts expected.
5. **Verify `main`**: `git log` shows `5b132a6` as HEAD; `git status` clean.
6. **Push `main`**: `git push origin main`.
7. **(Optional) Push and retire `wp-13`**: `git push origin wp-13` (fast-forward) then `git branch -d wp-13` and `git push origin --delete wp-13` once main is confirmed authoritative.
8. **Leave `incongruous-table` / `origin/update` untouched** (out of scope).

## 6- Risk Assessment

- **Uncommitted state carried across checkout**: If step 1 is skipped, `git checkout main` could fail or carry modified `CURRENT_STATUS.md`/`package-lock.json`. Mitigation: commit on `wp-13` first.
- **`tools/nile-key.log` committed by mistake**: transient log leaks runtime data. Mitigation: gitignore/delete before commit.
- **`.kilo/kilo.jsonc` machine-specific**: may contain local paths. Mitigation: prefer gitignore unless confirmed shared.
- **`origin/wp-13` divergence**: currently only behind (safe fast-forward). If a remote push arrives between now and execution, push may be rejected — re-verify `git fetch` then re-assess. No evidence of such divergence now.
- **Data loss**: None, provided all pending files are committed before merge and `main` fast-forwards. No reset/rebase/force used.

## 7- Final Recommendation

Execute the plan in section 5 in a dedicated implementation session. Result target:
- Working tree clean.
- `main` = `5b132a6` (authoritative, in sync with `origin/main`).
- `wp-13` retired after merge.
- All pending files preserved (committed or intentionally gitignored).
- No data loss; no use of reset/rebase/force.

**Project Stabilization = READY FOR EXECUTION** (pending user approval of the plan and the two flagged decision points in section 2: `.kilo/kilo.jsonc` and `.kilo/plans/*` fate).
