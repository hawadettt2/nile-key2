from typing import Any, Dict, List, Optional

from app.agent.memory.interface import MemoryProvider


async def recall_cross_session(
    memory_provider: Optional[MemoryProvider],
    user_id: int,
    current_session_id: str,
    query: str = "cross_session_context",
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """Recall memories from previous sessions for the same user with isolation."""
    if memory_provider is None:
        return []

    try:
        if hasattr(memory_provider, "recall"):
            try:
                memories = await memory_provider.recall(
                    user_id=user_id,
                    session_id=current_session_id,
                    query=query,
                    limit=limit,
                    cross_session=True,
                )
            except TypeError:
                memories = await memory_provider.recall(
                    user_id=user_id,
                    session_id=current_session_id,
                    query=query,
                    limit=limit,
                )
        else:
            memories = []
        return memories or []
    except Exception:
        return []


async def store_cross_system(
    memory_provider: Optional[MemoryProvider],
    user_id: int,
    session_id: str,
    system_name: str,
    key: str,
    value: Any,
    memory_type: str = "cross_system",
    importance: int = 5,
    expires_at: Optional[Any] = None,
) -> str:
    """Store a memory item with cross-system scope."""
    if memory_provider is None:
        return ""

    scoped_key = f"{system_name}:{key}"
    try:
        return await memory_provider.store(
            user_id=user_id,
            session_id=session_id,
            key=scoped_key,
            value=value,
            memory_type=memory_type,
            importance=importance,
            expires_at=expires_at,
        )
    except Exception:
        return ""


async def recall_cross_system(
    memory_provider: Optional[MemoryProvider],
    user_id: int,
    session_id: str,
    system_name: str,
    query: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Recall memories from a specific system scope for the same user/session."""
    if memory_provider is None:
        return []

    scoped_query = f"{system_name}:{query}"
    try:
        memories = await memory_provider.recall(
            user_id=user_id,
            session_id=session_id,
            query=scoped_query,
            limit=limit,
        )
        return memories or []
    except Exception:
        return []


async def store_cross_component(
    memory_provider: Optional[MemoryProvider],
    user_id: int,
    session_id: str,
    component_name: str,
    key: str,
    value: Any,
    memory_type: str = "cross_component",
    importance: int = 5,
    expires_at: Optional[Any] = None,
) -> str:
    """Store a memory item with cross-component scope."""
    if memory_provider is None:
        return ""

    scoped_key = f"{component_name}:{key}"
    try:
        return await memory_provider.store(
            user_id=user_id,
            session_id=session_id,
            key=scoped_key,
            value=value,
            memory_type=memory_type,
            importance=importance,
            expires_at=expires_at,
        )
    except Exception:
        return ""


async def recall_cross_component(
    memory_provider: Optional[MemoryProvider],
    user_id: int,
    session_id: str,
    component_name: str,
    query: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Recall memories from a specific component scope for the same user/session."""
    if memory_provider is None:
        return []

    scoped_query = f"{component_name}:{query}"
    try:
        memories = await memory_provider.recall(
            user_id=user_id,
            session_id=session_id,
            query=scoped_query,
            limit=limit,
        )
        return memories or []
    except Exception:
        return []
