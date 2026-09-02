from typing import Optional, Dict, Any, List
from datetime import datetime
import sqlite3
import json

from .schema import Plan


class PlanRepository:
    def __init__(self, db_factory):
        self.db_factory = db_factory

    def create(self, plan: Plan) -> Plan:
        with self.db_factory() as db:
            db.execute(
                """
                INSERT INTO agent_plans (
                    plan_id, goal_id, user_id, session_id, objective, missions,
                    dependencies, constraints, approval_policy, fallback_strategy,
                    status, created_at, updated_at, completed_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    plan.plan_id,
                    plan.goal_id,
                    plan.user_id,
                    plan.session_id,
                    plan.objective,
                    json.dumps(plan.missions),
                    json.dumps(plan.dependencies),
                    json.dumps(plan.constraints),
                    json.dumps(plan.approval_policy),
                    json.dumps(plan.fallback_strategy),
                    plan.status,
                    plan.created_at.isoformat(),
                    plan.updated_at.isoformat(),
                    plan.completed_at.isoformat() if plan.completed_at else None,
                    json.dumps(plan.metadata),
                ),
            )
            db.commit()
        return plan

    def get(self, plan_id: str) -> Optional[Plan]:
        with self.db_factory() as db:
            row = db.execute(
                "SELECT * FROM agent_plans WHERE plan_id = ?",
                (plan_id,),
            ).fetchone()
        if not row:
            return None
        return self._row_to_plan(row)

    def list(self, goal_id: str) -> List[Plan]:
        with self.db_factory() as db:
            rows = db.execute(
                "SELECT * FROM agent_plans WHERE goal_id = ? ORDER BY created_at DESC",
                (goal_id,),
            ).fetchall()
        return [self._row_to_plan(row) for row in rows]

    def update(self, plan_id: str, updates: Dict[str, Any]) -> Optional[Plan]:
        allowed = {"missions", "dependencies", "constraints", "approval_policy", "fallback_strategy", "status", "completed_at", "metadata"}
        set_clauses = []
        params: List[Any] = []
        for key, value in updates.items():
            if key not in allowed:
                continue
            if key in {"missions", "dependencies", "constraints", "approval_policy", "fallback_strategy", "metadata"}:
                value = json.dumps(value)
            set_clauses.append(f"{key} = ?")
            params.append(value)
        if not set_clauses:
            return self.get(plan_id)
        set_clauses.append("updated_at = ?")
        params.append(datetime.utcnow().isoformat())
        params.append(plan_id)
        with self.db_factory() as db:
            db.execute(
                f"UPDATE agent_plans SET {', '.join(set_clauses)} WHERE plan_id = ?",
                params,
            )
            db.commit()
        return self.get(plan_id)

    def append_mission(self, plan_id: str, mission_id: str) -> bool:
        with self.db_factory() as db:
            row = db.execute(
                "SELECT missions FROM agent_plans WHERE plan_id = ?",
                (plan_id,),
            ).fetchone()
            if not row:
                return False
            missions = json.loads(row["missions"]) if row["missions"] else []
            if mission_id not in missions:
                missions.append(mission_id)
                db.execute(
                    "UPDATE agent_plans SET missions = ?, updated_at = ? WHERE plan_id = ?",
                    (json.dumps(missions), datetime.utcnow().isoformat(), plan_id),
                )
                db.commit()
        return True

    def get_active_plan(self, goal_id: str) -> Optional[Plan]:
        with self.db_factory() as db:
            row = db.execute(
                "SELECT * FROM agent_plans WHERE goal_id = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1",
                (goal_id,),
            ).fetchone()
        if not row:
            return None
        return self._row_to_plan(row)

    def get_plan_missions(self, plan_id: str) -> List[str]:
        with self.db_factory() as db:
            row = db.execute(
                "SELECT missions FROM agent_plans WHERE plan_id = ?",
                (plan_id,),
            ).fetchone()
        if not row:
            return []
        return json.loads(row["missions"]) if row["missions"] else []

    def archive(self, plan_id: str, status: str) -> bool:
        with self.db_factory() as db:
            db.execute(
                "UPDATE agent_plans SET status = ?, updated_at = ? WHERE plan_id = ?",
                (status, datetime.utcnow().isoformat(), plan_id),
            )
            db.commit()
        return True

    def _row_to_plan(self, row) -> Plan:
        return Plan(
            plan_id=row["plan_id"],
            goal_id=row["goal_id"],
            user_id=row["user_id"],
            session_id=row["session_id"],
            objective=row["objective"],
            missions=json.loads(row["missions"]) if row["missions"] else [],
            dependencies=json.loads(row["dependencies"]) if row["dependencies"] else [],
            constraints=json.loads(row["constraints"]) if row["constraints"] else [],
            approval_policy=json.loads(row["approval_policy"]) if row["approval_policy"] else {},
            fallback_strategy=json.loads(row["fallback_strategy"]) if row["fallback_strategy"] else {},
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )
