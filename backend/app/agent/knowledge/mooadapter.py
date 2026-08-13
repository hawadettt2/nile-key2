from typing import Any, Dict, List, Optional

from .provider import KnowledgeProvider
from .mooadapter_client import MoaahApiClient


class MoaahExternalSourceAdapter(KnowledgeProvider):
    """External source adapter boundary for Moaah API.

    This adapter isolates Moaah-specific schema and transport details from
    the DEM core. It owns:
      - Moaah API communication
      - Authentication/configuration via configuration layer
      - Response transformation into DEM knowledge shape
      - ``source_id`` assignment
      - Confidence calculation per contract
      - Additional fields placement into ``metadata``

    The adapter does not:
      - Mutate DEM core
      - Expose raw Moaah responses to users
      - Perform external research on behalf of users
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._source_id = self._config.get("source_id", "moaah")
        self._provider_name = self._config.get("name", "Moaah External Knowledge")
        self._provider_type = self._config.get("type", "external")
        self._version = self._config.get("version", "1.0.0")
        self._updated_at = self._config.get("updated_at", "")

        base_url = self._config.get("base_url", "")
        api_key = self._config.get("api_key")
        timeout_seconds = float(self._config.get("timeout_seconds", 10.0))
        self._client = MoaahApiClient(
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
            country = None
            search_type = "keyword"
            if isinstance(scope, str) and scope:
                search_type = scope
            if isinstance(context, dict):
                country = context.get("country")

            if not country:
                return {
                    "results": [],
                    "confidence": None,
                    "sources": [self._source_id],
                }

            params: Dict[str, Any] = {
                "q": query or "",
                "type": search_type,
                "country": country,
            }
            if isinstance(context, dict):
                affected_country = context.get("affected_country")
                if affected_country:
                    params["affected_country"] = affected_country
                start_date = context.get("start_date")
                end_date = context.get("end_date")
                if start_date:
                    params["start_date"] = start_date
                if end_date:
                    params["end_date"] = end_date

            raw = await self._client.search_regulations(params=params)
        except ValueError:
            raise
        except Exception:
            return {
                "results": [],
                "confidence": None,
                "sources": [self._source_id],
            }

        results = self._transform(raw, limit=limit)
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

    def _transform(self, raw: Any, limit: int = 10) -> List[Dict[str, Any]]:
        if not isinstance(raw, dict):
            return []

        items: List[Dict[str, Any]] = []
        for key in ("antidumping", "importLicensing", "pr", "qr", "docs", "docs_origin"):
            section = raw.get(key)
            if isinstance(section, list):
                for entry in section:
                    if isinstance(entry, dict):
                        items.append(self._transform_entry(entry, section_label=key))
            elif isinstance(section, dict):
                for value in section.values():
                    if isinstance(value, list):
                        for entry in value:
                            if isinstance(entry, dict):
                                items.append(self._transform_entry(entry, section_label=key))
                    elif isinstance(value, dict):
                        for entry in value.get("data", []) or value.get("dataOrigin", []) or []:
                            if isinstance(entry, dict):
                                items.append(self._transform_entry(entry, section_label=key))

        matched_hs_codes = raw.get("matched_hs_codes")
        if isinstance(matched_hs_codes, list):
            for entry in matched_hs_codes:
                if isinstance(entry, dict):
                    items.append(self._transform_entry(entry, section_label="matched_hs_code"))

        return items[:limit]

    def _transform_entry(self, entry: Dict[str, Any], section_label: str) -> Dict[str, Any]:
        title = (
            entry.get("subject_product")
            or entry.get("desc")
            or entry.get("title")
            or section_label
        )
        content = (
            entry.get("duty_measure_detail")
            or entry.get("summary")
            or entry.get("description")
            or entry.get("requirement")
            or entry.get("regulation_text")
            or ""
        )
        if isinstance(content, dict):
            content = " | ".join(f"{k}: {v}" for k, v in content.items() if v is not None)

        effective_date = entry.get("publication_date") or entry.get("initiation_dt") or entry.get("effective_date")
        source_url = entry.get("id_link") or entry.get("source_url") or entry.get("url")

        confidence = 0.75
        if source_url:
            confidence = 0.85
        if effective_date:
            confidence = 0.9

        record_id = str(entry.get("uuid") or entry.get("id") or id(entry))
        record_hash = str(hash(frozenset(entry.items()))) if entry else ""

        return {
            "id": record_id,
            "content": f"{title} - {content}" if title else str(content),
            "source_id": self._source_id,
            "confidence": confidence,
            "metadata": {
                "section": section_label,
                "effective_date": effective_date,
                "source_url": source_url,
                "country": entry.get("country"),
                "hs_code": entry.get("hs_code") or entry.get("HSCode") or entry.get("code"),
                "regulation_type": entry.get("regulation_type") or section_label,
                "category": entry.get("category"),
                "version": self._version,
                "fetch_timestamp": self._updated_at,
                "record_hash": record_hash,
                "retrieval_status": "success",
            },
        }

    async def get_sources(self) -> List[Dict[str, Any]]:
        source: Dict[str, Any] = {
            "id": self._source_id,
            "name": self._provider_name,
            "type": self._provider_type,
            "version": self._version,
            "updated_at": self._updated_at,
        }
        return [source]
