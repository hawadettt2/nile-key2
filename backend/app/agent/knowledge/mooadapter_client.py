import asyncio
from typing import Any, Dict, Optional

import httpx


class MoaahApiClient:
    """Isolated HTTP client for Moaah API.

    This client is intentionally kept outside the DEM core and outside
    ``KnowledgeProvider``. It is owned by the Moaah adapter boundary and
    may change without affecting DEM core or the provider contract.
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout_seconds: float = 10.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {
            "Accept": "application/json",
        }
        return headers

    def _params(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {}
        if self._api_key:
            params["token"] = self._api_key
        if extra:
            params.update(extra)
        return params

    async def search_regulations(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        query = (params or {}).get("q", "")
        country = (params or {}).get("country", "")
        search_type = (params or {}).get("type", "keyword")
        affected_country = (params or {}).get("affected_country")
        start_date = (params or {}).get("start_date")
        end_date = (params or {}).get("end_date")

        if not query or not country or not search_type:
            raise ValueError("q, country, and type are required for /regs-search")

        request_params: Dict[str, Any] = {
            "q": query,
            "type": search_type,
            "country": country,
        }
        if affected_country:
            request_params["affected_country"] = affected_country
        if start_date:
            request_params["start_date"] = start_date
        if end_date:
            request_params["end_date"] = end_date

        return await self._request_with_retry(
            "GET",
            f"{self._base_url}/regs-search",
            params=self._params(request_params),
        )

    async def get_country_measures(self, country_code: str) -> Dict[str, Any]:
        if not country_code:
            raise ValueError("country_code is required for country measures")

        return await self._request_with_retry(
            "GET",
            f"{self._base_url}/country-list",
            params=self._params({"country": country_code}),
        )

    async def _request_with_retry(self, method: str, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        max_attempts = 3
        backoff = 1.0

        last_exc: Optional[Exception] = None
        for attempt in range(1, max_attempts + 1):
            try:
                async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                    response = await client.request(
                        method,
                        url,
                        headers=self._headers(),
                        params=params,
                    )
                    if response.status_code == 429:
                        if attempt < max_attempts:
                            await asyncio.sleep(backoff)
                            backoff *= 2
                            continue
                    response.raise_for_status()
                    return response.json()
            except (httpx.TimeoutException, httpx.NetworkError) as exc:
                last_exc = exc
                if attempt < max_attempts:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                break
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code == 429 and attempt < max_attempts:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                raise

        if last_exc:
            raise last_exc
        raise RuntimeError(f"Request to {url} failed after {max_attempts} attempts")

    async def close(self) -> None:
        return None
