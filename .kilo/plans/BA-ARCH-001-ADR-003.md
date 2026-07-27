# ADR-BA-003: MCP Integration as Enhancement, Not Requirement

**Date:** 2026-07-22
**Status:** Accepted
**Deciders:** Chief Software Architect
**Source:** BA-ARCH-001 Section 25 — ADR-BA-003

---

## Context

The `.playwright-mcp/` empty directory at the project root indicates that Browser Automation was intended or expected to use MCP at some point. However, MCP availability depends on the `@playwright/mcp` package and Kilo/IDE configuration, both of which are external to the project repository.

The platform must be functional regardless of MCP host availability.

---

## Options Considered

| Option | Description | Trade-off |
|--------|-------------|-----------|
| A — MCP required | Make MCP a mandatory dependency for all test execution | Tight integration but fragile; tests fail if MCP unavailable |
| B — MCP only (chosen) | Implement only MCP-based execution, no CLI | Maximum AI integration but zero fallback |
| C — CLI first, MCP as enhancement (chosen) | Implement `tests/e2e/` CLI first; MCP layer is optional enhancement | Platform is functional without MCP; `.playwright-mcp/` populated with config but not required |

---

## Decision

Implement `tests/e2e/` CLI first. MCP layer is an enhancement dependent on external tool availability. `.playwright-mcp/` is populated with configuration but not required for test execution.

---

## Rationale

1. **Resilience:** Tests must be runnable even if MCP is unavailable. CLI execution is the primary path; MCP enhances but is never required.
2. **Decoupling:** Avoids coupling the test platform to a specific AI tooling version or availability.
3. **Graceful degradation:** Developers without MCP configuration can still run all test suites. Developers with MCP gain additional UAT assistance capabilities.
4. **Project precedent:** The empty `.playwright-mcp/` directory suggests prior intent; populating it with versioned config honors that intent without making it a hard dependency.

---

## Consequences

- ✅ Platform is functional regardless of MCP host availability
- ✅ `.playwright-mcp/` populated with versioned config (no longer empty)
- ⚠️ MCP integration requires separate verification per environment
- ✅ Clear documentation of MCP as optional enhancement
- ⚠️ Kilo configuration must reference `.playwright-mcp/` config files when MCP is enabled

---

## Related

- BA-ARCH-001 Section 8.2 (Logical Boundaries — MCP Layer)
- BA-ARCH-001 Section 13.1 (Manual Assisted UAT — MCP-enhanced)
- BA-IMPL-001 MCP Setup section
