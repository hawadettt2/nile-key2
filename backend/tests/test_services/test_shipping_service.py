from unittest.mock import MagicMock, patch

import pytest

from app.services.shipping import (
    get_rates,
    list_shipments,
    track_shipment,
    get_shipment,
    create_shipment,
    update_shipment,
    get_label,
    fetch_rates,
    cancel_shipment,
    validate_phone,
    validate_address,
    validate_parcels,
    create_provider,
    list_providers,
    get_provider_by_id,
    update_provider,
    delete_provider,
    create_parcel_template,
    list_parcel_templates,
    get_parcel_template,
    update_parcel_template,
    delete_parcel_template,
)
from app.services.shipping.base import ShippingError, ValidationError
from app.schemas.shipping import RateRequest, ShippingAddress, ShippingContact, Parcel


# ========== Helpers ==========

def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


# ========== Rate Calculation ==========

def test_get_rates_returns_empty_list_when_no_providers():
    with patch("app.services.shipping.get_enabled_providers", return_value=[]):
        result = get_rates(RateRequest(origin="EG", destination="US", weight=1))
    assert result == []


def test_get_rates_aggregates_from_providers():
    mock_provider = MagicMock()
    mock_provider.get_available_services.return_value = [
        {"carrier": "TestCarrier", "service": "Standard", "estimated_days": 3, "cost": 10.0, "currency": "USD"}
    ]
    with patch("app.services.shipping.get_enabled_providers", return_value=[mock_provider]):
        result = get_rates(RateRequest(origin="EG", destination="US", weight=1))
    assert len(result) == 1
    assert result[0]["carrier"] == "TestCarrier"
    assert result[0]["cost"] == 10.0


def test_get_rates_sorted_by_cost():
    mock_provider1 = MagicMock()
    mock_provider1.get_available_services.return_value = [
        {"carrier": "A", "service": "S", "estimated_days": 3, "cost": 20.0, "currency": "USD"}
    ]
    mock_provider2 = MagicMock()
    mock_provider2.get_available_services.return_value = [
        {"carrier": "B", "service": "S", "estimated_days": 2, "cost": 10.0, "currency": "USD"}
    ]
    with patch("app.services.shipping.get_enabled_providers", return_value=[mock_provider1, mock_provider2]):
        result = get_rates(RateRequest(origin="EG", destination="US", weight=1))
    assert result[0]["cost"] == 10.0
    assert result[1]["cost"] == 20.0


def test_get_rates_isolates_provider_failures():
    mock_provider1 = MagicMock()
    mock_provider1.get_available_services.side_effect = Exception("Provider down")
    mock_provider2 = MagicMock()
    mock_provider2.get_available_services.return_value = [
        {"carrier": "B", "service": "S", "estimated_days": 2, "cost": 10.0, "currency": "USD"}
    ]
    with patch("app.services.shipping.get_enabled_providers", return_value=[mock_provider1, mock_provider2]):
        result = get_rates(RateRequest(origin="EG", destination="US", weight=1))
    assert len(result) == 1
    assert result[0]["carrier"] == "B"


# ========== List Shipments ==========

def test_list_shipments_returns_rows():
    mock_rows = [
        {"id": 1, "tracking_number": "NK1", "status": "pending"},
    ]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        result = list_shipments()

    assert len(result) == 1
    assert result[0]["id"] == 1


# ========== Get Shipment ==========

def test_get_shipment_defaults_none_origin_and_destination():
    mock_row = {"id": 1, "origin": None, "destination": None}
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        result = get_shipment(1)

    assert result["origin"] == ""
    assert result["destination"] == ""


def test_get_shipment_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        with pytest.raises(ShippingError, match="Shipment not found"):
            get_shipment(999)


# ========== Track Shipment ==========

def test_track_shipment_returns_shipment_with_tracking_events():
    mock_row = {
        "id": 1,
        "tracking_number": "NK1",
        "status": "in_transit",
        "origin": "EG",
        "destination": "US",
        "shipped_at": "2026-07-05T00:00:00",
        "delivered_at": None,
        "service_provider": "",
        "provider_shipment_id": None,
        "carrier": "TestCarrier",
    }
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        result = track_shipment("NK1")

    assert result["tracking_number"] == "NK1"
    assert len(result["tracking_events"]) >= 1


def test_track_shipment_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        with pytest.raises(ShippingError, match="Shipment not found"):
            track_shipment("UNKNOWN")


# ========== Create Shipment ==========

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
    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        with patch("app.services.shipping.datetime") as mock_datetime:
            mock_datetime.utcnow.return_value.strftime.return_value = "20260705120000"
            with patch("random.randint", return_value=1234):
                result = create_shipment(mock_data, {"id": 1})

    assert result["id"] == 3
    assert "tracking_number" in result
    assert result["message"] == "Shipment created successfully"
    assert mock_conn.commit.call_count == 2
    assert mock_cursor.execute.call_count >= 1


# ========== Update Shipment ==========

def test_update_shipment_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        with pytest.raises(ShippingError, match="Shipment not found"):
            update_shipment(999, MagicMock(), {"id": 1})


def test_update_shipment_no_changes():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()
    mock_data.model_dump.return_value = {}

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        result = update_shipment(1, mock_data, {"id": 1})

    assert result["message"] == "Shipment updated successfully"


def test_update_shipment_success():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (1,)
    mock_conn = _mock_connection(mock_cursor)
    mock_data = MagicMock()
    mock_data.model_dump.return_value = {"status": "in_transit"}

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        result = update_shipment(1, mock_data, {"id": 1})

    assert result["message"] == "Shipment updated successfully"


# ========== Label ==========

def test_get_label_returns_expected_shape():
    result = get_label(5)

    assert result["shipment_id"] == 5
    assert "label_url" in result
    assert result["message"] == "Label retrieved successfully"


# ========== Validation Helpers ==========

def test_validate_phone_valid():
    assert validate_phone("+201234567890") == "+201234567890"


def test_validate_phone_invalid():
    with pytest.raises(ValidationError):
        validate_phone("0123456789")


def test_validate_address_success():
    addr = ShippingAddress(title="Home", line1="123 St", city="Cairo", pincode="12345", country="EG")
    result = validate_address(addr)
    assert result.pincode == "12345"


def test_validate_address_missing_country():
    with pytest.raises(ValidationError):
        validate_address(ShippingAddress(title="Home", line1="123 St", city="Cairo", pincode="12345", country=""))


def test_validate_parcels_success():
    parcels = [Parcel(length=10, width=10, height=10, weight=1)]
    assert validate_parcels(parcels) == parcels


def test_validate_parcels_zero_dimension():
    with pytest.raises(Exception):
        validate_parcels([Parcel(length=0, width=10, height=10, weight=1)])


# ========== Provider CRUD ==========

def test_create_provider():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    mock_data = MagicMock()
    mock_data.name = "Test"
    mock_data.provider_type = "letmeship"
    mock_data.environment = "Pre-Production"
    mock_data.enabled = True
    mock_data.is_default = False
    mock_data.config = {}
    mock_data.status = "active"

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        with patch("app.services.shipping.get_provider_by_id") as mock_get:
            mock_get.return_value = MagicMock()
            result = create_provider(mock_data, {"id": 1})

    assert mock_cursor.execute.call_count == 1
    mock_conn.commit.assert_called_once()


def test_list_providers():
    mock_rows = [{"id": 1, "name": "LetMeShip", "config": "{}"}]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        result = list_providers()

    assert len(result) == 1
    assert result[0]["name"] == "LetMeShip"


# ========== Parcel Template CRUD ==========

def test_create_parcel_template():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 1
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        with patch("app.services.shipping.get_parcel_template") as mock_get:
            mock_get.return_value = MagicMock()
            result = create_parcel_template(
                MagicMock(name="Small", length=10, width=10, height=10, weight=1),
                {"id": 1}
            )

    assert mock_cursor.execute.call_count == 1
    mock_conn.commit.assert_called_once()


def test_list_parcel_templates():
    mock_rows = [{"id": 1, "name": "Small", "length": 10, "width": 10, "height": 10, "weight": 1}]
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        result = list_parcel_templates()

    assert len(result) == 1
    assert result[0]["name"] == "Small"


# ========== Cancellation ==========

def test_cancel_shipment_success():
    mock_row = {
        "id": 1,
        "tracking_number": "NK1",
        "status": "booked",
        "service_provider": "LetMeShip",
        "provider_shipment_id": "123",
    }
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = mock_row
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.shipping.get_db_connection", return_value=mock_conn):
        with patch("app.services.shipping.get_provider") as mock_provider:
            mock_provider.return_value.cancel_shipment.return_value = {"message": "cancelled"}
            result = cancel_shipment(1, {"id": 1})

    assert result["status"] == "cancelled"
