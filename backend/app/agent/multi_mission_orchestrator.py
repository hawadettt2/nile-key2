"""Multi-Mission Orchestration subsystem.

Provides deterministic, LLM-free scheduling and execution coordination for
multiple Missions under a single Plan.

Components:
- MissionDependencyGraph: DAG representation of inter-mission dependencies.
- MissionOutcome: Structured per-mission execution result.
- PlanOutcome: Aggregated plan-level outcome.
- MultiMissionOrchestrator: Top-level coordinator that respects dependencies,
  supports parallel execution where allowed, propagates failures, and
  preserves existing autonomy / approval / audit contracts.
"""

from typing import Any, Dict, List, Optional, Callable
from datetime import datetime, timezone
import asyncio

from .schemas.enums import MissionStatus, ExecutionMode
from .schemas.mission import Mission
from .execution_engine.orchestrator import ToolOrchestrator
from .outcome import ExecutionOutcome, OutcomeEvaluator, OutcomeFeedbackLoop
from .audit.recorder import AuditRecorder


# ---------------------------------------------------------------------------
# Dependency Graph
# ---------------------------------------------------------------------------

class MissionDependencyGraph:
    """Directed graph encoding inter-mission dependencies inside a Plan.

    Edge semantics: {"from": A, "to": B} means "B depends on A".
    Therefore A must complete before B can start.
    """

    def __init__(self) -> None:
        self._missions: Dict[str, Dict[str, Any]] = {}
        self._dependencies: List[Dict[str, str]] = []
        self._outgoing: Dict[str, List[str]] = {}   # from -> [to, ...]
        self._incoming: Dict[str, List[str]] = {}   # to   -> [from, ...]

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def load_plan(
        self,
        missions: List[Dict[str, Any]],
        dependencies: List[Dict[str, Any]],
    ) -> None:
        """Populate the graph from Plan.missions and Plan.dependencies."""
        for mission in missions:
            mid = mission.get("mission_id") if isinstance(mission, dict) else str(mission)
            if not mid:
                continue
            self._missions[mid] = {
                "status": mission.get("status", "pending") if isinstance(mission, dict) else "pending",
                "priority": mission.get("priority", 5) if isinstance(mission, dict) else 5,
                "mission": mission if isinstance(mission, dict) else {"mission_id": mid},
            }
            self._outgoing.setdefault(mid, [])
            self._incoming.setdefault(mid, [])

        self._dependencies = list(dependencies) if dependencies else []
        for dep in self._dependencies:
            from_id = dep.get("from")
            to_id = dep.get("to")
            if from_id and to_id and from_id in self._missions and to_id in self._missions:
                if to_id not in self._outgoing.get(from_id, []):
                    self._outgoing.setdefault(from_id, []).append(to_id)
                if from_id not in self._incoming.get(to_id, []):
                    self._incoming.setdefault(to_id, []).append(from_id)

    def add_mission(
        self,
        mission_id: str,
        status: str = "pending",
        priority: int = 5,
        mission_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._missions[mission_id] = {
            "status": status,
            "priority": priority,
            "mission": mission_data or {"mission_id": mission_id},
        }
        self._outgoing.setdefault(mission_id, [])
        self._incoming.setdefault(mission_id, [])

    def add_dependency(self, from_id: str, to_id: str) -> None:
        if from_id not in self._missions or to_id not in self._missions:
            return
        if to_id in self._outgoing.get(from_id, []):
            return
        self._outgoing.setdefault(from_id, []).append(to_id)
        self._incoming.setdefault(to_id, []).append(from_id)
        self._dependencies.append({"from": from_id, "to": to_id})

    def mark_completed(self, mission_id: str) -> None:
        if mission_id in self._missions:
            self._missions[mission_id]["status"] = "completed"

    def mark_failed(self, mission_id: str, reason: str = "") -> None:
        if mission_id in self._missions:
            self._missions[mission_id]["status"] = "failed"
            self._missions[mission_id]["failure_reason"] = reason

    def mark_running(self, mission_id: str) -> None:
        if mission_id in self._missions:
            self._missions[mission_id]["status"] = "running"

    def mark_pending_approval(self, mission_id: str) -> None:
        if mission_id in self._missions:
            self._missions[mission_id]["status"] = "pending_approval"

    def remove_mission(self, mission_id: str) -> None:
        """Remove a mission and all edges referencing it."""
        if mission_id not in self._missions:
            return
        for dep in list(self._incoming.get(mission_id, [])):
            if mission_id in self._outgoing.get(dep, []):
                self._outgoing[dep].remove(mission_id)
        for dep in list(self._outgoing.get(mission_id, [])):
            if mission_id in self._incoming.get(dep, []):
                self._incoming[dep].remove(mission_id)
        self._dependencies = [
            d for d in self._dependencies
            if d.get("from") != mission_id and d.get("to") != mission_id
        ]
        self._missions.pop(mission_id, None)
        self._outgoing.pop(mission_id, None)
        self._incoming.pop(mission_id, None)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def is_ready(self, mission_id: str) -> bool:
        """True when the mission is pending and all incoming deps are completed."""
        if mission_id not in self._missions:
            return False
        if self._missions[mission_id]["status"] != "pending":
            return False
        incoming = self._incoming.get(mission_id, [])
        return all(self._missions.get(dep, {}).get("status") == "completed" for dep in incoming)

    def get_ready_missions(self) -> List[str]:
        """Pending missions whose dependencies are all satisfied.

        Sorted by descending priority then ascending mission_id for determinism.
        """
        ready = [
            mid for mid, info in self._missions.items()
            if info["status"] == "pending" and self.is_ready(mid)
        ]
        ready.sort(key=lambda mid: (-self._missions[mid]["priority"], mid))
        return ready

    def get_dependents(self, mission_id: str) -> List[str]:
        """Return missions that directly depend on *mission_id*."""
        return list(self._outgoing.get(mission_id, []))

    def get_all_blocked_by(self, mission_id: str) -> List[str]:
        """Return all missions transitively blocked when *mission_id* fails."""
        blocked: List[str] = []
        queue = list(self._outgoing.get(mission_id, []))
        visited = {mission_id}
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            blocked.append(current)
            queue.extend(self._outgoing.get(current, []))
        return blocked

    def mark_all_blocked_by(self, mission_id: str, reason: str = "") -> None:
        """Mark every transitive dependent as failed."""
        for mid in self.get_all_blocked_by(mission_id):
            if self._missions[mid]["status"] == "pending":
                self.mark_failed(mid, reason)

    def get_mission_status(self, mission_id: str) -> Optional[str]:
        if mission_id in self._missions:
            return self._missions[mission_id]["status"]
        return None

    def get_pending_missions(self) -> List[str]:
        return [mid for mid, info in self._missions.items() if info["status"] == "pending"]

    def all_completed(self) -> bool:
        return bool(self._missions) and all(
            info["status"] == "completed" for info in self._missions.values()
        )

    def get_completed_missions(self) -> List[str]:
        return [mid for mid, info in self._missions.items() if info["status"] == "completed"]

    def get_failed_missions(self) -> List[str]:
        return [mid for mid, info in self._missions.items() if info["status"] == "failed"]

    def get_running_missions(self) -> List[str]:
        return [mid for mid, info in self._missions.items() if info["status"] == "running"]


# ---------------------------------------------------------------------------
# Outcome types
# ---------------------------------------------------------------------------

class MissionOutcome:
    """Structured outcome for a single mission execution."""

    def __init__(
        self,
        mission_id: str,
        status: str,
        execution_output: Dict[str, Any],
        duration_ms: Optional[float] = None,
        error: Optional[str] = None,
    ) -> None:
        self.mission_id = mission_id
        self.status = status
        self.execution_output = execution_output or {}
        self.duration_ms = duration_ms
        self.error = error
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "status": self.status,
            "execution_output": self.execution_output,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "timestamp": self.timestamp,
        }


class PlanOutcome:
    """Aggregated outcome of every mission within a Plan."""

    def __init__(self, plan_id: str) -> None:
        self.plan_id = plan_id
        self.mission_outcomes: Dict[str, MissionOutcome] = {}
        self.status: str = "pending"
        self.aggregated_results: List[Dict[str, Any]] = []
        self.failed_mission_ids: List[str] = []
        self.blocked_mission_ids: List[str] = []
        self.execution_metadata: Dict[str, Any] = {}
        self.completed_at: Optional[str] = None

    def add_mission_outcome(self, outcome: MissionOutcome) -> None:
        self.mission_outcomes[outcome.mission_id] = outcome
        if outcome.status == "completed":
            self.aggregated_results.extend(outcome.execution_output.get("results", []) or [])
        elif outcome.status == "failed":
            self.failed_mission_ids.append(outcome.mission_id)
        elif outcome.status in ("blocked", "partial"):
            self.blocked_mission_ids.append(outcome.mission_id)

    def compute_plan_status(self) -> str:
        if not self.mission_outcomes:
            return "pending"
        if all(o.status == "completed" for o in self.mission_outcomes.values()):
            return "completed"
        if any(o.status == "failed" for o in self.mission_outcomes.values()):
            return "failed"
        if any(
            o.status in ("partial", "pending_approval", "blocked")
            for o in self.mission_outcomes.values()
        ):
            return "partial"
        return "partial"

    def finalize(self) -> None:
        self.status = self.compute_plan_status()
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.execution_metadata = {
            "total_missions": len(self.mission_outcomes),
            "completed_count": sum(
                1 for o in self.mission_outcomes.values() if o.status == "completed"
            ),
            "failed_count": len(self.failed_mission_ids),
            "blocked_count": len(self.blocked_mission_ids),
            "partial_count": sum(
                1 for o in self.mission_outcomes.values() if o.status == "partial"
            ),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "status": self.status,
            "mission_outcomes": {
                mid: o.to_dict() for mid, o in self.mission_outcomes.items()
            },
            "aggregated_results": self.aggregated_results,
            "failed_mission_ids": self.failed_mission_ids,
            "blocked_mission_ids": self.blocked_mission_ids,
            "execution_metadata": self.execution_metadata,
            "completed_at": self.completed_at,
        }


# ---------------------------------------------------------------------------
# Multi-Mission Orchestrator
# ---------------------------------------------------------------------------

class MultiMissionOrchestrator:
    """Deterministic orchestrator for multiple Missions under a single Plan.

    Design principles:
    - Dependency enforcement is deterministic (no LLM involvement).
    - Existing ToolOrchestrator is reused per mission; no new execution engine.
    - Existing ReplanningHandler is reused when a mission failure requires
      strategic replanning.
    - Existing AutonomyPolicyInterpreter / ApprovalGate contracts are
      preserved because ToolOrchestrator continues to own per-task approval.
    - OutcomeFeedbackLoop is reused for per-mission outcome integration.
    """

    def __init__(
        self,
        tool_orchestrator: ToolOrchestrator,
        session_manager=None,
        outcome_feedback_loop: Optional[OutcomeFeedbackLoop] = None,
        audit_recorder: Optional[AuditRecorder] = None,
        replanning_handler=None,
    ) -> None:
        self.tool_orchestrator = tool_orchestrator
        self.session_manager = session_manager
        self.outcome_feedback_loop = outcome_feedback_loop
        self.audit_recorder = audit_recorder
        self.replanning_handler = replanning_handler

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def execute_plan(
        self,
        plan: Any,
        mission_store: Any,
        session_context: Optional[Dict[str, Any]] = None,
    ) -> PlanOutcome:
        """Execute all missions in a Plan while respecting dependencies.

        Args:
            plan: Plan-like object (Plan model or dict with ``missions``
                  and ``dependencies``).
            mission_store: dict or callable ``(mission_id) -> mission_dict``
                           used to resolve each mission for execution.
            session_context: Optional dict forwarded to ToolOrchestrator.

        Returns:
            PlanOutcome with per-mission outcomes and aggregated results.
        """
        session_context = session_context or {}
        plan_id = getattr(plan, "plan_id", None) or str(
            plan.get("plan_id", "") if isinstance(plan, dict) else ""
        )

        raw_missions = getattr(plan, "missions", None) or (
            plan.get("missions", []) if isinstance(plan, dict) else []
        )
        raw_dependencies = getattr(plan, "dependencies", None) or (
            plan.get("dependencies", []) if isinstance(plan, dict) else []
        )

        # Resolve mission dicts from the store
        mission_data_list: List[Dict[str, Any]] = []
        for raw in raw_missions:
            if isinstance(raw, dict):
                mission_data_list.append(raw)
            else:
                mission_data_list.append(
                    await self._resolve_mission(str(raw), mission_store)
                )

        # Determine execution mode (default sequential)
        execution_mode = "sequential"
        if isinstance(getattr(plan, "metadata", None), dict):
            execution_mode = plan.metadata.get("execution_mode", "sequential")
        if not execution_mode:
            execution_mode = session_context.get("execution_mode", "sequential")

        # Build dependency graph
        graph = MissionDependencyGraph()
        graph.load_plan(mission_data_list, raw_dependencies)

        plan_outcome = PlanOutcome(plan_id=plan_id)

        # Main deterministic scheduling loop
        max_iterations = len(mission_data_list) + 1
        for _ in range(max_iterations):
            if graph.all_completed() or not graph.get_pending_missions():
                break

            ready = graph.get_ready_missions()
            if not ready:
                # Nothing ready but pending remains -> circular / blocked deps
                for mid in graph.get_pending_missions():
                    graph.mark_failed(mid, reason="blocked_by_dependency")
                    plan_outcome.add_mission_outcome(
                        MissionOutcome(mid, "blocked", {"error": "blocked_by_dependency"})
                    )
                break

            if execution_mode == ExecutionMode.PARALLEL.value:
                batch_outcomes = await self._execute_parallel_batch(
                    ready, graph, mission_store, session_context
                )
                for outcome in batch_outcomes:
                    plan_outcome.add_mission_outcome(outcome)
            else:
                for mission_id in ready:
                    if graph.get_mission_status(mission_id) != "pending":
                        continue
                    outcome = await self._execute_single_mission(
                        mission_id, graph, mission_store, session_context
                    )
                    plan_outcome.add_mission_outcome(outcome)

        # Capture any missions that were never executed (e.g. blocked by
        # dependency failure) so callers can inspect every mission outcome.
        for mid, info in graph._missions.items():
            if mid not in plan_outcome.mission_outcomes:
                status = info.get("status", "pending")
                if status == "failed":
                    plan_outcome.add_mission_outcome(
                        MissionOutcome(mid, "blocked", {"error": info.get("failure_reason", "blocked_by_dependency")})
                    )
                elif status == "pending_approval":
                    plan_outcome.add_mission_outcome(
                        MissionOutcome(mid, "pending_approval", {"error": "Approval required"})
                    )
                else:
                    plan_outcome.add_mission_outcome(
                        MissionOutcome(mid, "pending", {})
                    )

        plan_outcome.finalize()
        return plan_outcome

    async def execute_plan_with_feedback(
        self,
        plan: Any,
        mission_store: Any,
        session_context: Optional[Dict[str, Any]] = None,
        goal_plan_context: Optional[Dict[str, Any]] = None,
        trigger_replanning_on: Optional[List[str]] = None,
    ) -> PlanOutcome:
        """Execute the plan and pipe each mission outcome through the
        existing OutcomeFeedbackLoop.

        Optionally triggers ReplanningHandler when mission failure categories
        match ``trigger_replanning_on``.
        """
        trigger_replanning_on = trigger_replanning_on or ["no_viable_path", "constraint_conflict"]
        goal_plan_context = goal_plan_context or {}

        plan_outcome = await self.execute_plan(plan, mission_store, session_context)

        for mission_id, mission_outcome in plan_outcome.mission_outcomes.items():
            execution_output = mission_outcome.execution_output
            exec_outcome = ExecutionOutcome(
                execution_output=execution_output,
                mission_id=mission_id,
                session_id=session_context.get("session_id", "") if session_context else "",
                goal_id=goal_plan_context.get("goal_id"),
                plan_id=(
                    getattr(plan, "plan_id", None)
                    or (plan.get("plan_id") if isinstance(plan, dict) else None)
                ),
            )
            evaluated = OutcomeEvaluator().evaluate(exec_outcome)

            if self.outcome_feedback_loop:
                await self.outcome_feedback_loop.process(
                    outcome=evaluated,
                    goal_plan_context=goal_plan_context,
                    session_context=session_context or {},
                )

            # Trigger replanning when required
            if (
                evaluated.status == "failure"
                and self.replanning_handler
                and evaluated.evaluation.get("failure_category") in trigger_replanning_on
            ):
                goal_id = goal_plan_context.get("goal_id")
                old_plan_id = getattr(plan, "plan_id", None)
                user_id = goal_plan_context.get("user_id")
                session_id = session_context.get("session_id", "") if session_context else ""
                if goal_id and old_plan_id and user_id:
                    self._trigger_replanning(
                        goal_id=goal_id,
                        old_plan_id=old_plan_id,
                        user_id=user_id,
                        session_id=session_id,
                        reason=evaluated.evaluation.get("failure_category", "mission_failure"),
                    )

        return plan_outcome

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _execute_single_mission(
        self,
        mission_id: str,
        graph: MissionDependencyGraph,
        mission_store: Any,
        session_context: Dict[str, Any],
    ) -> MissionOutcome:
        graph.mark_running(mission_id)
        mission_data = await self._resolve_mission(mission_id, mission_store)

        session_id = session_context.get("session_id", "")

        if self.audit_recorder:
            try:
                self.audit_recorder.record_agent_action(
                    session_id=session_id,
                    agent_id="multi_mission_orchestrator",
                    action="mission_started",
                    input_data={
                        "mission_id": mission_id,
                        "mission_type": mission_data.get("mission_type"),
                    },
                    output_data={"status": "running"},
                )
            except Exception:
                pass

        start_time = datetime.now(timezone.utc)
        try:
            execution_result = await self.tool_orchestrator.execute(
                mission_data, session_context
            )
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

            mission_status = execution_result.get("mission_status", "failed")
            error = None
            if mission_status == "failed":
                error = (execution_result.get("failure_summary") or {}).get("error")
            elif mission_status == "pending_approval":
                error = "Approval required"

            if mission_status == "completed":
                graph.mark_completed(mission_id)
            elif mission_status == "pending_approval":
                graph.mark_pending_approval(mission_id)
                graph.mark_all_blocked_by(mission_id, reason="pending_approval")
            else:
                graph.mark_failed(mission_id, error or "execution_failed")
                graph.mark_all_blocked_by(mission_id, reason="dependency_failed")

            outcome_status = "failed" if mission_status == "failed" else mission_status
            outcome = MissionOutcome(
                mission_id=mission_id,
                status=outcome_status,
                execution_output=execution_result,
                duration_ms=duration_ms,
                error=error,
            )
        except Exception as exc:
            duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            graph.mark_failed(mission_id, str(exc))
            graph.mark_all_blocked_by(mission_id, reason="execution_error")
            outcome = MissionOutcome(
                mission_id=mission_id,
                status="failed",
                execution_output={"error": str(exc), "mission_status": "failed"},
                duration_ms=duration_ms,
                error=str(exc),
            )

        if self.audit_recorder:
            try:
                self.audit_recorder.record_agent_action(
                    session_id=session_id,
                    agent_id="multi_mission_orchestrator",
                    action="mission_completed",
                    input_data={"mission_id": mission_id},
                    output_data={"status": outcome.status, "error": outcome.error},
                )
            except Exception:
                pass

        return outcome

    async def _execute_parallel_batch(
        self,
        mission_ids: List[str],
        graph: MissionDependencyGraph,
        mission_store: Any,
        session_context: Dict[str, Any],
    ) -> List[MissionOutcome]:
        pending = [
            mid for mid in mission_ids if graph.get_mission_status(mid) == "pending"
        ]
        if not pending:
            return []
        return list(
            await asyncio.gather(
                *(
                    self._execute_single_mission(mid, graph, mission_store, session_context)
                    for mid in pending
                )
            )
        )

    async def _resolve_mission(
        self, mission_id: str, mission_store: Any
    ) -> Dict[str, Any]:
        if callable(mission_store):
            if asyncio.iscoroutinefunction(mission_store):
                data = await mission_store(mission_id)
            else:
                data = mission_store(mission_id)
        elif isinstance(mission_store, dict):
            data = mission_store.get(mission_id, {})
        else:
            data = {}
        return data if data else {"mission_id": mission_id}

    def _trigger_replanning(
        self,
        goal_id: str,
        old_plan_id: str,
        user_id: int,
        session_id: str,
        reason: str,
    ) -> Dict[str, Any]:
        try:
            return self.replanning_handler.execute(
                goal_id=goal_id,
                old_plan_id=old_plan_id,
                user_id=user_id,
                session_id=session_id,
                db_factory=None,
                goal_repository=None,
                plan_planner=None,
                plan_manager=None,
                session_manager=self.session_manager,
                trigger="no_viable_path",
                reason=reason,
            )
        except Exception:
            return {"success": False, "error": "replanning_exception"}
