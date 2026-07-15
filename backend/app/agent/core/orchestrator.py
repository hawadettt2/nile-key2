import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from ..tools.registry import tool_registry, ToolRegistry
from ..tools.base import BaseTool, ToolResult
from ..core.planner import Planner, ExecutionPlan
from ..audit.recorder import AuditRecorder
from ..session.manager import SessionManager
from ..schemas.tool_result import ToolResultSchema


class AgentOrchestrator:
    def __init__(
        self,
        tool_registry: ToolRegistry,
        session_manager: SessionManager,
        audit_recorder: AuditRecorder,
        agent_id: str = "wp30-digital-export-manager",
    ):
        self.tool_registry = tool_registry
        self.session_manager = session_manager
        self.audit_recorder = audit_recorder
        self.agent_id = agent_id
        self.planner = Planner()

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

                execution_start = time.time()
                try:
                    tool_result = await tool_instance.execute(context, {**parameters, **step.parameters})
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
                        result=ToolResultSchema(status="error", error=error_msg),
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

