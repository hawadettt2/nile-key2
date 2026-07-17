from typing import Optional, Dict, Any, List, Union
from datetime import datetime, timezone
import asyncio

from ..schemas.enums import TaskStatus, MissionStatus
from ..tools.base import BaseTool, ToolResult
from ..tools.registry import ToolRegistry
from ..schemas.mission import Mission
from ..exceptions import ExecutionEngineException, ToolNotFoundException, ToolExecutionException
from ..approval.gate import ApprovalGate
from ..monitoring.service import MonitoringService


class ExecutionStep:
    def __init__(self, task_id, tool_name, start_time, finish_time, execution_status, result, retry_count=0):
        self.task_id = task_id
        self.tool_name = tool_name
        self.start_time = start_time
        self.finish_time = finish_time
        self.execution_status = execution_status
        self.result = result
        self.retry_count = retry_count

    def to_dict(self):
        result = self.result
        if hasattr(result, "to_dict"):
            result = result.to_dict()
        elif result is None:
            result = None
        return {
            "task_id": self.task_id,
            "tool_name": self.tool_name,
            "start_time": self.start_time.isoformat() if isinstance(self.start_time, datetime) else self.start_time,
            "finish_time": self.finish_time.isoformat() if isinstance(self.finish_time, datetime) else self.finish_time,
            "execution_status": self.execution_status,
            "result": result,
            "retry_count": self.retry_count,
        }


class ToolOrchestrator:
    """Tool Orchestrator for the Digital Export Manager.

    Executes ExecutionPlans by invoking Tools via the Tool Registry.
    Supports sequential execution with stop-on-failure semantics,
    retry with backoff, idempotency propagation, and graceful degradation.
    """

    def __init__(self, tool_registry=None, audit_recorder=None, session_manager=None, approval_gate=None, monitoring_service=None):
        self.tool_registry = tool_registry
        self.audit_recorder = audit_recorder
        self.session_manager = session_manager
        self.approval_gate = approval_gate or ApprovalGate()
        self.monitoring_service = monitoring_service or MonitoringService()

    async def execute(self, execution_plan, session_context=None) -> Dict[str, Any]:
        """Execute an ExecutionPlan sequentially.

        Args:
            execution_plan: ExecutionPlan, Mission, or dict with tasks list
            session_context: Optional session context dict passed to tools

        Returns:
            Dict containing:
                - execution_trace: list of structured step records
                - mission_status: final mission status
                - results: list of successful tool result dicts
                - failed_task_id: task_id that caused failure, or None
                - degraded: bool indicating if execution was degraded
                - failure_summary: structured failure information
        """
        tasks = []
        mission_id = None
        execution_policy = {}
        idempotency_key = None

        if isinstance(execution_plan, Mission):
            mission_id = execution_plan.mission_id
            execution_policy = execution_plan.execution_policy or {}
            idempotency_key = execution_plan.idempotency_key
            tasks = execution_plan.payload.get("tasks", []) if isinstance(execution_plan.payload, dict) else []
            if not tasks:
                tasks = execution_policy.get("tasks", [])
        elif hasattr(execution_plan, "tasks"):
            tasks = execution_plan.tasks
            mission_id = getattr(execution_plan, "mission_id", None)
            if hasattr(execution_plan, "execution_policy"):
                execution_policy = execution_plan.execution_policy or {}
            if hasattr(execution_plan, "idempotency_key"):
                idempotency_key = execution_plan.idempotency_key
        elif isinstance(execution_plan, dict):
            tasks = execution_plan.get("tasks", [])
            mission_id = execution_plan.get("mission_id")
            execution_policy = execution_plan.get("execution_policy", {})
            idempotency_key = execution_plan.get("idempotency_key")

        if not tasks:
            return {
                "execution_trace": [],
                "mission_status": MissionStatus.COMPLETED.value,
                "results": [],
                "failed_task_id": None,
                "degraded": False,
                "failure_summary": {},
            }

        retry_policy = self._get_retry_policy_from_policy(execution_policy, session_context)
        if not idempotency_key:
            idempotency_key = self._get_idempotency_key_from_context(session_context)

        execution_trace: List[Dict[str, Any]] = []
        results: List[Dict[str, Any]] = []
        failed_task_id = None
        mission_status = MissionStatus.COMPLETED.value
        context = session_context or {}
        completed_task_ids = set()

        for task_dict in tasks:
            task_id = task_dict.get("task_id")
            tool_name = task_dict.get("tool_name")
            parameters = task_dict.get("parameters", {})
            depends_on = task_dict.get("depends_on", []) or []

            if failed_task_id is not None:
                task_dict["status"] = TaskStatus.FAILED.value
                task_dict["result"] = {"error": "Skipped due to previous failure"}
                execution_trace.append(
                    ExecutionStep(
                        task_id=task_id,
                        tool_name=tool_name,
                        start_time=datetime.now(timezone.utc),
                        finish_time=datetime.now(timezone.utc),
                        execution_status="skipped",
                        result=ToolResult(status="skipped", error="Skipped due to previous failure"),
                    ).to_dict()
                )
                if self.monitoring_service:
                    self.monitoring_service.record_task_execution(
                        mission_id=mission_id or "",
                        task_id=task_id,
                        tool_name=tool_name,
                        execution_status="skipped",
                        execution_time_ms=0.0,
                        retry_count=0,
                        error="Skipped due to previous failure",
                    )
                continue

            if depends_on:
                missing_deps = [dep for dep in depends_on if dep not in completed_task_ids]
                if missing_deps:
                    task_dict["status"] = TaskStatus.FAILED.value
                    task_dict["result"] = {"error": f"Skipped due to unmet dependencies: {missing_deps}"}
                    execution_trace.append(
                        ExecutionStep(
                            task_id=task_id,
                            tool_name=tool_name,
                            start_time=datetime.now(timezone.utc),
                            finish_time=datetime.now(timezone.utc),
                            execution_status="skipped",
                            result=ToolResult(status="skipped", error=f"Skipped due to unmet dependencies: {missing_deps}"),
                        ).to_dict()
                    )
                    failed_task_id = task_id
                    mission_status = MissionStatus.FAILED.value
                    if self.monitoring_service:
                        self.monitoring_service.record_task_execution(
                            mission_id=mission_id or "",
                            task_id=task_id,
                            tool_name=tool_name,
                            execution_status="skipped",
                            execution_time_ms=0.0,
                            retry_count=0,
                            error=f"Skipped due to unmet dependencies: {missing_deps}",
                        )
                    continue

            requires_approval, approval_status = self.approval_gate.check_approval(
                chosen_path=context.get("chosen_path", ""),
                intent=context.get("intent", ""),
                parameters=parameters,
            )
            if requires_approval:
                task_dict["status"] = TaskStatus.PENDING.value
                task_dict["result"] = {"approval_required": True, "approval_status": approval_status}
                execution_trace.append(
                    ExecutionStep(
                        task_id=task_id,
                        tool_name=tool_name,
                        start_time=datetime.now(timezone.utc),
                        finish_time=datetime.now(timezone.utc),
                        execution_status="pending_approval",
                        result=ToolResult(status="pending_approval", error="Approval required before execution"),
                    ).to_dict()
                )
                failed_task_id = task_id
                mission_status = MissionStatus.FAILED.value
                if self.monitoring_service:
                    self.monitoring_service.record_task_execution(
                        mission_id=mission_id or "",
                        task_id=task_id,
                        tool_name=tool_name,
                        execution_status="pending_approval",
                        execution_time_ms=0.0,
                        retry_count=0,
                        error="Approval required before execution",
                    )
                continue

            start_time = datetime.now(timezone.utc)

            if not self.tool_registry or not self.tool_registry.has_tool(tool_name):
                error_msg = f"Tool not found: {tool_name}"
                task_dict["status"] = TaskStatus.FAILED.value
                task_dict["result"] = {"error": error_msg}
                failed_task_id = task_id
                mission_status = MissionStatus.FAILED.value
                execution_trace.append(
                    ExecutionStep(
                        task_id=task_id,
                        tool_name=tool_name,
                        start_time=start_time,
                        finish_time=datetime.now(timezone.utc),
                        execution_status="failed",
                        result=ToolResult(status="error", error=error_msg),
                    ).to_dict()
                )
                continue

            tool = self.tool_registry.create_instance(tool_name)
            if tool is None:
                error_msg = f"Failed to instantiate tool: {tool_name}"
                task_dict["status"] = TaskStatus.FAILED.value
                task_dict["result"] = {"error": error_msg}
                failed_task_id = task_id
                mission_status = MissionStatus.FAILED.value
                execution_trace.append(
                    ExecutionStep(
                        task_id=task_id,
                        tool_name=tool_name,
                        start_time=start_time,
                        finish_time=datetime.now(timezone.utc),
                        execution_status="failed",
                        result=ToolResult(status="error", error=error_msg),
                    ).to_dict()
                )
                continue

            if idempotency_key is not None:
                parameters = {**parameters, "idempotency_key": idempotency_key}

            tool_result, exhausted = await self._execute_tool_with_retry(
                tool, context, parameters, retry_policy, start_time, task_id, tool_name,
                execution_trace, task_dict
            )

            if tool_result is not None:
                results.append(tool_result.to_dict())
                if tool_result.status == "success":
                    completed_task_ids.add(task_id)
                else:
                    failed_task_id = task_id
                    mission_status = MissionStatus.FAILED.value

                finish_time = datetime.now(timezone.utc)
                execution_time_ms = (finish_time - start_time).total_seconds() * 1000
                retry_count = task_dict.get("retry_count", 0)
                error_message = tool_result.error if hasattr(tool_result, "error") else None
                if self.monitoring_service:
                    self.monitoring_service.record_task_execution(
                        mission_id=mission_id or "",
                        task_id=task_id,
                        tool_name=tool_name,
                        execution_status=tool_result.status,
                        execution_time_ms=execution_time_ms,
                        retry_count=retry_count,
                        error=error_message,
                    )

        if self.session_manager and mission_id:
            try:
                self.session_manager.update_mission_status(
                    mission_id,
                    mission_status,
                    {"results": results, "failed_task_id": failed_task_id},
                )
            except Exception:
                pass

        if self.monitoring_service and mission_id:
            self.monitoring_service.record_mission_completed(mission_id, mission_status)

        failure_summary = self._build_failure_summary(failed_task_id, execution_trace, tasks)
        degraded = failed_task_id is not None

        return {
            "execution_trace": execution_trace,
            "mission_status": mission_status,
            "results": results,
            "failed_task_id": failed_task_id,
            "degraded": degraded,
            "failure_summary": failure_summary,
        }

    async def _execute_tool_with_retry(self, tool, context, parameters, retry_policy, start_time, task_id, tool_name, execution_trace, task_dict):
        max_retries = retry_policy.get("max_retries", 2)
        backoff_seconds = retry_policy.get("backoff_seconds", 0)
        last_result = None

        for attempt in range(max_retries + 1):
            attempt_start = datetime.now(timezone.utc)
            try:
                tool_result = await tool.execute(context, parameters)
            except Exception as e:
                attempt_finish = datetime.now(timezone.utc)
                error_result = ToolResult(status="error", error=str(e))
                execution_trace.append(
                    ExecutionStep(
                        task_id=task_id,
                        tool_name=tool_name,
                        start_time=attempt_start,
                        finish_time=attempt_finish,
                        execution_status="failed",
                        result=error_result,
                        retry_count=attempt,
                    ).to_dict()
                )
                if not self._is_retryable_exception(e):
                    task_dict["status"] = TaskStatus.FAILED.value
                    task_dict["result"] = error_result.to_dict()
                    return error_result, False
                last_result = error_result
                if attempt < max_retries and backoff_seconds > 0:
                    await asyncio.sleep(backoff_seconds)
                continue

            attempt_finish = datetime.now(timezone.utc)

            if tool_result.status == "success":
                task_dict["status"] = TaskStatus.COMPLETED.value
                task_dict["result"] = tool_result.to_dict()
                execution_trace.append(
                    ExecutionStep(
                        task_id=task_id,
                        tool_name=tool_name,
                        start_time=attempt_start,
                        finish_time=attempt_finish,
                        execution_status="completed",
                        result=tool_result,
                        retry_count=attempt,
                    ).to_dict()
                )
                return tool_result, False

            execution_trace.append(
                ExecutionStep(
                    task_id=task_id,
                    tool_name=tool_name,
                    start_time=attempt_start,
                    finish_time=attempt_finish,
                    execution_status="failed",
                    result=tool_result,
                    retry_count=attempt,
                ).to_dict()
            )

            if not self._is_retryable_tool_result(tool_result):
                task_dict["status"] = TaskStatus.FAILED.value
                task_dict["result"] = tool_result.to_dict()
                return tool_result, False

            last_result = tool_result
            if attempt < max_retries and backoff_seconds > 0:
                await asyncio.sleep(backoff_seconds)

        finish_time = datetime.now(timezone.utc)
        task_dict["status"] = TaskStatus.FAILED.value
        task_dict["result"] = last_result.to_dict() if last_result else {"error": "Retry exhausted"}
        execution_trace.append(
            ExecutionStep(
                task_id=task_id,
                tool_name=tool_name,
                start_time=start_time,
                finish_time=finish_time,
                execution_status="failed",
                result=last_result,
                retry_count=max_retries,
            ).to_dict()
        )
        return last_result, True

    def _is_retryable_exception(self, exception: Exception) -> bool:
        retryable_types = (ConnectionError, TimeoutError, OSError)
        if isinstance(exception, retryable_types):
            return True
        error_msg = str(exception).lower()
        transient_keywords = ["transient", "temporary", "timeout", "connection", "unavailable"]
        return any(kw in error_msg for kw in transient_keywords)

    def _is_retryable_tool_result(self, tool_result: ToolResult) -> bool:
        if tool_result.status != "error":
            return False
        error_msg = (tool_result.error or "").lower()
        transient_keywords = ["transient", "temporary", "timeout", "connection", "unavailable", "rate limit"]
        return any(kw in error_msg for kw in transient_keywords)

    def _get_retry_policy_from_policy(self, execution_policy: Dict[str, Any], session_context) -> Dict[str, Any]:
        policy = {
            "max_retries": 2,
            "backoff_seconds": 0,
        }

        if isinstance(execution_policy, dict):
            retry_policy = execution_policy.get("retry_policy", {})
            if isinstance(retry_policy, dict):
                policy.update(retry_policy)

        if session_context and isinstance(session_context, dict):
            ctx_policy = session_context.get("execution_policy", {})
            if isinstance(ctx_policy, dict):
                retry_policy = ctx_policy.get("retry_policy", {})
                if isinstance(retry_policy, dict):
                    policy.update(retry_policy)

        return policy

    def _get_idempotency_key_from_context(self, session_context) -> Optional[str]:
        if session_context and isinstance(session_context, dict):
            key = session_context.get("idempotency_key")
            if key:
                return key
        return None

    def _build_failure_summary(self, failed_task_id, execution_trace, tasks) -> Dict[str, Any]:
        if not failed_task_id:
            return {}

        failed_task = None
        for task in tasks:
            if task.get("task_id") == failed_task_id:
                failed_task = task
                break

        failed_step = None
        for step in reversed(execution_trace):
            if step.get("task_id") == failed_task_id and step.get("execution_status") in ("failed", "skipped"):
                failed_step = step
                break

        completed_count = sum(1 for step in execution_trace if step.get("execution_status") == "completed")
        total_count = len(tasks)

        error = None
        if failed_step:
            step_result = failed_step.get("result")
            if isinstance(step_result, dict):
                error = step_result.get("error")
            elif step_result is not None and hasattr(step_result, "error"):
                error = step_result.error

        return {
            "failed_task_id": failed_task_id,
            "failed_tool_name": failed_task.get("tool_name") if failed_task else None,
            "error": error,
            "completed_tasks_count": completed_count,
            "total_tasks_count": total_count,
            "retry_exhausted": failed_step.get("retry_count", 0) > 0 if failed_step else False,
            "can_degrade": completed_count > 0,
        }
