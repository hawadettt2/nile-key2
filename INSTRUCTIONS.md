# Kilo Operating Framework

## Official Project Rules

This document defines the official operating framework for the Kilo project. All work MUST comply with these rules.

### 1. Forensic Audit Methodology
All project work MUST follow the Forensic Audit methodology. Every change must be traceable, justified, and evidence-based. No modification may proceed without a clear audit trail.

### 2. Evidence First
No action, fix, or change may proceed without verifiable evidence. Evidence includes: logs, test results, code inspection, reproduction steps, runtime verification output, and documented observations. Unverified assumptions are not acceptable.

### 3. Minimal Fix
Changes must be minimal and targeted to the specific incident. Do not refactor, clean up, or modify code outside the scope of the current incident unless explicitly required by the fix. Scope expansion is prohibited.

### 4. One Incident at a Time
Work on exactly one incident at a time. Complete the current incident fully before beginning another. Parallel incident work is prohibited.

### 5. Runtime Verification Before Commit
Runtime verification MUST be completed and pass before any commit is made. Verification includes: test execution, linting, type checking, and runtime checks. Commits without passing verification are prohibited.

### 6. One Commit, One Purpose
Each commit must serve exactly one purpose. Do not bundle multiple incidents or unrelated changes into a single commit. Commit messages must accurately reflect the change.

### 7. Closed Incidents Stay Closed
Closed incidents may not be reopened without new, verifiable evidence that was not available at the time of closure. Reopening without new evidence is prohibited.
