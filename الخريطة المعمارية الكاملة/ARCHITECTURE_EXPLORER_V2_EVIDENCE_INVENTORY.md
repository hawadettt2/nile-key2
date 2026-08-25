# DEM Architecture Explorer v2 — Evidence Inventory

**Purpose:** evidence baseline for the Complete Architectural Map.  
**Repository:** `hawadettt2/nile-key2`  
**Branch:** `main`  
**Runtime impact:** none.

## Architectural spine

The evidence must be organized around the Intelligent Operating Platform architecture rather than around repository folders:

```text
Human Employees
        ↓
Digital Export Manager — Executive Intelligence
        ↓
Cognitive Layer
  Reasoning + Company Knowledge + Long-Term Memory + LLM
        ↓
Planning Layer
  Task Planner + Execution Planner
        ↓
Orchestration Layer
  Tool Orchestrator + Tool Registry + Approval + Audit + Monitoring
        ↓
Business Systems Layer
  Tools + Business Services + operational systems + Persistence
```

## Governing evidence

- `PLAN.md`
- `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`
- `CURRENT_STATUS.md`
- relevant ADRs
- `backend/main.py`
- `backend/app/**`
- `frontend/src/**`
- repository AI/Agent architecture and its implementation evidence

## Verified repository boundaries

### Agent

`backend/app/agent/` contains dedicated areas for approval, audit, avatar, core, decision engine, execution engine, execution planner, interfaces, knowledge, LLM, memory, mission planner, monitoring, schemas, session, tools, training, and exceptions.

The verified Digital Export Manager integration path is:

```text
Session
 → ReasoningEngine
 → TaskPlanner
 → ExecutionPlanner
 → ToolOrchestrator / Tool Registry
 → Agent Tools
 → Business Services
```

The graph must still distinguish primary runtime, implemented non-primary, and conditional paths where bootstrap/configuration evidence requires it.

### Core Infrastructure

`backend/app/core/` contains configuration, credentials, CSRF, database, schedulers, and security. These are explicit cross-cutting infrastructure boundaries.

### API

`backend/app/routers/` and `backend/app/schemas/` form an API boundary distinct from downstream services and agent execution.

### Knowledge

Knowledge Ingestion is bounded by the External Knowledge Ingestion Contract. It must remain distinct from Research, Reasoning, Execution, LLM orchestration, and other excluded concerns.

### Research

`backend/app/research/` is an implemented subsystem with orchestration, retrieval, sources, evidence, quality, and results. It remains distinct from Knowledge Ingestion.

### Knowledge Graph

Knowledge Graph is an explicit capability/subsystem and must be connected to Knowledge, Memory, and Reasoning only where repository evidence supports the relationship.

### Business capabilities

Actual services include Export Readiness, Trade Intelligence, Knowledge Graph, Customs, Shipping, ETA, Invoice, Customers, Suppliers, Documents, Notifications, Dashboard, Search, Resource, Workflow, and other verified services. Capability identity must be distinguished from router and service implementation identity.

### Persistence

Current runtime persistence is SQLite through `backend/app/core/database.py`. `backend/app/models/` must not be represented as a complete ORM/domain layer without evidence. PostgreSQL is a documented future migration path, not current runtime.

### Frontend

`frontend/src/` contains components, hooks, lib, locales, pages, services, store, test, and types. The frontend is part of the platform boundary but is not the executive intelligence itself.

## Cross-cutting concerns

Authentication/roles, security, CORS/CSRF, credentials, audit, monitoring, scheduling, configuration, schemas/contracts, evidence/provenance where implemented, and external integrations must remain discoverable.

## Modeling discipline

- Repository structure is evidence, not the architecture itself.
- Import is not invocation.
- Directory presence is not runtime wiring.
- Tool is not Business Service.
- Knowledge is not Research.
- LLM is not the whole Agent.
- Future architecture is not current runtime.
- Modular services do not imply microservices.
- English technical names remain exact.

This inventory is evidence for the canonical graph; it is not intended to become another parallel architecture document.
