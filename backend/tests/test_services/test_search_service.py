from unittest.mock import MagicMock, patch

import pytest

from app.services.search import (
    _calculate_relevance,
    search_all,
)


def test_calculate_relevance_exact_match():
    assert _calculate_relevance("Alice", "Alice") == 1.0
    assert _calculate_relevance("alice", "ALICE") == 1.0


def test_calculate_relevance_starts_with():
    assert _calculate_relevance("Alice Corp", "Alice") == 0.8
    assert _calculate_relevance("alice corp", "ALICE") == 0.8


def test_calculate_relevance_contains():
    assert _calculate_relevance("Alice Corp", "Corp") == 0.6
    assert _calculate_relevance("Alice Corp", "ice") == 0.6


def test_calculate_relevance_no_match():
    assert _calculate_relevance("Alice", "xyz") == 0.0


def test_calculate_relevance_empty_inputs():
    assert _calculate_relevance("", "query") == 0.0
    assert _calculate_relevance("Alice", "") == 0.0
    assert _calculate_relevance(None, "query") == 0.0


def test_search_all_empty_query():
    result = search_all("")
    assert result.total == 0
    assert result.results == []
    assert result.query == ""


def test_search_all_entity_type_filter():
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
    assert result.results[0].id == 1


def test_search_all_returns_sorted_by_relevance():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"id": 1, "name": "ABC", "contact_person": None, "email": None, "phone": None},
        {"id": 2, "name": "A", "contact_person": None, "email": None, "phone": None},
        {"id": 3, "name": "XYZ", "contact_person": None, "email": None, "phone": None},
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.search.connection", return_value=mock_conn):
        with patch("app.services.search.build_list_query", return_value=("SELECT * FROM customers WHERE 1=1 AND (name LIKE ? OR name_en LIKE ? OR email LIKE ? OR phone LIKE ?) LIMIT 50 OFFSET 0", ["%A%", "%A%", "%A%", "%A%"])):
            result = search_all("A", entity_type="customer")

    relevances = [r.relevance for r in result.results]
    assert relevances == sorted(relevances, reverse=True)


def test_search_all_multiple_entities():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.side_effect = [
        [{"id": 1, "name": "Alice", "contact_person": None, "email": None, "phone": None}],
        [],
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    def fake_build_list_query(table, search_fields=None, search=None, limit=100, **kwargs):
        like = f"%{search}%"
        clauses = [f"{field} LIKE ?" for field in (search_fields or [])]
        query = f"SELECT * FROM {table} WHERE 1=1"
        params = []
        if search and clauses:
            query += " AND (" + " OR ".join(clauses) + ")"
            params.extend([like] * len(clauses))
        query += " LIMIT ? OFFSET 0"
        params.append(limit)
        return query, params

    with patch("app.services.search.connection", return_value=mock_conn):
        with patch("app.services.search.build_list_query", side_effect=fake_build_list_query):
            result = search_all("Alice", entity_type="customer")

    assert result.total == 1
    assert len(result.results) == 1
    assert result.results[0].entity_type == "customer"
