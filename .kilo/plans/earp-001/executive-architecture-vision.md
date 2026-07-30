# Executive Architecture Vision

**Plan:** EARP-001  
**Document:** Executive Architecture Vision  
**Status:** Draft — Pending Executive Approval  
**Authority:** This document is the highest-level architectural reference for EARP-001. All subsequent phases must conform to it.  

---

## 1. What Is the Actual Product?

The Nile Key Platform is an **Intelligent Operating Platform** for export operations. It is not a chatbot, not a generic AI assistant, and not a collection of disconnected microservices.

The platform provides a persistent, session-based digital workspace owned by the company, in which structured export missions are created, reasoned about, planned, executed, and audited through a governed loop that combines internal intelligence with external ERP tool contracts.

The product is the **Digital Export Manager (DEM)**.

---

## 2. What Is the Intelligent Operating Platform?

The **Intelligent Operating Platform** is the underlying substrate that hosts the Digital Export Manager and the bounded contexts it coordinates.

It provides:
- Session and mission lifecycle management
- Reasoning and decision infrastructure
- Memory and knowledge substrate
- Tool orchestration and execution
- ERP entity services (ETA, Shipping, Customs, Invoices, Documents, Resources, Customers, Suppliers)
- Audit, notification, and governance hooks

The platform is operationally persistent. It survives across sessions, deployments, and personnel turnover through its Memory Layer.

---

## 3. Who Is the Digital Export Manager?

The **Digital Export Manager (DEM)** is the **Executive Intelligence** layer of the platform.

- The DEM is the **product**.
- The DEM is the **platform**.
- The DEM is the **root bounded context**.

The DEM is not an Agent sitting on top of ERP. The DEM is the executive layer that owns export operations, coordinates internal intelligence subsystems, and presents a business façade to users and to ERP tool contracts.

Users connect to the DEM, operate within a Persistent Digital Export Session, and submit structured Missions.

---

## 4. What Is the Root Bounded Context?

The **Digital Export Manager** is the root bounded context.

All other bounded contexts are either:
- Internal subsystems of the DEM (Reasoning Engine, Task Planner, Execution Planner, Tool Orchestrator), or
- Independent bounded contexts consumed by the DEM (Long-Term Memory, Company Knowledge, Knowledge Graph, Trade Intelligence), or
- External ERP entity services invoked as tool contracts (ETA, Shipping, Customs, Invoices, Documents, Resources, Customers, Suppliers).

Nothing outside the DEM owns Session, Mission, or the public API contract.

---

## 5. Where Does the Intelligence Layer Start?

The intelligence layer starts at the **DEM API**.

The DEM API is a **business façade**. Behind this façade:
- The Reasoning Engine evaluates options and produces Decisions.
- The Task Planner decomposes Decisions into Missions.
- The Execution Planner decomposes Missions into ExecutionPlans.
- The Tool Orchestrator executes Tasks via the Tool Registry.

None of these internal components is the entry point. The entry point is the DEM.

---

## 6. Where Does the ERP Layer End?

The ERP layer ends at the **Tool Registry and Tool Contracts**.

ERP integrations are external tool contracts invoked by the Tool Orchestrator. They are:
- Not DEM core dependencies.
- Not intelligence layer components.
- Not bounded contexts owned by the DEM.

The DEM interacts with ERP through registered tools. The ERP entity services exist to support tool execution, not to define DEM behavior.

---

## 7. What Are the Official System Layers?

From outermost to innermost:

1. **User Layer** — Human operators, dashboards, avatars.
2. **Business Façade Layer** — DEM public API (`/api/v1/digital-export-manager`).
3. **Executive Intelligence Layer** — Digital Export Manager: Session, Mission, governance.
4. **Reasoning Layer** — Reasoning Engine: option evaluation, decisions, standing orders, approval gates.
5. **Planning Layer** — Task Planner and Execution Planner: mission decomposition, execution sequencing.
6. **Execution Layer** — Tool Orchestrator: task execution via Tool Registry.
7. **Knowledge Layer** — Company Knowledge, Knowledge Graph, Long-Term Memory: context, memory, relationships.
8. **Analytics Layer** — Trade Intelligence: read-only analytical insights over entity data.
9. **ERP Tool Layer** — ETA, Shipping, Customs, Invoices, Documents, Resources, Customers, Suppliers: external tool contracts.
10. **Data Layer** — SQLite persistence, migrations, audit logs.

---

## 8. What Are the Architecture Invariants?

These rules are non-negotiable and must hold in every architecture document, every Work Package, and every implementation decision.

### Invariant 1 — DEM Is Root
The Digital Export Manager is the root bounded context and the sole owner of Session and Mission lifecycle.

### Invariant 2 — Façade Stability
The DEM API is a business façade. Internal Agent Intelligence implementation may evolve without breaking the public contract.

### Invariant 3 — Bounded Context Boundaries
Company Knowledge, Long-Term Memory, Knowledge Graph, and Trade Intelligence are separate bounded contexts. None modifies DEM core logic.

### Invariant 4 — ERP Isolation
ERP integrations are external tool contracts, not DEM dependencies. Adding or removing an ERP tool must not require changes to DEM core.

### Invariant 5 — Knowledge Source Extensibility
Adding a new knowledge source must require zero changes to DEM core.

### Invariant 6 — Graceful Degradation
Memory Layer and Knowledge Layer may be unavailable. The platform must degrade gracefully without failing.

### Invariant 7 — No Agent-Centric Naming
Public API paths, documentation, and user-facing references must use Digital Export Manager terminology, not Agent terminology.

### Invariant 8 — Audit by Default
Every DEM action produces an immutable audit record.

---

## 9. Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Project Owner | | | |
| Architecture Lead | | | |
| Documentation Engineer | | | |

---

**Status:** Draft — Pending Executive Approval  
**Next Action:** Project Owner review and approval of this Executive Architecture Vision  
**Location:** `.kilo/plans/earp-001/executive-architecture-vision.md`
