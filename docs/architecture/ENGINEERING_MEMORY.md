# Engineering Memory

**Last Updated:** 2026-07-21
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
| WP-37 | ✅ Complete | working tree | Knowledge Ingestion Pipeline: RegulationsKnowledgeProvider; JSON file ingestion; REGULATIONS_FILE_PATH configurable; 12 tests; no regressions |
| WP-40 | ✅ Complete | c30a935 / a0dfd20 / 195b204 | Docker Compose Final Verification: both images build, services healthy, API reachable, frontend served on port 3000, database persistence verified, frontend TypeScript build errors resolved |

---

## Completed Commits

| Hash | Message | Date |
|------|---------|------|
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

*Memory Last Updated: WP-41 closure — 876+ tests, Docker validated, TypeScript errors resolved, documentation updated.*
