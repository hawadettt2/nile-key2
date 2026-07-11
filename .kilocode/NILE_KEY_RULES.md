# Nile Key Architecture Constitution

## 1. Project Mission
Deliver secure, reliable, and maintainable key management solutions with uncompromising data integrity and backward compatibility.

## 2. General Principles
- Execute patch-by-patch only. Never modify files outside current patch scope.
- Never commit unless explicitly requested.
- Never refactor unrelated code.
- Never change API contract without explicit approval.
- Never change database schema without approval.
- Prefer router fixes over schema changes.
- Do not add features during repairs.
- Do not guess. Report uncertainty explicitly.
- Investigate before repairing. Find a single root cause.
- Apply the minimal safe fix. Verify every repair before declaring completion.

## 3. Architecture Rules
- Maintain clean separation between presentation, business logic, and data layers.
- Ensure all components follow single responsibility principle.
- Keep changes scoped to the minimum necessary for the fix.
- Preserve existing module boundaries and interfaces.

## 4. Patch Rules
- Each patch must address exactly one issue.
- No patch may include changes outside its defined scope.
- All patches must be tested and verified independently.
- Document the root cause in each patch.

## 5. Investigation Rules
- Identify and isolate the single root cause before proposing solutions.
- Analyze impact radius before making changes.
- Verify the problem exists through multiple data sources when possible.
- Document investigation findings before proceeding.

## 6. Minimal Safe Fix Policy
- The fix must address only the identified root cause.
- No optimizations, enhancements, or side fixes without explicit approval.
- Preserve all existing functionality and behavior.
- Verify the fix resolves the issue without introducing regressions.

## 7. Legacy Compatibility Policy
- Preserve backward compatibility for all existing APIs.
- Do not remove or modify existing interfaces without approval.
- Maintain support for legacy data formats and structures.

## 8. Database Rules
- Never modify database schema without explicit approval.
- Prefer router-level fixes over schema modifications.
- Preserve all existing data access patterns.
- Ensure database changes are backward compatible.

## 9. API Contract Rules
- API contracts are immutable without explicit approval.
- Never change endpoint signatures, request/response formats, or status codes.
- Maintain all existing API behaviors.
- Document any required API changes for future approval.

## 10. Git Rules
- Never commit unless explicitly requested by the user.
- Never push without explicit approval.
- Keep commits atomic and focused on single changes.
- Write clear, descriptive commit messages when committing.

## 11. Testing Rules
- Verify every repair before declaring completion.
- Test the specific issue fixed.
- Ensure no regression in existing functionality.
- Do not modify tests without explicit approval.

## 12. Communication Rules
- Report uncertainty and blockers explicitly.
- Acknowledge when investigation scope changes.
- Confirm understanding before making changes.
- Document rationale for all architectural decisions.

## 13. Forbidden Actions
- Do not add new features during bug fixes.
- Do not refactor code outside the patch scope.
- Do not modify configuration files without justification.
- Do not remove or rename existing files.
- Do not introduce new dependencies without approval.
- Do not make assumptions about undocumented behavior.

## 14. Completion Checklist
- [ ] Root cause identified and documented
- [ ] Minimal fix applied within patch scope
- [ ] Fix verified to resolve the specific issue
- [ ] No regression in existing functionality
- [ ] Backward compatibility preserved
- [ ] User explicitly requested commit (if applicable)

## 15. Established Project Patterns
- Follow existing naming conventions for functions, classes, and variables.
- Reuse existing utilities and helper functions.
- Mirror the structure of similar components when adding new code.
- Maintain consistency with established error handling patterns.

## 16. Root Cause Policy
- Investigate systematically from symptoms to source.
- Validate root cause with at least two independent observations.
- Confirm the fix addresses the root cause, not symptoms.
- Document the causal chain in investigation notes.

## 17. Repair Workflow
1. Investigate and identify root cause
2. Propose minimal fix within patch scope
3. Implement the fix
4. Verify fix resolves the issue
5. Check for regressions
6. Report completion with verification evidence

## 18. Legacy Compatibility Priority
- Backward compatibility takes precedence over code consistency.
- Preserve legacy bugs if fixing them would break existing users.
- Maintain deprecated code paths until approved for removal.
- Document legacy behavior for future reference.

## 19. Database Investigation
- Examine all existing queries and migrations before schema changes.
- Identify data dependencies across the codebase.
- Verify data integrity impact of any proposed change.
- Review database access patterns in related components.

## 20. Delete Policy
- Do not delete files, tables, or code without explicit approval.
- Deprecate first, delete later only with confirmation.
- Archive configurations before removing them.
- Maintain deletion logs for audit purposes.

## 21. API Contract Priority
- Existing API contracts are unchangeable without approval.
- New endpoints require explicit design review.
- Version all public APIs.
- Document breaking changes with migration path.

## 22. AI Behavior
- Never assume undocumented behavior.
- Ask for clarification on ambiguous requirements.
- Report confidence levels for all assertions.
- Stop and investigate when encountering unexpected patterns.

## 23. Final Completion Rule
- No task is complete until the user explicitly approves completion.
- All verifications must pass before completion declaration.
- Uncertainty must be reported before declaring completion.

## 24. Official Mode Selection
- Before any future task: do not assume the operating Mode.
- If operating modes are documented inside the project, follow those documents.
- If operating modes are not documented inside the project:
  - Do not assume any Mode.
  - Identify the official Kilo Code mode appropriate and supported for this specific task.
  - State before execution begins:
    1. The official Mode name.
    2. The reason it was chosen.

## 25. Automatic Resume
- If a task is interrupted for any reason (session loss, restart, disconnect, context exhaustion, or any unintended stop):
  - Resume from the last confirmed checkpoint.
  - Do not restart from zero.
  - Do not redo completed work.
  - Do not skip any step.
  - Continue automatically until the entire task is complete.
  - Maintain the same methodology: Evidence First, no assumptions, stop only at approval points or evidence conflicts.