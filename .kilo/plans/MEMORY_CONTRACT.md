# Memory Contract

**Work Package:** WP-30G — Memory Interface Definition  
**Status:** Interface Definition Only — No Implementation  
**Date:** 2026-07-16  

---

## 1. Purpose

This document defines the contract between the Digital Export Manager and the Long-Term Memory interface (WP-31). It specifies how memory operations are performed without modifying the DEM core.

---

## 2. Principles

| Principle | Description |
|-----------|-------------|
| Not a general database | Memory is structured institutional memory, not a generic key-value store. |
| Graceful degradation | WP-30 must function without WP-31. When unavailable, DEM treats memory as empty. |
| Session-scoped | Memories are organized by session_id. Cross-session access is through explicit query. |
| Structured operations | Only four operations are exposed: recall, store, forget, summarize. |
| Importance-weighted | Memories carry an importance score (0-10) for prioritization. |

---

## 3. Provider Interface Contract

Every memory implementation must implement `MemoryProvider`:

```python
class MemoryProvider(ABC):
    @abstractmethod
    async def recall(
        self,
        session_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
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
        ...

    @abstractmethod
    async def forget(self, session_id: str, key: str) -> bool:
        ...

    @abstractmethod
    async def summarize(self, session_id: str) -> Dict[str, Any]:
        ...
```

**Return shape for `recall()`:**

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

**Return shape for `store()`:**

```python
str  # unique memory identifier
```

**Return shape for `forget()`:**

```python
bool  # True if removed, False if not found
```

**Return shape for `summarize()`:**

```python
{
    "summary": str,
    "memory_count": int,
    "key_themes": List[str],
}
```

---

## 4. Memory Types

| Type | Description | Examples |
|------|-------------|----------|
| `context` | General session context | Current workflow state, active entities |
| `preference` | User preferences | Preferred shipping provider, notification settings |
| `decision` | Past decisions | Chosen paths, approval grants |
| `standing_order` | Reusable instructions | "Always use DHL for EU shipments" |

---

## 5. Graceful Degradation Contract

When `MemoryProvider` is unavailable:

1. `recall()` returns empty list `[]`
2. `store()` returns empty string `""` or dummy ID
3. `forget()` returns `False`
4. `summarize()` returns empty dict `{}`

The DEM core must handle all four cases without raising exceptions.

---

## 6. Out of Scope for WP-30G

- Concrete memory provider implementations
- Database persistence for memory
- Memory ingestion pipelines
- Memory eviction or archival logic
- MemoryRegistry (no registry is defined for WP-30G)

---

## 7. References

- `.kilo/plans/wp30-implementation-plan.md` Phase 7 (Tasks 7.1–7.2)
- `.kilo/plans/1784079736812-wp30-architecture-compliance-review.md` Phase 7
- `backend/app/agent/memory/interface.py` — `MemoryProvider` ABC
- `backend/app/agent/schemas/agent_schemas.py` — Memory schemas
