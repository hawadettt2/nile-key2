from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import sqlite3

from app.routers.auth import get_current_user, require_role
from app.schemas.knowledge_graph import (
    KnowledgeGraphNode,
    KnowledgeGraphNodeCreate,
    KnowledgeGraphEdge,
    KnowledgeGraphEdgeCreate,
    KnowledgeGraphRelationships,
    KnowledgeGraphTraversal,
    SyncResult,
)
from app.schemas.common import MessageResponse
from app.services.knowledge_graph import (
    get_node as _get_node,
    create_node as _create_node,
    update_node as _update_node,
    delete_node as _delete_node,
    create_edge as _create_edge,
    delete_edge as _delete_edge,
    list_edges_for_node as _list_edges_for_node,
    _derive_edges_from_entity,
    traverse as _traverse,
    search_nodes as _search_nodes,
    sync_all as _sync_all,
    get_edge as _get_edge,
)

router = APIRouter(prefix="/api/v1/knowledge-graph", tags=["Knowledge Graph"])


@router.get("/nodes/{entity_type}/{entity_id}", response_model=KnowledgeGraphNode)
def get_graph_node(entity_type: str, entity_id: int, current_user: dict = Depends(get_current_user)):
    try:
        node_id = f"{entity_type}:{entity_id}"
        return _get_node(node_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/nodes", response_model=KnowledgeGraphNode)
def upsert_graph_node(data: KnowledgeGraphNodeCreate, current_user: dict = Depends(require_role(["owner", "manager"]))):
    node_id = f"{data.entity_type}:{data.entity_id}"
    try:
        _get_node(node_id)
        result = _update_node(node_id=node_id, data=data, current_user=current_user)
    except ValueError as exc:
        err_msg = str(exc)
        if "Unsupported entity type" in err_msg or "Invalid node id format" in err_msg or "Invalid entity id" in err_msg:
            raise HTTPException(status_code=400, detail=err_msg)
        result = _create_node(data=data, current_user=current_user)
    return _get_node(result["id"])


@router.delete("/nodes/{entity_type}/{entity_id}", response_model=MessageResponse)
def delete_graph_node(entity_type: str, entity_id: int, current_user: dict = Depends(require_role(["owner", "manager"]))):
    try:
        node_id = f"{entity_type}:{entity_id}"
        return _delete_node(node_id=node_id, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Node not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.get("/nodes/{entity_type}/{entity_id}/relationships", response_model=KnowledgeGraphRelationships)
def get_node_relationships(entity_type: str, entity_id: int, current_user: dict = Depends(get_current_user)):
    try:
        node_id = f"{entity_type}:{entity_id}"
        node = _get_node(node_id)
        explicit_edges = _list_edges_for_node(node_id)
        derived_edges = _derive_edges_from_entity(entity_type, entity_id)
        all_edges = explicit_edges + derived_edges
        seen_ids = set()
        unique_edges = []
        for edge in all_edges:
            edge_id = edge.get("id")
            if edge_id and edge_id in seen_ids:
                continue
            unique_edges.append(edge)
            if edge_id:
                seen_ids.add(edge_id)
        return {"node": node, "relationships": unique_edges}
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/edges", response_model=KnowledgeGraphEdge)
def create_graph_edge(data: KnowledgeGraphEdgeCreate, current_user: dict = Depends(require_role(["owner", "manager"]))):
    try:
        result = _create_edge(data=data, current_user=current_user)
        return _get_edge(result["id"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.delete("/edges/{edge_id}", response_model=MessageResponse)
def delete_graph_edge(edge_id: str, current_user: dict = Depends(require_role(["owner", "manager"]))):
    try:
        return _delete_edge(edge_id=edge_id, current_user=current_user)
    except ValueError as exc:
        if str(exc) == "Edge not found":
            raise HTTPException(status_code=404, detail=str(exc))
        raise


@router.get("/traverse/{entity_type}/{entity_id}", response_model=KnowledgeGraphTraversal)
def traverse_graph(entity_type: str, entity_id: int, depth: int = Query(1, ge=1), direction: str = Query("both"), current_user: dict = Depends(get_current_user)):
    try:
        result = _traverse(entity_type=entity_type, entity_id=entity_id, depth=depth, direction=direction)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/search", response_model=list[KnowledgeGraphNode])
def search_graph_nodes(query: str = Query(..., min_length=1), entity_type: Optional[str] = None, skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), current_user: dict = Depends(get_current_user)):
    return _search_nodes(query=query, entity_type=entity_type, skip=skip, limit=limit)


@router.post("/sync", response_model=SyncResult)
def sync_graph(current_user: dict = Depends(require_role(["owner", "manager"]))):
    try:
        result = _sync_all()
        return SyncResult(synced_nodes=result.get("synced", 0), synced_edges=0, errors=[])
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
