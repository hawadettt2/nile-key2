import hashlib
from typing import Any, Dict, List, Optional

from .provider import KnowledgeProvider
from .faostat_client import FaostatApiClient


class FaostatExternalSourceAdapter(KnowledgeProvider):
    """External source adapter boundary for FAOSTAT API.

    This adapter isolates FAOSTAT-specific schema and transport details from
    the DEM core. It owns:
      - FAOSTAT API communication
      - Authentication/configuration via configuration layer
      - Response transformation into DEM knowledge shape
      - ``source_id`` assignment
      - Confidence calculation per contract
      - Additional fields placement into ``metadata``

    The adapter does not:
      - Mutate DEM core
      - Expose raw FAOSTAT responses to users
      - Perform external research on behalf of users
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._source_id = self._config.get("source_id", "faostat")
        self._provider_name = self._config.get("name", "FAOSTAT External Knowledge")
        self._provider_type = self._config.get("type", "external_agrifood_intelligence")
        self._version = self._config.get("version", "1.0.0")
        self._updated_at = self._config.get("updated_at", "")
        self._default_domain = self._config.get("default_domain", "QCL")

        base_url = self._config.get("base_url", "")
        self._base_url = base_url.rstrip("/")
        api_key = self._config.get("api_key")
        timeout_seconds = float(self._config.get("timeout_seconds", 30.0))
        self._client = FaostatApiClient(
            base_url=base_url,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )

    async def query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        sources: Optional[List[str]] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        try:
            path, params = self._build_request(query=query, context=context, scope=scope, limit=limit)
            if not path:
                return {
                    "results": [],
                    "confidence": None,
                    "sources": [self._source_id],
                }

            raw = await self._client.request(method="GET", path=path, params=params)
        except Exception:
            return {
                "results": [],
                "confidence": None,
                "sources": [self._source_id],
            }

        results = self._transform(raw, context=context, limit=limit, scope=scope)
        if not results:
            return {
                "results": results,
                "confidence": None,
                "sources": [self._source_id],
            }
        confidence = sum(item["confidence"] for item in results) / len(results)
        return {
            "results": results,
            "confidence": confidence,
            "sources": [self._source_id],
        }

    def _build_request(
        self,
        query: str,
        context: Optional[Dict[str, Any]],
        scope: Optional[str],
        limit: int,
    ) -> tuple:
        """Build FAOSTAT API request path and query parameters.

        Returns:
            Tuple of (path, params).
        """
        if not isinstance(context, dict):
            context = {}

        domain = scope or self._default_domain
        if not isinstance(domain, str) or not domain:
            domain = self._default_domain

        path = f"/en/data/{domain}"

        params: Dict[str, Any] = {}
        area = context.get("area")
        item = context.get("item")
        element = context.get("element")
        year = context.get("year")

        if area:
            params["area"] = area
        if item:
            params["item"] = item
        if element:
            params["element"] = element
        if year:
            params["year"] = year

        params["format"] = "json"

        return path, params

    def _transform(self, raw: Any, context: Optional[Dict[str, Any]], limit: int, scope: Optional[str]) -> List[Dict[str, Any]]:
        if not isinstance(raw, dict):
            return []

        data = raw.get("data")
        if not isinstance(data, list):
            return []

        items: List[Dict[str, Any]] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            items.append(self._transform_entry(entry, scope=scope))

        return items[:limit]

    def _transform_entry(self, entry: Dict[str, Any], scope: Optional[str] = None) -> Dict[str, Any]:
        area = entry.get("area", "")
        area_code = entry.get("areaCode", "")
        item = entry.get("item", "")
        item_code = entry.get("itemCode", "")
        element = entry.get("element", "")
        element_code = entry.get("elementCode", "")
        year = entry.get("year", "")
        unit = entry.get("unit", "")
        value = entry.get("value", "")
        flag = entry.get("flag", "")

        record_id = f"{area_code}_{item_code}_{element_code}_{year}_{hash(str(entry))}"
        record_hash = str(hash(frozenset(entry.items()))) if entry else ""

        confidence = self._compute_confidence(flag=flag, value=value, area_code=area_code, item_code=item_code)

        content = self._build_content(item=item, element=element, area=area, year=year, value=value, unit=unit, flag=flag)

        effective_date = f"{year}-12-31" if isinstance(year, str) and year.isdigit() else (year or "")

        return {
            "id": record_id,
            "content": content,
            "source_id": self._source_id,
            "confidence": confidence,
            "metadata": {
                "area": area,
                "area_code": area_code,
                "item": item,
                "item_code": item_code,
                "element": element,
                "element_code": element_code,
                "year": year,
                "unit": unit,
                "source_authority": "FAO",
                "effective_date": effective_date,
                "source_url": self._build_source_url(scope=scope),
                "updated_at": self._updated_at,
                "version": self._version,
                "record_hash": record_hash,
                "retrieval_status": "success",
                "flag": flag,
            },
        }

    def _build_content(self, item: str, element: str, area: str, year: str, value: str, unit: str, flag: str) -> str:
        parts = []
        if item:
            parts.append(item)
        if element:
            parts.append(element)
        if area:
            parts.append(f"in {area}")
        if year:
            parts.append(f"({year})")
        if value:
            parts.append(f": {value}")
        if unit:
            parts.append(f" {unit}")
        content = " ".join(parts) if parts else ""

        if flag:
            flag_upper = str(flag).upper()
            if flag_upper in ("E", "F", "N"):
                content = f"{content} [{flag_upper}]"
            else:
                content = f"{content} [flag: {flag}]"

        return content or f"{item} {element} data"

    def _compute_confidence(self, flag: str, value: str, area_code: str, item_code: str) -> float:
        if not area_code or not item_code:
            return 0.6

        confidence = 0.95
        if flag:
            flag_upper = str(flag).upper()
            if flag_upper == "A":
                confidence = 0.95
            elif flag_upper in ("E", "F", "N"):
                confidence = 0.85
            else:
                confidence = 0.75

        if not value or value == "" or value == "0":
            confidence = min(confidence, 0.70)

        return confidence

    def _build_source_url(self, scope: Optional[str] = None) -> str:
        domain = scope or self._default_domain
        if not isinstance(domain, str) or not domain:
            domain = self._default_domain
        return f"{self._base_url}/en/data/{domain}?format=json"

    async def get_sources(self) -> List[Dict[str, Any]]:
        source: Dict[str, Any] = {
            "id": self._source_id,
            "name": self._provider_name,
            "type": self._provider_type,
            "version": self._version,
            "updated_at": self._updated_at,
        }
        return [source]
