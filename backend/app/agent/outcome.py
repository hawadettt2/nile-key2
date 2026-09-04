from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


class ExecutionOutcome:
    """Structured execution outcome for traceability and feedback loop."""

    def __init__(
        self,
        execution_output: Dict[str, Any],
        mission_id: str,
        session_id: str,
        goal_id: Optional[str] = None,
        plan_id: Optional[str] = None,
    ):
        self.execution_output = execution_output or {}
        self.mission_id = mission_id
        self.session_id = session_id
        self.goal_id = goal_id
        self.plan_id = plan_id
        self.outcome_timestamp = datetime.now(timezone.utc)
        self.status = "unknown"
        self.evaluation: Dict[str, Any] = {}
        self.feedback: Dict[str, Any] = {}
        self.audit_events: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "session_id": self.session_id,
            "goal_id": self.goal_id,
            "plan_id": self.plan_id,
            "status": self.status,
            "evaluation": self.evaluation,
            "feedback": self.feedback,
            "outcome_timestamp": self.outcome_timestamp.isoformat(),
            "execution_output": self.execution_output,
            "audit_events": self.audit_events,
        }


class OutcomeEvaluator:
    """Evaluate execution outcomes deterministically.

    Produces structured outcome, evaluation, and feedback
    for the next AI cycle without invoking LLM as final decision maker.
    """

    def evaluate(self, outcome: ExecutionOutcome) -> ExecutionOutcome:
        mission_status = self._safe_mission_status(outcome.execution_output)
        degraded = bool(outcome.execution_output.get("degraded"))
        failed_task_id = outcome.execution_output.get("failed_task_id")
        failure_summary = outcome.execution_output.get("failure_summary") or {}

        if mission_status == "completed" and not degraded:
            outcome.status = "success"
        elif mission_status == "completed" and degraded:
            outcome.status = "partial"
        elif mission_status == "pending_approval":
            outcome.status = "partial"
        elif mission_status == "failed":
            outcome.status = "failure"
        else:
            outcome.status = "unknown"

        outcome.evaluation = {
            "mission_status": mission_status,
            "degraded": degraded,
            "failed_task_id": failed_task_id,
            "failure_category": self._categorize_failure(failure_summary),
            "task_success_count": len(outcome.execution_output.get("results") or []),
            "has_feedback_signal": bool(failed_task_id or failure_summary),
        }

        outcome.feedback = self._build_feedback(outcome)
        return outcome

    def _safe_mission_status(self, execution_output: Dict[str, Any]) -> str:
        status = execution_output.get("mission_status")
        if isinstance(status, str):
            return status.lower()
        return "failed"

    def _categorize_failure(self, failure_summary: Dict[str, Any]) -> str:
        if not failure_summary:
            return "none"
        error = (failure_summary.get("error") or "").lower()
        if "approval" in error:
            return "approval_required"
        if "timeout" in error:
            return "timeout"
        if "not found" in error or "tool" in error:
            return "tool_unavailable"
        if "dependency" in error:
            return "dependency_issue"
        return "unknown"

    def _build_feedback(self, outcome: ExecutionOutcome) -> Dict[str, Any]:
        evaluation = outcome.evaluation
        failed_task_id = evaluation.get("failed_task_id")
        failure_category = evaluation.get("failure_category")
        feedback: Dict[str, Any] = {
            "status": outcome.status,
            "failure_category": failure_category,
            "actionable": outcome.status in ("failure", "partial"),
            "suggested_actions": [],
            "blocked_paths": [],
            "preserve_signals": [],
        }

        if outcome.status == "success":
            feedback["suggested_actions"] = ["continue_current_path"]
            feedback["preserve_signals"] = ["execution_trace", "results"]
        elif outcome.status == "partial":
            feedback["suggested_actions"] = ["review_failed_tasks", "consider_retry"]
            feedback["preserve_signals"] = ["execution_trace", "results", "failed_task_id"]
        elif outcome.status == "failure":
            if failure_category == "approval_required":
                feedback["suggested_actions"] = ["await_approval", "do_not_retry_without_approval"]
                feedback["blocked_paths"] = [outcome.execution_output.get("chosen_path")]
            elif failure_category == "tool_unavailable":
                feedback["suggested_actions"] = ["replan_with_alternative_tools"]
                feedback["blocked_paths"] = []
            elif failure_category == "dependency_issue":
                feedback["suggested_actions"] = ["review_dependencies", "replan_affected_mission"]
            else:
                feedback["suggested_actions"] = ["investigate_failure", "replan_if_needed"]
            feedback["preserve_signals"] = ["execution_trace", "failure_summary"]

        return feedback


class OutcomeFeedbackLoop:
    """Update Goal/Plan/Decision/Session context from execution outcome.

    Maintains auditability and preserves autonomy/approval constraints.
    Does not create replacement Goals.
    """

    def __init__(
        self,
        goal_repository,
        plan_repository,
        session_manager,
        audit_recorder,
    ):
        self.goal_repository = goal_repository
        self.plan_repository = plan_repository
        self.session_manager = session_manager
        self.audit_recorder = audit_recorder

    def process(
        self,
        outcome: ExecutionOutcome,
        goal_plan_context: Optional[Dict[str, Any]] = None,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        goal_plan_context = goal_plan_context if goal_plan_context is not None else {}
        session_context = session_context if session_context is not None else {}
        feedback = outcome.feedback
        evaluation = outcome.evaluation

        self._update_session_context(outcome, session_context)
        self._update_goal_metadata(outcome, goal_plan_context)
        self._update_plan_metadata(outcome, goal_plan_context)
        self._record_audit(outcome)

        return {
            "outcome": outcome.to_dict(),
            "updated_session_context": session_context,
            "updated_goal_plan_context": goal_plan_context,
        }

    def _update_session_context(self, outcome: ExecutionOutcome, session_context: Dict[str, Any]) -> None:
        if not self.session_manager:
            return

        history = session_context.get("execution_history", [])
        history.append(
            {
                "mission_id": outcome.mission_id,
                "session_id": outcome.session_id,
                "goal_id": outcome.goal_id,
                "plan_id": outcome.plan_id,
                "status": outcome.status,
                "outcome_timestamp": outcome.outcome_timestamp.isoformat(),
                "feedback": outcome.feedback,
                "evaluation": outcome.evaluation,
            }
        )
        session_context["execution_history"] = history[-50:]
        session_context["last_execution_status"] = outcome.status
        session_context["last_execution_feedback"] = outcome.feedback
        session_context["updated_at"] = datetime.now(timezone.utc).isoformat()

        if self.session_manager:
            try:
                self.session_manager.update_context(outcome.session_id, session_context)
            except Exception:
                pass

    def _update_goal_metadata(self, outcome: ExecutionOutcome, goal_plan_context: Dict[str, Any]) -> None:
        if not self.goal_repository or not goal_plan_context.get("goal_id"):
            return

        goal_id = goal_plan_context["goal_id"]
        goal = self.goal_repository.get(goal_id)
        if not goal:
            return

        history = goal.metadata.get("execution_history", []) if isinstance(goal.metadata, dict) else []
        history.append(
            {
                "mission_id": outcome.mission_id,
                "plan_id": outcome.plan_id,
                "status": outcome.status,
                "outcome_timestamp": outcome.outcome_timestamp.isoformat(),
                "feedback": outcome.feedback,
            }
        )
        updates = {
            "metadata": {
                **goal.metadata,
                "execution_history": history[-50:],
                "last_execution_status": outcome.status,
                "last_outcome_timestamp": outcome.outcome_timestamp.isoformat(),
            }
        }
        try:
            self.goal_repository.update(goal_id, updates)
        except Exception:
            pass

    def _update_plan_metadata(self, outcome: ExecutionOutcome, goal_plan_context: Dict[str, Any]) -> None:
        if not self.plan_repository or not goal_plan_context.get("plan_id"):
            return

        plan_id = goal_plan_context["plan_id"]
        plan = self.plan_repository.get(plan_id)
        if not plan:
            return

        history = plan.metadata.get("execution_history", []) if isinstance(plan.metadata, dict) else []
        history.append(
            {
                "mission_id": outcome.mission_id,
                "status": outcome.status,
                "outcome_timestamp": outcome.outcome_timestamp.isoformat(),
                "feedback": outcome.feedback,
            }
        )
        updates = {
            "metadata": {
                **plan.metadata,
                "execution_history": history[-50:],
                "last_execution_status": outcome.status,
                "last_outcome_timestamp": outcome.outcome_timestamp.isoformat(),
            }
        }
        try:
            self.plan_repository.update(plan_id, updates)
        except Exception:
            pass

    def _record_audit(self, outcome: ExecutionOutcome) -> None:
        if not self.audit_recorder:
            return

        try:
            self.audit_recorder.record_agent_action(
                session_id=outcome.session_id,
                agent_id="system",
                action="execution_outcome",
                input_data={
                    "mission_id": outcome.mission_id,
                    "goal_id": outcome.goal_id,
                    "plan_id": outcome.plan_id,
                },
                output_data={
                    "status": outcome.status,
                    "evaluation": outcome.evaluation,
                    "feedback": outcome.feedback,
                    "outcome_timestamp": outcome.outcome_timestamp.isoformat(),
                },
            )
        except Exception:
            pass
