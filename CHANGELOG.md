# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- WP-30F: Company Knowledge Layer interface definitions
  - `KnowledgeProvider` ABC with `query()` and `get_sources()` methods
  - `KnowledgeQuery` Pydantic schemas (`AgentKnowledgeQueryRequest`, `AgentKnowledgeQueryResponse`)
  - `KnowledgeProviderRegistry` with register, unregister, get, list, exists, query
  - Knowledge Ingestion Contract document (`.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`)
- 17 new unit tests for knowledge layer (`tests/agent/test_knowledge.py`)
- ED-WP30-002: WP-30F scope clarification (Tasks 6.1–6.4 only)
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
- `PLAN.md` updated with WP-30B–WP-30H completion status
- `wp30-implementation-plan.md` updated with ED-WP30-002 reference and Task 6.5 exclusion note
- `1784079736812-wp30-architecture-compliance-review.md` updated with ED-WP30-002 reference
- WP-30I: Advanced Features — all tasks completed and closed
  - Task 9.1: Multi-step workflow executor with dependency resolution
  - Task 9.2: Proactive monitoring with alert thresholds
  - Task 9.3: Training mode as structured workflow
  - Task 9.4: Approval gates for destructive operations
- `PLAN.md` updated with WP-30I completion status
- `CURRENT_STATUS.md` updated to reflect WP-30I closure

- WP-31: AI Memory — completed
  - SQLiteMemoryProvider concrete implementation with cleanup_expired()
  - Memory injection into session context at session start
  - Decision persistence hook and active recall biases in ReasoningEngine
  - Mission schema extended with tasks and execution_plan fields
  - All scope creep items reverted; repository compliant with approved WP-31 scope

- WP-32: Knowledge Graph — completed
  - Knowledge Graph schemas: `KnowledgeGraphNode`, `KnowledgeGraphEdge`, `KnowledgeGraphRelationships`, `KnowledgeGraphTraversal`, `SyncResult`
  - Service layer: `knowledge_graph.py` with CRUD, derived edges, traversal, sync, search, MemoryProvider integration, audit logging
  - Router: 9 endpoints under `/api/v1/knowledge-graph` (nodes CRUD, edges CRUD, relationships, traverse, search, sync)
  - KnowledgeProvider: `KnowledgeGraphProvider` registered in `KnowledgeProviderRegistry`
  - Database tables: `knowledge_nodes`, `knowledge_edges`
  - Tests: 105 tests (59 service unit tests, 35 integration tests, 4 performance tests, 7 security tests)
  - Governance: ED-WP32-001 recorded — Document Edge Handling clarification
  - No modifications to existing entity tables or DEM core

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
