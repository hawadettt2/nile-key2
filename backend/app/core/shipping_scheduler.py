"""
Shipping Scheduler
Background jobs for Shipping Engine operations using APScheduler.
"""

import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger("shipping")

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> Optional[AsyncIOScheduler]:
    """Get the global shipping scheduler instance."""
    return _scheduler


def init_scheduler() -> AsyncIOScheduler:
    """Initialize and configure the shipping scheduler."""
    global _scheduler

    _scheduler = AsyncIOScheduler(
        job_defaults={
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": 300,
        }
    )

    _scheduler.add_job(
        _poll_tracking_job,
        "interval",
        hours=24,
        id="shipping_tracking_poll",
        name="Shipping Tracking Poll",
        replace_existing=True,
    )

    logger.info("Shipping scheduler initialized with %d jobs", len(_scheduler.get_jobs()))
    return _scheduler


def start_scheduler() -> None:
    """Start the scheduler if not already running."""
    if _scheduler and not _scheduler.running:
        _scheduler.start()
        logger.info("Shipping scheduler started")


def shutdown_scheduler() -> None:
    """Shutdown the scheduler gracefully."""
    global _scheduler

    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=True)
        logger.info("Shipping scheduler stopped")
        _scheduler = None


def _poll_tracking_job() -> None:
    """Background job: poll booked shipments for tracking updates."""
    try:
        from app.services.shipping import track_shipment
        from app.core.database import get_db_connection

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, tracking_number, provider_shipment_id, service_provider
                   FROM shipments
                   WHERE (status = 'booked' OR tracking_status = 'booked')
                     AND provider_shipment_id IS NOT NULL
                   LIMIT 100"""
            )
            rows = cursor.fetchall()

        for row in rows:
            shipment = dict(row)
            try:
                track_shipment(shipment["tracking_number"] or str(shipment["id"]))
                logger.info("Tracking updated for shipment %s", shipment["id"])
            except Exception as exc:
                logger.error("Tracking poll failed for shipment %s: %s", shipment["id"], exc)
    except Exception as exc:
        logger.error("Shipping tracking poll failed: %s", exc, exc_info=True)
