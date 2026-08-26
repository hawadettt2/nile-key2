from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from .loader import CanonicalGraphLoader, CanonicalGraphLoadError, CanonicalGraphValidationError
from .models import (
    CanonicalGraph,
    CanonicalNode,
    CanonicalEdge,
    EdgeQuery,
    LevelProjection,
    NodeQuery,
    SearchResult,
    TraversalResult,
)


class ExplorerEngineError(Exception):
    """Base explorer engine error."""


class NodeNotFoundError(ExplorerEngineError):
    """Raised when a requested node does not exist."""


class ArchitectureExplorerEngine:
    def __init__(self, graph_path: Optional[str] = None) -> None:
        if graph_path is None:
            graph_path = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "الخريطة المعمارية الكاملة" / "ARCHITECTURE_EXPLORER_V2_CANONICAL_GRAPH.json"
        else:
            graph_path = Path(graph_path)
        self._loader = CanonicalGraphLoader(graph_path)
        self._graph: Optional[CanonicalGraph] = None

    def load(self) -> CanonicalGraph:
        self._graph = self._loader.load()
        return self._graph

    @property
    def graph(self) -> CanonicalGraph:
        if self._graph is None:
            raise ExplorerEngineError("Graph not loaded. Call load() first.")
        return self._graph

    def get_node(self, node_id: str) -> CanonicalNode:
        node = self.graph.get_node(node_id)
        if node is None:
            raise NodeNotFoundError(f"Node not found: {node_id}")
        return node

    def get_node_evidence(self, node_id: str) -> List[str]:
        return self.get_node(node_id).evidence

    def get_edge_evidence(self, edge_id: str) -> List[str]:
        for edge in self.graph.edges:
            if edge.id == edge_id:
                return edge.evidence
        raise ExplorerEngineError(f"Edge not found: {edge_id}")

    def query_nodes(self, query: NodeQuery) -> List[CanonicalNode]:
        results = []
        for node in self.graph.nodes:
            if query.node_id is not None and node.id != query.node_id:
                continue
            if query.type is not None and node.type != query.type:
                continue
            if query.status is not None and node.status != query.status:
                continue
            if query.level is not None and query.level not in node.levels:
                continue
            if query.tag is not None and query.tag not in node.tags:
                continue
            if query.parent_id is not None and query.parent_id not in node.parent_ids:
                continue
            if query.search_text is not None:
                haystack = " ".join([
                    node.technical_name,
                    node.arabic_meaning,
                    node.type,
                    " ".join(node.tags),
                    " ".join(node.responsibilities),
                    " ".join(node.non_responsibilities),
                ]).lower()
                if query.search_text.lower() not in haystack:
                    continue
            results.append(node)
        return results

    def query_edges(self, query: EdgeQuery) -> List[CanonicalEdge]:
        return self.graph.get_edges(
            source=query.source,
            target=query.target,
            relation_type=query.relation_type,
            direction=query.direction,
            status=query.status,
        )

    def get_children(self, node_id: str) -> List[CanonicalNode]:
        return self.graph.get_children(node_id)

    def get_parents(self, node_id: str) -> List[CanonicalNode]:
        return self.graph.get_parents(node_id)

    def traverse(
        self,
        start_node_id: str,
        direction: str = "outbound",
        max_depth: int = 3,
        relation_filter: Optional[str] = None,
    ) -> List[TraversalResult]:
        if max_depth < 1:
            return []

        start_node = self.get_node(start_node_id)
        results: List[TraversalResult] = []

        def _walk(current_id: str, current_path: List[str], current_edges: List[CanonicalEdge], depth: int) -> None:
            if depth > max_depth:
                return

            matched_edges = []
            for edge in self.graph.edges:
                if direction == "outbound" and edge.source == current_id:
                    if relation_filter is None or edge.relation_type == relation_filter:
                        matched_edges.append(edge)
                elif direction == "inbound" and edge.target == current_id:
                    if relation_filter is None or edge.relation_type == relation_filter:
                        matched_edges.append(edge)

            if not matched_edges:
                if len(current_path) > 1:
                    path_nodes = [self.get_node(nid) for nid in current_path]
                    results.append(
                        TraversalResult(
                            start_node=start_node,
                            path=path_nodes,
                            edges=list(current_edges),
                            depth=len(current_path) - 1,
                        )
                    )
                return

            for edge in matched_edges:
                next_id = edge.target if direction == "outbound" else edge.source
                if next_id in current_path:
                    continue
                new_path = current_path + [next_id]
                new_edges = current_edges + [edge]
                _walk(next_id, new_path, new_edges, depth + 1)

        _walk(start_node_id, [start_node_id], [], 0)
        return results

    def search(self, query_text: str, limit: Optional[int] = None) -> SearchResult:
        matches = []
        query_text_lower = query_text.lower()
        for node in self.graph.nodes:
            haystack = " ".join([
                node.technical_name,
                node.arabic_meaning,
                node.type,
                " ".join(node.tags),
                " ".join(node.responsibilities),
                " ".join(node.non_responsibilities),
                " ".join(node.paths),
                " ".join(node.evidence),
            ]).lower()
            if query_text_lower in haystack:
                matches.append(node)
        if limit is not None:
            matches = matches[:limit]
        return SearchResult(query=query_text, matches=matches, total=len(matches))

    def project_level(self, level: int) -> LevelProjection:
        nodes = self.graph.get_level_nodes(level)
        node_ids = {node.id for node in nodes}
        edges = [
            edge for edge in self.graph.edges
            if edge.source in node_ids or edge.target in node_ids
        ]
        return LevelProjection(level=level, nodes=nodes, edges=edges)

    def resolve_evidence(self, node_id: str) -> Dict[str, Any]:
        node = self.get_node(node_id)
        supporting_edges = self.graph.get_edges(source=node_id) + self.graph.get_edges(target=node_id)
        return {
            "node": node.to_dict(),
            "evidence_paths": node.evidence,
            "supporting_edges": [edge.to_dict() for edge in supporting_edges],
        }

    def get_agent_runtime_path(self) -> List[str]:
        return list(self.graph.agent_runtime_path.get("sequence", []))

    def get_classification_rules(self) -> Dict[str, Any]:
        return dict(self.graph.classification_rules)

    def get_graph_contract(self) -> Dict[str, Any]:
        return dict(self.graph.graph_contract)

    def get_validation_state(self) -> Dict[str, Any]:
        return dict(self.graph.validation)

    def get_artifact_metadata(self) -> Dict[str, Any]:
        return {
            "artifact": self.graph.artifact,
            "version": self.graph.version,
            "purpose": self.graph.purpose,
            "governing_principle": self.graph.governing_principle,
            "source": self.graph.source,
            "levels": self.graph.levels,
            "next_work": self.graph.next_work,
        }

    def to_dict(self) -> Dict[str, Any]:
        return self.graph.to_dict()
