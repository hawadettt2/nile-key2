from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List


class KnowledgeProvider(ABC):
    """Interface for Company Knowledge Layer.

    Each knowledge source implements this interface and registers with
    KnowledgeProviderRegistry. The Digital Export Manager queries knowledge
    through the registry; it never accesses providers directly.
    """

    @abstractmethod
    async def query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        sources: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Query this knowledge provider.

        Args:
            query: The search query string.
            context: Optional context dictionary (e.g., session parameters).
            scope: Optional scope filter (e.g., "regulations", "procedures").
            sources: Optional list of source identifiers to restrict search.
            limit: Maximum number of results to return.

        Returns:
            Dict with keys:
                - results: List[Dict[str, Any]] — matching knowledge items.
                - confidence: Optional[float] — average confidence score (0.0–1.0).
                - sources: List[str] — source identifiers contributing to results.
        """
        raise NotImplementedError("KnowledgeProvider.query() is not implemented.")

    @abstractmethod
    async def get_sources(self) -> List[Dict[str, Any]]:
        """List all knowledge sources provided by this implementation.

        Returns:
            List of dicts with at least:
                - id: str — unique source identifier.
                - name: str — human-readable source name.
                - type: str — source type (e.g., "regulation", "procedure").
        """
        raise NotImplementedError("KnowledgeProvider.get_sources() is not implemented.")
