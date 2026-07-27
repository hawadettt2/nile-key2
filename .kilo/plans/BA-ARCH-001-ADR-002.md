# ADR-BA-002: Browser Selection — Chromium Only Initially

**Date:** 2026-07-22
**Status:** Accepted
**Deciders:** Chief Software Architect
**Source:** BA-ARCH-001 Section 25 — ADR-BA-002

---

## Context

Playwright supports Chromium, Firefox, and WebKit. Testing all three browsers adds operational overhead, increases execution time, and expands the flakiness surface.

The project needs a deterministic initial release with minimal browser-related instability.

---

## Options Considered

| Option | Description | Trade-off |
|--------|-------------|-----------|
| A — All three browsers | Support Chromium, Firefox, WebKit from initial release | Maximum coverage but highest complexity, longest execution time, most flakiness |
| B — Chromium only (chosen) | Support Chromium only in initial release | Minimal scope, fastest execution, least flakiness |
| C — Chromium + Firefox | Two most popular browsers | Moderate scope; WebKit coverage gap remains |

---

## Decision

Support Chromium only in initial release. Other browsers deferred to future Work Package.

---

## Rationale

1. **Widest adoption:** Chromium-based browsers (Chrome, Edge, Brave) cover 65%+ of global browser market share.
2. **Stability:** Playwright Chromium is the most stable on both Windows and Linux CI environments.
3. **Scope reduction:** Reduces initial scope and flakiness surface, enabling faster stabilization of the test platform.
4. **Clear upgrade path:** Adding Firefox and WebKit later is a documented extension point in BA-ARCH-001 Section 22.

---

## Consequences

- ✅ Minimal browser-related flakiness initially
- ✅ Fastest execution time for smoke and regression suites
- ✅ Simplest Docker image configuration
- ⚠️ Firefox/WebKit coverage gap (acceptable for MVP; documented as future extension)
- ✅ Clear upgrade path when platform stabilizes

---

## Related

- BA-ARCH-001 Section 13 (Supported Execution Modes)
- BA-ARCH-001 Section 22 (Future Extensibility)
- BA-IMPL-001 Dependency Matrix
