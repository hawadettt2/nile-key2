# Proposed: Frontend AI/DEM User Experience Work Package

**Work Package:** Proposed — Frontend AI/DEM User Experience  
**Phase:** Post-WP-42 — Intelligent Platform Product Exposure  
**Baseline:** d4347f7 (current HEAD)  
**Authority:** PLAN.md (Master Roadmap v2.1) — Single Source of Truth  
**Governing Documents:** `PLAN.md` Section 23, `.kilo/plans/WP-42-spec.md`, `.kilo/plans/archive/wp30-implementation-plan.md`, `.kilo/plans/MEMORY_CONTRACT.md`, `.kilo/plans/AVATAR_CONTRACT.md`  
**Date:** 2026-08-01  
**Status:** Implementation-Ready — Pending Owner Approval  

---

## 1. Executive Summary

This Work Package transforms the existing backend Intelligent Platform into a **user-visible, usable AI/DEM product experience**. The backend Digital Export Manager, reasoning engine, execution engine, knowledge graph, trade intelligence, memory providers, and approval detection are fully implemented and tested. However, the Frontend currently exposes **zero** of these capabilities. The product as experienced by the user is a traditional ERP system with no visible AI layer.

This WP does **not** rebuild backend capabilities. It integrates existing public APIs into the Frontend, adds minimal backend API enhancements where verified as necessary, and delivers a cohesive user experience that presents the DEM as the **"Executive Intelligence / Business Façade"** envisioned in the architecture plan.

**Core principle maintained:** *"The DEM is the mind; the ERP is the hands. The user directs the mind; the mind operates the hands."*

All open decisions have been closed based on repository evidence. See Section 14.

---

## 2. Scope

### 2.1 In Scope — MVP (Must Have)

| Component | Description | Type |
|-----------|-------------|------|
| **DEM Connect/Disconnect UI** | Session management interface for starting/ending DEM sessions | Frontend |
| **Mission Composer** | Form to submit structured missions to the DEM using existing mission types | Frontend + backend API enhancement |
| **Mission Dashboard** | List of missions, status tracking, detail view with results | Frontend |
| **Execution Progress** | Polling-based execution status updates | Frontend only — uses existing API |
| **Reasoning Viewer** | Display DEM decision trace returned from backend | Frontend + backend API enhancement |
| **Approval Inbox** | Interface for managers to review approval-required missions | Frontend + minimal backend API |
| **Knowledge Explorer** | Entity search and relationship tree/list view | Frontend only — uses existing API |
| **Intelligence Dashboard** | Supplier analysis and trend detection with charts | Frontend only — uses existing API |
| **Navigation Integration** | DEM entry in sidebar, routing, protected routes | Frontend |
| **API Client Integration** | DEM/KG/TI API functions in `services/api.ts` | Frontend |
| **Backend: MissionResponse expansion** | Add `reasoning`, `requires_approval`, `approval_status` to response | Backend — minimal change |
| **Backend: MissionStatus enum** | Add `pending_approval` status | Backend — minimal change |
| **Backend: Orchestrator approval handling** | Set mission status to `pending_approval` instead of `failed` when approval is required | Backend — minimal change |
| **Backend: Approval API** | 3 new endpoints for approval workflow | Backend — minimal change |

### 2.2 Explicitly Out of Scope

| Item | Reason |
|------|--------|
| Backend DEM core reconstruction | Already implemented and tested |
| LLM integration | Explicitly out of scope per `wp30-implementation-plan.md` L105-106 |
| Knowledge ingestion pipeline | Deferred to future WP per `KNOWLEDGE_INGESTION_CONTRACT.md` Section 5 |
| Goal/Plan reasoning layers | Reserved for future WP per `wp30-implementation-plan.md` L104, L534 |
| Avatar UI implementation | Explicitly excluded per `WP-30I-spec.md` L28 |
| PostgreSQL migration | Out of scope per current phase |
| Training Mode UI | Internal testing feature; not user-facing |
| Monitoring Service UI | Internal operations feature; not user-facing |
| Full Knowledge Graph visualization | Post-MVP — tree/list view sufficient for MVP |
| Buyer analysis / Entity comparison | Post-MVP — lower business priority than supplier analysis and trends |
| PDF report generation | Post-MVP — CSV download sufficient for MVP |
| WebSocket/SSE real-time | Post-MVP — polling sufficient for MVP |
| Inline approval UX | Post-MVP — separate inbox chosen for MVP |
| Approval resume/halt logic | Post-MVP — MVP records decision only; execution remains paused |

---

## 3. Closed Decisions (Evidence-Based)

### Decision 1: Priority vs WP-42

**Decision:** WP-42 closes first on its current scope. This WP begins after WP-42 closure as the next implementation WP.

**Rationale:**
- WP-42 is currently DEFERRED but remains the active acceptance gate for the existing product.
- This WP delivers new product capability that requires new UAT scope.
- The current `docs/appendices/UAT_CHECKLIST.md` explicitly excludes Frontend GUI rendering and AI/DEM functionality from its scope (L532-535).
- Adding AI/DEM to WP-42 UAT would expand WP-42 scope beyond its acceptance-driven nature.
- Cleaner governance: WP-42 closes the current product; this WP delivers the next product iteration.

**Execution sequence:**
1. WP-42 closes on current scope (traditional ERP UI).
2. This WP implements AI/DEM Frontend UX.
3. A new acceptance gate validates the AI/DEM surfaces.

### Decision 2: Real-Time Progress — Polling

**Decision:** Polling via `GET /api/v1/digital-export-manager/sessions/{session_id}`.

**Rationale:**
- The `/missions` endpoint is synchronous and blocks until completion — verified in `backend/app/routers/digital_export_manager.py` L111-210.
- No WebSocket or SSE infrastructure exists in the current backend — verified in `backend/main.py`.
- `SessionDetailResponse` already includes `missions: List[Dict[str, Any]]` — verified in `backend/app/agent/schemas/session.py` L54-62.
- Each mission dict includes `status` field from `MissionStatus` enum — verified in `backend/app/agent/schemas/enums.py`.
- Polling requires **zero backend changes**. The data needed for progress display is already returned by the existing API.
- Polling interval: 3 seconds during active mission execution, 15 seconds when idle.

**Frontend behavior:**
- `pending` → show spinner with "Mission queued..."
- `running` → show progress indicator with step count
- `completed` → show results
- `failed` → show error with details
- `pending_approval` → show approval pending message and link to Approval Inbox

### Decision 3: Approval UX — Separate Approval Inbox

**Decision:** Separate `/digital-export-manager/approvals` page. Not inline within mission flow.

**Rationale:**
- Approval is a manager function, not an employee function.
- Approval requires RBAC (`owner`/`manager` roles) — verified in existing `require_role` decorator pattern.
- Separate inbox allows managers to review all pending approvals in one place.
- Aligns with existing notification patterns in the product (`/notifications` page).
- Simpler to implement: dedicated page with list, detail, and action buttons.

**Current backend behavior (verified):**
- `ApprovalGate.check_approval()` exists and is wired into `ToolOrchestrator` — verified in `backend/app/agent/execution_engine/orchestrator.py` L178-208.
- When approval is required, the orchestrator sets `mission_status = MissionStatus.FAILED.value` and `execution_status="pending_approval"` on the task — verified at L197.
- The mission is saved with status "failed" — verified in `backend/app/routers/digital_export_manager.py` L182-186.
- **No pause-and-resume mechanism exists.** The mission fails; execution does not continue.

**MVP approval flow:**
1. DEM detects approval requirement during mission execution
2. Task is marked `pending_approval`; mission status changes from "failed" to "pending_approval"
3. Manager opens Approval Inbox → sees pending approval with mission context
4. Manager clicks Approve or Reject
5. Decision is recorded in `agent_audit_logs`
6. Mission remains in `pending_approval` state
7. **Resume/halt logic is Post-MVP**

**Backend minimum required for MVP:**
- Add `pending_approval` to `MissionStatus` enum
- Modify orchestrator to set `mission_status = MissionStatus.PENDING_APPROVAL.value` instead of `FAILED.value` when approval is required
- Modify router to preserve `pending_approval` status in `MissionResponse`
- Reuse `agent_audit_logs` table for approval record persistence (no new table needed)
- 3 new endpoints:
  - `GET /api/v1/digital-export-manager/approvals` — list pending approvals
  - `POST /api/v1/digital-export-manager/approvals/{id}/approve` — approve
  - `POST /api/v1/digital-export-manager/approvals/{id}/reject` — reject

### Decision 4: Knowledge Graph MVP — Tree/List Exploration

**Decision:** Tree/List exploration via existing search and traverse endpoints. No graph visualization library in MVP.

**Rationale:**
- Full graph visualization (D3.js, Cytoscape.js) adds significant complexity and dependency weight.
- The existing Knowledge Graph APIs already support search and traversal — verified in `backend/app/routers/knowledge_graph.py`.
- Tree/list view using existing `/search` and `/traverse` endpoints delivers the core value: finding entities and understanding relationships.
- Graph visualization can be added in Post-MVP if business requires it.
- MVP uses existing Recharts library (already in frontend) for any relationship charts.

**MVP surfaces:**
- Search bar → calls `/api/v1/knowledge-graph/search`
- Entity detail → calls `/api/v1/knowledge-graph/nodes/{entity_type}/{entity_id}`
- Relationships → calls `/api/v1/knowledge-graph/nodes/{entity_type}/{entity_id}/relationships`
- Relationship traversal → calls `/api/v1/knowledge-graph/traverse/{entity_type}/{entity_id}`

### Decision 5: Trade Intelligence MVP — Supplier Analysis + Trends

**Decision:** Supplier analysis and trend detection only. Buyer analysis, comparison, and reports deferred to Post-MVP.

**Rationale:**
- Business context: Nile Key is an export platform. Supplier intelligence is the highest-value analysis for export operations.
- Trends detection supports proactive decision-making.
- Buyer analysis and comparison are valuable but secondary to supplier analysis in the current business context.
- Report generation (CSV/PDF) is nice-to-have; on-screen results are sufficient for MVP.
- Verified APIs exist: `/api/v1/trade-intelligence/suppliers/analyze` and `/api/v1/trade-intelligence/trends/detect` — verified in `backend/app/routers/trade_intelligence.py`.

### Decision 6: Mission Types — All 8 Existing Types

**Decision:** Expose all 8 existing mission types in the Mission Composer for MVP.

**Rationale:**
- The backend already defines 8 mission types in `MissionType` enum — verified in `backend/app/agent/schemas/enums.py`.
- Each mission type maps directly to an existing ERP tool — verified in `backend/app/agent/tools/erp_tools.py`.
- The tools are already registered in `ToolRegistry` and exposed via `/api/v1/digital-export-manager/tools` — verified in `backend/app/routers/digital_export_manager.py` L262-268.
- Limiting mission types in MVP would require arbitrary exclusion criteria not supported by architecture or business requirements.
- The Mission Composer UI will present mission types as selectable cards/buttons with context-aware payload forms.

**Mission types available in MVP:**
1. `CREATE_SHIPMENT` → `shipping_create_shipment` tool
2. `SUBMIT_INVOICE` → `eta_submit_invoice` tool
3. `FILE_CUSTOMS` → `customs_file_declaration` tool
4. `GENERATE_DOCUMENT` → `documents_generate` tool
5. `SEARCH_ENTITIES` → `search_global` tool
6. `GET_DASHBOARD` → `dashboard_get_stats` tool
7. `SEND_NOTIFICATION` → `notifications_send` tool
8. `TRANSITION_WORKFLOW` → `workflow_transition` tool

---

## 4. Capability → User Journey → UI/UX → API → Backend Mapping

### 4.1 DEM Connect / Disconnect

| Attribute | Value |
|-----------|-------|
| **Goal** | Employee starts and ends a persistent DEM work session |
| **User Journey** | Employee opens DEM landing page → Clicks "Connect" → Session created → Sees active session indicator → Works through missions → Clicks "Disconnect" when done |
| **UI/UX** | Connect button on DEM landing page. Session status indicator in DEM header. Disconnect button with confirmation. Session history list. |
| **Frontend Routes/Pages** | `/digital-export-manager` (landing), `/digital-export-manager/sessions` (history) |
| **Frontend Components** | `DEMConnectButton`, `DEMSessionStatus`, `DEMSessionList`, `DEMSessionDetail` |
| **API Dependencies** | `POST /api/v1/digital-export-manager/connect`, `POST /api/v1/digital-export-manager/sessions/{id}/close`, `GET /api/v1/digital-export-manager/sessions/{id}` |
| **Backend Components** | `SessionManager.create_session()`, `SessionManager.end_session()`, `SessionManager.get_session()` |
| **Backend Changes Required** | None — APIs verified |
| **Classification** | Frontend Integration Required |

### 4.2 Mission Composer

| Attribute | Value |
|-----------|-------|
| **Goal** | Employee submits structured missions to the DEM |
| **User Journey** | Employee opens DEM → Sees mission type cards → Selects type → Sees dynamic payload form → Enters parameters → Submits → Sees mission appear in dashboard |
| **UI/UX** | Mission type selector as cards/buttons showing tool name and description from `/tools` endpoint. Dynamic payload form based on mission type. Context display showing active session. Submit button with loading/error states. |
| **Frontend Routes/Pages** | `/digital-export-manager/missions/new` |
| **Frontend Components** | `MissionTypeSelector`, `MissionPayloadForm`, `MissionSubmitButton`, `MissionContextDisplay` |
| **API Dependencies** | `POST /api/v1/digital-export-manager/missions`, `GET /api/v1/digital-export-manager/tools` |
| **Backend Components** | `MissionPlanner.plan()`, `ExecutionPlanner.plan()`, `ToolOrchestrator.execute()` |
| **Backend Changes Required** | **Yes** — `MissionResponse` must include `reasoning` and `requires_approval` fields; `MissionStatus` must include `pending_approval`; orchestrator must set `pending_approval` instead of `failed` when approval is required |
| **Classification** | Frontend Integration Required + Backend API Enhancement |

### 4.3 Mission Dashboard

| Attribute | Value |
|-----------|-------|
| **Goal** | Employee views all missions and their status |
| **User Journey** | Employee opens DEM → Sees mission list → Clicks mission → Views detail with results, reasoning, and execution log |
| **UI/UX** | Mission list table with status badges. Filter by status. Mission detail with tabs: Results, Reasoning, Execution Log. |
| **Frontend Routes/Pages** | `/digital-export-manager/missions`, `/digital-export-manager/missions/{id}` |
| **Frontend Components** | `MissionList`, `MissionCard`, `MissionDetail`, `MissionStatusBadge`, `MissionResultsView`, `MissionReasoningView` |
| **API Dependencies** | `GET /api/v1/digital-export-manager/sessions/{id}` (includes missions), enhanced `MissionResponse` |
| **Backend Components** | `SessionManager.get_missions()`, enhanced `MissionResponse` schema |
| **Backend Changes Required** | **Yes** — `MissionResponse` must include `reasoning` and `requires_approval`; `MissionStatus` must include `pending_approval` |
| **Classification** | Frontend Integration Required + Backend API Enhancement |

### 4.4 Execution Progress

| Attribute | Value |
|-----------|-------|
| **Goal** | Employee watches DEM execute mission via polling |
| **User Journey** | Employee submits mission → Sees progress indicator → Polling updates status → Watches steps complete → Sees final result or approval pending |
| **UI/UX** | Progress bar. Execution step list with timestamps. Status badge. Auto-refresh every 3 seconds while running. |
| **Frontend Routes/Pages** | Embedded in Mission Detail view |
| **Frontend Components** | `ExecutionProgress`, `ExecutionStep`, `ExecutionLog` |
| **API Dependencies** | `GET /api/v1/digital-export-manager/sessions/{session_id}` — polls for updated mission status |
| **Backend Components** | Existing session/mission storage — minimal changes needed for `pending_approval` status |
| **Backend Changes Required** | **Yes** — `MissionStatus` enum must include `pending_approval`; orchestrator must set this status when approval is required |
| **Classification** | Frontend Integration Required + Backend API Enhancement |

### 4.5 Reasoning Viewer

| Attribute | Value |
|-----------|-------|
| **Goal** | Employee understands why the DEM made each decision |
| **User Journey** | Employee views mission detail → Clicks "Reasoning" tab → Sees decision trace, options considered, chosen path |
| **UI/UX** | Structured display: chosen path, reasoning text, context summary. Expandable sections. No internal architecture exposed. |
| **Frontend Routes/Pages** | Embedded in Mission Detail view |
| **Frontend Components** | `ReasoningViewer`, `ReasoningStep`, `DecisionTrace` |
| **API Dependencies** | Enhanced `MissionResponse` with `reasoning` field |
| **Backend Components** | `ReasoningEngine.reason()` — produces reasoning dict, but `reasoning` field not currently returned in `MissionResponse` — verified in `backend/app/routers/digital_export_manager.py` L151 |
| **Backend Changes Required** | **Yes** — `MissionResponse` must include `reasoning: Optional[str]` from `decision.get("reasoning")` |
| **Classification** | Frontend Integration Required + Backend API Enhancement |

### 4.6 Approval Inbox

| Attribute | Value |
|-----------|-------|
| **Goal** | Manager reviews and acts on pending approvals |
| **User Journey** | Manager opens Approval Inbox → Sees pending approval with mission context → Clicks Approve or Reject → Decision is recorded |
| **UI/UX** | Approval list page. Approval cards showing mission, action, risk level, reasoning. Approve/Reject buttons. Status badge. |
| **Frontend Routes/Pages** | `/digital-export-manager/approvals` |
| **Frontend Components** | `ApprovalInbox`, `ApprovalCard`, `ApprovalActionButtons` |
| **API Dependencies** | `GET /api/v1/digital-export-manager/approvals`, `POST /api/v1/digital-export-manager/approvals/{id}/approve`, `POST /api/v1/digital-export-manager/approvals/{id}/reject` |
| **Backend Components** | `ApprovalGate.check_approval()` exists and is wired into `ToolOrchestrator` — verified. New API endpoints needed. |
| **Backend Changes Required** | **Yes** — `MissionStatus` enum must include `pending_approval`; orchestrator must set this status; 3 new endpoints + persistence via `agent_audit_logs` |
| **Classification** | Frontend Integration Required + Backend New Capability (minimal) |

**MVP limitation:** Approval decision is recorded but does NOT automatically resume execution. Execution remains in `pending_approval` state. Resume/halt logic is Post-MVP.

### 4.7 Knowledge Explorer

| Attribute | Value |
|-----------|-------|
| **Goal** | Employee searches and explores entity relationships |
| **User Journey** | Employee opens Knowledge Explorer → Searches entity → Views detail → Sees related entities in tree/list → Clicks to drill down |
| **UI/UX** | Search bar. Entity detail panel. Relationship tree/list. No graph visualization in MVP. |
| **Frontend Routes/Pages** | `/knowledge-graph` |
| **Frontend Components** | `KnowledgeGraphSearch`, `KnowledgeGraphNodeDetail`, `KnowledgeGraphRelationshipList` |
| **API Dependencies** | `/api/v1/knowledge-graph/search`, `/api/v1/knowledge-graph/nodes/{entity_type}/{entity_id}`, `/api/v1/knowledge-graph/nodes/{entity_type}/{entity_id}/relationships`, `/api/v1/knowledge-graph/traverse/{entity_type}/{entity_id}` |
| **Backend Components** | `KnowledgeGraphService` — fully implemented and tested |
| **Backend Changes Required** | None — verified APIs exist |
| **Classification** | Frontend Integration Required |

### 4.8 Intelligence Dashboard

| Attribute | Value |
|-----------|-------|
| **Goal** | Employee runs supplier analysis and views trends |
| **User Journey** | Employee opens Intelligence Dashboard → Selects "Supplier Analysis" → Enters parameters → Runs → Views results with charts |
| **UI/UX** | Analysis type selector (Supplier Analysis, Trends). Parameter forms. Results with Recharts. |
| **Frontend Routes/Pages** | `/trade-intelligence` |
| **Frontend Components** | `TIDashboard`, `TISupplierAnalysisForm`, `TIResultsChart`, `TITrendChart` |
| **API Dependencies** | `/api/v1/trade-intelligence/suppliers/analyze`, `/api/v1/trade-intelligence/trends/detect` |
| **Backend Components** | `TradeIntelligenceService` — fully implemented and tested |
| **Backend Changes Required** | None — verified APIs exist |
| **Classification** | Frontend Integration Required |

---

## 5. Frontend Architecture

### 5.1 Routing Structure

```
/digital-export-manager
  ├── / (landing: Connect button, session status, quick actions)
  ├── /sessions
  │   ├── / (list of sessions)
  │   └── /{session_id} (session detail with missions)
  ├── /missions
  │   ├── / (list of all missions across sessions)
  │   ├── /new (mission composer)
  │   └── /{mission_id} (mission detail with reasoning, results, execution log)
  ├── /approvals (approval inbox)
  └── /tools (tools registry viewer)

/knowledge-graph
  ├── / (search, entity detail, relationships)
  └── /nodes/{entity_type}/{entity_id} (entity detail)

/trade-intelligence
  ├── / (dashboard with analysis types)
  ├── /suppliers/analyze
  └── /trends/detect
```

### 5.2 Navigation Integration

**Sidebar additions** (in `Sidebar.tsx`):
- Digital Export Manager (primary, top of list)
- Knowledge Graph
- Trade Intelligence

**Navigation principle:** DEM is presented as the **primary intelligent layer**, not as a subsection of ERP features.

### 5.3 State Management

**New Zustand stores:**
- `useDEMStore` — session state, active session ID, mission list, current mission detail, execution progress
- `useApprovalStore` — pending approvals, approval actions, loading states
- `useKnowledgeGraphStore` — search results, selected entity, relationships
- `useTradeIntelligenceStore` — analysis results, trends data, loading states

**Existing stores preserved:**
- `useAuthStore` — unchanged
- `useToast` hook — reused for notifications

### 5.4 API Client Integration

**New functions in `services/api.ts`:**
```typescript
// DEM
export const connectToDEM = (data: SessionCreateRequest) => api.post('/api/v1/digital-export-manager/connect', data);
export const disconnectDEM = (sessionId: string) => api.post(`/api/v1/digital-export-manager/sessions/${sessionId}/close`);
export const getDEMSession = (sessionId: string) => api.get(`/api/v1/digital-export-manager/sessions/${sessionId}`);
export const createMission = (sessionId: string, data: MissionRequest) => api.post(`/api/v1/digital-export-manager/missions?session_id=${sessionId}`, data);
export const getDEMTools = () => api.get('/api/v1/digital-export-manager/tools');
export const getApprovals = () => api.get('/api/v1/digital-export-manager/approvals');
export const approveMission = (approvalId: string) => api.post(`/api/v1/digital-export-manager/approvals/${approvalId}/approve`);
export const rejectMission = (approvalId: string) => api.post(`/api/v1/digital-export-manager/approvals/${approvalId}/reject`);

// Knowledge Graph
export const getGraphNode = (entityType: string, entityId: number) => api.get(`/api/v1/knowledge-graph/nodes/${entityType}/${entityId}`);
export const searchGraph = (query: string, entityType?: string) => api.get('/api/v1/knowledge-graph/search', { params: { query, entity_type: entityType } });
export const traverseGraph = (entityType: string, entityId: number, depth?: number) => api.get(`/api/v1/knowledge-graph/traverse/${entityType}/${entityId}`, { params: { depth } });
export const getGraphRelationships = (entityType: string, entityId: number) => api.get(`/api/v1/knowledge-graph/nodes/${entityType}/${entityId}/relationships`);

// Trade Intelligence
export const analyzeSupplier = (data: AnalyzeRequest) => api.post('/api/v1/trade-intelligence/suppliers/analyze', data);
export const detectTrends = (data: TrendRequest) => api.post('/api/v1/trade-intelligence/trends/detect', data);
```

### 5.5 Component Architecture Principles

**Avatar Contract compliance:**
- DEM produces structured intents and responses (Pydantic models)
- Frontend renders them as UI components, never exposes internal architecture
- No "Agent" or "AI Assistant" branding — always "Digital Export Manager"
- Reasoning is presented as "Decision Trace" or "Analysis" not as "AI thinking"

**Business Façade principle:**
- Frontend interacts with DEM via `/api/v1/digital-export-manager` only
- Never calls internal agent packages directly
- Never exposes `agent/`, `reasoning_engine/`, `execution_engine/` paths in UI

---

## 6. Backend Changes Required

### 6.1 Verified Changes — Minimal Scope

| # | Change | Component | Evidence | Classification |
|---|--------|-----------|----------|----------------|
| 1 | **MissionStatus enum expansion** | `backend/app/agent/schemas/enums.py` | Current enum has `pending`, `running`, `completed`, `failed` only. Need `pending_approval` for approval flow. | API Enhancement |
| 2 | **MissionResponse expansion** | `backend/app/agent/schemas/api_response.py` | Current model missing `reasoning`, `requires_approval`, `approval_status`. `decision.get("reasoning")` exists in router L151 but not returned. | API Enhancement |
| 3 | **Orchestrator approval handling** | `backend/app/agent/execution_engine/orchestrator.py` | Current code sets `mission_status = MissionStatus.FAILED.value` when approval is required (L197). Must change to `MissionStatus.PENDING_APPROVAL.value`. | API Enhancement |
| 4 | **Router status preservation** | `backend/app/routers/digital_export_manager.py` | Current router maps any non-completed status to "failed" (L182). Must preserve `pending_approval` status. | API Enhancement |
| 5 | **Approval API endpoints** | New routes in `backend/app/routers/digital_export_manager.py` | `ApprovalGate.check_approval()` verified in `backend/app/agent/approval/gate.py`. Wired into `ToolOrchestrator` L178-208. No API exposure exists. | New Capability (minimal) |
| 6 | **Approval persistence** | Reuse `agent_audit_logs` table | Table exists per `backend/app/core/database.py` and `AuditRecorder`. No approval-specific table needed for MVP. | API Enhancement |

### 6.2 What Is NOT Changing

| Component | Reason |
|-----------|--------|
| DEM core architecture (`agent/` internal packages) | Already implemented and tested; protected by baseline policy |
| Knowledge Graph service layer | Already implemented and tested; APIs verified |
| Trade Intelligence service layer | Already implemented and tested; APIs verified |
| Existing ERP routers and services | Out of scope; must remain untouched |
| Database schema | Existing tables sufficient; no new tables required |
| WebSocket/SSE infrastructure | Deferred to Post-MVP; polling sufficient |
| Avatar contract | Interface only; UI explicitly out of scope |
| Mission execution resume after approval | Post-MVP; MVP records decision only |

### 6.3 Verified Claims

| Claim | Status | Evidence |
|-------|--------|----------|
| DEM core implemented | Verified | `backend/app/agent/` — 14+ modules, all tests passing |
| ReasoningEngine produces reasoning | Verified | `decision.get("reasoning")` in `digital_export_manager.py` L151 |
| ApprovalGate exists and is wired | Verified | `backend/app/agent/approval/gate.py` + `orchestrator.py` L178-208 |
| Approval currently fails mission | Verified | `orchestrator.py` L197: `mission_status = MissionStatus.FAILED.value` when approval required |
| Knowledge Graph APIs exist | Verified | `backend/app/routers/knowledge_graph.py` — 9 endpoints |
| Trade Intelligence APIs exist | Verified | `backend/app/routers/trade_intelligence.py` — 6 endpoints |
| SessionDetailResponse includes missions | Verified | `backend/app/agent/schemas/session.py` L61 |
| Tools endpoint exists | Verified | `backend/app/routers/digital_export_manager.py` L262-268 |
| 8 mission types defined | Verified | `backend/app/agent/schemas/enums.py` |
| 14 ERP tools registered | Verified | `backend/app/agent/tools/erp_tools.py` |
| No WebSocket/SSE exists | Verified | `backend/main.py` — no WebSocket/SSE imports or routes |
| `/missions` is synchronous | Verified | `digital_export_manager.py` L111-210 — awaits full execution |
| `MissionResponse` missing reasoning fields | Verified | `backend/app/agent/schemas/api_response.py` — 7 fields only |
| `MissionStatus` missing `pending_approval` | Verified | `backend/app/agent/schemas/enums.py` — 4 values only |
| Approval persistence missing | Verified | No approval API endpoints exist; `ApprovalGate` is internal only |

---

## 7. MVP — Must Have

The MVP delivers the minimum end-to-end AI/DEM user experience:

**DEM Connect → Mission Composer → Mission Dashboard → Execution Progress → Results → Decision Trace → Approval Inbox**

### 7.1 MVP Surfaces

| Surface | Purpose | Backend Change? |
|---------|---------|-----------------|
| DEM Landing + Connect/Disconnect | Session management | None |
| Mission Composer (8 types) | Submit missions to DEM | MissionResponse expansion + MissionStatus + orchestrator |
| Mission Dashboard | View missions, status, results | MissionResponse expansion + MissionStatus |
| Execution Progress (polling) | See mission status updates | MissionStatus enum |
| Reasoning Viewer | See decision trace | MissionResponse expansion |
| Approval Inbox | Review approval-required missions | 3 new endpoints + persistence + MissionStatus + orchestrator |
| Knowledge Explorer (search + tree) | Search entities, view relationships | None |
| Intelligence Dashboard (supplier + trends) | Run and view analysis | None |

### 7.2 MVP Exclusions (Post-MVP)

| Capability | Reason for Deferral |
|------------|---------------------|
| Full Knowledge Graph visualization | Heavy dependency; tree/list sufficient for MVP |
| Buyer analysis / Entity comparison | Lower business priority than supplier analysis and trends |
| PDF report generation | CSV/on-screen results sufficient for MVP |
| WebSocket/SSE real-time | Polling sufficient for MVP; simpler implementation |
| Inline approval UX | Separate inbox cleaner for MVP; inline adds complexity |
| Mission execution resume after approval | MVP approval records decision only; resume in Post-MVP |
| Approval halt/revert logic | MVP records decision; execution state management in Post-MVP |

---

## 8. Post-MVP / Next Iteration

| Capability | Trigger for Inclusion |
|------------|----------------------|
| Full Knowledge Graph visualization (D3/Cytoscape) | Business requirement for visual graph exploration |
| Buyer analysis / Entity comparison | Business demand for comparative intelligence |
| PDF report generation | Need for offline/shared reports |
| WebSocket/SSE real-time progress | User feedback that polling is insufficient |
| Inline approval UX | User feedback that separate inbox is disruptive |
| Mission execution resume after approval | Workflow requirement for long-running missions |
| Mission Runner/Scheduler | Queued missions, background workers |
| Knowledge Ingestion Pipeline | External system integration requirements |

---

## 9. Tasks / Phases / Dependencies

### Phase 1: Backend API Enhancements (Minimal)

**Task 1.1: Enhance MissionResponse and MissionStatus**
- Add `pending_approval` to `MissionStatus` enum in `backend/app/agent/schemas/enums.py`
- Add `reasoning: Optional[str]` to `MissionResponse` — from `decision.get("reasoning")` in `digital_export_manager.py` L151
- Add `requires_approval: bool` to `MissionResponse` — from `decision.get("requires_approval")` L144
- Add `approval_status: str` to `MissionResponse` — from `decision.get("approval_status")` L145
- **Dependency:** None
- **Deliverable:** Updated schemas in `backend/app/agent/schemas/enums.py` and `backend/app/agent/schemas/api_response.py`

**Task 1.2: Update orchestrator and router for approval status**
- Modify `ToolOrchestrator.execute()` to set `mission_status = MissionStatus.PENDING_APPROVAL.value` instead of `MissionStatus.FAILED.value` when approval is required — verified current behavior at `orchestrator.py` L197
- Modify `create_mission` endpoint in `digital_export_manager.py` to preserve `pending_approval` status in `MissionResponse` instead of mapping to "failed"
- **Dependency:** Task 1.1
- **Deliverable:** Updated orchestrator and router handling approval status

**Task 1.3: Create Approval API endpoints and persistence**
- Add `GET /api/v1/digital-export-manager/approvals` — list pending approvals for current user
- Add `POST /api/v1/digital-export-manager/approvals/{id}/approve` — approve
- Add `POST /api/v1/digital-export-manager/approvals/{id}/reject` — reject
- Persist approval records in `agent_audit_logs` table with approval-specific metadata
- **Dependency:** Task 1.2
- **Deliverable:** 3 new endpoints with tests

### Phase 2: Frontend DEM Core

**Task 2.1: DEM Navigation & Routing**
- Add DEM entries to `Sidebar.tsx`
- Add routes in `App.tsx`: `/digital-export-manager`, `/digital-export-manager/sessions`, `/digital-export-manager/missions`, `/digital-export-manager/approvals`, `/digital-export-manager/tools`
- Add protected route wrapper for DEM pages
- **Dependency:** None — parallel with Phase 1
- **Deliverable:** DEM navigation and routing

**Task 2.2: DEM Landing Page & Session Management**
- Implement `DEMConnectButton`, `DEMSessionStatus`, `DEMSessionList`, `DEMSessionDetail`
- Add API functions to `services/api.ts`
- Add `useDEMStore` Zustand store
- **Dependency:** Task 2.1
- **Deliverable:** Connect/Disconnect UI, session management

**Task 2.3: Mission Composer**
- Implement `MissionTypeSelector` — cards for all 8 mission types from `/tools` endpoint
- Implement `MissionPayloadForm` — dynamic form based on selected mission type
- Implement `MissionSubmitButton` with loading/error states
- Add API functions to `services/api.ts`
- **Dependency:** Task 2.1, Task 1.1
- **Deliverable:** Mission creation form and submission flow

**Task 2.4: Mission Dashboard**
- Implement `MissionList` with status filters
- Implement `MissionDetail` with tabs: Results, Reasoning, Execution Log
- Implement `MissionStatusBadge`
- Add API functions to `services/api.ts`
- **Dependency:** Task 2.1, Task 1.1, Task 1.2
- **Deliverable:** Mission list and detail views

**Task 2.5: Execution Progress & Reasoning Viewer**
- Implement `ExecutionProgress` — polls `GET /sessions/{id}` every 3s when running
- Implement `ExecutionStep` component
- Implement `ReasoningViewer` — displays `reasoning` field from enhanced `MissionResponse`
- **Dependency:** Task 2.4
- **Deliverable:** Progress display and reasoning visualization

**Task 2.6: Approval Inbox**
- Implement `ApprovalInbox` — list of pending approvals
- Implement `ApprovalCard` — shows mission, action, reasoning, approve/reject buttons
- Add API functions to `services/api.ts`
- **Dependency:** Task 2.1, Task 1.3
- **Deliverable:** Approval inbox page

### Phase 3: Knowledge & Intelligence (Parallel with Phase 2)

**Task 3.1: Knowledge Explorer**
- Implement `KnowledgeGraphSearch` — calls `/search` endpoint
- Implement `KnowledgeGraphNodeDetail` — calls `/nodes/{entity_type}/{entity_id}`
- Implement `KnowledgeGraphRelationshipList` — calls `/relationships` and `/traverse`
- Add API functions to `services/api.ts`
- **Dependency:** None — parallel with Phase 2
- **Deliverable:** Knowledge Graph page with search and tree/list exploration

**Task 3.2: Intelligence Dashboard**
- Implement `TIDashboard` — analysis type selector
- Implement `TISupplierAnalysisForm` — calls `/suppliers/analyze`
- Implement `TITrendDetectionForm` — calls `/trends/detect`
- Implement `TIResultsChart` — displays results with Recharts
- Add API functions to `services/api.ts`
- **Dependency:** None — parallel with Phase 2
- **Deliverable:** Trade Intelligence page with supplier analysis and trends

### Phase 4: Integration, Polish & Validation

**Task 4.1: DEM Landing Page Unification**
- Create cohesive DEM landing page presenting Connect, recent missions, and quick actions
- Ensure DEM is presented as "Executive Intelligence" not chatbot
- **Dependency:** Tasks 2.2, 2.3, 2.4
- **Deliverable:** DEM landing page

**Task 4.2: Error Handling & Edge Cases**
- Loading states for all DEM operations
- Error states with user-friendly messages
- Empty states (no sessions, no missions, no approvals)
- Network error handling
- **Dependency:** All Phase 2 tasks
- **Deliverable:** Robust error/loading/empty states

**Task 4.3: Permission Enforcement**
- Ensure approval actions require owner/manager role
- Ensure Knowledge Graph node creation requires owner/manager role
- Ensure DEM access respects existing RBAC
- **Dependency:** All Phase 2 tasks
- **Deliverable:** Permission-enforced UI

**Task 4.4: Responsive Design & i18n**
- Ensure all DEM pages are responsive
- Add Arabic/English translations for DEM UI strings
- **Dependency:** All Phase 2 tasks
- **Deliverable:** Responsive, localized DEM UI

**Task 4.5: Integration Testing**
- E2E tests for DEM flows: Connect → Create Mission → View Progress → View Results → Disconnect
- E2E tests for Approval flow: Mission requires approval → Manager sees in inbox → Approves/Rejects → Mission status updates
- E2E tests for Knowledge Graph: Search → View node → View relationships
- E2E tests for Trade Intelligence: Run analysis → View results
- **Dependency:** All Phase 2 and 3 tasks
- **Deliverable:** E2E test suite

---

## 10. Deliverables

| Deliverable | Description |
|-------------|-------------|
| **Enhanced MissionResponse schema** | Backend Pydantic model with `reasoning`, `requires_approval`, `approval_status` |
| **MissionStatus enum expansion** | Add `pending_approval` value |
| **Orchestrator approval handling** | Set `pending_approval` status instead of `failed` when approval required |
| **Router status preservation** | Preserve `pending_approval` status in API response |
| **Approval API endpoints** | 3 new backend endpoints for approval workflow |
| **Approval persistence** | Reuse of `agent_audit_logs` for approval records |
| **DEM Navigation** | Sidebar entries and routing for DEM, Knowledge Graph, Trade Intelligence |
| **DEM Landing Page** | Connect/Disconnect UI, session status, quick actions |
| **Session Management UI** | Session list, detail view, history |
| **Mission Composer** | Mission type selection (8 types), payload form, submission |
| **Mission Dashboard** | Mission list, filters, detail view with tabs |
| **Execution Progress UI** | Polling-based progress indicator, execution log |
| **Reasoning Viewer** | Decision trace display, reasoning explanation |
| **Approval Inbox** | Pending approvals list, approve/reject actions |
| **Knowledge Explorer** | Search, entity detail, relationship tree/list |
| **Intelligence Dashboard** | Supplier analysis, trend detection, charts |
| **API Client Functions** | New functions in `services/api.ts` for DEM/KG/TI |
| **State Management** | New Zustand stores for DEM, approvals, knowledge graph, trade intelligence |
| **E2E Tests** | Integration tests proving User → Frontend → DEM → ERP path works |
| **UAT Items** | New UAT checklist items for AI/DEM functionality |
| **Documentation Updates** | `README.md`, `CURRENT_STATUS.md` updates |

---

## 11. Acceptance Criteria

### AC-1: DEM Connect/Disconnect
- Employee can connect to DEM from Frontend
- Active session status is visible
- Employee can disconnect from DEM
- Session history is accessible

### AC-2: Mission Composer
- Employee can select from all 8 mission types
- Employee can enter mission payload
- Employee can submit mission
- Submission errors are displayed clearly

### AC-3: Mission Dashboard
- Employee can view list of all missions
- Employee can view mission detail with results
- Mission status is clearly displayed (pending, running, completed, failed, pending_approval)

### AC-4: Execution Progress
- Employee can see execution progress via polling
- Execution steps are displayed as they complete
- Final result is displayed when execution completes
- `pending_approval` status is displayed with link to Approval Inbox

### AC-5: Reasoning Viewer
- Employee can view reasoning trace for each mission
- Reasoning is presented in structured, readable format
- Decision context is displayed

### AC-6: Approval Inbox
- Manager can view pending approvals
- Manager can approve or reject
- Approval decision is recorded in audit log
- Mission remains in `pending_approval` state after decision (resume in Post-MVP)

### AC-7: Knowledge Explorer
- Employee can search for entities
- Employee can view entity relationships in tree/list format
- Employee can view entity details

### AC-8: Intelligence Dashboard
- Employee can run supplier analysis
- Employee can detect trends
- Results are displayed with charts

### AC-9: Navigation & Routing
- DEM is accessible from sidebar navigation
- All DEM pages are protected routes
- Navigation reflects DEM as primary intelligent layer

### AC-10: End-to-End User Journey
- User can complete full journey: Login → Connect to DEM → Create Mission → Watch Execution → View Results → View Reasoning → Disconnect
- All steps are visible and usable from Frontend
- No backend architecture is exposed to user

---

## 12. Integration / E2E / UAT Strategy

### 12.1 Integration Tests
- Backend: Test enhanced `MissionResponse` fields, `pending_approval` status, approval API endpoints
- Frontend: Test API client functions, state management, component rendering

### 12.2 E2E Tests
- DEM Connect/Disconnect flow
- Mission creation and execution flow
- Approval workflow: mission requires approval → manager sees in inbox → approves/rejects → mission status updates
- Knowledge Graph search and exploration
- Trade Intelligence analysis

### 12.3 UAT Items
New UAT checklist items added to `docs/appendices/UAT_CHECKLIST.md`:
- DEM Connect/Disconnect
- Mission Composer
- Mission Dashboard
- Execution Progress
- Reasoning Viewer
- Approval Inbox
- Knowledge Explorer
- Intelligence Dashboard

### 12.4 Evidence Requirements
- Screenshots of each DEM surface
- Network logs showing API calls to DEM/KG/TI endpoints
- Execution logs showing mission lifecycle including `pending_approval` status
- Approval workflow logs

---

## 13. Risks / Blockers

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Approval persistence design conflicts with existing architecture | Low | Medium | Reuse existing `agent_audit_logs` table; minimal schema change |
| MissionResponse changes break existing tests | Medium | Low | Update tests in same WP; maintain backward compatibility |
| Frontend state complexity for mission lifecycle | Medium | Medium | Use Zustand with clear state machines for mission status |
| RBAC enforcement gaps in new endpoints | Low | High | Security review of all new endpoints before deployment |
| Polling frequency causes performance issues | Low | Low | 3s interval is conservative; can be adjusted |

---

## 14. Definition of Done

- [ ] Backend: `MissionStatus` enum includes `pending_approval`
- [ ] Backend: `MissionResponse` enhanced with `reasoning`, `requires_approval`, `approval_status`
- [ ] Backend: Orchestrator sets `pending_approval` instead of `failed` when approval required
- [ ] Backend: Router preserves `pending_approval` status in response
- [ ] Backend: 3 approval API endpoints implemented and tested
- [ ] Backend: Approval persistence via `agent_audit_logs` verified
- [ ] Frontend: DEM navigation and routing complete
- [ ] Frontend: DEM landing page with Connect/Disconnect implemented
- [ ] Frontend: Mission Composer with all 8 mission types implemented
- [ ] Frontend: Mission Dashboard with list and detail views implemented
- [ ] Frontend: Execution Progress via polling implemented
- [ ] Frontend: Reasoning Viewer implemented
- [ ] Frontend: Approval Inbox implemented
- [ ] Frontend: Knowledge Explorer implemented
- [ ] Frontend: Intelligence Dashboard (supplier analysis + trends) implemented
- [ ] Frontend: API client functions for DEM/KG/TI implemented
- [ ] Frontend: State management (Zustand stores) implemented
- [ ] Frontend: Error/loading/empty states handled
- [ ] Frontend: RBAC enforced in UI
- [ ] Frontend: Responsive design verified
- [ ] Frontend: Arabic/English localization complete
- [ ] E2E tests passing
- [ ] UAT checklist updated with AI/DEM items
- [ ] Documentation updated (`README.md`, `CURRENT_STATUS.md`)
- [ ] Git working tree clean

---

## 15. Relationship with WP-42

**WP-42 closes first. This WP begins after WP-42 closure.**

WP-42 is the acceptance gate for the current product (traditional ERP UI). This WP delivers new product capability (AI/DEM Frontend UX) that requires its own acceptance gate.

**Execution sequence:**
1. WP-42 closes on current scope (traditional ERP UI).
2. This WP implements AI/DEM Frontend UX.
3. A new acceptance gate validates the AI/DEM surfaces.

**If WP-42 is re-activated before this WP is complete:**
- WP-42 UAT covers current product scope only
- AI/DEM surfaces are excluded from WP-42 UAT
- This WP delivers new product capability requiring its own acceptance gate

---

## 16. Relationship with Existing Closed WPs

| Closed WP | Relationship to This WP |
|-----------|-------------------------|
| WP-30 / WP-30B–WP-30I | Backend DEM architecture implemented and closed. This WP integrates those capabilities into Frontend. No modification to WP-30 deliverables. |
| WP-31 (AI Memory) | Memory interface and SQLite provider implemented. Internal only; not user-facing. |
| WP-32 (Knowledge Graph) | Knowledge Graph service and API fully implemented. This WP adds Frontend search and tree/list exploration. |
| WP-33 (Trade Intelligence) | Trade Intelligence service and API fully implemented. This WP adds Frontend dashboard for supplier analysis and trends. |
| WP-40 (Docker) | Deployment infrastructure unchanged. New Frontend components deploy within existing Docker setup. |
| WP-41 (Documentation) | Documentation updates required after this WP completes. |
| WP-42 (Owner Acceptance) | Separate acceptance gate for current product. This WP delivers new product capability. |

**Baseline protection:** All closed WPs remain closed. This WP produces new baselines for new deliverables.

---

## 17. Implementation Boundary

### This Session
Plan refinement and approval preparation only. No implementation work.

### Next Session
Implementation of the approved Work Package only, starting with:
1. Backend Task 1.1: MissionResponse and MissionStatus schema enhancements
2. Backend Task 1.2: Orchestrator and router approval handling
3. Backend Task 1.3: Approval API endpoints
4. Frontend Task 2.1: DEM Navigation & Routing (in parallel)

Execution starts only after:
1. All decisions are confirmed closed
2. MVP scope is approved
3. Work Package name and number are assigned
4. Acceptance Criteria are approved
5. A new implementation session is initiated with clean context

---

## 18. Verified Technical Claims

| Claim | Status | Evidence |
|-------|--------|----------|
| DEM core implemented | Verified | `backend/app/agent/` — 14+ modules, all tests passing |
| ReasoningEngine produces reasoning | Verified | `decision.get("reasoning")` in `digital_export_manager.py` L151 |
| ApprovalGate exists and is wired | Verified | `backend/app/agent/approval/gate.py` + `orchestrator.py` L178-208 |
| Approval currently fails mission | Verified | `orchestrator.py` L197: `mission_status = MissionStatus.FAILED.value` when approval required |
| Knowledge Graph APIs exist | Verified | `backend/app/routers/knowledge_graph.py` — 9 endpoints |
| Trade Intelligence APIs exist | Verified | `backend/app/routers/trade_intelligence.py` — 6 endpoints |
| SessionDetailResponse includes missions | Verified | `backend/app/agent/schemas/session.py` L61 |
| Tools endpoint exists | Verified | `backend/app/routers/digital_export_manager.py` L262-268 |
| 8 mission types defined | Verified | `backend/app/agent/schemas/enums.py` |
| 14 ERP tools registered | Verified | `backend/app/agent/tools/erp_tools.py` |
| No WebSocket/SSE exists | Verified | `backend/main.py` — no WebSocket/SSE imports or routes |
| `/missions` is synchronous | Verified | `digital_export_manager.py` L111-210 — awaits full execution |
| `MissionResponse` missing reasoning fields | Verified | `backend/app/agent/schemas/api_response.py` — 7 fields only |
| `MissionStatus` missing `pending_approval` | Verified | `backend/app/agent/schemas/enums.py` — 4 values only |
| Approval persistence missing | Verified | No approval API endpoints exist; `ApprovalGate` is internal only |

---

## 19. Closed Decisions Summary

| # | Decision | Choice | Evidence |
|---|----------|--------|----------|
| 1 | Priority vs WP-42 | WP-42 closes first; this WP begins after | WP-42 is active deferred acceptance gate; this WP is new implementation |
| 2 | Real-time progress | Polling (3s interval) | No WebSocket/SSE exists; session API returns mission status; zero backend changes |
| 3 | Approval UX | Separate Approval Inbox | ApprovalGate wired into orchestrator; manager function; aligns with `/notifications` pattern |
| 4 | Knowledge Graph MVP | Tree/List exploration | Search/traverse APIs exist; graph visualization deferred to Post-MVP |
| 5 | Trade Intelligence MVP | Supplier analysis + Trends | APIs verified; highest business value for export platform |
| 6 | Mission types | All 8 existing types | All defined in `MissionType` enum; all map to registered tools |

---

## 20. Owner Recommendation

Based on repository evidence, the plan recommends:

1. **Approve MVP scope:** The 8 surfaces in Section 7.1 are the minimum viable AI/DEM experience supported by existing backend capabilities.
2. **Approve backend changes:** The 5 minimal backend changes (MissionStatus enum, MissionResponse expansion, orchestrator modification, router modification, 3 approval endpoints) are necessary and sufficient for MVP.
3. **Execution sequence:** WP-42 closes first on current scope. This WP begins after as the next implementation WP.

---

## 21. Owner Decision Required

Only one decision requires Owner input:

**Assign Work Package name and number.**

Formal name and number for this Work Package to be assigned by Project Owner upon approval.

---

## 22. Final Status

**Implementation-Ready — Pending Owner Approval**

All technical decisions are closed based on repository evidence. MVP scope is defined and minimized. Backend changes are verified and minimal. Dependencies are clear. Acceptance Criteria are testable. Definition of Done is complete.

No implementation work has begun. No source code has been modified. No commits have been made.
