from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class NodeQuerySchema(BaseModel):
    node_id: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    level: Optional[int] = None
    tag: Optional[str] = None
    parent_id: Optional[str] = None
    search_text: Optional[str] = None


class EdgeQuerySchema(BaseModel):
    edge_id: Optional[str] = None
    source: Optional[str] = None
    target: Optional[str] = None
    relation_type: Optional[str] = None
    direction: Optional[str] = None
    status: Optional[str] = None


class TraversalRequestSchema(BaseModel):
    direction: str = "outbound"
    max_depth: int = 3
    relation_filter: Optional[str] = None


class NodeResponseSchema(BaseModel):
    id: str
    technical_name: str
    arabic_meaning: str
    type: str
    levels: List[int]
    status: str
    paths: List[str]
    responsibilities: List[str]
    non_responsibilities: List[str]
    evidence: List[str]
    parent_ids: List[str]
    tags: List[str]
    metadata: Dict[str, Any]


class EdgeResponseSchema(BaseModel):
    id: str
    source: str
    target: str
    relation_type: str
    direction: str
    status: str
    evidence: List[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any]


class TraversalResponseSchema(BaseModel):
    start_node_id: str
    path: List[str]
    edges: List[EdgeResponseSchema]
    depth: int


class SearchResponseSchema(BaseModel):
    query: str
    total: int
    matches: List[NodeResponseSchema]


class LevelProjectionResponseSchema(BaseModel):
    level: int
    nodes: List[NodeResponseSchema]
    edges: List[EdgeResponseSchema]


class EvidenceResponseSchema(BaseModel):
    node: NodeResponseSchema
    evidence_paths: List[str]
    supporting_edges: List[EdgeResponseSchema]


class ArtifactMetadataResponseSchema(BaseModel):
    artifact: str
    version: str
    purpose: str
    governing_principle: str
    source: Dict[str, Any]
    levels: List[Dict[str, Any]]
    next_work: str
