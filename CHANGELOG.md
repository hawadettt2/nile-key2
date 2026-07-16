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

### Changed
- `AgentKnowledgeQueryRequest` now includes `context` and `scope` fields
- `AgentKnowledgeQueryResponse` now includes `confidence` and `sources` fields
- `KnowledgeProvider.query()` signature extended with `scope` parameter

### Documentation
- `CURRENT_STATUS.md` updated with WP-30F closure
- `PLAN.md` updated with WP-30B–WP-30F completion status
- `wp30-implementation-plan.md` updated with ED-WP30-002 reference and Task 6.5 exclusion note
- `1784079736812-wp30-architecture-compliance-review.md` updated with ED-WP30-002 reference

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
