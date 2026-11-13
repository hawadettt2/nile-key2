---
description: Optional post-completion readiness check. Runs only on explicit user request.
agent: code
---

# Commit Verification Workflow

## Purpose
Optional post-completion check. Runs only on explicit user request. This workflow never commits.

## When to use
After a task is complete and the user explicitly asks for a commit-readiness check. It is not part of the standard workflow chain.

## Steps
1. Review the staged changes
2. Confirm changes align with a single purpose
3. Verify no unrelated changes are included
4. Confirm runtime verification passed
5. Verify commit message follows conventions
6. Report readiness; do not commit without explicit user request

## Output
- Commit message
- Change summary
- Verification confirmation
- Explicit statement that no commit was made