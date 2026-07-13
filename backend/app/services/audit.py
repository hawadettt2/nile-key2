import json
import logging
from typing import Any, Optional

from app.services.base import connection, now_iso, dumps_json, build_list_query
from app.schemas.audit import AuditLogCreate

logger = logging.getLogger("audit")


def log_audit(
    current_user: dict,
    data: AuditLogCreate,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    session_id: Optional[str] = None,
) -> dict:
    user_id = current_user.get("id") if current_user else None
    created_at = now_iso()

    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO audit_logs 
               (user_id, action, entity_type, entity_id, details, created_at, ip_address, user_agent, session_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                data.action,
                data.entity_type,
                data.entity_id,
                data.details,
                created_at,
                ip_address,
                user_agent,
                session_id,
            ),
        )
        conn.commit()
        log_id = cursor.lastrowid

    logger.info("Audit log created: id=%s action=%s entity=%s:%s user=%s", log_id, data.action, data.entity_type, data.entity_id, user_id)
    return {"id": log_id, "message": "Audit log created successfully"}


def list_audit_logs(
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    action: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    filters = {}
    if user_id is not None:
        filters["user_id"] = user_id
    if entity_type is not None:
        filters["entity_type"] = entity_type
    if action is not None:
        filters["action"] = action

    with connection() as conn:
        cursor = conn.cursor()

        query = "SELECT * FROM audit_logs WHERE 1=1"
        params: list[Any] = []

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)
        if entity_type is not None:
            query += " AND entity_type = ?"
            params.append(entity_type)
        if action is not None:
            query += " AND action = ?"
            params.append(action)
        if date_from is not None:
            query += " AND created_at >= ?"
            params.append(date_from)
        if date_to is not None:
            query += " AND created_at <= ?"
            params.append(date_to)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])

        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
