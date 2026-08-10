from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.research.retrieval.contracts import (
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
    SourceRetriever,
)
from app.research.retrieval.providers.capability import ProviderCapability
from app.schemas.research import Source


class SearchProviderAdapter(SourceRetriever):
    """Provider-agnostic adapter interface for search providers.

    Extends the existing ``SourceRetriever`` contract with capability
    description and health checking so that a router can select and
    fail over between providers without knowing their internal APIs.
    """

    @property
    @abstractmethod
    def capability(self) -> ProviderCapability:
        """Return the capability descriptor for this provider."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True when the provider is reachable and operational."""
        ...
