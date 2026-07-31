from typing import Any, Dict, List, Optional

from .provider import KnowledgeProvider


class CompanyKnowledgeProvider(KnowledgeProvider):
    """Company Knowledge Provider implementation.

    Queries the existing Company Knowledge corpus stored in the resources
    service layer. This includes external trade references, regulations,
    SOPs, manuals, and verified institutional knowledge.
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
            from app.services.resource import list_resources, search_resources
        except ImportError:
            return {
                "results": [],
                "confidence": None,
                "sources": ["company-knowledge"],
            }

        try:
            country = None
            category = None
            if isinstance(context, dict):
                country = context.get("country")
                category = context.get("category")

            if query:
                raw_results = search_resources(q=query)
            else:
                raw_results = list_resources(
                    resource_type=scope,
                    category=category,
                    country=country,
                    skip=0,
                    limit=limit,
                )
        except Exception:
            return {
                "results": [],
                "confidence": None,
                "sources": ["company-knowledge"],
            }

        results = []
        for resource in raw_results[:limit]:
            metadata = resource.get("metadata") or {}
            if isinstance(metadata, str):
                metadata = {}

            tags = metadata.get("tags", "")
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
            elif not isinstance(tags, list):
                tags = []

            results.append({
                "id": str(resource.get("id")),
                "content": resource.get("description") or resource.get("title") or "",
                "source_id": "company-knowledge",
                "confidence": 0.9,
                "metadata": {
                    "title": resource.get("title"),
                    "url": resource.get("url"),
                    "resource_type": resource.get("resource_type"),
                    "category": resource.get("category"),
                    "country": resource.get("country"),
                    "tags": tags,
                    "is_active": resource.get("is_active"),
                },
            })

        confidence = 0.9 if results else None
        return {
            "results": results,
            "confidence": confidence,
            "sources": ["company-knowledge"],
        }

    async def get_sources(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "company-knowledge",
                "name": "Company Knowledge",
                "type": "company",
                "version": "1.0.0",
                "updated_at": "2026-07-31T00:00:00Z",
            }
        ]
