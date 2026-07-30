# Browser Automation Platform — Implementation Plan

**Plan ID:** BA-IMPL-001
**Authority:** BA-DEC-001 (Executive Decision)
**Reference Architecture:** BA-ARCH-001
**Governing Documents:** PLAN.md, `PLAN.md` Section 23
**Date:** 2026-07-22
**Status:** Ready for Execution
**Baseline:** ebc2181 (HEAD)

---

## 1. Executive Summary

This Implementation Plan defines the execution strategy for the Browser Automation Platform (`tests/e2e/` subtree and `.playwright-mcp/` configuration) derived from the approved architecture specification `BA-ARCH-001`.

This plan covers:
- Detailed configuration parameters and environment setup
- Dependency installation and version pinning
- Repository layout with specific directories and files
- Migration phases from current state to target state
- Verification acceptance criteria with commands and evidence requirements
- Success metrics and operational procedures
- Security operations (credential management, `.env` handling, CI secrets)

**Note:** Architectural principles, boundaries, and integration contracts are defined in `BA-ARCH-001`. This document contains implementation and operations details only.

---

## 2. Scope

### In Scope
- Creating `tests/e2e/` directory structure with all config, test suites, page objects, fixtures, and utilities
- Installing and pinning all test runtime dependencies
- Configuring Playwright for local, Docker, and production-safe environments
- Setting up `.playwright-mcp/` with versioned configuration
- Seeding test data and creating test accounts
- Executing migration phases to bring platform from current state to operational
- Capturing and retaining evidence per project governance

### Out of Scope
- Modifying FastAPI backend code
- Modifying React frontend code
- Adding Playwright to backend/frontend runtime Docker images
- CI/CD pipeline wiring (deferred to future WP)
- Multi-browser support (Chromium only — see ADR-BA-002)

---

## 3. Dependencies

| Dependency | Type | Status | Notes |
|-----------|------|--------|-------|
| BA-ARCH-001 approved | Must be approved | Pending | Architecture must be approved before implementation |
| Project Owner approval | Required | Pending | Per BA-DEC-001 |
| Python 3.11+ | Runtime | ✅ Available | Existing backend environment |
| Node.js | Runtime | ✅ Available | Existing frontend environment |
| Playwright installation | Tooling | ✅ Global install present (1.61.1); project-local install required | Will be pinned in test Node workspace |
| SQLite database | Test data | ✅ Available | `nile_key.db` |
| Backend running | Service | Required for test execution | `uvicorn main:app --reload` |
| Frontend running | Service | Required for test execution | `npm run dev` or `npm run preview` |

---

## 4. Repository Layout

### 4.1 Directory Structure

```
F:\nilekey\nile-key-project\nile-key2\
├── .playwright-mcp/                          # MCP server config (version-controlled)
│   ├── README.md
│   ├── default-config.json
│   ├── ai-profile.json
│   └── scenarios/
│       └── uat-assist.json
├── tests/
│   └── e2e/                                  # Browser automation root
│       ├── README.md
│       ├── package.json                      # Node workspace for MCP server deps
│       ├── package-lock.json
│       ├── playwright.config.ts              # Shared Playwright configuration
│       ├── .env.example                      # Environment variable template
│       ├── .env                              # ENVIRONMENT-SPECIFIC — DO NOT COMMIT
│       │
│       ├── suites/                           # Test suites by execution mode
│       │   ├── uat/
│       │   ├── smoke/
│       │   ├── regression/
│       │   ├── prod/
│       │   └── shared/
│       │
│       ├── page-objects/                     # Page Object Models
│       │   ├── LoginPage.ts
│       │   ├── DashboardPage.ts
│       │   ├── SuppliersPage.ts
│       │   ├── CustomersPage.ts
│       │   ├── ShipmentsPage.ts
│       │   ├── InvoicesPage.ts
│       │   ├── CustomsPage.ts
│       │   ├── DocumentsPage.ts
│       │   ├── ResourcesPage.ts
│       │   └── ProfilePage.ts
│       │
│       ├── fixtures/                         # Test data and factories
│       │   ├── factories/
│       │   │   ├── user.factory.ts
│       │   │   ├── supplier.factory.ts
│       │   │   ├── customer.factory.ts
│       │   │   └── shipment.factory.ts
│       │   └── seed-data/
│       │       └── uat-seed.sql
│       │
│       ├── config/                           # Environment-specific configs
│       │   ├── base.config.ts
│       │   ├── local.config.ts
│       │   ├── docker-compose.config.ts
│       │   └── prod.config.ts
│       │
│       ├── utils/                            # Utilities
│       │   ├── auth.ts                       # Login/logout helpers
│       │   ├── api.ts                        # API response helpers
│       │   ├── evidence.ts                   # Screenshot/trace capture
│       │   └── reporter.ts                   # Custom reporter
│       │
│       └── docs/                             # Platform-specific documentation
│           ├── ADR/
│           ├── runner-guide.md
│           ├── mcp-setup.md
│           ├── uat-workflow.md
│           └── troubleshooting.md
```

### 4.2 File Creation Sequence

| Phase | Files Created | Files Modified | Owner |
|-------|---------------|----------------|-------|
| **Bootstrap** | `tests/e2e/README.md`, `tests/e2e/package.json`, `tests/e2e/package-lock.json`, `tests/e2e/playwright.config.ts`, `tests/e2e/.env.example` | None | DevOps |
| **Config** | `tests/e2e/config/*.ts` | None | DevOps |
| **MCP** | `.playwright-mcp/README.md`, `.playwright-mcp/default-config.json`, `.playwright-mcp/ai-profile.json`, `.playwright-mcp/scenarios/uat-assist.json` | None | Architect |
| **Suites** | `tests/e2e/suites/{uat,smoke,regression,prod,shared}/**/*.ts` | None | QA + Dev |
| **Page Objects** | `tests/e2e/page-objects/*.ts` | None | QA + Dev |
| **Fixtures** | `tests/e2e/fixtures/**/*` | `tests/e2e/fixtures/seed-data/uat-seed.sql` | QA |
| **Utils** | `tests/e2e/utils/*.ts` | None | Dev |
| **Docs** | `tests/e2e/docs/**/*.md` | None | Architect + QA |

---

## 5. Configuration Strategy

### 5.1 Configuration Hierarchy

Configurations are layered, with later configs overriding earlier ones:

1. `tests/e2e/playwright.config.ts` — Base config (defaults, committed)
2. `tests/e2e/config/local.config.ts` — Developer local overrides (not committed)
3. `tests/e2e/.env` — Environment variables (not committed)
4. CLI arguments — Runtime overrides (highest precedence)

### 5.2 Key Configuration Parameters

| Parameter | Default (local) | Docker | Production | Description |
|-----------|-----------------|--------|------------|-------------|
| `baseURL` | `http://localhost:3000` | `http://frontend:3000` | `https://nile-key.com` | Frontend URL under test |
| `apiURL` | `http://localhost:8000` | `http://backend:8000` | `https://api.nile-key.com` | Backend URL |
| `browser` | `chromium` | `chromium` | `chromium` | Browser type |
| `headless` | `false` | `true` | `true` | Headless mode |
| `trace` | `on-first-retry` | `on-first-retry` | `on-first-retry` | Trace capture mode |
| `video` | `retain-on-failure` | `off` | `off` | Video capture |
| `screenshot` | `only-on-failure` | `only-on-failure` | `only-on-failure` | Screenshot capture |
| `workers` | `1` | `1` | `1` | Parallel workers (initial value) |
| `timeout` | `30000` | `30000` | `30000` | Default test timeout (ms) |

### 5.3 Configuration Principles

| Principle | Enforcement |
|-----------|------------|
| No secrets in committed config | `.env` in `.gitignore`; template committed |
| Environment isolation | Each environment has separate config file |
| Sensible defaults | `base.config.ts` is runnable without overrides (using localhost) |
| Override visibility | Every override documented in BA-IMPL-001 |

---

## 6. Environment Strategy

### 6.1 Developer Environment

| Step | Action | Command |
|------|--------|---------|
| 1 | Clone repository | `git clone <repo-url>` |
| 2 | Install backend dependencies | `cd backend && pip install -r requirements.txt` |
| 3 | Install frontend dependencies | `cd frontend && npm install` |
| 4 | Install test workspace dependencies | `cd tests/e2e && npm install` |
| 5 | Install Chromium browser | `cd tests/e2e && npx playwright install chromium` |
| 6 | Copy environment template | `cd tests/e2e && cp .env.example .env` |
| 7 | Configure `.env` with local URLs | Edit `.env` with `baseURL=http://localhost:3000`, `apiURL=http://localhost:8000` |
| 8 | Seed test data | Apply `tests/e2e/fixtures/seed-data/uat-seed.sql` to `nile_key.db` |
| 9 | Start backend | `cd backend && uvicorn main:app --reload` |
| 10 | Start frontend | `cd frontend && npm run dev` |
| 11 | Run smoke test | `cd tests/e2e && npm run test:smoke` |

### 6.2 Docker Environment

| Aspect | Specification |
|--------|---------------|
| **Service name** | `playwright` (or `tests`) |
| **Base image** | Node.js image with Python and Chromium dependencies |
| **Build** | Separate Dockerfile in `tests/e2e/Dockerfile` |
| **Dependencies** | Installed at build time; cached across runs |
| **Volume** | Evidence output volume-mounted at `/app/evidence` |
| **Network** | Shares project network; accesses backend via service name |
| **Execution** | `docker compose run --rm playwright test:smoke` |

### 6.3 CI Environment (Future)

| Aspect | Specification |
|--------|---------------|
| **Runner** | Platform-native (GitHub Actions / GitLab CI — WP to be defined) |
| **Browser** | Pre-installed in CI image or downloaded via Playwright |
| **Parallelism** | Initially 1 worker; scalable after baseline stabilizes |
| **Secrets** | From CI secrets store; never in repo |
| **Artifacts** | Uploaded to CI artifact store with retention policy |

### 6.4 Production-Safe Environment

| Aspect | Specification |
|--------|---------------|
| **Trigger** | Manual, post-deployment only |
| **Credentials** | Separate test account; never production admin |
| **Scope** | Read-only checks where possible; no create/update/delete |
| **Data impact** | Zero — tests create no persistent data in production |
| **Alerting** | Separate from development alerting; failure does not block deployment |

---

## 7. Security Operations

### 7.1 Credential Management

| Environment | Storage | Access |
|-------------|---------|--------|
| **Local** | `.env` file in `tests/e2e/`, excluded from git via `.gitignore` | Developer only |
| **Docker** | Environment variables injected via Compose `environment:` block | Docker secrets or env file |
| **CI** | CI secrets store; mapped to test container at runtime | CI service account |
| **Production** | Separate secrets with restricted access; audit log of access | Production operator |

### 7.2 `.env` Handling

```
# tests/e2e/.gitignore
.env
.env.local
.env.*.local
```

**Procedure:**
1. `tests/e2e/.env.example` is committed with placeholder values
2. Each developer copies `.env.example` to `.env` and fills in local values
3. `.env` is never committed
4. `.env.example` is reviewed and updated when new environment variables are added

### 7.3 Test Data Isolation

| Rule | Enforcement |
|------|------------|
| Schema integrity | Tests run against the same database schema as application |
| Data pollution | Tests clean up created records or use transaction rollback patterns |
| Cross-test dependencies | Forbidden — no test depends on state created by another test |
| Seed data | Version-controlled seed SQL in `tests/e2e/fixtures/seed-data/` |

### 7.4 Credential Seeding

| Account | Purpose | Credential Storage |
|---------|---------|-------------------|
| `uat-owner` | Owner-role UAT testing | `tests/e2e/fixtures/seed-data/uat-seed.sql` |
| `uat-manager` | Manager-role UAT testing | `tests/e2e/fixtures/seed-data/uat-seed.sql` |
| `uat-sales` | Sales-role UAT testing | `tests/e2e/fixtures/seed-data/uat-seed.sql` |
| `uat-accountant` | Accountant-role UAT testing | `tests/e2e/fixtures/seed-data/uat-seed.sql` |
| `uat-logistics` | Logistics-role UAT testing | `tests/e2e/fixtures/seed-data/uat-seed.sql` |

**Note:** Passwords are bcrypt-hashed in seed data. Seed SQL is version-controlled and reviewed.

---

## 8. Dependency Matrix

### 8.1 Project Dependencies (New)

| Dependency | Type | Version Strategy | Scope | Notes |
|-----------|------|-----------------|-------|-------|
| `playwright` (Python) | Application runtime for tests | Pinned in `tests/e2e/requirements.txt` | Test only | Outside main `requirements.txt` |
| `pytest-playwright` | pytest plugin | Pinned | Test only | pytest-compatible test runner |
| `@playwright/mcp` | Node.js MCP server | Pinned in `tests/e2e/package.json` | Test/MCP only | In `tests/e2e/` Node workspace |
| `typescript`, `ts-node` | Dev tooling (config) | Pinned in `tests/e2e/package.json` | Development | For `playwright.config.ts` |

### 8.2 System Dependencies

| Dependency | Purpose | Managed By |
|-----------|---------|-----------|
| `Chromium` | Browser binary | Playwright `npx playwright install chromium` |
| `Node.js` | `@playwright/mcp` runtime | Docker / local Node install |
| `Python 3.11+` | Playwright Python runtime | Existing backend environment |

### 8.3 No New Dependencies in Application Images

| Image | Current Dependencies | Post-Change |
|-------|---------------------|-------------|
| backend Docker image | FastAPI + app deps | **Unchanged** |
| frontend Docker image | React + build deps | **Unchanged** |
| **test runner image** (NEW) | — | Node.js + Python + Playwright + Chromium |

---

## 9. Migration Strategy

### 9.1 Pre-Migration Checkpoint

**Current State:**
- No browser automation in repository
- No MCP config in repository
- Global Playwright exists but is unversioned
- WP-42 pending closure

**Target State:**
- `tests/e2e/` platform committed and runnable
- `.playwright-mcp/` populated with tracked configuration
- Evidence repository structured per UAT checklist
- WP-42 closure supported by automation-assisted UAT

### 9.2 Migration Phases

| Phase | Activity | Output | Owner | Duration |
|-------|----------|--------|-------|----------|
| **Phase 0: Lock** | Freeze scope; approve BA-ARCH-001 | Approved architecture | Architect | 1 day |
| **Phase 1: Bootstrap** | Create directory structure; install and pin dependencies | Empty `tests/e2e/` tree with committed config | DevOps | 2 days |
| **Phase 2: UAT Assist** | Implement UAT assistance tests for WP-42 | Working smoke + UAT assist test | QA + Dev | 3 days |
| **Phase 3: Evidence** | Run WP-42 UAT; capture evidence package | `.kilo/plans/wp42-uat-evidence/` populated | QA + Project Owner | 2 days |
| **Phase 4: Sign-off** | WP-42 closure with evidence review | WP-42 closure report | Project Owner | 1 day |
| **Phase 5: Extend** | Implement regression suite for full entity coverage | `tests/e2e/suites/regression/` populated | QA | 5 days |
| **Phase 6: Governance** | Update `PLAN.md` Section 23 and TECH_DEBT.md | Resolved debt; updated rules | Architect | 1 day |
| **Phase 7: CI Ready** | Wire test image to CI | CI workflow configuration | DevOps | Future WP |

### 9.3 Rollback Points

| Checkpoint | Rollback Condition | Rollback Action |
|------------|-------------------|-----------------|
| After Phase 1 | Platform dependencies cannot be installed reproducibly | Remove `tests/e2e/` and `.playwright-mcp/`; document blockers |
| After Phase 2 | UAT assist tests fail to mirror actual UAT checklist | Pause; investigate mismatch with Architect |
| After Phase 3 | Evidence quality insufficient for WP-42 | Rerun with guidance; do not proceed to closure |
| After Phase 4 | Project Owner does not accept UAT evidence | Reopen WP-42; fix failed items |
| After Phase 5 | Regression suite causes regression itself (fragile tests) | Isolate failing tests; implement stability fixes |

### 9.4 Legacy State Cleanup

| Item | Action | Notes |
|------|--------|-------|
| `.playwright-mcp/` (empty) | Populate with versioned config | No deletion; replace content |
| Global Playwright install | Document as legacy; do not remove system-wide | Developer personal choice |
| Any external MCP config (IDE-level) | Migrate to `.playwright-mcp/` | Iteratively; not blocking |

---

## 10. Acceptance Criteria (Verification)

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| AC-BA-1 | `tests/e2e/` directory exists with committed configuration files | `git ls-files tests/e2e/` |
| AC-BA-2 | `npm run test:smoke` passes in local environment from fresh checkout | Terminal execution with zero config changes beyond `.env` |
| AC-BA-3 | `npm run test:uat-assist` executes at least one UAT checklist item with evidence capture | Test output + evidence file in target directory |
| AC-BA-4 | No Playwright dependencies exist in backend/frontend runtime Docker images | `docker inspect` on backend/frontend images |
| AC-BA-5 | All configuration files are version-controlled except `.env` | Git status shows tracked files and ignores `.env` |
| AC-BA-6 | UAT evidence for WP-42 is captured in `.kilo/plans/wp42-uat-evidence/` | Directory populated with structured artifacts |
| AC-BA-7 | `.playwright-mcp/` contains at least one valid configuration file | File content validated |
| AC-BA-8 | No secrets are present in committed repository files | Secret scan passes |
| AC-BA-9 | Documentation (README, runner guide) is present and matches actual execution | Manual review |

**Note:** Architectural acceptance criteria (AC-BA-7, AC-BA-8, AC-BA-10) are specified in `BA-ARCH-001`.

---

## 11. Success Metrics

| Metric | Target (Initial) | Target (Mature) | Measurement |
|--------|-----------------|-----------------|-------------|
| UAT assistance test pass rate on UAT checklist items | 100% (for covered items) | 100% | `npm run test:uat` |
| Smoke test execution time | < 5 minutes | < 3 minutes | Test runner output |
| Regression test execution time | < 30 minutes | < 15 minutes | Test runner output |
| Flaky test rate | < 5% | < 2% | Re-run analysis |
| Test maintenance effort (PRs requiring test updates per UI change) | TBD baseline | < 20% of UI change PRs | PR analytics |
| Developer environment bootstrap time | < 15 minutes | < 10 minutes | Developer feedback + README step count |
| Evidence completeness (screenshots, traces per failure) | 100% | 100% | CI artifact audit |

---

## 12. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|-----------|
| R-1 | Playwright browser binaries fail to install in some developer environments | Medium | High | Documented `playwright install` with fallback; Docker guarantees reproducibility |
| R-2 | Test flakiness in web environment (timing, network) | High | Medium | Retry policy; isolated browser contexts |
| R-3 | Global Playwright version mismatch | Medium | Low | Pin Playwright version; Docker guarantees consistency |
| R-4 | Coupling risk via MCP | Low | Medium | Fallback: CLI-only execution; MCP is enhancement, not requirement |
| R-5 | Test-to-UAT traceability drift | Medium | Medium | Traceability matrix update as part of every WP that touches UAT scope |
| R-6 | Docker image proliferation | Low | Medium | Separate image namespaces; strict network isolation |

---

## 13. Exit Criteria

1. `tests/e2e/` directory created with all committed configuration files
2. `npm run test:smoke` passes in local environment
3. `npm run test:uat-assist` executes at least one UAT checklist item with evidence capture
4. No Playwright dependencies exist in backend/frontend runtime Docker images
5. All configuration files are version-controlled except `.env`
6. `.playwright-mcp/` contains at least one valid configuration file
7. No secrets present in committed repository files
8. Documentation (README, runner guide) is present and matches actual execution
9. Architect and Project Manager approve implementation readiness
10. Project Owner approves proceeding to implementation phase

---

## 14. Post-Execution Next Step

After this plan is executed and the platform is operational:
1. Browser Automation Platform is ready for WP-42 UAT assistance
2. Regression suite can be extended for ongoing protection
3. Future WPs can add CI/CD integration and additional execution modes
4. Platform becomes permanent part of Nile Key project infrastructure

---

**Plan ID:** BA-IMPL-001
**Status:** Ready for Execution
**Approval Required:** Project Owner (per BA-DEC-001)
**Execution Sequence:** Phases 0 → 1 → 2 → 3 → 4 → 5
**Blocking Dependencies:** Phase 0 (BA-ARCH-001 approval + Project Owner approval)
