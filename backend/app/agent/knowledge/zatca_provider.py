import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional

from app.core.credentials.credential_store import CredentialStore
from .provider import KnowledgeProvider
from .zatca_client import ZatcaApiClient


class ZatcaExternalSourceAdapter(KnowledgeProvider):
    """External source adapter boundary for ZATCA Open Data APIs.

    This adapter isolates ZATCA-specific schema and transport details from
    the DEM core. It owns:
      - ZATCA API communication
      - Authentication/configuration via configuration layer
      - Response transformation into DEM knowledge shape
      - ``source_id`` assignment
      - Confidence calculation per contract
      - Additional fields placement into ``metadata``

    The adapter does not:
      - Mutate DEM core
      - Expose raw ZATCA responses to users
      - Perform external research on behalf of users

    **Note:** Exact ZATCA endpoint paths and request/response schemas are TBD
    pending sandbox access and Swagger documentation review. This implementation
    provides the adapter contract and generic transformation logic; endpoint-specific
    details are resolved during Task 3 sandbox integration.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, credential_store: Optional[CredentialStore] = None) -> None:
        self._config = config or {}
        self._source_id = self._config.get("source_id", "zatca")
        self._provider_name = self._config.get("name", "ZATCA Open Data APIs")
        self._provider_type = self._config.get("type", "external_trade_intelligence")
        self._version = self._config.get("version", "1.0")
        self._updated_at = self._config.get("updated_at", "")

        base_url = self._config.get("base_url", "")
        api_key = self._config.get("api_key")
        timeout_seconds = float(self._config.get("timeout_seconds", 30.0))
        self._client = ZatcaApiClient(
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
            country = None
            if isinstance(context, dict):
                country = context.get("country")

            if not country:
                return {
                    "results": [],
                    "confidence": None,
                    "sources": [self._source_id],
                }

            path, params, body = self._build_request(query=query, context=context, scope=scope, limit=limit)
            if not path:
                return {
                    "results": [],
                    "confidence": None,
                    "sources": [self._source_id],
                }

            if body is not None:
                raw = await self._client.request(method="POST", path=path, params=params, json=body)
            else:
                raw = await self._client.request(method="GET", path=path, params=params)
        except ValueError:
            raise
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

    def _build_request(self, query: str, context: Optional[Dict[str, Any]], scope: Optional[str], limit: int) -> tuple[str, Dict[str, Any], Optional[Dict[str, Any]]]:
        """Build ZATCA API request path, query params, and optional JSON body.

        Returns:
            Tuple of (path, params, body). body is None for GET requests.

        **Note:** Exact endpoint paths and parameter formats are TBD pending
        Swagger documentation review. This implementation uses documented API
        names as scope values and constructs plausible request shapes; actual
        paths/params must be verified during Task 3 sandbox integration.
        """
        if not isinstance(context, dict):
            context = {}

        scope_value = (scope or "export_import_details").lower()

        scope_to_path = {
            "export_import_details": "/api/v1/export-import-details",
            "clearance_port": "/api/v1/clearance-port",
            "port_clearance_details": "/api/v1/port-clearance-details",
            "port_traffic": "/api/v1/port-traffic",
            "explore_data": "/api/v1/explore-data",
        }
        path = scope_to_path.get(scope_value)
        if not path:
            path = "/api/v1/export-import-details"

        params: Dict[str, Any] = {}
        body: Optional[Dict[str, Any]] = None

        start_date = context.get("start_date")
        end_date = context.get("end_date")
        if start_date and end_date:
            params["start_date"] = str(start_date)
            params["end_date"] = str(end_date)

        port_name = context.get("port_name")
        if port_name:
            params["port_name"] = str(port_name)

        traffic_type = context.get("traffic_type")
        if traffic_type:
            params["traffic_type"] = str(traffic_type)

        params["limit"] = str(max(1, limit))

        if query:
            params["q"] = str(query)

        return path, params, body

    def _transform(self, raw: Any, context: Optional[Dict[str, Any]], limit: int, scope: Optional[str]) -> List[Dict[str, Any]]:
        """Transform ZATCA API response into DEM knowledge shape.

        **Note:** ZATCA response schema is TBD pending Swagger review. This
        implementation handles common response patterns:
        - List of records
        - Dict with a data/list field containing records
        - Single dict record
        Unknown structures are gracefully degraded into a single record with
        minimal metadata.
        """
        if not isinstance(raw, dict):
            return []

        entries: List[Dict[str, Any]] = []
        data = raw.get("data")
        if isinstance(data, list):
            entries = [item for item in data if isinstance(item, dict)]
        elif raw:
            entries = [raw]

        if not entries:
            return []

        requested_start_date = None
        requested_end_date = None
        port_name = None
        traffic_type = None
        if isinstance(context, dict):
            requested_start_date = context.get("start_date")
            requested_end_date = context.get("end_date")
            port_name = context.get("port_name")
            traffic_type = context.get("traffic_type")

        items: List[Dict[str, Any]] = []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            items.append(self._transform_entry(entry, requested_start_date=requested_start_date, requested_end_date=requested_end_date, port_name=port_name, traffic_type=traffic_type))

        return items[:limit]

    def _transform_entry(
        self,
        entry: Dict[str, Any],
        requested_start_date: Optional[str],
        requested_end_date: Optional[str],
        port_name: Optional[str],
        traffic_type: Optional[str],
    ) -> Dict[str, Any]:
        # Best-effort extraction from unknown ZATCA schema.
        # These mappings will be refined during Task 3 once Swagger schemas are available.
        source_authority = "ZATCA_OpenData"
        if isinstance(entry.get("source"), str) and entry.get("source"):
            source_authority = str(entry.get("source"))

        effective_date = ""
        for key in ("date", "effective_date", "timestamp", "created_at", "updated_at"):
            value = entry.get(key)
            if isinstance(value, str) and value:
                effective_date = value
                break

        country = "SA"
        for key in ("country", "country_code", "nationality"):
            value = entry.get(key)
            if isinstance(value, str) and value:
                country = value.upper()
                break

        source_url = ""
        for key in ("endpoint", "api_endpoint", "url", "link"):
            value = entry.get(key)
            if isinstance(value, str) and value:
                source_url = value
                break

        legal_act_reference = ""
        for key in ("legal_act_reference", "regulation", "act", "reference"):
            value = entry.get(key)
            if isinstance(value, str) and value:
                legal_act_reference = value
                break
            if isinstance(value, dict) and value:
                legal_act_reference = str(value)
                break

        content_parts = []
        for key in ("description", "details", "summary", "name", "title", "product", "goods_description"):
            value = entry.get(key)
            if isinstance(value, str) and value:
                content_parts.append(value)
                break

        for key in ("port_name", "port", "portName"):
            value = entry.get(key)
            if isinstance(value, str) and value:
                content_parts.append(f"Port: {value}")
                break

        for key in ("traffic_type", "type", "movement_type"):
            value = entry.get(key)
            if isinstance(value, str) and value:
                content_parts.append(f"Type: {value}")
                break

        metrics = []
        for key in ("quantity", "weight", "amount", "value", "teu", "twenty_foot_equivalent"):
            value = entry.get(key)
            if value is not None:
                metrics.append(f"{key}: {value}")
        if metrics:
            content_parts.append(f"Metrics: {' | '.join(metrics)}")

        content = " | ".join(content_parts) if content_parts else json.dumps(entry, default=str)

        confidence = self._calculate_confidence(
            entry=entry,
            data_source=source_authority,
            date=effective_date,
            country=country,
            requested_start_date=requested_start_date,
            requested_end_date=requested_end_date,
        )
        retrieval_status = self._calculate_retrieval_status(
            entry=entry,
            data_source=source_authority,
            date=effective_date,
            country=country,
        )

        record_id = str(entry.get("id") or entry.get("record_id") or entry.get("declaration_number") or uuid.uuid4())
        record_hash = hashlib.sha256(json.dumps(entry, sort_keys=True, default=str).encode("utf-8")).hexdigest()

        return {
            "id": record_id,
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
        entry: Dict[str, Any],
        data_source: str,
        date: str,
        country: str,
        requested_start_date: Optional[str],
        requested_end_date: Optional[str],
    ) -> float:
        if data_source and date and country:
            confidence = 0.85
        elif data_source or date:
            confidence = 0.75
        elif entry.get("hsCode") or entry.get("buyerName") or entry.get("supplierName") or entry.get("description") or entry.get("details"):
            confidence = 0.65
        else:
            confidence = 0.50

        if date and requested_start_date and requested_end_date:
            try:
                record_date = int(date.replace("-", ""))
                start = int(requested_start_date.replace("-", ""))
                end = int(requested_end_date.replace("-", ""))
                if record_date < start or record_date > end:
                    confidence = max(confidence - 0.10, 0.50)
            except (ValueError, TypeError):
                pass

        lower_priority_sources = ("unknown", "aggregated", "estimated")
        if any(marker in data_source.lower() for marker in lower_priority_sources):
            confidence = max(confidence - 0.05, 0.50)

        return confidence

    def _calculate_retrieval_status(self, entry: Dict[str, Any], data_source: str, date: str, country: str) -> str:
        if data_source and date and country:
            return "success"
        if data_source or date or country or entry.get("description") or entry.get("details") or entry.get("name"):
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
