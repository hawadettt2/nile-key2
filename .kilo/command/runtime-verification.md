# Runtime Verification Workflow

## Purpose
Verify that the current project state passes all runtime checks before any commit.

## Steps
1. Identify verification requirements for the current change
2. Run linting: `npm run lint` or equivalent
3. Run type checking: `npm run typecheck` or equivalent
4. Run tests: `npm test` or equivalent
5. Run runtime checks if applicable
6. Record all verification results
7. Fail if any verification step fails

## Output
- Verification checklist
- Pass/fail status for each check
- Logs and error output if any
