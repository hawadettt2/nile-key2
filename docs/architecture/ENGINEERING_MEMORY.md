# Engineering Memory

**Last Updated:** 2026-08-15
**Project:** Nile Key Platform
**Authority:** `PLAN.md` (Master Roadmap v2.1) — Single Source of Truth

## Architecture Vision Statement

Nile Key is an Intelligent Operating Platform with Digital Export Manager (DEM) as the first Executive Intelligence Layer.

Target Architecture layers:
- Executive Intelligence: DEM
- Cognitive: Reasoning Engine, Company Knowledge Layer, Long-Term Memory (WP-31)
- Planning: Task Planner, Execution Planner
- Orchestration: Tool Orchestrator
- Business / ERP Services: Shipping, ETA, Customs, Suppliers, Customers, Documents, Resources, Notifications, Audit, Workflow, Dashboard, Search
- Database: SQLite (MVP) → PostgreSQL (Production)

Current implementation status:
- Phase 1 + Phase 1.5 complete
- Phase 2 in progress: WP-30B–WP-30I complete as scaffolding/intelligence layer
- Current intelligence is Deterministic/Scaffolded Intelligence — rule-based, interfaces, and registry-driven
- LLM Provider connected: Google AI (Gemini) via WP-LLM-001
- No final decision yet on operating cost, Knowledge Ingestion, or Avatar Renderer
- Absence of a current LLM is not an architectural failure; it is an architecture-ready step toward a future target

Deferred / Future:
- LLM integration — completed via WP-LLM-001 (Google AI / Gemini provider integrated)
- Avatar Renderer — contract defined, implementation deferred
- Goal and Plan reasoning layers — deferred to future work packages
- Multi-agent coordination — future
- Full export operations autonomy — future

---

| WP | Status | Commit | Notes |
|----|--------|--------|-------|
| WP-01A | ✅ Complete | 3597c67 | Unicode emoji fix in main.py lifespan for Windows compatibility |
| WP-01B | ✅ Complete | d036c06 (recovery) | Reverted to bcrypt, installed bcrypt<4.0 for passport compatibility |
| WP-02A | ✅ Complete | a0e87e7 | Added username, phone, company, updated_at columns to users table; fixed auth.py column reference |
| WP-02B | ✅ Complete | 94ae639 | Added suppliers schema + response compatibility + role case fixes |
| WP-02C | ✅ Complete | 5cec3ca | Added customers schema + response compatibility layer with legacy fallbacks |
| WP-02D | ✅ Complete | 547aa13 | Added shipments schema + response compatibility layer (ADR-0001) |
| WP-02D | ✅ Complete | 3219904 | Added invoices schema + response compatibility layer |
| WP-02F | ✅ Complete | 3219904 | Added customs_declarations schema + response compatibility layer |
| WP-02G | ✅ Complete | 3219904 | Added resources schema + response compatibility layer |
| WP-02H | ✅ Complete | 3219904 | Added documents schema + response compatibility layer |
| WP-03 | ✅ Complete | dbe1ef4 | Aligned OAuth2 status codes: 401 for missing auth, 403 for missing role |
| WP-04 | ✅ Complete | — | All CRUD operations verified working against aligned schema |
| WP-02-Infra | ✅ Complete | 98838d1 | Added ensure_columns() helper for reusable schema migrations |
| Doc-01 | ✅ Complete | 9a1682d | Established ENGINEERING_MEMORY.md, docs/appendices/WORK_PACKAGE_PLAN.md, PLAN.md Section 22, docs/architecture/REPOSITORY_INTELLIGENCE.md (archived), ARCHITECTURE_CHARTER.md (archived) |
| WP-05 | ✅ Complete | — | Frontend builds successfully |
| WP-06 | ✅ Complete | — | Integration testing complete; 21 pytest tests pass |
| WP-07 | ✅ Complete | — | SECRET_KEY externalized, CORS configuration replaced with settings.ALLOWED_ORIGINS |
| WP-08 | ✅ Complete | — | .env.example aligned with config.py; execute_update() helper added |
| WP-09 | ✅ Complete | — | Extracted execute_update() helper; integrated into 8 routers; ~120 lines removed |
| WP-10 | ✅ Complete | 56fc391 | Alembic migrations initialized; legacy column cleanup committed; invoices.uuid removed |
| WP-11 | ✅ Complete | 08a9924 | Synchronize project documentation with current implementation |
| WP-12 | ✅ Complete | 54f7c49 | Harden Docker deployment and finalize Compose configuration |
| WP-13A | ✅ Complete | c66087e / 3351a4d | Extract supplier and customer business logic into service layer |
| WP-14 | ⏳ Integrated | — | Combined into WP-15 |
| WP-15 | ✅ Complete | 1d545b1 | Complete service layer extraction for resources, customs, documents, shipping, invoices |
| WP-16A | ⏳ Integrated | — | Executed as part of WP-15/WP-16B verification |
| WP-16B | ✅ Complete | b4ff64f | Introduce shared service base infrastructure (base.py, standardized helpers) |
| WP-17A | ✅ Complete | cdb8bb9 | Expand API endpoint coverage: 48 new tests across 6 domains |
| WP-17B | ✅ Complete | working tree | Add service-layer unit tests: 59 new tests across 7 modules; production code unchanged |
| WP-18 | ✅ Complete | working tree | Fix HS-code `created_at` schema mismatch; fix document upload `type` omission; validate Docker production artifacts |
| WP-19 | ✅ Complete | working tree | ETA Engine: schemas, client, service layer, router, scheduler, 71 tests (70 passing, 1 skipped); business logic extracted from erpnext_egypt_compliance |
| WP-20 | ✅ Complete | working tree | Shipping Engine: provider abstraction, LetMeShip + SendCloud clients, scheduler, 34+ tests |
| WP-21 | ✅ Complete | working tree | Platform integration: notifications, audit, search, dashboard, workflows, frontend integration |
| WP-30B | ✅ Complete | working tree | Session Management + Mission Lifecycle; 6 DEM endpoints; router registered |
| WP-30C | ✅ Complete | working tree | Task Planner + Execution Engine; structured mission execution; retry, idempotency, audit |
| WP-30D | ✅ Complete | working tree | Decision Engine; reasoning loop with knowledge/memory graceful degradation |
| WP-30E | ✅ Complete | working tree | 14 ERP tool wrappers with metadata; ToolRegistry populated; legacy planner drift fixed |
| WP-30F | ✅ Complete | working tree | Company Knowledge Layer interface; KnowledgeProvider, KnowledgeQuery, KnowledgeProviderRegistry, ingestion contract; 17 tests |
| WP-30G | ✅ Complete | working tree | MemoryProvider interface with recall/store/forget/summarize; DEM core graceful degradation; 12 tests |
| WP-30H | ✅ Complete | working tree | Avatar Contract; IntentContent and AvatarRenderer interfaces; structured intents confirmed; 15 tests; AVATAR_CONTRACT.md created; no regressions |
| WP-30I | ✅ Complete | working tree | Advanced Features: multi-step workflow executor, proactive monitoring, training mode, approval gates |
| WP-31 | ✅ Complete | working tree | AI Memory: SQLiteMemoryProvider concrete implementation; memory injection; 151 agent tests passing |
| WP-32 | ✅ Complete | working tree | Knowledge Graph: 9 node types, 9 API endpoints, derived edges, graph traversal, entity sync, MemoryProvider integration, audit logging; 105 tests |
| WP-33 | ✅ Complete | working tree | Trade Intelligence: supplier/buyer analysis, trend detection, comparisons, report generation; 120 tests |
| WP-34 | ✅ Complete | working tree | External Research Capability; 103 tests; Research lifecycle, evidence/provenance, result structuring, verification/quality |
| WP-37 | ✅ Complete | working tree | Knowledge Ingestion Pipeline: RegulationsKnowledgeProvider; JSON file ingestion; REGULATIONS_FILE_PATH configurable; 12 tests; no regressions |
| WP-38a | ✅ Complete | working tree | External Source Integration: Moaah API adapter with retry/backoff, provenance metadata, registry registration, 15 tests (9 unit + 6 integration); no regressions |
| WP-38b | ✅ Complete | working tree | Global Trade Intelligence: TradeData API adapter with retry/backoff, provenance metadata, registry registration, 21 tests (14 unit + 7 integration); no regressions; baseline `baseline-wp38b-final` at `02bad55`; Owner Acceptance obtained |
| WP-38c | ✅ Complete | working tree | Jordan + UAE + Saudi/GCC Sources: ZATCA Open Data APIs adapter with retry/backoff, provenance metadata, registry registration, 19 tests (13 unit + 6 integration); no regressions |
| WP-38d | ✅ Complete | working tree | GCC Expansion: GCC-Stat Open Data APIs adapter with retry/backoff, provenance metadata, registry registration, 23 tests (16 unit + 7 integration); no regressions |
| Export Readiness Vertical Slice | ✅ Complete | working tree | Product-layer composition of existing providers into `/export-readiness` page + `POST /api/v1/export-readiness/analyze`; explicit provider routing with primary/fallback sources; direct World Bank LPI query; LLM recommendation with RuntimeError graceful degradation; 7 backend tests + 9 frontend tests; no regressions; no new providers, no coverage/ceiling changes |
| Knowledge Orchestration / Fusion Layer | ✅ Complete | working tree | KnowledgeOrchestrator: classification, routing, ranking, dedup, conflict resolution; 85 new tests (66 unit + 18 integration); 46/47 regression pass; 1 pre-existing failure confirmed; router adjustment for shared ReasoningEngine; 5 config settings added |
| WP-40 | ✅ Complete | c30a935 / a0dfd20 / 195b204 | Docker Compose Final Verification: both images build, services healthy, API reachable, frontend served on port 3000, database persistence verified, frontend TypeScript build errors resolved |

---

## Completed Commits

| Hash | Message | Date |
|------|---------|------|
| 02bad55 | feat(wp-38b): finalize TradeData first provider implementation | 2026-08-13 |
| 13fb461 | feat(wp-38a): finalize Moaah first provider implementation | 2026-08-13 |
| 195b204 | docs(wp40): add WP-40 planning and closure reports | 2026-07-21 |
| a0dfd20 | docs(wp40): update governance documents and close WP-40 | 2026-07-21 |
| c30a935 | fix(frontend): resolve TypeScript build errors for Docker deployment | 2026-07-21 |
| e48ece1 | docs(wp33): close WP-33 and update planning documents | 2026-07-21 |
| 524c733 | feat(wp31): close WP-31 — AI Memory | 2026-07-21 |
| bbd7abb | feat(wp31): close WP-31 — AI Memory (earlier commit) | 2026-07-21 |
| 3b953d0 | feat(wp33): implement Trade Intelligence service layer and API | 2026-07-21 |
| d94a929 | test(wp33): add Trade Intelligence test suite | 2026-07-21 |
| b4ff64f | refactor: introduce shared service base infrastructure (WP-16B) | 2026-07-05 |
| 1d545b1 | refactor: complete service layer extraction (WP-15) | 2026-07-05 |
| 3351a4d | WP-13A: Extract customer business logic into service layer | 2026-07-05 |
| c66087e | WP-13A: Extract supplier business logic into service layer | 2026-07-05 |
| 54f7c49 | WP-12: Harden Docker deployment and finalize Compose configuration | 2026-07-05 |
| 08a9924 | WP-11: Synchronize project documentation with current implementation | 2026-07-05 |
| 56fc391 | WP-10: Repair Alembic migration history for invoices schema | 2026-07-04 |
| dbe1ef4 | WP-03: Align authentication status codes with OAuth2 standard | 2026-06-30 |

---

## Important Architectural Decisions

1. **SQLite is implementation detail** (per PLAN.md Section 9.9) - will change to PostgreSQL in production
2. **Pydantic schemas are Source of Truth** - database must follow schemas (PLAN.md Section 9.3)
3. **bcrypt is required password algorithm** - passlib[bcrypt] in requirements.txt
4. **No business logic in routers** (PLAN.md Section 9.10) - must move to services layer
5. **Code duplication prohibited** (PLAN.md Section 9.8) - execute_update() extracted in WP-09
6. **Legacy Compatibility Policy** - Legacy columns are excluded from API responses, not used as fallbacks
7. **ADR-0001: Shipments Legacy Columns** - Legacy columns are NOT fallback pairs; excluded entirely from API contract. See docs/architecture/ADR-0001-shipments-legacy-columns.md
8. **Database initialization flow** - `init_db()` creates/maintains schema; Alembic handles destructive post-init cleanup
9. **FastAPI is public contract** - routers must reflect business operations (PLAN.md Section 9.10)
10. **Frontend consumes API only** - Frontend never defines business rules (PLAN.md Section 9.11)

---

## WP-10 Migration System

### Database Initialization Flow

1. FastAPI startup calls `init_db()`
2. `init_db()` creates tables from scratch via raw SQL
3. `init_db()` applies incremental column additions via `_ensure_*_schema()`
4. `init_db()` inserts seed data
5. Alembic migrations run afterward for destructive schema cleanup

### Alembic Chain

- `9f6e6d58ca0f_initial` — empty revision chain start
- `0f82a20f2bb7_legacy_cleanup` — drops legacy columns via SQLite-safe patterns
- `bdab744e83e3_legacy_cleanup_fix` — rebuilds `invoices` without `uuid` for SQLite safety

---

## Rejected Approaches

| Approach | Reason |
|----------|--------|
| bcrypt 5.0.0 with passlib 1.7.4 | Incompatible: __about__ attribute removed in bcrypt 5.x |
| pbkdf2_sha256 for password hashing | Violates requirements.txt (bcrypt specified) |
| Keeping Unicode emojis in main.py | Causes UnicodeEncodeError on Windows cp1256 console |
| ORM abstraction layer | Raw SQL preferred for SQLite control and PostgreSQL migration path |
| Legacy column fallbacks | Violates ADR-0001; legacy columns excluded from API contract |

---

## Recovery Checkpoints

| File | Change | Reason |
|------|--------|--------|
| backend/app/core/config.py | DEBUG: bool -> str | Pydantic-settings needs string for env vars |
| backend/app/core/database.py | Added get_db(), ensure_columns(), execute_update() | Required by router code and WP-02/09 |
| backend/app/models/__init__.py | Removed imports / added SQLAlchemy target_metadata | Was causing ImportError; supports Alembic autogenerate |
| backend/app/routers/*.py | Removed legacy compatibility filters | Legacy columns removed from schema in WP-10 |

All recovery changes: **KEEP** (syntactically valid, functionally safe)

---

## Known Risks

| Risk Level | Issue | Status |
|------------|-------|--------|
| 🔴 CRITICAL | Database schema mismatch | ✅ WP-02A-H complete - all entities aligned |
| 🟡 MEDIUM | Docker deployment unvalidated | ✅ RESOLVED — Both images build successfully; `docker compose up --build` verified with healthy services; database persistence confirmed via Docker volume |
| 🟢 LOW | Manual frontend types | ✅ Automatically generated types match API |
| 🟡 MEDIUM | No rate limiting | Open — listed in TECH_DEBT.md |
| 🟡 MEDIUM | PostgreSQL migration path | Open — SQLite is implementation detail per PLAN.md |
| 🟢 LOW | Root `alembic.ini` exists | Low priority cleanup |
| 🟢 LOW | `__pycache__` directories | Mostly gitignored |

---

## Current Project Status

| Component | Status |
|-----------|--------|
| Backend | ✅ Starts; health endpoint healthy; 16 routers registered in main.py |
| Frontend | ✅ Builds (`npm run build` passes); 11 pages |
| Tests | ✅ 876 passing, 5 failed (pre-existing), 8 skipped by design |
| Alembic | ✅ Migration chain functional (3 revisions) |
| Docker | ✅ Validated; both services healthy on ports 8000/3000 |
| Services layer | ✅ Implemented (19 service modules excluding package inits) |
| Schemas | ✅ 18 Pydantic schema modules |
| ETA Engine | ✅ Implemented (WP-19); OAuth2, batch submission, scheduler, 71 tests |
| Shipping Engine | ✅ Implemented (WP-20); LetMeShip + SendCloud, 34+ tests |
| Platform Integration | ✅ Complete (WP-21); notifications, audit, search, dashboard, workflows |
| Digital Export Manager | ✅ Complete (WP-30B-30I); session management, task planner, decision engine, tools, knowledge, memory, avatar, monitoring |
| AI Memory | ✅ Complete (WP-31); SQLiteMemoryProvider, 151 agent tests |
| Knowledge Graph | ✅ Complete (WP-32); 9 node types, 9 endpoints, 105 tests |
| Trade Intelligence | ✅ Complete (WP-33); analysis, trends, comparisons, 120 tests |
| Notification Triggers | ✅ Implemented (WP-21 M3); ETA + Shipping triggers, 17 tests |
| Frontend Tests | ✅ 17 Vitest + React Testing Library tests |
| Database Persistence | ✅ Confirmed via Docker volume in WP-40 |

---

## WP-37 Implementation Summary

### WP-37: Knowledge Ingestion Pipeline — File-based Regulations Provider (Completed)
- **RegulationsKnowledgeProvider:** New `KnowledgeProvider` implementation reading local JSON regulation files
- **File Format:** JSON array of objects with id, title, description, regulation_type, category, country, effective_date, source_url, version
- **Configuration:** `REGULATIONS_FILE_PATH` added to `config.py` with default `backend/data/regulations.json`
- **Bootstrap:** Provider registered in `main.py` lifespan alongside existing providers
- **Confidence Rules:** 0.5 if effective_date missing; 0.85 if source_url present; 0.75 if source_url absent
- **Updated At:** Derived from file mtime in ISO-8601 UTC format
- **Semantics:** Append-only; file is single source of truth; re-read on startup only
- **Tests:** 12 new tests (8 unit + 4 integration); all passing
- **Regression:** No regressions in knowledge layer; 2 pre-existing failures in unrelated reasoning engine tests confirmed
- **Constraints:** No DEM core changes, no Knowledge Graph schema changes, no Memory/LLM/Research integration, no database migrations, no CSV/External API support

## WP-38a Implementation Summary

### WP-38a: External Source Integration — Moaah First Provider (Closed)
- **MoaahExternalSourceAdapter:** New `KnowledgeProvider` implementation fetching from Moaah `/regs-search` REST API
- **MoaahApiClient:** Isolated HTTP client with 3-attempt retry and exponential backoff (1s→2s) for timeouts, network errors, and HTTP 429
- **Configuration:** `MOAAH_BASE_URL`, `MOAAH_API_KEY`, `MOAAH_TIMEOUT_SECONDS`, `MOAAH_SOURCE_ID`, `MOAAH_SOURCE_NAME`, `MOAAH_SOURCE_TYPE`, `MOAAH_SOURCE_VERSION` added to `config.py`
- **Bootstrap:** Provider conditionally registered in `main.py` `lifespan()` wrapped in try/except
- **Confidence Rules:** 0.75 if source_url absent; 0.85 if source_url present and effective_date present; 0.90 if legal_act_reference present
- **Provenance Metadata:** source_id, source_url, source_authority, effective_date, legal_act_reference, fetch_timestamp, record_hash, retrieval_status assigned by adapter
- **Tests:** 15 new tests (9 unit + 6 integration); all passing
- **Regression:** No regressions; 1 pre-existing failure in unrelated ReasoningEngine reasoning text formatting confirmed
- **Baseline:** `baseline-wp38a-final` at commit `13fb461b`
- **Constraints:** No DEM core changes, no Knowledge Graph schema changes, no Memory/LLM/Research integration, no database migrations, no CSV support

## WP-38b Implementation Summary

### WP-38b: Global Trade Intelligence — TradeData First Provider (Closed)
- **TradeDataExternalSourceAdapter:** New `KnowledgeProvider` implementation fetching from TradeData `/api/v1/tradeDetail` REST API
- **TradeDataApiClient:** Isolated HTTP client with retry/backoff (429: 3 attempts exponential 1s→2s; network/5xx: 2 attempts exponential 2s→4s)
- **Configuration:** `TRADEDATA_BASE_URL`, `TRADEDATA_API_KEY`, `TRADEDATA_TIMEOUT_SECONDS`, `TRADEDATA_SOURCE_ID`, `TRADEDATA_SOURCE_NAME`, `TRADEDATA_SOURCE_TYPE`, `TRADEDATA_SOURCE_VERSION` added to `config.py`
- **Bootstrap:** Provider conditionally registered in `main.py` `lifespan()` wrapped in try/except when `TRADEDATA_API_KEY` and `TRADEDATA_BASE_URL` are configured
- **Confidence Rules:** 0.85 if dataSource + date + country code present; 0.75 if dataSource or date present; 0.65 if only hsCode/buyerName/supplierName present; 0.50 otherwise; +0.05 for hs_code/buyer_name/supplier_name filter matches (cap 0.95); -0.10 for out-of-range dates (floor 0.50); -0.05 for lower-priority sources (floor 0.50)
- **Provenance Metadata:** source_id, source_authority, effective_date, country, source_url, legal_act_reference, updated_at, version, record_hash, retrieval_status assigned by adapter
- **Field Mapping:** dataSource→source_authority, date→effective_date, buyerName/supplierName/hsCodeDesc/productKeyword→content, originCountryCode/destinationCountryCode→country, masterBl/containerNo→source_url, otherInfo→legal_act_reference
- **Tests:** 21 new tests (14 unit + 7 integration); all passing
- **Regression:** No regressions in Moaah tests (15/15 passing)
- **Baseline:** Pending G5 closure
- **Constraints:** No DEM core changes, no Knowledge Graph schema changes, no Memory/LLM/Research integration, no database migrations, no CSV support, Provider-Agnostic architecture preserved

## WP-38c Implementation Summary

### WP-38c: Jordan + UAE + Saudi/GCC Sources — ZATCA Open Data APIs (Task 8 Completed)
- **ZatcaExternalSourceAdapter:** New `KnowledgeProvider` implementation fetching from ZATCA Open Data APIs (`zatca.gov.sa`)
- **ZatcaApiClient:** Isolated HTTP client with retry/backoff (429: 3 attempts exponential 1s→2s; network/5xx: 2 attempts exponential 2s→4s)
- **Configuration:** `ZATCA_BASE_URL`, `ZATCA_API_KEY`, `ZATCA_TIMEOUT_SECONDS`, `ZATCA_SOURCE_ID`, `ZATCA_SOURCE_NAME`, `ZATCA_SOURCE_TYPE`, `ZATCA_SOURCE_VERSION` added to `config.py`
- **Bootstrap:** Provider conditionally registered in `main.py` `lifespan()` wrapped in try/except when `ZATCA_API_KEY` and `ZATCA_BASE_URL` are configured
- **Confidence Rules:** 0.85 if valid data with timestamp present; 0.75 if timestamp missing but core fields present; 0.65 if only minimal fields present; 0.50 if malformed/incomplete; +0.05 for port_name/traffic_type filter matches (cap 0.95); -0.10 for out-of-range dates (floor 0.50)
- **Provenance Metadata:** source_id, source_authority, effective_date, country, source_url, legal_act_reference, updated_at, version, record_hash, retrieval_status assigned by adapter
- **Field Mapping:** description/port_name/traffic_type/quantity/weight/amount → content (metrics), date → effective_date, endpoint → source_url, country → SA
- **Tests:** 19 new tests (13 unit + 6 integration); all passing
- **Regression:** No regressions in TradeData (21/21) and Moaah (15/15) tests
- **Constraints:** No DEM core changes, no Knowledge Graph schema changes, no Memory/LLM/Research integration, no database migrations, no CSV support, Provider-Agnostic architecture preserved

## WP-38d Implementation Summary

### WP-38d: GCC Expansion — GCC-Stat Open Data APIs (Task 8 Completed)
- **GccstatExternalSourceAdapter:** New `KnowledgeProvider` implementation fetching from GCC-Stat SDMX/REST APIs (`gccstat.org`)
- **GccstatApiClient:** Isolated HTTP client with retry/backoff (429: 3 attempts exponential 1s→2s; network/5xx: 2 attempts exponential 2s→4s)
- **Configuration:** `GCCSTAT_BASE_URL`, `GCCSTAT_API_KEY`, `GCCSTAT_TIMEOUT_SECONDS`, `GCCSTAT_SOURCE_ID`, `GCCSTAT_SOURCE_NAME`, `GCCSTAT_SOURCE_TYPE`, `GCCSTAT_SOURCE_VERSION` added to `config.py`
- **Bootstrap:** Provider conditionally registered in `main.py` `lifespan()` wrapped in try/except when `GCCSTAT_BASE_URL` is configured
- **Confidence Rules:** 0.85 if source_authority + effective_date + country present; 0.75 if source_authority or effective_date present; 0.65 if obs_value present; 0.50 otherwise
- **Provenance Metadata:** source_id, source_authority, effective_date, country, source_url, legal_act_reference, updated_at, version, record_hash, retrieval_status assigned by adapter
- **Field Mapping:** SDMX observation value → content (metrics), TIME_PERIOD → effective_date, ref_area → country, dataflow reference → source_url
- **Tests:** 23 new tests (16 unit + 7 integration); all passing
- **Regression:** No regressions in existing tests
- **Constraints:** No DEM core changes, no Knowledge Graph schema changes, no Memory/LLM/Research integration, no database migrations, no CSV support, Provider-Agnostic architecture preserved

## Knowledge Orchestration / Fusion Layer Implementation Summary

### Knowledge Orchestration / Fusion Layer (Closed)
- **KnowledgeOrchestrator:** New orchestration layer wrapping `KnowledgeProviderRegistry` with deterministic classification, routing, parallel querying, composite ranking, deduplication, and conflict resolution
- **Classification:** 6 query types (agrifood, customs, market_access, regulatory, trade_statistics, rules_of_origin) + general fallback; deterministic keyword matching
- **Routing:** Primary/secondary provider routing per query type; sources filter bypass; graceful skip of missing providers
- **Ranking:** Composite score = confidence * 0.4 + authority_weight * 0.3 + recency_weight * 0.2 + relevance_weight * 0.1; deterministic tie-breaking by effective_date DESC, source_id ASC
- **Deduplication:** Cross-provider dedup key = sha1(content[:100] + "|" + effective_date); same-source → highest composite_score; cross-source → highest authority_weight then composite_score
- **Conflict Resolution:** "latest_official_wins" strategy; authority diff > 1 → authority wins; otherwise date wins; equal authority+date → both kept with conflict flag
- **engine.py Changes:** Extracted `_query_knowledge_legacy()` (byte-for-byte equivalent to original); `_query_knowledge()` uses orchestrator when attached, else legacy fallback; orchestration metadata cached in `_last_orchestration_meta` and preserved in `Decision.context["knowledge_orchestration"]`
- **main.py Wiring:** `KnowledgeOrchestrator` initialized in `lifespan()` when `KNOWLEDGE_ORCHESTRATION_ENABLED=True`; attached to shared `ReasoningEngine` via `app.state.reasoning_engine`
- **Router Adjustment:** `get_reasoning_engine()` in `digital_export_manager.py` returns shared `app.state.reasoning_engine` instead of creating new instance per request — necessary technical change to preserve orchestrator attachment
- **Configuration:** 5 new `KNOWLEDGE_ORCHESTRATION_*` settings added to `config.py`
- **Tests:** 85 new tests (66 unit + 18 integration); all passing
- **Regression:** 46/47 existing tests pass; 1 pre-existing failure in `test_registry_provider_failure_does_not_crash_reasoning` confirmed present in baseline (score threshold behavior, not Fusion Layer related)
- **Baseline:** `baseline-fusion-layer` at commit `4b5dafe`
- **Constraints:** No new providers, no new knowledge families, no logistics, no LLM synthesis, no Knowledge Graph changes, no database migrations, no frontend/avatar changes, no modifications to `KnowledgeProvider`, `KnowledgeProviderRegistry`, `Decision` schema, or `PLAN.md`

## Credential Management Implementation Summary

### Credential Management Implementation (Closed)
- **Credential Abstraction Layer:** Introduced `Credential` interface with concrete types: `ApiKeyCredential`, `UsernamePasswordCredential`, `ClientIdSecretCredential`
- **CredentialStore:** Registry with `register()`, `get()`, `get_or_raise()`, `list_sources()`, `list_all()` methods; populated at startup from environment settings
- **Masking/Redaction:** All credential types implement `mask()` per approved design; first 4 chars visible if length > 4, else `***`
- **Lifecycle Hooks:** `on_before_use()`, `on_after_use()`, `on_expiry()` implemented; FAOSTAT JWT lifecycle preserved exactly
- **Migrated Services:** FAOSTAT, ETA, LetMeShip, SendCloud, Moaah, TradeData, ZATCA, GCC-Stat, SMTP/Notification, LLM (Gemini)
- **Gates:** G1–G6 all PASS
- **Tests:** 163 new tests across Phases 1–6; all passing
- **Regression:** No regressions in migrated adapters; 5 pre-existing failures in unrelated auth/workflow tests confirmed
- **Baseline:** Pending commit/baseline
- **Constraints:** No DEM Core changes, no Secret Store dependency, no new providers, no RefreshToken mechanism, no live validation outside WP scope

---

## Engineering Decisions Log

| Decision | Date | Status |
|----------|------|--------|
| ED-WP30-001 | WP-30B | Approved |
| ED-WP30-002 | WP-30F | Approved |
| ED-WP32-001 | WP-32 | Approved |
| ED-WP33-001 | WP-33 | Approved |
| ED-WP33-002 | WP-33 | Approved |
| ED-WP33-003 | WP-33 | Approved |

---

*Memory Last Updated: WP-38d closure — Task 8 completed; documentation updated; 23/23 tests passing; no regressions.*
