from unittest.mock import MagicMock, patch

import pytest

from app.services.dashboard import (
    _count,
    _recent_activities,
    _upcoming_shipments,
    _pending_invoices,
    _notification_count,
    get_dashboard,
)


def test_count_returns_zero_for_empty_table():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (0,)
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.dashboard.connection", return_value=mock_conn):
        result = _count("customers")

    assert result == 0
    mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM customers")


def test_count_returns_positive_count():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (42,)
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.dashboard.connection", return_value=mock_conn):
        result = _count("invoices")

    assert result == 42


def test_recent_activities_returns_list():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"action": "create", "entity_type": "customer", "details": "Created Alice", "created_at": "2024-01-01T00:00:00"},
        {"action": "update", "entity_type": "invoice", "details": "Updated INV-1", "created_at": "2024-01-02T00:00:00"},
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.dashboard.connection", return_value=mock_conn):
        result = _recent_activities(limit=2)

    assert len(result) == 2
    assert result[0]["action"] == "create"
    assert result[1]["entity_type"] == "invoice"


def test_upcoming_shipments_returns_list():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "tracking_number": "TRK-1", "status": "pending", "origin": "Cairo", "destination": "Dubai", "eta": "2024-01-01"},
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.dashboard.connection", return_value=mock_conn):
        result = _upcoming_shipments(limit=10)

    assert len(result) == 1
    assert result[0]["tracking_number"] == "TRK-1"
    assert isinstance(result[0], dict)


def test_pending_invoices_returns_list():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "invoice_number": "INV-001", "status": "draft", "total": 1000.0, "currency": "EGP"},
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.dashboard.connection", return_value=mock_conn):
        result = _pending_invoices(limit=10)

    assert len(result) == 1
    assert result[0]["invoice_number"] == "INV-001"
    assert result[0]["total"] == 1000.0


def test_notification_count_returns_zero_when_empty():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (0,)
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.dashboard.connection", return_value=mock_conn):
        result = _notification_count()

    assert result == 0
    mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM notification_logs")


def test_get_dashboard_returns_response():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        (10,),  # customers
        (5,),   # suppliers
        (3,),   # shipments
        (8,),   # invoices
        (2,),   # customs_declarations
        (4,),   # documents
        (6,),   # resources
        (1,),   # eta_connectors
        (10,),  # notification_logs
    ]
    mock_cursor.fetchall.side_effect = [
        [{"action": "create", "entity_type": "customer", "details": "Created", "created_at": "2024-01-01"}],
        [{"id": 1, "tracking_number": "TRK-1", "status": "pending", "origin": "Cairo", "destination": "Dubai", "eta": "2024-01-01"}],
        [{"id": 1, "invoice_number": "INV-1", "status": "draft", "total": 100.0, "currency": "EGP"}],
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.dashboard.connection", return_value=mock_conn):
        result = get_dashboard()

    assert result.stats.customers == 10
    assert result.stats.suppliers == 5
    assert result.stats.shipments == 3
    assert result.stats.invoices == 8
    assert result.stats.customs_declarations == 2
    assert result.stats.documents == 4
    assert result.stats.resources == 6
    assert result.stats.eta_connectors == 1
    assert result.notifications_count == 10
    assert len(result.timeline.recent_activities) == 1
    assert len(result.timeline.upcoming_shipments) == 1
    assert len(result.timeline.pending_invoices) == 1
