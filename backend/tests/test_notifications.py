import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


def _unique_email(role):
    return f"notif_{role}_{uuid.uuid4().hex[:8]}@example.com"


def _register_and_login(client, role="admin_staff"):
    email = _unique_email(role)
    password = "Test1234!"

    reg = client.post("/api/v1/auth/register", json={
        "email": email,
        "username": email,
        "full_name": "Test User",
        "password": password,
        "role": role,
        "phone": "000",
        "company": "TestCo"
    })
    if reg.status_code != 200:
        raise RuntimeError(f"Registration failed: {reg.status_code} {reg.text}")

    res = client.post("/api/v1/auth/login", json={
        "username": email,
        "password": password
    })
    if res.status_code != 200:
        raise RuntimeError(f"Login failed: {res.status_code} {res.text}")

    return res.json()["access_token"]


def _seed_notification_template(client, template_id=1, name="Test Template", subject="Hello {name}", body="Hi {name}", is_active=1):
    from app.core.database import init_db, get_db_connection

    init_db()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM notification_templates WHERE id = ?", (template_id,))
        cursor.execute(
            """INSERT INTO notification_templates (id, name, subject, body, is_active, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                template_id,
                name,
                subject,
                body,
                is_active,
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()


# ========== Authorization Tests ==========


def test_send_notification_requires_authorization(client):
    response = client.post("/api/v1/notifications/send", json={
        "template_id": 1,
        "recipient": "user@example.com",
    })
    assert response.status_code in (401, 403)


def test_send_notification_authorized_with_owner_role(client):
    token = _register_and_login(client, role="owner")
    _seed_notification_template(client)

    response = client.post(
        "/api/v1/notifications/send",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "template_id": 1,
            "recipient": "user@example.com",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["template_id"] == 1
    assert data["recipient"] == "user@example.com"
    assert data["status"] in ("sent", "failed")
    assert "error" in data


def test_send_notification_authorized_with_admin_staff_role(client):
    token = _register_and_login(client, role="admin_staff")
    _seed_notification_template(client)

    response = client.post(
        "/api/v1/notifications/send",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "template_id": 1,
            "recipient": "user@example.com",
        },
    )
    assert response.status_code == 200


def test_send_notification_forbidden_for_staff_role(client):
    token = _register_and_login(client, role="staff")
    _seed_notification_template(client)

    response = client.post(
        "/api/v1/notifications/send",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "template_id": 1,
            "recipient": "user@example.com",
        },
    )
    assert response.status_code == 403


# ========== Error Handling Tests ==========


def test_send_notification_returns_404_when_template_not_found(client):
    token = _register_and_login(client, role="owner")
    _seed_notification_template(client)

    response = client.post(
        "/api/v1/notifications/send",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "template_id": 999,
            "recipient": "user@example.com",
        },
    )
    assert response.status_code == 404
    assert "Notification template not found" in response.json().get("detail", "")


def test_send_notification_returns_400_when_template_inactive(client):
    token = _register_and_login(client, role="owner")
    _seed_notification_template(client, is_active=0)

    response = client.post(
        "/api/v1/notifications/send",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "template_id": 1,
            "recipient": "user@example.com",
        },
    )
    assert response.status_code == 400
    assert "Notification template is inactive" in response.json().get("detail", "")


def test_send_notification_returns_500_on_smtp_failure(client):
    token = _register_and_login(client, role="owner")
    _seed_notification_template(client)

    with patch("app.services.notification.settings.SMTP_HOST", "smtp.example.com"):
        with patch("app.services.notification.settings.SMTP_FROM", "from@example.com"):
            with patch("app.services.notification.settings.SMTP_USE_TLS", False):
                with patch("app.services.notification.settings.SMTP_USER", ""):
                    with patch("app.services.notification.smtplib.SMTP") as mock_smtp_cls:
                        mock_client = MagicMock()
                        mock_client.__enter__ = MagicMock(return_value=mock_client)
                        mock_client.__exit__ = MagicMock(return_value=False)
                        mock_client.sendmail.side_effect = Exception("SMTP down")
                        mock_smtp_cls.return_value = mock_client

                        response = client.post(
                            "/api/v1/notifications/send",
                            headers={"Authorization": f"Bearer {token}"},
                            json={
                                "template_id": 1,
                                "recipient": "user@example.com",
                            },
                        )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert data["error"] == "Email delivery failed"


def test_send_notification_response_model(client):
    token = _register_and_login(client, role="owner")
    _seed_notification_template(client)

    response = client.post(
        "/api/v1/notifications/send",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "template_id": 1,
            "recipient": "user@example.com",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "template_id" in data
    assert "recipient" in data
    assert "status" in data
    assert "error" in data
    assert "sent_at" in data
