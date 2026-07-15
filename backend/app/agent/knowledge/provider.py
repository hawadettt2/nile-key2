from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List


class KnowledgeProvider(ABC):
    """Interface for Company Knowledge Layer."""

    @abstractmethod
    async def query(self, query: str, context: Optional[Dict[str, Any]] = None, sources: Optional[List[str]] = None, limit: int = 10) -> Dict[str, Any]:
        raise NotImplementedError("KnowledgeProvider.query() is not implemented in Phase 1.")

    @abstractmethod
    async def get_sources(self) -> List[Dict[str, Any]]:
        raise NotImplementedError("KnowledgeProvider.get_sources() is not implemented in Phase 1.")
