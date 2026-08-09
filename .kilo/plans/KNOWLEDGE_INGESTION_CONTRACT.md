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

## 3.1 Knowledge Ingestion — Definition and Boundaries

**Knowledge Ingestion** is the capability to receive, import, transform, and register knowledge and data from external systems into the Company Knowledge Layer.

### In Scope — Knowledge Ingestion Responsibilities

- Reading raw knowledge items from external systems (document stores, regulations databases, file imports, APIs).
- Transforming items into the `KnowledgeProvider.query()` return shape.
- Assigning metadata and versioning information.
- Registering providers via `KnowledgeProviderRegistry.register()`.
- Supporting append-only updates and version tracking.
- Ensuring zero changes to DEM core logic; only provider implementations change.

### Out of Scope — Explicit Boundaries

The following capabilities are **NOT** part of Knowledge Ingestion:

- **External Research:** Active searching, querying, or retrieving information from external sources on demand.
- **Business Analysis:** Interpreting, analyzing, or drawing conclusions from ingested knowledge.
- **Plan Generation:** Converting knowledge into executable plans or strategies.
- **Execution:** Running or orchestrating any business process.
- **Reasoning:** Deriving new insights or decisions from knowledge.
- **LLM Orchestration:** Using language models to generate, summarize, or enhance knowledge content.
- **Evidence Verification:** Validating the accuracy, authenticity, or trustworthiness of external sources.
- **Source Provenance Tracking:** Maintaining audit trails of where information originated beyond basic `source_id`.
- **Knowledge Quality Scoring:** Advanced algorithms for confidence scoring beyond basic metadata.
- **Deduplication:** Advanced duplicate detection beyond registry overwrite rules.

These capabilities must be implemented as separate concerns, potentially as future work packages, and must not be introduced into the Ingestion contract.

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
3. Assign metadata and versioning information.
4. Register the provider via `KnowledgeProviderRegistry.register()`.
5. Never mutate the DEM core; only the provider implementation changes.

**Boundary reminder:** The ingestion pipeline is limited to import, transform, and registration. It does not include external research, business analysis, plan generation, execution, reasoning, LLM orchestration, evidence verification, source provenance tracking, knowledge quality scoring, or deduplication. See Section 3.1 for the full boundary definition.

---

## 6. Versioning

| Artifact | Versioning Rule |
|----------|-----------------|
| `KnowledgeProvider` interface | SemVer on the interface file when method signatures change |
| Provider implementation | Independent SemVer per source |
| Source content | `version` field in `get_sources()` return value |

---

## 7. Out of Scope for WP-30F

The following are explicitly out of scope for this contract and must not be introduced into the Knowledge Ingestion capability:

- Concrete knowledge source implementations
- Ingestion pipeline implementation
- Database persistence for knowledge items
- Confidence scoring algorithms
- Source deprecation or archival logic
- **External Research** — active searching or querying external sources on demand
- **Business Analysis** — interpreting or analyzing ingested knowledge
- **Plan Generation** — converting knowledge into executable plans
- **Execution** — running or orchestrating business processes
- **Reasoning** — deriving new insights or decisions from knowledge
- **LLM Orchestration** — using language models to generate or enhance knowledge content
- **Evidence Verification** — validating accuracy or authenticity of sources
- **Source Provenance Tracking** — maintaining detailed audit trails beyond basic `source_id`
- **Knowledge Quality Scoring** — advanced algorithms beyond basic metadata
- **Deduplication** — advanced duplicate detection beyond registry overwrite rules

These capabilities may be addressed in future work packages as separate concerns.

---

## 8. References

- `.kilo/plans/wp30-implementation-plan.md` Phase 6 (Tasks 6.1–6.4)
- `.kilo/plans/1784079736812-wp30-architecture-compliance-review.md` Phase 6
- `.kilo/plans/ED-WP30-002.md` — WP-30F scope clarification
- `PLAN.md` Section 22.3 — Deferred / Future items
- `CURRENT_STATUS.md` — WP-30F implementation summary

---

## 9. Architectural Decision Record

**Decision:** Knowledge Ingestion is bounded to import, transform, and registration only.

**Rationale:** The project vision is an Intelligent Operating Platform where the Digital Export Manager acts as an Executive Intelligence Layer. Knowledge Ingestion provides the data foundation, but active reasoning, external research, business analysis, and execution are separate capabilities that must not be conflated with data import.

**Implications:**
- Future work packages must respect these boundaries.
- External Research, Evidence Verification, and Business Analysis are separate future capabilities.
- The Knowledge Ingestion contract does not preclude future expansion; it defines the minimum viable boundary for the current phase.

---
