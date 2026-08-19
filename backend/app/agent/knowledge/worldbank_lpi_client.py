import asyncio
from typing import Any, Dict, List, Optional

import httpx


class WorldBankLpiApiClient:
    """Isolated HTTP client for World Bank Indicators API.

    This client is intentionally kept outside the DEM core and outside
    ``KnowledgeProvider``. It is owned by the World Bank LPI adapter boundary
    and may change without affecting DEM core or the provider contract.
    """

    def __init__(self, base_url: str, timeout_seconds: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not path:
            raise ValueError("path is required for World Bank Indicators API request")

        url = f"{self._base_url}{path}" if path.startswith("/") else f"{self._base_url}/{path}"

        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            response = await client.request(
                method,
                url,
                headers={"Accept": "application/json"},
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def close(self) -> None:
        return None
