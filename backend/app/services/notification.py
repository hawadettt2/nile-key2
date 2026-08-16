import json
import logging
import sqlite3
import smtplib
from email.mime.text import MIMEText
from typing import Optional

from app.core.config import settings
from app.core.credentials.credential_store import CredentialStore
from app.core.credentials.username_password_credential import UsernamePasswordCredential
from app.core.database import get_db
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate

logger = logging.getLogger("notification")

credential_store = CredentialStore()


def _get_smtp_credentials(credential_store: Optional[CredentialStore]):
    if credential_store is not None:
        credential = credential_store.get("smtp_credentials")
        if credential is not None:
            return credential.get_username(), credential.get_password()
    return None, None


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


def _log_notification(
    template_id: int,
    recipient: str,
    subject: str,
    body: str,
    status: str,
    error: Optional[str],
    current_user: Optional[dict],
) -> None:
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO notification_logs (template_id, recipient, subject, body, status, error)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (template_id, recipient, subject, body, status, error),
        )
        conn.commit()

    if current_user:
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(
                action="send",
                entity_type="notification",
                entity_id=template_id,
                details=f"{status}: {recipient}",
            ),
        )


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
    credential_store: Optional[CredentialStore] = None,
) -> None:
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_use_tls = settings.SMTP_USE_TLS
    smtp_from = settings.SMTP_FROM
    smtp_user = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD

    active_store = credential_store if credential_store is not None else globals().get("credential_store")
    if active_store is not None:
        cred_user, cred_password = _get_smtp_credentials(active_store)
        if cred_user is not None and cred_password is not None:
            smtp_user = cred_user
            smtp_password = cred_password

    if not smtp_host:
        raise EmailSendError("SMTP host is not configured")
    if not smtp_from and not from_addr:
        raise EmailSendError("SMTP from address is not configured")

    rendered_body = _render_template(body, variables)
    sender = from_addr or smtp_from
    msg = MIMEText(rendered_body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as client:
            if smtp_use_tls:
                client.starttls()
            if smtp_user:
                client.login(smtp_user, smtp_password)
            client.sendmail(sender, [to], msg.as_string())
    except Exception as exc:
        logger.error("Failed to send email to %s", to)
        raise EmailSendError("Email delivery failed") from exc

    logger.info("Email sent to %s", to)


def send_template_email(
    template_id: int,
    recipient: str,
    variables: Optional[dict[str, object]] = None,
    current_user: Optional[dict] = None,
    credential_store: Optional[CredentialStore] = None,
) -> dict:
    template = _load_template(template_id)
    try:
        send_email(
            to=recipient,
            subject=template["subject"],
            body=template["body"],
            variables=variables,
            credential_store=credential_store,
        )
    except EmailSendError as exc:
        _log_notification(
            template_id=template_id,
            recipient=recipient,
            subject=template["subject"],
            body=template["body"],
            status="failed",
            error=str(exc),
            current_user=current_user,
        )
        return {
            "template_id": template_id,
            "recipient": recipient,
            "status": "failed",
            "error": str(exc),
        }

    _log_notification(
        template_id=template_id,
        recipient=recipient,
        subject=template["subject"],
        body=template["body"],
        status="sent",
        error=None,
        current_user=current_user,
    )

    return {
        "template_id": template_id,
        "recipient": recipient,
        "status": "sent",
        "error": None,
    }
