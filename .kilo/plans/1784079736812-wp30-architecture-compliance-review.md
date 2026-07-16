# WP-30 Architecture Compliance Review

**Status:** Planning — Final architectural refinement; implementation-ready
**Date:** 2026-07-15
**Reference:** PLAN.md Section 15.3, `.kilo/plans/1784089363000-wp30-digital-export-manager-architecture.md`, `.kilo/plans/ED-WP30-001.md`, `.kilo/plans/ED-WP30-002.md`

---

## Level-0 Architecture: The Digital Export Manager

### 1. Root Bounded Context

The Digital Export Manager is the **root bounded context** of WP-30. It is the product. It is the platform.

Agent Intelligence is **not** the architecture's primary entry point. Agent Intelligence is an internal subsystem used by the Digital Export Manager to perform reasoning and execution.

```
┌───────────────────────────────────────────────────────────┐
│              Digital Export Manager (WP-30)               │
│              Root Bounded Context                         │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                    Agent Intelligence                │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │ │
│  │  │ Decision    │  │ Mission     │  │ Execution   │  │ │
│  │  │ Engine      │  │ Planner     │  │ Engine      │  │ │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │ │
│  │         │                │                │         │ │
│  │  ┌──────▼────────────────▼────────────────▼──────┐  │ │
│  │  │         Execution Coordination Layer           │  │ │
│  │  └──────┬────────────────┬────────────────┬──────┘  │ │
│  │         │                │                │         │ │
│  │  ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐  │ │
│  │  │ Company     │  │ Memory      │  │ Tool        │  │ │
│  │  │ Knowledge   │  │ Interface   │  │ Registry    │  │ │
│  │  │ Layer       │  │ (WP-31)     │  │             │  │ │
│  │  └──────┬──────┘  └─────────────┘  └──────┬──────┘  │ │
│  │         │                                │         │ │
│  │  ┌──────▼────────────────────────────────▼──────┐  │ │
│  │  │              Audit Layer                      │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  │                                                     │ │
│  │  ┌──────────────────────────────────────────────┐  │ │
│  │  │              Avatar Contract                  │  │ │
│  │  └──────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐ │
│  │          Platform Services (Non-Agent)              │ │
│  │  Auth, Users, Settings, Scheduling, Notifications   │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
                        │
                        ▼
              ERP Services / Company Tools
                        │
                        ▼
                    Database
```

### 2. Execution Flow

```
User Request
    │
    ▼
Digital Export Manager
    │
    ▼
Decision Engine
    │
    ▼
Mission Planner
    │
    ▼
Mission (Domain Object)
    │
    ▼
Execution Engine
    │
    ├──► ERP Tools (Shipping, ETA, Customs, Documents, Search, Dashboard, Notifications, Workflows)
    ├──► Company Knowledge Layer
    ├──► Memory Interface (WP-31)
    │
    ▼
Audit Record
```

**Critical distinction:** The Mission is an internal domain object produced by the Mission Planner. It is not the architectural entry point. The entry point is the Digital Export Manager receiving a user request.

### 3. Layer Responsibilities

| Layer | Responsibility | NOT Responsible For |
|-------|----------------|---------------------|
| **Digital Export Manager** | Owns the export operation; receives user requests; coordinates all internal layers; produces final outcome | Performing business logic; accessing databases directly; hosting LLM inference |
| **Decision Engine** | Reasons about the current state; determines whether action is needed; evaluates options; applies company rules and preferences | Executing tools; storing long-term memory; producing UI markup |
| **Mission Planner** | Decomposes decisions into executable missions; defines mission structure and parameters; consults standing orders and user preferences | Keyword-matching free text; calling ERP endpoints directly; business logic |
| **Execution Engine** | Runs missions by selecting and invoking tools; handles parallel/sequential execution; retries; graceful degradation | Reasoning; planning; knowledge retrieval; memory storage |
| **Company Knowledge Layer** | Queries company SOPs, regulations, Incoterms, manuals, historical knowledge, templates, employee expertise; read-only corpus | Mutating knowledge; hosting inference; direct database access |
| **Memory Interface (WP-31)** | Recall/store/forget/summarize institutional memory across sessions; persists decisions, preferences, context | Business logic; ERP operations; knowledge ingestion |
| **Tool Registry** | Discovers, registers, and versions ERP tools; enforces tool contracts | Business logic; reasoning; direct service access |
| **Audit Layer** | Records every agent action with immutable audit trail; input hash, output status, timing, metadata | Business logic; execution; reasoning |
| **Avatar Contract** | Defines intent-content interface between Digital Export Manager and presentation layer | UI rendering; audio/video; business logic |

### 4. Future Reasoning Evolution

The architecture reserves space for future reasoning layers even though they are implemented in later work packages:

```
Goal
    │
    ▼
Plan
    │
    ▼
Mission
    │
    ▼
Task
    │
    ▼
Tool
```

- **Goal:** High-level business objective (e.g., "deliver 10 tons of onions to Hamburg by Friday"). Implemented in future WP.
- **Plan:** Decomposes goals into ordered missions. Implemented in future WP.
- **Mission:** Current level of abstraction. A mission is a structured operation that the Execution Engine can execute.
- **Task:** A single tool invocation within a mission. Already exists as tool execution.
- **Tool:** ERP module wrapper. Already exists as `BaseTool`.

**WP-30 implements Mission and Task. Goal and Plan are reserved for future work packages.**

### 5. API Contract: The Business Façade

**Confirmed:** The canonical API contract uses a **single unified endpoint with a discriminated Pydantic union** (Option A).

The Digital Export Manager API is a **business façade**. The Agent Intelligence implementation behind that façade may evolve over time without breaking the public API. This abstraction layer is a long-term architectural requirement.

**Endpoint:**

```
POST /api/v1/digital-export-manager/missions
```

**Semantic meaning:** "Create a Digital Export Manager operation."

This is NOT "Execute an Agent Mission." The Mission is an internal artifact. The endpoint represents a business operation on the Digital Export Manager.

**Request model:**

```python
class MissionRequest(BaseModel):
    mission_type: MissionType  # Discriminator enum
    payload: MissionPayload  # Discriminated union — typed per mission_type
```

**MissionType enum (examples):**

- `CREATE_SHIPMENT`
- `SUBMIT_INVOICE`
- `FILE_CUSTOMS`
- `GENERATE_DOCUMENT`
- `SEARCH_ENTITIES`
- `GET_DASHBOARD`
- `SEND_NOTIFICATION`
- `TRANSITION_WORKFLOW`

**Payload hierarchy (discriminated union):**

Each mission type owns its own strongly-typed payload model:

- `CreateShipmentPayload`
- `SubmitInvoicePayload`
- `FileCustomsPayload`
- `GenerateDocumentPayload`
- `SearchEntitiesPayload`
- `GetDashboardPayload`
- `SendNotificationPayload`
- `TransitionWorkflowPayload`

Pydantic validates the union based on `mission_type`. Invalid combinations are rejected at the API boundary.

**Response model:**

```python
class MissionResponse(BaseModel):
    mission_id: str
    status: MissionStatus  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
```

**Separation of concerns:**

```
External Request (HTTP)
    │
    ▼
MissionRequest (API Schema)
    │  ← validated, typed, sanitized
    ▼
Mission (Domain Object)
    │  ← adds execution metadata not present in request
    ▼
ExecutionPlan
    │  ← decomposed by Mission Planner
    ▼
Tasks
    │  ← atomic tool invocations
    ▼
Tools
    │  ← thin ERP wrappers
    ▼
Results
    │
    ▼
MissionResponse (API Schema)
    │  ← sanitized, no internal details
    ▼
External Response (HTTP)
```

The client never sees the internal `Mission`, `ExecutionPlan`, or `Task` objects. The API layer translates between external requests/responses and internal domain objects.

### 6. The Mission Model

**Confirmed:** The canonical mission representation is a **strongly-typed Pydantic Mission model**.

The Mission is an **internal domain object** — it is not an API request. The API layer validates incoming data and converts it into a Mission. The Execution Engine executes Missions. Tools never receive raw API requests.

**Mission model structure:**

```python
class Mission:
    # Generic execution metadata (populated by system, not client)
    mission_id: str
    mission_type: MissionType
    objective: str
    priority: int  # 1-10
    requester: UserReference
    context: Dict[str, Any]
    constraints: List[Constraint]
    approval_policy: ApprovalPolicy
    execution_policy: ExecutionPolicy
    created_at: datetime
    correlation_id: str
    idempotency_key: str
    audit_context: AuditContext

    # Business payload (encapsulated separately)
    payload: MissionPayload  # Typed per mission_type
```

**Mission payload encapsulation:**

Business-specific payload is encapsulated separately rather than mixed with execution metadata. Each `mission_type` has a corresponding `MissionPayload` subclass:

- `CreateShipmentPayload`
- `SubmitInvoicePayload`
- `FileCustomsPayload`
- `GenerateDocumentPayload`
- etc.

This separation ensures that:
- Execution metadata is uniform across all mission types
- Business payload can evolve independently per mission type
- Tools receive only the payload relevant to them
- Audit trails capture execution metadata separately from business data

### 7. Ownership Model

| Artifact | Owner | Lifecycle |
|----------|-------|-----------|
| **Mission** | Execution Engine | Created by Mission Planner, executed by Execution Engine, archived after completion |
| **Task** | Execution Engine | Created by Execution Engine from Mission, executed, then discarded |
| **ExecutionPlan** | Mission Planner | Created by Mission Planner from Decision, consumed by Execution Engine |
| **Decision** | Decision Engine | Created by Decision Engine from user request, consumed by Mission Planner |
| **ExportWorkflow** | Workflow Tool / ERP | Owned by the workflow service; represents a business process instance |
| **Tool** | Tool Registry / ERP Service | Registered by developer, invoked by Execution Engine |
| **Session** | Digital Export Manager | Created on first user request, persists across missions, closed explicitly or by timeout |
| **Memory entry** | Memory Interface (WP-31) | Created by Digital Export Manager, queried by Decision Engine and Mission Planner |

**Key principle:** The Digital Export Manager owns the Session. Missions, Tasks, and Execution Plans are transient artifacts within a Session. ExportWorkflows are owned by the ERP workflow service, not by the Digital Export Manager.

### 8. Mission vs. ExportWorkflow Relationship

Missions and ExportWorkflows are **separate abstractions** at different architectural levels:

- **ExportWorkflow** is an ERP business process instance with a state machine (`draft → customs_ready → shipped → delivered`). It is owned by the workflow service.
- **Mission** is an internal execution artifact of the Digital Export Manager. It represents a single coordinated operation.

A mission may **invoke the workflow tool** to transition an ExportWorkflow, but the mission does not IS the workflow. The relationship is:

```
Mission
    │
    ├──► Tool: create_shipment
    ├──► Tool: submit_invoice
    └──► Tool: transition_workflow  ← operates on ExportWorkflow
```

The workflow tool is one of many tools a mission may call. Missions can exist without workflows, and workflows can be manipulated outside of missions.

### 9. Company Knowledge Layer (Renamed from Knowledge Provider)

The previous "Knowledge Provider" concept is replaced by the **Company Knowledge Layer** — a broader architectural component.

**Sources the layer must eventually consume:**

- Company SOPs
- Export regulations (Egyptian, EU, GCC, etc.)
- Incoterms 2020
- Export books and reference materials
- Internal manuals
- Previous company decisions
- Historical company knowledge
- Document templates
- Employee expertise profiles
- Future external knowledge sources

**Architectural requirements:**

- The Company Knowledge Layer is a **read-heavy, append-optimized** corpus.
- WP-30 queries it to answer questions, train employees, and explain procedures.
- WP-30 **never mutates** the Knowledge Layer directly.
- A separate ingestion pipeline (out of scope for WP-30) populates it.
- Adding a new knowledge source must require **zero changes** to the Digital Export Manager core.
- The Knowledge Layer exposes a **query interface** only. Mutation is through ingestion only.

**WP-30 deliverables for Knowledge:**

- Define the `KnowledgeQuery` contract (input: query, context, scope; output: results, confidence, sources)
- Define the `KnowledgeProvider` interface that each source implements
- Define the provider registry
- Document the ingestion contract (no implementation)
- The Decision Engine and Mission Planner may query knowledge; the Execution Engine does not

### 10. Memory Interface (WP-31 Boundary)

- WP-30 defines the `MemoryProvider` interface: `recall`, `store`, `forget`, `summarize`.
- WP-31 implements the interface against persistent storage.
- The Digital Export Manager uses memory to maintain context across sessions and personnel turnover.
- Memory is **not** a general database. It is a structured institutional memory.
- WP-30 must function without WP-31 (graceful degradation).

### 11. Tool Registry and Tool Contracts

Each ERP module is a Tool. Tools are **thin wrappers** around existing service endpoints.

**Tool categories:**

| Category | Examples | Access Pattern |
|----------|----------|----------------|
| Shipping | Create shipment, get rates, print label, track | Async API call + result callback |
| ETA | Submit invoice, check status, cancel, download PDF | Async API call + result callback |
| Customs | File declaration, lookup HS code, calculate duties | Sync API call |
| Documents | Generate document, upload, search templates | Sync API call |
| Notifications | Send email, create alert | Fire-and-forget with receipt |
| Dashboard | Read shipment status, invoice metrics | Read-only query |
| Search | Search customers, suppliers, shipments | Read-only query |
| Workflow | Multi-step export process orchestration | Sequence of tool calls |

**Tool contract fields (required):**

- `tool_name`: unique identifier
- `description`: human-readable
- `input_schema`: JSON Schema or Pydantic model
- `output_schema`: JSON Schema or Pydantic model
- `side_effects`: READ / WRITE / DELETE / NOTIFY
- `idempotency_key`: Optional[str] — for deduplication
- `auth_requirements`: Dict[str, Any] — structured auth needs
- `version`: SemVer for independent tool evolution

### 12. Audit Layer

Every Digital Export Manager action produces an immutable audit record:

- `session_id`
- `agent_id`
- `tool_name` (or "decision", "mission_plan", etc.)
- `input_hash` (SHA256)
- `output_status` (success / failure / timeout)
- `result_ref`
- `duration_ms`
- `timestamp`
- `metadata`

Audit records are never mutated after creation.

### 13. Avatar Contract

The Avatar is the **presentation layer** through which users perceive the Digital Export Manager.

- WP-30 produces **structured intents** and **text payloads** — never UI markup, audio streams, or avatar animation data.
- Avatar may be text, voice, or embodied — WP-30 must not assume any specific modality.
- Multiple Avatars may serve the same Digital Export Manager instance.
- The contract is a strict `IntentContent` object with: `intent_type`, `content`, `context`, `suggested_actions`.

---

## Component Classification

### KEEP

| Component | Location | Why |
|-----------|----------|-----|
| Bounded context package structure | `backend/app/agent/` | Correct architectural boundary. Separation of concerns is correct. |
| Tool interface base class | `backend/app/agent/tools/base.py` | `BaseTool`, `ToolResult`, `ToolSideEffect` are the right abstractions. |
| Tool registry | `backend/app/agent/tools/registry.py` | `ToolRegistry` supports discovery, registration, versioning. |
| Session management | `backend/app/agent/session/manager.py` | Persistent sessions with context storage are required for continuity. |
| Audit framework | `backend/app/agent/audit/recorder.py` | P4 (Audit by Design) — every action produces immutable audit records. |
| LLM provider abstraction | `backend/app/agent/llm/provider.py` | Separation of reasoning from inference hosting. |
| Database tables | `backend/app/core/database.py` | `agent_sessions`, `agent_memory`, `agent_audit_logs` schema is correct. |
| Agent API router | `backend/app/routers/agent.py` | Additive API layer. |

### MODIFY

| Component | Location | Why and What |
|-----------|----------|--------------|
| Package naming | `backend/app/agent/` | Keep `agent/` as internal package. Rename API paths to `/api/v1/digital-export-manager`. Internal subpackages: `decision_engine/`, `mission_planner/`, `execution_engine/`. |
| Tool base class contract | `backend/app/agent/tools/base.py` | Add `idempotency_key`, `auth_requirements` structured field, `version`. |
| Tool result envelope | `backend/app/agent/schemas/tool_result.py` | Make `audit_ref` required. |
| Session context model | `backend/app/agent/session/manager.py` | Add typed export-domain state: `active_workflows`, `linked_entities`, `standing_orders`, `user_preferences`. |
| Execution Engine | `backend/app/agent/core/orchestrator.py` | Rename from `AgentOrchestrator`. Accepts `Mission` objects (not free-text intents). Add graceful degradation, idempotency propagation, structured step trace. |
| Mission Planner | `backend/app/agent/core/planner.py` | Rename from `Planner`. Accepts `Decision` objects. Decomposes into `Mission` objects with ordered `Task` lists. Never uses free-text keyword matching. |
| Agent schemas | `backend/app/schemas/agent/`, `backend/app/agent/schemas/` | Consolidate. Replace `intent` with `mission_type` and typed fields. Define `Mission` Pydantic model with execution metadata + payload. Define `MissionRequest` as discriminated union at API boundary. |
| Agent router | `backend/app/routers/agent.py` | Evolve from `/execute` (intent-based) to `/missions` (mission-oriented). Document as "Create a Digital Export Manager operation." Keep `/health`, `/tools`, `/sessions`. |
| Agent ID | `backend/app/agent/core/orchestrator.py` | Make configurable via settings. |

### REFACTOR

| Component | Location | Why and What |
|-----------|----------|--------------|
| Decision Engine | NEW: `backend/app/agent/decision_engine/` | Extract reasoning logic from orchestrator/planner into a distinct `DecisionEngine` that: (1) receives user requests, (2) queries Company Knowledge Layer and Memory Interface, (3) evaluates options, (4) produces a `Decision` object passed to Mission Planner. |
| Mission Planner | NEW: `backend/app/agent/mission_planner/` | Rename from `Planner`. Accepts `Decision` objects. Decomposes into `Mission` objects with ordered `Task` lists. Consults standing orders and user preferences. Never uses free-text keyword matching. |
| Execution Engine | `backend/app/agent/core/orchestrator.py` | Rename from `AgentOrchestrator`. Accepts `Mission` objects. Executes tasks via Tool Registry. Supports parallel steps, retry, structured step trace. |
| Company Knowledge Layer | `backend/app/agent/knowledge/` | Rename from "Knowledge Provider" to "Company Knowledge Layer". Define `KnowledgeProvider` interface (not a single implementation). Define `KnowledgeQuery` contract. Document ingestion contract. Zero implementations in WP-30. |
| Memory Interface | `backend/app/agent/memory/` | Define `MemoryProvider` interface: `recall`, `store`, `forget`, `summarize`. Zero implementations in WP-31. |
| Avatar Contract | `backend/app/agent/avatar/` | Define `IntentContentContract`. Agent produces structured intents, never UI markup. |
| Schema duplication | `backend/app/agent/schemas/agent_schemas.py` vs `backend/app/schemas/agent/` | Consolidate into single module. |
| API response model | `backend/app/schemas/agent/response.py` | Replace `AgentExecuteResponse` with `MissionStatusResponse`, `DecisionResponse`, etc. |

### REMOVE

| Component | Location | Why |
|-----------|----------|-----|
| Free-text intent pattern | `planner.py`, `orchestrator.py`, `routers/agent.py`, `schemas/agent/` | Chatbot architecture prohibited. Replace with structured missions. |
| Chatbot-style `/execute` endpoint | `backend/app/routers/agent.py` | Replace with mission-oriented endpoints. |
| Duplicate schema files | `backend/app/schemas/agent/request.py`, `response.py` | Consolidate into `backend/app/agent/schemas/`. |
| `_plan_training` and `_plan_general` | `backend/app/agent/core/planner.py` | Chatbot fallback patterns. Training is a structured workflow, not a keyword fallback. |
| Hardcoded `agent_id` | `backend/app/agent/core/orchestrator.py` | Make configurable. |
| "Agent" terminology in public API | `backend/app/routers/agent.py`, schemas | Rename to `digital_export_manager` or `dem` in API paths and response models to match product identity. |

---

## Resolved Architectural Decisions

| # | Decision | Resolution |
|---|----------|------------|
| 1 | Mission definition format | **Strongly-typed Pydantic Mission model.** Technology-independent domain object. API layer validates and converts to Mission. |
| 2 | Internal API call mechanism | **Direct service-layer call.** Tools call `app.services.*` functions directly. No HTTP overhead. Auth is internal. |
| 3 | Workflow definitions storage | **Database-backed.** `export_workflows` table already exists. Tools read workflow definitions from database. |
| 4 | Mission origin | **Both — user-issued via frontend + system-triggered.** User missions come from API. System missions come from scheduler, triggers, or monitoring. |
| 5 | Mission vs. ExportWorkflow relationship | **Missions USE the workflow tool.** Missions and ExportWorkflows are separate abstractions. A mission may invoke the workflow tool to transition an ExportWorkflow. |
| 6 | Package naming | **Keep `backend/app/agent/` as internal package.** Rename API paths to `/api/v1/digital-export-manager`. Internal subpackages: `decision_engine/`, `mission_planner/`, `execution_engine/`. |
| 7 | Decision Engine placement | **Inside `agent/` package as `decision_engine/` subpackage.** Not a separate top-level package. |
| 8 | API contract shape | **Single unified endpoint with discriminated union.** `POST /api/v1/digital-export-manager/missions` documented as "Create a Digital Export Manager operation." Request uses `MissionRequest` with `mission_type` discriminator and typed `payload`. |
| 9 | Mission ownership | **Execution Engine creates missions; Session owns them.** Missions are transient artifacts within a Session. |
| 10 | Workflow ownership | **ERP workflow service owns ExportWorkflows.** The Digital Export Manager interacts with workflows via the workflow tool. |
| 11 | Façade principle | **The Digital Export Manager API is a business façade.** Agent Intelligence implementation behind the façade may evolve without breaking the public API. |

---

## Gap Analysis

| Requirement | Current State | Gap |
|-------------|---------------|-----|
| Digital Export Manager as root bounded context | Partial — core loop exists as "Agent Orchestrator" | Rename/reorganize internal architecture to reflect DEM hierarchy |
| Decision Engine | Not implemented | New bounded context; extracts reasoning from orchestrator |
| Mission Planner | Partial — `Planner` exists but is keyword-based | Refactor to accept structured decisions |
| Execution Engine | Partial — `AgentOrchestrator` exists | Rename and align with mission-based execution |
| Company Knowledge Layer | Empty package | Define `KnowledgeProvider` interface; rename from "Knowledge Provider" |
| Memory Interface (WP-31) | Empty package | Define `MemoryProvider` interface |
| Tool Registry | Implemented | Compliant; add `version` field |
| Audit Layer | Implemented | Compliant; make `audit_ref` required |
| Avatar Contract | Empty package | Define `IntentContentContract` |
| Future Goal/Plan support | Not reserved | Reserve data structures for Goal and Plan even if not implemented in WP-30 |
| No chatbot patterns | Violated — free-text `intent` exists | Remove all free-text intent patterns |
| Mission as internal domain object | Violated — `intent: str` is public API | Replace with typed Mission model; API validates and converts |
| Business façade abstraction | Missing | API paths renamed to `/digital-export-manager`; internal Agent Intelligence can evolve independently |

---

## Revised Implementation Order

### Phase 1: Digital Export Manager Foundation (WP-30A)

| Task | Description |
|------|-------------|
| 1.1 | Rename/reorganize internal packages: `core/orchestrator.py` → `execution_engine/`, `core/planner.py` → `mission_planner/`, add `decision_engine/` |
| 1.2 | Define `Decision` object schema: output of Decision Engine, input to Mission Planner |
| 1.3 | Define `Mission` object schema with execution metadata + encapsulated business payload |
| 1.4 | Define `Task` object schema: atomic unit within a Mission |
| 1.5 | Refactor `BaseTool` to enforce full contract: `idempotency_key`, `auth_requirements`, `version` |
| 1.6 | Make `audit_ref` required in `ToolResult` |
| 1.7 | Consolidate duplicate schemas into `backend/app/agent/schemas/` |
| 1.8 | Make `agent_id` configurable via settings |
| 1.9 | Evolve API: add `/missions` endpoint with discriminated union request model; document as "Create a Digital Export Manager operation." Deprecate `/execute` intent pattern. |

### Phase 2: Execution Engine (WP-30B)

| Task | Description |
|------|-------------|
| 2.1 | Rename `AgentOrchestrator` to `ExecutionEngine` |
| 2.2 | ExecutionEngine accepts `Mission` objects (not free-text intents) |
| 2.3 | Add graceful degradation for unavailable tools |
| 2.4 | Add parallel step execution |
| 2.5 | Add retry-with-backoff per tool |
| 2.6 | Add structured step trace with reasoning states |
| 2.7 | Add idempotency key propagation |

### Phase 3: Mission Planner (WP-30C)

| Task | Description |
|------|-------------|
| 3.1 | Rename `Planner` to `MissionPlanner` |
| 3.2 | MissionPlanner accepts `Decision` objects (not free-text intents) |
| 3.3 | Decomposes decisions into missions with ordered tasks |
| 3.4 | Consults standing orders and user preferences |
| 3.5 | Never uses free-text keyword matching |

### Phase 4: Decision Engine (WP-30D)

| Task | Description |
|------|-------------|
| 4.1 | Create `DecisionEngine` in new package |
| 4.2 | Receives user requests |
| 4.3 | Queries Company Knowledge Layer and Memory Interface |
| 4.4 | Evaluates options against company rules |
| 4.5 | Produces `Decision` object |
| 4.6 | Handles approval gates for destructive operations |

### Phase 5: Tool Implementations (WP-30E)

| Task | Description |
|------|-------------|
| 5.1 | Implement 8 ERP tool wrappers |
| 5.2 | Each tool calls existing service layer directly |
| 5.3 | Each tool returns standardized envelope |
| 5.4 | Register all tools with version field |

### Phase 6: Company Knowledge Layer Interface (WP-30F)

| Task | Description |
|------|-------------|
| 6.1 | Define `KnowledgeProvider` interface |
| 6.2 | Define `KnowledgeQuery` contract |
| 6.3 | Define provider registry |
| 6.4 | Document ingestion contract (no implementation) |
| 6.5 | Decision Engine and Mission Planner can query knowledge |

### Phase 7: Memory Interface Definition (WP-30G)

| Task | Description |
|------|-------------|
| 7.1 | Define `MemoryProvider` interface: `recall`, `store`, `forget`, `summarize` |
| 7.2 | Agent core uses interface; graceful degradation when unavailable |
| 7.3 | WP-31 implements interface |

### Phase 8: Avatar Contract (WP-30H)

| Task | Description |
|------|-------------|
| 8.1 | Define `IntentContentContract` |
| 8.2 | Define `AvatarRenderer` interface |
| 8.3 | Agent produces structured intents, never UI markup |

### Phase 9: Advanced Features (WP-30I)

| Task | Description |
|------|-------------|
| 9.1 | Multi-step workflow executor using structured missions |
| 9.2 | Proactive monitoring with alert thresholds |
| 9.3 | Training mode as structured workflow |
| 9.4 | Human oversight: approval gates |

---

## What Must NOT Happen

1. **Do not** expose free-text `intent` as the primary interface
2. **Do not** put business logic in the Digital Export Manager core
3. **Do not** let the agent access databases directly
4. **Do not** implement knowledge ingestion in WP-30
5. **Do not** implement Avatar UI in WP-30
6. **Do not** design the system around an "Agent" entry point — the entry point is the Digital Export Manager
7. **Do not** mix business payload with execution metadata in the Mission model — they must be separate
8. **Do not** let tools receive raw API requests — they receive validated domain objects only
9. **Do not** expose internal orchestration concepts (Mission, Task, ExecutionPlan) in the public API more than necessary
10. **Do not** call the endpoint "Execute an Agent Mission" — it is "Create a Digital Export Manager operation"

---

## Implementation Issues (To Be Fixed During Execution)

| Issue | Location | Description |
|-------|----------|-------------|
| Missing `Field` import | `backend/app/agent/schemas/agent_schemas.py` lines 10, 27, 38 | `Field` is used without importing it from `pydantic`. Fix during Phase 1 schema consolidation. |

---

## Open Architectural Decisions

**All decisions resolved.** No remaining open questions. The plan is implementation-ready.
