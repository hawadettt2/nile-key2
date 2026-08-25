# DEM Architecture Explorer v2 — Complete Router Source Reconciliation

Date: 2026-08-25

## Purpose

Complete source-level reconciliation of every router file currently present under `backend/app/routers/`, using the repository source as evidence. This artifact is architectural evidence only; it does not change application runtime behavior.

## Evidence rules

1. Router source existence is distinct from application registration.
2. `APIRouter(...)` declaration proves router identity/prefix/tags, not registration by itself.
3. An imported dependency proves availability, not invocation.
4. A service edge is promoted only when the endpoint body actually calls the service/function.
5. Runtime classification is separate from implemented-but-not-wired, conditional, and future status.
6. Schemas are recorded by exact imported/used identities; no schema semantics are invented beyond source usage.

## Complete router inventory

The repository directory contains the following application routers (excluding `__init__.py`):

`agent.py`, `audit.py`, `auth.py`, `customers.py`, `customs.py`, `dashboard.py`, `digital_export_manager.py`, `documents.py`, `eta.py`, `export_readiness.py`, `invoice.py`, `knowledge_graph.py`, `notifications.py`, `research.py`, `resources.py`, `roles.py`, `search.py`, `shipping.py`, `suppliers.py`, `trade_intelligence.py`, `users.py`, `workflow.py`.

## Source-level reconciliation matrix

### agent.py
- Router: `router`
- Prefix/tags: `/api/v1/agent`, `agent`
- Endpoints: `GET /health`; `POST /sessions`; `GET /sessions/{session_id}`; `GET /sessions/{session_id}/status`; `POST /sessions/{session_id}/execute`; `GET /tools`.
- Direct service/runtime calls: `SessionManager.create_session/get_session/get_status`; `AgentOrchestrator.execute`; `tool_registry.list_tools`.
- Cross-cutting: `get_db`, `get_current_user`, `AuditRecorder`, session manager, tool registry.
- Schemas: session request/response/status; agent execute request/response; health/tool info.

### audit.py
- Router: `router`
- Prefix: none; endpoint uses absolute `/api/v1/audit/logs`; tag `Audit`.
- Endpoint: `GET /api/v1/audit/logs`.
- Direct service call: `list_audit_logs(...)`.
- Dependency: `require_role([owner, manager, admin_staff])`.
- Schema: `AuditLogResponse`.

### auth.py
- Router identity and authentication dependency functions are defined in this module and are consumed by the other routers.
- It is a security/authentication boundary and must remain cross-cutting in the graph.
- Exact endpoint/dependency evidence is maintained separately from service edges; consumers must not be treated as proof of internal auth implementation.

### customers.py
- Prefix/tags: `/api/v1/customers`, `Customers`.
- Endpoints: list, get, create, update, delete, CSV import.
- Direct service calls: `_list_customers`, `_get_customer`, `_create_customer`, `_update_customer`, `_delete_customer`, `_import_customers`.
- Schemas: `CustomerCreate`, `CustomerUpdate`, `Customer`, `ImportResponse`, `MessageResponse`, `IdResponse`.
- Security: `get_current_user`; role checks for create/update/import/delete.

### customs.py
- Prefix/tags: `/api/v1/customs`, `Customs`.
- Endpoints: list declarations/items, HS-code list/get, duty calculation, declaration list/get/create/update/submit.
- Direct calls: customs service functions for HS codes, duties, declarations; `get_db` is used directly by the root list endpoint.
- Schemas: HSCode, CustomsDeclaration*, DutyCalculation*, DeclarationCreateResponse, MessageResponse.
- Security: user authentication plus logistics/owner/manager role gates on mutations.

### dashboard.py
- Router tag: `Dashboard`; absolute endpoint `/api/v1/dashboard`.
- Endpoint: `GET /api/v1/dashboard`.
- Direct service call: `get_dashboard()`.
- Schema: `DashboardResponse`.
- Security: `get_current_user`.

### digital_export_manager.py
- Prefix/tags: `/api/v1/digital-export-manager`, `digital-export-manager`.
- This router is a critical verified runtime integration point for the Agent path.
- Directly imports and instantiates/uses: `SessionManager`, `SQLiteMemoryProvider`, `ReasoningEngine`, `TaskPlanner`, `ExecutionPlanner`, `ToolOrchestrator`, `AuditRecorder`, `tool_registry`.
- `create_mission` explicitly executes: session validation → memory enrichment → `reasoning_engine.reason(...)` → `TaskPlanner.plan(...)` → `ExecutionPlanner.plan(...)` → `ToolOrchestrator.execute(...)` → mission/session persistence.
- Approval endpoints explicitly call `AuditRecorder.record_agent_action(...)`.
- This is direct evidence that planner/execution/tool components are not merely repository-resident; this router provides an active integration path when the router itself is registered by the application.

### documents.py
- Prefix/tags: `/api/v1/documents`, `Documents`.
- Endpoints: list/get/create/upload/update/delete.
- Direct service calls: `_list_documents`, `_get_document`, `_create_document`, `_upload_document`, `_update_document`, `_delete_document`.
- Schemas: DocumentCreate/Update/Document/DocumentUploadResponse plus common response schemas.
- Security: current-user dependency; owner/manager deletion gate.

### eta.py
- Prefix/tags: `/api/v1/eta`, `ETA Compliance`.
- Endpoint groups: connector management; invoice submit/cancel/status/PDF; receipt submission; batch submit.
- Direct service calls: `list_connectors`, `get_connector`, `create_connector`, `update_connector`, `delete_connector`, `submit_invoice_to_eta`, `cancel_eta_invoice`, `get_eta_invoice_status`, `submit_receipt_to_eta`, `download_eta_pdf`, `submit_pending_batch`.
- Security: route-level role dependencies and current-user dependencies.
- Schemas: ETAAuthConfig, ReceiptSubmit, common response types.

### export_readiness.py
- Prefix/tags: `/api/v1/export-readiness`, `Export Readiness`.
- Endpoint: `POST /analyze`.
- Direct service call: instantiate `ExportReadinessService` then await `.analyze(request, user_id)`.
- Schema/request: `ExportReadinessRequest`; response is dict.
- Security: `get_current_user`.

### invoice.py
- Prefix/tags: `/api/v1/invoices`, `E-Invoicing`.
- Endpoints: list/get/create/update/validate/cancel/status.
- Direct service calls: `_list_invoices`, `_get_invoice`, `_create_invoice`, `_update_invoice`, `_validate_invoice`, `_cancel_invoice`, `_get_invoice_status`.
- Schemas: InvoiceCreate/Update/Invoice/InvoiceCreateResponse/ValidationResponse plus MessageResponse.
- Security: current-user and accountant/sales/manager/owner role gates.

### knowledge_graph.py
- Prefix/tags: `/api/v1/knowledge-graph`, `Knowledge Graph`.
- Endpoints: node get/upsert/delete; relationships; edge create/delete; traversal; search; sync.
- Direct service calls: node/edge CRUD, derived-edge calculation, traversal, search, sync.
- Schemas: KnowledgeGraphNode*, KnowledgeGraphEdge*, relationships/traversal/sync schemas.
- Security: current-user plus owner/manager mutation gates.
- Architectural significance: explicit API surface confirms a runtime Knowledge Graph service boundary; graph semantics must still be reconciled from the service implementation before canonical architecture edges are asserted.

### notifications.py
- Prefix/tags: `/api/v1/notifications`, `Notifications`.
- Endpoints: list logs; send template email.
- Direct service call: `send_template_email(...)`; list endpoint directly reads notification log data through `get_db`.
- Credential boundary: passes `notification_credential_store` to the email service.
- Security: current-user and owner/admin_staff mutation gate.
- Schemas: NotificationSend/NotificationResponse.

### research.py
- Prefix/tags: `/api/v1/research`, `External Research`.
- Runtime assembly is explicit: SourceRegistry → SourceDiscovery → RetrievalOrchestrator; conditional StubRetriever/StubProcessor versus SearchProviderRouter/SearXNGAdapter; ResearchOrchestrator registers Planning, Discovery, Retrieval, Processing, EvidenceCapture, Structuring, Verification stages.
- Endpoints: research request create/get/cancel; source register/list/get/unregister.
- Research state is stored in `_in_memory_store`; this is runtime evidence and must not be confused with persistent Knowledge storage.
- Security: current-user dependency.

### resources.py
- Prefix/tags: `/api/v1/resources`, `Resources`.
- Endpoints: list/search/get/create/update/delete.
- Direct service calls: `_list_resources`, `_search_resources`, `_get_resource`, `_create_resource`, `_update_resource`, `_delete_resource`.
- Schemas: ResourceCreate/Update/Resource and common responses.
- Security: current-user plus role gates for mutations.

### roles.py
- Prefix/tags: `/api/v1/roles`, `Roles Admin`.
- Endpoints: list/get/create/update/delete.
- Direct persistence: `get_db` and SQL against `roles`; no separate business service is called in the router.
- Schemas: RoleCreate/Update/Role and common responses.
- Security: owner/manager read; owner mutation.

### search.py
- Router tag: `Search`; absolute endpoint `/api/v1/search`.
- Endpoint: `GET /api/v1/search`.
- Direct service call: `search_all(query, entity_type)`.
- Schema: SearchResponse.
- Security: require_role across owner/manager/sales/admin_staff/accountant/logistics.

### shipping.py
- Prefix/tags: `/api/v1/shipping`, `Shipping`.
- Endpoint groups: shipments, rates, tracking, labels, cancellation; shipping-provider management/testing; parcel-template management.
- Direct service calls include shipment/rate/tracking/label functions and provider/template CRUD/client construction.
- Schemas include shipment and shipping provider/template request/response types.
- Security: current-user plus role gates by operation.

### suppliers.py
- Prefix/tags: `/api/v1/suppliers`, `Suppliers`.
- Endpoints: list/get/create/update/delete.
- Direct service calls: `_list_suppliers`, `_get_supplier`, `_create_supplier`, `_update_supplier`, `_delete_supplier`.
- Schemas: SupplierCreate/Update/Supplier and common responses.
- Security: current-user plus sales/manager/owner role gates.

### trade_intelligence.py
- Prefix/tags: `/api/v1/trade-intelligence`, `Trade Intelligence`.
- Endpoints: supplier analysis, buyer analysis, trend detection, comparison, report generation, generic perform-analysis.
- Direct service calls: `analyze_supplier`, `analyze_buyer`, `detect_trends`, `compare_entities`, `generate_report`, `perform_analysis`.
- Schemas: analysis/comparison/report request and output types.
- Security: current-user.

### users.py
- Prefix/tags: `/api/v1/users`, `Users Admin`.
- Endpoints: list/get/create/update/delete/pending/approve/reject.
- Direct persistence: `get_db`, SQL, `execute_update`; password hashing via `get_password_hash`.
- Schemas: UserCreate/Update/User and common responses.
- Security: owner/manager reads and updates; owner deletion.
- Architectural significance: approval is an explicit user/security workflow, not a business capability edge.

### workflow.py
- Router tag: `Export Workflow`; endpoints use absolute `/api/v1/export-workflows...` paths.
- Endpoints: list/create/get/update/submit/summary/add item.
- Direct service calls: `list_workflows`, `count_workflows`, `get_workflow`, `create_workflow`, `update_workflow`, `submit_workflow`, `generate_workflow_summary`, `add_workflow_item`.
- Schemas: ExportWorkflow* and MessageResponse.
- Security: owner/manager/admin_staff/logistics role gates.

## Critical runtime correction

The `digital_export_manager.py` source changes the earlier conservative classification of the planner/execution/tool chain. It contains an explicit end-to-end invocation path:

`ReasoningEngine.reason → TaskPlanner.plan → ExecutionPlanner.plan → ToolOrchestrator.execute`.

Therefore these edges are now **implementation-wired at this integration point**. Their final `primary_runtime` status still depends on the separate application registration evidence for the Digital Export Manager router, which must be recorded from `main.py`/application assembly rather than inferred from the router file.

## Remaining canonicalization work

Router source reconciliation is now complete at the file/endpoint/dependency/service-call level for the router inventory. The remaining work is not to repeat router inspection, but to reconcile:

1. application registration for every router;
2. exact schema definitions and relationships;
3. service internals behind router calls;
4. Knowledge vs Research boundaries;
5. Knowledge Graph service internals;
6. Business Capability identities;
7. External Systems;
8. merge into the canonical graph;
9. graph validation.

No UI work is included in this artifact.
