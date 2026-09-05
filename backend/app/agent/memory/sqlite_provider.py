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
    
    # Add user_id column if it doesn't exist (migration for existing databases)
    cursor.execute("PRAGMA table_info(agent_memory)")
    columns = [row[1] for row in cursor.fetchall()]
    if 'user_id' not in columns:
        cursor.execute("ALTER TABLE agent_memory ADD COLUMN user_id INTEGER")
        # Backfill user_id from agent_sessions where possible
        cursor.execute("""
            UPDATE agent_memory
            SET user_id = (SELECT agent_sessions.user_id FROM agent_sessions WHERE agent_sessions.id = agent_memory.session_id)
            WHERE session_id IN (SELECT id FROM agent_sessions WHERE user_id IS NOT NULL)
        """)
        # Rebuild table with NOT NULL constraint
        cursor.execute("""
            CREATE TABLE agent_memory_new (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                session_id TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                memory_type TEXT DEFAULT 'context',
                importance INTEGER DEFAULT 5,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (session_id) REFERENCES agent_sessions(id)
            )
        """)
        cursor.execute("""
            INSERT INTO agent_memory_new
            SELECT id, user_id, session_id, key, value, memory_type, importance, expires_at, created_at, updated_at
            FROM agent_memory
            WHERE user_id IS NOT NULL
        """)
        cursor.execute("DROP TABLE agent_memory")
        cursor.execute("ALTER TABLE agent_memory_new RENAME TO agent_memory")
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_agent_memory_user_session
        ON agent_memory(user_id, session_id)
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
    def __init__(self, db_path: str = "nile_key.db", audit_recorder=None):
        self._db_path = db_path
        self._audit_recorder = audit_recorder
        try:
            conn = sqlite3.connect(db_path)
            _ensure_memory_schema(conn)
            conn.close()
        except Exception as exc:
            logger.error("Failed to initialize agent_memory schema: %s", exc)

    async def _run(self, func, *args, **kwargs):
        return await asyncio.to_thread(func, *args, **kwargs)

    def _record_audit(self, operation: str, session_id: str, memory_type: Optional[str] = None, memory_key: Optional[str] = None, result_count: Optional[int] = None, component: Optional[str] = None, system: Optional[str] = None) -> None:
        if not self._audit_recorder:
            return
        try:
            self._audit_recorder.record_memory_operation(
                session_id=session_id,
                agent_id="memory_provider",
                operation=operation,
                memory_type=memory_type,
                memory_key=memory_key,
                result_count=result_count,
                component=component,
                system=system,
            )
        except Exception:
            pass

    async def recall(
        self,
        user_id: int,
        session_id: str,
        query: str,
        limit: int = 10,
        cross_session: bool = False,
    ) -> List[Dict[str, Any]]:
        try:
            def _query():
                conn = sqlite3.connect(self._db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                if cross_session:
                    cursor.execute(
                        """
                        SELECT id, user_id, session_id, key, value, memory_type, importance,
                               created_at, updated_at
                        FROM agent_memory
                        WHERE user_id = ?
                          AND (
                                key LIKE ?
                                OR value LIKE ?
                              )
                          AND (expires_at IS NULL OR expires_at > ?)
                        """,
                        (
                            user_id,
                            f"%{query}%",
                            f"%{query}%",
                            datetime.utcnow().isoformat(),
                        ),
                    )
                else:
                    cursor.execute(
                        """
                        SELECT id, user_id, session_id, key, value, memory_type, importance,
                               created_at, updated_at
                        FROM agent_memory
                        WHERE user_id = ?
                          AND session_id = ?
                          AND (
                                key LIKE ?
                                OR value LIKE ?
                              )
                          AND (expires_at IS NULL OR expires_at > ?)
                        """,
                        (
                            user_id,
                            session_id,
                            f"%{query}%",
                            f"%{query}%",
                            datetime.utcnow().isoformat(),
                        ),
                    )
                rows = cursor.fetchall()
                conn.close()

                memory_type_weights = {
                    "standing_order": 1.5,
                    "preference": 1.3,
                    "decision": 1.2,
                    "context": 1.0,
                }

                query_lower = query.lower()
                results = []
                for row in rows:
                    item = dict(row)
                    try:
                        item["value"] = json.loads(item["value"]) if item["value"] is not None else None
                    except json.JSONDecodeError:
                        item["value"] = item["value"]

                    key_lower = (item.get("key") or "").lower()
                    value_lower = (str(item.get("value") or "")).lower()

                    exact_match = query_lower == key_lower
                    key_contains = query_lower in key_lower
                    value_contains = query_lower in value_lower

                    score = 0.0
                    if exact_match:
                        score += 2.0
                    if key_contains:
                        score += 1.0
                    if value_contains:
                        score += 0.5

                    importance = item.get("importance", 5)
                    if isinstance(importance, int):
                        score += importance * 0.1

                    memory_type = item.get("memory_type") or "context"
                    score += memory_type_weights.get(memory_type, 1.0)

                    item["recall_score"] = score
                    results.append(item)

                results.sort(key=lambda r: r.get("recall_score", 0), reverse=True)
                return results[:limit]

            return await self._run(_query)
        except Exception as exc:
            logger.error("Memory recall failed: %s", exc)
            return []
        finally:
            self._record_audit("memory_recall", session_id, memory_type="query", memory_key=query, component="sqlite_provider", system="memory")

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
                        id, user_id, session_id, key, value, memory_type, importance,
                        expires_at, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        memory_id,
                        user_id,
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
            self._record_audit("memory_store", session_id, memory_type=memory_type, memory_key=key, component="sqlite_provider", system="memory")
            return memory_id
        except Exception as exc:
            logger.error("Memory store failed: %s", exc)
            return ""

    async def forget(self, user_id: int, session_id: str, key: str) -> bool:
        try:
            def _delete():
                conn = sqlite3.connect(self._db_path)
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM agent_memory WHERE user_id = ? AND session_id = ? AND key = ?",
                    (user_id, session_id, key),
                )
                deleted = cursor.rowcount > 0
                conn.commit()
                conn.close()
                return deleted

            result = await self._run(_delete)
            self._record_audit("memory_forget", session_id, memory_key=key, component="sqlite_provider", system="memory")
            return result
        except Exception as exc:
            logger.error("Memory forget failed: %s", exc)
            return False

    async def summarize(self, user_id: int, session_id: str) -> Dict[str, Any]:
        try:
            def _summarize():
                conn = sqlite3.connect(self._db_path)
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT memory_type, COUNT(*) as count, AVG(importance) as avg_importance
                    FROM agent_memory
                    WHERE user_id = ?
                      AND session_id = ?
                      AND (expires_at IS NULL OR expires_at > ?)
                    GROUP BY memory_type
                    """,
                    (user_id, session_id, datetime.utcnow().isoformat()),
                )
                rows = cursor.fetchall()
                cursor.execute(
                    """
                    SELECT key, memory_type, importance
                    FROM agent_memory
                    WHERE user_id = ?
                      AND session_id = ?
                      AND (expires_at IS NULL OR expires_at > ?)
                    ORDER BY importance DESC
                    LIMIT 20
                    """,
                    (user_id, session_id, datetime.utcnow().isoformat()),
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

    async def cleanup_expired(self, user_id: Optional[int] = None) -> int:
        """حذف السجلات منتهية الصلاحية من قاعدة البيانات.

        تلتزم الدالة بحذف السجلات التي تخطت الوقت الحالي فقط (expires_at <= now).
        تعود بعدد السجلات المحذوفة، وفي حالة حدوث خطأ تعود بـ 0 تلبية للتدهور الآمن.
        """
        try:
            def _cleanup():
                conn = sqlite3.connect(self._db_path)
                cursor = conn.cursor()

                now_str = datetime.utcnow().isoformat()
                if user_id is not None:
                    cursor.execute(
                        """
                        DELETE FROM agent_memory
                        WHERE expires_at IS NOT NULL
                          AND expires_at <= ?
                          AND user_id = ?
                        """,
                        (now_str, user_id),
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
