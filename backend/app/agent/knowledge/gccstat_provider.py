import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional

from app.core.credentials.credential_store import CredentialStore
from .provider import KnowledgeProvider
from .gccstat_client import GccstatApiClient


class GccstatExternalSourceAdapter(KnowledgeProvider):
    """External source adapter boundary for GCC-Stat Data Portal.

    This adapter isolates GCC-Stat-specific schema and transport details from
    the DEM core. It owns:
      - GCC-Stat API communication
      - Authentication/configuration via configuration layer
      - Response transformation into DEM knowledge shape
      - ``source_id`` assignment
      - Confidence calculation per contract
      - Additional fields placement into ``metadata``

    The adapter does not:
      - Mutate DEM core
      - Expose raw GCC-Stat responses to users
      - Perform external research on behalf of users
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, credential_store: Optional[CredentialStore] = None) -> None:
        self._config = config or {}
        self._source_id = self._config.get("source_id", "gccstat")
        self._provider_name = self._config.get("name", "GCC-Stat Data Portal")
        self._provider_type = self._config.get("type", "external_trade_intelligence")
        self._version = self._config.get("version", "1.0")
        self._updated_at = self._config.get("updated_at", "")

        base_url = self._config.get("base_url", "")
        api_key = self._config.get("api_key")
        timeout_seconds = float(self._config.get("timeout_seconds", 30.0))
        self._client = GccstatApiClient(
            base_url=base_url,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
            credential_store=credential_store,
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
        """Build GCC-Stat API request path and query parameters.

        **Note:** Exact dataflow IDs and dimension mappings are TBD pending
        live API verification. This implementation uses documented dataflow
        IDs from the GCC-Stat data portal as scope values.
        """
        if not isinstance(context, dict):
            context = {}

        scope_value = (scope or "population").lower()

        scope_to_dataflow = {
            "population": "DF_PSS_DEM_POP",
            "labour": "DF_PSS_LAB",
            "agriculture": "DF_DCD_AGR",
            "tourism": "DF_GEETS_TUR",
            "national_accounts": "DF_ES_NA",
            "health": "DF_PSS_HLT_FACILITIES",
            "education": "DF_PSS_EDU_STUDENTS",
        }

        dataflow_id = scope_to_dataflow.get(scope_value, "DF_PSS_DEM_POP")
        agency_id = "GCCSTAT.PSS"
        if dataflow_id in ("DF_DCD_AGR",):
            agency_id = "GCCSTAT.DCD"
        elif dataflow_id in ("DF_GEETS_TUR",):
            agency_id = "GCCSTAT.GEETS"
        elif dataflow_id in ("DF_ES_NA",):
            agency_id = "GCCSTAT.ES"
        elif dataflow_id in ("DF_RDI_SDG",):
            agency_id = "GCCSTAT.RDI"

        path = f"/FusionRegistry/ws/public/sdmxapi/rest/data/{agency_id},{dataflow_id},1.0/all/all"
        params: Dict[str, Any] = {
            "labels": "name",
            "format": "sdmx-json",
        }

        return path, params

    def _transform(
        self,
        raw: Any,
        context: Optional[Dict[str, Any]],
        limit: int,
        scope: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Transform GCC-Stat SDMX response into DEM knowledge shape.

        **Note:** GCC-Stat response schema follows SDMX JSON format.
        This implementation handles the standard SDMX JSON structure with
        series/observations. Exact dimension mappings may be refined during
        Task 3 sandbox integration.
        """
        if not isinstance(raw, dict):
            return []

        data_section = raw.get("data")
        if not isinstance(data_section, dict):
            return []

        data_sets = data_section.get("dataSets")
        if not isinstance(data_sets, list) or not data_sets:
            return []

        first_data_set = data_sets[0]
        if not isinstance(first_data_set, dict):
            return []

        series = first_data_set.get("series")
        if not isinstance(series, dict):
            return []

        structures = data_section.get("structures")
        dimension_map = {}
        if isinstance(structures, list) and structures:
            first_structure = structures[0]
            if isinstance(first_structure, dict):
                dimensions = first_structure.get("dimensions", {})
                if isinstance(dimensions, dict):
                    observation = dimensions.get("observation", [])
                    if isinstance(observation, list):
                        dimension_map = {str(i): dim for i, dim in enumerate(observation)}

        items: List[Dict[str, Any]] = []
        for series_key, series_value in series.items():
            if not isinstance(series_value, dict):
                continue
            items.extend(
                self._transform_series(
                    series_key=series_key,
                    series_value=series_value,
                    dimension_map=dimension_map,
                    context=context,
                    scope=scope,
                )
            )

        return items[:limit]

    def _transform_series(
        self,
        series_key: str,
        series_value: Dict[str, Any],
        dimension_map: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        scope: Optional[str],
    ) -> List[Dict[str, Any]]:
        """Transform a single SDMX series into DEM knowledge items."""
        observations = series_value.get("observations")
        if not isinstance(observations, dict):
            return []

        requested_country = None
        if isinstance(context, dict):
            requested_country = context.get("country")

        items: List[Dict[str, Any]] = []
        for obs_key, obs_values in observations.items():
            if not isinstance(obs_values, list) or not obs_values:
                continue

            item = self._transform_observation(
                series_key=series_key,
                obs_key=obs_key,
                obs_value=obs_values[0],
                dimension_map=dimension_map,
                requested_country=requested_country,
                scope=scope,
            )
            if item:
                items.append(item)

        return items

    def _transform_observation(
        self,
        series_key: str,
        obs_key: str,
        obs_value: str,
        dimension_map: Dict[str, Any],
        requested_country: Optional[str],
        scope: Optional[str],
    ) -> Dict[str, Any]:
        """Transform a single SDMX observation into DEM knowledge item."""
        source_authority = "GCC-Stat"

        effective_date = ""
        if isinstance(obs_key, str) and obs_key.isdigit():
            effective_date = obs_key

        country = ""
        if requested_country:
            country = requested_country.upper()
        else:
            series_parts = series_key.split(":")
            if series_parts:
                country = series_parts[0].upper()

        source_url = ""
        if scope:
            source_url = f"sdmx:{scope}"

        legal_act_reference = ""

        content_parts = []
        if scope:
            content_parts.append(f"Indicator: {scope}")
        if country:
            content_parts.append(f"Country: {country}")
        if effective_date:
            content_parts.append(f"Period: {effective_date}")
        content_parts.append(f"Value: {obs_value}")

        content = " | ".join(content_parts) if content_parts else f"GCC-Stat observation: {obs_value}"

        confidence = self._calculate_confidence(
            source_authority=source_authority,
            effective_date=effective_date,
            country=country,
            obs_value=obs_value,
        )
        retrieval_status = self._calculate_retrieval_status(
            source_authority=source_authority,
            effective_date=effective_date,
            country=country,
            obs_value=obs_value,
        )

        record_hash = hashlib.sha256(
            f"{series_key}:{obs_key}:{obs_value}".encode("utf-8")
        ).hexdigest()

        return {
            "id": str(uuid.uuid4()),
            "content": content,
            "source_id": self._source_id,
            "confidence": confidence,
            "metadata": {
                "source_authority": source_authority,
                "effective_date": effective_date,
                "country": country,
                "source_url": source_url,
                "legal_act_reference": legal_act_reference,
                "updated_at": self._updated_at,
                "version": self._version,
                "record_hash": record_hash,
                "retrieval_status": retrieval_status,
            },
        }

    def _calculate_confidence(
        self,
        source_authority: str,
        effective_date: str,
        country: str,
        obs_value: str,
    ) -> float:
        if source_authority and effective_date and country:
            confidence = 0.85
        elif source_authority or effective_date:
            confidence = 0.75
        elif obs_value:
            confidence = 0.65
        else:
            confidence = 0.50
        return confidence

    def _calculate_retrieval_status(
        self,
        source_authority: str,
        effective_date: str,
        country: str,
        obs_value: str,
    ) -> str:
        if source_authority and effective_date and country:
            return "success"
        if source_authority or effective_date or country or obs_value:
            return "partial"
        return "failed"

    async def get_sources(self) -> List[Dict[str, Any]]:
        source: Dict[str, Any] = {
            "id": self._source_id,
            "name": self._provider_name,
            "type": self._provider_type,
            "version": self._version,
            "updated_at": self._updated_at,
        }
        return [source]
