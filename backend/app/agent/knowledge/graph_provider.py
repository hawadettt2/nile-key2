from typing import Any, Dict, List, Optional

from .provider import KnowledgeProvider


_ENTITY_TYPE_TO_PATH = {
    "shipment": "shipping",
    "invoice": "eta",
    "customs_declaration": "customs",
    "document": "document",
    "export_workflow": "workflow",
}


class KnowledgeGraphProvider(KnowledgeProvider):
    """Knowledge Provider implementation for the Knowledge Graph.

    Queries the existing Knowledge Graph service layer to return
    graph nodes as knowledge results.
    """

    async def query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        sources: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        try:
            from app.services.knowledge_graph import search_nodes
        except ImportError:
            return {
                "results": [],
                "confidence": None,
                "sources": ["knowledge-graph"],
            }

        try:
            nodes = search_nodes(
                query=query,
                entity_type=scope,
                skip=0,
                limit=limit,
            )
        except Exception:
            return {
                "results": [],
                "confidence": None,
                "sources": ["knowledge-graph"],
            }

        results = []
        for node in nodes:
            entity_type = node.get("entity_type")
            path = _ENTITY_TYPE_TO_PATH.get(entity_type) if entity_type else None
            results.append({
                "id": node.get("id"),
                "content": node.get("label") or "",
                "source_id": "knowledge-graph",
                "confidence": 0.8,
                "metadata": {
                    "entity_type": entity_type,
                    "entity_id": node.get("entity_id"),
                    "properties": node.get("properties"),
                    "created_at": node.get("created_at"),
                    "updated_at": node.get("updated_at"),
                },
                "path": path,
            })

        confidence = 0.8 if results else None
        return {
            "results": results,
            "confidence": confidence,
            "sources": ["knowledge-graph"],
        }

    async def get_sources(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "knowledge-graph",
                "name": "Knowledge Graph",
                "type": "graph",
                "version": "1.0.0",
                "updated_at": "2026-07-20T00:00:00Z",
            }
        ]
