from unittest.mock import MagicMock, patch, AsyncMock
import pytest

from app.services.knowledge_graph import (
    _node_row_to_response,
    _edge_row_to_response,
    _validate_node_id,
    _validate_entity_type,
    create_node,
    get_node,
    update_node,
    delete_node,
    create_edge,
    get_edge,
    delete_edge,
    list_edges_for_node,
    _derive_edges_from_entity,
    traverse,
    _get_entity_name,
    _sync_entity,
    sync_entity,
    sync_all,
    search_nodes,
    _store_graph_context,
    _recall_graph_context,
    _audit_mutation,
    set_memory_provider,
    SUPPORTED_NODE_TYPES,
    ENTITY_REFERENCE_COLUMNS,
)


# ========== Helpers ==========


def _mock_connection(mock_cursor):
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    return mock_conn


def _make_node_row(node_id="customer:1", entity_type="customer", entity_id=1, label="Customer 1"):
    return {
        "id": node_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "label": label,
        "properties": None,
        "created_at": "2026-07-20T00:00:00",
        "updated_at": "2026-07-20T00:00:00",
    }


def _make_edge_row(edge_id="edge-1", source_node_id="customer:1", target_node_id="supplier:1", relationship_type="references_supplier"):
    return {
        "id": edge_id,
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "relationship_type": relationship_type,
        "properties": None,
        "created_at": "2026-07-20T00:00:00",
        "created_by": 1,
    }


def _make_user(user_id=1):
    return {"id": user_id}


# ========== _node_row_to_response Tests ==========


def test_node_row_to_response_maps_fields():
    row = _make_node_row()
    result = _node_row_to_response(row)
    assert result["id"] == "customer:1"
    assert result["entity_type"] == "customer"
    assert result["entity_id"] == 1
    assert result["label"] == "Customer 1"


def test_node_row_to_response_parses_null_properties():
    row = _make_node_row()
    row["properties"] = None
    result = _node_row_to_response(row)
    assert result["properties"] == {}


# ========== _edge_row_to_response Tests ==========


def test_edge_row_to_response_maps_fields():
    row = _make_edge_row()
    result = _edge_row_to_response(row)
    assert result["id"] == "edge-1"
    assert result["source_node_id"] == "customer:1"
    assert result["target_node_id"] == "supplier:1"
    assert result["relationship_type"] == "references_supplier"
    assert result["created_by"] == 1


# ========== Validation Tests ==========


def test_validate_node_id_valid():
    _validate_node_id("customer:1")


def test_validate_node_id_invalid_format():
    with pytest.raises(ValueError, match="Invalid node id format"):
        _validate_node_id("invalid")


def test_validate_node_id_unsupported_entity_type():
    with pytest.raises(ValueError, match="Unsupported entity type"):
        _validate_node_id("product:1")


def test_validate_node_id_non_digit_entity_id():
    with pytest.raises(ValueError, match="Invalid entity id"):
        _validate_node_id("customer:abc")


def test_validate_entity_type_valid():
    _validate_entity_type("customer")


def test_validate_entity_type_unsupported():
    with pytest.raises(ValueError, match="Unsupported entity type"):
        _validate_entity_type("product")


# ========== Node CRUD Tests ==========


def test_create_node_inserts_record():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with patch("app.services.knowledge_graph.now_iso", return_value="2026-07-20T00:00:00"):
            result = create_node(
                data=MagicMock(entity_type="customer", entity_id=1, label="Customer 1", properties={}),
                current_user=_make_user(1),
            )

    assert result["id"] == "customer:1"
    assert result["message"] == "Node created successfully"
    mock_conn.commit.assert_called_once()
    assert mock_cursor.execute.call_count == 1


def test_get_node_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _make_node_row()
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = get_node("customer:1")

    assert result["id"] == "customer:1"
    assert result["label"] == "Customer 1"


def test_get_node_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Node not found"):
            get_node("customer:999")


def test_update_node_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _make_node_row()
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with patch("app.services.knowledge_graph.now_iso", return_value="2026-07-20T00:00:00"):
            result = update_node(
                node_id="customer:1",
                data=MagicMock(label="Updated", properties={}),
                current_user=_make_user(1),
            )

    assert result["id"] == "customer:1"
    assert result["message"] == "Node updated successfully"
    mock_conn.commit.assert_called_once()


def test_update_node_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Node not found"):
            update_node(
                node_id="customer:999",
                data=MagicMock(label="Updated", properties={}),
                current_user=_make_user(1),
            )


def test_delete_node_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _make_node_row()
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = delete_node("customer:1", current_user=_make_user(1))

    assert result["id"] == "customer:1"
    assert result["message"] == "Node deleted successfully"
    assert mock_cursor.execute.call_count == 3


def test_delete_node_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Node not found"):
            delete_node("customer:999", current_user=_make_user(1))


# ========== Edge CRUD Tests ==========


def test_create_edge_inserts_record():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.side_effect = [_make_node_row(), _make_node_row()]

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with patch("app.services.knowledge_graph.now_iso", return_value="2026-07-20T00:00:00"):
            result = create_edge(
                data=MagicMock(source_node_id="customer:1", target_node_id="supplier:1", relationship_type="references_supplier", properties={}),
                current_user=_make_user(1),
            )

    assert "id" in result
    assert result["message"] == "Edge created successfully"
    mock_conn.commit.assert_called_once()


def test_create_edge_source_node_not_found():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.return_value = None

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Source node not found"):
            create_edge(
                data=MagicMock(source_node_id="missing:1", target_node_id="supplier:1", relationship_type="ref", properties={}),
                current_user=_make_user(1),
            )


def test_create_edge_target_node_not_found():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.side_effect = [_make_node_row(), None]

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Target node not found"):
            create_edge(
                data=MagicMock(source_node_id="customer:1", target_node_id="missing:1", relationship_type="ref", properties={}),
                current_user=_make_user(1),
            )


def test_get_edge_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _make_edge_row()
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = get_edge("edge-1")

    assert result["id"] == "edge-1"
    assert result["source_node_id"] == "customer:1"


def test_get_edge_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Edge not found"):
            get_edge("missing-edge")


def test_delete_edge_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _make_edge_row()
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = delete_edge("edge-1", current_user=_make_user(1))

    assert result["id"] == "edge-1"
    assert result["message"] == "Edge deleted successfully"
    mock_conn.commit.assert_called_once()


def test_delete_edge_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with pytest.raises(ValueError, match="Edge not found"):
            delete_edge("missing-edge", current_user=_make_user(1))


def test_list_edges_for_node_returns_edges():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [_make_edge_row()]
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = list_edges_for_node("customer:1")

    assert len(result) == 1
    assert result[0]["id"] == "edge-1"


# ========== Derived Edge Discovery Tests ==========


def test_derive_edges_from_shipment():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.side_effect = [(1, 1), (1, 2), (1, 3)]

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = _derive_edges_from_entity("shipment", 1)

    assert len(result) == 3
    assert result[0]["relationship_type"] == "references_supplier"
    assert result[0]["target_node_id"] == "supplier:1"
    assert result[1]["relationship_type"] == "references_customer"
    assert result[1]["target_node_id"] == "customer:2"
    assert result[2]["relationship_type"] == "references_customs_declaration"
    assert result[2]["target_node_id"] == "customs_declaration:3"


def test_derive_edges_from_invoice():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.return_value = (1, 2, 3)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = _derive_edges_from_entity("invoice", 1)

    assert len(result) == 3
    assert result[0]["relationship_type"] == "references_customer"
    assert result[1]["relationship_type"] == "references_supplier"
    assert result[2]["relationship_type"] == "references_shipment"


def test_derive_edges_from_customs_declaration():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.return_value = (1, 2)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = _derive_edges_from_entity("customs_declaration", 1)

    assert len(result) == 2
    assert result[0]["relationship_type"] == "references_shipment"
    assert result[1]["relationship_type"] == "references_hs_code"


def test_derive_edges_from_export_workflow():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.return_value = (1, 2, 3, 4, 5)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = _derive_edges_from_entity("export_workflow", 1)

    assert len(result) == 5
    assert result[0]["relationship_type"] == "references_customer"
    assert result[4]["relationship_type"] == "references_shipment"


def test_derive_edges_from_document_valid_target():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.side_effect = [("customer", 1), None]

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = _derive_edges_from_entity("document", 1)

    assert len(result) == 1
    assert result[0]["target_node_id"] == "customer:1"
    assert result[0]["relationship_type"] == "references_customer"


def test_derive_edges_from_document_unsupported_target():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.return_value = ("unsupported_type", 1)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = _derive_edges_from_entity("document", 1)

    assert len(result) == 0


def test_derive_edges_from_document_no_target():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.return_value = None

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = _derive_edges_from_entity("document", 1)

    assert len(result) == 0


# ========== Graph Traversal Tests ==========


def test_traverse_returns_start_node():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _make_node_row()
    mock_cursor.fetchall.return_value = []
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with patch("app.services.knowledge_graph.get_node", side_effect=[_make_node_row(), ValueError("not found")]):
            with patch("app.services.knowledge_graph.list_edges_for_node", return_value=[]):
                with patch("app.services.knowledge_graph._derive_edges_from_entity", return_value=[]):
                    result = traverse("customer", 1, depth=1)

    assert len(result["nodes"]) == 1
    assert result["nodes"][0]["id"] == "customer:1"


def test_traverse_respects_depth():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _make_node_row()
    mock_cursor.fetchall.return_value = []
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with patch("app.services.knowledge_graph.get_node", side_effect=[_make_node_row(), ValueError("stop")]):
            with patch("app.services.knowledge_graph.list_edges_for_node", return_value=[]):
                with patch("app.services.knowledge_graph._derive_edges_from_entity", return_value=[]):
                    result = traverse("customer", 1, depth=1)

    assert result["depth"] == 1


# ========== Entity Name Tests ==========


def test_get_entity_name_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = ("Customer 1",)
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = _get_entity_name("customer", 1)

    assert result == "Customer 1"


def test_get_entity_name_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = _get_entity_name("customer", 999)

    assert result is None


# ========== Entity Synchronization Tests ==========


def test_sync_entity_creates_new_node():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.side_effect = [None, None]

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with patch("app.services.knowledge_graph.now_iso", return_value="2026-07-20T00:00:00"):
            with patch("app.services.knowledge_graph._get_entity_name", return_value="Customer 1"):
                result = _sync_entity("customer", 1)

    assert result["action"] == "created"
    assert result["id"] == "customer:1"
    mock_conn.commit.assert_called_once()


def test_sync_entity_updates_existing_node():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _make_node_row()
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with patch("app.services.knowledge_graph.now_iso", return_value="2026-07-20T00:00:00"):
            with patch("app.services.knowledge_graph._get_entity_name", return_value="Updated Name"):
                result = _sync_entity("customer", 1)

    assert result["action"] == "updated"
    assert result["id"] == "customer:1"


def test_sync_entity_wrapper():
    with patch("app.services.knowledge_graph._sync_entity", return_value={"id": "customer:1", "action": "created"}) as mock_sync:
        result = sync_entity("customer", 1)

    assert result["id"] == "customer:1"
    mock_sync.assert_called_once_with("customer", 1)


def test_sync_all_iterates_entities():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.return_value = (1,)
    mock_cursor.fetchall.return_value = [(1,)]

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with patch("app.services.knowledge_graph._sync_entity", return_value={"id": "customer:1", "action": "created"}) as mock_sync:
            result = sync_all()

    assert result["synced"] == len(SUPPORTED_NODE_TYPES)
    assert mock_sync.call_count == len(SUPPORTED_NODE_TYPES)


# ========== Search Tests ==========


def test_search_nodes_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [_make_node_row()]
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = search_nodes(query="Customer", skip=0, limit=100)

    assert len(result) == 1
    assert result[0]["id"] == "customer:1"


def test_search_nodes_with_entity_type_filter():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [_make_node_row()]
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = search_nodes(query="Customer", entity_type="customer", skip=0, limit=100)

    assert len(result) == 1
    executed_sql = mock_cursor.execute.call_args[0][0]
    assert "entity_type = ?" in executed_sql


def test_search_nodes_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = []
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = search_nodes(query="NonExistent", skip=0, limit=100)

    assert result == []


# ========== Memory Integration Tests ==========


@pytest.mark.asyncio
async def test_store_graph_context_without_provider():
    result = await _store_graph_context("session-123", "key", {"test": "value"})
    assert result is None


@pytest.mark.asyncio
async def test_recall_graph_context_without_provider():
    result = await _recall_graph_context("session-123", "query")
    assert result == []


@pytest.mark.asyncio
async def test_store_graph_context_with_provider():
    mock_provider = AsyncMock()
    mock_provider.store.return_value = "memory-1"
    set_memory_provider(mock_provider)

    result = await _store_graph_context("session-123", "key", {"test": "value"})

    mock_provider.store.assert_called_once_with(
        session_id="session-123",
        key="key",
        value={"test": "value"},
        memory_type="context",
        importance=7,
    )
    assert result is None


@pytest.mark.asyncio
async def test_recall_graph_context_with_provider():
    mock_provider = AsyncMock()
    mock_provider.recall.return_value = [{"key": "key", "value": {"test": "value"}}]
    set_memory_provider(mock_provider)

    result = await _recall_graph_context("session-123", "query")

    mock_provider.recall.assert_called_once_with(
        session_id="session-123",
        query="query",
        limit=10,
    )
    assert len(result) == 1


@pytest.mark.asyncio
async def test_store_graph_context_handles_provider_exception():
    mock_provider = AsyncMock()
    mock_provider.store.side_effect = Exception("Memory error")
    set_memory_provider(mock_provider)

    result = await _store_graph_context("session-123", "key", {"test": "value"})

    assert result is None


@pytest.mark.asyncio
async def test_recall_graph_context_handles_provider_exception():
    mock_provider = AsyncMock()
    mock_provider.recall.side_effect = Exception("Memory error")
    set_memory_provider(mock_provider)

    result = await _recall_graph_context("session-123", "query")

    assert result == []


# ========== Audit Integration Tests ==========


def test_audit_mutation_with_user_calls_log_audit():
    with patch("app.services.knowledge_graph.log_audit") as mock_log_audit:
        with patch("app.services.knowledge_graph.AuditLogCreate") as mock_audit_create:
            mock_audit_create.return_value = MagicMock()
            _audit_mutation(_make_user(1), "create", "knowledge_graph", "customer:1", "Node created")

    mock_log_audit.assert_called_once()
    call_kwargs = mock_log_audit.call_args
    assert call_kwargs.kwargs["current_user"] == {"id": 1}
    audit_data_call = mock_audit_create.call_args
    assert audit_data_call.kwargs["action"] == "create"
    assert audit_data_call.kwargs["entity_type"] == "knowledge_graph"
    assert audit_data_call.kwargs["entity_id"] == "customer:1"
    assert audit_data_call.kwargs["details"] == "Node created"


def test_audit_mutation_without_user_skips_logging():
    with patch("app.services.knowledge_graph.log_audit") as mock_log_audit:
        _audit_mutation(None, "create", "knowledge_graph", "customer:1", "Node created")

    mock_log_audit.assert_not_called()


def test_audit_mutation_handles_log_audit_exception():
    with patch("app.services.knowledge_graph.log_audit", side_effect=Exception("Audit error")):
        _audit_mutation(_make_user(1), "create", "knowledge_graph", "customer:1", "Node created")


# ========== Graceful Degradation Tests ==========


def test_create_node_without_current_user_no_audit():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with patch("app.services.knowledge_graph.now_iso", return_value="2026-07-20T00:00:00"):
            result = create_node(
                data=MagicMock(entity_type="customer", entity_id=1, label="Customer 1", properties={}),
                current_user=None,
            )

    assert result["id"] == "customer:1"
    assert result["message"] == "Node created successfully"


def test_create_edge_without_current_user_no_audit():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = MagicMock(return_value=mock_conn)
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_cursor.fetchone.side_effect = [_make_node_row(), _make_node_row()]

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with patch("app.services.knowledge_graph.now_iso", return_value="2026-07-20T00:00:00"):
            result = create_edge(
                data=MagicMock(source_node_id="customer:1", target_node_id="supplier:1", relationship_type="ref", properties={}),
                current_user=None,
            )

    assert "id" in result
    assert result["message"] == "Edge created successfully"


def test_delete_node_without_current_user_no_audit():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _make_node_row()
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = delete_node("customer:1", current_user=None)

    assert result["message"] == "Node deleted successfully"


def test_delete_edge_without_current_user_no_audit():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _make_edge_row()
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        result = delete_edge("edge-1", current_user=None)

    assert result["message"] == "Edge deleted successfully"


def test_update_node_without_current_user_no_audit():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = _make_node_row()
    mock_conn = _mock_connection(mock_cursor)

    with patch("app.services.knowledge_graph.connection", return_value=mock_conn):
        with patch("app.services.knowledge_graph.now_iso", return_value="2026-07-20T00:00:00"):
            result = update_node(
                node_id="customer:1",
                data=MagicMock(label="Updated", properties={}),
                current_user=None,
            )

    assert result["message"] == "Node updated successfully"


# ========== Constants Tests ==========


def test_supported_node_types_includes_expected_types():
    assert "customer" in SUPPORTED_NODE_TYPES
    assert "supplier" in SUPPORTED_NODE_TYPES
    assert "shipment" in SUPPORTED_NODE_TYPES
    assert "invoice" in SUPPORTED_NODE_TYPES
    assert "document" in SUPPORTED_NODE_TYPES
    assert "resource" in SUPPORTED_NODE_TYPES
    assert "hs_code" in SUPPORTED_NODE_TYPES
    assert "customs_declaration" in SUPPORTED_NODE_TYPES
    assert "export_workflow" in SUPPORTED_NODE_TYPES
    assert len(SUPPORTED_NODE_TYPES) == 9


def test_entity_reference_columns_has_expected_keys():
    assert "shipment" in ENTITY_REFERENCE_COLUMNS
    assert "invoice" in ENTITY_REFERENCE_COLUMNS
    assert "customs_declaration" in ENTITY_REFERENCE_COLUMNS
    assert "export_workflow" in ENTITY_REFERENCE_COLUMNS
    assert "document" in ENTITY_REFERENCE_COLUMNS


def test_entity_reference_columns_document_is_empty():
    assert ENTITY_REFERENCE_COLUMNS["document"] == []
