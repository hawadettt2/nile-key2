from unittest.mock import patch, MagicMock

import pytest

from app.services.eta import (
    submit_invoice_to_eta,
    submit_receipt_to_eta,
    _send_eta_notification,
)
from app.services.eta.eta_client import ETAHttpError
from app.services.notification import TemplateNotFoundError


# ========== _send_eta_notification Edge Cases ==========


def test_send_eta_notification_skips_when_user_id_none():
    with patch("app.services.eta.send_template_email") as mock_send:
        _send_eta_notification(template_id=1, user_id=None)
        mock_send.assert_not_called()


def test_send_eta_notification_skips_when_preference_disabled():
    with patch("app.services.eta.send_template_email") as mock_send:
        with patch("app.services.eta._is_notification_enabled", return_value=False):
            _send_eta_notification(template_id=1, user_id=1)
        mock_send.assert_not_called()


def test_send_eta_notification_skips_when_no_email():
    with patch("app.services.eta.send_template_email") as mock_send:
        with patch("app.services.eta._is_notification_enabled", return_value=True):
            with patch("app.services.eta._get_user_email", return_value=None):
                _send_eta_notification(template_id=1, user_id=1)
        mock_send.assert_not_called()


def test_send_eta_notification_calls_send_template_email_when_enabled():
    with patch("app.services.eta.send_template_email") as mock_send:
        with patch("app.services.eta._is_notification_enabled", return_value=True):
            with patch("app.services.eta._get_user_email", return_value="test@example.com"):
                _send_eta_notification(
                    template_id=1,
                    user_id=1,
                    variables={"invoice_id": 123, "submission_id": "SUB-1"},
                )
        mock_send.assert_called_once_with(
            template_id=1,
            recipient="test@example.com",
            variables={"invoice_id": 123, "submission_id": "SUB-1"},
        )


# ========== submit_invoice_to_eta Notification Trigger ==========


@patch("app.services.eta.send_template_email")
@patch("app.services.eta.log_audit")
@patch("app.services.eta.create_eta_log")
@patch("app.services.eta.ETAClient")
@patch("app.services.eta._get_default_connector")
@patch("app.services.eta.check_invoice_idempotency")
@patch("app.services.eta.get_db_connection")
def test_submit_invoice_sends_notification_on_success(
    mock_get_db,
    mock_idempotency,
    mock_connector,
    mock_client_cls,
    mock_create_log,
    mock_log_audit,
    mock_send_template,
):
    mock_idempotency.return_value = None
    mock_connector.return_value = {
        "id": 1,
        "client_id": "test",
        "client_secret": "secret",
        "environment": "Pre-Production",
    }

    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        {"id": 1, "client_id": "test", "client_secret": "secret", "environment": "Pre-Production"},
        {"id": 1, "eta_status": "", "eta_uuid": None, "invoice_number": "INV-1"},
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_get_db.return_value = mock_conn

    mock_client = MagicMock()
    mock_client.submit_invoices.return_value = {
        "documents": [{"uuid": "UUID-123"}],
        "submissionId": "SUB-123",
    }
    mock_client_cls.return_value = mock_client
    mock_client.close = MagicMock()

    mock_create_log.return_value = {"id": 1}

    with patch("app.services.eta._is_notification_enabled", return_value=True):
        with patch("app.services.eta._get_user_email", return_value="test@example.com"):
            result = submit_invoice_to_eta(invoice_id=1, connector_id=1, current_user={"id": 1})

    mock_send_template.assert_called_once()
    assert mock_send_template.call_args[1]["template_id"] == 1
    assert mock_send_template.call_args[1]["recipient"] == "test@example.com"
    assert "invoice_id" in mock_send_template.call_args[1]["variables"]
    assert result["uuid"] == "UUID-123"


@patch("app.services.eta.send_template_email")
@patch("app.services.eta.log_audit")
@patch("app.services.eta.create_eta_log")
@patch("app.services.eta.ETAClient")
@patch("app.services.eta._get_default_connector")
@patch("app.services.eta.check_invoice_idempotency")
@patch("app.services.eta.get_db_connection")
def test_submit_invoice_does_not_send_notification_on_failure(
    mock_get_db,
    mock_idempotency,
    mock_connector,
    mock_client_cls,
    mock_create_log,
    mock_log_audit,
    mock_send_template,
):
    mock_idempotency.return_value = None
    mock_connector.return_value = {
        "id": 1,
        "client_id": "test",
        "client_secret": "secret",
        "environment": "Pre-Production",
    }

    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        {"id": 1, "client_id": "test", "client_secret": "secret", "environment": "Pre-Production"},
        {"id": 1, "eta_status": "", "eta_uuid": None, "invoice_number": "INV-1"},
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_get_db.return_value = mock_conn

    mock_client = MagicMock()
    mock_client.submit_invoices.side_effect = ETAHttpError(
        status_code=400, message="Bad Request", details=[]
    )
    mock_client_cls.return_value = mock_client
    mock_client.close = MagicMock()

    with pytest.raises(ValueError):
        submit_invoice_to_eta(invoice_id=1, connector_id=1, current_user={"id": 1})

    mock_send_template.assert_not_called()


# ========== submit_receipt_to_eta Notification Trigger ==========


@patch("app.services.eta.send_template_email")
@patch("app.services.eta.log_audit")
@patch("app.services.eta.create_eta_log")
@patch("app.services.eta.ETAClient")
@patch("app.services.eta._get_default_connector")
@patch("app.services.eta.get_db_connection")
@patch("app.services.eta.ReceiptSubmit")
def test_submit_receipt_sends_notification_on_success(
    mock_receipt_submit,
    mock_get_db,
    mock_connector,
    mock_client_cls,
    mock_create_log,
    mock_log_audit,
    mock_send_template,
):
    mock_connector.return_value = {
        "id": 1,
        "client_id": "test",
        "client_secret": "secret",
        "environment": "Pre-Production",
        "pos_serial": "POS1",
        "pos_os_version": "1.0",
    }

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": 1,
        "client_id": "test",
        "client_secret": "secret",
        "environment": "Pre-Production",
    }
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_get_db.return_value = mock_conn

    mock_client = MagicMock()
    mock_client.submit_receipts.return_value = {
        "submissionId": "REC-SUB-123",
        "acceptedDocuments": 1,
        "rejectedDocuments": 0,
    }
    mock_client_cls.return_value = mock_client
    mock_client.close = MagicMock()

    mock_create_log.return_value = {"id": 1}

    with patch("app.services.eta._is_notification_enabled", return_value=True):
        with patch("app.services.eta._get_user_email", return_value="test@example.com"):
            result = submit_receipt_to_eta(
                receipt_data={"document_id": 1},
                connector_id=1,
                current_user={"id": 1},
            )

    mock_send_template.assert_called_once()
    assert mock_send_template.call_args[1]["template_id"] == 2
    assert mock_send_template.call_args[1]["recipient"] == "test@example.com"
    assert "document_id" in mock_send_template.call_args[1]["variables"]
    assert result["submission_id"] == "REC-SUB-123"


@patch("app.services.eta.send_template_email")
@patch("app.services.eta.log_audit")
@patch("app.services.eta.create_eta_log")
@patch("app.services.eta.ETAClient")
@patch("app.services.eta._get_default_connector")
@patch("app.services.eta.get_db_connection")
@patch("app.services.eta.ReceiptSubmit")
def test_submit_receipt_does_not_send_notification_on_failure(
    mock_receipt_submit,
    mock_get_db,
    mock_connector,
    mock_client_cls,
    mock_create_log,
    mock_log_audit,
    mock_send_template,
):
    mock_connector.return_value = {
        "id": 1,
        "client_id": "test",
        "client_secret": "secret",
        "environment": "Pre-Production",
        "pos_serial": "POS1",
        "pos_os_version": "1.0",
    }

    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = {
        "id": 1,
        "client_id": "test",
        "client_secret": "secret",
        "environment": "Pre-Production",
    }
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_get_db.return_value = mock_conn

    mock_client = MagicMock()
    mock_client.submit_receipts.side_effect = ETAHttpError(
        status_code=500, message="Server Error", details=[]
    )
    mock_client_cls.return_value = mock_client
    mock_client.close = MagicMock()

    with pytest.raises(ValueError):
        submit_receipt_to_eta(
            receipt_data={"document_id": 1},
            connector_id=1,
            current_user={"id": 1},
        )

    mock_send_template.assert_not_called()
