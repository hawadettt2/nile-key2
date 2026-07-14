from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from app.routers.auth import get_current_user, require_role
from app.schemas.notification import NotificationSend, NotificationResponse
from app.schemas.common import MessageResponse
from app.services.notification import send_template_email, TemplateNotFoundError, TemplateInactiveError, EmailSendError

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


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
