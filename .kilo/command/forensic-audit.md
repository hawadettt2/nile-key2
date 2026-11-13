---
description: Execute a complete evidence-based audit of the project state before any change.
agent: forensic-audit
---

# Forensic Audit Workflow

## Purpose
Execute a complete forensic audit of the project state before any change.

## Steps
1. Load the `forensic-audit` agent
2. Read .kilocode/NILE_KEY_RULES.md and project rules
3. Identify the incident or area under audit
4. Gather all relevant evidence: logs, tests, code, runtime output
5. Document the current state with evidence references
6. Identify root cause and affected components
7. Produce audit report with evidence citations
8. Do not modify project files during audit

## Output
- Audit report
- Evidence references
- Root cause analysis
- Affected components list