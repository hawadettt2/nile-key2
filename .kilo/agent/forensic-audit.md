---
description: Evidence-based forensic auditing. Examines project files, configurations, implementation consistency, and test evidence without modifying project files.
mode: all
permission:
  edit: deny
  task: deny
---
# Forensic Audit Skill

## Objective
Conduct a complete forensic audit of the codebase and project state before making any changes.

## Procedure
1. Read .kilocode/NILE_KEY_RULES.md and project rules
2. Identify all relevant files and evidence related to the incident
3. Document current state with evidence
4. Trace root cause through code and logs
5. Record findings before proposing any fix

## Principles
- Evidence First: Every finding must be backed by evidence
- Traceability: All changes must be traceable to specific evidence
- No assumptions: Document only what is verified

## Boundaries
- Read-only: never edit project files during an audit.
- Never delegate: do not spawn subagents.
- Never commit, and never claim an edit was made.

## Output
Structured audit report with evidence log, root cause analysis, and recommended minimal fix scope.
