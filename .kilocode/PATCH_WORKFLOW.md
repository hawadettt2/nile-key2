# Nile Key Patch Workflow

## Stage Ownership

Each stage is owned by a command, an approval gate, or manual work:

| Stage | Owner |
|---|---|
| Planning | Manual |
| Investigation | `/forensic-audit` |
| Repair Decision | Project owner approval |
| Repair | `/incident-remediation` |
| Verification | `/runtime-verification` |
| Completion | Closure report + project owner approval (no commit) |

## Stage 1: Planning

- Understand the Patch requirements and objectives.
- Determine dependencies on other systems or components.
- Verify prerequisites are available and accessible.
- Produce a detailed execution plan with scope boundaries.

↓

## Stage 2: Investigation

Owned by `/forensic-audit`.

- Inspect router endpoints and request handling.
- Inspect schema definitions and type constraints.
- Inspect database structures and relationships.
- Inspect migrations and historical changes.
- Identify exactly one root cause for the issue.

↓

## Stage 3: Repair Decision

- Select the minimal safe fix that addresses the root cause.
- Explain the rationale for the chosen approach.
- Wait for approval if architecture changes are required.

↓

## Stage 4: Repair

Owned by `/incident-remediation`.

- Modify only files inside current Patch scope.
- Preserve backward compatibility at all times.
- Avoid unrelated edits or opportunistic changes.

↓

## Stage 5: Verification

Owned by `/runtime-verification`.

- Execute endpoint verification for affected routes.
- Compare expected vs actual behavior and responses.
- Detect any regressions in existing functionality.

↓

## Stage 6: Completion

Patch is COMPLETE only when:

- Root cause removed
- Tests pass
- No regressions detected
- API contract preserved
- Compatibility preserved
- Project owner has approved closure

**No commit is performed at Completion.** Closing a patch means the work is verified and accepted, not committed. Never commit unless the project owner explicitly asks (`.kilocode/NILE_KEY_RULES.md`, section 10).

## Optional Post-Completion: Commit Readiness

`/commit-verification` is an **optional** check that runs **only** after Completion and **only** on explicit user request. It is not part of the standard chain, and it reports readiness rather than committing.

## Common Failure Patterns

- Router ahead of schema
- Schema ahead of router
- Legacy compatibility breaking
- Nullable mismatch
- Wrong DELETE assumption
- Stale backend process
- Wrong database connection