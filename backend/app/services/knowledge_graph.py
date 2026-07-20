import uuid
from typing import Optional, List, Dict, Any

from app.services.base import connection, now_iso, parse_json, dumps_json
from app.services.audit import log_audit
from app.schemas.audit import AuditLogCreate
from app.schemas.knowledge_graph import (
    KnowledgeGraphNodeCreate,
    KnowledgeGraphEdgeCreate,
)

SUPPORTED_NODE_TYPES = (
    "customer",
    "supplier",
    "shipment",
    "invoice",
    "document",
    "resource",
    "hs_code",
    "customs_declaration",
    "export_workflow",
)

_memory_provider = None


def set_memory_provider(provider) -> None:
    global _memory_provider
    _memory_provider = provider


async def _store_graph_context(session_id: str, key: str, value: Any) -> None:
    if _memory_provider is None:
        return
    try:
        await _memory_provider.store(
            session_id=session_id,
            key=key,
            value=value,
            memory_type="context",
            importance=7,
        )
    except Exception:
        pass


async def _recall_graph_context(session_id: str, query: str) -> List[Dict[str, Any]]:
    if _memory_provider is None:
        return []
    try:
        return await _memory_provider.recall(
            session_id=session_id,
            query=query,
            limit=10,
        )
    except Exception:
        return []


def _audit_mutation(
    current_user: Optional[dict],
    action: str,
    entity_type: str,
    entity_id: str,
    details: str = "",
) -> None:
    if current_user is None:
        return
    try:
        log_audit(
            current_user=current_user,
            data=AuditLogCreate(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details,
            ),
        )
    except Exception:
        pass

ENTITY_REFERENCE_COLUMNS = {
    "shipment": [
        ("supplier_id", "supplier"),
        ("customer_id", "customer"),
        ("customs_declaration_id", "customs_declaration"),
    ],
    "invoice": [
        ("customer_id", "customer"),
        ("supplier_id", "supplier"),
        ("shipment_id", "shipment"),
    ],
    "customs_declaration": [
        ("shipment_id", "shipment"),
        ("hs_code_id", "hs_code"),
    ],
    "export_workflow": [
        ("customer_id", "customer"),
        ("supplier_id", "supplier"),
        ("invoice_id", "invoice"),
        ("customs_declaration_id", "customs_declaration"),
        ("shipment_id", "shipment"),
    ],
    "document": [],
}

REVERSE_ENTITY_REFERENCES = {
    "supplier": [
        ("shipments", "supplier_id"),
        ("invoices", "supplier_id"),
        ("export_workflows", "supplier_id"),
    ],
    "customer": [
        ("shipments", "customer_id"),
        ("invoices", "customer_id"),
        ("export_workflows", "customer_id"),
    ],
    "shipment": [
        ("invoices", "shipment_id"),
        ("customs_declarations", "shipment_id"),
        ("export_workflows", "shipment_id"),
    ],
    "invoice": [
        ("export_workflows", "invoice_id"),
    ],
    "customs_declaration": [
        ("shipments", "customs_declaration_id"),
        ("export_workflows", "customs_declaration_id"),
    ],
    "hs_code": [
        ("customs_declarations", "hs_code_id"),
    ],
}

ENTITY_NAME_QUERIES = {
    "customer": "SELECT name FROM customers WHERE id = ?",
    "supplier": "SELECT name FROM suppliers WHERE id = ?",
    "shipment": "SELECT tracking_number FROM shipments WHERE id = ?",
    "invoice": "SELECT invoice_number FROM invoices WHERE id = ?",
    "document": "SELECT title FROM documents WHERE id = ?",
    "resource": "SELECT title FROM resources WHERE id = ?",
    "hs_code": "SELECT code FROM hs_codes WHERE id = ?",
    "customs_declaration": "SELECT declaration_number FROM customs_declarations WHERE id = ?",
    "export_workflow": "SELECT workflow_number FROM export_workflows WHERE id = ?",
}

ENTITY_TABLES = {
    "customer": "customers",
    "supplier": "suppliers",
    "shipment": "shipments",
    "invoice": "invoices",
    "document": "documents",
    "resource": "resources",
    "hs_code": "hs_codes",
    "customs_declaration": "customs_declarations",
    "export_workflow": "export_workflows",
}


def _node_row_to_response(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "entity_type": row.get("entity_type"),
        "entity_id": row.get("entity_id"),
        "label": row.get("label"),
        "properties": parse_json(row.get("properties")),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
    }


def _edge_row_to_response(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "source_node_id": row.get("source_node_id"),
        "target_node_id": row.get("target_node_id"),
        "relationship_type": row.get("relationship_type"),
        "properties": parse_json(row.get("properties")),
        "created_at": row.get("created_at"),
        "created_by": row.get("created_by"),
    }


def _validate_node_id(node_id: str) -> None:
    if ":" not in node_id:
        raise ValueError("Invalid node id format")
    entity_type, _, entity_id_str = node_id.partition(":")
    if entity_type not in SUPPORTED_NODE_TYPES:
        raise ValueError(f"Unsupported entity type: {entity_type}")
    if not entity_id_str.isdigit():
        raise ValueError("Invalid entity id")


def _validate_entity_type(entity_type: str) -> None:
    if entity_type not in SUPPORTED_NODE_TYPES:
        raise ValueError(f"Unsupported entity type: {entity_type}")


def create_node(data: KnowledgeGraphNodeCreate, current_user: Optional[dict] = None) -> dict:
    _validate_entity_type(data.entity_type)
    node_id = f"{data.entity_type}:{data.entity_id}"
    now = now_iso()
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO knowledge_nodes (id, entity_type, entity_id, label, properties, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                node_id,
                data.entity_type,
                data.entity_id,
                data.label,
                dumps_json(data.properties),
                now,
                now,
            ),
        )
        conn.commit()
    _audit_mutation(current_user, "create", "knowledge_graph", node_id, f"Node {node_id} created")
    return {"id": node_id, "message": "Node created successfully"}


def get_node(node_id: str) -> dict:
    _validate_node_id(node_id)
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM knowledge_nodes WHERE id = ?", (node_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Node not found")
        return _node_row_to_response(dict(row))


def update_node(node_id: str, data: KnowledgeGraphNodeCreate, current_user: Optional[dict] = None) -> dict:
    _validate_node_id(node_id)
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM knowledge_nodes WHERE id = ?", (node_id,))
        if not cursor.fetchone():
            raise ValueError("Node not found")
        now = now_iso()
        cursor.execute(
            """UPDATE knowledge_nodes SET label = ?, properties = ?, updated_at = ? WHERE id = ?""",
            (data.label, dumps_json(data.properties), now, node_id),
        )
        conn.commit()
    _audit_mutation(current_user, "update", "knowledge_graph", node_id, f"Node {node_id} updated")
    return {"id": node_id, "message": "Node updated successfully"}


def delete_node(node_id: str, current_user: Optional[dict] = None) -> dict:
    _validate_node_id(node_id)
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM knowledge_nodes WHERE id = ?", (node_id,))
        if not cursor.fetchone():
            raise ValueError("Node not found")
        cursor.execute("DELETE FROM knowledge_edges WHERE source_node_id = ? OR target_node_id = ?", (node_id, node_id))
        cursor.execute("DELETE FROM knowledge_nodes WHERE id = ?", (node_id,))
        conn.commit()
    _audit_mutation(current_user, "delete", "knowledge_graph", node_id, f"Node {node_id} deleted")
    return {"id": node_id, "message": "Node deleted successfully"}


def create_edge(data: KnowledgeGraphEdgeCreate, current_user: Optional[dict] = None) -> dict:
    edge_id = str(uuid.uuid4().hex)
    now = now_iso()
    created_by = current_user.get("id") if current_user else None
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM knowledge_nodes WHERE id = ?", (data.source_node_id,))
        if not cursor.fetchone():
            raise ValueError("Source node not found")
        cursor.execute("SELECT id FROM knowledge_nodes WHERE id = ?", (data.target_node_id,))
        if not cursor.fetchone():
            raise ValueError("Target node not found")
        cursor.execute(
            """INSERT INTO knowledge_edges (id, source_node_id, target_node_id, relationship_type, properties, created_at, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                edge_id,
                data.source_node_id,
                data.target_node_id,
                data.relationship_type,
                dumps_json(data.properties),
                now,
                created_by,
            ),
        )
        conn.commit()
    _audit_mutation(current_user, "create", "knowledge_graph", edge_id, f"Edge {edge_id} created")
    return {"id": edge_id, "message": "Edge created successfully"}


def get_edge(edge_id: str) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM knowledge_edges WHERE id = ?", (edge_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError("Edge not found")
        return _edge_row_to_response(dict(row))


def delete_edge(edge_id: str, current_user: Optional[dict] = None) -> dict:
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM knowledge_edges WHERE id = ?", (edge_id,))
        if not cursor.fetchone():
            raise ValueError("Edge not found")
        cursor.execute("DELETE FROM knowledge_edges WHERE id = ?", (edge_id,))
        conn.commit()
    _audit_mutation(current_user, "delete", "knowledge_graph", edge_id, f"Edge {edge_id} deleted")
    return {"id": edge_id, "message": "Edge deleted successfully"}


def search_nodes(query: str, entity_type: Optional[str] = None, skip: int = 0, limit: int = 100) -> list[dict]:
    q = f"%{query}%"
    with connection() as conn:
        cursor = conn.cursor()
        sql = "SELECT * FROM knowledge_nodes WHERE label LIKE ?"
        params: list[Any] = [q]
        if entity_type:
            sql += " AND entity_type = ?"
            params.append(entity_type)
        sql += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, skip])
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [_node_row_to_response(dict(r)) for r in rows]


def list_edges_for_node(node_id: str) -> list[dict]:
    _validate_node_id(node_id)
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM knowledge_edges WHERE source_node_id = ? OR target_node_id = ?",
            (node_id, node_id),
        )
        rows = cursor.fetchall()
        return [_edge_row_to_response(dict(r)) for r in rows]


def _derive_edges_from_entity(entity_type: str, entity_id: int) -> List[Dict[str, Any]]:
    _validate_entity_type(entity_type)
    edges: List[Dict[str, Any]] = []
    source_node_id = f"{entity_type}:{entity_id}"

    with connection() as conn:
        cursor = conn.cursor()

        if entity_type in ENTITY_REFERENCE_COLUMNS:
            table = ENTITY_TABLES[entity_type]
            for column_name, target_type in ENTITY_REFERENCE_COLUMNS[entity_type]:
                cursor.execute(
                    f"SELECT id, {column_name} FROM {table} WHERE id = ?",
                    (entity_id,),
                )
                row = cursor.fetchone()
                if row and row[1] is not None:
                    target_id = row[1]
                    target_node_id = f"{target_type}:{target_id}"
                    edges.append({
                        "id": f"derived:{source_node_id}:{target_node_id}:references_{target_type}",
                        "source_node_id": source_node_id,
                        "target_node_id": target_node_id,
                        "relationship_type": f"references_{target_type}",
                        "properties": {"derived": True, "source_column": column_name},
                        "created_at": "1970-01-01T00:00:00",
                        "derived": True,
                    })

        if entity_type == "document":
            cursor.execute(
                "SELECT entity_type, entity_id FROM documents WHERE id = ?",
                (entity_id,),
            )
            row = cursor.fetchone()
            if row and row[0] is not None and row[1] is not None:
                target_entity_type = row[0]
                target_entity_id = row[1]
                if target_entity_type in SUPPORTED_NODE_TYPES:
                    target_node_id = f"{target_entity_type}:{target_entity_id}"
                    edges.append({
                        "id": f"derived:{source_node_id}:{target_node_id}:references_{target_entity_type}",
                        "source_node_id": source_node_id,
                        "target_node_id": target_node_id,
                        "relationship_type": f"references_{target_entity_type}",
                        "properties": {"derived": True, "source_column": "entity_type/entity_id"},
                        "created_at": "1970-01-01T00:00:00",
                        "derived": True,
                    })

        if entity_type in REVERSE_ENTITY_REFERENCES:
            for table, column_name in REVERSE_ENTITY_REFERENCES[entity_type]:
                cursor.execute(
                    f"SELECT id FROM {table} WHERE {column_name} = ?",
                    (entity_id,),
                )
                rows = cursor.fetchall()
                for row in rows:
                    source_node_id = f"{table.rstrip('s')}:{row[0]}"
                    edges.append({
                        "id": f"derived:{source_node_id}:{entity_type}:{entity_id}:references_{entity_type}",
                        "source_node_id": source_node_id,
                        "target_node_id": f"{entity_type}:{entity_id}",
                        "relationship_type": f"references_{entity_type}",
                        "properties": {"derived": True, "source_column": column_name},
                        "created_at": "1970-01-01T00:00:00",
                        "derived": True,
                    })

    return edges


def traverse(entity_type: str, entity_id: int, depth: int = 1, direction: str = "both") -> Dict[str, Any]:
    _validate_entity_type(entity_type)
    if depth < 1:
        raise ValueError("Depth must be at least 1")

    start_node_id = f"{entity_type}:{entity_id}"
    visited = {start_node_id}
    result_nodes: List[Dict[str, Any]] = []
    result_edges: List[Dict[str, Any]] = []
    queue = [(start_node_id, 0)]

    while queue:
        current_id, current_depth = queue.pop(0)
        if current_depth > depth:
            continue

        try:
            node = get_node(current_id)
            result_nodes.append(node)
        except ValueError:
            continue

        explicit_edges = list_edges_for_node(current_id)
        derived_edges = _derive_edges_from_entity(
            current_id.split(":")[0],
            int(current_id.split(":")[1]),
        )

        all_edges = explicit_edges + derived_edges
        seen_edge_ids = {e.get("id") for e in result_edges if e.get("id")}
        for edge in all_edges:
            edge_id = edge.get("id")
            if edge_id and edge_id in seen_edge_ids:
                continue
            result_edges.append(edge)
            if edge_id:
                seen_edge_ids.add(edge_id)

            if current_depth < depth:
                neighbor = edge["target_node_id"] if edge["source_node_id"] == current_id else edge["source_node_id"]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, current_depth + 1))

    return {
        "nodes": result_nodes,
        "edges": result_edges,
        "depth": min(depth, current_depth if queue else depth),
    }


def _get_entity_name(entity_type: str, entity_id: int) -> Optional[str]:
    query = ENTITY_NAME_QUERIES.get(entity_type)
    if not query:
        return None
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (entity_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
    return None


def _sync_entity(entity_type: str, entity_id: int) -> dict:
    _validate_entity_type(entity_type)
    node_id = f"{entity_type}:{entity_id}"
    label = _get_entity_name(entity_type, entity_id)
    properties = {"entity_type": entity_type, "entity_id": entity_id}
    if label:
        properties["name"] = label

    now = now_iso()
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM knowledge_nodes WHERE id = ?", (node_id,))
        if cursor.fetchone():
            cursor.execute(
                """UPDATE knowledge_nodes SET label = ?, properties = ?, updated_at = ? WHERE id = ?""",
                (label, dumps_json(properties), now, node_id),
            )
            conn.commit()
            return {"id": node_id, "message": "Node synced successfully", "action": "updated"}
        else:
            cursor.execute(
                """INSERT INTO knowledge_nodes (id, entity_type, entity_id, label, properties, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    node_id,
                    entity_type,
                    entity_id,
                    label,
                    dumps_json(properties),
                    now,
                    now,
                ),
            )
            conn.commit()
            return {"id": node_id, "message": "Node synced successfully", "action": "created"}


def sync_entity(entity_type: str, entity_id: int) -> dict:
    return _sync_entity(entity_type, entity_id)


def sync_all() -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    with connection() as conn:
        cursor = conn.cursor()
        for entity_type, table in ENTITY_TABLES.items():
            cursor.execute(f"SELECT id FROM {table}")
            rows = cursor.fetchall()
            for row in rows:
                result = _sync_entity(entity_type, row[0])
                results.append(result)
    return {"synced": len(results), "results": results}
