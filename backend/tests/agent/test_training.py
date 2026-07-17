import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone

from app.agent.training.service import TrainingService, TrainingMissionBuilder, TrainingIsolationContext
from app.agent.schemas.mission import Mission
from app.agent.schemas.enums import MissionStatus
from app.agent.exceptions import ExecutionEngineException


@pytest.fixture
def training_service():
    execution_engine = MagicMock()
    execution_engine.execute = AsyncMock()
    return TrainingService(execution_engine=execution_engine)


class TestTrainingMissionBuilder:
    """WP-30I Task 9.3: Training Mode as Structured Workflow."""

    def test_build_training_mission_creates_valid_mission(self):
        builder = TrainingMissionBuilder()
        mission = builder.build_training_mission(
            objective="Test training",
            tasks=[{"task_id": "task-1", "tool_name": "tool", "parameters": {}}],
        )

        assert isinstance(mission, Mission)
        assert mission.mission_type == "TRANSITION_WORKFLOW"
        assert mission.objective == "Test training"
        assert mission.status == MissionStatus.PENDING.value
        assert mission.context.get("mode") == "training"
        assert "training_session_id" in mission.context
        assert mission.execution_policy.get("is_training") is True
        assert mission.execution_policy.get("mode") == "training"

    def test_build_training_mission_sets_isolated_ids(self):
        builder = TrainingMissionBuilder()
        mission = builder.build_training_mission(
            objective="Test training",
            tasks=[],
        )

        assert mission.mission_id.startswith("training-mission-")
        assert mission.correlation_id.startswith("training-")
        assert mission.idempotency_key.startswith("training-")
        assert mission.context["training_session_id"].startswith("training-session-")

    def test_build_training_mission_with_custom_context(self):
        builder = TrainingMissionBuilder()
        mission = builder.build_training_mission(
            objective="Test training",
            tasks=[],
            context={"custom_key": "custom_value"},
        )

        assert mission.context["custom_key"] == "custom_value"
        assert mission.context["mode"] == "training"

    def test_build_training_mission_with_custom_requester(self):
        builder = TrainingMissionBuilder()
        requester = {"user_id": 42, "role": "trainer"}
        mission = builder.build_training_mission(
            objective="Test training",
            tasks=[],
            requester=requester,
        )

        assert mission.requester == requester


class TestTrainingIsolationContext:
    """WP-30I Task 9.3: Training data isolation."""

    def test_to_session_context_marks_training(self):
        isolation = TrainingIsolationContext(training_session_id="session-123")
        context = isolation.to_session_context()

        assert context["mode"] == "training"
        assert context["is_training"] is True
        assert context["training_session_id"] == "session-123"

    def test_to_session_context_preserves_base_context(self):
        isolation = TrainingIsolationContext(training_session_id="session-123")
        base_context = {"user_id": 10, "existing_key": "value"}
        context = isolation.to_session_context(base_context=base_context)

        assert context["user_id"] == 10
        assert context["existing_key"] == "value"
        assert context["mode"] == "training"

    def test_is_training_context_returns_true_for_training(self):
        isolation = TrainingIsolationContext(training_session_id="session-123")
        context = {"mode": "training", "user_id": 1}

        assert isolation.is_training_context(context) is True

    def test_is_training_context_returns_false_for_production(self):
        isolation = TrainingIsolationContext(training_session_id="session-123")
        context = {"mode": "production", "user_id": 1}

        assert isolation.is_training_context(context) is False

    def test_is_training_context_returns_true_when_is_training_flag_set(self):
        isolation = TrainingIsolationContext(training_session_id="session-123")
        context = {"is_training": True}

        assert isolation.is_training_context(context) is True


class TestTrainingService:
    """WP-30I Task 9.3: TrainingService integration."""

    @pytest.mark.asyncio
    async def test_execute_training_calls_execution_engine(self, training_service):
        mission = training_service.create_training_mission(
            objective="Test training",
            tasks=[{"task_id": "task-1", "tool_name": "tool", "parameters": {}}],
        )

        training_service.execution_engine.execute.return_value = {
            "execution_trace": [],
            "mission_status": MissionStatus.COMPLETED.value,
            "results": [],
            "failed_task_id": None,
        }

        result = await training_service.execute_training(mission)

        training_service.execution_engine.execute.assert_called_once()
        call_args = training_service.execution_engine.execute.call_args
        assert call_args[0][0] == mission
        assert call_args[1]["session_context"]["mode"] == "training"
        assert call_args[1]["session_context"]["is_training"] is True

    @pytest.mark.asyncio
    async def test_execute_training_returns_execution_result(self, training_service):
        mission = training_service.create_training_mission(
            objective="Test training",
            tasks=[],
        )
        expected_result = {
            "execution_trace": [],
            "mission_status": MissionStatus.COMPLETED.value,
            "results": [],
            "failed_task_id": None,
        }
        training_service.execution_engine.execute.return_value = expected_result

        result = await training_service.execute_training(mission)

        assert result == expected_result

    @pytest.mark.asyncio
    async def test_execute_training_raises_for_non_training_mission(self, training_service):
        mission = Mission(
            mission_id="prod-mission-1",
            mission_type="CREATE_SHIPMENT",
            objective="Production mission",
            priority=1,
            requester={"user_id": 1},
            context={"mode": "production"},
            constraints=[],
            approval_policy={},
            execution_policy={"is_training": False},
            created_at=datetime.now(timezone.utc),
            correlation_id="corr-1",
            idempotency_key="idem-1",
            audit_context={},
            payload={"tasks": []},
            status=MissionStatus.PENDING.value,
        )

        with pytest.raises(ExecutionEngineException) as exc_info:
            await training_service.execute_training(mission)

        assert "not configured for training mode" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_training_with_monitoring_service(self):
        mock_monitoring = MagicMock()
        mock_monitoring.get_metrics.return_value = []
        execution_engine = MagicMock()
        execution_engine.execute = AsyncMock(return_value={
            "execution_trace": [],
            "mission_status": MissionStatus.COMPLETED.value,
            "results": [],
            "failed_task_id": None,
        })

        service = TrainingService(
            execution_engine=execution_engine,
            monitoring_service=mock_monitoring,
        )
        mission = service.create_training_mission(
            objective="Test training",
            tasks=[],
        )

        result = await service.execute_training(mission)

        assert "training_metrics" in result
        assert result["training_metrics"] == []

    def test_create_training_mission_returns_mission_object(self, training_service):
        mission = training_service.create_training_mission(
            objective="Test training",
            tasks=[{"task_id": "task-1", "tool_name": "tool", "parameters": {}}],
        )

        assert isinstance(mission, Mission)
        assert mission.objective == "Test training"
        assert len(mission.payload.get("tasks", [])) == 1

    def test_training_mission_has_unique_ids(self, training_service):
        mission1 = training_service.create_training_mission(objective="Training 1", tasks=[])
        mission2 = training_service.create_training_mission(objective="Training 2", tasks=[])

        assert mission1.mission_id != mission2.mission_id
        assert mission1.context["training_session_id"] != mission2.context["training_session_id"]
