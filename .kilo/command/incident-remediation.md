---
description: Remediate a single incident with a minimal, targeted change after root cause is confirmed.
agent: incident-remediation
---

# Incident Remediation Workflow

## Purpose
Remediate a single incident with minimal, targeted changes. This workflow never commits.

## Steps
1. Load the `incident-remediation` agent
2. Verify incident has new evidence
3. Confirm incident is not already resolved
4. Isolate the minimal scope of change
5. Implement the minimal fix
6. Run runtime verification
7. Report completion with verification evidence
8. Document resolution

## Output
- Incident record
- Change diff
- Verification results
- Explicit statement that no commit was made