# WP-31 — AI Memory: Implementation Plan

**Reference:** PLAN.md (Master Roadmap v2.1)  
**Architecture:** `.kilo/plans/1784089363000-wp30-digital-export-manager-architecture.md`  
**Memory Contract:** `.kilo/plans/MEMORY_CONTRACT.md`  
**WP-30G Interface:** `backend/app/agent/memory/interface.py`  
**Phase:** 2 — Intelligent Platform  
**Status:** Completed — All tasks implemented and verified  
**Date:** 2026-07-18

---

## 1. Executive Summary

WP-31 implements the **Long-Term Memory** bounded context for the Digital Export Manager (DEM). It is the persistent memory substrate that survives across sessions, deployments, and employee turnover.

WP-30 defines the `MemoryProvider` interface with four operations: `recall`, `store`, `forget`, `summarize`. WP-31 provides the concrete implementation of this interface against persistent storage.

**Core principle:** Memory is structured institutional memory, not a generic database. The DEM reads from WP-31 to recall past decisions, preferences, context, and institutional knowledge. The DEM writes to WP-31 after significant interactions, decisions, and learned patterns.

---

## 2. Architectural Alignment

This implementation plan derives from the approved Intelligent Operating Platform architecture:

```
Human Employees
        │
        ▼
Digital Export Manager (Executive Intelligence)
        │
        ▼
Core Modules: (Reasoning Engine | Company Knowledge | Long-Term Memory)
        │
        ▼
    Task Planner
        │
        ▼
  Execution Planner
        │
        ▼
  Tool Orchestrator
        │
        ▼
  ERP Services & Database
```

**Confirmed properties:**
- DEM is the root bounded context.
- Long-Term Memory (WP-31) is a **separate bounded context** with its own data model, lifecycle, and ownership.
- WP-31 exposes only memory-specific operations: `recall`, `store`, `forget`, `summarize`.
- WP-30 never treats WP-31 as a generic database.
- WP-31 must survive across sessions, deployments, and employee turnover.
- WP-30 must function without WP-31 (graceful degradation), but WP-31 must not function without WP-30 as its sole authorized writer.

---

## 3. Scope

### In Scope
- Implement `MemoryProvider` interface against persistent storage (SQLite)
- Memory types: `context`, `preference`, `decision`, `standing_order`
- Importance-weighted memory (0-10)
- Session-scoped memory organization
- Cross-session memory query via explicit `recall()`
- Memory expiration via `expires_at`
- Graceful degradation when memory is unavailable
- Memory summarization via `summarize()`

### Out of Scope
- Knowledge ingestion pipelines (deferred to future WP)
- LLM-powered memory reasoning (out of scope)
- Memory eviction or archival logic beyond `expires_at`
- Generic key-value database operations
- Memory registry or provider discovery (single implementation in WP-31)

---

## 4. Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| WP-30G (Memory Interface Definition) | Must be complete | ✅ Completed per PLAN.md L245 |
| WP-30I (Advanced Features) | Must be complete | ✅ Completed per PLAN.md L247 |
| WP-30 (Digital Export Manager) | Must be complete | ✅ Completed per PLAN.md L240-247 |
| WP-32 (Knowledge Graph) | Must NOT start before WP-31 | WP-32 is listed after WP-31 in PLAN.md L249 |
| WP-33 (Trade Intelligence) | Must NOT start before WP-31 | WP-33 is listed after WP-31 in PLAN.md L250 |

---

## 5. Memory Provider Interface

The `MemoryProvider` interface is already defined in `backend/app/agent/memory/interface.py` from WP-30G. WP-31 implements this interface.

### 5.1 Interface Contract

```python
class MemoryProvider(ABC):
    @abstractmethod
    async def recall(
        self,
        session_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Recall memories matching a query."""
        ...

    @abstractmethod
    async def store(
        self,
        session_id: str,
        key: str,
        value: Any,
        memory_type: str = "context",
        importance: int = 5,
        expires_at: Optional[datetime] = None,
    ) -> str:
        """Store a memory item."""
        ...

    @abstractmethod
    async def forget(
        self,
        session_id: str,
        key: str,
    ) -> bool:
        """Remove a memory item."""
        ...

    @abstractmethod
    async def summarize(
        self,
        session_id: str,
    ) -> Dict[str, Any]:
        """Produce a summary of memories for a session."""
        ...
```

### 5.2 Return Shapes

**`recall()` return shape:**
```python
[
    {
        "key": str,
        "value": Any,
        "memory_type": str,
        "importance": int,
        "created_at": str,  # ISO-8601
        "updated_at": str,  # ISO-8601
    }
]
```

**`store()` return shape:**
```python
str  # unique memory identifier
```

**`forget()` return shape:**
```python
bool  # True if removed, False if not found
```

**`summarize()` return shape:**
```python
{
    "summary": str,
    "memory_count": int,
    "key_themes": List[str],
}
```

---

## 6. Memory Types

| Type | Description | Examples |
|------|-------------|----------|
| `context` | General session context | Current workflow state, active entities |
| `preference` | User preferences | Preferred shipping provider, notification settings |
| `decision` | Past decisions | Chosen paths, approval grants |
| `standing_order` | Reusable instructions | "Always use DHL for EU shipments" |

---

## 7. Graceful Degradation Contract

When `MemoryProvider` is unavailable:

1. `recall()` returns empty list `[]`
2. `store()` returns empty string `""` or dummy ID
3. `forget()` returns `False`
4. `summarize()` returns empty dict `{}`

The DEM core must handle all four cases without raising exceptions.

---

## 8. Implementation Tasks

### Phase 1: Memory Storage Implementation (WP-31A)

**Goal:** Implement persistent memory storage with SQLite backend.

| Task | Description |
|------|-------------|
| 8.1 | Create `SQLiteMemoryProvider` implementing `MemoryProvider` interface |
| 8.2 | Implement `store()` with importance weighting and expiration support |
| 8.3 | Implement `recall()` with query matching and limit |
| 8.4 | Implement `forget()` with session-scoped key removal |
| 8.5 | Implement `summarize()` with theme extraction |
| 8.6 | Create `agent_memory` table schema with indexes for performance |
| 8.7 | Add memory cleanup job for expired entries |

### Phase 2: Integration with DEM Core (WP-31B)

**Goal:** Integrate memory provider into DEM core with graceful degradation.

| Task | Description |
|------|-------------|
| 9.1 | Update DEM core to use `MemoryProvider` interface instead of direct DB access |
| 9.2 | Implement memory injection into session context at session start |
| 9.3 | Implement memory persistence after significant interactions |
| 9.4 | Implement memory recall during decision-making |
| 9.5 | Add graceful degradation: empty memory store when provider unavailable |
| 9.6 | Update `SessionContext` to include memory references |

### Phase 3: Testing & Validation (WP-31C)

**Goal:** Ensure memory operations are reliable and performant.

| Task | Description |
|------|-------------|
| 10.1 | Unit tests for `SQLiteMemoryProvider` (all 4 operations) |
| 10.2 | Integration tests for memory persistence across sessions |
| 10.3 | Integration tests for graceful degradation |
| 10.4 | Performance tests for memory recall with large datasets |
| 10.5 | Security tests: memory isolation between users/sessions |

---

## 9. Database Schema

### `agent_memory` table (extend existing from WP-30G)

```sql
CREATE TABLE IF NOT EXISTS agent_memory (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT,
    memory_type TEXT DEFAULT 'context',
    importance INTEGER DEFAULT 5,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_memory_session_id ON agent_memory(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_memory_type ON agent_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_agent_memory_importance ON agent_memory(importance);
CREATE INDEX IF NOT EXISTS idx_agent_memory_expires_at ON agent_memory(expires_at);
```

---

## 10. Acceptance Criteria

| ID | Criterion | Verification Method |
|----|-----------|---------------------|
| AC-31.1 | `recall()` returns matching memories within limit | Unit test |
| AC-31.2 | `store()` persists memory with correct metadata | Unit + integration test |
| AC-31.3 | `forget()` removes memory by key within session | Unit test |
| AC-31.4 | `summarize()` returns valid summary with themes | Unit test |
| AC-31.5 | Memory persists across sessions | Integration test |
| AC-31.6 | Memory expires after `expires_at` | Integration test |
| AC-31.7 | Graceful degradation: DEM functions without memory provider | Integration test |
| AC-31.8 | Memory isolated between users/sessions | Security test |
| AC-31.9 | Importance weighting affects recall ordering | Unit test |
| AC-31.10 | No memory provider implementation in WP-30G | Code review |

---

## 11. What Must NOT Happen

1. **Do not** treat WP-31 as a generic database — it is structured institutional memory only
2. **Do not** implement memory ingestion pipelines in WP-31
3. **Do not** add LLM-powered reasoning to memory operations
4. **Do not** expose memory internals to the public API
5. **Do not** allow cross-session memory access without explicit `recall()` query
6. **Do not** implement memory registry or provider discovery (single implementation)
7. **Do not** modify the `MemoryProvider` interface defined in WP-30G
8. **Do not** implement memory eviction logic beyond `expires_at`

---

## 12. Security & Compliance

| Aspect | Requirement |
|--------|-------------|
| Data isolation | Memories are scoped to `session_id`; no cross-user leakage |
| Authorization | Only the DEM core writes to memory; no direct user access |
| Encryption | Sensitive memory values should be encrypted at rest (future enhancement) |
| Audit | All memory operations are logged via existing audit framework |
| Retention | `expires_at` enforces automatic cleanup of stale memories |

---

## 13. Out of Scope for WP-31

- Memory encryption at rest
- Memory sharing between organizations
- Memory backup/restore mechanisms
- Memory analytics dashboard
- Memory import/export
- LLM-powered memory summarization
- Memory recommendation engine

---

## 14. References

- `PLAN.md` Section 8.1 — Work Packages status
- `PLAN.md` Section 16.3 — Phase 2 exit criteria
- `.kilo/plans/1784089363000-wp30-digital-export-manager-architecture.md` Section 5 — WP-31 relationship
- `.kilo/plans/MEMORY_CONTRACT.md` — Memory interface contract
- `.kilo/plans/wp30-implementation-plan.md` Phase 7 — WP-30G Memory Interface Definition
- `backend/app/agent/memory/interface.py` — `MemoryProvider` ABC

---

## 15. Document Authority

This document defines the implementation plan for WP-31.

All implementation tasks, technical designs, and code changes for WP-31 MUST derive from this document and the referenced architecture documents.

Any deviation requires a documented architectural decision recorded in the Architectural Decision Log (PLAN.md Section 13) with explicit rationale.

**Status:** Planned — implementation begins after WP-30I closure.
