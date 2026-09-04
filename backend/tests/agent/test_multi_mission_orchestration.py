import asyncio
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.agent.plan.schema import Plan
from app.agent.schemas.mission import Mission
from app.agent.multi_mission_orchestrator import (
    MissionDependencyGraph,
    MultiMissionOrchestrator,
)


def _build_plan(plan_id, goal_id, session_id, missions, dependencies=None, execution_mode="sequential"):
    mission_ids = [m if isinstance(m, str) else m["mission_id"] for m in missions]
    return Plan(
        plan_id=plan_id, goal_id=goal_id, user_id=1, session_id=session_id,
        objective="Test plan", missions=mission_ids, dependencies=dependencies or [],
        constraints=[], approval_policy={}, fallback_strategy={}, status="active",
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
        completed_at=None, metadata={"execution_mode": execution_mode},
    )


def _build_mission(mission_id, priority=5):
    return Mission(
        mission_id=mission_id, mission_type="SEARCH_ENTITIES",
        objective=f"Mission {mission_id}", priority=priority,
        requester={"user_id": 1, "session_id": "session-1"}, context={}, constraints=[],
        approval_policy={}, execution_policy={}, created_at=datetime.now(timezone.utc),
        correlation_id=mission_id, idempotency_key=mission_id, audit_context={},
        payload={"goal_id": "goal-1", "plan_id": "plan-1"}, status="pending",
    )


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class FakeToolOrchestrator:
    def __init__(self, results):
        self.results = results
        self.calls = []
        self.timings = []

    async def execute(self, mission_data, session_context=None):
        mid = mission_data.get("mission_id") if isinstance(mission_data, dict) else getattr(mission_data, "mission_id", None)
        self.calls.append(mid)
        start = asyncio.get_event_loop().time()
        await asyncio.sleep(0.02)
        end = asyncio.get_event_loop().time()
        self.timings.append((mid, start, end))
        return self.results.get(mid, {
            "execution_trace": [], "mission_status": "completed",
            "results": [{"mission_id": mid, "status": "success"}],
            "failed_task_id": None, "degraded": False, "failure_summary": {},
        })


class TestMissionDependencyGraph:
    def test_ready_when_no_dependencies(self):
        g = MissionDependencyGraph()
        g.add_mission("m1"); g.add_mission("m2")
        assert g.get_ready_missions() == ["m1", "m2"]

    def test_mission_becomes_ready_after_dep_completes(self):
        g = MissionDependencyGraph()
        g.add_mission("m1"); g.add_mission("m2")
        g.add_dependency("m1", "m2")
        assert g.get_ready_missions() == ["m1"]
        g.mark_completed("m1")
        assert g.get_ready_missions() == ["m2"]

    def test_not_ready_with_pending_dependency(self):
        g = MissionDependencyGraph()
        g.add_mission("m1"); g.add_mission("m2")
        g.add_dependency("m1", "m2")
        assert g.is_ready("m2") is False

    def test_ready_sorted_by_priority_descending(self):
        g = MissionDependencyGraph()
        g.add_mission("m1", priority=1); g.add_mission("m2", priority=10); g.add_mission("m3", priority=5)
        assert g.get_ready_missions() == ["m2", "m3", "m1"]

    def test_failure_blocked_set_computed_transitively(self):
        g = MissionDependencyGraph()
        g.add_mission("m1"); g.add_mission("m2"); g.add_mission("m3")
        g.add_dependency("m1", "m2"); g.add_dependency("m2", "m3")
        assert set(g.get_all_blocked_by("m1")) == {"m2", "m3"}

    def test_remove_mission_cleans_all_edges(self):
        g = MissionDependencyGraph()
        g.add_mission("m1"); g.add_mission("m2"); g.add_mission("m3")
        g.add_dependency("m1", "m2"); g.add_dependency("m2", "m3")
        g.remove_mission("m2")
        assert "m2" not in g._missions
        assert "m2" not in g._outgoing.get("m1", [])
        assert "m2" not in g._incoming.get("m3", [])
        assert g.get_ready_missions() == ["m1", "m3"]

    def test_all_completed_true_when_all_done(self):
        g = MissionDependencyGraph()
        g.add_mission("m1")
        assert g.all_completed() is False
        g.mark_completed("m1")
        assert g.all_completed() is True

    def test_load_plan_populates_graph(self):
        missions = [{"mission_id": "m1", "priority": 1}, {"mission_id": "m2", "priority": 2}]
        deps = [{"from": "m1", "to": "m2"}]
        g = MissionDependencyGraph()
        g.load_plan(missions, deps)
        assert g.get_ready_missions() == ["m1"]
        g.mark_completed("m1")
        assert g.get_ready_missions() == ["m2"]


class TestMultiMissionOrchestrator:
    def test_single_mission_plan_executes(self):
        mission = _build_mission("m1")
        plan = _build_plan("plan-1", "goal-1", "session-1", ["m1"])
        fake = FakeToolOrchestrator({"m1": {"mission_status": "completed", "results": [{"x": 1}]}})
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake)
        outcome = _run(orchestrator.execute_plan(plan, {"m1": mission.model_dump()}))
        assert outcome.status == "completed"
        assert outcome.mission_outcomes["m1"].status == "completed"
        assert fake.calls == ["m1"]

    def test_dependency_ordering_sequential(self):
        ma = _build_mission("m-a"); mb = _build_mission("m-b")
        plan = _build_plan("plan-1", "goal-1", "session-1",
            [ma.model_dump(), mb.model_dump()], dependencies=[{"from": "m-a", "to": "m-b"}])
        fake = FakeToolOrchestrator({
            "m-a": {"mission_status": "completed", "results": [{"x": 1}]},
            "m-b": {"mission_status": "completed", "results": [{"y": 2}]},
        })
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake)
        outcome = _run(orchestrator.execute_plan(plan, {"m-a": ma.model_dump(), "m-b": mb.model_dump()}))
        assert fake.calls == ["m-a", "m-b"]
        assert outcome.status == "completed"

    def test_parallel_execution_independent_missions(self):
        ids = ["m1", "m2", "m3"]
        missions = {mid: _build_mission(mid).model_dump() for mid in ids}
        plan = _build_plan("plan-1", "goal-1", "session-1", ids, execution_mode="parallel")
        fake = FakeToolOrchestrator({mid: {"mission_status": "completed", "results": [{"id": mid}]} for mid in ids})
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake)
        outcome = _run(orchestrator.execute_plan(plan, missions))
        assert set(fake.calls) == set(ids)
        starts = [t[1] for t in fake.timings]
        assert max(starts) - min(starts) < 0.05
        assert outcome.status == "completed"

    def test_blocking_when_dependency_not_met(self):
        ma = _build_mission("m-a"); mb = _build_mission("m-b")
        plan = _build_plan("plan-1", "goal-1", "session-1",
            [ma.model_dump(), mb.model_dump()], dependencies=[{"from": "m-a", "to": "m-b"}])
        fake = FakeToolOrchestrator({
            "m-a": {"mission_status": "failed", "results": [], "failed_task_id": "t1", "failure_summary": {"error": "tool not found"}},
        })
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake)
        outcome = _run(orchestrator.execute_plan(plan, {"m-a": ma.model_dump(), "m-b": mb.model_dump()}))
        assert fake.calls == ["m-a"]
        assert outcome.mission_outcomes["m-b"].status == "blocked"
        assert outcome.status == "failed"

    def test_success_propagation_to_dependents(self):
        ma = _build_mission("m-a"); mb = _build_mission("m-b")
        plan = _build_plan("plan-1", "goal-1", "session-1",
            [ma.model_dump(), mb.model_dump()], dependencies=[{"from": "m-a", "to": "m-b"}])
        fake = FakeToolOrchestrator({
            "m-a": {"mission_status": "completed", "results": [{"x": 1}]},
            "m-b": {"mission_status": "completed", "results": [{"y": 2}]},
        })
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake)
        outcome = _run(orchestrator.execute_plan(plan, {"m-a": ma.model_dump(), "m-b": mb.model_dump()}))
        assert fake.calls == ["m-a", "m-b"]
        assert outcome.status == "completed"

    def test_failure_propagates_transitively(self):
        ma = _build_mission("m-a"); mb = _build_mission("m-b"); mc = _build_mission("m-c")
        plan = _build_plan("plan-1", "goal-1", "session-1",
            [ma.model_dump(), mb.model_dump(), mc.model_dump()],
            dependencies=[{"from": "m-a", "to": "m-b"}, {"from": "m-b", "to": "m-c"}])
        fake = FakeToolOrchestrator({
            "m-a": {"mission_status": "completed", "results": [{"x": 1}]},
            "m-b": {"mission_status": "failed", "results": [], "failed_task_id": "t1", "failure_summary": {"error": "tool not found"}},
        })
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake)
        outcome = _run(orchestrator.execute_plan(plan, {
            "m-a": ma.model_dump(), "m-b": mb.model_dump(), "m-c": mc.model_dump(),
        }))
        assert fake.calls == ["m-a", "m-b"]
        assert outcome.mission_outcomes["m-b"].status == "failed"
        assert outcome.mission_outcomes["m-c"].status == "blocked"
        assert outcome.status == "failed"

    def test_plan_level_outcome_aggregation(self):
        ids = ["m1", "m2", "m3"]
        missions = {mid: _build_mission(mid).model_dump() for mid in ids}
        plan = _build_plan("plan-1", "goal-1", "session-1", ids)
        fake = FakeToolOrchestrator({mid: {"mission_status": "completed", "results": [{"id": mid}]} for mid in ids})
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake)
        outcome = _run(orchestrator.execute_plan(plan, missions))
        assert outcome.status == "completed"
        assert len(outcome.aggregated_results) == 3
        assert outcome.execution_metadata["completed_count"] == 3
        assert outcome.execution_metadata["total_missions"] == 3

    def test_audit_trail_recorded(self):
        mission = _build_mission("m1")
        plan = _build_plan("plan-1", "goal-1", "session-1", ["m1"])
        fake = FakeToolOrchestrator({"m1": {"mission_status": "completed", "results": [{"x": 1}]}})
        audit_recorder = MagicMock()
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake, audit_recorder=audit_recorder)
        _run(orchestrator.execute_plan(plan, {"m1": mission.model_dump()}, session_context={"session_id": "session-1"}))
        actions = [c.kwargs.get("action") for c in audit_recorder.record_agent_action.call_args_list]
        assert "mission_started" in actions
        assert "mission_completed" in actions

    def test_replanning_triggered_on_mission_failure(self):
        mission = _build_mission("m1")
        plan = _build_plan("plan-1", "goal-1", "session-1", ["m1"])
        fake = FakeToolOrchestrator({
            "m1": {"mission_status": "failed", "results": [], "failed_task_id": "t1", "failure_summary": {"error": "no_viable_path"}},
        })
        replanning_handler = MagicMock()
        replanning_handler.execute.return_value = {"success": True, "new_plan_id": "plan-2"}
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake, replanning_handler=replanning_handler)
        outcome = _run(orchestrator.execute_plan_with_feedback(
            plan, {"m1": mission.model_dump()},
            session_context={"session_id": "session-1"},
            goal_plan_context={"goal_id": "goal-1", "plan_id": "plan-1", "user_id": 1},
        ))
        assert outcome.status == "failed"
        replanning_handler.execute.assert_called_once()

    def test_approval_pending_preserved(self):
        mission = _build_mission("m1")
        plan = _build_plan("plan-1", "goal-1", "session-1", ["m1"])
        fake = FakeToolOrchestrator({
            "m1": {"mission_status": "pending_approval", "results": [], "failure_summary": {"error": "approval_required"}},
        })
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake)
        outcome = _run(orchestrator.execute_plan(plan, {"m1": mission.model_dump()}, session_context={"session_id": "session-1"}))
        assert outcome.mission_outcomes["m1"].status == "pending_approval"
        assert outcome.status == "partial"

    def test_circular_dependency_blocks_all(self):
        missions = {mid: _build_mission(mid).model_dump() for mid in ["m-a", "m-b", "m-c"]}
        plan = _build_plan("plan-1", "goal-1", "session-1", list(missions.keys()),
            dependencies=[{"from": "m-a", "to": "m-b"}, {"from": "m-b", "to": "m-c"}, {"from": "m-c", "to": "m-a"}])
        fake = FakeToolOrchestrator({})
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake)
        outcome = _run(orchestrator.execute_plan(plan, missions))
        assert fake.calls == []
        assert outcome.status == "partial"

    def test_fallback_strategy_executes_on_primary_failure(self):
        ma = _build_mission("m-a"); mb = _build_mission("m-b")
        plan = _build_plan("plan-1", "goal-1", "session-1",
            [ma.model_dump(), mb.model_dump()])
        plan.fallback_strategy = {"primary_mission_id": "m-a", "fallback_mission_id": "m-b", "activation_condition": "primary_mission_failed"}
        fake = FakeToolOrchestrator({
            "m-a": {"mission_status": "failed", "results": [], "failed_task_id": "t1", "failure_summary": {"error": "no_viable_path"}},
            "m-b": {"mission_status": "completed", "results": [{"fallback": True}]},
        })
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake)
        outcome = _run(orchestrator.execute_plan(plan, {"m-a": ma.model_dump(), "m-b": mb.model_dump()}))
        assert "m-a" in fake.calls
        assert outcome.mission_outcomes["m-a"].status == "failed"
        assert "m-b" in fake.calls
        assert outcome.mission_outcomes["m-b"].status == "completed"

    def test_priority_ordering_among_ready_missions(self):
        ml = _build_mission("m-low", priority=1)
        mh = _build_mission("m-high", priority=10)
        plan = _build_plan("plan-1", "goal-1", "session-1", [ml.model_dump(), mh.model_dump()])
        fake = FakeToolOrchestrator({
            "m-low": {"mission_status": "completed", "results": [{"id": "low"}]},
            "m-high": {"mission_status": "completed", "results": [{"id": "high"}]},
        })
        orchestrator = MultiMissionOrchestrator(tool_orchestrator=fake)
        _run(orchestrator.execute_plan(plan, {"m-low": ml.model_dump(), "m-high": mh.model_dump()}))
        assert fake.calls == ["m-high", "m-low"]
