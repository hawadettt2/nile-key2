الوثيقة الدستورية للمشروع
# Nile Key Project — Architecture Charter v1.0

**Status:** Official Engineering Constitution

**Authority:** Lead Software Architect

**Applies to:** Every AI Agent, Human Developer, Code Generator, and Automation Tool working on this repository.

---

# 1. Mission

Nile Key is developed as a production-grade software platform.

Every engineering decision must improve:

* Stability
* Correctness
* Maintainability
* Scalability
* Security
* Readability

Speed is never more important than correctness.

---

# 2. Repository Ownership

Treat this repository as a long-term production system.

Every file belongs to the architecture.

Every dependency must have a purpose.

Every module must have an owner.

No code is "temporary."

---

# 3. Source of Truth

The single authoritative source of truth is:

**Backend Domain Models + Pydantic Schemas + OpenAPI Contract**

Everything else must conform to this.

Priority order:

1. Backend Pydantic Schemas
2. FastAPI API Contract
3. Business Rules
4. Database Schema
5. Frontend Types
6. Documentation

Never reverse this order.

---

# 4. Architecture Philosophy

Always prefer:

Refactor > Rewrite

Simplify > Expand

Reuse > Duplicate

Remove > Add

Consistency > Cleverness

Correctness > Speed

Long-term maintainability > Short-term convenience

---

# 5. Working Model

Before changing any code:

Understand.

Investigate.

Map dependencies.

Estimate impact.

Only then modify.

Never begin coding immediately after reading a request.

---

# 6. Repository Exploration Rules

Before significant modifications:

* inspect the complete project
* inspect dependencies
* inspect imports
* inspect architecture
* inspect configuration
* inspect build process
* inspect deployment
* inspect security
* inspect API contracts
* inspect database model

Never assume.

Always verify.

---

# 7. Modification Policy

Every modification must answer:

Why does this problem exist?

What breaks if ignored?

Risk level?

Files affected?

Expected benefit?

Rollback strategy?

---

# 8. Coding Principles

Never duplicate logic.

Never create dead code.

Never introduce hidden side effects.

Prefer explicit behavior.

Prefer small functions.

Prefer isolated modules.

Prefer deterministic behavior.

---

# 9. Database Rules

Database follows Backend.

Backend never follows Database.

SQLite schema is an implementation detail.

Business model lives in Backend Schemas.

Migrations become the only legal way to evolve persistence after Phase 3.

---

# 10. API Rules

FastAPI is the public contract.

Routers must reflect business operations.

Responses must remain consistent.

Validation belongs in Pydantic.

Business logic does not belong inside routers.

---

# 11. Frontend Rules

Frontend consumes the API.

Frontend never defines business rules.

Frontend types should eventually be generated from OpenAPI.

Avoid duplicated interfaces.

Never silently ignore API errors.

---

# 12. Security Rules

Never hardcode secrets.

Never trust client input.

Validate every request.

Hash passwords using approved algorithms.

Avoid wildcard CORS in production.

Follow least-privilege principles.

---

# 13. Performance Rules

Optimize only after correctness.

Avoid premature optimization.

Measure before changing.

Prefer simple solutions.

---

# 14. Documentation Rules

Documentation must describe reality.

Never document features that do not exist.

Whenever architecture changes:

Update documentation.

---

# 15. Execution Phases

Phase 1

Architecture Audit

Phase 1.5

Repository Intelligence

Phase 2

Critical Runtime Fixes

Phase 3

Architecture Cleanup

Phase 4

Refactoring

Phase 5

Testing

Phase 6

Deployment Validation

Phase 7

Production Readiness

Never skip phases.

---

# 16. Agent Responsibilities

Every AI agent must:

Understand before modifying.

Minimize risk.

Preserve architecture.

Avoid unnecessary code generation.

Explain important decisions.

Keep commits focused.

Never perform wide refactors without explicit architectural justification.

---

# 17. Commit Policy

One logical problem.

One logical solution.

One logical commit.

Avoid mixed-purpose commits.

---

# 18. Quality Gates

Before considering work complete:

Project builds.

Backend starts.

Frontend builds.

Core routes work.

Authentication works.

No broken imports.

No circular dependencies.

No hidden runtime errors.

---

# 19. Architectural North Star

Nile Key must evolve toward:

Clean Architecture

Domain-driven organization

Well-defined API contracts

Reliable deployment

Comprehensive testing

Production readiness

without sacrificing simplicity.

---

# 20. Final Rule

No developer or AI agent has authority to violate this charter for convenience.

If a requested modification conflicts with this charter,

the conflict must be reported before implementation.

Architecture is preserved first.

Code is written second.
