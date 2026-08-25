# DEM Architecture Explorer v2 — Agent Path Evidence Reconciliation

## Status

**Phase:** 1 — Architecture Graph / Data Model  
**Scope:** Agent execution path expansion and evidence reconciliation  
**Runtime impact:** None. Documentation/data-model only.  
**Classification rule:** Repository implementation evidence is not automatically equivalent to verified runtime wiring.

## 1. Verified repository path

The repository contains the following Agent implementation areas:

```text
Session
  ↓
ReasoningEngine
  ↓
TaskPlanner
  ↓
ExecutionPlanner
  ↓
ToolOrchestrator
  ↓
ToolRegistry
  ↓
Concrete Tools
  ↓
Business Services
```

The important correction for the Explorer graph is that **the existence of each implementation layer is verified, but the current `main.py` evidence does not establish that the entire chain is wired into the active HTTP runtime path**.

Therefore the graph must distinguish:

- `implemented_runtime` — verified runtime wiring;
- `implemented_non_primary` — implementation exists and has architectural/runtime-facing contracts, but primary active wiring is not established by the inspected bootstrap evidence;
- `unverified` — insufficient evidence for the assertion.

## 2. Session

**Identity:** Agent Session subsystem  
**Path:** `backend/app/agent/session/`  
**Graph status:** `implemented_runtime` only where runtime/session integration is separately evidenced; otherwise do not infer additional call edges.

The Evidence Inventory already establishes Session as a required part of the Agent execution model. The Explorer must not fabricate a direct `Session → ReasoningEngine` call merely from directory co-location.

## 3. ReasoningEngine

**Identity:** `ReasoningEngine`  
**Implementation:** `backend/app/agent/decision_engine/engine.py`  
**Class:** `ReasoningEngine`

Verified behavior:

1. Reads `intent`, parameters, and context.
2. Maps intent to candidate paths.
3. Queries Memory.
4. Queries Knowledge through `KnowledgeOrchestrator` when attached, otherwise uses the legacy provider path.
5. Applies memory biases.
6. Evaluates candidates.
7. Optionally enhances candidate selection and reasoning through the LLM registry / Gemini provider.
8. Selects the best path.
9. Checks Approval.
10. Creates a `Decision`.
11. Persists significant decisions through the configured memory provider when available.

Evidence: `backend/app/agent/decision_engine/engine.py`.

Bootstrap evidence: `backend/main.py` creates `ReasoningEngine`, attaches the Knowledge Orchestrator when available, and stores it in `app.state.reasoning_engine`.

Therefore:

```text
ReasoningEngine --knowledge_flow--> Knowledge Integration
ReasoningEngine --memory_flow--> Memory
ReasoningEngine --depends_on--> LLM Integration
ReasoningEngine --invokes--> Approval
```

are evidence-backed relationships.

## 4. TaskPlanner

**Identity:** `TaskPlanner`  
**Implementation:** `backend/app/agent/mission_planner/planner.py`  
**Class:** `TaskPlanner`

Verified behavior:

1. Validates a Decision.
2. Maps `chosen_path` to `MissionType`.
3. Consults standing orders and user preferences through Memory when available.
4. Creates a `Mission`.
5. Creates ordered `Task` objects.
6. Creates an `ExecutionPlan`.
7. Each task contains a concrete `tool_name`.

The deterministic task sequences are explicitly implemented for shipping, ETA invoice, customs, documents, search, dashboard, notifications, and workflow.

Important boundary:

`TaskPlanner` is **not** the Tool Orchestrator. It creates task definitions; it does not itself execute the tools.

## 5. ExecutionPlanner

**Identity:** `ExecutionPlanner`  
**Implementation:** `backend/app/agent/execution_planner/planner.py`  
**Class:** `ExecutionPlanner`

Verified behavior:

- Reads a Mission.
- Determines execution mode from `execution_policy`, defaulting to sequential execution.
- Obtains task definitions from the Mission or embedded ExecutionPlan.
- Constructs an `ExecutionPlan`.
- Returns the plan and execution mode.

Boundary:

`ExecutionPlanner` prepares an ExecutionPlan for execution; it does not invoke concrete tools.

## 6. ToolOrchestrator / Execution Engine

**Identity:** `ToolOrchestrator`  
**Implementation:** `backend/app/agent/execution_engine/orchestrator.py`  
**Class:** `ToolOrchestrator`

Verified behavior:

- Accepts an ExecutionPlan, Mission, or task dictionary.
- Executes tasks sequentially.
- Enforces task dependencies.
- Checks Approval before execution.
- Resolves tools through `ToolRegistry`.
- Instantiates tools.
- Propagates idempotency keys.
- Executes tools with retry/backoff logic.
- Produces structured execution traces.
- Records monitoring information.
- Updates mission status through a Session Manager when available.
- Produces failure summaries and degraded-execution information.

The exact runtime implementation relationship is therefore:

```text
ToolOrchestrator
    --depends_on--> ToolRegistry
    --invokes--> Concrete Tool
    --invokes--> ApprovalGate
    --monitored_by--> MonitoringService
```

The module is named `execution_engine`; the class providing the orchestration behavior is `ToolOrchestrator`. The Explorer must preserve both identities instead of incorrectly treating `ToolOrchestrator` as a separate directory that does not exist.

## 7. Tool Registry

**Identity:** `ToolRegistry`  
**Implementation:** `backend/app/agent/tools/registry.py`

Verified behavior:

- Registers tool classes by `tool_name`.
- Unregisters tools.
- Resolves tool classes.
- Lists tool metadata.
- Checks whether a tool exists.
- Instantiates concrete tools.
- Exposes versions.

Therefore:

```text
ToolOrchestrator --delegates_to--> ToolRegistry
```

is evidence-backed by the `has_tool()` and `create_instance()` calls in `execution_engine/orchestrator.py`.

## 8. Concrete Tools

The repository contains concrete tools in `backend/app/agent/tools/erp_tools.py`.

Verified concrete tool identities include at least:

```text
shipping_get_rates
shipping_create_shipment
shipping_print_label
eta_submit_invoice
eta_check_status
customs_get_declarations
customs_file_declaration
documents_generate
documents_upload
search_global
```

Additional tool definitions in the file must be reconciled in the next seed-expansion pass rather than silently omitted from the final graph.

## 9. Tool → Business Service evidence

The concrete tools directly import and invoke business services. Examples verified in `erp_tools.py`:

```text
ShippingGetRatesTool
    → app.services.shipping.fetch_rates

ShippingCreateShipmentTool
    → app.services.shipping.create_shipment

ShippingPrintLabelTool
    → app.services.shipping.get_label

EtaSubmitInvoiceTool
    → app.services.eta.submit_invoice_to_eta

EtaCheckStatusTool
    → app.services.eta.get_eta_invoice_status

CustomsGetDeclarationsTool
    → app.services.customs.list_declarations / get_declaration

CustomsFileDeclarationTool
    → app.services.customs.submit_declaration

DocumentsGenerateTool
    → app.services.document.create_document

DocumentsUploadTool
    → app.services.document.upload_document

SearchGlobalTool
    → app.services.search.search_all
```

These are the edges that should replace any earlier generic or inferred `ReasoningEngine → Business Services` shortcut.

## 10. Critical runtime-wiring finding

The inspected `backend/main.py` explicitly creates and wires:

- `KnowledgeProviderRegistry`
- `KnowledgeOrchestrator`
- `ReasoningEngine`
- Memory provider
- LLM provider
- Knowledge providers
- routers
- schedulers

However, the inspected bootstrap section does **not** explicitly construct and attach `TaskPlanner`, `ExecutionPlanner`, `ToolOrchestrator`, or `ToolRegistry` to the FastAPI application state.

Therefore the graph must **not** claim an end-to-end active runtime chain merely because the classes and modules exist.

This is not a defect declaration. It is an evidence classification decision. Any additional integration discovered elsewhere must be added only after direct repository evidence is identified.

## 11. Required graph relationships

The next Agent graph expansion should model the following with the stated evidence level:

```text
Agent
 ├─contains→ ReasoningEngine
 ├─contains→ TaskPlanner
 ├─contains→ ExecutionPlanner
 ├─contains→ ToolOrchestrator
 ├─contains→ ToolRegistry
 └─contains→ Concrete Tools

ReasoningEngine
 ├─knowledge_flow→ Knowledge Integration
 ├─memory_flow→ Memory
 ├─depends_on→ LLM Integration
 └─invokes→ Approval

TaskPlanner
 └─produces→ Mission/Task definitions

ExecutionPlanner
 └─produces→ ExecutionPlan

ToolOrchestrator
 ├─delegates_to→ ToolRegistry
 ├─invokes→ Concrete Tools
 ├─invokes→ Approval
 └─monitored_by→ MonitoringService

Concrete Tool
 └─invokes→ Business Service
```

`produces` is a graph semantic that should be added to the controlled edge vocabulary because plan-production is not accurately represented by `depends_on` or `delegates_to`.

## 12. Acceptance condition for this reconciliation pass

This pass is complete only when:

1. The Agent implementation nodes are represented individually.
2. No nonexistent `tool_orchestrator/` directory is invented; the implementation identity remains `execution_engine/orchestrator.py` + `ToolOrchestrator`.
3. Task planning is distinguished from execution planning.
4. Execution planning is distinguished from execution/orchestration.
5. Tool Registry is distinguished from concrete Tools.
6. Concrete Tool → Business Service calls are represented using exact implementation evidence.
7. Runtime wiring is not claimed where bootstrap evidence is absent.
8. The earlier generic Reasoning → Business Services shortcut is not used as a substitute for the real intermediate path.
9. The remaining concrete tools and their service calls are reconciled before the Agent graph is called complete.
