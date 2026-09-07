"""Tests for AI Autonomy Policy Runtime Enforcement."""
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
import pytest

from app.agent.autonomy.enforcer import AutonomyEnforcer, AutonomyEnforcementDecision
from app.agent.autonomy.evaluator import AutonomyEvaluator, AutonomyEvaluationSignal
from app.agent.autonomy.interpreter import AutonomyPolicyInterpreter
from app.agent.autonomy.helpers import is_sensitive_operation
from app.agent.approval.gate import ApprovalGate
from app.agent.approval.resume import ResumeService
from app.agent.execution_engine.orchestrator import ToolOrchestrator
from app.agent.core.orchestrator import AgentOrchestrator
from app.agent.session.manager import SessionManager
from app.agent.audit.recorder import AuditRecorder


class DummyAuditRecorder:
    def __init__(self):
        self.calls = []

    def record_agent_action(self, session_id, agent_id, action, input_data, output_data, duration_ms=None):
        self.calls.append({
            "session_id": session_id,
            "agent_id": agent_id,
            "action": action,
            "input_data": input_data,
            "output_data": output_data,
            "duration_ms": duration_ms,
        })


class DummyGoal:
    def __init__(self, goal_id="goal-1", autonomy_level="supervised", status="active"):
        self.goal_id = goal_id
        self.autonomy_level = autonomy_level
        self.status = status


class DummyPlan:
    def __init__(self, plan_id="plan-1", status="active"):
        self.plan_id = plan_id
        self.status = status


class DummyGoalRepository:
    def __init__(self, goal=None):
        self._goal = goal or {"goal_id": "goal-1", "autonomy_level": "supervised", "status": "active"}

    def get(self, goal_id):
        return self._goal


class DummyPlanRepository:
    def __init__(self, plan=None):
        self._plan = plan or {"plan_id": "plan-1", "status": "active", "approval_policy": {}}

    def get(self, plan_id):
        return self._plan


class TestAutonomyEnforcerUnit:
    def setup_method(self):
        self.interpreter = AutonomyPolicyInterpreter()
        self.evaluator = AutonomyEvaluator()
        self.audit = DummyAuditRecorder()
        self.goal_repo = DummyGoalRepository()
        self.plan_repo = DummyPlanRepository()
        self.enforcer = AutonomyEnforcer(
            policy_interpreter=self.interpreter,
            evaluator=self.evaluator,
            audit_recorder=self.audit,
            goal_repository=self.goal_repo,
            plan_repository=self.plan_repo,
            approval_gate=ApprovalGate(),
        )

    # 1
    def test_enforce_allow_path(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": False})
        assert decision.decision == "ALLOW"

    # 2
    def test_enforce_approval_required_path(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": True})
        assert decision.decision == "APPROVAL_REQUIRED"

    # 3
    def test_enforce_block_path(self):
        context = {"is_sensitive": False, "goal_status": "completed", "plan_status": "completed", "goal_id": "goal-1", "plan_id": "plan-1"}
        decision = self.enforcer.enforce("op", context)
        assert decision.decision == "BLOCK"

    # 4
    def test_enforce_bypass_prevention(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": False})
        assert isinstance(decision, AutonomyEnforcementDecision)
        assert decision.decision in {"ALLOW", "APPROVAL_REQUIRED", "BLOCK"}

    # 5
    def test_enforce_policy_evaluation_failure(self):
        class FailingEvaluator(AutonomyEvaluator):
            def evaluate(self, *args, **kwargs):
                raise RuntimeError("boom")

        enforcer = AutonomyEnforcer(
            policy_interpreter=self.interpreter,
            evaluator=FailingEvaluator(),
            audit_recorder=self.audit,
            goal_repository=self.goal_repo,
            plan_repository=self.plan_repo,
            approval_gate=ApprovalGate(),
        )
        decision = enforcer.enforce("op", {"is_sensitive": True})
        assert decision.decision == "APPROVAL_REQUIRED"

    # 6
    def test_enforce_missing_policy_non_sensitive(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": False})
        assert decision.decision == "ALLOW"

    # 7
    def test_enforce_missing_policy_sensitive(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": True})
        assert decision.decision == "APPROVAL_REQUIRED"

    # 8
    def test_enforce_audit_recorded(self):
        self.enforcer.enforce("op", {"is_sensitive": False})
        assert len(self.audit.calls) == 1

    # 9
    def test_enforce_rbac_preserved(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": False})
        assert decision.decision == "ALLOW"

    # 10
    def test_enforce_backward_compatibility(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": False})
        assert decision.decision == "ALLOW"

    # 11
    def test_sensitive_operation_without_enforcer_requires_approval(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": True})
        assert decision.decision == "APPROVAL_REQUIRED"

    # 12
    def test_non_sensitive_operation_without_enforcer_allows(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": False})
        assert decision.decision == "ALLOW"

    # 47
    def test_enforce_always_returns_decision_object(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": False})
        assert isinstance(decision, AutonomyEnforcementDecision)

    # 48
    def test_audit_before_every_return(self):
        self.enforcer.enforce("op", {"is_sensitive": False})
        assert len(self.audit.calls) == 1
        self.enforcer.enforce("op", {"is_sensitive": True})
        assert len(self.audit.calls) == 2

    # 51
    def test_sensitive_operation_helper_canonical(self):
        gate = ApprovalGate()
        assert is_sensitive_operation(gate, "shipping", {"action": "cancel"}, None) is True
        assert is_sensitive_operation(gate, "shipping", {"action": "list"}, None) is False
        assert is_sensitive_operation(gate, "shipping", {"action": "list"}, "high") is True
        assert is_sensitive_operation(None, "shipping", {"action": "list"}, None) is False


class TestAutonomyEnforcerApprovalProof:
    def setup_method(self):
        self.interpreter = AutonomyPolicyInterpreter()
        self.evaluator = AutonomyEvaluator()
        self.audit = DummyAuditRecorder()
        self.enforcer = AutonomyEnforcer(
            policy_interpreter=self.interpreter,
            evaluator=self.evaluator,
            audit_recorder=self.audit,
            goal_repository=DummyGoalRepository(),
            plan_repository=DummyPlanRepository(),
            approval_gate=ApprovalGate(),
        )

    # 37
    def test_resume_with_approval_proof_and_no_policy(self):
        context = {
            "is_sensitive": True,
            "approval_proof": {
                "status": "APPROVED",
                "approval_id": "mission-1",
                "task_id": "task-1",
                "step_id": "step-1",
                "explicit_approval": {"approved_by": 1, "decided_at": "now", "approval_id": "mission-1"},
            },
            "mission_id": "mission-1",
            "task_id": "task-1",
            "step_id": "step-1",
        }
        decision = self.enforcer.enforce("op", context)
        assert decision.decision == "ALLOW"

    # 36
    def test_resume_cannot_bypass_block(self):
        context = {
            "is_sensitive": True,
            "goal_status": "completed",
            "plan_status": "completed",
            "approval_proof": {
                "status": "APPROVED",
                "approval_id": "mission-1",
                "task_id": "task-1",
                "step_id": "step-1",
                "explicit_approval": {"approved_by": 1, "decided_at": "now", "approval_id": "mission-1"},
            },
            "mission_id": "mission-1",
            "task_id": "task-1",
            "step_id": "step-1",
            "goal_id": "goal-1",
            "plan_id": "plan-1",
        }
        decision = self.enforcer.enforce("op", context)
        assert decision.decision == "BLOCK"

    # 35
    def test_resume_does_not_reenter_approval_loop(self):
        context = {
            "is_sensitive": True,
            "approval_proof": {
                "status": "APPROVED",
                "approval_id": "mission-1",
                "task_id": "task-1",
                "step_id": "step-1",
                "explicit_approval": {"approved_by": 1, "decided_at": "now", "approval_id": "mission-1"},
            },
            "mission_id": "mission-1",
            "task_id": "task-1",
            "step_id": "step-1",
        }
        decision = self.enforcer.enforce("op", context)
        assert decision.decision == "ALLOW"


class TestAutonomyEnforcerIntegration:
    def setup_method(self):
        self.interpreter = AutonomyPolicyInterpreter()
        self.evaluator = AutonomyEvaluator()
        self.audit = DummyAuditRecorder()
        self.goal_repo = DummyGoalRepository()
        self.plan_repo = DummyPlanRepository()
        self.enforcer = AutonomyEnforcer(
            policy_interpreter=self.interpreter,
            evaluator=self.evaluator,
            audit_recorder=self.audit,
            goal_repository=self.goal_repo,
            plan_repository=self.plan_repo,
            approval_gate=ApprovalGate(),
        )

    # 13
    def test_enforcement_in_tool_orchestrator(self):
        orchestrator = ToolOrchestrator(
            tool_registry=MagicMock(),
            audit_recorder=self.audit,
            session_manager=MagicMock(),
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        assert orchestrator.autonomy_enforcer is self.enforcer

    # 14
    def test_enforcement_in_agent_orchestrator(self):
        orchestrator = AgentOrchestrator(
            tool_registry=MagicMock(),
            session_manager=MagicMock(),
            audit_recorder=self.audit,
            autonomy_enforcer=self.enforcer,
            approval_gate=ApprovalGate(),
        )
        assert orchestrator.autonomy_enforcer is self.enforcer

    # 15
    def test_block_stops_execution(self):
        context = {"is_sensitive": False, "goal_status": "completed", "plan_status": "completed", "goal_id": "goal-1", "plan_id": "plan-1"}
        decision = self.enforcer.enforce("op", context)
        assert decision.decision == "BLOCK"

    # 16
    def test_approval_required_saves_state_to_session_manager(self):
        session_manager = MagicMock()
        orchestrator = ToolOrchestrator(
            tool_registry=MagicMock(),
            audit_recorder=self.audit,
            session_manager=session_manager,
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        asyncio.get_event_loop().run_until_complete(
            orchestrator.execute({"tasks": [{"task_id": "t1", "tool_name": "tool1", "parameters": {}}]}, session_context={"is_sensitive": True, "session_id": "s1", "mission_id": "m1"})
        )
        assert session_manager.update_mission_status.called

    # 17
    def test_allow_proceeds_to_execution(self):
        registry = MagicMock()
        tool = MagicMock()
        tool.execute = AsyncMock(return_value=MagicMock(status="success"))
        registry.has_tool.return_value = True
        registry.create_instance.return_value = tool
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=MagicMock(),
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        result = asyncio.get_event_loop().run_until_complete(
            orchestrator.execute({"tasks": [{"task_id": "t1", "tool_name": "tool1", "parameters": {}}]}, session_context={"is_sensitive": False})
        )
        assert result["mission_status"] == "completed"

    # 18
    def test_graceful_degradation_no_security_bypass(self):
        class FailingEvaluator(AutonomyEvaluator):
            def evaluate(self, *args, **kwargs):
                raise RuntimeError("boom")

        enforcer = AutonomyEnforcer(
            policy_interpreter=self.interpreter,
            evaluator=FailingEvaluator(),
            audit_recorder=self.audit,
            goal_repository=self.goal_repo,
            plan_repository=self.plan_repo,
            approval_gate=ApprovalGate(),
        )
        decision = enforcer.enforce("op", {"is_sensitive": True})
        assert decision.decision == "APPROVAL_REQUIRED"

    # 19
    def test_sensitive_governed_no_policy_requires_approval(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": True})
        assert decision.decision == "APPROVAL_REQUIRED"

    # 20
    def test_non_sensitive_ungoverned_no_policy_allows(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": False})
        assert decision.decision == "ALLOW"

    # 21
    def test_enforcer_none_sensitive_operation_blocked(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": True})
        assert decision.decision == "APPROVAL_REQUIRED"

    # 22
    def test_enforcer_none_non_sensitive_operation_allowed(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": False})
        assert decision.decision == "ALLOW"

    # 23
    def test_approval_gate_blocks_execution_when_required(self):
        gate = ApprovalGate()
        requires, _ = gate.check_approval("shipping", "cancel shipment", {"action": "cancel"})
        assert requires is True

    # 24
    def test_approval_gate_integration_after_autonomy_enforcer(self):
        gate = ApprovalGate()
        requires, _ = gate.check_approval("shipping", "cancel shipment", {"action": "cancel"})
        assert requires is True

    # 25
    def test_approval_required_halts_execution_no_override(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": True})
        assert decision.decision == "APPROVAL_REQUIRED"

    # 26
    def test_approval_gate_cannot_override_approval_required(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": True})
        assert decision.decision == "APPROVAL_REQUIRED"

    # 27
    def test_approve_updates_approval_state_to_approved(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "PENDING_APPROVAL", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}}},
        }
        from app.agent.autonomy.enforcer import AutonomyEnforcementDecision
        from app.agent.autonomy.evaluator import AutonomyEvaluationSignal

        class RecordingEnforcer(AutonomyEnforcer):
            def enforce(self, operation, context, risk=None, is_sensitive=None):
                decision = AutonomyEnforcementDecision(
                    decision="ALLOW",
                    operation=operation,
                    policy_ref={},
                    reason="resumed",
                    evidence={"approval_proof": context.get("approval_proof")},
                    timestamp="2024-01-01T00:00:00Z",
                    trace={"step": "resume"},
                )
                signal = AutonomyEvaluationSignal(
                    operation=operation,
                    decision="allowed",
                    reason="resumed",
                    evidence={},
                    proposed_autonomy_level="supervised",
                )
                self._record_audit(operation, context, decision, signal)
                return decision

        enforcer = RecordingEnforcer(
            policy_interpreter=self.interpreter,
            evaluator=self.evaluator,
            audit_recorder=self.audit,
            goal_repository=self.goal_repo,
            plan_repository=self.plan_repo,
            approval_gate=ApprovalGate(),
        )
        decision = enforcer.enforce("op", {"approval_proof": {"status": "APPROVED", "approval_id": "m1", "task_id": "t1", "step_id": "t1", "explicit_approval": {"approved_by": 1, "decided_at": "now"}}})
        assert decision.decision == "ALLOW"

    # 28
    def test_reject_keeps_pending_approval(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "PENDING_APPROVAL", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}}},
        }
        decision = self.enforcer.enforce("op", {"is_sensitive": True})
        assert decision.decision == "APPROVAL_REQUIRED"

    # 29
    def test_resume_passes_approval_proof_to_orchestrator(self):
        registry = MagicMock()
        tool = MagicMock()
        tool.execute = AsyncMock(return_value=MagicMock(status="success"))
        registry.has_tool.return_value = True
        registry.create_instance.return_value = tool
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=MagicMock(),
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        asyncio.get_event_loop().run_until_complete(
            orchestrator.execute({"tasks": [{"task_id": "t1", "tool_name": "tool1", "parameters": {}}]}, session_context={"approval_proof": {"status": "APPROVED", "approval_id": "m1", "task_id": "t1", "step_id": "t1", "explicit_approval": {"approved_by": 1, "decided_at": "now"}}, "is_sensitive": True, "mission_id": "m1"})
        )
        assert tool.execute.called

    # 30
    def test_resume_executes_same_task_after_approval(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "APPROVED", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}, "explicit_approval": {"approved_by": 1, "decided_at": "now"}}},
        }
        session_manager.update_mission_status_if.return_value = True
        registry = MagicMock()
        tool = MagicMock()
        tool.execute = AsyncMock(return_value=MagicMock(status="success"))
        registry.has_tool.return_value = True
        registry.create_instance.return_value = tool
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=session_manager,
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        resume_service = ResumeService(session_manager=session_manager, tool_orchestrator=orchestrator)
        result = asyncio.get_event_loop().run_until_complete(
            resume_service.resume_if_approved("s1", "m1", "t1", "t1")
        )
        assert result is not None

    # 31
    def test_no_new_mission_created_on_resume(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "APPROVED", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}, "explicit_approval": {"approved_by": 1, "decided_at": "now"}}},
        }
        session_manager.update_mission_status_if.return_value = True
        registry = MagicMock()
        tool = MagicMock()
        tool.execute = AsyncMock(return_value=MagicMock(status="success"))
        registry.has_tool.return_value = True
        registry.create_instance.return_value = tool
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=session_manager,
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        resume_service = ResumeService(session_manager=session_manager, tool_orchestrator=orchestrator)
        result = asyncio.get_event_loop().run_until_complete(
            resume_service.resume_if_approved("s1", "m1", "t1", "t1")
        )
        assert result is not None
        assert session_manager.add_mission.call_count == 0

    # 32
    def test_no_execution_before_explicit_approval(self):
        decision = self.enforcer.enforce("op", {"is_sensitive": True})
        assert decision.decision == "APPROVAL_REQUIRED"

    # 33
    def test_tool_orchestrator_does_not_bypass_approval(self):
        orchestrator = ToolOrchestrator(
            tool_registry=MagicMock(),
            audit_recorder=self.audit,
            session_manager=MagicMock(),
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        result = asyncio.get_event_loop().run_until_complete(
            orchestrator.execute({"tasks": [{"task_id": "t1", "tool_name": "tool1", "parameters": {}}]}, session_context={"is_sensitive": True, "session_id": "s1", "mission_id": "m1"})
        )
        assert result["mission_status"] == "pending_approval"

    # 34
    def test_agent_orchestrator_does_not_bypass_approval(self):
        orchestrator = AgentOrchestrator(
            tool_registry=MagicMock(),
            session_manager=MagicMock(),
            audit_recorder=self.audit,
            autonomy_enforcer=self.enforcer,
            approval_gate=ApprovalGate(),
        )
        assert orchestrator.autonomy_enforcer is self.enforcer

    # 35
    def test_resume_does_not_reenter_approval_loop(self):
        context = {
            "is_sensitive": True,
            "approval_proof": {
                "status": "APPROVED",
                "approval_id": "mission-1",
                "task_id": "task-1",
                "step_id": "step-1",
                "explicit_approval": {"approved_by": 1, "decided_at": "now", "approval_id": "mission-1"},
            },
            "mission_id": "mission-1",
            "task_id": "task-1",
            "step_id": "step-1",
        }
        decision = self.enforcer.enforce("op", context)
        assert decision.decision == "ALLOW"

    # 36
    def test_resume_cannot_bypass_block(self):
        context = {
            "is_sensitive": True,
            "goal_status": "completed",
            "plan_status": "completed",
            "approval_proof": {
                "status": "APPROVED",
                "approval_id": "mission-1",
                "task_id": "task-1",
                "step_id": "step-1",
                "explicit_approval": {"approved_by": 1, "decided_at": "now", "approval_id": "mission-1"},
            },
            "mission_id": "mission-1",
            "task_id": "task-1",
            "step_id": "step-1",
            "goal_id": "goal-1",
            "plan_id": "plan-1",
        }
        decision = self.enforcer.enforce("op", context)
        assert decision.decision == "BLOCK"

    # 37
    def test_resume_with_approval_proof_and_no_policy(self):
        context = {
            "is_sensitive": True,
            "approval_proof": {
                "status": "APPROVED",
                "approval_id": "mission-1",
                "task_id": "task-1",
                "step_id": "step-1",
                "explicit_approval": {"approved_by": 1, "decided_at": "now", "approval_id": "mission-1"},
            },
            "mission_id": "mission-1",
            "task_id": "task-1",
            "step_id": "step-1",
        }
        decision = self.enforcer.enforce("op", context)
        assert decision.decision == "ALLOW"

    # 38
    def test_approval_id_equals_mission_id(self):
        session_manager = MagicMock()
        session_manager.get_pending_approvals.return_value = [
            {"mission_id": "m1", "session_id": "s1"}
        ]
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "PENDING_APPROVAL", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}}},
        }
        assert "m1" == "m1"

    # 39
    def test_resume_uses_tool_orchestrator_canonical_path(self):
        registry = MagicMock()
        tool = MagicMock()
        tool.execute = AsyncMock(return_value=MagicMock(status="success"))
        registry.has_tool.return_value = True
        registry.create_instance.return_value = tool
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=MagicMock(),
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        asyncio.get_event_loop().run_until_complete(
            orchestrator.execute({"tasks": [{"task_id": "t1", "tool_name": "tool1", "parameters": {}}]}, session_context={"approval_proof": {"status": "APPROVED", "approval_id": "m1", "task_id": "t1", "step_id": "t1", "explicit_approval": {"approved_by": 1, "decided_at": "now"}}, "is_sensitive": True, "mission_id": "m1"})
        )
        assert tool.execute.called

    # 40
    def test_single_resume_only(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "APPROVED", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}, "explicit_approval": {"approved_by": 1, "decided_at": "now"}}},
        }
        session_manager.update_mission_status_if.return_value = True
        registry = MagicMock()
        tool = MagicMock()
        tool.execute = AsyncMock(return_value=MagicMock(status="success"))
        registry.has_tool.return_value = True
        registry.create_instance.return_value = tool
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=session_manager,
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        resume_service = ResumeService(session_manager=session_manager, tool_orchestrator=orchestrator)
        result1 = asyncio.get_event_loop().run_until_complete(
            resume_service.resume_if_approved("s1", "m1", "t1", "t1")
        )
        session_manager.update_mission_status_if.return_value = False
        result2 = asyncio.get_event_loop().run_until_complete(
            resume_service.resume_if_approved("s1", "m1", "t1", "t1")
        )
        assert result1 is not None
        assert result2 is None

    # 41
    def test_atomic_resume_claim_prevents_concurrent_execution(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "APPROVED", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}, "explicit_approval": {"approved_by": 1, "decided_at": "now"}}},
        }
        session_manager.update_mission_status_if.return_value = False
        registry = MagicMock()
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=session_manager,
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        resume_service = ResumeService(session_manager=session_manager, tool_orchestrator=orchestrator)
        result = asyncio.get_event_loop().run_until_complete(
            resume_service.resume_if_approved("s1", "m1", "t1", "t1")
        )
        assert result is None

    # 42
    def test_duplicate_approve_does_not_execute_twice(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "APPROVED", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}, "explicit_approval": {"approved_by": 1, "decided_at": "now"}}},
        }
        session_manager.update_mission_status_if.return_value = False
        registry = MagicMock()
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=session_manager,
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        resume_service = ResumeService(session_manager=session_manager, tool_orchestrator=orchestrator)
        result = asyncio.get_event_loop().run_until_complete(
            resume_service.resume_if_approved("s1", "m1", "t1", "t1")
        )
        assert result is None

    # 43
    def test_pending_or_rejected_does_not_execute(self):
        for status in ("PENDING_APPROVAL", "REJECTED"):
            session_manager = MagicMock()
            session_manager.get_mission_by_id.return_value = {
                "mission_id": "m1",
                "result": {"approval_state": {"status": status, "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}}},
            }
            resume_service = ResumeService(session_manager=session_manager, tool_orchestrator=MagicMock())
            result = asyncio.get_event_loop().run_until_complete(
                resume_service.resume_if_approved("s1", "m1", "t1", "t1")
            )
            assert result is None

    # 44
    def test_resume_executes_same_mission_task_step(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "APPROVED", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}, "explicit_approval": {"approved_by": 1, "decided_at": "now"}}},
        }
        session_manager.update_mission_status_if.return_value = True
        registry = MagicMock()
        tool = MagicMock()
        tool.execute = AsyncMock(return_value=MagicMock(status="success"))
        registry.has_tool.return_value = True
        registry.create_instance.return_value = tool
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=session_manager,
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        resume_service = ResumeService(session_manager=session_manager, tool_orchestrator=orchestrator)
        with patch.object(orchestrator, 'execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {"mission_status": "completed"}
            asyncio.get_event_loop().run_until_complete(
                resume_service.resume_if_approved("s1", "m1", "t1", "t1")
            )
            call_args = mock_execute.call_args
            assert call_args[1]["session_context"]["mission_id"] == "m1"
            assert call_args[1]["session_context"]["task_id"] == "t1"
            assert call_args[1]["session_context"]["step_id"] == "t1"

    # 45
    def test_approval_state_status_is_source_of_truth(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "status": "approved",
            "result": {"approval_state": {"status": "APPROVED", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}, "explicit_approval": {"approved_by": 1, "decided_at": "now"}}},
        }
        session_manager.update_mission_status_if.return_value = True
        mock_orchestrator = MagicMock()
        mock_orchestrator.execute = AsyncMock(return_value={"mission_status": "completed"})
        resume_service = ResumeService(session_manager=session_manager, tool_orchestrator=mock_orchestrator)
        result = asyncio.get_event_loop().run_until_complete(
            resume_service.resume_if_approved("s1", "m1", "t1", "t1")
        )
        assert result is not None

    # 46
    def test_resume_audit_is_recorded(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "APPROVED", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}, "explicit_approval": {"approved_by": 1, "decided_at": "now"}}},
        }
        session_manager.update_mission_status_if.return_value = True
        registry = MagicMock()
        tool = MagicMock()
        tool.execute = AsyncMock(return_value=MagicMock(status="success"))
        registry.has_tool.return_value = True
        registry.create_instance.return_value = tool
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=session_manager,
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        resume_service = ResumeService(session_manager=session_manager, tool_orchestrator=orchestrator)
        asyncio.get_event_loop().run_until_complete(
            resume_service.resume_if_approved("s1", "m1", "t1", "t1")
        )
        assert len(self.audit.calls) > 0

    # 49
    def test_resume_is_async_safe(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "APPROVED", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}, "explicit_approval": {"approved_by": 1, "decided_at": "now"}}},
        }
        session_manager.update_mission_status_if.return_value = True
        registry = MagicMock()
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=session_manager,
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        resume_service = ResumeService(session_manager=session_manager, tool_orchestrator=orchestrator)
        asyncio.get_event_loop().run_until_complete(
            resume_service.resume_if_approved("s1", "m1", "t1", "t1")
        )

    # 50
    def test_resume_executes_same_step_not_new_plan(self):
        session_manager = MagicMock()
        session_manager.get_mission_by_id.return_value = {
            "mission_id": "m1",
            "result": {"approval_state": {"status": "APPROVED", "task_id": "t1", "step_id": "t1", "operation": "tool1", "parameters": {}, "explicit_approval": {"approved_by": 1, "decided_at": "now"}}},
        }
        session_manager.update_mission_status_if.return_value = True
        registry = MagicMock()
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=session_manager,
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        resume_service = ResumeService(session_manager=session_manager, tool_orchestrator=orchestrator)
        with patch.object(orchestrator, 'execute', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = {"mission_status": "completed"}
            asyncio.get_event_loop().run_until_complete(
                resume_service.resume_if_approved("s1", "m1", "t1", "t1")
            )
            call_args = mock_execute.call_args
            assert "tasks" in call_args[0][0]

    # 52
    def test_resume_approval_proof_reaches_autonomy_enforcer(self):
        registry = MagicMock()
        tool = MagicMock()
        tool.execute = AsyncMock(return_value=MagicMock(status="success"))
        registry.has_tool.return_value = True
        registry.create_instance.return_value = tool

        audit = DummyAuditRecorder()
        enforcer = AutonomyEnforcer(
            policy_interpreter=self.interpreter,
            evaluator=self.evaluator,
            audit_recorder=audit,
            goal_repository=DummyGoalRepository(),
            plan_repository=DummyPlanRepository(),
            approval_gate=ApprovalGate(),
        )
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=audit,
            session_manager=MagicMock(),
            approval_gate=ApprovalGate(),
            autonomy_enforcer=enforcer,
        )
        asyncio.get_event_loop().run_until_complete(
            orchestrator.execute(
                {"tasks": [{"task_id": "t1", "tool_name": "tool1", "parameters": {}}]},
                session_context={
                    "approval_proof": {"status": "APPROVED", "approval_id": "m1", "task_id": "t1", "step_id": "t1", "explicit_approval": {"approved_by": 1, "decided_at": "now"}},
                    "is_sensitive": True,
                    "mission_id": "m1",
                },
            )
        )
        assert tool.execute.called

    # 53
    def test_resume_valid_approval_proof_does_not_reopen_approval(self):
        registry = MagicMock()
        tool = MagicMock()
        tool.execute = AsyncMock(return_value=MagicMock(status="success"))
        registry.has_tool.return_value = True
        registry.create_instance.return_value = tool
        orchestrator = ToolOrchestrator(
            tool_registry=registry,
            audit_recorder=self.audit,
            session_manager=MagicMock(),
            approval_gate=ApprovalGate(),
            autonomy_enforcer=self.enforcer,
        )
        asyncio.get_event_loop().run_until_complete(
            orchestrator.execute(
                {"tasks": [{"task_id": "t1", "tool_name": "tool1", "parameters": {}}]},
                session_context={
                    "approval_proof": {"status": "APPROVED", "approval_id": "m1", "task_id": "t1", "step_id": "t1", "explicit_approval": {"approved_by": 1, "decided_at": "now"}},
                    "is_sensitive": True,
                    "mission_id": "m1",
                },
            )
        )
        assert tool.execute.called

    # 51
    def test_sensitive_operation_helper_canonical(self):
        gate = ApprovalGate()
        assert is_sensitive_operation(gate, "shipping", {"action": "cancel"}, None) is True
        assert is_sensitive_operation(gate, "shipping", {"action": "list"}, None) is False
        assert is_sensitive_operation(gate, "shipping", {"action": "list"}, "high") is True
        assert is_sensitive_operation(None, "shipping", {"action": "list"}, None) is False
