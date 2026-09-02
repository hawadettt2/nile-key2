import pytest
from datetime import datetime, timezone

from app.agent.goal.schema import Goal
from app.agent.goal.repository import GoalRepository
from app.agent.goal.manager import GoalManager
from app.core.database import get_db


class TestGoalSchema:
    def test_goal_creation(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="g1",
            user_id=1,
            session_id="s1",
            objective="O1",
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
        assert goal.goal_id == "g1"
        assert goal.status == "active"

    def test_goal_hierarchy(self):
        now = datetime.now(timezone.utc)
        goal = Goal(
            goal_id="g-parent",
            user_id=1,
            session_id="s1",
            objective="Parent",
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
        assert goal.parent_goal_id is None
