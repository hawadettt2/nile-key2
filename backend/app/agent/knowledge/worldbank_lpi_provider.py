import hashlib
import json
from typing import Any, Dict, List, Optional

from .provider import KnowledgeProvider
from .worldbank_lpi_client import WorldBankLpiApiClient


class WorldBankLpiExternalSourceAdapter(KnowledgeProvider):
    """External source adapter boundary for World Bank LPI Indicators API.

    This adapter isolates World Bank LPI-specific schema and transport details
    from the DEM core. It owns:
      - World Bank Indicators API communication
      - Configuration via configuration layer
      - Response transformation into DEM knowledge shape
      - ``source_id`` assignment
      - Confidence calculation per contract
      - Additional fields placement into ``metadata``

    The adapter does not:
      - Mutate DEM core
      - Expose raw World Bank responses to users
      - Perform external research on behalf of users
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._source_id = self._config.get("source_id", "worldbank-lpi")
        self._provider_name = self._config.get("name", "World Bank Logistics Performance Index")
        self._provider_type = self._config.get("type", "external_logistics_intelligence")
        self._version = self._config.get("version", "1.0.0")
        self._updated_at = self._config.get("updated_at", "")

        base_url = self._config.get("base_url", "")
        self._base_url = base_url.rstrip("/")
        timeout_seconds = float(self._config.get("timeout_seconds", 30.0))
        self._client = WorldBankLpiApiClient(
            base_url=base_url,
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
        """Build World Bank Indicators API request path and query parameters.

        Returns:
            Tuple of (path, params).
        """
        if not isinstance(context, dict):
            context = {}

        country = context.get("country")
        if not isinstance(country, str) or not country:
            return "", {}

        indicator = scope or context.get("indicator") or "LP.LPI.OVRL.XQ"
        if not isinstance(indicator, str) or not indicator:
            indicator = "LP.LPI.OVRL.XQ"

        path = f"/country/{country}/indicator/{indicator}"

        params: Dict[str, Any] = {"format": "json"}
        params["per_page"] = min(limit, 100)

        year = context.get("year")
        if year is not None:
            params["date"] = str(year)

        return path, params

    def _transform(self, raw: Any, context: Optional[Dict[str, Any]], limit: int, scope: Optional[str]) -> List[Dict[str, Any]]:
        if not isinstance(raw, list) or len(raw) < 2:
            return []

        records = raw[1]
        if not isinstance(records, list):
            return []

        items: List[Dict[str, Any]] = []
        for entry in records:
            if not isinstance(entry, dict):
                continue
            items.append(self._transform_entry(entry))

        return items[:limit]

    def _transform_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        indicator = entry.get("indicator", {})
        country = entry.get("country", {})
        indicator_id = indicator.get("id", "") if isinstance(indicator, dict) else ""
        indicator_name = indicator.get("value", "") if isinstance(indicator, dict) else ""
        country_code = country.get("id", "") if isinstance(country, dict) else ""
        country_name = country.get("value", "") if isinstance(country, dict) else ""
        countryiso3code = entry.get("countryiso3code", "")
        year = entry.get("date", "")
        value = entry.get("value")
        unit = entry.get("unit", "") or ""
        obs_status = entry.get("obs_status", "") or ""
        decimal = entry.get("decimal")
        record_hash = hashlib.md5(json.dumps(entry, sort_keys=True, default=str).encode()).hexdigest() if entry else ""

        confidence = self._compute_confidence(value=value, obs_status=obs_status, countryiso3code=countryiso3code, indicator_id=indicator_id)

        content = self._build_content(indicator_name=indicator_name, year=year, value=value, unit=unit)

        return {
            "id": f"{countryiso3code}_{indicator_id}_{year}_{record_hash[-8:]}",
            "content": content,
            "source_id": self._source_id,
            "confidence": confidence,
            "metadata": {
                "indicator_id": indicator_id,
                "indicator_name": indicator_name,
                "country_code": country_code,
                "country_name": country_name,
                "countryiso3code": countryiso3code,
                "year": year,
                "value": value,
                "unit": unit,
                "obs_status": obs_status,
                "decimal": decimal,
                "source_authority": "World Bank",
                "effective_date": str(year) if year else "",
                "source_url": f"https://data.worldbank.org/indicator/{indicator_id}" if indicator_id else "",
                "record_hash": record_hash,
                "retrieval_status": "success",
                "updated_at": self._updated_at,
                "version": self._version,
            },
        }

    def _build_content(self, indicator_name: str, year: str, value: Any, unit: str) -> str:
        if indicator_name and year:
            if value is not None:
                unit_suffix = f" {unit}" if unit else ""
                return f"{indicator_name} ({year}): {value}{unit_suffix}"
            return f"{indicator_name} ({year}): data not available"
        return "World Bank LPI — data not available"

    def _compute_confidence(self, value: Any, obs_status: str, countryiso3code: str, indicator_id: str) -> float:
        if value is None or not countryiso3code or not indicator_id:
            return 0.6
        if obs_status:
            return 0.75
        return 0.95

    async def get_sources(self) -> List[Dict[str, Any]]:
        source: Dict[str, Any] = {
            "id": self._source_id,
            "name": self._provider_name,
            "type": self._provider_type,
            "version": self._version,
            "updated_at": self._updated_at,
        }
        return [source]
