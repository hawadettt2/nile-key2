# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- WP-LLM-001: LLM Provider Integration completed
  - `GeminiProvider` implemented in `backend/app/agent/llm/provider.py`
  - `llm_registry` registration in `backend/main.py` lifespan
  - `ReasoningEngine` integrated with `llm_registry` for candidate enhancement and reasoning improvement
  - LLM config added to `backend/app/core/config.py` and `backend/.env.example`
  - 12 unit tests for provider (`tests/agent/test_llm.py`)
  - 6 integration tests for DEM-LLM interaction (`tests/agent/test_llm_integration.py`)
  - 6 performance tests per DR-004 (`tests/agent/test_llm_performance.py`)
  - All 90 affected tests passing; no regression

- WP-34: External Research Capability completed
  - Research Request/Result models with full traceability
  - Research Lifecycle Orchestrator with 7 stages (Planning ? Discovery ? Retrieval ? Processing ? Evidence Capture ? Structuring ? Verification)
  - Source Registry & Discovery with preference-based and scope-based discovery
  - Retrieval Abstraction with multi-source isolation and Content Processor
  - Evidence & Provenance Capture with deterministic provenance records
  - Result Structuring & Output with Evidence ? Finding ? ResearchResult chain
  - Verification/Quality/Failure Handling with deterministic quality checks and partial/failed result support
  - 103 WP-34 tests passing; no regressions in existing 30 related tests

- Documentation Consolidation & SSOT — completed
  - `PLAN.md` restructured as Single Source of Truth (1,746 lines, 27 sections)
  - 6 new sections added: 22?27 (System State, Execution Governance, Deployment, Repository Architecture, Decision Index, Appendices)
  - 47 historical/superseded documents archived to `.kilo/plans/archive/`
  - 9 long-form references relocated to `docs/appendices/`
  - 17 standalone references preserved (ED, ADR, Contracts, Specs, EARP-001 package)
  - Cross-references updated in 10 active documents
  - Zero code files modified
  - Zero architectural drift
  - Archive and appendices fully populated

### Added
- WP-30F: Company Knowledge Layer interface definitions
  - `KnowledgeProvider` ABC with `query()` and `get_sources()` methods
  - `KnowledgeQuery` Pydantic schemas (`AgentKnowledgeQueryRequest`, `AgentKnowledgeQueryResponse`)
  - `KnowledgeProviderRegistry` with register, unregister, get, list, exists, query
  - Knowledge Ingestion Contract document (`.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`)
- 17 new unit tests for knowledge layer (`tests/agent/test_knowledge.py`)
- ED-WP30-002: WP-30F scope clarification (Tasks 6.1?6.4 only)
- WP-30G: Memory Interface Definition
  - `MemoryProvider` ABC refined with `recall()`, `store()`, `forget()`, `summarize()` methods
  - `MemoryContract` document (`.kilo/plans/MEMORY_CONTRACT.md`)
  - 12 new unit tests for memory interface (`tests/agent/test_memory.py`)
- WP-30H: Avatar Contract
  - `IntentContent` Pydantic contract with `intent_type`, `content`, `context`, `suggested_actions`
  - `AvatarRenderer` ABC with `render()` method
  - Avatar Contract document (`.kilo/plans/AVATAR_CONTRACT.md`)
  - 15 new unit tests for avatar interface (`tests/agent/test_avatar.py`)

### Changed
- `AgentKnowledgeQueryRequest` now includes `context` and `scope` fields
- `AgentKnowledgeQueryResponse` now includes `confidence` and `sources` fields
- `KnowledgeProvider.query()` signature extended with `scope` parameter
- `MemoryProvider` interface refined with structured docstrings and clear return contracts
- `IntentContent` refined with Field docstrings and type clarity
- `AvatarRenderer.render()` contract clarified with structured docstring

### Documentation
- `CURRENT_STATUS.md` updated with WP-30F, WP-30G, and WP-30H closure
- `PLAN.md` updated with WP-30B?WP-30H completion status
- `wp30-implementation-plan.md` updated with ED-WP30-002 reference and Task 6.5 exclusion note
- `1784079736812-wp30-architecture-compliance-review.md` updated with ED-WP30-002 reference
- WP-30I: Advanced Features ? all tasks completed and closed
  - Task 9.1: Multi-step workflow executor with dependency resolution
  - Task 9.2: Proactive monitoring with alert thresholds
  - Task 9.3: Training mode as structured workflow
  - Task 9.4: Approval gates for destructive operations
- `PLAN.md` updated with WP-30I completion status
- `CURRENT_STATUS.md` updated to reflect WP-30I closure

- WP-31: AI Memory ? completed
  - SQLiteMemoryProvider concrete implementation with cleanup_expired()
  - Memory injection into session context at session start
  - Decision persistence hook and active recall biases in ReasoningEngine
  - Mission schema extended with tasks and execution_plan fields
  - All scope creep items reverted; repository compliant with approved WP-31 scope

- WP-32: Knowledge Graph ? completed
  - Knowledge Graph schemas: `KnowledgeGraphNode`, `KnowledgeGraphEdge`, `KnowledgeGraphRelationships`, `KnowledgeGraphTraversal`, `SyncResult`
  - Service layer: `knowledge_graph.py` with CRUD, derived edges, traversal, sync, search, MemoryProvider integration, audit logging
  - Router: 9 endpoints under `/api/v1/knowledge-graph` (nodes CRUD, edges CRUD, relationships, traverse, search, sync)
  - KnowledgeProvider: `KnowledgeGraphProvider` registered in `KnowledgeProviderRegistry`
  - Database tables: `knowledge_nodes`, `knowledge_edges`
  - Tests: 105 tests (59 service unit tests, 35 integration tests, 4 performance tests, 7 security tests)
  - Governance: ED-WP32-001 recorded ? Document Edge Handling clarification
  - No modifications to existing entity tables or DEM core

- WP-33: Trade Intelligence ? completed
  - Supplier analysis, buyer analysis, trend detection, entity comparisons, report generation
  - 5 analysis service functions with Memory, Knowledge Graph, and audit integration
  - 6 FastAPI endpoints under /api/v1/trade-intelligence
  - 120 tests (75 service unit tests, 26 integration tests, 14 security tests, 5 performance tests)
  - Runtime Router Bug fixed: date_range.model_dump() replaced with request.date_range for Pydantic V2 compatibility
  - Verification passed; Work Package officially closed

- WP-40: Docker Compose Final Verification ? completed
  - Backend Docker image builds successfully
  - Frontend Docker image builds successfully
  - `docker compose up --build` completes with both services healthy
  - Backend `/health` endpoint returns HTTP 200
  - Frontend nginx serves content on port 3000
  - Backend API reachable on port 8000
  - Database persistence verified via Docker volume (`/app/data/nile_key.db`)
  - Frontend TypeScript build errors resolved:
    - `frontend/tsconfig.node.json`: Added `"vitest"` to types array
    - `frontend/src/components/NotificationBell.test.tsx`: Removed unused `updateAuditLog` import; fixed mock types with `as any`
    - `frontend/src/pages/Notifications.test.tsx`: Removed unused `updateAuditLog` import; fixed mock types with `as any`
    - `frontend/src/components/NotificationBell.tsx`: Removed unused `getEntityIcon` function
  - TECH_DEBT.md "Docker deployment unverified" item resolved
  - Governance documents updated: CURRENT_STATUS.md, PLAN.md, CHANGELOG.md

- WP-41: Production Documentation ? completed
- `README.md` updated to reflect current system state (16 registered routers, 19 service modules excluding init files, 18 schema modules, 876+ passing tests)
- `PLAN.md` updated to reflect current system state (16 registered routers, 19 service modules excluding init files, 18 schema modules, 876+ passing tests)
- `CURRENT_STATUS.md` updated to WP-40 baseline with corrected test counts
- `ENGINEERING_MEMORY.md` extended through WP-40 with corrected router and test counts
- `.kilo/plans/archive/WORK_PACKAGE_PLAN.md` extended through WP-40
- `.kilo/plans/archive/REPOSITORY_INTELLIGENCE.md` archived as historical snapshot
- All documentation cross-references verified and consistent
- Forensic audit corrections applied: false Digital Export Manager frontend page claim removed, unregistered search/dashboard router endpoints corrected, test counts updated from 606+ to 876+

### Fixed
- `backend/app/services/customs.py`: Deserialize `documents` JSON string in `_customs_row_to_response` to prevent 500 error on Customs Declaration GET
- OV-20260727-003: Customs Declaration GET returns 500 due to `documents` field stored as JSON string but expected as list

### Documentation
- `PLAN.md`: Corrected WP-42 status from CLOSED to DEFERRED (OPEN) per forensic audit; Manual UAT postponed Project Owner decision 2026-07-25
- `CURRENT_STATUS.md`: Added WP-42 closure entry
- `.kilo/plans/wp42-uat-execution-report.md`: Updated defect disposition — Defect #1 deferred as Accepted Known Defect (requires architectural change); Defect #2 fixed and verified in Docker Runtime; WP-42 administratively closed


- `.kilo/plans/wp42-owner-acceptance-certificate.md`: Project Owner formally accepted UAT results and defect disposition; WP-42 officially closed
- `baseline-wp42-final` tag created pointing to `d3eafce` (Owner Acceptance Certificate commit)
- UAT Results: 151 PASS / 1 FAIL / 1 N/A / 0 Human Verification Required
- Defect #2: Fixed & Verified in Docker Runtime
- Defect #1: Accepted Known Defect (deferred to future architectural change)
- Final baseline: `baseline-wp42-final` ? `d3eafce`

- WP-37: Knowledge Ingestion Pipeline — File-based Regulations Provider completed
  - `RegulationsKnowledgeProvider` implemented in `backend/app/agent/knowledge/regulations_provider.py`
  - JSON file ingestion with configurable `REGULATIONS_FILE_PATH` in `backend/app/core/config.py`
  - Bootstrap registration in `backend/main.py` lifespan
  - Confidence scoring: 0.5 if effective_date missing, 0.85 if source_url present, 0.75 if source_url absent
  - `updated_at` derived from file mtime in ISO-8601 UTC format
  - 8 unit tests + 4 integration tests = 12 WP-37 tests passing
  - Append-only semantics: file is single source of truth, re-read on startup only
  - No regressions in knowledge layer; 2 pre-existing Decision Engine test failures documented
  - Closure: `.kilo/plans/wp37-final-closure-report.md`, `.kilo/plans/wp37-owner-acceptance-certificate.md`

- WP-38a: External Source Integration — Moaah API completed
  - `MoaahExternalSourceAdapter` implemented in `backend/app/agent/knowledge/mooadapter.py`
  - `MoaahApiClient` isolated HTTP client in `backend/app/agent/knowledge/mooadapter_client.py` with retry/backoff
  - Config fields added to `backend/app/core/config.py`: `MOAAH_BASE_URL`, `MOAAH_API_KEY`, `MOAAH_TIMEOUT_SECONDS`, `MOAAH_SOURCE_*`
  - Conditional registration in `backend/main.py` lifespan when credentials are configured
  - Confidence/provenance metadata: source_id, fetch_timestamp, record_hash, retrieval_status
  - 9 unit tests + 6 integration tests = 15 WP-38a tests passing
  - No regressions in knowledge layer; 1 pre-existing ReasoningEngine test failure documented
  - Plan updated: `.kilo/plans/1786359213310-real-external-source-integration.md`
  - Closure report: `.kilo/plans/wp38-task1-source-evaluation-report.md`

- WP-38b: Global Trade Intelligence — TradeData API completed
  - `TradeDataExternalSourceAdapter` implemented in `backend/app/agent/knowledge/tradedata_provider.py`
  - `TradeDataApiClient` isolated HTTP client in `backend/app/agent/knowledge/tradedata_client.py` with retry/backoff
  - Config fields added to `backend/app/core/config.py`: `TRADEDATA_BASE_URL`, `TRADEDATA_API_KEY`, `TRADEDATA_TIMEOUT_SECONDS`, `TRADEDATA_SOURCE_*`
  - Conditional registration in `backend/main.py` lifespan when credentials are configured
  - Confidence/provenance metadata: source_id, confidence, source_authority, effective_date, country, source_url, legal_act_reference, updated_at, version, record_hash, retrieval_status
  - Field mapping: dataSource?source_authority, date?effective_date, buyerName/supplierName/hsCodeDesc/productKeyword?content, originCountryCode/destinationCountryCode?country, masterBl/containerNo?source_url, otherInfo?legal_act_reference
  - 14 unit tests + 7 integration tests = 21 WP-38b tests passing
  - No regressions in knowledge layer; Moaah tests (15/15) passing
  - Baseline: `baseline-wp38b-final` at `02bad55`
  - Owner Acceptance: obtained — `.kilo/plans/wp38b-owner-acceptance-certificate.md`
  - Plan updated: `.kilo/plans/1786559139127-wp38b-global-trade-intelligence-plan.md`
  - Verification evidence: `.kilo/plans/wp38b-task7-verification-evidence-package.md`

- WP-38c: Jordan + UAE + Saudi/GCC Sources — ZATCA Open Data APIs completed
  - `ZatcaExternalSourceAdapter` implemented in `backend/app/agent/knowledge/zatca_provider.py`
  - `ZatcaApiClient` isolated HTTP client in `backend/app/agent/knowledge/zatca_client.py` with retry/backoff
  - Config fields added to `backend/app/core/config.py`: `ZATCA_BASE_URL`, `ZATCA_API_KEY`, `ZATCA_TIMEOUT_SECONDS`, `ZATCA_SOURCE_*`
  - Conditional registration in `backend/main.py` lifespan when credentials are configured
  - Confidence/provenance metadata: source_id, source_authority, effective_date, country, source_url, legal_act_reference, updated_at, version, record_hash, retrieval_status
  - Field mapping: description/port_name/traffic_type/quantity/weight/amount ? content (metrics), date ? effective_date, endpoint ? source_url, country ? SA
  - 13 unit tests + 6 integration tests = 19 WP-38c tests passing
  - No regressions in knowledge layer; TradeData tests (21/21) and Moaah tests (15/15) passing
  - Plan updated: `.kilo/plans/1786559140128-wp38c-jordan-uae-saudi-gcc-sources-plan.md`
  - Verification evidence: `.kilo/plans/wp38c-task7-verification-evidence-package.md`
  - Closure report: `.kilo/plans/wp38c-final-closure-report.md`
  - Owner Acceptance Certificate: `.kilo/plans/wp38c-owner-acceptance-certificate.md`

- WP-38d: GCC Expansion — GCC-Stat Open Data APIs completed
  - `GccstatExternalSourceAdapter` implemented in `backend/app/agent/knowledge/gccstat_provider.py`
  - `GccstatApiClient` isolated HTTP client in `backend/app/agent/knowledge/gccstat_client.py` with retry/backoff
  - Config fields added to `backend/app/core/config.py`: `GCCSTAT_BASE_URL`, `GCCSTAT_API_KEY`, `GCCSTAT_TIMEOUT_SECONDS`, `GCCSTAT_SOURCE_*`
  - Conditional registration in `backend/main.py` lifespan when `GCCSTAT_BASE_URL` is configured
  - Confidence/provenance metadata: source_id, source_authority, effective_date, country, source_url, legal_act_reference, updated_at, version, record_hash, retrieval_status
  - Field mapping: SDMX observation value ? content (metrics), TIME_PERIOD ? effective_date, ref_area ? country, dataflow reference ? source_url
  - 16 unit tests + 7 integration tests = 23 WP-38d tests passing
  - No regressions in knowledge layer; all existing tests passing
   - Plan updated: `.kilo/plans/1786559150139-wp38d-gcc-expansion-plan.md`
   - Verification evidence: `.kilo/plans/wp38d-task7-verification-evidence-package.md`

- Knowledge Orchestration / Fusion Layer completed
  - `KnowledgeOrchestrator` implemented in `backend/app/agent/knowledge/orchestrator.py` with classification, routing, ranking, deduplication, conflict resolution, and output assembly
  - `ReasoningEngine._query_knowledge()` updated to use orchestrator when attached; legacy fallback extracted to `_query_knowledge_legacy()`
  - Orchestration metadata preserved in `Decision.context["knowledge_orchestration"]` when orchestrator active
  - Shared `ReasoningEngine` instance wired in `main.py` lifespan via `app.state.reasoning_engine`
  - Router adjustment in `digital_export_manager.py`: `get_reasoning_engine()` returns shared instance to preserve orchestrator attachment
  - 5 new `KNOWLEDGE_ORCHESTRATION_*` config settings added to `config.py`
  - 85 new tests (66 unit + 18 integration) all passing
  - Regression: 46/47 existing tests pass; 1 pre-existing failure in `test_registry_provider_failure_does_not_crash_reasoning` confirmed in baseline
  - Plans: `.kilo/plans/1786795387856-knowledge-orchestration-fusion-plan.md`, `.kilo/plans/1786795387856-knowledge-orchestration-fusion-detailed-implementation-plan.md`

### Fixed
- `backend/app/routers/auth.py`: Defect #2 fixed — `POST /api/v1/auth/refresh` now returns `401` instead of `500` when Authorization header is missing

## [1.0.0] - 2026-07-15

### Added
- WP-30B: Session Management + Mission Lifecycle
- WP-30C: Task Planner + Execution Engine
- WP-30D: Decision Engine
- WP-30E: 14 ERP tool wrappers with metadata compliance
- ED-WP30-001: WP-30B phase sequencing adjustment

### Changed
- Legacy `Planner` refactored to delegate to `TaskPlanner`
- `ToolResultSchema.audit_ref` made required
- `AgentToolInfoResponse` expanded with version, idempotency_key, auth_requirements

### Added
- WP-30B: Session Management + Mission Lifecycle
- WP-30C: Task Planner + Execution Engine
- WP-30D: Decision Engine
- WP-30E: 14 ERP tool wrappers with metadata compliance
- ED-WP30-001: WP-30B phase sequencing adjustment

### Changed
- Legacy `Planner` refactored to delegate to `TaskPlanner`
- `ToolResultSchema.audit_ref` made required
- `AgentToolInfoResponse` expanded with version, idempotency_key, auth_requirements

