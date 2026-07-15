from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel


class IntentContent(BaseModel):
    intent_type: str
    content: Dict[str, Any]
    context: Dict[str, Any]
    suggested_actions: List[str]


class AvatarRenderer(ABC):
    """Interface for Avatar presentation layer."""

    @abstractmethod
    async def render(self, intent_content: IntentContent) -> Dict[str, Any]:
        raise NotImplementedError("AvatarRenderer.render() is not implemented in Phase 1.")
