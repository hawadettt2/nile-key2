# DEM Architecture Explorer v2 — Approved Implementation Plan

## Architectural purpose

Build the **Complete Architectural Map** as the owner's visual window into the DEM repository: a human-first Architecture Explorer, not merely a prettier diagram.

The governing architectural spine is:

```text
INTELLIGENT OPERATING PLATFORM
            ↓
DIGITAL EXPORT MANAGER
            ↓
Executive Intelligence
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
  Tools + Business Services + ERP/operational systems + Persistence
```

Repository evidence proves and refines this spine. It does not replace it with a repository-folder taxonomy.

## 1. Non-negotiable accuracy rule

The Explorer must be grounded in the actual repository and governing project documents. It must not invent architecture merely because a conventional architecture diagram would normally contain it.

Conversely, no real architectural element may disappear merely because it is small or inconvenient to draw.

The Explorer must distinguish:

- actual runtime architecture;
- implemented but non-primary paths;
- conditional/configuration-dependent paths;
- repository structure;
- planned/future architecture;
- reserved/minimal structures;
- governance/documentation concepts;
- external systems.

## 2. Architecture Explorer levels

### Level 0 — DEM Universe

Complete platform mental model: human employees, intelligent operating platform, business intent, major boundaries, and external world.

### Level 1 — Operating Platform Architecture

The primary narrative is the Intelligent Operating Platform and Digital Export Manager, followed by the Cognitive, Planning, Orchestration, and Business Systems layers.

Supporting/cross-cutting boundaries include Frontend, API, Security, Credentials, Research, Knowledge Graph, Persistence, Governance, and External Systems.

### Level 2 — Subsystem Architecture

Major subsystems open into their internal architecture. Agent internals must explicitly expose Session, Decision/Reasoning Engine, Mission/Task Planning, Execution Planning, Execution Engine, Tools/Tool Registry/Orchestration, Knowledge, Memory, LLM, Approval, Audit, Monitoring, Avatar, Interfaces, and other verified Agent packages.

Knowledge and Research remain distinct.

### Level 3 — Code Architecture

Each subsystem can be opened down to exact package/module/file/class/function identity, direct dependencies, inbound/outbound relationships, evidence, and current status.

## 3. Bilingual representation

English names remain the exact technical identity. Arabic supplies the functional meaning and explanation.

English = Identity  
Arabic = Meaning  
Code path = Evidence

## 4. Architectural boundaries

The Explorer must explain what each layer owns and what it must not own.

- Executive Intelligence: represents the executive intelligence persona through which employees interact with the platform.
- Cognitive Layer: reasoning, company knowledge, long-term memory, and LLM-assisted cognition.
- Planning Layer: converts decisions into structured missions/tasks/execution plans.
- Orchestration Layer: coordinates tools and controlled execution, including approval/audit/monitoring concerns where evidenced.
- Business Systems Layer: operational capabilities and services; it is the execution system, not the cognitive brain.
- Knowledge: governed company/external knowledge ingestion and access within the Knowledge Ingestion Contract boundary.
- Research: external research subsystem, explicitly separate from Knowledge Ingestion.

## 5. Required coverage

The final graph must account for Frontend, API/Routers/Schemas, Agent internals, Knowledge, Research, Knowledge Graph, Business Capabilities, Core Infrastructure, Security, Credentials, Audit, Monitoring, Schedulers, Persistence, External Systems, and governance boundaries where evidenced.

`backend/app/models/` must not be represented as a completed ORM/domain-model layer unless repository evidence establishes that fact.

## 6. Relationship-first design

The graph is about relationships, not boxes. Edges must distinguish structural containment, runtime/control flow, invocation/delegation, data flow, knowledge flow, memory flow, dependency, external integration, persistence, governance, audit, monitoring, security, scheduling, implementation, and future migration where evidenced.

## 7. Evidence and status

Every meaningful architectural assertion must carry evidence. Runtime claims require runtime-wiring evidence; imports, directory presence, or names alone do not prove invocation.

Supported statuses include implemented runtime, implemented non-primary, conditional, governance documented, planned future, reserved/minimal, external, and unverified where needed by the graph contract.

## 8. Canonical source model

`ARCHITECTURE_EXPLORER_V2_CANONICAL_GRAPH.json` is the canonical architecture source model. The Explorer UI is only a projection of that model.

No new per-subsystem reconciliation document should be created merely to feed the Explorer. Evidence should be consolidated into the canonical graph.

## 9. Governing evidence

At minimum reconcile against:

- `PLAN.md`
- `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`
- `CURRENT_STATUS.md`
- relevant ADRs
- actual `backend/main.py`
- actual `backend/app/**`
- actual `frontend/src/**`
- the repository's AI/agent architecture and its verified runtime implementation

Where sources conflict, preserve the distinction and identify the authoritative source rather than silently choosing.

## 10. Business narrative

The Explorer must preserve the business intent narrative while distinguishing it from a verified runtime execution path:

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

## 11. Acceptance criterion

The work is complete only when the owner can enter Level 0 and progressively answer through one connected model:

- What is DEM?
- Why is it an Intelligent Operating Platform rather than an ERP with AI features?
- What is Digital Export Manager?
- What happens when a human asks it to do something?
- Where does reasoning happen?
- Where does company knowledge come from?
- Where is memory used/stored?
- How does planning become execution?
- How does execution reach business capabilities?
- Where are approval, audit, security, monitoring, and credentials involved?
- Where does data persist?
- Which systems are external?
- What is implemented now versus planned/reserved?
- Where exactly is each capability implemented in the repository?

## 12. Implementation discipline

This plan governs the Complete Architectural Map/Explorer only. It does not authorize unrelated runtime application changes.

The implementation sequence is:

```text
Architectural Spine
    ↓
Evidence Mapping
    ↓
Canonical Graph
    ↓
Graph Validation
    ↓
Explorer Engine
    ↓
Level 0–3 Explorer UI
    ↓
Owner Acceptance Review
```

The canonical graph is the architecture source of truth; the UI must never become the source of architectural knowledge.
