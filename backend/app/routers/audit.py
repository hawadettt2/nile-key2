from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional

from app.routers.auth import require_role
from app.schemas.audit import AuditLogResponse
from app.services.audit import list_audit_logs

router = APIRouter(tags=["Audit"])


@router.get("/api/v1/audit/logs", response_model=list[AuditLogResponse])
def get_audit_logs(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    action: Optional[str] = Query(None, description="Filter by action"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO format)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    current_user: dict = Depends(require_role(["owner", "manager", "admin_staff"])),
):
    try:
        return list_audit_logs(
            user_id=user_id,
            entity_type=entity_type,
            action=action,
            date_from=date_from,
            date_to=date_to,
            skip=skip,
            limit=limit,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch audit logs")
