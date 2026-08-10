# WP-37: Knowledge Ingestion Pipeline — File-based Regulations Ingestion Provider

**Work Package:** WP-37 — Knowledge Ingestion Pipeline (Phase 2.1)  
**Status:** Ready for Project Owner Approval  
**Authority:** `PLAN.md` (Master Roadmap v2.1) — Single Source of Truth  
**Governing Contract:** `.kilo/plans/KNOWLEDGE_INGESTION_CONTRACT.md`  
**Vertical Slice:** File-based Regulations Ingestion Provider  
**Date:** 2026-08-10  
**Plan Path:** `.kilo/plans/1786359213310-knowledge-ingestion-pipeline.md`

---

## 1. Architectural Intent

Implement the first concrete Knowledge Ingestion Provider that reads local regulation files (JSON), transforms them into the `KnowledgeProvider.query()` return shape, and registers them in the existing `KnowledgeProviderRegistry` — without modifying DEM core, Knowledge Graph schema, Memory, Research, or any existing contracts.

**Goal:** Prove the Knowledge Ingestion contract is executable end-to-end with a minimal, testable, production-safe vertical slice.

---

## 2. Current State (Verified)

| Component | State | Evidence |
|-----------|-------|----------|
| `KnowledgeProvider` ABC | ✅ Exists | `backend/app/agent/knowledge/provider.py` |
| `KnowledgeProviderRegistry` | ✅ Exists | `backend/app/agent/knowledge/registry.py` |
| `CompanyKnowledgeProvider` | ✅ Exists | `backend/app/agent/knowledge/company_knowledge_provider.py` — queries `resources` table |
| `KnowledgeGraphProvider` | ✅ Exists | `backend/app/agent/knowledge/graph_provider.py` — queries `knowledge_nodes` |
| ReasoningEngine integration | ✅ Exists | `backend/app/agent/decision_engine/engine.py` — accepts `knowledge_provider_registry` |
| Bootstrap wiring | ✅ Exists | `backend/main.py` — registers both providers at startup |
| Research (WP-34) | ✅ Separate | `backend/app/research/orchestrator.py` — 7-stage lifecycle, independent |
| Memory (WP-31) | ✅ Separate | `backend/app/agent/memory/sqlite_provider.py` — no coupling to ingestion |
| `config.py` pattern | ✅ Existing | `backend/app/core/config.py` — Pydantic Settings with env vars; `REGULATIONS_FILE_PATH` absent but pattern established |

**Gap:** No `KnowledgeProvider` implementation reads external files or APIs. All current providers query internal databases only.

---

## 3. Target State

A new `RegulationsKnowledgeProvider` that:
1. Reads local regulation files from a configured path (JSON)
2. Transforms each record into the `KnowledgeProvider.query()` return shape
3. Exposes source metadata via `get_sources()` with SemVer `version` and ISO-8601 `updated_at`
4. Assigns confidence scores (0.0–1.0) based on configurable rules
5. Registers itself in `KnowledgeProviderRegistry` at application startup
6. Is queryable by `ReasoningEngine` and `Trade Intelligence` without any DEM core changes

---

## 4. Boundaries

### In Scope
- `RegulationsKnowledgeProvider` class implementing `KnowledgeProvider`
- JSON file reader for local regulation files
- Transform logic mapping file records → `query()` return shape
- Confidence scoring based on metadata rules
- `get_sources()` with versioning
- Registration in `KnowledgeProviderRegistry` via existing bootstrap
- Append-only semantics: the file is the single source of truth; the provider re-reads it on startup only. Updates require file replacement and application restart. No in-place mutation or incremental ingestion.
- Unit tests + integration tests
- Documentation update after implementation completion

### Explicit Out of Scope
- Database schema changes
- Knowledge Graph direct writes
- Memory integration
- Avatar integration
- LLM orchestration
- Research/Retrieval lifecycle
- External APIs or webhooks
- Frontend changes
- DEM core modifications
- Deduplication logic beyond registry overwrite rules
- Evidence verification or provenance tracking beyond basic `source_id`
- Rate limiting, PostgreSQL migration, or any infrastructure work beyond this provider
- CSV support (JSON only for this vertical slice)

---

## 5. Decisions (Final)

### Decision 1: Regulation File Format — JSON

**Chosen:** JSON array of objects.

**Justification:**
- Project already uses JSON extensively: `resources` table stores `metadata` as JSON string, `backend/uat_results.json` exists, Pydantic schemas are JSON-native
- Nested metadata (required by `KnowledgeProvider.query()` return shape) maps naturally to JSON without flattening
- Pydantic already handles JSON parsing/validation natively
- CSV would require manual type coercion and loses structural clarity for nested fields
- No existing CSV ingestion pattern in the codebase to follow

**Format contract:**
```json
[
  {
    "id": "reg-001",
    "title": "ETA Invoice Requirements",
    "description": "Invoices must include customer VAT number...",
    "regulation_type": "tax",
    "category": "invoicing",
    "country": "EG",
    "effective_date": "2025-01-01",
    "source_url": "https://example.com/eta-regs",
    "version": "1.0.0"
  }
]
```

### Decision 2: File Location — Configurable Setting with Default

**Chosen:** Add `REGULATIONS_FILE_PATH` to `backend/app/core/config.py` with default `backend/data/regulations.json`.

**Justification:**
- Consistent with project pattern: all external configuration is in `config.py` via Pydantic Settings (`SECRET_KEY`, `DATABASE_URL`, `ETA_CLIENT_ID`, etc.)
- `backend/data/` directory already exists (contains `nile_key.db`)
- Environment-overridable default follows existing convention
- No hardcoded paths in application code
- Default file may not exist at first run; provider handles missing file gracefully

**Setting definition:**
```python
REGULATIONS_FILE_PATH: str = "backend/data/regulations.json"
```

**Usage:** Provider receives path from `settings.REGULATIONS_FILE_PATH` at startup.

### Decision 3: Initial Data File — Test Fixture Created as Part of Task 1

**Chosen:** A test fixture file at `backend/tests/fixtures/regulations.json` created during Task 1 implementation. This is test/reference data only, not a production source.

**Justification:**
- No external data source exists in the repository; inventing one would be out of scope
- A fixture is sufficient to prove the contract end-to-end
- Fixture is explicitly labeled as test/reference data
- Production data ingestion is deferred to a future WP that would connect real sources

---

## 6. Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| `KnowledgeProvider` ABC | ✅ Existing | No changes |
| `KnowledgeProviderRegistry` | ✅ Existing | No changes |
| `CompanyKnowledgeProvider` | ✅ Existing | Reference implementation only |
| `KnowledgeGraphProvider` | ✅ Existing | Reference implementation only |
| `backend/main.py` bootstrap | ✅ Existing | Will add one `await registry.register(RegulationsKnowledgeProvider(...))` call |
| `backend/app/core/config.py` | ✅ Existing | Will add `REGULATIONS_FILE_PATH` setting |
| `backend/data/` directory | ✅ Existing | Default file location |
| Test fixture | ⚠️ Created in Task 1 | `backend/tests/fixtures/regulations.json` — test/reference data only |

**No blocking dependencies.**

---

## 7. Tasks (Ordered)

### Task 1: Define Regulation File Format and Create Test Fixture
- Finalize JSON schema as specified in Decision 1
- Create `backend/tests/fixtures/regulations.json` with 3–5 sample records covering:
  - Record with `source_url` (high confidence)
  - Record without `source_url` (medium confidence)
  - Record with missing `effective_date` (low confidence)
  - Record with different `regulation_type` and `country`
- Document format in WP-37 plan Section 4
- **Deliverable:** Fixture file + format spec

### Task 2: Implement `RegulationsKnowledgeProvider`
- **File:** `backend/app/agent/knowledge/regulations_provider.py` (new)
- Read JSON file from `settings.REGULATIONS_FILE_PATH`
- Transform each record to `query()` return shape:
  ```python
  {
      "id": str,
      "content": str,        # title + description
      "source_id": "regulations",
      "confidence": float,   # 0.0–1.0
      "metadata": {
          "regulation_type": str,
          "category": str,
          "country": str,
          "effective_date": str,
          "source_url": str,
          "version": str,
      }
  }
  ```
- Implement `get_sources()` returning:
  ```python
  {
      "id": "regulations",
      "name": "Regulations Knowledge",
      "type": "regulation",
      "version": "1.0.0",
      "updated_at": "<ISO-8601 UTC timestamp derived from the regulation file's last-modified time>"
  }
  ```
- Confidence rules (applied in order; the first matching rule wins):
  - 0.5 if `effective_date` is missing or empty
  - 0.85 if `source_url` is present
  - 0.75 if `source_url` is absent
- **Deliverable:** New provider class, no DEM core changes

### Task 3: Add Configuration Setting
- **File:** `backend/app/core/config.py` (modification)
- Add `REGULATIONS_FILE_PATH: str = "backend/data/regulations.json"`
- **Deliverable:** Setting available to provider and bootstrap; must complete before Task 4

### Task 4: Bootstrap Registration
- **File:** `backend/main.py` (modification)
- Add import and registration call in `lifespan()`:
  ```python
  from app.agent.knowledge.regulations_provider import RegulationsKnowledgeProvider
  # ...
  regulations_provider = RegulationsKnowledgeProvider(file_path=settings.REGULATIONS_FILE_PATH)
  await knowledge_provider_registry.register(regulations_provider)
  ```
- Wrap in try/except to match existing provider registration pattern
- **Deliverable:** Provider registered at startup, no other code changes

### Task 5: Unit Tests
- **File:** `backend/tests/agent/test_regulations_knowledge_provider.py` (new)
- Test cases:
  1. `get_sources()` returns expected structure with `id`, `name`, `type`, `version`, `updated_at`
  2. `query()` with matching query returns results with correct shape
  3. `query()` with no query returns all records up to `limit`
  4. `query()` returns empty list when no matches
  5. Confidence scores within 0.0–1.0 range
  6. `query()` handles missing file gracefully (returns empty results, no exception)
  7. `query()` handles malformed JSON gracefully (returns empty results, no exception)
  8. `get_sources()` raises `ValueError` if no sources found (contract requirement)
- **Deliverable:** 8+ passing unit tests

### Task 6: Integration Test
- **File:** `backend/tests/agent/test_regulations_knowledge_integration.py` (new)
- Test cases:
  1. Provider registers successfully in `KnowledgeProviderRegistry`
  2. Provider is queryable via `registry.query("regulations", "...")`
  3. `ReasoningEngine` can query the new provider through its registry without code changes
  4. Existing `CompanyKnowledgeProvider` and `KnowledgeGraphProvider` registration still works
- **Deliverable:** 4+ passing integration tests

### Task 7: Regression Verification
- Run full backend test suite: `pytest backend/tests/`
- Verify no existing tests break
- Verify no import cycles introduced
- **Deliverable:** Test report showing 0 regressions

### Task 8: Documentation
- Update `ENGINEERING_MEMORY.md` with WP-37 completion entry after all tests pass
- Update `CURRENT_STATUS.md` with WP-37 entry after closure
- **Deliverable:** Updated docs reflecting actual completion state

---

## 8. Files Expected to Be Modified or Created

| File | Action | Purpose |
|------|--------|---------|
| `backend/app/agent/knowledge/regulations_provider.py` | Create | New provider implementation |
| `backend/tests/agent/test_regulations_knowledge_provider.py` | Create | Unit tests |
| `backend/tests/agent/test_regulations_knowledge_integration.py` | Create | Integration tests |
| `backend/tests/fixtures/regulations.json` | Create | Test fixture (test/reference data only) |
| `backend/main.py` | Modify | Registration call in `lifespan()` |
| `backend/app/core/config.py` | Modify | Add `REGULATIONS_FILE_PATH` setting |
| `ENGINEERING_MEMORY.md` | Modify | Add WP-37 closure entry |
| `CURRENT_STATUS.md` | Modify | Add WP-37 entry after closure |

**No other files.** No DEM core, no routers, no schemas, no services, no database migrations.

---

## 9. Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| AC-37.1 | `RegulationsKnowledgeProvider` implements `KnowledgeProvider` interface | Type check + tests |
| AC-37.2 | `get_sources()` returns valid source metadata with `version` and `updated_at` | Unit test |
| AC-37.3 | `query()` returns results in contract shape: `results`, `confidence`, `sources` | Unit test |
| AC-37.4 | Confidence scores are within 0.0–1.0 | Unit test |
| AC-37.5 | Provider registers successfully in `KnowledgeProviderRegistry` | Integration test |
| AC-37.6 | Provider is queryable via registry without DEM core changes | Integration test |
| AC-37.7 | `ReasoningEngine` can query provider through existing registry | Integration test |
| AC-37.8 | All existing tests pass (no regressions) | Full pytest run |
| AC-37.9 | No DEM core files modified | Code review / git diff |
| AC-37.10 | No database schema changes | Code review / git diff |
| AC-37.11 | Documentation updated | Doc review |

---

## 10. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Regulation file format changes | Medium | Medium | Version files; provider reloads on startup only |
| Large file performance | Low | Low | Add `limit` parameter; file read is one-time at startup |
| Confidence scoring too simplistic | Low | Low | Start with rule-based; can enhance later without contract change |
| File not found at startup | Medium | Low | Graceful fallback to empty provider; log warning |

---

## 11. Governance Notes

- **LLM Master Roadmap discrepancy:** `.kilo/plans/1786063180198-master-roadmap-remaining-phases.md` lists "LLM Provider Integration" as "deferred", while `ENGINEERING_MEMORY.md` and git history confirm it is completed via WP-LLM-001. This document is out of date but is not addressed in WP-37 scope.
- **PLAN.md consistency:** This plan does not modify `PLAN.md`. WP-37 entry should be added only after Project Owner approval and implementation completion.

---

*Plan Status: Ready for Project Owner Approval*
