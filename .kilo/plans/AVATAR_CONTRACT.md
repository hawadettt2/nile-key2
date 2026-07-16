# Avatar Contract

**Work Package:** WP-30H — Avatar Contract  
**Status:** Interface Definition Only — No Implementation  
**Date:** 2026-07-17  

---

## 1. Purpose

This document defines the contract between the Digital Export Manager and the Avatar presentation layer. It specifies how intents are structured and how renderers must behave without modifying the DEM core.

---

## 2. Principles

| Principle | Description |
|-----------|-------------|
| Structured intents only | The DEM produces `IntentContent` objects, never UI markup, HTML, audio streams, or avatar animation data. |
| Modality-agnostic | The same intent can be rendered as text, voice, or embodied UI. The DEM does not assume any specific modality. |
| Multiple avatars | Multiple AvatarRenderers may serve the same Digital Export Manager instance. |
| Presentation independence | The DEM core never imports or depends on any Avatar implementation. |
| No UI logic in WP-30 | Avatar UI implementation is explicitly out of scope for WP-30. |

---

## 3. IntentContent Contract

Every intent produced by the Digital Export Manager must conform to `IntentContent`:

```python
class IntentContent(BaseModel):
    intent_type: str
    content: Dict[str, Any]
    context: Dict[str, Any]
    suggested_actions: List[str]
```

**Field definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `intent_type` | `str` | Type of intent (e.g., `mission_started`, `mission_completed`, `approval_required`, `error`) |
| `content` | `Dict[str, Any]` | Structured payload for the intent. Shape varies by `intent_type`. |
| `context` | `Dict[str, Any]` | Execution context (`session_id`, `mission_id`, `correlation_id`, etc.) |
| `suggested_actions` | `List[str]` | List of suggested follow-up actions for the user |

**Example:**

```python
{
    "intent_type": "mission_completed",
    "content": {
        "mission_id": "abc-123",
        "result": {"shipment_id": 42, "tracking_number": "DHL-123"},
    },
    "context": {
        "session_id": "session-456",
        "correlation_id": "corr-789",
    },
    "suggested_actions": ["view_shipment", "create_another"],
}
```

---

## 4. AvatarRenderer Contract

Every avatar implementation must implement `AvatarRenderer`:

```python
class AvatarRenderer(ABC):
    @abstractmethod
    async def render(self, intent_content: IntentContent) -> Dict[str, Any]:
        ...
```

**Return shape:**

```python
{
    "modality": str,        # "text", "voice", "embodied"
    "payload": Any,         # renderer-specific representation
    "metadata": Dict[str, Any],  # renderer-specific metadata
}
```

**Responsibilities:**
- Accept `IntentContent` from the DEM
- Render it in a presentation-specific modality
- Never modify the `IntentContent`
- Never call back into the DEM core

**Boundaries:**
- The DEM never calls `render()` directly
- The DEM never imports any `AvatarRenderer` implementation
- A separate presentation layer or gateway invokes `render()`

---

## 5. DEM Core Responsibilities

The Digital Export Manager must:

1. Produce `IntentContent` objects for all user-facing events
2. Never produce UI markup, HTML, Markdown, audio streams, or avatar animation data
3. Never assume a specific avatar modality
4. Never import `AvatarRenderer` or any avatar-specific package
5. Continue operation when no avatar is configured (graceful degradation)

---

## 6. Graceful Degradation

When no AvatarRenderer is configured:
- The DEM still produces `IntentContent` objects
- Presentation layer may discard or log intents
- No exceptions are raised
- DEM core operation is unaffected

---

## 7. Out of Scope for WP-30H

- Concrete AvatarRenderer implementations
- Text rendering logic
- Voice rendering logic
- Embodied UI rendering logic
- HTML/Markdown generation
- Audio/video streaming
- WebSocket logic
- Frontend code
- CSS/JavaScript
- Avatar registry

---

## 8. References

- `.kilo/plans/wp30-implementation-plan.md` Phase 8 (Tasks 8.1–8.3)
- `.kilo/plans/1784079736812-wp30-architecture-compliance-review.md` Phase 8
- `backend/app/agent/avatar/interface.py` — `IntentContent` and `AvatarRenderer`
- `backend/app/routers/digital_export_manager.py` — DEM router produces structured responses only
