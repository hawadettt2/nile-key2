# Browser Automation Platform — Architecture Specification

**Document ID:** BA-ARCH-001
**Status:** Approved — Ready for Implementation
**Date:** 2026-07-22
**Baseline:** ebc2181 (HEAD)
**Authority:** PLAN.md (Master Roadmap v2.1)
**Deciders:** Chief Software Architect, Project Manager
**Governing Documents:** PLAN.md, `PLAN.md` Section 23, `docs/appendices/UAT_CHECKLIST.md`

---

## 1. Executive Summary

Browser Automation was identified during WP-42 closure preparation as an operational capability that was never formally integrated into the Nile Key project repository. Evidence confirms it existed only as an external environment capability (global Playwright installation, external MCP configuration, or IDE-level integration) and was never version-controlled within the project.

This document defines the architecture for a permanent, first-class Browser Automation Platform that will become part of the Nile Key project codebase. The platform will support Manual UAT Assistance, Automated UAT, Smoke Testing, Regression Testing, and future Production Verification.

**Note:** This document contains architecture only. Implementation details, configuration parameters, dependency versions, migration phases, verification procedures, and operational metrics are documented in `BA-IMPL-001`.

---

## 2. Background

### 2.1 Operational Discovery

During WP-42 (Owner Acceptance) preparation, the project team discovered that Browser Automation — previously relied upon for Manual UAT support — was unavailable in the current operational environment.

### 2.2 Investigation Findings

| Finding | Evidence | Source |
|---------|----------|--------|
| No Playwright MCP configuration | `C:\Users\OSAMA\.config\kilo\kilo.jsonc` contains no `mcp` section | Global Kilo config |
| No Playwright in project dependencies | No `playwright` in `frontend/package.json`, `backend/requirements.txt`, or project root `package.json` | Project files |
| Empty `.playwright-mcp/` directory | Directory exists at project root with 0 files | Project filesystem |
| No version-controlled browser automation | Full content search found no `playwright.config.*`, no `@playwright/mcp`, no e2e test directory | Repository content audit |
| Historical confirmation | `WP21_M5_StageB_Gap_Analysis_Remediation_Plan.md` records: `No Playwright, Cypress, or Selenium tests exist` | Archived project document |
| Global Playwright present | `npx playwright --version` returns `1.61.1` from system PATH only | Environment audit |
| No MCP tools in active agent | Available tools list contains no `playwright_*`, `browser_*`, or `mcp_*` tools | Agent capabilities audit |

### 2.3 Historical Context

The `.playwright-mcp/` empty directory at the project root indicates that Browser Automation was intended or expected to be part of the project at some point, but was never materialized into version-controlled code or configuration. This aligns with the conclusion that the capability was provided by an external environment rather than being a project deliverable.

### 2.4 Impact

- Manual UAT for WP-42 cannot be assisted by Browser Automation
- No automated browser test suite exists for regression protection
- No reusable browser automation infra for future maintenance
- WP-42 closure requires alternative manual verification path

---

## 3. Problem Statement

The Nile Key project has no governed, reproducible, version-controlled Browser Automation Platform. The absence of this platform:

1. Reduces Manual UAT execution efficiency and evidence quality
2. Creates operational fragility dependent on undocumented external environment
3. Prevents regression testing after deployment
4. Eliminates production verification capability
5. Violates project governance by depending on unversioned infrastructure

---

## 4. Goals

| ID | Goal | Measurable Outcome |
|----|------|-------------------|
| G-1 | Create a permanent Browser Automation Platform as part of the project | Code, configuration, and documentation committed to repository |
| G-2 | Enable Manual UAT Assistance for WP-42 and future acceptance cycles | UAT execution time reduced; evidence capture automated |
| G-3 | Enable Automated UAT execution for regression protection | Reusable test suites executable via CLI |
| G-4 | Enable Smoke Testing post-deployment | Deployment validation script included |
| G-5 | Enable Production Verification | Production environment can run browser checks with secured credentials |
| G-6 | Establish reproducible developer environments | New developer can bootstrap browser automation in documented steps |
| G-7 | Maintain no codebase coupling | Automation is outside the application bundle |
| G-8 | Maintain governance compliance | All configuration version-controlled; all decisions ADR-tracked |

---

## 5. Non-Goals

| Non-Goal | Reason |
|----------|--------|
| Modify FastAPI backend code | Out of scope for platform infrastructure |
| Modify React frontend code | Out of scope for platform infrastructure |
| Add Playwright to backend/frontend runtime dependencies | Violates G-7 |
| Support browsers other than Chromium in initial release | ADR-BA-002: Chromium only |
| Add CI/CD pipeline in this phase | CI integration deferred to future WP |
| Create a monolithic test suite | Tests organized by execution mode |
| Replace existing backend/frontend tests | Complementary tool only |
| Support parallel execution in initial release | Single-worker mode sufficient |

---

## 6. Current State Assessment

### 6.1 Environment

| Component | Current State | Gap |
|-----------|--------------|-----|
| Playwright binary | Installed globally (`1.61.1`) | Not tied to project version; version drift risk |
| Playwright MCP | Not configured; no tools active | Zero capability in current session |
| `.playwright-mcp/` directory | Exists, empty | Placeholder with no content |
| Browser Automation code | Absent from repository | N/A |
| Browser Automation documentation | Absent from repository | N/A |
| End-to-end test suite | Absent | Confirmed gap in WP21_M5_StageB |

### 6.2 Execution Environment

- **OS:** Windows (`win32`)
- **Shell:** PowerShell 5.1
- **Node:** Available via `npx` (Playwright installed)
- **Python:** 3.11+ (backend requirement)
- **Docker:** Backend (`8000`), Frontend (`3000`) — two-service stack
- **Database:** SQLite (`nile_key.db`)
- **Backend:** FastAPI + Uvicorn
- **Frontend:** React 18 + Vite + Tailwind

### 6.3 Existing Test Infrastructure

| Layer | Framework | Count | Scope |
|-------|-----------|-------|-------|
| Backend | pytest | 876 passed, 4 pre-existing failures, 8 skipped | Unit, integration |
| Frontend | Vitest | Component tests only | React component unit tests |
| E2E/Browser | **None** | **0** | **Gap** |

---

## 7. Target Architecture

### 7.1 High-Level Target State

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Nile Key Project Repository                           │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Browser Automation Platform (NEW — governed, version-controlled)     │  │
│  │                                                                       │  │
│  │  Owns: test code, config, fixtures, docs, runner scripts             │  │
│  │  Does NOT import into or couple with application runtime             │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│          ┌─────────────────────────┼─────────────────────────┐              │
│          │                         │                         │              │
│          ▼                         ▼                         ▼              │
│   ┌─────────────┐         ┌─────────────┐          ┌─────────────┐          │
│   │ FastAPI     │         │ React       │          │  MCP Host   │          │
│   │ Backend     │         │ Frontend    │          │  (Kilo/     │          │
│   │ :8000       │         │ :3000       │          │   VS Code)  │          │
│   └─────────────┘         └─────────────┘          └──────┬──────┘          │
│                                                            │                  │
│                                          ┌───────────────▼────────┐         │
│                                          │  Playwright MCP Server  │         │
│                                          │  (Node-based MCP)       │         │
│                                          └───────────────┬────────┘         │
│                                                            │                  │
│                                          ┌───────────────▼────────┐         │
│                                          │  Playwright (Python)    │         │
│                                          │  Test Engine            │         │
│                                          └───────────────┬────────┘         │
│                                                            │                  │
│                                          ┌───────────────▼────────┐         │
│                                          │  Chromium (isolated)    │         │
│                                          │  browser context        │         │
│                                          └────────────────────────┘         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Isolation** | Browser automation runs in a dedicated directory tree; no import paths overlap with application code |
| **Version control** | All test code, configuration, and documentation committed to repository |
| **Environment independence** | Runtime dependencies installed per-environment but pinned via lockfiles |
| **No runtime coupling** | Application Docker images do NOT include Browser Automation dependencies |
| **Evidence-based** | Every test produces capture artifacts (screenshots, traces, HAR files) as defined in config |
| **Reproducibility** | A single documented setup sequence produces identical execution environment |
| **Fail-safe defaults** | Local fallback mode works without MCP; MCP enhances but is not required |

---

## 8. Logical Architecture

### 8.1 Logical Components

| Component | Type | Responsibility |
|-----------|------|----------------|
| **UAT Test Suite** | Test code | Execute Manual UAT checklist with browser automation |
| **Smoke Test Suite** | Test code | Post-deployment health checks |
| **Regression Test Suite** | Test code | Full-page workflow regression coverage |
| **Production Verification Suite** | Test code | Production environment checks |
| **Configuration Layer** | Config | Environment-specific test configuration |
| **Fixture Layer** | Test data | Page Object Models, factory functions, seeded test accounts |
| **MCP Orchestration Layer** | Integration | Node.js MCP server for Kilo agent integration |
| **Evidence Repository** | Output | Structured artifacts: screenshots, traces, videos, HAR files |
| **Execution Modes** | Orchestration | Unified runner delegating to appropriate suite per execution mode |

### 8.2 Logical Boundaries

```
+-----------------------------------------------------------------------------+
|                        Browser Automation Platform                          |
|  (Owns: test code, config, fixtures, docs, runner scripts)                  |
+-----------------------------------------------------------------------------+
                                     │
                              owns/external
                                     │
        ┌────────────────────────────┼──────────────────────────────────┐
        │                            │                                  │
        ▼                            ▼                                  ▼
  ┌──────────┐              ┌──────────────┐                  ┌──────────────┐
  │ Playwright │              │ @playwright/ │                  │  Chromium    │
  │ (Python)   │              │ mcp (Node)   │                  │  (binary)    │
  │ Test Engine │              │ MCP Server   │                  │  Browser      │
  └──────────┘              └──────────────┘                  └──────────────┘
        │                            │                                  │
        └────────────────────────────┴──────────────────────────────────┘
                                     │
                         interacts with (HTTP)
                                     │
        ┌────────────────────────────┼──────────────────────────────────┐
        │                            │                                  │
        ▼                            ▼                                  ▼
  ┌──────────────┐          ┌──────────────────┐            ┌──────────────┐
  │ FastAPI      │          │ React Frontend   │            │  SQLite DB   │
  │ Backend      │          │ (served app)     │            │  nile_key.db │
  └──────────────┘          └──────────────────┘            └──────────────┘
```

---

## 9. Repository Layout

### 9.1 File Ownership and Governance

| Directory/File | Owner | Change Policy |
|----------------|-------|---------------|
| `tests/e2e/suites/*` | QA Engineer | Must align with `docs/appendices/UAT_CHECKLIST.md` |
| `tests/e2e/page-objects/*` | Dev/QA | Changes require architectural review |
| `tests/e2e/fixtures/*` | QA Engineer | Seed data must be regeneratable |
| `tests/e2e/playwright.config.ts` | Architect | Configuration changes require ADR |
| `tests/e2e/.env*` | DevOps | Secrets never committed; template versioned |
| `.playwright-mcp/**` | Architect | MCP config changes require ADR |
| `tests/e2e/docs/*` | Architect | Documentation changes per evidence policy |

**Note:** Detailed directory tree and file names are specified in `BA-IMPL-001` Section on Repository Layout.

---

## 10. Component Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Nile Key Browser Automation Platform                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐   ┌──────────────┐   ┌───────────────────────────┐        │
│  │ Test Runner │   │   Config     │   │    Evidence Repository     │        │
│  │  (CLI)      │──▶│  Layer       │──▶│   (screenshots/videos/     │        │
│  │             │   │              │   │    traces/HAR)             │        │
│  └──────┬──────┘   └──────────────┘   └───────────────────────────┘        │
│         │                                                                   │
│         │ spawns                                                           │
│         ▼                                                                   │
│  ┌─────────────┐   ┌──────────────┐   ┌───────────────────────────┐        │
│  │ Suites/     │   │  Page        │   │    Fixtures /              │        │
│  │ uat/smoke/  │──▶│  Objects     │──▶│    Factories               │        │
│  │ regression/ │   │              │   │                            │        │
│  └──────┬──────┘   └──────┬───────┘   └───────────────────────────┘        │
│         │                 │                                                 │
│         │ uses            │ instantiates                                    │
│         ▼                 ▼                                                 │
│  ┌─────────────────────────────────────┐   ┌─────────────────────────┐     │
│  │    Playwright Test Engine           │──▶│   Chromium Context       │     │
│  │    (Python via pytest-compatible plugin)  │   │   (isolated browser)     │     │
│  └─────────────────────────────────────┘   └───────────┬─────────────┘     │
│                                                         │                  │
│                                                         │ HTTP             │
│                                                         ▼                  │
│                                                 ┌─────────────────┐       │
│                                                 │  Nile Key App   │       │
│                                                 │  FastAPI:8000   │       │
│                                                 │  React:3000     │       │
│                                                 └─────────────────┘       │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │   MCP Layer (Optional — Kilo/IDE integration)                     │     │
│  │   Standard MCP server (Node.js) ──▶ MCP Server ──▶ Playwright Engine      │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Runtime Flow

### 11.1 Manual UAT Assistance Flow

```
User Request (Kilo/IDE)
    │
    ▼
MCP Host loads configuration-defined MCP server
    │
    ▼
MCP → Playwright Test Engine
    │
    ▼
Select UAT test scenario by ID (matches docs/appendices/UAT_CHECKLIST.md)
    │
    ▼
Page Object opens browser → navigates to target URL
    │
    ▼
Executes UAT step (e.g., "Login with valid credentials")
    │
    ▼
Evidence captured: screenshot + page HTML
    │
    ▼
Pass/Fail reported to user
    │
    ▼
Result logged to Evidence Repository with UAT checklist item reference
```

### 11.2 Automated Suites Flow

```
Batch Execution Trigger (CLI / CI)
    │
    ▼
Select suite: smoke / regression / prod / uat
    │
    ▼
Load environment config
    │
    ▼
For each test case in suite:
    │
    ├─ Open isolated browser context
    ├─ Execute test steps
    ├─ Capture evidence on failure
    ├─ Produce test report (HTML/JUnit/JSON)
    │
    ▼
Aggregate results
    │
    ▼
Exit with appropriate code (0 = pass, 1 = fail, 2 = infrastructure error)
```

---

## 12. Browser Automation Lifecycle

| Phase | Activity | Owner | Artifact |
|-------|----------|-------|----------|
| **Setup** | Install dependencies, configure environment, seed test data | DevOps/Dev | README, config files |
| **Authoring** | Write/update Page Objects, test cases, fixtures | QA/Dev | `.ts` test files, POMs |
| **Local Execution** | Developer runs relevant test locally for validation | Developer | Terminal output, artifacts |
| **Review** | Code review of test changes; adherence to UAT checklist | Architect/QA | Git PR review |
| **UAT Execution** | Executed during Manual or Automated UAT cycles | QA + Project Owner | Evidence package |
| **Regression Gate** | Run on every deployment; included in exit criteria | CI/DevOps | CI artifacts |
| **Maintenance** | Update tests when UAT checklist or UI changes | QA | Updated test files |
| **Archive** | Evidence retained per project retention policy | QA | Archived artifacts |

---

## 13. Supported Execution Modes

### 13.1 Manual Assisted UAT

**Purpose:** Assist Project Owner during Manual UAT execution per `PLAN.md` Section 23.

| Aspect | Specification |
|--------|---------------|
| Trigger | User invokes MCP tool or runs test runner in assist mode |
| Execution | Single test step at a time; waits for Project Owner observation |
| Evidence | Screenshot + page state captured on each step |
| Output | Markdown summary referencing `docs/appendices/UAT_CHECKLIST.md` item IDs |
| Human-in-the-loop | Required — execution pauses between UAT items |

### 13.2 Automated UAT

**Purpose:** Execute full UAT checklist automatically without human intervention.

| Aspect | Specification |
|--------|---------------|
| Trigger | Batch execution command |
| Execution | Full UAT suite without pauses |
| Evidence | HTML report with embedded screenshots; JUnit XML for CI |
| Output | Pass/Fail per UAT checklist item |
| Human-in-the-loop | Not required; designed for unattended execution |
| Traceability | Each test case references `docs/appendices/UAT_CHECKLIST.md` section |

### 13.3 Smoke Testing

**Purpose:** Rapid post-deployment verification that the application is functional.

| Aspect | Specification |
|--------|---------------|
| Trigger | Post-deployment or on-demand |
| Execution | ~10-20 high-level navigations and assertions |
| Time target | < 5 minutes |
| Coverage | Login, Dashboard load, API health, navigation between key pages |
| Evidence | Screenshot per failed step only |
| Output | Pass/Fail exit code |

### 13.4 Regression Testing

**Purpose:** Protect against regressions in existing functionality.

| Aspect | Specification |
|--------|---------------|
| Trigger | Scheduled or on-demand |
| Execution | Full entity CRUD workflows across all modules |
| Time target | < 30 minutes (measured and optimized over time) |
| Coverage | All UAT areas in `docs/appendices/UAT_CHECKLIST.md` executable via browser |
| Evidence | Full HTML report with traces; HAR files for network debugging |
| Output | Pass/Fail with detailed breakdown per entity |

### 13.5 Production Verification

**Purpose:** Verify production deployment behaves correctly after release.

| Aspect | Specification |
|--------|---------------|
| Trigger | Manual, post-deployment only |
| Execution | Limited subset: login, dashboard, key entity loads |
| Security | Test credentials from secrets manager; never in repo |
| Isolation | Runs against production URL only; uses test tenant if available |
| Evidence | Retained separately; not mixed with development evidence |
| Output | Pass/Fail with alerting hooks (future CI integration) |

---

## 14. Integration Points

### 14.1 FastAPI Backend

| Integration Aspect | Specification |
|-------------------|---------------|
| **Base URL** | Config-driven: localhost (local), service name (Docker), production URL |
| **Protocol** | HTTP over same-origin or CORS-enabled |
| **Authentication** | Reuses existing JWT/cookie auth flow |
| **Test data** | Seeded via API or direct DB fixture injection (no code change to backend) |
| **Health check** | `/health` endpoint used as smoke test first assertion |
| **Constraints** | No backend code changes; uses existing API contract only |

### 14.2 React Frontend

| Integration Aspect | Specification |
|-------------------|---------------|
| **Base URL** | `localhost:3000` (local), served via Vite dev server or preview |
| **Routing** | Mirror React Router paths from `frontend/src/App.tsx` |
| **State** | Tests interact with rendered DOM only; no internal state manipulation |
| **Constraints** | No frontend code changes; only tests against existing UI |

### 14.3 Docker

| Integration Aspect | Specification |
|-------------------|---------------|
| **Compose** | Separate test service added to `docker-compose.yml` as a new service (not modifying existing backend/frontend) |
| **Network** | Shares project network; accesses backend via service name |
| **Dependencies** | `depends_on` backend (healthy) and frontend (healthy) |
| **Volumes** | Evidence output volume-mounted |
| **Image** | Separate test image based on Node.js + Python, NOT modifying existing app images |

### 14.4 CI/CD (Future Ready)

| Integration Aspect | Specification |
|-------------------|---------------|
| **Trigger** | Post-deployment; on PR for smoke tests only |
| **Runner** | Platform-native (to be specified in future WP) |
| **Artifacts** | HTML reports, screenshots, traces uploaded as CI artifacts |
| **Secrets** | From CI secrets store; never in repo |
| **Failure behavior** | CI failure on any smoke/regression failure |

### 14.5 Kilo (MCP Host)

| Integration Aspect | Specification |
|-------------------|---------------|
| **Configuration file** | `.playwright-mcp/default-config.json` (project-local MCP config) |
| **AI Profile** | `.playwright-mcp/ai-profile.json` (scenario definitions for UAT assistance) |
| **Adoption** | Config format compatible with Kilo MCP spec |
| **Fallback** | Without MCP, tests still runnable via CLI |

### 14.6 MCP (Model Context Protocol)

| Integration Aspect | Specification |
|-------------------|---------------|
| **Protocol** | Standard MCP protocol over stdio transport |
| **Configuration** | Project-local configuration in `.playwright-mcp/` directory |
| **Scenarios** | UAT assistance scenarios defined in `.playwright-mcp/scenarios/*.json` |
| **Scope** | MCP layer is one execution path; CLI execution remains primary |
| **Fallback** | Without MCP, tests still runnable via CLI |

**Note:** Specific MCP server implementation details are specified in `BA-IMPL-001` Section on MCP Setup.

### 14.7 Playwright

| Integration Aspect | Specification |
|-------------------|---------------|
| **Core engine** | Playwright test engine for browser automation |
| **Config pin** | Single source of truth for browser settings in `tests/e2e/playwright.config.ts` |
| **Browser** | Chromium only (initial release — see ADR-BA-002) |
| **Trace** | Trace capture enabled on first retry |
| **Video** | Video capture retained on failure only |
| **Screenshot** | Screenshot on failure for automation; full-page capture for UAT assist |

**Note:** Specific configuration parameter names and default values are specified in `BA-IMPL-001` Section on Configuration Strategy.

---

## 15. Configuration Strategy

Configuration is layered with later configs overriding earlier ones:

```
tests/e2e/playwright.config.ts       ← Base config (defaults, committed)
    ▼
tests/e2e/config/local.config.ts     ← Developer local overrides (not committed)
    ▼
tests/e2e/.env                       ← Environment variables (not committed)
    ▼
CLI arguments                        ← Runtime overrides (highest precedence)
```

**Principles:**
- No secrets in committed config
- Environment isolation per environment
- Sensible defaults in base config
- Every override must be documented in ADR

**Parameters:** Specific parameter names and default values are specified in `BA-IMPL-001` Section on Configuration Strategy.

---

## 16. Environment Strategy

### 16.1 Developer Environment

| Aspect | Specification |
|--------|---------------|
| **OS** | Windows, macOS, or Linux (Playwright-supported) |
| **Setup** | Documented in `BA-IMPL-001` |
| **Browser setup** | Documented browser installation procedure per `BA-IMPL-001` |
| **Test data** | Seeded via documented procedure |
| **Execution** | Test runner commands from `tests/e2e/` directory |
| **MCP** | Optional; developer may use IDE MCP integration separately |

### 16.2 Docker Environment

| Aspect | Specification |
|--------|---------------|
| **Image** | Separate test service in `docker-compose.yml` |
| **Base** | Node.js image with Python + Chromium dependencies |
| **Network** | Shares project network; accesses backend via service name |
| **Execution** | Docker-based test execution per `BA-IMPL-001` |

### 16.3 CI Environment (Future)

| Aspect | Specification |
|--------|---------------|
| **Runner** | Platform-native (to be specified in future WP) |
| **Browser** | Pre-installed in CI image or downloaded via Playwright |
| **Parallelism** | Initially 1 worker; scalable after baseline stabilizes |
| **Secrets** | From CI secrets store; never in repo |
| **Artifacts** | Uploaded to CI artifact store with retention policy |

### 16.4 Production-Safe Environment

| Aspect | Specification |
|--------|---------------|
| **Trigger** | Manual, post-deployment only |
| **Credentials** | Separate test account; never production admin |
| **Scope** | Read-only checks where possible |
| **Data impact** | Zero — tests create no persistent data in production |
| **Alerting** | Separate from development alerting |

---

## 17. Security Considerations

### 17.1 Architectural Security Principles

| Principle | Enforcement |
|-----------|------------|
| No secrets in committed config | `.env` in `.gitignore`; template committed |
| Test data isolation | Tests run against same database schema; clean up created records |
| Credential management | Environment variables only; never committed |
| Network isolation | Internal URLs for development; HTTPS for production |

**Note:** Operational security procedures (`.env` exclusion details, CI secrets handling, credential seeding) are specified in `BA-IMPL-001` Section on Security Operations.

---

## 18. Governance Rules

### 18.1 Test-to-UAT Traceability

| Rule | Enforcement |
|------|------------|
| Every UAT assistance test must reference an item in `docs/appendices/UAT_CHECKLIST.md` | Test naming convention: `uat-{section}-{item-id}` |
| Every smoke test must reference an API or route in `PLAN.md` Section 24 | Test justification section in each file |
| Every regression test must map to a documented user workflow | Traceability matrix updated with each WP that changes the UI |

### 18.2 Evidence Retention

| Rule | Specification |
|------|---------------|
| UAT evidence for WP-42 | Retained in `.kilo/plans/wp42-uat-evidence/` per WP-42 spec |
| General evidence retention | 90 days local; 1 year CI artifacts (configurable) |
| Evidence format | Screenshot (PNG), Trace (ZIP), HTML report |
| Evidence naming | `{suite}-{test-name}-{timestamp}-{attempt}` |

### 18.3 Change Control

| Rule | Enforcement |
|------|------------|
| Test strategy changes require ADR | Architecture Decision Record in `tests/e2e/docs/ADR/` |
| Config changes require architectural review | Changes to `playwright.config.ts` reviewed by Architect |
| New test files must be approved per existing PR gates | Standard project PR workflow |

### 18.4 Backward Compatibility

| Rule | Enforcement |
|------|------------|
| Existing backend/frontend tests must not be modified | No changes to `backend/tests/` or `frontend` test files |
| UAT checklist (`docs/appendices/UAT_CHECKLIST.md`) is source of truth | Test additions must not modify the checklist |
| Application Docker images must not grow | Test dependencies are in separate image only |

---

## 19. Dependency Matrix

### 19.1 Summary

| Dependency Category | Type | Scope | Notes |
|-----------|------|-------|-------|
| Browser automation engine | Test runtime | Test only | Outside main `requirements.txt` |
| Test runner plugin | Test framework integration | Test only | pytest-compatible test runner |
| MCP protocol server | Test/MCP integration | Test/MCP only | In `tests/e2e/` Node workspace |
| Browser binary | Test runtime | Test only | Downloaded via standard Playwright procedure |

**Note:** Specific package names, version strategies, and complete dependency list are specified in `BA-IMPL-001` Section on Dependencies.

### 19.2 No New Dependencies in Application Images

| Image | Current Dependencies | Post-Change |
|-------|---------------------|-------------|
| backend Docker image | FastAPI + app deps | **Unchanged** |
| frontend Docker image | React + build deps | **Unchanged** |
| **test runner image** (NEW) | — | Node.js + Python + Playwright + Chromium |

---

## 20. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|-----------|
| R-1 | Playwright browser binaries fail to install in some developer environments | Medium | High | Documented `playwright install` with fallback; Docker guarantees reproducibility |
| R-2 | Test flakiness in web environment (timing, network) | High | Medium | Retry policy; isolated browser contexts |
| R-3 | Global Playwright version mismatch | Medium | Low | Pin Playwright version; Docker guarantees consistency |
| R-4 | Coupling risk via MCP | Low | Medium | Fallback: CLI-only execution; MCP is enhancement, not requirement |
| R-5 | Test-to-UAT traceability drift | Medium | Medium | Traceability matrix update as part of every WP that touches UAT scope |
| R-6 | Docker image proliferation | Low | Medium | Separate image namespaces; strict network isolation |

---

## 21. Migration Strategy

### 21.1 Pre-Migration State

- No browser automation in repository
- No MCP config in repository
- Global Playwright exists but is unversioned
- WP-42 pending closure

### 21.2 Target State

- `tests/e2e/` platform committed and runnable
- `.playwright-mcp/` populated with tracked configuration
- Evidence repository structured per UAT checklist
- WP-42 closure supported by automation-assisted UAT

### 21.3 Migration Principles

| Principle | Enforcement |
|-----------|------------|
| Isolation requirement | No runtime coupling during migration; application images unchanged |
| Incremental adoption | CLI-first; MCP enhancement follows |
| Evidence-first | UAT evidence captured from first execution |
| Rollback readiness | Each phase has defined rollback condition |

**Note:** Detailed migration phases, owners, deliverables, and rollback points are specified in `BA-IMPL-001` Section on Migration Strategy.

---

## 22. Future Extensibility

### 22.1 Planned Extensions (Post-Initial)

| Extension | Trigger | WP Candidate |
|-----------|---------|--------------|
| Multi-browser support (Firefox, WebKit) | After Chromium suite stabilizes | Future WP |
| Parallel test execution | CI infrastructure available; test stability proven | Future WP |
| Visual regression testing | Design system stabilizes; baseline images captured | Future WP |
| Mobile viewport tests | Responsive design demands | Future WP |
| Performance testing (Lighthouse) | Performance budgets defined | Future WP |
| CI/CD pipeline integration | WP following WP-42 closure | Future WP |
| Test reporting dashboard | Team needs execution trend visibility | Future WP |

### 22.2 Extension Points

| Extension Point | Mechanism |
|-----------------|-----------|
| New suites | Add directory under `tests/e2e/suites/`; register in runner |
| New environments | Add config file under `tests/e2e/config/`; inherit from base |
| New page objects | Add under `tests/e2e/page-objects/`; import as needed |
| New MCP scenarios | Add JSON under `.playwright-mcp/scenarios/` |
| New fixtures | Add under `tests/e2e/fixtures/`; export from index files |

---

## 23. Open Questions

| ID | Question | Owner | Blocking? | Decision Required By |
|----|----------|-------|-----------|----------------------|
| OQ-1 | Is a standard MCP server package available and compatible with current Kilo version? | Architect | Yes (Phase 2) | Before MCP configuration is finalized |
| OQ-2 | What is the exact Docker base image for the test runner service? | DevOps | No | During implementation execution |
| OQ-3 | Should tests use direct API calls for auth or full browser login flow? | Architect | Yes | Before Page Object implementation |
| OQ-4 | What is the Project Owner's preferred evidence format for UAT documentation? | Project Manager | No | During WP-42 execution |
| OQ-5 | Is a separate test database required, or should tests use the same SQLite file? | Backend QA | Yes | Before test data seeding strategy |

---

## 24. Traceability to Governing Documents

| Document | Section | Alignment |
|----------|---------|-----------|
| `PLAN.md` | Section 9.14 (Documentation Rules), Section 10.11 (Architecture Preservation) | Platform adds new capability without modifying existing architecture |
| `PLAN.md` Section 23 | Section 5 (Evidence-Based), Section 10 (Decision Gates), Section 16 (UAT) | Platform enforces evidence capture; supports but does not replace Manual UAT |
| `docs/appendices/UAT_CHECKLIST.md` | All sections | Test artifacts directly map to checklist items |
| `NILE_KEY_RULES.md` | Section 13 (Forbidden Actions), Section 3 (Architecture Rules) | No application code changes; isolation maintained |
| `PLAN.md` | Deprecated — content merged into `PLAN.md` | Platform follows consolidation principle |

---

## 25. ADR Index

| ADR | Title | Status | File |
|-----|-------|--------|------|
| ADR-BA-001 | Browser Automation Platform Scope and Isolation | Accepted | `.kilo/plans/BA-ARCH-001-ADR-001.md` |
| ADR-BA-002 | Browser Selection — Chromium Only Initially | Accepted | `.kilo/plans/BA-ARCH-001-ADR-002.md` |
| ADR-BA-003 | MCP Integration as Enhancement, Not Requirement | Accepted | `.kilo/plans/BA-ARCH-001-ADR-003.md` |

**Note:** Full ADR content is in standalone files per project governance. This index provides traceability from the architecture document to each decision.

---

## 26. Acceptance Criteria (Architectural)

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| AC-BA-7 | All configuration files version-controlled except `.env` | Git status shows tracked files and ignores `.env` |
| AC-BA-8 | No secrets present in committed repository files | Secret scan passes |
| AC-BA-10 | Architecture Specification is approved per project governance | Formal sign-off |

**Note:** Verification acceptance criteria (AC-BA-1 through AC-BA-6, AC-BA-9) are specified in `BA-IMPL-001`.

---

## 27. Document Control

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-07-22 | Initial Architecture Specification — refined per BA-DEC-001 | Chief Software Architect |

**Approval:**

| Role | Name | Date | Status |
|------|------|------|--------|
| Architect | — | — | Pending |
| Project Manager | — | — | Pending |
| Project Owner | — | — | Pending |

**Next Document:** `BA-IMPL-001` — Browser Automation Platform Implementation Plan

---

*This document is the single source of truth for Browser Automation Platform architecture. No implementation may proceed without approval of this specification and an approved Implementation Plan derived from it.*
