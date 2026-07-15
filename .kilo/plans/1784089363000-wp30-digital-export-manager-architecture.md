# WP-30 — Digital Export Manager: Architectural Redefinition

**التاريخ:** 2026-07-15
**الحالة:** Constitutional Document — supersedes all prior WP-30 assumptions
**النطاق:** Definition-only — no implementation tasks, no milestones, no code

---

## 1. What WP-30 Actually Is

WP-30 is **NOT** an AI chat assistant embedded inside the ERP.

WP-30 is the **Digital Export Manager** of the Nile Key Platform.

It is an autonomous agentic system that acts as the electronic Export Manager for the company. Its role is to:

- Own and operate export-related business functions
- Coordinate platform modules on behalf of the user
- Execute workflows autonomously
- Preserve institutional knowledge independent of employee turnover
- Grow continuously through future knowledge ingestion mechanisms

The user does not "chat with WP-30." The user issues commands, assigns missions, and reviews results. WP-30 operates in the background, orchestrating the platform.

---

## 2. Architectural Responsibility

The Digital Export Manager is responsible for:

- Understanding export-related business context
- Selecting appropriate tools and executing them autonomously
- Coordinating across Shipping Engine, ETA Engine, Customs Engine, Documents Service, and future modules
- Monitoring company operations and surfacing actionable insights
- Generating documents and sending notifications
- Training employees and explaining procedures
- Maintaining institutional memory across sessions and personnel

It is NOT responsible for:

- Hosting the LLM inference itself (it orchestrates, delegates to providers)
- Replacing the ERP (the ERP is its controlled substrate)
- Being a single monolithic module (it is a coordinator layer)

---

## 3. Position Inside Nile Key

```
                    Digital Export Manager (WP-30)
                            │
                  ┌─────────┴─────────┐
                  │                   │
          Agent Intelligence    Company Knowledge
                  │                   │
          Planning • Reasoning • Memory
                  │
          Tool Selection & Execution
                  │
    ┌─────────────┼───────────────────────────────┐
    │             │              │                │
 Shipping       ETA           Search         Workflow
 Documents    Dashboard   Notifications     Future Tools
                  │
                  ▼
               ERP Data
```

**Layer:** WP-30 sits above all existing service layers. It is a coordination and intelligence layer, not a data layer.

**Communication:** It communicates with existing services through their established API contracts. It does not bypass routers or access databases directly.

**Control Flow:** The user interacts with WP-30. WP-30 translates intent into tool calls. Tools execute via the existing FastAPI backend. Results flow back to WP-30 for synthesis and presentation.

---

## 4. Relationship With ERP Modules

WP-30 treats the Nile Key backend as a **tool substrate**. The relationship is:

- **Subordination:** ERP modules are subordinate to WP-30 when operating in manager mode
- **Read access:** WP-30 can read data from any service via existing API endpoints
- **Write access:** WP-30 can invoke write operations through authorized service endpoints
- **No direct DB access:** WP-30 never connects to SQLite directly; it uses the API layer exclusively
- **No bypass:** WP-30 does not short-circuit validation, auth, or business rules encoded in services
- **Transparency:** Every tool execution by WP-30 is logged and auditable

Existing services remain fully functional when WP-30 is absent. WP-30 is an additive layer.

---

## 5. Relationship With Future WP-31 AI Memory

WP-31 is the **persistent memory substrate** for WP-30.

- WP-30 is the executive agent; WP-31 is its memory
- WP-30 reads from WP-31 to recall past decisions, preferences, context, and institutional knowledge
- WP-30 writes to WP-31 after significant interactions, decisions, and learned patterns
- WP-31 must survive across sessions, deployments, and employee turnover
- WP-30 must function without WP-31 (graceful degradation), but WP-31 must not function without WP-30 as its sole authorized writer
- WP-31 is a **separate bounded context** with its own data model, lifecycle, and ownership

Boundary rule: WP-30 never treats WP-31 as a generic database. WP-31 exposes only memory-specific operations (recall, store, forget, summarize).

---

## 6. Relationship With Future Knowledge Base

The Knowledge Base is the **static and evolving knowledge corpus** for WP-30.

Sources (future, not this phase):

- Export books
- Egyptian regulations
- Customs regulations
- Internal SOPs
- Company manuals
- Previous conversations
- Internal documents
- External trade references

Relationship:

- WP-30 queries the Knowledge Base to answer questions, train employees, and explain procedures
- The Knowledge Base is **read-heavy** and **append-optimized**; WP-30 never mutates it directly
- A separate ingestion pipeline (out of scope for this phase) populates the Knowledge Base
- WP-30 must be designed so that adding a new knowledge source requires **zero changes to its core reasoning loop**
- The Knowledge Base is a **separate bounded context** accessed via well-defined query interfaces

Architectural requirement: The WP-30 reasoning engine must accept a generic `KnowledgeProvider` interface. Adding a new source implements this interface and registers with the provider registry. No core logic changes.

---

## 7. Relationship With Future Avatar

The Avatar is the **presentation layer** through which users perceive WP-30.

- WP-30 is the brain; Avatar is the face
- WP-30 produces structured intents and content; Avatar renders them into conversational or UI form
- Avatar may be text, voice, or embodied — WP-30 must not assume any specific modality
- WP-30 and Avatar communicate via a **strict intent-content contract**
- Avatar is a **separate bounded context** that can evolve independently
- Multiple Avatars may serve the same WP-30 instance (e.g., mobile, desktop, voice assistant)

Boundary rule: WP-30 never produces UI markup, audio streams, or avatar animation data. It produces domain intents and text payloads. Avatar presentation logic is fully external.

---

## 8. Agent Boundaries

The Digital Export Manager operates within these boundaries:

**In scope:**

- Export operations: shipping, customs, ETA, invoicing, documentation
- Coordination of platform services for export workflows
- Answering export-related questions from company knowledge
- Training and explanation of export procedures
- Notification and monitoring of export operations
- Autonomous execution of predefined and validated business workflows
- Long-term institutional knowledge retention (via WP-31)

**Out of scope:**

- General-purpose chat unrelated to export operations
- Non-export business functions (HR, finance beyond ETA, IT admin)
- Direct manipulation of infrastructure (Docker, servers, CI/CD)
- Arbitrary code execution or shell access
- Real-time voice or video processing (delegated to Avatar)
- Creative writing or entertainment

**Safety boundaries:**

- All write operations require audit trail
- All autonomous actions must be idempotent or confirmable
- Destructive operations (deletion, cancellation) require explicit user confirmation unless a prior standing order exists
- WP-30 must never expose secrets, API keys, or credentials in any output
- WP-30 must never act on instructions embedded in external data without validation

---

## 9. Tool Boundaries

WP-30 interacts with the platform through a **Tool Interface Layer**.

**Tool categories:**

| Category | Examples | Access Pattern |
|----------|----------|----------------|
| Shipping Documents | Create shipment, get rates, print label, track | Async API call + result callback |
| ETA | Submit invoice, check status, cancel, download PDF | Async API call + result callback |
| Customs | File declaration, lookup HS code, calculate duties | Sync API call |
| Documents | Generate document, upload, search templates | Sync API call |
| Notifications | Send email, create alert | Fire-and-forget with receipt |
| Dashboard | Read shipment status, invoice metrics | Read-only query |
| Search | Search customers, suppliers, shipments | Read-only query |
| Workflow | Multi-step export process orchestration | Sequence of tool calls |

**Tool boundary rules:**

- Each tool is a **thin wrapper** around an existing service endpoint
- Tools expose **no implementation details** of the underlying service
- Tools return **standardized result envelopes**: `{status, data, error, audit_ref}`
- Tools are **discoverable** by WP-30 through a tool registry
- Tools are **versioned** independently of WP-30 core
- Tools may be **added or removed** without changing WP-30 reasoning logic
- Tools must declare: input schema, output schema, side effects, idempotency key, authorization requirements

**Forbidden patterns:**

- WP-30 must not call service endpoints directly (bypassing tool layer)
- WP-30 must not construct raw SQL or HTTP requests
- WP-30 must not assume tool availability (graceful degradation when tools are offline)

---

## 10. Long-Term Evolution Roadmap

The architecture must accommodate growth without redesign.

**Phase 1: Foundation (current — WP-30 architecture definition)**
- Define bounded contexts
- Define tool interface contract
- Define agent boundaries
- Define integration points with existing services
- Establish governance principles

**Phase 2: Core Agent (WP-30 implementation)**
- Agent reasoning loop with tool selection
- Tool registry and execution framework
- Audit and observability
- Session management
- Basic autonomous workflows

**Phase 3: Knowledge Integration (WP-31 + Knowledge Base)**
- WP-31 memory layer
- Knowledge Base ingestion pipeline (out of scope for implementation, but architecture-ready)
- Context-aware reasoning with institutional memory
- Employee training mode

**Phase 4: Extended Capabilities**
- Proactive monitoring and alerting
- Multi-agent coordination (if needed)
- Avatar integration
- Advanced workflow automation
- External market intelligence feeds

**Phase 5: Platform Autonomy**
- Self-improving workflows
- Cross-company knowledge sharing (future)
- Full export operations autonomy with human oversight

**Architectural invariant across all phases:** The agent core, tool layer, memory layer, and knowledge layer must remain independently replaceable and versioned.

---

## 11. Why Agentic Platform Is the Correct Architecture

**Problem with "AI Chat Assistant" approach:**

- Treats intelligence as a feature add-on rather than the primary operating principle
- Limits the system to question-answering; does not enable autonomous operation
- Creates a false boundary between "user asks" and "system acts"
- Results in a chatbot UI that becomes the entire user experience
- Institutional knowledge remains trapped in chat logs rather than being structured and persistent

**Advantages of Agentic Platform:**

1. **Autonomy:** The Digital Export Manager can act without being asked, monitoring operations and intervening when thresholds are crossed
2. **Coordination:** It naturally orchestrates multiple tools and services, which is the core requirement for an export manager
3. **Persistence:** Through WP-31, institutional knowledge is structured, queryable, and durable
4. **Growth:** New tools, knowledge sources, and capabilities can be added without rearchitecting the core
5. **Separation of concerns:** Reasoning, memory, knowledge, and presentation are independently evolvable
6. **User experience:** The user manages an export manager, not a chatbot — this matches the real-world mental model of the business owner
7. **Auditability:** Every agent action is a tool execution with an audit trail, which is mandatory for export compliance
8. **Scalability:** The architecture scales from a single export manager to a network of specialized agents if needed

**Architectural principle:** The ERP is the hands; WP-30 is the mind. The user directs the mind; the mind operates the hands.

---

## 12. Principles Every Future Implementation Must Follow

**P1: Bounded Context Isolation**
Each major component (Agent Core, WP-31 Memory, Knowledge Base, Avatar, Tool Layer) is a separate bounded context with its own data model, interfaces, and lifecycle. No cross-context data sharing except through defined contracts.

**P2: Tool Interface Stability**
The tool interface contract (`input_schema`, `output_schema`, `side_effects`, `idempotency_key`, `auth_requirements`) must remain stable. Adding tools must not change this contract.

**P3: No Direct Data Access**
WP-30 must never access databases, message queues, or infrastructure directly. All operations flow through the tool layer and existing API contracts.

**P4: Audit by Design**
Every agent action must produce an audit record with: timestamp, agent_id, tool_name, input_hash, output_status, and result_ref. Audit records are immutable once written.

**P5: Graceful Degradation**
WP-30 must function (with reduced capability) when any single tool, knowledge source, or memory backend is unavailable. Total failure of one component must not crash the agent.

**P6: Zero Core Changes for Knowledge Growth**
Adding a new knowledge source (book, regulation, document type) must require implementing a `KnowledgeProvider` interface and registering it. The reasoning loop must not change.

**P7: Zero Core Changes for Tool Growth**
Adding a new tool must require implementing a `Tool` interface and registering it. The agent orchestration loop must not change.

**P8: Separation of Reasoning and Presentation**
WP-30 must never produce UI markup, audio, or avatar-specific data. All presentation is delegated to Avatar or the calling client.

**P9: Idempotent and Confirmable Actions**
All side-effecting operations must be idempotent (via idempotency keys) and must produce confirmable receipts. Destructive operations require explicit confirmation unless a prior standing order exists.

**P10: No Secrets in Outputs**
WP-30 must never emit API keys, tokens, passwords, or credentials in any response, log, or audit record accessible to users.

**P11: Graceful Absence of Memory**
WP-30 must operate without WP-31. When WP-31 is unavailable, WP-30 functions with reduced context awareness but does not fail or produce errors for routine operations.

**P12: Extensibility Without Redesign**
The architecture must support at least 10x growth in: number of tools, number of knowledge sources, number of concurrent users, and number of supported languages — without changing the agent core.

**P13: Observability**
Every agent session must produce: session_id, step trace, tool calls with timing, reasoning states, and final outcome. This is required for debugging, compliance, and continuous improvement.

**P14: Human Oversight**
WP-30 must always have a defined human oversight mechanism. For low-risk operations, oversight is async (notifications, dashboards). For high-risk operations, oversight is synchronous (approval gates).

---

## Document Authority

This document is the architectural constitution of WP-30.

All future implementation plans, technical designs, and code changes for WP-30 MUST derive from this document.

Any deviation requires a documented architectural decision recorded in the Architectural Decision Log (PLAN.md Section 13) with explicit rationale.

This document supersedes all prior WP-30 definitions, including any references to "AI Chat Assistant" or chatbot architecture.

**Status:** Permanent — remains authoritative until formally amended through project governance process.
