from datetime import datetime, timedelta

import pytest

from app.schemas.audit import AuditLogCreate
from app.services.audit import log_audit, list_audit_logs


# ========== Helpers ==========


def _make_user(user_id=1):
    return {"id": user_id}


def _make_audit_data(action="created", entity_type="customer", entity_id=1, details="Test details"):
    return AuditLogCreate(action=action, entity_type=entity_type, entity_id=entity_id, details=details)


# ========== log_audit Tests ==========


def test_log_audit_creates_record_with_user():
    from app.core.database import init_db, get_db_connection

    init_db()

    result = log_audit(
        current_user=_make_user(5),
        data=_make_audit_data(action="created", entity_type="invoice", entity_id=10, details="Created invoice"),
    )

    assert "id" in result
    assert result["message"] == "Audit log created successfully"

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs WHERE id = ?", (result["id"],))
        row = cursor.fetchone()
        assert row is not None
        assert row["user_id"] == 5
        assert row["action"] == "created"
        assert row["entity_type"] == "invoice"
        assert row["entity_id"] == 10
        assert row["details"] == "Created invoice"
        assert row["ip_address"] is None
        assert row["user_agent"] is None
        assert row["session_id"] is None


def test_log_audit_handles_current_user_none():
    from app.core.database import init_db, get_db_connection

    init_db()

    result = log_audit(
        current_user=None,
        data=_make_audit_data(action="system", entity_type="config", entity_id=None, details="System event"),
    )

    assert "id" in result

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs WHERE id = ?", (result["id"],))
        row = cursor.fetchone()
        assert row is not None
        assert row["user_id"] is None
        assert row["action"] == "system"
        assert row["entity_type"] == "config"


def test_log_audit_stores_optional_fields():
    from app.core.database import init_db, get_db_connection

    init_db()

    result = log_audit(
        current_user=_make_user(3),
        data=_make_audit_data(),
        ip_address="192.168.1.1",
        user_agent="Mozilla/5.0",
        session_id="sess-123",
    )

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs WHERE id = ?", (result["id"],))
        row = cursor.fetchone()
        assert row["ip_address"] == "192.168.1.1"
        assert row["user_agent"] == "Mozilla/5.0"
        assert row["session_id"] == "sess-123"


def test_log_audit_created_at_is_timestamp():
    from app.core.database import init_db, get_db_connection

    init_db()

    result = log_audit(
        current_user=_make_user(),
        data=_make_audit_data(),
    )

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT created_at FROM audit_logs WHERE id = ?", (result["id"],))
        row = cursor.fetchone()
        created_at = row["created_at"]
        assert isinstance(created_at, str)
        parsed = datetime.fromisoformat(created_at)
        assert datetime.utcnow() - parsed < timedelta(seconds=5)


# ========== list_audit_logs Tests ==========


def _seed_audit_logs():
    from app.core.database import init_db, get_db_connection

    init_db()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM audit_logs")
        conn.commit()

    now = datetime.utcnow()
    logs = [
        {"user_id": 1, "action": "created", "entity_type": "customer", "entity_id": 1, "details": "Created customer 1"},
        {"user_id": 1, "action": "updated", "entity_type": "customer", "entity_id": 1, "details": "Updated customer 1"},
        {"user_id": 2, "action": "created", "entity_type": "invoice", "entity_id": 10, "details": "Created invoice 10"},
        {"user_id": 2, "action": "deleted", "entity_type": "invoice", "entity_id": 10, "details": "Deleted invoice 10"},
        {"user_id": None, "action": "system", "entity_type": "config", "entity_id": None, "details": "System startup"},
    ]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        for log in logs:
            cursor.execute(
                """INSERT INTO audit_logs (user_id, action, entity_type, entity_id, details, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    log["user_id"],
                    log["action"],
                    log["entity_type"],
                    log["entity_id"],
                    log["details"],
                    datetime.utcnow().isoformat(),
                ),
            )
        conn.commit()


def test_list_audit_logs_returns_all_without_filters():
    _seed_audit_logs()
    result = list_audit_logs()
    assert len(result) == 5


def test_list_audit_logs_filters_by_user_id():
    _seed_audit_logs()
    result = list_audit_logs(user_id=1)
    assert len(result) == 2
    for row in result:
        assert row["user_id"] == 1


def test_list_audit_logs_filters_by_entity_type():
    _seed_audit_logs()
    result = list_audit_logs(entity_type="invoice")
    assert len(result) == 2
    for row in result:
        assert row["entity_type"] == "invoice"


def test_list_audit_logs_filters_by_action():
    _seed_audit_logs()
    result = list_audit_logs(action="created")
    assert len(result) == 2
    for row in result:
        assert row["action"] == "created"


def test_list_audit_logs_filters_by_date_range():
    _seed_audit_logs()
    now = datetime.utcnow()
    date_from = (now - timedelta(hours=1)).isoformat()
    date_to = (now + timedelta(hours=1)).isoformat()
    result = list_audit_logs(date_from=date_from, date_to=date_to)
    assert len(result) == 5


def test_list_audit_logs_pagination_skip():
    _seed_audit_logs()
    result = list_audit_logs(skip=2, limit=100)
    assert len(result) == 3


def test_list_audit_logs_pagination_limit():
    _seed_audit_logs()
    result = list_audit_logs(skip=0, limit=2)
    assert len(result) == 2


def test_list_audit_logs_combined_filters():
    _seed_audit_logs()
    result = list_audit_logs(user_id=1, action="created")
    assert len(result) == 1
    assert result[0]["user_id"] == 1
    assert result[0]["action"] == "created"
    assert result[0]["entity_type"] == "customer"


def test_list_audit_logs_empty_result():
    _seed_audit_logs()
    result = list_audit_logs(user_id=999)
    assert result == []


def test_list_audit_logs_returns_list_of_dicts():
    _seed_audit_logs()
    result = list_audit_logs()
    assert isinstance(result, list)
    assert all(isinstance(row, dict) for row in result)
    expected_keys = {"id", "user_id", "action", "entity_type", "entity_id", "details", "created_at", "ip_address", "user_agent", "session_id"}
    for row in result:
        assert expected_keys.issubset(row.keys())
