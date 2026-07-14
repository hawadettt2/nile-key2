from app.schemas.dashboard import DashboardStats, DashboardTimeline, DashboardResponse
from app.services.base import connection


def _count(table: str) -> int:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        row = cursor.fetchone()
        return row[0] if row else 0


def _recent_activities(limit: int = 10) -> list[dict]:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT action, entity_type, details, created_at
               FROM audit_logs
               ORDER BY created_at DESC
               LIMIT ?""",
            (limit,),
        )
        rows = cursor.fetchall()
        return [
            {
                "action": row["action"],
                "entity_type": row["entity_type"],
                "details": row["details"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]


def _upcoming_shipments(limit: int = 10) -> list[dict]:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, tracking_number, status, origin, destination, eta
               FROM shipments
               WHERE status IN ('pending', 'in_transit')
               ORDER BY created_at DESC
               LIMIT ?""",
            (limit,),
        )
        return [dict(r) for r in cursor.fetchall()]


def _pending_invoices(limit: int = 10) -> list[dict]:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, invoice_number, status, total, currency
               FROM invoices
               WHERE status IN ('draft', 'pending')
               ORDER BY created_at DESC
               LIMIT ?""",
            (limit,),
        )
        return [dict(r) for r in cursor.fetchall()]


def _notification_count() -> int:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM notification_logs")
        row = cursor.fetchone()
        return row[0] if row else 0


def get_dashboard() -> DashboardResponse:
    stats = DashboardStats(
        customers=_count("customers"),
        suppliers=_count("suppliers"),
        shipments=_count("shipments"),
        invoices=_count("invoices"),
        customs_declarations=_count("customs_declarations"),
        documents=_count("documents"),
        resources=_count("resources"),
        eta_connectors=_count("eta_connectors"),
    )

    timeline = DashboardTimeline(
        recent_activities=_recent_activities(),
        upcoming_shipments=_upcoming_shipments(),
        pending_invoices=_pending_invoices(),
    )

    return DashboardResponse(
        stats=stats,
        timeline=timeline,
        notifications_count=_notification_count(),
    )
