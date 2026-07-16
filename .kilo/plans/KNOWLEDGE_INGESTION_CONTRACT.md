# Knowledge Ingestion Contract

**Work Package:** WP-30F — Company Knowledge Layer Interface  
**Status:** Interface Definition Only — No Implementation  
**Date:** 2026-07-16  

---

## 1. Purpose

This document defines the contract between the Company Knowledge Layer and external ingestion pipelines. It specifies how knowledge sources are registered, updated, and removed without modifying the Digital Export Manager core.

---

## 2. Principles

| Principle | Description |
|-----------|-------------|
| Read-only from DEM | The Digital Export Manager queries knowledge; it never mutates it directly. |
| Append-optimized | Ingestion is append-only. Updates create new versions; old versions remain queryable until explicitly deprecated. |
| Zero core changes | Adding a new knowledge source requires implementing `KnowledgeProvider` and registering it. No DEM core logic changes. |
| Source-scoped | Each knowledge item belongs to a named source. Sources are registered via `KnowledgeProviderRegistry`. |
| Confidence-scored | Every query result includes a confidence score (0.0–1.0). |

---

## 3. Provider Interface Contract

Every knowledge source must implement `KnowledgeProvider`:

```python
class KnowledgeProvider(ABC):
    @abstractmethod
    async def query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        sources: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        ...

    @abstractmethod
    async def get_sources(self) -> List[Dict[str, Any]]:
        ...
```

**Return shape for `query()`:**

```python
{
    "results": [
        {
            "id": str,
            "content": str,
            "source_id": str,
            "confidence": float,
            "metadata": Dict[str, Any],
        }
    ],
    "confidence": float,  # average across results
    "sources": [str],     # source IDs that contributed
}
```

**Return shape for `get_sources()`:**

```python
[
    {
        "id": str,          # unique source identifier (used as registry key)
        "name": str,        # human-readable name
        "type": str,        # e.g., "regulation", "procedure", "faq"
        "version": str,     # SemVer of source content
        "updated_at": str,  # ISO-8601 timestamp of last ingestion
    }
]
```

---

## 4. Registration Contract

```python
registry = KnowledgeProviderRegistry()
provider = MyKnowledgeProvider()  # implements KnowledgeProvider
registry.register(provider)
```

**Registration rules:**
- A provider must expose at least one source via `get_sources()`.
- Each source must have a unique `id`.
- Registering a provider with an existing source `id` overwrites the previous entry.

---

## 5. Ingestion Pipeline Contract (Future)

An ingestion pipeline is **out of scope for WP-30F**. When implemented in a future work package, it must:

1. Read raw knowledge items from an external system (document store, regulations DB, etc.).
2. Transform items into the `query()` return shape.
3. Assign confidence scores based on source authority and freshness.
4. Register the provider via `KnowledgeProviderRegistry.register()`.
5. Never mutate the DEM core; only the provider implementation changes.

---

## 6. Versioning

| Artifact | Versioning Rule |
|----------|-----------------|
| `KnowledgeProvider` interface | SemVer on the interface file when method signatures change |
| Provider implementation | Independent SemVer per source |
| Source content | `version` field in `get_sources()` return value |

---

## 7. Out of Scope for WP-30F

- Concrete knowledge source implementations
- Ingestion pipeline implementation
- Database persistence for knowledge items
- Confidence scoring algorithms
- Source deprecation or archival logic

---

## 8. References

- `.kilo/plans/wp30-implementation-plan.md` Phase 6 (Tasks 6.1–6.4)
- `.kilo/plans/1784079736812-wp30-architecture-compliance-review.md` Phase 6
- `.kilo/plans/ED-WP30-002.md` — WP-30F scope clarification
