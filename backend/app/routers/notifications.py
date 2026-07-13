from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
import sqlite3

from app.routers.auth import get_current_user, require_role
from app.schemas.notification import NotificationSend, NotificationResponse
from app.schemas.common import MessageResponse
from app.services.notification import send_email, EmailSendError
from app.core.database import get_db

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.post("/send", response_model=NotificationResponse)
def send_notification(
    data: NotificationSend,
    current_user: dict = Depends(require_role(["owner", "admin_staff"])),
):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT subject, body, is_active FROM notification_templates WHERE id = ?", (data.template_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Notification template not found")
    if not row["is_active"]:
        raise HTTPException(status_code=400, detail="Notification template is inactive")

    subject = row["subject"]
    body = row["body"]
    try:
        send_email(
            to=data.recipient,
            subject=subject,
            body=body,
            variables=data.variables,
        )
    except EmailSendError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {
        "id": 0,
        "template_id": data.template_id,
        "recipient": data.recipient,
        "status": "sent",
        "error": None,
        "sent_at": None,
    }
