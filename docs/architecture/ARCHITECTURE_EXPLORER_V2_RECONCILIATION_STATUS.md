# DEM Architecture Explorer v2 — Reconciliation Status

Date: 2026-08-25

## Purpose

This document records the evidence-driven reconciliation pass against the approved V2 plan. It is a status/evidence artifact only and does not alter application runtime behavior.

## Current finding

The repository evidence currently available through the verified architecture artifacts is sufficient to continue the graph construction, but not sufficient to claim that the canonical graph is complete.

The following distinctions remain mandatory:

- repository presence != primary runtime wiring;
- documented architecture != implemented runtime;
- business capability existence != proof of Agent invocation;
- planned persistence != current persistence;
- Knowledge != Research.

## Reconciled coverage

### Agent path

Verified implementation identities include:

- Session
- ReasoningEngine
- TaskPlanner
- ExecutionPlanner
- ToolOrchestrator
- ToolRegistry
- concrete Agent Tools
- Business Service targets used by concrete tools
- Knowledge integration
- Memory
- LLM integration
- Approval

Primary-runtime status remains conservative for planner/execution/tool components where bootstrap evidence is not established.

### Agent cross-cutting

Audit, Monitoring, Avatar, Interfaces, and remaining Agent packages require explicit repository evidence before canonicalization. No node is invented merely because the plan requires a category.

### API / Routers / Schemas

These remain a dedicated reconciliation pass. `backend/main.py` is authoritative for application bootstrap relationships; router/schema existence must be traced to exact files and registration points before runtime edges are claimed.

### Core Infrastructure

The current evidence establishes SQLite as runtime persistence and PostgreSQL as a documented future migration path. Configuration, CredentialStore/credentials, security, CSRF, database, schedulers, and other core modules require individual evidence records and runtime-wiring classification.

### Knowledge / Research

Knowledge and Research remain separate architectural boundaries. Knowledge provider/registry/orchestration evidence must be reconciled against the governing Knowledge Ingestion Contract. Research retrieval/source/evidence/quality components must not be absorbed into Knowledge.

### Knowledge Graph

Knowledge Graph requires explicit node/edge evidence and supported relationships to Knowledge, Memory, and Reasoning. It must not be inferred solely from service naming.

### Business capabilities

Business Services must be decomposed into individually discoverable capabilities. The existing evidence identifies service areas such as shipping, customs, invoice, customer, supplier, document, workflow, notification, resources, trade intelligence, export readiness, knowledge graph, audit, dashboard, and search; each requires final identity/status/evidence reconciliation.

### External systems

External knowledge providers and other external integrations must be represented according to their actual architectural role and evidence, with external status kept distinct from internal runtime components.

## Canonicalization gate

The canonical graph must not be merged/finalized until:

1. every required category has either verified nodes or an explicit documented absence;
2. every runtime edge has implementation evidence;
3. planned/future structures are separated from runtime;
4. business capabilities have individual identities;
5. orphan nodes and contradictory status claims are validated;
6. the graph can support Level 0 through Level 3 navigation without requiring UI-specific hidden knowledge.

## Next execution order

1. Complete exact-file reconciliation for API/Routers/Schemas and Core/Security/Credentials.
2. Complete Knowledge, Research, and Knowledge Graph evidence.
3. Complete Business Capability and External System inventory.
4. Merge graph fragments into the canonical dataset.
5. Run graph validation.
6. Only then implement Explorer Engine and UI.
