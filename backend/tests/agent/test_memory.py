import pytest
from unittest.mock import AsyncMock
from datetime import datetime, timezone

from app.agent.memory.interface import MemoryProvider
from app.agent.schemas.agent_schemas import (
    AgentMemoryRequest,
    AgentMemoryResponse,
    AgentMemoryRecallRequest,
    AgentMemoryRecallResponse,
)


class ConcreteMemoryProvider(MemoryProvider):
    """Concrete implementation for testing."""

    async def recall(self, session_id, query, limit=10):
        return [
            {
                "key": "test-memory",
                "value": {"preferred_path": "shipping"},
                "memory_type": "preference",
                "importance": 8,
                "created_at": "2026-07-16T00:00:00Z",
                "updated_at": "2026-07-16T00:00:00Z",
            }
        ]

    async def store(self, session_id, key, value, memory_type="context", importance=5, expires_at=None):
        return "memory-123"

    async def forget(self, session_id, key):
        return True

    async def summarize(self, session_id):
        return {
            "summary": "User prefers shipping via DHL",
            "memory_count": 1,
            "key_themes": ["shipping", "preferences"],
        }


class TestMemoryProviderInterface:
    """Verify MemoryProvider interface contract."""

    def test_interface_is_abstract(self):
        with pytest.raises(TypeError):
            MemoryProvider()

    @pytest.mark.asyncio
    async def test_concrete_provider_implements_recall(self):
        provider = ConcreteMemoryProvider()
        result = await provider.recall("session-123", "preferences", limit=5)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["key"] == "test-memory"

    @pytest.mark.asyncio
    async def test_concrete_provider_implements_store(self):
        provider = ConcreteMemoryProvider()
        memory_id = await provider.store(
            "session-123",
            "preference:shipping",
            {"provider": "DHL"},
            memory_type="preference",
            importance=8,
        )
        assert memory_id == "memory-123"

    @pytest.mark.asyncio
    async def test_concrete_provider_implements_forget(self):
        provider = ConcreteMemoryProvider()
        result = await provider.forget("session-123", "test-memory")
        assert result is True

    @pytest.mark.asyncio
    async def test_concrete_provider_implements_summarize(self):
        provider = ConcreteMemoryProvider()
        result = await provider.summarize("session-123")
        assert "summary" in result
        assert "memory_count" in result
        assert "key_themes" in result
        assert result["memory_count"] == 1


class TestMemorySchemas:
    """Verify memory-related schemas."""

    def test_memory_request_defaults(self):
        request = AgentMemoryRequest(key="test", value={"a": 1})
        assert request.key == "test"
        assert request.value == {"a": 1}
        assert request.memory_type == "context"
        assert request.importance == 5
        assert request.expires_at is None

    def test_memory_request_with_all_fields(self):
        expires = datetime.now(timezone.utc)
        request = AgentMemoryRequest(
            key="test",
            value={"a": 1},
            memory_type="preference",
            importance=8,
            expires_at=expires,
        )
        assert request.memory_type == "preference"
        assert request.importance == 8
        assert request.expires_at == expires

    def test_memory_response(self):
        now = datetime.now(timezone.utc)
        response = AgentMemoryResponse(
            memory_id="mem-123",
            key="test",
            value={"a": 1},
            memory_type="context",
            importance=5,
            created_at=now,
            updated_at=now,
        )
        assert response.memory_id == "mem-123"
        assert response.key == "test"
        assert response.memory_type == "context"

    def test_memory_recall_request_defaults(self):
        request = AgentMemoryRecallRequest(session_id="session-123", query="preferences")
        assert request.session_id == "session-123"
        assert request.query == "preferences"
        assert request.limit == 10

    def test_memory_recall_request_custom_limit(self):
        request = AgentMemoryRecallRequest(
            session_id="session-123", query="preferences", limit=20
        )
        assert request.limit == 20

    def test_memory_recall_response(self):
        response = AgentMemoryRecallResponse(
            memories=[],
            total=0,
        )
        assert response.total == 0
        assert response.memories == []

    def test_memory_recall_response_with_memories(self):
        now = datetime.now(timezone.utc)
        memories = [
            AgentMemoryResponse(
                memory_id="mem-1",
                key="test",
                value={"a": 1},
                memory_type="context",
                importance=5,
                created_at=now,
                updated_at=now,
            )
        ]
        response = AgentMemoryRecallResponse(memories=memories, total=1)
        assert response.total == 1
        assert len(response.memories) == 1
