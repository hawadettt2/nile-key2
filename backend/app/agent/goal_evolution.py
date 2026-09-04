"""Long-term Goal Evolution subsystem.

Provides deterministic, evidence-based goal evolution based on accumulated
execution outcomes and operational memory.

Components:
- GoalEvolutionSignal: Result of goal evolution evaluation.
- GoalEvolutionEvaluator: Determines if a Goal needs evolution based on
  execution_history evidence.
- GoalEvolutionHandler: Executes goal evolution by updating scope/constraints
  and regenerating the plan.

Design principles:
- Reuses existing Goal, Plan, Mission, Outcome, Feedback, Memory, Replanning.
- Deterministic rules; LLM is not the final decision maker for state transitions.
- No new abstractions unless strictly necessary.
- Preserves Goal identity unless architecture explicitly requires replacement.
- Respects terminal Goal states (completed, abandoned).
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timezone

from .goal.schema import Goal
from .goal.manager import GoalManager
from .goal.repository import GoalRepository

from .plan.planner import PlanPlanner
from .plan.manager import PlanManager
from .plan.repository import PlanRepository

from .schemas.enums import ExecutionMode
from .schemas.mission import Mission

from .outcome import ExecutionOutcome, OutcomeEvaluator

from .memory.interface import MemoryProvider


class GoalEvolutionSignal:
    """Structured signal indicating whether and how a Goal should evolve."""

    def __init__(
        self,
        goal_id: str,
        decision: str,
        reason: str,
        evidence: Dict[str, Any],
        proposed_changes: Dict[str, Any],
        memory_insights: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.goal_id = goal_id
        self.decision = decision
        self.reason = reason
        self.evidence = evidence
        self.proposed_changes = proposed_changes
        self.memory_insights = memory_insights or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "decision": self.decision,
            "reason": self.reason,
            "evidence": self.evidence,
            "proposed_changes": self.proposed_changes,
            "memory_insights": self.memory_insights,
            "timestamp": self.timestamp,
        }


class GoalEvolutionEvaluator:
    """Deterministic evaluator for long-term goal evolution.

    Evaluates accumulated execution outcomes to determine if a Goal needs
    evolution. Does not modify state; only produces a signal.

    Decision rules:
    - goal_terminal: Goal status is completed or abandoned.
    - no_evolution: Insufficient evidence (< MIN_EVIDENCE_COUNT outcomes).
    - no_evolution: All outcomes successful with no pattern shifts.
    - no_evolution: Outcomes show no consistent directional change.
    - goal_evolved: Sufficient evidence of pattern shift or repeated
      constraint/scope adjustments needed.
    """

    MIN_EVIDENCE_COUNT = 3
    SUCCESS_RATE_THRESHOLD = 0.7
    FAILURE_RATE_THRESHOLD = 0.4
    PATTERN_SHIFT_THRESHOLD = 0.3

    def evaluate(self, goal: Goal) -> GoalEvolutionSignal:
        """Evaluate whether the Goal needs evolution based on execution history.

        Args:
            goal: Goal model with execution_history in metadata.

        Returns:
            GoalEvolutionSignal with decision, reason, evidence, and proposed changes.
        """
        goal_id = goal.goal_id
        status = goal.status
        evidence: Dict[str, Any] = {}
        proposed_changes: Dict[str, Any] = {}

        if status in ("completed", "abandoned"):
            return GoalEvolutionSignal(
                goal_id=goal_id,
                decision="goal_terminal",
                reason=f"Goal is in terminal state: {status}",
                evidence={"goal_status": status},
                proposed_changes={},
            )

        execution_history = self._get_execution_history(goal)
        evidence["execution_history_count"] = len(execution_history)

        if len(execution_history) < self.MIN_EVIDENCE_COUNT:
            return GoalEvolutionSignal(
                goal_id=goal_id,
                decision="no_evolution",
                reason=f"Insufficient evidence: {len(execution_history)} < {self.MIN_EVIDENCE_COUNT} required outcomes",
                evidence=evidence,
                proposed_changes={},
            )

        success_count = sum(1 for entry in execution_history if entry.get("status") == "completed")
        failure_count = sum(1 for entry in execution_history if entry.get("status") == "failed")
        total_count = len(execution_history)
        success_rate = success_count / total_count if total_count > 0 else 0.0
        failure_rate = failure_count / total_count if total_count > 0 else 0.0

        evidence.update({
            "success_count": success_count,
            "failure_count": failure_count,
            "total_count": total_count,
            "success_rate": success_rate,
            "failure_rate": failure_rate,
        })

        if success_rate >= self.SUCCESS_RATE_THRESHOLD:
            return GoalEvolutionSignal(
                goal_id=goal_id,
                decision="no_evolution",
                reason=f"High success rate ({success_rate:.0%}); no evolution needed",
                evidence=evidence,
                proposed_changes={},
            )

        failure_categories = self._extract_failure_categories(execution_history)
        evidence["failure_categories"] = failure_categories

        constraint_conflicts = failure_categories.count("constraint_conflict")
        no_viable_path = failure_categories.count("no_viable_path")
        tool_unavailable = failure_categories.count("tool_unavailable")
        dependency_issue = failure_categories.count("dependency_issue")

        if constraint_conflicts > 0 and constraint_conflicts / max(failure_count, 1) >= self.PATTERN_SHIFT_THRESHOLD:
            proposed_changes["constraints"] = self._relax_constraints(goal.constraints)
            return GoalEvolutionSignal(
                goal_id=goal_id,
                decision="goal_evolved",
                reason=f"Constraint conflicts in {constraint_conflicts} of {failure_count} failures",
                evidence=evidence,
                proposed_changes=proposed_changes,
            )

        if no_viable_path > 0 and no_viable_path / max(failure_count, 1) >= self.PATTERN_SHIFT_THRESHOLD:
            proposed_changes["scope"] = self._narrow_scope(goal.scope)
            return GoalEvolutionSignal(
                goal_id=goal_id,
                decision="goal_evolved",
                reason=f"No viable path in {no_viable_path} of {failure_count} failures",
                evidence=evidence,
                proposed_changes=proposed_changes,
            )

        if tool_unavailable > 0:
            proposed_changes["scope"] = self._adjust_scope_for_tools(goal.scope, tool_unavailable)
            return GoalEvolutionSignal(
                goal_id=goal_id,
                decision="goal_evolved",
                reason=f"Tool unavailable in {tool_unavailable} of {failure_count} failures",
                evidence=evidence,
                proposed_changes=proposed_changes,
            )

        if failure_rate >= self.FAILURE_RATE_THRESHOLD:
            proposed_changes["constraints"] = self._relax_constraints(goal.constraints)
            return GoalEvolutionSignal(
                goal_id=goal_id,
                decision="goal_evolved",
                reason=f"High failure rate ({failure_rate:.0%})",
                evidence=evidence,
                proposed_changes=proposed_changes,
            )

        return GoalEvolutionSignal(
            goal_id=goal_id,
            decision="no_evolution",
            reason="No consistent pattern requiring evolution detected",
            evidence=evidence,
            proposed_changes={},
        )

    def _get_execution_history(self, goal: Goal) -> List[Dict[str, Any]]:
        """Extract execution history from Goal metadata."""
        if isinstance(goal.metadata, dict):
            history = goal.metadata.get("execution_history", [])
            if isinstance(history, list):
                return history
        return []

    def _extract_failure_categories(self, execution_history: List[Dict[str, Any]]) -> List[str]:
        """Extract failure categories from execution history entries."""
        categories: List[str] = []
        for entry in execution_history:
            if entry.get("status") == "failed":
                evaluation = entry.get("evaluation", {})
                category = evaluation.get("failure_category", "unknown")
                if category and category != "unknown":
                    categories.append(category)
        return categories

    def _relax_constraints(self, current_constraints: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Propose relaxed constraints."""
        relaxed = []
        for constraint in current_constraints:
            relaxed_constraint = dict(constraint)
            if "hard" in relaxed_constraint.get("type", "").lower():
                relaxed_constraint["type"] = relaxed_constraint["type"].replace("hard", "soft")
            relaxed.append(relaxed_constraint)
        return relaxed if relaxed else current_constraints

    def _narrow_scope(self, current_scope: Dict[str, Any]) -> Dict[str, Any]:
        """Propose narrowed scope."""
        new_scope = dict(current_scope)
        if "regions" in new_scope and isinstance(new_scope["regions"], list):
            new_scope["regions"] = new_scope["regions"][: max(1, len(new_scope["regions"]) // 2)]
        if "targets" in new_scope and isinstance(new_scope["targets"], list):
            new_scope["targets"] = new_scope["targets"][: max(1, len(new_scope["targets"]) // 2)]
        return new_scope

    def _adjust_scope_for_tools(self, current_scope: Dict[str, Any], tool_failure_count: int) -> Dict[str, Any]:
        """Propose scope adjusted for tool availability."""
        new_scope = dict(current_scope)
        new_scope["_evolution_note"] = f"Scope adjusted due to {tool_failure_count} tool unavailability events"
        return new_scope


class GoalEvolutionHandler:
    """Executes goal evolution by updating the Goal and regenerating the Plan.

    Reuses existing GoalManager, PlanPlanner, PlanManager, and MemoryProvider.
    Records audit events for traceability.
    """

    def __init__(
        self,
        goal_manager: GoalManager,
        goal_repository: GoalRepository,
        plan_planner: PlanPlanner,
        plan_manager: PlanManager,
        plan_repository: PlanRepository,
        memory_provider: Optional[MemoryProvider] = None,
        audit_recorder: Optional[Any] = None,
    ) -> None:
        self.goal_manager = goal_manager
        self.goal_repository = goal_repository
        self.plan_planner = plan_planner
        self.plan_manager = plan_manager
        self.plan_repository = plan_repository
        self.memory_provider = memory_provider
        self.audit_recorder = audit_recorder

    def execute(
        self,
        goal_id: str,
        user_id: int,
        session_id: str,
        signal: GoalEvolutionSignal,
        session_manager: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Execute goal evolution based on the evaluation signal.

        Args:
            goal_id: Target Goal ID.
            user_id: User ID for authorization.
            session_id: Session ID for context.
            signal: GoalEvolutionSignal from GoalEvolutionEvaluator.
            session_manager: Optional SessionManager for adding new missions.

        Returns:
            Dict with success status, goal_id, plan_id, and details.
        """
        if signal.decision != "goal_evolved":
            return {
                "success": True,
                "goal_id": goal_id,
                "plan_id": None,
                "decision": signal.decision,
                "reason": signal.reason,
                "changes_applied": False,
            }

        goal = self.goal_manager.get_goal(goal_id, user_id)
        if not goal:
            return {"success": False, "error": f"Goal {goal_id} not found"}

        if goal.status in ("completed", "abandoned"):
            return {
                "success": False,
                "error": f"Cannot evolve terminal goal: {goal.status}",
                "goal_id": goal_id,
            }

        proposed_changes = signal.proposed_changes
        updates: Dict[str, Any] = {}
        updates["metadata"] = dict(goal.metadata)
        updates["metadata"]["last_evolution"] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": signal.reason,
            "evidence": signal.evidence,
            "proposed_changes": proposed_changes,
        }

        if "scope" in proposed_changes:
            updates["scope"] = proposed_changes["scope"]
        if "constraints" in proposed_changes:
            updates["constraints"] = proposed_changes["constraints"]

        updated_goal = self.goal_manager.update_goal(goal_id, user_id, updates)
        if not updated_goal:
            return {"success": False, "error": f"Failed to update Goal {goal_id}"}

        old_plan = self.plan_manager.get_active_plan(goal_id, user_id)
        old_plan_id = old_plan.plan_id if old_plan else None

        try:
            new_plan, new_missions = self.plan_planner.decompose_goal_to_plan(updated_goal, self.goal_repository)
            self.plan_manager.create_plan(new_plan)
            self.plan_manager.activate_plan(new_plan.plan_id, user_id)

            if old_plan_id:
                self.plan_repository.update(old_plan_id, {"status": "superseded"})

            if session_manager is not None:
                for mission in new_missions:
                    session_manager.add_mission(session_id, mission)
                    self.plan_manager.append_mission(new_plan.plan_id, user_id, mission.mission_id)

            if self.audit_recorder:
                try:
                    self.audit_recorder.record_agent_action(
                        session_id=session_id,
                        agent_id="goal_evolution_handler",
                        action="goal_evolved",
                        input_data={
                            "goal_id": goal_id,
                            "old_plan_id": old_plan_id,
                            "new_plan_id": new_plan.plan_id,
                            "changes": proposed_changes,
                        },
                        output_data={
                            "success": True,
                            "new_plan_id": new_plan.plan_id,
                            "missions_created": len(new_missions),
                        },
                    )
                except Exception:
                    pass

            if self.memory_provider:
                try:
                    self.memory_provider.store(
                        user_id=user_id,
                        session_id=session_id,
                        key=f"goal_evolution_{goal_id}_{new_plan.plan_id}",
                        value={
                            "goal_id": goal_id,
                            "old_plan_id": old_plan_id,
                            "new_plan_id": new_plan.plan_id,
                            "reason": signal.reason,
                            "changes": proposed_changes,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        },
                        memory_type="goal_evolution",
                        importance=0.8,
                        expires_at=None,
                    )
                except Exception:
                    pass

            return {
                "success": True,
                "goal_id": goal_id,
                "plan_id": new_plan.plan_id,
                "old_plan_id": old_plan_id,
                "decision": signal.decision,
                "reason": signal.reason,
                "changes_applied": True,
                "missions_created": len(new_missions),
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Evolution execution failed: {str(exc)}",
                "goal_id": goal_id,
                "changes_applied": False,
            }
