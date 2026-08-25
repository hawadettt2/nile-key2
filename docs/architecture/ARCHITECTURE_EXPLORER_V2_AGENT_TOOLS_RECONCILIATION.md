# DEM Architecture Explorer v2 — Agent Tools Reconciliation

## Purpose

Evidence reconciliation for the concrete Agent Tools required by the V2 Architecture Explorer. This document identifies exact tool classes, tool names, implementation paths, direct business-service targets, and execution semantics without claiming primary runtime wiring where bootstrap evidence does not establish it.

## Status vocabulary

- **implemented_non_primary** — implementation exists and is callable through the Agent execution machinery, but inspected primary application wiring does not establish it as the active default runtime path.
- **direct_service_boundary** — the tool directly delegates business operation to a service function.

## Verified concrete tools

| Domain | Tool class | Tool name | File | Direct service target | Side effect | Auth |
|---|---|---|---|---|---|---|
| Shipping | `ShippingGetRatesTool` | `shipping_get_rates` | `backend/app/agent/tools/erp_tools.py` | `app.services.shipping.fetch_rates()` | READ | authenticated |
| Shipping | `ShippingCreateShipmentTool` | `shipping_create_shipment` | `backend/app/agent/tools/erp_tools.py` | `app.services.shipping.create_shipment()` | WRITE | role-based: owner, manager, sales, logistics |
| Shipping | `ShippingPrintLabelTool` | `shipping_print_label` | `backend/app/agent/tools/erp_tools.py` | `app.services.shipping.get_label()` | READ | authenticated |
| ETA | `EtaSubmitInvoiceTool` | `eta_submit_invoice` | `backend/app/agent/tools/erp_tools.py` | `app.services.eta.submit_invoice_to_eta()` | WRITE | role-based: owner, accountant |
| ETA | `EtaCheckStatusTool` | `eta_check_status` | `backend/app/agent/tools/erp_tools.py` | `app.services.eta.get_eta_invoice_status()` | READ | authenticated |
| Customs | `CustomsGetDeclarationsTool` | `customs_get_declarations` | `backend/app/agent/tools/erp_tools.py` | `app.services.customs.list_declarations()` / `get_declaration()` | READ | authenticated |
| Customs | `CustomsFileDeclarationTool` | `customs_file_declaration` | `backend/app/agent/tools/erp_tools.py` | `app.services.customs.submit_declaration()` | WRITE | role-based: owner, manager, logistics |
| Documents | `DocumentsGenerateTool` | `documents_generate` | `backend/app/agent/tools/erp_tools.py` | `app.services.document.create_document()` | WRITE | authenticated |
| Documents | `DocumentsUploadTool` | `documents_upload` | `backend/app/agent/tools/erp_tools.py` | `app.services.document.upload_document()` | WRITE | authenticated |
| Search | `SearchGlobalTool` | `search_global` | `backend/app/agent/tools/erp_tools.py` | `app.services.search.search_all()` | READ | tool declares no auth requirement; registry/orchestrator policy remains authoritative |

## Boundary conclusions

### 1. Tools are an orchestration boundary, not the business layer

The concrete tools adapt Agent parameters/context into service-layer requests and return `ToolResult`. They do not own the underlying shipping, customs, ETA, document, or search business logic.

### 2. ToolRegistry is the resolution boundary

`ToolRegistry` maps tool names to concrete classes and exposes registration, lookup, availability, instantiation, and version metadata. `ToolOrchestrator` resolves concrete tools through this registry before execution.

### 3. ToolOrchestrator is implemented under Execution Engine

The repository identity is:

`backend/app/agent/execution_engine/orchestrator.py`

with class `ToolOrchestrator`. The Explorer must not invent a separate `tool_orchestrator/` package.

### 4. Runtime status remains conservative

The tools and their orchestration machinery are implemented, but the inspected `backend/main.py` application bootstrap does not establish these components as the primary default execution path. Therefore the Explorer graph should preserve `implemented_non_primary` until runtime wiring is explicitly reconciled.

## Evidence

Primary evidence:

- `backend/app/agent/tools/erp_tools.py`
- `backend/app/agent/tools/registry.py`
- `backend/app/agent/execution_engine/orchestrator.py`
- `backend/main.py`

The concrete tool implementations define their input/output schemas, side effects, idempotency, authorization requirements, and direct service calls in `erp_tools.py`.

## Explorer mapping

The canonical model should eventually expose the chain at Level 3 as:

`Execution Engine → Tool Registry → Concrete Tool → Business Service → Service Function`

Examples:

`ShippingCreateShipmentTool → services.shipping.create_shipment()`

`CustomsFileDeclarationTool → services.customs.submit_declaration()`

`EtaSubmitInvoiceTool → services.eta.submit_invoice_to_eta()`

`DocumentsGenerateTool → services.document.create_document()`

`SearchGlobalTool → services.search.search_all()`

No direct `ReasoningEngine → Business Service` edge should be used to hide these intermediate boundaries.
