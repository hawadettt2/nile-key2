# ADR-BA-001: Browser Automation Platform Scope and Isolation

**Date:** 2026-07-22
**Status:** Accepted
**Deciders:** Chief Software Architect, Project Manager
**Source:** BA-ARCH-001 Section 25 — ADR-BA-001

---

## Context

Browser Automation was identified during WP-42 closure preparation as an operational capability that was never formally integrated into the Nile Key project repository. Evidence confirms it existed only as an external environment capability and was never version-controlled within the project.

The project needs Browser Automation to support Manual UAT Assistance, Automated UAT, Smoke Testing, Regression Testing, and future Production Verification. However, the project must not couple browser automation infrastructure to the application runtime.

**Source:** BA-ARCH-001 Section 2, Section 3; `.playwright-mcp/` empty directory; global Playwright installation evidence.

---

## Options Considered

| Option | Description | Trade-off |
|--------|-------------|-----------|
| A — Runtime integration | Add Playwright to application `requirements.txt` and `package.json` | Simple but violates cleanup/rebuild isolation; bloats production image |
| B — Separate repository | Standalone repo for browser automation | Overhead of separate repo; loses connection to application version |
| C — In-repo isolated subtree (chosen) | `tests/e2e/` + `.playwright-mcp/` within project, own lockfiles, not imported by app | Moderate complexity; no runtime coupling; maintainable |

---

## Decision

Adopt Option C — in-repo isolated subtree with separate lockfiles, own `package.json`/`requirements.txt`, and no coupling to application Docker images.

---

## Rationale

1. **Isolation principle:** Application Docker images must remain unchanged per project governance. Runtime integration would require adding Playwright to backend/frontend images, violating the boundary between application and test infrastructure.

2. **Version control:** All test infrastructure must be version-controlled with the application. A separate repository would disconnect test evolution from application evolution.

3. **Maintainability:** An in-repo subtree allows test code to evolve alongside application code, with the same PR review process and branch strategy.

4. **No runtime coupling:** Test dependencies are installed per-environment but are never imported by application code. The application is unaware of the test subtree's existence.

5. **Reproducibility:** A single repository checkout contains both application and test infrastructure, ensuring reproducible environments.

---

## Consequences

- ✅ Application images remain unchanged
- ✅ Test infrastructure versioned with application
- ✅ Independent update cycle for test tooling
- ⚠️ Requires discipline to not import test utilities into application code
- ⚠️ Test directory must be excluded from application build processes

---

## Related

- BA-ARCH-001 Section 7.2 (Design Principles)
- BA-ARCH-001 Section 8.2 (Logical Boundaries)
- BA-IMPL-001 Section on Repository Layout
