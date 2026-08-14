import asyncio
from typing import Any, Dict, Optional

import httpx


class ZatcaApiClient:
    """Isolated HTTP client for ZATCA Open Data APIs.

    This client is intentionally kept outside the DEM core and outside
    ``KnowledgeProvider``. It is owned by the ZATCA adapter boundary and
    may change without affecting DEM core or the provider contract.

    **Note:** Exact endpoint paths and request/response schemas are TBD
    pending sandbox access and Swagger documentation review. This client
    provides the generic HTTP transport with retry/backoff; endpoint-specific
    logic is owned by ``ZatcaExternalSourceAdapter``.
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout_seconds: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not path:
            raise ValueError("path is required for ZATCA API request")

        url = f"{self._base_url}{path}" if path.startswith("/") else f"{self._base_url}/{path}"
        return await self._request_with_retry(method=method, url=url, params=params, json=json)

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        max_429_attempts = 3
        max_network_attempts = 2
        max_5xx_attempts = 2
        backoff_429 = 1.0
        backoff_network = 2.0
        backoff_5xx = 2.0

        attempt_429 = 0
        attempt_network = 0
        attempt_5xx = 0

        while True:
            try:
                async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                    response = await client.request(
                        method,
                        url,
                        headers=self._headers(),
                        json=json,
                        params=params,
                    )
                    if response.status_code == 429:
                        attempt_429 += 1
                        if attempt_429 < max_429_attempts:
                            await asyncio.sleep(backoff_429)
                            backoff_429 *= 2
                            continue
                        response.raise_for_status()
                    if 500 <= response.status_code < 600:
                        attempt_5xx += 1
                        if attempt_5xx < max_5xx_attempts:
                            await asyncio.sleep(backoff_5xx)
                            backoff_5xx *= 2
                            continue
                        response.raise_for_status()
                    response.raise_for_status()
                    return response.json()
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                attempt_network += 1
                if attempt_network < max_network_attempts:
                    await asyncio.sleep(backoff_network)
                    backoff_network *= 2
                    continue
                raise
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429:
                    attempt_429 += 1
                    if attempt_429 < max_429_attempts:
                        await asyncio.sleep(backoff_429)
                        backoff_429 *= 2
                        continue
                if 500 <= exc.response.status_code < 600:
                    attempt_5xx += 1
                    if attempt_5xx < max_5xx_attempts:
                        await asyncio.sleep(backoff_5xx)
                        backoff_5xx *= 2
                        continue
                raise

    async def close(self) -> None:
        return None
