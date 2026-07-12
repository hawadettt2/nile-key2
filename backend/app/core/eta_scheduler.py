"""
ETA Scheduler
Background jobs for ETA operations using APScheduler.
"""

import logging
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler

logger = logging.getLogger("eta")

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> Optional[AsyncIOScheduler]:
    """Get the global scheduler instance."""
    return _scheduler


def init_scheduler() -> AsyncIOScheduler:
    """Initialize and configure the ETA scheduler."""
    global _scheduler
    
    _scheduler = AsyncIOScheduler(
        job_defaults={
            "coalesce": True,
            "max_instances": 1,
            "misfire_grace_time": 300,  # 5 minutes grace period
        }
    )
    
    # Schedule ETA status polling every hour
    _scheduler.add_job(
        _poll_eta_statuses_job,
        "interval",
        hours=1,
        id="eta_status_polling",
        name="ETA Status Polling",
        replace_existing=True,
    )
    
    # Schedule batch submission every hour (at minute 5 to avoid collision with polling)
    _scheduler.add_job(
        _batch_submit_job,
        "interval",
        hours=1,
        id="eta_batch_submit",
        name="ETA Batch Submit",
        replace_existing=True,
        misfire_grace_time=600,
    )
    
    logger.info("ETA scheduler initialized with %d jobs", len(_scheduler.get_jobs()))
    return _scheduler


def start_scheduler() -> None:
    """Start the scheduler if not already running."""
    if _scheduler and not _scheduler.running:
        _scheduler.start()
        logger.info("ETA scheduler started")


def shutdown_scheduler() -> None:
    """Shutdown the scheduler gracefully."""
    global _scheduler
    
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=True)
        logger.info("ETA scheduler stopped")
        _scheduler = None


def _poll_eta_statuses_job() -> None:
    """Background job: poll pending ETA invoice statuses."""
    try:
        from app.services.eta import poll_pending_invoice_statuses
        
        # Poll with default connector
        result = poll_pending_invoice_statuses(limit=100)
        logger.info("ETA status polling completed: %s", result.get("message", "no result"))
    except Exception as exc:
        logger.error("ETA status polling failed: %s", exc, exc_info=True)


def _batch_submit_job() -> None:
    """Background job: submit pending invoices in batch mode."""
    try:
        from app.services.eta import submit_pending_batch, list_connectors
        
        # Get default connector
        connectors = list_connectors(status="active")
        if not connectors:
            logger.warning("No active ETA connectors found for batch submit")
            return
        
        # Use first active connector (or default)
        connector = next((c for c in connectors if c.get("is_default")), connectors[0])
        result = submit_pending_batch(connector_id=connector["id"])
        logger.info("ETA batch submit completed: %s", result.get("message", "no result"))
    except Exception as exc:
        logger.error("ETA batch submit failed: %s", exc, exc_info=True)
