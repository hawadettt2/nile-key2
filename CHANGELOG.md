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
  - Research Lifecycle Orchestrator with 7 stages (Planning → Discovery → Retrieval → Processing → Evidence Capture → Structuring → Verification)
  - Source Registry & Discovery with preference-based and scope-based discovery
  - Retrieval Abstraction with multi-source isolation and Content Processor
  - Evidence & Provenance Capture with deterministic provenance records
  - Result Structuring & Output with Evidence → Finding → ResearchResult chain
  - Verification/Quality/Failure Handling with deterministic quality checks and partial/failed result support
  - 103 WP-34 tests passing; no regressions in existing 30 related tests

- Documentation Consolidation & SSOT — completed
  - `PLAN.md` restructured as Single Source of Truth (1,746 lines, 27 sections)
  - 6 new sections added: 22�27 (System State, Execution Governance, Deployment, Repository Architecture, Decision Index, Appendices)
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
- ED-WP30-002: WP-30F scope clarification (Tasks 6.1�6.4 only)
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
- `PLAN.md` updated with WP-30B�WP-30H completion status
- `wp30-implementation-plan.md` updated with ED-WP30-002 reference and Task 6.5 exclusion note
- `1784079736812-wp30-architecture-compliance-review.md` updated with ED-WP30-002 reference
- WP-30I: Advanced Features � all tasks completed and closed
  - Task 9.1: Multi-step workflow executor with dependency resolution
  - Task 9.2: Proactive monitoring with alert thresholds
  - Task 9.3: Training mode as structured workflow
  - Task 9.4: Approval gates for destructive operations
- `PLAN.md` updated with WP-30I completion status
- `CURRENT_STATUS.md` updated to reflect WP-30I closure

- WP-31: AI Memory � completed
  - SQLiteMemoryProvider concrete implementation with cleanup_expired()
  - Memory injection into session context at session start
  - Decision persistence hook and active recall biases in ReasoningEngine
  - Mission schema extended with tasks and execution_plan fields
  - All scope creep items reverted; repository compliant with approved WP-31 scope

- WP-32: Knowledge Graph � completed
  - Knowledge Graph schemas: `KnowledgeGraphNode`, `KnowledgeGraphEdge`, `KnowledgeGraphRelationships`, `KnowledgeGraphTraversal`, `SyncResult`
  - Service layer: `knowledge_graph.py` with CRUD, derived edges, traversal, sync, search, MemoryProvider integration, audit logging
  - Router: 9 endpoints under `/api/v1/knowledge-graph` (nodes CRUD, edges CRUD, relationships, traverse, search, sync)
  - KnowledgeProvider: `KnowledgeGraphProvider` registered in `KnowledgeProviderRegistry`
  - Database tables: `knowledge_nodes`, `knowledge_edges`
  - Tests: 105 tests (59 service unit tests, 35 integration tests, 4 performance tests, 7 security tests)
  - Governance: ED-WP32-001 recorded � Document Edge Handling clarification
  - No modifications to existing entity tables or DEM core

- WP-33: Trade Intelligence � completed
  - Supplier analysis, buyer analysis, trend detection, entity comparisons, report generation
  - 5 analysis service functions with Memory, Knowledge Graph, and audit integration
  - 6 FastAPI endpoints under /api/v1/trade-intelligence
  - 120 tests (75 service unit tests, 26 integration tests, 14 security tests, 5 performance tests)
  - Runtime Router Bug fixed: date_range.model_dump() replaced with request.date_range for Pydantic V2 compatibility
  - Verification passed; Work Package officially closed

- WP-40: Docker Compose Final Verification � completed
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

- WP-41: Production Documentation � completed
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

