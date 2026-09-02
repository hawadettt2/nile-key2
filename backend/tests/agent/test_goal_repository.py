import pytest
from datetime import datetime, timezone

from app.core.database import get_db
from app.agent.goal.repository import GoalRepository
from app.agent.goal.schema import Goal


def _ensure_test_user_and_session():
    with get_db() as db:
        db.execute("INSERT OR IGNORE INTO users (id, email, password_hash, full_name, username, role, is_active, approval_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (1, "test@example.com", "hash", "Test", "test", "owner", 1, "approved"))
        db.execute("INSERT OR IGNORE INTO agent_sessions (id, user_id, status) VALUES (?, ?, ?)",
                   ("session-1", 1, "active"))
        db.commit()


class TestGoalRepository:
    def setup_method(self):
        _ensure_test_user_and_session()
        self.repo = GoalRepository(get_db)

    def test_create_and_get(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-1",
            user_id=1,
            session_id="session-1",
            objective="Test",
            scope={},
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
        self.repo.create(goal)
        fetched = self.repo.get("goal-1")
        assert fetched is not None
        assert fetched.objective == "Test"

    def test_list_by_user(self):
        now = datetime.now(timezone.utc)
        for i in range(3):
            goal = Goal(
                goal_id=f"goal-{i}",
                user_id=1,
                session_id="session-1",
                objective=f"Goal {i}",
                scope={},
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
            self.repo.create(goal)
        goals = self.repo.list(user_id=1)
        assert len(goals) == 3

    def test_get_active_goals(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-active",
            user_id=1,
            session_id="session-1",
            objective="Active",
            scope={},
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
        self.repo.create(goal)
        active = self.repo.get_active_goals(user_id=1)
        assert len(active) == 1
        assert active[0].goal_id == "goal-active"

    def test_update_goal(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-update",
            user_id=1,
            session_id="session-1",
            objective="Original",
            scope={},
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
        self.repo.create(goal)
        updated = self.repo.update("goal-update", {"objective": "Updated"})
        assert updated.objective == "Updated"

    def test_archive_goal(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="goal-archive",
            user_id=1,
            session_id="session-1",
            objective="Test",
            scope={},
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
        self.repo.create(goal)
        self.repo.archive("goal-archive", "abandoned")
        fetched = self.repo.get("goal-archive")
        assert fetched.status == "abandoned"
