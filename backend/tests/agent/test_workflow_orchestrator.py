"""Tests for Workflow-Aware Mission Orchestration."""
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import pytest
from fastapi.testclient import TestClient
from main import app
from app.routers.digital_export_manager import router
from app.routers.auth import get_current_user, require_role
from app.agent.workflow.orchestrator import WorkflowOrchestrator

client = TestClient(app)


def _override_current_user():
    return {"id": 1, "username": "test", "email": "test@example.com", "role": "owner", "roles": ["owner"]}


app.dependency_overrides[get_current_user] = _override_current_user
app.dependency_overrides[require_role(["owner", "manager", "sales", "admin_staff", "accountant", "logistics"])] = _override_current_user
app.dependency_overrides[require_role(["owner", "manager"])] = _override_current_user
app.dependency_overrides[require_role(["owner"])] = _override_current_user


class TestWorkflowOrchestrator:
    def setup_method(self):
        self.orchestrator = WorkflowOrchestrator(db_session_factory=MagicMock(), current_user={"id": 1})

    def test_mission_type_to_stage_mapping(self):
        assert self.orchestrator.MISSION_TYPE_TO_STAGE["CREATE_SHIPMENT"] == "shipped"
        assert self.orchestrator.MISSION_TYPE_TO_STAGE["SUBMIT_INVOICE"] == "customs_ready"
        assert self.orchestrator.MISSION_TYPE_TO_STAGE["TRANSITION_WORKFLOW"] is None

    def test_mission_status_to_workflow_mapping(self):
        assert self.orchestrator.MISSION_STATUS_TO_WORKFLOW["completed"] == "advance"
        assert self.orchestrator.MISSION_STATUS_TO_WORKFLOW["failed"] == "blocked"
        assert self.orchestrator.MISSION_STATUS_TO_WORKFLOW["pending_approval"] == "paused"

    def test_get_workflow_state_returns_none_without_workflow(self):
        self.orchestrator._get_session_context = MagicMock(return_value=None)
        result = asyncio.get_event_loop().run_until_complete(
            self.orchestrator.get_workflow_state("session-1")
        )
        assert result is None

    def test_get_workflow_state_returns_none_without_workflow_id(self):
        self.orchestrator._get_session_context = MagicMock(return_value={})
        result = asyncio.get_event_loop().run_until_complete(
            self.orchestrator.get_workflow_state("session-1")
        )
        assert result is None

    def test_update_workflow_state_returns_none_without_workflow_id(self):
        self.orchestrator._get_session_context = MagicMock(return_value={})
        result = asyncio.get_event_loop().run_until_complete(
            self.orchestrator.update_workflow_state("session-1", "CREATE_SHIPMENT", "completed")
        )
        assert result is None

    def test_ensure_workflow_for_mission_returns_none_without_entities(self):
        result = asyncio.get_event_loop().run_until_complete(
            self.orchestrator.ensure_workflow_for_mission("session-1", "CREATE_SHIPMENT", {"foo": "bar"})
        )
        assert result is None

    def test_determine_next_stage_draft_to_customs_ready(self):
        workflow = {"state": "draft", "invoice_id": 1}
        result = self.orchestrator._determine_next_stage("draft", workflow)
        assert result == "customs_ready"

    def test_determine_next_stage_draft_to_shipped(self):
        workflow = {"state": "draft", "shipment_id": 1}
        result = self.orchestrator._determine_next_stage("draft", workflow)
        assert result == "shipped"

    def test_check_transition_preconditions_shipped_requires_shipment(self):
        workflow = {"shipment_id": None}
        assert self.orchestrator._check_transition_preconditions("shipped", workflow) is False

    def test_check_transition_preconditions_delivered_always_true(self):
        assert self.orchestrator._check_transition_preconditions("delivered", {}) is True


class TestDEMWorkflowAPI:
    def test_get_session_workflow_returns_empty_when_no_workflow(self):
        with patch('app.routers.digital_export_manager.get_db') as mock_db, \
             patch('app.routers.digital_export_manager.SessionManager') as mock_session_manager, \
             patch('app.routers.digital_export_manager.WorkflowOrchestrator') as mock_orchestrator_cls:
            mock_session = MagicMock()
            mock_session.user_id = 1
            mock_session_manager.return_value.get_session.return_value = mock_session
            mock_session_manager.return_value.get_context.return_value = {}

            mock_orchestrator = MagicMock()
            mock_orchestrator.get_workflow_state = AsyncMock(return_value=None)
            mock_orchestrator_cls.return_value = mock_orchestrator

            response = client.get("/api/v1/digital-export-manager/sessions/session-1/workflow")
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "session-1"
            assert data["workflow_id"] is None

    def test_get_session_workflow_returns_workflow_when_linked(self):
        with patch('app.routers.digital_export_manager.get_db') as mock_db, \
             patch('app.routers.digital_export_manager.SessionManager') as mock_session_manager, \
             patch('app.routers.digital_export_manager.WorkflowOrchestrator') as mock_orchestrator_cls:
            mock_session = MagicMock()
            mock_session.user_id = 1
            mock_session_manager.return_value.get_session.return_value = mock_session
            mock_session_manager.return_value.get_context.return_value = {"workflow_id": 1}

            mock_orchestrator = MagicMock()
            mock_orchestrator.get_workflow_state = AsyncMock(return_value={
                "id": 1,
                "workflow_number": "WF-001",
                "state": "draft",
                "customer_id": 10,
                "supplier_id": 20,
                "items": [],
            })
            mock_orchestrator_cls.return_value = mock_orchestrator

            response = client.get("/api/v1/digital-export-manager/sessions/session-1/workflow")
            assert response.status_code == 200
            data = response.json()
            assert data["workflow_id"] == 1
            assert data["state"] == "draft"

    def test_get_session_workflow_summary_returns_empty_when_no_workflow(self):
        with patch('app.routers.digital_export_manager.get_db') as mock_db, \
             patch('app.routers.digital_export_manager.SessionManager') as mock_session_manager, \
             patch('app.routers.digital_export_manager.WorkflowOrchestrator') as mock_orchestrator_cls:
            mock_session = MagicMock()
            mock_session.user_id = 1
            mock_session_manager.return_value.get_session.return_value = mock_session
            mock_session_manager.return_value.get_context.return_value = {}

            mock_orchestrator = MagicMock()
            mock_orchestrator.get_workflow_state = AsyncMock(return_value=None)
            mock_orchestrator_cls.return_value = mock_orchestrator

            response = client.get("/api/v1/digital-export-manager/sessions/session-1/workflow/summary")
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "session-1"
            assert data["workflow"] is None

    def test_get_session_workflow_summary_returns_summary_when_linked(self):
        with patch('app.routers.digital_export_manager.get_db') as mock_db, \
             patch('app.routers.digital_export_manager.SessionManager') as mock_session_manager, \
             patch('app.routers.digital_export_manager.WorkflowOrchestrator') as mock_orchestrator_cls, \
             patch('app.services.workflow.generate_workflow_summary') as mock_summary:
            mock_session = MagicMock()
            mock_session.user_id = 1
            mock_session_manager.return_value.get_session.return_value = mock_session
            mock_session_manager.return_value.get_context.return_value = {"workflow_id": 1}

            mock_orchestrator = MagicMock()
            mock_orchestrator.get_workflow_state = AsyncMock(return_value={"id": 1})
            mock_orchestrator_cls.return_value = mock_orchestrator

            mock_summary.return_value = {
                "workflow": {"id": 1, "state": "draft"},
                "customer": {"name": "ACME"},
                "supplier": {"name": "EG Supplier"},
                "invoice": {"number": "INV-1"},
                "customs_declaration": None,
                "shipment": None,
                "documents": [],
                "audit_logs": [],
                "items": [],
            }

            response = client.get("/api/v1/digital-export-manager/sessions/session-1/workflow/summary")
            assert response.status_code == 200
            data = response.json()
            assert data["workflow"]["state"] == "draft"
            assert data["customer"]["name"] == "ACME"
