from typing import Optional, Dict, Any, List
from datetime import datetime
import sqlite3
import json

from .schema import Goal


class GoalRepository:
    def __init__(self, db_factory):
        self.db_factory = db_factory

    def create(self, goal: Goal) -> Goal:
        with self.db_factory() as db:
            db.execute(
                """
                INSERT INTO agent_goals (
                    goal_id, user_id, session_id, objective, scope, constraints,
                    stakeholders, autonomy_level, status, created_at, updated_at,
                    completed_at, parent_goal_id, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    goal.goal_id,
                    goal.user_id,
                    goal.session_id,
                    goal.objective,
                    json.dumps(goal.scope),
                    json.dumps(goal.constraints),
                    json.dumps(goal.stakeholders),
                    goal.autonomy_level,
                    goal.status,
                    goal.created_at.isoformat(),
                    goal.updated_at.isoformat(),
                    goal.completed_at.isoformat() if goal.completed_at else None,
                    goal.parent_goal_id,
                    json.dumps(goal.metadata),
                ),
            )
            db.commit()
        return goal

    def get(self, goal_id: str) -> Optional[Goal]:
        with self.db_factory() as db:
            row = db.execute(
                "SELECT * FROM agent_goals WHERE goal_id = ?",
                (goal_id,),
            ).fetchone()
        if not row:
            return None
        return self._row_to_goal(row)

    def list(self, user_id: int, filters: Dict[str, Any] = None) -> List[Goal]:
        query = "SELECT * FROM agent_goals WHERE user_id = ?"
        params: List[Any] = [user_id]
        if filters:
            if filters.get("status"):
                query += " AND status = ?"
                params.append(filters["status"])
            if filters.get("session_id"):
                query += " AND session_id = ?"
                params.append(filters["session_id"])
        query += " ORDER BY created_at DESC"
        with self.db_factory() as db:
            rows = db.execute(query, params).fetchall()
        return [self._row_to_goal(row) for row in rows]

    def update(self, goal_id: str, updates: Dict[str, Any]) -> Optional[Goal]:
        allowed = {"status", "scope", "constraints", "stakeholders", "autonomy_level", "completed_at", "metadata", "objective"}
        set_clauses = []
        params: List[Any] = []
        for key, value in updates.items():
            if key not in allowed:
                continue
            if key in {"scope", "constraints", "stakeholders", "metadata"}:
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            params.append(value)
        if not set_clauses:
            return self.get(goal_id)
        set_clauses.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(goal_id)
        with self.db_factory() as db:
            db.execute(
                f"UPDATE agent_goals SET {', '.join(set_clauses)} WHERE goal_id = ?",
                params,
            )
            db.commit()
        return self.get(goal_id)

    def archive(self, goal_id: str, status: str) -> bool:
        with self.db_factory() as db:
            db.execute(
                "UPDATE agent_goals SET status = ?, updated_at = ? WHERE goal_id = ?",
                (status, datetime.utcnow().isoformat(), goal_id),
            )
            db.commit()
        return True

    def get_active_goals(self, user_id: int) -> List[Goal]:
        with self.db_factory() as db:
            rows = db.execute(
                "SELECT * FROM agent_goals WHERE user_id = ? AND status = 'active' ORDER BY created_at DESC",
                (user_id,),
            ).fetchall()
        return [self._row_to_goal(row) for row in rows]

    def _row_to_goal(self, row) -> Goal:
        return Goal(
            goal_id=row["goal_id"],
            user_id=row["user_id"],
            session_id=row["session_id"],
            objective=row["objective"],
            scope=json.loads(row["scope"]) if row["scope"] else {},
            constraints=json.loads(row["constraints"]) if row["constraints"] else [],
            stakeholders=json.loads(row["stakeholders"]) if row["stakeholders"] else [],
            autonomy_level=row["autonomy_level"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            parent_goal_id=row["parent_goal_id"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )
