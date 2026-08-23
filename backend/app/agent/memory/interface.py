from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime


class MemoryProvider(ABC):
    """Interface for Long-Term Memory (WP-31).

    The Digital Export Manager uses memory to maintain context across sessions
    and personnel turnover. Memory is **not** a general database. It is a
    structured institutional memory.

    WP-30 must function without WP-31 (graceful degradation). When a
    MemoryProvider is unavailable, the DEM core treats it as an empty memory
    store and continues operation.
    """

    @abstractmethod
    async def recall(
        self,
        user_id: int,
        session_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Recall memories matching a query.

        Args:
            user_id: The user identifier.
            session_id: The session identifier.
            query: The memory query string (e.g., "standing_orders",
                "user_preferences", "historical_decisions").
            limit: Maximum number of memories to return.

        Returns:
            List of memory dicts. Each dict must contain at least:
                - key: str — memory identifier.
                - value: Any — stored memory value.
                - memory_type: str — type of memory.
                - importance: int — importance score (0-10).
                - created_at: str — ISO-8601 timestamp.
                - updated_at: str — ISO-8601 timestamp.
        """
        raise NotImplementedError("MemoryProvider.recall() is not implemented.")

    @abstractmethod
    async def store(
        self,
        user_id: int,
        session_id: str,
        key: str,
        value: Any,
        memory_type: str = "context",
        importance: int = 5,
        expires_at: Optional[datetime] = None,
    ) -> str:
        """Store a memory item.

        Args:
            user_id: The user identifier.
            session_id: The session identifier.
            key: Memory key/identifier.
            value: Memory value to store.
            memory_type: Type of memory (e.g., "context", "preference",
                "decision", "standing_order").
            importance: Importance score (0-10).
            expires_at: Optional expiration timestamp.

        Returns:
            str — unique memory identifier.
        """
        raise NotImplementedError("MemoryProvider.store() is not implemented.")

    @abstractmethod
    async def forget(self, user_id: int, session_id: str, key: str) -> bool:
        """Remove a memory item.

        Args:
            user_id: The user identifier.
            session_id: The session identifier.
            key: Memory key to remove.

        Returns:
            bool — True if the memory was removed, False if it did not exist.
        """
        raise NotImplementedError("MemoryProvider.forget() is not implemented.")

    @abstractmethod
    async def summarize(self, user_id: int, session_id: str) -> Dict[str, Any]:
        """Produce a summary of memories for a session.

        Args:
            user_id: The user identifier.
            session_id: The session identifier.

        Returns:
            Dict with keys:
                - summary: str — human-readable summary.
                - memory_count: int — number of memories.
                - key_themes: List[str] — extracted themes/topics.
        """
        raise NotImplementedError("MemoryProvider.summarize() is not implemented.")

    @abstractmethod
    async def cleanup_expired(self, user_id: Optional[int] = None) -> int:
        """Remove expired memory items.

        Args:
            user_id: Optional user identifier. If provided, only clean up
                memories for this user. If None, clean up all expired memories.

        Returns:
            int — number of deleted records.
        """
        raise NotImplementedError("MemoryProvider.cleanup_expired() is not implemented.")
