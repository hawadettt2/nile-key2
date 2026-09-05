"""Extract patterns from Goal / Plan / Mission / Outcome / Feedback / Memory."""

from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.agent.memory.cross_system import recall_cross_component


class ExtractedPatterns:
    """Container for extracted operational patterns."""

    def __init__(self) -> None:
        self.total_executions: int = 0
        self.success_count: int = 0
        self.failure_count: int = 0
        self.partial_count: int = 0
        self.recent_failures: List[Dict[str, Any]] = []
        self.failure_categories: Dict[str, int] = {}
        self.operation_outcomes: Dict[str, Dict[str, Any]] = {}
        self.goal_progress: Dict[str, Any] = {}
        self.plan_completion_rate: float = 0.0
        self.has_successful_pattern: bool = False
        self.has_repeated_failure: bool = False
        self.memory_restrictions: List[Dict[str, Any]] = []
        self.memory_preferences: List[Dict[str, Any]] = []
        self.evidence: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_executions": self.total_executions,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "partial_count": self.partial_count,
            "recent_failures": self.recent_failures,
            "failure_categories": self.failure_categories,
            "operation_outcomes": self.operation_outcomes,
            "goal_progress": self.goal_progress,
            "plan_completion_rate": self.plan_completion_rate,
            "has_successful_pattern": self.has_successful_pattern,
            "has_repeated_failure": self.has_repeated_failure,
            "memory_restrictions": self.memory_restrictions,
            "memory_preferences": self.memory_preferences,
            "evidence": self.evidence,
        }


class PatternExtractor:
    """Deterministic extractor of operational patterns from existing state.

    Uses Goal / Plan / Mission metadata, execution history, Outcome / Feedback,
    and MemoryProvider recall to build evidence-backed patterns.
    """

    RECENT_FAILURE_WINDOW = 5
    MIN_HISTORY_FOR_PATTERN = 3
    SUCCESS_RATE_THRESHOLD = 0.8
    FAILURE_RATE_THRESHOLD = 0.3

    def extract(
        self,
        goal: Optional[Any] = None,
        plan: Optional[Any] = None,
        missions: Optional[List[Any]] = None,
        execution_history: Optional[List[Dict[str, Any]]] = None,
        memory_provider: Optional[Any] = None,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> ExtractedPatterns:
        """Extract patterns from available state.

        Args:
            goal: Goal model instance.
            plan: Plan model instance.
            missions: List of Mission model instances.
            execution_history: List of execution history entries.
            memory_provider: Optional MemoryProvider for additional signals.
            user_id: User identifier for memory recall.
            session_id: Session identifier for memory recall.

        Returns:
            ExtractedPatterns with deterministic pattern signals.
        """
        patterns = ExtractedPatterns()
        history = execution_history or []

        if goal is not None:
            patterns.goal_progress = self._extract_goal_progress(goal)
            patterns.evidence.append({
                "source": "goal",
                "reference_id": getattr(goal, "goal_id", None),
                "data": {
                    "status": getattr(goal, "status", None),
                    "metadata": getattr(goal, "metadata", {}) or {},
                },
            })

        if plan is not None:
            patterns.plan_completion_rate = self._compute_plan_completion_rate(plan, missions or [])
            patterns.evidence.append({
                "source": "plan",
                "reference_id": getattr(plan, "plan_id", None),
                "data": {
                    "status": getattr(plan, "status", None),
                    "missions_count": len(getattr(plan, "missions", []) or []),
                },
            })

        for entry in history:
            status = entry.get("status")
            if status == "success":
                patterns.success_count += 1
            elif status == "failure":
                patterns.failure_count += 1
                patterns.recent_failures.append(entry)
            elif status == "partial":
                patterns.partial_count += 1

            evaluation = entry.get("evaluation", {})
            operation = evaluation.get("operation") or entry.get("mission_id") or "unknown"
            if operation not in patterns.operation_outcomes:
                patterns.operation_outcomes[operation] = {"success": 0, "failure": 0, "partial": 0}
            if status == "success":
                patterns.operation_outcomes[operation]["success"] += 1
            elif status == "failure":
                patterns.operation_outcomes[operation]["failure"] += 1
            elif status == "partial":
                patterns.operation_outcomes[operation]["partial"] += 1

            failure_category = evaluation.get("failure_category")
            if failure_category and failure_category != "none":
                patterns.failure_categories[failure_category] = patterns.failure_categories.get(failure_category, 0) + 1

        patterns.total_executions = len(history)
        patterns.recent_failures = patterns.recent_failures[-self.RECENT_FAILURE_WINDOW:]

        if patterns.total_executions >= self.MIN_HISTORY_FOR_PATTERN:
            success_rate = patterns.success_count / patterns.total_executions
            if success_rate >= self.SUCCESS_RATE_THRESHOLD:
                patterns.has_successful_pattern = True
            failure_rate = patterns.failure_count / patterns.total_executions
            if failure_rate >= self.FAILURE_RATE_THRESHOLD:
                patterns.has_repeated_failure = True

        if memory_provider and user_id and session_id:
            patterns.memory_restrictions = self._recall_memory(memory_provider, user_id, session_id, "standing_order")
            patterns.memory_preferences = self._recall_memory(memory_provider, user_id, session_id, "preference")

            cross_component_patterns = self._recall_cross_component_memory(
                memory_provider, user_id, session_id, "insights", "cross_component_pattern"
            )
            if cross_component_patterns:
                patterns.evidence.append({
                    "source": "cross_component_memory",
                    "reference_id": session_id,
                    "data": {
                        "pattern_count": len(cross_component_patterns),
                        "components": list({
                            m.get("key", "").split(":")[0] if m.get("key") else "unknown"
                            for m in cross_component_patterns
                            if isinstance(m, dict)
                        }),
                    },
                })

            patterns.evidence.append({
                "source": "memory",
                "reference_id": session_id,
                "data": {
                    "restriction_count": len(patterns.memory_restrictions),
                    "preference_count": len(patterns.memory_preferences),
                },
            })

        return patterns

    def _extract_goal_progress(self, goal: Any) -> Dict[str, Any]:
        status = getattr(goal, "status", None)
        metadata = getattr(goal, "metadata", {}) or {}
        history = metadata.get("execution_history", []) if isinstance(metadata, dict) else []
        total = len(history)
        successes = sum(1 for entry in history if entry.get("status") == "success")
        failures = sum(1 for entry in history if entry.get("status") == "failure")
        completion_estimate = successes / total if total > 0 else 0.0
        return {
            "status": status,
            "execution_count": total,
            "success_count": successes,
            "failure_count": failures,
            "completion_estimate": completion_estimate,
        }

    def _compute_plan_completion_rate(self, plan: Any, missions: List[Any]) -> float:
        mission_list = getattr(plan, "missions", []) or []
        total = len(mission_list)
        if total == 0:
            return 0.0
        completed = sum(1 for m in missions if getattr(m, "status", None) == "completed")
        return completed / total

    def _recall_memory(
        self, memory_provider: Any, user_id: int, session_id: str, query: str
    ) -> List[Dict[str, Any]]:
        try:
            result = memory_provider.recall(user_id=user_id, session_id=session_id, query=query, limit=5)
            if hasattr(result, "__await__"):
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                    return []
                except RuntimeError:
                    return asyncio.run(result) or []
            return result or []
        except Exception:
            return []

    def _recall_cross_component_memory(
        self, memory_provider: Any, user_id: int, session_id: str, component_name: str, query: str
    ) -> List[Dict[str, Any]]:
        try:
            result = recall_cross_component(
                memory_provider=memory_provider,
                user_id=user_id,
                session_id=session_id,
                component_name=component_name,
                query=query,
                limit=5,
            )
            if hasattr(result, "__await__"):
                import asyncio
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
                if loop is not None and loop.is_running():
                    new_loop = asyncio.new_event_loop()
                    try:
                        return new_loop.run_until_complete(result) or []
                    finally:
                        new_loop.close()
                return asyncio.run(result) or []
            return result or []
        except Exception:
            return []
