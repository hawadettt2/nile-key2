from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.routers.auth import get_current_user, require_role
from app.core.database import get_db
from app.schemas.notification import NotificationSend, NotificationResponse
from app.schemas.common import MessageResponse
from app.services.notification import send_template_email, TemplateNotFoundError, TemplateInactiveError, EmailSendError, credential_store as notification_credential_store

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get("/", response_model=list[dict])
def list_notifications(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, template_id, recipient, subject, status, sent_at FROM notification_logs ORDER BY sent_at DESC LIMIT ? OFFSET ?",
        (limit, skip),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


@router.post("/send", response_model=NotificationResponse)
def send_notification(
    data: NotificationSend,
    current_user: dict = Depends(require_role(["owner", "admin_staff"])),
):
    try:
        result = send_template_email(
            template_id=data.template_id,
            recipient=data.recipient,
            variables=data.variables,
            current_user=current_user,
            credential_store=notification_credential_store,
        )
    except TemplateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except TemplateInactiveError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except EmailSendError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "id": 0,
        "template_id": result["template_id"],
        "recipient": result["recipient"],
        "status": result["status"],
        "error": result.get("error"),
        "sent_at": None,
    }
