from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AlertSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class Alert:
    alert_id: str
    severity: AlertSeverity
    status: AlertStatus
    message: str
    metric_name: str
    current_value: float
    threshold: float
    created_at: str
    acknowledged_at: Optional[str] = None
    resolved_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricSample:
    metric_name: str
    value: float
    timestamp: str
    tags: Dict[str, str] = field(default_factory=dict)


class MonitoringConfig:
    def __init__(
        self,
        error_rate_threshold: float = 0.1,
        execution_time_threshold_ms: float = 5000.0,
        failure_count_threshold: int = 3,
        pending_approval_threshold: int = 1,
        retry_rate_threshold: float = 0.2,
        alert_cooldown_seconds: float = 60.0,
    ):
        self.error_rate_threshold = error_rate_threshold
        self.execution_time_threshold_ms = execution_time_threshold_ms
        self.failure_count_threshold = failure_count_threshold
        self.pending_approval_threshold = pending_approval_threshold
        self.retry_rate_threshold = retry_rate_threshold
        self.alert_cooldown_seconds = alert_cooldown_seconds


class MonitoringService:
    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self._metrics: List[MetricSample] = []
        self._alerts: List[Alert] = []
        self._alert_cooldowns: Dict[str, datetime] = {}
        self._mission_stats: Dict[str, Dict[str, Any]] = {}
        self._pending_approvals: List[Dict[str, Any]] = []

    def record_task_execution(
        self,
        mission_id: str,
        task_id: str,
        tool_name: str,
        execution_status: str,
        execution_time_ms: float,
        retry_count: int = 0,
        error: Optional[str] = None,
    ) -> None:
        metric_samples = [
            MetricSample(
                metric_name="task.execution.count",
                value=1.0,
                timestamp=datetime.now(timezone.utc).isoformat(),
                tags={"mission_id": mission_id, "tool_name": tool_name, "status": execution_status},
            ),
            MetricSample(
                metric_name="task.execution.time_ms",
                value=execution_time_ms,
                timestamp=datetime.now(timezone.utc).isoformat(),
                tags={"mission_id": mission_id, "tool_name": tool_name},
            ),
            MetricSample(
                metric_name="task.retry.count",
                value=float(retry_count),
                timestamp=datetime.now(timezone.utc).isoformat(),
                tags={"mission_id": mission_id, "tool_name": tool_name},
            ),
        ]

        if execution_status == "failed" or execution_status == "skipped":
            metric_samples.append(
                MetricSample(
                    metric_name="task.error.count",
                    value=1.0,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    tags={"mission_id": mission_id, "tool_name": tool_name, "error": error or "unknown"},
                )
            )

        self._metrics.extend(metric_samples)
        self._update_mission_stats(mission_id, execution_status, execution_time_ms, retry_count, error)

        if execution_status == "pending_approval":
            self._pending_approvals.append({
                "mission_id": mission_id,
                "task_id": task_id,
                "tool_name": tool_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })

        self._evaluate_thresholds(mission_id)

    def record_mission_completed(self, mission_id: str, mission_status: str) -> None:
        stats = self._mission_stats.get(mission_id, {})
        total_tasks = stats.get("total_tasks", 0)
        failed_tasks = stats.get("failed_tasks", 0)
        error_rate = failed_tasks / total_tasks if total_tasks > 0 else 0.0

        self._metrics.append(
            MetricSample(
                metric_name="mission.error_rate",
                value=error_rate,
                timestamp=datetime.now(timezone.utc).isoformat(),
                tags={"mission_id": mission_id, "mission_status": mission_status},
            )
        )

        if mission_id in self._mission_stats:
            self._mission_stats[mission_id]["mission_status"] = mission_status
            self._mission_stats[mission_id]["completed_at"] = datetime.now(timezone.utc).isoformat()

    def _update_mission_stats(
        self,
        mission_id: str,
        execution_status: str,
        execution_time_ms: float,
        retry_count: int,
        error: Optional[str],
    ) -> None:
        if mission_id not in self._mission_stats:
            self._mission_stats[mission_id] = {
                "total_tasks": 0,
                "failed_tasks": 0,
                "total_retries": 0,
                "total_execution_time_ms": 0.0,
                "errors": [],
                "started_at": datetime.now(timezone.utc).isoformat(),
            }

        stats = self._mission_stats[mission_id]
        stats["total_tasks"] += 1
        stats["total_execution_time_ms"] += execution_time_ms
        stats["total_retries"] += retry_count

        if execution_status in ("failed", "skipped"):
            stats["failed_tasks"] += 1
            if error:
                stats["errors"].append(error)

    def _evaluate_thresholds(self, mission_id: str) -> None:
        stats = self._mission_stats.get(mission_id)
        if not stats:
            return

        total_tasks = stats.get("total_tasks", 0)
        failed_tasks = stats.get("failed_tasks", 0)
        total_retries = stats.get("total_retries", 0)
        total_execution_time_ms = stats.get("total_execution_time_ms", 0.0)

        if total_tasks > 0:
            error_rate = failed_tasks / total_tasks
            self._check_threshold(
                metric_name="mission.error_rate",
                current_value=error_rate,
                threshold=self.config.error_rate_threshold,
                mission_id=mission_id,
                severity=AlertSeverity.WARNING,
                message=f"Error rate {error_rate:.2%} exceeds threshold {self.config.error_rate_threshold:.2%}",
            )

        avg_execution_time = total_execution_time_ms / total_tasks if total_tasks > 0 else 0.0
        self._check_threshold(
            metric_name="task.avg_execution_time_ms",
            current_value=avg_execution_time,
            threshold=self.config.execution_time_threshold_ms,
            mission_id=mission_id,
            severity=AlertSeverity.WARNING,
            message=f"Average execution time {avg_execution_time:.2f}ms exceeds threshold {self.config.execution_time_threshold_ms:.2f}ms",
        )

        if total_tasks > 0:
            retry_rate = total_retries / total_tasks
            self._check_threshold(
                metric_name="task.retry_rate",
                current_value=retry_rate,
                threshold=self.config.retry_rate_threshold,
                mission_id=mission_id,
                severity=AlertSeverity.INFO,
                message=f"Retry rate {retry_rate:.2%} exceeds threshold {self.config.retry_rate_threshold:.2%}",
            )

        if failed_tasks >= self.config.failure_count_threshold:
            self._check_threshold(
                metric_name="task.failure_count",
                current_value=float(failed_tasks),
                threshold=float(self.config.failure_count_threshold),
                mission_id=mission_id,
                severity=AlertSeverity.CRITICAL,
                message=f"Failure count {failed_tasks} exceeds threshold {self.config.failure_count_threshold}",
            )

        pending_count = len(self._pending_approvals)
        if pending_count >= self.config.pending_approval_threshold:
            self._check_threshold(
                metric_name="approval.pending_count",
                current_value=float(pending_count),
                threshold=float(self.config.pending_approval_threshold),
                mission_id=mission_id,
                severity=AlertSeverity.WARNING,
                message=f"Pending approvals {pending_count} exceed threshold {self.config.pending_approval_threshold}",
            )

    def _check_threshold(
        self,
        metric_name: str,
        current_value: float,
        threshold: float,
        mission_id: str,
        severity: AlertSeverity,
        message: str,
    ) -> None:
        if current_value < threshold:
            return

        cooldown_key = f"{metric_name}:{mission_id}"
        now = datetime.now(timezone.utc)
        last_alert = self._alert_cooldowns.get(cooldown_key)
        if last_alert and (now - last_alert).total_seconds() < self.config.alert_cooldown_seconds:
            return

        alert = Alert(
            alert_id=f"{metric_name}:{mission_id}:{now.timestamp()}",
            severity=severity,
            status=AlertStatus.OPEN,
            message=message,
            metric_name=metric_name,
            current_value=current_value,
            threshold=threshold,
            created_at=now.isoformat(),
            metadata={"mission_id": mission_id},
        )
        self._alerts.append(alert)
        self._alert_cooldowns[cooldown_key] = now

    def get_alerts(self, status: Optional[str] = None, severity: Optional[str] = None) -> List[Alert]:
        result = self._alerts
        if status is not None:
            result = [a for a in result if a.status == status]
        if severity is not None:
            result = [a for a in result if a.severity == severity]
        return result

    def get_metrics(self, metric_name: Optional[str] = None) -> List[MetricSample]:
        if metric_name is None:
            return list(self._metrics)
        return [m for m in self._metrics if m.metric_name == metric_name]

    def get_mission_stats(self, mission_id: str) -> Optional[Dict[str, Any]]:
        return self._mission_stats.get(mission_id)

    def acknowledge_alert(self, alert_id: str) -> bool:
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.status = AlertStatus.ACKNOWLEDGED
                alert.acknowledged_at = datetime.now(timezone.utc).isoformat()
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.status = AlertStatus.RESOLVED
                alert.resolved_at = datetime.now(timezone.utc).isoformat()
                return True
        return False

    def reset(self) -> None:
        self._metrics.clear()
        self._alerts.clear()
        self._alert_cooldowns.clear()
        self._mission_stats.clear()
        self._pending_approvals.clear()
