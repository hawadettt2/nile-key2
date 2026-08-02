import uuid
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from ..schemas.session import (
    SessionCreateRequest,
    SessionResponse,
    SessionStatusResponse,
    SessionContext,
)
from ..schemas.mission import Mission
from ..exceptions import SessionException


class SessionManager:
    def __init__(self, db_session_factory):
        self.db_session_factory = db_session_factory

    def create_session(self, request: SessionCreateRequest) -> SessionResponse:
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        context = SessionContext(
            user_id=request.user_id,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            status="active",
            metadata=request.metadata or {},
        ).model_dump()

        try:
            with self.db_session_factory() as db:
                db.execute(
                    """
                    INSERT INTO agent_sessions (id, user_id, context, status, started_at, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        request.user_id,
                        json.dumps(context, default=str),
                        "active",
                        now.isoformat(),
                        json.dumps(request.metadata or {}, default=str),
                    ),
                )
                db.commit()
        except Exception as e:
            raise SessionException(f"Failed to create session: {e}")

        return SessionResponse(
            session_id=session_id,
            user_id=request.user_id,
            status="active",
            started_at=now,
            metadata=request.metadata,
        )

    def get_session(self, session_id: str) -> Optional[SessionResponse]:
        try:
            with self.db_session_factory() as db:
                row = db.execute(
                    "SELECT id, user_id, status, started_at, ended_at, metadata FROM agent_sessions WHERE id = ?",
                    (session_id,),
                ).fetchone()

                if not row:
                    return None

                return SessionResponse(
                    session_id=row[0],
                    user_id=row[1],
                    status=row[2],
                    started_at=datetime.fromisoformat(row[3]),
                    ended_at=datetime.fromisoformat(row[4]) if row[4] else None,
                    metadata=json.loads(row[5]) if row[5] else None,
                )
        except Exception:
            return None

    def get_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        try:
            with self.db_session_factory() as db:
                row = db.execute(
                    "SELECT context FROM agent_sessions WHERE id = ?",
                    (session_id,),
                ).fetchone()

                if not row:
                    return None

                return json.loads(row[0]) if row[0] else {}
        except Exception:
            return None

    def update_context(self, session_id: str, context_updates: Dict[str, Any]) -> bool:
        try:
            current_context = self.get_context(session_id)
            if current_context is None:
                return False

            current_context.update(context_updates)
            current_context["updated_at"] = datetime.now(timezone.utc).isoformat()

            with self.db_session_factory() as db:
                db.execute(
                    "UPDATE agent_sessions SET context = ? WHERE id = ?",
                    (json.dumps(current_context, default=str), session_id),
                )
                db.commit()
            return True
        except Exception:
            return False

    def end_session(self, session_id: str) -> bool:
        try:
            now = datetime.now(timezone.utc).isoformat()
            with self.db_session_factory() as db:
                db.execute(
                    "UPDATE agent_sessions SET status = ?, ended_at = ? WHERE id = ?",
                    ("completed", now, session_id),
                )
                db.commit()
            return True
        except Exception:
            return False

    def get_status(self, session_id: str) -> Optional[SessionStatusResponse]:
        session = self.get_session(session_id)
        if not session:
            return None

        context = self.get_context(session_id) or {}
        steps = context.get("steps", [])

        return SessionStatusResponse(
            session_id=session_id,
            status=session.status,
            current_step=context.get("current_step"),
            steps_completed=len(steps),
            started_at=session.started_at,
            last_activity=datetime.fromisoformat(context.get("updated_at", session.started_at.isoformat())),
        )

    def add_mission(self, session_id: str, mission: Mission) -> bool:
        """Add a mission to the session context."""
        try:
            context = self.get_context(session_id)
            if context is None:
                return False

            missions = context.get("missions", [])
            missions.append(mission.model_dump(mode="json"))
            context["missions"] = missions
            context["current_step"] = "mission_created"
            context["updated_at"] = datetime.now(timezone.utc).isoformat()

            with self.db_session_factory() as db:
                db.execute(
                    "UPDATE agent_sessions SET context = ? WHERE id = ?",
                    (json.dumps(context, default=str), session_id),
                )
                db.commit()
            return True
        except Exception:
            return False

    def get_missions(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all missions in a session."""
        context = self.get_context(session_id)
        if context is None:
            return []
        return context.get("missions", [])

    def update_mission_status(self, session_id: str, mission_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """Update a mission's status within a session."""
        try:
            context = self.get_context(session_id)
            if context is None:
                return False

            missions = context.get("missions", [])
            for mission in missions:
                if mission.get("mission_id") == mission_id:
                    mission["status"] = status
                    if result is not None:
                        mission["result"] = result
                    mission["updated_at"] = datetime.now(timezone.utc).isoformat()
                    break

            context["missions"] = missions
            context["updated_at"] = datetime.now(timezone.utc).isoformat()

            with self.db_session_factory() as db:
                db.execute(
                    "UPDATE agent_sessions SET context = ? WHERE id = ?",
                    (json.dumps(context, default=str), session_id),
                )
                db.commit()
            return True
        except Exception:
            return False

    async def initialize_session_memory(self, session_id: str, memory_provider, user_id: int) -> bool:
        """إثراء سياق الجلسة بالذكريات التاريخية للمستخدم عند بدء الجلسة.

        تلتزم الدالة بالتدهور الآمن؛ أي خطأ أو عدم توفر للمزود لن يعطل استمرار الجلسة.
        تستعلم الدالة عن الذاكرة التاريخية بناءً على سياق المستخدم (user_id) لتحقيق توارث الذاكرة.
        """
        if not memory_provider:
            return False
        try:
            memories = await memory_provider.recall(session_id=str(user_id), query="context", limit=10)
            if not memories:
                return False

            memory_keys = [m.get("key") for m in memories if m.get("key")]

            return self.update_context(session_id, {
                "memory_refs": memory_keys,
                "memory_keys": memory_keys,
            })
        except Exception:
            return False

    def get_pending_approvals(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find all missions with pending_approval status across sessions."""
        try:
            with self.db_session_factory() as db:
                rows = db.execute(
                    "SELECT id, user_id, context FROM agent_sessions WHERE status = ?",
                    ("active",),
                ).fetchall()

            approvals = []
            for row in rows:
                session_id, row_user_id, context_json = row
                if user_id is not None and row_user_id != user_id:
                    continue
                try:
                    context = json.loads(context_json) if context_json else {}
                except Exception:
                    continue
                missions = context.get("missions", [])
                for mission in missions:
                    if mission.get("status") == "pending_approval":
                        approvals.append({
                            "mission_id": mission.get("mission_id"),
                            "session_id": session_id,
                            "user_id": row_user_id,
                            "mission_type": mission.get("mission_type"),
                            "status": mission.get("status"),
                            "requires_approval": mission.get("requires_approval", False),
                            "approval_status": mission.get("approval_status", "pending"),
                            "reasoning": mission.get("reasoning"),
                            "created_at": mission.get("created_at"),
                        })
            return approvals
        except Exception:
            return []

    def get_mission_by_id(self, session_id: str, mission_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific mission from a session."""
        context = self.get_context(session_id)
        if context is None:
            return None
        missions = context.get("missions", [])
        for mission in missions:
            if mission.get("mission_id") == mission_id:
                return mission
        return None
