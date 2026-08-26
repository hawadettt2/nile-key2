from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .models import (
    CanonicalEdge,
    CanonicalGraph,
    CanonicalNode,
)


class CanonicalGraphLoadError(Exception):
    """Raised when the canonical graph cannot be loaded."""


class CanonicalGraphValidationError(Exception):
    """Raised when the canonical graph fails runtime validation."""


class CanonicalGraphLoader:
    def __init__(self, graph_path: str | Path) -> None:
        self.graph_path = Path(graph_path)

    def load(self) -> CanonicalGraph:
        if not self.graph_path.exists():
            raise CanonicalGraphLoadError(
                f"Canonical graph file not found: {self.graph_path}"
            )

        with open(self.graph_path, "r", encoding="utf-8") as f:
            try:
                raw: Dict[str, Any] = json.load(f)
            except json.JSONDecodeError as exc:
                raise CanonicalGraphLoadError(
                    f"Canonical graph contains invalid JSON: {exc}"
                ) from exc

        self._validate_raw(raw)
        return self._build_graph(raw)

    def _validate_raw(self, raw: Dict[str, Any]) -> None:
        required_top_level = [
            "artifact",
            "version",
            "purpose",
            "governing_principle",
            "source",
            "levels",
            "nodes",
            "edges",
            "agent_runtime_path",
            "classification_rules",
            "graph_contract",
            "validation",
            "next_work",
        ]
        missing = [key for key in required_top_level if key not in raw]
        if missing:
            raise CanonicalGraphValidationError(
                f"Canonical graph missing required top-level keys: {missing}"
            )

        if not isinstance(raw["nodes"], list) or not raw["nodes"]:
            raise CanonicalGraphValidationError("Canonical graph must contain a non-empty nodes list.")

        if not isinstance(raw["edges"], list):
            raise CanonicalGraphValidationError("Canonical graph must contain an edges list.")

        node_ids = set()
        for node in raw["nodes"]:
            node_id = node.get("id")
            if not node_id:
                raise CanonicalGraphValidationError("Node missing id.")
            if node_id in node_ids:
                raise CanonicalGraphValidationError(f"Duplicate node id: {node_id}")
            node_ids.add(node_id)

        edge_ids = set()
        for edge in raw["edges"]:
            edge_id = edge.get("id")
            if not edge_id:
                raise CanonicalGraphValidationError("Edge missing id.")
            if edge_id in edge_ids:
                raise CanonicalGraphValidationError(f"Duplicate edge id: {edge_id}")
            edge_ids.add(edge_id)

            if edge.get("source") not in node_ids:
                raise CanonicalGraphValidationError(
                    f"Edge {edge_id} references missing source: {edge.get('source')}"
                )
            if edge.get("target") not in node_ids:
                raise CanonicalGraphValidationError(
                    f"Edge {edge_id} references missing target: {edge.get('target')}"
                )

    def _build_graph(self, raw: Dict[str, Any]) -> CanonicalGraph:
        nodes = [
            CanonicalNode(
                id=node["id"],
                technical_name=node["technical_name"],
                arabic_meaning=node["arabic_meaning"],
                type=node["type"],
                levels=node["levels"],
                status=node["status"],
                paths=node["paths"],
                responsibilities=node["responsibilities"],
                non_responsibilities=node["non_responsibilities"],
                evidence=node["evidence"],
                parent_ids=node.get("parent_ids", []),
                tags=node["tags"],
                metadata=node.get("metadata", {}),
            )
            for node in raw["nodes"]
        ]

        edges = [
            CanonicalEdge(
                id=edge["id"],
                source=edge["source"],
                target=edge["target"],
                relation_type=edge["relation_type"],
                direction=edge["direction"],
                status=edge["status"],
                evidence=edge["evidence"],
                data=edge.get("data", {}),
                metadata=edge.get("metadata", {}),
            )
            for edge in raw["edges"]
        ]

        return CanonicalGraph(
            artifact=raw["artifact"],
            version=raw["version"],
            purpose=raw["purpose"],
            governing_principle=raw["governing_principle"],
            source=raw["source"],
            levels=raw["levels"],
            nodes=nodes,
            edges=edges,
            agent_runtime_path=raw["agent_runtime_path"],
            classification_rules=raw["classification_rules"],
            graph_contract=raw["graph_contract"],
            validation=raw["validation"],
            next_work=raw["next_work"],
        )
