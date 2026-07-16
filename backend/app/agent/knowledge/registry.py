from typing import Dict, List, Optional, Any
from .provider import KnowledgeProvider


class KnowledgeProviderRegistry:
    """Registry for KnowledgeProvider implementations.

    Follows the same pattern as ToolRegistry. Providers register themselves
    or are registered by the application bootstrap. The Digital Export Manager
    queries the registry; it never accesses providers directly.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, KnowledgeProvider] = {}

    async def register(self, provider: KnowledgeProvider) -> None:
        """Register a knowledge provider instance.

        Args:
            provider: A KnowledgeProvider implementation instance.

        Raises:
            ValueError: If the provider does not expose any sources via
                get_sources(), or if a source lacks an 'id'.
        """
        sources = await provider.get_sources()
        if not sources:
            raise ValueError(
                f"Knowledge provider {provider.__class__.__name__} must expose "
                "at least one source via get_sources()."
            )
        for source in sources:
            source_id = source.get("id")
            if not source_id:
                raise ValueError(
                    f"Knowledge provider {provider.__class__.__name__} returned "
                    "a source without an 'id'."
                )
            self._providers[source_id] = provider

    def unregister(self, source_id: str) -> None:
        """Remove a knowledge provider by source ID."""
        if source_id in self._providers:
            del self._providers[source_id]

    def get(self, source_id: str) -> Optional[KnowledgeProvider]:
        """Get a knowledge provider by source ID."""
        return self._providers.get(source_id)

    async def list_providers(self) -> List[Dict[str, Any]]:
        """List all registered knowledge sources with their metadata."""
        seen = set()
        providers_info = []
        for provider in self._providers.values():
            for source in await provider.get_sources():
                source_id = source.get("id")
                if source_id and source_id not in seen:
                    seen.add(source_id)
                    providers_info.append(source)
        return providers_info

    def exists(self, source_id: str) -> bool:
        """Check if a knowledge source is registered."""
        return source_id in self._providers

    async def query(
        self,
        source_id: str,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Query a specific knowledge source by ID.

        Args:
            source_id: The source identifier to query.
            query: The search query string.
            context: Optional context dictionary.
            scope: Optional scope filter.
            limit: Maximum number of results.

        Returns:
            Dict with keys: results, confidence, sources.

        Raises:
            KeyError: If the source_id is not registered.
        """
        provider = self._providers.get(source_id)
        if not provider:
            raise KeyError(f"Knowledge source '{source_id}' is not registered.")
        return await provider.query(
            query=query,
            context=context,
            scope=scope,
            limit=limit,
        )
