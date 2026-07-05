from unittest.mock import MagicMock, patch

import pytest

from app.services.shipping import (
    CARRIERS,
    create_shipment,
    get_label,
    get_rates,
    get_shipment,
    list_shipments,
    track_shipment,
    update_shipment,
)


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


def test_get_rates_returns_sorted_list_with_expected_keys():
    request = MagicMock(weight=10)
    with patch("app.services.shipping.random.uniform", return_value=1.0):
        with patch("app.services.shipping.random.randint", return_value=5):
            result = get_rates(request)

    assert len(result) == 10
    for rate in result:
        assert set(rate.keys()) == {"carrier", "service", "estimated_days", "cost", "currency"}
        assert rate["currency"] == "USD"
        assert rate["estimated_days"] == 5
    costs = [rate["cost"] for rate in result]
    assert costs == sorted(costs)


def test_get_rates_cost_formula_is_deterministic():
    request = MagicMock(weight=2)
    with patch("app.services.shipping.random.uniform", return_value=1.0):
        with patch("app.services.shipping.random.randint", return_value=5):
            result = get_rates(request)

    dhl_rate = next(rate for rate in result if rate["carrier"] == "DHL" and rate["service"] == "Express")
    expected_cost = round(25.0 * max(1, 2 * 0.5) * 1.0, 2)
    assert dhl_rate["cost"] == expected_cost


def test_list_shipments_returns_rows():
    mock_rows = [
        {"id": 1, "tracking_number": "NK1", "status": "pending"},
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.connection", return_value=mock_conn):
        result = list_shipments()

    assert len(result) == 1
    assert result[0]["id"] == 1


def test_track_shipment_returns_shipment_with_tracking_events():
    mock_row = {
        "id": 1,
        "tracking_number": "NK1",
        "status": "in_transit",
        "origin": "EG",
        "destination": "US",
        "shipped_at": "2026-07-05T00:00:00",
        "delivered_at": None,
    }
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.connection", return_value=mock_conn):
        result = track_shipment("NK1")

    assert result["tracking_number"] == "NK1"
    assert len(result["tracking_events"]) == 3
    assert result["tracking_events"][0]["status"] == "picked_up"
    assert result["tracking_events"][1]["status"] == "in_transit"
    assert result["tracking_events"][2]["status"] == "in_transit"


def test_track_shipment_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Shipment not found"):
            track_shipment("UNKNOWN")


def test_get_shipment_defaults_none_origin_and_destination():
    mock_row = {"id": 1, "origin": None, "destination": None}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.connection", return_value=mock_conn):
        result = get_shipment(1)

    assert result["origin"] == ""
    assert result["destination"] == ""


def test_get_shipment_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Shipment not found"):
            get_shipment(999)


def test_create_shipment_inserts_and_returns_tracking_number():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 3
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_data = MagicMock()
    mock_data.reference = "REF1"
    mock_data.supplier_id = 1
    mock_data.customer_id = 2
    mock_data.origin = "EG"
    mock_data.destination = "US"
    mock_data.carrier = "DHL"
    mock_data.service_type = "Express"
    mock_data.weight = 10
    mock_data.weight_unit = "kg"
    mock_data.dimensions = "10x10x10"
    mock_data.value = 100.0
    mock_data.currency = "USD"
    mock_data.items_count = 1
    mock_data.description = "Desc"
    mock_data.eta = None

    fixed_now = "2026-07-05T12:00:00"
    with patch("app.services.shipping.connection", return_value=mock_conn):
        with patch("app.services.shipping.now_iso", return_value=fixed_now):
            with patch("app.services.shipping.datetime") as mock_datetime:
                mock_datetime.utcnow.return_value.strftime.return_value = "20260705120000"
                with patch("app.services.shipping.random.randint", return_value=1234):
                    result = create_shipment(mock_data, {"id": 1})

    assert result["id"] == 3
    assert result["tracking_number"] == "NK202607051200001234"
    assert result["message"] == "Shipment created successfully"
    mock_conn.commit.assert_called_once()
    assert mock_cursor.execute.call_count == 1


def test_update_shipment_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Shipment not found"):
            update_shipment(999, MagicMock(), {"id": 1})


def test_update_shipment_no_changes():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.shipping.connection", return_value=mock_conn):
        with patch("app.services.shipping.execute_update", return_value=False):
            result = update_shipment(1, mock_data, {"id": 1})

    assert result == {"message": "No changes"}


def test_update_shipment_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()

    with patch("app.services.shipping.connection", return_value=mock_conn):
        with patch("app.services.shipping.execute_update", return_value=True):
            result = update_shipment(1, mock_data, {"id": 1})

    assert result == {"message": "Shipment updated successfully"}


def test_get_label_returns_expected_shape():
    result = get_label(5)

    assert result["shipment_id"] == 5
    assert result["label_url"] == "/api/v1/shipping/shipments/5/label.pdf"
    assert result["message"] == "Label generated"
