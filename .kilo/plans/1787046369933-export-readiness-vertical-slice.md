# Export Readiness Vertical Slice — Implementation Plan

**Date:** 2026-08-20  
**Authority:** `.kilo/plans/1786559160142-external-knowledge-portfolio-re-evaluation.md` Section 32  
**Plan Path:** `.kilo/plans/1787046369933-export-readiness-vertical-slice.md`  
**Status:** Implemented — Verified — Closed  
**Governing Decision:** DEM Product Priority = Export Readiness Vertical Slice

---

## 1. Current State Assessment

### 1.1 Verified Existing Capabilities

| Capability | Location | Status | Verified |
|------------|----------|--------|----------|
| Knowledge Orchestrator | `backend/app/agent/knowledge/orchestrator.py` | ✅ Implemented & Verified (77/77 tests) | Yes |
| Reasoning Engine | `backend/app/agent/decision_engine/engine.py` | ✅ Implemented | Yes |
| LLM (Gemini) | `backend/app/agent/llm/provider.py` | ✅ Implemented | Yes |
| Moaah External Source Adapter | `backend/app/agent/knowledge/mooadapter.py` | ✅ Implemented | Yes |
| ZATCA External Source Adapter | `backend/app/agent/knowledge/zatcaprovider.py` | ✅ Implemented | Yes |
| GCC-Stat External Source Adapter | `backend/app/agent/knowledge/gccstatprovider.py` | ✅ Implemented | Yes |
| UN Comtrade External Source Adapter | `backend/app/agent/knowledge/uncomtradeprovider.py` | ✅ Implemented | Yes |
| World Bank LPI External Source Adapter | `backend/app/agent/knowledge/worldbanklprovider.py` | ✅ Implemented | Yes |
| FAOSTAT External Source Adapter | `backend/app/agent/knowledge/faostatprovider.py` | ✅ Implemented | Yes |
| TradeData External Source Adapter | `backend/app/agent/knowledge/tradedataprovider.py` | ✅ Implemented | Yes |
| Knowledge Graph | `backend/app/agent/knowledge/graph_provider.py` | ✅ Implemented | Yes |
| DEM Mission Infrastructure | `backend/app/routers/digital_export_manager.py` | ✅ Implemented | Yes |
| Frontend Layout/Routing/Auth | `frontend/src/` | ✅ Implemented | Yes |
| DEM Landing Page | `frontend/src/pages/DEMLanding.tsx` | ✅ Implemented | Yes |
| DEM Mission Composer | `frontend/src/pages/DEMMissionComposer.tsx` | ✅ Implemented | Yes |
| DEM Mission Detail | `frontend/src/pages/DEMMissionDetail.tsx` | ✅ Implemented | Yes |

### 1.2 Confirmed Missing Capabilities

| Gap | Location | Status |
|-----|----------|--------|
| `/export-readiness` frontend page | `frontend/src/pages/` | ❌ Missing |
| Export Readiness API endpoint | `backend/app/routers/` | ❌ Missing |
| Report assembly service | `backend/app/services/` | ❌ Missing |
| EXPORT_READINESS mission type | `backend/app/agent/schemas/enums.py` | ❌ Missing (mission types are ERP-only) |

### 1.3 Critical Architectural Finding

**The existing DEM Mission infrastructure is designed for ERP tool execution, not knowledge queries.**

Current flow:
```
create_mission → reasoning_engine.reason() → task_planner.plan() → execution_planner.plan() → tool_orchestrator.execute()
```

This executes tools sequentially (shipping, customs, documents). It is NOT designed for:
- Querying multiple knowledge providers
- Assembling results into a report
- Generating LLM-based recommendations

**Conclusion:** Export Readiness requires a **dedicated API flow**, not a new Mission Type in the existing ERP mission infrastructure.

---

## 2. Architecture / API Flow

### 2.1 New Endpoint

**POST `/api/v1/export-readiness/analyze`**

**Request:**
```json
{
  "product_id": 123,          // optional: existing product ID
  "hs_code": "080510",        // optional: HS code if no product_id
  "product_name": "Oranges",  // optional: for report display
  "target_market": "DE",      // required: ISO country code
  "user_id": 1                // from auth context
}
```

**Response:**
```json
{
  "report_id": "uuid",
  "product": { "product_id": 123, "hs_code": "080510", "name": "Oranges" },
  "target_market": "DE",
  "sections": [
    {
      "title": "Regulatory Requirements",
      "source": "Moaah/ZATCA/GCC-Stat",
      "confidence": 0.85,
      "data": { ... },
      "availability": "available" | "partial" | "not_available"
    },
    {
      "title": "Market Access",
      "source": "Moaah/ZATCA",
      "confidence": 0.80,
      "data": { ... },
      "availability": "available" | "partial" | "not_available"
    },
    {
      "title": "Logistics Profile",
      "source": "World Bank LPI",
      "confidence": 0.75,
      "data": { ... },
      "availability": "available" | "partial" | "not_available"
    },
    {
      "title": "Historical Trade Context",
      "source": "UN Comtrade / TradeData",
      "confidence": 0.70,
      "data": { ... },
      "availability": "available" | "partial" | "not_available"
    }
  ],
  "action_checklist": [ ... ],
  "recommendation": "LLM-generated text or null if LLM unavailable",
  "data_quality_note": "Some sections are partial because...",
  "generated_at": "2026-08-20T14:00:00Z"
}
```

### 2.2 Backend Flow

```
POST /api/v1/export-readiness/analyze
  |
  v
ExportReadinessService.analyze(product_id, hs_code, product_name, target_market, user_id)
  |
  +---> 1. Query KnowledgeOrchestrator with explicit sources to bypass classification order
  |         - Regulatory: orchestrate(..., sources=["moaah", "zatca"], context={"country": "<ISO2>"})
  |           fallback: sources=["moaah", "zatca", "gccstat"]
  |         - Market Access: orchestrate(..., sources=["moaah", "zatca", "tradedata"], context={"country": "<ISO2>"})
  |           fallback: sources=["moaah", "zatca", "gccstat"]
  |         - Historical Trade Context: orchestrate(..., sources=["un-comtrade", "tradedata"], context={"country": "<ISO2>", "product": "<name>"})
  |           fallback: sources=["un-comtrade", "tradedata", "faostat"]
  |
  +---> 2. Logistics Profile: direct registry.query("worldbank-lpi", context={"country": "<ISO2>"})
  |
  +---> 3. Collect provider results with confidence, source, effective_date
  |
  +---> 4. Filter/rank results per section
  |
  +---> 5. Determine availability per section:
  |         - available: confidence >= 0.6 and data present
  |         - partial: some data present but gaps
  |         - not_available: no data from any provider for this section
  |
  +---> 6. Assemble Action Checklist (deterministic rules)
  |
  +---> 7. Call LLM (if available) to generate recommendation
  |         - Prompt includes: product, market, available data summary, gaps
  |         - If LLM unavailable or raises RuntimeError: recommendation = null
  |
  +---> 8. Return structured report
```

### 2.3 Why Not Reuse Existing Mission Infrastructure?

| Aspect | Existing Mission Infrastructure | Export Readiness Needs |
|--------|--------------------------------|------------------------|
| Purpose | Execute ERP tools sequentially | Query knowledge + generate report |
| Input | Mission type + payload | Product + market |
| Output | Tool execution results | Structured decision report |
| Tool execution | Yes (shipping, customs, etc.) | No — read-only knowledge queries |
| LLM integration | No | Yes — for recommendation synthesis |
| Report assembly | No | Yes — multi-source aggregation |

**Decision:** New dedicated endpoint is cleaner and avoids misusing ERP mission infrastructure for knowledge queries.

---

## 3. Frontend Flow

### 3.1 New Page: `/export-readiness`

**Route:** Added to `App.tsx` under `PrivateRoute` + `Layout`

**Components:**
- Reuse existing: `Layout`, `Sidebar`, `Button`, `Card`, `Input`, `Label`, `Select`, `Skeleton`, `useToast`, `api`
- New: `ExportReadiness.tsx` page component

**User Flow:**
```
1. User navigates to /export-readiness (from Sidebar or DEM Landing)
2. Page shows:
   - Product dropdown (from existing products) OR manual HS Code input
   - Target Market dropdown (countries)
   - "Analyze Readiness" button
3. User clicks "Analyze Readiness"
4. Page calls POST /api/v1/export-readiness/analyze
5. Loading state shown
6. Results displayed as structured report:
   - Section cards (Regulatory, Market Access, Logistics, Trade History)
   - Each card shows: title, source, confidence badge, data/not_available status
   - Action Checklist section
   - Recommendation section (if LLM available)
   - Data Quality Note
```

### 3.2 Routing Changes

**File:** `frontend/src/App.tsx`
- Add route: `<Route path="export-readiness" element={<ExportReadiness />} />`

**File:** `frontend/src/components/layout/Sidebar.tsx`
- Add nav item for `/export-readiness` with appropriate roles

---

## 4. Knowledge Flow

### 4.1 Provider Routing

**Important:** The Export Readiness workflow does **not** rely on `KnowledgeOrchestrator._classify_query()` for provider selection.

**Why:** The classification rules are evaluated in a fixed order (`agrifood` -> `customs` -> `market_access` -> `regulatory` -> ...). A query containing "requirements" would match `market_access` before reaching `regulatory`, causing the wrong providers to be selected.

**Solution:** Use the `sources` parameter of `orchestrator.orchestrate()` to explicitly select providers, bypassing classification entirely.

**Direct LPI Query:** `worldbank-lpi` is not in the orchestrator routing table. It must be queried directly via `registry.query("worldbank-lpi", query, context, scope, limit)`.

**Confirmed source IDs (from `config.py`):**
- `moaah`
- `zatca`
- `gccstat`
- `un-comtrade`
- `tradedata`
- `worldbank-lpi`

**Query strategy for Export Readiness:**

| Report Section | Orchestrator Call | Direct Query | Fallback |
|----------------|-------------------|--------------|----------|
| **Regulatory Requirements** | `orchestrator.orchestrate(query, context={"country": "<ISO2>"}, sources=["moaah", "zatca"], limit=10)` | — | If empty: retry with `sources=["moaah", "zatca", "gccstat"]` |
| **Market Access** | `orchestrator.orchestrate(query, context={"country": "<ISO2>", "hs_code": "<code>"}, sources=["moaah", "zatca", "tradedata"], limit=10)` | — | If empty: retry with `sources=["moaah", "zatca", "gccstat"]` |
| **Logistics Profile** | — | `registry.query("worldbank-lpi", query, context={"country": "<ISO2>"}, scope="LP.LPI.OVRL.XQ", limit=10)` | — |
| **Historical Trade Context** | `orchestrator.orchestrate(query, context={"country": "<ISO2>", "product": "<name>"}, sources=["un-comtrade", "tradedata"], limit=10)` | — | If empty: retry with `sources=["un-comtrade", "tradedata", "faostat"]` |

**Key points:**
- `context["country"]` must be a valid ISO2 country code for the target market.
- For World Bank LPI, `scope="LP.LPI.OVRL.XQ"` requests the overall LPI score. Other indicator codes may be used if needed.
- The `query` string is still passed to orchestrator for full-text matching within the selected providers, but provider selection is deterministic via `sources`.
- No modifications to `_routing_table` or `_classification_rules` are required or recommended for this feature.

---

### 4.2 LLM Integration

**Current LLM setup:**
- Provider: Gemini (configurable via `LLM_PROVIDER` env var)
- Registry: `llm_registry` (global)
- Used in: Reasoning Engine for mission reasoning

**GeminiProvider.generate() behavior:**
- On success: returns `LLMResponse(content=..., model=..., usage=..., finish_reason=...)`
- On failure: raises `RuntimeError("LLM generation failed")`
- Does **not** return `None` on failure.

**For Export Readiness:**
- Use existing `llm_registry` to get the LLM provider via `llm_registry.get_provider("gemini")`
- Construct a prompt with:
  - Product name + HS code
  - Target market
  - Available data summary (what each provider returned)
  - Data gaps (what was not available)
  - Request: "Generate a concise recommendation for the user about exporting this product to this market"
- Wrap in try/except for `RuntimeError`:
  ```python
  try:
      response = await provider.generate(prompt, system_prompt, parameters)
      recommendation = response.content
  except RuntimeError:
      recommendation = None
  ```
- If LLM unavailable or raises `RuntimeError`: `recommendation = null` (graceful degradation)

---

## 5. Decision Report Specification

### 5.1 Report Sections (Minimum)

| Section | Data Source | Availability Logic |
|---------|-------------|-------------------|
| **Product & Market Summary** | User input + Knowledge Graph (if product exists) | Always available |
| **Regulatory Requirements** | Moaah, ZATCA via Orchestrator (explicit `sources=["moaah", "zatca"]`) | available if ≥1 provider returns data with confidence ≥ 0.5 |
| **Market Access Conditions** | Moaah, ZATCA, TradeData via Orchestrator (explicit `sources=["moaah", "zatca", "tradedata"]`) | available if ≥1 provider returns data with confidence ≥ 0.5 |
| **Logistics Profile** | World Bank LPI direct query (`registry.query("worldbank-lpi", context={"country": "<ISO2>"})`) | available if LPI data exists for target market |
| **Historical Trade Context** | UN Comtrade, TradeData via Orchestrator (explicit `sources=["un-comtrade", "tradedata"]`) | available if ≥1 provider returns data with confidence ≥ 0.5 |
| **Action Checklist** | Deterministic rules based on available sections | Always generated |
| **Recommendation** | LLM synthesis | null if LLM unavailable |

### 5.2 Availability Labels

| Label | Condition |
|-------|-----------|
| `available` | Data present, confidence ≥ 0.6, from ≥1 provider |
| `partial` | Some data present but gaps, or confidence < 0.6 |
| `not_available` | No data from any provider for this section |

### 5.3 Data Quality Note

Always included. Examples:
- "Regulatory data covers Egypt-Saudi corridor only. For EU markets, manual verification required."
- "Logistics data is from 2023. Check current conditions."
- "No trade history found between Egypt and this market."

---

## 6. Integration Points

### 6.1 Routing

**File:** `frontend/src/App.tsx`
```tsx
<Route path="export-readiness" element={<ExportReadiness />} />
```

**File:** `frontend/src/components/layout/Sidebar.tsx`
- Add nav item for `/export-readiness` with roles: `['owner', 'manager', 'sales', 'admin_staff', 'accountant', 'logistics']`

### 6.2 Authentication

- Uses existing `useAuthStore` and `api` axios instance with Bearer token
- Backend endpoint uses `Depends(get_current_user)`
- `get_current_user` returns a `dict` from the users table row, containing at least `id` (int) and `role` (str)
- The `user_id` for the report should be taken from `current_user["id"]`

---

### 6.3 Services

**New file:** `frontend/src/services/exportReadiness.ts`
```tsx
export const analyzeExportReadiness = (data: {
  product_id?: number;
  hs_code?: string;
  product_name?: string;
  target_market: string;
}) => api.post('/api/v1/export-readiness/analyze', data);
```

**Update:** `frontend/src/services/api.ts` — no changes needed if using separate service file

### 6.4 State Management

- No new global store needed for MVP
- Local component state in `ExportReadiness.tsx` is sufficient:
  - `productId`, `hsCode`, `productName`, `targetMarket`
  - `report`, `loading`, `error`

### 6.5 Backend Router

**New file:** `backend/app/routers/export_readiness.py`
- Prefix: `/api/v1/export-readiness`
- Endpoint: `POST /analyze`
- Auth: `Depends(get_current_user)`
- Service: `ExportReadinessService`

### 6.6 Backend Service

**New file:** `backend/app/services/export_readiness.py`
- `ExportReadinessService.analyze()`
- Uses: `KnowledgeOrchestrator`, `llm_registry`, provider registry
- Returns: `ExportReadinessReport` Pydantic model

---

## 7. Implementation Tasks

### Task 1: Backend — Export Readiness Service
**File:** `backend/app/services/export_readiness.py`

1. Define Pydantic models:
   - `ExportReadinessSection`
   - `ExportReadinessReport`
   - `ExportReadinessRequest`
2. Implement `ExportReadinessService.analyze()`:
   - Accept product/market inputs
   - Query orchestrator for each section
   - Handle LPI direct query (not in routing table)
   - Determine availability per section
   - Generate action checklist
   - Call LLM for recommendation (with fallback)
   - Return structured report

### Task 2: Backend — Export Readiness Router
**File:** `backend/app/routers/export_readiness.py`

1. Create router with prefix `/api/v1/export-readiness`
2. Add `POST /analyze` endpoint
3. Wire into `main.py` (add `include_router(export_readiness.router)`)

### Task 3: Frontend — Export Readiness Page
**File:** `frontend/src/pages/ExportReadiness.tsx`

1. Create page component with:
   - Product input (dropdown + manual HS code)
   - Target Market dropdown
   - Analyze button
   - Report display (section cards, checklist, recommendation)
   - Loading/error states
2. Reuse existing UI components (Card, Button, Input, Select, Skeleton, Badge)

### Task 4: Frontend — Routing + Navigation
**Files:** `frontend/src/App.tsx`, `frontend/src/components/layout/Sidebar.tsx`

1. Add `/export-readiness` route to App.tsx
2. Add nav item to Sidebar.tsx

### Task 5: Frontend — API Service
**File:** `frontend/src/services/exportReadiness.ts`

1. Create `analyzeExportReadiness()` function
2. Export for use in page component

### Task 6: Testing
**Backend:**
- Unit test for `ExportReadinessService.analyze()` with mocked orchestrator
- Test availability logic (available/partial/not_available)
- Test LLM fallback when unavailable
- Test error handling

**Frontend:**
- Component render test (loading, error, success states)
- API integration test with mocked backend

**E2E (if supported):**
- User enters product + market → sees report

---

## 8. Acceptance Criteria

1. **User can navigate to `/export-readiness`** from sidebar or DEM Landing
2. **User can select/enter a product and target market**
3. **User clicks "Analyze Readiness" and sees a loading state**
4. **System returns a report with at least 3 of 4 sections populated** (given current provider coverage)
5. **Each section shows:** title, source, confidence, availability status, data or "not available" message
6. **Action Checklist is always generated** based on available sections
7. **Recommendation appears if LLM is configured**, otherwise shows gracefully
8. **Data Quality Note is always present**
9. **No new providers added**
10. **No changes to Coverage Scores or Provider Ceiling**
11. **All existing tests continue to pass**

---

## 9. Risks / Blockers

| Risk | Severity | Mitigation |
|------|----------|------------|
| World Bank LPI not in orchestrator routing table | Medium | Query LPI directly as fallback for MVP |
| LLM not configured (no API key) | Low | Graceful degradation — recommendation = null |
| Some providers return empty results for certain markets | Low | Availability labels handle this |
| Product dropdown source unclear | Low | MVP can use simple text input + optional product selection |
| HS Code validation not implemented | Low | Accept free text, pass to orchestrator as query terms |

---

## 10. Confirmed Non-Goals (Out of Scope)

- ❌ No new providers
- ❌ No new research paths
- ❌ No external knowledge expansion
- ❌ No coverage score changes
- ❌ No provider ceiling changes
- ❌ No WP creation
- ❌ No Market Opportunity analysis
- ❌ No Global SPS/TBT coverage
- ❌ No avatar/renderer features
- ❌ No multi-market comparison
- ❌ No PDF export (v1 shows on-screen only)

---

## 11. Next Code Step

**After plan approval, the first implementation task is:**

**Task 1: Backend — Export Readiness Service + Router**

Create:
1. `backend/app/services/export_readiness.py` — Service with Pydantic models + `analyze()` method
2. `backend/app/routers/export_readiness.py` — Router with `POST /analyze` endpoint
3. Wire router into `backend/main.py`

This is the smallest backend change that makes the feature callable from the frontend. It can be built and tested independently of the frontend.

---

*Plan Status: Ready for Implementation — Export Readiness Vertical Slice — Product Priority per Section 32 of External Knowledge Portfolio Re-Evaluation Plan*
