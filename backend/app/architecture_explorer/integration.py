from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.architecture_explorer.engine import (
    ArchitectureExplorerEngine,
    ExplorerEngineError,
    NodeNotFoundError,
)
from app.architecture_explorer.exceptions import GraphNotLoadedError
from app.architecture_explorer.models import (
    CanonicalEdge,
    CanonicalNode,
    EdgeQuery,
    LevelProjection,
    NodeQuery,
    SearchResult,
    TraversalResult,
)
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


class ExplorerIntegrationError(Exception):
    """Raised when the Explorer API integration fails."""


class ArchitectureExplorerIntegration:
    def __init__(self, graph_path: Optional[str] = None) -> None:
        self._engine = ArchitectureExplorerEngine(graph_path)

    def load(self) -> None:
        try:
            self._engine.load()
        except ExplorerEngineError as exc:
            raise ExplorerIntegrationError(str(exc)) from exc

    def _node_to_response(self, node: CanonicalNode) -> NodeResponseSchema:
        return NodeResponseSchema(
            id=node.id,
            technical_name=node.technical_name,
            arabic_meaning=node.arabic_meaning,
            type=node.type,
            levels=node.levels,
            status=node.status,
            paths=node.paths,
            responsibilities=node.responsibilities,
            non_responsibilities=node.non_responsibilities,
            evidence=node.evidence,
            parent_ids=node.parent_ids,
            tags=node.tags,
            metadata=node.metadata,
        )

    def _edge_to_response(self, edge: CanonicalEdge) -> EdgeResponseSchema:
        return EdgeResponseSchema(
            id=edge.id,
            source=edge.source,
            target=edge.target,
            relation_type=edge.relation_type,
            direction=edge.direction,
            status=edge.status,
            evidence=edge.evidence,
            data=edge.data,
            metadata=edge.metadata,
        )

    def _traversal_to_response(self, result: TraversalResult) -> TraversalResponseSchema:
        return TraversalResponseSchema(
            start_node_id=result.start_node.id,
            path=[node.id for node in result.path],
            edges=[self._edge_to_response(edge) for edge in result.edges],
            depth=result.depth,
        )

    def get_node(self, node_id: str) -> NodeResponseSchema:
        try:
            node = self._engine.get_node(node_id)
        except NodeNotFoundError as exc:
            raise ExplorerIntegrationError(str(exc)) from exc
        return self._node_to_response(node)

    def get_children(self, node_id: str) -> List[NodeResponseSchema]:
        try:
            children = self._engine.get_children(node_id)
        except NodeNotFoundError as exc:
            raise ExplorerIntegrationError(str(exc)) from exc
        return [self._node_to_response(child) for child in children]

    def get_parents(self, node_id: str) -> List[NodeResponseSchema]:
        try:
            parents = self._engine.get_parents(node_id)
        except NodeNotFoundError as exc:
            raise ExplorerIntegrationError(str(exc)) from exc
        return [self._node_to_response(parent) for parent in parents]

    def query_nodes(self, query: NodeQuerySchema) -> List[NodeResponseSchema]:
        try:
            engine_query = NodeQuery(
                node_id=query.node_id,
                type=query.type,
                status=query.status,
                level=query.level,
                tag=query.tag,
                parent_id=query.parent_id,
                search_text=query.search_text,
            )
            nodes = self._engine.query_nodes(engine_query)
        except ExplorerEngineError as exc:
            raise ExplorerIntegrationError(str(exc)) from exc
        return [self._node_to_response(node) for node in nodes]

    def query_edges(self, query: EdgeQuerySchema) -> List[EdgeResponseSchema]:
        try:
            engine_query = EdgeQuery(
                edge_id=query.edge_id,
                source=query.source,
                target=query.target,
                relation_type=query.relation_type,
                direction=query.direction,
                status=query.status,
            )
            edges = self._engine.query_edges(engine_query)
        except ExplorerEngineError as exc:
            raise ExplorerIntegrationError(str(exc)) from exc
        return [self._edge_to_response(edge) for edge in edges]

    def traverse(
        self,
        start_node_id: str,
        request: TraversalRequestSchema,
    ) -> List[TraversalResponseSchema]:
        try:
            results = self._engine.traverse(
                start_node_id=start_node_id,
                direction=request.direction,
                max_depth=request.max_depth,
                relation_filter=request.relation_filter,
            )
        except (NodeNotFoundError, ExplorerEngineError) as exc:
            raise ExplorerIntegrationError(str(exc)) from exc
        return [self._traversal_to_response(result) for result in results]

    def search(self, query_text: str, limit: Optional[int] = None) -> SearchResponseSchema:
        try:
            result = self._engine.search(query_text, limit=limit)
        except ExplorerEngineError as exc:
            raise ExplorerIntegrationError(str(exc)) from exc
        return SearchResponseSchema(
            query=result.query,
            total=result.total,
            matches=[self._node_to_response(node) for node in result.matches],
        )

    def project_level(self, level: int) -> LevelProjectionResponseSchema:
        try:
            projection = self._engine.project_level(level)
        except ExplorerEngineError as exc:
            raise ExplorerIntegrationError(str(exc)) from exc
        return LevelProjectionResponseSchema(
            level=projection.level,
            nodes=[self._node_to_response(node) for node in projection.nodes],
            edges=[self._edge_to_response(edge) for edge in projection.edges],
        )

    def resolve_evidence(self, node_id: str) -> EvidenceResponseSchema:
        try:
            evidence = self._engine.resolve_evidence(node_id)
        except (NodeNotFoundError, ExplorerEngineError) as exc:
            raise ExplorerIntegrationError(str(exc)) from exc
        return EvidenceResponseSchema(
            node=self._node_to_response(evidence["node"]),
            evidence_paths=evidence["evidence_paths"],
            supporting_edges=[self._edge_to_response(edge) for edge in evidence["supporting_edges"]],
        )

    def get_artifact_metadata(self) -> ArtifactMetadataResponseSchema:
        try:
            metadata = self._engine.get_artifact_metadata()
        except ExplorerEngineError as exc:
            raise ExplorerIntegrationError(str(exc)) from exc
        return ArtifactMetadataResponseSchema(**metadata)
