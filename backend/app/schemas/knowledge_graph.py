from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, List, Dict


class KnowledgeGraphNode(BaseModel):
    id: str
    entity_type: str
    entity_id: int
    label: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class KnowledgeGraphNodeCreate(BaseModel):
    entity_type: str
    entity_id: int
    label: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class KnowledgeGraphEdge(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    properties: Optional[Dict[str, Any]] = None
    created_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True


class KnowledgeGraphEdgeCreate(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship_type: str
    properties: Optional[Dict[str, Any]] = None


class KnowledgeGraphRelationships(BaseModel):
    node: KnowledgeGraphNode
    relationships: List[KnowledgeGraphEdge]


class KnowledgeGraphTraversal(BaseModel):
    nodes: List[KnowledgeGraphNode]
    edges: List[KnowledgeGraphEdge]
    depth: int


class SyncResult(BaseModel):
    synced_nodes: int
    synced_edges: int
    errors: List[str] = []
