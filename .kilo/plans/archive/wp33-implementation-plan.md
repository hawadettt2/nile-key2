# WP-33 — Trade Intelligence: Implementation Plan

**Reference:** PLAN.md (Master Roadmap v2.1)  
**Specification:** `.kilo/plans/WP-33-spec.md`  
**Engineering Decisions:** `.kilo/plans/ED-WP33-001.md`, `.kilo/plans/ED-WP33-002.md`, `.kilo/plans/ED-WP33-003.md`  
**Phase:** 2 — Intelligent Platform  
**Status:** Complete — implementation finished, verified, and closed  
**Date:** 2026-07-21  

---

## 1. Executive Summary

WP-33 implements the **Trade Intelligence** bounded context for the Digital Export Manager (DEM). Trade Intelligence provides a read-only analytical layer over existing platform entity data — specifically suppliers and buyers — enabling the DEM to discover trends, compare entities, and generate reports for decision-making.

Trade Intelligence:
- Reads existing entity data directly from entity tables via `connection()` from `app.services.base`
- Produces analytical insights without modifying any data
- Integrates with Knowledge Graph (WP-32) via `KnowledgeProviderRegistry` → `KnowledgeProvider.query()`
- Integrates with Memory (WP-31) via `MemoryProvider.recall()` / `MemoryProvider.store()`
- Integrates with Company Knowledge (WP-30F) via `KnowledgeProviderRegistry` → `KnowledgeProvider.query()` (provider not yet implemented; graceful degradation applies)
- Integrates with Decision Engine (WP-30D), Execution Engine (WP-30C), and Dashboard (WP-21) via FastAPI endpoints
- Does NOT make business decisions
- Does NOT execute actions
- Does NOT modify entity data or Knowledge Graph
- Is STATELESS — owns no persistent database tables

Per ED-WP33-001, scope is limited to Capability #9 (Trade Intelligence), Capability #15 (Supplier Intelligence), and Capability #16 (Buyer Intelligence). Capability #13 (Opportunity Discovery) and Capability #14 (Market Analysis) are deferred.

---

## 2. Architectural Alignment

The Trade Intelligence layer follows the same bounded-context pattern as other DEM internal modules, positioned in the Intelligence Layer:

```
┌─────────────────────────────────────────┐
│         Digital Export Manager (DEM)     │
│                                           │
│  ┌───────────────────────────────────┐  │
│  │       Intelligence Layer          │  │
│  │  ┌─────────────────────────────┐  │  │
│  │  │     Trade Intelligence      │  │  │
│  │  │         (WP-33)              │  │  │
│  │  │  ┌───────────────────────┐  │  │  │
│  │  │  │  Analysis Services    │  │  │  │
│  │  │  │  - SupplierAnalysis   │  │  │
│  │  │  │  - BuyerAnalysis      │  │  │
│  │  │  │  - TrendsDetection    │  │  │
│  │  │  │  - Comparisons        │  │  │
│  │  │  │  - ReportGeneration   │  │  │
│  │  │  └───────────────────────┘  │  │  │
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Confirmed properties:**
- WP-33 is a separate bounded context with its own service module and API router.
- It does not modify DEM core logic or existing entity tables.
- It integrates with existing interfaces (`KnowledgeProvider`, `MemoryProvider`) without modifying them.
- It is stateless — no persistent storage owned by WP-33.
- It uses the existing audit framework for all operations.
- It reads entity data directly from entity tables (consistent with existing service-layer pattern where services do not call each other).
- It accesses `KnowledgeProviderRegistry` via module-level setter (same pattern as `set_memory_provider()` in `knowledge_graph.py`).
- It accesses `MemoryProvider` via module-level setter (`set_memory_provider()`).

---

## 3. Dependencies

| Dependency | Type | Status | Source |
|------------|------|--------|--------|
| WP-30D: Decision Engine | Must be complete | ✅ Complete per PLAN.md Section 15.3 | PLAN.md Section 7 |
| WP-30C: Execution Engine | Must be complete | ✅ Complete per PLAN.md Section 15.3 | PLAN.md Section 7 |
| WP-30F: Company Knowledge Layer | Must be complete | ✅ Complete per PLAN.md Section 15.3 | PLAN.md Section 7 |
| WP-31: AI Memory | Must be complete | ✅ Complete per PLAN.md Section 15.3 | PLAN.md Section 7 |
| WP-32: Knowledge Graph | Must be complete | ✅ Complete per PLAN.md Section 15.3 | PLAN.md Section 7 |
| Python FastAPI | Runtime | ✅ Available | Repository evidence |
| Pydantic | Schema validation | ✅ Available | Repository evidence |
| pytest | Testing framework | ✅ Available | Repository evidence |
| `reportlab` | PDF generation | ⚠️ Not in `requirements.txt` — must be added during implementation | ED-WP33-003 (PDF export required) |
| `KnowledgeProviderRegistry` accessibility | Pattern | ⚠️ Registry is local to `main.py`; must be exported via setter pattern | Codebase investigation |
| `MemoryProvider` setup | Pattern | ⚠️ `set_memory_provider()` exists but is never called in production; must be called in `main.py` startup | Codebase investigation |
| `CompanyKnowledgeProvider` | Implementation | ⚠️ Not implemented — only `KnowledgeGraphProvider` exists; graceful degradation applies | Codebase investigation |

---

## 4. Implementation Phases

### Phase 1: Foundation (WP-33A)

**Goal:** Define all Pydantic schemas, set up cross-cutting provider access in `main.py`, and create the service module structure.

**Exit Criteria:**
- [ ] All request schemas defined
- [ ] All response schemas defined
- [ ] Insight model defined
- [ ] Error response model defined
- [ ] Schemas import cleanly
- [ ] `main.py` calls `set_memory_provider()` and exports `knowledge_provider_registry` access
- [ ] Service module structure created with setter functions

#### Commit 1: Pydantic Schemas + Provider Setup

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 1.1 | Define request schemas for all 5 public interfaces | `backend/app/schemas/trade_intelligence.py` | None | `SupplierAnalysisRequest`, `BuyerAnalysisRequest`, `TrendDetectionRequest`, `ComparisonRequest`, `ReportGenerationRequest` | None | Schemas validate correctly against Section 9.1 of Specification; all required fields present | None (schema-only) | Interface-specific schemas required because generic Input DTO from Section 9.1 does not map 1:1 to each endpoint's inputs |
| 1.2 | Define response and error schemas | `backend/app/schemas/trade_intelligence.py` | None | `Insight`, `AnalysisOutput`, `ErrorResponse`, `ReportOutput`, `ComparisonOutput` | Task 1.1 | Schemas validate correctly against Section 9.2, 9.3, 10 of Specification | None (schema-only) | None |
| 1.3 | Set up Memory and Knowledge providers in `main.py` | None | `backend/main.py` | Call `set_memory_provider()` with the MemoryProvider instance; make `knowledge_provider_registry` accessible to services via setter | None | `set_memory_provider()` called during startup; registry accessible via `set_knowledge_registry()` | None (wiring only) | `set_memory_provider()` currently only called in tests — production wiring missing |
| 1.4 | Create service module with shared infrastructure | `backend/app/services/trade_intelligence.py` | None | Module with `set_memory_provider()`, `set_knowledge_registry()`, async memory/Knowledge helpers, error formatter, direct DB access helpers | Phase 1 complete | Module imports cleanly; no circular imports | None (module structure) | Circular import with existing services |

**Commit Message:** `feat(wp33): define trade intelligence schemas and provider setup`

---

### Phase 2: Service Layer (WP-33B)

**Goal:** Implement the 5 analytical service functions with Memory, Knowledge Graph, and audit integration. WP-33 reads entity data directly from entity tables using `connection()` from `app.services.base` — consistent with the existing pattern where services do not call each other.

**Exit Criteria:**
- [ ] All 5 service functions implemented
- [ ] Memory integration functional
- [ ] Knowledge Graph integration functional (graceful degradation when provider returns empty)
- [ ] Audit logging functional
- [ ] Graceful degradation implemented
- [ ] Service module imports cleanly

#### Commit 2: Service Module Structure + Supplier + Buyer Analysis

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 2.1 | Implement service module with shared infrastructure and `perform_analysis` dispatcher | `backend/app/services/trade_intelligence.py` | None | Module with `set_memory_provider()`, `set_knowledge_registry()`, `perform_analysis()` dispatcher (per ED-WP33-002 Section 12.2), async memory/Knowledge helpers, error formatter, direct DB access helpers | Phase 1 complete | Module imports cleanly; no circular imports; `perform_analysis()` dispatches to appropriate analysis function based on `analysis_type` | None (module structure) | Circular import with existing services |
| 2.2 | Implement `analyze_supplier` function | `backend/app/services/trade_intelligence.py` | None | Supplier analysis: reads `suppliers` table directly, queries Knowledge Graph for relationships, generates insights with confidence scores, stores results in Memory, logs audit | Task 2.1 | Returns valid insights with confidence scores; uses direct DB access for entity data; stores results in Memory via `store()`; logs audit via `log_audit()` with `current_user` | Unit tests with mocked MemoryProvider and KnowledgeProvider | Entity schema changes break direct DB access — mitigated by using stable column names |
| 2.3 | Implement `analyze_buyer` function | `backend/app/services/trade_intelligence.py` | None | Buyer analysis: reads `customers` table directly, queries Knowledge Graph for relationships, generates insights with confidence scores, stores results in Memory, logs audit | Task 2.1 | Returns valid insights with confidence scores; uses direct DB access for entity data; stores results in Memory; logs audit with `current_user` | Unit tests with mocked dependencies | Same as Task 2.2 |
| 2.4 | Add PDF generation dependency | None | `backend/requirements.txt` | Add `reportlab` to dependencies | None | `reportlab` available for PDF generation | None (dependency update) | New dependency must be approved per project dependency policy |

**Commit Message:** `feat(wp33): implement supplier and buyer analysis with provider setup and report dependency`

#### Commit 3: Trends + Comparisons + Reports

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 3.1 | Implement `detect_trends` function | `backend/app/services/trade_intelligence.py` | None | Trend detection: reads entity data directly, queries Knowledge Graph for relationship trends, applies moving-average with outlier detection, returns trends with confidence scores | Commit 2 complete | Returns trends with confidence scores; uses direct DB access and Knowledge Graph; logs audit with `current_user` | Unit tests with mocked dependencies | Trend algorithm is simplified — exact thresholds deferred to implementation agent |
| 3.2 | Implement `compare_entities` function | `backend/app/services/trade_intelligence.py` | None | Entity comparison: reads multiple entity records directly, computes gap analysis, returns comparison results with recommendations | Commit 2 complete | Returns comparison results with recommendations; supports suppliers and customers; logs audit with `current_user` | Unit tests with mocked dependencies | None |
| 3.3 | Implement `generate_report` function | `backend/app/services/trade_intelligence.py` | None | Report generation: produces CSV (stdlib `csv`) and PDF (via `reportlab`) with required sections per Section 11 of Specification | Commit 2 complete, Task 2.4 | Generates valid CSV and PDF reports with required sections | Unit tests for CSV and PDF generation | PDF generation complexity — implementation agent may defer to simpler PDF library |

**Commit Message:** `feat(wp33): implement trends detection, comparisons, and report generation`

---

### Phase 3: API Layer (WP-33C)

**Goal:** Expose analysis operations via FastAPI router with authentication. Register router and wire Memory/Knowledge providers.

**Exit Criteria:**
- [ ] Router registered in main.py
- [ ] Memory provider wired to WP-33
- [ ] Knowledge registry wired to WP-33
- [ ] All endpoints return valid responses
- [ ] OpenAPI schema generated

#### Commit 4: Router + Registration

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 4.1 | Create FastAPI router with 5 analysis endpoints | `backend/app/routers/trade_intelligence.py` | None | 5 endpoints: `/suppliers/analyze`, `/buyers/analyze`, `/trends/detect`, `/compare`, `/reports/generate` | Phase 2 complete | All endpoints use `async def`; return correct status codes and shapes; authentication required on all endpoints via `get_current_user`; no role restrictions beyond authentication (read-only analysis); `current_user` passed to service functions for audit logging | None (router wiring only) | None |
| 4.2 | Register router and providers in `backend/main.py` | None | `backend/main.py` | Register `trade_intelligence.router` with prefix `/api/v1/trade-intelligence`; call `set_memory_provider()` with the MemoryProvider instance; call `set_knowledge_registry()` with the `knowledge_provider_registry` instance | Task 4.1 | Router appears in OpenAPI schema; endpoints accessible; WP-33 can access Memory and Knowledge Graph | None (registration only) | Import error or circular dependency; `knowledge_provider_registry` is currently local to `main.py` and must be made accessible |

**Commit Message:** `feat(wp33): expose trade intelligence API endpoints`

---

### Phase 4: Testing (WP-33D)

**Goal:** Comprehensive test coverage for all analysis operations.

**Exit Criteria:**
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All security tests pass
- [ ] Performance tests meet thresholds
- [ ] Full regression test suite passes

#### Commit 5: Unit Tests

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 5.1 | Write service layer unit tests | `backend/tests/test_services/test_trade_intelligence.py` | None | 30+ unit tests covering supplier analysis, buyer analysis, trends, comparisons, reports, `perform_analysis` dispatcher, memory integration, audit logging, graceful degradation | Phase 2 complete | All unit tests pass | pytest | Mock complexity for MemoryProvider and KnowledgeProvider |

**Commit Message:** `test(wp33): add service layer unit tests`

#### Commit 6: Integration Tests

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 6.1 | Write router integration tests | `backend/tests/test_trade_intelligence.py` | None | 20+ integration tests covering all endpoints, auth, input validation, error responses | Commit 4 complete | All integration tests pass | pytest with test client | Test database setup/teardown |

**Commit Message:** `test(wp33): add router integration tests`

#### Commit 7: Security + Performance + Regression

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 7.1 | Write security tests | `backend/tests/test_trade_intelligence_security.py` | None | Security tests for authentication, authorization, input validation, SQL injection prevention, audit completeness | Commit 4 complete | All security tests pass | pytest | None |
| 7.2 | Write performance tests | `backend/tests/test_trade_intelligence_performance.py` | None | Performance tests verifying response time thresholds per Section 18.1 of Specification | Commit 4 complete | All operations meet defined thresholds | pytest with timing assertions | Thresholds undefined in spec — defined as <2s for analysis, <5s for reports |
| 7.3 | Verify regression test suite | None | None | Full test suite passes | All previous commits | 100% existing tests pass | pytest | Existing tests broken by changes |

**Commit Messages:**
- `test(wp33): add security and performance tests`
- `test(wp33): verify regression test suite`

---

### Phase 5: Documentation & Closure (WP-33E)

**Goal:** Document implementation and formally close WP-33.

**Exit Criteria:**
- [x] `CURRENT_STATUS.md` updated
- [x] `CHANGELOG.md` updated
- [x] Closure review passed

#### Commit 8: Documentation Updates

| Task | Goal | Files Created | Files Modified | Deliverables | Dependencies | Acceptance Criteria | Tests Required | Risks |
|------|------|---------------|----------------|--------------|--------------|---------------------|----------------|-------|
| 8.1 | Update `CURRENT_STATUS.md` | None | `CURRENT_STATUS.md` | WP-33 marked complete with summary | Phase 4 complete | Documentation reflects implementation | None | None |
| 8.2 | Update `CHANGELOG.md` | None | `CHANGELOG.md` | WP-33 entry added | Phase 4 complete | Changelog documents all changes | None | None |

**Commit Message:** `docs(wp33): update documentation and close WP-33`

---

## 5. Commit Sequence

| Order | Commit | Phase | Tasks | Files Created | Files Modified | Build Risk | Test Risk |
|-------|--------|-------|-------|---------------|----------------|------------|-----------|
| 1 | `feat(wp33): define trade intelligence schemas and provider setup` | 1 | 1.1, 1.2, 1.3, 1.4 | 2 | 1 | Low | Low |
| 2 | `feat(wp33): implement supplier and buyer analysis with provider setup and report dependency` | 2 | 2.1, 2.2, 2.3, 2.4 | 1 | 1 | Low | Medium |
| 3 | `feat(wp33): implement trends detection, comparisons, and report generation` | 2 | 3.1, 3.2, 3.3 | 0 | 1 | Low | Medium |
| 4 | `feat(wp33): expose trade intelligence API endpoints` | 3 | 4.1, 4.2 | 1 | 1 | Medium | Medium |
| 5 | `test(wp33): add service layer unit tests` | 4 | 5.1 | 1 | 0 | Low | Low |
| 6 | `test(wp33): add router integration tests` | 4 | 6.1 | 1 | 0 | Low | Medium |
| 7 | `test(wp33): add security and performance tests` | 4 | 7.1, 7.2 | 2 | 0 | Low | Medium |
| 8 | `test(wp33): verify regression test suite` | 4 | 7.3 | 0 | 0 | Low | Medium |
| 9 | `docs(wp33): update documentation and close WP-33` | 5 | 8.1, 8.2 | 0 | 2 | Low | Low |

---

## 6. Dependency Analysis

### 6.1 Task Dependencies

```
Phase 1: Foundation (Commit 1)
├── Task 1.1: Request schemas
└── Task 1.2: Response and error schemas
    └── Dependencies: Task 1.1

Phase 2: Service Layer (Commits 2-3)
├── Commit 2
│   ├── Task 2.1: Service module structure
│   │   └── Dependencies: Phase 1 complete
│   ├── Task 2.2: Supplier analysis
│   │   └── Dependencies: Task 2.1
│   ├── Task 2.3: Buyer analysis
│   │   └── Dependencies: Task 2.1
│   └── Task 2.4: PDF generation dependency
│       └── Dependencies: None
└── Commit 3
    ├── Task 3.1: Trends detection
    │   └── Dependencies: Commit 2 complete
    ├── Task 3.2: Comparisons
    │   └── Dependencies: Commit 2 complete
    └── Task 3.3: Report generation
        └── Dependencies: Commit 2 complete

Phase 3: API Layer (Commit 4)
├── Task 4.1: Create router
│   └── Dependencies: Phase 2 complete
└── Task 4.2: Register router
    └── Dependencies: Task 4.1

Phase 4: Testing (Commits 5-8)
├── Commit 5: Unit tests
│   └── Dependencies: Phase 2 complete
├── Commit 6: Integration tests
│   └── Dependencies: Commit 4 complete
├── Commit 7: Security + Performance tests
│   └── Dependencies: Commit 4 complete
└── Commit 8: Regression tests
    └── Dependencies: All previous commits

Phase 5: Documentation (Commit 9)
└── Dependencies: Phase 4 complete
```

### 6.2 Circular Dependency Check

| Check | Result | Evidence |
|-------|--------|----------|
| Service layer imports schemas | ✅ Safe | `backend/app/services/supplier.py` imports from `app/schemas/supplier.py` — same pattern |
| Router imports service layer | ✅ Safe | `backend/app/routers/suppliers.py` imports from `app/services/supplier.py` — same pattern |
| Service layer imports database | ✅ Safe | `backend/app/services/base.py` provides `connection()` — same pattern |
| Service layer imports audit | ✅ Safe | `backend/app/services/supplier.py` imports `log_audit` — same pattern |
| Service layer imports Memory/Knowledge | ✅ Safe | `backend/app/services/knowledge_graph.py` already imports and uses MemoryProvider |
| No DEM core modifications | ✅ Safe | WP-33 does not modify DEM core per ED-WP33-001 |

**No circular dependencies detected.**

### 6.3 Build Safety Check

| Check | Result | Evidence |
|-------|--------|----------|
| New modules follow existing naming conventions | ✅ Safe | `trade_intelligence.py` follows same pattern as `supplier.py`, `knowledge_graph.py` |
| New schemas follow existing Pydantic patterns | ✅ Safe | `backend/app/schemas/supplier.py` pattern followed |
| New router follows existing registration pattern | ✅ Safe | `backend/main.py` includes `app.include_router(...)` for all routers |
| No modifications to existing entity tables | ✅ Safe | WP-33 is stateless per ED-WP33-001 — no database tables |
| No modifications to DEM core | ✅ Safe | Only `backend/main.py` modified for router registration |

**Build safety maintained throughout all commits.**

### 6.4 Test Safety Check

| Check | Result | Evidence |
|-------|--------|----------|
| Unit tests run in isolation | ✅ Safe | Tests use mocks for MemoryProvider and KnowledgeProvider |
| Integration tests use test database | ✅ Safe | Follows existing `conftest.py` pattern |
| Regression tests run after all changes | ✅ Safe | Commit 8 runs full test suite |
| No existing tests modified | ✅ Safe | Only new test files created |

**Test safety maintained throughout all commits.**

---

## 7. File Inventory

### 7.1 Files Created

| File | Phase | Commit | Purpose |
|------|-------|--------|---------|
| `backend/app/schemas/trade_intelligence.py` | 1 | 1 | Pydantic schemas for all request/response/insight/error DTOs |
| `backend/app/services/trade_intelligence.py` | 2 | 2, 3 | Service module with 5 analysis functions and shared infrastructure |
| `backend/app/routers/trade_intelligence.py` | 3 | 4 | FastAPI router exposing 5 analysis endpoints |
| `backend/tests/test_services/test_trade_intelligence.py` | 4 | 5 | Service layer unit tests |
| `backend/tests/test_trade_intelligence.py` | 4 | 6 | Router integration tests |
| `backend/tests/test_trade_intelligence_security.py` | 4 | 7 | Security tests |
| `backend/tests/test_trade_intelligence_performance.py` | 4 | 7 | Performance tests |

### 7.2 Files Modified

| File | Phase | Commit | Changes |
|------|-------|--------|---------|
| `backend/main.py` | 1, 3 | 1, 4 | Call `set_memory_provider()` during startup; make `knowledge_provider_registry` accessible via `set_knowledge_registry()`; register `trade_intelligence.router` |
| `backend/requirements.txt` | 2 | 2 | Add `reportlab` for PDF generation |

---

## 8. Risk Register

| Risk | Likelihood | Impact | Mitigation | Phase |
|------|------------|--------|------------|-------|
| PDF generation requires new dependency | High | Medium | Add `reportlab` to `requirements.txt` in Task 2.4; implementation agent may choose alternative lightweight library | 2 |
| `set_memory_provider()` never called in production | High | Low | Add explicit call in `main.py` startup (Task 1.3) | 1 |
| `knowledge_provider_registry` not accessible from services | High | Low | Add `set_knowledge_registry()` setter in `knowledge_graph.py` or new shared module; call from `main.py` | 1 |
| Company Knowledge provider not implemented | High | Low | Graceful degradation per spec — continue without Company Knowledge; log warning | 2 |
| KnowledgeGraphProvider.query() returns empty results | High | Low | Graceful degradation per spec — continue with entity data only; graph enhances but is not required | 2 |
| Entity data access via direct DB queries | Low | Medium | Use stable column names; avoid SELECT *; follow existing `build_list_query()` pattern | 2 |
| Exact analysis algorithms not specified | High | Low | Define high-level algorithms in Implementation Plan; implementation agent refines within specified bounds | 2 |
| Test database setup/teardown issues | Medium | Medium | Follow existing `conftest.py` patterns | 4 |
| Existing tests broken by changes | Low | High | Regression test suite in Commit 8 | 4 |

---

## 9. Acceptance Criteria Summary

All acceptance criteria from WP-33 Specification Section 19 are covered:

| AC ID | Criterion | Covered In |
|-------|-----------|------------|
| AC-33.1 | Supplier analysis returns valid insights with confidence scores | Commit 2 (Task 2.2) |
| AC-33.1 | Supplier analysis uses Knowledge Graph for relationship data | Commit 2 (Task 2.2) |
| AC-33.1 | Supplier analysis stores results in Memory | Commit 2 (Task 2.2) |
| AC-33.1 | Supplier analysis is auditable | Commit 2 (Task 2.2) |
| AC-33.2 | Buyer analysis returns valid insights with confidence scores | Commit 2 (Task 2.3) |
| AC-33.2 | Buyer analysis uses Knowledge Graph for relationship data | Commit 2 (Task 2.3) |
| AC-33.2 | Buyer analysis stores results in Memory | Commit 2 (Task 2.3) |
| AC-33.2 | Buyer analysis is auditable | Commit 2 (Task 2.3) |
| AC-33.3 | Market trends detects patterns in entity data | Commit 3 (Task 3.1) |
| AC-33.3 | Market trends returns confidence scores | Commit 3 (Task 3.1) |
| AC-33.3 | Market trends is auditable | Commit 3 (Task 3.1) |
| AC-33.4 | Comparisons returns valid comparison results | Commit 3 (Task 3.2) |
| AC-33.4 | Comparisons supports multiple entity types | Commit 3 (Task 3.2) |
| AC-33.4 | Comparisons is auditable | Commit 3 (Task 3.2) |
| AC-33.5 | Reports generated in PDF format | Commit 3 (Task 3.3) |
| AC-33.5 | Reports generated in CSV format | Commit 3 (Task 3.3) |
| AC-33.5 | Reports include all required sections | Commit 3 (Task 3.3) |
| AC-33.6 | Decision Engine can consume analysis results | Commit 4 (Task 4.1) |
| AC-33.6 | Execution Engine can execute analysis tasks | Commit 4 (Task 4.1) |
| AC-33.6 | Dashboard can display analysis results | Commit 4 (Task 4.1) |
| AC-33.6 | Knowledge Graph integration works | Commit 2 (Task 2.2, 2.3) |
| AC-33.6 | Memory integration works | Commit 2 (Task 2.2, 2.3) |
| AC-33.6 | Company Knowledge integration ready | Commit 2 (Task 2.1) — integration point defined; graceful degradation verified when provider unavailable |
| AC-33.7 | WP-33 never modifies entity data | Design — read-only service functions |
| AC-33.7 | WP-33 never makes business decisions | Design — analysis only, no decision logic |
| AC-33.7 | WP-33 never executes actions | Design — no execution logic |
| AC-33.7 | WP-33 never modifies Knowledge Graph | Design — read-only KnowledgeProvider.query() calls |
| AC-33.7 | WP-33 never modifies Memory owned by others | Design — MemoryProvider.store() for analysis results only |
| AC-33.8 | All tests pass | Commit 8 (Task 7.3) |
| AC-33.8 | No regressions in existing tests | Commit 8 (Task 7.3) |

---

## 10. Quality Gates

Per PLAN.md Section 10.8, the following quality gates must be passed before WP-33 closure:

| Gate | Verification | Phase |
|------|--------------|-------|
| Project builds | Backend starts without import errors | 3 |
| Core paths work | Analysis endpoints return valid responses | 4 |
| Authentication works | Auth required for all endpoints | 4 |
| No broken imports | Static analysis passes | 2 |
| No circular dependencies | Static analysis passes | 2 |
| No hidden runtime errors | Full test suite passes | 4 |
| Tests pass | All unit + integration + security tests pass | 4 |

---

## 11. Implementation Notes

### 11.1 Knowledge Graph and Memory Access Pattern

WP-33 accesses `KnowledgeProviderRegistry` and `MemoryProvider` via module-level setters, following the existing pattern in `backend/app/services/knowledge_graph.py`:

```python
# In backend/app/services/trade_intelligence.py
_memory_provider = None
_knowledge_registry = None

def set_memory_provider(provider) -> None:
    global _memory_provider
    _memory_provider = provider

def set_knowledge_registry(registry) -> None:
    global _knowledge_registry
    _knowledge_registry = registry

async def _get_knowledge_provider(source_id: str = "knowledge-graph"):
    if _knowledge_registry is None:
        return None
    return _knowledge_registry.get(source_id)
```

In `backend/main.py` startup:
```python
from app.services.trade_intelligence import set_memory_provider, set_knowledge_registry
from app.agent.knowledge.registry import KnowledgeProviderRegistry

# ... after providers are initialized ...
set_memory_provider(memory_provider_instance)
set_knowledge_registry(knowledge_provider_registry)
```

**Note:** `set_memory_provider()` exists in `knowledge_graph.py` but is never called in production. WP-33 will define its own setters or reuse the existing pattern. The `knowledge_provider_registry` instance created in `main.py` must be made accessible to services.

### 11.2 Company Knowledge Integration Gap

**Current state:** Only `KnowledgeGraphProvider` is implemented. No `CompanyKnowledgeProvider` exists.

**Implication:** WP-33's integration with Company Knowledge (WP-30F) cannot function until a `CompanyKnowledgeProvider` is implemented. Per FR-33.8 and ED-WP33-002, WP-33 must gracefully degrade when Company Knowledge is unavailable.

**Implementation approach:**
- WP-33 queries `KnowledgeProviderRegistry` for all registered providers
- If `CompanyKnowledgeProvider` is not registered, WP-33 continues without it and logs a warning
- The integration point is ready; it will work automatically when the provider is added

### 11.3 Entity Data Access

WP-33 reads entity data directly from entity tables using `connection()` from `app.services.base`. This follows the existing pattern where services do not call each other. WP-33 does NOT import or call `supplier.py` or `customer.py` service functions.

Entity tables accessed:
- `suppliers` — for supplier analysis
- `customers` — for buyer analysis
- `shipments` — for trend detection
- `invoices` — for trend detection
- `customs_declarations` — for trend detection

WP-33 uses parameterized queries to prevent SQL injection, consistent with PLAN.md Section 9.12.

### 11.4 Exact Method Signatures

All service functions are async to support integration with async `MemoryProvider` and `KnowledgeProvider` interfaces. This follows the existing pattern used in `backend/app/agent/` and the async internal helpers in `backend/app/services/knowledge_graph.py`.

```python
# Service function signatures (defined in Task 2.1)
async def analyze_supplier(supplier_id: int, analysis_type: str, date_range: Optional[dict], requested_by: str, current_user: dict, correlation_id: Optional[str]) -> dict
async def analyze_buyer(buyer_id: int, analysis_type: str, date_range: Optional[dict], requested_by: str, current_user: dict, correlation_id: Optional[str]) -> dict
async def detect_trends(entity_type: str, trend_parameters: dict, requested_by: str, current_user: dict, correlation_id: Optional[str]) -> dict
async def compare_entities(entity_ids: list[int], comparison_criteria: dict, requested_by: str, current_user: dict, correlation_id: Optional[str]) -> dict
async def generate_report(analysis_ids: list[str], report_type: str, requested_by: str, current_user: dict, correlation_id: Optional[str]) -> dict

# Dispatcher for Execution Engine (per ED-WP33-002 Section 12.2)
async def perform_analysis(analysis_type: str, parameters: dict, current_user: dict, correlation_id: Optional[str]) -> dict
```

### 11.5 Exact Data Schemas

Schemas are defined in `backend/app/schemas/trade_intelligence.py` per Task 1.1 and 1.2. Each public interface has its own request schema. The generic Input DTO from Section 9.1 is represented as a base class with interface-specific subclasses because the generic DTO does not map 1:1 to each endpoint's inputs (e.g., `compare_entities` takes `entity_ids` array, not a single `entity_id`).

### 11.6 Exact Report Formats

- **CSV:** Standard comma-separated format with header row; one row per insight or metric. Generated using Python stdlib `csv` module.
- **PDF:** Structured document with title, required sections per Section 11 of Specification, and tables. Generated using `reportlab` library, which must be added to `backend/requirements.txt` in Task 2.3.

### 11.7 Exact Confidence Calculation

Confidence score is a weighted composite:
- 40% data quality (completeness of entity records — ratio of non-null fields)
- 35% source reliability (Knowledge Graph availability, Company Knowledge availability)
- 25% analysis method certainty (sample size, date range coverage)

Range: 0.0 (no confidence) to 1.0 (full confidence).

### 11.8 Exact Caching Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Cache key prefix | `trade_intelligence:` | Namespace isolation |
| Default TTL | 24 hours | Per WP-33-spec.md Section 14.3 |
| Invalidation trigger | Explicit on new analysis request | Per WP-33-spec.md Section 14.3 |
| Memory type | `context` | Per WP-31 MemoryProvider interface |
| Importance | 7 (scale 0-10) | High — analytical results are valuable context |

### 11.9 Knowledge Graph Integration

WP-33 uses `KnowledgeProviderRegistry` to access `KnowledgeProvider.query()` and `KnowledgeProvider.get_sources()`. The current `KnowledgeGraphProvider.query()` returns empty results. WP-33 gracefully degrades to entity-data-only analysis when Knowledge Graph returns no results, per FR-33.8 and ED-WP33-002.

### 11.10 Memory Integration

WP-33 uses `MemoryProvider.recall()` and `MemoryProvider.store()` for caching analysis results. The `set_memory_provider()` function must be called in `main.py` during startup (currently only called in tests). When Memory is unavailable, WP-33 continues without caching and logs a warning, per FR-33.8 and ED-WP33-002.

### 11.11 Dashboard Integration

The Dashboard (WP-21) consumes WP-33 results via the FastAPI endpoints exposed by WP-33's router. There is no direct service-to-service call. The Dashboard calls `/api/v1/trade-intelligence/*` endpoints and renders the results.

### 11.12 Decision Engine and Execution Engine Integration

The Decision Engine (WP-30D) and Execution Engine (WP-30C) consume WP-33 results via two possible patterns:

**Pattern A — Direct service calls:**
The agent modules import `backend/app/services/trade_intelligence.py` and call the async service functions directly. This is the simplest approach and follows the pattern used in `erp_tools.py` where tools import services internally.

**Pattern B — Tool wrappers:**
The implementation agent may create tool wrappers in `backend/app/agent/tools/` following the existing `BaseTool` pattern (see `ShippingGetRatesTool`, `EtaSubmitInvoiceTool`, etc.). Each tool would:
- Declare `tool_name = "trade_intelligence_analyze_supplier"` etc.
- Set `side_effects = ToolSideEffect.READ` and `idempotent = True`
- Call the corresponding service function in `execute()`
- Be registered in `ToolRegistry`

Pattern B is consistent with WP-30E and the existing agent architecture. Pattern A is simpler and requires fewer files. The implementation agent chooses based on project conventions at implementation time.

### 11.13 Audit Logging Pattern

All service functions must call `log_audit()` with `current_user` from the router. The audit `entity_type` should be `"trade_intelligence"` and `entity_id` should be the analysis target ID (supplier_id, buyer_id, etc.) or the generated `analysis_id`. This follows the existing pattern in `supplier.py`, `customer.py`, etc.

---

## 12. Document Authority

This document defines the implementation plan for WP-33.

All implementation tasks, technical designs, and code changes for WP-33 MUST derive from this document and the referenced Specification and Engineering Decisions.

Any deviation requires a documented architectural decision recorded in the Architectural Decision Log (PLAN.md Section 13) with explicit rationale.

**Status:** Complete — implementation finished, verified, and closed.

---

## 13. References

- `PLAN.md` Section 6.2 — Capability #9: Trade Intelligence
- `PLAN.md` Section 7 — Work Package execution order
- `PLAN.md` Section 9.3 — Source of Truth: Pydantic Schemas
- `PLAN.md` Section 9.9 — Database Rules
- `PLAN.md` Section 9.10 — API Rules
- `PLAN.md` Section 9.12 — Security Rules
- `PLAN.md` Section 10.4 — Testing Rules
- `PLAN.md` Section 10.8 — Quality Gates
- `PLAN.md` Section 14.1 — Implementation Rules
- `PLAN.md` Section 15.3 — WP-33 status
- `PLAN.md` Section 16.3 — Phase 2 exit criteria
- `.kilo/plans/WP-33-spec.md` — WP-33 Specification
- `.kilo/plans/ED-WP33-001.md` — Capability Boundaries
- `.kilo/plans/ED-WP33-002.md` — Integration Contracts
- `.kilo/plans/ED-WP33-003.md` — Public Interface & Data Contracts
- `backend/app/agent/knowledge/provider.py` — `KnowledgeProvider` ABC
- `backend/app/agent/knowledge/registry.py` — `KnowledgeProviderRegistry`
- `backend/app/agent/memory/interface.py` — `MemoryProvider` ABC
- `backend/app/services/base.py` — Service layer utilities
- `backend/app/services/audit.py` — Audit logging
- `backend/app/services/knowledge_graph.py` — Memory provider setter pattern
- `backend/app/core/database.py` — Database initialization pattern
- `backend/main.py` — Application entry point and router registration
- `backend/app/routers/auth.py` — `get_current_user`, `require_role` dependencies
- `.kilo/plans/wp32-implementation-plan.md` — WP-32 implementation pattern
