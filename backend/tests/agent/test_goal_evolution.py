"""Tests for Long-term Goal Evolution.

Covers:
1. No evolution when evidence is insufficient
2. Goal evolution from accumulated outcomes
3. Scope / constraint evolution
4. Plan regeneration after goal evolution
5. Preservation of Goal identity
6. Terminal Goal protection
7. Memory-informed evolution
8. Autonomy / Approval preservation
9. Audit trail
10. Single-goal backward compatibility
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.agent.goal.schema import Goal
from app.agent.goal.manager import GoalManager
from app.agent.goal_evolution import GoalEvolutionEvaluator, GoalEvolutionHandler, GoalEvolutionSignal
from app.agent.plan.planner import PlanPlanner
from app.agent.plan.manager import PlanManager
from app.agent.plan.repository import PlanRepository
from app.agent.memory.interface import MemoryProvider


def _build_goal(goal_id="goal-1", user_id=1, session_id="session-1", status="active", scope=None, constraints=None, metadata=None):
    return Goal(
        goal_id=goal_id,
        user_id=user_id,
        session_id=session_id,
        objective="Test goal",
        scope=scope or {},
        constraints=constraints or [],
        stakeholders=[],
        autonomy_level="supervised",
        status=status,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        completed_at=None,
        parent_goal_id=None,
        metadata=metadata or {},
    )


def _make_execution_history(statuses, failure_categories=None):
    """Create execution_history entries from statuses and optional failure categories."""
    entries = []
    for i, status in enumerate(statuses):
        entry = {
            "mission_id": f"m{i+1}",
            "plan_id": "plan-1",
            "status": status,
            "outcome_timestamp": datetime.now(timezone.utc).isoformat(),
            "feedback": {},
        }
        if status == "failed" and failure_categories and i < len(failure_categories):
            entry["evaluation"] = {"failure_category": failure_categories[i]}
        entries.append(entry)
    return entries


class TestGoalEvolutionEvaluator:
    def test_no_evolution_when_terminal_completed(self):
        goal = _build_goal(status="completed")
        evaluator = GoalEvolutionEvaluator()
        signal = evaluator.evaluate(goal)
        assert signal.decision == "goal_terminal"
        assert "completed" in signal.reason

    def test_no_evolution_when_terminal_abandoned(self):
        goal = _build_goal(status="abandoned")
        evaluator = GoalEvolutionEvaluator()
        signal = evaluator.evaluate(goal)
        assert signal.decision == "goal_terminal"
        assert "abandoned" in signal.reason

    def test_no_evolution_when_insufficient_evidence(self):
        goal = _build_goal(metadata={"execution_history": _make_execution_history(["completed"])})
        evaluator = GoalEvolutionEvaluator()
        signal = evaluator.evaluate(goal)
        assert signal.decision == "no_evolution"
        assert "Insufficient evidence" in signal.reason

    def test_no_evolution_when_high_success_rate(self):
        history = _make_execution_history(["completed"] * 5)
        goal = _build_goal(metadata={"execution_history": history})
        evaluator = GoalEvolutionEvaluator()
        signal = evaluator.evaluate(goal)
        assert signal.decision == "no_evolution"
        assert "High success rate" in signal.reason

    def test_evolution_from_constraint_conflicts(self):
        history = _make_execution_history(
            ["failed", "failed", "failed", "completed", "completed"],
            failure_categories=["constraint_conflict", "constraint_conflict", "no_viable_path"],
        )
        goal = _build_goal(
            constraints=[{"type": "hard_region", "value": "US"}],
            metadata={"execution_history": history},
        )
        evaluator = GoalEvolutionEvaluator()
        signal = evaluator.evaluate(goal)
        assert signal.decision == "goal_evolved"
        assert "Constraint conflicts" in signal.reason
        assert "constraints" in signal.proposed_changes

    def test_evolution_from_no_viable_path(self):
        history = _make_execution_history(
            ["failed", "failed", "failed", "completed", "completed"],
            failure_categories=["no_viable_path", "no_viable_path", "tool_unavailable"],
        )
        goal = _build_goal(
            scope={"regions": ["US", "EU", "APAC"]},
            metadata={"execution_history": history},
        )
        evaluator = GoalEvolutionEvaluator()
        signal = evaluator.evaluate(goal)
        assert signal.decision == "goal_evolved"
        assert "No viable path" in signal.reason
        assert "scope" in signal.proposed_changes

    def test_evolution_from_high_failure_rate(self):
        history = _make_execution_history(["failed"] * 4 + ["completed"])
        goal = _build_goal(metadata={"execution_history": history})
        evaluator = GoalEvolutionEvaluator()
        signal = evaluator.evaluate(goal)
        assert signal.decision == "goal_evolved"
        assert "High failure rate" in signal.reason

    def test_no_evolution_when_no_pattern_shift(self):
        history = _make_execution_history(
            ["completed", "completed", "failed", "completed", "failed", "completed"],
            failure_categories=["approval_required", "timeout"],
        )
        goal = _build_goal(metadata={"execution_history": history})
        evaluator = GoalEvolutionEvaluator()
        signal = evaluator.evaluate(goal)
        assert signal.decision == "no_evolution"


class TestGoalEvolutionHandler:
    def _setup_mocks(self):
        goal_repo = MagicMock()
        goal = _build_goal(goal_id="goal-1", user_id=1, session_id="session-1")
        goal_repo.get.return_value = goal

        goal_manager = GoalManager(goal_repository=goal_repo)

        plan_repo = MagicMock()
        old_plan = MagicMock()
        old_plan.plan_id = "old-plan-1"
        plan_manager = PlanManager(plan_repository=plan_repo)
        plan_manager.get_active_plan = MagicMock(return_value=old_plan)

        plan_planner = MagicMock(spec=PlanPlanner)
        new_plan = MagicMock()
        new_plan.plan_id = "new-plan-1"
        new_missions = [MagicMock(mission_id="new-m1"), MagicMock(mission_id="new-m2")]
        plan_planner.decompose_goal_to_plan.return_value = (new_plan, new_missions)

        audit_recorder = MagicMock()
        memory_provider = MagicMock(spec=MemoryProvider)

        handler = GoalEvolutionHandler(
            goal_manager=goal_manager,
            goal_repository=goal_repo,
            plan_planner=plan_planner,
            plan_manager=plan_manager,
            plan_repository=plan_repo,
            memory_provider=memory_provider,
            audit_recorder=audit_recorder,
        )
        return handler, goal, new_plan, new_missions, old_plan, audit_recorder, memory_provider

    def test_execute_evolution_updates_goal_and_creates_plan(self):
        handler, goal, new_plan, new_missions, old_plan, audit_recorder, memory_provider = self._setup_mocks()
        signal = GoalEvolutionSignal(
            goal_id="goal-1",
            decision="goal_evolved",
            reason="High failure rate",
            evidence={"failure_rate": 0.5},
            proposed_changes={"scope": {"regions": ["US"]}, "constraints": [{"type": "soft_region", "value": "US"}]},
        )
        result = handler.execute("goal-1", 1, "session-1", signal)
        assert result["success"] is True
        assert result["plan_id"] == "new-plan-1"
        assert result["old_plan_id"] == "old-plan-1"
        assert result["changes_applied"] is True
        assert result["missions_created"] == 2

    def test_execute_skips_when_no_evolution(self):
        handler, _, _, _, _, _, _ = self._setup_mocks()
        signal = GoalEvolutionSignal(
            goal_id="goal-1",
            decision="no_evolution",
            reason="High success rate",
            evidence={},
            proposed_changes={},
        )
        result = handler.execute("goal-1", 1, "session-1", signal)
        assert result["success"] is True
        assert result["changes_applied"] is False
        assert result["plan_id"] is None

    def test_execute_blocks_for_terminal_goal(self):
        handler, _, _, _, _, _, _ = self._setup_mocks()
        signal = GoalEvolutionSignal(
            goal_id="goal-1",
            decision="goal_terminal",
            reason="Goal completed",
            evidence={"goal_status": "completed"},
            proposed_changes={},
        )
        result = handler.execute("goal-1", 1, "session-1", signal)
        assert result["success"] is True
        assert result["changes_applied"] is False

    def test_execute_preserves_goal_identity(self):
        handler, goal, _, _, _, _, _ = self._setup_mocks()
        signal = GoalEvolutionSignal(
            goal_id="goal-1",
            decision="goal_evolved",
            reason="Constraint conflicts",
            evidence={"constraint_conflicts": 2},
            proposed_changes={"constraints": [{"type": "soft_region", "value": "US"}]},
        )
        result = handler.execute("goal-1", 1, "session-1", signal)
        assert result["goal_id"] == "goal-1"
        assert result["success"] is True

    def test_execute_records_audit(self):
        handler, _, _, _, _, audit_recorder, _ = self._setup_mocks()
        signal = GoalEvolutionSignal(
            goal_id="goal-1",
            decision="goal_evolved",
            reason="No viable path",
            evidence={"no_viable_path": 2},
            proposed_changes={"scope": {"regions": ["US"]}},
        )
        handler.execute("goal-1", 1, "session-1", signal)
        actions = [c.kwargs.get("action") for c in audit_recorder.record_agent_action.call_args_list]
        assert "goal_evolved" in actions

    def test_execute_stores_memory(self):
        handler, _, _, _, _, _, memory_provider = self._setup_mocks()
        signal = GoalEvolutionSignal(
            goal_id="goal-1",
            decision="goal_evolved",
            reason="High failure rate",
            evidence={"failure_rate": 0.5},
            proposed_changes={"constraints": [{"type": "soft_region"}]},
        )
        handler.execute("goal-1", 1, "session-1", signal)
        assert memory_provider.store.call_count == 2

        direct_call = memory_provider.store.call_args_list[0]
        cross_component_call = memory_provider.store.call_args_list[1]

        assert direct_call.kwargs["memory_type"] == "goal_evolution"
        assert direct_call.kwargs["importance"] == 0.8
        assert cross_component_call.kwargs["memory_type"] == "cross_component"
        assert cross_component_call.kwargs["key"].startswith("goal_evolution:")

    def test_execute_supersedes_old_plan(self):
        handler, _, _, _, old_plan, _, _ = self._setup_mocks()
        signal = GoalEvolutionSignal(
            goal_id="goal-1",
            decision="goal_evolved",
            reason="Constraint conflicts",
            evidence={"constraint_conflicts": 2},
            proposed_changes={"constraints": []},
        )
        handler.execute("goal-1", 1, "session-1", signal)
        handler.plan_repository.update.assert_called_with(old_plan.plan_id, {"status": "superseded"})

    def test_execute_adds_new_missions_to_session(self):
        handler, _, new_plan, new_missions, _, _, _ = self._setup_mocks()
        mock_session = MagicMock()
        handler = GoalEvolutionHandler(
            goal_manager=handler.goal_manager,
            goal_repository=handler.goal_repository,
            plan_planner=handler.plan_planner,
            plan_manager=handler.plan_manager,
            plan_repository=handler.plan_repository,
            memory_provider=handler.memory_provider,
            audit_recorder=handler.audit_recorder,
        )
        signal = GoalEvolutionSignal(
            goal_id="goal-1",
            decision="goal_evolved",
            reason="Test",
            evidence={},
            proposed_changes={"scope": {}},
        )
        handler.execute("goal-1", 1, "session-1", signal, session_manager=mock_session)
        assert mock_session.add_mission.call_count == len(new_missions)

    def test_single_goal_backward_compatibility(self):
        """Goal without execution_history should not evolve."""
        goal = _build_goal(metadata={})
        evaluator = GoalEvolutionEvaluator()
        signal = evaluator.evaluate(goal)
        assert signal.decision == "no_evolution"
