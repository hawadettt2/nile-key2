from unittest.mock import patch, MagicMock

import pytest

from app.services.shipping import (
    create_shipment,
    update_shipment,
    _send_shipping_notification,
)


# ========== Helpers ==========


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


# ========== _send_shipping_notification Edge Cases ==========


def test_send_shipping_notification_skips_when_user_id_none():
    with patch("app.services.shipping.send_template_email") as mock_send:
        _send_shipping_notification(template_id=3, user_id=None)
        mock_send.assert_not_called()


def test_send_shipping_notification_skips_when_preference_disabled():
    with patch("app.services.shipping.send_template_email") as mock_send:
        with patch("app.services.shipping._is_notification_enabled", return_value=False):
            _send_shipping_notification(template_id=3, user_id=1)
        mock_send.assert_not_called()


def test_send_shipping_notification_skips_when_no_email():
    with patch("app.services.shipping.send_template_email") as mock_send:
        with patch("app.services.shipping._is_notification_enabled", return_value=True):
            with patch("app.services.shipping._get_user_email", return_value=None):
                _send_shipping_notification(template_id=3, user_id=1)
        mock_send.assert_not_called()


def test_send_shipping_notification_calls_send_template_email_when_enabled():
    with patch("app.services.shipping.send_template_email") as mock_send:
        with patch("app.services.shipping._is_notification_enabled", return_value=True):
            with patch("app.services.shipping._get_user_email", return_value="user@example.com"):
                _send_shipping_notification(
                    template_id=3,
                    user_id=1,
                    variables={"shipment_id": 10, "tracking_number": "NK123"},
                )
        mock_send.assert_called_once_with(
            template_id=3,
            recipient="user@example.com",
            variables={"shipment_id": 10, "tracking_number": "NK123"},
            current_user=None,
        )


# ========== create_shipment Notification Trigger ==========


@patch("app.services.shipping.send_template_email")
@patch("app.services.shipping.get_db_connection")
def test_create_shipment_sends_notification_on_success(mock_get_db, mock_send_template):
    mock_result = MagicMock()
    mock_result.shipment_id = 10
    mock_result.message = "Shipment created successfully"

    with patch("app.services.shipping._new_create_shipment", return_value=mock_result):
        with patch("app.services.shipping._is_notification_enabled", return_value=True):
            with patch("app.services.shipping._get_user_email", return_value="user@example.com"):
                mock_cursor = MagicMock()
                mock_cursor.fetchone.return_value = {"tracking_number": "NK123"}
                mock_conn = _mock_connection(mock_cursor)
                mock_get_db.return_value = mock_conn

                mock_data = MagicMock()
                mock_data.carrier = "LetMeShip"
                mock_data.service_type = "Standard"
                mock_data.origin = "EG"
                mock_data.destination = "US"
                mock_data.weight = 1
                mock_data.weight_unit = "kg"
                mock_data.dimensions = None
                mock_data.value = None
                mock_data.currency = "USD"
                mock_data.reference = None
                mock_data.supplier_id = None
                mock_data.customer_id = None
                mock_data.description_of_content = None
                mock_data.eta = None
                mock_data.pickup_from_type = None
                mock_data.delivery_to_type = None
                result = create_shipment(mock_data, {"id": 1})

    assert result["id"] == 10
    assert result["tracking_number"] == "NK123"
    mock_send_template.assert_called_once()
    assert mock_send_template.call_args[1]["template_id"] == 3
    assert mock_send_template.call_args[1]["recipient"] == "user@example.com"
    assert "shipment_id" in mock_send_template.call_args[1]["variables"]


@patch("app.services.shipping.send_template_email")
@patch("app.services.shipping.get_db_connection")
def test_create_shipment_skips_notification_when_user_id_none(mock_get_db, mock_send_template):
    mock_result = MagicMock()
    mock_result.shipment_id = 10
    mock_result.message = "Shipment created successfully"

    with patch("app.services.shipping._new_create_shipment", return_value=mock_result):
        with patch("app.services.shipping._is_notification_enabled", return_value=True):
            with patch("app.services.shipping._get_user_email", return_value="user@example.com"):
                mock_cursor = MagicMock()
                mock_cursor.fetchone.return_value = {"tracking_number": "NK123"}
                mock_conn = _mock_connection(mock_cursor)
                mock_get_db.return_value = mock_conn

                mock_data = MagicMock()
                mock_data.carrier = "LetMeShip"
                mock_data.service_type = "Standard"
                mock_data.origin = "EG"
                mock_data.destination = "US"
                mock_data.weight = 1
                mock_data.weight_unit = "kg"
                mock_data.dimensions = None
                mock_data.value = None
                mock_data.currency = "USD"
                mock_data.reference = None
                mock_data.supplier_id = None
                mock_data.customer_id = None
                mock_data.description_of_content = None
                mock_data.eta = None
                mock_data.pickup_from_type = None
                mock_data.delivery_to_type = None
                result = create_shipment(mock_data, current_user=None)

    assert result["id"] == 10
    mock_send_template.assert_not_called()


# ========== update_shipment Notification Trigger ==========


@patch("app.services.shipping.send_template_email")
@patch("app.services.shipping.get_db_connection")
def test_update_shipment_sends_notification_on_status_update(mock_get_db, mock_send_template):
    with patch("app.services.shipping._new_update_shipment_status") as mock_update:
        with patch("app.services.shipping._is_notification_enabled", return_value=True):
            with patch("app.services.shipping._get_user_email", return_value="user@example.com"):
                mock_update.return_value = {"message": "Shipment updated successfully"}

                mock_data = MagicMock()
                mock_data.status = "in_transit"

                result = update_shipment(10, mock_data, {"id": 1})

    assert result["message"] == "Shipment updated successfully"
    mock_send_template.assert_called_once()
    assert mock_send_template.call_args[1]["template_id"] == 4
    assert mock_send_template.call_args[1]["recipient"] == "user@example.com"
    assert mock_send_template.call_args[1]["variables"]["shipment_id"] == 10
    assert mock_send_template.call_args[1]["variables"]["status"] == "in_transit"


@patch("app.services.shipping.send_template_email")
@patch("app.services.shipping.get_db_connection")
def test_update_shipment_skips_notification_when_user_id_none(mock_get_db, mock_send_template):
    with patch("app.services.shipping._new_update_shipment_status") as mock_update:
        with patch("app.services.shipping._is_notification_enabled", return_value=True):
            with patch("app.services.shipping._get_user_email", return_value="user@example.com"):
                mock_update.return_value = {"message": "Shipment updated successfully"}

                mock_data = MagicMock()
                mock_data.status = "in_transit"

                result = update_shipment(10, mock_data, current_user=None)

    assert result["message"] == "Shipment updated successfully"
    mock_send_template.assert_not_called()


@patch("app.services.shipping.send_template_email")
@patch("app.services.shipping.get_db_connection")
def test_update_shipment_skips_notification_when_no_status_change(mock_get_db, mock_send_template):
    with patch("app.services.shipping._new_update_shipment_status") as mock_update:
        mock_update.return_value = {"message": "Shipment updated successfully"}

        mock_data = MagicMock()
        mock_data.status = None

        result = update_shipment(10, mock_data, {"id": 1})

    assert result["message"] == "Shipment updated successfully"
    mock_send_template.assert_not_called()
