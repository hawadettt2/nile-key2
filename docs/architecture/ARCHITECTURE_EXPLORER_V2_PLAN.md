# DEM Architecture Explorer v2 — Approved Implementation Plan

## Purpose

Build a **human-first Architecture Explorer**, not merely a prettier diagram. The objective is to make the repository architecture itself understandable as a connected mental model: what each subsystem does, why it exists, what it depends on, what depends on it, what enters it, what leaves it, and where the exact implementation lives.

The governing principle is:

> **Build a map that lets the human and the architect understand the project itself.**

This plan is approved as the implementation baseline for the next architecture-documentation iteration.

---

## 1. Non-negotiable accuracy rule

The Explorer must be grounded in the **actual repository and governing project documents**. It must not invent architecture merely because a conventional architecture diagram would normally contain it.

Conversely, no real architectural element should disappear merely because it is small or inconvenient to draw.

### Rule

> **No real architectural element may be absent from the Explorer without having a known place at one of its levels.**

The Explorer must distinguish:

- actual runtime architecture;
- repository structure;
- planned/future architecture;
- reserved/minimal structures;
- governance/documentation concepts.

Example: `backend/app/models/` must not be presented as a completed ORM/domain-model layer if the current runtime does not implement it that way.

---

## 2. Architecture Explorer levels

The Explorer will use four progressive levels instead of forcing the entire system into one diagram.

### Level 0 — DEM Universe

The complete platform mental model:

- Business / user intent
- Platform / application
- External world
- major boundaries and relationships

### Level 1 — System Architecture

High-level runtime architecture:

- Business Experience
- Frontend
- API boundary
- Backend application
- Agent
- Business Services
- Knowledge
- Research
- Core Infrastructure
- Persistence
- External integrations

### Level 2 — Subsystem Architecture

Clicking a major subsystem opens its internal architecture.

At minimum, the Agent view must explicitly expose:

- Session
- Decision Engine
- Mission Planner
- Execution Planner
- Execution Engine
- Tools / Tool Registry
- Knowledge
- Memory
- LLM
- Approval
- Audit
- Monitoring
- Avatar
- Interfaces
- related core/orchestration components discovered during repository verification

Knowledge and Research must remain distinct.

### Level 3 — Code Architecture

Each subsystem can be opened down to implementation identity:

- exact package/module
- exact file path
- important classes/functions
- direct dependencies
- inbound/outbound relationships
- inputs/outputs where meaningful
- current runtime status

Example target path:

`Execution Engine → Tool Registry → ShippingCreateShipmentTool → services.shipping.create_shipment()`.

---

## 3. Bilingual representation

English names remain the **exact technical identity**.

Arabic is added as the **functional meaning**, not as a replacement.

Preferred node format:

```text
Agent Orchestration
تنسيق وتشغيل الوكيل
```

On selection, the detail panel must provide:

1. English technical name
2. Arabic functional meaning
3. Arabic deep explanation
4. role in the architecture
5. inbound relationships
6. outbound relationships
7. dependencies
8. dependents
9. exact repository path(s)
10. runtime/planned status when relevant

Thus:

> English = Identity
>
> Arabic = Meaning
>
> Code path = Evidence

---

## 4. Required architecture coverage

The Explorer must explicitly account for, at minimum, the following areas identified during the repository/governance review.

### Application / API

- Frontend
- HTTP/API boundary
- FastAPI application entry point
- Routers
- Schemas / API contracts
- application wiring

### Agent

Do not collapse the Agent into one box. Explicitly model:

- session
- decision engine
- mission planner
- execution planner
- execution engine
- tools
- tool registry/orchestration
- knowledge integration
- memory
- LLM integration
- approval
- audit
- monitoring
- avatar
- interfaces
- other actual Agent packages discovered during implementation verification

### Business capabilities

Explicitly preserve major business capabilities rather than hiding them in a generic `services` box, including:

- Export Readiness
- Trade Intelligence
- Knowledge Graph
- Customs
- Shipping
- Invoice
- Customer
- Supplier
- Document
- Notification
- Resource
- Dashboard
- Workflow
- other actual services discovered during final inventory

### Knowledge

Model the knowledge subsystem as an actual architecture, not a provider list only:

- provider identity/registry
- Knowledge Orchestrator
- normalization
- evidence/provenance where implemented
- quality/governance boundaries
- provider adapters
- external knowledge sources
- relationship to Reasoning

The External Knowledge Ingestion Contract must remain authoritative for the ingestion boundary.

### Research

Keep Research separate from Knowledge Ingestion.

Represent, where actually implemented:

- retrieval
- sources
- evidence
- verification
- quality
- research-specific orchestration

Do not imply that Research and Knowledge Ingestion are the same subsystem.

### Knowledge Graph

Show Knowledge Graph explicitly and show its relationships with Knowledge, Memory, and Reasoning where supported by the repository.

### Core Infrastructure

Do not hide Core as an unnamed implementation detail. Explicitly account for actual infrastructure such as:

- configuration
- credentials / CredentialStore
- security
- CSRF
- database
- schedulers
- other actual core infrastructure modules

### Persistence / Models

Show the actual current persistence architecture accurately.

Do not depict a complete ORM/domain-model layer unless the repository actually implements one.

Clearly distinguish:

- current SQLite runtime
- actual database access implementation
- `models/` current status
- any future/bounded migration path such as PostgreSQL if documented

### External systems

Show external knowledge providers and other external systems separately where their architectural role differs.

### Governance / Audit / Security / Observability

Do not lose cross-cutting concerns merely because they cross multiple layers. Where they are real repository capabilities, make them discoverable and explain their relationships.

---

## 5. Relationship-first design

The Explorer must prioritize **relationships**, not boxes.

Every meaningful node should answer:

- Who calls me?
- Who do I call?
- What data/knowledge crosses the boundary?
- What responsibility do I own?
- What responsibility do I explicitly not own?

Edges should be semantically distinguishable where practical, for example:

- runtime/control flow
- data flow
- knowledge flow
- external integration
- dependency
- governance/audit relationship

---

## 6. Interaction model

The user must be able to:

- click nodes;
- drill down into subsystems;
- return to the parent level;
- search by English technical name;
- search by Arabic meaning;
- search by repository path/module;
- highlight relationships;
- reset focus;
- switch between major perspectives such as business flow, runtime flow, and code map.

The detail panel is part of the architecture model, not an afterthought.

---

## 7. Business mental model

The Explorer must preserve the DEM business path as the central narrative:

```text
Product
  ↓
HS Code / Product Understanding
  ↓
Target Market
  ↓
External Knowledge
  ↓
Trade Intelligence
  ↓
Export Readiness
  ↓
Risk / Requirements / Opportunities
  ↓
Decision / Report / Action
```

The exact sequence must be reconciled with the current repository implementation before being labeled as a runtime execution path. It may be presented as the **business intent / capability narrative** where appropriate.

---

## 8. Evidence and status labels

Nodes must be able to distinguish:

- **Implemented / Runtime**
- **Implemented but not primary runtime path**
- **Documented / Governance**
- **Planned / Future**
- **Reserved / Minimal**
- **External**

This is essential to prevent the Explorer from confusing architectural intent with current implementation.

---

## 9. Governing documentation

Before finalizing the Explorer, implementation must reconcile the map against the repository and governing documentation, including at minimum:

- `PLAN.md`
- `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`
- `CURRENT_STATUS.md`
- relevant architecture/ADR documents
- actual `backend/app` and `frontend/src` structure
- actual application wiring in `backend/main.py`

Where a conflict exists, do not silently choose one. Mark the distinction and identify the authoritative source according to project governance.

---

## 10. What this plan explicitly rejects

The following are **not** acceptable substitutes for the Explorer:

- a prettier static diagram;
- a simple folder tree;
- a generic microservices diagram;
- invented ORM/domain layers;
- collapsing Agent into one box;
- collapsing Knowledge and Research into one box;
- replacing English technical names with Arabic translations;
- hiding small but real subsystems;
- presenting future architecture as current runtime architecture.

---

## 11. Acceptance criterion

The work is complete only when a human can enter at Level 0 and progressively answer, without reconstructing the system mentally from disconnected documents:

> What is DEM?
>
> What happens when a user asks it to do something?
>
> Which layer receives the request?
>
> Where does reasoning happen?
>
> Where does knowledge come from?
>
> Where is memory kept?
>
> How does execution reach business capabilities?
>
> Where are approvals, audit, security, monitoring, and credentials involved?
>
> Where does data persist?
>
> Which systems are external?
>
> What is actually implemented today versus planned?
>
> Where exactly is each capability implemented in the repository?

The final Explorer should make these answers visible through one connected model rather than requiring the user to assemble them from separate diagrams.

---

## 12. Implementation discipline

This document is the approved plan for **documentation/architecture visualization only**. It does not authorize unrelated application changes.

Implementation must be evidence-driven and must not alter runtime behavior merely to make the architecture diagram easier to draw.
