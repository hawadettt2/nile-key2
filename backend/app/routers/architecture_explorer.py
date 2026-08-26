from fastapi import APIRouter, HTTPException

from app.architecture_explorer.integration import ArchitectureExplorerIntegration
from app.schemas.architecture_explorer import (
    ArtifactMetadataResponseSchema,
    EdgeQuerySchema,
    EdgeResponseSchema,
    EvidenceResponseSchema,
    LevelProjectionResponseSchema,
    NodeQuerySchema,
    NodeResponseSchema,
    SearchResponseSchema,
    TraversalRequestSchema,
    TraversalResponseSchema,
)


router = APIRouter(prefix="/api/v1/architecture-explorer", tags=["architecture-explorer"])

integration = ArchitectureExplorerIntegration()


@router.get("/health")
def health():
    return {"status": "healthy", "component": "architecture-explorer"}


@router.get("/metadata", response_model=ArtifactMetadataResponseSchema)
def get_metadata():
    try:
        integration.load()
        return integration.get_artifact_metadata()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/nodes/{node_id}", response_model=NodeResponseSchema)
def get_node(node_id: str):
    try:
        integration.load()
        return integration.get_node(node_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/nodes", response_model=list[NodeResponseSchema])
def list_nodes(
    node_id: str | None = None,
    type: str | None = None,
    status: str | None = None,
    level: int | None = None,
    tag: str | None = None,
    parent_id: str | None = None,
    search_text: str | None = None,
):
    try:
        integration.load()
        return integration.query_nodes(
            NodeQuerySchema(
                node_id=node_id,
                type=type,
                status=status,
                level=level,
                tag=tag,
                parent_id=parent_id,
                search_text=search_text,
            )
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/nodes/query", response_model=list[NodeResponseSchema])
def query_nodes(payload: NodeQuerySchema):
    try:
        integration.load()
        return integration.query_nodes(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/nodes/{node_id}/children", response_model=list[NodeResponseSchema])
def get_children(node_id: str):
    try:
        integration.load()
        return integration.get_children(node_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/nodes/{node_id}/parents", response_model=list[NodeResponseSchema])
def get_parents(node_id: str):
    try:
        integration.load()
        return integration.get_parents(node_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/edges/query", response_model=list[EdgeResponseSchema])
def query_edges(payload: EdgeQuerySchema):
    try:
        integration.load()
        return integration.query_edges(payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/traverse/{start_node_id}", response_model=list[TraversalResponseSchema])
def traverse(start_node_id: str, request: TraversalRequestSchema):
    try:
        integration.load()
        return integration.traverse(start_node_id, request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/search", response_model=SearchResponseSchema)
def search(q: str, limit: int | None = None):
    try:
        integration.load()
        return integration.search(q, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/levels/{level}", response_model=LevelProjectionResponseSchema)
def project_level(level: int):
    try:
        integration.load()
        return integration.project_level(level)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/nodes/{node_id}/evidence", response_model=EvidenceResponseSchema)
def get_evidence(node_id: str):
    try:
        integration.load()
        return integration.resolve_evidence(node_id)
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
