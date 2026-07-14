from unittest.mock import MagicMock, patch

import pytest

from app.routers.search import router as search_router
from app.services.search import search_all, _calculate_relevance


def test_search_router_has_expected_route():
    routes = [route.path for route in search_router.routes]
    assert "/api/v1/search" in routes


def test_search_router_tags():
    assert search_router.tags == ["Search"]


def test_search_route_handler_delegates_to_service():
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {"results": [], "query": "test", "total": 0}

    with patch("app.routers.search.search_all", return_value=mock_response) as mock_search:
        route = [r for r in search_router.routes if r.path == "/api/v1/search"][0]
        handler = route.endpoint
        result = handler(query="test", entity_type=None, current_user={"id": 1})

    mock_search.assert_called_once_with(query="test", entity_type=None)
    assert result == mock_response


def test_search_route_handler_passes_entity_type():
    mock_response = MagicMock()
    mock_response.model_dump.return_value = {"results": [], "query": "test", "total": 0}

    with patch("app.routers.search.search_all", return_value=mock_response) as mock_search:
        route = [r for r in search_router.routes if r.path == "/api/v1/search"][0]
        handler = route.endpoint
        result = handler(query="test", entity_type="customer", current_user={"id": 1})

    mock_search.assert_called_once_with(query="test", entity_type="customer")
    assert result == mock_response


def test_search_service_relevance_exact_match():
    assert _calculate_relevance("Alice", "Alice") == 1.0


def test_search_service_relevance_starts_with():
    assert _calculate_relevance("Alice Corp", "Alice") == 0.8


def test_search_service_relevance_contains():
    assert _calculate_relevance("Alice Corp", "Corp") == 0.6


def test_search_service_empty_query():
    result = search_all("")
    assert result.total == 0
    assert result.results == []


def test_search_service_entity_type_filter():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "Alice", "contact_person": "Bob", "email": "a@example.com", "phone": "123"},
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.search.connection", return_value=mock_conn):
        with patch("app.services.search.build_list_query", return_value=("SELECT * FROM customers WHERE 1=1 AND (name LIKE ? OR name_en LIKE ? OR email LIKE ? OR phone LIKE ?) LIMIT 50 OFFSET 0", ["%Alice%", "%Alice%", "%Alice%", "%Alice%"])):
            result = search_all("Alice", entity_type="customer")

    assert len(result.results) == 1
    assert result.results[0].entity_type == "customer"
