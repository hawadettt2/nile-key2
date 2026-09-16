import hashlib
from typing import Any, Dict, List, Optional

from .provider import KnowledgeProvider
from .uncomtrade_client import UnComtradeApiClient


class UnComtradeExternalSourceAdapter(KnowledgeProvider):
    """External source adapter boundary for UN Comtrade API.

    This adapter isolates UN Comtrade-specific schema and transport details from
    the DEM core. It owns:
      - UN Comtrade API communication
      - Authentication/configuration via configuration layer
      - Response transformation into DEM knowledge shape
      - ``source_id`` assignment
      - Confidence calculation per contract
      - Additional fields placement into ``metadata``

    The adapter does not:
      - Mutate DEM core
      - Expose raw UN Comtrade responses to users
      - Perform external research on behalf of users
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        self._config = config or {}
        self._source_id = self._config.get("source_id", "un-comtrade")
        self._provider_name = self._config.get("name", "UN Comtrade External Knowledge")
        self._provider_type = self._config.get("type", "external_trade_intelligence")
        self._version = self._config.get("version", "1.0.0")
        self._updated_at = self._config.get("updated_at", "")

        base_url = self._config.get("base_url", "")
        self._base_url = base_url.rstrip("/")
        api_key = self._config.get("api_key")
        timeout_seconds = float(self._config.get("timeout_seconds", 30.0))
        self._client = UnComtradeApiClient(
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
            requests = self._build_request(query=query, context=context, scope=scope, limit=limit)
            if not requests:
                return {
                    "results": [],
                    "confidence": None,
                    "sources": [self._source_id],
                }

            raw_results: List[tuple] = []
            for path, params, _cmd_code in requests:
                try:
                    raw = await self._client.request(method="GET", path=path, params=params)
                    raw_results.append((raw, _cmd_code))
                except Exception:
                    continue

            results = self._transform_multi(raw_results, context=context, limit=limit, scope=scope)
        except Exception:
            return {
                "results": [],
                "confidence": None,
                "sources": [self._source_id],
            }

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
    ) -> List[tuple]:
        """Build UN Comtrade API request path and query parameters.

        Returns:
            List of (path, params, cmd_code) tuples, one per commodity.
        """
        if not isinstance(context, dict):
            context = {}

        type_code = scope or context.get("type") or "C"
        if not isinstance(type_code, str) or not type_code:
            type_code = "C"

        freq_code = context.get("frequency") or "A"
        if not isinstance(freq_code, str) or not freq_code:
            freq_code = "A"

        cl_code = context.get("classification") or "HS"
        if not isinstance(cl_code, str) or not cl_code:
            cl_code = "HS"

        path = f"/public/v1/preview/{type_code}/{freq_code}/{cl_code}"

        base_params: Dict[str, Any] = {}
        reporter = context.get("reporter")
        if reporter is not None:
            base_params["reporterCode"] = reporter
        partner = context.get("partner")
        if partner is not None:
            base_params["partnerCode"] = partner
        flow = context.get("flow") or "X"
        if not isinstance(flow, str) or not flow:
            flow = "X"
        base_params["flowCode"] = flow
        period = context.get("period")
        if period is not None:
            base_params["period"] = period

        maxrecords = min(limit, 500)
        base_params["maxrecords"] = maxrecords

        commodities = context.get("commodities") or (scope.get("commodities") if isinstance(scope, dict) else None)
        requests: List[tuple] = []
        if commodities:
            if isinstance(commodities, list):
                cmd_codes = [c for c in commodities if isinstance(c, str) and c]
            else:
                cmd_codes = [commodities] if isinstance(commodities, str) and commodities else []
            for cmd_code in cmd_codes:
                params = dict(base_params)
                params["cmdCode"] = cmd_code
                requests.append((path, params, cmd_code))
        else:
            requests.append((path, dict(base_params), None))

        return requests

    def _transform_multi(
        self,
        raw_results: List[tuple],
        context: Optional[Dict[str, Any]],
        limit: int,
        scope: Optional[str],
    ) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for raw, _cmd_code in raw_results:
            if not isinstance(raw, dict):
                continue
            data = raw.get("data") or raw.get("dataset")
            if not isinstance(data, list):
                continue
            for entry in data:
                if not isinstance(entry, dict):
                    continue
                item = self._transform_entry(entry)
                if _cmd_code:
                    item_cmd = item.get("metadata", {}).get("cmd_code") or item.get("cmd_code") or ""
                    if item_cmd != _cmd_code:
                        continue
                items.append(item)
        return items[:limit]

    def _transform(self, raw: Any, context: Optional[Dict[str, Any]], limit: int, scope: Optional[str]) -> List[Dict[str, Any]]:
        if not isinstance(raw, dict):
            return []

        data = raw.get("data") or raw.get("dataset")
        if not isinstance(data, list):
            return []

        items: List[Dict[str, Any]] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue
            items.append(self._transform_entry(entry))

        return items[:limit]
    def _transform_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        reporter_code = entry.get("reporterCode", "")
        reporter_desc = entry.get("reporterDesc") or ""
        partner_code = entry.get("partnerCode", "")
        partner_desc = entry.get("partnerDesc") or ""
        flow_code = entry.get("flowCode", "")
        cmd_code = entry.get("cmdCode", "")
        cmd_desc = entry.get("cmdDesc") or ""
        ref_year = entry.get("refYear", "")
        freq_code = entry.get("freqCode", "")
        classification_code = entry.get("classificationCode", "")
        fobvalue = entry.get("fobvalue", 0.0)
        net_wgt = entry.get("netWgt")
        qty = entry.get("qty", 0.0)
        alt_qty = entry.get("altQty")
        is_reported = entry.get("isReported", False)

        record_id = f"{reporter_code}_{partner_code}_{cmd_code}_{ref_year}"
        record_hash = str(hash(frozenset(entry.items()))) if entry else ""

        confidence = 0.9 if is_reported else 0.7

        content = self._build_content(cmd_desc=cmd_desc, cmd_code=cmd_code, fobvalue=fobvalue)

        return {
            "id": record_id,
            "content": content,
            "source_id": self._source_id,
            "confidence": confidence,
            "metadata": {
                "reporter_code": reporter_code,
                "reporter_desc": reporter_desc,
                "partner_code": partner_code,
                "partner_desc": partner_desc,
                "flow_code": flow_code,
                "cmd_code": cmd_code,
                "cmd_desc": cmd_desc,
                "ref_year": ref_year,
                "freq_code": freq_code,
                "classification_code": classification_code,
                "fobvalue": fobvalue,
                "net_weight": net_wgt,
                "quantity": qty,
                "alt_quantity": alt_qty,
                "is_reported": is_reported,
                "source_authority": "UN",
                "source_url": "https://comtrade.un.org",
                "record_hash": record_hash,
                "retrieval_status": "success",
                "updated_at": self._updated_at,
                "version": self._version,
            },
        }

    def _build_content(self, cmd_desc: str, cmd_code: str, fobvalue: float) -> str:
        if cmd_desc:
            return f"{cmd_desc} ({cmd_code}) — {fobvalue} USD"
        if cmd_code:
            return f"HS {cmd_code} — {fobvalue} USD"
        return f"Trade flow — {fobvalue} USD"

    async def get_sources(self) -> List[Dict[str, Any]]:
        source: Dict[str, Any] = {
            "id": self._source_id,
            "name": self._provider_name,
            "type": self._provider_type,
            "version": self._version,
            "updated_at": self._updated_at,
            "source_url": "https://comtrade.un.org",
        }
        return [source]



