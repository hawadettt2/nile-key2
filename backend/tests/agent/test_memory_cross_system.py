import pytest
import sqlite3
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.agent.memory.interface import MemoryProvider
from app.agent.memory.sqlite_provider import SQLiteMemoryProvider
from app.agent.memory.cross_system import (
    recall_cross_session,
    store_cross_system,
    recall_cross_system,
    store_cross_component,
    recall_cross_component,
)
from app.agent.audit.recorder import AuditRecorder


class ConcreteMemoryProvider(MemoryProvider):
    async def recall(self, user_id: int, session_id: str, query: str, limit: int = 10):
        return []

    async def store(self, user_id: int, session_id: str, key: str, value, memory_type="context", importance=5, expires_at=None):
        return "memory-123"

    async def forget(self, user_id: int, session_id: str, key: str):
        return True

    async def summarize(self, user_id: int, session_id: str):
        return {"summary": "", "memory_count": 0, "key_themes": []}

    async def cleanup_expired(self, user_id=None):
        return 0


class TestCrossSessionRecall:
    @pytest.mark.asyncio
    async def test_recall_cross_session_returns_memories(self, tmp_path):
        db_path = str(tmp_path / "test_cross_session.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                status TEXT
            )
        """)
        conn.execute("INSERT INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)", ("session-1", 1, "active"))
        conn.commit()
        conn.close()

        provider = SQLiteMemoryProvider(db_path=db_path)
        await provider.store(1, "session-1", "cross_session_context", {"history": "order_123"})
        memories = await recall_cross_session(
            memory_provider=provider,
            user_id=1,
            current_session_id="session-2",
            query="cross_session_context",
            limit=5,
        )
        assert len(memories) == 1
        assert memories[0]["key"] == "cross_session_context"

    @pytest.mark.asyncio
    async def test_recall_cross_session_none_provider(self):
        memories = await recall_cross_session(
            memory_provider=None,
            user_id=1,
            current_session_id="session-1",
        )
        assert memories == []

    @pytest.mark.asyncio
    async def test_recall_cross_session_user_isolation(self, tmp_path):
        db_path = str(tmp_path / "test_cross_session_isolation.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                status TEXT
            )
        """)
        conn.execute("INSERT INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)", ("session-1", 1, "active"))
        conn.execute("INSERT INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)", ("session-2", 2, "active"))
        conn.commit()
        conn.close()

        provider = SQLiteMemoryProvider(db_path=db_path)
        await provider.store(1, "session-1", "cross_session_context", {"history": "order_123"})
        memories = await recall_cross_session(
            memory_provider=provider,
            user_id=2,
            current_session_id="session-2",
            query="cross_session_context",
            limit=5,
        )
        assert len(memories) == 0


class TestCrossSystemMemory:
    @pytest.mark.asyncio
    async def test_store_cross_system_scopes_key(self, tmp_path):
        db_path = str(tmp_path / "test_cross_system.db")
        provider = SQLiteMemoryProvider(db_path=db_path)
        memory_id = await store_cross_system(
            memory_provider=provider,
            user_id=1,
            session_id="session-1",
            system_name="shipping",
            key="decision_abc",
            value={"path": "shipping"},
            memory_type="cross_system",
            importance=8,
        )
        assert memory_id != ""
        memories = await provider.recall(1, "session-1", "shipping:decision_abc")
        assert len(memories) == 1
        assert memories[0]["key"] == "shipping:decision_abc"

    @pytest.mark.asyncio
    async def test_recall_cross_system_scopes_query(self, tmp_path):
        db_path = str(tmp_path / "test_cross_system_recall.db")
        provider = SQLiteMemoryProvider(db_path=db_path)
        await provider.store(1, "session-1", "decision_engine:cross_system_decision:shipping", {"path": "shipping"})
        memories = await recall_cross_system(
            memory_provider=provider,
            user_id=1,
            session_id="session-1",
            system_name="decision_engine",
            query="cross_system_decision",
            limit=10,
        )
        assert len(memories) == 1
        assert memories[0]["key"] == "decision_engine:cross_system_decision:shipping"

    @pytest.mark.asyncio
    async def test_cross_system_memory_none_provider(self):
        result = await store_cross_system(None, 1, "session-1", "shipping", "key", "value")
        assert result == ""
        result = await recall_cross_system(None, 1, "session-1", "shipping", "query")
        assert result == []


class TestCrossComponentMemory:
    @pytest.mark.asyncio
    async def test_store_cross_component_scopes_key(self, tmp_path):
        db_path = str(tmp_path / "test_cross_component.db")
        provider = SQLiteMemoryProvider(db_path=db_path)
        memory_id = await store_cross_component(
            memory_provider=provider,
            user_id=1,
            session_id="session-1",
            component_name="goal_evolution",
            key="evolution_1",
            value={"goal_id": "1"},
            memory_type="cross_component",
            importance=5,
        )
        assert memory_id != ""
        memories = await provider.recall(1, "session-1", "goal_evolution:evolution_1")
        assert len(memories) == 1
        assert memories[0]["key"] == "goal_evolution:evolution_1"

    @pytest.mark.asyncio
    async def test_recall_cross_component_scopes_query(self, tmp_path):
        db_path = str(tmp_path / "test_cross_component_recall.db")
        provider = SQLiteMemoryProvider(db_path=db_path)
        await provider.store(1, "session-1", "insights:cross_component_pattern:workflow", {"pattern": "success"})
        memories = await recall_cross_component(
            memory_provider=provider,
            user_id=1,
            session_id="session-1",
            component_name="insights",
            query="cross_component_pattern",
            limit=10,
        )
        assert len(memories) == 1
        assert memories[0]["key"] == "insights:cross_component_pattern:workflow"

    @pytest.mark.asyncio
    async def test_cross_component_memory_none_provider(self):
        result = await store_cross_component(None, 1, "session-1", "insights", "key", "value")
        assert result == ""
        result = await recall_cross_component(None, 1, "session-1", "insights", "query")
        assert result == []


class TestMemoryAuditTrail:
    def test_record_memory_operation_inserts_log(self, tmp_path):
        db_path = str(tmp_path / "test_audit.db")
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                agent_id TEXT,
                tool_name TEXT,
                input_hash TEXT,
                output_status TEXT,
                result_ref TEXT,
                duration_ms INTEGER,
                timestamp TEXT,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

        def factory():
            return sqlite3.connect(db_path)

        recorder = AuditRecorder(db_session_factory=factory)
        recorder.record_memory_operation(
            session_id="session-1",
            agent_id="memory_provider",
            operation="memory_recall",
            memory_type="context",
            memory_key="cross_session_context",
            result_count=3,
            component="sqlite_provider",
            system="memory",
        )

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT tool_name, metadata FROM agent_audit_logs WHERE session_id = ?", ("session-1",))
        rows = cursor.fetchall()
        conn.close()
        assert len(rows) == 1
        assert rows[0][0] == "memory_recall"
        assert "cross_session_context" in rows[0][1]
        assert "result_count" in rows[0][1]

    @pytest.mark.asyncio
    async def test_sqlite_provider_audit_on_recall(self, tmp_path):
        db_path = str(tmp_path / "test_provider_audit.db")
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                agent_id TEXT,
                tool_name TEXT,
                input_hash TEXT,
                output_status TEXT,
                result_ref TEXT,
                duration_ms INTEGER,
                timestamp TEXT,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

        def factory():
            return sqlite3.connect(db_path)

        recorder = AuditRecorder(db_session_factory=factory)
        provider = SQLiteMemoryProvider(db_path=db_path, audit_recorder=recorder)
        await provider.recall(1, "session-1", "context", limit=5)

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT tool_name FROM agent_audit_logs WHERE session_id = ?", ("session-1",))
        rows = cursor.fetchall()
        conn.close()
        assert len(rows) == 1
        assert rows[0][0] == "memory_recall"

    @pytest.mark.asyncio
    async def test_sqlite_provider_audit_on_store(self, tmp_path):
        db_path = str(tmp_path / "test_provider_audit_store.db")
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                agent_id TEXT,
                tool_name TEXT,
                input_hash TEXT,
                output_status TEXT,
                result_ref TEXT,
                duration_ms INTEGER,
                timestamp TEXT,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

        def factory():
            return sqlite3.connect(db_path)

        recorder = AuditRecorder(db_session_factory=factory)
        provider = SQLiteMemoryProvider(db_path=db_path, audit_recorder=recorder)
        await provider.store(1, "session-1", "key1", "value1", memory_type="context")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT tool_name FROM agent_audit_logs WHERE session_id = ?", ("session-1",))
        rows = cursor.fetchall()
        conn.close()
        assert len(rows) == 1
        assert rows[0][0] == "memory_store"

    @pytest.mark.asyncio
    async def test_sqlite_provider_audit_on_forget(self, tmp_path):
        db_path = str(tmp_path / "test_provider_audit_forget.db")
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                agent_id TEXT,
                tool_name TEXT,
                input_hash TEXT,
                output_status TEXT,
                result_ref TEXT,
                duration_ms INTEGER,
                timestamp TEXT,
                metadata TEXT
            )
        """)
        conn.commit()
        conn.close()

        def factory():
            return sqlite3.connect(db_path)

        recorder = AuditRecorder(db_session_factory=factory)
        provider = SQLiteMemoryProvider(db_path=db_path, audit_recorder=recorder)
        await provider.store(1, "session-1", "key1", "value1", memory_type="context")
        await provider.forget(1, "session-1", "key1")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT tool_name FROM agent_audit_logs WHERE session_id = ?", ("session-1",))
        rows = cursor.fetchall()
        conn.close()
        assert len(rows) == 2
        tool_names = [r[0] for r in rows]
        assert "memory_store" in tool_names
        assert "memory_forget" in tool_names
