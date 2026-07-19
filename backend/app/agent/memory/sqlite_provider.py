import asyncio
import json
import logging
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .interface import MemoryProvider

logger = logging.getLogger(__name__)


def _ensure_memory_schema(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_memory (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            memory_type TEXT DEFAULT 'context',
            importance INTEGER DEFAULT 5,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_memory_session_id
        ON agent_memory(session_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_memory_type
        ON agent_memory(memory_type)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_memory_importance
        ON agent_memory(importance)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_memory_expires_at
        ON agent_memory(expires_at)
    """)
    conn.commit()


class SQLiteMemoryProvider(MemoryProvider):
    def __init__(self, db_path: str = "nile_key.db"):
        self._db_path = db_path
        try:
            conn = sqlite3.connect(db_path)
            _ensure_memory_schema(conn)
            conn.close()
        except Exception as exc:
            logger.error("Failed to initialize agent_memory schema: %s", exc)

    async def _run(self, func, *args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    async def recall(
        self,
        session_id: str,
        query: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        try:
            def _query():
                conn = sqlite3.connect(self._db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, session_id, key, value, memory_type, importance,
                           created_at, updated_at
                    FROM agent_memory
                    WHERE session_id = ?
                      AND (
                            key LIKE ?
                            OR value LIKE ?
                          )
                      AND (expires_at IS NULL OR expires_at > ?)
                    ORDER BY importance DESC
                    LIMIT ?
                    """,
                    (
                        session_id,
                        f"%{query}%",
                        f"%{query}%",
                        datetime.utcnow().isoformat(),
                        limit,
                    ),
                )
                rows = cursor.fetchall()
                conn.close()
                results = []
                for row in rows:
                    item = dict(row)
                    try:
                        item["value"] = json.loads(item["value"]) if item["value"] is not None else None
                    except json.JSONDecodeError:
                        item["value"] = item["value"]
                    results.append(item)
                return results

            return await self._run(_query)
        except Exception as exc:
            logger.error("Memory recall failed: %s", exc)
            return []

    async def store(
        self,
        session_id: str,
        key: str,
        value: Any,
        memory_type: str = "context",
        importance: int = 5,
        expires_at: Optional[datetime] = None,
    ) -> str:
        try:
            memory_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()
            value_text = json.dumps(value, default=str)

            def _insert():
                conn = sqlite3.connect(self._db_path)
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO agent_memory (
                        id, session_id, key, value, memory_type, importance,
                        expires_at, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        memory_id,
                        session_id,
                        key,
                        value_text,
                        memory_type,
                        importance,
                        expires_at.isoformat() if expires_at else None,
                        now,
                        now,
                    ),
                )
                conn.commit()
                conn.close()

            await self._run(_insert)
            return memory_id
        except Exception as exc:
            logger.error("Memory store failed: %s", exc)
            return ""

    async def forget(self, session_id: str, key: str) -> bool:
        try:
            def _delete():
                conn = sqlite3.connect(self._db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM agent_memory WHERE session_id = ? AND key = ?",
                    (session_id, key),
                )
                deleted = cursor.rowcount > 0
                conn.commit()
                conn.close()
                return deleted

            return await self._run(_delete)
        except Exception as exc:
            logger.error("Memory forget failed: %s", exc)
            return False

    async def summarize(self, session_id: str) -> Dict[str, Any]:
        try:
            def _summarize():
                conn = sqlite3.connect(self._db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT memory_type, COUNT(*) as count, AVG(importance) as avg_importance
                    FROM agent_memory
                    WHERE session_id = ?
                      AND (expires_at IS NULL OR expires_at > ?)
                    GROUP BY memory_type
                    """,
                    (session_id, datetime.utcnow().isoformat()),
                )
                rows = cursor.fetchall()
                cursor.execute(
                    """
                    SELECT key, memory_type, importance
                    FROM agent_memory
                    WHERE session_id = ?
                      AND (expires_at IS NULL OR expires_at > ?)
                    ORDER BY importance DESC
                    LIMIT 20
                    """,
                    (session_id, datetime.utcnow().isoformat()),
                )
                top_rows = cursor.fetchall()
                conn.close()

                type_stats = []
                key_themes = []
                for row in rows:
                    entry = dict(row)
                    type_stats.append({
                        "memory_type": entry["memory_type"],
                        "count": entry["count"],
                        "avg_importance": round(entry["avg_importance"], 2) if entry["avg_importance"] is not None else 0,
                    })
                    key_themes.append(entry["memory_type"])

                top_keys = [dict(row)["key"] for row in top_rows]
                return {
                    "summary": f"Session {session_id}: {len(type_stats)} memory types, "
                               f"{sum(item['count'] for item in type_stats)} total memories.",
                    "memory_count": sum(item["count"] for item in type_stats),
                    "key_themes": key_themes,
                    "type_stats": type_stats,
                    "top_keys": top_keys,
                }

            return await self._run(_summarize)
        except Exception as exc:
            logger.error("Memory summarize failed: %s", exc)
            return {}

    async def cleanup_expired(self, session_id: Optional[str] = None) -> int:
        """حذف السجلات منتهية الصلاحية من قاعدة البيانات.

        تلتزم الدالة بحذف السجلات التي تخطت الوقت الحالي فقط (expires_at <= now).
        تعود بعدد السجلات المحذوفة، وفي حالة حدوث خطأ تعود بـ 0 تلبية للتدهور الآمن.
        """
        try:
            def _cleanup():
                conn = sqlite3.connect(self._db_path)
                cursor = conn.cursor()

                now_str = datetime.utcnow().isoformat()
                if session_id:
                    cursor.execute(
                        """
                        DELETE FROM agent_memory
                        WHERE expires_at IS NOT NULL
                          AND expires_at <= ?
                          AND session_id = ?
                        """,
                        (now_str, session_id),
                    )
                else:
                    cursor.execute(
                        """
                        DELETE FROM agent_memory
                        WHERE expires_at IS NOT NULL
                          AND expires_at <= ?
                        """,
                        (now_str,),
                    )

                deleted_count = cursor.rowcount
                conn.commit()
                conn.close()
                return deleted_count

            return await self._run(_cleanup)
        except Exception as exc:
            logger.error("Memory expired cleanup failed: %s", exc)
            return 0
