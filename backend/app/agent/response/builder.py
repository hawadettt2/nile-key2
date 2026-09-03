from typing import Optional, Dict, Any, List

from ..avatar.interface import IntentContent
from ..autonomy.schema import AutonomyPolicy


class ResponseBuilder:
    """Deterministic mapping/normalization layer from DEM internal state to IntentContent.

    This builder transforms existing DEM state into structured business-facing
    responses. It does not infer new business decisions, apply business rules,
    or change the meaning of underlying data.
    """

    @staticmethod
    def _map_status_to_intent_type(status: str) -> str:
        mapping = {
            "completed": "mission_completed",
            "failed": "mission_failed",
            "pending_approval": "approval_required",
        }
        return mapping.get(status, "mission_unknown")

    @staticmethod
    def _build_outcome(chosen_path: str, status: str, result: Optional[Dict[str, Any]]) -> str:
        if status == "completed":
            return f"{chosen_path} completed successfully"
        if status == "failed":
            return f"{chosen_path} failed"
        if status == "pending_approval":
            return f"{chosen_path} pending approval"
        return f"{chosen_path} status: {status}"

    @staticmethod
    def _build_progress(goal: Optional[Dict[str, Any]], plan: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        progress: Dict[str, Any] = {}
        if goal:
            progress["goal_status"] = goal.get("status")
            progress["goal_objective"] = goal.get("objective")
        if plan:
            progress["plan_status"] = plan.get("status")
            progress["plan_objective"] = plan.get("objective")
        return progress

    @staticmethod
    def _build_policy_hints(autonomy_policy: Optional[AutonomyPolicy]) -> Optional[Dict[str, Any]]:
        if autonomy_policy is None:
            return None
        return {
            "autonomy_level": autonomy_policy.autonomy_level,
            "approvers": autonomy_policy.approvers,
            "escalation_path": autonomy_policy.escalation_path,
        }

    @staticmethod
    def _build_suggested_actions(status: str, chosen_path: str) -> List[str]:
        if status == "completed":
            return ["view_result", "create_another"]
        if status == "failed":
            return ["retry", "view_error"]
        if status == "pending_approval":
            return ["approve", "reject"]
        return ["view_details"]

    @classmethod
    def build(
        cls,
        mission: Any,
        decision: Dict[str, Any],
        goal: Optional[Dict[str, Any]] = None,
        plan: Optional[Dict[str, Any]] = None,
        autonomy_policy: Optional[AutonomyPolicy] = None,
    ) -> IntentContent:
        """Build IntentContent from existing DEM state.

        This is a deterministic mapping/normalization. It does not infer new
        business decisions or change the meaning of underlying data.
        """
        status = mission.status
        chosen_path = decision.get("chosen_path", "unknown")
        mission_result = mission.result or {}
        context = decision.get("context", {})
        request_context = context.get("request_context", {})

        intent_type = cls._map_status_to_intent_type(status)
        outcome = cls._build_outcome(chosen_path, status, mission_result)
        progress = cls._build_progress(goal, plan)
        policy_hints = cls._build_policy_hints(autonomy_policy)
        suggested_actions = cls._build_suggested_actions(status, chosen_path)

        content: Dict[str, Any] = {
            "outcome": outcome,
            "result": mission_result,
            "progress": progress,
        }
        if policy_hints:
            content["policy_hints"] = policy_hints

        response_context: Dict[str, Any] = {
            "session_id": mission.context.get("session_id") or request_context.get("session_id"),
            "mission_id": mission.mission_id,
            "goal_id": request_context.get("goal_id"),
            "plan_id": request_context.get("plan_id"),
        }
        response_context = {k: v for k, v in response_context.items() if v is not None}

        return IntentContent(
            intent_type=intent_type,
            content=content,
            context=response_context,
            suggested_actions=suggested_actions,
        )
