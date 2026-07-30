# Executive Architecture Decision — EARP-001

**Plan:** EARP-001  
**Document:** Executive Architecture Decision (EAD)  
**Status:** Approved — Effective  
**Authority:** This document is the highest-authority architectural reference for EARP-001 Phase 5. All documentation updates in Phase 5 must conform to this decision. Any conflict between this document and any other project document is resolved in favor of this document.  
**Supersedes:** All prior architecture naming and terminology statements in affected documents listed in Section 7.  
**Does Not Supersede:** PLAN.md, ED-WP30-001, ED-WP30-002, ED-WP32-001, approved architecture specifications, or any code.

---

## 1. Executive Summary

The Nile Key Platform architecture is sound. The approved architecture defines the **Digital Export Manager (DEM)** as the **root bounded context** and **Executive Intelligence layer** of the **Intelligent Operating Platform**. No architectural redesign is required.

Phase 2 and Phase 3 identified **10 documentation gaps** across 7 documents. All gaps are **naming and terminology inconsistencies** only. There is **zero Architectural Drift** of any kind: no Boundary Drift, no Responsibility Drift, no Layer Drift, no Dependency Drift, and no Lifecycle Drift.

This Executive Architecture Decision:
- Freezes the official architecture vision.
- Establishes the final Architecture Invariants.
- Defines the Naming Policy for external and internal references.
- Defines the rules for Legacy Naming migration.
- Defines exactly what Phase 5 must update and what it must not change.
- Serves as the single traceable source for all Phase 5 documentation refactoring.

**Required remediation for Phase 5 is Documentation Refactoring Only. Architecture Redesign is not required.**

---

## 2. Background

EARP-001 was initiated because documentation drift across multiple Work Packages produced inconsistent terminology. Some documents still refer to "Agent" as the primary entry point, use legacy naming such as "AgentOrchestrator", or imply multi-agent patterns that are not implemented.

Phase 0 established the Executive Architecture Vision. Phase 1 froze the architecture knowledge baseline. Phase 2 audited all architecture documents and classified them as Fully Conformant, Partially Conformant, or Non-Conformant. Phase 2 Final Verification confirmed that all Partially Conformant findings are naming-only issues with zero Architectural Drift. Phase 3 consolidated findings into 10 gaps classified as Naming Gap or Terminology Gap only.

This decision consolidates all Phase 3 findings into binding executive decisions that govern Phase 5.

---

## 3. Findings

### 3.1 Architecture Is Structurally Sound

The approved architecture is fully consistent with the Executive Architecture Vision:

- **DEM is Root Bounded Context.** No component outside DEM owns Session, Mission, or the public API contract.
- **DEM API is the business façade.** Internal Agent Intelligence implementation is an internal detail behind the façade.
- **Official system layers** from User Layer to Data Layer are correctly defined and respected.
- **ERP integrations** are external tool contracts invoked via the Tool Registry. They are not DEM core dependencies.
- **Dependency chain** follows the approved order: Session → Mission → ExecutionPlan → Task → Tool.
- **Session and Mission lifecycles** match the approved model: Connect → Session → Multiple Missions → Disconnect.
- **Bounded context boundaries** are respected: Company Knowledge, Long-Term Memory, Knowledge Graph, and Trade Intelligence are separate contexts that do not modify DEM core logic.

### 3.2 All Gaps Are Naming and Terminology Only

Phase 3 identified 10 gaps. Breakdown:

| Gap Category | Count |
|--------------|-------|
| Naming Gap | 6 |
| Terminology Gap | 4 |
| Documentation Gap | 0 |
| Traceability Gap | 0 |
| Governance Gap | 0 |
| Consistency Gap | 0 |

Zero gaps constitute architectural drift.

### 3.3 Affected Documents

| Document | Gap Count | Impact |
|----------|-----------|--------|
| PLAN.md | 3 | Critical |
| README.md | 2 | Critical |
| CURRENT_STATUS.md | 1 | High |
| ENGINEERING_MEMORY.md | 1 | High |
| wp32-implementation-plan.md | 1 | Medium |
| WP-32-spec.md | 1 | Medium |
| wp30-architecture-compliance-review.md | 1 | Medium |

---

## 4. Executive Decisions

### Decision 1 — Product Identity

The official product of the Nile Key Platform is the **Digital Export Manager (DEM)**.

The DEM is the **Intelligent Operating Platform** for export operations. It is not a chatbot, not a generic AI assistant, and not a collection of disconnected microservices.

All user-facing references, public documentation, and capability labels must use **Digital Export Manager** or **DEM**. The term "AI Agent" is not approved as a product name.

### Decision 2 — Platform and Root Bounded Context

The **Intelligent Operating Platform** is the underlying substrate that hosts the Digital Export Manager and the bounded contexts it coordinates.

The **Digital Export Manager** is the **root bounded context** of the platform.

All other bounded contexts are either:
- Internal subsystems of the DEM (Reasoning Engine, Task Planner, Execution Planner, Tool Orchestrator), or
- Independent bounded contexts consumed by the DEM (Long-Term Memory, Company Knowledge, Knowledge Graph, Trade Intelligence), or
- External ERP entity services invoked as tool contracts (ETA, Shipping, Customs, Invoices, Documents, Resources, Customers, Suppliers).

Nothing outside the DEM owns Session, Mission, or the public API contract.

### Decision 3 — Layer Boundaries

The official system layers from outermost to innermost are:

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

The intelligence layer starts at the **DEM API**. The ERP layer ends at the **Tool Registry and Tool Contracts**.

### Decision 4 — ERP Isolation

ERP integrations are external tool contracts invoked by the Tool Orchestrator. They are:
- Not DEM core dependencies.
- Not intelligence layer components.
- Not bounded contexts owned by the DEM.

The DEM interacts with ERP through registered tools. The ERP entity services exist to support tool execution, not to define DEM behavior.

Adding or removing an ERP tool must not require changes to DEM core.

### Decision 5 — Façade Stability

The DEM API is a business façade. Internal Agent Intelligence implementation may evolve without breaking the public contract.

### Decision 6 — Graceful Degradation

Memory Layer and Knowledge Layer may be unavailable. The platform must degrade gracefully without failing.

### Decision 7 — Extensibility

Adding a new knowledge source must require zero changes to DEM core.

### Decision 8 — Audit by Default

Every DEM action produces an immutable audit record.

### Decision 9 — Naming Policy

#### 9.1 External Terminology (Public API, User-Facing Docs, Capability Lists)

The following terms are approved for external use:

| Approved Term | Context |
|---------------|---------|
| Digital Export Manager | Product name, architecture docs, user-facing references |
| DEM | Abbreviation for Digital Export Manager |
| Intelligent Operating Platform | Platform name |
| Mission | User-submitted operation |
| Session | Persistent Digital Export Session |
| Tool | ERP integration |
| Reasoning Engine | Internal subsystem |
| Task Planner | Internal subsystem |
| Execution Planner | Internal subsystem |
| Tool Orchestrator | Internal subsystem |
| Company Knowledge | Internal subsystem |
| Long-Term Memory | Internal subsystem |
| Knowledge Graph | Internal subsystem |
| Trade Intelligence | Internal subsystem |

The following terms are **not approved** for external or user-facing use:

| Deprecated Term | Replacement |
|-----------------|-------------|
| AI Agent | Digital Export Manager or DEM |
| Agent | Digital Export Manager or DEM |
| Agent Intelligence | Internal Agent Intelligence (internal use only) |
| Agent Orchestrator | Tool Orchestrator |
| Agent Core | DEM Core |
| Agent Router | DEM Router |
| Multi-Agent | Not applicable; single DEM architecture |

#### 9.2 Internal Terminology (Code, Internal Docs, Implementation Details)

The following internal package and class names are preserved as implementation details:

| Internal Term | Context | Rule |
|---------------|---------|------|
| `backend/app/agent/` | Package path | Retained as internal implementation detail. Public API paths must not use `agent`. |
| `AgentIntelligence` | Internal subsystem description | Permitted only in internal implementation docs and code comments. |
| `AgentOrchestrator` | Historical class name | Permitted only in code history and internal migration notes. Must not appear in public docs. |
| `Planner` | Historical class name | Permitted only in code history and internal migration notes. |

Internal implementation details are not visible through the public API and do not affect the architecture vision.

#### 9.3 Legacy Naming Migration Rule

All legacy naming occurrences in Tier 1–4 documents must be migrated to approved terminology in Phase 5. Legacy naming is permitted only in:
- Git history and commit messages.
- Internal code migration notes.
- Historical document archives explicitly marked as superseded.

Legacy naming is not permitted in:
- Active governing documents.
- Public API documentation.
- User-facing README or capability lists.
- Status documents that are read by operators or new developers.

### Decision 10 — Backward Compatibility for Documents

Documentation updates in Phase 5 must preserve:
- All technical content, section structure, and evidence.
- All approved architectural decisions and their rationale.
- All citations to governing documents.
- All implementation plans and Work Package scopes.

Only terminology and naming statements may change. No architectural content may be altered.

### Decision 11 — Scope of Phase 5

Phase 5 must update **only** the following:

- Terminology and naming statements in affected documents.
- Section titles, table entries, and labels that use deprecated terms.
- Index, capability list, and status entries that use deprecated terms.
- Internal cross-references that rely on deprecated terminology.

Phase 5 must apply updates **only** to the 7 affected documents identified in Phase 3.

### Decision 12 — Out of Scope for Phase 5

The following are explicitly out of scope for Phase 5 and must not be changed:

- PLAN.md architectural content.
- Approved Work Package definitions or scopes.
- Code, routers, services, schemas, or migrations.
- ED-WP30-001, ED-WP30-002, ED-WP32-001, or any Engineering Decision.
- Approved specifications (WP-30I-spec, WP-32-spec, WP-33-spec).
- Approved contracts (MEMORY_CONTRACT, KNOWLEDGE_INGESTION_CONTRACT, AVATAR_CONTRACT).
- Architecture diagrams that are technically correct.
- Implementation order or Work Package sequencing.

### Decision 13 — No Architectural Redesign Required

The gaps identified in Phase 3 require **Documentation Refactoring Only**. No Architectural Redesign is required.

The architecture is fully aligned with the Executive Architecture Vision. The remediation is limited to replacing deprecated terminology with approved terminology across affected documents.

---

## 5. Final Architecture Invariants

These rules are non-negotiable and must hold in every architecture document, every Work Package, and every implementation decision.

1. **DEM Is Root.** The Digital Export Manager is the root bounded context and the sole owner of Session and Mission lifecycle.
2. **Façade Stability.** The DEM API is a business façade. Internal Agent Intelligence implementation may evolve without breaking the public contract.
3. **Bounded Context Boundaries.** Company Knowledge, Long-Term Memory, Knowledge Graph, and Trade Intelligence are separate bounded contexts. None modifies DEM core logic.
4. **ERP Isolation.** ERP integrations are external tool contracts, not DEM dependencies. Adding or removing an ERP tool must not require changes to DEM core.
5. **Knowledge Source Extensibility.** Adding a new knowledge source must require zero changes to DEM core.
6. **Graceful Degradation.** Memory Layer and Knowledge Layer may be unavailable. The platform must degrade gracefully without failing.
7. **No Agent-Centric Naming Publicly.** Public API paths, documentation, and user-facing references must use Digital Export Manager terminology, not Agent terminology.
8. **Audit by Default.** Every DEM action produces an immutable audit record.

---

## 6. Naming Policy

### 6.1 Approved External Terms

Use these terms in all public-facing, user-facing, and governing documents:

- Digital Export Manager
- DEM
- Intelligent Operating Platform
- Mission
- Session
- Tool
- Reasoning Engine
- Task Planner
- Execution Planner
- Tool Orchestrator
- Company Knowledge
- Long-Term Memory
- Knowledge Graph
- Trade Intelligence

### 6.2 Deprecated Terms and Replacements

| Deprecated Term | Approved Replacement | Context |
|-----------------|----------------------|---------|
| AI Agent | Digital Export Manager or DEM | All public and governing documents |
| Agent | Digital Export Manager or DEM | All public and governing documents |
| Agent Orchestrator | Tool Orchestrator | Public architecture docs |
| Agent Intelligence | Internal Agent Intelligence | Internal docs and code only |
| Agent Core | DEM Core | Internal docs and code only |
| Agent Router | DEM Router | Internal docs and code only |
| Multi-Agent | Not applicable | Remove or replace with single-DEM description |

### 6.3 Internal Implementation Terms

The package path `backend/app/agent/` and internal class names are implementation details. They are not subject to this naming policy as long as they remain internal and do not appear in public API paths or user-facing documentation.

### 6.4 Legacy Naming in Historical Context

Legacy naming may appear in:
- Git history.
- Internal code comments describing migration steps.
- Superseded documents explicitly marked as historical.

Legacy naming must not appear in active governing documents, public APIs, or user-facing content after Phase 5.

---

## 7. Scope of Phase 5

Phase 5 must update the following 7 documents to replace deprecated terminology with approved terminology:

| # | Document | Required Updates |
|---|----------|------------------|
| 1 | PLAN.md | Replace "AI Agent" in Section 11 title, WP-30 heading, and exit criteria. |
| 2 | README.md | Replace "AI Agent" in Business Capabilities table and status table. |
| 3 | CURRENT_STATUS.md | Replace "AI Agent" in completed components table. |
| 4 | ENGINEERING_MEMORY.md | Replace "AI Agent" in completed components table. |
| 5 | wp32-implementation-plan.md | Replace "WP-30: AI Agent" with "WP-30: Digital Export Manager" in dependencies table. |
| 6 | WP-32-spec.md | Replace "WP-30: AI Agent" with "WP-30: Digital Export Manager" in dependencies table. |
| 7 | wp30-architecture-compliance-review.md | Replace "AgentOrchestrator" with approved internal terminology in component tables. |

For each update:
- Apply only the terminology changes mandated by this EAD.
- Preserve all technical content, structure, and evidence.
- Record the EAD clause that mandates each change in the Phase 5 change log.
- Do not introduce new architectural content or modify existing decisions.

---

## 8. Out of Scope

The following are explicitly out of scope for Phase 5 and must not be modified:

- PLAN.md architecture sections, Work Package definitions, or execution rules.
- Any Work Package implementation plan scope or sequencing.
- Code, routers, services, schemas, migrations, or tests.
- Approved Engineering Decisions (ED-WP30-001, ED-WP30-002, ED-WP32-001).
- Approved specifications (WP-30I-spec, WP-32-spec, WP-33-spec).
- Approved contracts (MEMORY_CONTRACT, KNOWLEDGE_INGESTION_CONTRACT, AVATAR_CONTRACT).
- Architecture diagrams that are technically correct.
- External API behavior or public API paths.
- Database schema or persistence logic.
- ERP tool contracts or integrations.

---

## 9. Impact Assessment

### 9.1 Requirements Impact

None. No requirements are added, removed, or modified.

### 9.2 Architecture Impact

None. No architectural components, boundaries, layers, or dependencies are changed.

### 9.3 Scope Impact

None. No Work Package scope or execution order is changed.

### 9.4 Backward Compatibility Impact

Documentation backward compatibility is preserved for all technical content. Terminology changes are applied consistently across affected documents to eliminate confusion. No breaking changes are introduced.

### 9.5 Implementation Impact

Zero. Phase 5 updates documentation only. No code changes are involved.

---

## 10. Approval Criteria

This Executive Architecture Decision is effective upon written approval by the Project Owner and Architecture Lead.

Approval signifies:
- The Executive Architecture Vision is accepted as the highest-authority architectural reference.
- The Naming Policy is accepted as binding for all project documents.
- The 10 gaps identified in Phase 3 are accepted as Documentation Refactoring Only.
- Phase 5 is authorized to proceed with the scoped documentation updates.
- No architectural redesign is required or authorized by EARP-001.

---

## 11. Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Project Owner | | | |
| Architecture Lead | | | |
| Documentation Engineer | | | |

---

**Status:** Approved — Effective  
**Next Action:** None — Phase 5 Documentation Refactoring Complete  
**Location:** `.kilo/plans/earp-001/EAD.md`
