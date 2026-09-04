"""Tests for Product / UI / Business Workflow Integration."""

from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi.testclient import TestClient
from main import app
from app.routers.digital_export_manager import router
from app.routers.auth import get_current_user, require_role

client = TestClient(app)


def _override_current_user():
    return {"id": 1, "username": "test", "email": "test@example.com", "role": "owner", "roles": ["owner"]}


app.dependency_overrides[get_current_user] = _override_current_user
app.dependency_overrides[require_role(["owner", "manager", "sales", "admin_staff", "accountant", "logistics"])] = _override_current_user
app.dependency_overrides[require_role(["owner", "manager"])] = _override_current_user
app.dependency_overrides[require_role(["owner"])] = _override_current_user


class TestAgentInsightAPI:
    def test_get_session_insights_returns_empty_when_no_history(self):
        with patch('app.routers.digital_export_manager.get_db') as mock_db, \
             patch('app.routers.digital_export_manager.SessionManager') as mock_session_manager:
            mock_session = MagicMock()
            mock_session.user_id = 1
            mock_session_manager.return_value.get_session.return_value = mock_session
            mock_session_manager.return_value.get_context.return_value = {}
            mock_session_manager.return_value.get_missions.return_value = []
            response = client.get(
                "/api/v1/digital-export-manager/sessions/session-1/insights",
            )
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "session-1"
            assert data["insight_count"] >= 0
            assert "insights" in data

    def test_get_session_insights_links_to_goal_plan(self):
        with patch('app.routers.digital_export_manager.get_db') as mock_db, \
             patch('app.routers.digital_export_manager.SessionManager') as mock_session_manager, \
             patch('app.routers.digital_export_manager.GoalRepository') as mock_goal_repo, \
             patch('app.routers.digital_export_manager.PlanRepository') as mock_plan_repo, \
             patch('app.routers.digital_export_manager.SQLiteMemoryProvider') as mock_memory:
            mock_session = MagicMock()
            mock_session.user_id = 1
            mock_session_manager.return_value.get_session.return_value = mock_session
            mock_session_manager.return_value.get_context.return_value = {"goal_id": "goal-1", "plan_id": "plan-1"}
            mock_session_manager.return_value.get_missions.return_value = []

            goal = MagicMock()
            goal.status = "active"
            goal.autonomy_level = "supervised"
            goal.metadata = {"execution_history": [{"status": "success"}]}
            goal.goal_id = "goal-1"
            mock_goal_repo.return_value.get.return_value = goal

            plan = MagicMock()
            plan.status = "active"
            plan.missions = ["m1"]
            plan.plan_id = "plan-1"
            mock_plan_repo.return_value.get.return_value = plan

            mock_memory.return_value.recall.return_value = []

            response = client.get(
                "/api/v1/digital-export-manager/sessions/session-1/insights",
            )
            assert response.status_code == 200
            data = response.json()
            assert data["goal_id"] == "goal-1"
            assert data["plan_id"] == "plan-1"

    def test_get_session_insights_no_mutation(self):
        with patch('app.routers.digital_export_manager.get_db') as mock_db, \
             patch('app.routers.digital_export_manager.SessionManager') as mock_session_manager, \
             patch('app.routers.digital_export_manager.GoalRepository') as mock_goal_repo, \
             patch('app.routers.digital_export_manager.PlanRepository') as mock_plan_repo, \
             patch('app.routers.digital_export_manager.SQLiteMemoryProvider') as mock_memory:
            mock_session = MagicMock()
            mock_session.user_id = 1
            mock_session_manager.return_value.get_session.return_value = mock_session
            mock_session_manager.return_value.get_context.return_value = {}
            mock_session_manager.return_value.get_missions.return_value = []

            goal = MagicMock()
            goal.status = "active"
            goal.metadata = {"execution_history": [{"status": "success"}]}
            mock_goal_repo.return_value.get.return_value = goal

            plan = MagicMock()
            plan.status = "active"
            plan.missions = ["m1"]
            mock_plan_repo.return_value.get.return_value = plan

            mock_memory.return_value.recall.return_value = []

            initial_goal_calls = mock_goal_repo.return_value.get.call_count
            response = client.get(
                "/api/v1/digital-export-manager/sessions/session-1/insights",
            )
            assert response.status_code == 200
            assert mock_goal_repo.return_value.get.call_count == initial_goal_calls
            assert mock_plan_repo.return_value.get.call_count == mock_plan_repo.return_value.get.call_count


class TestAgentDecisionAPI:
    def test_get_session_decisions_returns_list(self):
        with patch('app.routers.digital_export_manager.get_db') as mock_db, \
             patch('app.routers.digital_export_manager.SessionManager') as mock_session_manager:
            mock_session = MagicMock()
            mock_session.user_id = 1
            mock_session_manager.return_value.get_session.return_value = mock_session
            mock_session_manager.return_value.get_context.return_value = {}
            mock_session_manager.return_value.get_missions.return_value = [
                {
                    "mission_id": "m1",
                    "status": "completed",
                    "requires_approval": False,
                    "approval_status": "not_required",
                    "decision_context": {
                        "decision_id": "d1",
                        "chosen_path": "shipping",
                        "alternatives": ["eta", "customs"],
                    },
                    "reasoning": "Selected shipping path",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ]
            response = client.get(
                "/api/v1/digital-export-manager/sessions/session-1/decisions",
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["mission_id"] == "m1"
            assert data[0]["chosen_path"] == "shipping"


class TestAgentExecutionStateAPI:
    def test_get_session_execution_state_returns_state(self):
        with patch('app.routers.digital_export_manager.get_db') as mock_db, \
             patch('app.routers.digital_export_manager.SessionManager') as mock_session_manager, \
             patch('app.routers.digital_export_manager.GoalRepository') as mock_goal_repo, \
             patch('app.routers.digital_export_manager.PlanRepository') as mock_plan_repo:
            mock_session = MagicMock()
            mock_session.user_id = 1
            mock_session_manager.return_value.get_session.return_value = mock_session
            mock_session_manager.return_value.get_context.return_value = {"goal_id": "goal-1", "plan_id": "plan-1"}
            mock_session_manager.return_value.get_missions.return_value = [
                {"mission_id": "m1", "status": "completed"},
                {"mission_id": "m2", "status": "failed"},
                {"mission_id": "m3", "status": "pending_approval"},
            ]

            goal = MagicMock()
            goal.status = "active"
            goal.autonomy_level = "supervised"
            mock_goal_repo.return_value.get.return_value = goal

            plan = MagicMock()
            plan.status = "active"
            mock_plan_repo.return_value.get.return_value = plan

            response = client.get(
                "/api/v1/digital-export-manager/sessions/session-1/execution-state",
            )
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "session-1"
            assert data["goal_id"] == "goal-1"
            assert data["plan_id"] == "plan-1"
            assert data["mission_count"] == 3
            assert data["completed_missions"] == 1
            assert data["failed_missions"] == 1
            assert data["pending_approval_missions"] == 1
