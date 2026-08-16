import hashlib
import json
import uuid
from typing import Any, Dict, List, Optional

from app.core.credentials.credential_store import CredentialStore
from .provider import KnowledgeProvider
from .tradedata_client import TradeDataApiClient


class TradeDataExternalSourceAdapter(KnowledgeProvider):
    """External source adapter boundary for TradeData API.

    This adapter isolates TradeData-specific schema and transport details from
    the DEM core. It owns:
      - TradeData API communication
      - Authentication/configuration via configuration layer
      - Response transformation into DEM knowledge shape
      - ``source_id`` assignment
      - Confidence calculation per contract
      - Additional fields placement into ``metadata``

    The adapter does not:
      - Mutate DEM core
      - Expose raw TradeData responses to users
      - Perform external research on behalf of users
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None, credential_store: Optional[CredentialStore] = None) -> None:
        self._config = config or {}
        self._source_id = self._config.get("source_id", "tradedata")
        self._provider_name = self._config.get("name", "TradeData External Knowledge")
        self._provider_type = self._config.get("type", "external_trade_intelligence")
        self._version = self._config.get("version", "1.0")
        self._updated_at = self._config.get("updated_at", "")

        base_url = self._config.get("base_url", "")
        api_key = self._config.get("api_key")
        timeout_seconds = float(self._config.get("timeout_seconds", 30.0))
        self._client = TradeDataApiClient(
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

            payload = self._build_payload(query=query, context=context, limit=limit)
            raw = await self._client.trade_detail(payload=payload)
        except ValueError:
            raise
        except Exception:
            return {
                "results": [],
                "confidence": None,
                "sources": [self._source_id],
            }

        results = self._transform(raw, context=context, limit=limit)
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

    def _build_payload(self, query: str, context: Optional[Dict[str, Any]], limit: int) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "data_coverage": 1,
            "date_range": [20220101, 20221231],
            "page": 1,
            "page_size": min(limit, 50),
            "sort": "date",
            "order": "desc",
        }

        if isinstance(context, dict):
            start_date = context.get("start_date")
            end_date = context.get("end_date")
            if start_date and end_date:
                payload["date_range"] = [int(start_date), int(end_date)]

            hs_code = context.get("hs_code")
            if hs_code:
                payload["hs_code"] = hs_code if isinstance(hs_code, list) else [hs_code]

            product_keyword = context.get("product_keyword") or query
            if product_keyword:
                payload["product_keyword"] = product_keyword if isinstance(product_keyword, list) else [product_keyword]

            buyer_name = context.get("buyer_name")
            if buyer_name:
                payload["buyer_name"] = buyer_name if isinstance(buyer_name, list) else [buyer_name]

            supplier_name = context.get("supplier_name")
            if supplier_name:
                payload["supplier_name"] = supplier_name if isinstance(supplier_name, list) else [supplier_name]

            country_code = context.get("country")
            affected_country = context.get("affected_country")
            if country_code:
                payload["desti_country_code"] = [country_code] if not isinstance(country_code, list) else country_code
                payload["origincl_country_code"] = [country_code] if not isinstance(country_code, list) else country_code
            if affected_country:
                payload["origincl_country_code"] = [affected_country] if not isinstance(affected_country, list) else affected_country

        return payload

    def _transform(self, raw: Any, context: Optional[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        if not isinstance(raw, dict):
            return []

        data = raw.get("data")
        if not isinstance(data, list):
            return []

        items: List[Dict[str, Any]] = []
        requested_hs_codes = []
        requested_buyers = []
        requested_suppliers = []
        requested_start_date = None
        requested_end_date = None
        if isinstance(context, dict):
            requested_hs_codes = context.get("hs_code", [])
            if isinstance(requested_hs_codes, str):
                requested_hs_codes = [requested_hs_codes]
            requested_buyers = context.get("buyer_name", [])
            if isinstance(requested_buyers, str):
                requested_buyers = [requested_buyers]
            requested_suppliers = context.get("supplier_name", [])
            if isinstance(requested_suppliers, str):
                requested_suppliers = [requested_suppliers]
            requested_start_date = context.get("start_date")
            requested_end_date = context.get("end_date")

        for entry in data:
            if not isinstance(entry, dict):
                continue
            items.append(self._transform_entry(entry, requested_hs_codes=requested_hs_codes, requested_buyers=requested_buyers, requested_suppliers=requested_suppliers, requested_start_date=requested_start_date, requested_end_date=requested_end_date))

        return items[:limit]

    def _transform_entry(self, entry: Dict[str, Any], requested_hs_codes: List[str], requested_buyers: List[str], requested_suppliers: List[str], requested_start_date: Optional[str], requested_end_date: Optional[str]) -> Dict[str, Any]:
        data_source = entry.get("dataSource") or ""
        date = entry.get("date") or ""
        buyer_name = entry.get("buyerName") or ""
        supplier_name = entry.get("supplierName") or ""
        origin_country = entry.get("originCountryCode") or ""
        destination_country = entry.get("destinationCountryCode") or ""
        hs_code = entry.get("hsCode") or ""
        hs_code_desc = entry.get("hsCodeDesc") or ""
        product_keyword = entry.get("productKeyword") or ""
        quantity = entry.get("quantity")
        weight = entry.get("weight")
        trade_amount = entry.get("tradeAmount")
        master_bl = entry.get("masterBl") or ""
        container_no = entry.get("containerNo") or ""
        other_info = entry.get("otherInfo")

        content_parts = []
        if buyer_name:
            content_parts.append(f"Buyer: {buyer_name}")
        if supplier_name:
            content_parts.append(f"Supplier: {supplier_name}")
        if hs_code_desc:
            content_parts.append(f"Product: {hs_code_desc}")
        if product_keyword:
            content_parts.append(f"Keyword: {product_keyword}")
        if quantity is not None or weight is not None or trade_amount is not None:
            metrics = []
            if quantity is not None:
                metrics.append(f"Qty: {quantity}")
            if weight is not None:
                metrics.append(f"Weight: {weight}kg")
            if trade_amount is not None:
                metrics.append(f"Amount: ${trade_amount}")
            content_parts.append(f"Metrics: {' | '.join(metrics)}")
        content = " | ".join(content_parts) if content_parts else product_keyword or hs_code_desc or "Trade record"

        country = destination_country or origin_country
        source_url = master_bl or container_no
        legal_act_reference = ""
        if isinstance(other_info, dict):
            legal_act_reference = str(other_info)

        confidence = self._calculate_confidence(entry=entry, data_source=data_source, date=date, hs_code=hs_code, requested_hs_codes=requested_hs_codes, requested_buyers=requested_buyers, requested_suppliers=requested_suppliers, requested_start_date=requested_start_date, requested_end_date=requested_end_date)
        retrieval_status = self._calculate_retrieval_status(entry=entry, data_source=data_source, date=date, country=country)

        record_id = str(entry.get("masterBl") or entry.get("containerNo") or uuid.uuid4())
        record_hash = hashlib.sha256(json.dumps(entry, sort_keys=True, default=str).encode("utf-8")).hexdigest()

        return {
            "id": record_id,
            "content": content,
            "source_id": self._source_id,
            "confidence": confidence,
            "metadata": {
                "source_authority": data_source,
                "effective_date": date,
                "country": country,
                "source_url": source_url,
                "legal_act_reference": legal_act_reference,
                "updated_at": self._updated_at,
                "version": self._version,
                "record_hash": record_hash,
                "retrieval_status": retrieval_status,
            },
        }

    def _calculate_confidence(self, entry: Dict[str, Any], data_source: str, date: str, hs_code: str, requested_hs_codes: List[str], requested_buyers: List[str], requested_suppliers: List[str], requested_start_date: Optional[str], requested_end_date: Optional[str]) -> float:
        if data_source and date and (entry.get("originCountryCode") or entry.get("destinationCountryCode")):
            confidence = 0.85
        elif data_source or date:
            confidence = 0.75
        elif entry.get("hsCode") or entry.get("buyerName") or entry.get("supplierName"):
            confidence = 0.65
        else:
            confidence = 0.50

        if hs_code and requested_hs_codes and hs_code in requested_hs_codes:
            confidence = min(confidence + 0.05, 0.95)
        buyer_name = entry.get("buyerName") or ""
        supplier_name = entry.get("supplierName") or ""
        if buyer_name and requested_buyers and buyer_name in requested_buyers:
            confidence = min(confidence + 0.05, 0.95)
        if supplier_name and requested_suppliers and supplier_name in requested_suppliers:
            confidence = min(confidence + 0.05, 0.95)

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
        if data_source or date or country or entry.get("hsCode") or entry.get("buyerName") or entry.get("supplierName"):
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
