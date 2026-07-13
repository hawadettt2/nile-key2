from unittest.mock import MagicMock, patch

import pytest

from app.services.notification import (
    _render_template,
    _load_template,
    send_email,
    send_template_email,
    EmailSendError,
    TemplateNotFoundError,
    TemplateInactiveError,
)


# ========== Helpers ==========


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


# ========== _render_template Tests ==========


def test_render_template_without_variables():
    assert _render_template("Hello World", None) == "Hello World"
    assert _render_template("Hello World", {}) == "Hello World"


def test_render_template_with_variables():
    body = "Hello {name}, your order {order_id} is ready."
    result = _render_template(body, {"name": "Alice", "order_id": "123"})
    assert result == "Hello Alice, your order 123 is ready."


def test_render_template_raises_on_missing_key():
    with pytest.raises(EmailSendError, match="Template variable substitution failed"):
        _render_template("Hello {name}, order {order_id}", {"name": "Alice"})


# ========== _load_template Tests ==========


def test_load_template_success():
    mock_row = {
        "id": 1,
        "subject": "Test Subject",
        "body": "Test Body",
        "is_active": 1,
    }
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.notification.get_db", return_value=mock_conn):
        result = _load_template(1)

    assert result["id"] == 1
    assert result["subject"] == "Test Subject"
    assert result["body"] == "Test Body"
    assert result["is_active"] == 1


def test_load_template_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.notification.get_db", return_value=mock_conn):
        with pytest.raises(TemplateNotFoundError, match="Notification template not found"):
            _load_template(999)


def test_load_template_inactive():
    mock_row = {
        "id": 1,
        "subject": "Test Subject",
        "body": "Test Body",
        "is_active": 0,
    }
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.notification.get_db", return_value=mock_conn):
        with pytest.raises(TemplateInactiveError, match="Notification template is inactive"):
            _load_template(1)


# ========== send_email Tests ==========


def test_send_email_raises_when_smtp_host_not_configured():
    with patch("app.services.notification.settings.SMTP_HOST", ""):
        with pytest.raises(EmailSendError, match="SMTP host is not configured"):
            send_email(to="test@example.com", subject="Test", body="Body")


def test_send_email_raises_when_smtp_from_not_configured():
    with patch("app.services.notification.settings.SMTP_HOST", "smtp.example.com"):
        with patch("app.services.notification.settings.SMTP_FROM", ""):
            with pytest.raises(EmailSendError, match="SMTP from address is not configured"):
                send_email(to="test@example.com", subject="Test", body="Body")


def test_send_email_uses_from_addr_override():
    with patch("app.services.notification.settings.SMTP_HOST", "smtp.example.com"):
        with patch("app.services.notification.settings.SMTP_FROM", "default@example.com"):
            with patch("app.services.notification.smtplib.SMTP") as mock_smtp_cls:
                mock_client = MagicMock()
                mock_client.__enter__ = MagicMock(return_value=mock_client)
                mock_client.__exit__ = MagicMock(return_value=False)
                mock_smtp_cls.return_value = mock_client

                send_email(to="test@example.com", subject="Test", body="Body", from_addr="override@example.com")

                mock_client.sendmail.assert_called_once()
                args = mock_client.sendmail.call_args[0]
                assert args[0] == "override@example.com"
                assert args[1] == ["test@example.com"]


def test_send_email_uses_default_from_addr():
    with patch("app.services.notification.settings.SMTP_HOST", "smtp.example.com"):
        with patch("app.services.notification.settings.SMTP_FROM", "default@example.com"):
            with patch("app.services.notification.settings.SMTP_USE_TLS", False):
                with patch("app.services.notification.settings.SMTP_USER", ""):
                    with patch("app.services.notification.smtplib.SMTP") as mock_smtp_cls:
                        mock_client = MagicMock()
                        mock_client.__enter__ = MagicMock(return_value=mock_client)
                        mock_client.__exit__ = MagicMock(return_value=False)
                        mock_smtp_cls.return_value = mock_client

                        send_email(to="test@example.com", subject="Test", body="Body")

                        mock_client.sendmail.assert_called_once()
                        args = mock_client.sendmail.call_args[0]
                        assert args[0] == "default@example.com"


def test_send_email_starts_tls_when_enabled():
    with patch("app.services.notification.settings.SMTP_HOST", "smtp.example.com"):
        with patch("app.services.notification.settings.SMTP_FROM", "from@example.com"):
            with patch("app.services.notification.settings.SMTP_USE_TLS", True):
                with patch("app.services.notification.settings.SMTP_USER", ""):
                    with patch("app.services.notification.smtplib.SMTP") as mock_smtp_cls:
                        mock_client = MagicMock()
                        mock_client.__enter__ = MagicMock(return_value=mock_client)
                        mock_client.__exit__ = MagicMock(return_value=False)
                        mock_smtp_cls.return_value = mock_client

                        send_email(to="test@example.com", subject="Test", body="Body")

                        mock_client.starttls.assert_called_once()


def test_send_email_logs_in_when_credentials_provided():
    with patch("app.services.notification.settings.SMTP_HOST", "smtp.example.com"):
        with patch("app.services.notification.settings.SMTP_FROM", "from@example.com"):
            with patch("app.services.notification.settings.SMTP_USE_TLS", False):
                with patch("app.services.notification.settings.SMTP_USER", "user"):
                    with patch("app.services.notification.settings.SMTP_PASSWORD", "pass"):
                        with patch("app.services.notification.smtplib.SMTP") as mock_smtp_cls:
                            mock_client = MagicMock()
                            mock_client.__enter__ = MagicMock(return_value=mock_client)
                            mock_client.__exit__ = MagicMock(return_value=False)
                            mock_smtp_cls.return_value = mock_client

                            send_email(to="test@example.com", subject="Test", body="Body")

                            mock_client.login.assert_called_once_with("user", "pass")


def test_send_email_raises_on_smtp_failure():
    with patch("app.services.notification.settings.SMTP_HOST", "smtp.example.com"):
        with patch("app.services.notification.settings.SMTP_FROM", "from@example.com"):
            with patch("app.services.notification.settings.SMTP_USE_TLS", False):
                with patch("app.services.notification.settings.SMTP_USER", ""):
                    with patch("app.services.notification.smtplib.SMTP") as mock_smtp_cls:
                        mock_client = MagicMock()
                        mock_client.__enter__ = MagicMock(return_value=mock_client)
                        mock_client.__exit__ = MagicMock(return_value=False)
                        mock_client.sendmail.side_effect = Exception("Connection refused")
                        mock_smtp_cls.return_value = mock_client

                        with pytest.raises(EmailSendError, match="Email delivery failed"):
                            send_email(to="test@example.com", subject="Test", body="Body")


# ========== send_template_email Tests ==========


def test_send_template_email_success():
    mock_row = {
        "id": 1,
        "subject": "Hello {name}",
        "body": "Hi {name}, welcome!",
        "is_active": 1,
    }
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.notification.get_db", return_value=mock_conn):
        with patch("app.services.notification.settings.SMTP_HOST", "smtp.example.com"):
            with patch("app.services.notification.settings.SMTP_FROM", "from@example.com"):
                with patch("app.services.notification.settings.SMTP_USE_TLS", False):
                    with patch("app.services.notification.settings.SMTP_USER", ""):
                        with patch("app.services.notification.smtplib.SMTP") as mock_smtp_cls:
                            mock_client = MagicMock()
                            mock_client.__enter__ = MagicMock(return_value=mock_client)
                            mock_client.__exit__ = MagicMock(return_value=False)
                            mock_smtp_cls.return_value = mock_client

                            result = send_template_email(
                                template_id=1,
                                recipient="user@example.com",
                                variables={"name": "Alice"},
                            )

    assert result["template_id"] == 1
    assert result["recipient"] == "user@example.com"
    assert result["status"] == "sent"
    assert result["error"] is None


def test_send_template_email_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.notification.get_db", return_value=mock_conn):
        with pytest.raises(TemplateNotFoundError, match="Notification template not found"):
            send_template_email(template_id=999, recipient="user@example.com")


def test_send_template_email_inactive():
    mock_row = {
        "id": 1,
        "subject": "Test",
        "body": "Body",
        "is_active": 0,
    }
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.notification.get_db", return_value=mock_conn):
        with pytest.raises(TemplateInactiveError, match="Notification template is inactive"):
            send_template_email(template_id=1, recipient="user@example.com")


def test_send_template_email_returns_failed_on_smtp_error():
    mock_row = {
        "id": 1,
        "subject": "Test",
        "body": "Body",
        "is_active": 1,
    }
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.notification.get_db", return_value=mock_conn):
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

                            result = send_template_email(
                                template_id=1,
                                recipient="user@example.com",
                            )

    assert result["status"] == "failed"
    assert result["error"] == "Email delivery failed"
