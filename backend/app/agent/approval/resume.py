import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class ResumeService:
    """Resume execution for a mission after explicit approval."""

    def __init__(self, session_manager, tool_orchestrator):
        self.session_manager = session_manager
        self.tool_orchestrator = tool_orchestrator

    async def resume_if_approved(self, session_id: str, mission_id: str, task_id: str, step_id: str) -> Optional[Dict[str, Any]]:
        """Resume execution for a specific task/step within a mission after explicit approval.

        Args:
            session_id: Session identifier
            mission_id: Mission identifier
            task_id: Task identifier within the mission
            step_id: Step identifier within the task

        Returns:
            Dict with execution result, or None if resume is not allowed
        """
        mission = self.session_manager.get_mission_by_id(session_id, mission_id)
        if not mission:
            return None

        approval_state = mission.get("result", {}).get("approval_state", {}) if isinstance(mission.get("result"), dict) else {}
        if not approval_state:
            return None

        if approval_state.get("status") != "APPROVED":
            return None

        if not approval_state.get("explicit_approval"):
            return None

        claim_succeeded = self._atomic_claim_resume(session_id, mission_id, approval_state)
        if not claim_succeeded:
            return None

        approval_proof = {
            "approval_id": mission_id,
            "task_id": task_id,
            "step_id": step_id,
            "status": "APPROVED",
            "explicit_approval": approval_state["explicit_approval"],
        }

        execution_plan = {
            "mission_id": mission_id,
            "task_id": task_id,
            "step_id": step_id,
            "tasks": [
                {
                    "task_id": task_id,
                    "tool_name": approval_state.get("operation", ""),
                    "parameters": approval_state.get("parameters", {}),
                }
            ],
        }

        try:
            session_context = {
                "session_id": session_id,
                "approval_proof": approval_proof,
                "goal_id": mission.get("goal_id"),
                "plan_id": mission.get("plan_id"),
                "risk": mission.get("risk"),
                "chosen_path": mission.get("chosen_path"),
                "intent": mission.get("intent"),
                "mission_id": mission_id,
                "task_id": task_id,
                "step_id": step_id,
            }
            result = await self.tool_orchestrator.execute(execution_plan, session_context=session_context)

            if result and result.get("mission_status") == "completed":
                self.session_manager.update_mission_status(
                    session_id=session_id,
                    mission_id=mission_id,
                    status="resumed",
                    result={"approval_state": {**approval_state, "status": "RESUMED"}},
                )
            return result
        except Exception:
            raise

    def _atomic_claim_resume(self, session_id: str, mission_id: str, approval_state: Dict[str, Any]) -> bool:
        """Atomically claim resume by transitioning approval_state from APPROVED to RESUMING.

        Uses approval_state.status as source of truth.
        SessionManager must support conditional atomic update:
        update_mission_status_if(
            session_id, mission_id,
            expected_status="APPROVED",
            new_status="RESUMING",
            result={"approval_state": approval_state}
        )

        Returns True if claim succeeded, False if already claimed/executed/rejected.
        """
        return self.session_manager.update_mission_status_if(
            session_id=session_id,
            mission_id=mission_id,
            expected_status="APPROVED",
            new_status="RESUMING",
            result={"approval_state": approval_state},
        )
