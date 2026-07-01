# Nile Key Patch Workflow

## Stage 1: Planning

- Understand the Patch requirements and objectives.
- Determine dependencies on other systems or components.
- Verify prerequisites are available and accessible.
- Produce a detailed execution plan with scope boundaries.

↓

## Stage 2: Investigation

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

- Modify only files inside current Patch scope.
- Preserve backward compatibility at all times.
- Avoid unrelated edits or opportunistic changes.

↓

## Stage 5: Verification

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

## Common Failure Patterns

- Router ahead of schema
- Schema ahead of router
- Legacy compatibility breaking
- Nullable mismatch
- Wrong DELETE assumption
- Stale backend process
- Wrong database connection