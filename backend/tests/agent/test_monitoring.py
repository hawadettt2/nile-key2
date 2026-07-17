import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from app.agent.monitoring.service import MonitoringService, MonitoringConfig, AlertSeverity, AlertStatus


@pytest.fixture
def monitoring_service():
    return MonitoringService()


class TestMonitoringServiceThresholds:
    """WP-30I Task 9.2: Proactive monitoring with alert thresholds."""

    def test_alert_created_when_error_rate_exceeds_threshold(self, monitoring_service):
        for i in range(5):
            monitoring_service.record_task_execution(
                mission_id="mission-1",
                task_id=f"task-{i}",
                tool_name="tool",
                execution_status="failed",
                execution_time_ms=100.0,
            )
        alerts = monitoring_service.get_alerts()
        assert len(alerts) > 0
        assert any("Error rate" in alert.message for alert in alerts)

    def test_no_alert_when_error_rate_below_threshold(self, monitoring_service):
        for i in range(5):
            monitoring_service.record_task_execution(
                mission_id="mission-1",
                task_id=f"task-{i}",
                tool_name="tool",
                execution_status="completed",
                execution_time_ms=100.0,
            )
        alerts = monitoring_service.get_alerts()
        assert len(alerts) == 0

    def test_alert_created_when_execution_time_exceeds_threshold(self, monitoring_service):
        config = MonitoringConfig(execution_time_threshold_ms=50.0)
        service = MonitoringService(config=config)
        service.record_task_execution(
            mission_id="mission-1",
            task_id="task-1",
            tool_name="tool",
            execution_status="completed",
            execution_time_ms=100.0,
        )
        alerts = service.get_alerts()
        assert len(alerts) > 0
        assert any("Average execution time" in alert.message for alert in alerts)

    def test_no_alert_when_execution_time_below_threshold(self, monitoring_service):
        config = MonitoringConfig(execution_time_threshold_ms=1000.0)
        service = MonitoringService(config=config)
        service.record_task_execution(
            mission_id="mission-1",
            task_id="task-1",
            tool_name="tool",
            execution_status="completed",
            execution_time_ms=50.0,
        )
        alerts = service.get_alerts()
        assert len(alerts) == 0

    def test_multiple_thresholds_triggered_simultaneously(self, monitoring_service):
        config = MonitoringConfig(
            error_rate_threshold=0.1,
            execution_time_threshold_ms=50.0,
        )
        service = MonitoringService(config=config)
        for i in range(5):
            service.record_task_execution(
                mission_id="mission-1",
                task_id=f"task-{i}",
                tool_name="tool",
                execution_status="failed",
                execution_time_ms=100.0,
            )
        alerts = service.get_alerts()
        assert len(alerts) >= 2

    def test_alert_cooldown_prevents_duplicate_alerts(self, monitoring_service):
        config = MonitoringConfig(alert_cooldown_seconds=60.0, error_rate_threshold=0.0)
        service = MonitoringService(config=config)
        service.record_task_execution(
            mission_id="mission-1",
            task_id="task-1",
            tool_name="tool",
            execution_status="failed",
            execution_time_ms=100.0,
        )
        alerts_first = service.get_alerts()
        service.record_task_execution(
            mission_id="mission-1",
            task_id="task-2",
            tool_name="tool",
            execution_status="failed",
            execution_time_ms=100.0,
        )
        alerts_second = service.get_alerts()
        assert len(alerts_first) == len(alerts_second)

    def test_boundary_case_error_rate_exactly_at_threshold(self, monitoring_service):
        config = MonitoringConfig(error_rate_threshold=0.5)
        service = MonitoringService(config=config)
        for i in range(4):
            service.record_task_execution(
                mission_id="mission-1",
                task_id=f"task-{i}",
                tool_name="tool",
                execution_status="completed",
                execution_time_ms=100.0,
            )
        service.record_task_execution(
            mission_id="mission-1",
            task_id="task-4",
            tool_name="tool",
            execution_status="failed",
            execution_time_ms=100.0,
        )
        alerts = service.get_alerts()
        assert len(alerts) == 0

    def test_boundary_case_error_rate_one_above_threshold(self, monitoring_service):
        config = MonitoringConfig(error_rate_threshold=0.5)
        service = MonitoringService(config=config)
        for i in range(2):
            service.record_task_execution(
                mission_id="mission-1",
                task_id=f"task-{i}",
                tool_name="tool",
                execution_status="completed",
                execution_time_ms=100.0,
            )
        for i in range(2, 5):
            service.record_task_execution(
                mission_id="mission-1",
                task_id=f"task-{i}",
                tool_name="tool",
                execution_status="failed",
                execution_time_ms=100.0,
            )
        alerts = service.get_alerts()
        assert len(alerts) > 0

    def test_pending_approval_alert_triggered(self, monitoring_service):
        config = MonitoringConfig(pending_approval_threshold=1)
        service = MonitoringService(config=config)
        service.record_task_execution(
            mission_id="mission-1",
            task_id="task-1",
            tool_name="tool",
            execution_status="pending_approval",
            execution_time_ms=0.0,
        )
        alerts = service.get_alerts()
        assert len(alerts) > 0
        assert any("Pending approvals" in alert.message for alert in alerts)

    def test_alert_acknowledge_and_resolve(self, monitoring_service):
        monitoring_service.record_task_execution(
            mission_id="mission-1",
            task_id="task-1",
            tool_name="tool",
            execution_status="failed",
            execution_time_ms=100.0,
        )
        alerts = monitoring_service.get_alerts()
        assert len(alerts) == 1
        alert_id = alerts[0].alert_id
        assert monitoring_service.acknowledge_alert(alert_id) is True
        assert monitoring_service.get_alerts(status=AlertStatus.ACKNOWLEDGED)[0].alert_id == alert_id
        assert monitoring_service.resolve_alert(alert_id) is True
        assert monitoring_service.get_alerts(status=AlertStatus.RESOLVED)[0].alert_id == alert_id

    def test_metrics_collection(self, monitoring_service):
        monitoring_service.record_task_execution(
            mission_id="mission-1",
            task_id="task-1",
            tool_name="tool",
            execution_status="completed",
            execution_time_ms=150.0,
        )
        metrics = monitoring_service.get_metrics()
        assert len(metrics) >= 2
        metric_names = {m.metric_name for m in metrics}
        assert "task.execution.count" in metric_names
        assert "task.execution.time_ms" in metric_names

    def test_mission_stats_tracking(self, monitoring_service):
        for i in range(3):
            monitoring_service.record_task_execution(
                mission_id="mission-1",
                task_id=f"task-{i}",
                tool_name="tool",
                execution_status="completed",
                execution_time_ms=100.0,
            )
        monitoring_service.record_mission_completed("mission-1", "completed")
        stats = monitoring_service.get_mission_stats("mission-1")
        assert stats is not None
        assert stats["total_tasks"] == 3
        assert stats["failed_tasks"] == 0

    def test_retry_rate_threshold(self, monitoring_service):
        config = MonitoringConfig(retry_rate_threshold=0.0)
        service = MonitoringService(config=config)
        service.record_task_execution(
            mission_id="mission-1",
            task_id="task-1",
            tool_name="tool",
            execution_status="completed",
            execution_time_ms=100.0,
            retry_count=1,
        )
        alerts = service.get_alerts()
        assert len(alerts) > 0
        assert any("Retry rate" in alert.message for alert in alerts)

    def test_failure_count_threshold(self, monitoring_service):
        config = MonitoringConfig(failure_count_threshold=2)
        service = MonitoringService(config=config)
        for i in range(3):
            service.record_task_execution(
                mission_id="mission-1",
                task_id=f"task-{i}",
                tool_name="tool",
                execution_status="failed",
                execution_time_ms=100.0,
            )
        alerts = service.get_alerts()
        assert len(alerts) > 0
        assert any("Failure count" in alert.message for alert in alerts)
