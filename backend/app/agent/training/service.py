from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
import uuid

from ..schemas.mission import Mission
from ..schemas.task import Task
from ..schemas.enums import MissionStatus
from ..exceptions import ExecutionEngineException


class TrainingMissionBuilder:
    """Builds training missions with isolated context.

    Creates Mission objects configured for training execution,
    ensuring isolation from production sessions and data.
    """

    def __init__(self, tool_registry=None):
        self.tool_registry = tool_registry

    def build_training_mission(
        self,
        objective: str,
        tasks: List[Dict[str, Any]],
        requester: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        constraints: Optional[List[Dict[str, Any]]] = None,
        approval_policy: Optional[Dict[str, Any]] = None,
        execution_policy: Optional[Dict[str, Any]] = None,
    ) -> Mission:
        """Build a Mission object for training execution.

        Args:
            objective: Training objective description.
            tasks: List of task definitions for the training mission.
            requester: Optional requester information.
            context: Optional base context. Will be merged with training isolation context.
            constraints: Optional constraints list.
            approval_policy: Optional approval policy.
            execution_policy: Optional execution policy overrides.

        Returns:
            Mission object configured for training execution.
        """
        training_context = context or {}
        training_context.setdefault("mode", "training")
        training_context.setdefault("training_session_id", self._generate_training_session_id())

        if requester is None:
            requester = {"user_id": 0, "role": "training_system"}

        if constraints is None:
            constraints = []

        if approval_policy is None:
            approval_policy = {"require_approval": False}

        training_execution_policy = execution_policy or {}
        training_execution_policy.setdefault("mode", "training")
        training_execution_policy.setdefault("is_training", True)

        now = datetime.now(timezone.utc)
        return Mission(
            mission_id=self._generate_mission_id(),
            mission_type="TRANSITION_WORKFLOW",
            objective=objective,
            priority=1,
            requester=requester,
            context=training_context,
            constraints=constraints,
            approval_policy=approval_policy,
            execution_policy=training_execution_policy,
            created_at=now,
            correlation_id=self._generate_correlation_id(),
            idempotency_key=self._generate_idempotency_key(),
            audit_context={"source": "training", "training_session_id": training_context["training_session_id"]},
            payload={"tasks": tasks},
            status=MissionStatus.PENDING.value,
        )

    def _generate_mission_id(self) -> str:
        return f"training-mission-{uuid.uuid4().hex[:12]}"

    def _generate_training_session_id(self) -> str:
        return f"training-session-{uuid.uuid4().hex[:8]}"

    def _generate_correlation_id(self) -> str:
        return f"training-{uuid.uuid4().hex[:8]}"

    def _generate_idempotency_key(self) -> str:
        return f"training-{uuid.uuid4().hex}"


class TrainingIsolationContext:
    """Provides isolated context for training execution.

    Ensures training executions do not affect production data
    by providing isolated session and context identifiers.
    """

    def __init__(self, training_session_id: str):
        self.training_session_id = training_session_id

    def to_session_context(self, base_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create an isolated session context for training.

        Args:
            base_context: Optional base context to extend.

        Returns:
            Session context dict with training isolation markers.
        """
        context = base_context or {}
        context["mode"] = "training"
        context["training_session_id"] = self.training_session_id
        context["is_training"] = True
        context["user_id"] = context.get("user_id", 0)
        return context

    def is_training_context(self, context: Dict[str, Any]) -> bool:
        """Check if a context belongs to a training session.

        Args:
            context: Session context dict to check.

        Returns:
            True if the context is a training context.
        """
        return context.get("mode") == "training" or context.get("is_training") is True


class TrainingService:
    """Service for managing training mode execution.

    Provides isolated execution of training workflows using the
    existing ExecutionEngine, ensuring no side effects on production data.
    """

    def __init__(
        self,
        execution_engine,
        tool_registry=None,
        session_manager=None,
        audit_recorder=None,
        monitoring_service=None,
    ):
        self.execution_engine = execution_engine
        self.tool_registry = tool_registry
        self.session_manager = session_manager
        self.audit_recorder = audit_recorder
        self.monitoring_service = monitoring_service
        self.mission_builder = TrainingMissionBuilder(tool_registry=self.tool_registry)
        self.isolation_context = None

    def create_training_mission(
        self,
        objective: str,
        tasks: List[Dict[str, Any]],
        requester: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        constraints: Optional[List[Dict[str, Any]]] = None,
        approval_policy: Optional[Dict[str, Any]] = None,
        execution_policy: Optional[Dict[str, Any]] = None,
    ) -> Mission:
        """Create a training mission with isolated context.

        Args:
            objective: Training objective description.
            tasks: List of task definitions.
            requester: Optional requester information.
            context: Optional base context.
            constraints: Optional constraints.
            approval_policy: Optional approval policy.
            execution_policy: Optional execution policy overrides.

        Returns:
            Mission object configured for training execution.
        """
        mission = self.mission_builder.build_training_mission(
            objective=objective,
            tasks=tasks,
            requester=requester,
            context=context,
            constraints=constraints,
            approval_policy=approval_policy,
            execution_policy=execution_policy,
        )
        self.isolation_context = TrainingIsolationContext(
            training_session_id=mission.context.get("training_session_id", "")
        )
        return mission

    async def execute_training(self, mission: Mission) -> Dict[str, Any]:
        """Execute a training mission in isolation.

        Args:
            mission: Mission object created by create_training_mission.

        Returns:
            Execution result dict from ExecutionEngine.

        Raises:
            ExecutionEngineException: If the mission is not a training mission.
        """
        if not self._is_training_mission(mission):
            raise ExecutionEngineException("Mission is not configured for training mode")

        session_context = self.isolation_context.to_session_context(
            base_context=mission.context
        ) if self.isolation_context else mission.context

        result = await self.execution_engine.execute(mission, session_context=session_context)

        if self.monitoring_service:
            training_metrics = self.monitoring_service.get_metrics()
            result["training_metrics"] = [
                {
                    "metric_name": m.metric_name,
                    "value": m.value,
                    "timestamp": m.timestamp,
                    "tags": {**m.tags, "mode": "training"},
                }
                for m in training_metrics
            ]

        return result

    def _is_training_mission(self, mission: Mission) -> bool:
        """Check if a mission is configured for training mode.

        Args:
            mission: Mission to check.

        Returns:
            True if the mission is a training mission.
        """
        execution_policy = mission.execution_policy or {}
        context = mission.context or {}
        return execution_policy.get("is_training") is True or context.get("mode") == "training"
