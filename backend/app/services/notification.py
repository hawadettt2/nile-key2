import logging
import sqlite3
import smtplib
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger("notification")


class EmailSendError(Exception):
    """Raised when an email cannot be sent."""


class TemplateNotFoundError(Exception):
    """Raised when a notification template does not exist."""


class TemplateInactiveError(Exception):
    """Raised when a notification template is inactive."""


def _render_template(body: str, variables: Optional[dict[str, object]]) -> str:
    if not variables:
        return body
    try:
        return body.format_map({k: str(v) for k, v in variables.items()})
    except (KeyError, ValueError) as exc:
        raise EmailSendError("Template variable substitution failed") from exc


def _load_template(template_id: int) -> dict:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, subject, body, is_active FROM notification_templates WHERE id = ?",
        (template_id,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise TemplateNotFoundError("Notification template not found")
    if not row["is_active"]:
        raise TemplateInactiveError("Notification template is inactive")
    return dict(row)


def _is_notification_enabled(user_id: int, notification_type: str) -> bool:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT enabled FROM notification_preferences WHERE user_id = ? AND notification_type = ?",
            (user_id, notification_type),
        )
        row = cursor.fetchone()
        if row:
            return bool(row["enabled"])
        return True


def send_email(
    to: str,
    subject: str,
    body: str,
    *,
    variables: Optional[dict[str, object]] = None,
    from_addr: Optional[str] = None,
) -> None:
    if not settings.SMTP_HOST:
        raise EmailSendError("SMTP host is not configured")
    if not settings.SMTP_FROM and not from_addr:
        raise EmailSendError("SMTP from address is not configured")

    rendered_body = _render_template(body, variables)
    sender = from_addr or settings.SMTP_FROM
    msg = MIMEText(rendered_body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as client:
            if settings.SMTP_USE_TLS:
                client.starttls()
            if settings.SMTP_USER:
                client.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            client.sendmail(sender, [to], msg.as_string())
    except Exception as exc:
        logger.error("Failed to send email to %s", to)
        raise EmailSendError("Email delivery failed") from exc

    logger.info("Email sent to %s", to)


def send_template_email(
    template_id: int,
    recipient: str,
    variables: Optional[dict[str, object]] = None,
) -> dict:
    template = _load_template(template_id)
    try:
        send_email(
            to=recipient,
            subject=template["subject"],
            body=template["body"],
            variables=variables,
        )
    except EmailSendError as exc:
        return {
            "template_id": template_id,
            "recipient": recipient,
            "status": "failed",
            "error": str(exc),
        }

    return {
        "template_id": template_id,
        "recipient": recipient,
        "status": "sent",
        "error": None,
    }
