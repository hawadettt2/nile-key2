# Nile Key — Project Execution Rules

## 1. Purpose
This document defines the mandatory workflow for every future task, bug fix, enhancement, and project closure within the Nile Key project. It serves as the permanent execution constitution and must be followed without exception.

## 2. Guiding Principles
- Evidence-based decision making in all technical activities.
- No assumptions without verification.
- Single-responsibility changes only.
- User-observed behavior always overrides assumptions or incomplete evidence.
- No task may be closed before Manual UAT.
- No project closure without Project Owner acceptance.

## 3. Roles and Responsibilities

### 3.1 Architect
- Defines and maintains technical standards and design architecture.
- Approves architectural changes.
- Reviews and validates technical evidence.
- Ensures adherence to the project's architecture charter.

### 3.2 Project Manager
- Coordinates work packages and task sequencing.
- Enforces execution gates.
- Tracks progress and reports status.
- Ensures resources are allocated appropriately.

### 3.3 Project Owner
- Holds final acceptance authority.
- Validates business requirements.
- Approves project closure.
- Has authority to reject incomplete work regardless of automated test results.
- May reopen any Work Package, UAT item, or project closure whenever new objective evidence demonstrates that the documented acceptance criteria have not actually been satisfied.

## 4. Execution Authority

### 4.1 Architect
- Technical decisions and standards approval.
- Design change authorization.
- Evidence validation and technical review.

### 4.2 Project Manager
- Work package prioritization and scheduling.
- Resource allocation.
- Gate compliance oversight and escalation.

### 4.3 Project Owner
- Final acceptance of deliverables.
- Business requirement validation.
- Project closure authorization.

### 4.4 Development Agent (Kilo Code)
- Implementation within defined scope only.
- Test execution and verification.
- Evidence collection and reporting.
- No architectural changes without Architect approval.

**Additional mandatory restrictions:**
- Must not create commits unless explicitly authorized by the Project Owner.
- Must not close Work Packages.
- Must not declare work complete.
- Must stop after implementation and reporting, awaiting review.
- Must escalate any newly discovered issue instead of fixing it automatically.
- Must provide objective evidence for every implementation, test result, and technical conclusion before requesting review.

## 5. Evidence-Based Development
Every technical conclusion must be supported by objective evidence. Never assume what can be verified.

Permitted evidence sources include, but are not limited to:
- Backend logs
- API responses (request/response payloads and status codes)
- Browser Network tab data
- Console output
- Git diff
- Git history (commits, tags, baselines)
- Test results
- Screenshots (when appropriate)

Conclusions without supporting evidence are not valid and must not be used as the basis for decisions, closures, or acceptance.

## 6. Root Cause Analysis Standard
Every RCA must answer the following questions:
1. What happened?
2. Why did it happen?
3. Why was it not detected earlier?
4. Why is this the actual root cause?
5. What evidence proves it?

An RCA is not complete until all five questions are answered with supporting evidence.

## 7. Change Scope Policy
Every change must have a single responsibility. Do not mix unrelated bug fixes, refactoring, or new features in one implementation. Each change must address exactly one defect, one task, or one enhancement. Mixing scopes is prohibited.

## 8. Regression Policy
Every fix must be verified by:
1. Original failing scenario
2. Adjacent scenarios
3. Potentially affected functionality

All three verification levels must pass before the fix is considered complete.

## 9. Baseline Policy
Before classifying a bug as a Regression:
1. Compare against the latest approved baseline.
2. Determine whether the behavior already existed in the baseline.
3. Document the evidence supporting the classification.

A bug may only be classified as a Regression when there is evidence that it did not exist in the approved baseline.

## 10. Decision Gates
Mandatory execution gates that cannot be skipped:

- **Gate 1 → Implementation Complete**: Code implementation is finished and ready for review. No commit yet.
- **Gate 2 → Code Review Passed**: Code review is completed and approved.
- **Gate 3 → Automated Tests Passed**: All automated tests pass.
- **Gate 4 → Manual UAT Passed**: Manual UAT is completed successfully per the UAT checklist.
- **Gate 5 → Project Owner Acceptance**: Project Owner formally accepts the deliverable.
- **Gate 6 → Authorized Git Commit**: Changes are committed only after explicit authorization from the Project Owner.
- **Gate 7 → Work Package Closed**: Work package is formally closed after all gates are satisfied.

No Work Package may be closed before all seven gates are satisfied.

## 11. Baseline Creation Policy
A baseline is an artifact produced after successful closure of a Work Package, milestone, or project.

A new approved baseline must be created after successful closure and must become the official reference for:
- Regression analysis
- Future change evaluation
- Project history

The Baseline Creation Policy is governance, not an execution gate.

## 12. Baseline Protection Policy
Approved baselines are immutable.

Once a baseline has been approved, it must never be modified.
Any future work shall begin as a new Work Package and produce a new approved baseline.

## 13. Project Execution Workflow
The mandatory execution lifecycle, in order:

Task
↓
Implementation
↓
Code Review
↓
Automated Tests
↓
Manual UAT
↓
Project Owner Acceptance
↓
Authorized Git Commit
↓
Work Package Closed
↓
Project Closure (when applicable)

## 14. Bug Handling Lifecycle
Every bug must follow this lifecycle:
1. Reproduce
2. Root Cause Analysis
3. Minimal Fix
4. Verify the Fix
5. Regression Check
6. Documentation
7. Close

Skipping any step is prohibited.

## 15. Work Package Completion Criteria
A Work Package is considered complete only when:
- All implementation is finished.
- All automated tests pass.
- Manual UAT is completed and passed.
- All evidence is documented.
- Project Owner acceptance is recorded.
- Git working tree is clean for the Work Package scope.
- Work Package is formally closed.

## 16. UAT Completion Criteria
UAT is not complete unless:
- All UAT checklist items are executed and marked as passed.
- Any failed item is resolved and retested.
- Evidence of each test result is retained.
- PROJECT_EXECUTION_RULES.md is satisfied.
- Project Owner acceptance is obtained.
- Manual UAT is executed by the Project Owner or under the direct observation of the Project Owner.

No UAT may be considered complete if any execution rule is violated. Successful automated execution never replaces Manual UAT.

## 17. Project Closure Criteria
Project closure requires ALL of the following:
- All Work Packages closed.
- No Critical defects.
- No High severity defects.
- Manual UAT completed successfully.
- Project Owner approval obtained.
- Documentation updated.
- Git working tree clean.
- Final approved baseline created, tagged, and documented.

Project closure is official only after the Project Owner signs the closure certificate.

## 18. Definition of Done
A task, bug fix, or work package is Done only when:
- Implementation is complete.
- All relevant automated tests pass.
- Manual UAT passes for the affected area.
- Evidence is documented.
- Code review is approved.
- Changes are approved and, when explicitly authorized by the Project Owner, committed.
- Related work package is closed per Gate 7.

## 19. Prohibited Practices
The following practices are strictly prohibited:
- Closing a task before Manual UAT.
- Closing multiple unrelated defects in one change.
- Implementing changes before confirming the root cause.
- Declaring the project complete without Project Owner acceptance.
- Skipping any Decision Gate.
- Treating automated test success as a substitute for Manual UAT when Manual UAT is required.
- Closing a UAT checklist item without objective evidence.

## 20. Lessons Learned
The Lessons Learned section is a living governance record.

- New lessons may be added whenever a significant project lesson is formally approved.
- Existing lessons are not removed without Project Owner approval.

Current lessons:

### Primary Rule
Never declare a project complete before executing Manual UAT as an actual end user.

### Supporting Rules
- Never assume something that can be verified.
- User-observed behavior always overrides assumptions or incomplete evidence.
- A passing automated test does not prove the user workflow is functional.
- Session restoration must be verified through actual user behavior, not only code inspection.
- Base URL and configuration values must be sanitized before use.
- Temporary debugging logging must be removed before any commit.

## 21. Amendment Policy
This document is the governing execution constitution of the Nile Key project.

Any modification to this document requires:
1. A documented rationale.
2. Explicit Project Owner approval.
3. Review for consistency with the Project Plan.
4. Documentation of the revision in the document history.

No execution rule may be changed implicitly through discussion, implementation, commit history, or undocumented agreement.

## 22. Governing Principle
> "In case of any conflict between successful automated verification and actual user behavior, actual user behavior always takes precedence."

## 23. Governance Hierarchy
Project governance documents have the following order of authority:

1. Project Plan (defines project scope and objectives)
2. PROJECT_EXECUTION_RULES.md (defines execution governance and acceptance rules)
3. UAT_CHECKLIST.md (defines operational user acceptance verification)

If a conflict exists, the higher-level document prevails.
