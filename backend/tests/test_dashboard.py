from unittest.mock import MagicMock, patch

import pytest

from app.routers.dashboard import router as dashboard_router
from app.services.dashboard import get_dashboard, _count, _recent_activities, _notification_count


def test_dashboard_router_has_expected_route():
    routes = [route.path for route in dashboard_router.routes]
    assert "/api/v1/dashboard" in routes


def test_dashboard_router_tags():
    assert dashboard_router.tags == ["Dashboard"]


def test_dashboard_route_handler_delegates_to_service():
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {"stats": {}, "timeline": {}, "notifications_count": 0}

    with patch("app.routers.dashboard.get_dashboard", return_value=mock_response) as mock_get:
        route = [r for r in dashboard_router.routes if r.path == "/api/v1/dashboard"][0]
        handler = route.endpoint
        result = handler(current_user={"id": 1})

    mock_get.assert_called_once()
    assert result == mock_response


def test_dashboard_service_count():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (42,)
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.dashboard.connection", return_value=mock_conn):
        result = _count("customers")

    assert result == 42
    mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM customers")


def test_dashboard_service_recent_activities():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"action": "create", "entity_type": "customer", "details": "Created Alice", "created_at": "2024-01-01T00:00:00"},
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.dashboard.connection", return_value=mock_conn):
        result = _recent_activities(limit=1)

    assert len(result) == 1
    assert result[0]["action"] == "create"


def test_dashboard_service_notification_count():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (5,)
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.dashboard.connection", return_value=mock_conn):
        result = _notification_count()

    assert result == 5
    mock_cursor.execute.assert_called_once_with("SELECT COUNT(*) FROM notification_logs")


def test_dashboard_service_get_dashboard():
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
    assert result.notifications_count == 10
    assert len(result.timeline.recent_activities) == 1
