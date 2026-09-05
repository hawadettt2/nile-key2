import pytest
import sqlite3
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

from app.agent.decision_engine.engine import ReasoningEngine
from app.agent.insights.extractor import PatternExtractor
from app.agent.goal_evolution import GoalEvolutionHandler, GoalEvolutionSignal
from app.agent.outcome import ExecutionOutcome, OutcomeEvaluator, OutcomeFeedbackLoop
from app.agent.memory.cross_system import recall_cross_system, store_cross_component
from app.agent.memory.sqlite_provider import SQLiteMemoryProvider


class TestDecisionEngineCrossSystemMemory:
    @pytest.mark.asyncio
    async def test_cross_system_memory_included_in_decision(self):
        memory_provider = AsyncMock()
        memory_provider.recall.return_value = [
            {"key": "decision_engine:cross_system_decision:shipping", "value": {"chosen_path": "shipping"}, "memory_type": "cross_system_decision", "importance": 8}
        ]
        engine = ReasoningEngine(memory_provider=memory_provider)
        engine._knowledge_orchestrator = None

        request = {
            "intent": "شحن بضاعة",
            "parameters": {},
            "context": {"user_id": 1},
        }
        result = await engine.reason("session-1", request)
        assert "memories" in result["context"]
        memory_keys = [m.get("key") for m in result["context"]["memories"] if isinstance(m, dict)]
        assert any("cross_system_decision" in str(k) for k in memory_keys)

    @pytest.mark.asyncio
    async def test_cross_system_store_in_decision(self):
        memory_provider = AsyncMock()
        memory_provider.store.return_value = "memory-123"
        engine = ReasoningEngine(memory_provider=memory_provider)
        engine._knowledge_orchestrator = None

        request = {
            "intent": "شحن بضاعة",
            "parameters": {},
            "context": {"user_id": 1},
        }
        result = await engine.reason("session-1", request)
        store_calls = [call for call in memory_provider.store.call_args_list]
        cross_system_calls = [
            call for call in store_calls
            if call.kwargs.get("key", "").startswith("decision_engine:") or (call.args and str(call.args[2]).startswith("decision_engine:"))
        ]
        assert len(cross_system_calls) >= 1


class TestInsightsCrossComponentMemory:
    @pytest.mark.asyncio
    async def test_cross_component_memory_recalled_in_insights(self, tmp_path):
        db_path = str(tmp_path / "test_insights.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                status TEXT
            )
        """)
        conn.execute("INSERT INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)", ("session-1", 1, "active"))
        conn.commit()
        conn.close()

        provider = SQLiteMemoryProvider(db_path=db_path)
        await provider.store(
            1,
            "session-1",
            "insights:cross_component_pattern:workflow",
            {"pattern": "success"},
            memory_type="cross_component",
        )

        extractor = PatternExtractor()
        patterns = extractor.extract(
            memory_provider=provider,
            user_id=1,
            session_id="session-1",
        )
        evidence_sources = [e.get("source") for e in patterns.evidence]
        assert "cross_component_memory" in evidence_sources

    @pytest.mark.asyncio
    async def test_cross_component_memory_none_provider(self):
        extractor = PatternExtractor()
        patterns = extractor.extract(
            memory_provider=None,
            user_id=1,
            session_id="session-1",
        )
        assert patterns.evidence == []


class TestGoalEvolutionCrossComponentMemory:
    @pytest.mark.asyncio
    async def test_goal_evolution_stores_cross_component(self):
        memory_provider = AsyncMock()
        memory_provider.store.return_value = "memory-123"

        goal_manager = MagicMock()
        goal_repo = MagicMock()
        plan_planner = MagicMock()
        plan_manager = MagicMock()
        plan_repo = MagicMock()
        evaluator = GoalEvolutionHandler(
            goal_manager=goal_manager,
            goal_repository=goal_repo,
            plan_planner=plan_planner,
            plan_manager=plan_manager,
            plan_repository=plan_repo,
            memory_provider=memory_provider,
        )
        goal = MagicMock()
        goal.goal_id = "goal-1"
        goal.status = "active"
        goal.metadata = {"execution_history": [{"status": "failure"}]}
        goal_repo.get.return_value = goal

        plan = MagicMock()
        plan.plan_id = "plan-1"
        plan.missions = []
        plan.metadata = {}
        plan_repo.get.return_value = plan
        plan_planner.plan.return_value = {"missions": []}

        new_plan = MagicMock()
        new_plan.plan_id = "plan-2"
        plan_manager.create_plan.return_value = new_plan
        plan_manager.create_missions.return_value = []

        result = evaluator.execute(
            "goal-1",
            user_id=1,
            session_id="session-1",
            signal=GoalEvolutionSignal(
                goal_id="goal-1",
                decision="evolve",
                reason="test",
                evidence={},
                proposed_changes={},
            ),
        )
        store_calls = memory_provider.store.call_args_list
        cross_component_calls = [
            call for call in store_calls
            if call.args and str(call.args[3]).startswith("goal_evolution:")
        ]
        assert len(cross_component_calls) >= 1


class TestOutcomeFeedbackCrossComponentMemory:
    @pytest.mark.asyncio
    async def test_outcome_feedback_stores_cross_component(self):
        memory_provider = AsyncMock()
        memory_provider.store.return_value = "memory-123"

        feedback_loop = OutcomeFeedbackLoop(
            goal_repository=MagicMock(),
            plan_repository=MagicMock(),
            session_manager=MagicMock(),
            audit_recorder=MagicMock(),
            memory_provider=memory_provider,
        )

        outcome = ExecutionOutcome(
            execution_output={"mission_status": "completed", "results": []},
            mission_id="mission-1",
            session_id="session-1",
            goal_id="goal-1",
            plan_id="plan-1",
        )
        outcome.status = "success"
        outcome.evaluation = {}
        outcome.feedback = {}
        outcome.outcome_timestamp = datetime.now(timezone.utc)

        result = await feedback_loop.process(outcome, goal_plan_context={"user_id": 1, "goal_id": "goal-1", "plan_id": "plan-1"})
        store_calls = memory_provider.store.call_args_list
        cross_component_calls = [
            call for call in store_calls
            if call.args and str(call.args[3]).startswith("outcome_feedback:")
        ]
        assert len(cross_component_calls) >= 1


class TestMemoryGracefulDegradation:
    @pytest.mark.asyncio
    async def test_recall_with_failing_provider(self):
        memory_provider = AsyncMock()
        memory_provider.recall.side_effect = Exception("DB error")

        memories = await recall_cross_system(
            memory_provider=memory_provider,
            user_id=1,
            session_id="session-1",
            system_name="decision_engine",
            query="test",
        )
        assert memories == []

    @pytest.mark.asyncio
    async def test_store_with_failing_provider(self):
        memory_provider = AsyncMock()
        memory_provider.store.side_effect = Exception("DB error")

        memory_id = await store_cross_component(
            memory_provider=memory_provider,
            user_id=1,
            session_id="session-1",
            component_name="insights",
            key="key1",
            value="value1",
        )
        assert memory_id == ""


class TestMemoryNoLeakageBetweenUsers:
    @pytest.mark.asyncio
    async def test_cross_session_recall_does_not_leak_between_users(self, tmp_path):
        db_path = str(tmp_path / "test_leakage.db")
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER,
                status TEXT
            )
        """)
        conn.execute("INSERT INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)", ("session-1", 1, "active"))
        conn.execute("INSERT INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)", ("session-2", 2, "active"))
        conn.commit()
        conn.close()

        provider = SQLiteMemoryProvider(db_path=db_path)
        await provider.store(1, "session-1", "cross_session_context", {"secret": "user1"})
        await provider.store(2, "session-2", "cross_session_context", {"secret": "user2"})

        memories_user1 = await recall_cross_session(
            memory_provider=provider,
            user_id=1,
            current_session_id="session-3",
            query="cross_session_context",
            limit=10,
        )
        memories_user2 = await recall_cross_session(
            memory_provider=provider,
            user_id=2,
            current_session_id="session-4",
            query="cross_session_context",
            limit=10,
        )

        assert len(memories_user1) == 1
        assert len(memories_user2) == 1
        assert memories_user1[0]["value"]["secret"] == "user1"
        assert memories_user2[0]["value"]["secret"] == "user2"
