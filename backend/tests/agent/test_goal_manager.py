import pytest
from datetime import datetime, timezone

from app.core.database import get_db
from app.agent.goal.schema import Goal
from app.agent.goal.manager import GoalManager
from app.agent.goal.repository import GoalRepository


def _ensure_test_user_and_session():
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO users (id, email, password_hash, full_name, username, role, is_active, approval_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (1, "test@example.com", "hash", "Test", "test", "owner", 1, "approved"))
        db.execute("INSERT OR IGNORE INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)",
                   ("session-1", 1, "active"))
        db.commit()


def test_goal_schema():
    now = datetime.now(timezone.utc)
    goal = Goal(
        goal_id="goal-1",
        user_id=1,
        session_id="session-1",
        objective="Test goal",
        scope={"market": "EG"},
        constraints=[],
        stakeholders=[],
        autonomy_level="supervised",
        status="active",
        created_at=now,
        updated_at=now,
        completed_at=None,
        parent_goal_id=None,
        metadata={},
    )
    assert goal.goal_id == "goal-1"
    assert goal.status == "active"


class TestGoalManager:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.goal_repo = GoalRepository(get_db)
        self.goal_manager = GoalManager(self.goal_repo)

    def test_create_goal(self):
        goal = self.goal_manager.create_goal(
            user_id=1,
            session_id="session-1",
            objective="Test goal",
        )
        assert goal.goal_id is not None
        assert goal.user_id == 1
        assert goal.status == "active"

    def test_get_goal_ownership(self):
        goal = self.goal_manager.create_goal(user_id=1, session_id="session-1", objective="Test")
        fetched = self.goal_manager.get_goal(goal.goal_id, user_id=1)
        assert fetched is not None
        assert fetched.goal_id == goal.goal_id
        wrong = self.goal_manager.get_goal(goal.goal_id, user_id=999)
        assert wrong is None

    def test_list_goals(self):
        self.goal_manager.create_goal(user_id=1, session_id="session-1", objective="G1")
        self.goal_manager.create_goal(user_id=1, session_id="session-1", objective="G2")
        goals = self.goal_manager.list_goals(user_id=1)
        assert len(goals) == 2

    def test_complete_goal(self):
        goal = self.goal_manager.create_goal(user_id=1, session_id="session-1", objective="Test")
        completed = self.goal_manager.complete_goal(goal.goal_id, user_id=1)
        assert completed.status == "completed"
        assert completed.completed_at is not None

    def test_abandon_goal(self):
        goal = self.goal_manager.create_goal(user_id=1, session_id="session-1", objective="Test")
        abandoned = self.goal_manager.abandon_goal(goal.goal_id, user_id=1)
        assert abandoned.status == "abandoned"
