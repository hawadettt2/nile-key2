# DEM Architecture Explorer v2 — Evidence Inventory

## Status

**Phase:** 0 — Architecture Evidence Inventory  
**Purpose:** Establish the evidence base before implementing the interactive Explorer.  
**Runtime impact:** None. Documentation-only.  
**Repository:** `hawadettt2/nile-key2`  
**Branch:** `main`  

## Governing evidence reviewed

- `PLAN.md` — master roadmap / architecture philosophy / capability map.
- `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md` — knowledge/ingestion boundary.
- `CURRENT_STATUS.md` — implemented Work Packages and current runtime status.
- `docs/architecture/ADR-0001-shipments-legacy-columns.md`.
- `docs/architecture/ADR-0002-postgresql-migration-path.md`.
- Actual `backend/main.py` application wiring.
- Actual `backend/app/**` repository structure.
- Actual `frontend/src/**` repository structure.

## Confirmed top-level application structure

```text
backend/
  main.py
  app/
    agent/
    core/
    models/
    research/
    routers/
    schemas/
    services/

frontend/
  src/
    components/
    hooks/
    lib/
    locales/
    pages/
    services/
    store/
    test/
    types/
```

The backend directory structure is confirmed directly from the repository. `app/models/` exists but is currently minimal; the Explorer must not present it as a completed ORM/domain-model implementation. fileciteturn34file0

The frontend contains explicit `components`, `hooks`, `lib`, `locales`, `pages`, `services`, `store`, `test`, and `types` areas. fileciteturn42file0

## Agent evidence

The actual `backend/app/agent` tree contains, among other items:

- `approval/`
- `audit/`
- `avatar/`
- `core/`
- `decision_engine/`
- `execution_engine/`
- `execution_planner/`
- `interfaces/`
- `knowledge/`
- `llm/`
- `memory/`
- `mission_planner/`
- `monitoring/`
- `schemas/`
- `session/`
- `tools/`
- `training/`
- `exceptions.py`

These must not be collapsed into a single undifferentiated Agent box in Level 2. fileciteturn35file0

The verified Digital Export Manager execution path is:

```text
Session
  → ReasoningEngine
  → TaskPlanner
  → ExecutionPlanner
  → ToolOrchestrator
  → Tool Registry
  → Tools
  → Business Services
  → Result / Mission State / Audit
```

This flow is evidenced by `backend/app/routers/digital_export_manager.py` and the agent implementation. fileciteturn22file0

`ReasoningEngine` explicitly consumes knowledge and memory and can use the configured LLM provider as an enhancement/fallback mechanism. fileciteturn23file0

`ToolOrchestrator` performs structured execution with dependencies, approval, retry/idempotency behavior, monitoring, and execution trace handling. fileciteturn24file0

## Agent Tools evidence

`backend/app/agent/tools/` contains:

- `base.py`
- `erp_tools.py`
- `registry.py`
- test tooling

Tools are not the same thing as Business Services. For example, the shipping creation tool delegates to `app.services.shipping.create_shipment()`. fileciteturn25file0 fileciteturn26file0

Therefore the Explorer must visually distinguish:

```text
Agent Tools
      ↓
Business Services
      ↓
Persistence / External Integration
```

## Core Infrastructure evidence

`backend/app/core/` explicitly contains:

- `config.py`
- `credentials/`
- `csrf.py`
- `database.py`
- `eta_scheduler.py`
- `security.py`
- `shipping_scheduler.py`

This is a genuine infrastructure boundary and must be represented explicitly. fileciteturn36file0

## Persistence evidence

The current runtime database implementation uses SQLite through `backend/app/core/database.py` and `sqlite3`.

`backend/app/models/` exists, but the current repository evidence does not justify drawing a fully implemented ORM/domain-model layer.

The accepted PostgreSQL ADR defines a bounded future migration path while keeping SQLite as the current unchanged runtime. fileciteturn17file0 fileciteturn21file0

Explorer requirement:

```text
Persistence
├── Current runtime: SQLite
├── Current access: core/database.py
├── Models status: minimal/reserved
└── Future path: bounded PostgreSQL migration
```

## Router/API evidence

`backend/app/routers/` is a substantial architectural boundary, not merely a generic HTTP box. Confirmed routers include, among others:

- `agent.py`
- `audit.py`
- `auth.py`
- `customers.py`
- `customs.py`
- `dashboard.py`
- `digital_export_manager.py`
- `documents.py`
- `eta.py`
- `export_readiness.py`
- `invoice.py`
- `knowledge_graph.py`
- `notifications.py`

The Explorer must preserve the distinction between API routing and downstream application/service logic. fileciteturn40file0

## Service evidence

`backend/app/services/` contains, at minimum:

- `audit.py`
- `base.py`
- `customer.py`
- `customs.py`
- `dashboard.py`
- `document.py`
- `eta/`
- `export_readiness.py`
- `invoice.py`
- `knowledge_graph.py`
- `notification.py`
- `resource.py`
- `search.py`
- `shipping.py`
- `shipping/`
- `supplier.py`
- `trade_intelligence.py`
- `workflow.py`

These are real implementation capabilities and must not be reduced to a single generic Services box at subsystem/code levels. fileciteturn41file0

## Business capability evidence

`CURRENT_STATUS.md` records completed capabilities including:

- Export Readiness
- Trade Intelligence
- Knowledge Graph
- Customs
- Shipping
- ETA / Invoice
- Suppliers
- Customers
- Documents
- Notifications
- Dashboard / Search
- Export workflow
- Digital Export Manager
- AI Memory
- External Research
- Credential Management

The Explorer must distinguish capability concepts from their exact service/router implementations.

## Knowledge architecture boundary

The Knowledge Ingestion Contract establishes that Knowledge Ingestion is bounded to:

- reading/importing external knowledge
- transforming to the provider query shape
- metadata/versioning
- registration through `KnowledgeProviderRegistry`
- append-only/version-aware updates
- zero changes to DEM core

It explicitly excludes:

- External Research
- Business Analysis
- Plan Generation
- Execution
- Reasoning
- LLM Orchestration
- Evidence Verification
- detailed provenance tracking
- advanced knowledge quality scoring
- deduplication

Therefore the Explorer must keep Knowledge Ingestion, Research, Reasoning, Execution, and LLM orchestration visually separate. fileciteturn32file0

## Research architecture evidence

`backend/app/research/` contains:

- `orchestrator.py`
- `quality.py`
- `result.py`
- `retrieval/`
- `sources/`
- `evidence/`

This is an implemented Research subsystem, distinct from Knowledge Ingestion. fileciteturn13file0

## Frontend evidence

The actual frontend structure includes:

- root application files
- `components/`
- `hooks/`
- `lib/`
- `locales/`
- `main.tsx`
- `pages/`
- `services/`
- `store/`
- `test/`
- `types/`

The Explorer must therefore not represent the frontend as only "pages" or only "components". fileciteturn42file0

## Cross-cutting concerns to preserve

The final Explorer must make discoverable:

- authentication / roles
- security
- CORS / CSRF
- credentials / CredentialStore
- audit
- monitoring
- scheduling
- configuration
- API schemas/contracts
- logging/quality/evidence where actually implemented

## Status semantics

Every Explorer node must eventually be able to distinguish:

- Implemented / Runtime
- Implemented but not primary runtime path
- Governance / Contract
- Planned / Future
- Reserved / Minimal
- External

## Known modeling traps to avoid

1. Do not draw Microservices merely because the project has many service modules. Current architecture remains a modular monolith-oriented application.
2. Do not draw `models/` as a complete ORM/domain layer.
3. Do not collapse Agent into one box.
4. Do not collapse Knowledge and Research.
5. Do not treat LLM as the complete Agent.
6. Do not treat Tools as Business Services.
7. Do not treat external provider adapters as direct frontend dependencies.
8. Do not present future PostgreSQL migration as the current runtime.
9. Do not replace English technical identities with translated names.
10. Do not use the visual diagram as evidence when repository code and governing documents disagree.

## Phase 0 result

**Evidence baseline established.**

The next implementation stage is the **Architecture Graph/Data Model**: define the node/edge/status schema that will drive all four Explorer levels, rather than hard-coding architecture directly into a visual SVG. This keeps the architecture content inspectable, searchable, bilingual, and maintainable.
