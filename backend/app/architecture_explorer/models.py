from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class CanonicalNode:
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
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "technical_name": self.technical_name,
            "arabic_meaning": self.arabic_meaning,
            "type": self.type,
            "levels": self.levels,
            "status": self.status,
            "paths": self.paths,
            "responsibilities": self.responsibilities,
            "non_responsibilities": self.non_responsibilities,
            "evidence": self.evidence,
            "parent_ids": self.parent_ids,
            "tags": self.tags,
            "metadata": self.metadata,
        }


@dataclass
class CanonicalEdge:
    id: str
    source: str
    target: str
    relation_type: str
    direction: str
    status: str
    evidence: List[str]
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "relation_type": self.relation_type,
            "direction": self.direction,
            "status": self.status,
            "evidence": self.evidence,
            "data": self.data,
            "metadata": self.metadata,
        }


@dataclass
class CanonicalGraph:
    artifact: str
    version: str
    purpose: str
    governing_principle: str
    source: Dict[str, Any]
    levels: List[Dict[str, Any]]
    nodes: List[CanonicalNode]
    edges: List[CanonicalEdge]
    agent_runtime_path: Dict[str, Any]
    classification_rules: Dict[str, Any]
    graph_contract: Dict[str, Any]
    validation: Dict[str, Any]
    next_work: str

    def get_node(self, node_id: str) -> Optional[CanonicalNode]:
        for node in self.nodes:
            if node.id == node_id:
                return node
        return None

    def get_edges(
        self,
        *,
        source: Optional[str] = None,
        target: Optional[str] = None,
        relation_type: Optional[str] = None,
        direction: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[CanonicalEdge]:
        results = []
        for edge in self.edges:
            if source is not None and edge.source != source:
                continue
            if target is not None and edge.target != target:
                continue
            if relation_type is not None and edge.relation_type != relation_type:
                continue
            if direction is not None and edge.direction != direction:
                continue
            if status is not None and edge.status != status:
                continue
            results.append(edge)
        return results

    def get_children(self, node_id: str) -> List[CanonicalNode]:
        children = []
        for edge in self.edges:
            if edge.source == node_id and edge.direction == "outbound":
                child = self.get_node(edge.target)
                if child:
                    children.append(child)
        return children

    def get_parents(self, node_id: str) -> List[CanonicalNode]:
        parents = []
        for edge in self.edges:
            if edge.target == node_id and edge.direction == "outbound":
                parent = self.get_node(edge.source)
                if parent:
                    parents.append(parent)
        return parents

    def get_level_nodes(self, level: int) -> List[CanonicalNode]:
        return [node for node in self.nodes if level in node.levels]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "artifact": self.artifact,
            "version": self.version,
            "purpose": self.purpose,
            "governing_principle": self.governing_principle,
            "source": self.source,
            "levels": self.levels,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "agent_runtime_path": self.agent_runtime_path,
            "classification_rules": self.classification_rules,
            "graph_contract": self.graph_contract,
            "validation": self.validation,
            "next_work": self.next_work,
        }


@dataclass
class NodeQuery:
    node_id: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    level: Optional[int] = None
    tag: Optional[str] = None
    parent_id: Optional[str] = None
    search_text: Optional[str] = None


@dataclass
class EdgeQuery:
    edge_id: Optional[str] = None
    source: Optional[str] = None
    target: Optional[str] = None
    relation_type: Optional[str] = None
    direction: Optional[str] = None
    status: Optional[str] = None


@dataclass
class TraversalResult:
    start_node: CanonicalNode
    path: List[CanonicalNode]
    edges: List[CanonicalEdge]
    depth: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start_node_id": self.start_node.id,
            "path": [node.id for node in self.path],
            "edges": [edge.to_dict() for edge in self.edges],
            "depth": self.depth,
        }


@dataclass
class SearchResult:
    query: str
    matches: List[CanonicalNode]
    total: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "total": self.total,
            "matches": [node.to_dict() for node in self.matches],
        }


@dataclass
class LevelProjection:
    level: int
    nodes: List[CanonicalNode]
    edges: List[CanonicalEdge]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }
