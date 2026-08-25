# DEM Architecture Explorer v2 — Canonical Architecture Graph Schema

**Purpose:** canonical data contract for the Complete Architectural Map.  
**Runtime impact:** none.  
**Principle:** the graph is the architecture source model; UI is only a projection.

## Core rules

1. Evidence is authoritative.
2. English technical identity is preserved exactly; Arabic is functional meaning.
3. Nodes and edges are first-class architecture knowledge.
4. Runtime and planned/future states must never be conflated.
5. Unknown/unverified is preferable to invention.
6. Repository presence alone does not prove runtime wiring.
7. Knowledge and Research remain distinct.
8. Agent Tools and Business Services remain distinct.
9. Current SQLite persistence and future PostgreSQL migration remain distinct.
10. No Explorer UI element may become the source of architectural truth.

## Node contract

```text
Node
├── id
├── technical_name
├── arabic_meaning
├── arabic_description
├── type
├── levels[]
├── status
├── responsibilities[]
├── non_responsibilities[]
├── paths[]
├── evidence[]
├── parent_ids[]
├── tags[]
└── metadata
```

Required architectural types include: universe, business_boundary, application, frontend, api_boundary, backend, router, schema_contract, agent_subsystem, agent_tool, orchestration, knowledge, research, business_capability, business_service, core_infrastructure, security, credential_management, audit, monitoring, scheduler, persistence, database, model_structure, external_system, governance, planned_architecture, reserved_structure.

## Status contract

- `implemented_runtime`
- `implemented_non_primary`
- `conditional`
- `governance_documented`
- `planned_future`
- `reserved_minimal`
- `external`
- `unverified`

## Evidence contract

```text
EvidenceRef
├── kind
├── path
├── detail
└── authority
```

Evidence kinds: repository_file, repository_directory, governance_document, adr, runtime_wiring, external_reference.

## Edge contract

```text
Edge
├── id
├── source
├── target
├── relation_type
├── direction
├── status
├── evidence[]
├── data
└── metadata
```

Important relation types: contains, exposes, routes_to, control_flow, invokes, delegates_to, depends_on, produces, data_flow, knowledge_flow, memory_flow, external_integration, persists_to, reads_from, writes_to, governed_by, audited_by, monitored_by, secured_by, scheduled_by, implements, planned_migration_to.

## Level projection

**L0:** DEM Universe and major boundaries.  
**L1:** Intelligent Operating Platform, Digital Export Manager, Cognitive/Planning/Orchestration/Business Systems and major supporting boundaries.  
**L2:** internal subsystem architecture.  
**L3:** exact repository implementation identity.

A node may legitimately appear at multiple levels; level is a presentation projection, not a change of identity.

## Required validation

- unique node IDs;
- unique edge IDs;
- all edge endpoints exist;
- every asserted node/edge has evidence;
- implemented nodes have repository/runtime evidence;
- future nodes/edges have governance/ADR evidence;
- no inferred invocation without call-site/runtime evidence;
- `contains` means structure, not runtime call;
- future migration is never current runtime flow;
- Knowledge ≠ Research;
- Tools ≠ Business Services;
- SQLite ≠ PostgreSQL current runtime;
- exhaustive coverage is not claimed until reconciliation is complete.
