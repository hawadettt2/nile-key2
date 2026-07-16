from abc import ABC, abstractmethod
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class IntentContent(BaseModel):
    """Structured intent contract between Digital Export Manager and Avatar.

    The Digital Export Manager produces intents; the Avatar renders them.
    This contract guarantees the DEM never produces UI markup, audio streams,
    or avatar-specific data. The Avatar is free to render the same intent
    as text, voice, or embodied UI.
    """

    intent_type: str = Field(
        ...,
        description="Type of intent (e.g., 'mission_started', 'mission_completed', 'approval_required', 'error').",
    )
    content: Dict[str, Any] = Field(
        ...,
        description="Structured payload for the intent. Shape varies by intent_type.",
    )
    context: Dict[str, Any] = Field(
        ...,
        description="Execution context (session_id, mission_id, correlation_id, etc.).",
    )
    suggested_actions: List[str] = Field(
        ...,
        description="List of suggested follow-up actions for the user.",
    )


class AvatarRenderer(ABC):
    """Interface for Avatar presentation layer.

    An AvatarRenderer receives structured intents and renders them in a
    presentation-specific modality. The Digital Export Manager never knows
    or cares which renderer is active.
    """

    @abstractmethod
    async def render(self, intent_content: IntentContent) -> Dict[str, Any]:
        """Render an intent for end-user presentation.

        Args:
            intent_content: Structured intent produced by the Digital Export Manager.

        Returns:
            A presentation-specific payload. Shape is renderer-dependent.
            Common keys include:
                - modality: str — "text", "voice", "embodied"
                - payload: Any — renderer-specific representation
                - metadata: Dict[str, Any] — renderer-specific metadata
        """
        raise NotImplementedError("AvatarRenderer.render() is not implemented.")
