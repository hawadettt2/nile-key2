import json
import os
import sqlite3
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from app.agent.memory.sqlite_provider import SQLiteMemoryProvider


@pytest.fixture
def db_path(tmp_path):
    """Create a temporary database path for each test."""
    db_file = tmp_path / "test_memory.db"
    return str(db_file)


@pytest.fixture
def provider(db_path):
    """Create a SQLiteMemoryProvider with the temporary database."""
    return SQLiteMemoryProvider(db_path=db_path)


@pytest.mark.asyncio
async def test_store_returns_uuid(provider):
    memory_id = await provider.store(
        session_id="session-123",
        key="preference:shipping",
        value={"provider": "DHL"},
        memory_type="preference",
        importance=8,
    )
    assert isinstance(memory_id, str)
    assert len(memory_id) > 0


@pytest.mark.asyncio
async def test_recall_returns_stored_memory(provider):
    await provider.store(
        session_id="session-123",
        key="preference:shipping",
        value={"provider": "DHL"},
        memory_type="preference",
        importance=8,
    )
    await provider.store(
        session_id="session-123",
        key="decision:provider",
        value={"chosen": "DHL"},
        memory_type="decision",
        importance=5,
    )

    results = await provider.recall("session-123", "shipping", limit=10)
    assert len(results) == 1
    assert results[0]["key"] == "preference:shipping"
    assert results[0]["importance"] == 8
    assert results[0]["memory_type"] == "preference"
    assert isinstance(results[0]["value"], dict)
    assert results[0]["value"]["provider"] == "DHL"


@pytest.mark.asyncio
async def test_recall_orders_by_importance_desc(provider):
    await provider.store(
        session_id="session-123",
        key="low",
        value="low importance",
        memory_type="context",
        importance=2,
    )
    await provider.store(
        session_id="session-123",
        key="high",
        value="high importance",
        memory_type="context",
        importance=9,
    )
    await provider.store(
        session_id="session-123",
        key="medium",
        value="medium importance",
        memory_type="context",
        importance=5,
    )

    results = await provider.recall("session-123", "importance", limit=10)
    assert len(results) == 3
    assert results[0]["importance"] == 9
    assert results[1]["importance"] == 5
    assert results[2]["importance"] == 2


@pytest.mark.asyncio
async def test_recall_respects_limit(provider):
    for i in range(5):
        await provider.store(
            session_id="session-123",
            key=f"item-{i}",
            value=f"value-{i}",
            memory_type="context",
            importance=i,
        )

    results = await provider.recall("session-123", "item", limit=2)
    assert len(results) == 2


@pytest.mark.asyncio
async def test_forget_removes_memory(provider):
    await provider.store(
        session_id="session-123",
        key="temp:memory",
        value={"data": "to-delete"},
        memory_type="context",
        importance=5,
    )

    deleted = await provider.forget("session-123", "temp:memory")
    assert deleted is True

    results = await provider.recall("session-123", "temp", limit=10)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_forget_returns_false_for_nonexistent_key(provider):
    deleted = await provider.forget("session-123", "nonexistent-key")
    assert deleted is False


@pytest.mark.asyncio
async def test_summarize_returns_expected_structure(provider):
    await provider.store(
        session_id="session-123",
        key="pref-1",
        value={"provider": "DHL"},
        memory_type="preference",
        importance=7,
    )
    await provider.store(
        session_id="session-123",
        key="decision-1",
        value={"chosen": "DHL"},
        memory_type="decision",
        importance=6,
    )
    await provider.store(
        session_id="session-123",
        key="context-1",
        value={"state": "active"},
        memory_type="context",
        importance=3,
    )

    summary = await provider.summarize("session-123")
    assert "summary" in summary
    assert "memory_count" in summary
    assert "key_themes" in summary
    assert "type_stats" in summary
    assert "top_keys" in summary
    assert summary["memory_count"] == 3
    assert len(summary["key_themes"]) == 3
    assert len(summary["top_keys"]) == 3
    assert summary["top_keys"][0] == "pref-1"


@pytest.mark.asyncio
async def test_recall_excludes_expired_memories(provider):
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    future = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()

    await provider.store(
        session_id="session-123",
        key="expired",
        value="old data",
        memory_type="context",
        importance=10,
        expires_at=datetime.fromisoformat(past.replace("Z", "+00:00")),
    )
    await provider.store(
        session_id="session-123",
        key="valid",
        value="new data",
        memory_type="context",
        importance=5,
        expires_at=datetime.fromisoformat(future.replace("Z", "+00:00")),
    )

    results = await provider.recall("session-123", "data", limit=10)
    assert len(results) == 1
    assert results[0]["key"] == "valid"


@pytest.mark.asyncio
async def test_recall_graceful_degradation_on_db_error(db_path):
    provider = SQLiteMemoryProvider(db_path=db_path)
    with patch("app.agent.memory.sqlite_provider.sqlite3.connect", side_effect=Exception("DB error")):
        results = await provider.recall("session-123", "query", limit=10)
        assert results == []


@pytest.mark.asyncio
async def test_store_graceful_degradation_on_db_error(db_path):
    provider = SQLiteMemoryProvider(db_path=db_path)
    with patch("app.agent.memory.sqlite_provider.sqlite3.connect", side_effect=Exception("DB error")):
        memory_id = await provider.store("session-123", "key", "value")
        assert memory_id == ""


@pytest.mark.asyncio
async def test_forget_graceful_degradation_on_db_error(db_path):
    provider = SQLiteMemoryProvider(db_path=db_path)
    with patch("app.agent.memory.sqlite_provider.sqlite3.connect", side_effect=Exception("DB error")):
        result = await provider.forget("session-123", "key")
        assert result is False


@pytest.mark.asyncio
async def test_summarize_graceful_degradation_on_db_error(db_path):
    provider = SQLiteMemoryProvider(db_path=db_path)
    with patch("app.agent.memory.sqlite_provider.sqlite3.connect", side_effect=Exception("DB error")):
        result = await provider.summarize("session-123")
        assert result == {}


@pytest.mark.asyncio
async def test_no_exceptions_raised_on_db_errors(db_path):
    provider = SQLiteMemoryProvider(db_path=db_path)
    with patch("app.agent.memory.sqlite_provider.sqlite3.connect", side_effect=Exception("DB error")):
        assert await provider.recall("s", "q") == []
        assert await provider.store("s", "k", "v") == ""
        assert await provider.forget("s", "k") is False
        assert await provider.summarize("s") == {}
