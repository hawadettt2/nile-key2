from __future__ import annotations

from typing import Any, Dict, List, Optional
import logging

import httpx

from app.research.retrieval.contracts import (
    RetrievedContent,
    RetrievalResult,
    RetrievalStatus,
)
from app.research.retrieval.providers.adapter import SearchProviderAdapter
from app.research.retrieval.providers.capability import ProviderCapability
from app.schemas.research import Source


logger = logging.getLogger(__name__)


class SearXNGAdapter(SearchProviderAdapter):
    """SearXNG search provider adapter.

    This is a concrete implementation of ``SearchProviderAdapter`` for SearXNG.
    It is one pluggable adapter inside the WP-35 provider-agnostic layer; it is
    not an architectural primary or mandatory default.

    Configuration is read from environment variables / settings:
    - ``SEARXNG_BASE_URL``: base URL of the SearXNG instance
    - ``SEARXNG_API_KEY``: optional API key passed as a Bearer token
    - ``SEARXNG_TIMEOUT_SECONDS``: HTTP timeout in seconds

    ``retrieve()`` maps SearXNG responses to the existing WP-34 contracts:
    - success → ``RetrievalStatus.SUCCESS`` with ``RetrievedContent``
    - timeout → ``RetrievalStatus.TIMEOUT``
    - connection/HTTP failure → ``RetrievalStatus.CONNECTION_FAILURE``
    - invalid JSON or missing ``results`` list → ``RetrievalStatus.INVALID_RESPONSE``

    ``health_check()`` performs a lightweight GET to ``/search`` and returns
    ``True`` only when the instance responds with HTTP 200.

    This adapter does not modify WP-34 contracts, does not depend on AI/LLM
    providers, and can be replaced or supplemented by other adapters without
    changing the research lifecycle.
    """

    def __init__(
        self,
        capability: ProviderCapability,
        base_url: str,
        api_key: str = "",
        timeout: float = 10.0,
    ) -> None:
        self._capability = capability
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout

    @property
    def capability(self) -> ProviderCapability:
        return self._capability

    async def retrieve(self, source: Source, query: str) -> RetrievalResult:
        search_url = f"{self._base_url}/search"
        params: Dict[str, Any] = {
            "q": query,
            "format": "json",
        }
        headers: Dict[str, str] = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(search_url, params=params, headers=headers)
        except httpx.TimeoutException:
            logger.warning("SearXNG timeout for source %s", source.source_id)
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.TIMEOUT,
                error="SearXNG request timed out",
            )
        except httpx.ConnectError:
            logger.warning("SearXNG connection failed for source %s", source.source_id)
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.CONNECTION_FAILURE,
                error="SearXNG connection failed",
            )
        except httpx.HTTPError as exc:
            logger.warning("SearXNG HTTP error for source %s: %s", source.source_id, exc)
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.CONNECTION_FAILURE,
                error=f"SearXNG HTTP error: {exc}",
            )

        if response.status_code != 200:
            logger.warning(
                "SearXNG returned status %s for source %s",
                response.status_code,
                source.source_id,
            )
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.CONNECTION_FAILURE,
                error=f"SearXNG returned status {response.status_code}",
            )

        try:
            data = response.json()
        except ValueError:
            logger.warning("SearXNG returned invalid JSON for source %s", source.source_id)
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.INVALID_RESPONSE,
                error="SearXNG returned invalid JSON",
            )

        results = data.get("results") if isinstance(data, dict) else None
        if not isinstance(results, list):
            logger.warning("SearXNG response missing results list for source %s", source.source_id)
            return RetrievalResult(
                source_id=source.source_id,
                status=RetrievalStatus.INVALID_RESPONSE,
                error="SearXNG response missing results list",
            )

        return RetrievalResult(
            source_id=source.source_id,
            status=RetrievalStatus.SUCCESS,
            content=RetrievedContent(
                source_id=source.source_id,
                raw_content={"results": results, "query": query},
                content_type="application/json",
                metadata={"provider": "searxng", "result_count": len(results)},
            ),
        )

    async def health_check(self) -> bool:
        health_url = f"{self._base_url}/search"
        params = {
            "q": "healthcheck",
            "format": "json",
        }
        headers = {}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(health_url, params=params, headers=headers)
                return response.status_code == 200
        except Exception:
            return False
