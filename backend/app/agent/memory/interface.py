from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime


class MemoryProvider(ABC):
    """Interface for Long-Term Memory (WP-31)."""

    @abstractmethod
    async def recall(self, session_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError("MemoryProvider.recall() is not implemented in Phase 1.")

    @abstractmethod
    async def store(self, session_id: str, key: str, value: Any, memory_type: str = "context", importance: int = 5, expires_at: Optional[datetime] = None) -> str:
        raise NotImplementedError("MemoryProvider.store() is not implemented in Phase 1.")

    @abstractmethod
    async def forget(self, session_id: str, key: str) -> bool:
        raise NotImplementedError("MemoryProvider.forget() is not implemented in Phase 1.")

    @abstractmethod
    async def summarize(self, session_id: str) -> Dict[str, Any]:
        raise NotImplementedError("MemoryProvider.summarize() is not implemented in Phase 1.")
