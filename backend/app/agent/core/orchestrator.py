import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from ..tools.registry import tool_registry, ToolRegistry
from ..tools.base import BaseTool, ToolResult
from ..core.planner import Planner, ExecutionPlan
from ..audit.recorder import AuditRecorder
from ..session.manager import SessionManager
from ..schemas.tool_result import ToolResultSchema
from ..approval.gate import ApprovalGate
from ..autonomy.helpers import is_sensitive_operation
from ..autonomy.enforcer import AutonomyEnforcer


class AgentOrchestrator:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        session_manager: SessionManager,
        audit_recorder: AuditRecorder,
        agent_id: str = "wp30-digital-export-manager",
        autonomy_enforcer: Optional[AutonomyEnforcer] = None,
        approval_gate: Optional[ApprovalGate] = None,
    ):
        self.tool_registry = tool_registry
        self.session_manager = session_manager
        self.audit_recorder = audit_recorder
        self.agent_id = agent_id
        self.planner = Planner()
        self.autonomy_enforcer = autonomy_enforcer
        self.approval_gate = approval_gate or ApprovalGate()

    async def execute(
        self,
        session_id: str,
        intent: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start_time = time.time()
        parameters = parameters or {}

        session = self.session_manager.get_session(session_id)
        if not session:
            return {
                "status": "error",
                "error": "Session not found",
                "session_id": session_id,
            }

        if session.status != "active":
            return {
                "status": "error",
                "error": f"Session is {session.status}",
                "session_id": session_id,
            }

        context = self.session_manager.get_context(session_id) or {}
        context["current_step"] = "planning"
        self.session_manager.update_context(session_id, {"current_step": "planning"})

        try:
            plan = self.planner.plan(intent, context)
            context["plan"] = {
                "intent": intent,
                "steps": len(plan.steps),
                "current_step_index": 0,
            }
            self.session_manager.update_context(session_id, {"plan": context["plan"]})

            results: List[Dict[str, Any]] = []
            final_result = None

            while plan.has_more_steps():
                step = plan.get_next_step()
                context["current_step"] = f"executing_{step.tool_name}"
                self.session_manager.update_context(
                    session_id,
                    {
                        "current_step": f"executing_{step.tool_name}",
                        "plan": context.get("plan", {}),
                    },
                )

                tool_instance = self.tool_registry.create_instance(step.tool_name)
                if not tool_instance:
                    error_msg = f"Tool {step.tool_name} not found"
                    self.audit_recorder.record_agent_action(
                        session_id=session_id,
                        agent_id=self.agent_id,
                        action=f"tool_not_found:{step.tool_name}",
                        input_data={"intent": intent, "step": step.step_id},
                        output_data={"error": error_msg},
                        duration_ms=int((time.time() - start_time) * 1000),
                    )
                    return {
                        "status": "error",
                        "error": error_msg,
                        "session_id": session_id,
                        "completed_steps": results,
                    }

                step_parameters = {**parameters, **step.parameters}
                risk = context.get("risk")
                is_sensitive = is_sensitive_operation(
                    approval_gate=self.approval_gate,
                    tool_name=step.tool_name,
                    parameters=step_parameters,
                    risk=risk,
                )

                if self.autonomy_enforcer:
                    step_context = {
                        "session_id": session_id,
                        "agent_id": self.agent_id,
                        "goal_id": context.get("goal_id"),
                        "plan_id": context.get("plan_id"),
                        "chosen_path": "",
                        "intent": intent,
                        "user_id": context.get("user_id"),
                        "execution_history": context.get("execution_history"),
                        "memory_provider": context.get("memory_provider"),
                        "mission_id": context.get("mission_id"),
                        "task_id": step.step_id,
                        "step_id": step.step_id,
                        "risk": risk,
                        "is_sensitive": is_sensitive,
                        "approval_proof": context.get("approval_proof"),
                    }

                    enforcement_decision = self.autonomy_enforcer.enforce(
                        operation=step.tool_name,
                        context=step_context,
                        risk=risk,
                    )

                    if enforcement_decision.decision == "BLOCK":
                        self.audit_recorder.record_agent_action(
                            session_id=session_id,
                            agent_id=self.agent_id,
                            action=f"tool_blocked:{step.tool_name}",
                            input_data={"intent": intent, "step": step.step_id},
                            output_data={"error": f"Blocked by autonomy policy: {enforcement_decision.reason}"},
                            duration_ms=0,
                        )
                        results.append({
                            "step_id": step.step_id,
                            "tool": step.tool_name,
                            "result": {"status": "blocked", "error": f"Blocked by autonomy policy: {enforcement_decision.reason}"},
                            "duration_ms": 0,
                        })
                        break

                    elif enforcement_decision.decision == "APPROVAL_REQUIRED":
                        approval_state = {
                            "mission_id": context.get("mission_id", ""),
                            "task_id": step.step_id,
                            "step_id": step.step_id,
                            "operation": step.tool_name,
                            "status": "PENDING_APPROVAL",
                            "autonomy_decision": enforcement_decision.to_dict(),
                            "approval_gate_result": {},
                            "explicit_approval": None,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                        }

                        if getattr(self, 'approval_gate', None):
                            requires_human_approval, approval_status = self.approval_gate.check_approval(
                                chosen_path="",
                                intent=intent,
                                parameters=step_parameters,
                            )
                            approval_state["approval_gate_result"] = {
                                "requires_approval": requires_human_approval,
                                "status": approval_status,
                            }

                        if self.session_manager and context.get("mission_id"):
                            self.session_manager.update_mission_status(
                                session_id=session_id,
                                mission_id=context.get("mission_id"),
                                status="pending_approval",
                                result={"approval_state": approval_state},
                            )

                        self.audit_recorder.record_agent_action(
                            session_id=session_id,
                            agent_id=self.agent_id,
                            action=f"tool_approval_required:{step.tool_name}",
                            input_data={"intent": intent, "step": step.step_id},
                            output_data={
                                "approval_required": True,
                                "approval_state": approval_state,
                            },
                            duration_ms=0,
                        )
                        results.append({
                            "step_id": step.step_id,
                            "tool": step.tool_name,
                            "result": {
                                "status": "pending_approval",
                                "approval_required": True,
                                "approval_state": approval_state,
                            },
                            "duration_ms": 0,
                        })
                        break

                else:
                    if is_sensitive:
                        approval_state = {
                            "mission_id": context.get("mission_id", ""),
                            "task_id": step.step_id,
                            "step_id": step.step_id,
                            "operation": step.tool_name,
                            "status": "PENDING_APPROVAL",
                            "autonomy_decision": {"decision": "APPROVAL_REQUIRED", "reason": "sensitive_operation_without_enforcer"},
                            "approval_gate_result": {},
                            "explicit_approval": None,
                            "created_at": datetime.now(timezone.utc).isoformat(),
                            "updated_at": datetime.now(timezone.utc).isoformat(),
                        }

                        if getattr(self, 'approval_gate', None):
                            requires_human_approval, approval_status = self.approval_gate.check_approval(
                                chosen_path="",
                                intent=intent,
                                parameters=step_parameters,
                            )
                            approval_state["approval_gate_result"] = {
                                "requires_approval": requires_human_approval,
                                "status": approval_status,
                            }

                        if self.session_manager and context.get("mission_id"):
                            self.session_manager.update_mission_status(
                                session_id=session_id,
                                mission_id=context.get("mission_id"),
                                status="pending_approval",
                                result={"approval_state": approval_state},
                            )

                        self.audit_recorder.record_agent_action(
                            session_id=session_id,
                            agent_id=self.agent_id,
                            action=f"tool_approval_required:{step.tool_name}",
                            input_data={"intent": intent, "step": step.step_id},
                            output_data={
                                "reason": "sensitive_operation_without_enforcer",
                                "approval_required": True,
                                "approval_state": approval_state,
                            },
                            duration_ms=0,
                        )
                        results.append({
                            "step_id": step.step_id,
                            "tool": step.tool_name,
                            "result": {
                                "status": "pending_approval",
                                "approval_required": True,
                                "reason": "sensitive_operation_without_enforcer",
                                "approval_state": approval_state,
                            },
                            "duration_ms": 0,
                        })
                        break

                execution_start = time.time()
                try:
                    tool_result = await tool_instance.execute(context, step_parameters)
                    duration_ms = int((time.time() - execution_start) * 1000)

                    result_schema = ToolResultSchema(
                        status=tool_result.status,
                        data=tool_result.data,
                        error=tool_result.error,
                        audit_ref=tool_result.audit_ref,
                    )

                    self.audit_recorder.record_tool_execution(
                        session_id=session_id,
                        agent_id=self.agent_id,
                        tool_name=step.tool_name,
                        parameters={**parameters, **step.parameters},
                        result=result_schema,
                        duration_ms=duration_ms,
                        metadata={"step_id": step.step_id, "description": step.description},
                    )

                    results.append({
                        "step_id": step.step_id,
                        "tool": step.tool_name,
                        "result": result_schema.to_dict(),
                        "duration_ms": duration_ms,
                    })

                    if tool_result.status == "success":
                        context[f"step_{step.step_id}_result"] = tool_result.data
                        final_result = tool_result.data
                    else:
                        return {
                            "status": "error",
                            "error": tool_result.error or f"Tool {step.tool_name} failed",
                            "session_id": session_id,
                            "completed_steps": results,
                        }

                except Exception as e:
                    duration_ms = int((time.time() - execution_start) * 1000)
                    error_msg = str(e)
                    self.audit_recorder.record_tool_execution(
                        session_id=session_id,
                        agent_id=self.agent_id,
                        tool_name=step.tool_name,
                        parameters={**parameters, **step.parameters},
                        result=ToolResultSchema(status="error", error=error_msg, audit_ref=f"error:{step.tool_name}:{int(time.time()*1000)}"),
                        duration_ms=duration_ms,
                        metadata={"step_id": step.step_id, "description": step.description},
                    )
                    return {
                        "status": "error",
                        "error": error_msg,
                        "session_id": session_id,
                        "completed_steps": results,
                    }

            context["current_step"] = "completed"
            context["last_result"] = final_result
            steps_list = context.get("steps", [])
            steps_list.append({
                "intent": intent,
                "result": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            self.session_manager.update_context(
                session_id,
                {
                    "current_step": "completed",
                    "last_result": final_result,
                    "steps": steps_list,
                },
            )

            total_duration = int((time.time() - start_time) * 1000)
            return {
                "status": "success",
                "session_id": session_id,
                "result": final_result,
                "reasoning": f"Executed {len(results)} steps to fulfill intent: {intent}",
                "steps": results,
                "duration_ms": total_duration,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            context["current_step"] = "failed"
            self.session_manager.update_context(session_id, {"current_step": "failed"})
            return {
                "status": "error",
                "error": str(e),
                "session_id": session_id,
            }

