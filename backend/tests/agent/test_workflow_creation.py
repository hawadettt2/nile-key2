"""Targeted test for workflow creation in Scenario 7."""
import os
os.environ['SECRET_KEY'] = 'ZkpJqi3KbOQ5m26hZmW2Ypr3-yHlXLQ_4owIIpqW_-PWTtbPx0g6sr3E-Dc2Whah'
os.environ['ALLOWED_ORIGINS'] = '["http://localhost:3000", "http://localhost:5173", "https://nile-key.com"]'
os.environ['OWNER_PASSWORD'] = 'TestOwnerPass123!'
os.environ['DISABLE_CSRF'] = 'true'
os.environ['SEARCH_STUB_FALLBACK'] = 'true'

import sys
module = sys.modules.get("backend.main") or sys.modules.get("main")
if module is None:
    raise RuntimeError("Application module not loaded")
app = module.app

from app.agent.workflow.orchestrator import WorkflowOrchestrator
from app.core.database import get_db

def get_db_factory():
    return get_db()

workflow_orchestrator = WorkflowOrchestrator(
    db_session_factory=get_db_factory,
    current_user={},
)

def test_workflow_creation_returns_id():
    payload = {
        "query": "cancel the workflow",
        "context": {"session_id": "test-session"},
        "customer_id": 1,
        "supplier_id": 1,
    }

    workflow_info = workflow_orchestrator._extract_workflow_context(payload)
    assert workflow_info is not None
    assert workflow_info["customer_id"] == 1
    assert workflow_info["supplier_id"] == 1

    workflow = workflow_orchestrator._create_workflow(workflow_info, user_id=1)
    assert workflow is not None
    assert "id" in workflow
    assert workflow["id"] > 0

    retrieved = workflow_orchestrator._safe_get_workflow(workflow["id"])
    assert retrieved is not None
    assert retrieved["id"] == workflow["id"]
